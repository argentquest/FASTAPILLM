#!/usr/bin/env python3
"""
Standalone MCP Server Runner

Run the MCP server independently on port 9999.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.mcp.server import run_standalone_mcp_server

if __name__ == "__main__":
    print("🚀 Starting standalone MCP server on port 9999...")
    run_standalone_mcp_server()