"""
Integration tests for complete story generation workflows.

Tests end-to-end story generation including database persistence, cost tracking, and logging.
"""

import pytest
from unittest.mock import patch, Mock
import asyncio
from decimal import Decimal


@pytest.mark.integration
class TestStoryGenerationWorkflow:
    """Test complete story generation workflow integration."""
    
    @pytest.mark.asyncio
    async def test_complete_story_generation_langchain(self, integration_db, client):
        """Test complete story generation workflow with LangChain."""
        story_data = {
            "primary_character": "Alice",
            "secondary_character": "Bob", 
            "setting": "Enchanted Forest",
            "genre": "Fantasy Adventure",
            "tone": "Whimsical",
            "length": "medium"
        }
        
        # Mock the AI service response
        expected_story = "Once upon a time in an enchanted forest, Alice and Bob discovered magical creatures and embarked on an extraordinary adventure."
        expected_usage = {
            "input_tokens": 125,
            "output_tokens": 87,
            "total_tokens": 212,
            "estimated_cost_usd": 0.00212,
            "generation_time_ms": 1500,
            "request_id": "story_test_001"
        }
        
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_generate:
            mock_generate.return_value = (expected_story, expected_usage)
            
            # Generate story through API
            response = client.post("/api/story/generate/langchain", json=story_data)
            
            assert response.status_code == 200
            response_data = response.json()
            
            # Verify API response
            assert response_data["story"] == expected_story
            assert response_data["metadata"]["method"] == "langchain"
            assert response_data["usage"]["total_tokens"] == 212
            
            # Verify database persistence
            with integration_db() as db:
                story_record = db.query(Story).filter_by(request_id="story_test_001").first()
                assert story_record is not None
                assert story_record.primary_character == "Alice"
                assert story_record.secondary_character == "Bob"
                assert story_record.story_content == expected_story
                assert story_record.method == "langchain"
                assert story_record.total_tokens == 212
                assert story_record.estimated_cost_usd == Decimal('0.00212')
    
    @pytest.mark.asyncio
    async def test_story_generation_with_error_handling(self, integration_db, client):
        """Test story generation workflow with error scenarios."""
        story_data = {
            "primary_character": "Charlie",
            "secondary_character": "Diana"
        }
        
        # Mock service to raise an exception
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_generate:
            mock_generate.side_effect = Exception("AI service temporarily unavailable")
            
            response = client.post("/api/story/generate/langchain", json=story_data)
            
            # Should return error response
            assert response.status_code == 500
            
            # Verify no incomplete record in database
            with integration_db() as db:
                incomplete_records = db.query(Story).filter_by(primary_character="Charlie").all()
                assert len(incomplete_records) == 0
    
    @pytest.mark.asyncio  
    async def test_concurrent_story_generation(self, integration_db, client):
        """Test multiple concurrent story generation requests."""
        story_requests = [
            {"primary_character": f"Hero{i}", "secondary_character": f"Companion{i}"}
            for i in range(5)
        ]
        
        # Mock successful responses for all requests
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_generate:
            mock_generate.side_effect = [
                (f"Story about Hero{i} and Companion{i}", {
                    "input_tokens": 100 + i * 10,
                    "output_tokens": 50 + i * 5,
                    "total_tokens": 150 + i * 15,
                    "estimated_cost_usd": 0.001 + i * 0.0001,
                    "request_id": f"concurrent_{i}"
                })
                for i in range(5)
            ]
            
            # Send concurrent requests
            tasks = []
            for story_data in story_requests:
                task = asyncio.create_task(
                    asyncio.to_thread(client.post, "/api/story/generate/langchain", json=story_data)
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks)
            
            # Verify all requests succeeded
            for i, response in enumerate(responses):
                assert response.status_code == 200
                data = response.json()
                assert f"Hero{i}" in data["story"]
            
            # Verify all records persisted
            with integration_db() as db:
                total_records = db.query(Story).count()
                assert total_records >= 5
    
    @pytest.mark.asyncio
    async def test_story_retrieval_workflow(self, integration_db, client, sample_data):
        """Test story retrieval after generation."""
        # Pre-populate database with test data
        with integration_db() as db:
            for story_data in sample_data["stories"]:
                story = Story(
                    primary_character=story_data.primary_character,
                    secondary_character=story_data.secondary_character,
                    combined_characters=f"{story_data.primary_character} and {story_data.secondary_character}",
                    story_content=story_data.story_content,
                    method="langchain",
                    total_tokens=100,
                    estimated_cost_usd=Decimal('0.001')
                )
                db.add(story)
            db.commit()
            
            # Get first story ID
            first_story = db.query(Story).first()
            story_id = first_story.id
        
        # Test retrieving single story
        response = client.get(f"/api/story/{story_id}")
        assert response.status_code == 200
        
        story_data = response.json()
        assert story_data["id"] == story_id
        assert "primary_character" in story_data
        assert "story_content" in story_data
        
        # Test retrieving story list
        response = client.get("/api/story/list")
        assert response.status_code == 200
        
        stories_list = response.json()
        assert isinstance(stories_list, list)
        assert len(stories_list) > 0


@pytest.mark.integration
class TestChatWorkflow:
    """Test complete chat workflow integration."""
    
    @pytest.mark.asyncio
    async def test_complete_chat_conversation(self, integration_db, client):
        """Test complete chat conversation workflow."""
        # Start new conversation
        first_message = "Hello, how are you today?"
        
        with patch('services.chat_services.langchain_chat_service.LangChainChatService.send_message') as mock_send:
            mock_send.return_value = (
                "Hello! I'm doing well, thank you for asking. How can I help you?",
                1,  # conversation_id
                2,  # message_id (user=1, assistant=2)
                {
                    "input_tokens": 25,
                    "output_tokens": 18,
                    "total_tokens": 43,
                    "estimated_cost_usd": 0.00043,
                    "request_id": "chat_test_001"
                }
            )
            
            response = client.post("/api/chat/langchain", json={
                "message": first_message,
                "conversation_id": None
            })
            
            assert response.status_code == 200
            data = response.json()
            
            conversation_id = data["conversation_id"]
            assert conversation_id == 1
            assert data["message_id"] == 2
        
        # Continue conversation
        second_message = "Can you help me write a story?"
        
        with patch('services.chat_services.langchain_chat_service.LangChainChatService.send_message') as mock_send:
            mock_send.return_value = (
                "I'd be happy to help you write a story! What kind of story are you interested in?",
                conversation_id,
                4,  # message_id (user=3, assistant=4)
                {
                    "input_tokens": 30,
                    "output_tokens": 22,
                    "total_tokens": 52,
                    "estimated_cost_usd": 0.00052,
                    "request_id": "chat_test_002"
                }
            )
            
            response = client.post("/api/chat/langchain", json={
                "message": second_message,
                "conversation_id": conversation_id
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["conversation_id"] == conversation_id
        
        # Verify database persistence
        with integration_db() as db:
            conversation = db.query(ChatConversation).filter_by(id=conversation_id).first()
            assert conversation is not None
            assert conversation.method == "langchain"
            
            messages = db.query(ChatMessage).filter_by(conversation_id=conversation_id).all()
            assert len(messages) >= 4  # 2 user + 2 assistant messages
    
    @pytest.mark.asyncio
    async def test_chat_conversation_retrieval(self, integration_db, client):
        """Test retrieving chat conversations and messages."""
        # Create test conversation in database
        with integration_db() as db:
            conversation = ChatConversation(
                title="Test Conversation",
                method="langchain"
            )
            db.add(conversation)
            db.flush()
            
            conv_id = conversation.id
            
            # Add test messages
            messages_data = [
                ("user", "Hello"),
                ("assistant", "Hi there!"),
                ("user", "How are you?"),
                ("assistant", "I'm doing well, thanks!")
            ]
            
            for role, content in messages_data:
                message = ChatMessage(
                    conversation_id=conv_id,
                    role=role,
                    content=content,
                    input_tokens=10,
                    output_tokens=5 if role == "assistant" else 0
                )
                db.add(message)
            
            db.commit()
        
        # Test retrieving conversations list
        response = client.get("/api/chat/conversations")
        assert response.status_code == 200
        
        conversations = response.json()
        assert isinstance(conversations, list)
        assert len(conversations) >= 1
        
        # Test retrieving specific conversation
        response = client.get(f"/api/chat/conversations/{conv_id}")
        assert response.status_code == 200
        
        conversation_data = response.json()
        assert conversation_data["id"] == conv_id
        assert "messages" in conversation_data
        assert len(conversation_data["messages"]) == 4


@pytest.mark.integration
class TestContextProcessingWorkflow:
    """Test complete context processing workflow integration."""
    
    @pytest.mark.asyncio
    async def test_complete_context_processing(self, integration_db, client, tmp_path):
        """Test complete context processing workflow."""
        # Create test file
        test_file_content = "This is a test document with important information about the project architecture."
        test_file = tmp_path / "test_doc.txt"
        test_file.write_text(test_file_content)
        
        # Mock context service response
        with patch('services.context_services.langchain_context_service.LangChainContextService.process_context_with_prompt') as mock_process:
            mock_process.return_value = (
                "This document discusses project architecture and contains technical details.",
                1,  # execution_id
                {
                    "input_tokens": 150,
                    "output_tokens": 75,
                    "total_tokens": 225,
                    "estimated_cost_usd": 0.00225,
                    "file_processing_time_ms": 100,
                    "llm_execution_time_ms": 1200,
                    "total_execution_time_ms": 1300,
                    "request_id": "context_test_001"
                }
            )
            
            # Process file through API
            with open(test_file, 'rb') as f:
                response = client.post("/api/context/process/langchain", 
                    files={'file': ('test_doc.txt', f, 'text/plain')},
                    data={
                        'system_prompt': 'Analyze this document: [context]',
                        'user_prompt': 'What are the main topics?',
                        'method': 'langchain'
                    }
                )
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["execution_id"] == 1
            assert "project architecture" in data["response"]
            assert data["usage"]["total_tokens"] == 225
        
        # Verify database persistence
        with integration_db() as db:
            execution = db.query(ContextPromptExecution).filter_by(id=1).first()
            assert execution is not None
            assert execution.original_filename == "test_doc.txt"
            assert execution.file_type == "txt"
            assert execution.method == "langchain"
            assert execution.status == "completed"
            assert execution.total_tokens == 225


@pytest.mark.integration
@pytest.mark.slow
class TestSystemPerformanceWorkflow:
    """Test system performance under load."""
    
    @pytest.mark.asyncio
    async def test_high_load_story_generation(self, integration_db, client):
        """Test system performance under high story generation load."""
        num_requests = 20
        
        # Mock consistent responses
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_generate:
            mock_generate.side_effect = [
                (f"Generated story {i}", {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "total_tokens": 150,
                    "estimated_cost_usd": 0.0015,
                    "request_id": f"load_test_{i:03d}"
                })
                for i in range(num_requests)
            ]
            
            # Create requests
            tasks = []
            for i in range(num_requests):
                story_data = {
                    "primary_character": f"Hero{i}",
                    "secondary_character": f"Companion{i}"
                }
                task = asyncio.create_task(
                    asyncio.to_thread(client.post, "/api/story/generate/langchain", json=story_data)
                )
                tasks.append(task)
            
            # Execute all requests concurrently
            start_time = asyncio.get_event_loop().time()
            responses = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()
            
            total_time = end_time - start_time
            
            # Verify all requests succeeded
            success_count = sum(1 for r in responses if r.status_code == 200)
            assert success_count >= num_requests * 0.9  # Allow 10% failure rate
            
            # Performance assertions
            assert total_time < 30.0  # Should complete within 30 seconds
            
            # Verify database records
            with integration_db() as db:
                total_records = db.query(Story).filter(Story.request_id.like("load_test_%")).count()
                assert total_records >= num_requests * 0.9
    
    @pytest.mark.asyncio
    async def test_mixed_workload_performance(self, integration_db, client):
        """Test system performance with mixed story and chat requests."""
        num_stories = 10
        num_chats = 10
        
        # Mock responses for both services
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_story, \
             patch('services.chat_services.langchain_chat_service.LangChainChatService.send_message') as mock_chat:
            
            mock_story.side_effect = [
                (f"Story {i}", {"total_tokens": 150, "estimated_cost_usd": 0.0015, "request_id": f"mixed_story_{i}"})
                for i in range(num_stories)
            ]
            
            mock_chat.side_effect = [
                (f"Chat response {i}", i+1, (i*2)+2, {"total_tokens": 50, "estimated_cost_usd": 0.0005, "request_id": f"mixed_chat_{i}"})
                for i in range(num_chats)
            ]
            
            # Create mixed tasks
            tasks = []
            
            # Story tasks
            for i in range(num_stories):
                task = asyncio.create_task(
                    asyncio.to_thread(client.post, "/api/story/generate/langchain", json={
                        "primary_character": f"Hero{i}",
                        "secondary_character": f"Companion{i}"
                    })
                )
                tasks.append(task)
            
            # Chat tasks
            for i in range(num_chats):
                task = asyncio.create_task(
                    asyncio.to_thread(client.post, "/api/chat/langchain", json={
                        "message": f"Chat message {i}",
                        "conversation_id": None
                    })
                )
                tasks.append(task)
            
            # Execute all tasks
            responses = await asyncio.gather(*tasks)
            
            # Verify mixed workload handling
            success_count = sum(1 for r in responses if r.status_code == 200)
            assert success_count >= (num_stories + num_chats) * 0.8  # Allow 20% failure rate for mixed load


@pytest.mark.integration
class TestCostTrackingIntegration:
    """Test cost tracking across all services."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_cost_tracking(self, integration_db, client):
        """Test cost tracking through complete workflows."""
        initial_cost = Decimal('0.00')
        
        # Generate multiple requests with known costs
        test_scenarios = [
            ("story", "/api/story/generate/langchain", {"primary_character": "A", "secondary_character": "B"}, Decimal('0.001')),
            ("chat", "/api/chat/langchain", {"message": "Hello", "conversation_id": None}, Decimal('0.0005')),
            ("story", "/api/story/generate/semantic-kernel", {"primary_character": "C", "secondary_character": "D"}, Decimal('0.0015'))
        ]
        
        total_expected_cost = sum(cost for _, _, _, cost in test_scenarios)
        
        # Mock services with known costs
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_story_lc, \
             patch('services.story_services.semantic_kernel_service.SemanticKernelService.generate_content') as mock_story_sk, \
             patch('services.chat_services.langchain_chat_service.LangChainChatService.send_message') as mock_chat:
            
            mock_story_lc.return_value = ("Story", {"estimated_cost_usd": 0.001, "total_tokens": 100, "request_id": "cost_story_lc"})
            mock_story_sk.return_value = ("Story", {"estimated_cost_usd": 0.0015, "total_tokens": 150, "request_id": "cost_story_sk"})
            mock_chat.return_value = ("Response", 1, 2, {"estimated_cost_usd": 0.0005, "total_tokens": 50, "request_id": "cost_chat"})
            
            # Execute test scenarios
            for service_type, endpoint, data, expected_cost in test_scenarios:
                response = client.post(endpoint, json=data)
                assert response.status_code == 200
        
        # Verify cost tracking in database
        with integration_db() as db:
            # Check individual records
            story_records = db.query(Story).filter(Story.request_id.like("cost_story_%")).all()
            chat_messages = db.query(ChatMessage).filter(ChatMessage.request_id.like("cost_chat%")).all()
            
            total_story_cost = sum(record.estimated_cost_usd or 0 for record in story_records)
            total_chat_cost = sum(message.estimated_cost_usd or 0 for message in chat_messages)
            total_actual_cost = total_story_cost + total_chat_cost
            
            # Allow small rounding differences
            assert abs(total_actual_cost - total_expected_cost) < Decimal('0.0001')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])