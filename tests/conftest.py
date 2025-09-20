"""
Global pytest configuration and fixtures for FASTAPILLM test suite.

This module provides:
- Environment-based test configuration
- Database session management (in-memory vs real DB)
- AI mocking vs real API toggle
- FastAPI test client setup
- Common test fixtures
"""

import os
import sys
import pytest
from typing import Generator, AsyncGenerator
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from pathlib import Path

# Add backend to Python path for imports
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import after path setup
from fastapi.testclient import TestClient
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Test environment configuration
REAL_AI_TESTS = os.getenv("REAL_AI_TESTS", "false").lower() == "true"
TEST_PROVIDER = os.getenv("TEST_PROVIDER", "test")
TEST_DB_URL = os.getenv("TEST_DB_URL")


@pytest.fixture(scope="session")
def test_config():
    """Test configuration fixture."""
    return {
        "real_ai_tests": REAL_AI_TESTS,
        "test_provider": TEST_PROVIDER,
        "test_db_url": TEST_DB_URL,
        "temp_dir": tempfile.mkdtemp(prefix="fastapillm_test_"),
    }


@pytest.fixture(scope="session")
def in_memory_db_engine():
    """Create an in-memory SQLite engine for fast unit tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    return engine


@pytest.fixture(scope="session") 
def test_db_engine(test_config):
    """Create a test database engine for integration tests."""
    if test_config["test_db_url"]:
        engine = create_engine(test_config["test_db_url"])
    else:
        # Use a temporary SQLite file for integration tests
        db_file = os.path.join(test_config["temp_dir"], "test.db")
        engine = create_engine(f"sqlite:///{db_file}")
    
    return engine


@pytest.fixture
def in_memory_db_session(in_memory_db_engine) -> Generator[Session, None, None]:
    """Provide an in-memory database session for unit tests."""
    try:
        from database import Base
    except ImportError:
        # Create a minimal Base for testing if database module not available
        from sqlalchemy.ext.declarative import declarative_base
        Base = declarative_base()
    
    # Create all tables
    Base.metadata.create_all(in_memory_db_engine)
    
    # Create session
    SessionLocal = sessionmaker(bind=in_memory_db_engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Clean up tables
        Base.metadata.drop_all(in_memory_db_engine)


@pytest.fixture
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Provide a real database session for integration tests with transaction rollback."""
    try:
        from database import Base
    except ImportError:
        # Create a minimal Base for testing if database module not available
        from sqlalchemy.ext.declarative import declarative_base
        Base = declarative_base()
    
    # Create all tables
    Base.metadata.create_all(test_db_engine)
    
    # Create session with transaction
    SessionLocal = sessionmaker(bind=test_db_engine)
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def db_session(request):
    """Smart database session fixture that chooses between in-memory and real DB based on test markers."""
    if "integration" in request.keywords or "api" in request.keywords or "e2e" in request.keywords:
        return request.getfixturevalue("test_db_session")
    else:
        return request.getfixturevalue("in_memory_db_session")


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for AI service tests."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "This is a test AI response."
    mock_response.usage.prompt_tokens = 50
    mock_response.usage.completion_tokens = 25
    mock_response.usage.total_tokens = 75
    
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def ai_client_factory(test_config):
    """Factory fixture for AI clients - returns mocked or real based on configuration."""
    def _create_client(service_type="openai"):
        if test_config["real_ai_tests"]:
            # Return real client for integration tests
            if service_type == "openai":
                from openai import AsyncOpenAI
                from backend.app_config import settings
                return AsyncOpenAI(
                    api_key=settings.provider_api_key,
                    base_url=settings.provider_api_base_url
                )
        else:
            # Return mocked client for unit tests
            return MagicMock()
    
    return _create_client


@pytest.fixture
def test_app():
    """Create FastAPI test application with test configuration."""
    # Patch configuration for testing
    with patch.dict(os.environ, {
        "PROVIDER_NAME": TEST_PROVIDER,
        "PROVIDER_API_KEY": "test-key",
        "PROVIDER_API_BASE_URL": "https://test.api.com/v1",
        "PROVIDER_MODEL": "test-model",
        "DEBUG_MODE": "true",
        "DATABASE_URL": "sqlite:///test.db"
    }):
        try:
            from main import create_app
            app = create_app()
            return app
        except ImportError:
            # Fallback for test-only FastAPI app
            from fastapi import FastAPI
            app = FastAPI(title="Test App")
            return app


@pytest.fixture
def client(test_app):
    """FastAPI test client."""
    return TestClient(test_app)


@pytest.fixture
async def async_client(test_app):
    """Async FastAPI test client."""
    from httpx import AsyncClient
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_story_request():
    """Sample story generation request for testing."""
    return {
        "primary_character": "Alice",
        "secondary_character": "Bob", 
        "setting": "Enchanted Forest",
        "genre": "Fantasy Adventure",
        "tone": "Whimsical",
        "length": "medium"
    }


@pytest.fixture
def sample_chat_request():
    """Sample chat request for testing."""
    return {
        "message": "Hello, how are you today?",
        "conversation_id": None,
        "system_prompt": "You are a helpful assistant."
    }


@pytest.fixture
def sample_context_request():
    """Sample context processing request for testing."""
    return {
        "file_ids": ["test-file-1", "test-file-2"],
        "system_prompt": "Analyze the following context: [context]",
        "user_prompt": "What are the key insights?",
        "method": "langchain"
    }


@pytest.fixture
def temp_upload_file():
    """Create a temporary file for upload testing."""
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write("This is test content for file upload testing.")
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    try:
        os.unlink(temp_file.name)
    except FileNotFoundError:
        pass


@pytest.fixture(autouse=True)
def mock_ai_services_for_unit_tests(request, mock_openai_client):
    """Automatically mock AI services for unit tests."""
    if "unit" in request.keywords and not REAL_AI_TESTS:
        # Only patch if the modules exist
        try:
            with patch("services.base_ai_service.AsyncOpenAI") as mock_openai:
                mock_openai.return_value = mock_openai_client
                yield
        except (ImportError, ModuleNotFoundError):
            # Module doesn't exist, skip patching
            yield
    else:
        yield


# Import API client fixtures
pytest_plugins = ["tests.fixtures.api_client"]


# Cleanup fixture
@pytest.fixture(scope="session", autouse=True)
def cleanup_temp_files(test_config):
    """Clean up temporary files after test session."""
    yield
    
    # Cleanup temporary directory
    if os.path.exists(test_config["temp_dir"]):
        shutil.rmtree(test_config["temp_dir"])


# Pytest hooks for better test organization
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    # Ensure our custom markers are registered
    config.addinivalue_line(
        "markers", "unit: Fast isolated unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: Service integration tests"  
    )
    config.addinivalue_line(
        "markers", "api: FastAPI endpoint tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "database" in str(item.fspath):
            item.add_marker(pytest.mark.database)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)


def pytest_runtest_setup(item):
    """Setup hook to handle environment-based test skipping."""
    # Skip ai_real tests if REAL_AI_TESTS is not set
    if "ai_real" in item.keywords and not REAL_AI_TESTS:
        pytest.skip("Real AI tests disabled (set REAL_AI_TESTS=1 to enable)")
    
    # Skip provider-specific tests if different provider is configured
    if "openrouter" in item.keywords and TEST_PROVIDER != "openrouter":
        pytest.skip(f"OpenRouter test skipped (current provider: {TEST_PROVIDER})")
    
    if "custom_provider" in item.keywords and TEST_PROVIDER != "custom":
        pytest.skip(f"Custom provider test skipped (current provider: {TEST_PROVIDER})")