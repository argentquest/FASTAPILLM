#!/usr/bin/env python3
"""
Test MCP server status
"""

import requests
import json

# Check if backend is running
try:
    response = requests.get("http://localhost:8000/")
    print("✅ Backend is running")
except Exception as e:
    print(f"❌ Backend not accessible: {e}")
    exit(1)

# Check MCP status
try:
    response = requests.get("http://localhost:8000/api/mcp-status")
    status = response.json()
    print("\n📊 MCP Status:")
    print(f"  - MCP Available: {status.get('mcp_available')}")
    print(f"  - MCP Mounted: {status.get('mcp_mounted')}")
    print(f"  - MCP Endpoint: {status.get('mcp_endpoint')}")
    print(f"  - Message: {status.get('message')}")
except Exception as e:
    print(f"❌ Failed to get MCP status: {e}")

# Try a direct MCP request with proper JSON-RPC format
print("\n🔧 Testing MCP endpoint with JSON-RPC...")
try:
    # MCP uses JSON-RPC format
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
    
    response = requests.post(
        "http://localhost:8000/mcp",
        json=mcp_request,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"  - Status Code: {response.status_code}")
    print(f"  - Response: {response.text[:200]}...")
    
    if response.status_code == 200:
        data = response.json()
        if "result" in data and "tools" in data["result"]:
            tools = data["result"]["tools"]
            print(f"\n✅ Found {len(tools)} MCP tools:")
            for tool in tools:
                print(f"    - {tool.get('name')}: {tool.get('description')}")
except Exception as e:
    print(f"❌ Failed to test MCP endpoint: {e}")

# Test tool listing endpoint if it exists
print("\n🔍 Checking for other MCP endpoints...")
for endpoint in ["/mcp/tools", "/mcp/tools/list", "/mcp/list-tools"]:
    try:
        response = requests.get(f"http://localhost:8000{endpoint}")
        print(f"  - {endpoint}: {response.status_code}")
    except:
        pass