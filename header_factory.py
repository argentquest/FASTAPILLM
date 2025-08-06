"""
Header Factory Module

This module provides a factory pattern for creating provider-specific headers
based on the PROVIDER_NAME configuration. It supports standard OpenAI headers
and custom header configurations.

Usage:
    from header_factory import HeaderFactory
    from config import settings
    
    headers = HeaderFactory.create_headers(
        provider_name=settings.provider_name,
        api_key=settings.provider_api_key,
        default_headers=settings.provider_headers
    )
"""

from typing import Dict, Optional
from logging_config import get_logger

logger = get_logger(__name__)


class HeaderFactory:
    """Factory class for creating provider-specific HTTP headers.
    
    This class implements header generation for:
    - OpenAI: Standard OpenAI-compatible headers
    - Custom: Extended headers using custom settings
    """
    
    @staticmethod
    def create_headers(
        provider_name: str,
        api_key: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Create headers based on the provider name.
        
        Args:
            provider_name: The name of the provider ('openai' or 'custom')
            api_key: The API key for authentication (optional)
            default_headers: Default headers from configuration (optional)
            
        Returns:
            Dictionary of headers to use for API requests
        """
        # Start with default headers if provided
        headers = default_headers.copy() if default_headers else {}
        
        # Normalize provider name to lowercase for comparison
        provider_lower = provider_name.lower()
        
        # Apply provider-specific header logic
        if provider_lower == "openai":
            # Standard OpenAI headers - the AsyncOpenAI client handles Authorization automatically
            logger.info("Using standard OpenAI headers")
            
        elif provider_lower == "custom":
            # Custom provider with specific header requirements
            headers = HeaderFactory._create_custom_headers(api_key, headers)
            
        else:
            # For any other provider, just use the default headers
            logger.info(f"Using default headers for provider '{provider_name}'")
        
        # Log the headers being used (without sensitive data)
        safe_headers = {k: v if k.lower() not in ['authorization', 'x-api-key', 'api-key', 'x-api-secret'] 
                       else '***' for k, v in headers.items()}
        logger.info(f"Created headers for provider '{provider_name}'", headers=safe_headers)
        
        return headers
    
    @staticmethod
    def _create_custom_headers(api_key: Optional[str], base_headers: Dict[str, str]) -> Dict[str, str]:
        """Create headers for custom provider using custom settings.
        
        This method integrates with custom_settings when PROVIDER_NAME=custom
        to support extended configuration options.
        """
        headers = base_headers.copy()
        
        # Import custom settings
        from config import custom_settings
        
        if custom_settings:
            # Use custom settings to build headers
            custom_headers = custom_settings.get_custom_headers()
            headers.update(custom_headers)
            
            # If OAuth is not used and we have an API key, add it
            if not custom_settings.custom_use_oauth and api_key:
                headers["X-API-Key"] = api_key
        else:
            # Fallback if custom settings not loaded
            if api_key:
                headers["X-API-Key"] = api_key
            
            headers["X-Provider-Type"] = "custom"
            headers["X-Request-Source"] = "fastapi-llm"
        
        # Ensure content type is set
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        
        return headers


def get_provider_headers(
    provider_name: str,
    api_key: Optional[str] = None,
    default_headers: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """Convenience function to get headers for a provider.
    
    Args:
        provider_name: The name of the provider
        api_key: The API key for authentication (optional)
        default_headers: Default headers from configuration (optional)
        
    Returns:
        Dictionary of headers to use for API requests
    """
    return HeaderFactory.create_headers(provider_name, api_key, default_headers)