#!/usr/bin/env python3
"""
Example: Using Global Settings and Custom Settings

This example demonstrates how to access settings and custom_settings
from anywhere in the application.
"""

# Recommended import
from backend.app_config import settings, custom_settings, is_custom_provider, get_custom_var

# Alternative: Import directly from config
# from backend.config import settings, custom_settings


def demonstrate_settings_access():
    """Show various ways to access settings."""
    
    print("=" * 60)
    print("GLOBAL SETTINGS ACCESS DEMONSTRATION")
    print("=" * 60)
    
    # Basic settings access
    print(f"\n1. Basic Settings:")
    print(f"   App Name: {settings.app_name}")
    print(f"   App Version: {settings.app_version}")
    print(f"   Provider: {settings.provider_name}")
    print(f"   Model: {settings.provider_model}")
    print(f"   Debug Mode: {settings.debug_mode}")
    
    # Provider settings
    print(f"\n2. Provider Configuration:")
    print(f"   API Base URL: {settings.provider_api_base_url}")
    print(f"   API Type: {settings.provider_api_type}")
    print(f"   Has API Key: {'Yes' if settings.provider_api_key else 'No'}")
    
    # Timeout settings
    print(f"\n3. Timeout Settings:")
    print(f"   API Timeout: {settings.api_timeout}s")
    print(f"   OpenAI Timeout: {settings.openai_timeout}s")
    
    # Rate limiting
    print(f"\n4. Rate Limiting:")
    print(f"   Enabled: {settings.rate_limiting_enabled}")
    if settings.rate_limiting_enabled:
        print(f"   Per IP Limit: {settings.rate_limit_per_ip}/min")
        print(f"   Story Generation: {settings.rate_limit_story_generation}/min")
    
    # Custom provider settings
    print(f"\n5. Custom Provider Settings:")
    print(f"   Is Custom Provider: {is_custom_provider()}")
    
    if custom_settings:
        print(f"   Custom Var: {custom_settings.custom_var}")
        print(f"   Has All Default Settings: Yes")
        print(f"   Example - App Name from custom_settings: {custom_settings.app_name}")
    else:
        print(f"   Custom Settings: Not loaded (PROVIDER_NAME != 'custom')")
    
    # Helper functions
    print(f"\n6. Helper Functions:")
    print(f"   get_provider_name(): {get_provider_name()}")
    print(f"   is_custom_provider(): {is_custom_provider()}")
    print(f"   get_custom_var(): {get_custom_var()}")


def demonstrate_in_service():
    """Show how services would use settings."""
    
    print(f"\n{'=' * 60}")
    print("SETTINGS IN SERVICE EXAMPLE")
    print("=" * 60)
    
    class ExampleService:
        def __init__(self):
            self.provider = settings.provider_name
            self.debug = settings.debug_mode
            
        def process(self):
            print(f"\nProcessing with {self.provider} provider...")
            
            # Provider-specific logic
            if settings.provider_name.lower() == "openrouter":
                print("Using OpenRouter configuration")
            elif settings.provider_name.lower() == "custom":
                print("Using custom provider configuration")
                if custom_settings and custom_settings.custom_var:
                    print(f"Custom context: {custom_settings.custom_var}")
            else:
                print(f"Using generic provider: {settings.provider_name}")
            
            # Debug information
            if self.debug:
                print(f"Debug: Timeout={settings.api_timeout}s")
                print(f"Debug: Rate Limiting={settings.rate_limiting_enabled}")
    
    service = ExampleService()
    service.process()


def demonstrate_conditional_logic():
    """Show conditional logic based on settings."""
    
    print(f"\n{'=' * 60}")
    print("CONDITIONAL LOGIC EXAMPLE")
    print("=" * 60)
    
    # Example 1: Feature flags
    if settings.debug_mode:
        print("\n✓ Debug mode is ON - showing detailed logs")
    else:
        print("\n✗ Debug mode is OFF - minimal logging")
    
    # Example 2: Provider-specific features
    if is_custom_provider():
        print("\n✓ Custom provider features enabled")
        if custom_settings.custom_var:
            print(f"  Using custom data: {custom_settings.custom_var}")
    else:
        print(f"\n✗ Standard provider: {settings.provider_name}")
    
    # Example 3: Performance tuning
    if settings.retry_enabled:
        print(f"\n✓ Retry enabled: {settings.retry_max_attempts} attempts")
    else:
        print("\n✗ Retry disabled")
    
    # Example 4: Security settings
    if settings.rate_limiting_enabled:
        print(f"\n✓ Rate limiting active: {settings.rate_limit_per_ip} req/min")
    else:
        print("\n✗ Rate limiting disabled")


if __name__ == "__main__":
    """Run all demonstrations."""
    
    print("\nGlobal Settings Access Examples")
    print("=" * 40)
    print("Settings are loaded once at startup and")
    print("remain constant during application runtime")
    print("=" * 40)
    
    # Run demonstrations
    demonstrate_settings_access()
    demonstrate_in_service()
    demonstrate_conditional_logic()
    
    print(f"\n{'=' * 60}")
    print("✅ Settings can be accessed from anywhere in the application!")
    print("   Just import: from backend.app_config import settings, custom_settings")