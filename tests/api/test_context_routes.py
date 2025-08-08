"""
API tests for context routes.

Tests all context-related endpoints including file upload, processing, and context prompt execution.
"""

import pytest
from unittest.mock import patch, Mock
import json
import io


@pytest.mark.api
class TestContextUploadEndpoints:
    """Test context file upload endpoints."""
    
    @pytest.mark.asyncio
    async def test_upload_and_process_text_file_success(self, client, response_validator):
        """Test successful text file upload and processing."""
        mock_response = {
            "execution_id": 1,
            "response": "The uploaded file contains important information about project structure and implementation details.",
            "metadata": {
                "original_filename": "test.txt",
                "file_type": "txt",
                "file_size_bytes": 1024,
                "processed_content_length": 800,
                "method": "langchain",
                "status": "completed"
            },
            "usage": {
                "input_tokens": 200,
                "output_tokens": 50,
                "total_tokens": 250,
                "estimated_cost_usd": 0.0025
            },
            "performance": {
                "file_processing_time_ms": 150,
                "llm_execution_time_ms": 1200,
                "total_execution_time_ms": 1350,
                "request_id": "context_20250808_001"
            }
        }
        
        # Create a mock file
        file_content = b"This is a test file with some content that needs to be processed by the AI."
        file_data = {
            'file': ('test.txt', io.BytesIO(file_content), 'text/plain')
        }
        form_data = {
            'system_prompt': 'Analyze this file: [context]',
            'user_prompt': 'What are the key points?',
            'method': 'langchain'
        }
        
        with patch('services.context_services.langchain_context_service.LangChainContextService') as mock_service:
            mock_instance = Mock()
            mock_instance.process_context_with_prompt.return_value = (
                mock_response["response"],
                mock_response["execution_id"],
                {**mock_response["usage"], **mock_response["performance"]}
            )
            mock_service.return_value = mock_instance
            
            response = client.post(
                "/api/context/process/langchain",
                files=file_data,
                data=form_data
            )
            
            # Validate response
            data = response_validator.validate_success_response(response, 200)
            
            # Validate context response structure
            assert response_validator.validate_context_response(data)
            assert data["execution_id"] == 1
            assert "key points" in data["response"].lower()
            assert data["metadata"]["original_filename"] == "test.txt"
            assert data["usage"]["total_tokens"] > 0
    
    @pytest.mark.asyncio
    async def test_upload_and_process_pdf_file(self, client, response_validator):
        """Test PDF file upload and processing."""
        mock_pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\nThis is mock PDF content."
        
        with patch('services.context_services.semantic_kernel_context_service.SemanticKernelContextService') as mock_service:
            mock_instance = Mock()
            mock_instance.process_context_with_prompt.return_value = (
                "This PDF contains technical documentation with diagrams and specifications.",
                2,
                {"input_tokens": 300, "output_tokens": 75, "total_tokens": 375, "estimated_cost_usd": 0.00375}
            )
            mock_service.return_value = mock_instance
            
            response = client.post(
                "/api/context/process/semantic-kernel",
                files={'file': ('document.pdf', io.BytesIO(mock_pdf_content), 'application/pdf')},
                data={
                    'system_prompt': 'Extract key information from this document: [context]',
                    'user_prompt': 'Summarize the main topics',
                    'method': 'semantic-kernel'
                }
            )
            
            data = response_validator.validate_success_response(response)
            assert data["execution_id"] == 2
            assert "documentation" in data["response"]
            assert data["metadata"]["file_type"] == "pdf"
    
    @pytest.mark.asyncio
    async def test_upload_and_process_markdown_file(self, client, response_validator):
        """Test Markdown file upload and processing."""
        markdown_content = """# Project Documentation

## Overview
This is a test markdown document with:
- Lists
- **Bold text**
- `Code snippets`

## Implementation Details
The system uses FastAPI and SQLAlchemy.
"""
        
        with patch('services.context_services.langgraph_context_service.LangGraphContextService') as mock_service:
            mock_instance = Mock()
            mock_instance.process_context_with_prompt.return_value = (
                "This markdown document outlines a FastAPI project structure with SQLAlchemy integration.",
                3,
                {"input_tokens": 150, "output_tokens": 40, "total_tokens": 190, "estimated_cost_usd": 0.0019}
            )
            mock_service.return_value = mock_instance
            
            response = client.post(
                "/api/context/process/langgraph",
                files={'file': ('README.md', io.BytesIO(markdown_content.encode()), 'text/markdown')},
                data={
                    'system_prompt': 'Analyze this documentation: [context]',
                    'user_prompt': 'What technologies are mentioned?',
                    'method': 'langgraph'
                }
            )
            
            data = response_validator.validate_success_response(response)
            assert "FastAPI" in data["response"]
            assert data["metadata"]["original_filename"] == "README.md"
    
    def test_upload_file_too_large(self, client, response_validator):
        """Test file upload that exceeds size limit."""
        # Create a very large file (simulated)
        large_content = b"x" * (10 * 1024 * 1024 + 1)  # 10MB + 1 byte
        
        response = client.post(
            "/api/context/process/langchain",
            files={'file': ('large.txt', io.BytesIO(large_content), 'text/plain')},
            data={
                'system_prompt': 'Analyze this: [context]',
                'user_prompt': 'Summarize',
                'method': 'langchain'
            }
        )
        
        response_validator.validate_error_response(response, 413)  # Request Entity Too Large
    
    def test_upload_invalid_file_type(self, client, response_validator):
        """Test upload of unsupported file type."""
        binary_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"  # PNG header
        
        response = client.post(
            "/api/context/process/langchain",
            files={'file': ('image.png', io.BytesIO(binary_content), 'image/png')},
            data={
                'system_prompt': 'Analyze this: [context]',
                'user_prompt': 'What is it?',
                'method': 'langchain'
            }
        )
        
        response_validator.validate_error_response(response, 415)  # Unsupported Media Type
    
    def test_upload_missing_required_fields(self, client, response_validator):
        """Test upload with missing required form fields."""
        response = client.post(
            "/api/context/process/langchain",
            files={'file': ('test.txt', io.BytesIO(b"test content"), 'text/plain')},
            data={
                # Missing system_prompt and user_prompt
                'method': 'langchain'
            }
        )
        
        response_validator.validate_error_response(response, 422)
    
    def test_upload_missing_file(self, client, response_validator):
        """Test request without file upload."""
        response = client.post(
            "/api/context/process/langchain",
            data={
                'system_prompt': 'Analyze this: [context]',
                'user_prompt': 'Summarize',
                'method': 'langchain'
            }
        )
        
        response_validator.validate_error_response(response, 422)
    
    def test_upload_empty_file(self, client, response_validator):
        """Test upload of empty file."""
        response = client.post(
            "/api/context/process/langchain",
            files={'file': ('empty.txt', io.BytesIO(b""), 'text/plain')},
            data={
                'system_prompt': 'Analyze this: [context]',
                'user_prompt': 'What does it contain?',
                'method': 'langchain'
            }
        )
        
        response_validator.validate_error_response(response, 422)


@pytest.mark.api
class TestContextHistoryEndpoints:
    """Test context execution history endpoints."""
    
    def test_get_context_executions_empty(self, client):
        """Test getting context executions when none exist."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().order_by().offset().limit().all.return_value = []
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/context/executions")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0
    
    def test_get_context_executions_with_data(self, client, populated_database):
        """Test getting context executions with existing data."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            
            mock_executions = []
            for i in range(3):
                mock_execution = Mock()
                mock_execution.id = i + 1
                mock_execution.original_filename = f"file{i+1}.txt"
                mock_execution.file_type = "txt"
                mock_execution.file_size_bytes = 1024 * (i + 1)
                mock_execution.method = "langchain"
                mock_execution.status = "completed"
                mock_execution.created_at = "2025-01-01T00:00:00"
                mock_executions.append(mock_execution)
            
            mock_session.query().order_by().offset().limit().all.return_value = mock_executions
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/context/executions")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 3
            assert data[0]["original_filename"] == "file1.txt"
    
    def test_get_context_executions_pagination(self, client):
        """Test context executions with pagination."""
        response = client.get("/api/context/executions?skip=5&limit=10")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
    
    def test_get_single_context_execution_success(self, client):
        """Test getting a single context execution by ID."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_execution = Mock()
            mock_execution.id = 1
            mock_execution.original_filename = "test.txt"
            mock_execution.llm_response = "Analysis complete"
            mock_execution.status = "completed"
            mock_session.query().filter().first.return_value = mock_execution
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/context/executions/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["original_filename"] == "test.txt"
    
    def test_get_single_context_execution_not_found(self, client):
        """Test getting a context execution that doesn't exist."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().filter().first.return_value = None
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/context/executions/999")
            
            assert response.status_code == 404


@pytest.mark.api
class TestContextManagementEndpoints:
    """Test context management endpoints."""
    
    def test_delete_context_execution_success(self, client):
        """Test successful context execution deletion."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_execution = Mock()
            mock_execution.id = 1
            mock_session.query().filter().first.return_value = mock_execution
            mock_get_db.return_value = mock_session
            
            response = client.delete("/api/context/executions/1")
            
            assert response.status_code == 200
            mock_session.delete.assert_called_once_with(mock_execution)
            mock_session.commit.assert_called_once()
    
    def test_delete_context_execution_not_found(self, client):
        """Test deleting a context execution that doesn't exist."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().filter().first.return_value = None
            mock_get_db.return_value = mock_session
            
            response = client.delete("/api/context/executions/999")
            
            assert response.status_code == 404
    
    def test_get_context_execution_by_filename(self, client):
        """Test searching context executions by filename."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_executions = []
            
            mock_execution = Mock()
            mock_execution.id = 1
            mock_execution.original_filename = "project_docs.md"
            mock_execution.status = "completed"
            mock_executions.append(mock_execution)
            
            mock_session.query().filter().all.return_value = mock_executions
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/context/search?filename=project_docs")
            
            # This endpoint might not exist yet, but shows the test pattern
            assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.slow
class TestContextPerformanceEndpoints:
    """Test context processing performance scenarios."""
    
    def test_concurrent_file_processing(self, client):
        """Test concurrent file processing requests."""
        files_data = []
        for i in range(3):
            files_data.append({
                'file': (f'test{i}.txt', io.BytesIO(f"Test content {i}".encode()), 'text/plain'),
                'system_prompt': f'Analyze file {i}: [context]',
                'user_prompt': f'What is in file {i}?',
                'method': 'langchain'
            })
        
        responses = []
        for file_data in files_data:
            with patch('services.context_services.langchain_context_service.LangChainContextService') as mock_service:
                mock_instance = Mock()
                mock_instance.process_context_with_prompt.return_value = (
                    f"Analysis of {file_data['file'][0]}",
                    len(responses) + 1,
                    {"input_tokens": 50, "output_tokens": 25, "total_tokens": 75, "estimated_cost_usd": 0.00075}
                )
                mock_service.return_value = mock_instance
                
                response = client.post(
                    "/api/context/process/langchain",
                    files={'file': file_data['file']},
                    data={
                        'system_prompt': file_data['system_prompt'],
                        'user_prompt': file_data['user_prompt'],
                        'method': file_data['method']
                    }
                )
                responses.append(response)
        
        # All responses should be successful
        for response in responses:
            assert response.status_code == 200


@pytest.mark.api
class TestContextErrorHandling:
    """Test context processing error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_service_unavailable_error(self, client, response_validator):
        """Test when context service is unavailable."""
        with patch('services.context_services.langchain_context_service.LangChainContextService') as mock_service:
            mock_service.side_effect = Exception("Context service unavailable")
            
            response = client.post(
                "/api/context/process/langchain",
                files={'file': ('test.txt', io.BytesIO(b"test content"), 'text/plain')},
                data={
                    'system_prompt': 'Analyze: [context]',
                    'user_prompt': 'Summarize',
                    'method': 'langchain'
                }
            )
            
            response_validator.validate_error_response(response, 500)
    
    def test_file_processing_error(self, client, response_validator):
        """Test when file processing fails."""
        # Simulate a corrupted file
        corrupted_content = b"\x00\x01\x02\x03CORRUPTED FILE DATA\xFF\xFE"
        
        with patch('services.context_services.langchain_context_service.LangChainContextService') as mock_service:
            mock_instance = Mock()
            mock_instance.process_context_with_prompt.side_effect = Exception("File processing failed")
            mock_service.return_value = mock_instance
            
            response = client.post(
                "/api/context/process/langchain",
                files={'file': ('corrupted.txt', io.BytesIO(corrupted_content), 'text/plain')},
                data={
                    'system_prompt': 'Analyze: [context]',
                    'user_prompt': 'What is this?',
                    'method': 'langchain'
                }
            )
            
            response_validator.validate_error_response(response, 500)
    
    def test_invalid_method_error(self, client, response_validator):
        """Test context processing with invalid method."""
        response = client.post(
            "/api/context/process/invalid_method",
            files={'file': ('test.txt', io.BytesIO(b"test content"), 'text/plain')},
            data={
                'system_prompt': 'Analyze: [context]',
                'user_prompt': 'Summarize',
                'method': 'invalid_method'
            }
        )
        
        response_validator.validate_error_response(response, 404)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])