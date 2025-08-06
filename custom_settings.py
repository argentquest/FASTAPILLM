"""
Custom Settings Module

ARCHITECTURE OVERVIEW:
This module provides extended configuration for custom providers while maintaining
full access to all default application settings.

DESIGN PRINCIPLES:
1. Conditional Loading: Only loads when PROVIDER_NAME=custom
2. Complete Inheritance: Contains ALL fields from main Settings class
3. Single Extension: Adds only CUSTOM_VAR field
4. No Circular Dependencies: Avoids importing from config.py

SETTINGS HIERARCHY:
- Main Settings (config.py): All default application configuration
- CustomProviderSettings: All default settings + CUSTOM_VAR extension
- HeaderFactory: Consumes both settings objects for dynamic header generation

HeaderFactory Integration:
- Static headers: Use PROVIDER_HEADERS environment variable (inherited from main settings)
- Programmatic headers: Use HeaderFactory.register_header_function() to register custom header logic
- The HeaderFactory will automatically use registered functions when provider_name="custom"
- Custom header functions receive (settings, custom_settings) parameters automatically

Example Usage:
    # In your initialization code
    from header_factory import HeaderFactory
    from config import settings, custom_settings
    
    def generate_custom_headers(settings, custom_settings):
        headers = {
            "X-App-Name": settings.app_name,        # Access all default settings
            "X-Debug": str(settings.debug_mode),     # Timeouts, logging, etc.
        }
        if custom_settings and custom_settings.custom_var:
            headers["X-Custom-Var"] = custom_settings.custom_var
        return headers
    
    HeaderFactory.register_header_function("custom", generate_custom_headers)
"""

from typing import Optional, Dict
from pydantic import Field, field_validator, AliasChoices
from pydantic_settings import BaseSettings
from logging_config import get_logger
import json

logger = get_logger(__name__)


class CustomProviderSettings(BaseSettings):
    """Custom provider settings with all default application settings.
    
    This class loads ALL default application settings from .env (same as main Settings class)
    plus the additional CUSTOM_VAR field when PROVIDER_NAME=custom.
    
    This ensures that when using a custom provider, you have access to:
    - All default application settings (debug_mode, cors_origins, timeouts, etc.)
    - All default provider settings (api_key, base_url, model, etc.)
    - The additional CUSTOM_VAR field
    """
    
    # =============================================================================
    # PROVIDER CONFIGURATION (inherited from main settings)
    # =============================================================================
    provider_api_key: Optional[str] = Field(default=None, validation_alias=AliasChoices("PROVIDER_API_KEY"))
    provider_api_base_url: Optional[str] = Field(default=None, validation_alias=AliasChoices("PROVIDER_API_BASE_URL"))
    provider_model: Optional[str] = Field(default=None, validation_alias=AliasChoices("PROVIDER_MODEL"))
    provider_api_type: str = Field(default="openai", validation_alias=AliasChoices("PROVIDER_API_TYPE"))
    provider_headers: Optional[Dict[str, str]] = Field(default=None, validation_alias=AliasChoices("PROVIDER_HEADERS"))
    provider_name: str = Field(default="Custom Provider", validation_alias=AliasChoices("PROVIDER_NAME"))
    
    # =============================================================================
    # APPLICATION CONFIGURATION (inherited from main settings)
    # =============================================================================
    app_name: str = Field(default="AI Testing Suite", validation_alias=AliasChoices("APP_NAME"))
    app_version: str = Field(default="1.0.0", validation_alias=AliasChoices("APP_VERSION"))
    debug_mode: bool = Field(default=False, validation_alias=AliasChoices("DEBUG_MODE"))
    
    # =============================================================================
    # TIMEOUT CONFIGURATION (inherited from main settings)
    # =============================================================================
    api_timeout: int = Field(default=30, validation_alias=AliasChoices("API_TIMEOUT"))
    openai_timeout: int = Field(default=60, validation_alias=AliasChoices("OPENAI_TIMEOUT"))
    
    # =============================================================================
    # LOGGING CONFIGURATION (inherited from main settings)
    # =============================================================================
    log_file_path: Optional[str] = Field(default="logs/app.log", validation_alias=AliasChoices("LOG_FILE_PATH"))
    log_level: str = Field(default="INFO", validation_alias=AliasChoices("LOG_LEVEL"))
    log_rotation_hours: int = Field(default=1, validation_alias=AliasChoices("LOG_ROTATION_HOURS"))
    log_retention_days: int = Field(default=7, validation_alias=AliasChoices("LOG_RETENTION_DAYS"))
    
    # =============================================================================
    # RETRY CONFIGURATION (inherited from main settings)
    # =============================================================================
    retry_enabled: bool = Field(default=True, validation_alias=AliasChoices("RETRY_ENABLED"))
    retry_max_attempts: int = Field(default=3, validation_alias=AliasChoices("RETRY_MAX_ATTEMPTS"))
    retry_max_wait_seconds: int = Field(default=30, validation_alias=AliasChoices("RETRY_MAX_WAIT_SECONDS"))
    retry_multiplier: float = Field(default=2.0, validation_alias=AliasChoices("RETRY_MULTIPLIER"))
    retry_min_wait_seconds: float = Field(default=1.0, validation_alias=AliasChoices("RETRY_MIN_WAIT_SECONDS"))
    
    # =============================================================================
    # RATE LIMITING CONFIGURATION (inherited from main settings)
    # =============================================================================
    rate_limiting_enabled: bool = Field(default=True, validation_alias=AliasChoices("RATE_LIMITING_ENABLED"))
    rate_limit_per_ip: int = Field(default=60, validation_alias=AliasChoices("RATE_LIMIT_PER_IP"))
    rate_limit_story_generation: int = Field(default=15, validation_alias=AliasChoices("RATE_LIMIT_STORY_GENERATION"))
    rate_limit_list_endpoints: int = Field(default=30, validation_alias=AliasChoices("RATE_LIMIT_LIST_ENDPOINTS"))
    rate_limit_health_status: int = Field(default=100, validation_alias=AliasChoices("RATE_LIMIT_HEALTH_STATUS"))
    rate_limit_global_server: int = Field(default=1000, validation_alias=AliasChoices("RATE_LIMIT_GLOBAL_SERVER"))
    
    # =============================================================================
    # CUSTOM PROVIDER EXTENSION
    # =============================================================================
    # Single custom variable from environment - the only addition to default settings
    # This value can be accessed by HeaderFactory registered functions for dynamic header generation
    custom_var: Optional[str] = Field(default=None, validation_alias=AliasChoices("CUSTOM_VAR"))
    
    @field_validator("provider_headers", mode='before')
    @classmethod
    def parse_provider_headers(cls, v):
        """Parse JSON string provider headers."""
        if v and isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse PROVIDER_HEADERS JSON: {e}")
                return None
        return v
    
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra fields that don't belong to this model
    }


def load_custom_settings() -> Optional[CustomProviderSettings]:
    """Load custom settings if provider is 'custom'.
    
    This function only loads CustomProviderSettings when PROVIDER_NAME=custom.
    The CustomProviderSettings inherits all default application settings
    from the same .env file, plus adds the CUSTOM_VAR field.
    
    HeaderFactory Integration:
        The returned settings instance can be used by HeaderFactory registered functions
        to access custom_var and other settings for dynamic header generation.
        
        Example:
            custom_settings = load_custom_settings()
            def my_headers():
                return {"X-Custom": custom_settings.custom_var}
            HeaderFactory.register_header_function("custom", my_headers)
    
    Returns:
        CustomProviderSettings instance if PROVIDER_NAME=custom, None otherwise
    """
    try:
        # Only load if we're using custom provider
        import os
        provider_name = os.getenv("PROVIDER_NAME", "").lower()
        
        if provider_name == "custom":
            settings = CustomProviderSettings()
            logger.info("Loaded custom provider settings", 
                       custom_var=settings.custom_var)
            return settings
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to load custom settings: {e}")
        return None