"""Test script for MCP server using FastMCP client - Enhanced to extract all MCP objects"""

from fastmcp import Client
import asyncio
import json
import inspect
import sys
import os
from typing import Any, Dict, List
from pprint import pprint

# Fix encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_mcp_objects(mcp_instance) -> Dict[str, Any]:
    """Extract all MCP objects and their details"""
    mcp_info = {
        "server_name": getattr(mcp_instance, 'name', 'Unknown'),
        "server_type": type(mcp_instance).__name__,
        "attributes": {},
        "tools": {},
        "resources": {},
        "methods": {},
        "properties": {},
        "internal_attributes": {}
    }
    
    # Get all attributes
    for attr_name in dir(mcp_instance):
        try:
            attr_value = getattr(mcp_instance, attr_name)
            
            # Skip private attributes unless they're important
            if attr_name.startswith('__') and not attr_name in ['__class__', '__module__']:
                continue
                
            # Categorize attributes
            if attr_name.startswith('_'):
                # Internal attributes
                if attr_name in ['_tools', '_resources', '_prompts', '_registry']:
                    mcp_info["internal_attributes"][attr_name] = {
                        "type": type(attr_value).__name__,
                        "value": str(attr_value)[:100] if not isinstance(attr_value, dict) else f"Dict with {len(attr_value)} items"
                    }
            elif callable(attr_value) and not inspect.isclass(attr_value):
                # Methods
                mcp_info["methods"][attr_name] = {
                    "signature": str(inspect.signature(attr_value)) if hasattr(inspect, 'signature') else "N/A",
                    "doc": inspect.getdoc(attr_value) or "No documentation"
                }
            else:
                # Regular attributes
                mcp_info["attributes"][attr_name] = {
                    "type": type(attr_value).__name__,
                    "value": str(attr_value)[:100]
                }
        except Exception as e:
            mcp_info["attributes"][attr_name] = {"error": str(e)}
    
    # Try to extract tools - enhanced approach for FastMCP
    tool_attrs = ['_tools', 'tools', '_tool_manager', 'tool_manager', '_handler_manager', 'handlers']
    for tool_attr in tool_attrs:
        if hasattr(mcp_instance, tool_attr):
            tools = getattr(mcp_instance, tool_attr)
            
            # Handle different tool storage formats
            if isinstance(tools, dict):
                for tool_name, tool in tools.items():
                    mcp_info["tools"][tool_name] = {
                        "name": getattr(tool, 'name', tool_name),
                        "description": getattr(tool, 'description', getattr(tool, '__doc__', 'No description')),
                        "parameters": getattr(tool, 'parameters', 'Unknown'),
                        "source": tool_attr
                    }
            elif hasattr(tools, '__dict__'):
                # Tool manager object - try to get tools from it
                if hasattr(tools, 'tools'):
                    tool_dict = getattr(tools, 'tools')
                    if isinstance(tool_dict, dict):
                        for tool_name, tool in tool_dict.items():
                            mcp_info["tools"][tool_name] = {
                                "name": getattr(tool, 'name', tool_name),
                                "description": getattr(tool, 'description', getattr(tool, '__doc__', 'No description')),
                                "parameters": str(getattr(tool, 'parameters', 'Unknown'))[:200],
                                "source": f"{tool_attr}.tools"
                            }
                elif hasattr(tools, '_tools'):
                    tool_dict = getattr(tools, '_tools')
                    if isinstance(tool_dict, dict):
                        for tool_name, tool in tool_dict.items():
                            mcp_info["tools"][tool_name] = {
                                "name": getattr(tool, 'name', tool_name),
                                "description": getattr(tool, 'description', getattr(tool, '__doc__', 'No description')),
                                "parameters": str(getattr(tool, 'parameters', 'Unknown'))[:200],
                                "source": f"{tool_attr}._tools"
                            }
    
    # Special handling for FastMCP tools - try to access through handlers
    try:
        # Try to get tools via FastMCP's handler system
        if hasattr(mcp_instance, '_handler_manager') and hasattr(mcp_instance._handler_manager, 'tools'):
            tools = mcp_instance._handler_manager.tools
            for tool_name, tool in tools.items():
                mcp_info["tools"][tool_name] = {
                    "name": getattr(tool, 'name', tool_name),
                    "description": getattr(tool, 'description', getattr(tool, '__doc__', 'No description')),
                    "parameters": str(getattr(tool, 'input_schema', 'Unknown'))[:200],
                    "source": "_handler_manager.tools"
                }
    except Exception as e:
        mcp_info["tools"]["_extraction_error"] = {"error": str(e)}
    
    # Try to extract resources
    resource_attrs = ['_resources', 'resources', '_resource_manager', 'resource_manager']
    for resource_attr in resource_attrs:
        if hasattr(mcp_instance, resource_attr):
            resources = getattr(mcp_instance, resource_attr)
            if isinstance(resources, dict):
                for resource_name, resource in resources.items():
                    mcp_info["resources"][resource_name] = {
                        "name": getattr(resource, 'name', resource_name),
                        "description": getattr(resource, '__doc__', 'No description'),
                        "source": resource_attr
                    }
            break
    
    return mcp_info

async def test_mcp_with_extraction():
    """Test MCP server and extract all objects"""
    # Import the mcp instance from the server file
    from mcp_server import mcp
    
    print("="*60)
    print("MCP SERVER OBJECT EXTRACTION")
    print("="*60)
    
    # Extract MCP objects
    mcp_objects = extract_mcp_objects(mcp)
    
    print("\n1. MCP Server Information:")
    print(f"   Name: {mcp_objects['server_name']}")
    print(f"   Type: {mcp_objects['server_type']}")
    
    print("\n2. Internal Attributes:")
    for attr, info in mcp_objects['internal_attributes'].items():
        print(f"   {attr}: {info}")
    
    # Additional exploration - print all attributes for debugging
    print("\n2b. All Attributes (Debug):")
    all_attrs = [attr for attr in dir(mcp) if not attr.startswith('__')]
    for attr in all_attrs[:20]:  # First 20 to avoid spam
        try:
            value = getattr(mcp, attr)
            print(f"   {attr}: {type(value).__name__} - {str(value)[:60]}")
        except Exception as e:
            print(f"   {attr}: ERROR - {str(e)[:60]}")
    
    print("\n3. Discovered Tools:")
    if mcp_objects['tools']:
        for tool_name, tool_info in mcp_objects['tools'].items():
            print(f"   - {tool_name}:")
            print(f"     Description: {tool_info['description']}")
            print(f"     Source: {tool_info['source']}")
    else:
        print("   No tools found via standard attributes")
    
    print("\n4. Discovered Resources:")
    if mcp_objects['resources']:
        for resource_name, resource_info in mcp_objects['resources'].items():
            print(f"   - {resource_name}: {resource_info['description']}")
    else:
        print("   No resources found")
    
    print("\n5. Available Methods:")
    for method_name, method_info in sorted(mcp_objects['methods'].items())[:10]:
        if not method_name.startswith('_'):
            print(f"   - {method_name}{method_info['signature']}")
    
    # Save full extraction to file
    with open('mcp_objects_extracted.json', 'w') as f:
        # Convert to JSON-serializable format
        json_safe = json.loads(json.dumps(mcp_objects, default=str))
        json.dump(json_safe, f, indent=2)
    print("\n✅ Full extraction saved to mcp_objects_extracted.json")
    
    print("\n" + "="*60)
    print("TESTING MCP CLIENT FUNCTIONALITY")
    print("="*60)
    
    client = Client(mcp)
    
    async with client:
        print("\nTesting MCP Server Tools:\n")
        
        # Test 1: List available frameworks
        print("1. Testing list_frameworks tool:")
        try:
            frameworks_result = await client.call_tool("list_frameworks", {})
            # Extract the content from CallToolResult
            frameworks = frameworks_result.content[0].text if frameworks_result.content else {}
            if isinstance(frameworks, str):
                frameworks = json.loads(frameworks)
            print(json.dumps(frameworks, indent=2))
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n" + "="*50 + "\n")
        
        # Test 2: Generate a simple story with LangChain
        print("2. Testing generate_story_langchain tool:")
        try:
            result = await client.call_tool("generate_story_langchain", {
                "primary_character": "Alice",
                "secondary_character": "Bob"
            })
            # Extract the content from CallToolResult
            story_data = result.content[0].text if result.content else {}
            if isinstance(story_data, str):
                story_data = json.loads(story_data)
            
            print("Story generated successfully!")
            print(f"Framework: {story_data.get('framework')}")
            print(f"Model: {story_data.get('model')}")
            print(f"Transaction ID: {story_data.get('transaction_guid', 'N/A')}")
            print(f"Request ID: {story_data.get('request_id', 'N/A')}")
            print(f"Tokens: {story_data.get('total_tokens')}")
            print(f"Cost: ${story_data.get('estimated_cost_usd', 0):.4f}")
            print(f"\nStory preview (first 200 chars):")
            print(story_data.get('story', '')[:200] + "...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("Starting Enhanced MCP Client Test...\n")
    asyncio.run(test_mcp_with_extraction())