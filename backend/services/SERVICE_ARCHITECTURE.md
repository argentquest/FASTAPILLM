# Service Architecture

## Overview

The service layer has been refactored to follow a more flexible inheritance hierarchy that better represents the different types of AI services in the application.

## Class Hierarchy

```
BaseAIService (base_ai_service.py)
├── ContentGenerationService (content_generation_service.py)
│   ├── LangChainService
│   ├── SemanticKernelService
│   └── LangGraphService
├── ChatService (chat_services/base_chat_service.py)
│   ├── LangChainChatService
│   ├── SemanticKernelChatService
│   └── LangGraphChatService
└── ContextService (context_services/base_context_service.py)
    ├── LangChainContextService
    ├── SemanticKernelContextService
    └── LangGraphContextService
```

## Base Classes

### BaseAIService
- **Purpose**: Provides common AI functionality for all services
- **Features**:
  - API client management
  - Retry logic and error handling
  - Token usage tracking and cost calculation
  - Provider-specific header generation
  - Access to settings and custom_settings
- **Methods**:
  - `_ensure_client()`: Lazy client initialization
  - `_create_client()`: Create OpenAI-compatible client
  - `_call_api()`: Make API calls with retry logic
  - `close()`: Clean up resources
- **When to use**: Extend this for any service that needs AI capabilities

### ContentGenerationService
- **Purpose**: Abstract base for content/story generation services
- **Extends**: BaseAIService
- **Abstract Methods**:
  - `generate_content(primary_input, secondary_input)`: Must be implemented by subclasses
- **Features**:
  - Backwards compatibility with `generate_story()` method
- **When to use**: Extend this for services that generate stories, articles, or other content

### ChatService
- **Purpose**: Base for conversational AI services
- **Extends**: BaseAIService directly
- **Methods**:
  - `send_message(message, conversation_history)`: Handle chat interactions
- **Features**:
  - Conversation history management
  - System prompt configuration
- **When to use**: Extend this for chat-based interactions

## Usage Patterns

### Content Generation Services
```python
from services.content_generation_service import ContentGenerationService

class MyContentService(ContentGenerationService):
    async def generate_content(self, primary, secondary):
        # Implementation
        pass
```

### Chat Services
```python
from services.base_ai_service import BaseAIService

class MyChatService(BaseAIService):
    async def send_message(self, message, history):
        # Implementation using self._call_api()
        pass
```

### Other AI Services
```python
from services.base_ai_service import BaseAIService

class MyCustomAIService(BaseAIService):
    async def my_custom_method(self):
        # Implementation using self._call_api()
        pass
```

## Benefits of Architecture

1. **Separation of Concerns**: Not all services need `generate_content()`
2. **Flexibility**: Services can extend the appropriate base class
3. **Type Safety**: Abstract methods are only where they belong
4. **Cleaner Code**: No empty implementations of unused abstract methods
5. **Better Documentation**: Each base class has a clear purpose

## Example Implementations

### Content Generation Service
```python
from services.content_generation_service import ContentGenerationService

class MyStoryService(ContentGenerationService):
    async def generate_content(self, character1: str, character2: str):
        messages = [
            {"role": "system", "content": "You are a storyteller"},
            {"role": "user", "content": f"Tell a story about {character1} and {character2}"}
        ]
        
        content, usage = await self._call_api(messages, temperature=0.8)
        return content, usage
```

### Chat Service
```python
from services.base_ai_service import BaseAIService

class MyAssistantService(BaseAIService):
    async def chat(self, message: str, context: list = None):
        messages = [
            {"role": "system", "content": "You are a helpful assistant"}
        ]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": message})
        
        response, usage = await self._call_api(messages)
        return response, usage
```

### Custom AI Service
```python
from services.base_ai_service import BaseAIService

class CodeAnalyzerService(BaseAIService):
    async def analyze_code(self, code: str, language: str):
        messages = [
            {"role": "system", "content": "You are a code analyzer"},
            {"role": "user", "content": f"Analyze this {language} code:\n{code}"}
        ]
        
        analysis, usage = await self._call_api(messages, max_tokens=1000)
        return analysis, usage
```