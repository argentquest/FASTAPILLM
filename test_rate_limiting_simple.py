#!/usr/bin/env python3
"""
Simple Rate Limiting Test Script (Windows Compatible)

Tests the SlowAPI rate limiting middleware implementation.
"""

import asyncio
import aiohttp
import time
import json

BASE_URL = "http://localhost:8000"

async def test_basic_rate_limiting():
    """Test basic rate limiting functionality."""
    print("Testing Rate Limiting...")
    print("=" * 50)
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print(f"ERROR: Server not responding (status: {response.status})")
                    return
                print("OK: Server is running")
    except Exception as e:
        print(f"ERROR: Cannot connect to server at {BASE_URL}")
        print(f"Make sure to start the server first: python backend/main.py")
        return
    
    # Test rapid requests to trigger rate limiting
    print("\nTesting rapid requests to /health endpoint...")
    
    success_count = 0
    rate_limited_count = 0
    
    async with aiohttp.ClientSession() as session:
        # Make 70 rapid requests (should exceed the 60/min limit)
        for i in range(70):
            try:
                async with session.get(f"{BASE_URL}/health") as response:
                    if response.status == 200:
                        success_count += 1
                        if i < 5 or i % 10 == 0:  # Show some progress
                            remaining = response.headers.get("X-RateLimit-Remaining", "?")
                            print(f"Request {i+1}: OK - Remaining: {remaining}")
                    elif response.status == 429:
                        rate_limited_count += 1
                        if rate_limited_count <= 3:  # Show first few rate limits
                            print(f"Request {i+1}: RATE LIMITED (429)")
                    
                    # Small delay to avoid overwhelming
                    await asyncio.sleep(0.1)
                    
            except Exception as e:
                print(f"Request {i+1}: ERROR - {e}")
    
    print(f"\nResults:")
    print(f"Successful requests: {success_count}")
    print(f"Rate limited requests: {rate_limited_count}")
    print(f"Total requests: {success_count + rate_limited_count}")
    
    if rate_limited_count > 0:
        print("SUCCESS: Rate limiting is working!")
    else:
        print("WARNING: No rate limiting detected - may need more aggressive testing")

async def test_story_generation_rate_limiting():
    """Test rate limiting on story generation endpoints (most restrictive)."""
    print("\nTesting story generation rate limiting...")
    print("-" * 40)
    
    success_count = 0
    rate_limited_count = 0
    error_count = 0
    
    async with aiohttp.ClientSession() as session:
        # Make 20 requests to story generation endpoint (limit is 15/min)
        for i in range(20):
            payload = {
                "primary_character": f"TestChar{i}",
                "secondary_character": f"TestChar{i+1}"
            }
            
            try:
                async with session.post(f"{BASE_URL}/api/langchain", json=payload) as response:
                    if response.status == 200:
                        success_count += 1
                        print(f"Story {i+1}: Generated successfully")
                    elif response.status == 429:
                        rate_limited_count += 1
                        print(f"Story {i+1}: RATE LIMITED")
                    else:
                        error_count += 1
                        print(f"Story {i+1}: ERROR ({response.status})")
                    
                    # Longer delay for story generation
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                error_count += 1
                print(f"Story {i+1}: EXCEPTION - {e}")
    
    print(f"\nStory Generation Results:")
    print(f"Successful: {success_count}")
    print(f"Rate limited: {rate_limited_count}")
    print(f"Errors: {error_count}")
    
    if rate_limited_count > 0:
        print("SUCCESS: Story generation rate limiting is working!")
    elif success_count < 15:
        print("INFO: May have hit API errors before rate limits")
    else:
        print("WARNING: Rate limiting may not be working for story generation")

async def test_concurrent_requests():
    """Test concurrent requests to trigger rate limiting."""
    print("\nTesting concurrent requests...")
    print("-" * 30)
    
    async def make_request(session, request_id):
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                return {
                    "id": request_id,
                    "status": response.status,
                    "remaining": response.headers.get("X-RateLimit-Remaining", "?")
                }
        except Exception as e:
            return {"id": request_id, "status": -1, "error": str(e)}
    
    async with aiohttp.ClientSession() as session:
        # Create 15 concurrent requests
        tasks = [make_request(session, i+1) for i in range(15)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == 200)
        rate_limited_count = sum(1 for r in results if isinstance(r, dict) and r.get("status") == 429)
        
        print(f"Concurrent request results:")
        print(f"Successful: {success_count}")
        print(f"Rate limited: {rate_limited_count}")
        
        if rate_limited_count > 0:
            print("SUCCESS: Concurrent rate limiting is working!")

def show_rate_limit_info():
    """Show current rate limit configuration."""
    print("\nRate Limit Configuration:")
    print("-" * 25)
    print("Per IP: 60 requests/minute")
    print("Story Generation: 15 requests/minute")
    print("List Endpoints: 30 requests/minute") 
    print("Health Status: 100 requests/minute")
    print("Global Server: 1000 requests/minute")
    print("\nTime Window: 1 minute (fixed)")
    print("Storage: In-memory")

async def main():
    """Main test function."""
    show_rate_limit_info()
    
    # Run basic tests
    await test_basic_rate_limiting()
    
    # Wait a bit before next test
    print("\nWaiting 10 seconds before next test...")
    await asyncio.sleep(10)
    
    # Test story generation rate limiting
    await test_story_generation_rate_limiting()
    
    # Wait a bit before concurrent test
    print("\nWaiting 5 seconds before concurrent test...")
    await asyncio.sleep(5)
    
    # Test concurrent requests
    await test_concurrent_requests()
    
    print("\nRate limiting tests complete!")
    print("\nTo view detailed logs, check: logs/app.log")

if __name__ == "__main__":
    print("Rate Limiting Test Suite")
    print("=" * 50)
    print("Make sure the FastAPI server is running first!")
    print("Command: python backend/main.py")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
    except Exception as e:
        print(f"\nTest suite failed: {e}")
        import traceback
        traceback.print_exc()