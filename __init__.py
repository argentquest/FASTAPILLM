"""
FASTAPILLM - AI Content Generation Platform

This module provides convenient access to application configuration.
"""

# Make settings and custom_settings available at package level
try:
    from backend.config import settings
    from backend.custom_settings import custom_settings, is_custom_provider, get_provider_name
except ImportError:
    # Fallback for development/testing
    from unittest.mock import Mock
    settings = Mock()
    custom_settings = Mock()
    is_custom_provider = lambda: False
    get_provider_name = lambda: "test"

__all__ = ['settings', 'custom_settings', 'is_custom_provider', 'get_provider_name']