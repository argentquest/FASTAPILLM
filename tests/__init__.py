"""
Test suite for FASTAPILLM - AI Content Generation Platform

This test suite provides comprehensive testing for the FASTAPILLM application
using pytest with multiple test types and flexible execution options.

Test Structure:
- unit/: Fast isolated unit tests for individual components
- integration/: Service integration tests with mocked external dependencies  
- api/: FastAPI endpoint tests with test client
- database/: Database and ORM-specific tests
- e2e/: End-to-end workflow tests

Test Execution:
- pytest -m unit                    # Fast unit tests only
- pytest -m integration             # Integration tests with mocks
- REAL_AI_TESTS=1 pytest -m ai_real # Integration tests with real AI APIs
- pytest -m "api and not slow"      # Fast API tests
- pytest                            # Full test suite with coverage

Environment Variables:
- REAL_AI_TESTS=1: Use real AI API calls instead of mocks
- TEST_PROVIDER=<name>: Override provider configuration for tests
- TEST_DB_URL=<url>: Override database URL for integration tests
"""