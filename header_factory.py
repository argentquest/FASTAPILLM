"""
Header Factory Module

This module provides a factory pattern for creating provider-specific headers
based on the PROVIDER_NAME configuration. It supports standard OpenAI headers
and custom header configurations.

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
    
    # Or register a custom header function
    def my_headers(settings, custom_settings):
        return {
            "X-App": settings.app_name,
            "X-Custom": custom_settings.custom_var if custom_settings else None
        }
    
    HeaderFactory.register_header_function("myprovider", my_headers)
"""

from typing import Dict, Optional, Callable, Any, TYPE_CHECKING
from logging_config import get_logger
import inspect

# Avoid circular imports
if TYPE_CHECKING:
    from config import Settings
    from custom_settings import CustomProviderSettings

logger = get_logger(__name__)


class HeaderFactory:
    """Factory class for creating provider-specific HTTP headers.
    
    ARCHITECTURE OVERVIEW:
    This factory provides a clean interface for header generation that integrates
    with both standard and custom provider configurations.
    
    DESIGN PRINCIPLES:
    1. Provider Agnostic: Works with any provider name
    2. Settings Integration: Automatically passes settings to header functions
    3. Function Signature Detection: Automatically detects what parameters functions expect
    4. No Circular Dependencies: Uses TYPE_CHECKING imports to avoid circular imports
    
    HEADER GENERATION FLOW:
    1. Static headers from provider configuration (PROVIDER_HEADERS)
    2. Provider-specific logic (e.g., API key placement)
    3. Registered dynamic header functions (with settings access)
    4. Safe logging (masks sensitive headers)
    
    SUPPORTED PROVIDERS:
    - OpenAI: Standard OpenAI-compatible headers (AsyncOpenAI handles Authorization)
    - Custom: Extended headers with CUSTOM_VAR access
    - Any: Registered functions work with any provider name
    """
    
    # Registry for custom header functions
    # Functions can accept (settings, custom_settings) parameters or no parameters
    # The factory automatically detects function signatures and passes appropriate parameters
    _header_functions: Dict[str, Callable[..., Dict[str, str]]] = {}
    
    @classmethod
    def register_header_function(cls, provider_name: str, func: Callable[..., Dict[str, str]]) -> None:
        """Register a custom header function for a specific provider.
        
        The function can optionally accept parameters:
        - settings: Main Settings object
        - custom_settings: CustomProviderSettings object (may be None)
        
        Args:
            provider_name: The provider name to associate with this function
            func: A callable that returns a dictionary of headers
            
        Example (no parameters):
            def my_custom_headers():
                return {"X-Custom": "value"}
            
        Example (with settings):
            def my_custom_headers(settings, custom_settings):
                headers = {"X-App": settings.app_name}
                if custom_settings and custom_settings.custom_var:
                    headers["X-Custom-Var"] = custom_settings.custom_var
                return headers
            
            HeaderFactory.register_header_function("mycustom", my_custom_headers)
        """
        cls._header_functions[provider_name.lower()] = func
        logger.info(f"Registered custom header function for provider '{provider_name}'")
    
    @classmethod
    def unregister_header_function(cls, provider_name: str) -> None:
        """Unregister a custom header function.
        
        Args:
            provider_name: The provider name to unregister
        """
        provider_lower = provider_name.lower()
        if provider_lower in cls._header_functions:
            del cls._header_functions[provider_lower]
            logger.info(f"Unregistered custom header function for provider '{provider_name}'")
    
    @classmethod
    def list_registered_functions(cls) -> Dict[str, str]:
        """List all registered header functions.
        
        Returns:
            Dictionary mapping provider names to function names
        """
        return {
            provider: func.__name__ for provider, func in cls._header_functions.items()
        }
    
    @staticmethod
    def create_headers(
        provider_name: str,
        api_key: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        settings: Optional['Settings'] = None,
        custom_settings: Optional['CustomProviderSettings'] = None
    ) -> Dict[str, str]:
        """Create headers based on the provider name.
        
        Args:
            provider_name: The name of the provider ('openai' or 'custom')
            api_key: The API key for authentication (optional)
            default_headers: Default headers from configuration (optional)
            settings: Main Settings object for header functions (optional)
            custom_settings: CustomProviderSettings object for header functions (optional)
            
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
        
        # Check if there's a registered header function for this provider
        # ARCHITECTURE NOTE: This is the key integration point between HeaderFactory and settings
        if provider_lower in HeaderFactory._header_functions:
            try:
                func = HeaderFactory._header_functions[provider_lower]
                
                # CRITICAL: Dynamic function signature detection
                # This allows backward compatibility with functions that don't need settings
                # while providing full settings access to functions that do
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                
                # Call function with appropriate parameters based on signature
                if len(params) == 0:
                    # Legacy functions with no parameters (backward compatibility)
                    dynamic_headers = func()
                elif len(params) >= 2:
                    # Modern functions that accept (settings, custom_settings)
                    # This is the preferred pattern for new header functions
                    dynamic_headers = func(settings, custom_settings)
                else:
                    # Functions that only want the main settings object
                    dynamic_headers = func(settings)
                
                if isinstance(dynamic_headers, dict):
                    headers.update(dynamic_headers)
                    logger.info(f"Applied dynamic headers from function '{func.__name__}' for provider '{provider_name}'")
                else:
                    logger.warning(f"Header function '{func.__name__}' returned non-dict: {type(dynamic_headers)}")
            except Exception as e:
                logger.error(f"Error calling header function for provider '{provider_name}': {e}", exc_info=True)
        
        # Log the headers being used (without sensitive data)
        safe_headers = {k: v if k.lower() not in ['authorization', 'x-api-key', 'api-key', 'x-api-secret'] 
                       else '***' for k, v in headers.items()}
        logger.info(f"Created headers for provider '{provider_name}'", headers=safe_headers)
        
        return headers
    
    @staticmethod
    def _create_custom_headers(api_key: Optional[str], base_headers: Dict[str, str]) -> Dict[str, str]:
        """Create headers for custom provider.
        
        This method creates basic headers for custom providers. Dynamic headers
        should be added via HeaderFactory.register_header_function() which are
        applied automatically in the main create_headers() method.
        """
        headers = base_headers.copy()
        
        # Add API key if provided
        if api_key:
            headers["X-API-Key"] = api_key
        
        # Add basic custom provider headers
        headers["X-Provider-Type"] = "custom"
        headers["X-Request-Source"] = "fastapi-llm"
        
        # Ensure content type is set
        if "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"
        
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