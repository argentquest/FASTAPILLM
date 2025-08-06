#!/usr/bin/env python3
"""
Intensive Rate Limiting Test - designed to trigger rate limits
"""

import asyncio
import aiohttp
import time

BASE_URL = "http://localhost:8000"

async def intensive_health_test():
    """Make many rapid requests to health endpoint."""
    print("Intensive Health Endpoint Test")
    print("Making 150 requests as fast as possible...")
    
    success_count = 0
    rate_limited_count = 0
    
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        
        # Make 150 rapid requests with minimal delay
        for i in range(150):
            try:
                async with session.get(f"{BASE_URL}/health") as response:
                    if response.status == 200:
                        success_count += 1
                        # Show rate limit headers from successful requests
                        if i < 10:
                            limit = response.headers.get("X-RateLimit-Limit", "?")
                            remaining = response.headers.get("X-RateLimit-Remaining", "?")
                            reset = response.headers.get("X-RateLimit-Reset", "?")
                            print(f"Request {i+1}: OK - Limit: {limit}, Remaining: {remaining}, Reset: {reset}")
                    elif response.status == 429:
                        rate_limited_count += 1
                        # Show rate limit response details
                        if rate_limited_count <= 5:
                            try:
                                data = await response.json()
                                retry_after = response.headers.get("Retry-After", "?")
                                print(f"Request {i+1}: RATE LIMITED - Retry after: {retry_after}s")
                                if rate_limited_count == 1:
                                    print(f"Rate limit details: {data}")
                            except:
                                print(f"Request {i+1}: RATE LIMITED (429)")
                    
                    # Very minimal delay
                    await asyncio.sleep(0.01)
                    
            except Exception as e:
                print(f"Request {i+1}: ERROR - {e}")
        
        elapsed = time.time() - start_time
        rate = (success_count + rate_limited_count) / elapsed
        
        print(f"\nIntensive Test Results:")
        print(f"Total time: {elapsed:.2f} seconds")
        print(f"Request rate: {rate:.1f} requests/second")
        print(f"Successful: {success_count}")
        print(f"Rate limited: {rate_limited_count}")
        
        if rate_limited_count > 0:
            print("SUCCESS: Rate limiting triggered!")
        else:
            print("WARNING: No rate limiting detected")

async def concurrent_burst_test():
    """Send many concurrent requests at once."""
    print("\nConcurrent Burst Test")
    print("Sending 50 concurrent requests...")
    
    async def make_request(session, request_id):
        try:
            async with session.get(f"{BASE_URL}/health") as response:
                return {
                    "id": request_id,
                    "status": response.status,
                    "limit": response.headers.get("X-RateLimit-Limit"),
                    "remaining": response.headers.get("X-RateLimit-Remaining"),
                    "reset": response.headers.get("X-RateLimit-Reset")
                }
        except Exception as e:
            return {"id": request_id, "status": -1, "error": str(e)}
    
    async with aiohttp.ClientSession() as session:
        # Create 50 concurrent requests
        tasks = [make_request(session, i+1) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        success_results = [r for r in results if r.get("status") == 200]
        rate_limited_results = [r for r in results if r.get("status") == 429]
        
        print(f"Concurrent results:")
        print(f"Successful: {len(success_results)}")
        print(f"Rate limited: {len(rate_limited_results)}")
        
        # Show first few successful responses with headers
        if success_results:
            print("First few successful responses:")
            for i, result in enumerate(success_results[:3]):
                print(f"  {result['id']}: Limit={result['limit']}, Remaining={result['remaining']}")
        
        # Show rate limited responses
        if rate_limited_results:
            print("Rate limited responses:")
            for result in rate_limited_results[:3]:
                print(f"  Request {result['id']}: Rate limited")

async def story_generation_burst():
    """Test story generation rate limiting."""
    print("\nStory Generation Burst Test")
    print("Sending 25 story generation requests...")
    
    success_count = 0
    rate_limited_count = 0
    error_count = 0
    
    async with aiohttp.ClientSession() as session:
        # Make 25 rapid story generation requests
        for i in range(25):
            payload = {
                "primary_character": f"TestChar{i}",
                "secondary_character": f"TestChar{i+100}"
            }
            
            try:
                async with session.post(f"{BASE_URL}/api/langchain", json=payload, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        success_count += 1
                        if success_count <= 5:
                            limit = response.headers.get("X-RateLimit-Limit", "?")
                            remaining = response.headers.get("X-RateLimit-Remaining", "?")
                            print(f"Story {i+1}: OK - Limit: {limit}, Remaining: {remaining}")
                    elif response.status == 429:
                        rate_limited_count += 1
                        print(f"Story {i+1}: RATE LIMITED")
                    else:
                        error_count += 1
                        print(f"Story {i+1}: ERROR ({response.status})")
                    
                    # No delay - test burst capacity
                    
            except asyncio.TimeoutError:
                error_count += 1
                print(f"Story {i+1}: TIMEOUT")
            except Exception as e:
                error_count += 1
                print(f"Story {i+1}: EXCEPTION - {e}")
    
    print(f"\nStory Generation Results:")
    print(f"Successful: {success_count}")
    print(f"Rate limited: {rate_limited_count}")
    print(f"Errors/Timeouts: {error_count}")

async def main():
    """Run intensive rate limiting tests."""
    print("Intensive Rate Limiting Tests")
    print("=" * 50)
    
    # Check server
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print(f"Server not responding: {response.status}")
                    return
    except Exception as e:
        print(f"Cannot connect to server: {e}")
        return
    
    # Run intensive tests
    await intensive_health_test()
    await asyncio.sleep(2)
    
    await concurrent_burst_test()
    await asyncio.sleep(2)
    
    await story_generation_burst()
    
    print("\nIntensive tests complete!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTests interrupted")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()