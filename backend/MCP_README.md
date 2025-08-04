# FASTAPILLM MCP Server

This is a standalone MCP (Model Context Protocol) server that provides AI story generation tools following FastMCP best practices from https://gofastmcp.com.

## Features

The MCP server exposes the following tools:

- `generate_story_semantic_kernel`: Generate stories using Microsoft's Semantic Kernel
- `generate_story_langchain`: Generate stories using LangChain framework  
- `generate_story_langgraph`: Generate stories using LangGraph with advanced editing
- `list_frameworks`: List all available AI frameworks

## Architecture Changes

### ✅ Refactored to FastMCP Best Practices
- **Standalone MCP Server**: `mcp_server.py` runs independently from main FastAPI app
- **Clean Separation**: Main API (`main.py`) and MCP server are completely decoupled
- **FastMCP Patterns**: Uses `@mcp.tool` decorators and `if __name__ == "__main__": mcp.run()`
- **Enhanced Logging**: Comprehensive request tracking with unique IDs and performance metrics

### ✅ Enhanced Logging System
Both `main.py` and `mcp_server.py` now feature detailed logging:

- **Request Tracking**: Unique request IDs for all operations
- **Performance Metrics**: Timing information for all requests
- **Error Tracking**: Detailed error logging with context
- **Structured Fields**: Consistent logging format across both services

## Running the MCP Server

### Standalone Mode (Recommended)

Run the MCP server independently:

```bash
# From the backend directory
python mcp_server.py
```

Or using FastMCP CLI:

```bash
fastmcp run backend.mcp_server:mcp
```

### VS Code Debug Configurations

Use the provided VS Code configurations:

- **MCP Server (Debug Mode)**: Direct Python execution with debugging
- **MCP Server (FastMCP CLI)**: Using FastMCP CLI with debugging
- **Backend + MCP Server**: Run both servers simultaneously
- **Test MCP Client (Enhanced)**: Run the enhanced MCP extraction test

## Integration

The main FastAPI application (main.py) now runs separately from the MCP server, following FastMCP best practices. This allows:

- Independent scaling of MCP and API services
- Easier testing and debugging
- Better separation of concerns
- Standard FastMCP tooling compatibility
- Full debugging support in VS Code

## Enhanced Testing & Extraction

### test_mcp_client.py (Enhanced)

The enhanced test client provides comprehensive MCP object extraction:

```python
from fastmcp import Client
import asyncio

async def test_mcp_with_extraction():
    from backend.mcp_server import mcp
    
    # Extract all MCP objects
    mcp_objects = extract_mcp_objects(mcp)
    
    # Test tools
    client = Client(mcp)
    async with client:
        # Test all available tools
        result = await client.call_tool("list_frameworks", {})
        print("Frameworks:", result)
```

### Extraction Results

The enhanced test successfully extracts:
- ✅ All 4 MCP tools via `_tool_manager._tools`
- ✅ Complete parameter schemas
- ✅ FastMCP internal structure
- ✅ Method signatures and documentation
- ✅ 25KB detailed JSON export (`mcp_objects_extracted.json`)

### Available Test Scripts

1. **test_mcp_working.py**: Basic MCP functionality test
2. **test_mcp_client.py**: Enhanced MCP object extraction
3. **test_enhanced_logging.py**: Logging system verification

## Logging Features

### MCP Server Logging
- Request IDs (e.g., `lc_20250804_121706_1124`)
- Performance timing for each tool call
- Detailed service creation and execution logs
- Cost and token tracking per request

### FastAPI Logging
- Application lifecycle events
- Middleware and router registration
- Request/response tracking
- Health check and endpoint access logs

## Current File Structure

```
backend/
├── main.py                     # FastAPI application (enhanced logging)
├── mcp_server.py              # Standalone MCP server (enhanced logging)
├── test_mcp_client.py         # Enhanced MCP extraction test
├── test_mcp_working.py        # Basic MCP functionality test
├── MCP_README.md              # This file
├── MCP_EXTRACTION_SUMMARY.md  # Detailed extraction results
└── mcp_objects_extracted.json # Full MCP object dump

.vscode/
├── launch.json                # Debug configurations for both servers
├── tasks.json                 # Build tasks for all services
└── DEBUG_README.md            # VS Code debugging guide
```

## Requirements

- fastmcp
- All dependencies from the main application (see requirements.txt)
- Python 3.11+ (for enhanced type hints and async features)

## Debugging & Development

The codebase now supports comprehensive debugging:

1. **Individual Debugging**: Debug MCP server or FastAPI independently
2. **Compound Debugging**: Debug both servers simultaneously  
3. **Enhanced Logging**: Detailed request tracing and performance metrics
4. **Object Extraction**: Complete MCP structure analysis and tool discovery

All configurations are ready for immediate use in VS Code with proper breakpoint support and variable inspection.