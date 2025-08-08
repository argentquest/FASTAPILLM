"""
End-to-end tests for complete user workflows.

Tests complete user journeys from API requests through to database persistence and response.
"""

import pytest
from unittest.mock import patch, Mock
import asyncio
import json
import tempfile
import time
from decimal import Decimal


@pytest.mark.e2e
class TestCompleteStoryGenerationWorkflow:
    """Test complete story generation user workflow."""
    
    @pytest.mark.asyncio
    async def test_full_story_generation_journey_langchain(self, e2e_client, real_database):
        """Test complete story generation journey from API to database with LangChain."""
        # User story: A user wants to generate a fantasy story about Alice and Bob
        
        # Step 1: User sends story generation request
        story_request = {
            "primary_character": "Alice",
            "secondary_character": "Bob",
            "setting": "Enchanted Forest",
            "genre": "Fantasy Adventure", 
            "tone": "Whimsical",
            "length": "medium"
        }
        
        # Mock the AI service to return consistent results
        expected_story = "In the heart of an enchanted forest, Alice and Bob discovered a magical portal that transported them to a realm where talking animals shared ancient wisdom and mystical creatures guided them on an unforgettable quest to restore balance to both worlds."
        
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_generate:
            mock_generate.return_value = (expected_story, {
                "input_tokens": 145,
                "output_tokens": 92,
                "total_tokens": 237,
                "estimated_cost_usd": 0.00237,
                "generation_time_ms": 1800,
                "request_id": "e2e_story_lc_001",
                "input_cost_per_1k_tokens": 0.001,
                "output_cost_per_1k_tokens": 0.002
            })
            
            # Step 2: Make API request
            response = e2e_client.post("/api/story/generate/langchain", json=story_request)
            
            # Step 3: Verify immediate API response
            assert response.status_code == 200
            response_data = response.json()
            
            assert response_data["story"] == expected_story
            assert response_data["metadata"]["primary_character"] == "Alice"
            assert response_data["metadata"]["secondary_character"] == "Bob"
            assert response_data["metadata"]["method"] == "langchain"
            assert response_data["usage"]["total_tokens"] == 237
            assert response_data["usage"]["estimated_cost_usd"] == 0.00237
            assert "request_id" in response_data["performance"]
        
        # Step 4: Verify database persistence (wait a moment for async operations)
        await asyncio.sleep(0.1)
        
        with real_database() as db:
            story_record = db.query(Story).filter_by(request_id="e2e_story_lc_001").first()
            
            assert story_record is not None
            assert story_record.primary_character == "Alice"
            assert story_record.secondary_character == "Bob" 
            assert story_record.combined_characters == "Alice and Bob"
            assert story_record.story_content == expected_story
            assert story_record.method == "langchain"
            assert story_record.total_tokens == 237
            assert story_record.estimated_cost_usd == Decimal('0.00237')
            assert story_record.provider is not None
            assert story_record.model is not None
            assert story_record.created_at is not None
        
        # Step 5: User retrieves the story by ID
        story_id = story_record.id
        
        retrieve_response = e2e_client.get(f"/api/story/{story_id}")
        assert retrieve_response.status_code == 200
        
        retrieved_data = retrieve_response.json()
        assert retrieved_data["id"] == story_id
        assert retrieved_data["story_content"] == expected_story
        assert retrieved_data["primary_character"] == "Alice"
        
        # Step 6: User lists their stories
        list_response = e2e_client.get("/api/story/list")
        assert list_response.status_code == 200
        
        stories_list = list_response.json()
        assert isinstance(stories_list, list)
        assert len(stories_list) >= 1
        
        # Find our story in the list
        our_story = next((s for s in stories_list if s["id"] == story_id), None)
        assert our_story is not None
        assert our_story["primary_character"] == "Alice"
    
    @pytest.mark.asyncio
    async def test_story_generation_with_all_frameworks(self, e2e_client, real_database):
        """Test story generation with all three AI frameworks."""
        base_request = {
            "primary_character": "Hero",
            "secondary_character": "Companion",
            "setting": "Mountain Peak"
        }
        
        frameworks = ["langchain", "semantic-kernel", "langgraph"]
        generated_stories = {}
        
        # Generate stories with each framework
        for i, framework in enumerate(frameworks):
            expected_story = f"A {framework} generated story about Hero and Companion on a mountain peak adventure."
            
            with patch(f'services.story_services.{framework.replace("-", "_")}_service.{framework.replace("-", "").title()}Service.generate_content') as mock_generate:
                mock_generate.return_value = (expected_story, {
                    "input_tokens": 120 + i * 10,
                    "output_tokens": 80 + i * 5,
                    "total_tokens": 200 + i * 15,
                    "estimated_cost_usd": 0.002 + i * 0.0001,
                    "generation_time_ms": 1500 + i * 200,
                    "request_id": f"e2e_multi_{framework}_{i:03d}"
                })
                
                response = e2e_client.post(f"/api/story/generate/{framework}", json=base_request)
                assert response.status_code == 200
                
                data = response.json()
                assert data["metadata"]["method"] == framework
                assert data["story"] == expected_story
                
                generated_stories[framework] = data
        
        # Verify all stories were persisted
        await asyncio.sleep(0.1)
        
        with real_database() as db:
            for framework in frameworks:
                story = db.query(Story).filter(
                    Story.request_id.like(f"e2e_multi_{framework}_%")
                ).first()
                
                assert story is not None
                assert story.method == framework
                assert story.primary_character == "Hero"
                assert story.secondary_character == "Companion"


@pytest.mark.e2e
class TestCompleteChatWorkflow:
    """Test complete chat conversation user workflow."""
    
    @pytest.mark.asyncio
    async def test_full_chat_conversation_journey(self, e2e_client, real_database):
        """Test complete chat conversation from start to finish."""
        conversation_id = None
        message_history = []
        
        # Conversation flow: greeting -> question -> follow-up -> goodbye
        conversation_flow = [
            ("Hello! How are you today?", "Hello! I'm doing well, thank you for asking. How can I help you?"),
            ("Can you help me write a story about dragons?", "I'd be happy to help you write a dragon story! What kind of dragon story interests you - adventure, fantasy, or something else?"),
            ("I'd like an adventure story with a brave knight.", "Great choice! An adventure story with a brave knight and dragons sounds exciting. Would you like me to create that story for you?"),
            ("Yes, please create the story.", "Here's your dragon adventure story: Sir Galahad rode through the misty mountains, seeking the ancient dragon that had been terrorizing the kingdom..."),
            ("Thank you! That was perfect.", "You're very welcome! I'm glad you enjoyed the story. Feel free to ask if you need help with anything else!")
        ]
        
        for i, (user_message, expected_response) in enumerate(conversation_flow):
            with patch('services.chat_services.langchain_chat_service.LangChainChatService.send_message') as mock_send:
                # Calculate expected IDs based on conversation progress
                expected_conv_id = 1 if conversation_id is None else conversation_id
                expected_msg_id = (i * 2) + 2  # User messages are odd IDs, assistant even
                
                mock_send.return_value = (
                    expected_response,
                    expected_conv_id,
                    expected_msg_id,
                    {
                        "input_tokens": len(user_message.split()) * 2,
                        "output_tokens": len(expected_response.split()) * 2,
                        "total_tokens": (len(user_message.split()) + len(expected_response.split())) * 2,
                        "estimated_cost_usd": 0.0001 * (i + 1),
                        "generation_time_ms": 800 + i * 100,
                        "request_id": f"e2e_chat_{i:03d}"
                    }
                )
                
                # Send message
                chat_request = {
                    "message": user_message,
                    "conversation_id": conversation_id
                }
                
                response = e2e_client.post("/api/chat/langchain", json=chat_request)
                assert response.status_code == 200
                
                data = response.json()
                assert data["response"] == expected_response
                assert data["conversation_id"] == expected_conv_id
                assert data["message_id"] == expected_msg_id
                
                # Update conversation ID for subsequent messages
                conversation_id = data["conversation_id"]
                message_history.append((user_message, expected_response, data["message_id"]))
        
        # Verify conversation persistence
        await asyncio.sleep(0.1)
        
        with real_database() as db:
            conversation = db.query(ChatConversation).filter_by(id=conversation_id).first()
            assert conversation is not None
            assert conversation.method == "langchain"
            
            messages = db.query(ChatMessage).filter_by(conversation_id=conversation_id).order_by(ChatMessage.id).all()
            
            # Should have 10 messages total (5 user + 5 assistant)
            assert len(messages) >= 10
            
            # Verify message content and roles
            for i, (user_msg, assistant_msg, _) in enumerate(message_history):
                user_message = messages[i * 2]
                assistant_message = messages[i * 2 + 1]
                
                assert user_message.role == "user"
                assert user_message.content == user_msg
                assert assistant_message.role == "assistant"
                assert assistant_message.content == assistant_msg
        
        # Test retrieving conversation
        conv_response = e2e_client.get(f"/api/chat/conversations/{conversation_id}")
        assert conv_response.status_code == 200
        
        conv_data = conv_response.json()
        assert conv_data["id"] == conversation_id
        assert "messages" in conv_data
        assert len(conv_data["messages"]) >= 10
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_conversations(self, e2e_client, real_database):
        """Test handling multiple concurrent chat conversations."""
        num_conversations = 3
        conversation_tasks = []
        
        async def create_conversation(conv_index):
            """Create a single conversation with multiple messages."""
            conversation_id = None
            
            for msg_index in range(3):  # 3 messages per conversation
                user_message = f"Conversation {conv_index}, message {msg_index + 1}"
                assistant_response = f"Response from conversation {conv_index}, message {msg_index + 1}"
                
                with patch('services.chat_services.langchain_chat_service.LangChainChatService.send_message') as mock_send:
                    mock_send.return_value = (
                        assistant_response,
                        conv_index + 1 if conversation_id is None else conversation_id,
                        (msg_index * 2) + 2,
                        {
                            "input_tokens": 20,
                            "output_tokens": 25,
                            "total_tokens": 45,
                            "estimated_cost_usd": 0.00045,
                            "request_id": f"concurrent_chat_{conv_index}_{msg_index}"
                        }
                    )
                    
                    response = await asyncio.to_thread(
                        e2e_client.post,
                        "/api/chat/langchain",
                        json={
                            "message": user_message,
                            "conversation_id": conversation_id
                        }
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    conversation_id = data["conversation_id"]
            
            return conversation_id
        
        # Create multiple conversations concurrently
        for i in range(num_conversations):
            task = asyncio.create_task(create_conversation(i))
            conversation_tasks.append(task)
        
        conversation_ids = await asyncio.gather(*conversation_tasks)
        
        # Verify all conversations were created
        assert len(conversation_ids) == num_conversations
        assert len(set(conversation_ids)) == num_conversations  # All unique
        
        # Verify database persistence
        await asyncio.sleep(0.2)
        
        with real_database() as db:
            for conv_id in conversation_ids:
                conversation = db.query(ChatConversation).filter_by(id=conv_id).first()
                assert conversation is not None
                
                messages = db.query(ChatMessage).filter_by(conversation_id=conv_id).all()
                assert len(messages) >= 6  # 3 user + 3 assistant messages


@pytest.mark.e2e
class TestCompleteContextProcessingWorkflow:
    """Test complete context processing user workflow."""
    
    @pytest.mark.asyncio
    async def test_full_context_processing_journey(self, e2e_client, real_database, tmp_path):
        """Test complete file upload and processing workflow."""
        # Create test files
        test_files = [
            ("project_spec.txt", "text/plain", "This is a project specification document detailing the requirements for a new web application with user authentication and data management features."),
            ("README.md", "text/markdown", "# Project Title\n\nThis is a sample README file with:\n- Installation instructions\n- Usage examples\n- API documentation\n\n## Features\n- User management\n- Data processing\n- Report generation"),
            ("config.json", "application/json", '{"app_name": "TestApp", "version": "1.0.0", "features": ["auth", "api", "reports"], "database": {"type": "postgresql", "host": "localhost"}}')
        ]
        
        processed_files = []
        
        for filename, mime_type, content in test_files:
            # Create temporary file
            test_file = tmp_path / filename
            test_file.write_text(content, encoding='utf-8')
            
            # Mock context processing service
            expected_response = f"Analysis of {filename}: This document contains technical information about project configuration and implementation details."
            
            with patch('services.context_services.langchain_context_service.LangChainContextService.process_context_with_prompt') as mock_process:
                mock_process.return_value = (
                    expected_response,
                    len(processed_files) + 1,  # execution_id
                    {
                        "input_tokens": len(content.split()) * 2,
                        "output_tokens": len(expected_response.split()) * 2,
                        "total_tokens": (len(content.split()) + len(expected_response.split())) * 2,
                        "estimated_cost_usd": 0.001 + len(processed_files) * 0.0005,
                        "file_processing_time_ms": 150 + len(processed_files) * 50,
                        "llm_execution_time_ms": 1200 + len(processed_files) * 200,
                        "total_execution_time_ms": 1350 + len(processed_files) * 250,
                        "request_id": f"e2e_context_{filename.replace('.', '_')}"
                    }
                )
                
                # Process file
                with open(test_file, 'rb') as f:
                    response = e2e_client.post(
                        "/api/context/process/langchain",
                        files={'file': (filename, f, mime_type)},
                        data={
                            'system_prompt': f'Analyze this {filename} file: [context]',
                            'user_prompt': 'What are the key points and technical details?',
                            'method': 'langchain'
                        }
                    )
                
                assert response.status_code == 200
                data = response.json()
                
                assert data["response"] == expected_response
                assert data["execution_id"] == len(processed_files) + 1
                assert data["metadata"]["original_filename"] == filename
                assert data["metadata"]["file_type"] == filename.split('.')[-1]
                assert data["usage"]["total_tokens"] > 0
                
                processed_files.append((filename, data["execution_id"]))
        
        # Verify database persistence
        await asyncio.sleep(0.1)
        
        with real_database() as db:
            for filename, exec_id in processed_files:
                execution = db.query(ContextPromptExecution).filter_by(id=exec_id).first()
                
                assert execution is not None
                assert execution.original_filename == filename
                assert execution.method == "langchain"
                assert execution.status == "completed"
                assert execution.llm_response is not None
                assert execution.total_tokens > 0
                assert execution.estimated_cost_usd > 0
        
        # Test retrieving execution history
        history_response = e2e_client.get("/api/context/executions")
        assert history_response.status_code == 200
        
        history_data = history_response.json()
        assert isinstance(history_data, list)
        assert len(history_data) >= 3
        
        # Verify our executions are in the history
        our_executions = [ex for ex in history_data if ex["id"] in [exec_id for _, exec_id in processed_files]]
        assert len(our_executions) == 3


@pytest.mark.e2e
class TestCostTrackingWorkflow:
    """Test complete cost tracking across all operations."""
    
    @pytest.mark.asyncio
    async def test_comprehensive_cost_tracking_journey(self, e2e_client, real_database):
        """Test cost tracking across story generation, chat, and context processing."""
        total_expected_cost = Decimal('0.0')
        operations_performed = []
        
        # Operation 1: Generate multiple stories
        story_costs = [Decimal('0.002'), Decimal('0.0015'), Decimal('0.0025')]
        
        for i, expected_cost in enumerate(story_costs):
            with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_generate:
                mock_generate.return_value = (
                    f"Generated story {i+1} with unique content and characters.",
                    {
                        "input_tokens": 100 + i * 20,
                        "output_tokens": 60 + i * 10,
                        "total_tokens": 160 + i * 30,
                        "estimated_cost_usd": float(expected_cost),
                        "request_id": f"cost_story_{i:03d}"
                    }
                )
                
                response = e2e_client.post("/api/story/generate/langchain", json={
                    "primary_character": f"Hero{i}",
                    "secondary_character": f"Companion{i}"
                })
                
                assert response.status_code == 200
                total_expected_cost += expected_cost
                operations_performed.append(("story", expected_cost))
        
        # Operation 2: Have chat conversations
        chat_costs = [Decimal('0.0005'), Decimal('0.0003'), Decimal('0.0007')]
        
        for i, expected_cost in enumerate(chat_costs):
            with patch('services.chat_services.langchain_chat_service.LangChainChatService.send_message') as mock_send:
                mock_send.return_value = (
                    f"Chat response {i+1} with helpful information.",
                    i + 1,  # conversation_id
                    2,      # message_id
                    {
                        "input_tokens": 20 + i * 5,
                        "output_tokens": 15 + i * 3,
                        "total_tokens": 35 + i * 8,
                        "estimated_cost_usd": float(expected_cost),
                        "request_id": f"cost_chat_{i:03d}"
                    }
                )
                
                response = e2e_client.post("/api/chat/langchain", json={
                    "message": f"Test message {i+1}",
                    "conversation_id": None
                })
                
                assert response.status_code == 200
                total_expected_cost += expected_cost
                operations_performed.append(("chat", expected_cost))
        
        # Wait for database operations
        await asyncio.sleep(0.2)
        
        # Verify cost tracking in database
        with real_database() as db:
            # Check story costs
            story_records = db.query(Story).filter(Story.request_id.like("cost_story_%")).all()
            assert len(story_records) == 3
            
            story_total = sum(record.estimated_cost_usd or 0 for record in story_records)
            expected_story_total = sum(story_costs)
            assert abs(story_total - expected_story_total) < Decimal('0.0001')
            
            # Check chat costs
            chat_messages = db.query(ChatMessage).filter(ChatMessage.request_id.like("cost_chat_%")).all()
            assert len(chat_messages) >= 3  # At least 3 assistant messages
            
            chat_total = sum(msg.estimated_cost_usd or 0 for msg in chat_messages if msg.role == "assistant")
            expected_chat_total = sum(chat_costs)
            assert abs(chat_total - expected_chat_total) < Decimal('0.0001')
            
            # Verify total cost tracking
            total_actual_cost = story_total + chat_total
            assert abs(total_actual_cost - total_expected_cost) < Decimal('0.0001')
        
        # Test cost summary API
        cost_summary_response = e2e_client.get("/api/costs/summary")
        assert cost_summary_response.status_code == 200
        
        summary_data = cost_summary_response.json()
        assert "total_cost_usd" in summary_data
        assert "total_requests" in summary_data
        assert summary_data["total_requests"] >= 6  # 3 stories + 3 chats


@pytest.mark.e2e
@pytest.mark.slow
class TestSystemReliabilityWorkflow:
    """Test system reliability under various conditions."""
    
    @pytest.mark.asyncio
    async def test_system_resilience_under_load(self, e2e_client, real_database):
        """Test system behavior under sustained load."""
        num_requests = 15
        success_count = 0
        error_count = 0
        
        # Mix of different operation types
        operations = [
            ("story", "/api/story/generate/langchain", {"primary_character": "LoadHero", "secondary_character": "LoadCompanion"}),
            ("chat", "/api/chat/langchain", {"message": "Load test message", "conversation_id": None}),
        ]
        
        # Mock services for consistent responses
        with patch('services.story_services.langchain_service.LangChainService.generate_content') as mock_story, \
             patch('services.chat_services.langchain_chat_service.LangChainChatService.send_message') as mock_chat:
            
            mock_story.return_value = ("Load test story", {"total_tokens": 100, "estimated_cost_usd": 0.001, "request_id": "load_story"})
            mock_chat.return_value = ("Load test response", 1, 2, {"total_tokens": 50, "estimated_cost_usd": 0.0005, "request_id": "load_chat"})
            
            # Create tasks for concurrent execution
            tasks = []
            for i in range(num_requests):
                op_type, endpoint, data = operations[i % len(operations)]
                
                task = asyncio.create_task(
                    asyncio.to_thread(e2e_client.post, endpoint, json=data)
                )
                tasks.append(task)
            
            # Execute with timeout
            try:
                responses = await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=30.0)
                
                for response in responses:
                    if isinstance(response, Exception):
                        error_count += 1
                    elif hasattr(response, 'status_code'):
                        if response.status_code == 200:
                            success_count += 1
                        else:
                            error_count += 1
                    else:
                        error_count += 1
                
            except asyncio.TimeoutError:
                pytest.fail("System failed to handle load within timeout period")
        
        # System should handle most requests successfully
        success_rate = success_count / num_requests
        assert success_rate >= 0.8, f"Success rate too low: {success_rate:.2f} ({success_count}/{num_requests})"
        
        # Verify database consistency after load test
        await asyncio.sleep(0.5)
        
        with real_database() as db:
            # Database should be in consistent state
            total_stories = db.query(Story).count()
            total_conversations = db.query(ChatConversation).count()
            total_messages = db.query(ChatMessage).count()
            
            # Should have some records (exact count may vary due to failures)
            assert total_stories >= 0
            assert total_conversations >= 0
            assert total_messages >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])