"""
Rate Limiting Middleware for FastAPI using SlowAPI

This module provides comprehensive rate limiting with multi-level protection:
- Global server limits (prevents server overload)
- Per IP address limits (prevents individual abuse)
- Per endpoint limits (protects expensive operations)

Features:
- In-memory storage with automatic cleanup
- Fixed time windows (1-minute buckets)
- Configurable limits via environment variables
- Detailed logging with transaction tracking
- Standard HTTP 429 responses with rate limit headers
- No exemptions policy for consistent enforcement

Usage:
    from rate_limiting import RateLimitingMiddleware
    app.add_middleware(RateLimitingMiddleware)
"""

import time
import threading
from typing import Dict, Optional, Tuple
from datetime import datetime, timezone
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config import settings
from logging_config import get_logger
from transaction_context import get_current_transaction_guid

logger = get_logger(__name__)

class InMemoryRateLimitStore:
    """
    Thread-safe in-memory storage for rate limit counters.
    
    Uses fixed time windows with automatic cleanup to prevent memory leaks.
    Each window is exactly 60 seconds starting from the minute boundary.
    """
    
    def __init__(self):
        self._data: Dict[str, int] = {}
        self._lock = threading.RLock()
        self._last_cleanup = time.time()
        
    def _get_window_key(self, limit_type: str, identifier: str) -> str:
        """
        Generate a time-windowed key for rate limiting.
        
        Args:
            limit_type: Type of limit (global, ip, endpoint)
            identifier: Unique identifier (IP address, endpoint path, etc.)
            
        Returns:
            String key with embedded time window
        """
        # Fixed window: round down to the nearest minute
        window_start = int(time.time() // 60) * 60
        return f"{limit_type}:{identifier}:{window_start}"
        
    def increment(self, limit_type: str, identifier: str) -> int:
        """
        Increment counter for a specific limit type and identifier.
        
        Args:
            limit_type: Type of limit being enforced
            identifier: Unique identifier for the limit
            
        Returns:
            Current count after increment
        """
        with self._lock:
            key = self._get_window_key(limit_type, identifier)
            current_count = self._data.get(key, 0) + 1
            self._data[key] = current_count
            
            # Perform cleanup periodically
            self._maybe_cleanup()
            
            return current_count
    
    def get_count(self, limit_type: str, identifier: str) -> int:
        """
        Get current count for a specific limit type and identifier.
        
        Args:
            limit_type: Type of limit being checked
            identifier: Unique identifier for the limit
            
        Returns:
            Current count in the time window
        """
        with self._lock:
            key = self._get_window_key(limit_type, identifier)
            return self._data.get(key, 0)
    
    def _maybe_cleanup(self):
        """
        Remove expired entries to prevent memory leaks.
        
        Runs cleanup every 5 minutes to remove old time windows.
        """
        now = time.time()
        if now - self._last_cleanup < 300:  # Cleanup every 5 minutes
            return
            
        self._last_cleanup = now
        current_window = int(now // 60) * 60
        
        # Remove entries older than 2 minutes (current + previous window)
        expired_keys = []
        for key in self._data:
            try:
                # Extract timestamp from key (format: type:identifier:timestamp)
                timestamp = int(key.split(':')[-1])
                if timestamp < current_window - 60:  # Older than previous window
                    expired_keys.append(key)
            except (ValueError, IndexError):
                # Invalid key format, remove it
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._data[key]
            
        if expired_keys:
            logger.debug("Cleaned up expired rate limit entries", 
                        expired_count=len(expired_keys),
                        current_entries=len(self._data))

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Multi-level rate limiting middleware for FastAPI applications.
    
    Implements three levels of rate limiting in priority order:
    1. Global server limits (highest priority)
    2. Per IP address limits (medium priority)
    3. Per endpoint limits (most specific)
    
    All limits are configurable via environment variables and can be
    enabled/disabled globally.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._store = InMemoryRateLimitStore()
        self._enabled = settings.rate_limiting_enabled
        
        # Log rate limiting configuration on startup
        if self._enabled:
            logger.info("Rate limiting middleware initialized",
                       per_ip_limit=settings.rate_limit_per_ip,
                       story_generation_limit=settings.rate_limit_story_generation,
                       list_endpoints_limit=settings.rate_limit_list_endpoints,
                       health_status_limit=settings.rate_limit_health_status,
                       global_server_limit=settings.rate_limit_global_server,
                       storage_backend=settings.rate_limit_storage_backend,
                       time_window=settings.rate_limit_time_window)
        else:
            logger.info("Rate limiting middleware disabled")
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP address from request.
        
        Checks various headers in order of preference:
        1. X-Forwarded-For (proxy/load balancer)
        2. X-Real-IP (proxy)
        3. Direct client IP
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address as string
        """
        # Check proxy headers first
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first one
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _classify_endpoint(self, path: str) -> str:
        """
        Classify endpoint based on path to determine appropriate rate limits.
        
        Args:
            path: Request path (e.g., "/api/langchain")
            
        Returns:
            Endpoint classification string
        """
        # Story generation endpoints (most expensive)
        story_endpoints = ['/api/langchain', '/api/semantic-kernel', '/api/langgraph']
        if path in story_endpoints:
            return 'story_generation'
        
        # List and query endpoints (moderate cost)
        if (path.startswith('/api/stories') or 
            path.startswith('/api/cost') or
            path.startswith('/api/context')):
            return 'list_endpoints'
        
        # Health and status endpoints (lightweight)
        health_endpoints = ['/health', '/status', '/metrics', '/docs', '/openapi.json']
        if path in health_endpoints:
            return 'health_status'
        
        # Default classification
        return 'default'
    
    def _get_endpoint_limit(self, endpoint_type: str) -> int:
        """
        Get rate limit for a specific endpoint type.
        
        Args:
            endpoint_type: Endpoint classification from _classify_endpoint
            
        Returns:
            Rate limit (requests per minute) for the endpoint type
        """
        limits = {
            'story_generation': settings.rate_limit_story_generation,
            'list_endpoints': settings.rate_limit_list_endpoints,
            'health_status': settings.rate_limit_health_status,
            'default': settings.rate_limit_per_ip
        }
        return limits.get(endpoint_type, settings.rate_limit_per_ip)
    
    def _check_rate_limit(self, limit_type: str, identifier: str, limit: int) -> Tuple[bool, int, int]:
        """
        Check if a request should be rate limited.
        
        Args:
            limit_type: Type of limit being enforced
            identifier: Unique identifier for the limit
            limit: Maximum requests allowed in the time window
            
        Returns:
            Tuple of (is_allowed, current_count, remaining_requests)
        """
        current_count = self._store.get_count(limit_type, identifier)
        
        if current_count >= limit:
            return False, current_count, 0
        
        # Increment counter for this request
        new_count = self._store.increment(limit_type, identifier)
        remaining = max(0, limit - new_count)
        
        return True, new_count, remaining
    
    def _get_reset_timestamp(self) -> int:
        """
        Get Unix timestamp when current rate limit window resets.
        
        Returns:
            Unix timestamp of next minute boundary
        """
        current_time = int(time.time())
        return ((current_time // 60) + 1) * 60
    
    def _create_rate_limit_response(self, 
                                  request: Request,
                                  limit_type: str, 
                                  limit: int, 
                                  current_count: int) -> JSONResponse:
        """
        Create a 429 rate limit exceeded response with proper headers.
        
        Args:
            request: FastAPI request object
            limit_type: Type of limit that was exceeded
            limit: The rate limit that was exceeded
            current_count: Current request count in window
            
        Returns:
            JSONResponse with 429 status and rate limit headers
        """
        reset_timestamp = self._get_reset_timestamp()
        retry_after_seconds = reset_timestamp - int(time.time())
        
        response_data = {
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Try again in {retry_after_seconds} seconds.",
            "details": {
                "limit": limit,
                "current": current_count,
                "window": "1 minute",
                "reset_at": datetime.fromtimestamp(reset_timestamp, tz=timezone.utc).isoformat(),
                "limit_type": limit_type
            }
        }
        
        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_timestamp),
            "Retry-After": str(retry_after_seconds)
        }
        
        # Log rate limit violation
        transaction_guid = get_current_transaction_guid()
        client_ip = self._get_client_ip(request)
        
        logger.warning("Rate limit exceeded",
                      transaction_guid=transaction_guid,
                      client_ip=client_ip,
                      path=request.url.path,
                      method=request.method,
                      limit_type=limit_type,
                      limit=limit,
                      current_count=current_count,
                      retry_after_seconds=retry_after_seconds)
        
        return JSONResponse(
            status_code=settings.rate_limit_return_status_code,
            content=response_data,
            headers=headers
        )
    
    def _add_rate_limit_headers(self, response: Response, limit: int, remaining: int):
        """
        Add rate limit headers to successful responses.
        
        Args:
            response: Response object to modify
            limit: Rate limit for this request
            remaining: Remaining requests in current window
        """
        reset_timestamp = self._get_reset_timestamp()
        
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_timestamp)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request through multi-level rate limiting.
        
        Checks limits in priority order:
        1. Global server limit
        2. Per IP limit
        3. Per endpoint limit
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in the chain
            
        Returns:
            Response object, either rate limited (429) or from next handler
        """
        # Skip rate limiting if disabled
        if not self._enabled:
            return await call_next(request)
        
        client_ip = self._get_client_ip(request)
        path = request.url.path
        endpoint_type = self._classify_endpoint(path)
        transaction_guid = get_current_transaction_guid()
        
        # 1. Check global server limit (highest priority)
        global_allowed, global_count, global_remaining = self._check_rate_limit(
            "global", "server", settings.rate_limit_global_server
        )
        
        if not global_allowed:
            logger.warning("Global server rate limit exceeded",
                          transaction_guid=transaction_guid,
                          global_limit=settings.rate_limit_global_server,
                          current_count=global_count)
            return self._create_rate_limit_response(
                request, "global_server", settings.rate_limit_global_server, global_count
            )
        
        # 2. Check per IP limit (medium priority)
        ip_allowed, ip_count, ip_remaining = self._check_rate_limit(
            "ip", client_ip, settings.rate_limit_per_ip
        )
        
        if not ip_allowed:
            return self._create_rate_limit_response(
                request, "per_ip", settings.rate_limit_per_ip, ip_count
            )
        
        # 3. Check per endpoint limit (most specific)
        endpoint_limit = self._get_endpoint_limit(endpoint_type)
        endpoint_key = f"{client_ip}:{endpoint_type}"
        endpoint_allowed, endpoint_count, endpoint_remaining = self._check_rate_limit(
            "endpoint", endpoint_key, endpoint_limit
        )
        
        if not endpoint_allowed:
            return self._create_rate_limit_response(
                request, f"endpoint_{endpoint_type}", endpoint_limit, endpoint_count
            )
        
        # Request is allowed, process it
        response = await call_next(request)
        
        # Add rate limit headers (use the most restrictive remaining count)
        most_restrictive_remaining = min(global_remaining, ip_remaining, endpoint_remaining)
        most_restrictive_limit = min(
            settings.rate_limit_global_server, 
            settings.rate_limit_per_ip, 
            endpoint_limit
        )
        
        self._add_rate_limit_headers(response, most_restrictive_limit, most_restrictive_remaining)
        
        # Log successful request with rate limit info
        logger.debug("Request processed with rate limiting",
                    transaction_guid=transaction_guid,
                    client_ip=client_ip,
                    path=path,
                    method=request.method,
                    endpoint_type=endpoint_type,
                    global_remaining=global_remaining,
                    ip_remaining=ip_remaining,
                    endpoint_remaining=endpoint_remaining)
        
        return response

def get_rate_limit_stats() -> Dict[str, any]:
    """
    Get current rate limiting configuration for monitoring/debugging.
    
    Returns:
        Dictionary containing rate limiting configuration and status
    """
    return {
        "enabled": settings.rate_limiting_enabled,
        "limits": {
            "per_ip": settings.rate_limit_per_ip,
            "story_generation": settings.rate_limit_story_generation,
            "list_endpoints": settings.rate_limit_list_endpoints,
            "health_status": settings.rate_limit_health_status,
            "global_server": settings.rate_limit_global_server
        },
        "config": {
            "storage_backend": settings.rate_limit_storage_backend,
            "time_window": settings.rate_limit_time_window,
            "return_status_code": settings.rate_limit_return_status_code
        }
    }

# Initialize with configuration logging
logger.info("Rate limiting module loaded", **get_rate_limit_stats())