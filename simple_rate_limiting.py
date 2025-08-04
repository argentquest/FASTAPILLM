"""
Simple Rate Limiting Middleware for Debug Testing
"""

import time
from typing import Dict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class SimpleRateLimitingMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware for testing."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._requests: Dict[str, list] = {}
        self._limit = 10  # 10 requests per minute for testing
        print("SimpleRateLimitingMiddleware initialized")
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client is rate limited."""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old requests
        if client_ip in self._requests:
            self._requests[client_ip] = [t for t in self._requests[client_ip] if t > minute_ago]
        else:
            self._requests[client_ip] = []
        
        # Check if limit exceeded
        if len(self._requests[client_ip]) >= self._limit:
            return True
        
        # Add current request
        self._requests[client_ip].append(now)
        return False
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        print(f"SimpleRateLimitingMiddleware: Processing {request.method} {request.url.path}")
        
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if self._is_rate_limited(client_ip):
            print(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"},
                headers={
                    "X-RateLimit-Limit": str(self._limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60"
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        current_count = len(self._requests.get(client_ip, []))
        remaining = max(0, self._limit - current_count)
        
        response.headers["X-RateLimit-Limit"] = str(self._limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        print(f"SimpleRateLimitingMiddleware: Request processed - Remaining: {remaining}")
        
        return response