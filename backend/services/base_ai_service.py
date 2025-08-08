"""
Base AI Service Module

This module provides the foundational service class for all AI-powered services.
It handles common functionality like API client management, retry logic, 
error handling, and cost tracking without imposing specific method signatures.

Class Hierarchy:
    BaseAIService (this file)
        ├── ContentGenerationService (for story/content generation)
        │   ├── LangChainService
        │   ├── SemanticKernelService
        │   └── LangGraphService
        ├── ChatService (for conversational AI)
        │   ├── LangChainChatService
        │   ├── SemanticKernelChatService
        │   └── LangGraphChatService
        └── ContextService (for context-aware processing)
            ├── LangChainContextService
            ├── SemanticKernelContextService
            └── LangGraphContextService
"""

from typing import Optional, Dict, Any, List
import asyncio
import time
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError
import httpx

from app_config import settings, custom_settings
from logging_config import get_logger
from pricing import calculate_cost, get_model_pricing
from transaction_context import TransactionAware, get_current_transaction_guid
from retry_utils import retry_api_calls, retry_network_ops
from exceptions import (
    APIKeyError,
    APIConnectionError as CustomAPIConnectionError,
    APIRateLimitError,
    TimeoutError
)

logger = get_logger(__name__)

class BaseAIService(TransactionAware):
    """Base class for all AI-powered services.
    
    This class provides common functionality for AI services including:
    - Client initialization for custom OpenAI-compatible providers
    - Connection pooling and retry logic
    - Error handling and logging
    - Token usage tracking
    - Cost calculation
    - Access to both main and custom settings configurations
    
    This is a concrete base class - services can inherit from it directly
    without needing to implement any abstract methods.
    
    Attributes:
        service_name: The name of the service class.
        provider_name: The custom provider name.
        custom_settings: CustomProviderSettings instance (None if PROVIDER_NAME != 'custom').
                        Provides access to CUSTOM_VAR and all default settings when using
                        custom providers.
    
    Settings Access:
        - settings: Global main settings (always available)
        - self.custom_settings: Custom provider settings (available when PROVIDER_NAME=custom)
        
    Example Usage in Subclasses:
        if self.custom_settings and self.custom_settings.custom_var:
            # Access custom variable for provider-specific logic
            custom_value = self.custom_settings.custom_var
            
        # Custom settings also has ALL default settings
        if self.custom_settings:
            timeout = self.custom_settings.api_timeout  # Same as settings.api_timeout
    """
    
    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None
        self._http_client: Optional[httpx.AsyncClient] = None
        self.service_name = self.__class__.__name__
        self.provider_name = settings.provider_name
        # Expose custom_settings to all services for header generation and custom logic
        self.custom_settings = custom_settings
        
    async def _ensure_client(self) -> AsyncOpenAI:
        """Ensure the OpenAI client is initialized.
        
        Creates the client on first access to avoid initialization
        overhead during service creation.
        
        Returns:
            An AsyncOpenAI client instance.
            
        Raises:
            APIKeyError: If client initialization fails.
        """
        if self._client is None:
            self._client = await self._create_client()
        return self._client
    
    @retry_network_ops
    async def _create_client(self) -> AsyncOpenAI:
        """Create OpenAI client with connection pooling.
        
        Initializes the client for the custom provider
        with optimized connection settings for performance.
        
        Returns:
            A configured AsyncOpenAI client.
            
        Raises:
            APIKeyError: If client initialization fails.
            NotImplementedError: If custom API type is not supported.
            
        Examples:
            >>> client = await self._create_client()
            >>> isinstance(client, AsyncOpenAI)
            True
        """
        try:
            # Create httpx client with connection pooling
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.openai_timeout),
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                )
            )
            
            # Create headers based on provider type
            # Start with default headers from environment if provided
            headers = settings.provider_headers.copy() if settings.provider_headers else {}
            
            # Apply provider-specific header logic
            provider_lower = settings.provider_name.lower()
            
            if provider_lower == "openrouter":
                # OpenRouter uses empty headers - the AsyncOpenAI client handles auth
                logger.info("Creating headers for OpenRouter provider")
                # OpenRouter authentication is handled by the api_key parameter
                # No additional headers needed
                
            elif provider_lower == "custom":
                # Custom provider with extended headers
                logger.info("Creating headers for custom provider")
                
                # Add API key if provided (some custom providers need it in headers)
                if settings.provider_api_key:
                    headers["X-API-Key"] = settings.provider_api_key
                
                # Add custom provider metadata
                headers["X-Provider-Type"] = "custom"
                headers["X-Request-Source"] = "fastapi-llm"
                
                # Add application info
                headers["X-App-Name"] = settings.app_name
                headers["X-App-Version"] = settings.app_version
                
                # Add debug headers if enabled
                if settings.debug_mode:
                    headers["X-Debug-Mode"] = "enabled"
                    headers["X-Debug-Level"] = "verbose"
                
                # Add timeout info for debugging
                headers["X-Timeout"] = str(settings.api_timeout)
                
                # Add custom variable if available
                if self.custom_settings and self.custom_settings.custom_var:
                    headers["X-Custom-Var"] = self.custom_settings.custom_var
                    headers["X-Custom-Data"] = self.custom_settings.custom_var
                
                # Add rate limiting info if enabled
                if settings.rate_limiting_enabled:
                    headers["X-Rate-Limit-Enabled"] = "true"
                
                # Ensure content type is set
                if "Content-Type" not in headers:
                    headers["Content-Type"] = "application/json"
                    
            else:
                # Generic provider - minimal headers
                logger.info(f"Creating headers for generic provider '{settings.provider_name}'")
                # Most providers handle auth via the api_key parameter
                # Add minimal app identification
                headers["X-App-Name"] = settings.app_name
                headers["X-App-Version"] = settings.app_version
            
            # Log the headers being used (mask sensitive data)
            safe_headers = {k: v if k.lower() not in ['authorization', 'x-api-key', 'api-key'] 
                           else '***' for k, v in headers.items()}
            logger.info(f"Created headers for provider '{settings.provider_name}'", headers=safe_headers)
            
            if settings.provider_api_type == "openai":
                # Use OpenAI-compatible client
                # The headers defined above are passed to ALL API calls made by this client
                client = AsyncOpenAI(
                    api_key=settings.provider_api_key,  # Sent as Authorization: Bearer {key}
                    base_url=settings.provider_api_base_url,
                    http_client=self._http_client,
                    max_retries=0,  # Disable OpenAI client retries - we handle retries with tenacity
                    default_headers=headers  # ← HEADERS ARE SET HERE for all requests
                )
            else:
                # For non-OpenAI compatible APIs, we'd need a custom implementation
                raise NotImplementedError(
                    f"Provider API type '{settings.provider_api_type}' is not yet implemented. "
                    "Currently only 'openai' compatible APIs are supported."
                )
            
            logger.info("Provider client created",
                       service=self.service_name,
                       provider=settings.provider_name,
                       base_url=settings.provider_api_base_url,
                       model=settings.provider_model)
            
            return client
        except Exception as e:
            logger.error("Failed to create provider client",
                        provider=settings.provider_name,
                        service=self.service_name,
                        error=str(e))
            raise APIKeyError(f"Failed to initialize {settings.provider_name} client")
    
    @retry_api_calls
    async def _call_api_with_retry(self, messages: List[Dict[str, str]], **kwargs) -> tuple[str, Dict[str, Any]]:
        """Call OpenAI API with comprehensive retry logic.
        
        Uses tenacity-based retry strategy with exponential backoff and jitter
        for handling transient connection errors, rate limits, and API failures.
        All retry attempts are logged with transaction GUID tracking.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            **kwargs: Additional parameters passed to the API call.
            
        Returns:
            A tuple of (response_content, usage_info) where usage_info
            contains token counts and execution time.
            
        Raises:
            APIConnectionError: If all retry attempts fail.
            APIError: If the API returns an error after all retries.
            
        Examples:
            >>> response, usage = await self._call_api_with_retry(
            ...     [{"role": "user", "content": "Tell me a story"}]
            ... )
        """
        return await self._call_api(messages, **kwargs)
    
    @retry_api_calls
    async def _call_api(self, messages: List[Dict[str, str]], **kwargs) -> tuple[str, Dict[str, Any]]:
        """Call OpenAI API.
        
        Makes the actual API call to the configured LLM provider with
        proper error handling and usage tracking.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            **kwargs: Optional parameters:
                - temperature: Controls randomness (0-2). Defaults to 0.7.
                - max_tokens: Maximum tokens to generate. Defaults to 500.
                
        Returns:
            A tuple containing:
            - response_content: The generated text response
            - usage_info: Dictionary with token counts and timing:
                - input_tokens: Number of tokens in the prompt
                - output_tokens: Number of tokens in the response
                - total_tokens: Sum of input and output tokens
                - execution_time_ms: API call duration in milliseconds
                - estimated_cost_usd: Estimated cost in USD
                - input_cost: Cost for input tokens
                - output_cost: Cost for output tokens
                
        Raises:
            TimeoutError: If the API call exceeds the timeout.
            APIRateLimitError: If rate limits are exceeded.
            CustomAPIConnectionError: For connection failures.
            APIError: For other API errors.
            
        Examples:
            >>> content, usage = await self._call_api(
            ...     [{"role": "system", "content": "You are a storyteller"},
            ...      {"role": "user", "content": "Tell me about Alice"}],
            ...     temperature=0.8,
            ...     max_tokens=1000
            ... )
        """
        try:
            # Set default parameters based on provider
            model = settings.provider_model
            
            params = {
                "model": model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 500),
                "timeout": settings.openai_timeout
            }
            
            # Make API call
            logger.debug("Calling provider API",
                        provider=settings.provider_name,
                        service=self.service_name,
                        model=model,
                        message_count=len(messages))
            
            start_time = time.time()
            client = await self._ensure_client()
            response = await asyncio.wait_for(
                client.chat.completions.create(**params),
                timeout=settings.openai_timeout
            )
            execution_time_ms = (time.time() - start_time) * 1000
            
            content = response.choices[0].message.content
            
            # Extract token usage from response
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            total_tokens = response.usage.total_tokens if response.usage else 0
            
            # Calculate cost information using pricing module
            input_cost, output_cost, total_cost = calculate_cost(model, input_tokens, output_tokens)
            pricing = get_model_pricing(model)
            
            # Prepare comprehensive usage information including costs
            usage_info = {
                # Token usage information
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                
                # Cost information (converted to float for JSON serialization)
                "estimated_cost_usd": float(total_cost),
                "input_cost": float(input_cost),
                "output_cost": float(output_cost),
                "input_cost_per_1k_tokens": float(pricing["input_cost_per_1k"]),
                "output_cost_per_1k_tokens": float(pricing["output_cost_per_1k"]),
                
                # Performance metrics
                "execution_time_ms": round(execution_time_ms, 2)
            }
            
            logger.info("API call successful",
                       service=self.service_name,
                       provider=settings.provider_name,
                       model=model,
                       response_length=len(content) if content else 0,
                       execution_time_ms=usage_info["execution_time_ms"],
                       input_tokens=usage_info["input_tokens"],
                       output_tokens=usage_info["output_tokens"],
                       total_tokens=usage_info["total_tokens"],
                       estimated_cost_usd=usage_info["estimated_cost_usd"])
            
            return content or "", usage_info
            
        except asyncio.TimeoutError:
            logger.error("API call timed out",
                        service=self.service_name,
                        timeout=settings.openai_timeout)
            raise TimeoutError(f"API call timed out after {settings.openai_timeout} seconds")
        
        except RateLimitError as e:
            logger.error("API rate limit exceeded",
                        service=self.service_name,
                        error=str(e))
            raise APIRateLimitError("API rate limit exceeded. Please try again later.")
        
        except APIConnectionError as e:
            logger.error("API connection failed",
                        service=self.service_name,
                        error=str(e))
            raise CustomAPIConnectionError(f"Failed to connect to API: {str(e)}")
        
        except APIError as e:
            logger.error("API error occurred",
                        service=self.service_name,
                        error=str(e),
                        error_type=type(e).__name__)
            raise CustomAPIConnectionError(f"API error: {str(e)}")
        
        except Exception as e:
            logger.error("Unexpected error in API call",
                        service=self.service_name,
                        error=str(e),
                        error_type=type(e).__name__)
            raise
    
    @retry_network_ops
    async def close(self):
        """Clean up resources.
        
        Closes the HTTP client connection if it exists. Should be called
        when the service is no longer needed to free up resources.
        
        Examples:
            >>> service = SomeAIService()
            >>> try:
            ...     # Use service
            ... finally:
            ...     await service.close()
        """
        if self._http_client:
            await self._http_client.aclose()
            logger.info("HTTP client connection closed", service=self.service_name)