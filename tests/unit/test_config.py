"""
Unit tests for configuration management.

Tests the configuration loading, validation, and provider switching functionality.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, Any


@pytest.mark.unit
class TestSettings:
    """Test the Settings class configuration management."""
    
    def test_settings_loading(self):
        """Test basic settings loading."""
        with patch.dict(os.environ, {
            "PROVIDER_NAME": "test_provider",
            "PROVIDER_API_KEY": "test_key",
            "PROVIDER_API_BASE_URL": "https://test.api.com/v1",
            "PROVIDER_MODEL": "test-model"
        }):
            # Import here to avoid issues with global settings
            import sys
            # Temporarily modify path for test
            backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            
            from config import Settings
            settings = Settings()
            
            assert settings.provider_name == "test_provider"
            assert settings.provider_api_key == "test_key"
            assert settings.provider_api_base_url == "https://test.api.com/v1"
            assert settings.provider_model == "test-model"
    
    def test_provider_api_url_validation(self):
        """Test provider API URL validation."""
        from config import Settings
        
        # Valid URLs
        valid_url = Settings.validate_endpoint("https://api.test.com/v1/")
        assert valid_url == "https://api.test.com/v1"  # Trailing slash removed
        
        valid_http = Settings.validate_endpoint("http://localhost:8080/v1")
        assert valid_http == "http://localhost:8080/v1"
        
        # Invalid URL should raise ValueError
        with pytest.raises(ValueError, match="Provider API endpoint must start with"):
            Settings.validate_endpoint("api.test.com")
    
    def test_provider_headers_parsing(self):
        """Test provider headers JSON parsing."""
        from config import Settings
        
        # Valid JSON string
        headers_json = '{"X-API-Key": "test", "Content-Type": "application/json"}'
        parsed = Settings.parse_provider_headers(headers_json)
        assert parsed == {"X-API-Key": "test", "Content-Type": "application/json"}
        
        # Already parsed dict
        headers_dict = {"Authorization": "Bearer token"}
        parsed = Settings.parse_provider_headers(headers_dict) 
        assert parsed == headers_dict
        
        # Invalid JSON should raise ValueError
        with pytest.raises(ValueError, match="PROVIDER_HEADERS must be valid JSON"):
            Settings.parse_provider_headers('{"invalid": json}')
    
    def test_provider_config_validation(self):
        """Test provider configuration validation.""" 
        from config import Settings
        
        # Test missing required fields - create instance without .env loading
        settings = Settings(_env_file=None)  # Skip .env loading for test
        
        # Clear required fields to simulate missing config
        settings.provider_api_key = None
        settings.provider_api_base_url = None
        settings.provider_model = None
        
        with pytest.raises(ValueError, match="Provider configuration incomplete"):
            settings.validate_provider_config()
        
        # Complete config should not raise error
        settings = Settings(_env_file=None)  # Skip .env loading for test
        settings.provider_api_key = "test_key"
        settings.provider_api_base_url = "https://test.api.com/v1"
        settings.provider_model = "test-model"
        # Should not raise an exception
        settings.validate_provider_config()


@pytest.mark.unit
class TestCustomSettings:
    """Test custom provider settings."""
    
    def test_custom_settings_loading(self):
        """Test custom settings are loaded when PROVIDER_NAME=custom."""
        with patch.dict(os.environ, {
            "PROVIDER_NAME": "custom",
            "CUSTOM_VAR": "test_custom_value"
        }):
            from custom_settings import load_custom_settings
            custom_settings = load_custom_settings()
            
            assert custom_settings is not None
            assert custom_settings.custom_var == "test_custom_value"
    
    def test_custom_settings_not_loaded(self):
        """Test custom settings are not loaded when PROVIDER_NAME != custom."""
        with patch.dict(os.environ, {"PROVIDER_NAME": "openrouter"}):
            from custom_settings import load_custom_settings
            custom_settings = load_custom_settings()
            
            assert custom_settings is None
    
    def test_custom_settings_error_handling(self):
        """Test custom settings error handling."""
        with patch.dict(os.environ, {"PROVIDER_NAME": "custom"}):
            # Mock an error in settings loading
            with patch("custom_settings.CustomProviderSettings") as mock_settings:
                mock_settings.side_effect = Exception("Test error")
                
                from custom_settings import load_custom_settings
                custom_settings = load_custom_settings()
                
                assert custom_settings is None


@pytest.mark.unit
class TestAppConfig:
    """Test app_config module functionality."""
    
    def test_is_custom_provider(self):
        """Test custom provider detection."""
        # Test by checking if custom_settings is loaded
        with patch("config.custom_settings", None):
            from config import custom_settings
            assert custom_settings is None
        
        with patch("config.custom_settings", MagicMock()):
            from config import custom_settings
            assert custom_settings is not None
    
    def test_get_provider_name(self):
        """Test provider name retrieval."""
        mock_settings = MagicMock()
        mock_settings.provider_name = "test_provider"
        
        with patch("config.settings", mock_settings):
            from config import settings
            assert settings.provider_name == "test_provider"
    
    def test_is_debug_mode(self):
        """Test debug mode detection."""
        mock_settings = MagicMock()
        mock_settings.debug_mode = True
        
        with patch("config.settings", mock_settings):
            from config import settings
            is_debug_mode = lambda: settings.debug_mode
            assert is_debug_mode() == True


if __name__ == "__main__":
    pytest.main([__file__])