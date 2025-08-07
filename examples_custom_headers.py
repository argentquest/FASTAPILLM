#!/usr/bin/env python3
"""
Examples of How HeaderFactory Adjusts Based on Provider

This file demonstrates how the simplified HeaderFactory.create_headers()
method automatically adjusts header generation based on the provider name.

NO REGISTRATION REQUIRED - The factory directly handles different providers
in its create_headers method based on the provider_name parameter.
"""

import time
import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional

# Import the header factory and settings
from header_factory import HeaderFactory
from config import settings, custom_settings

# =============================================================================
# UNDERSTANDING THE NEW APPROACH
# =============================================================================
"""
The HeaderFactory.create_headers() method automatically adjusts based on provider:

1. OpenAI Provider:
   - Standard OpenAI-compatible headers
   - Authorization header handled by AsyncOpenAI client
   
2. Custom Provider:
   - Calls _create_custom_headers() internally
   - Full access to settings and custom_settings
   - Adds custom headers based on configuration
   
3. Any Other Provider:
   - Generic header handling
   - Adds app name, version, API key as needed
   - Can be extended in HeaderFactory
"""

# =============================================================================
# EXAMPLE 1: Testing Different Providers
# =============================================================================

def demonstrate_provider_based_headers():
    """Show how HeaderFactory automatically adjusts based on provider."""
    
    print("="*60)
    print("DEMONSTRATING PROVIDER-BASED HEADER GENERATION")
    print("="*60)
    
    # Example 1: OpenAI provider
    print("\n1. OpenAI Provider Headers:")
    headers = HeaderFactory.create_headers(
        provider_name="openai",
        api_key="sk-1234567890",
        default_headers={"X-Custom": "value"},
        settings=settings,
        custom_settings=None
    )
    print_headers(headers)
    
    # Example 2: Custom provider
    print("\n2. Custom Provider Headers:")
    headers = HeaderFactory.create_headers(
        provider_name="custom",
        api_key="custom-key-123",
        default_headers={"X-Base": "custom-base"},
        settings=settings,
        custom_settings=custom_settings
    )
    print_headers(headers)
    
    # Example 3: Generic provider
    print("\n3. Generic Provider Headers (e.g., 'anthropic'):")
    headers = HeaderFactory.create_headers(
        provider_name="anthropic",
        api_key="ant-key-456",
        default_headers={"X-Anthropic": "claude"},
        settings=settings,
        custom_settings=None
    )
    print_headers(headers)

# =============================================================================
# EXAMPLE 2: Extending HeaderFactory for New Providers
# =============================================================================

def show_how_to_extend_factory():
    """
    Demonstrate how you would extend HeaderFactory for new providers.
    
    To add support for a new provider, you would modify the 
    HeaderFactory.create_headers() method directly:
    
    elif provider_lower == "anthropic":
        headers["X-Anthropic-Version"] = "2023-01-01"
        headers["X-Anthropic-Beta"] = "messages-2023-12-15"
        if api_key:
            headers["X-API-Key"] = api_key
    
    elif provider_lower == "cohere":
        headers["Cohere-Version"] = "1"
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
    """
    
    print("\n" + "="*60)
    print("HOW TO EXTEND FOR NEW PROVIDERS")
    print("="*60)
    
    print("""
To add a new provider, modify header_factory.py:

1. In the create_headers() method, add a new elif block:

    elif provider_lower == "your_provider":
        # Your provider-specific logic
        headers["X-YourProvider-Version"] = "1.0"
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Access settings if needed
        if settings and settings.debug_mode:
            headers["X-Debug"] = "true"

2. No registration needed - it works automatically when 
   PROVIDER_NAME=your_provider is set in .env
""")

# =============================================================================
# EXAMPLE 3: Custom Provider with Dynamic Headers
# =============================================================================

def demonstrate_custom_provider_features():
    """Show the full capabilities of the custom provider."""
    
    print("\n" + "="*60)
    print("CUSTOM PROVIDER ADVANCED FEATURES")
    print("="*60)
    
    # Simulate having custom settings
    class MockCustomSettings:
        custom_var = "my-custom-data-123"
        provider_name = "custom"
        app_name = "Test App"
        app_version = "2.0.0"
        debug_mode = True
        api_timeout = 30
        rate_limiting_enabled = True
    
    mock_custom = MockCustomSettings()
    
    # Create headers with full custom settings
    headers = HeaderFactory.create_headers(
        provider_name="custom",
        api_key="custom-api-key",
        default_headers={
            "X-Base-Header": "base-value",
            "Content-Type": "application/json"  # Will not be overridden
        },
        settings=settings,
        custom_settings=mock_custom
    )
    
    print("\nGenerated Custom Headers:")
    print_headers(headers)
    
    print("\nNotice how the custom provider:")
    print("- Includes the CUSTOM_VAR as X-Custom-Var")
    print("- Adds debug headers when debug_mode is True")
    print("- Includes rate limiting info")
    print("- Preserves existing Content-Type")
    print("- Has access to ALL settings fields")

# =============================================================================
# EXAMPLE 4: Real-World Usage in Services
# =============================================================================

def show_service_usage():
    """Demonstrate how services use HeaderFactory."""
    
    print("\n" + "="*60)
    print("REAL-WORLD SERVICE USAGE")
    print("="*60)
    
    print("""
In BaseService, headers are created like this:

    headers = HeaderFactory.create_headers(
        provider_name=settings.provider_name,      # From PROVIDER_NAME env
        api_key=settings.provider_api_key,         # From PROVIDER_API_KEY env
        default_headers=settings.provider_headers, # From PROVIDER_HEADERS env
        settings=settings,                         # Global settings object
        custom_settings=self.custom_settings       # Only set if PROVIDER_NAME=custom
    )

The headers are then passed to the AsyncOpenAI client:

    client = AsyncOpenAI(
        api_key=settings.provider_api_key,
        base_url=settings.provider_api_base_url,
        http_client=self._http_client,
        default_headers=headers  # <- All requests use these headers
    )
""")

# =============================================================================
# EXAMPLE 5: Dynamic Header Generation Patterns
# =============================================================================

def dynamic_header_patterns():
    """Show patterns for dynamic header generation."""
    
    print("\n" + "="*60)
    print("DYNAMIC HEADER PATTERNS")
    print("="*60)
    
    # Pattern 1: Time-based headers
    print("\n1. Time-based Headers:")
    headers = {
        "X-Request-Time": datetime.utcnow().isoformat() + "Z",
        "X-Timestamp": str(int(time.time())),
        "X-Request-ID": str(uuid.uuid4())
    }
    print_headers(headers)
    
    # Pattern 2: Signature-based headers
    print("\n2. Signature-based Headers:")
    timestamp = str(int(time.time()))
    nonce = str(uuid.uuid4())
    signature = hashlib.sha256(f"{timestamp}:{nonce}:secret".encode()).hexdigest()
    
    headers = {
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": signature
    }
    print_headers(headers)
    
    print("""
To implement these patterns in HeaderFactory:

1. Modify the _create_custom_headers() method
2. Or add a new provider-specific block in create_headers()
3. The headers will be generated fresh for each API client creation
""")

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def print_headers(headers: Dict[str, str], mask_sensitive: bool = True):
    """Pretty print headers, masking sensitive values."""
    for key, value in headers.items():
        if mask_sensitive and any(sensitive in key.lower() 
                                for sensitive in ['key', 'token', 'secret', 'authorization']):
            print(f"  {key}: ***")
        else:
            print(f"  {key}: {value}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    """Run all examples."""
    
    print("\nHeaderFactory Provider-Based Examples")
    print("="*40)
    print("NO REGISTRATION REQUIRED!")
    print("Headers are generated based on provider_name parameter")
    print("="*40)
    
    # Run all demonstrations
    demonstrate_provider_based_headers()
    show_how_to_extend_factory()
    demonstrate_custom_provider_features()
    show_service_usage()
    dynamic_header_patterns()
    
    print("\n" + "="*60)
    print("KEY TAKEAWAYS:")
    print("="*60)
    print("""
1. No registration system - just call HeaderFactory.create_headers()
2. Provider name determines header generation logic
3. Custom provider has full access to settings and custom_settings
4. To add new providers, modify HeaderFactory directly
5. Headers are created fresh for each API client

Current supported providers in HeaderFactory:
- "openai": Standard OpenAI-compatible headers
- "custom": Extended headers with settings access
- Any other: Generic headers with app info

To use:
1. Set PROVIDER_NAME in your .env file
2. Headers are automatically generated in BaseService
3. All API calls will include the appropriate headers
""")