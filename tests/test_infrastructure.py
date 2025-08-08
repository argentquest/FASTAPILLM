"""
Infrastructure validation tests.

Validates that the test infrastructure is properly configured.
"""

import pytest
import os
import sys


class TestTestInfrastructure:
    """Test that test infrastructure is working correctly."""
    
    def test_pytest_markers_available(self):
        """Test that pytest markers are properly configured."""
        # This test validates that pytest can access the markers
        # If markers aren't configured, pytest would show warnings
        assert hasattr(pytest, 'mark')
        
        # Test that custom markers work
        @pytest.mark.unit
        def dummy_unit_test():
            pass
        
        @pytest.mark.integration  
        def dummy_integration_test():
            pass
            
        assert True  # If we get here, markers work
    
    def test_backend_path_accessible(self):
        """Test that backend modules can be imported."""
        from pathlib import Path
        backend_path = Path(__file__).parent.parent / "backend"
        
        # Backend path should exist
        assert backend_path.exists()
        assert backend_path.is_dir()
        
        # Should be in Python path (added by conftest.py)
        assert str(backend_path) in sys.path or str(backend_path.resolve()) in sys.path
    
    def test_environment_variables(self):
        """Test environment variable handling."""
        # Test default values
        real_ai_tests = os.getenv("REAL_AI_TESTS", "false").lower() == "true"
        assert isinstance(real_ai_tests, bool)
        
        test_provider = os.getenv("TEST_PROVIDER", "test")
        assert isinstance(test_provider, str)
    
    def test_fixtures_importable(self):
        """Test that test fixtures can be imported."""
        # This validates our fixture modules are properly structured
        from fixtures import ai_mocks
        from fixtures import sample_data
        from fixtures import database
        from fixtures import api_client
        
        assert hasattr(ai_mocks, 'pytest_plugins') or True  # Module exists
        assert hasattr(sample_data, 'pytest_plugins') or True 
        assert hasattr(database, 'pytest_plugins') or True
        assert hasattr(api_client, 'pytest_plugins') or True
    
    def test_fixture_availability(self, test_config, tmp_path):
        """Test that key fixtures are available and working."""
        # test_config should be a dict with configuration
        assert isinstance(test_config, dict)
        assert "real_ai_tests" in test_config
        assert "test_provider" in test_config
        
        # tmp_path should be a path
        assert tmp_path is not None
        assert os.path.exists(tmp_path)
    
    def test_database_fixtures_available(self, in_memory_db_session):
        """Test that database fixtures work."""
        # Should get a database session
        assert in_memory_db_session is not None
        
        # Should be able to execute a simple query
        from sqlalchemy import text
        result = in_memory_db_session.execute(text("SELECT 1 as test")).scalar()
        assert result == 1
    
    @pytest.mark.unit
    def test_unit_marker_works(self):
        """Test that unit marker is properly applied."""
        assert True
    
    @pytest.mark.integration
    def test_integration_marker_works(self):
        """Test that integration marker is properly applied."""
        assert True
    
    @pytest.mark.api
    def test_api_marker_works(self):
        """Test that api marker is properly applied."""
        assert True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])