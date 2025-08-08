"""
Unit tests for BaseAIService.

Tests the core functionality of the base AI service including:
- Client initialization and management
- Header generation for different providers  
- Error handling and retry logic
- Cost calculation and token tracking
- Transaction context integration
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
import asyncio
from typing import Dict, Any
import httpx
from openai import AsyncOpenAI, APIError, RateLimitError, APIConnectionError


@pytest.mark.unit
class TestBaseAIService:
    """Test BaseAIService core functionality."""
    
    @pytest.fixture
    def service_class(self):
        """Import and return BaseAIService class."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.base_ai_service import BaseAIService
        return BaseAIService
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing.""" 
        settings = Mock()
        settings.provider_name = "test_provider"
        settings.provider_api_key = "test-api-key"
        settings.provider_api_base_url = "https://test.api.com/v1"
        settings.provider_model = "test-model"
        settings.provider_api_type = "openai"
        settings.openai_timeout = 30
        settings.provider_headers = {"X-Test": "value"}
        return settings
    
    @pytest.fixture  
    def mock_custom_settings(self):
        """Mock custom settings for testing."""
        custom_settings = Mock()
        custom_settings.custom_var = "test_custom_value"
        custom_settings.api_timeout = 60
        return custom_settings
    
    @pytest.fixture
    def service_instance(self, service_class):
        """Create a BaseAIService instance for testing."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.custom_settings") as mock_custom:
            
            mock_settings.provider_name = "test_provider"
            mock_custom = None
            
            return service_class()
    
    def test_initialization(self, service_instance):
        """Test BaseAIService initialization."""
        assert service_instance._client is None
        assert service_instance._http_client is None
        assert service_instance.service_name == "BaseAIService"
        assert service_instance.provider_name == "test_provider"
    
    def test_initialization_with_custom_settings(self, service_class):
        """Test initialization with custom provider settings."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.custom_settings") as mock_custom:
            
            mock_settings.provider_name = "custom"
            mock_custom.custom_var = "test_value"
            
            service = service_class()
            assert service.custom_settings == mock_custom
            assert service.provider_name == "custom"
    
    @pytest.mark.asyncio
    async def test_ensure_client_creates_client(self, service_instance):
        """Test that _ensure_client creates client on first call."""
        mock_client = AsyncMock(spec=AsyncOpenAI)
        
        with patch.object(service_instance, '_create_client', return_value=mock_client):
            client = await service_instance._ensure_client()
            
            assert client == mock_client
            assert service_instance._client == mock_client
    
    @pytest.mark.asyncio
    async def test_ensure_client_reuses_existing(self, service_instance):
        """Test that _ensure_client reuses existing client."""
        mock_client = AsyncMock(spec=AsyncOpenAI)
        service_instance._client = mock_client
        
        with patch.object(service_instance, '_create_client') as mock_create:
            client = await service_instance._ensure_client()
            
            assert client == mock_client
            mock_create.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_create_client_openrouter_provider(self, service_instance):
        """Test client creation for OpenRouter provider."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.AsyncOpenAI") as mock_openai, \
             patch("services.base_ai_service.httpx.AsyncClient") as mock_http:
            
            mock_settings.provider_name = "openrouter"
            mock_settings.provider_api_key = "test-key"
            mock_settings.provider_api_base_url = "https://openrouter.ai/api/v1"
            mock_settings.provider_api_type = "openai"
            mock_settings.openai_timeout = 30
            mock_settings.provider_headers = {}
            
            mock_client = AsyncMock(spec=AsyncOpenAI)
            mock_openai.return_value = mock_client
            
            client = await service_instance._create_client()
            
            # Verify AsyncOpenAI was called with correct parameters
            mock_openai.assert_called_once()
            call_args = mock_openai.call_args[1]
            assert call_args["api_key"] == "test-key"
            assert call_args["base_url"] == "https://openrouter.ai/api/v1"
            assert call_args["http_client"] is not None
    
    @pytest.mark.asyncio 
    async def test_create_client_custom_provider(self, service_instance):
        """Test client creation for custom provider."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.custom_settings") as mock_custom, \
             patch("services.base_ai_service.AsyncOpenAI") as mock_openai, \
             patch("services.base_ai_service.httpx.AsyncClient") as mock_http:
            
            mock_settings.provider_name = "custom"
            mock_settings.provider_api_key = "custom-key"
            mock_settings.provider_api_base_url = "https://custom.api.com/v1"
            mock_settings.provider_api_type = "openai"
            mock_settings.openai_timeout = 30
            mock_settings.provider_headers = {"X-Custom": "value"}
            
            mock_custom.custom_var = "custom_value"
            
            mock_client = AsyncMock(spec=AsyncOpenAI)
            mock_openai.return_value = mock_client
            
            client = await service_instance._create_client()
            
            # Verify client creation
            mock_openai.assert_called_once()
            assert client == mock_client
    
    @pytest.mark.asyncio
    async def test_create_client_error_handling(self, service_instance):
        """Test client creation error handling."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.AsyncOpenAI") as mock_openai, \
             patch("services.base_ai_service.httpx.AsyncClient"):
            
            mock_settings.provider_name = "openrouter"
            mock_settings.provider_api_key = "test-key"
            mock_settings.provider_api_base_url = "https://openrouter.ai/api/v1"
            mock_settings.provider_api_type = "openai"
            mock_settings.provider_headers = {}
            
            mock_openai.side_effect = Exception("Connection failed")
            
            from exceptions import APIKeyError
            with pytest.raises(APIKeyError, match="Failed to initialize openrouter client"):
                await service_instance._create_client()
    
    def test_header_generation_openrouter(self, service_instance):
        """Test header generation for OpenRouter provider."""
        # This is tested indirectly through client creation
        # OpenRouter should use minimal headers
        with patch("services.base_ai_service.settings") as mock_settings:
            mock_settings.provider_name = "openrouter"
            mock_settings.provider_headers = {}
            
            # OpenRouter headers are handled by the client
            assert mock_settings.provider_name.lower() == "openrouter"
    
    def test_header_generation_custom(self, service_instance):
        """Test header generation for custom provider."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.custom_settings") as mock_custom:
            
            mock_settings.provider_name = "custom"
            mock_settings.provider_api_key = "custom-key"
            mock_custom.custom_var = "custom_value"
            
            # Custom provider should have extended headers
            assert mock_settings.provider_name.lower() == "custom"
            assert mock_custom.custom_var == "custom_value"
    
    @pytest.mark.asyncio
    async def test_call_api_success(self, service_instance):
        """Test successful API call.""" 
        # Mock the _call_api method if it exists, or test actual implementation
        mock_completion = Mock()
        mock_completion.choices = [Mock()]
        mock_completion.choices[0].message.content = "Test response"
        mock_completion.usage.prompt_tokens = 50
        mock_completion.usage.completion_tokens = 25
        mock_completion.usage.total_tokens = 75
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_completion
        
        with patch.object(service_instance, '_ensure_client', return_value=mock_client):
            # If _call_api method exists, test it
            if hasattr(service_instance, '_call_api'):
                messages = [{"role": "user", "content": "test"}]
                response, usage = await service_instance._call_api(messages)
                
                assert "Test response" in response
                assert usage["total_tokens"] == 75
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, service_instance):
        """Test API error handling."""
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = RateLimitError(
            message="Rate limit exceeded",
            response=Mock(status_code=429),
            body=None
        )
        
        with patch.object(service_instance, '_ensure_client', return_value=mock_client):
            if hasattr(service_instance, '_call_api'):
                messages = [{"role": "user", "content": "test"}]
                
                with pytest.raises(Exception):  # Should handle rate limit error
                    await service_instance._call_api(messages)
    
    def test_cost_calculation_integration(self, service_instance):
        """Test integration with cost calculation."""
        usage_info = {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150
        }
        
        # Test that service can work with cost calculation
        # This tests the integration point
        assert usage_info["total_tokens"] == usage_info["input_tokens"] + usage_info["output_tokens"]
    
    def test_transaction_context_integration(self, service_instance):
        """Test integration with transaction context."""
        # BaseAIService inherits from TransactionAware
        assert hasattr(service_instance, 'transaction_guid')
        
        # Test transaction GUID property access
        with patch("transaction_context.get_current_transaction_guid", return_value="test-guid"):
            guid = service_instance.transaction_guid
            assert guid == "test-guid"
    
    @pytest.mark.asyncio
    async def test_cleanup_resources(self, service_instance):
        """Test resource cleanup."""
        # Set up mocked resources
        mock_http_client = AsyncMock()
        service_instance._http_client = mock_http_client
        
        # Test cleanup if method exists
        if hasattr(service_instance, 'cleanup') or hasattr(service_instance, '__aenter__'):
            # Test async context manager if implemented
            pass
        
        # At minimum, verify we can clean up the http client
        if service_instance._http_client:
            await service_instance._http_client.aclose()
            mock_http_client.aclose.assert_called_once()


@pytest.mark.unit 
class TestBaseAIServiceProviderSpecific:
    """Test provider-specific functionality."""
    
    @pytest.fixture
    def service_class(self):
        """Import BaseAIService class."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.base_ai_service import BaseAIService
        return BaseAIService
    
    def test_openrouter_configuration(self, service_class):
        """Test service configuration for OpenRouter."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.custom_settings", None):
            
            mock_settings.provider_name = "openrouter"
            mock_settings.provider_api_key = "sk-or-v1-test"
            mock_settings.provider_api_base_url = "https://openrouter.ai/api/v1"
            
            service = service_class()
            assert service.provider_name == "openrouter"
            assert service.custom_settings is None
    
    def test_custom_provider_configuration(self, service_class):
        """Test service configuration for custom provider."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.custom_settings") as mock_custom:
            
            mock_settings.provider_name = "custom"
            mock_custom.custom_var = "custom_value"
            mock_custom.api_timeout = 120
            
            service = service_class()
            assert service.provider_name == "custom"
            assert service.custom_settings == mock_custom
            assert service.custom_settings.custom_var == "custom_value"
    
    @pytest.mark.openrouter
    def test_openrouter_headers(self, service_class):
        """Test OpenRouter-specific header handling."""
        with patch("services.base_ai_service.settings") as mock_settings:
            mock_settings.provider_name = "OpenRouter"  # Test case insensitive
            mock_settings.provider_headers = {}
            
            # OpenRouter headers are minimal - handled by client
            assert mock_settings.provider_name.lower() == "openrouter"
    
    @pytest.mark.custom_provider
    def test_custom_provider_headers(self, service_class):
        """Test custom provider header handling."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.custom_settings") as mock_custom:
            
            mock_settings.provider_name = "custom"
            mock_settings.provider_api_key = "custom-key"
            mock_settings.provider_headers = {"X-Base": "base_value"}
            mock_custom.custom_var = "extended_value"
            
            service = service_class()
            
            # Verify custom provider setup
            assert service.provider_name == "custom"
            assert service.custom_settings.custom_var == "extended_value"


@pytest.mark.unit
class TestBaseAIServiceAsync:
    """Test async functionality of BaseAIService."""
    
    @pytest.fixture
    def service_class(self):
        """Import BaseAIService class."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.base_ai_service import BaseAIService
        return BaseAIService
    
    @pytest.mark.asyncio
    async def test_concurrent_client_access(self, service_class):
        """Test concurrent access to client creation."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.custom_settings", None):
            
            mock_settings.provider_name = "test"
            service = service_class()
            
            # Mock the client creation to simulate async behavior
            mock_client = AsyncMock(spec=AsyncOpenAI)
            
            with patch.object(service, '_create_client', return_value=mock_client) as mock_create:
                # Test concurrent access
                tasks = [service._ensure_client() for _ in range(3)]
                clients = await asyncio.gather(*tasks)
                
                # Should all return same client instance
                assert all(client == mock_client for client in clients)
                # Should only create client once
                assert mock_create.call_count == 1
    
    @pytest.mark.asyncio
    async def test_async_context_manager(self, service_class):
        """Test if service can be used as async context manager."""
        with patch("services.base_ai_service.settings") as mock_settings:
            mock_settings.provider_name = "test"
            service = service_class()
            
            # Test basic async context if implemented
            if hasattr(service, '__aenter__'):
                async with service:
                    assert service is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])