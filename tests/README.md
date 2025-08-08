# FASTAPILLM Test Suite

A comprehensive pytest-based test system for the FASTAPILLM AI content generation platform.

## Quick Start

```bash
# Run all tests
pytest

# Run only fast unit tests
pytest -m unit

# Run API endpoint tests
pytest -m api  

# Run integration tests with mocked AI
pytest -m integration

# Run with real AI APIs (costs money!)
REAL_AI_TESTS=1 pytest -m ai_real
```

## Test Structure

```
tests/
├── conftest.py              # Global fixtures and configuration
├── fixtures/                # Test fixtures
│   ├── ai_mocks.py         # AI service mocks  
│   ├── api_client.py       # API client helpers
│   ├── database.py         # Database fixtures
│   └── sample_data.py      # Sample test data
├── unit/                   # Fast isolated tests
├── integration/            # Service integration tests
├── api/                   # FastAPI endpoint tests
├── database/              # Database/ORM tests
└── e2e/                   # End-to-end workflow tests
```

## Test Categories

### Unit Tests (`pytest -m unit`)
- ✅ **Fast**: Run in seconds, use in-memory SQLite
- ✅ **Isolated**: Mock all external dependencies (AI APIs, file system)
- ✅ **Focused**: Test individual functions and classes

Example:
```bash
pytest tests/unit/test_config.py -v
```

### Integration Tests (`pytest -m integration`)
- ✅ **Service Integration**: Test interactions between services
- ✅ **Real Database**: Use test database with transaction rollback
- ✅ **Mocked AI**: AI calls are mocked for speed and cost control

Example:
```bash
pytest tests/integration/ -v
```

### API Tests (`pytest -m api`)
- ✅ **FastAPI Testing**: Test all REST endpoints
- ✅ **Request/Response**: Validate API contracts
- ✅ **Error Handling**: Test error responses

Example:
```bash
pytest tests/api/test_story_routes.py -v
```

### Database Tests (`pytest -m database`)
- ✅ **ORM Models**: Test SQLAlchemy models and relationships
- ✅ **Migrations**: Test database migration scripts
- ✅ **Transactions**: Test transaction behavior

### End-to-End Tests (`pytest -m e2e`)
- ✅ **Complete Workflows**: Test full user journeys
- ✅ **Real Dependencies**: Use real database and mocked AI
- ✅ **Performance**: Track response times and resource usage

## Environment Variables

### Test Behavior Control
- `REAL_AI_TESTS=1` - Use real AI APIs instead of mocks (costs money!)
- `TEST_PROVIDER=<name>` - Override provider configuration (openrouter, custom, test)
- `TEST_DB_URL=<url>` - Override database URL for integration tests

### Provider Testing
```bash
# Test with OpenRouter configuration
TEST_PROVIDER=openrouter pytest -m openrouter

# Test with custom provider
TEST_PROVIDER=custom pytest -m custom_provider

# Test real AI integration (careful - this costs money!)
REAL_AI_TESTS=1 pytest -m ai_real
```

## Test Fixtures

### AI Mocking
```python
def test_story_generation(mock_openai_client):
    # mock_openai_client provides predictable responses
    service = StoryService()
    result = await service.generate_story(...)
    assert "test story" in result
```

### Database
```python
def test_model_creation(db_session, story_factory):
    # story_factory creates test stories
    story = story_factory(character="Alice")
    assert story.id is not None
```

### API Testing
```python
def test_story_api(story_api_client):
    # story_api_client provides specialized API methods
    response = story_api_client.generate_story(
        primary_character="Alice",
        method="langchain"
    )
    assert response.status_code == 200
```

## Writing Tests

### Unit Test Example
```python
import pytest

@pytest.mark.unit
def test_config_validation():
    from backend.config import Settings
    
    settings = Settings(provider_api_key="test")
    with pytest.raises(ValueError):
        settings.validate_provider_config()
```

### API Test Example
```python
import pytest

@pytest.mark.api
def test_story_generation_endpoint(story_api_client):
    response = story_api_client.generate_story(
        primary_character="Alice",
        secondary_character="Bob",
        setting="Forest"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "story" in data
    assert "usage" in data
```

### Integration Test Example
```python
import pytest

@pytest.mark.integration
@pytest.mark.ai_real  # Only runs with REAL_AI_TESTS=1
async def test_real_ai_integration(ai_client_factory):
    client = ai_client_factory("openai")
    
    # This makes a real API call!
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
    
    assert response.choices[0].message.content
```

## Test Data

### Factories vs Fixtures
- **Fixtures**: Use for simple, reusable test data
- **Factories**: Use for complex objects that need variations

```python
# Fixture - simple, reusable
@pytest.fixture
def sample_story_request():
    return {"character": "Alice", "setting": "Forest"}

# Factory - flexible, parametrizable  
def story_factory(db_session):
    def _create_story(character="Alice", **kwargs):
        story = Story(character=character, **kwargs)
        db_session.add(story)
        return story
    return _create_story
```

## Performance & Debugging

### Run Tests by Speed
```bash
# Fast tests only (< 1 second each)
pytest -m "unit and not slow"

# Skip slow tests
pytest -m "not slow"

# Only slow tests
pytest -m slow
```

### Debugging Failed Tests
```bash
# Stop on first failure
pytest -x

# Show local variables on failure
pytest --tb=long

# Run specific test with verbose output
pytest tests/unit/test_config.py::test_settings_loading -v -s
```

### Coverage Reports
```bash
# Generate HTML coverage report (when pytest-cov is installed)
pytest --cov=backend --cov-report=html

# Open htmlcov/index.html in browser
```

## Continuous Integration

Tests are designed to run efficiently in CI/CD:

### GitHub Actions Workflow
```yaml
- name: Run Fast Tests
  run: pytest -m unit

- name: Run Integration Tests  
  run: pytest -m integration
  env:
    TEST_DB_URL: postgresql://test:test@localhost/test
    REAL_AI_TESTS: false
```

### Test Parallelization
```bash
# Install pytest-xdist for parallel execution
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Run from backend directory for proper imports
cd backend && pytest ../tests/
```

**Database Errors**
```bash
# Clean test database
rm -f test.db
pytest tests/database/
```

**AI API Errors**
```bash
# Ensure environment variables are set
export PROVIDER_API_KEY=your_key
export PROVIDER_API_BASE_URL=your_url
```

### Test Isolation
Each test runs in isolation:
- ✅ **Database**: Fresh database session per test
- ✅ **Environment**: Patched environment variables
- ✅ **Files**: Temporary files cleaned up automatically
- ✅ **AI Calls**: Mocked by default, no external calls

## Best Practices

### Test Organization
1. **One test per function/behavior**
2. **Clear test names** that describe what is being tested
3. **Arrange-Act-Assert** pattern
4. **Use appropriate markers** for test categorization

### Mocking Strategy
1. **Mock external services** (AI APIs, file system, network)
2. **Use real implementations** for internal logic
3. **Test with realistic data** that matches production
4. **Verify mock calls** when behavior matters

### Performance
1. **Keep unit tests fast** (< 1 second each)
2. **Use in-memory database** for unit tests
3. **Batch integration tests** to reduce setup overhead
4. **Mark slow tests** appropriately

## Examples

See the `tests/unit/test_infrastructure.py` file for working examples of:
- ✅ Basic test structure
- ✅ Fixture usage
- ✅ Marker application
- ✅ Environment testing
- ✅ Database testing

Happy testing! 🧪