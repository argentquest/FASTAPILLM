# FASTAPILLM - AI Content Generation Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![MCP Server](https://img.shields.io/badge/MCP-Server-blue.svg)](https://modelcontextprotocol.io)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)

A modern, enterprise-grade AI content generation platform featuring multi-framework support, MCP (Model Context Protocol) integration, comprehensive cost tracking, and full-stack web interface. Built with FastAPI, React, and designed for production deployment.

## 🚀 Features

### Core Capabilities
- **Multi-Framework AI Generation**: Three distinct AI frameworks for different use cases
  - **Semantic Kernel**: User-friendly, encouraging content creation
  - **LangChain**: Structured, analytical text processing
  - **LangGraph**: Complex multi-step workflows with iterative refinement
- **Dual Interface Support**: Story generation and conversational chat with context management
- **Universal Provider Compatibility**: Works with any OpenAI-compatible API (Azure OpenAI, OpenRouter, Ollama, custom endpoints)

### MCP (Model Context Protocol) Integration
- **Embedded MCP Server**: Expose story generation as MCP tools for integration with Claude Desktop and other MCP clients
- **All Framework Access**: Each AI framework available as separate MCP tool
- **HTTP-based Protocol**: Easy integration at `/mcp` endpoint

### Modern Frontend Options
- **React Frontend** (`/frontendReact/`): Modern SPA with TypeScript, Vite, Tailwind CSS
  - Real-time data fetching with React Query
  - Comprehensive TypeScript support
  - Mobile-responsive design
  - Advanced form handling and validation
- **Dual Frontend Architecture**: Choose between React for complex UIs or simple HTML for lightweight deployments

### Advanced Features
- **Context Management**: Upload files and execute prompts with contextual understanding
- **Comprehensive Cost Tracking**: 
  - Individual transaction monitoring
  - Token usage analytics
  - Cost breakdowns by framework and model
  - Detailed performance metrics
- **Chat Management**: 
  - Persistent conversation history
  - Framework switching mid-conversation
  - Conversation search and management
- **Story Management**:
  - Full story history and search
  - Character-based story filtering
  - Export capabilities (copy, download)
  - Story preview and full view modes

### Production-Ready Infrastructure
- **Structured Logging**: JSON-formatted logs with request tracking and performance metrics
- **Web-based Log Viewer**: Real-time log monitoring with filtering and search
- **Database Flexibility**: SQLite for development, PostgreSQL-ready for production
- **Docker Support**: Multi-stage builds with separate frontend/backend containers
- **Health Monitoring**: Comprehensive health checks and error tracking
- **Security**: Input validation, CORS configuration, rate limiting, secure API key management

## Architecture Improvements

### Security & Configuration
- ✅ Environment variable validation at startup
- ✅ CORS middleware with configurable origins
- ✅ Input sanitization and validation
- ✅ Request size limits

### Performance
- ✅ Connection pooling for API clients
- ✅ Lazy service initialization
- ✅ Async/await throughout
- ✅ Request timeout handling

### Reliability
- ✅ Retry logic with exponential backoff
- ✅ Comprehensive error handling
- ✅ Structured logging with request IDs
- ✅ Health check endpoint

## Requirements

### Backend
- Python 3.11+ (recommended)
- FastAPI 0.109.0+
- Pydantic V2 (2.5.3+)
- SQLAlchemy with Alembic for database migrations
- FastMCP for Model Context Protocol integration

### Frontend (React - Optional)
- Node.js 18+
- npm or yarn
- Modern browser with ES2020+ support

## Installation

### Local Development

1. Clone the repository
2. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

3. Configure your provider:

```env
# Your API key for authentication
PROVIDER_API_KEY=your-api-key

# Base URL for the API (must be OpenAI-compatible)
PROVIDER_API_BASE_URL=https://api.your-provider.com/v1

# Model name/identifier
PROVIDER_MODEL=your-model-name

# Display name for your provider
PROVIDER_NAME=Your Provider Name
```

**Example configurations:**

*For Ollama (local):*
```env
PROVIDER_API_BASE_URL=http://localhost:11434/v1
PROVIDER_MODEL=llama2
PROVIDER_NAME=Ollama Local
```

*For Tachyon LLM:*
```env
PROVIDER_API_BASE_URL=https://api.tachyon.ai/v1
PROVIDER_MODEL=tachyon-fast
PROVIDER_NAME=Tachyon LLM
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
# Full application (backend + embedded MCP server)
python backend/main.py

# For React frontend development (separate terminals)
# Terminal 1: Backend
python backend/main.py

# Terminal 2: React Frontend
cd frontendReact
npm install
npm run dev
```

### Docker Deployment

```bash
# Separated architecture with React frontend
docker-compose -f docker-compose.separated.yml up --build

# Legacy monolithic deployment
docker-compose up --build

# Manual build
docker build -t ai-story-generator .
docker run -p 8000:8000 --env-file .env ai-story-generator
```

## Configuration

All configuration is done via environment variables. See `.env.example` for available options:

### Provider Configuration
- `LLM_PROVIDER`: Choose "azure", "openrouter", or "custom" (required)

### Azure OpenAI (if using Azure)
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Your deployment name

### OpenRouter (if using OpenRouter)
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_MODEL`: Model to use (default: openai/gpt-4-turbo-preview)
- `OPENROUTER_SITE_URL`: Your site URL for analytics (optional)
- `OPENROUTER_APP_NAME`: Your app name for analytics (optional)

### Custom Provider (if using Custom)
- `CUSTOM_API_KEY`: Your API key
- `CUSTOM_API_BASE_URL`: Base URL for the API (must be OpenAI-compatible)
- `CUSTOM_MODEL`: Model name to use
- `CUSTOM_PROVIDER_NAME`: Display name for the provider (default: Custom LLM)
- `CUSTOM_API_TYPE`: API type, currently only "openai" supported (default: openai)
- `CUSTOM_HEADERS`: Additional headers as JSON (optional)

### Application Settings
- `DEBUG_MODE`: Enable debug logging and docs (default: false)
- `CORS_ORIGINS`: Allowed CORS origins (default: ["http://localhost:8000"])
- `MAX_REQUEST_SIZE`: Maximum request size in bytes (default: 1048576)

### Logging Configuration
- `LOG_FILE_PATH`: Path to log file (default: "logs/app.log")
- `LOG_LEVEL`: Logging level - DEBUG, INFO, WARNING, ERROR (default: "INFO")
- `LOG_ROTATION_HOURS`: Hours between log file rotation (default: 1)
- `LOG_RETENTION_DAYS`: Days to retain old log files (default: 7)

## API Endpoints

### Core Application
- `GET /health`: Health check endpoint
- `GET /api/provider`: Get current AI provider information

### Story Generation
- `POST /api/semantic-kernel`: Generate story using Semantic Kernel
- `POST /api/langchain`: Generate story using LangChain
- `POST /api/langgraph`: Generate story using LangGraph
- `GET /api/stories`: List all stories with pagination
- `GET /api/stories/{id}`: Get specific story
- `GET /api/stories/search/characters`: Search stories by character
- `DELETE /api/stories`: Delete all stories

### Chat System
- `POST /api/chat/semantic-kernel`: Chat using Semantic Kernel
- `POST /api/chat/langchain`: Chat using LangChain
- `POST /api/chat/langgraph`: Chat using LangGraph
- `GET /api/chat/conversations`: List chat conversations
- `GET /api/chat/conversations/{id}`: Get specific conversation
- `DELETE /api/chat/conversations/{id}`: Delete conversation
- `DELETE /api/chat/conversations`: Delete all conversations

### Cost Tracking
- `GET /api/cost/usage`: Get usage summaries by date range
- `GET /api/cost/transactions`: Get individual transaction details
- `DELETE /api/cost/usage`: Clear all usage data

### Context Management
- `POST /api/context/upload`: Upload context files
- `GET /api/context/files`: List uploaded files
- `DELETE /api/context/files/{id}`: Delete context file
- `POST /api/context/execute`: Execute prompt with context
- `GET /api/context/executions`: Get execution history

### MCP (Model Context Protocol)
- `GET /mcp`: MCP server endpoint for tool discovery
- `POST /mcp`: MCP tool execution

### Log Management
- `GET /logs`: Web-based log viewer interface
- `GET /logs/files`: List available log files
- `GET /logs/entries/{file_path}`: Get paginated log entries

### Request Format
```json
{
    "primary_character": "Santa Claus",
    "secondary_character": "Rudolph"
}
```

### Response Format
```json
{
    "story": "Generated story content...",
    "combined_characters": "Santa Claus and Rudolph",
    "method": "LangChain",
    "generation_time_ms": 1234.56,
    "request_id": "uuid-here"
}
```

## Testing

### Backend Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.
```

### MCP Server Testing
```bash
# Test MCP tools directly
python test_mcp_working.py

# Test with FastMCP client
python test_mcp_fastmcp.py
```

### Frontend Testing (React)
```bash
cd frontendReact
# Run React tests (when implemented)
npm test
```

## Frontend Architecture

The platform supports a modern React frontend alongside the FastAPI backend:

### React Frontend Features
- **Modern Stack**: React 18, TypeScript, Vite, Tailwind CSS
- **Real-time Updates**: React Query for efficient data fetching and caching
- **Responsive Design**: Mobile-first design principles
- **Type Safety**: Full TypeScript support with comprehensive type definitions
- **Advanced UI**: Form validation, loading states, toast notifications
- **Performance**: Code splitting, optimistic updates, and intelligent caching

### Deployment Options
```bash
# Development (separate terminals)
# Backend
python backend/main.py

# React Frontend
cd frontendReact && npm run dev

# Production with Docker
docker-compose -f docker-compose.separated.yml up --build
```

### Access Points
- **React Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **MCP Server**: http://localhost:8000/mcp

## Database Management

The application uses SQLAlchemy with Alembic for database migrations:

```bash
# Apply migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Check migration status
alembic current
```

### Database Models
- **StoryDB**: Stores generated stories with metadata
- **ChatConversation**: Manages chat conversations
- **ChatMessage**: Individual chat messages
- **CostUsage**: Tracks API usage and costs
- **ContextFile**: Uploaded context files
- **ContextPromptExecution**: Context execution history

## Development Commands

```bash
# Check setup and dependencies
python check-setup.py

# Run development server with auto-reload
python backend/main.py

# Run all services with Docker
docker-compose -f docker-compose.separated.yml up --build

# View logs in real-time
python test_logging.py  # Generate test logs
# Then visit http://localhost:8000/logs
```

## Architecture Overview

```
AI Story Generator Platform
├── Backend (FastAPI)
│   ├── Story Generation Services
│   │   ├── Semantic Kernel Service
│   │   ├── LangChain Service
│   │   └── LangGraph Service
│   ├── Chat System
│   ├── Context Management
│   ├── Cost Tracking
│   ├── MCP Server Integration
│   └── Database Layer (SQLAlchemy)
├── Frontend (React + TypeScript)
│   ├── Story Generator Interface
│   ├── Chat Interface
│   ├── Story History & Search
│   ├── Cost Tracking Dashboard
│   └── Context Management UI
├── MCP Integration
│   ├── Story Generation Tools
│   ├── Framework Comparison
│   └── Claude Desktop Compatible
└── Infrastructure
    ├── Docker Containers
    ├── Database (SQLite/PostgreSQL)
    ├── Logging System
    └── Health Monitoring
```

## Monitoring

### Structured Logging
The application includes comprehensive structured logging with JSON output:
- Request start/completion with duration and token usage
- API calls with retry attempts and response times
- Error tracking with stack traces and context
- Token usage tracking for cost monitoring

### Log Files
Logs are written to both console and rotating files:
- **Console**: Human-readable format in development
- **Files**: JSON format in `logs/app.log` (configurable)
- **Rotation**: Hourly rotation with configurable retention
- **Format**: Each log entry includes timestamp, level, service, request_id, and structured data

### Log Levels
- **DEBUG**: Detailed debugging information
- **INFO**: General application events, API calls, token usage
- **WARNING**: Retry attempts, rate limiting
- **ERROR**: Application errors with full context

### Web-Based Log Viewer
The application includes a comprehensive web-based log viewer accessible at `/logs`:

**Features:**
- **Real-time log viewing** with auto-refresh (30s intervals)
- **Advanced filtering** by log level, search terms, and file selection
- **Pagination support** (25/50/100/200 entries per page)
- **Detailed log entry inspection** with expandable JSON view
- **Performance metrics** display (response times, token usage, etc.)
- **Security event monitoring** (suspicious input detection, validation failures)
- **Mobile-responsive design** with Bootstrap 5

**Usage:**
1. Navigate to `http://localhost:8000/logs`
2. Select a log file from the dropdown
3. Use filters to narrow down entries
4. Click the eye icon to expand full log details
5. Auto-refresh keeps logs current

**Test Log Generation:**
```bash
python3 test_logging.py
```

## Error Handling

Custom exceptions with specific error codes:
- `ValidationError`: Input validation failures
- `APIKeyError`: Missing or invalid API credentials
- `APIConnectionError`: Failed API connections
- `APIRateLimitError`: Rate limit exceeded
- `TimeoutError`: Operation timeouts

## Performance Considerations

- API calls timeout after 60 seconds
- Maximum 3 retry attempts with exponential backoff
- Connection pooling limits: 10 connections, 5 keep-alive

## Security Notes

- All user input is sanitized and validated
- Character names limited to 100 characters
- HTML/script injection prevention
- CORS configured for specific origins only

## MCP Integration

The platform includes a built-in MCP (Model Context Protocol) server that exposes story generation capabilities as tools:

### Available MCP Tools
- `generate_story_semantic_kernel`: Generate stories using Semantic Kernel
- `generate_story_langchain`: Generate stories using LangChain  
- `generate_story_langgraph`: Generate stories using LangGraph

**Note**: The `compare_frameworks` tool has been removed. See [FRAMEWORK_COMPARISON.md](FRAMEWORK_COMPARISON.md) for details about the removed functionality and alternative implementation approaches.

### MCP Server Configuration
- **Endpoint**: `http://localhost:8000/mcp` (primary) or `http://localhost:9999/mcp` (fallback)
- **Protocol**: HTTP-based MCP implementation using FastMCP
- **Integration**: Mounted as ASGI sub-application via `http_app()` method
- **Auto-start**: Integrated with main application
- **Logging**: Full structured logging with console output

### Claude Desktop Integration
```json
{
  "mcpServers": {
    "ai-story-generator": {
      "command": "http",
      "args": ["http://localhost:8000/mcp"]
    }
  }
}
```

## Provider Comparison

### Azure OpenAI
- **Pros**: Enterprise support, SLA guarantees, data privacy
- **Cons**: Requires Azure account, region-specific
- **Best for**: Enterprise deployments, regulated industries

### OpenRouter
- **Pros**: Access to multiple models, easy setup, pay-per-use
- **Cons**: Third-party service, usage-based pricing
- **Best for**: Development, testing, multi-model comparison

### Custom Provider (e.g., Tachyon)
- **Pros**: Use any OpenAI-compatible API, self-hosted options, specialized models
- **Cons**: Requires manual configuration, limited to OpenAI-compatible APIs
- **Best for**: Custom deployments, specialized models, local LLMs

## Switching Providers

To switch to a different provider:

### For OpenRouter:
1. Copy the OpenRouter example configuration:
```bash
cp .env.openrouter.example .env
```
2. Add your OpenRouter API key (get one at https://openrouter.ai/keys)
3. Choose your preferred model (see https://openrouter.ai/models)
4. Restart the application

### For Custom Provider (e.g., Tachyon):
1. Copy the custom provider example configuration:
```bash
cp .env.custom.example .env
```
2. Configure your provider details:
   - Set `CUSTOM_API_KEY` to your API key
   - Set `CUSTOM_API_BASE_URL` to your provider's endpoint
   - Set `CUSTOM_MODEL` to your desired model
   - Set `CUSTOM_PROVIDER_NAME` to display name (e.g., "Tachyon LLM")
3. Restart the application

The application will automatically use the configured provider without any code changes.

## Supported Custom Providers

Any OpenAI-compatible API should work, including:
- **Tachyon LLM** - High-performance LLM service
- **Ollama** - Run LLMs locally
- **LM Studio** - Local LLM server
- **vLLM** - High-throughput LLM serving
- **FastChat** - Multi-model serving
- **LocalAI** - OpenAI compatible local API
- **Text Generation Inference** - Hugging Face's LLM server

## Prompt Management

The application uses a modular prompt system where prompts are stored in separate `.txt` files for easy editing:

```
prompts/
├── langchain/
│   ├── langchain_system_prompt.txt          # LangChain system prompt
│   └── langchain_user_prompt_template.txt   # LangChain user template
├── langgraph/
│   ├── langgraph_storyteller_system_prompt.txt  # LangGraph storyteller prompt
│   ├── langgraph_initial_story_template.txt     # LangGraph initial story template
│   ├── langgraph_editor_system_prompt.txt       # LangGraph editor prompt
│   └── langgraph_enhancement_template.txt       # LangGraph enhancement template
└── semantic_kernel/
    ├── semantic_kernel_system_prompt.txt        # Semantic Kernel system prompt
    └── semantic_kernel_user_message_template.txt # Semantic Kernel user template
```

### Editing Prompts

To customize the story generation behavior:

1. Navigate to the appropriate subdirectory in `prompts/` (langchain, langgraph, or semantic_kernel)
2. Edit the relevant `.txt` file for the framework you want to customize
3. Maintain the template variables like `{primary_character}` and `{secondary_character}`
4. Restart the application to load the new prompts

### Template Variables

All user prompt templates support these variables:
- `{primary_character}` - The first character name
- `{secondary_character}` - The second character name
- `{story}` (LangGraph only) - The initial story for enhancement