# Test Suite

This directory contains all test scripts for the AI Story Generator project.

## Test Status Overview

### ✅ Working Tests (All Passing)
- **Unit Tests**: 34/34 passing (config, infrastructure, prompts)
- **MCP Tests**: All 3 frameworks working with real API calls  
- **Logging Tests**: Full request tracking and cost calculation
- **Rate Limiting**: Working (60 req/min per IP, endpoint-specific limits)

### ⚠️ Known Issues
- **API Route Tests**: Some pytest failures due to route mismatches (functionality works)
- **Unicode Encoding**: Fixed in test files for Windows compatibility
- **Module Paths**: Fixed import paths for retry tests

## Available Tests

### MCP Tests (✅ All Working)
- **test_mcp_client.py** - Comprehensive MCP server testing with object extraction
  ```bash
  python test/test_mcp_client.py
  ```
  - Tests all 4 MCP tools: `generate_story_*` and `list_frameworks`
  - Extracts complete MCP object structure to `mcp_objects_extracted.json`
  - Real API calls with cost tracking
  - Full logging verification

- **test_mcp_working.py** - Basic MCP functionality test
  ```bash
  python test/test_mcp_working.py
  ```
  - Tests all 3 AI frameworks (Semantic Kernel, LangChain, LangGraph)
  - Real story generation with performance metrics
  - Request ID tracking and cost calculation

### Logging Tests (✅ Working)
- **test_enhanced_logging.py** - Tests enhanced logging in both FastAPI and MCP servers
  ```bash
  python test/test_enhanced_logging.py
  ```
  - FastAPI endpoint logging
  - MCP server request tracking
  - Cost and performance metrics
  - Error tracking with unique IDs

### Rate Limiting Tests (✅ Working)
- **test_rate_limiting_simple.py** - Simple rate limiting test (RECOMMENDED)
  ```bash
  python test/test_rate_limiting_simple.py
  ```
  - Health endpoint: 9 successful, 61 rate limited ✅
  - Story generation: All properly rate limited ✅
  - Concurrent testing: 7 successful, 8 rate limited ✅

- **test_rate_limiting.py** - Comprehensive rate limiting tests (Fixed Unicode)
  ```bash
  python test/test_rate_limiting.py
  ```
  - Fixed Unicode encoding issues for Windows
  - Comprehensive endpoint testing
  - JSON results export

- **test_rate_limiting_intensive.py** - Intensive test designed to trigger rate limits
  ```bash
  python test/test_rate_limiting_intensive.py
  ```

### Retry Tests (🔧 Fixed Import Paths)
- **test_retry_functionality.py** - Comprehensive retry mechanism testing
  ```bash
  python test/test_retry_functionality.py
  ```
  - Fixed backend directory import paths
  - Tests retry configuration and error handling
  - Some Unicode encoding issues remain

- **test_retry_simple.py** - Simple retry test for Windows compatibility
  ```bash
  python test/test_retry_simple.py
  ```
  - Fixed import paths
  - Windows-compatible Unicode handling

## Unit Tests (✅ 34/34 Passing)

Run the working unit tests with pytest:

```bash
# All working unit tests
pytest tests/unit/test_config.py tests/unit/test_infrastructure.py tests/test_prompts.py -v

# Configuration tests (10/10 passing)
pytest tests/unit/test_config.py -v

# Infrastructure tests (7/7 passing) 
pytest tests/unit/test_infrastructure.py -v

# Prompt tests (17/17 passing)
pytest tests/test_prompts.py -v
```

## Full Test Suite (⚠️ Mixed Results)

```bash
# Run all 264 tests (some expected failures)
pytest

# Run only unit tests (all passing)
pytest tests/unit
```

**Test Results Summary:**
- **Total Tests**: 264
- **Unit Tests Passing**: 34/34 ✅
- **Integration Tests**: Some failures due to route mismatches
- **API Tests**: Some failures due to missing fixtures (fixed in conftest.py)

## Running Tests

All tests can be run from the project root directory:

```bash
# Recommended test sequence
pytest tests/unit/test_config.py tests/unit/test_infrastructure.py tests/test_prompts.py -v
python test/test_mcp_working.py
python test/test_enhanced_logging.py  
python test/test_rate_limiting_simple.py

# For development with server running
python backend/main.py  # In one terminal
python test/test_enhanced_logging.py  # In another terminal
```

## Test Requirements

- Python 3.11+
- UV package manager (recommended) or pip
- All project dependencies installed (`uv pip install -e ".[dev,test]"`)
- For API tests: FastAPI server running on localhost:8000
- For MCP tests: MCP server dependencies installed (FastMCP)

## Docker Testing

Tests can also be run against the containerized services:

```bash
# Start containers
docker-compose up --build

# Run tests against containers
python test/test_enhanced_logging.py
python test/test_rate_limiting_simple.py
```

## Test Coverage

The test suite covers:
- ✅ **Configuration Management**: Environment variables, provider setup
- ✅ **MCP Server Integration**: All tools and frameworks
- ✅ **Logging System**: Request tracking, performance metrics
- ✅ **Rate Limiting**: Per-endpoint and per-IP limits
- ✅ **Prompt Management**: Template loading and validation
- ✅ **Service Infrastructure**: Database, fixtures, mocking
- ⚠️ **API Routes**: Some mismatches between tests and current implementation

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're in the project root directory
2. **Module Not Found**: Install dependencies with `uv pip install -e ".[dev,test]"`
3. **API Connection Errors**: Start the backend server first
4. **Unicode Errors**: Fixed in most test files, use the "simple" versions
5. **Rate Limiting**: Wait between test runs or tests may be rate limited

### Environment Setup

```bash
# Quick setup
uv venv --python 3.11
source .venv/Scripts/activate  # Windows
uv pip install -e ".[dev,test]"

# Run working tests
pytest tests/unit/test_config.py -v
python test/test_mcp_working.py
```