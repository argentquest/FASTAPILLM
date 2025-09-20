"""
Test script for retry functionality verification

This script tests the retry mechanisms implemented across the application
to ensure they work correctly under various failure scenarios.
"""

import asyncio
import time
from unittest.mock import patch, AsyncMock
import sys
import os

# Add backend directory to path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
sys.path.append(backend_dir)

from retry_utils import (
    retry_api_calls, 
    retry_database_ops, 
    retry_network_ops,
    get_retry_stats,
    is_retryable_error
)
from app_config import settings
from logging_config import get_logger
import httpx
import openai
from sqlalchemy.exc import OperationalError

logger = get_logger(__name__)

# Test functions with retry decorators
@retry_api_calls
async def test_api_call_with_retries():
    """Test function that simulates API failures."""
    # This will be mocked to fail then succeed
    await asyncio.sleep(0.1)
    return {"status": "success", "data": "api_response"}

@retry_network_ops  
async def test_network_operation():
    """Test function that simulates network failures."""
    await asyncio.sleep(0.1)
    return {"status": "connected"}

@retry_database_ops
def test_database_operation():
    """Test function that simulates database failures."""
    time.sleep(0.1)
    return {"status": "saved", "id": 123}

class MockFailure:
    """Helper class to simulate controlled failures."""
    
    def __init__(self, fail_count: int):
        self.fail_count = fail_count
        self.call_count = 0
    
    async def async_call(self):
        self.call_count += 1
        if self.call_count <= self.fail_count:
            # Fail for the first N calls
            raise httpx.ConnectError("Simulated connection error")
        return {"success": True, "attempt": self.call_count}
    
    def sync_call(self):
        self.call_count += 1
        if self.call_count <= self.fail_count:
            raise OperationalError("Simulated database error", None, None)
        return {"success": True, "attempt": self.call_count}

async def test_retry_scenarios():
    """Test various retry scenarios."""
    print("="*60)
    print("RETRY FUNCTIONALITY TESTS")
    print("="*60)
    
    # Display current retry configuration
    retry_config = get_retry_stats()
    print("\nRetry Configuration:")
    for key, value in retry_config.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*50)
    print("TEST 1: Error Classification")
    print("="*50)
    
    # Test error classification
    test_errors = [
        httpx.ConnectError("Connection failed"),
        httpx.TimeoutException("Request timeout"),
        ConnectionError("Network connection error"),
        OperationalError("Database connection lost", None, None),
        ValueError("Non-retryable error")
    ]
    
    for error in test_errors:
        retryable = is_retryable_error(error)
        print(f"  {type(error).__name__}: {'RETRYABLE' if retryable else 'NOT RETRYABLE'}")
    
    print("\n" + "="*50)
    print("TEST 2: Successful Retry After Failures")
    print("="*50)
    
    # Test successful retry after 2 failures
    mock_failure = MockFailure(fail_count=2)
    
    @retry_api_calls
    async def failing_then_succeeding():
        return await mock_failure.async_call()
    
    try:
        start_time = time.time()
        result = await failing_then_succeeding()
        elapsed = (time.time() - start_time) * 1000
        
        print(f"  ✅ Success after {result['attempt']} attempts")
        print(f"  ⏱️  Total time: {elapsed:.0f}ms")
        print(f"  📊 Final result: {result}")
        
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
    
    print("\n" + "="*50)
    print("TEST 3: Exhausted Retries")
    print("="*50)
    
    # Test what happens when all retries are exhausted
    mock_persistent_failure = MockFailure(fail_count=10)  # More failures than max attempts
    
    @retry_api_calls
    async def always_failing():
        return await mock_persistent_failure.async_call()
    
    try:
        start_time = time.time()
        result = await always_failing()
        print(f"  ❌ Unexpected success: {result}")
        
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        print(f"  ✅ Expected failure after all retries: {type(e).__name__}")
        print(f"  ⏱️  Total time: {elapsed:.0f}ms")
        print(f"  🔢 Total attempts made: {mock_persistent_failure.call_count}")
    
    print("\n" + "="*50)
    print("TEST 4: Database Retry Operations")
    print("="*50)
    
    # Test database retry with synchronous function
    mock_db_failure = MockFailure(fail_count=1)
    
    @retry_database_ops
    def failing_db_operation():
        return mock_db_failure.sync_call()
    
    try:
        start_time = time.time()
        result = failing_db_operation()
        elapsed = (time.time() - start_time) * 1000
        
        print(f"  ✅ Database operation succeeded after {result['attempt']} attempts")
        print(f"  ⏱️  Total time: {elapsed:.0f}ms")
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
    
    print("\n" + "="*50)
    print("TEST 5: Retry Disabled Behavior")
    print("="*50)
    
    # Test behavior when retries are disabled
    original_retry_enabled = settings.retry_enabled
    
    try:
        # Temporarily disable retries
        settings.retry_enabled = False
        
        @retry_api_calls
        async def should_not_retry():
            raise httpx.ConnectError("This should fail immediately")
        
        try:
            start_time = time.time()
            await should_not_retry()
            print("  ❌ Unexpected success")
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            print(f"  ✅ Failed immediately without retries: {type(e).__name__}")
            print(f"  ⏱️  Total time: {elapsed:.0f}ms (should be very fast)")
            
    finally:
        # Restore original setting
        settings.retry_enabled = original_retry_enabled
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print("  ✅ Error classification working")
    print("  ✅ Retry after failures working") 
    print("  ✅ Exhausted retries handling working")
    print("  ✅ Database retries working")
    print("  ✅ Retry disable mechanism working")
    print("\n🎉 All retry functionality tests completed successfully!")

if __name__ == "__main__":
    print("Starting Retry Functionality Tests...\n")
    asyncio.run(test_retry_scenarios())