# AI Content Generation Platform - Architecture Overview

## Table of Contents
- [System Overview](#system-overview)
- [Architecture Principles](#architecture-principles)
- [Core Components](#core-components)
- [Service Architecture](#service-architecture)
- [Data Layer](#data-layer)
- [API Layer](#api-layer)
- [Prompt Management](#prompt-management)
- [Logging & Monitoring](#logging--monitoring)
- [Security & Error Handling](#security--error-handling)
- [Deployment Architecture](#deployment-architecture)
- [Extensibility & Future Considerations](#extensibility--future-considerations)

## System Overview

The AI Content Generation Platform is a modular, extensible web application that provides content generation capabilities through multiple AI frameworks. The system is designed with a service-oriented architecture that supports multiple AI providers (Azure OpenAI, OpenRouter, custom endpoints) and different AI frameworks (Semantic Kernel, LangChain, LangGraph).

### Key Features
- **Multi-Framework Support**: Semantic Kernel, LangChain, and LangGraph implementations
- **Provider Flexibility**: Azure OpenAI, OpenRouter, and custom API providers
- **Dual Functionality**: Both content generation and conversational chat capabilities
- **Comprehensive Logging**: Structured logging with plain-text format for easy analysis
- **Web-Based Management**: Log viewer, conversation management, and API monitoring
- **Generic Design**: Framework-agnostic base classes for easy extension

## Architecture Principles

### 1. **Modularity**
- Clear separation of concerns between AI frameworks
- Pluggable service architecture
- Independent prompt management

### 2. **Extensibility**
- Abstract base classes for easy framework addition
- Generic interfaces that support various use cases
- Configurable provider settings

### 3. **Maintainability**
- External prompt files for easy modification
- Comprehensive logging and monitoring
- Clear documentation and type hints

### 4. **Reliability**
- Robust error handling and retry logic
- Database transaction management
- Graceful degradation strategies

### 5. **Performance**
- Connection pooling for HTTP clients
- Efficient database queries with proper indexing
- Asynchronous processing throughout

## Core Components

```
├── services/                    # Business Logic Layer
│   ├── base_service.py         # Abstract base service
│   ├── chat_services/          # Conversational AI services
│   └── story_services/         # Content generation services
├── routes/                     # API Layer
│   ├── chat_routes.py          # Chat endpoints
│   ├── story_routes.py         # Content generation endpoints
│   └── log_routes.py           # Logging and monitoring endpoints
├── prompts/                    # Prompt Management
│   ├── chat_prompts.py         # Chat prompt loader
│   ├── semantic_kernel/        # SK-specific prompts
│   ├── langchain/              # LangChain prompts
│   └── langgraph/              # LangGraph prompts
├── database.py                 # Data Access Layer
├── config.py                   # Configuration Management
├── logging_config.py           # Structured Logging
├── middleware.py               # Request/Response Processing
└── exceptions.py               # Error Handling
```

## Service Architecture

### Base Service Pattern

All AI services inherit from `BaseService`, providing:
- **Client Management**: Lazy initialization with connection pooling
- **Provider Abstraction**: Support for Azure, OpenRouter, and custom APIs
- **Retry Logic**: Exponential backoff for transient failures
- **Usage Tracking**: Token consumption and performance metrics
- **Error Handling**: Consistent exception handling across providers

```python
abstract class BaseService:
    - _create_client() -> Union[AsyncAzureOpenAI, AsyncOpenAI]
    - _call_api_with_retry() -> tuple[str, Dict[str, Any]]
    - generate_content() -> Tuple[str, Dict[str, Any]]  # Abstract
```

### Service Specializations

#### 1. **Semantic Kernel Services**
- **Focus**: User-friendly, encouraging content creation
- **Approach**: Direct prompt-to-completion pattern
- **Use Cases**: General content creation, creative writing

#### 2. **LangChain Services**
- **Focus**: Structured text processing and analysis
- **Approach**: Template-based prompt engineering
- **Use Cases**: Document analysis, structured content generation

#### 3. **LangGraph Services**
- **Focus**: Complex multi-step workflows
- **Approach**: Graph-based reasoning with iterative refinement
- **Use Cases**: Complex narratives, multi-stage content development

### Dual Service Model

Each framework implements both:
- **Content Generation Services**: For structured content creation
- **Chat Services**: For conversational interactions

```
services/
├── story_services/             # Content Generation
│   ├── semantic_kernel_service.py
│   ├── langchain_service.py
│   └── langgraph_service.py
└── chat_services/              # Conversational AI
    ├── semantic_kernel_chat_service.py
    ├── langchain_chat_service.py
    └── langgraph_chat_service.py
```

## Data Layer

### Database Schema

#### Stories Table
```sql
CREATE TABLE stories (
    id INTEGER PRIMARY KEY,
    primary_character VARCHAR(100),
    secondary_character VARCHAR(100),
    combined_characters VARCHAR(200),
    story_content TEXT,
    method VARCHAR(50),           -- semantic_kernel, langchain, langgraph
    generation_time_ms FLOAT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    request_id VARCHAR(50),
    provider VARCHAR(50),         -- azure, openrouter, custom
    model VARCHAR(100),
    created_at TIMESTAMP
);
```

#### Chat System
```sql
CREATE TABLE chat_conversations (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200),
    method VARCHAR(50),
    provider VARCHAR(50),
    model VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER REFERENCES chat_conversations(id),
    role VARCHAR(20),             -- 'user' or 'assistant'
    content TEXT,
    generation_time_ms FLOAT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    request_id VARCHAR(50),
    created_at TIMESTAMP
);
```

### Data Access Patterns

#### Transaction Management
```python
@contextmanager
def get_db_context():
    """Provides automatic transaction management with rollback on failure"""
    
with get_db_context() as db:
    # Operations are automatically committed or rolled back
```

#### Dependency Injection
```python
def get_db() -> Generator:
    """FastAPI dependency for database sessions"""
```

## API Layer

### RESTful Endpoints

#### Content Generation API
```
POST /api/stories/semantic-kernel    # Generate with Semantic Kernel
POST /api/stories/langchain          # Generate with LangChain  
POST /api/stories/langgraph          # Generate with LangGraph
GET  /api/stories                    # List generated content
GET  /api/stories/{id}               # Get specific content
```

#### Chat API
```
POST /api/chat/semantic-kernel       # Chat with Semantic Kernel
POST /api/chat/langchain             # Chat with LangChain
POST /api/chat/langgraph             # Chat with LangGraph
GET  /api/conversations              # List conversations
GET  /api/conversations/{id}         # Get conversation history
```

#### Monitoring API
```
GET  /api/logs                       # View application logs
GET  /api/logs/files                 # List log files
GET  /api/health                     # Health check endpoint
```

### Request/Response Flow

1. **Request Processing**
   - Middleware logs request details
   - Input validation and sanitization
   - Service instance retrieval/creation

2. **Service Execution**  
   - Prompt loading and formatting
   - API call with retry logic
   - Usage metrics collection

3. **Data Persistence**
   - Transaction-wrapped database operations
   - Comprehensive metadata storage

4. **Response Formation**
   - Consistent response format
   - Error handling and user-friendly messages
   - Performance metrics inclusion

## Prompt Management

### External Prompt Files

Prompts are stored as external text files for easy maintenance:

```
prompts/
├── chat_prompts.py                 # Prompt loading utilities
├── semantic_kernel/
│   ├── semantic_kernel_system_prompt.txt
│   ├── semantic_kernel_chat_system_prompt.txt
│   └── semantic_kernel_user_message_template.txt
├── langchain/
│   ├── langchain_system_prompt.txt
│   ├── langchain_chat_system_prompt.txt
│   └── langchain_user_prompt_template.txt
└── langgraph/
    ├── langgraph_storyteller_system_prompt.txt
    ├── langgraph_chat_system_prompt.txt
    ├── langgraph_initial_story_template.txt
    └── langgraph_enhancement_template.txt
```

### Prompt Loading Architecture

```python
def load_prompt_file(filename: str, prompt_dir: Path) -> str:
    """Load and cache prompt content with error handling"""

def get_chat_prompt_by_service(service_name: str) -> str:
    """Dynamic prompt loading based on service type"""
```

### Framework-Specific Approaches

- **Semantic Kernel**: Simple, encouraging prompts for creativity
- **LangChain**: Structured, analytical prompts for processing
- **LangGraph**: Complex, multi-step prompts for workflows

## Logging & Monitoring

### Structured Logging

The platform implements comprehensive structured logging using `structlog`:

```python
logger.info("API call successful",
           service=self.service_name,
           provider=settings.llm_provider,
           model=model,
           response_length=len(content),
           execution_time_ms=usage_info["execution_time_ms"],
           input_tokens=usage_info["input_tokens"],
           output_tokens=usage_info["output_tokens"])
```

### Dual-Format Logging

- **Console**: Colored, human-readable format for development
- **File**: Plain text format for analysis and log viewers

### Log Categories

1. **Request Tracking**: Complete request lifecycle
2. **Database Operations**: Transaction details and performance
3. **AI Service Calls**: Provider interactions and metrics
4. **Error Handling**: Comprehensive error context
5. **Performance Metrics**: Response times and resource usage

### Web-Based Log Viewer

- **Real-time Viewing**: Live log streaming capability
- **Pagination**: Efficient handling of large log files
- **Filtering**: Search and filter by log level, service, etc.
- **Export**: Download logs for external analysis

## Security & Error Handling

### Error Handling Strategy

#### Custom Exception Hierarchy
```python
class Error(Exception):
    """Base exception for application errors"""

class APIConnectionError(Error):
    """API connection and communication errors"""

class APIRateLimitError(Error):
    """API rate limiting errors"""

class TimeoutError(Error):
    """Timeout-related errors"""
```

#### Error Boundaries
- Service-level error isolation
- Graceful degradation for non-critical failures
- Comprehensive error logging and reporting

### Security Measures

1. **API Key Management**: Secure environment variable storage
2. **Input Validation**: Comprehensive request sanitization
3. **Rate Limiting**: Protection against abuse
4. **Error Information**: No sensitive data in error responses
5. **CORS Configuration**: Proper cross-origin restrictions

## Deployment Architecture

### Environment Configuration

```python
class Settings(BaseSettings):
    # AI Provider Settings
    llm_provider: str = "azure"
    azure_openai_api_key: str
    azure_openai_endpoint: str
    
    # Application Settings
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # Database Settings
    database_url: str = "sqlite:///./stories.db"
```

### Docker Support

The application is containerized for consistent deployment:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Database**: SQLite for development, PostgreSQL for production
2. **Logging**: File rotation and centralized log aggregation
3. **Monitoring**: Health checks and performance metrics
4. **Scaling**: Horizontal scaling support through stateless design

## Extensibility & Future Considerations

### Adding New AI Frameworks

1. **Create Service Classes**: Inherit from `BaseService`
2. **Implement Required Methods**: `generate_content()` and `generate_story()`
3. **Add Prompt Files**: Framework-specific prompt templates
4. **Update Routes**: Add API endpoints for the new framework
5. **Update Configuration**: Add framework-specific settings

### Adding New Providers

1. **Extend Client Creation**: Update `_create_client()` method
2. **Add Configuration**: Provider-specific settings
3. **Update Error Handling**: Provider-specific error patterns
4. **Test Integration**: Comprehensive provider testing

### Scalability Enhancements

1. **Caching Layer**: Redis for prompt and response caching
2. **Queue System**: Async job processing for long-running tasks
3. **Load Balancing**: Multiple instance support
4. **Database Sharding**: Horizontal database scaling

### Monitoring Enhancements

1. **Metrics Collection**: Prometheus/Grafana integration
2. **Alerting**: Automated error and performance alerts
3. **Distributed Tracing**: Request tracing across services
4. **Analytics**: Usage patterns and performance analytics

---

This architecture provides a solid foundation for a scalable, maintainable AI content generation platform while maintaining flexibility for future enhancements and integrations.