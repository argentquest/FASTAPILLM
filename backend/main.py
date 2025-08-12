from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, HTMLResponse, Response
from contextlib import asynccontextmanager
import time
from typing import Dict, Any
import sys
import os
import platform
from datetime import datetime

# Ensure backend directory is in path for all imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Also add parent directory for imports like simple_rate_limiting
parent_dir = os.path.dirname(backend_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Now import with confidence
from config import settings
from logging_config import configure_logging, get_logger

# Force colored output in development
if settings.debug_mode:
    os.environ['FORCE_COLOR'] = '1'

# Configure logging
configure_logging(
    debug=settings.debug_mode,
    log_file_path=settings.log_file_path,
    log_level=settings.log_level,
    rotation_hours=settings.log_rotation_hours,
    retention_days=settings.log_retention_days
)
logger = get_logger(__name__)

# Log application initialization
logger.info("FastAPI application initializing",
            python_version=sys.version,
            platform=platform.platform(),
            pid=os.getpid(),
            working_dir=os.getcwd())
from routes.story_routes import router as story_router
from routes.chat_routes import router as chat_router
from routes.log_routes import router as log_router
from routes.cost_routes import router as cost_router
try:
    from routes.context_routes import router as context_router
    logger.info("Full context routes loaded successfully")
except Exception as e:
    logger.error(f"Error loading full context routes: {e}")
    try:
        from routes.context_routes_simple import router as context_router
        logger.info("Using simplified context routes")
    except:
        # Create a dummy router if both fail
        from fastapi import APIRouter
        context_router = APIRouter(prefix="/api/context", tags=["context"])
        logger.warning("Using dummy context router")
from middleware import LoggingMiddleware, ErrorHandlingMiddleware
from database import init_db

# Import rate limiting middleware (from parent directory - already added to path above)
# Temporarily use simple middleware for testing
from simple_rate_limiting import SimpleRateLimitingMiddleware as RateLimitingMiddleware


@asynccontextmanager
async def base_lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    startup_time = time.time()
    startup_id = f"startup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Startup
    logger.info("Starting AI Testing Suite - Backend API",
                startup_id=startup_id,
                version=settings.app_version,
                environment="development" if settings.debug_mode else "production",
                debug_mode=settings.debug_mode,
                log_level=settings.log_level,
                provider=settings.provider_name,
                model=settings.provider_model)
    
    # Log configuration details
    logger.debug("Application configuration",
                startup_id=startup_id,
                cors_enabled=True,
                api_docs_url="/api/docs",
                api_redoc_url="/api/redoc",
                api_timeout=settings.api_timeout,
                openai_timeout=settings.openai_timeout)
    
    # Initialize database
    try:
        logger.info("Initializing database", startup_id=startup_id)
        init_db()
        logger.info("Database initialized successfully", startup_id=startup_id)
    except Exception as e:
        logger.error("Database initialization failed",
                    startup_id=startup_id,
                    error=str(e),
                    error_type=type(e).__name__)
        raise
    
    startup_elapsed = (time.time() - startup_time) * 1000
    logger.info("Application startup complete",
                startup_id=startup_id,
                startup_time_ms=startup_elapsed)
    
    # Store startup time for health checks
    app.state.startup_time = startup_time
    
    yield
    
    # Shutdown
    shutdown_time = time.time()
    shutdown_id = f"shutdown_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    logger.info("Shutting down AI Testing Suite - Backend API",
                shutdown_id=shutdown_id,
                uptime_seconds=int(time.time() - startup_time))

# Create FastAPI app
app = FastAPI(
    title=f"{settings.app_name} - Backend API",
    version=settings.app_version,
    lifespan=base_lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

logger.info("FastAPI app created",
            app_name=settings.app_name,
            app_version=settings.app_version,
            openapi_url=app.openapi_url,
            docs_url=app.docs_url,
            redoc_url=app.redoc_url)

# Configure CORS - Allow all origins in development
cors_config = {
    "allow_origins": ["*"],  # Allow all origins
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["*"],
    "max_age": 3600,
}

app.add_middleware(CORSMiddleware, **cors_config)

logger.info("CORS middleware configured",
            allow_origins=cors_config["allow_origins"],
            allow_credentials=cors_config["allow_credentials"],
            max_age=cors_config["max_age"])

# Add middleware (order matters - last added is executed first)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitingMiddleware)

logger.info("Custom middleware added",
            middlewares=["ErrorHandlingMiddleware", "LoggingMiddleware", "RateLimitingMiddleware"])

# Add trusted host middleware for security
allowed_hosts = ["localhost", "127.0.0.1", "*.localhost", "backend"] if settings.debug_mode else ["*"]
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts
)

logger.info("TrustedHost middleware configured",
            allowed_hosts=allowed_hosts,
            debug_mode=settings.debug_mode)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed logging"""
    errors = exc.errors()
    error_id = f"val_err_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(errors)) % 10000}"
    
    # Log validation error details
    logger.error("Validation error",
                error_id=error_id,
                request_id=getattr(request.state, 'request_id', None),
                path=request.url.path,
                method=request.method,
                client_host=request.client.host if request.client else None,
                error_count=len(errors),
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
    
    response_content = {
        "error": {
            "type": "ValidationError",
            "message": "Request validation failed",
            "error_id": error_id,
            "details": formatted_errors
        }
    }
    
    logger.debug("Validation error response sent",
                error_id=error_id,
                status_code=422,
                error_fields=[err["field"] for err in formatted_errors])
    
    return JSONResponse(
        status_code=422,
        content=response_content
    )

# Include routers
routers = [
    ("story", story_router),
    ("chat", chat_router),
    ("log", log_router),
    ("cost", cost_router),
    ("context", context_router)
]

for router_name, router in routers:
    app.include_router(router)
    logger.debug(f"Router included: {router_name}",
                router_name=router_name,
                prefix=getattr(router, "prefix", "none"),
                tags=getattr(router, "tags", []))

logger.info("All routers included",
            router_count=len(routers),
            routers=[name for name, _ in routers])

@app.get("/api/mcp-status")
async def mcp_status(request: Request):
    """Check MCP server status"""
    request_id = getattr(request.state, 'request_id', None)
    
    logger.info("MCP status check requested",
                request_id=request_id,
                client_host=request.client.host if request.client else None)
    
    status_info = {
        "mcp_available": False,
        "mcp_server_info": "MCP server runs separately. Use: python backend/mcp_server.py",
        "message": "MCP server is now a standalone service following FastMCP best practices",
        "standalone_command": "python backend/mcp_server.py",
        "fastmcp_cli_command": "fastmcp run backend/mcp_server.py:mcp"
    }
    
    logger.debug("MCP status returned",
                request_id=request_id,
                mcp_available=status_info["mcp_available"],
                mode="standalone")
    
    return status_info

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - API only backend with helpful links"""
    request_id = getattr(request.state, 'request_id', None)
    
    logger.debug("Root endpoint accessed",
                request_id=request_id,
                client_host=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent", "unknown"))
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Story Generator - Backend API</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
            .header {{ text-align: center; color: #333; }}
            .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 20px 0; }}
            .btn {{ display: inline-block; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; margin: 5px; }}
            .btn:hover {{ background: #0056b3; }}
            .status {{ color: #28a745; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚀 AI Story Generator</h1>
            <h2>Backend API Server</h2>
            <p class="status">✅ API Server Running</p>
            <p>Version: {settings.app_version}</p>
        </div>
        
        <div class="card">
            <h3>📖 API Documentation</h3>
            <p>Explore the API endpoints and test them directly:</p>
            <a href="/api/docs" class="btn">Interactive API Docs (Swagger)</a>
            <a href="/api/redoc" class="btn">API Documentation (ReDoc)</a>
        </div>
        
        <div class="card">
            <h3>🌐 Frontend Applications</h3>
            <p>Choose your preferred frontend interface:</p>
            <a href="http://localhost:3001" class="btn">React Frontend</a>
            <p><small>Note: Frontend servers must be started separately</small></p>
        </div>
        
        <div class="card">
            <h3>🔧 Quick Start</h3>
            <p>To run the complete application:</p>
            <ol>
                <li><strong>React Frontend:</strong> <code>cd frontendReact && npm install && npm run dev</code></li>
            </ol>
        </div>
        
        <div class="card">
            <h3>🔗 Direct API Access</h3>
            <p>Some useful API endpoints:</p>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/api/provider">Provider Info</a></li>
                <li>POST /api/semantic-kernel - Generate story with Semantic Kernel</li>
                <li>POST /api/langchain - Generate story with LangChain</li>
                <li>POST /api/langgraph - Generate story with LangGraph</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/favicon.ico")
async def favicon():
    """Simple favicon response to avoid 404"""
    # Return a minimal SVG favicon
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#007bff">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
    </svg>"""
    return Response(content=svg_content, media_type="image/svg+xml")

@app.get("/health")
async def health_check(request: Request) -> Dict[str, Any]:
    """Health check endpoint"""
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.app_version,
        "request_id": getattr(request.state, 'request_id', None),
        "environment": "development" if settings.debug_mode else "production",
        "uptime_seconds": int(time.time() - app.state.startup_time) if hasattr(app.state, 'startup_time') else 0
    }
    
    logger.debug("Health check requested",
                request_id=health_data["request_id"],
                client_host=request.client.host if request.client else None,
                status=health_data["status"])
    
    return health_data

@app.get("/api/provider")
async def get_provider_info(request: Request) -> Dict[str, Any]:
    """Get current LLM provider information"""
    request_id = getattr(request.state, 'request_id', None)
    
    logger.info("Provider info requested",
                request_id=request_id,
                client_host=request.client.host if request.client else None)
    
    provider_name = settings.provider_name or "Not configured"
    provider_model = settings.provider_model or "Not configured"
    is_configured = bool(settings.provider_api_key and settings.provider_api_base_url)
    
    provider_info = {
        "provider": provider_name,
        "model": provider_model,
        "configured": is_configured
    }
    
    logger.debug("Provider info returned",
                request_id=request_id,
                provider=provider_name,
                model=provider_model,
                configured=is_configured)
    
    return provider_info

if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Uvicorn server",
                host="0.0.0.0",
                port=8000,
                reload=settings.debug_mode,
                workers=1)
    
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.debug_mode,
            log_config=None  # Use our custom logging
        )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested via keyboard interrupt")
    except Exception as e:
        logger.error("Server crashed",
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True)
        raise
    finally:
        logger.info("Server shutdown complete")