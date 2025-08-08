"""
Unit tests for ContentGenerationService.

Tests the abstract base class for content generation services including:
- Abstract method contract enforcement
- Integration with BaseAIService
- Method signature validation
- Service hierarchy behavior
"""

import pytest
from unittest.mock import Mock, patch
from abc import ABC
from typing import Tuple, Dict, Any


@pytest.mark.unit
class TestContentGenerationService:
    """Test ContentGenerationService abstract base class."""
    
    @pytest.fixture
    def service_class(self):
        """Import ContentGenerationService class."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.content_generation_service import ContentGenerationService
        return ContentGenerationService
    
    def test_is_abstract_base_class(self, service_class):
        """Test that ContentGenerationService is an abstract base class."""
        assert issubclass(service_class, ABC)
        
        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            service_class()
    
    def test_inherits_from_base_ai_service(self, service_class):
        """Test that ContentGenerationService inherits from BaseAIService."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.base_ai_service import BaseAIService
        
        assert issubclass(service_class, BaseAIService)
    
    def test_abstract_method_signature(self, service_class):
        """Test that generate_content has correct abstract method signature."""
        # Check that generate_content is an abstract method
        abstract_methods = service_class.__abstractmethods__
        assert 'generate_content' in abstract_methods
        
        # Check method signature exists
        assert hasattr(service_class, 'generate_content')
    
    def test_concrete_implementation_works(self, service_class):
        """Test that concrete implementations can be created."""
        # Create a concrete implementation
        class ConcreteContentService(service_class):
            async def generate_content(self, primary_input: str, secondary_input: str) -> Tuple[str, Dict[str, Any]]:
                return "Generated content", {
                    "input_tokens": 50,
                    "output_tokens": 25,
                    "total_tokens": 75,
                    "execution_time_ms": 1000,
                    "estimated_cost_usd": 0.001
                }
        
        # Should be able to instantiate concrete implementation
        with patch("services.base_ai_service.settings"), \
             patch("services.base_ai_service.custom_settings", None):
            service = ConcreteContentService()
            assert service is not None
            assert isinstance(service, service_class)
    
    @pytest.mark.asyncio
    async def test_concrete_implementation_method_call(self, service_class):
        """Test that concrete implementation methods work correctly."""
        expected_content = "Test generated content"
        expected_usage = {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
            "execution_time_ms": 1500,
            "estimated_cost_usd": 0.002,
            "input_cost": 0.001,
            "output_cost": 0.001
        }
        
        class TestContentService(service_class):
            async def generate_content(self, primary_input: str, secondary_input: str) -> Tuple[str, Dict[str, Any]]:
                assert isinstance(primary_input, str)
                assert isinstance(secondary_input, str)
                return expected_content, expected_usage
        
        with patch("services.base_ai_service.settings"), \
             patch("services.base_ai_service.custom_settings", None):
            
            service = TestContentService()
            content, usage = await service.generate_content("primary", "secondary")
            
            assert content == expected_content
            assert usage == expected_usage
            assert usage["total_tokens"] == usage["input_tokens"] + usage["output_tokens"]
    
    def test_incomplete_implementation_fails(self, service_class):
        """Test that incomplete implementations cannot be instantiated."""
        # Create class that doesn't implement abstract method
        class IncompleteService(service_class):
            pass  # Missing generate_content implementation
        
        # Should raise TypeError when trying to instantiate
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteService()
    
    def test_method_signature_validation(self, service_class):
        """Test method signature validation for generate_content."""
        # Create implementation with wrong signature
        class WrongSignatureService(service_class):
            async def generate_content(self, wrong_param):  # Wrong signature
                return "content", {}
        
        # This should still be instantiable (Python doesn't enforce signatures at runtime)
        with patch("services.base_ai_service.settings"), \
             patch("services.base_ai_service.custom_settings", None):
            service = WrongSignatureService()
            assert service is not None
    
    def test_return_type_expectations(self, service_class):
        """Test that return type expectations are documented correctly."""
        # Check docstring for return type documentation
        generate_method = service_class.generate_content
        assert generate_method.__doc__ is not None
        assert "tuple" in generate_method.__doc__.lower()  # Check for lowercase tuple
        assert "usage_info" in generate_method.__doc__
        assert "input_tokens" in generate_method.__doc__
        assert "output_tokens" in generate_method.__doc__
    
    def test_inheritance_chain(self, service_class):
        """Test the complete inheritance chain."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.base_ai_service import BaseAIService
        
        # ContentGenerationService -> BaseAIService -> TransactionAware -> ABC
        assert issubclass(service_class, BaseAIService)
        assert issubclass(service_class, ABC)
        
        # Should have all BaseAIService functionality
        class TestService(service_class):
            async def generate_content(self, primary_input: str, secondary_input: str) -> Tuple[str, Dict[str, Any]]:
                return "content", {}
        
        with patch("services.base_ai_service.settings"), \
             patch("services.base_ai_service.custom_settings", None):
            service = TestService()
            
            # Should have BaseAIService attributes
            assert hasattr(service, 'service_name')
            assert hasattr(service, 'provider_name')
            assert hasattr(service, '_client')
            assert hasattr(service, '_ensure_client')


@pytest.mark.unit
class TestContentGenerationServiceImplementations:
    """Test realistic implementations of ContentGenerationService."""
    
    @pytest.fixture
    def service_class(self):
        """Import ContentGenerationService class."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.content_generation_service import ContentGenerationService
        return ContentGenerationService
    
    @pytest.fixture
    def mock_story_service(self, service_class):
        """Create a realistic story service implementation."""
        class MockStoryService(service_class):
            async def generate_content(self, primary_input: str, secondary_input: str) -> Tuple[str, Dict[str, Any]]:
                """Generate a story with the given characters."""
                story = f"Once upon a time, {primary_input} met {secondary_input} and they went on an adventure."
                
                usage = {
                    "input_tokens": len(primary_input + secondary_input) // 4,  # Rough estimate
                    "output_tokens": len(story) // 4,
                    "total_tokens": 0,
                    "execution_time_ms": 1000,
                    "estimated_cost_usd": 0.001,
                    "input_cost": 0.0005,
                    "output_cost": 0.0005
                }
                usage["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
                
                return story, usage
        
        return MockStoryService
    
    @pytest.mark.asyncio
    async def test_realistic_story_generation(self, mock_story_service):
        """Test realistic story generation implementation."""
        with patch("services.base_ai_service.settings"), \
             patch("services.base_ai_service.custom_settings", None):
            
            service = mock_story_service()
            
            story, usage = await service.generate_content("Alice", "Bob")
            
            # Verify story content
            assert "Alice" in story
            assert "Bob" in story
            assert "adventure" in story
            
            # Verify usage info structure
            assert "input_tokens" in usage
            assert "output_tokens" in usage
            assert "total_tokens" in usage
            assert "execution_time_ms" in usage
            assert "estimated_cost_usd" in usage
            
            # Verify calculations
            assert usage["total_tokens"] == usage["input_tokens"] + usage["output_tokens"]
            assert usage["estimated_cost_usd"] > 0
    
    def test_service_name_inheritance(self, mock_story_service):
        """Test that service name is properly inherited."""
        with patch("services.base_ai_service.settings"), \
             patch("services.base_ai_service.custom_settings", None):
            
            service = mock_story_service()
            assert service.service_name == "MockStoryService"
    
    def test_provider_configuration_inheritance(self, mock_story_service):
        """Test that provider configuration is inherited from BaseAIService."""
        with patch("services.base_ai_service.settings") as mock_settings, \
             patch("services.base_ai_service.custom_settings", None):
            
            mock_settings.provider_name = "test_provider"
            
            service = mock_story_service()
            assert service.provider_name == "test_provider"
    
    def test_custom_settings_access(self, mock_story_service):
        """Test access to custom settings in content services."""
        with patch("services.base_ai_service.settings"), \
             patch("services.base_ai_service.custom_settings") as mock_custom:
            
            mock_custom.custom_var = "custom_value"
            
            service = mock_story_service()
            assert service.custom_settings == mock_custom
            assert service.custom_settings.custom_var == "custom_value"


@pytest.mark.unit
class TestContentGenerationServiceDocumentation:
    """Test documentation and contract specification."""
    
    @pytest.fixture
    def service_class(self):
        """Import ContentGenerationService class."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[3] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from services.content_generation_service import ContentGenerationService
        return ContentGenerationService
    
    def test_class_documentation(self, service_class):
        """Test that class has proper documentation."""
        assert service_class.__doc__ is not None
        assert "abstract base class" in service_class.__doc__.lower()
        assert "content generation" in service_class.__doc__.lower()
    
    def test_method_documentation(self, service_class):
        """Test that generate_content method has proper documentation."""
        method_doc = service_class.generate_content.__doc__
        assert method_doc is not None
        assert "primary_input" in method_doc
        assert "secondary_input" in method_doc
        assert "Returns" in method_doc
        assert "usage_info" in method_doc
    
    def test_usage_info_specification(self, service_class):
        """Test that usage_info specification is documented."""
        method_doc = service_class.generate_content.__doc__
        
        # Check that all expected usage fields are documented
        expected_fields = [
            "input_tokens",
            "output_tokens", 
            "total_tokens",
            "execution_time_ms",
            "estimated_cost_usd"
        ]
        
        for field in expected_fields:
            assert field in method_doc, f"Field {field} not documented in usage_info"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])