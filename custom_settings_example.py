"""
Example: Using Custom Settings in Services

This example shows how to access and use custom settings when PROVIDER_NAME=custom
"""

from config import settings, custom_settings
from header_factory import HeaderFactory


def example_custom_provider_usage():
    """Example of using custom settings in your application."""
    
    # Check if we're using custom provider
    if settings.provider_name.lower() == "custom" and custom_settings:
        print("Using custom provider with extended settings")
        
        # Access custom settings
        print(f"Custom Environment: {custom_settings.custom_environment}")
        print(f"Custom API Version: {custom_settings.custom_api_version}")
        print(f"Using OAuth: {custom_settings.custom_use_oauth}")
        
        # Map model names
        standard_model = "gpt-3.5-turbo"
        custom_model = custom_settings.map_model_name(standard_model)
        print(f"Model mapping: {standard_model} -> {custom_model}")
        
        # Get custom headers
        headers = HeaderFactory.create_headers(
            provider_name=settings.provider_name,
            api_key=settings.provider_api_key,
            default_headers=settings.provider_headers
        )
        print(f"Generated headers: {headers}")
        
        # Use custom timeout
        timeout = custom_settings.custom_timeout_seconds
        print(f"Using custom timeout: {timeout} seconds")
        
        # Check custom flags
        if custom_settings.custom_require_signature:
            print("This provider requires request signatures")
        
        # Access custom max tokens if set
        if custom_settings.custom_max_tokens:
            print(f"Using custom max tokens: {custom_settings.custom_max_tokens}")
    else:
        print("Using standard provider settings")


# Example .env configuration for custom provider:
"""
# Standard provider settings
PROVIDER_NAME=custom
PROVIDER_API_KEY=sk-custom-key-123
PROVIDER_API_BASE_URL=https://api.customprovider.com/v1
PROVIDER_MODEL=custom-chat-model

# Custom provider extensions (these 6 extra fields you mentioned)
CUSTOM_AUTH_TOKEN=oauth-token-xyz
CUSTOM_CLIENT_ID=client-123
CUSTOM_CLIENT_SECRET=secret-456
CUSTOM_TENANT_ID=tenant-789
CUSTOM_ENVIRONMENT=production
CUSTOM_API_VERSION=v2

# Additional custom settings
CUSTOM_USE_OAUTH=true
CUSTOM_MAX_TOKENS=4000
CUSTOM_TEMPERATURE=0.7
CUSTOM_TIMEOUT_SECONDS=120
CUSTOM_EXTRA_HEADERS={"X-Region": "us-west", "X-Priority": "high"}
CUSTOM_MODEL_MAPPING={"gpt-3.5-turbo": "custom-chat", "gpt-4": "custom-advanced"}
"""


# Usage in base_service.py or other services:
def get_model_for_provider():
    """Get the correct model name based on provider."""
    model = settings.provider_model
    
    # If using custom provider, check for model mapping
    if settings.provider_name.lower() == "custom" and custom_settings:
        model = custom_settings.map_model_name(model)
    
    return model


def get_request_timeout():
    """Get timeout based on provider."""
    if settings.provider_name.lower() == "custom" and custom_settings:
        return custom_settings.custom_timeout_seconds
    return settings.openai_timeout


def get_default_params():
    """Get default parameters based on provider."""
    params = {
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    if settings.provider_name.lower() == "custom" and custom_settings:
        if custom_settings.custom_temperature is not None:
            params["temperature"] = custom_settings.custom_temperature
        if custom_settings.custom_max_tokens is not None:
            params["max_tokens"] = custom_settings.custom_max_tokens
    
    return params