# Configuration module for the AI Testing Suite Platform
# Handles all application settings including provider configuration,
# security settings, and application parameters using Pydantic.

import os
import sys
from typing import Optional, Dict
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, ValidationInfo, AliasChoices
import structlog
import json

# Initialize structured logger for configuration events
logger = structlog.get_logger()

class Settings(BaseSettings):
    """Application settings with environment variable support.
    
    This class manages all configuration settings for the AI Testing Suite
    application using any OpenAI-compatible LLM provider (OpenRouter, Ollama,
    Tachyon, etc.).
    
    All settings can be overridden using environment variables or a .env file.
    The class automatically loads from .env files and validates all settings.
    
    Provider Configuration:
        provider_api_key: API key for authentication with your provider
        provider_api_base_url: Base URL for API calls (must be OpenAI-compatible)
        provider_model: Model identifier (e.g., 'llama2', 'gpt-3.5-turbo')
        provider_name: Display name for the provider
        provider_api_type: API compatibility type (currently only 'openai')
        provider_headers: Additional HTTP headers as JSON (for auth, etc.)
        
    Application Settings:
        app_name: Application name for logging and identification
        debug_mode: Enable debug logging and extended error messages
        cors_origins: List of allowed CORS origins for web requests
        api_timeout: General API timeout in seconds
        
    Security & Validation:
        max_character_length: Maximum allowed character name length
        min_character_length: Minimum allowed character name length
        max_request_size: Maximum HTTP request size in bytes
        
    Logging Configuration:
        log_file_path: Path to log file
        log_level: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
        log_rotation_hours: Hours between log file rotations
        log_retention_days: Days to keep old log files
        
    Examples:
        >>> # Load settings from environment and .env file
        >>> settings = Settings()
        >>> settings.validate_provider_config()  # Validates required fields
        >>> 
        >>> # Access provider settings
        >>> print(f"Using {settings.provider_name} with model {settings.provider_model}")
    """
    # =============================================================================
    # PROVIDER CONFIGURATION
    # =============================================================================
    # Configure your OpenAI-compatible AI provider here.
    # See PROVIDERS.md for detailed setup instructions for different providers.
    # 
    # Required: API key, base URL, and model name
    # Optional: provider name, headers, API type
    # API key for authentication - REQUIRED
    # Examples: OpenRouter key, Tachyon key, or "not-needed" for local models
    provider_api_key: Optional[str] = Field(default=None, validation_alias=AliasChoices("PROVIDER_API_KEY"))
    
    # Base URL for API calls - REQUIRED, must be OpenAI-compatible
    # Examples:
    # - OpenRouter: https://openrouter.ai/api/v1
    # - Ollama: http://localhost:11434/v1
    # - Tachyon: https://api.tachyon.ai/v1
    provider_api_base_url: Optional[str] = Field(default=None, validation_alias=AliasChoices("PROVIDER_API_BASE_URL"))
    
    # Model identifier - REQUIRED
    # Examples: "llama2", "meta-llama/llama-3-8b-instruct", "gpt-3.5-turbo"
    provider_model: Optional[str] = Field(default=None, validation_alias=AliasChoices("PROVIDER_MODEL"))
    
    # API compatibility type - currently only "openai" is supported
    provider_api_type: str = Field(default="openai", validation_alias=AliasChoices("PROVIDER_API_TYPE"))
    
    # Additional HTTP headers as JSON string - OPTIONAL
    # Examples:
    # - OpenRouter: {"HTTP-Referer": "http://localhost:8000", "X-Title": "App Name"}
    # - Custom auth: {"X-API-Key": "key", "Authorization": "Bearer token"}
    # - Local models: {} (empty)
    provider_headers: Optional[Dict[str, str]] = Field(default=None, validation_alias=AliasChoices("PROVIDER_HEADERS"))
    
    # API version for providers that require it - OPTIONAL
    provider_api_version: Optional[str] = Field(default=None, validation_alias=AliasChoices("PROVIDER_API_VERSION"))
    
    # Display name for the provider - shown in logs and UI
    provider_name: str = Field(default="LLM Provider", validation_alias=AliasChoices("PROVIDER_NAME"))
    
    # =============================================================================
    # APPLICATION CONFIGURATION
    # =============================================================================
    # Basic application settings and metadata
    # Application name - used in logs, headers, and identification
    app_name: str = Field(default="AI Testing Suite", validation_alias=AliasChoices("APP_NAME"))
    
    # Application version - for tracking and debugging
    app_version: str = Field(default="1.0.0", validation_alias=AliasChoices("APP_VERSION"))
    
    # Enable debug mode - shows detailed logs and error information
    # WARNING: Don't enable in production as it may expose sensitive data
    debug_mode: bool = Field(default=False, validation_alias=AliasChoices("DEBUG_MODE"))
    
    
    # =============================================================================
    # SECURITY CONFIGURATION
    # =============================================================================
    # Settings for security, CORS, and request limits
    # Allowed CORS origins - list of URLs that can make requests to the API
    # Examples: ["http://localhost:3000", "https://yourdomain.com"]
    cors_origins: list[str] = Field(default=[
        "http://localhost:8000",      # Backend self-reference
        "http://localhost:3000",      # React production frontend
        "http://localhost:3001",      # React development frontend
        "http://localhost:5173"       # Vite default port
    ], validation_alias=AliasChoices("CORS_ORIGINS"))
    
    # Maximum HTTP request size in bytes (default: 1MB)
    # Prevents large payloads from overwhelming the server
    max_request_size: int = Field(default=1048576, validation_alias=AliasChoices("MAX_REQUEST_SIZE"))
    
    # =============================================================================
    # TIMEOUT CONFIGURATION
    # =============================================================================
    # API and request timeout settings
    # General API timeout in seconds - for internal operations
    api_timeout: int = Field(default=30, validation_alias=AliasChoices("API_TIMEOUT"))
    
    # Provider API timeout in seconds - how long to wait for AI responses
    # Increase for slower models or local setups, decrease for faster responses
    openai_timeout: int = Field(default=60, validation_alias=AliasChoices("OPENAI_TIMEOUT"))
    
    # =============================================================================
    # LOGGING CONFIGURATION
    # =============================================================================
    # Settings for application logging, rotation, and retention
    # Path to the main log file - set to None to disable file logging
    log_file_path: Optional[str] = Field(default="logs/app.log", validation_alias=AliasChoices("LOG_FILE_PATH"))
    
    # Logging level - controls verbosity of logs
    # Options: DEBUG (most verbose), INFO, WARNING, ERROR (least verbose)
    log_level: str = Field(default="INFO", validation_alias=AliasChoices("LOG_LEVEL"))
    
    # Hours between log file rotations - prevents log files from growing too large
    log_rotation_hours: int = Field(default=1, validation_alias=AliasChoices("LOG_ROTATION_HOURS"))
    
    # Days to keep old log files before deletion - manages disk space
    log_retention_days: int = Field(default=7, validation_alias=AliasChoices("LOG_RETENTION_DAYS"))
    
    # =============================================================================
    # INPUT VALIDATION  
    # =============================================================================
    # Limits for user input validation
    # Maximum length for character names - prevents excessively long inputs
    max_character_length: int = Field(default=100, validation_alias=AliasChoices("MAX_CHARACTER_LENGTH"))
    
    # Minimum length for character names - ensures meaningful inputs
    min_character_length: int = Field(default=1, validation_alias=AliasChoices("MIN_CHARACTER_LENGTH"))
    
    # =============================================================================
    # RETRY CONFIGURATION
    # =============================================================================
    # Settings for automatic retry mechanisms using tenacity
    # Enable/disable the retry mechanism globally
    retry_enabled: bool = Field(default=True, validation_alias=AliasChoices("RETRY_ENABLED"))
    
    # Maximum number of retry attempts for failed operations
    # Applies to API calls, database operations, and network requests
    retry_max_attempts: int = Field(default=3, validation_alias=AliasChoices("RETRY_MAX_ATTEMPTS"))
    
    # Maximum wait time between retries in seconds
    # Uses exponential backoff with jitter, capped at this value
    retry_max_wait_seconds: int = Field(default=30, validation_alias=AliasChoices("RETRY_MAX_WAIT_SECONDS"))
    
    # Exponential backoff multiplier for retry delays
    # Each retry waits multiplier^attempt_number seconds (with jitter)
    retry_multiplier: float = Field(default=2.0, validation_alias=AliasChoices("RETRY_MULTIPLIER"))
    
    # Minimum wait time between retries in seconds
    # Base delay before exponential backoff and jitter are applied
    retry_min_wait_seconds: float = Field(default=1.0, validation_alias=AliasChoices("RETRY_MIN_WAIT_SECONDS"))
    
    # =============================================================================
    # RATE LIMITING CONFIGURATION
    # =============================================================================
    # Settings for API rate limiting using SlowAPI to prevent abuse
    # Enable/disable rate limiting globally
    rate_limiting_enabled: bool = Field(default=True, validation_alias=AliasChoices("RATE_LIMITING_ENABLED"))
    
    # Per IP address limits (requests per minute)
    # General rate limit applied to all IPs regardless of endpoint
    rate_limit_per_ip: int = Field(default=60, validation_alias=AliasChoices("RATE_LIMIT_PER_IP"))
    
    # Per endpoint limits (requests per minute per IP)
    # AI story generation endpoints - most expensive operations
    rate_limit_story_generation: int = Field(default=15, validation_alias=AliasChoices("RATE_LIMIT_STORY_GENERATION"))
    
    # List and query endpoints - moderate database operations
    rate_limit_list_endpoints: int = Field(default=30, validation_alias=AliasChoices("RATE_LIMIT_LIST_ENDPOINTS"))
    
    # Health and status endpoints - lightweight operations
    rate_limit_health_status: int = Field(default=100, validation_alias=AliasChoices("RATE_LIMIT_HEALTH_STATUS"))
    
    # Global server limits (requests per minute across all users)
    # Total server capacity to prevent overload
    rate_limit_global_server: int = Field(default=1000, validation_alias=AliasChoices("RATE_LIMIT_GLOBAL_SERVER"))
    
    # Rate limiting behavior settings
    # Storage backend for rate limit counters (memory, redis, database)
    rate_limit_storage_backend: str = Field(default="memory", validation_alias=AliasChoices("RATE_LIMIT_STORAGE_BACKEND"))
    
    # Time window type (fixed, sliding)
    rate_limit_time_window: str = Field(default="fixed", validation_alias=AliasChoices("RATE_LIMIT_TIME_WINDOW"))
    
    # HTTP status code to return when rate limited
    rate_limit_return_status_code: int = Field(default=429, validation_alias=AliasChoices("RATE_LIMIT_RETURN_STATUS_CODE"))
    
    @field_validator("provider_api_base_url")
    @classmethod
    def validate_endpoint(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize provider API endpoint URL.
        
        This validator ensures that:
        1. The URL has a proper protocol (http:// or https://)
        2. Trailing slashes are removed for consistency
        3. The URL format is valid for API calls
        
        Args:
            v: The endpoint URL to validate (from PROVIDER_API_BASE_URL env var)
            
        Returns:
            The normalized endpoint URL or None if not provided
            
        Raises:
            ValueError: If the endpoint doesn't start with https:// or http://
            
        Examples:
            >>> # Valid URLs that get normalized
            >>> Settings.validate_endpoint("https://api.provider.com/")
            'https://api.provider.com'
            >>> Settings.validate_endpoint("http://localhost:11434/v1/")
            'http://localhost:11434/v1'
            >>> 
            >>> # Invalid URL that raises error
            >>> Settings.validate_endpoint("api.provider.com")
            ValueError: Provider API endpoint must start with https:// or http://
        """
        if v and not v.startswith(("https://", "http://")):
            raise ValueError(
                "Provider API endpoint must start with https:// or http://. "
                f"Got: {v}. Example: https://api.provider.com/v1"
            )
        # Remove trailing slash for consistency
        return v.rstrip("/") if v else v
    
    @field_validator("provider_headers")
    @classmethod
    def parse_provider_headers(cls, v: Optional[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """Parse and validate provider headers from environment variable.
        
        This validator handles the conversion of headers from JSON string format
        (as stored in environment variables) to Python dictionaries. Headers are
        used for provider-specific authentication and metadata.
        
        Args:
            v: The headers value - can be a JSON string or already parsed dict
            
        Returns:
            Parsed headers as a dictionary, or None if not provided
            
        Raises:
            ValueError: If the JSON string is malformed or invalid
            
        Examples:
            >>> # JSON string from environment variable
            >>> Settings.parse_provider_headers('{"X-API-Key": "secret"}')
            {'X-API-Key': 'secret'}
            >>> 
            >>> # Already parsed dictionary (direct assignment)
            >>> Settings.parse_provider_headers({'HTTP-Referer': 'http://localhost:8000'})
            {'HTTP-Referer': 'http://localhost:8000'}
            >>> 
            >>> # OpenRouter example
            >>> headers = '{"HTTP-Referer": "http://localhost:8000", "X-Title": "My App"}'
            >>> Settings.parse_provider_headers(headers)
            {'HTTP-Referer': 'http://localhost:8000', 'X-Title': 'My App'}
            >>> 
            >>> # Invalid JSON raises error
            >>> Settings.parse_provider_headers('{"invalid": json}')
            ValueError: PROVIDER_HEADERS must be valid JSON...
        """
        if v and isinstance(v, str):
            try:
                parsed = json.loads(v)
                if not isinstance(parsed, dict):
                    raise ValueError("PROVIDER_HEADERS must be a JSON object (dictionary)")
                return parsed
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"PROVIDER_HEADERS must be valid JSON. Error: {e}. "
                    'Example: {"X-API-Key": "your-key", "Content-Type": "application/json"}'
                )
        return v
    
    def validate_provider_config(self) -> None:
        """Validate that all required provider configuration is present.
        
        This method performs comprehensive validation of the provider configuration
        to ensure the application can successfully connect to and use the AI provider.
        It checks for required fields and provides helpful error messages.
        
        Called automatically during settings loading to catch configuration
        errors early before the application starts making API calls.
        
        Raises:
            ValueError: If any required configuration fields are missing,
                       with specific details about what's missing
                
        Examples:
            >>> # Valid configuration
            >>> settings = Settings()
            >>> settings.provider_api_key = "sk-or-v1-abc123"
            >>> settings.provider_api_base_url = "https://openrouter.ai/api/v1"
            >>> settings.provider_model = "meta-llama/llama-3-8b-instruct"
            >>> settings.validate_provider_config()  # No exception - all good!
            >>> 
            >>> # Missing required fields
            >>> settings = Settings()
            >>> settings.validate_provider_config()
            ValueError: Provider configuration incomplete. Missing: PROVIDER_API_KEY, PROVIDER_API_BASE_URL, PROVIDER_MODEL...
        """
        missing_fields = []
        
        # Check each required field
        if not self.provider_api_key:
            missing_fields.append("PROVIDER_API_KEY")
        if not self.provider_api_base_url:
            missing_fields.append("PROVIDER_API_BASE_URL")
        if not self.provider_model:
            missing_fields.append("PROVIDER_MODEL")
            
        if missing_fields:
            raise ValueError(
                f"Provider configuration incomplete. Missing: {', '.join(missing_fields)}. "
                "Please set these environment variables in your .env file. "
                "See PROVIDERS.md for setup instructions."
            )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra fields that don't belong to this model
    }

def load_settings() -> Settings:
    """Load and validate application settings from environment and .env files.
    
    This function is the main entry point for configuration loading. It:
    1. Creates a Settings instance (automatically loads from .env and environment)
    2. Validates the provider configuration
    3. Logs successful loading with key details
    4. Exits gracefully if configuration is invalid
    
    The function ensures that the application never starts with invalid
    configuration, preventing runtime errors and API failures.
    
    Returns:
        A fully validated Settings instance ready for use
        
    Raises:
        SystemExit: If configuration loading or validation fails.
                   The application will exit with code 1 and log the error.
        
    Examples:
        >>> # Successful loading
        >>> settings = load_settings()
        >>> print(f"Loaded config for {settings.provider_name}")
        'Loaded config for OpenRouter'
        >>> 
        >>> # The function handles all error cases internally
        >>> # If .env is missing required fields, it will log and exit
    """
    try:
        # Load settings from environment variables and .env file
        # Pydantic automatically handles the loading and type conversion
        settings = Settings()
        
        # Validate that all required provider settings are present
        # This catches configuration errors before the app starts
        settings.validate_provider_config()
        
        # Log successful configuration loading with key details
        logger.info("Configuration loaded successfully", 
                   app_name=settings.app_name,
                   app_version=settings.app_version,
                   debug_mode=settings.debug_mode,
                   provider_name=settings.provider_name,
                   provider_model=settings.provider_model,
                   log_level=settings.log_level)
        
        return settings
        
    except Exception as e:
        # Log the configuration error with details
        logger.error("Failed to load configuration", 
                    error=str(e),
                    error_type=type(e).__name__)
        
        # Print to stderr for immediate visibility
        print(f"Configuration Error: {e}", file=sys.stderr)
        print("Please check your .env file and environment variables.", file=sys.stderr)
        print("See PROVIDERS.md for setup instructions.", file=sys.stderr)
        
        # Exit with error code
        sys.exit(1)

# =============================================================================
# GLOBAL SETTINGS INSTANCE
# =============================================================================
# This creates the global settings instance that's used throughout the application.
# It automatically loads configuration from environment variables and .env files,
# validates all settings, and exits if configuration is invalid.
# 
# Import this in other modules: from config import settings
settings = load_settings()

# =============================================================================
# CUSTOM PROVIDER SETTINGS
# =============================================================================
# Load custom settings if PROVIDER_NAME=custom
# This allows for extended configuration for custom providers
from custom_settings import load_custom_settings
custom_settings = load_custom_settings()