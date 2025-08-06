#!/usr/bin/env python3
"""
Test script to verify enhanced logging in both main.py and mcp_server.py
"""

import asyncio
import aiohttp
import json
import sys
import os

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend directory to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(root_dir, 'backend'))

async def test_api_logging():
    """Test main.py API logging"""
    print("=" * 60)
    print("🧪 Testing main.py API Enhanced Logging")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("\n1️⃣ Testing /health endpoint...")
        async with session.get(f"{base_url}/health") as resp:
            data = await resp.json()
            print(f"✅ Health check: {data['status']}")
            print(f"   Request ID: {data.get('request_id', 'N/A')}")
            print(f"   Uptime: {data.get('uptime_seconds', 0)} seconds")
        
        # Test provider info endpoint
        print("\n2️⃣ Testing /api/provider endpoint...")
        async with session.get(f"{base_url}/api/provider") as resp:
            data = await resp.json()
            print(f"✅ Provider: {data['provider']}")
            print(f"   Model: {data['model']}")
            print(f"   Configured: {data['configured']}")
        
        # Test MCP status endpoint
        print("\n3️⃣ Testing /api/mcp-status endpoint...")
        async with session.get(f"{base_url}/api/mcp-status") as resp:
            data = await resp.json()
            print(f"✅ MCP Available: {data['mcp_available']}")
            print(f"   Message: {data['message']}")
        
        # Test validation error logging
        print("\n4️⃣ Testing validation error logging...")
        try:
            async with session.post(f"{base_url}/api/langchain", 
                                  json={"invalid": "data"}) as resp:
                if resp.status == 422:
                    data = await resp.json()
                    print(f"✅ Validation error caught")
                    print(f"   Error ID: {data['error'].get('error_id', 'N/A')}")
                    print(f"   Fields: {len(data['error']['details'])} validation errors")
        except Exception as e:
            print(f"❌ Error: {e}")

async def test_mcp_logging():
    """Test mcp_server.py logging"""
    print("\n" + "=" * 60)
    print("🧪 Testing mcp_server.py Enhanced Logging")
    print("=" * 60)
    
    try:
        from fastmcp import Client
        from backend.mcp_server import mcp
        
        client = Client(mcp)
        
        async with client:
            # Test list_frameworks
            print("\n1️⃣ Testing list_frameworks logging...")
            result = await client.call_tool("list_frameworks", {})
            if hasattr(result, 'content') and result.content:
                data = result.content[0].text
                if isinstance(data, str):
                    data = json.loads(data)
                print(f"✅ Frameworks listed: {len(data.get('frameworks', []))}")
            
            # Test story generation with unique characters
            print("\n2️⃣ Testing story generation logging...")
            test_chars = [
                ("Alice", "Bob"),
                ("Charlie", "Diana"),
                ("Eve", "Frank")
            ]
            
            for primary, secondary in test_chars:
                print(f"\n   Testing with {primary} and {secondary}...")
                try:
                    result = await client.call_tool("generate_story_langchain", {
                        "primary_character": primary,
                        "secondary_character": secondary
                    })
                    print(f"   ✅ Story generated for {primary} & {secondary}")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                # Small delay to see separate log entries
                await asyncio.sleep(0.5)
                
    except ImportError:
        print("❌ FastMCP not available")
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Run all tests"""
    print("🚀 Enhanced Logging Test Suite")
    print("=" * 60)
    print("This test verifies detailed logging in both main.py and mcp_server.py")
    print("Watch the console output to see the enhanced logging in action!")
    print("=" * 60)
    
    # Test API logging
    await test_api_logging()
    
    # Test MCP logging
    await test_mcp_logging()
    
    print("\n" + "=" * 60)
    print("✅ Enhanced Logging Test Complete!")
    print("Check the logs for detailed information including:")
    print("  - Request IDs for tracing")
    print("  - Timing information")
    print("  - Detailed debug logs")
    print("  - Error tracking with IDs")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())