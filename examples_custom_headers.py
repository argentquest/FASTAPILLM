#!/usr/bin/env python3
"""
Examples of Programmatic Custom Header Generation

This file demonstrates how to create custom headers programmatically 
without relying on .env file configuration.
"""

import time
import uuid
import hashlib
import json
from datetime import datetime
from typing import Dict

# Import the header factory and custom settings
from header_factory import HeaderFactory
from config import custom_settings

# =============================================================================
# EXAMPLE 1: Simple Dynamic Headers
# =============================================================================

def simple_dynamic_headers() -> Dict[str, str]:
    """Generate simple dynamic headers with timestamp and request ID."""
    return {
        "X-Request-Timestamp": str(int(time.time())),
        "X-Request-ID": str(uuid.uuid4()),
        "X-Client-Version": "1.0.0"
    }

# =============================================================================
# EXAMPLE 2: Authentication Token Headers
# =============================================================================

def auth_token_headers() -> Dict[str, str]:
    """Generate headers with dynamic authentication tokens."""
    # Simulate getting a fresh token
    def get_current_auth_token():
        # In real implementation, this might:
        # - Fetch from a token store
        # - Generate JWT tokens
        # - Call an auth service
        # - Read from secure storage
        return f"token_{int(time.time())}"
    
    return {
        "X-Auth-Token": get_current_auth_token(),
        "X-Auth-Type": "Bearer",
        "X-Token-Timestamp": datetime.utcnow().isoformat() + "Z"
    }

# =============================================================================
# EXAMPLE 3: Request Signature Headers
# =============================================================================

def signature_headers() -> Dict[str, str]:
    """Generate headers with request signatures for security."""
    timestamp = str(int(time.time()))
    nonce = str(uuid.uuid4())
    
    # Create signature (example - use your own signing logic)
    def create_signature(timestamp: str, nonce: str) -> str:
        data = f"timestamp={timestamp}&nonce={nonce}"
        secret = "your-secret-key"  # In real code, get from secure storage
        signature = hashlib.sha256(f"{data}&secret={secret}".encode()).hexdigest()
        return signature
    
    signature = create_signature(timestamp, nonce)
    
    return {
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": signature,
        "X-Signature-Algorithm": "SHA256"
    }

# =============================================================================
# EXAMPLE 4: Context-Aware Headers
# =============================================================================

def context_aware_headers() -> Dict[str, str]:
    """Generate headers based on current application context."""
    headers = {
        "X-Request-Time": datetime.utcnow().isoformat() + "Z",
        "X-Service-Name": "fastapi-llm",
    }
    
    # Add environment-specific headers
    import os
    if os.getenv("DEBUG_MODE", "false").lower() == "true":
        headers["X-Debug-Mode"] = "enabled"
        headers["X-Debug-Level"] = "verbose"
    
    # Add custom provider context if available
    if custom_settings:
        if custom_settings.custom_var:
            headers["X-Custom-Data"] = custom_settings.custom_var
    
    return headers

# =============================================================================
# EXAMPLE 5: API Rate Limiting Headers
# =============================================================================

class RateLimitTracker:
    """Simple rate limit tracker for demonstration."""
    def __init__(self):
        self.requests = []
    
    def get_rate_limit_headers(self) -> Dict[str, str]:
        now = time.time()
        # Clean old requests (last minute)
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        # Add current request
        self.requests.append(now)
        
        return {
            "X-RateLimit-Remaining": str(max(0, 100 - len(self.requests))),
            "X-RateLimit-Reset": str(int(now + 60)),
            "X-RateLimit-Used": str(len(self.requests))
        }

# Global rate limiter instance
rate_limiter = RateLimitTracker()

def rate_limit_headers() -> Dict[str, str]:
    """Generate rate limiting headers."""
    return rate_limiter.get_rate_limit_headers()

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

def setup_dynamic_headers_example():
    """Example of how to set up dynamic headers in your application."""
    
    print("Setting up dynamic header examples...")
    
    # Method 1: Register with HeaderFactory (works for any provider name)
    HeaderFactory.register_header_function("mycustom", simple_dynamic_headers)
    HeaderFactory.register_header_function("authprovider", auth_token_headers)
    HeaderFactory.register_header_function("secure", signature_headers)
    
    # Method 2: Register for custom provider (when PROVIDER_NAME=custom)
    HeaderFactory.register_header_function("custom", context_aware_headers)
    print("Registered context-aware headers for custom provider")
    
    # Or combine multiple header generators
    def combined_headers():
        headers = {}
        headers.update(simple_dynamic_headers())
        headers.update(rate_limit_headers())
        return headers
    
    HeaderFactory.register_header_function("combined", combined_headers)
    print("Registered combined headers for 'combined' provider")
    
    # List registered functions
    registered = HeaderFactory.list_registered_functions()
    print(f"Registered header functions: {registered}")

def test_header_generation():
    """Test the different header generation methods."""
    
    print("\n" + "="*50)
    print("TESTING DYNAMIC HEADER GENERATION")
    print("="*50)
    
    # Test each header function
    functions = [
        ("Simple Dynamic", simple_dynamic_headers),
        ("Auth Token", auth_token_headers),
        ("Signature", signature_headers),
        ("Context Aware", context_aware_headers),
        ("Rate Limit", rate_limit_headers)
    ]
    
    for name, func in functions:
        print(f"\n{name} Headers:")
        try:
            headers = func()
            for key, value in headers.items():
                # Mask sensitive values
                display_value = "***" if "token" in key.lower() or "secret" in key.lower() else value
                print(f"  {key}: {display_value}")
        except Exception as e:
            print(f"  Error: {e}")

def runtime_header_modification_example():
    """Example of modifying headers at runtime."""
    
    print("\n" + "="*50)
    print("RUNTIME HEADER MODIFICATION")
    print("="*50)
    
    # Start with simple headers
    HeaderFactory.register_header_function("runtime", simple_dynamic_headers)
    print("1. Registered simple headers")
    headers1 = HeaderFactory.create_headers("runtime", "test-key")
    print(f"   Generated: {len(headers1)} headers")
    
    # Switch to auth headers
    HeaderFactory.register_header_function("runtime", auth_token_headers)
    print("2. Switched to auth headers")
    headers2 = HeaderFactory.create_headers("runtime", "test-key")
    print(f"   Generated: {len(headers2)} headers")
    
    # Clear the function
    HeaderFactory.unregister_header_function("runtime")
    print("3. Unregistered header function")
    headers3 = HeaderFactory.create_headers("runtime", "test-key")
    print(f"   Generated: {len(headers3)} headers")

if __name__ == "__main__":
    """Run the examples."""
    
    print("Custom Headers Programming Examples")
    print("="*40)
    
    # Set up the examples
    setup_dynamic_headers_example()
    
    # Test header generation
    test_header_generation()
    
    # Test runtime modification
    runtime_header_modification_example()
    
    print(f"\n{'='*50}")
    print("To use in your application:")
    print("1. Import: from header_factory import HeaderFactory")
    print("2. Define your header function")
    print("3. Register it: HeaderFactory.register_header_function('provider_name', func)")
    print("4. Set PROVIDER_NAME=provider_name in .env")
    print("5. Headers will be automatically generated for each request")
    print("\nFor custom providers:")
    print("- Set PROVIDER_NAME=custom in .env")
    print("- Register with HeaderFactory.register_header_function('custom', your_function)")
    print("- Access CUSTOM_VAR in your function via custom_settings.custom_var")