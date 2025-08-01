#!/usr/bin/env python3
"""
Test FastMCP client using the correct Client class.
"""

import asyncio
import json

async def test_fastmcp_client():
    """Test MCP server using proper FastMCP Client"""
    print("🔧 Testing MCP Server with FastMCP Client")
    print("="*50)
    
    try:
        from fastmcp import Client
        
        # Connect to HTTP MCP server on port 9999
        async with Client("http://localhost:9999/mcp") as client:
            print("✅ Connected to MCP server")
            
            # List available tools
            tools = await client.list_tools()
            print(f"📋 Available tools: {len(tools)}")
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Test individual story generation
            if tools:
                # Test first tool
                tool_name = tools[0].name
                print(f"\n🧪 Testing {tool_name}...")
                
                result = await client.call_tool(
                    tool_name,
                    {
                        "primary_character": "Alice",
                        "secondary_character": "Bob"
                    }
                )
                
                print("✅ Story generation successful!")
                print(f"📄 Full JSON Result:")
                print(json.dumps(result, indent=2, default=str))
                
                if isinstance(result, dict) and 'story' in result:
                    story = result['story']
                    preview = story[:150] + "..." if len(story) > 150 else story
                    print(f"\n📖 Story preview: {preview}")
                    print(f"💰 Cost: ${result.get('estimated_cost_usd', 0):.6f}")
                
                # Note: compare_frameworks tool has been removed
                # See FRAMEWORK_COMPARISON.md for details about the removed functionality
                
    except ImportError:
        print("❌ FastMCP Client not available")
        print("Checking what's available in fastmcp package...")
        
        try:
            import fastmcp
            print("FastMCP package contents:")
            print([name for name in dir(fastmcp) if not name.startswith('_')])
        except Exception as e:
            print(f"Error exploring fastmcp: {e}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    asyncio.run(test_fastmcp_client())