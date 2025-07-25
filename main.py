from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from typing import Dict, Any

from config import settings
from logging_config import configure_logging, get_logger
from routes.story_routes import router as story_router
from routes.chat_routes import router as chat_router
from routes.log_routes import router as log_router
from middleware import LoggingMiddleware, ErrorHandlingMiddleware
from database import init_db

# Configure logging
configure_logging(
    debug=settings.debug_mode,
    log_file_path=settings.log_file_path,
    log_level=settings.log_level,
    rotation_hours=settings.log_rotation_hours,
    retention_days=settings.log_retention_days
)
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("Starting AI Story Generator", 
                version=settings.app_version,
                environment="development" if settings.debug_mode else "production")
    
    # Initialize database
    init_db()
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Story Generator")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs" if settings.debug_mode else None,
    redoc_url="/api/redoc" if settings.debug_mode else None,
)


# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
    max_age=3600,
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"] if settings.debug_mode else ["*"]
)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging"""
    errors = exc.errors()
    
    # Log validation error details
    logger.error("Validation error",
                request_id=getattr(request.state, 'request_id', None),
                path=request.url.path,
                method=request.method,
                errors=errors,
                body=exc.body if hasattr(exc, 'body') else None)
    
    # Format error response
    formatted_errors = []
    for error in errors:
        formatted_errors.append({
            "field": " -> ".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", "Unknown error"),
            "type": error.get("type", "unknown"),
            "input": error.get("input", None)
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "type": "ValidationError",
                "message": "Request validation failed",
                "details": formatted_errors
            }
        }
    )

# Include routers
app.include_router(story_router)
app.include_router(chat_router)
app.include_router(log_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

@app.get("/debug")
async def read_debug():
    """Debug interface for testing API endpoints"""
    return FileResponse('static/debug.html')

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": time.time()
    }

@app.get("/api/provider")
async def get_provider_info() -> Dict[str, Any]:
    """Get information about the configured LLM provider"""
    provider_info = {
        "provider": settings.llm_provider
    }
    
    if settings.llm_provider == "azure":
        provider_info.update({
            "model": settings.azure_openai_deployment_name,
            "endpoint": settings.azure_openai_endpoint.split('.')[0] + ".***" if settings.azure_openai_endpoint else None
        })
    elif settings.llm_provider == "openrouter":
        provider_info.update({
            "model": settings.openrouter_model,
            "available_models": ["openai/gpt-4-turbo-preview", "anthropic/claude-3-opus", "google/gemini-pro", "mistralai/mixtral-8x7b-instruct"]
        })
    else:  # custom
        provider_info.update({
            "provider_name": settings.custom_provider_name,
            "model": settings.custom_model,
            "api_type": settings.custom_api_type,
            "base_url": settings.custom_api_base_url.split('/')[2] if settings.custom_api_base_url else None
        })
    
    return provider_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug_mode,
        log_config=None  # We're using structlog
    )