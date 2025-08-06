# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FASTAPILLM is a FastAPI-based AI content generation platform that supports multiple AI frameworks (Semantic Kernel, LangChain, LangGraph) and providers (Azure OpenAI, OpenRouter, custom OpenAI-compatible APIs).

**Recent Major Updates:**
- ✅ **Standalone MCP Server**: Refactored to follow FastMCP best practices
- ✅ **Enhanced Logging**: Comprehensive request tracking and performance metrics
- ✅ **VS Code Integration**: Full debugging support for both FastAPI and MCP servers
- ✅ **MCP Object Extraction**: Complete tool and structure analysis capabilities
- ✅ **Custom Provider Support**: Extended configuration system for custom providers
- ✅ **Header Factory**: Dynamic header generation based on provider type
- ✅ **Async Service Layer**: Fully async-compatible base service implementation

## Essential Commands

```bash
# Development
python backend/main.py            # Run the FastAPI application locally
python backend/mcp_server.py      # Run the standalone MCP server
pip install -r requirements.txt   # Install dependencies

# MCP Server (FastMCP CLI)
fastmcp run backend.mcp_server:mcp  # Run MCP server with FastMCP CLI

# Testing (All tests now in test/ directory)
pytest                               # Run all tests
python test/test_mcp_client.py       # Enhanced MCP object extraction
python test/test_mcp_working.py      # Basic MCP functionality test
python test/test_enhanced_logging.py # Logging system verification
python test/test_retry_functionality.py # Retry mechanism testing
python test/test_rate_limiting.py    # Rate limiting functionality

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

**Available MCP Components:**

**Tools (4):**
- `generate_story_semantic_kernel` - Microsoft Semantic Kernel stories
- `generate_story_langchain` - LangChain framework stories
- `generate_story_langgraph` - LangGraph with advanced editing
- `list_frameworks` - List all available AI frameworks

**Resources (2):**
- `data://config` - Server configuration and version information
- `stories/recent/{limit}` - Recent generated stories (pending DB integration)

**Prompts (6):**
- `classic_adventure_story` - Adventure story prompts with customizable settings
- `mystery_story` - Mystery/detective story prompts
- `sci_fi_story` - Science fiction story prompts
- `fantasy_quest_story` - Fantasy quest story prompts
- `comedy_story` - Humorous story prompts
- `story_prompt_list` - List of creative story ideas

**Testing & Extraction:**
- `test/test_mcp_client.py` - Enhanced MCP object extraction and analysis
- `test/test_mcp_working.py` - Basic MCP functionality testing
- Exports complete MCP structure to `mcp_objects_extracted.json`

### Configuration
Environment variables are used extensively. Key variables:
- `PROVIDER_NAME` - Provider type ('openai' or 'custom')
- `PROVIDER_API_KEY` - API key for the provider
- `PROVIDER_API_BASE_URL` - Base URL for API calls
- `PROVIDER_MODEL` - Model identifier
- `PROVIDER_HEADERS` - Optional JSON headers
- `DATABASE_URL` - Database connection string

**Custom Provider Settings** (when `PROVIDER_NAME=custom`):
- `CUSTOM_AUTH_TOKEN`, `CUSTOM_API_SECRET` - Authentication tokens
- `CUSTOM_CLIENT_ID`, `CUSTOM_CLIENT_SECRET` - OAuth credentials
- `CUSTOM_TENANT_ID` - Tenant identifier
- `CUSTOM_ENVIRONMENT` - Environment name (production, staging)
- `CUSTOM_API_VERSION` - API version
- `CUSTOM_VAR` - Custom string variable for provider-specific data
- `CUSTOM_USE_OAUTH` - Enable OAuth authentication
- `CUSTOM_EXTRA_HEADERS` - Additional headers as JSON
- `CUSTOM_MODEL_MAPPING` - Model name mapping as JSON
- See `custom_settings.py` and `.env.example` for full list

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