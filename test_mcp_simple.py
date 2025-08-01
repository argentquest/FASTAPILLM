#!/usr/bin/env python3
"""
Simple test script for MCP Server story generation tools.

This script tests the MCP server by making direct HTTP/WebSocket calls
to validate the story generation tools are working correctly.
"""

import asyncio
import json
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional


class SimpleMCPTester:
    """Simple MCP client tester using direct protocol calls"""
    
    def __init__(self, base_url: str = "http://localhost:9999"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool via HTTP"""
        # MCP protocol typically uses JSON-RPC 2.0
        request_data = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/mcp",
                json=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            ) as response:
                result = await response.json()
                return result
        except Exception as e:
            return {"error": str(e)}
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available MCP tools"""
        # FastMCP uses session-based connections
        # First, establish a session
        try:
            # Connect to FastMCP session endpoint
            async with self.session.post(
                f"{self.base_url}/mcp/session",  # Session endpoint
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            ) as session_response:
                if session_response.status == 200:
                    session_data = await session_response.json()
                    session_id = session_data.get("session_id")
                    
                    # Now make the tools/list request with session ID
                    request_data = {
                        "jsonrpc": "2.0",
                        "method": "tools/list",
                        "params": {},
                        "id": 1
                    }
                    
                    async with self.session.post(
                        f"{self.base_url}/mcp",
                        json=request_data,
                        headers={
                            "Content-Type": "application/json",
                            "Accept": "application/json, text/event-stream",
                            "X-Session-ID": session_id
                        }
                    ) as response:
                        result = await response.json()
                        return result
                else:
                    return {"error": f"Failed to establish session: {session_response.status}"}
        except Exception as e:
            return {"error": str(e)}
    
    async def test_story_generation(self, framework: str, primary: str, secondary: str):
        """Test a specific story generation framework"""
        tool_name = f"generate_story_{framework}"
        
        print(f"\n🧪 Testing {tool_name}")
        print(f"   Characters: {primary} & {secondary}")
        
        start_time = datetime.now()
        
        result = await self.call_tool(
            tool_name,
            {
                "primary_character": primary,
                "secondary_character": secondary
            }
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        if "result" in result:
            story_data = result["result"]
            print(f"✅ Success! Generated in {duration:.2f}s")
            print(f"   Story length: {len(story_data.get('story', ''))} chars")
            print(f"   Cost: ${story_data.get('estimated_cost_usd', 0):.6f}")
            return True
        else:
            print(f"❌ Unexpected response: {result}")
            return False


async def test_with_http_api():
    """Test using direct HTTP API calls (fallback if MCP not available)"""
    print("\n📡 Testing via direct HTTP API...")
    
    async with aiohttp.ClientSession() as session:
        # Test each framework
        frameworks = ["semantic-kernel", "langchain", "langgraph"]
        
        for framework in frameworks:
            print(f"\n🧪 Testing {framework}")
            
            try:
                async with session.post(
                    f"http://localhost:8000/api/{framework}",
                    json={
                        "primary_character": "TestHero",
                        "secondary_character": "TestVillain"
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Success!")
                        print(f"   Story ID: {data.get('id')}")
                        print(f"   Length: {len(data.get('story', ''))} chars")
                        print(f"   Cost: ${data.get('estimated_cost_usd', 0):.6f}")
                    else:
                        print(f"❌ Failed with status: {response.status}")
                        
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            await asyncio.sleep(1)  # Rate limiting


async def main():
    """Main test function"""
    print("🚀 MCP Story Generation Tester")
    print("="*50)
    
    # First, try to test MCP server
    print("\n1️⃣ Testing MCP Server on port 9999...")
    
    try:
        async with SimpleMCPTester() as tester:
            # List tools
            tools_response = await tester.list_tools()
            
            if "error" not in tools_response:
                print("✅ MCP server is responding!")
                
                # Test each framework
                frameworks = ["semantic_kernel", "langchain", "langgraph"]
                test_cases = [
                    ("Alice", "Bob"),
                    ("Dragon", "Knight")
                ]
                
                success_count = 0
                total_tests = len(frameworks) * len(test_cases)
                
                for framework in frameworks:
                    for primary, secondary in test_cases:
                        if await tester.test_story_generation(framework, primary, secondary):
                            success_count += 1
                        await asyncio.sleep(1)
                
                print(f"\n📊 MCP Tests Complete: {success_count}/{total_tests} successful")
                
            else:
                print(f"❌ MCP server not available: {tools_response['error']}")
                print("\n2️⃣ Falling back to HTTP API testing...")
                await test_with_http_api()
                
    except Exception as e:
        print(f"❌ Error connecting to MCP server: {str(e)}")
        print("\n2️⃣ Falling back to HTTP API testing...")
        await test_with_http_api()


if __name__ == "__main__":
    print("📋 Pre-flight checks:")
    
    # Check if FastAPI is running
    import socket
    
    api_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    api_result = api_sock.connect_ex(('localhost', 8000))
    api_sock.close()
    
    mcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mcp_result = mcp_sock.connect_ex(('localhost', 9999))
    mcp_sock.close()
    
    print(f"   FastAPI server (port 8000): {'✅ Running' if api_result == 0 else '❌ Not running'}")
    print(f"   MCP server (port 9999): {'✅ Running' if mcp_result == 0 else '❌ Not running'}")
    
    if api_result != 0:
        print("\n⚠️  FastAPI server is not running!")
        print("   Please start it first: python main.py")
        exit(1)
    
    print("\n" + "="*50)
    
    # Run tests
    asyncio.run(main())