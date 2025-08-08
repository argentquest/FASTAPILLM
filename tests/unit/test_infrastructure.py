"""
Test the pytest infrastructure itself.

Simple tests to verify our test setup is working correctly.
"""

import pytest
import os
import sys


@pytest.mark.unit
def test_pytest_markers():
    """Test that pytest markers are working."""
    # This test should be marked as 'unit' by our conftest.py
    assert True


@pytest.mark.unit  
def test_environment_detection():
    """Test environment variable detection."""
    # Test our environment configuration
    assert "REAL_AI_TESTS" not in os.environ or os.environ.get("REAL_AI_TESTS", "false").lower() in ["true", "false"]


@pytest.mark.unit
def test_python_path():
    """Test that Python path is set up correctly."""
    # Backend should be in path for imports
    backend_paths = [p for p in sys.path if "backend" in p.lower()]
    assert len(backend_paths) > 0


@pytest.mark.unit
def test_fixtures_available(test_config):
    """Test that our test fixtures are available."""
    # test_config fixture should be available
    assert isinstance(test_config, dict)
    assert "real_ai_tests" in test_config
    assert "test_provider" in test_config


@pytest.mark.unit
def test_mock_ai_fixtures(mock_openai_client):
    """Test AI mocking fixtures."""
    # Mock client should be available
    assert mock_openai_client is not None
    assert hasattr(mock_openai_client, "chat")


@pytest.mark.unit
def test_sample_data_fixtures(sample_story_request, sample_chat_request):
    """Test sample data fixtures."""
    # Sample data should be available
    assert isinstance(sample_story_request, dict)
    assert "primary_character" in sample_story_request
    
    assert isinstance(sample_chat_request, dict)
    assert "message" in sample_chat_request


@pytest.mark.unit
def test_database_fixture(in_memory_db_session):
    """Test in-memory database fixture."""
    from sqlalchemy import text
    
    # Database session should be available
    assert in_memory_db_session is not None
    # Should be able to execute a simple query
    result = in_memory_db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])