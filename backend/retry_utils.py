"""
Retry Utilities Module

This module provides comprehensive retry mechanisms using tenacity library
for handling transient failures across the application. It implements
exponential backoff with jitter to prevent thundering herd problems
and provides transaction-aware logging for full traceability.

Features:
- Exponential backoff with randomized jitter
- Configurable retry attempts and timing
- Transaction GUID tracking across retries
- Comprehensive error classification
- Detailed retry logging with structured data
- Pre-configured decorators for different scenarios

Usage:
    from retry_utils import retry_api_calls, retry_database_ops
    
    @retry_api_calls
    async def call_ai_service():
        # This will retry on API failures
        pass
    
    @retry_database_ops  
    def save_to_database():
        # This will retry on database failures
        pass
"""

import asyncio
import time
from typing import Any, Callable, Optional, Type, Union, List
from functools import wraps
import inspect

# Third party imports
import tenacity
from tenacity import (
    retry,
    stop_after_attempt, 
    wait_exponential_jitter,
    retry_if_exception_type,
    retry_if_exception,
    before_sleep_log,
    after_log,
    RetryCallState
)

# Application imports
from config import settings
from logging_config import get_logger
from transaction_context import get_current_transaction_guid
from exceptions import (
    APIConnectionError,
    APIRateLimitError, 
    TimeoutError
)

# Standard library and third-party exceptions we want to retry
import httpx
import openai
from sqlalchemy.exc import OperationalError, DisconnectionError
from fastapi import HTTPException

logger = get_logger(__name__)

# Suppress or redirect tenacity's internal logging to avoid unformatted console output
import logging as stdlib_logging
tenacity_logger = stdlib_logging.getLogger('tenacity')
tenacity_logger.setLevel(stdlib_logging.WARNING)  # Only show warnings and errors
tenacity_logger.propagate = False  # Don't propagate to root logger

# Also suppress OpenAI and httpx retry logs that might not be formatted
openai_logger = stdlib_logging.getLogger('openai')
openai_logger.setLevel(stdlib_logging.WARNING)
openai_logger.propagate = False

httpx_logger = stdlib_logging.getLogger('httpx')
httpx_logger.setLevel(stdlib_logging.WARNING)
httpx_logger.propagate = False

# Suppress httpcore logs as well (used by httpx internally)
httpcore_logger = stdlib_logging.getLogger('httpcore')
httpcore_logger.setLevel(stdlib_logging.WARNING)
httpcore_logger.propagate = False

# =============================================================================
# ERROR CLASSIFICATION
# =============================================================================

def is_network_error(exception: Exception) -> bool:
    """Check if exception is a network/connection error that should be retried.
    
    Args:
        exception: The exception to classify
        
    Returns:
        True if this is a retryable network error
    """
    return isinstance(exception, (
        # HTTP/Network errors
        httpx.ConnectError,
        httpx.ConnectTimeout,
        httpx.ReadTimeout,
        httpx.NetworkError,
        httpx.TimeoutException,
        ConnectionError,
        # OpenAI SDK errors
        openai.APIConnectionError,
        openai.APITimeoutError,
        # Custom application errors
        APIConnectionError,
        TimeoutError
    ))

def is_rate_limit_error(exception: Exception) -> bool:
    """Check if exception is a rate limiting error that should be retried.
    
    Args:
        exception: The exception to classify
        
    Returns:
        True if this is a retryable rate limit error
    """
    return isinstance(exception, (
        openai.RateLimitError,
        APIRateLimitError
    )) or (
        isinstance(exception, (httpx.HTTPStatusError, HTTPException)) and 
        getattr(exception, 'status_code', None) == 429
    )

def is_server_error(exception: Exception) -> bool:
    """Check if exception is a server error that should be retried.
    
    Args:
        exception: The exception to classify
        
    Returns:
        True if this is a retryable server error (5xx status codes)
    """
    return (
        isinstance(exception, (httpx.HTTPStatusError, HTTPException)) and
        500 <= getattr(exception, 'status_code', 0) < 600
    ) or isinstance(exception, (
        openai.InternalServerError,
        openai.APIError
    ))

def is_database_error(exception: Exception) -> bool:
    """Check if exception is a database error that should be retried.
    
    Args:
        exception: The exception to classify
        
    Returns:
        True if this is a retryable database error
    """
    return isinstance(exception, (
        OperationalError,
        DisconnectionError
    ))

def is_retryable_error(exception: Exception) -> bool:
    """Check if any exception should be retried.
    
    This is the main retry condition that combines all error types.
    
    Args:
        exception: The exception to classify
        
    Returns:
        True if this exception should trigger a retry
    """
    return (
        is_network_error(exception) or
        is_rate_limit_error(exception) or 
        is_server_error(exception) or
        is_database_error(exception)
    )

# =============================================================================
# RETRY LOGGING CALLBACKS
# =============================================================================

def log_retry_attempt(retry_state: RetryCallState) -> None:
    """Log retry attempt with transaction tracking and detailed context.
    
    Args:
        retry_state: Tenacity retry state containing attempt information
    """
    if not settings.retry_enabled:
        return
        
    transaction_guid = get_current_transaction_guid()
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    
    # Classify the error for better logging
    error_type = "unknown"
    if exception:
        if is_network_error(exception):
            error_type = "network_error"
        elif is_rate_limit_error(exception):
            error_type = "rate_limit_error"  
        elif is_server_error(exception):
            error_type = "server_error"
        elif is_database_error(exception):
            error_type = "database_error"
    
    # Calculate timing information
    next_sleep = retry_state.next_action.sleep if retry_state.next_action else 0
    elapsed_time = time.time() - retry_state.start_time
    
    logger.warning(
        "Retry attempt failed, retrying",
        transaction_guid=transaction_guid,
        function_name=retry_state.fn.__name__ if retry_state.fn else "unknown",
        retry_attempt=f"{retry_state.attempt_number}/{settings.retry_max_attempts}",
        error_type=error_type,
        error_message=str(exception) if exception else "Unknown error",
        next_retry_in=f"{next_sleep:.2f}s" if next_sleep > 0 else "final_attempt",
        total_elapsed=f"{elapsed_time:.2f}s",
        retry_enabled=settings.retry_enabled
    )

def log_retry_success(retry_state: RetryCallState) -> None:
    """Log successful completion after retries.
    
    Args:
        retry_state: Tenacity retry state containing attempt information
    """
    if retry_state.attempt_number > 1:  # Only log if we actually retried
        transaction_guid = get_current_transaction_guid()
        elapsed_time = time.time() - retry_state.start_time
        
        logger.info(
            "Operation succeeded after retries",
            transaction_guid=transaction_guid,
            function_name=retry_state.fn.__name__ if retry_state.fn else "unknown",
            total_attempts=retry_state.attempt_number,
            total_elapsed=f"{elapsed_time:.2f}s",
            retry_enabled=settings.retry_enabled
        )

def log_retry_failure(retry_state: RetryCallState) -> None:
    """Log final failure after all retries exhausted.
    
    Args:
        retry_state: Tenacity retry state containing attempt information
    """
    transaction_guid = get_current_transaction_guid()
    exception = retry_state.outcome.exception() if retry_state.outcome else None
    elapsed_time = time.time() - retry_state.start_time
    
    logger.error(
        "Operation failed after all retry attempts",
        transaction_guid=transaction_guid,
        function_name=retry_state.fn.__name__ if retry_state.fn else "unknown",
        total_attempts=retry_state.attempt_number,
        max_attempts=settings.retry_max_attempts,
        total_elapsed=f"{elapsed_time:.2f}s",
        final_error=str(exception) if exception else "Unknown error",
        retry_enabled=settings.retry_enabled
    )

# =============================================================================
# PRE-CONFIGURED RETRY DECORATORS
# =============================================================================

def create_retry_decorator(
    name: str,
    stop_condition: Optional[tenacity.stop.stop_base] = None,
    wait_condition: Optional[tenacity.wait.wait_base] = None,
    retry_condition: Optional[Callable] = None
) -> Callable:
    """Create a retry decorator with optional configuration override.
    
    Args:
        name: Name for logging purposes
        stop_condition: When to stop retrying (defaults to configured max attempts)
        wait_condition: How long to wait between retries (defaults to exponential backoff)
        retry_condition: Which exceptions to retry (defaults to all retryable errors)
        
    Returns:
        Configured retry decorator
    """
    if not settings.retry_enabled:
        # Return a no-op decorator if retries are disabled
        def no_retry_decorator(func):
            return func
        return no_retry_decorator
    
    # Use provided conditions or fall back to defaults
    stop_condition = stop_condition or stop_after_attempt(settings.retry_max_attempts)
    wait_condition = wait_condition or wait_exponential_jitter(
        initial=settings.retry_min_wait_seconds,
        max=settings.retry_max_wait_seconds,
        exp_base=settings.retry_multiplier,
        jitter=True
    )
    retry_condition = retry_condition or retry_if_exception(is_retryable_error)
    
    def decorator(func):
        # Handle both sync and async functions
        if inspect.iscoroutinefunction(func):
            @retry(
                stop=stop_condition,
                wait=wait_condition,
                retry=retry_condition,
                before_sleep=lambda retry_state: log_retry_attempt(retry_state),
                after=lambda retry_state: (
                    log_retry_success(retry_state) if retry_state.outcome and not retry_state.outcome.failed 
                    else log_retry_failure(retry_state) if retry_state.attempt_number >= settings.retry_max_attempts
                    else None
                ),
                reraise=True
            )
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            return async_wrapper
        else:
            @retry(
                stop=stop_condition,
                wait=wait_condition,
                retry=retry_condition,
                before_sleep=lambda retry_state: log_retry_attempt(retry_state),
                after=lambda retry_state: (
                    log_retry_success(retry_state) if retry_state.outcome and not retry_state.outcome.failed
                    else log_retry_failure(retry_state) if retry_state.attempt_number >= settings.retry_max_attempts
                    else None
                ),
                reraise=True
            )
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return sync_wrapper
    
    return decorator

# Pre-configured decorators for different scenarios
retry_api_calls = create_retry_decorator(
    name="api_calls",
    retry_condition=retry_if_exception(lambda e: is_network_error(e) or is_rate_limit_error(e) or is_server_error(e))
)

retry_database_ops = create_retry_decorator(
    name="database_ops", 
    retry_condition=retry_if_exception(is_database_error)
)

retry_network_ops = create_retry_decorator(
    name="network_ops",
    retry_condition=retry_if_exception(is_network_error)
)

retry_all_errors = create_retry_decorator(
    name="all_errors",
    retry_condition=retry_if_exception(is_retryable_error)
)

# =============================================================================
# SPECIALIZED RETRY DECORATORS
# =============================================================================

def retry_with_backoff(
    max_attempts: Optional[int] = None,
    max_wait: Optional[int] = None,
    multiplier: Optional[float] = None,
    min_wait: Optional[float] = None
) -> Callable:
    """Create a custom retry decorator with specific timing parameters.
    
    Args:
        max_attempts: Override default max attempts
        max_wait: Override default max wait time
        multiplier: Override default backoff multiplier  
        min_wait: Override default min wait time
        
    Returns:
        Configured retry decorator with custom timing
    """
    return create_retry_decorator(
        name="custom_backoff",
        stop_condition=stop_after_attempt(max_attempts or settings.retry_max_attempts),
        wait_condition=wait_exponential_jitter(
            initial=min_wait or settings.retry_min_wait_seconds,
            max=max_wait or settings.retry_max_wait_seconds,
            multiplier=multiplier or settings.retry_multiplier,
            jitter=True
        )
    )

def retry_on_exceptions(*exception_types: Type[Exception]) -> Callable:
    """Create a retry decorator for specific exception types only.
    
    Args:
        *exception_types: Exception types that should trigger retries
        
    Returns:
        Configured retry decorator for specific exceptions
    """
    return create_retry_decorator(
        name="specific_exceptions",
        retry_condition=retry_if_exception_type(exception_types)
    )

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_retry_stats() -> dict:
    """Get current retry configuration statistics.
    
    Returns:
        Dictionary containing retry configuration details
    """
    return {
        "retry_enabled": settings.retry_enabled,
        "max_attempts": settings.retry_max_attempts,
        "max_wait_seconds": settings.retry_max_wait_seconds,
        "multiplier": settings.retry_multiplier,
        "min_wait_seconds": settings.retry_min_wait_seconds
    }

def log_retry_config() -> None:
    """Log the current retry configuration for debugging."""
    logger.info("Retry configuration loaded", **get_retry_stats())

# Initialize logging of retry configuration
log_retry_config()