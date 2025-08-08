"""
AI Service Mock Fixtures

Provides realistic mock responses for different AI frameworks and providers.
"""

import pytest
from typing import Dict, Any
from unittest.mock import MagicMock, AsyncMock
import json


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response with realistic structure."""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1635000000,
        "model": "test-model",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is a test story about Alice and Bob in the Enchanted Forest. Once upon a time, in a magical realm where talking animals roamed freely and ancient trees whispered secrets of old, there lived two unlikely friends who would embark on the adventure of a lifetime."
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 125,
            "completion_tokens": 87,
            "total_tokens": 212
        }
    }


@pytest.fixture
def mock_openai_chat_response():
    """Mock OpenAI chat response."""
    return {
        "id": "chatcmpl-chat123", 
        "object": "chat.completion",
        "created": 1635000001,
        "model": "test-model",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant", 
                "content": "Hello! I'm doing well, thank you for asking. How can I help you today?"
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 25,
            "completion_tokens": 18,
            "total_tokens": 43
        }
    }


@pytest.fixture
def mock_openai_context_response():
    """Mock OpenAI context processing response."""
    return {
        "id": "chatcmpl-context123",
        "object": "chat.completion", 
        "created": 1635000002,
        "model": "test-model",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Based on the provided context, here are the key insights:\n\n1. The document contains important information about user behavior patterns\n2. There are clear trends indicating increased engagement\n3. The data suggests opportunities for optimization\n\nThese insights can help inform strategic decision-making."
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 450,
            "completion_tokens": 92,
            "total_tokens": 542
        }
    }


@pytest.fixture  
def mock_async_openai_client(mock_openai_response):
    """Mock AsyncOpenAI client with realistic responses."""
    client = MagicMock()
    
    # Mock the completion response
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = mock_openai_response["choices"][0]["message"]["content"]
    mock_completion.usage.prompt_tokens = mock_openai_response["usage"]["prompt_tokens"]
    mock_completion.usage.completion_tokens = mock_openai_response["usage"]["completion_tokens"] 
    mock_completion.usage.total_tokens = mock_openai_response["usage"]["total_tokens"]
    
    # Make the create method async
    async_create = AsyncMock(return_value=mock_completion)
    client.chat.completions.create = async_create
    
    # Also mock the beta.chat.completions.parse structure for structured outputs
    client.beta = MagicMock()
    client.beta.chat = MagicMock()
    client.beta.chat.completions = MagicMock()
    client.beta.chat.completions.parse = AsyncMock(return_value=mock_completion)
    
    return client


@pytest.fixture
def mock_openai_client(mock_async_openai_client):
    """Mock OpenAI client (alias for async client for compatibility)."""
    return mock_async_openai_client


@pytest.fixture
def mock_langchain_llm():
    """Mock LangChain LLM with realistic responses."""
    llm = MagicMock()
    llm.agenerate.return_value = MagicMock()
    llm.agenerate.return_value.generations = [[MagicMock()]]
    llm.agenerate.return_value.generations[0][0].text = "Test LangChain response"
    llm.agenerate.return_value.llm_output = {
        "token_usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }
    return llm


@pytest.fixture 
def mock_semantic_kernel_service():
    """Mock Semantic Kernel service with realistic responses."""
    service = MagicMock()
    service.invoke_async.return_value = "Test Semantic Kernel response"
    return service


@pytest.fixture
def ai_response_factory():
    """Factory for creating AI responses with different characteristics."""
    def _create_response(
        content: str = "Test AI response",
        prompt_tokens: int = 100,
        completion_tokens: int = 50,
        framework: str = "openai"
    ) -> Dict[str, Any]:
        """Create a mock AI response."""
        if framework == "openai":
            return {
                "choices": [{
                    "message": {"content": content}
                }],
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens
                }
            }
        elif framework == "langchain":
            return {
                "generations": [[{"text": content}]],
                "llm_output": {
                    "token_usage": {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens
                    }
                }
            }
        else:
            return {"content": content, "tokens": prompt_tokens + completion_tokens}
    
    return _create_response


@pytest.fixture
def mock_ai_error_responses():
    """Mock AI error responses for testing error handling."""
    return {
        "rate_limit": {
            "error": {
                "code": "rate_limit_exceeded",
                "message": "Rate limit exceeded. Please try again later.",
                "type": "rate_limit_error"
            }
        },
        "invalid_request": {
            "error": {
                "code": "invalid_request_error", 
                "message": "Invalid request parameters",
                "type": "invalid_request_error"
            }
        },
        "api_error": {
            "error": {
                "code": "api_error",
                "message": "Internal server error",
                "type": "api_error"
            }
        }
    }


@pytest.fixture
def provider_specific_mocks():
    """Provider-specific mock configurations."""
    return {
        "openrouter": {
            "headers": {},
            "base_url": "https://openrouter.ai/api/v1",
            "model": "meta-llama/llama-3-8b-instruct"
        },
        "custom": {
            "headers": {
                "X-API-Key": "test-key",
                "X-Provider-Type": "custom"
            },
            "base_url": "https://custom.api.com/v1", 
            "model": "custom-model-v1"
        },
        "test": {
            "headers": {"X-Test": "true"},
            "base_url": "https://test.api.com/v1",
            "model": "test-model"
        }
    }