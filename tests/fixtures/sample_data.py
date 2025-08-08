"""
Sample Test Data Fixtures

Provides realistic test data for different parts of the application.
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List


@pytest.fixture
def sample_story_requests():
    """Various story generation requests for comprehensive testing."""
    return {
        "basic": {
            "primary_character": "Alice",
            "secondary_character": "Bob",
            "setting": "Enchanted Forest", 
            "genre": "Fantasy Adventure",
            "tone": "Whimsical",
            "length": "medium"
        },
        "minimal": {
            "primary_character": "Hero",
            "setting": "Space Station"
        },
        "complex": {
            "primary_character": "Detective Sarah Chen",
            "secondary_character": "Professor Marcus Williams",
            "setting": "Victorian London, 1895",
            "genre": "Mystery/Thriller",
            "tone": "Dark and suspenseful", 
            "length": "long",
            "additional_context": "A series of bizarre disappearances plague the foggy streets"
        },
        "edge_case": {
            "primary_character": "X",
            "secondary_character": "Y",
            "setting": "Z",
            "genre": "?",
            "tone": "Neutral",
            "length": "short"
        }
    }


@pytest.fixture
def sample_chat_conversations():
    """Sample chat conversations for testing."""
    return {
        "simple": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hello! How can I help you today?"},
            {"role": "user", "content": "Tell me a joke"},
            {"role": "assistant", "content": "Why did the programmer quit his job? He didn't get arrays!"}
        ],
        "complex": [
            {"role": "system", "content": "You are a helpful coding assistant"},
            {"role": "user", "content": "How do I implement a binary search in Python?"},
            {"role": "assistant", "content": "Here's a simple binary search implementation:\n\n```python\ndef binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1\n```"},
            {"role": "user", "content": "Can you explain the time complexity?"}
        ]
    }


@pytest.fixture  
def sample_file_contents():
    """Sample file contents for context processing tests."""
    return {
        "txt": "This is a sample text file for testing.\nIt contains multiple lines of content.\nThe file processor should handle this correctly.",
        "csv": "name,age,city\nAlice,25,New York\nBob,30,San Francisco\nCharlie,35,Chicago",
        "json": '{"users": [{"name": "Alice", "age": 25}, {"name": "Bob", "age": 30}], "total": 2}',
        "pdf_text": "This is extracted text from a PDF file.\n\nIt may contain multiple paragraphs and formatting.\n\nThe content should be processed correctly by the file processor."
    }


@pytest.fixture
def sample_database_records():
    """Sample database records for testing."""
    return {
        "stories": [
            {
                "id": 1,
                "primary_character": "Alice",
                "secondary_character": "Bob",
                "setting": "Forest",
                "genre": "Adventure",
                "tone": "Light",
                "length": "medium",
                "generated_story": "Once upon a time, Alice and Bob went on an adventure...",
                "provider": "openrouter",
                "model": "llama-3-8b",
                "input_tokens": 100,
                "output_tokens": 200,
                "total_tokens": 300,
                "estimated_cost_usd": 0.003,
                "created_at": datetime.utcnow()
            }
        ],
        "chat_conversations": [
            {
                "id": 1, 
                "title": "General Chat",
                "provider": "openrouter",
                "model": "llama-3-8b",
                "created_at": datetime.utcnow()
            }
        ],
        "chat_messages": [
            {
                "id": 1,
                "conversation_id": 1,
                "role": "user",
                "content": "Hello",
                "input_tokens": 5,
                "output_tokens": 0,
                "created_at": datetime.utcnow()
            },
            {
                "id": 2,
                "conversation_id": 1, 
                "role": "assistant",
                "content": "Hello! How can I help you?",
                "input_tokens": 0,
                "output_tokens": 15,
                "created_at": datetime.utcnow()
            }
        ]
    }


@pytest.fixture
def sample_api_responses():
    """Sample API response structures."""
    return {
        "story_generation_success": {
            "story": "Once upon a time, in a magical forest...",
            "metadata": {
                "primary_character": "Alice",
                "secondary_character": "Bob",
                "setting": "Enchanted Forest",
                "genre": "Fantasy",
                "tone": "Whimsical",
                "length": "medium"
            },
            "usage": {
                "input_tokens": 150,
                "output_tokens": 300,
                "total_tokens": 450,
                "estimated_cost_usd": 0.0045
            },
            "provider_info": {
                "provider": "openrouter",
                "model": "meta-llama/llama-3-8b-instruct"
            }
        },
        "chat_response_success": {
            "response": "I'm doing well, thank you for asking!",
            "conversation_id": 123,
            "message_id": 456,
            "usage": {
                "input_tokens": 20,
                "output_tokens": 15,
                "total_tokens": 35,
                "estimated_cost_usd": 0.0004
            }
        },
        "context_processing_success": {
            "response": "Based on the provided context, here are the key insights...",
            "file_info": {
                "original_filename": "test.txt",
                "file_type": "txt",
                "file_size_bytes": 1024,
                "processed_content_length": 512
            },
            "usage": {
                "input_tokens": 500,
                "output_tokens": 150,
                "total_tokens": 650,
                "estimated_cost_usd": 0.0065
            }
        },
        "error_response": {
            "detail": "Validation error: Primary character is required",
            "error_type": "validation_error",
            "error_code": 422
        }
    }


@pytest.fixture
def sample_cost_data():
    """Sample cost tracking data."""
    return {
        "daily_costs": [
            {
                "date": "2025-01-01",
                "provider": "openrouter",
                "model": "llama-3-8b",
                "total_requests": 150,
                "input_tokens": 15000,
                "output_tokens": 7500, 
                "total_cost_usd": 0.225
            },
            {
                "date": "2025-01-02", 
                "provider": "openrouter",
                "model": "llama-3-8b",
                "total_requests": 200,
                "input_tokens": 20000,
                "output_tokens": 10000,
                "total_cost_usd": 0.30
            }
        ],
        "provider_breakdown": {
            "openrouter": {"cost": 0.525, "requests": 350},
            "custom": {"cost": 0.125, "requests": 75}
        }
    }


@pytest.fixture
def file_upload_scenarios():
    """Different file upload scenarios for testing."""
    return {
        "valid_txt": {
            "filename": "test.txt",
            "content": b"This is a test file for upload.",
            "content_type": "text/plain",
            "expected_size": 29
        },
        "valid_json": {
            "filename": "data.json", 
            "content": b'{"test": true, "data": [1, 2, 3]}',
            "content_type": "application/json",
            "expected_size": 33
        },
        "large_file": {
            "filename": "large.txt",
            "content": b"x" * (11 * 1024 * 1024),  # 11MB - should be rejected
            "content_type": "text/plain",
            "expected_error": "File too large"
        },
        "invalid_type": {
            "filename": "test.exe",
            "content": b"fake executable content",
            "content_type": "application/octet-stream", 
            "expected_error": "Unsupported file type"
        }
    }