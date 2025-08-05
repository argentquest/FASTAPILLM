# Technical Architecture Document Design

## Overview

The Technical Architecture Document will be a comprehensive reference document that captures the complete architecture of the FASTAPILLM - AI Content Generation Platform. This document will serve as the definitive guide for understanding the system's structure, components, data flow, and technical decisions.

The platform is a modern, enterprise-grade AI content generation system featuring:
- Multi-framework AI support (Semantic Kernel, LangChain, LangGraph)
- MCP (Model Context Protocol) integration for external tool access
- Full-stack web interface with React frontend and FastAPI backend
- Comprehensive cost tracking and performance monitoring
- Universal provider compatibility with any OpenAI-compatible API

## Architecture

### Document Structure

The Technical Architecture Document will be organized into the following major sections:

1. **Executive Summary** - High-level overview and key architectural decisions
2. **System Overview** - Platform purpose, capabilities, and target users
3. **Architecture Diagrams** - Visual representations of system components and data flow
4. **Component Architecture** - Detailed breakdown of all system components
5. **Data Architecture** - Database schema, data models, and data flow
6. **API Architecture** - REST API design, endpoints, and integration patterns
7. **Security Architecture** - Authentication, authorization, and security controls
8. **Deployment Architecture** - Infrastructure, containerization, and deployment strategies
9. **Performance Architecture** - Scalability, monitoring, and optimization strategies
10. **Integration Architecture** - External integrations, MCP server, and provider configurations
11. **Development Architecture** - Development practices, testing strategies, and quality gates
12. **Operational Architecture** - Monitoring, logging, maintenance, and troubleshooting

### Documentation Format

The document will be created as a comprehensive Markdown file with:
- Mermaid diagrams for visual representations
- Code examples and configuration snippets
- Tables for structured information
- Cross-references between sections
- Table of contents with deep linking

## Components and Interfaces

### Core Components

#### 1. Backend API Layer (FastAPI)
- **Purpose**: Main application server providing REST API endpoints
- **Key Files**: `backend/main.py`, `config.py`, `database.py`
- **Responsibilities**:
  - HTTP request handling and routing
  - Middleware processing (logging, error handling, rate limiting)
  - API endpoint implementation
  - Database connection management
  - Configuration management

#### 2. Service Layer
- **Purpose**: Business logic implementation for AI framework integration
- **Key Files**: `services/` directory with framework-specific implementations
- **Components**:
  - `BaseService`: Abstract base class with common functionality
  - `SemanticKernelService`: Microsoft Semantic Kernel integration
  - `LangChainService`: LangChain framework integration
  - `LangGraphService`: LangGraph advanced workflow integration
  - Chat services for conversational interfaces
  - Context services for file processing

#### 3. Data Layer
- **Purpose**: Database models and data access patterns
- **Key Files**: `database.py`, `schemas/` directory
- **Components**:
  - SQLAlchemy ORM models
  - Database session management
  - Migration support via Alembic
  - Data validation schemas

#### 4. Frontend Layer (React)
- **Purpose**: Modern web interface for user interactions
- **Key Files**: `frontendReact/` directory
- **Components**:
  - React 18 with TypeScript
  - Vite build system
  - Tailwind CSS for styling
  - React Query for data fetching
  - React Router for navigation

#### 5. MCP Server
- **Purpose**: Standalone Model Context Protocol server for external integrations
- **Key Files**: `backend/mcp_server.py`
- **Components**:
  - FastMCP framework implementation
  - Tool definitions for story generation
  - Resource endpoints for data access
  - Transaction tracking and logging

#### 6. Cross-Cutting Concerns
- **Logging System**: Structured logging with JSON output and rotation
- **Retry Mechanism**: Tenacity-based retry logic with exponential backoff
- **Cost Tracking**: Token usage and cost calculation system
- **Transaction Context**: Thread-safe GUID tracking across operations
- **Rate Limiting**: API rate limiting with configurable thresholds
- **Error Handling**: Custom exception hierarchy with proper error responses

### Interface Definitions

#### HTTP API Interfaces
- REST endpoints following OpenAPI 3.0 specification
- JSON request/response format
- Standard HTTP status codes
- Request/response validation using Pydantic

#### Service Interfaces
- Abstract base classes defining common contracts
- Async/await pattern for non-blocking operations
- Standardized error handling and logging
- Transaction context propagation

#### Database Interfaces
- SQLAlchemy ORM for database abstraction
- Repository pattern for data access
- Connection pooling and session management
- Migration support for schema evolution

## Data Models

### Database Schema

The system uses SQLAlchemy ORM with the following core models:

#### Story Model
```python
class Story(Base):
    id: Integer (Primary Key)
    primary_character: String(100)
    secondary_character: String(100)
    combined_characters: String(200)
    story_content: Text
    method: String(50)  # Framework used
    generation_time_ms: Float
    input_tokens: Integer
    output_tokens: Integer
    total_tokens: Integer
    estimated_cost_usd: Numeric(10,6)
    transaction_guid: String(36)
    provider: String(50)
    model: String(100)
    created_at: DateTime
```

#### Chat Models
```python
class ChatConversation(Base):
    id: Integer (Primary Key)
    title: String(200)
    method: String(50)
    transaction_guid: String(36)
    provider: String(50)
    model: String(100)
    created_at: DateTime
    updated_at: DateTime
    messages: Relationship to ChatMessage

class ChatMessage(Base):
    id: Integer (Primary Key)
    conversation_id: Integer (Foreign Key)
    role: String(20)  # 'user' or 'assistant'
    content: Text
    generation_time_ms: Float
    token usage and cost fields...
    created_at: DateTime
```

#### Context Processing Model
```python
class ContextPromptExecution(Base):
    id: Integer (Primary Key)
    original_filename: String(255)
    file_type: String(10)
    file_size_bytes: Integer
    system_prompt: Text
    user_prompt: Text
    llm_response: Text
    performance and cost metrics...
    transaction_guid: String(36)
    created_at: DateTime
```

### Data Flow Patterns

#### Request Processing Flow
1. HTTP request received by FastAPI
2. Middleware processing (logging, validation, rate limiting)
3. Route handler invocation
4. Service layer business logic execution
5. Database operations (if required)
6. Response formatting and return

#### AI Generation Flow
1. User input validation
2. Service instantiation with provider configuration
3. Prompt template processing
4. API call to configured LLM provider
5. Response processing and token counting
6. Cost calculation and logging
7. Database persistence
8. Response formatting

## Error Handling

### Exception Hierarchy
- `Error`: Base custom exception class
- `ValidationError`: Input validation failures
- `APIKeyError`: Missing or invalid API credentials
- `APIConnectionError`: Failed API connections
- `APIRateLimitError`: Rate limit exceeded
- `TimeoutError`: Operation timeouts

### Error Processing Strategy
1. **Validation Errors**: Caught at input validation layer, return 422 status
2. **API Errors**: Handled by retry mechanism, logged with context
3. **System Errors**: Caught by error middleware, return 500 status
4. **Rate Limit Errors**: Return 429 status with retry information

### Logging Strategy
- Structured JSON logging with transaction GUIDs
- Error context preservation across retry attempts
- Performance metrics logging
- Security event logging

## Testing Strategy

### Testing Layers

#### Unit Testing
- Service layer business logic testing
- Database model testing
- Utility function testing
- Mock external API dependencies

#### Integration Testing
- API endpoint testing
- Database integration testing
- Service integration testing
- MCP server tool testing

#### End-to-End Testing
- Full user workflow testing
- Frontend-backend integration testing
- Multi-framework comparison testing
- Error scenario testing

### Testing Infrastructure
- pytest framework for Python testing
- FastAPI TestClient for API testing
- Database fixtures for data testing
- Mock providers for AI service testing

### Quality Gates
- Code coverage requirements
- Linting and formatting checks
- Type checking with mypy
- Security scanning
- Performance benchmarking

This design provides the foundation for creating a comprehensive technical architecture document that will serve as the definitive reference for understanding, maintaining, and extending the FASTAPILLM platform.