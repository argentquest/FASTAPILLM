"""
Custom Settings Module

This module provides extended settings for custom providers that require
additional configuration fields beyond the standard provider settings.

When PROVIDER_NAME=custom, these additional settings are loaded and made
available throughout the application.
"""

from typing import Optional, Dict, Any
from pydantic import Field, BaseModel, field_validator
from pydantic_settings import BaseSettings
import json
from logging_config import get_logger

logger = get_logger(__name__)


class CustomProviderSettings(BaseSettings):
    """Extended settings for custom providers.
    
    These settings are only loaded when PROVIDER_NAME=custom.
    Add any custom fields here that your specific provider needs.
    """
    
    # Custom authentication fields
    custom_auth_token: Optional[str] = Field(default=None, env="CUSTOM_AUTH_TOKEN")
    custom_api_secret: Optional[str] = Field(default=None, env="CUSTOM_API_SECRET")
    custom_client_id: Optional[str] = Field(default=None, env="CUSTOM_CLIENT_ID")
    custom_client_secret: Optional[str] = Field(default=None, env="CUSTOM_CLIENT_SECRET")
    
    # Custom endpoint configuration
    custom_auth_endpoint: Optional[str] = Field(default=None, env="CUSTOM_AUTH_ENDPOINT")
    custom_token_endpoint: Optional[str] = Field(default=None, env="CUSTOM_TOKEN_ENDPOINT")
    
    # Custom behavior flags
    custom_use_oauth: bool = Field(default=False, env="CUSTOM_USE_OAUTH")
    custom_require_signature: bool = Field(default=False, env="CUSTOM_REQUIRE_SIGNATURE")
    custom_enable_retry: bool = Field(default=True, env="CUSTOM_ENABLE_RETRY")
    
    # Custom metadata
    custom_tenant_id: Optional[str] = Field(default=None, env="CUSTOM_TENANT_ID")
    custom_environment: Optional[str] = Field(default="production", env="CUSTOM_ENVIRONMENT")
    custom_api_version: Optional[str] = Field(default="v1", env="CUSTOM_API_VERSION")
    custom_var: Optional[str] = Field(default=None, env="CUSTOM_VAR")
    
    # Custom request configuration
    custom_max_tokens: Optional[int] = Field(default=None, env="CUSTOM_MAX_TOKENS")
    custom_temperature: Optional[float] = Field(default=None, env="CUSTOM_TEMPERATURE")
    custom_timeout_seconds: int = Field(default=60, env="CUSTOM_TIMEOUT_SECONDS")
    
    # Custom additional headers (JSON string)
    custom_extra_headers: Optional[Dict[str, str]] = Field(default=None, env="CUSTOM_EXTRA_HEADERS")
    
    # Custom model mapping (JSON string) - maps standard models to custom model names
    custom_model_mapping: Optional[Dict[str, str]] = Field(default=None, env="CUSTOM_MODEL_MAPPING")
    
    @field_validator("custom_extra_headers", "custom_model_mapping", mode='before')
    @classmethod
    def parse_json_fields(cls, v):
        """Parse JSON string fields."""
        if v and isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON field: {e}")
                return None
        return v
    
    def get_custom_headers(self) -> Dict[str, str]:
        """Get all custom headers including extra headers."""
        headers = {}
        
        # Add authentication headers based on configuration
        if self.custom_use_oauth and self.custom_auth_token:
            headers["Authorization"] = f"Bearer {self.custom_auth_token}"
        elif self.custom_api_secret:
            headers["X-API-Secret"] = self.custom_api_secret
        
        if self.custom_client_id:
            headers["X-Client-ID"] = self.custom_client_id
        
        if self.custom_tenant_id:
            headers["X-Tenant-ID"] = self.custom_tenant_id
        
        if self.custom_environment:
            headers["X-Environment"] = self.custom_environment
        
        if self.custom_api_version:
            headers["X-API-Version"] = self.custom_api_version
        
        # Add any extra headers
        if self.custom_extra_headers:
            headers.update(self.custom_extra_headers)
        
        return headers
    
    def map_model_name(self, standard_model: str) -> str:
        """Map standard model names to custom provider model names."""
        if self.custom_model_mapping and standard_model in self.custom_model_mapping:
            return self.custom_model_mapping[standard_model]
        return standard_model
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra fields that don't belong to this model
    }


def load_custom_settings() -> Optional[CustomProviderSettings]:
    """Load custom settings if provider is 'custom'.
    
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
                       custom_environment=settings.custom_environment,
                       custom_use_oauth=settings.custom_use_oauth)
            return settings
        
        return None
        
    except Exception as e:
        logger.error(f"Failed to load custom settings: {e}")
        return None


# Example .env configuration for custom provider:
"""
# Standard provider settings
PROVIDER_NAME=custom
PROVIDER_API_KEY=your-api-key
PROVIDER_API_BASE_URL=https://custom-api.example.com/v1
PROVIDER_MODEL=custom-model-name

# Custom provider extensions (only used when PROVIDER_NAME=custom)
CUSTOM_AUTH_TOKEN=your-oauth-token
CUSTOM_API_SECRET=your-api-secret
CUSTOM_CLIENT_ID=your-client-id
CUSTOM_CLIENT_SECRET=your-client-secret
CUSTOM_TENANT_ID=your-tenant-id
CUSTOM_ENVIRONMENT=production
CUSTOM_API_VERSION=v2
CUSTOM_VAR=your-custom-string-value
CUSTOM_USE_OAUTH=true
CUSTOM_REQUIRE_SIGNATURE=false
CUSTOM_MAX_TOKENS=4000
CUSTOM_TEMPERATURE=0.7
CUSTOM_TIMEOUT_SECONDS=120
CUSTOM_EXTRA_HEADERS={"X-Custom-Header": "value", "X-Request-ID": "12345"}
CUSTOM_MODEL_MAPPING={"gpt-3.5-turbo": "custom-chat-model", "gpt-4": "custom-advanced-model"}
"""