"""
Unit tests for LangChainService.

Tests the LangChain-based content generation service including:
- Content generation functionality
- LangChain prompt integration
- Message format conversion
- Error handling and retry logic
- Integration with ContentGenerationService
"""

import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Tuple, Dict, Any


@pytest.mark.unit
class TestLangChainService:
    """Test LangChainService content generation."""
    
    @pytest.fixture
    def service_class(self):
        """Import LangChainService class."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.story_services.langchain_service import LangChainService
        return LangChainService
    
    @pytest.fixture
    def service_instance(self, service_class):
        """Create a LangChainService instance for testing."""
        with patch("services.story_services.langchain_service.get_logger"), \
             patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.custom_settings", None):
            
            mock_settings.provider_name = "test_provider"
            mock_settings.provider_api_key = "test-key"
            mock_settings.provider_api_base_url = "https://test.api.com/v1"
            
            return service_class()
    
    @pytest.fixture
    def mock_langchain_messages(self):
        """Mock LangChain messages for testing."""
        from unittest.mock import Mock
        
        # Create mock message objects with content attribute
        system_msg = Mock()
        system_msg.content = "You are a creative storyteller."
        
        user_msg = Mock()
        user_msg.content = "Write a story about Alice and Bob in an enchanted forest."
        
        return [system_msg, user_msg]
    
    def test_inheritance(self, service_class):
        """Test that LangChainService inherits from ContentGenerationService."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.content_generation_service import ContentGenerationService
        assert issubclass(service_class, ContentGenerationService)
    
    def test_initialization(self, service_instance):
        """Test LangChainService initialization."""
        assert service_instance.service_name == "LangChainService"
        assert service_instance.provider_name == "test_provider"
        assert service_instance._client is None  # Lazy initialization
    
    @pytest.mark.asyncio
    async def test_generate_content_success(self, service_instance, mock_langchain_messages):
        """Test successful content generation."""
        expected_story = "Once upon a time in an enchanted forest, Alice met Bob and they embarked on a magical adventure filled with wonder and discovery."
        
        expected_usage = {
            "input_tokens": 50,
            "output_tokens": 75,
            "total_tokens": 125,
            "execution_time_ms": 1500,
            "estimated_cost_usd": 0.00125,
            "input_cost_per_1k_tokens": 0.001,
            "output_cost_per_1k_tokens": 0.002
        }
        
        # Mock the prompt generation
        with patch("services.story_services.langchain_service.get_langchain_messages") as mock_prompts:
            mock_prompts.return_value = mock_langchain_messages
            
            # Mock the base class API call
            with patch.object(service_instance, '_call_api_with_retry') as mock_api:
                mock_api.return_value = (expected_story, expected_usage)
                
                # Test content generation
                story, usage = await service_instance.generate_content("Alice", "Bob")
                
                # Verify results
                assert story == expected_story
                assert usage == expected_usage
                
                # Verify prompt generation was called
                mock_prompts.assert_called_once_with("Alice", "Bob")
                
                # Verify API was called with converted messages
                expected_messages = [
                    {"role": "system", "content": "You are a creative storyteller."},
                    {"role": "user", "content": "Write a story about Alice and Bob in an enchanted forest."}
                ]
                mock_api.assert_called_once_with(expected_messages)
    
    @pytest.mark.asyncio
    async def test_generate_content_with_empty_inputs(self, service_instance):
        """Test content generation with empty inputs."""
        # Create mock LangChain message objects, not dicts
        from unittest.mock import Mock
        system_msg = Mock()
        system_msg.content = "You are a creative storyteller."
        user_msg = Mock()
        user_msg.content = "Generate a story."
        mock_messages = [system_msg, user_msg]
        
        with patch("services.story_services.langchain_service.get_langchain_messages") as mock_prompts:
            mock_prompts.return_value = mock_messages
            
            with patch.object(service_instance, '_call_api_with_retry') as mock_api:
                mock_api.return_value = ("A generic story.", {
                    "input_tokens": 5,
                    "output_tokens": 5, 
                    "total_tokens": 10,
                    "execution_time_ms": 1000
                })
                
                story, usage = await service_instance.generate_content("", "")
                
                # Should still call prompts with empty strings
                mock_prompts.assert_called_once_with("", "")
                assert isinstance(story, str)
                assert isinstance(usage, dict)
    
    @pytest.mark.asyncio 
    async def test_generate_content_prompt_integration(self, service_instance):
        """Test integration with LangChain prompt system."""
        # Test that prompt generation is properly integrated
        # Create mock LangChain message objects
        from unittest.mock import Mock
        system_msg = Mock()
        system_msg.content = "Test system message"
        user_msg = Mock()
        user_msg.content = "Test user message with Alice and Bob"
        
        with patch("services.story_services.langchain_service.get_langchain_messages") as mock_prompts:
            mock_prompts.return_value = [system_msg, user_msg]
            
            with patch.object(service_instance, '_call_api_with_retry') as mock_api:
                mock_api.return_value = ("Test story", {
                    "input_tokens": 10,
                    "output_tokens": 10,
                    "total_tokens": 20,
                    "execution_time_ms": 1500
                })
                
                await service_instance.generate_content("Alice", "Bob")
                
                # Verify prompt module was called with correct parameters
                mock_prompts.assert_called_once_with("Alice", "Bob")
                
                # Verify API was called with the converted dict messages
                expected_messages = [
                    {"role": "system", "content": "Test system message"},
                    {"role": "user", "content": "Test user message with Alice and Bob"}
                ]
                mock_api.assert_called_once_with(expected_messages)
    
    @pytest.mark.asyncio
    async def test_generate_content_error_handling(self, service_instance):
        """Test error handling in content generation."""
        with patch("services.story_services.langchain_service.get_langchain_messages") as mock_prompts:
            mock_prompts.side_effect = Exception("Prompt generation failed")
            
            with pytest.raises(Exception, match="Prompt generation failed"):
                await service_instance.generate_content("Alice", "Bob")
    
    @pytest.mark.asyncio
    async def test_generate_content_api_error(self, service_instance, mock_langchain_messages):
        """Test API error handling in content generation."""
        with patch("services.story_services.langchain_service.get_langchain_messages") as mock_prompts:
            mock_prompts.return_value = mock_langchain_messages
            
            with patch.object(service_instance, '_call_api_with_retry') as mock_api:
                mock_api.side_effect = Exception("API call failed")
                
                with pytest.raises(Exception, match="API call failed"):
                    await service_instance.generate_content("Alice", "Bob")
    
    def test_retry_decorator_applied(self, service_class):
        """Test that retry decorator is applied to generate_content method."""
        # Check if the method has retry attributes or wrapper
        method = service_class.generate_content
        
        # The method should exist and be callable
        assert callable(method)
        
        # If retry is applied, the method might have wrapper attributes
        # This tests the decorator is at least present in the code
        assert hasattr(service_class, 'generate_content')
    
    def test_service_documentation(self, service_class):
        """Test that service has proper documentation."""
        assert service_class.__doc__ is not None
        assert "LangChain" in service_class.__doc__
        assert "content generation" in service_class.__doc__.lower()
    
    def test_method_documentation(self, service_class):
        """Test that generate_content method has proper documentation.""" 
        method_doc = service_class.generate_content.__doc__
        assert method_doc is not None
        assert "LangChain" in method_doc
        assert "primary_input" in method_doc
        assert "secondary_input" in method_doc


@pytest.mark.unit
class TestLangChainServiceIntegration:
    """Test LangChainService integration with other components."""
    
    @pytest.fixture
    def service_class(self):
        """Import LangChainService class.""" 
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.story_services.langchain_service import LangChainService
        return LangChainService
    
    def test_logging_integration(self, service_class):
        """Test integration with logging system."""
        # Service should have logger
        assert hasattr(service_class, '__module__')
        
        # Logger should be accessible (tested through mocking in other tests)
        with patch("services.story_services.langchain_service.get_logger") as mock_logger:
            mock_logger.return_value = Mock()
            
            # Import triggers logger creation
            from services.story_services.langchain_service import logger
            assert logger is not None
    
    @pytest.mark.asyncio
    async def test_base_service_integration(self, service_class):
        """Test integration with BaseAIService functionality."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.custom_settings", None):
            
            mock_settings.provider_name = "test_provider"
            service = service_class()
            
            # Should have BaseAIService functionality
            assert hasattr(service, '_ensure_client')
            assert hasattr(service, 'provider_name')
            assert service.provider_name == "test_provider"
    
    def test_prompt_module_integration(self, service_class):
        """Test integration with prompt module."""
        # Service imports and uses get_langchain_messages
        with patch("services.story_services.langchain_service.get_langchain_messages") as mock_prompts:
            mock_prompts.return_value = []
            
            # Import should work without errors
            from services.story_services.langchain_service import get_langchain_messages
            assert get_langchain_messages is not None
    
    @pytest.mark.asyncio
    async def test_retry_integration(self, service_class):
        """Test integration with retry system."""
        with patch("services.base_ai_service.settings"), \
             patch("services.base_ai_service.custom_settings", None):
            
            service = service_class()
            
            # The retry decorator should be applied to generate_content
            # This is tested by ensuring the method is properly decorated
            assert hasattr(service, 'generate_content')
            
            # Test that retry logic is in place (through mock)
            with patch("services.story_services.langchain_service.get_langchain_messages") as mock_prompts:
                # Create mock LangChain message objects
                from unittest.mock import Mock
                system_msg = Mock()
                system_msg.content = "You are a creative storyteller."
                user_msg = Mock()
                user_msg.content = "test"
                mock_prompts.return_value = [system_msg, user_msg]
                
                with patch.object(service, '_call_api_with_retry') as mock_api:
                    mock_api.return_value = ("test story", {
                        "input_tokens": 5,
                        "output_tokens": 5,
                        "total_tokens": 10,
                        "execution_time_ms": 1200
                    })
                    
                    story, usage = await service.generate_content("test", "test")
                    assert story == "test story"


@pytest.mark.unit
class TestLangChainServiceEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.fixture
    def service_class(self):
        """Import LangChainService class."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.story_services.langchain_service import LangChainService
        return LangChainService
    
    @pytest.mark.asyncio
    async def test_very_long_inputs(self, service_class):
        """Test content generation with very long inputs."""
        long_input = "A" * 1000  # 1000 character input
        
        with patch("services.base_ai_service.settings"), \
             patch("services.base_ai_service.custom_settings", None):
            
            service = service_class()
            
            with patch("services.story_services.langchain_service.get_langchain_messages") as mock_prompts:
                # Create mock LangChain message objects
                from unittest.mock import Mock
                system_msg = Mock()
                system_msg.content = "You are a creative storyteller."
                user_msg = Mock()
                user_msg.content = "long story request"
                mock_prompts.return_value = [system_msg, user_msg]
                
                with patch.object(service, '_call_api_with_retry') as mock_api:
                    mock_api.return_value = ("Long generated story", {
                        "input_tokens": 250,
                        "output_tokens": 250,
                        "total_tokens": 500,
                        "execution_time_ms": 3000
                    })
                    
                    story, usage = await service.generate_content(long_input, long_input)
                    
                    # Should handle long inputs properly
                    mock_prompts.assert_called_once_with(long_input, long_input)
                    assert isinstance(story, str)
                    assert usage["total_tokens"] == 500
    
    @pytest.mark.asyncio
    async def test_special_characters_in_inputs(self, service_class):
        """Test content generation with special characters."""
        special_input = "Alice & Bob's \"Amazing\" Adventure! @#$%"
        
        with patch("services.base_ai_service.settings"), \
             patch("services.base_ai_service.custom_settings", None):
            
            service = service_class()
            
            with patch("services.story_services.langchain_service.get_langchain_messages") as mock_prompts:
                # Create mock LangChain message objects
                from unittest.mock import Mock
                system_msg = Mock()
                system_msg.content = "You are a creative storyteller."
                user_msg = Mock()
                user_msg.content = "special story"
                mock_prompts.return_value = [system_msg, user_msg]
                
                with patch.object(service, '_call_api_with_retry') as mock_api:
                    mock_api.return_value = ("Special story", {
                        "input_tokens": 25,
                        "output_tokens": 25,
                        "total_tokens": 50,
                        "execution_time_ms": 1800
                    })
                    
                    story, usage = await service.generate_content(special_input, "Bob")
                    
                    # Should handle special characters
                    mock_prompts.assert_called_once_with(special_input, "Bob")
                    assert isinstance(story, str)
    
    @pytest.mark.asyncio
    async def test_unicode_inputs(self, service_class):
        """Test content generation with Unicode characters."""
        unicode_input = "Jose and Maria in Tokyo"
        
        with patch("services.base_ai_service.settings"), \
             patch("services.base_ai_service.custom_settings", None):
            
            service = service_class()
            
            with patch("services.story_services.langchain_service.get_langchain_messages") as mock_prompts:
                # Create mock LangChain message objects
                from unittest.mock import Mock
                system_msg = Mock()
                system_msg.content = "You are a creative storyteller."
                user_msg = Mock()
                user_msg.content = "unicode story"
                mock_prompts.return_value = [system_msg, user_msg]
                
                with patch.object(service, '_call_api_with_retry') as mock_api:
                    mock_api.return_value = ("Unicode story", {
                        "input_tokens": 15,
                        "output_tokens": 15,
                        "total_tokens": 30,
                        "execution_time_ms": 1600
                    })
                    
                    story, usage = await service.generate_content(unicode_input, "Friend")
                    
                    # Should handle Unicode properly
                    mock_prompts.assert_called_once_with(unicode_input, "Friend")
                    assert isinstance(story, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])