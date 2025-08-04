# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FASTAPILLM is a FastAPI-based AI content generation platform that supports multiple AI frameworks (Semantic Kernel, LangChain, LangGraph) and providers (Azure OpenAI, OpenRouter, custom OpenAI-compatible APIs).

**Recent Major Updates:**
- ✅ **Standalone MCP Server**: Refactored to follow FastMCP best practices
- ✅ **Enhanced Logging**: Comprehensive request tracking and performance metrics
- ✅ **VS Code Integration**: Full debugging support for both FastAPI and MCP servers
- ✅ **MCP Object Extraction**: Complete tool and structure analysis capabilities

## Essential Commands

```bash
# Development
python backend/main.py            # Run the FastAPI application locally
python backend/mcp_server.py      # Run the standalone MCP server
pip install -r requirements.txt   # Install dependencies

# MCP Server (FastMCP CLI)
fastmcp run backend.mcp_server:mcp  # Run MCP server with FastMCP CLI

# Testing
pytest                           # Run all tests
python backend/test_mcp_client.py      # Enhanced MCP object extraction
python test_mcp_working.py             # Basic MCP functionality test
python test_enhanced_logging.py        # Logging system verification

# Docker
docker-compose up --build        # Build and run with Docker
docker build -t ai-story-generator .  # Manual Docker build

# Database Migrations
alembic upgrade head             # Apply database migrations
alembic revision --autogenerate -m "description"  # Create new migration

# VS Code Debugging
# Use "Backend + MCP Server" compound configuration to debug both services
```

## Architecture

### Service Layer Structure
The application uses a multi-framework approach with parallel implementations:
- `/services/chat_services/` - Chat implementations for each framework
- `/services/story_services/` - Story generation implementations for each framework
- Each service follows the pattern: `{framework}_service.py` (e.g., `langchain_service.py`)

### Routing Pattern
Routes are organized by feature in `/routes/`:
- `story_routes.py` - Story generation endpoints
- `chat_routes.py` - Chat endpoints
- `logging_routes.py` - Logging viewer endpoints
- `cost_routes.py` - Cost tracking endpoints

### External Prompts
Prompts are externalized in `/prompts/{framework}/` directories as text files, loaded dynamically by services.

### Database
- SQLAlchemy ORM with Alembic migrations
- Models defined inline within service files
- PostgreSQL in production, SQLite for development

### MCP Server Integration
**Standalone MCP Server** (`backend/mcp_server.py`):
- Follows FastMCP best practices from https://gofastmcp.com
- Uses `@mcp.tool` decorators for tool registration
- Runs independently from the main FastAPI application
- Supports both direct execution and FastMCP CLI
- Comprehensive logging with request tracking

**Available MCP Tools:**
- `generate_story_semantic_kernel` - Microsoft Semantic Kernel stories
- `generate_story_langchain` - LangChain framework stories
- `generate_story_langgraph` - LangGraph with advanced editing
- `list_frameworks` - List all available AI frameworks

**Testing & Extraction:**
- `test_mcp_client.py` - Enhanced MCP object extraction and analysis
- `test_mcp_working.py` - Basic MCP functionality testing
- Exports complete MCP structure to `mcp_objects_extracted.json`

### Configuration
Environment variables are used extensively. Key variables:
- `AZURE_OPENAI_KEY`, `AZURE_OPENAI_ENDPOINT` - Azure OpenAI settings
- `OPENROUTER_API_KEY` - OpenRouter API key
- `LANGSMITH_API_KEY` - LangSmith tracing
- `DATABASE_URL` - Database connection string

## Development Patterns

### Adding New AI Framework
1. Create service files in `/services/chat_services/` and `/services/story_services/`
2. Add corresponding routes in `/routes/`
3. Create prompt directory in `/prompts/{framework}/`
4. Update schemas in `/schemas/` if needed
5. Add MCP tool in `backend/mcp_server.py` with `@mcp.tool` decorator

### Enhanced Logging System
**Both FastAPI and MCP servers feature comprehensive logging:**
- **Request Tracking**: Unique request IDs for tracing (e.g., `lc_20250804_121706_1124`)
- **Performance Metrics**: Timing information for all operations
- **Error Tracking**: Detailed error logging with context and traceback
- **Structured Fields**: Consistent logging format with structured data
- **Cost Tracking**: Token usage and estimated costs per request

**Log Files:**
- `logs/app.log` - Main application log with rotation
- Console output with colored formatting in development

### Error Handling
- All services use comprehensive try-catch blocks
- Errors are logged with full context and unique error IDs
- HTTP exceptions are raised with appropriate status codes
- MCP tools include error tracking with request correlation

### Testing
- Use pytest for all tests
- Mock external API calls
- Test files should mirror the source structure
- **MCP Testing**: Use `test_mcp_client.py` for complete MCP analysis
- **Logging Testing**: Use `test_enhanced_logging.py` for logging verification

### VS Code Integration
**Debug Configurations** (`.vscode/launch.json`):
- **Individual**: Debug FastAPI or MCP server separately
- **Compound**: "Backend + MCP Server" runs both simultaneously
- **Enhanced Testing**: Dedicated configs for all test scripts

**Tasks** (`.vscode/tasks.json`):
- **Run Backend + MCP**: Parallel execution of both servers
- **Kill Python Processes**: Clean shutdown helper
- **Individual Tasks**: Run each service independently

## Workspace Considerations
- Remember you are running in WSL while we are running in Windows
- Use VS Code compound configurations for full-stack debugging
- Both servers can be debugged simultaneously with breakpoints