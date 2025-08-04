#!/usr/bin/env python3
"""
Test FastMCP client using the correct Client class.
Following FastMCP best practices, the MCP server runs standalone.
"""

import asyncio
import json
import sys
import os
from retry_utils import get_retry_stats

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

async def test_fastmcp_client():
    """Test MCP server using proper FastMCP Client"""
    print("🔧 Testing MCP Server with FastMCP Client")
    print("="*50)
    
    # Display retry configuration
    retry_config = get_retry_stats()
    print("\n⚙️ Retry Configuration:")
    print(f"  Enabled: {retry_config['retry_enabled']}")
    print(f"  Max Attempts: {retry_config['max_attempts']}")
    print(f"  Max Wait: {retry_config['max_wait_seconds']}s")
    print(f"  Backoff Multiplier: {retry_config['multiplier']}")
    print()
    
    try:
        from fastmcp import Client
        
        # Import the MCP server instance directly (for local testing)
        from backend.mcp_server import mcp
        
        print("🔄 Creating local client from MCP server instance...")
        client = Client(mcp)
        
        async with client:
            print("✅ Connected to MCP server")
            
            # List available tools
            print("\n📋 Listing available tools...")
            tools_result = await client.call_tool("list_frameworks", {})
            
            # Extract content from CallToolResult
            if hasattr(tools_result, 'content') and tools_result.content:
                frameworks_data = tools_result.content[0].text
                if isinstance(frameworks_data, str):
                    frameworks_data = json.loads(frameworks_data)
                
                print(f"Available frameworks:")
                for framework in frameworks_data.get('frameworks', []):
                    print(f"  - {framework['name']}: {framework['description']}")
                    if retry_config['retry_enabled']:
                        print(f"    🔄 Retry protection: ENABLED")
                    for feature in framework.get('features', []):
                        print(f"    • {feature}")
            
            # Test story generation with each framework
            test_frameworks = ["langchain", "semantic_kernel", "langgraph"]
            
            for framework in test_frameworks:
                print(f"\n🧪 Testing generate_story_{framework}...")
                
                try:
                    result = await client.call_tool(
                        f"generate_story_{framework}",
                        {
                            "primary_character": "Alice",
                            "secondary_character": "Bob"
                        }
                    )
                    
                    # Extract content from CallToolResult
                    if hasattr(result, 'content') and result.content:
                        story_data = result.content[0].text
                        if isinstance(story_data, str):
                            story_data = json.loads(story_data)
                        
                        print(f"✅ {framework} generation successful!")
                        print(f"  Model: {story_data.get('model', 'N/A')}")
                        print(f"  Tokens: {story_data.get('total_tokens', 0)}")
                        print(f"  Cost: ${story_data.get('estimated_cost_usd', 0):.6f}")
                        
                        story = story_data.get('story', '')
                        preview = story[:150] + "..." if len(story) > 150 else story
                        print(f"  Story preview: {preview}")
                    
                except Exception as e:
                    print(f"⚠️  Failed to generate story with {framework}: {e}")
                
    except ImportError as e:
        print("❌ Import error:", str(e))
        print("\nMake sure you have FastMCP installed:")
        print("  pip install fastmcp")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fastmcp_client())