#!/usr/bin/env python3
"""
Example: Using custom_settings in BaseService

This example demonstrates how to access custom_settings in service classes
that inherit from BaseService.
"""

from services.base_service import BaseService
from config import settings
from typing import Dict, Any, Tuple

class ExampleService(BaseService):
    """Example service showing custom_settings usage."""
    
    async def generate_content(self, primary_input: str, secondary_input: str) -> Tuple[str, Dict[str, Any]]:
        """Generate content with custom provider awareness."""
        
        # Standard settings are always available via global 'settings'
        base_prompt = f"App: {settings.app_name} - Generate content about {primary_input} and {secondary_input}"
        
        # Custom settings are available via self.custom_settings (None if not custom provider)
        if self.custom_settings:
            print(f"🔧 Using custom provider: {self.custom_settings.provider_name}")
            
            # Access CUSTOM_VAR if available
            if self.custom_settings.custom_var:
                base_prompt += f" with custom context: {self.custom_settings.custom_var}"
                print(f"📝 Custom variable: {self.custom_settings.custom_var}")
            
            # Access any default setting through custom_settings (they're all inherited)
            print(f"⏱️  Timeout: {self.custom_settings.api_timeout}s")
            print(f"🔧 Debug: {self.custom_settings.debug_mode}")
            
            # Custom provider specific logic
            content = f"Custom Provider Response: {base_prompt}"
        else:
            # Standard provider logic
            print(f"🔧 Using standard provider: {settings.provider_name}")
            content = f"Standard Response: {base_prompt}"
        
        # Return generated content and usage info
        usage_info = {
            "provider_type": "custom" if self.custom_settings else "standard",
            "custom_var_used": bool(self.custom_settings and self.custom_settings.custom_var)
        }
        
        return content, usage_info

# Example usage
async def main():
    """Demonstrate service usage with different provider types."""
    
    service = ExampleService()
    
    print("="*60)
    print("EXAMPLE: BaseService custom_settings Usage")
    print("="*60)
    
    print(f"\n🏗️  Service Info:")
    print(f"   - Service Name: {service.service_name}")
    print(f"   - Provider Name: {service.provider_name}")
    print(f"   - Custom Settings: {'Available' if service.custom_settings else 'Not Available'}")
    
    print(f"\n📋 Settings Access:")
    print(f"   - Main settings: Always available via 'settings' global")
    print(f"   - Custom settings: Available via 'self.custom_settings' (None if not custom)")
    
    if service.custom_settings:
        print(f"\n🔧 Custom Provider Configuration:")
        print(f"   - Provider: {service.custom_settings.provider_name}")
        print(f"   - Custom Var: {service.custom_settings.custom_var}")
        print(f"   - App Name: {service.custom_settings.app_name}")
        print(f"   - Timeout: {service.custom_settings.api_timeout}s")
    else:
        print(f"\n🔧 Standard Provider Configuration:")
        print(f"   - Provider: {settings.provider_name}")
        print(f"   - App Name: {settings.app_name}")
        print(f"   - Timeout: {settings.api_timeout}s")
    
    print(f"\n🚀 Content Generation Test:")
    content, usage = await service.generate_content("Alice", "Wonderland")
    print(f"   Generated: {content[:100]}...")
    print(f"   Usage: {usage}")
    
    print(f"\n✅ Example completed successfully!")
    
    # Clean up
    await service.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())