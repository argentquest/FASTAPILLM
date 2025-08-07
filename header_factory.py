"""
Header Factory Module

This module provides a simple factory for creating provider-specific headers
with direct access to settings and custom_settings.

ARCHITECTURE OVERVIEW:
- Single create_headers method that has access to all settings
- No registration system - headers are created directly based on provider logic
- Direct access to both main settings and custom_settings for any provider

Usage:
    from header_factory import HeaderFactory
    from config import settings, custom_settings
    
    headers = HeaderFactory.create_headers(
        provider_name=settings.provider_name,
        api_key=settings.provider_api_key,
        default_headers=settings.provider_headers,
        settings=settings,
        custom_settings=custom_settings
    )
"""

from typing import Dict, Optional, TYPE_CHECKING
from logging_config import get_logger

# Avoid circular imports
if TYPE_CHECKING:
    from config import Settings
    from custom_settings import CustomProviderSettings

logger = get_logger(__name__)


class HeaderFactory:
    """Factory class for creating provider-specific HTTP headers.
    
    ARCHITECTURE OVERVIEW:
    This factory provides a simple interface for header generation with
    direct access to both standard and custom provider configurations.
    
    DESIGN PRINCIPLES:
    1. Simplicity: Single method with direct logic, no registration system
    2. Settings Integration: Direct access to settings and custom_settings
    3. Provider Agnostic: Works with any provider name
    4. No Circular Dependencies: Uses TYPE_CHECKING imports
    
    HEADER GENERATION FLOW:
    1. Static headers from provider configuration (PROVIDER_HEADERS)
    2. Provider-specific logic (e.g., API key placement)
    3. Custom provider logic with access to settings and custom_settings
    4. Safe logging (masks sensitive headers)
    
    SUPPORTED PROVIDERS:
    - OpenAI: Standard OpenAI-compatible headers
    - Custom: Extended headers with full settings access
    - Any: Generic provider support
    """
    
    @staticmethod
    def create_headers(
        provider_name: str,
        api_key: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        settings: Optional['Settings'] = None,
        custom_settings: Optional['CustomProviderSettings'] = None
    ) -> Dict[str, str]:
        """Create headers based on provider name with full settings access.
        
        Args:
            provider_name: The name of the provider ('openai', 'custom', etc.)
            api_key: The API key for authentication (optional)
            default_headers: Default headers from configuration (optional)
            settings: Main Settings object with all configuration (optional)
            custom_settings: CustomProviderSettings object (optional)
            
        Returns:
            Dictionary of headers to use for API requests
        """
        # Start with default headers if provided
        headers = default_headers.copy() if default_headers else {}
        
        # Normalize provider name to lowercase for comparison
        provider_lower = provider_name.lower()
        
        # Apply provider-specific header logic with full settings access
        if provider_lower == "openai":
            # Standard OpenAI headers - AsyncOpenAI client handles Authorization automatically
            logger.info("Creating standard OpenAI headers")
            
        elif provider_lower == "custom":
            # Custom provider with access to all settings and custom_settings
            headers = HeaderFactory._create_custom_headers(api_key, headers, settings, custom_settings)
            
        else:
            # Generic provider - can still access settings for custom logic
            logger.info(f"Creating generic headers for provider '{provider_name}'")
            if settings:
                headers.update({
                    "X-App-Name": settings.app_name,
                    "X-App-Version": settings.app_version
                })
            
            # Add API key if provided
            if api_key:
                headers["X-API-Key"] = api_key
        
        # Add common headers based on settings (if available)
        if settings:
            if settings.debug_mode:
                headers["X-Debug-Mode"] = "true"
        
        # Custom settings can override or add to headers for any provider
        if custom_settings and custom_settings.custom_var:
            headers["X-Custom-Data"] = custom_settings.custom_var
        
        # Log the headers being used (without sensitive data)
        safe_headers = {k: v if k.lower() not in ['authorization', 'x-api-key', 'api-key', 'x-api-secret'] 
                       else '***' for k, v in headers.items()}
        logger.info(f"Created headers for provider '{provider_name}'", headers=safe_headers)
        
        return headers
    
    @staticmethod
    def _create_custom_headers(
        api_key: Optional[str], 
        base_headers: Dict[str, str],
        settings: Optional['Settings'],
        custom_settings: Optional['CustomProviderSettings']
    ) -> Dict[str, str]:
        """Create headers for custom provider with full settings access.
        
        Args:
            api_key: API key for authentication
            base_headers: Base headers to start with
            settings: Main settings object
            custom_settings: Custom provider settings
        """
        headers = base_headers.copy()
        
        # Add API key if provided
        if api_key:
            headers["X-API-Key"] = api_key
        
        # Add basic custom provider headers
        headers["X-Provider-Type"] = "custom"
        headers["X-Request-Source"] = "fastapi-llm"
        
        # Add settings-based headers if available
        if settings:
            headers["X-App-Name"] = settings.app_name
            headers["X-App-Version"] = settings.app_version
            
            if settings.debug_mode:
                headers["X-Debug-Mode"] = "enabled"
                headers["X-Debug-Level"] = "verbose"
            
            # Add timeout info for debugging
            headers["X-Timeout"] = str(settings.api_timeout)
        
        # Add custom provider specific headers
        if custom_settings:
            # Access the custom variable
            if custom_settings.custom_var:
                headers["X-Custom-Var"] = custom_settings.custom_var
            
            # Custom settings has ALL default settings too, so we can access anything
            headers["X-Provider-Name"] = custom_settings.provider_name
            
            # Example: Use custom settings for advanced configuration
            if custom_settings.rate_limiting_enabled:
                headers["X-Rate-Limit-Enabled"] = "true"
        
        # Ensure content type is set
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        
        logger.info("Created custom provider headers with settings integration")
        return headers


def get_provider_headers(
    provider_name: str,
    api_key: Optional[str] = None,
    default_headers: Optional[Dict[str, str]] = None,
    settings: Optional['Settings'] = None,
    custom_settings: Optional['CustomProviderSettings'] = None
) -> Dict[str, str]:
    """Convenience function to get headers for a provider.
    
    Args:
        provider_name: The name of the provider
        api_key: The API key for authentication (optional)
        default_headers: Default headers from configuration (optional)
        settings: Main Settings object for header functions (optional)
        custom_settings: CustomProviderSettings object for header functions (optional)
        
    Returns:
        Dictionary of headers to use for API requests
    """
    return HeaderFactory.create_headers(provider_name, api_key, default_headers, settings, custom_settings)