# VS Code Debug Configurations

This folder contains VS Code configurations for debugging the AI Story Generator application.

## Available Debug Configurations

### Individual Configurations

1. **Backend (Debug Mode)** - Runs the FastAPI backend using uvicorn with hot reload
2. **Backend Direct** - Runs the FastAPI backend directly via main.py
3. **MCP Server (Debug Mode)** - Runs the MCP server standalone
4. **MCP Server (FastMCP CLI)** - Runs the MCP server using FastMCP CLI
5. **Test MCP Working** - Runs the MCP test script
6. **Test Enhanced Logging** - Runs the enhanced logging test script

### Compound Configurations

1. **Backend + MCP Server** - Runs both Backend and MCP Server in debug mode simultaneously
2. **All Servers (Backend + MCP)** - Runs all servers using direct Python execution

## How to Use

### Running Individual Servers

1. Open the Run and Debug panel (Ctrl+Shift+D)
2. Select the configuration from the dropdown
3. Click the green play button or press F5

### Running Multiple Servers

1. Select one of the compound configurations:
   - "Backend + MCP Server" for debugging both servers
   - "All Servers (Backend + MCP)" for running everything

2. Both servers will start in separate terminal panels

### Using Tasks

You can also use VS Code tasks (Terminal > Run Task):

- **Run Backend + MCP** - Runs both servers as a task
- **Run All + MCP** - Runs backend, MCP server, and React frontend
- **Kill Python Processes** - Stops all Python processes

## Environment Variables

All configurations set the following environment variables:
- `PYTHONPATH`: Set to workspace folder
- `DEBUG_MODE`: "true"
- `LOG_LEVEL`: "DEBUG"

## Tips

1. Use compound configurations to debug the full stack
2. Set breakpoints in both main.py and mcp_server.py
3. Check the terminal output for detailed logging
4. Use "justMyCode": false to debug into libraries

## Troubleshooting

If servers don't start properly:
1. Run "Kill Python Processes" task
2. Check that ports 8000 (backend) are free
3. Ensure virtual environment is activated
4. Check logs/app.log for detailed error messages