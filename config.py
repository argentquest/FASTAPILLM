import os
import sys
from typing import Optional, Dict
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ValidationInfo
import structlog
import json

logger = structlog.get_logger()

class Settings(BaseSettings):
    """Application settings with environment variable support.
    
    This class manages all configuration settings for the AI Story Generator
    application. It supports multiple LLM providers (Azure OpenAI, OpenRouter,
    and custom providers) and validates configuration based on the selected
    provider.
    
    All settings can be overridden using environment variables or a .env file.
    
    Attributes:
        llm_provider: The LLM provider to use ("azure", "openrouter", or "custom").
        azure_openai_*: Configuration for Azure OpenAI.
        openrouter_*: Configuration for OpenRouter.
        custom_*: Configuration for custom LLM providers.
        app_name: Application name for logging and identification.
        debug_mode: Whether to enable debug mode.
        cors_origins: Allowed CORS origins.
        api_timeout: General API timeout in seconds.
        log_*: Logging configuration settings.
        max_character_length: Maximum allowed character name length.
        min_character_length: Minimum allowed character name length.
        
    Examples:
        >>> settings = Settings(llm_provider="azure")
        >>> settings.validate_provider_config()
    """
    # Provider Configuration
    llm_provider: str = Field(default="azure", env="LLM_PROVIDER")  # "azure", "openrouter", or "custom"
    
    # Azure OpenAI Configuration
    azure_openai_api_key: Optional[str] = Field(default=None, env="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: Optional[str] = Field(default=None, env="AZURE_OPENAI_ENDPOINT")
    azure_openai_deployment_name: Optional[str] = Field(default=None, env="AZURE_OPENAI_DEPLOYMENT_NAME")
    azure_openai_api_version: str = Field(default="2024-02-01", env="AZURE_OPENAI_API_VERSION")
    
    # OpenRouter Configuration
    openrouter_api_key: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    openrouter_model: str = Field(default="openai/gpt-4-turbo-preview", env="OPENROUTER_MODEL")
    openrouter_site_url: Optional[str] = Field(default=None, env="OPENROUTER_SITE_URL")
    openrouter_app_name: Optional[str] = Field(default="AI Story Generator", env="OPENROUTER_APP_NAME")
    
    # Custom Provider Configuration (e.g., Tachyon)
    custom_api_key: Optional[str] = Field(default=None, env="CUSTOM_API_KEY")
    custom_api_base_url: Optional[str] = Field(default=None, env="CUSTOM_API_BASE_URL")
    custom_model: Optional[str] = Field(default=None, env="CUSTOM_MODEL")
    custom_api_type: str = Field(default="openai", env="CUSTOM_API_TYPE")  # "openai" or "custom"
    custom_headers: Optional[Dict[str, str]] = Field(default=None, env="CUSTOM_HEADERS")
    custom_api_version: Optional[str] = Field(default=None, env="CUSTOM_API_VERSION")
    custom_provider_name: str = Field(default="Custom LLM", env="CUSTOM_PROVIDER_NAME")
    
    # Application Configuration
    app_name: str = Field(default="AI Story Generator", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    
    
    # Security Configuration
    cors_origins: list[str] = Field(default=["http://localhost:8000"], env="CORS_ORIGINS")
    max_request_size: int = Field(default=1048576, env="MAX_REQUEST_SIZE")  # 1MB
    
    # Timeout Configuration
    api_timeout: int = Field(default=30, env="API_TIMEOUT")  # seconds
    openai_timeout: int = Field(default=60, env="OPENAI_TIMEOUT")  # seconds
    
    # Logging Configuration
    log_file_path: Optional[str] = Field(default="logs/app.log", env="LOG_FILE_PATH")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_rotation_hours: int = Field(default=1, env="LOG_ROTATION_HOURS")
    log_retention_days: int = Field(default=7, env="LOG_RETENTION_DAYS")
    
    # Input Validation
    max_character_length: int = Field(default=100, env="MAX_CHARACTER_LENGTH")
    min_character_length: int = Field(default=1, env="MIN_CHARACTER_LENGTH")
    
    @field_validator("azure_openai_endpoint")
    @classmethod
    def validate_endpoint(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize Azure OpenAI endpoint URL.
        
        Ensures the endpoint URL has proper protocol and removes trailing slashes.
        
        Args:
            v: The endpoint URL to validate.
            
        Returns:
            The normalized endpoint URL or None.
            
        Raises:
            ValueError: If the endpoint doesn't start with https:// or http://.
            
        Examples:
            >>> Settings.validate_endpoint("https://api.azure.com/")
            'https://api.azure.com'
            >>> Settings.validate_endpoint("api.azure.com")
            ValueError: Azure OpenAI endpoint must start with https:// or http://
        """
        if v and not v.startswith(("https://", "http://")):
            raise ValueError("Azure OpenAI endpoint must start with https:// or http://")
        return v.rstrip("/") if v else v
    
    @field_validator("llm_provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate the LLM provider selection.
        
        Ensures only supported LLM providers are configured.
        
        Args:
            v: The provider name to validate.
            
        Returns:
            The validated provider name.
            
        Raises:
            ValueError: If the provider is not supported.
            
        Examples:
            >>> Settings.validate_provider("azure")
            'azure'
            >>> Settings.validate_provider("invalid")
            ValueError: LLM provider must be 'azure', 'openrouter', or 'custom'
        """
        logger.debug("Validating LLM provider", provider=v)
        if v not in ["azure", "openrouter", "custom"]:
            logger.error("Invalid LLM provider specified", 
                        provider=v, 
                        valid_providers=["azure", "openrouter", "custom"])
            raise ValueError("LLM provider must be 'azure', 'openrouter', or 'custom'")
        logger.info("LLM provider validated successfully", provider=v)
        return v
    
    @field_validator("custom_headers")
    @classmethod
    def parse_custom_headers(cls, v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Parse custom headers from environment variable.
        
        Handles JSON string parsing when headers are provided as an
        environment variable string.
        
        Args:
            v: The headers value (string or dict).
            
        Returns:
            Parsed headers as a dictionary or None.
            
        Raises:
            ValueError: If the JSON string is invalid.
            
        Examples:
            >>> Settings.parse_custom_headers('{"X-API-Key": "secret"}')
            {'X-API-Key': 'secret'}
            >>> Settings.parse_custom_headers({'X-API-Key': 'secret'})
            {'X-API-Key': 'secret'}
        """
        if v and isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("CUSTOM_HEADERS must be valid JSON")
        return v
    
    def validate_provider_config(self) -> None:
        """Validate that required fields are set based on provider.
        
        Ensures all necessary configuration fields are provided for the
        selected LLM provider. This method should be called after settings
        are loaded to verify the configuration is complete.
        
        Raises:
            ValueError: If required configuration fields are missing for
                the selected provider.
                
        Examples:
            >>> settings = Settings(llm_provider="azure")
            >>> settings.azure_openai_api_key = "key"
            >>> settings.azure_openai_endpoint = "https://api.azure.com"
            >>> settings.azure_openai_deployment_name = "gpt-35-turbo"
            >>> settings.validate_provider_config()  # No exception
        """
        if self.llm_provider == "azure":
            if not all([self.azure_openai_api_key, self.azure_openai_endpoint, self.azure_openai_deployment_name]):
                raise ValueError("Azure provider requires AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME")
        elif self.llm_provider == "openrouter":
            if not self.openrouter_api_key:
                raise ValueError("OpenRouter provider requires OPENROUTER_API_KEY")
        elif self.llm_provider == "custom":
            if not all([self.custom_api_key, self.custom_api_base_url, self.custom_model]):
                raise ValueError("Custom provider requires CUSTOM_API_KEY, CUSTOM_API_BASE_URL, and CUSTOM_MODEL")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }

def load_settings() -> Settings:
    """Load and validate application settings.
    
    Loads settings from environment variables and .env file, validates
    the configuration, and returns a Settings instance. If configuration
    loading fails, the application exits with an error.
    
    Returns:
        A validated Settings instance with all configuration loaded.
        
    Raises:
        SystemExit: If configuration loading or validation fails.
        
    Examples:
        >>> settings = load_settings()
        >>> print(settings.app_name)
        'AI Story Generator'
    """
    try:
        settings = Settings()
        settings.validate_provider_config()
        logger.info("Configuration loaded successfully", 
                   app_name=settings.app_name,
                   debug_mode=settings.debug_mode,
                   llm_provider=settings.llm_provider)
        return settings
    except Exception as e:
        logger.error("Failed to load configuration", error=str(e))
        sys.exit(1)

# Global settings instance
settings = load_settings()