"""
API Client Test Fixtures

Provides FastAPI test client configurations and helpers.
"""

import pytest
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient
import tempfile
import os
from io import BytesIO


@pytest.fixture
def authenticated_client(client: TestClient):
    """Test client with authentication headers (if needed)."""
    # For now, return regular client since no auth is implemented
    return client


@pytest.fixture
def api_headers():
    """Standard API headers for testing."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "fastapillm-test-client/1.0"
    }


@pytest.fixture
def file_upload_client(client: TestClient):
    """Client configured for file upload testing."""
    class FileUploadClient:
        def __init__(self, client: TestClient):
            self.client = client
        
        def upload_file(
            self,
            content: bytes,
            filename: str = "test.txt",
            content_type: str = "text/plain",
            endpoint: str = "/api/context/upload"
        ):
            """Helper method for file uploads."""
            files = {
                "file": (filename, BytesIO(content), content_type)
            }
            return self.client.post(endpoint, files=files)
        
        def upload_text_file(self, content: str, filename: str = "test.txt"):
            """Upload a text file."""
            return self.upload_file(
                content.encode(),
                filename=filename,
                content_type="text/plain"
            )
        
        def upload_json_file(self, data: dict, filename: str = "test.json"):
            """Upload a JSON file."""
            import json
            return self.upload_file(
                json.dumps(data).encode(),
                filename=filename,
                content_type="application/json"
            )
        
        def upload_csv_file(self, content: str, filename: str = "test.csv"):
            """Upload a CSV file."""
            return self.upload_file(
                content.encode(),
                filename=filename,
                content_type="text/csv"
            )
    
    return FileUploadClient(client)


@pytest.fixture
def api_request_factory(client: TestClient, api_headers: Dict[str, str]):
    """Factory for creating API requests with consistent configuration."""
    class APIRequestFactory:
        def __init__(self, client: TestClient, default_headers: Dict[str, str]):
            self.client = client
            self.default_headers = default_headers
        
        def post(
            self,
            url: str,
            data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
        ):
            """Make a POST request with default headers."""
            request_headers = {**self.default_headers}
            if headers:
                request_headers.update(headers)
            
            return self.client.post(
                url, 
                json=data,
                headers=request_headers,
                **kwargs
            )
        
        def get(
            self,
            url: str,
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
        ):
            """Make a GET request with default headers."""
            request_headers = {**self.default_headers}
            if headers:
                request_headers.update(headers)
            
            return self.client.get(
                url,
                params=params,
                headers=request_headers,
                **kwargs
            )
        
        def put(
            self,
            url: str,
            data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
        ):
            """Make a PUT request with default headers."""
            request_headers = {**self.default_headers}
            if headers:
                request_headers.update(headers)
            
            return self.client.put(
                url,
                json=data,
                headers=request_headers,
                **kwargs
            )
        
        def delete(
            self,
            url: str,
            headers: Optional[Dict[str, str]] = None,
            **kwargs
        ):
            """Make a DELETE request with default headers."""
            request_headers = {**self.default_headers}
            if headers:
                request_headers.update(headers)
            
            return self.client.delete(
                url,
                headers=request_headers,
                **kwargs
            )
    
    return APIRequestFactory(client, api_headers)


@pytest.fixture
def story_api_client(api_request_factory):
    """Specialized client for story API testing."""
    class StoryAPIClient:
        def __init__(self, request_factory):
            self.api = request_factory
        
        def generate_story(
            self,
            primary_character: str = "Alice",
            secondary_character: str = "Bob", 
            setting: str = "Forest",
            genre: str = "Adventure",
            tone: str = "Light",
            length: str = "medium",
            method: str = "langchain"
        ):
            """Generate a story via API."""
            data = {
                "primary_character": primary_character,
                "secondary_character": secondary_character,
                "setting": setting,
                "genre": genre,
                "tone": tone,
                "length": length
            }
            return self.api.post(f"/api/story/generate/{method}", data=data)
        
        def get_stories(self, skip: int = 0, limit: int = 20):
            """Get list of stories."""
            return self.api.get("/api/stories", params={"skip": skip, "limit": limit})
        
        def get_story(self, story_id: int):
            """Get specific story by ID."""
            return self.api.get(f"/api/stories/{story_id}")
        
        def delete_story(self, story_id: int):
            """Delete a story."""
            return self.api.delete(f"/api/stories/{story_id}")
    
    return StoryAPIClient(api_request_factory)


@pytest.fixture
def chat_api_client(api_request_factory):
    """Specialized client for chat API testing."""
    class ChatAPIClient:
        def __init__(self, request_factory):
            self.api = request_factory
        
        def send_message(
            self,
            message: str,
            conversation_id: Optional[int] = None,
            system_prompt: Optional[str] = None,
            method: str = "langchain"
        ):
            """Send a chat message."""
            data = {
                "message": message,
                "conversation_id": conversation_id,
                "system_prompt": system_prompt
            }
            return self.api.post(f"/api/chat/{method}", data=data)
        
        def get_conversations(self, skip: int = 0, limit: int = 20):
            """Get list of conversations.""" 
            return self.api.get("/api/chat/conversations", params={"skip": skip, "limit": limit})
        
        def get_conversation(self, conversation_id: int):
            """Get specific conversation."""
            return self.api.get(f"/api/chat/conversations/{conversation_id}")
        
        def delete_conversation(self, conversation_id: int):
            """Delete a conversation."""
            return self.api.delete(f"/api/chat/conversations/{conversation_id}")
    
    return ChatAPIClient(api_request_factory)


@pytest.fixture
def context_api_client(api_request_factory, file_upload_client):
    """Specialized client for context API testing.""" 
    class ContextAPIClient:
        def __init__(self, request_factory, upload_client):
            self.api = request_factory
            self.upload = upload_client
        
        def upload_and_process(
            self,
            file_content: str,
            system_prompt: str,
            user_prompt: str,
            filename: str = "test.txt",
            method: str = "langchain"
        ):
            """Upload file and process with context prompt."""
            # Upload file
            upload_response = self.upload.upload_text_file(file_content, filename)
            if upload_response.status_code != 200:
                return upload_response
            
            file_id = upload_response.json()["file_id"]
            
            # Process with context
            data = {
                "file_ids": [file_id],
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "method": method
            }
            return self.api.post("/api/context/execute", data=data)
        
        def get_executions(self, skip: int = 0, limit: int = 20):
            """Get list of context executions."""
            return self.api.get("/api/context/executions", params={"skip": skip, "limit": limit})
        
        def get_uploaded_files(self):
            """Get list of uploaded files."""
            return self.api.get("/api/context/files")
    
    return ContextAPIClient(api_request_factory, file_upload_client)


@pytest.fixture
def response_validator():
    """Helper for validating API responses."""
    class ResponseValidator:
        @staticmethod
        def validate_success_response(response, expected_status: int = 200):
            """Validate a successful API response."""
            assert response.status_code == expected_status
            assert response.headers["content-type"] == "application/json"
            return response.json()
        
        @staticmethod
        def validate_error_response(response, expected_status: int = 400):
            """Validate an error API response."""
            assert response.status_code == expected_status
            data = response.json()
            assert "detail" in data
            return data
        
        @staticmethod
        def validate_story_response(response_data: dict):
            """Validate story generation response structure."""
            required_fields = ["story", "metadata", "usage", "provider_info"]
            for field in required_fields:
                assert field in response_data
            
            # Validate metadata
            metadata = response_data["metadata"]
            assert "primary_character" in metadata
            assert "setting" in metadata
            
            # Validate usage
            usage = response_data["usage"]
            assert "input_tokens" in usage
            assert "output_tokens" in usage
            assert "total_tokens" in usage
            
            return True
        
        @staticmethod
        def validate_chat_response(response_data: dict):
            """Validate chat response structure."""
            required_fields = ["response", "conversation_id", "message_id", "usage"]
            for field in required_fields:
                assert field in response_data
            return True
        
        @staticmethod
        def validate_context_response(response_data: dict):
            """Validate context processing response structure."""
            required_fields = ["response", "execution_id", "metadata", "usage"]
            for field in required_fields:
                assert field in response_data
            
            # Validate metadata
            metadata = response_data["metadata"]
            assert "original_filename" in metadata
            assert "file_type" in metadata
            assert "method" in metadata
            
            # Validate usage
            usage = response_data["usage"]
            assert "total_tokens" in usage
            
            return True
    
    return ResponseValidator()


@pytest.fixture
def mock_external_api():
    """Mock external API responses for testing."""
    from unittest.mock import Mock
    
    mock = Mock()
    
    # Default OpenAI-style response
    mock.chat.completions.create.return_value = Mock(
        choices=[Mock(
            message=Mock(content="This is a test response from the AI service."),
            finish_reason="stop"
        )],
        usage=Mock(
            prompt_tokens=50,
            completion_tokens=25,
            total_tokens=75
        ),
        model="test-model",
        id="test-completion-id"
    )
    
    return mock


@pytest.fixture
def performance_timer():
    """Timer utility for performance testing."""
    import time
    
    class PerformanceTimer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            """Start timing."""
            self.start_time = time.time()
            return self
        
        def stop(self):
            """Stop timing and return duration."""
            self.end_time = time.time()
            return self.duration
        
        @property
        def duration(self):
            """Get duration in seconds."""
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
        
        def __enter__(self):
            return self.start()
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.stop()
    
    return PerformanceTimer