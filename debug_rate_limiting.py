#!/usr/bin/env python3
"""
Debug script to test rate limiting middleware functionality
"""

import asyncio
import aiohttp
import time

BASE_URL = "http://localhost:8000"

async def debug_single_request():
    """Make a single request and examine all headers."""
    print("Debug: Single Request Analysis")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/health") as response:
            print(f"Status Code: {response.status}")
            print(f"Content-Type: {response.content_type}")
            
            print("\nAll Response Headers:")
            for name, value in response.headers.items():
                print(f"  {name}: {value}")
            
            print(f"\nRate Limit Headers:")
            print(f"  X-RateLimit-Limit: {response.headers.get('X-RateLimit-Limit', 'NOT SET')}")
            print(f"  X-RateLimit-Remaining: {response.headers.get('X-RateLimit-Remaining', 'NOT SET')}")
            print(f"  X-RateLimit-Reset: {response.headers.get('X-RateLimit-Reset', 'NOT SET')}")
            print(f"  Retry-After: {response.headers.get('Retry-After', 'NOT SET')}")
            
            content = await response.text()
            print(f"\nResponse Content (first 200 chars):")
            print(content[:200])

async def debug_rate_limit_config():
    """Check if we can access rate limit configuration."""
    print("\nDebug: Rate Limit Configuration Check")
    print("=" * 40)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Try to access rate limit status endpoint (if it exists)
            async with session.get(f"{BASE_URL}/api/rate-limit-status") as response:
                if response.status == 200:
                    data = await response.json()
                    print("Rate limit config from server:")
                    print(data)
                else:
                    print(f"No rate limit status endpoint (status: {response.status})")
    except Exception as e:
        print(f"Cannot access rate limit config: {e}")

async def debug_middleware_execution():
    """Test if middleware is executing by making requests to different endpoints."""
    print("\nDebug: Middleware Execution Test")
    print("=" * 40)
    
    endpoints = [
        "/health",
        "/api/provider", 
        "/",
        "/api/stories"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                print(f"\nTesting endpoint: {endpoint}")
                async with session.get(f"{BASE_URL}{endpoint}") as response:
                    print(f"  Status: {response.status}")
                    
                    # Check for rate limit headers
                    has_rate_headers = any(
                        h.startswith('X-RateLimit') or h == 'Retry-After' 
                        for h in response.headers.keys()
                    )
                    print(f"  Has rate limit headers: {has_rate_headers}")
                    
                    # Check for custom headers that might indicate middleware execution
                    custom_headers = [h for h in response.headers.keys() if h.startswith(('X-', 'x-'))]
                    print(f"  Custom headers: {custom_headers}")
                    
            except Exception as e:
                print(f"  Error: {e}")

async def debug_rapid_requests():
    """Make rapid requests to see if any rate limiting occurs."""
    print("\nDebug: Rapid Request Test")
    print("=" * 40)
    
    print("Making 20 rapid requests to /health...")
    
    async with aiohttp.ClientSession() as session:
        for i in range(20):
            try:
                start_time = time.time()
                async with session.get(f"{BASE_URL}/health") as response:
                    duration = (time.time() - start_time) * 1000
                    
                    # Check for rate limit headers
                    limit = response.headers.get('X-RateLimit-Limit')
                    remaining = response.headers.get('X-RateLimit-Remaining')
                    reset = response.headers.get('X-RateLimit-Reset')
                    
                    status_symbol = "OK" if response.status == 200 else "ERR"
                    rate_info = f"L:{limit} R:{remaining}" if limit else "No rate headers"
                    
                    print(f"  {i+1:2d} {status_symbol} {response.status} ({duration:4.0f}ms) - {rate_info}")
                    
                    if response.status == 429:
                        print(f"      RATE LIMITED! Retry-After: {response.headers.get('Retry-After', 'not set')}")
                        try:
                            error_data = await response.json()
                            print(f"      Error details: {error_data}")
                        except:
                            pass
                    
                    # No delay - test maximum rate
                    
            except Exception as e:
                print(f"  {i+1:2d} ERROR: {e}")

async def main():
    """Run debugging tests."""
    print("Rate Limiting Middleware Debug")
    print("=" * 50)
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health", timeout=aiohttp.ClientTimeout(total=3)) as response:
                if response.status != 200:
                    print(f"Server not responding properly: {response.status}")
                    return
                print("OK: Server is responding")
    except Exception as e:
        print(f"ERROR: Cannot connect to server: {e}")
        print("Make sure to start the server: python backend/main.py")
        return
    
    # Run debug tests
    await debug_single_request()
    await debug_rate_limit_config()
    await debug_middleware_execution()
    await debug_rapid_requests()
    
    print("\nDebug Analysis Complete!")
    print("\nExpected behavior if rate limiting is working:")
    print("- X-RateLimit-* headers should be present in responses")
    print("- After 60+ requests per minute, should get 429 status codes")
    print("- Rate limited responses should include Retry-After header")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDebug interrupted")
    except Exception as e:
        print(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()