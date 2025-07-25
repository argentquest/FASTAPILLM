from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
import uuid
from typing import Callable
import json

from logging_config import get_logger
from exceptions import Error

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses.
    
    This middleware intercepts all HTTP requests and responses to provide
    comprehensive logging including:
    - Request details (method, path, body for POST requests)
    - Response status and duration
    - Error details for failed requests
    - Request IDs for tracing
    
    Each request is assigned a unique ID that is included in all related
    log entries and returned in the X-Request-ID response header.
    
    Examples:
        >>> app = FastAPI()
        >>> app.add_middleware(LoggingMiddleware)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process and log HTTP requests and responses.
        
        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or endpoint handler.
            
        Returns:
            The HTTP response with added X-Request-ID header.
            
        Raises:
            Any exceptions from the application are passed through.
        """
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Get request body for POST requests
        request_body = None
        if request.method == "POST":
            try:
                body = await request.body()
                request_body = body.decode() if body else None
                # Need to recreate the request with the body since we consumed it
                from starlette.datastructures import Headers
                from starlette.requests import Request as StarletteRequest
                
                async def receive():
                    return {"type": "http.request", "body": body}
                
                request = StarletteRequest(request.scope, receive)
                request.state.request_id = request_id
            except Exception as e:
                logger.error("Failed to read request body", error=str(e))
        
        # Log request
        start_time = time.time()
        logger.info("Request started",
                   request_id=request_id,
                   method=request.method,
                   path=request.url.path,
                   client_host=request.client.host if request.client else None,
                   request_body=request_body)
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000
        
        # Log response with error details for 4xx/5xx status codes
        log_data = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2)
        }
        
        # For error responses, try to get the response body
        if response.status_code >= 400:
            try:
                # Store the body to log it
                body_bytes = b""
                async for chunk in response.body_iterator:
                    body_bytes += chunk
                
                # Try to parse as JSON
                try:
                    error_body = json.loads(body_bytes.decode())
                    log_data["error_response"] = error_body
                except:
                    log_data["error_response"] = body_bytes.decode()
                
                # Create a new response with the same body
                response = Response(
                    content=body_bytes,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type=response.media_type
                )
                
                logger.error("Request failed", **log_data)
            except Exception as e:
                logger.error("Failed to log error response", error=str(e), **log_data)
        else:
            logger.info("Request completed", **log_data)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling exceptions.
    
    This middleware catches all exceptions thrown by the application and
    converts them to appropriate JSON error responses. It handles:
    - Custom Error exceptions with specific error codes
    - Unexpected exceptions with generic error responses
    
    All errors are logged with appropriate severity levels.
    
    Examples:
        >>> app = FastAPI()
        >>> app.add_middleware(ErrorHandlingMiddleware)
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle exceptions and convert them to JSON responses.
        
        Args:
            request: The incoming HTTP request.
            call_next: The next middleware or endpoint handler.
            
        Returns:
            Either the normal response or a JSON error response if an
            exception occurred.
            
        Examples:
            Normal response:
            >>> {"result": "success"}
            
            Custom error response:
            >>> {
            ...   "error": {
            ...     "type": "ValidationError",
            ...     "message": "Invalid input",
            ...     "code": "VALIDATION_ERROR"
            ...   }
            ... }
            
            Unexpected error response:
            >>> {
            ...   "error": {
            ...     "type": "InternalServerError",
            ...     "message": "An unexpected error occurred",
            ...     "code": "INTERNAL_ERROR"
            ...   }
            ... }
        """
        try:
            response = await call_next(request)
            return response
        except Error as e:
            # Handle custom exceptions
            logger.warning("Application error",
                          error_type=type(e).__name__,
                          error_message=str(e),
                          error_code=getattr(e, 'error_code', None),
                          request_id=getattr(request.state, 'request_id', None))
            
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "type": type(e).__name__,
                        "message": str(e),
                        "code": getattr(e, 'error_code', None)
                    }
                }
            )
        except Exception as e:
            # Handle unexpected exceptions
            logger.error("Unexpected error",
                        error_type=type(e).__name__,
                        error_message=str(e),
                        request_id=getattr(request.state, 'request_id', None),
                        exc_info=True)
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "type": "InternalServerError",
                        "message": "An unexpected error occurred",
                        "code": "INTERNAL_ERROR"
                    }
                }
            )