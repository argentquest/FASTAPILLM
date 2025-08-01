# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a FastAPI-based AI content generation platform that supports multiple AI frameworks (Semantic Kernel, LangChain, LangGraph) and providers (Azure OpenAI, OpenRouter, custom OpenAI-compatible APIs).

## Essential Commands

```bash
# Development
python backend/main.py            # Run the application locally
pip install -r requirements.txt   # Install dependencies

# Testing
pytest                           # Run all tests

# Docker
docker-compose up --build        # Build and run with Docker
docker build -t ai-story-generator .  # Manual Docker build

# Database Migrations
alembic upgrade head             # Apply database migrations
alembic revision --autogenerate -m "description"  # Create new migration
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

### Error Handling
- All services use comprehensive try-catch blocks
- Errors are logged with full context
- HTTP exceptions are raised with appropriate status codes

### Testing
- Use pytest for all tests
- Mock external API calls
- Test files should mirror the source structure