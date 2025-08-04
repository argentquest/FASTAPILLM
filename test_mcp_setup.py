#!/usr/bin/env python3
"""
Test MCP setup without running the full server
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from fastmcp import FastMCP
    print("✅ FastMCP imported successfully")
    
    # Try creating a simple MCP server
    mcp = FastMCP("Test MCP Server")
    print("✅ FastMCP instance created")
    
    # Try creating http_app
    try:
        mcp_app = mcp.http_app(path='/mcp')
        print("✅ http_app created successfully")
        print(f"   Type: {type(mcp_app)}")
        print(f"   Has lifespan: {hasattr(mcp_app, 'lifespan')}")
    except Exception as e:
        print(f"❌ Error creating http_app: {e}")
        print(f"   Error type: {type(e).__name__}")
    
    # Check available methods
    print("\n📋 Available MCP methods:")
    methods = [m for m in dir(mcp) if not m.startswith('_')]
    for method in sorted(methods):
        print(f"   - {method}")
        
except ImportError as e:
    print(f"❌ Failed to import FastMCP: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    print(f"   Error type: {type(e).__name__}")