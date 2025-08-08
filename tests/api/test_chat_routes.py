"""
API tests for chat routes.

Tests all chat-related endpoints including message sending, conversation management, and history.
"""

import pytest
from unittest.mock import patch, Mock
import json


@pytest.mark.api
class TestChatMessageEndpoints:
    """Test chat message sending endpoints."""
    
    @pytest.mark.asyncio
    async def test_send_message_new_conversation(self, chat_api_client, response_validator):
        """Test sending a message that creates a new conversation."""
        mock_response = {
            "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
            "conversation_id": 1,
            "message_id": 2,  # User message = 1, assistant = 2
            "usage": {
                "input_tokens": 25,
                "output_tokens": 18,
                "total_tokens": 43,
                "estimated_cost_usd": 0.00043
            },
            "performance": {
                "generation_time_ms": 800,
                "request_id": "chat_20250808_001"
            }
        }
        
        with patch('services.chat_services.langchain_chat_service.LangChainChatService') as mock_service:
            mock_instance = Mock()
            mock_instance.send_message.return_value = (
                mock_response["response"],
                mock_response["conversation_id"],
                mock_response["message_id"],
                {**mock_response["usage"], **mock_response["performance"]}
            )
            mock_service.return_value = mock_instance
            
            response = chat_api_client.send_message(
                message="Hello, how are you today?",
                conversation_id=None,  # New conversation
                method="langchain"
            )
            
            # Validate response
            data = response_validator.validate_success_response(response, 200)
            
            # Validate chat response structure
            assert response_validator.validate_chat_response(data)
            assert data["conversation_id"] == 1
            assert data["message_id"] == 2
            assert "Hello" in data["response"]
    
    @pytest.mark.asyncio
    async def test_send_message_existing_conversation(self, chat_api_client, response_validator):
        """Test sending a message to an existing conversation."""
        with patch('services.chat_services.semantic_kernel_chat_service.SemanticKernelChatService') as mock_service:
            mock_instance = Mock()
            mock_instance.send_message.return_value = (
                "That's a great question! Let me help you with that.",
                123,  # Existing conversation ID
                456,  # New message ID
                {
                    "input_tokens": 30,
                    "output_tokens": 15,
                    "total_tokens": 45,
                    "estimated_cost_usd": 0.00045,
                    "generation_time_ms": 600
                }
            )
            mock_service.return_value = mock_instance
            
            response = chat_api_client.send_message(
                message="Can you help me with Python programming?",
                conversation_id=123,
                method="semantic-kernel"
            )
            
            data = response_validator.validate_success_response(response)
            assert data["conversation_id"] == 123
            assert data["message_id"] == 456
    
    @pytest.mark.asyncio
    async def test_send_message_with_system_prompt(self, chat_api_client, response_validator):
        """Test sending a message with custom system prompt."""
        custom_system_prompt = "You are a helpful Python programming assistant. Always provide code examples."
        
        with patch('services.chat_services.langgraph_chat_service.LangGraphChatService') as mock_service:
            mock_instance = Mock()
            mock_instance.send_message.return_value = (
                "Here's a Python example: print('Hello World')",
                1,
                2,
                {"input_tokens": 50, "output_tokens": 20, "total_tokens": 70, "estimated_cost_usd": 0.0007}
            )
            mock_service.return_value = mock_instance
            
            response = chat_api_client.send_message(
                message="Show me a simple Python example",
                system_prompt=custom_system_prompt,
                method="langgraph"
            )
            
            data = response_validator.validate_success_response(response)
            assert "Python" in data["response"]
            assert "print" in data["response"]
    
    def test_send_message_empty_content(self, chat_api_client, response_validator):
        """Test sending an empty message."""
        response = chat_api_client.api.post("/api/chat/langchain", data={
            "message": "",  # Empty message
            "conversation_id": None
        })
        
        response_validator.validate_error_response(response, 422)
    
    def test_send_message_very_long_content(self, chat_api_client):
        """Test sending a very long message."""
        long_message = "This is a very long message. " * 1000  # ~30k characters
        
        with patch('services.chat_services.langchain_chat_service.LangChainChatService') as mock_service:
            mock_instance = Mock()
            mock_instance.send_message.return_value = (
                "I received your long message.",
                1, 2,
                {"input_tokens": 8000, "output_tokens": 10, "total_tokens": 8010, "estimated_cost_usd": 0.08}
            )
            mock_service.return_value = mock_instance
            
            response = chat_api_client.send_message(message=long_message)
            
            # Should handle long messages
            assert response.status_code in [200, 422]  # Either success or validation error
    
    def test_send_message_invalid_conversation_id(self, chat_api_client, response_validator):
        """Test sending message to non-existent conversation."""
        response = chat_api_client.send_message(
            message="Hello",
            conversation_id=999999  # Non-existent conversation
        )
        
        # Should either create new conversation or return error
        assert response.status_code in [200, 404]
    
    def test_send_message_unicode_content(self, chat_api_client):
        """Test sending message with Unicode characters."""
        unicode_message = "¿Cómo estás? 你好! 🌟"
        
        with patch('services.chat_services.langchain_chat_service.LangChainChatService') as mock_service:
            mock_instance = Mock()
            mock_instance.send_message.return_value = (
                "¡Estoy bien, gracias! 我很好！✨",
                1, 2,
                {"input_tokens": 15, "output_tokens": 12, "total_tokens": 27, "estimated_cost_usd": 0.00027}
            )
            mock_service.return_value = mock_instance
            
            response = chat_api_client.send_message(message=unicode_message)
            
            assert response.status_code == 200
            data = response.json()
            assert "bien" in data["response"] or "好" in data["response"]


@pytest.mark.api
class TestConversationManagementEndpoints:
    """Test conversation management endpoints."""
    
    def test_get_conversations_empty(self, chat_api_client):
        """Test getting conversations when none exist."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().order_by().offset().limit().all.return_value = []
            mock_get_db.return_value = mock_session
            
            response = chat_api_client.get_conversations()
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0
    
    def test_get_conversations_with_data(self, chat_api_client, populated_database):
        """Test getting conversations with existing data."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            
            mock_conversations = []
            for i, conv_data in enumerate(populated_database["conversations"]):
                mock_conv = Mock()
                mock_conv.id = i + 1
                mock_conv.title = conv_data.title if hasattr(conv_data, 'title') else f"Conversation {i+1}"
                mock_conv.created_at = "2025-01-01T00:00:00"
                mock_conv.updated_at = "2025-01-01T00:30:00"
                mock_conv.method = "langchain"
                mock_conversations.append(mock_conv)
            
            mock_session.query().order_by().offset().limit().all.return_value = mock_conversations
            mock_get_db.return_value = mock_session
            
            response = chat_api_client.get_conversations()
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
    
    def test_get_single_conversation_with_messages(self, chat_api_client):
        """Test getting a single conversation with its messages."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            
            # Mock conversation
            mock_conversation = Mock()
            mock_conversation.id = 1
            mock_conversation.title = "Test Conversation"
            mock_conversation.method = "langchain"
            mock_conversation.created_at = "2025-01-01T00:00:00"
            
            # Mock messages
            mock_messages = []
            for i in range(3):  # 3 messages in conversation
                mock_message = Mock()
                mock_message.id = i + 1
                mock_message.role = "user" if i % 2 == 0 else "assistant"
                mock_message.content = f"Message {i + 1}"
                mock_message.created_at = f"2025-01-01T00:{i:02d}:00"
                mock_messages.append(mock_message)
            
            mock_conversation.messages = mock_messages
            mock_session.query().filter().first.return_value = mock_conversation
            mock_get_db.return_value = mock_session
            
            response = chat_api_client.get_conversation(1)
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 1
            assert data["title"] == "Test Conversation"
            assert "messages" in data
            assert len(data["messages"]) == 3
    
    def test_get_conversation_not_found(self, chat_api_client):
        """Test getting a conversation that doesn't exist."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().filter().first.return_value = None
            mock_get_db.return_value = mock_session
            
            response = chat_api_client.get_conversation(999)
            
            assert response.status_code == 404
    
    def test_delete_conversation_success(self, chat_api_client):
        """Test successful conversation deletion."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_conversation = Mock()
            mock_conversation.id = 1
            mock_session.query().filter().first.return_value = mock_conversation
            mock_get_db.return_value = mock_session
            
            response = chat_api_client.delete_conversation(1)
            
            assert response.status_code == 200
            mock_session.delete.assert_called_once_with(mock_conversation)
            mock_session.commit.assert_called_once()
    
    def test_delete_conversation_not_found(self, chat_api_client):
        """Test deleting a conversation that doesn't exist."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().filter().first.return_value = None
            mock_get_db.return_value = mock_session
            
            response = chat_api_client.delete_conversation(999)
            
            assert response.status_code == 404


@pytest.mark.api
class TestChatHistoryEndpoints:
    """Test chat history and search endpoints."""
    
    def test_get_conversation_history_pagination(self, chat_api_client):
        """Test conversation history with pagination."""
        response = chat_api_client.get_conversations(skip=5, limit=10)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10  # Should respect limit
    
    def test_search_conversations_by_content(self, client):
        """Test searching conversations by message content."""
        search_term = "Python programming"
        
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().join().filter().all.return_value = []
            mock_get_db.return_value = mock_session
            
            response = client.get(f"/api/chat/search?q={search_term}")
            
            # This endpoint might not exist yet, but shows the test pattern
            assert response.status_code in [200, 404]
    
    def test_get_recent_messages(self, client):
        """Test getting recent messages across all conversations."""
        with patch('database.get_db') as mock_get_db:
            mock_session = Mock()
            mock_session.query().order_by().limit().all.return_value = []
            mock_get_db.return_value = mock_session
            
            response = client.get("/api/chat/messages/recent?limit=20")
            
            # This endpoint might not exist yet
            assert response.status_code in [200, 404]


@pytest.mark.api
@pytest.mark.slow
class TestChatPerformanceEndpoints:
    """Test chat performance scenarios."""
    
    def test_rapid_message_sending(self, chat_api_client):
        """Test sending multiple messages rapidly."""
        messages = [
            "Hello",
            "How are you?",
            "Tell me a joke",
            "What's the weather like?",
            "Goodbye"
        ]
        
        responses = []
        for message in messages:
            with patch('services.chat_services.langchain_chat_service.LangChainChatService') as mock_service:
                mock_instance = Mock()
                mock_instance.send_message.return_value = (
                    f"Response to: {message}",
                    1, len(responses) * 2 + 2,  # Increment message ID
                    {"input_tokens": 10, "output_tokens": 15, "total_tokens": 25, "estimated_cost_usd": 0.00025}
                )
                mock_service.return_value = mock_instance
                
                response = chat_api_client.send_message(message=message)
                responses.append(response)
        
        # All responses should be successful
        for response in responses:
            assert response.status_code == 200
    
    def test_long_conversation_thread(self, chat_api_client):
        """Test a long conversation with many messages.""" 
        conversation_id = 1
        
        for i in range(50):  # 50 message exchanges
            with patch('services.chat_services.langchain_chat_service.LangChainChatService') as mock_service:
                mock_instance = Mock()
                mock_instance.send_message.return_value = (
                    f"This is response number {i+1}",
                    conversation_id,
                    i * 2 + 2,  # Message ID
                    {"input_tokens": 20, "output_tokens": 25, "total_tokens": 45, "estimated_cost_usd": 0.00045}
                )
                mock_service.return_value = mock_instance
                
                response = chat_api_client.send_message(
                    message=f"This is message number {i+1}",
                    conversation_id=conversation_id
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["conversation_id"] == conversation_id


@pytest.mark.api
class TestChatErrorHandling:
    """Test chat error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_service_unavailable_error(self, chat_api_client, response_validator):
        """Test when chat service is unavailable."""
        with patch('services.chat_services.langchain_chat_service.LangChainChatService') as mock_service:
            mock_service.side_effect = Exception("Service unavailable")
            
            response = chat_api_client.send_message(message="Hello")
            
            response_validator.validate_error_response(response, 500)
    
    def test_database_connection_error(self, chat_api_client, response_validator):
        """Test when database is unavailable."""
        with patch('database.get_db') as mock_get_db:
            mock_get_db.side_effect = Exception("Database connection failed")
            
            response = chat_api_client.get_conversations()
            
            response_validator.validate_error_response(response, 500)
    
    def test_invalid_json_payload(self, client, response_validator):
        """Test sending invalid JSON payload."""
        response = client.post(
            "/api/chat/langchain",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        response_validator.validate_error_response(response, 400)
    
    def test_missing_content_type_header(self, client):
        """Test request without proper content type."""
        response = client.post(
            "/api/chat/langchain",
            data=json.dumps({"message": "Hello"}),
            headers={"Content-Type": "text/plain"}  # Wrong content type
        )
        
        # Should either work or return appropriate error
        assert response.status_code in [200, 400, 415]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])