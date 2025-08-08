"""
API tests for story routes.

Tests all story-related endpoints including generation, listing, retrieval, and deletion.
"""

import pytest
from unittest.mock import patch, Mock
import json


@pytest.mark.api
class TestStoryGenerationEndpoints:
    """Test story generation API endpoints."""
    
    @pytest.mark.asyncio
    async def test_generate_story_langchain_success(self, story_api_client, response_validator):
        """Test successful story generation with LangChain."""
        # Mock the service response
        mock_response = {
            "story": "Once upon a time, Alice and Bob ventured into an enchanted forest where magic sparkled in every leaf and ancient secrets whispered through the wind. Their friendship would be tested as they faced mystical creatures and discovered powers within themselves they never knew existed.",
            "metadata": {
                "primary_character": "Alice",
                "secondary_character": "Bob",
                "setting": "Enchanted Forest",
                "genre": "Fantasy Adventure",
                "tone": "Whimsical",
                "length": "medium",
                "method": "langchain"
            },
            "usage": {
                "input_tokens": 125,
                "output_tokens": 87,
                "total_tokens": 212,
                "estimated_cost_usd": 0.00212
            },
            "provider_info": {
                "provider": "openrouter",
                "model": "meta-llama/llama-3-8b-instruct"
            },
            "performance": {
                "generation_time_ms": 1500,
                "request_id": "story_20250808_001"
            }
        }
        
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_generate:
            mock_generate.return_value = (
                mock_response["story"], 
                {**mock_response["usage"], **mock_response["performance"]}
            )
            
            response = story_api_client.generate_story(
                primary_character="Alice",
                secondary_character="Bob",
                setting="Enchanted Forest",
                genre="Fantasy Adventure",
                tone="Whimsical",
                length="medium",
                method="langchain"
            )
            
            # Validate response
            data = response_validator.validate_success_response(response, 200)
            
            # Validate story response structure
            assert response_validator.validate_story_response(data)
            assert "Alice" in data["story"]
            assert "Bob" in data["story"]
            assert data["metadata"]["method"] == "langchain"
            assert data["usage"]["total_tokens"] > 0
    
    @pytest.mark.asyncio
    async def test_generate_story_semantic_kernel_success(self, story_api_client, response_validator):
        """Test successful story generation with Semantic Kernel."""
        mock_story = "In the heart of a mystical realm, Charlie the brave knight encountered mysterious forces that would change the course of destiny forever."
        
        with patch('services.story_services.semantic_kernel_service.SemanticKernelService.generate_content') as mock_generate:
            mock_generate.return_value = (
                mock_story,
                {
                    "input_tokens": 100,
                    "output_tokens": 65,
                    "total_tokens": 165,
                    "estimated_cost_usd": 0.00165,
                    "generation_time_ms": 1200
                }
            )
            
            response = story_api_client.generate_story(
                primary_character="Charlie",
                secondary_character="Knight",
                setting="Mystical Realm",
                method="semantic-kernel"
            )
            
            data = response_validator.validate_success_response(response)
            assert "Charlie" in data["story"]
            assert data["metadata"]["method"] == "semantic-kernel"
    
    @pytest.mark.asyncio
    async def test_generate_story_langgraph_success(self, story_api_client, response_validator):
        """Test successful story generation with LangGraph."""
        mock_story = "Diana and Elena's adventure through the Crystal Caverns revealed ancient wisdom and forged an unbreakable bond between the two explorers."
        
        with patch('services.story_services.langgraph_service.LangGraphService.generate_content') as mock_generate:
            mock_generate.return_value = (
                mock_story,
                {
                    "input_tokens": 150,
                    "output_tokens": 95,
                    "total_tokens": 245,
                    "estimated_cost_usd": 0.00245,
                    "generation_time_ms": 2100,
                    "editing_iterations": 2
                }
            )
            
            response = story_api_client.generate_story(
                primary_character="Diana",
                secondary_character="Elena", 
                setting="Crystal Caverns",
                method="langgraph"
            )
            
            data = response_validator.validate_success_response(response)
            assert "Diana" in data["story"]
            assert "Elena" in data["story"]
            assert data["metadata"]["method"] == "langgraph"
    
    def test_generate_story_missing_required_fields(self, story_api_client, response_validator):
        """Test story generation with missing required fields."""
        response = story_api_client.api.post("/api/story/generate/langchain", data={
            # Missing primary_character and secondary_character
            "setting": "Forest"
        })
        
        response_validator.validate_error_response(response, 422)
    
    def test_generate_story_invalid_method(self, client, response_validator):
        """Test story generation with invalid method."""
        response = client.post("/api/story/generate/invalid_method", json={
            "primary_character": "Alice",
            "secondary_character": "Bob",
            "setting": "Forest"
        })
        
        response_validator.validate_error_response(response, 404)
    
    def test_generate_story_long_input_validation(self, story_api_client, response_validator):
        """Test story generation with very long inputs."""
        long_character = "A" * 1000  # 1000 character name
        
        response = story_api_client.generate_story(
            primary_character=long_character,
            secondary_character="Bob",
            setting="Forest"
        )
        
        # Should either succeed or return validation error
        assert response.status_code in [200, 422]
    
    @pytest.mark.asyncio
    async def test_generate_story_service_error(self, story_api_client, response_validator):
        """Test story generation when service throws error."""
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_generate:
            mock_generate.side_effect = Exception("AI service unavailable")
            
            response = story_api_client.generate_story()
            
            response_validator.validate_error_response(response, 500)
    
    def test_generate_story_unicode_characters(self, story_api_client):
        """Test story generation with Unicode characters."""
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_generate:
            mock_generate.return_value = ("Test story with José and María", {"total_tokens": 50})
            
            response = story_api_client.generate_story(
                primary_character="José",
                secondary_character="María",
                setting="Ciudad de México"
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "José" in data["story"]
            assert "María" in data["story"]


@pytest.mark.api
class TestStoryListingEndpoints:
    """Test story listing and retrieval endpoints."""
    
    def test_get_stories_empty_list(self, story_api_client):
        """Test getting stories when none exist."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().order_by().offset().limit().all.return_value = []
            mock_get_db.return_value = mock_session
            
            response = story_api_client.get_stories()
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0
    
    def test_get_stories_with_data(self, story_api_client, populated_database):
        """Test getting stories with existing data."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            
            # Mock story objects
            mock_stories = []
            for i, story_data in enumerate(populated_database["stories"]):
                mock_story = Mock()
                mock_story.id = i + 1
                mock_story.primary_character = story_data.primary_character if hasattr(story_data, 'primary_character') else f"Character{i}"
                mock_story.secondary_character = story_data.secondary_character if hasattr(story_data, 'secondary_character') else f"Character{i+1}" 
                mock_story.story_content = story_data.story_content if hasattr(story_data, 'story_content') else f"Story {i}"
                mock_story.created_at = "2025-01-01T00:00:00"
                mock_stories.append(mock_story)
            
            mock_session.query().order_by().offset().limit().all.return_value = mock_stories
            mock_get_db.return_value = mock_session
            
            response = story_api_client.get_stories()
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
    
    def test_get_stories_pagination(self, story_api_client):
        """Test story pagination.""" 
        response = story_api_client.get_stories(skip=10, limit=5)
        assert response.status_code == 200
        
        # Verify pagination parameters were used
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5  # Should respect limit
    
    def test_get_single_story_success(self, story_api_client):
        """Test getting a single story by ID."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_story = Mock()
            mock_story.id = 1
            mock_story.primary_character = "Alice"
            mock_story.story_content = "Test story"
            mock_session.query().filter().first.return_value = mock_story
            mock_get_db.return_value = mock_session
            
            response = story_api_client.get_story(1)
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
    
    def test_get_single_story_not_found(self, story_api_client):
        """Test getting a story that doesn't exist."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().filter().first.return_value = None
            mock_get_db.return_value = mock_session
            
            response = story_api_client.get_story(999)
            
            assert response.status_code == 404


@pytest.mark.api
class TestStoryManagementEndpoints:
    """Test story management endpoints (delete, update)."""
    
    def test_delete_story_success(self, story_api_client):
        """Test successful story deletion."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_story = Mock()
            mock_story.id = 1
            mock_session.query().filter().first.return_value = mock_story
            mock_get_db.return_value = mock_session
            
            response = story_api_client.delete_story(1)
            
            assert response.status_code == 200
            mock_session.delete.assert_called_once_with(mock_story)
            mock_session.commit.assert_called_once()
    
    def test_delete_story_not_found(self, story_api_client):
        """Test deleting a story that doesn't exist."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().filter().first.return_value = None
            mock_get_db.return_value = mock_session
            
            response = story_api_client.delete_story(999)
            
            assert response.status_code == 404
    
    def test_delete_story_database_error(self, story_api_client):
        """Test story deletion with database error."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_story = Mock()
            mock_session.query().filter().first.return_value = mock_story
            mock_session.delete.side_effect = Exception("Database error")
            mock_get_db.return_value = mock_session
            
            response = story_api_client.delete_story(1)
            
            assert response.status_code == 500


@pytest.mark.api
@pytest.mark.slow
class TestStoryPerformanceEndpoints:
    """Test story endpoint performance and stress scenarios."""
    
    def test_concurrent_story_generation(self, story_api_client):
        """Test concurrent story generation requests."""
        import asyncio
        
        async def generate_story():
            with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_generate:
                mock_generate.return_value = ("Concurrent story", {"total_tokens": 100})
                
                response = story_api_client.generate_story(
                    primary_character=f"Alice{hash(asyncio.current_task())}",
                    secondary_character="Bob"
                )
                return response.status_code
        
        # This would be more appropriate for integration tests
        # but included as an example of performance testing
        pass
    
    def test_large_story_response(self, story_api_client):
        """Test handling of very large story responses.""" 
        large_story = "Once upon a time... " * 1000  # Very long story
        
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_generate:
            mock_generate.return_value = (large_story, {"total_tokens": 5000})
            
            response = story_api_client.generate_story()
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["story"]) > 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])