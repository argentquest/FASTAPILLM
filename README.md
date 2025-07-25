# AI Content Generation Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A modern, extensible AI content generation platform supporting multiple AI frameworks and providers. Built with FastAPI and designed for scalability, maintainability, and ease of use.

## 🚀 Features

### Multi-Framework Support
- **Semantic Kernel**: User-friendly content creation with encouraging prompts
- **LangChain**: Structured text processing and analytical content generation  
- **LangGraph**: Complex multi-step workflows with iterative refinement

### Flexible AI Providers
- **Azure OpenAI**: Enterprise-grade AI with GPT models
- **OpenRouter**: Access to multiple AI models through a single API
- **Custom Providers**: Support for any OpenAI-compatible API

### Dual Functionality
- **Content Generation**: Structured content creation for stories, articles, and more
- **Conversational Chat**: Interactive AI conversations with context management

### Production-Ready Features
- **Comprehensive Logging**: Structured logging with web-based log viewer
- **Database Integration**: SQLite for development, PostgreSQL-ready for production
- **Error Handling**: Robust error handling with retry logic and graceful degradation
- **Performance Monitoring**: Request tracking, token usage analytics, and performance metrics
- **Security**: Input validation, rate limiting, and secure API key management

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

- Python 3.8+
- Pydantic V2 (2.5.3+)
- FastAPI 0.109.0+

## Installation

### Local Development

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your LLM provider:
```bash
cp .env.example .env
```

3. Configure your chosen provider:

**For Azure OpenAI:**
```env
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

**For OpenRouter:**
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your-api-key
OPENROUTER_MODEL=openai/gpt-4-turbo-preview
```

**For Custom Provider (e.g., Tachyon, Ollama, etc.):**
```env
LLM_PROVIDER=custom
CUSTOM_API_KEY=your-api-key
CUSTOM_API_BASE_URL=https://api.tachyon.ai/v1
CUSTOM_MODEL=tachyon-fast
CUSTOM_PROVIDER_NAME=Tachyon LLM
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python main.py
```

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build manually
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

### Web Interface
- `GET /`: Main web interface
- `GET /logs`: Web-based log viewer with pagination
- `GET /health`: Health check endpoint

### Story Generation
- `POST /api/semantic-kernel`: Generate story using Semantic Kernel
- `POST /api/langchain`: Generate story using LangChain
- `POST /api/langgraph`: Generate story using LangGraph

### Chat Endpoints
- `POST /api/chat/semantic-kernel`: Chat using Semantic Kernel
- `POST /api/chat/langchain`: Chat using LangChain
- `POST /api/chat/langgraph`: Chat using LangGraph
- `GET /api/chat/conversations`: List chat conversations
- `GET /api/chat/conversations/{id}`: Get specific conversation
- `DELETE /api/chat/conversations/{id}`: Delete conversation

### Log Management
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

Run tests with pytest:
```bash
pytest
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