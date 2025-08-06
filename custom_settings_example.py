"""
Example: Using Simplified Custom Settings

This example shows how to use the simplified custom settings with only CUSTOM_VAR
and programmatic header functions when PROVIDER_NAME=custom
"""

from config import settings, custom_settings
from header_factory import HeaderFactory
import time
import uuid


def example_custom_provider_usage():
    """Example of using simplified custom settings."""
    
    # Check if we're using custom provider
    if settings.provider_name.lower() == "custom" and custom_settings:
        print("Using custom provider with simplified settings")
        
        # Access the single custom variable
        print(f"Custom Variable: {custom_settings.custom_var}")
        
        # Set up dynamic headers using the custom_var
        def my_dynamic_headers():
            return {
                "X-Custom-Var": custom_settings.custom_var or "default-value",
                "X-Request-Time": str(int(time.time())),
                "X-Request-ID": str(uuid.uuid4()),
                "X-Provider-Type": "custom"
            }
        
        # Register the header function
        custom_settings.set_header_function(my_dynamic_headers)
        
        # Get headers with dynamic generation
        headers = HeaderFactory.create_headers(
            provider_name=settings.provider_name,
            api_key=settings.provider_api_key,
            default_headers=settings.provider_headers
        )
        print(f"Generated headers: {headers}")
        
    else:
        print("Using standard provider settings")


# Example .env configuration for simplified custom provider:
"""
# Standard provider settings
PROVIDER_NAME=custom
PROVIDER_API_KEY=sk-custom-key-123
PROVIDER_API_BASE_URL=https://api.customprovider.com/v1
PROVIDER_MODEL=custom-chat-model

# Single custom setting - use for any custom data your provider needs
CUSTOM_VAR=my-custom-identifier-123
"""


def setup_custom_headers_example():
    """Example of setting up complex headers programmatically."""
    
    if settings.provider_name.lower() == "custom" and custom_settings:
        
        def complex_custom_headers():
            """Generate complex headers using the custom_var."""
            custom_id = custom_settings.custom_var
            
            return {
                # Use custom_var in headers
                "X-Custom-ID": custom_id,
                "X-Client-Type": f"fastapi-{custom_id}",
                
                # Dynamic values
                "X-Timestamp": str(int(time.time())),
                "X-Request-UUID": str(uuid.uuid4()),
                
                # Custom authentication based on custom_var
                "X-Auth-Context": f"provider-{custom_id}",
                
                # Environment or tenant info
                "X-Environment": "production" if custom_id else "development"
            }
        
        # Set the header function
        custom_settings.set_header_function(complex_custom_headers)
        print("Set up complex custom headers using CUSTOM_VAR")


if __name__ == "__main__":
    example_custom_provider_usage()
    setup_custom_headers_example()