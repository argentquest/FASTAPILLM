# Test Suite

This directory contains all test scripts for the AI Story Generator project.

## Available Tests

### MCP Tests
- **test_mcp_client.py** - Comprehensive MCP server testing with object extraction
  ```bash
  python test/test_mcp_client.py
  ```

- **test_mcp_working.py** - Basic MCP functionality test
  ```bash
  python test/test_mcp_working.py
  ```

### Logging Tests
- **test_enhanced_logging.py** - Tests enhanced logging in both FastAPI and MCP servers
  ```bash
  python test/test_enhanced_logging.py
  ```

### Retry Tests
- **test_retry_functionality.py** - Comprehensive retry mechanism testing
  ```bash
  python test/test_retry_functionality.py
  ```

- **test_retry_simple.py** - Simple retry test for Windows compatibility
  ```bash
  python test/test_retry_simple.py
  ```

### Rate Limiting Tests
- **test_rate_limiting.py** - Comprehensive rate limiting tests
  ```bash
  python test/test_rate_limiting.py
  ```

- **test_rate_limiting_simple.py** - Simple rate limiting test
  ```bash
  python test/test_rate_limiting_simple.py
  ```

- **test_rate_limiting_intensive.py** - Intensive test designed to trigger rate limits
  ```bash
  python test/test_rate_limiting_intensive.py
  ```

## Running Tests

All tests can be run from the project root directory:

```bash
# Run MCP tests
python test/test_mcp_client.py

# Run with the FastAPI server running
python backend/main.py  # In one terminal
python test/test_enhanced_logging.py  # In another terminal
```

## Test Requirements

- Python 3.11+
- All project dependencies installed
- For API tests: FastAPI server running on localhost:8000
- For MCP tests: MCP server dependencies installed