#!/usr/bin/env python3
"""
Test script for Rate Limiting functionality.

This script tests the SlowAPI rate limiting middleware implementation
by making multiple rapid requests to different endpoints and verifying
that rate limits are properly enforced.

Usage:
    python test_rate_limiting.py

Requirements:
    - FastAPI server running on localhost:8000
    - Rate limiting middleware enabled
"""

import asyncio
import aiohttp
import time
import sys
from typing import Dict, List, Optional

# Fix Unicode output on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_ENDPOINTS = {
    "health": "/health",
    "provider": "/api/provider",
    "story_generation": "/api/langchain",  # Most restrictive
    "list_endpoints": "/api/stories",      # Moderate
    "health_status": "/health"             # Least restrictive
}

class RateLimitTester:
    """Test suite for rate limiting functionality."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.results: Dict[str, List[Dict]] = {}
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = "GET", **kwargs) -> Dict:
        """Make a single HTTP request and capture response details."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_time = (time.time() - start_time) * 1000
                
                # Capture rate limit headers
                rate_limit_info = {
                    "limit": response.headers.get("X-RateLimit-Limit"),
                    "remaining": response.headers.get("X-RateLimit-Remaining"),
                    "reset": response.headers.get("X-RateLimit-Reset"),
                    "retry_after": response.headers.get("Retry-After")
                }
                
                # Try to get response content
                try:
                    content = await response.json()
                except:
                    content = await response.text()
                
                return {
                    "status_code": response.status,
                    "response_time_ms": round(response_time, 2),
                    "rate_limit_headers": rate_limit_info,
                    "content": content,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            return {
                "status_code": -1,
                "response_time_ms": (time.time() - start_time) * 1000,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def test_endpoint_rate_limit(self, endpoint_name: str, endpoint_path: str, 
                                     request_count: int = 20, delay_ms: int = 50) -> List[Dict]:
        """Test rate limiting for a specific endpoint."""
        print(f"\n🧪 Testing {endpoint_name} rate limiting...")
        print(f"   Making {request_count} requests to {endpoint_path} with {delay_ms}ms delay")
        
        results = []
        
        for i in range(request_count):
            # Determine request method and payload based on endpoint
            if endpoint_path == "/api/langchain":
                # Story generation endpoint needs POST with data
                payload = {
                    "primary_character": f"TestChar{i}",
                    "secondary_character": f"TestChar{i+1}"
                }
                result = await self.make_request(endpoint_path, "POST", json=payload)
            else:
                # Other endpoints are GET
                result = await self.make_request(endpoint_path, "GET")
            
            result["request_number"] = i + 1
            results.append(result)
            
            # Show progress for rate limited requests
            if result["status_code"] == 429:
                print(f"   Request {i+1}: RATE LIMITED (429)")
            elif result["status_code"] >= 400:
                print(f"   Request {i+1}: ERROR ({result['status_code']})")
            elif i == 0 or (i + 1) % 5 == 0:
                remaining = result.get("rate_limit_headers", {}).get("remaining", "?")
                print(f"   Request {i+1}: OK ({result['status_code']}) - Remaining: {remaining}")
            
            # Add delay between requests
            if delay_ms > 0:
                await asyncio.sleep(delay_ms / 1000)
        
        return results
    
    async def test_concurrent_requests(self, endpoint_path: str, concurrent_count: int = 10) -> List[Dict]:
        """Test concurrent requests to trigger rate limiting."""
        print(f"\n⚡ Testing concurrent requests to {endpoint_path}...")
        print(f"   Making {concurrent_count} simultaneous requests")
        
        # Create concurrent tasks
        tasks = []
        for i in range(concurrent_count):
            if endpoint_path == "/api/langchain":
                payload = {
                    "primary_character": f"ConcurrentChar{i}",
                    "secondary_character": f"ConcurrentChar{i+1}"
                }
                task = self.make_request(endpoint_path, "POST", json=payload)
            else:
                task = self.make_request(endpoint_path, "GET")
            tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "request_number": i + 1,
                    "status_code": -1,
                    "error": str(result),
                    "timestamp": time.time()
                })
            else:
                result["request_number"] = i + 1
                processed_results.append(result)
        
        # Show summary
        success_count = sum(1 for r in processed_results if r["status_code"] == 200)
        rate_limited_count = sum(1 for r in processed_results if r["status_code"] == 429)
        error_count = sum(1 for r in processed_results if r["status_code"] not in [200, 429])
        
        print(f"   Results: {success_count} successful, {rate_limited_count} rate limited, {error_count} errors")
        
        return processed_results
    
    def analyze_results(self, endpoint_name: str, results: List[Dict]):
        """Analyze test results and provide summary."""
        if not results:
            print(f"ERROR: No results for {endpoint_name}")
            return
        
        total_requests = len(results)
        successful = sum(1 for r in results if r["status_code"] == 200)
        rate_limited = sum(1 for r in results if r["status_code"] == 429)
        errors = sum(1 for r in results if r["status_code"] not in [200, 429])
        
        # Find when rate limiting kicked in
        first_rate_limit = next((r["request_number"] for r in results if r["status_code"] == 429), None)
        
        print(f"\n📊 Analysis for {endpoint_name}:")
        print(f"   Total requests: {total_requests}")
        print(f"   Successful: {successful}")
        print(f"   Rate limited: {rate_limited}")
        print(f"   Errors: {errors}")
        
        if first_rate_limit:
            print(f"   Rate limiting started at request: {first_rate_limit}")
        
        # Show rate limit headers from first successful request
        first_success = next((r for r in results if r["status_code"] == 200), None)
        if first_success and first_success.get("rate_limit_headers"):
            headers = first_success["rate_limit_headers"]
            if headers.get("limit"):
                print(f"   Rate limit: {headers['limit']} requests per minute")
                print(f"   Remaining after first request: {headers.get('remaining', 'N/A')}")
        
        # Check if rate limiting is working as expected
        if rate_limited > 0:
            print(f"   SUCCESS: Rate limiting is working - blocked {rate_limited} requests")
        else:
            print(f"   WARNING:  No rate limiting detected - may need more aggressive testing")
    
    async def run_comprehensive_test(self):
        """Run comprehensive rate limiting tests."""
        print("Starting comprehensive rate limiting tests...")
        print(f"Testing server at: {self.base_url}")
        
        # Test each endpoint type
        test_scenarios = [
            ("Health Check", "/health", 25, 20),
            ("Provider Info", "/api/provider", 25, 20),
            ("Story Generation (Most Restrictive)", "/api/langchain", 20, 100),
            ("Stories List", "/api/stories", 35, 30),
        ]
        
        for endpoint_name, endpoint_path, request_count, delay_ms in test_scenarios:
            try:
                results = await self.test_endpoint_rate_limit(
                    endpoint_name, endpoint_path, request_count, delay_ms
                )
                self.results[endpoint_name] = results
                self.analyze_results(endpoint_name, results)
                
                # Wait between tests to avoid cross-contamination
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"ERROR: Error testing {endpoint_name}: {e}")
        
        # Test concurrent requests on most restrictive endpoint
        try:
            concurrent_results = await self.test_concurrent_requests("/api/langchain", 15)
            self.results["Concurrent Story Generation"] = concurrent_results
            self.analyze_results("Concurrent Story Generation", concurrent_results)
        except Exception as e:
            print(f"ERROR: Error testing concurrent requests: {e}")
        
        print("\nCOMPLETE: Rate limiting test complete!")
        return self.results

async def main():
    """Main test execution function."""
    print("Rate Limiting Test Suite")
    print("=" * 50)
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print(f"ERROR: Server not responding properly (status: {response.status})")
                    return
                print("OK: Server is running and responding")
    except Exception as e:
        print(f"ERROR: Cannot connect to server at {BASE_URL}")
        print(f"   Error: {e}")
        print("   Make sure the FastAPI server is running with: python backend/main.py")
        return
    
    # Run comprehensive tests
    async with RateLimitTester(BASE_URL) as tester:
        results = await tester.run_comprehensive_test()
        
        # Save results to file for analysis
        try:
            with open("rate_limiting_test_results.json", "w") as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\nSAVED: Test results saved to: rate_limiting_test_results.json")
        except Exception as e:
            print(f"WARNING:  Could not save results to file: {e}")

if __name__ == "__main__":
    print("Starting rate limiting tests...")
    print("Note: Make sure the FastAPI server is running first!")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nINTERRUPTED: Tests interrupted by user")
    except Exception as e:
        print(f"\nERROR: Test suite failed: {e}")
        import traceback
        traceback.print_exc()