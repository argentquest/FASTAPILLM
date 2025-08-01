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

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from logging_config import configure_logging, get_logger
from routes.story_routes import router as story_router
from routes.chat_routes import router as chat_router
from routes.log_routes import router as log_router
from routes.cost_routes import router as cost_router
try:
    from routes.context_routes import router as context_router
    print("✅ Full context routes loaded successfully")
except Exception as e:
    print(f"❌ Error loading full context routes: {e}")
    try:
        from routes.context_routes_simple import router as context_router
        print("✅ Using simplified context routes")
    except:
        # Create a dummy router if both fail
        from fastapi import APIRouter
        context_router = APIRouter(prefix="/api/context", tags=["context"])
        print("⚠️ Using dummy context router")
from middleware import LoggingMiddleware, ErrorHandlingMiddleware
from database import init_db

# Import MCP components
try:
    from fastmcp import FastMCP
    from pydantic import Field
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("⚠️  FastMCP not available. MCP features disabled.")

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

# MCP Server Setup
if MCP_AVAILABLE:
    # Import story services for MCP tools
    from services.story_services import (
        SemanticKernelService,
        LangChainService,
        LangGraphService
    )
    
    # Create FastMCP instance
    mcp = FastMCP("AI Story Generator MCP Server")
    
    @mcp.tool()
    async def generate_story_semantic_kernel(
        primary_character: str,
        secondary_character: str
    ) -> Dict[str, Any]:
        """Generate a story using Semantic Kernel framework."""
        logger.info("MCP: Generating story with Semantic Kernel",
                        primary=primary_character,
                        secondary=secondary_character)
        
        try:
            # Create service instance
            service = SemanticKernelService()
            
            # Generate story and usage info
            result, usage_info = await service.generate_story(
                primary_character=primary_character,
                secondary_character=secondary_character
            )
            
            # Return structured response
            return {
                "id": None,  # Will be assigned when saved to DB
                "story": result,
                "primary_character": primary_character,
                "secondary_character": secondary_character,
                "framework": "semantic_kernel",
                "model": usage_info.get("model", "unknown"),
                "total_tokens": usage_info.get("total_tokens", 0),
                "estimated_cost_usd": usage_info.get("estimated_cost_usd", 0),
                "generation_time_ms": usage_info.get("execution_time_ms", 0)
            }
            
        except Exception as e:
            logger.error("MCP: Error generating story with Semantic Kernel",
                        error=str(e),
                        error_type=type(e).__name__)
            raise Exception(f"Story generation failed: {str(e)}")

    @mcp.tool()
    async def generate_story_langchain(
        primary_character: str,
        secondary_character: str
    ) -> Dict[str, Any]:
        """Generate a story using LangChain framework."""
        logger.info("MCP: Generating story with LangChain",
                    primary=primary_character,
                    secondary=secondary_character)
        
        try:
            # Create service instance
            service = LangChainService()
            
            # Generate story and usage info
            result, usage_info = await service.generate_story(
                primary_character=primary_character,
                secondary_character=secondary_character
            )
            
            # Return structured response
            return {
                "id": None,
                "story": result,
                "primary_character": primary_character,
                "secondary_character": secondary_character,
                "framework": "langchain",
                "model": usage_info.get("model", "unknown"),
                "total_tokens": usage_info.get("total_tokens", 0),
                "estimated_cost_usd": usage_info.get("estimated_cost_usd", 0),
                "generation_time_ms": usage_info.get("execution_time_ms", 0)
            }
            
        except Exception as e:
            logger.error("MCP: Error generating story with LangChain",
                        error=str(e),
                        error_type=type(e).__name__)
            raise Exception(f"Story generation failed: {str(e)}")

    @mcp.tool()
    async def generate_story_langgraph(
        primary_character: str,
        secondary_character: str
    ) -> Dict[str, Any]:
        """Generate a story using LangGraph framework with advanced editing."""
        logger.info("MCP: Generating story with LangGraph",
                    primary=primary_character,
                    secondary=secondary_character)
        
        try:
            # Create service instance
            service = LangGraphService()
            
            # Generate story and usage info
            result, usage_info = await service.generate_story(
                primary_character=primary_character,
                secondary_character=secondary_character
            )
            
            # Return structured response
            return {
                "id": None,
                "story": result,
                "primary_character": primary_character,
                "secondary_character": secondary_character,
                "framework": "langgraph",
                "model": usage_info.get("model", "unknown"),
                "total_tokens": usage_info.get("total_tokens", 0),
                "estimated_cost_usd": usage_info.get("estimated_cost_usd", 0),
                "generation_time_ms": usage_info.get("execution_time_ms", 0)
            }
            
        except Exception as e:
            logger.error("MCP: Error generating story with LangGraph",
                        error=str(e),
                        error_type=type(e).__name__)
            raise Exception(f"Story generation failed: {str(e)}")


    # Optional: Add a resource to list recent stories
    @mcp.resource("stories/recent/{limit}")
    async def get_recent_stories(limit: int = 10) -> Dict[str, Any]:
        """Get recent generated stories."""
        # This would need database access
        # For now, return a placeholder
        return {
            "stories": [],
            "message": "Database integration pending",
            "limit": limit
        }

    def get_mcp_server():
        """Get the configured MCP server instance."""
        return mcp
else:
    # Define dummy function if MCP not available
    def get_mcp_server():
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("Starting AI Testing Suite - Backend API", 
                version=settings.app_version,
                environment="development" if settings.debug_mode else "production",
                mcp_enabled=MCP_AVAILABLE)
    
    # Initialize database
    init_db()
    
    # MCP server initialization happens during module load
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Testing Suite - Backend API")

# Create FastAPI app
app = FastAPI(
    title=f"{settings.app_name} - Backend API",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS - Allow all origins in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Add middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost", "backend"] if settings.debug_mode else ["*"]
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
app.include_router(cost_router)
app.include_router(context_router)

# Setup MCP server on separate port
if MCP_AVAILABLE:
    import threading
    import asyncio
    
    def run_mcp_server():
        """Run MCP server on port 9999 like before"""
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Get the MCP server instance
            mcp_server = get_mcp_server()
            
            # Run FastMCP's HTTP server
            # This is similar to what we had in run_standalone_mcp_server
            import uvicorn
            
            # Check if FastMCP has an http_app attribute (like before)
            if hasattr(mcp_server, 'http_app'):
                logger.info("MCP: Starting server on port 9999 using http_app")
                uvicorn.run(
                    mcp_server.http_app,
                    host="0.0.0.0",
                    port=9999,
                    log_level="info"
                )
            elif hasattr(mcp_server, 'run_http_async'):
                logger.info("MCP: Starting server on port 9999 using run_http_async")
                loop.run_until_complete(mcp_server.run_http_async(host="0.0.0.0", port=9999))
            else:
                logger.error("MCP: No suitable method found for running MCP server")
                
        except Exception as e:
            logger.error("MCP: Failed to start MCP server", error=str(e), error_type=type(e).__name__)
    
    # Start MCP server in separate thread
    mcp_thread = threading.Thread(
        target=run_mcp_server, 
        daemon=True,
        name="MCPServerThread"
    )
    mcp_thread.start()
    logger.info("MCP: Server thread started on port 9999")
    
    # Update the test script to use port 9999
    logger.info("MCP: To test, connect to http://localhost:9999/mcp")
else:
    logger.warning("MCP: FastMCP not available - install with: pip install fastmcp")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - API only backend with helpful links"""
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
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.app_version,
        "request_id": getattr(request.state, 'request_id', None),
        "environment": "development" if settings.debug_mode else "production"
    }

@app.get("/api/provider")
async def get_provider_info(request: Request) -> Dict[str, Any]:
    """Get current LLM provider information"""
    logger.info("Provider info requested",
                request_id=getattr(request.state, 'request_id', None))
    
    provider_name = settings.provider_name or "Not configured"
    provider_model = settings.provider_model or "Not configured"
    
    return {
        "provider": provider_name,
        "model": provider_model,
        "configured": bool(settings.provider_api_key and settings.provider_api_base_url)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug_mode,
        log_config=None  # Use our custom logging
    )