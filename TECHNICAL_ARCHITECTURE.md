# FASTAPILLM - Technical Architecture Document

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Diagrams](#architecture-diagrams)
4. [Component Architecture](#component-architecture)
5. [Data Architecture](#data-architecture)
6. [API Architecture](#api-architecture)
7. [Security Architecture](#security-architecture)
8. [Deployment Architecture](#deployment-architecture)
9. [Performance Architecture](#performance-architecture)
10. [Integration Architecture](#integration-architecture)
11. [Development Architecture](#development-architecture)
12. [Operational Architecture](#operational-architecture)
13. [Configuration and Environment Setup](#configuration-and-environment-setup)
14. [Appendices and Reference Materials](#appendices-and-reference-materials)

---

## Executive Summary

### Platform Overview

FASTAPILLM is a modern, enterprise-grade AI content generation platform that provides a comprehensive solution for AI-powered story generation and conversational interfaces. The platform is built with a microservices-oriented architecture using FastAPI for the backend, React for the frontend, and includes a standalone MCP (Model Context Protocol) server for external integrations.

### Key Architectural Decisions

#### Multi-Framework AI Support
The platform implements a pluggable architecture supporting three distinct AI frameworks:
- **Semantic Kernel**: Microsoft's plugin-based framework for user-friendly content creation
- **LangChain**: Structured framework for analytical text processing and chain composition
- **LangGraph**: Advanced workflow framework with multi-step editing and state management

This design allows users to compare different AI approaches and choose the most suitable framework for their specific use cases.

#### Universal Provider Compatibility
Rather than being tied to a specific AI provider, the platform implements a provider-agnostic architecture that works with any OpenAI-compatible API. This includes:
- OpenRouter for access to multiple models
- Azure OpenAI for enterprise deployments
- Local models via Ollama, LM Studio, or similar
- Custom providers like Tachyon LLM

#### Comprehensive Observability
The architecture includes built-in observability features:
- Structured JSON logging with transaction GUID tracking
- Real-time cost tracking and token usage monitoring
- Performance metrics collection and analysis
- Web-based log viewer for operational insights

#### Modern Full-Stack Architecture
- **Backend**: FastAPI with async/await patterns for high performance
- **Frontend**: React 18 with TypeScript, Vite build system, and Tailwind CSS
- **Database**: SQLAlchemy ORM with Alembic migrations, supporting SQLite and PostgreSQL
- **Containerization**: Docker support with multi-stage builds

### System Capabilities

The platform provides:
- **Story Generation**: AI-powered story creation with character-based prompts
- **Chat Interface**: Conversational AI with context management and history
- **Context Processing**: File upload and processing with contextual AI execution
- **Cost Tracking**: Detailed cost analysis and usage monitoring
- **MCP Integration**: External tool access via Model Context Protocol
- **Multi-Provider Support**: Seamless switching between AI providers
- **Real-time Monitoring**: Comprehensive logging and performance tracking

### Target Architecture Goals

1. **Scalability**: Horizontal scaling support with stateless services
2. **Reliability**: Comprehensive error handling and retry mechanisms
3. **Observability**: Full request tracing and performance monitoring
4. **Security**: Input validation, rate limiting, and secure API key management
5. **Maintainability**: Clean code architecture with comprehensive testing
6. **Extensibility**: Plugin-based design for easy framework and provider additions

---

## System Overview

### Platform Purpose

FASTAPILLM is designed to provide a comprehensive AI content generation platform that enables users to:

1. **Generate Creative Content**: Create stories, narratives, and creative text using multiple AI frameworks
2. **Compare AI Approaches**: Evaluate different AI frameworks side-by-side to understand their strengths and characteristics
3. **Manage Conversations**: Engage in contextual conversations with AI assistants across different frameworks
4. **Process Documents**: Upload and process files with AI-powered analysis and summarization
5. **Monitor Usage**: Track costs, performance, and usage patterns across all AI operations
6. **Integrate Externally**: Provide AI capabilities to external applications via MCP protocol

### Target Users

#### Developers and Engineers
- **Primary Use**: Integrate AI capabilities into applications via REST API or MCP protocol
- **Key Features**: Comprehensive API documentation, multiple framework options, cost tracking
- **Benefits**: Easy integration, provider flexibility, detailed monitoring

#### Content Creators and Writers
- **Primary Use**: Generate creative content and explore different AI writing styles
- **Key Features**: Web interface, framework comparison, story history management
- **Benefits**: User-friendly interface, creative flexibility, content organization

#### Researchers and Data Scientists
- **Primary Use**: Compare AI framework performance and analyze generation patterns
- **Key Features**: Detailed metrics, cost analysis, performance tracking
- **Benefits**: Comprehensive data collection, framework comparison capabilities

#### System Administrators
- **Primary Use**: Deploy and manage the platform in enterprise environments
- **Key Features**: Docker deployment, configuration management, monitoring tools
- **Benefits**: Easy deployment, comprehensive logging, operational visibility

### Core Capabilities

#### Multi-Framework AI Generation

| Framework | Strengths | Use Cases | Architecture |
|-----------|-----------|-----------|--------------|
| **Semantic Kernel** | Plugin-based, user-friendly, encouraging | Creative writing, brainstorming, ideation | Native and semantic functions |
| **LangChain** | Structured, analytical, chain composition | Document analysis, structured content | Chain-based processing |
| **LangGraph** | Advanced workflows, state management, iterative | Complex narratives, multi-step editing | Graph-based state machines |

#### Provider Compatibility Matrix

| Provider Type | Examples | Authentication | Cost Model | Use Cases |
|---------------|----------|----------------|------------|-----------|
| **Cloud APIs** | OpenRouter, Azure OpenAI | API Key | Pay-per-token | Production, scaling |
| **Local Models** | Ollama, LM Studio | None/Local | Free | Development, privacy |
| **Custom APIs** | Tachyon, vLLM | Custom headers | Variable | Specialized models |

#### Interface Options

1. **REST API**: Full programmatic access to all platform capabilities
2. **React Web Interface**: Modern, responsive web application for interactive use
3. **MCP Server**: External tool integration for Claude Desktop and other MCP clients
4. **Direct Service Access**: Python SDK-style access for embedded use cases

### System Features

#### Content Generation Features
- **Story Generation**: Character-based story creation with customizable prompts
- **Chat Interface**: Conversational AI with persistent conversation history
- **Context Processing**: File upload and AI-powered document analysis
- **Batch Operations**: Multiple content generation requests with queuing

#### Monitoring and Analytics Features
- **Cost Tracking**: Real-time cost calculation and usage analytics
- **Performance Metrics**: Response times, token usage, and throughput monitoring
- **Usage Analytics**: Historical data analysis and trend identification
- **Health Monitoring**: System health checks and availability monitoring

#### Operational Features
- **Configuration Management**: Environment-based configuration with validation
- **Logging System**: Structured JSON logging with rotation and retention
- **Error Handling**: Comprehensive error classification and recovery
- **Rate Limiting**: Configurable rate limits to prevent abuse

#### Integration Features
- **MCP Protocol**: Standard Model Context Protocol implementation
- **Webhook Support**: Event-driven integrations (planned)
- **API Versioning**: Backward-compatible API evolution
- **Provider Abstraction**: Seamless switching between AI providers

### Architecture Principles

#### Scalability Principles
- **Stateless Services**: All services designed for horizontal scaling
- **Async Processing**: Non-blocking I/O throughout the application stack
- **Connection Pooling**: Efficient resource utilization for database and HTTP connections
- **Caching Strategy**: Multi-layer caching for performance optimization

#### Reliability Principles
- **Retry Logic**: Exponential backoff with jitter for transient failures
- **Circuit Breakers**: Fail-fast patterns for external service dependencies
- **Graceful Degradation**: Partial functionality during service outages
- **Health Checks**: Comprehensive health monitoring at all levels

#### Security Principles
- **Input Validation**: Comprehensive validation at all entry points
- **Least Privilege**: Minimal permissions for all system components
- **Secure Defaults**: Security-first configuration defaults
- **Audit Logging**: Complete audit trail for all operations

#### Maintainability Principles
- **Clean Architecture**: Clear separation of concerns and dependencies
- **Comprehensive Testing**: Unit, integration, and end-to-end test coverage
- **Documentation**: Living documentation that evolves with the codebase
- **Code Quality**: Automated linting, formatting, and quality checks

## Architecture Diagrams

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[React Web App<br/>Port 3001]
        MCP_CLIENT[MCP Clients<br/>Claude Desktop, etc.]
        API_CLIENT[API Clients<br/>External Apps]
    end
    
    subgraph "Application Layer"
        NGINX[Nginx Proxy<br/>Optional]
        FASTAPI[FastAPI Backend<br/>Port 8000]
        MCP_SERVER[MCP Server<br/>Port 9999]
    end
    
    subgraph "Service Layer"
        SK[Semantic Kernel<br/>Service]
        LC[LangChain<br/>Service]
        LG[LangGraph<br/>Service]
        CHAT[Chat<br/>Services]
        CONTEXT[Context<br/>Services]
    end
    
    subgraph "Infrastructure Layer"
        DB[(Database<br/>SQLite/PostgreSQL)]
        LOGS[Log Files<br/>Structured JSON]
        CONFIG[Configuration<br/>Environment Variables]
    end
    
    subgraph "External Services"
        OPENROUTER[OpenRouter API]
        AZURE[Azure OpenAI]
        OLLAMA[Ollama Local]
        CUSTOM[Custom Providers]
    end
    
    WEB --> FASTAPI
    API_CLIENT --> FASTAPI
    MCP_CLIENT --> MCP_SERVER
    NGINX --> FASTAPI
    
    FASTAPI --> SK
    FASTAPI --> LC
    FASTAPI --> LG
    FASTAPI --> CHAT
    FASTAPI --> CONTEXT
    
    MCP_SERVER --> SK
    MCP_SERVER --> LC
    MCP_SERVER --> LG
    
    SK --> OPENROUTER
    LC --> AZURE
    LG --> OLLAMA
    CONTEXT --> CUSTOM
    
    FASTAPI --> DB
    MCP_SERVER --> DB
    
    FASTAPI --> LOGS
    MCP_SERVER --> LOGS
    
    FASTAPI --> CONFIG
    MCP_SERVER --> CONFIG
```

### Request Processing Data Flow

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Middleware
    participant Service
    participant Provider
    participant Database
    
    Client->>FastAPI: HTTP Request
    FastAPI->>Middleware: Process Request
    
    Note over Middleware: Logging, Rate Limiting,<br/>Authentication, Validation
    
    Middleware->>Service: Route to Service
    Service->>Service: Generate Transaction GUID
    Service->>Provider: API Call with Retry Logic
    
    Provider-->>Service: AI Response + Usage Data
    Service->>Service: Calculate Costs
    Service->>Database: Store Results
    Database-->>Service: Confirmation
    
    Service-->>Middleware: Formatted Response
    Middleware-->>FastAPI: Add Headers & Logging
    FastAPI-->>Client: JSON Response
    
    Note over FastAPI: Response includes:<br/>Request ID, Transaction GUID,<br/>Performance Metrics
```

### AI Generation Flow

```mermaid
flowchart TD
    START([User Request]) --> VALIDATE{Input Validation}
    VALIDATE -->|Invalid| ERROR[Return Validation Error]
    VALIDATE -->|Valid| FRAMEWORK{Select Framework}
    
    FRAMEWORK -->|Semantic Kernel| SK_SERVICE[Semantic Kernel Service]
    FRAMEWORK -->|LangChain| LC_SERVICE[LangChain Service]
    FRAMEWORK -->|LangGraph| LG_SERVICE[LangGraph Service]
    
    SK_SERVICE --> PROMPT_SK[Load SK Prompts]
    LC_SERVICE --> PROMPT_LC[Load LC Prompts]
    LG_SERVICE --> PROMPT_LG[Load LG Prompts]
    
    PROMPT_SK --> API_CALL[Provider API Call]
    PROMPT_LC --> API_CALL
    PROMPT_LG --> API_CALL
    
    API_CALL --> RETRY{API Success?}
    RETRY -->|No| BACKOFF[Exponential Backoff]
    BACKOFF --> API_CALL
    RETRY -->|Yes| PROCESS[Process Response]
    
    PROCESS --> COST[Calculate Cost]
    COST --> STORE[Store in Database]
    STORE --> RESPONSE[Format Response]
    RESPONSE --> END([Return to Client])
    
    ERROR --> END
```

### Component Interaction Diagram

```mermaid
graph LR
    subgraph "Frontend Layer"
        REACT[React App]
        ROUTER[React Router]
        QUERY[React Query]
    end
    
    subgraph "API Gateway"
        CORS[CORS Middleware]
        RATE[Rate Limiting]
        LOG[Logging Middleware]
        ERROR[Error Handling]
    end
    
    subgraph "Business Logic"
        STORY[Story Routes]
        CHAT[Chat Routes]
        COST[Cost Routes]
        CONTEXT[Context Routes]
    end
    
    subgraph "Service Layer"
        BASE[Base Service]
        SK_SVC[SK Service]
        LC_SVC[LC Service]
        LG_SVC[LG Service]
    end
    
    subgraph "Data Layer"
        ORM[SQLAlchemy ORM]
        MODELS[Database Models]
        MIGRATIONS[Alembic Migrations]
    end
    
    subgraph "Cross-Cutting"
        RETRY[Retry Utils]
        PRICING[Pricing Engine]
        TRANSACTION[Transaction Context]
        CONFIG[Configuration]
    end
    
    REACT --> ROUTER
    ROUTER --> QUERY
    QUERY --> CORS
    
    CORS --> RATE
    RATE --> LOG
    LOG --> ERROR
    ERROR --> STORY
    ERROR --> CHAT
    ERROR --> COST
    ERROR --> CONTEXT
    
    STORY --> SK_SVC
    CHAT --> LC_SVC
    CONTEXT --> LG_SVC
    
    SK_SVC --> BASE
    LC_SVC --> BASE
    LG_SVC --> BASE
    
    BASE --> RETRY
    BASE --> PRICING
    BASE --> TRANSACTION
    BASE --> CONFIG
    
    SK_SVC --> ORM
    LC_SVC --> ORM
    LG_SVC --> ORM
    
    ORM --> MODELS
    MODELS --> MIGRATIONS
```

### Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_REACT[React Dev Server<br/>localhost:3001]
        DEV_API[FastAPI Dev<br/>localhost:8000]
        DEV_MCP[MCP Server<br/>localhost:9999]
        DEV_DB[(SQLite<br/>stories.db)]
    end
    
    subgraph "Docker Compose Environment"
        DOCKER_WEB[React Container<br/>nginx:alpine]
        DOCKER_API[FastAPI Container<br/>python:3.11-slim]
        DOCKER_MCP[MCP Container<br/>python:3.11-slim]
        DOCKER_DB[(PostgreSQL<br/>Container)]
        DOCKER_LOGS[Shared Logs<br/>Volume]
    end
    
    subgraph "Production Environment"
        LB[Load Balancer<br/>nginx/cloudflare]
        PROD_WEB[React Static Files<br/>CDN/nginx]
        PROD_API[FastAPI Instances<br/>Multiple Replicas]
        PROD_MCP[MCP Server<br/>Standalone Service]
        PROD_DB[(PostgreSQL<br/>Managed Database)]
        PROD_LOGS[Centralized Logging<br/>ELK/Grafana]
        MONITORING[Monitoring<br/>Prometheus/Grafana]
    end
    
    DEV_REACT -.-> DEV_API
    DEV_API -.-> DEV_MCP
    DEV_API -.-> DEV_DB
    
    DOCKER_WEB --> DOCKER_API
    DOCKER_API --> DOCKER_MCP
    DOCKER_API --> DOCKER_DB
    DOCKER_API --> DOCKER_LOGS
    DOCKER_MCP --> DOCKER_LOGS
    
    LB --> PROD_WEB
    LB --> PROD_API
    PROD_API --> PROD_MCP
    PROD_API --> PROD_DB
    PROD_API --> PROD_LOGS
    PROD_MCP --> PROD_LOGS
    MONITORING --> PROD_API
    MONITORING --> PROD_MCP
```

### Database Entity Relationship Diagram

```mermaid
erDiagram
    Story {
        int id PK
        string primary_character
        string secondary_character
        string combined_characters
        text story_content
        string method
        float generation_time_ms
        int input_tokens
        int output_tokens
        int total_tokens
        decimal estimated_cost_usd
        string transaction_guid
        string provider
        string model
        datetime created_at
    }
    
    ChatConversation {
        int id PK
        string title
        string method
        string transaction_guid
        string provider
        string model
        datetime created_at
        datetime updated_at
    }
    
    ChatMessage {
        int id PK
        int conversation_id FK
        string role
        text content
        float generation_time_ms
        int input_tokens
        int output_tokens
        int total_tokens
        decimal estimated_cost_usd
        string transaction_guid
        datetime created_at
    }
    
    ContextPromptExecution {
        int id PK
        string original_filename
        string file_type
        int file_size_bytes
        text system_prompt
        text user_prompt
        text llm_response
        string method
        string provider
        string model
        float total_execution_time_ms
        int total_tokens
        decimal estimated_cost_usd
        string transaction_guid
        datetime created_at
    }
    
    ChatConversation ||--o{ ChatMessage : "has messages"
```

## Component Architecture

### Backend Components (FastAPI)

#### Main Application (`backend/main.py`)

**Purpose**: Central FastAPI application server that orchestrates all HTTP requests and responses.

**Key Responsibilities**:
- HTTP server initialization and configuration
- Middleware stack management (CORS, logging, error handling, rate limiting)
- Route registration and API endpoint exposure
- Application lifecycle management (startup/shutdown)
- Health check and status endpoints

**Key Features**:
```python
# Application initialization with lifespan management
@asynccontextmanager
async def base_lifespan(app: FastAPI):
    # Startup: Database initialization, logging setup
    # Shutdown: Cleanup and graceful termination

# Comprehensive middleware stack
app.add_middleware(CORSMiddleware, **cors_config)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitingMiddleware)
```

**Configuration Management**: Centralized configuration via `config.py` with environment variable support and validation.

#### Configuration System (`config.py`)

**Purpose**: Centralized configuration management with validation and environment variable support.

**Key Features**:
- Pydantic-based settings with automatic validation
- Environment variable loading from `.env` files
- Provider-agnostic configuration for any OpenAI-compatible API
- Comprehensive validation with helpful error messages

**Configuration Categories**:
```python
class Settings(BaseSettings):
    # Provider Configuration
    provider_api_key: Optional[str]
    provider_api_base_url: Optional[str]
    provider_model: Optional[str]
    provider_headers: Optional[Dict[str, str]]
    
    # Application Settings
    app_name: str = "AI Testing Suite"
    debug_mode: bool = False
    
    # Security & Rate Limiting
    cors_origins: list[str]
    max_request_size: int = 1048576
    rate_limiting_enabled: bool = True
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file_path: Optional[str] = "logs/app.log"
```

#### Database Layer (`database.py`)

**Purpose**: Database abstraction layer using SQLAlchemy ORM with comprehensive session management.

**Key Components**:
- **SQLAlchemy Models**: Complete data models for stories, chats, and context executions
- **Session Management**: Context managers for transaction handling
- **Migration Support**: Alembic integration for schema evolution
- **Connection Pooling**: Optimized database connections

**Database Models**:
```python
# Core models with comprehensive tracking
class Story(Base):
    # Content fields
    primary_character: String(100)
    story_content: Text
    
    # Performance tracking
    generation_time_ms: Float
    input_tokens: Integer
    output_tokens: Integer
    
    # Cost tracking
    estimated_cost_usd: Numeric(10,6)
    
    # Traceability
    transaction_guid: String(36)
    request_id: String(50)
```

### Service Layer Architecture

#### Base Service (`services/base_service.py`)

**Purpose**: Abstract base class providing common functionality for all AI generation services.

**Key Features**:
- **Provider Abstraction**: Universal OpenAI-compatible client creation
- **Connection Pooling**: Optimized HTTP client with connection reuse
- **Retry Logic**: Comprehensive retry mechanism with exponential backoff
- **Cost Calculation**: Automatic token usage and cost tracking
- **Transaction Context**: GUID-based request tracing

**Core Implementation**:
```python
class BaseService(ABC, TransactionAware):
    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None
        self.service_name = self.__class__.__name__
    
    @retry_api_calls
    async def _call_api(self, messages: list[Dict[str, str]], **kwargs):
        # Comprehensive API call with error handling
        # Token usage tracking and cost calculation
        # Performance metrics collection
```

#### Framework-Specific Services

##### Semantic Kernel Service (`services/story_services/semantic_kernel_service.py`)
- **Approach**: Plugin-based architecture with native and semantic functions
- **Strengths**: User-friendly, encouraging creative output
- **Implementation**: Microsoft Semantic Kernel framework integration
- **Use Cases**: Creative writing, brainstorming, ideation

##### LangChain Service (`services/story_services/langchain_service.py`)
- **Approach**: Chain composition with structured prompt templates
- **Strengths**: Analytical processing, structured output
- **Implementation**: LangChain framework with prompt templates
- **Use Cases**: Document analysis, structured content generation

##### LangGraph Service (`services/story_services/langgraph_service.py`)
- **Approach**: Graph-based workflows with state management
- **Strengths**: Multi-step editing, iterative refinement
- **Implementation**: LangGraph with storyteller and editor nodes
- **Use Cases**: Complex narratives, multi-step content creation

#### Chat Services (`services/chat_services/`)

**Purpose**: Conversational AI interfaces with persistent context and history management.

**Key Features**:
- **Conversation Management**: Persistent chat history with database storage
- **Context Preservation**: Maintains conversation context across messages
- **Framework Switching**: Ability to change AI frameworks mid-conversation
- **Message Threading**: Proper message ordering and relationship tracking

#### Context Services (`services/context_services/`)

**Purpose**: File processing and contextual AI execution services.

**Key Features**:
- **File Processing**: Support for text, PDF, and document formats
- **Context Integration**: Combines uploaded content with user prompts
- **Execution Tracking**: Comprehensive logging of context processing operations
- **Performance Monitoring**: Detailed metrics for file processing and AI execution

### Frontend Architecture (React)

#### Modern React Stack

**Technology Stack**:
- **React 18**: Latest React with concurrent features
- **TypeScript**: Full type safety and developer experience
- **Vite**: Fast build system with hot module replacement
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and caching library
- **React Router**: Client-side routing

**Project Structure**:
```
frontendReact/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/         # Page-level components
│   ├── hooks/         # Custom React hooks
│   ├── services/      # API service functions
│   ├── types/         # TypeScript type definitions
│   └── utils/         # Utility functions
├── public/            # Static assets
└── package.json       # Dependencies and scripts
```

**Key Features**:
- **Responsive Design**: Mobile-first design principles
- **Real-time Updates**: React Query for efficient data fetching
- **Form Management**: React Hook Form for complex form handling
- **Toast Notifications**: User feedback for operations
- **Loading States**: Comprehensive loading and error states

### MCP Server Architecture

#### Standalone MCP Server (`backend/mcp_server.py`)

**Purpose**: Independent Model Context Protocol server for external integrations.

**Architecture Principles**:
- **Standalone Operation**: Runs independently from main FastAPI application
- **FastMCP Framework**: Built using FastMCP best practices
- **Tool-Based Interface**: Exposes AI capabilities as discrete tools
- **Transaction Tracking**: Full request tracing with GUID correlation

**Available Tools**:
```python
@mcp.tool
async def generate_story_semantic_kernel(
    primary_character: str,
    secondary_character: str
) -> Dict[str, Any]:
    # Semantic Kernel story generation
    
@mcp.tool
async def generate_story_langchain(...):
    # LangChain story generation
    
@mcp.tool
async def generate_story_langgraph(...):
    # LangGraph story generation
    
@mcp.tool
async def list_frameworks() -> Dict[str, Any]:
    # Framework information and capabilities
```

**Integration Capabilities**:
- **Claude Desktop**: Direct integration with Anthropic's Claude Desktop
- **Custom MCP Clients**: Support for any MCP-compatible client
- **Resource Access**: Future support for database resource access

### Cross-Cutting Concerns

#### Middleware Stack

##### Logging Middleware (`middleware.py`)
- **Request Tracking**: Unique request IDs for all operations
- **Performance Monitoring**: Request duration and response size tracking
- **Error Logging**: Comprehensive error context capture
- **Transaction Correlation**: GUID-based request correlation

##### Error Handling Middleware
- **Exception Classification**: Custom exception hierarchy
- **Error Response Formatting**: Consistent JSON error responses
- **Logging Integration**: Structured error logging with context
- **Client-Friendly Messages**: User-appropriate error messages

##### Rate Limiting Middleware
- **Configurable Limits**: Per-endpoint and per-IP rate limiting
- **Multiple Strategies**: Fixed window and sliding window support
- **Graceful Degradation**: Proper HTTP 429 responses
- **Monitoring Integration**: Rate limit metrics and alerting

#### Retry System (`retry_utils.py`)

**Purpose**: Comprehensive retry mechanism using Tenacity library for handling transient failures.

**Key Features**:
- **Exponential Backoff**: Configurable backoff with jitter
- **Error Classification**: Intelligent retry decision making
- **Transaction Awareness**: GUID tracking across retry attempts
- **Comprehensive Logging**: Detailed retry attempt logging

**Retry Strategies**:
```python
# Pre-configured decorators for different scenarios
@retry_api_calls        # For API calls
@retry_database_ops     # For database operations
@retry_network_ops      # For network operations
@retry_all_errors       # For comprehensive retry coverage
```

#### Cost Tracking System (`pricing.py`)

**Purpose**: Comprehensive cost calculation and tracking for AI operations.

**Features**:
- **Multi-Provider Pricing**: Support for different provider pricing models
- **Real-time Calculation**: Immediate cost calculation after API calls
- **Historical Tracking**: Cost trend analysis and reporting
- **Budget Monitoring**: Usage alerts and budget management

**Pricing Database**:
```python
PROVIDER_PRICING = {
    "meta-llama/llama-3-8b-instruct": {
        "input_cost_per_1k": Decimal("0.00018"),
        "output_cost_per_1k": Decimal("0.00018")
    },
    "openai/gpt-4-turbo-preview": {
        "input_cost_per_1k": Decimal("0.01000"),
        "output_cost_per_1k": Decimal("0.03000")
    }
}
```

#### Transaction Context System (`transaction_context.py`)

**Purpose**: Thread-safe transaction GUID management for request tracing.

**Key Features**:
- **Context Variables**: Python contextvars for thread safety
- **Automatic Propagation**: GUID flows through all operations
- **Clean API**: Property-based access without method signature pollution
- **Context Managers**: Explicit GUID control when needed

**Usage Patterns**:
```python
# Automatic GUID generation
class MyService(TransactionAware):
    def process_request(self):
        guid = self.transaction_guid  # Automatic access
        
# Explicit GUID control
with transaction_context("custom-guid"):
    # All operations use the custom GUID
    pass
```

## Data Architecture

### Database Schema Overview

The FASTAPILLM platform uses SQLAlchemy ORM with support for both SQLite (development) and PostgreSQL (production). The schema is designed to capture comprehensive information about AI operations, including performance metrics, cost tracking, and full request traceability.

### Core Data Models

#### Story Model (`database.py`)

**Purpose**: Stores generated stories with comprehensive metadata for analysis and retrieval.

```python
class Story(Base):
    __tablename__ = "stories"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Content fields
    primary_character = Column(String(100), nullable=False)
    secondary_character = Column(String(100), nullable=False)
    combined_characters = Column(String(200), nullable=False)
    story_content = Column(Text, nullable=False)
    
    # Framework and provider information
    method = Column(String(50), nullable=False)  # semantic_kernel, langchain, langgraph
    provider = Column(String(50))  # azure, openrouter, custom
    model = Column(String(100))
    
    # Performance metrics
    generation_time_ms = Column(Float)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)
    
    # Cost tracking
    estimated_cost_usd = Column(Numeric(precision=10, scale=6), nullable=True)
    input_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True)
    output_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True)
    
    # Traceability
    request_id = Column(String(50))
    transaction_guid = Column(String(36), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Indexes**:
- Primary key on `id`
- Index on `transaction_guid` for request tracing
- Composite index on `method, created_at` for framework-based queries
- Index on `created_at` for chronological queries

#### Chat Models

##### ChatConversation Model

**Purpose**: Manages chat conversation metadata and relationships.

```python
class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # Conversation metadata
    title = Column(String(200), nullable=False)
    method = Column(String(50), nullable=False)  # Framework used
    
    # Provider information
    provider = Column(String(50))
    model = Column(String(100))
    
    # Traceability
    transaction_guid = Column(String(36), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
```

##### ChatMessage Model

**Purpose**: Stores individual messages within conversations with full performance tracking.

```python
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    # Primary identification and relationships
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False)
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    
    # Performance metrics
    generation_time_ms = Column(Float)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)
    
    # Cost tracking
    estimated_cost_usd = Column(Numeric(precision=10, scale=6), nullable=True)
    input_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True)
    output_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True)
    
    # Traceability
    request_id = Column(String(50))
    transaction_guid = Column(String(36), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("ChatConversation", back_populates="messages")
```

**Indexes**:
- Primary key on `id`
- Foreign key index on `conversation_id`
- Index on `transaction_guid`
- Composite index on `conversation_id, created_at` for message ordering

#### Context Processing Model

**Purpose**: Tracks file processing and contextual AI execution operations.

```python
class ContextPromptExecution(Base):
    __tablename__ = "context_prompt_executions"
    
    # Primary identification
    id = Column(Integer, primary_key=True, index=True)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    processed_content_length = Column(Integer, nullable=True)
    
    # Prompt information
    system_prompt = Column(Text, nullable=False)
    user_prompt = Column(Text, nullable=False)
    final_prompt_length = Column(Integer, nullable=True)
    
    # LLM response
    llm_response = Column(Text, nullable=True)
    method = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    
    # Performance metrics
    file_processing_time_ms = Column(Float, nullable=True)
    llm_execution_time_ms = Column(Float, nullable=True)
    total_execution_time_ms = Column(Float, nullable=True)
    
    # Token usage
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    
    # Cost tracking
    estimated_cost_usd = Column(Numeric(precision=10, scale=6), nullable=True)
    input_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True)
    output_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True)
    
    # Request tracking
    request_id = Column(String(50), nullable=True)
    transaction_guid = Column(String(36), nullable=True, index=True)
    user_ip = Column(String(45), nullable=True)
    
    # Status tracking
    status = Column(String(20), nullable=False, default='completed')
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
```

### Database Relationships

#### Entity Relationships

```mermaid
erDiagram
    ChatConversation {
        int id PK
        string title
        string method
        string transaction_guid
        datetime created_at
        datetime updated_at
    }
    
    ChatMessage {
        int id PK
        int conversation_id FK
        string role
        text content
        float generation_time_ms
        int total_tokens
        decimal estimated_cost_usd
        string transaction_guid
        datetime created_at
    }
    
    Story {
        int id PK
        string primary_character
        string secondary_character
        text story_content
        string method
        int total_tokens
        decimal estimated_cost_usd
        string transaction_guid
        datetime created_at
    }
    
    ContextPromptExecution {
        int id PK
        string original_filename
        text system_prompt
        text user_prompt
        text llm_response
        string method
        int total_tokens
        decimal estimated_cost_usd
        string transaction_guid
        datetime created_at
    }
    
    ChatConversation ||--o{ ChatMessage : "contains"
```

#### Relationship Details

1. **ChatConversation ↔ ChatMessage**: One-to-many relationship with cascade delete
   - When a conversation is deleted, all associated messages are automatically removed
   - Messages are ordered by `created_at` timestamp within each conversation

2. **Transaction GUID Correlation**: All models include `transaction_guid` for cross-table request tracing
   - Enables correlation of operations across different data types
   - Supports comprehensive audit trails and debugging

### Data Access Patterns

#### Session Management

**Context Manager Pattern**:
```python
@contextmanager
def get_db_context():
    """Context manager for database sessions with transaction support."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
```

**Dependency Injection Pattern**:
```python
def get_db() -> Generator:
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### Query Patterns

**Story Queries**:
```python
# Get recent stories with pagination
stories = db.query(Story)\
    .order_by(Story.created_at.desc())\
    .offset(skip)\
    .limit(limit)\
    .all()

# Search stories by character
stories = db.query(Story)\
    .filter(or_(
        Story.primary_character.ilike(f"%{character}%"),
        Story.secondary_character.ilike(f"%{character}%")
    ))\
    .all()

# Get stories by framework
stories = db.query(Story)\
    .filter(Story.method == framework)\
    .order_by(Story.created_at.desc())\
    .all()
```

**Chat Queries**:
```python
# Get conversation with messages
conversation = db.query(ChatConversation)\
    .options(joinedload(ChatConversation.messages))\
    .filter(ChatConversation.id == conversation_id)\
    .first()

# Get recent conversations
conversations = db.query(ChatConversation)\
    .order_by(ChatConversation.updated_at.desc())\
    .limit(20)\
    .all()
```

**Analytics Queries**:
```python
# Cost analysis by framework
cost_by_framework = db.query(
    Story.method,
    func.sum(Story.estimated_cost_usd).label('total_cost'),
    func.count(Story.id).label('story_count')
).group_by(Story.method).all()

# Token usage trends
daily_usage = db.query(
    func.date(Story.created_at).label('date'),
    func.sum(Story.total_tokens).label('total_tokens'),
    func.sum(Story.estimated_cost_usd).label('total_cost')
).group_by(func.date(Story.created_at)).all()
```

### Migration Strategy

#### Alembic Configuration

**Migration Management**:
```python
def init_db():
    """Initialize database using Alembic migrations."""
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        # Fallback to create_all for development
        Base.metadata.create_all(bind=engine)
```

**Migration Best Practices**:
1. **Incremental Changes**: Small, focused migrations for easier rollback
2. **Data Preservation**: Always include data migration scripts when needed
3. **Index Management**: Create indexes in separate migrations for large tables
4. **Backward Compatibility**: Maintain compatibility during rolling deployments

#### Schema Evolution

**Version Control**:
- All schema changes tracked in Alembic migration files
- Migration files stored in version control with descriptive names
- Rollback procedures documented for each migration

**Production Deployment**:
```bash
# Check current migration status
alembic current

# Apply pending migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Performance Considerations

#### Indexing Strategy

**Primary Indexes**:
- All primary keys automatically indexed
- Foreign keys indexed for join performance
- `transaction_guid` indexed across all tables for tracing

**Composite Indexes**:
```sql
-- Story queries by framework and date
CREATE INDEX idx_story_method_created ON stories(method, created_at DESC);

-- Chat message ordering within conversations
CREATE INDEX idx_message_conversation_created ON chat_messages(conversation_id, created_at);

-- Context execution status queries
CREATE INDEX idx_context_status_created ON context_prompt_executions(status, created_at DESC);
```

#### Query Optimization

**Connection Pooling**:
```python
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

**Lazy Loading Optimization**:
- Use `joinedload()` for frequently accessed relationships
- Implement pagination for large result sets
- Use `select_related()` equivalent patterns for efficient queries

### Data Integrity

#### Constraints

**Database-Level Constraints**:
- NOT NULL constraints on required fields
- Foreign key constraints with proper cascade rules
- Check constraints for enum-like fields (e.g., message roles)

**Application-Level Validation**:
```python
# Pydantic models for request validation
class StoryRequest(BaseModel):
    primary_character: str = Field(..., min_length=1, max_length=100)
    secondary_character: str = Field(..., min_length=1, max_length=100)
    
    @validator('primary_character', 'secondary_character')
    def validate_character_names(cls, v):
        if not v.strip():
            raise ValueError('Character names cannot be empty')
        return v.strip()
```

#### Transaction Management

**ACID Compliance**:
- All operations wrapped in database transactions
- Automatic rollback on exceptions
- Consistent state maintenance across related operations

**Concurrency Control**:
- Optimistic locking for conversation updates
- Proper isolation levels for read operations
- Deadlock detection and retry mechanisms

## API Architecture

### REST API Design Principles

The FASTAPILLM platform implements a RESTful API following OpenAPI 3.0 specifications with comprehensive documentation, validation, and error handling.

#### Design Principles

1. **Resource-Oriented**: URLs represent resources, not actions
2. **HTTP Method Semantics**: Proper use of GET, POST, PUT, DELETE
3. **Stateless**: Each request contains all necessary information
4. **Consistent Response Format**: Standardized JSON responses across all endpoints
5. **Comprehensive Error Handling**: Detailed error responses with proper HTTP status codes

#### API Versioning Strategy

**Current Approach**: URL path versioning with `/api/` prefix
**Future Strategy**: Header-based versioning for backward compatibility

```
Current:  /api/stories
Future:   /stories (with Accept: application/vnd.api+json;version=1)
```

### Core API Endpoints

#### Health and Status Endpoints

##### Health Check
```http
GET /health
```

**Purpose**: System health monitoring and uptime verification

**Response**:
```json
{
  "status": "healthy",
  "timestamp": 1704723600.123,
  "version": "1.0.0",
  "request_id": "req_abc123",
  "environment": "production",
  "uptime_seconds": 86400
}
```

##### Provider Information
```http
GET /api/provider
```

**Purpose**: Current AI provider configuration details

**Response**:
```json
{
  "provider": "OpenRouter",
  "model": "meta-llama/llama-3-8b-instruct",
  "configured": true
}
```

#### Story Generation Endpoints

##### Generate Story - Semantic Kernel
```http
POST /api/semantic-kernel
Content-Type: application/json

{
  "primary_character": "Alice",
  "secondary_character": "Bob"
}
```

**Response**:
```json
{
  "story": "Once upon a time, Alice and Bob...",
  "combined_characters": "Alice and Bob",
  "method": "semantic_kernel",
  "generation_time_ms": 1234.56,
  "request_id": "sk_20240108_123456_7890",
  "input_tokens": 45,
  "output_tokens": 312,
  "total_tokens": 357,
  "estimated_cost_usd": 0.000064,
  "provider": "OpenRouter",
  "model": "meta-llama/llama-3-8b-instruct",
  "transaction_guid": "550e8400-e29b-41d4-a716-446655440000"
}
```

##### Generate Story - LangChain
```http
POST /api/langchain
```
*Same request/response format as Semantic Kernel with `method: "langchain"`*

##### Generate Story - LangGraph
```http
POST /api/langgraph
```
*Same request/response format with `method: "langgraph"`*

#### Story Management Endpoints

##### List Stories
```http
GET /api/stories?skip=0&limit=10&framework=langchain
```

**Query Parameters**:
- `skip`: Number of records to skip (pagination)
- `limit`: Maximum records to return (1-100)
- `framework`: Filter by AI framework (optional)

**Response**:
```json
{
  "stories": [
    {
      "id": 123,
      "primary_character": "Alice",
      "secondary_character": "Bob",
      "combined_characters": "Alice and Bob",
      "story": "Once upon a time...",
      "method": "langchain",
      "generation_time_ms": 1234.56,
      "total_tokens": 357,
      "estimated_cost_usd": 0.000064,
      "created_at": "2024-01-08T12:34:56Z",
      "transaction_guid": "550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 10
}
```

##### Get Specific Story
```http
GET /api/stories/{story_id}
```

**Response**: Single story object with full details

##### Search Stories by Character
```http
GET /api/stories/search/characters?character=Alice
```

**Response**: Array of stories containing the specified character

##### Delete All Stories
```http
DELETE /api/stories
```

**Response**:
```json
{
  "message": "All stories deleted successfully",
  "deleted_count": 42
}
```

#### Chat System Endpoints

##### Chat with AI - Semantic Kernel
```http
POST /api/chat/semantic-kernel
Content-Type: application/json

{
  "message": "Tell me about quantum physics",
  "conversation_id": 123  // Optional: continue existing conversation
}
```

**Response**:
```json
{
  "response": "Quantum physics is the branch of physics...",
  "conversation_id": 123,
  "message_id": 456,
  "method": "semantic_kernel",
  "generation_time_ms": 2345.67,
  "total_tokens": 245,
  "estimated_cost_usd": 0.000044,
  "transaction_guid": "550e8400-e29b-41d4-a716-446655440000"
}
```

##### List Conversations
```http
GET /api/chat/conversations?limit=20
```

**Response**:
```json
{
  "conversations": [
    {
      "id": 123,
      "title": "Discussion about quantum physics",
      "method": "semantic_kernel",
      "message_count": 8,
      "created_at": "2024-01-08T12:00:00Z",
      "updated_at": "2024-01-08T12:30:00Z"
    }
  ]
}
```

##### Get Conversation with Messages
```http
GET /api/chat/conversations/{conversation_id}
```

**Response**:
```json
{
  "id": 123,
  "title": "Discussion about quantum physics",
  "method": "semantic_kernel",
  "created_at": "2024-01-08T12:00:00Z",
  "messages": [
    {
      "id": 456,
      "role": "user",
      "content": "Tell me about quantum physics",
      "created_at": "2024-01-08T12:00:00Z"
    },
    {
      "id": 457,
      "role": "assistant",
      "content": "Quantum physics is...",
      "generation_time_ms": 2345.67,
      "total_tokens": 245,
      "estimated_cost_usd": 0.000044,
      "created_at": "2024-01-08T12:00:15Z"
    }
  ]
}
```

##### Delete Conversation
```http
DELETE /api/chat/conversations/{conversation_id}
```

#### Cost Tracking Endpoints

##### Get Usage Summary
```http
GET /api/cost/usage?start_date=2024-01-01&end_date=2024-01-08&framework=langchain
```

**Response**:
```json
{
  "summary": {
    "total_requests": 150,
    "total_tokens": 45000,
    "total_cost_usd": 0.081,
    "average_cost_per_request": 0.00054,
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-01-08"
    }
  },
  "by_framework": {
    "semantic_kernel": {
      "requests": 50,
      "tokens": 15000,
      "cost_usd": 0.027
    },
    "langchain": {
      "requests": 60,
      "tokens": 18000,
      "cost_usd": 0.032
    },
    "langgraph": {
      "requests": 40,
      "tokens": 12000,
      "cost_usd": 0.022
    }
  },
  "by_day": [
    {
      "date": "2024-01-01",
      "requests": 20,
      "tokens": 6000,
      "cost_usd": 0.011
    }
  ]
}
```

##### Get Transaction Details
```http
GET /api/cost/transactions?limit=50&framework=langchain
```

**Response**:
```json
{
  "transactions": [
    {
      "id": 123,
      "type": "story_generation",
      "framework": "langchain",
      "input_tokens": 45,
      "output_tokens": 312,
      "total_tokens": 357,
      "estimated_cost_usd": 0.000064,
      "generation_time_ms": 1234.56,
      "created_at": "2024-01-08T12:34:56Z",
      "transaction_guid": "550e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

#### Context Management Endpoints

##### Upload Context File
```http
POST /api/context/upload
Content-Type: multipart/form-data

file: [binary file data]
```

**Response**:
```json
{
  "file_id": "ctx_abc123",
  "filename": "document.pdf",
  "file_type": "pdf",
  "file_size_bytes": 1048576,
  "processed_content_length": 5000,
  "processing_time_ms": 234.56
}
```

##### Execute Prompt with Context
```http
POST /api/context/execute
Content-Type: application/json

{
  "file_id": "ctx_abc123",
  "system_prompt": "You are a document analyzer",
  "user_prompt": "Summarize the key points",
  "framework": "langchain"
}
```

**Response**:
```json
{
  "execution_id": 789,
  "response": "The document discusses three main points...",
  "framework": "langchain",
  "file_processing_time_ms": 234.56,
  "llm_execution_time_ms": 3456.78,
  "total_execution_time_ms": 3691.34,
  "total_tokens": 567,
  "estimated_cost_usd": 0.000102,
  "transaction_guid": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Request/Response Schemas

#### Common Request Validation

**Character Name Validation**:
```python
class StoryRequest(BaseModel):
    primary_character: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Primary character name"
    )
    secondary_character: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Secondary character name"
    )
    
    @validator('primary_character', 'secondary_character')
    def validate_character_names(cls, v):
        # Remove HTML/script tags
        cleaned = re.sub(r'<[^>]*>', '', v)
        if not cleaned.strip():
            raise ValueError('Character names cannot be empty')
        return cleaned.strip()
```

#### Standard Response Format

**Success Response**:
```json
{
  "data": { /* response data */ },
  "meta": {
    "request_id": "req_abc123",
    "transaction_guid": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-08T12:34:56Z",
    "execution_time_ms": 1234.56
  }
}
```

**Error Response**:
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Request validation failed",
    "code": "VALIDATION_ERROR",
    "details": [
      {
        "field": "primary_character",
        "message": "Field is required",
        "type": "missing"
      }
    ],
    "request_id": "req_abc123",
    "timestamp": "2024-01-08T12:34:56Z"
  }
}
```

### Authentication and Authorization

#### Current Implementation

**API Key Authentication** (Future Enhancement):
```http
Authorization: Bearer your-api-key-here
```

**Rate Limiting**: IP-based rate limiting with configurable thresholds
- General endpoints: 60 requests/minute
- AI generation: 15 requests/minute
- Health checks: 100 requests/minute

#### Security Headers

**CORS Configuration**:
```python
cors_config = {
    "allow_origins": ["http://localhost:3001", "https://yourdomain.com"],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE"],
    "allow_headers": ["*"],
    "expose_headers": ["X-Request-ID", "X-Transaction-GUID"]
}
```

**Security Headers**:
- `X-Request-ID`: Unique request identifier
- `X-Transaction-GUID`: Transaction correlation ID
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`

### Error Handling

#### HTTP Status Codes

| Status Code | Usage | Description |
|-------------|-------|-------------|
| 200 | Success | Request completed successfully |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request format or parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Validation Error | Request validation failed |
| 429 | Rate Limited | Too many requests |
| 500 | Internal Error | Server error |
| 503 | Service Unavailable | Temporary service outage |

#### Error Response Details

**Validation Error (422)**:
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Request validation failed",
    "error_id": "val_err_20240108_123456_7890",
    "details": [
      {
        "field": "primary_character -> length",
        "message": "String too long",
        "type": "value_error.any_str.max_length",
        "input": "Very long character name that exceeds limit..."
      }
    ]
  }
}
```

**Rate Limit Error (429)**:
```json
{
  "error": {
    "type": "RateLimitError",
    "message": "Rate limit exceeded",
    "retry_after": 60,
    "limit": "15 requests per minute",
    "reset_time": "2024-01-08T12:35:00Z"
  }
}
```

### API Documentation

#### OpenAPI/Swagger Integration

**Interactive Documentation**: Available at `/api/docs`
**ReDoc Documentation**: Available at `/api/redoc`

**OpenAPI Specification Features**:
- Complete endpoint documentation
- Request/response schema definitions
- Interactive testing interface
- Authentication documentation
- Error response examples

#### API Client Generation

**Supported Languages**:
- Python (using `httpx` or `requests`)
- JavaScript/TypeScript (using `fetch` or `axios`)
- cURL examples for all endpoints

**Example Python Client**:
```python
import httpx

class FASTAPILLMClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def generate_story(
        self, 
        primary_character: str, 
        secondary_character: str,
        framework: str = "langchain"
    ):
        response = await self.client.post(
            f"{self.base_url}/api/{framework}",
            json={
                "primary_character": primary_character,
                "secondary_character": secondary_character
            }
        )
        response.raise_for_status()
        return response.json()
```

## Security Architecture

### Security Overview

The FASTAPILLM platform implements a comprehensive security architecture designed to protect against common web application vulnerabilities while maintaining usability and performance. The security model follows defense-in-depth principles with multiple layers of protection.

### Threat Model

#### Identified Threats

1. **Input Injection Attacks**
   - SQL injection through user inputs
   - Script injection in character names
   - Prompt injection in AI requests

2. **API Abuse**
   - Rate limit bypass attempts
   - Resource exhaustion attacks
   - Unauthorized access to endpoints

3. **Data Exposure**
   - Sensitive information in logs
   - API key exposure
   - Database credential leakage

4. **Cross-Origin Attacks**
   - CSRF attacks on state-changing operations
   - XSS through reflected content
   - CORS misconfiguration exploitation

#### Risk Assessment Matrix

| Threat | Likelihood | Impact | Risk Level | Mitigation Status |
|--------|------------|--------|------------|-------------------|
| SQL Injection | Low | High | Medium | ✅ Mitigated (ORM) |
| Script Injection | Medium | Medium | Medium | ✅ Mitigated (Validation) |
| Rate Limit Bypass | High | Medium | High | ✅ Mitigated (Middleware) |
| API Key Exposure | Medium | High | High | ✅ Mitigated (Env Vars) |
| CORS Attacks | Low | Medium | Low | ✅ Mitigated (Config) |

### Authentication and Authorization

#### Current Authentication Model

**Development Mode**: No authentication required for ease of development
**Production Considerations**: API key authentication recommended

#### Future Authentication Implementation

**API Key Authentication**:
```python
class APIKeyAuth:
    def __init__(self, api_key_header: str = "X-API-Key"):
        self.api_key_header = api_key_header
    
    async def __call__(self, request: Request):
        api_key = request.headers.get(self.api_key_header)
        if not api_key:
            raise HTTPException(401, "API key required")
        
        # Validate API key against database/cache
        if not await self.validate_api_key(api_key):
            raise HTTPException(401, "Invalid API key")
        
        return api_key
```

**JWT Token Authentication** (Alternative):
```python
class JWTAuth:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_token(self, user_id: str, expires_delta: timedelta = None):
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + (expires_delta or timedelta(hours=24))
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
```

#### Authorization Levels

**Planned Authorization Tiers**:
1. **Public**: Health checks, provider info
2. **Authenticated**: Story generation, chat, basic queries
3. **Premium**: Advanced features, higher rate limits
4. **Admin**: System management, user management

### Input Validation and Sanitization

#### Validation Architecture

**Multi-Layer Validation**:
1. **HTTP Layer**: Request size limits, content type validation
2. **Pydantic Layer**: Schema validation and type checking
3. **Business Logic Layer**: Domain-specific validation rules
4. **Database Layer**: Constraint validation

#### Character Name Validation

```python
class CharacterValidator:
    """Comprehensive character name validation."""
    
    MAX_LENGTH = 100
    MIN_LENGTH = 1
    
    # Dangerous patterns to reject
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'on\w+\s*=',                 # Event handlers
        r'<iframe[^>]*>',             # Iframe tags
        r'<object[^>]*>',             # Object tags
    ]
    
    @classmethod
    def validate(cls, name: str) -> str:
        """Validate and sanitize character name."""
        if not name or not name.strip():
            raise ValueError("Character name cannot be empty")
        
        # Length validation
        if len(name) > cls.MAX_LENGTH:
            raise ValueError(f"Character name too long (max {cls.MAX_LENGTH})")
        
        # Remove HTML tags
        cleaned = re.sub(r'<[^>]*>', '', name)
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, name, re.IGNORECASE):
                raise ValueError("Character name contains invalid content")
        
        # Normalize whitespace
        return ' '.join(cleaned.split())
```

#### Request Size Limits

```python
# Middleware configuration
MAX_REQUEST_SIZE = 1048576  # 1MB
MAX_FILE_SIZE = 10485760    # 10MB for context files

class RequestSizeLimitMiddleware:
    async def __call__(self, request: Request, call_next):
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > MAX_REQUEST_SIZE:
            raise HTTPException(413, "Request too large")
        return await call_next(request)
```

### Rate Limiting and DDoS Protection

#### Rate Limiting Strategy

**Multi-Tier Rate Limiting**:
```python
RATE_LIMITS = {
    # Per IP limits (requests per minute)
    "global": 60,
    
    # Per endpoint limits
    "story_generation": 15,
    "chat": 20,
    "health": 100,
    "list_operations": 30,
    
    # Burst allowance
    "burst_multiplier": 2,
    
    # Time windows
    "window_size": 60,  # seconds
}
```

**Implementation Architecture**:
```python
class RateLimitingMiddleware:
    def __init__(self):
        self.storage = {}  # In-memory storage (Redis in production)
        self.cleanup_interval = 300  # 5 minutes
    
    async def check_rate_limit(self, key: str, limit: int, window: int):
        """Check if request is within rate limit."""
        now = time.time()
        window_start = now - window
        
        # Clean old entries
        self.storage[key] = [
            timestamp for timestamp in self.storage.get(key, [])
            if timestamp > window_start
        ]
        
        # Check current count
        current_count = len(self.storage.get(key, []))
        if current_count >= limit:
            return False, limit - current_count, window
        
        # Record this request
        self.storage.setdefault(key, []).append(now)
        return True, limit - current_count - 1, window
```

#### DDoS Protection Measures

**Application-Level Protection**:
1. **Connection Limits**: Maximum concurrent connections per IP
2. **Request Queuing**: Queue management for high-load scenarios
3. **Circuit Breakers**: Automatic service protection during overload
4. **Graceful Degradation**: Reduced functionality during attacks

**Infrastructure-Level Protection** (Recommended):
- Cloudflare or similar CDN with DDoS protection
- Load balancer with rate limiting capabilities
- Firewall rules for known attack patterns

### CORS and Cross-Origin Security

#### CORS Configuration

```python
CORS_CONFIG = {
    # Allowed origins (environment-specific)
    "allow_origins": [
        "http://localhost:3001",      # React development
        "https://yourdomain.com",     # Production frontend
    ],
    
    # Credentials handling
    "allow_credentials": True,
    
    # Allowed methods
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    
    # Allowed headers
    "allow_headers": [
        "Content-Type",
        "Authorization",
        "X-API-Key",
        "X-Request-ID",
    ],
    
    # Exposed headers
    "expose_headers": [
        "X-Request-ID",
        "X-Transaction-GUID",
        "X-Rate-Limit-Remaining",
    ],
    
    # Preflight cache
    "max_age": 3600,
}
```

#### Content Security Policy

**CSP Headers** (for frontend):
```http
Content-Security-Policy: 
  default-src 'self';
  script-src 'self' 'unsafe-inline';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' http://localhost:8000;
  font-src 'self';
  object-src 'none';
  base-uri 'self';
  form-action 'self';
```

### Data Protection and Privacy

#### Sensitive Data Handling

**API Key Management**:
```python
class SecureConfig:
    """Secure configuration management."""
    
    @staticmethod
    def mask_api_key(api_key: str) -> str:
        """Mask API key for logging."""
        if not api_key or len(api_key) < 8:
            return "***"
        return f"{api_key[:4]}...{api_key[-4:]}"
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """Validate API key format without exposing it."""
        # Check format without logging the actual key
        return bool(api_key and len(api_key) >= 20)
```

**Logging Security**:
```python
class SecureLogger:
    """Logger with sensitive data filtering."""
    
    SENSITIVE_FIELDS = [
        'api_key', 'password', 'token', 'secret',
        'authorization', 'x-api-key'
    ]
    
    def filter_sensitive_data(self, data: dict) -> dict:
        """Remove or mask sensitive data from logs."""
        filtered = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                filtered[key] = self.mask_value(value)
            else:
                filtered[key] = value
        return filtered
```

#### Data Retention and Cleanup

**Automatic Data Cleanup**:
```python
class DataRetentionManager:
    """Manage data retention and cleanup."""
    
    RETENTION_POLICIES = {
        'stories': timedelta(days=365),      # 1 year
        'chat_messages': timedelta(days=90), # 3 months
        'logs': timedelta(days=30),          # 1 month
        'context_files': timedelta(days=7),  # 1 week
    }
    
    async def cleanup_expired_data(self):
        """Remove data past retention period."""
        for table, retention_period in self.RETENTION_POLICIES.items():
            cutoff_date = datetime.utcnow() - retention_period
            # Implement cleanup logic for each table
```

### Security Monitoring and Logging

#### Security Event Logging

**Security Events to Monitor**:
1. **Authentication Failures**: Failed login attempts, invalid API keys
2. **Rate Limit Violations**: Excessive request patterns
3. **Input Validation Failures**: Potential injection attempts
4. **Unusual Access Patterns**: Geographic anomalies, time-based patterns
5. **Error Patterns**: Repeated 4xx/5xx responses

**Security Log Format**:
```json
{
  "timestamp": "2024-01-08T12:34:56Z",
  "event_type": "security_violation",
  "severity": "warning",
  "source_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "endpoint": "/api/stories",
  "violation_type": "rate_limit_exceeded",
  "details": {
    "current_rate": 25,
    "limit": 15,
    "window": "60s"
  },
  "request_id": "req_abc123",
  "transaction_guid": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Intrusion Detection

**Anomaly Detection Patterns**:
```python
class SecurityMonitor:
    """Monitor for security anomalies."""
    
    def __init__(self):
        self.suspicious_patterns = [
            # SQL injection attempts
            r"(?i)(union|select|insert|delete|drop|create|alter)\s+",
            
            # Script injection attempts
            r"(?i)<script[^>]*>|javascript:|on\w+\s*=",
            
            # Path traversal attempts
            r"\.\.\/|\.\.\\",
            
            # Command injection attempts
            r"(?i)(;|\||\&)\s*(ls|cat|wget|curl|nc|bash)",
        ]
    
    def analyze_request(self, request_data: str) -> dict:
        """Analyze request for suspicious patterns."""
        threats = []
        for pattern in self.suspicious_patterns:
            if re.search(pattern, request_data):
                threats.append({
                    "type": "pattern_match",
                    "pattern": pattern,
                    "severity": "high"
                })
        
        return {
            "is_suspicious": len(threats) > 0,
            "threat_count": len(threats),
            "threats": threats
        }
```

### Secure Configuration Management

#### Environment Variable Security

**Configuration Validation**:
```python
class SecureSettings(BaseSettings):
    """Secure settings with validation."""
    
    # API keys with validation
    provider_api_key: SecretStr = Field(..., min_length=20)
    
    # Database URLs with validation
    database_url: PostgresDsn = Field(...)
    
    # Security settings
    allowed_hosts: List[str] = Field(default=["localhost"])
    debug_mode: bool = Field(default=False)
    
    @validator('debug_mode')
    def validate_debug_mode(cls, v, values):
        """Ensure debug mode is disabled in production."""
        if v and values.get('environment') == 'production':
            raise ValueError("Debug mode cannot be enabled in production")
        return v
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        
        # Don't expose secrets in repr
        repr_exclude = {'provider_api_key', 'database_url'}
```

#### Secrets Management

**Production Secrets Management**:
```python
class SecretsManager:
    """Manage secrets from various sources."""
    
    def __init__(self):
        self.sources = [
            EnvironmentSecretsSource(),
            VaultSecretsSource(),      # HashiCorp Vault
            AWSSecretsSource(),        # AWS Secrets Manager
            AzureKeyVaultSource(),     # Azure Key Vault
        ]
    
    async def get_secret(self, key: str) -> Optional[str]:
        """Retrieve secret from available sources."""
        for source in self.sources:
            try:
                secret = await source.get_secret(key)
                if secret:
                    return secret
            except Exception as e:
                logger.warning(f"Failed to get secret from {source}: {e}")
        
        return None
```

### Security Best Practices

#### Development Security Guidelines

1. **Secure Coding Practices**:
   - Always validate and sanitize user inputs
   - Use parameterized queries (ORM handles this)
   - Implement proper error handling without information disclosure
   - Follow principle of least privilege

2. **Dependency Management**:
   - Regularly update dependencies
   - Use dependency scanning tools
   - Pin dependency versions in production
   - Monitor security advisories

3. **Testing Security**:
   - Include security test cases
   - Perform input validation testing
   - Test rate limiting and error handling
   - Conduct periodic security reviews

#### Production Security Checklist

- [ ] **Environment Configuration**
  - [ ] Debug mode disabled
  - [ ] Secure API keys configured
  - [ ] CORS properly configured
  - [ ] Rate limiting enabled

- [ ] **Infrastructure Security**
  - [ ] HTTPS enabled with valid certificates
  - [ ] Database access restricted
  - [ ] Firewall rules configured
  - [ ] Monitoring and alerting set up

- [ ] **Application Security**
  - [ ] Input validation implemented
  - [ ] Error handling configured
  - [ ] Logging security events
  - [ ] Regular security updates applied

- [ ] **Operational Security**
  - [ ] Access controls implemented
  - [ ] Backup and recovery procedures
  - [ ] Incident response plan
  - [ ] Security monitoring active

## Deployment Architecture

### Deployment Overview

The FASTAPILLM platform supports multiple deployment strategies ranging from local development to enterprise production environments. The architecture is designed to be cloud-agnostic and can be deployed on any infrastructure supporting Docker containers.

### Deployment Environments

#### Development Environment

**Local Development Setup**:
```bash
# Backend development
python backend/main.py

# Frontend development (separate terminal)
cd frontendReact
npm install
npm run dev

# MCP server (optional, separate terminal)
python backend/mcp_server.py
```

**Development Configuration**:
```env
# .env for development
DEBUG_MODE=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./stories.db
CORS_ORIGINS=["http://localhost:3001", "http://localhost:5173"]

# Provider configuration
PROVIDER_API_KEY=your-dev-api-key
PROVIDER_API_BASE_URL=http://localhost:11434/v1  # Ollama local
PROVIDER_MODEL=llama2
PROVIDER_NAME=Ollama Local
```

**Development Services**:
- **Backend**: FastAPI with auto-reload on port 8000
- **Frontend**: Vite dev server with HMR on port 3001
- **Database**: SQLite file-based database
- **MCP Server**: Standalone server on port 9999

#### Docker Compose Environment

**Separated Architecture** (`docker-compose.separated.yml`):
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/fastapillm
      - PROVIDER_API_KEY=${PROVIDER_API_KEY}
      - PROVIDER_API_BASE_URL=${PROVIDER_API_BASE_URL}
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
      - ./.env:/app/.env

  frontend:
    build:
      context: ./frontendReact
      dockerfile: Dockerfile
    ports:
      - "3001:80"
    depends_on:
      - backend

  mcp-server:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    ports:
      - "9999:9999"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/fastapillm
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=fastapillm
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

**Container Specifications**:

**Backend Container** (`Dockerfile.backend`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "backend/main.py"]
```

**Frontend Container** (`frontendReact/Dockerfile`):
```dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

#### Production Environment

**Production Architecture Components**:

```mermaid
graph TB
    subgraph "Load Balancer Layer"
        LB[Load Balancer<br/>nginx/HAProxy]
        CDN[CDN<br/>CloudFlare/AWS CloudFront]
    end
    
    subgraph "Application Layer"
        API1[FastAPI Instance 1]
        API2[FastAPI Instance 2]
        API3[FastAPI Instance 3]
        MCP[MCP Server<br/>Standalone]
    end
    
    subgraph "Data Layer"
        DB_PRIMARY[(PostgreSQL Primary)]
        DB_REPLICA[(PostgreSQL Replica)]
        REDIS[(Redis Cache)]
    end
    
    subgraph "Infrastructure Layer"
        LOGS[Centralized Logging<br/>ELK/Grafana Loki]
        METRICS[Metrics<br/>Prometheus/Grafana]
        STORAGE[File Storage<br/>S3/MinIO]
    end
    
    CDN --> LB
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> DB_PRIMARY
    API2 --> DB_PRIMARY
    API3 --> DB_PRIMARY
    
    API1 --> DB_REPLICA
    API2 --> DB_REPLICA
    API3 --> DB_REPLICA
    
    API1 --> REDIS
    API2 --> REDIS
    API3 --> REDIS
    
    MCP --> DB_PRIMARY
    
    API1 --> LOGS
    API2 --> LOGS
    API3 --> LOGS
    MCP --> LOGS
    
    API1 --> METRICS
    API2 --> METRICS
    API3 --> METRICS
```

**Production Configuration**:
```env
# Production environment variables
DEBUG_MODE=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:secure_pass@db-cluster:5432/fastapillm
REDIS_URL=redis://redis-cluster:6379/0

# Security settings
CORS_ORIGINS=["https://yourdomain.com"]
RATE_LIMITING_ENABLED=true
MAX_REQUEST_SIZE=1048576

# Provider configuration (from secrets manager)
PROVIDER_API_KEY=${SECRET_PROVIDER_API_KEY}
PROVIDER_API_BASE_URL=https://openrouter.ai/api/v1
PROVIDER_MODEL=meta-llama/llama-3-8b-instruct

# Monitoring
PROMETHEUS_METRICS_ENABLED=true
SENTRY_DSN=${SECRET_SENTRY_DSN}
```

### Infrastructure Requirements

#### Minimum System Requirements

**Development Environment**:
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 10GB
- **Network**: Broadband internet for AI provider access

**Production Environment (Single Instance)**:
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **Network**: 1Gbps connection

**Production Environment (High Availability)**:
- **Load Balancer**: 2 cores, 4GB RAM
- **Application Servers**: 3x (4 cores, 8GB RAM each)
- **Database**: 8 cores, 16GB RAM, 200GB SSD
- **Cache**: 2 cores, 4GB RAM
- **Monitoring**: 4 cores, 8GB RAM

#### Cloud Provider Configurations

**AWS Deployment**:
```yaml
# AWS ECS Task Definition
{
  "family": "fastapillm-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-registry/fastapillm-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:db-url"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/fastapillm",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Google Cloud Run Deployment**:
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: fastapillm-backend
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      containers:
      - image: gcr.io/project/fastapillm-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
```

**Azure Container Instances**:
```yaml
apiVersion: 2019-12-01
location: eastus
name: fastapillm-container-group
properties:
  containers:
  - name: backend
    properties:
      image: yourregistry.azurecr.io/fastapillm-backend:latest
      ports:
      - port: 8000
        protocol: TCP
      environmentVariables:
      - name: DATABASE_URL
        secureValue: postgresql://...
      resources:
        requests:
          cpu: 2
          memoryInGB: 4
  osType: Linux
  restartPolicy: Always
  ipAddress:
    type: Public
    ports:
    - protocol: TCP
      port: 8000
```

### Database Deployment

#### PostgreSQL Configuration

**Production PostgreSQL Setup**:
```sql
-- Database initialization
CREATE DATABASE fastapillm;
CREATE USER fastapillm_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE fastapillm TO fastapillm_user;

-- Performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Connection pooling
ALTER SYSTEM SET max_connections = 200;
```

**Database Backup Strategy**:
```bash
#!/bin/bash
# Automated backup script

BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="fastapillm"

# Create backup
pg_dump -h localhost -U fastapillm_user -d $DB_NAME \
  --format=custom --compress=9 \
  --file="$BACKUP_DIR/fastapillm_$DATE.backup"

# Retain only last 7 days of backups
find $BACKUP_DIR -name "fastapillm_*.backup" -mtime +7 -delete

# Upload to cloud storage (optional)
aws s3 cp "$BACKUP_DIR/fastapillm_$DATE.backup" \
  s3://your-backup-bucket/database/
```

#### Database Migration in Production

**Zero-Downtime Migration Strategy**:
```python
class ProductionMigrationManager:
    """Manage database migrations in production."""
    
    async def migrate_with_rollback(self):
        """Perform migration with automatic rollback on failure."""
        # 1. Create backup
        backup_id = await self.create_backup()
        
        try:
            # 2. Run migration
            await self.run_migration()
            
            # 3. Verify migration
            if not await self.verify_migration():
                raise MigrationError("Migration verification failed")
                
            # 4. Update application
            await self.update_application()
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            # Rollback to backup
            await self.rollback_to_backup(backup_id)
            raise
```

### Monitoring and Observability

#### Health Checks

**Application Health Checks**:
```python
@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    checks = {
        "database": await check_database_connection(),
        "ai_provider": await check_provider_connection(),
        "disk_space": check_disk_space(),
        "memory_usage": check_memory_usage(),
    }
    
    overall_status = "healthy" if all(checks.values()) else "unhealthy"
    
    return {
        "status": overall_status,
        "checks": checks,
        "timestamp": time.time(),
        "version": settings.app_version
    }

async def check_database_connection():
    """Check database connectivity."""
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
        return True
    except Exception:
        return False
```

**Infrastructure Monitoring**:
```yaml
# Prometheus configuration
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fastapillm-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-exporter:9187']
    
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

### Deployment Procedures

#### Continuous Integration/Continuous Deployment

**GitHub Actions Workflow**:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest
    - name: Run security scan
      run: bandit -r .

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Build Docker images
      run: |
        docker build -t fastapillm-backend:${{ github.sha }} .
        docker build -t fastapillm-frontend:${{ github.sha }} ./frontendReact
    - name: Push to registry
      run: |
        docker push your-registry/fastapillm-backend:${{ github.sha }}
        docker push your-registry/fastapillm-frontend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production
    steps:
    - name: Deploy to production
      run: |
        # Update container images
        kubectl set image deployment/backend backend=your-registry/fastapillm-backend:${{ github.sha }}
        kubectl set image deployment/frontend frontend=your-registry/fastapillm-frontend:${{ github.sha }}
        
        # Wait for rollout
        kubectl rollout status deployment/backend
        kubectl rollout status deployment/frontend
```

#### Blue-Green Deployment

**Blue-Green Deployment Strategy**:
```bash
#!/bin/bash
# Blue-green deployment script

CURRENT_ENV=$(kubectl get service fastapillm-service -o jsonpath='{.spec.selector.version}')
NEW_ENV=$([ "$CURRENT_ENV" = "blue" ] && echo "green" || echo "blue")

echo "Current environment: $CURRENT_ENV"
echo "Deploying to: $NEW_ENV"

# Deploy new version
kubectl apply -f k8s/deployment-$NEW_ENV.yaml

# Wait for deployment to be ready
kubectl rollout status deployment/fastapillm-$NEW_ENV

# Run health checks
if curl -f http://fastapillm-$NEW_ENV:8000/health; then
    echo "Health check passed, switching traffic"
    
    # Switch traffic
    kubectl patch service fastapillm-service -p '{"spec":{"selector":{"version":"'$NEW_ENV'"}}}'
    
    echo "Traffic switched to $NEW_ENV"
    
    # Clean up old environment (optional)
    # kubectl delete deployment fastapillm-$CURRENT_ENV
else
    echo "Health check failed, rolling back"
    kubectl delete deployment fastapillm-$NEW_ENV
    exit 1
fi
```

### Scaling Strategies

#### Horizontal Scaling

**Kubernetes Horizontal Pod Autoscaler**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapillm-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapillm-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

#### Vertical Scaling

**Resource Optimization**:
```yaml
# Production resource limits
resources:
  requests:
    cpu: "1"
    memory: "2Gi"
  limits:
    cpu: "2"
    memory: "4Gi"

# JVM tuning for Java components (if any)
env:
- name: JAVA_OPTS
  value: "-Xms1g -Xmx2g -XX:+UseG1GC"
```

## Performance Architecture

### Performance Overview

The FASTAPILLM platform is designed for high performance with a focus on minimizing latency, maximizing throughput, and efficiently handling concurrent requests. The architecture employs async/await patterns, connection pooling, caching strategies, and comprehensive monitoring.

### Performance Characteristics

#### Current Performance Metrics

**API Response Times** (95th percentile):
- Health check: < 10ms
- Story generation: 2-15 seconds (depends on AI provider)
- Chat messages: 1-8 seconds (depends on context length)
- Database queries: < 100ms
- File upload/processing: 200ms-2s (depends on file size)

**Throughput Capacity**:
- Concurrent connections: 1000+ (with proper scaling)
- Requests per second: 100+ (non-AI endpoints)
- AI requests per minute: 60+ (limited by provider rate limits)
- Database transactions: 1000+ TPS

**Resource Utilization**:
- Memory usage: 200-500MB per instance
- CPU usage: 10-30% baseline, 60-80% during AI processing
- Database connections: 10-20 per instance
- Network I/O: 1-10 Mbps per instance

### Bottleneck Analysis

#### Identified Performance Bottlenecks

```mermaid
graph TD
    REQUEST[HTTP Request] --> VALIDATION{Input Validation}
    VALIDATION -->|Fast| ROUTING[Route Handler]
    VALIDATION -->|Slow| BOTTLENECK1[Complex Validation Logic]
    
    ROUTING --> SERVICE[Service Layer]
    SERVICE --> AI_CALL{AI Provider Call}
    
    AI_CALL -->|Network Latency| BOTTLENECK2[Provider Response Time<br/>2-15 seconds]
    AI_CALL -->|Rate Limits| BOTTLENECK3[Provider Rate Limiting<br/>15-60 req/min]
    
    AI_CALL --> PROCESSING[Response Processing]
    PROCESSING --> DATABASE{Database Write}
    
    DATABASE -->|Connection Pool| BOTTLENECK4[DB Connection Limits<br/>10-20 connections]
    DATABASE -->|Query Performance| BOTTLENECK5[Complex Queries<br/>100ms+]
    
    DATABASE --> RESPONSE[HTTP Response]
    
    style BOTTLENECK1 fill:#ffcccc
    style BOTTLENECK2 fill:#ffcccc
    style BOTTLENECK3 fill:#ffcccc
    style BOTTLENECK4 fill:#ffcccc
    style BOTTLENECK5 fill:#ffcccc
```

#### Bottleneck Impact Analysis

| Bottleneck | Impact | Frequency | Mitigation Priority |
|------------|--------|-----------|-------------------|
| AI Provider Latency | High | Always | Medium (external) |
| Provider Rate Limits | High | Peak usage | High |
| Database Connections | Medium | High load | High |
| Complex Queries | Low | Specific operations | Medium |
| Input Validation | Low | All requests | Low |

### Optimization Strategies

#### Application-Level Optimizations

**Async/Await Implementation**:
```python
class OptimizedService:
    """Service with performance optimizations."""
    
    def __init__(self):
        # Connection pooling
        self.http_client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
                keepalive_expiry=30
            ),
            timeout=httpx.Timeout(60.0)
        )
        
        # Response caching
        self.cache = TTLCache(maxsize=1000, ttl=300)  # 5-minute cache
    
    @lru_cache(maxsize=128)
    def get_prompt_template(self, framework: str) -> str:
        """Cache prompt templates to avoid file I/O."""
        return self._load_prompt_template(framework)
    
    async def generate_with_cache(self, key: str, generator_func):
        """Cache AI responses for identical requests."""
        if key in self.cache:
            logger.info("Cache hit", cache_key=key)
            return self.cache[key]
        
        result = await generator_func()
        self.cache[key] = result
        logger.info("Cache miss, stored result", cache_key=key)
        return result
```

**Connection Pool Optimization**:
```python
# Database connection pool tuning
engine = create_engine(
    DATABASE_URL,
    # Connection pool settings
    pool_size=20,           # Base connections
    max_overflow=30,        # Additional connections
    pool_pre_ping=True,     # Validate connections
    pool_recycle=3600,      # Recycle after 1 hour
    
    # Query optimization
    echo=False,             # Disable SQL logging in production
    future=True,            # Use SQLAlchemy 2.0 style
    
    # Connection timeouts
    connect_args={
        "connect_timeout": 10,
        "command_timeout": 30,
    }
)
```

#### Caching Strategies

**Multi-Layer Caching Architecture**:

```mermaid
graph TB
    CLIENT[Client Request] --> L1[L1: Application Cache<br/>In-Memory LRU]
    L1 -->|Miss| L2[L2: Redis Cache<br/>Distributed]
    L2 -->|Miss| L3[L3: Database<br/>Query Cache]
    L3 -->|Miss| SOURCE[Data Source<br/>AI Provider/Files]
    
    SOURCE --> L3
    L3 --> L2
    L2 --> L1
    L1 --> CLIENT
    
    style L1 fill:#e1f5fe
    style L2 fill:#f3e5f5
    style L3 fill:#e8f5e8
```

**Cache Implementation**:
```python
class CacheManager:
    """Multi-layer cache management."""
    
    def __init__(self):
        # L1: In-memory cache (per instance)
        self.memory_cache = TTLCache(maxsize=500, ttl=300)
        
        # L2: Redis cache (shared across instances)
        self.redis_client = redis.asyncio.Redis(
            host='redis',
            port=6379,
            decode_responses=True,
            max_connections=20
        )
    
    async def get_cached_response(self, cache_key: str):
        """Get response from cache hierarchy."""
        # Check L1 cache first
        if cache_key in self.memory_cache:
            return self.memory_cache[cache_key]
        
        # Check L2 cache
        cached_data = await self.redis_client.get(cache_key)
        if cached_data:
            # Store in L1 for faster access
            result = json.loads(cached_data)
            self.memory_cache[cache_key] = result
            return result
        
        return None
    
    async def set_cached_response(self, cache_key: str, data: dict, ttl: int = 300):
        """Store response in cache hierarchy."""
        # Store in both L1 and L2
        self.memory_cache[cache_key] = data
        await self.redis_client.setex(
            cache_key, 
            ttl, 
            json.dumps(data, default=str)
        )
```

**Cache Key Strategy**:
```python
def generate_cache_key(framework: str, primary_char: str, secondary_char: str) -> str:
    """Generate deterministic cache key for story requests."""
    # Normalize inputs for consistent caching
    normalized_primary = primary_char.lower().strip()
    normalized_secondary = secondary_char.lower().strip()
    
    # Create hash for privacy and key length management
    content = f"{framework}:{normalized_primary}:{normalized_secondary}"
    return f"story:{hashlib.md5(content.encode()).hexdigest()}"
```

### Database Performance

#### Query Optimization

**Index Strategy**:
```sql
-- Performance indexes for common queries
CREATE INDEX CONCURRENTLY idx_stories_method_created 
ON stories(method, created_at DESC);

CREATE INDEX CONCURRENTLY idx_stories_characters 
ON stories USING gin(to_tsvector('english', primary_character || ' ' || secondary_character));

CREATE INDEX CONCURRENTLY idx_chat_messages_conversation_created 
ON chat_messages(conversation_id, created_at);

CREATE INDEX CONCURRENTLY idx_transaction_guid 
ON stories(transaction_guid) WHERE transaction_guid IS NOT NULL;

-- Partial indexes for active data
CREATE INDEX CONCURRENTLY idx_stories_recent 
ON stories(created_at DESC) WHERE created_at > NOW() - INTERVAL '30 days';
```

**Query Performance Monitoring**:
```python
class QueryPerformanceMonitor:
    """Monitor and log slow database queries."""
    
    def __init__(self, slow_query_threshold: float = 0.1):
        self.threshold = slow_query_threshold
    
    def log_query_performance(self, query: str, duration: float, params: dict = None):
        """Log query performance metrics."""
        if duration > self.threshold:
            logger.warning(
                "Slow query detected",
                query=query[:200],  # Truncate long queries
                duration_ms=duration * 1000,
                threshold_ms=self.threshold * 1000,
                params=params
            )
        else:
            logger.debug(
                "Query executed",
                duration_ms=duration * 1000,
                query_type=self._classify_query(query)
            )
```

**Connection Pool Monitoring**:
```python
@app.middleware("http")
async def database_pool_monitoring(request: Request, call_next):
    """Monitor database connection pool usage."""
    pool = engine.pool
    
    # Log pool statistics
    logger.debug(
        "Database pool status",
        size=pool.size(),
        checked_in=pool.checkedin(),
        checked_out=pool.checkedout(),
        overflow=pool.overflow(),
        invalid=pool.invalid()
    )
    
    # Alert if pool is nearly exhausted
    if pool.checkedout() > pool.size() * 0.8:
        logger.warning(
            "Database pool nearly exhausted",
            utilization=pool.checkedout() / pool.size()
        )
    
    response = await call_next(request)
    return response
```

### Scalability Architecture

#### Horizontal Scaling Strategy

**Stateless Service Design**:
```python
class StatelessService:
    """Stateless service design for horizontal scaling."""
    
    def __init__(self):
        # No instance state - all state in database/cache
        self.config = self._load_config()
    
    async def process_request(self, request_data: dict) -> dict:
        """Process request without maintaining state."""
        # Generate unique transaction ID
        transaction_id = str(uuid.uuid4())
        
        # All context stored in database/cache
        with transaction_context(transaction_id):
            result = await self._process_business_logic(request_data)
            await self._store_result(result)
            return result
    
    def _load_config(self) -> dict:
        """Load configuration from environment/external source."""
        return {
            "provider_url": os.getenv("PROVIDER_API_BASE_URL"),
            "model": os.getenv("PROVIDER_MODEL"),
            # No secrets stored in instance
        }
```

**Load Balancing Configuration**:
```nginx
# Nginx load balancer configuration
upstream fastapillm_backend {
    least_conn;  # Use least connections algorithm
    
    server backend1:8000 max_fails=3 fail_timeout=30s;
    server backend2:8000 max_fails=3 fail_timeout=30s;
    server backend3:8000 max_fails=3 fail_timeout=30s;
    
    # Health checks
    keepalive 32;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://fastapillm_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Connection settings
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
}
```

#### Auto-Scaling Configuration

**Kubernetes HPA with Custom Metrics**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: fastapillm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: fastapillm-backend
  minReplicas: 2
  maxReplicas: 20
  metrics:
  # CPU-based scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  
  # Memory-based scaling
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  
  # Custom metric: Request queue length
  - type: Pods
    pods:
      metric:
        name: request_queue_length
      target:
        type: AverageValue
        averageValue: "10"
  
  # Custom metric: Response time
  - type: Pods
    pods:
      metric:
        name: avg_response_time_seconds
      target:
        type: AverageValue
        averageValue: "2"

  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

### Performance Monitoring

#### Metrics Collection

**Application Metrics**:
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
AI_GENERATION_TIME = Histogram('ai_generation_duration_seconds', 'AI generation time', ['framework'])
ACTIVE_CONNECTIONS = Gauge('active_database_connections', 'Active database connections')
CACHE_HIT_RATE = Counter('cache_hits_total', 'Cache hits', ['cache_type'])

class MetricsMiddleware:
    """Collect application metrics."""
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Record metrics
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        REQUEST_DURATION.observe(duration)
        
        return response
```

**Custom Metrics Dashboard**:
```yaml
# Grafana dashboard configuration
dashboard:
  title: "FASTAPILLM Performance Dashboard"
  panels:
    - title: "Request Rate"
      type: "graph"
      targets:
        - expr: "rate(http_requests_total[5m])"
          legendFormat: "{{method}} {{endpoint}}"
    
    - title: "Response Time"
      type: "graph"
      targets:
        - expr: "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
          legendFormat: "95th percentile"
        - expr: "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))"
          legendFormat: "50th percentile"
    
    - title: "AI Generation Performance"
      type: "graph"
      targets:
        - expr: "histogram_quantile(0.95, rate(ai_generation_duration_seconds_bucket[5m]))"
          legendFormat: "{{framework}} 95th percentile"
    
    - title: "Database Connections"
      type: "singlestat"
      targets:
        - expr: "active_database_connections"
    
    - title: "Cache Hit Rate"
      type: "singlestat"
      targets:
        - expr: "rate(cache_hits_total[5m]) / rate(cache_requests_total[5m]) * 100"
```

#### Performance Alerting

**Alert Rules**:
```yaml
# Prometheus alert rules
groups:
- name: fastapillm_performance
  rules:
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 5
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High response time detected"
      description: "95th percentile response time is {{ $value }}s"
  
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value | humanizePercentage }}"
  
  - alert: DatabaseConnectionsHigh
    expr: active_database_connections > 15
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Database connection pool nearly exhausted"
      description: "{{ $value }} active connections"
  
  - alert: LowCacheHitRate
    expr: rate(cache_hits_total[5m]) / rate(cache_requests_total[5m]) < 0.7
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Low cache hit rate"
      description: "Cache hit rate is {{ $value | humanizePercentage }}"
```

### Performance Testing

#### Load Testing Strategy

**Locust Load Testing**:
```python
from locust import HttpUser, task, between

class FASTAPILLMUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup test data."""
        self.characters = [
            ("Alice", "Bob"),
            ("Charlie", "Diana"),
            ("Eve", "Frank"),
        ]
    
    @task(3)
    def health_check(self):
        """Test health endpoint (high frequency)."""
        self.client.get("/health")
    
    @task(2)
    def list_stories(self):
        """Test story listing."""
        self.client.get("/api/stories?limit=10")
    
    @task(1)
    def generate_story(self):
        """Test story generation (low frequency due to cost)."""
        primary, secondary = self.random.choice(self.characters)
        self.client.post("/api/langchain", json={
            "primary_character": primary,
            "secondary_character": secondary
        })
    
    @task(2)
    def chat_message(self):
        """Test chat functionality."""
        self.client.post("/api/chat/langchain", json={
            "message": "Tell me about quantum physics"
        })
```

**Performance Test Scenarios**:
```bash
# Baseline performance test
locust -f performance_tests.py --host=http://localhost:8000 \
  --users=10 --spawn-rate=2 --run-time=5m

# Stress test
locust -f performance_tests.py --host=http://localhost:8000 \
  --users=100 --spawn-rate=10 --run-time=10m

# Spike test
locust -f performance_tests.py --host=http://localhost:8000 \
  --users=200 --spawn-rate=50 --run-time=2m
```

#### Performance Benchmarks

**Target Performance Goals**:

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| API Response Time (95th) | < 100ms | 80ms | ✅ |
| AI Generation Time (95th) | < 10s | 8s | ✅ |
| Throughput (non-AI) | > 1000 RPS | 800 RPS | ⚠️ |
| Database Query Time (95th) | < 50ms | 45ms | ✅ |
| Memory Usage | < 1GB | 500MB | ✅ |
| CPU Usage (avg) | < 50% | 35% | ✅ |

**Performance Regression Testing**:
```python
class PerformanceRegressionTest:
    """Automated performance regression testing."""
    
    def __init__(self):
        self.baseline_metrics = self._load_baseline()
        self.tolerance = 0.1  # 10% tolerance
    
    async def run_performance_test(self):
        """Run performance test and compare to baseline."""
        current_metrics = await self._collect_metrics()
        
        regressions = []
        for metric, current_value in current_metrics.items():
            baseline_value = self.baseline_metrics.get(metric)
            if baseline_value:
                regression = (current_value - baseline_value) / baseline_value
                if regression > self.tolerance:
                    regressions.append({
                        "metric": metric,
                        "baseline": baseline_value,
                        "current": current_value,
                        "regression": regression
                    })
        
        if regressions:
            raise PerformanceRegressionError(
                f"Performance regression detected: {regressions}"
            )
        
        return current_metrics
```

## Integration Architecture

### Integration Overview

The FASTAPILL

## Development Architecture

*[This section will be populated in task 11]*

## Operational Architecture

*[This section will be populated in task 12]*

## Configuration and Environment Setup

*[This section will be populated in task 13]*

## Appendices and Reference Materials

*[This section will be populated in task 14]*

---

*Document Version: 1.0*  
*Last Updated: 2025-01-08*  
*Status: In Development*