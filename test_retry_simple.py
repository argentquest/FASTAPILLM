"""Simple retry functionality test for Windows compatibility"""

import asyncio
import time
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from retry_utils import retry_api_calls, get_retry_stats
import httpx

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class TestFailure:
    def __init__(self, fail_count: int):
        self.fail_count = fail_count
        self.call_count = 0
    
    async def call(self):
        self.call_count += 1
        if self.call_count <= self.fail_count:
            raise httpx.ConnectError("Simulated connection error")
        return {"success": True, "attempt": self.call_count}

async def test_retry():
    print("="*50)
    print("RETRY FUNCTIONALITY TEST")
    print("="*50)
    
    # Display retry configuration
    config = get_retry_stats()
    print("\nRetry Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    print("\nTesting retry with 2 failures before success...")
    
    failure_sim = TestFailure(fail_count=2)
    
    @retry_api_calls
    async def test_function():
        return await failure_sim.call()
    
    try:
        start_time = time.time()
        result = await test_function()
        elapsed = (time.time() - start_time) * 1000
        
        print(f"\n[SUCCESS] Operation succeeded after {result['attempt']} attempts")
        print(f"[TIME] Total elapsed: {elapsed:.0f}ms")
        print(f"[RESULT] {result}")
        print("\n[PASS] Retry functionality is working correctly!")
        
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")

if __name__ == "__main__":
    print("Testing retry functionality...\n")
    asyncio.run(test_retry())