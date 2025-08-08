"""
Application Configuration - Central Access Point

This module provides a single import point for accessing application settings
and custom provider settings throughout the codebase.

Usage:
    from app_config import settings, custom_settings
    
    # Access any setting
    print(settings.app_name)
    print(settings.provider_name)
    
    # Check if custom provider is active
    if custom_settings:
        print(custom_settings.custom_var)

Settings are loaded once at startup and remain constant during runtime.
"""

# Import the global settings instances
try:
    # When running from backend directory
    from config import settings, custom_settings
except ImportError:
    # When imported as package from root
    from .config import settings, custom_settings

# Re-export for convenient access
__all__ = ['settings', 'custom_settings']

# Optionally, you can add helper functions here
def is_custom_provider() -> bool:
    """Check if the application is using a custom provider."""
    return custom_settings is not None

def get_provider_name() -> str:
    """Get the current provider name."""
    return settings.provider_name

def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return settings.debug_mode

def get_custom_var() -> str | None:
    """Get the custom variable if using custom provider."""
    return custom_settings.custom_var if custom_settings else None

# Log current configuration for debugging
try:
    from logging_config import get_logger
except ImportError:
    from .logging_config import get_logger
logger = get_logger(__name__)

logger.info(
    "Application configuration loaded",
    provider=settings.provider_name,
    is_custom=is_custom_provider(),
    debug_mode=settings.debug_mode,
    app_name=settings.app_name
)