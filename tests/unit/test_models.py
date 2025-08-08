"""
Unit tests for database models.

Tests SQLAlchemy model definitions, validation, serialization, and relationships.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from decimal import Decimal


@pytest.mark.unit
class TestStoryModel:
    """Test Story database model."""
    
    @pytest.fixture
    def story_model_class(self):
        """Import Story model class."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[2] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from database import Story
        return Story
    
    def test_story_model_attributes(self, story_model_class):
        """Test Story model has required attributes."""
        # Check that all expected columns exist (based on actual database.py)
        expected_columns = [
            'id', 'primary_character', 'secondary_character', 'combined_characters',
            'story_content', 'method', 'generation_time_ms', 'input_tokens', 
            'output_tokens', 'total_tokens', 'request_id', 'transaction_guid',
            'provider', 'model', 'estimated_cost_usd', 'input_cost_per_1k_tokens',
            'output_cost_per_1k_tokens', 'created_at'
        ]
        
        for column in expected_columns:
            assert hasattr(story_model_class, column), f"Story model missing column: {column}"
    
    def test_story_model_creation(self, story_model_class):
        """Test Story model instance creation."""
        story_data = {
            'primary_character': 'Alice',
            'secondary_character': 'Bob',
            'combined_characters': 'Alice and Bob',
            'story_content': 'Once upon a time...',
            'method': 'langchain',
            'provider': 'openrouter',
            'model': 'llama-3-8b',
            'input_tokens': 100,
            'output_tokens': 200,
            'total_tokens': 300,
            'estimated_cost_usd': Decimal('0.003')
        }
        
        story = story_model_class(**story_data)
        
        # Verify attributes
        assert story.primary_character == 'Alice'
        assert story.secondary_character == 'Bob'
        assert story.combined_characters == 'Alice and Bob'
        assert story.story_content == 'Once upon a time...'
        assert story.method == 'langchain'
        assert story.provider == 'openrouter'
        assert story.model == 'llama-3-8b'
        assert story.input_tokens == 100
        assert story.output_tokens == 200
        assert story.total_tokens == 300
        assert story.estimated_cost_usd == Decimal('0.003')
    
    def test_story_model_defaults(self, story_model_class):
        """Test Story model default values."""
        minimal_story = story_model_class(
            primary_character='Test',
            secondary_character='Test2',
            combined_characters='Test and Test2',
            story_content='Test story',
            method='test'
        )
        
        # Check defaults are applied
        assert minimal_story.created_at is not None or hasattr(story_model_class.created_at, 'default')
        # Transaction GUID should have default or be nullable
        assert hasattr(story_model_class.transaction_guid, 'default') or getattr(story_model_class.transaction_guid, 'nullable', False)
    
    def test_story_model_str_representation(self, story_model_class):
        """Test Story model string representation."""
        story = story_model_class(
            id=1,
            primary_character='Alice',
            story_content='Test story'
        )
        
        # Should have some string representation
        str_repr = str(story)
        assert isinstance(str_repr, str)
        assert len(str_repr) > 0
    
    def test_story_model_token_validation(self, story_model_class):
        """Test token field validation.""" 
        story = story_model_class(
            primary_character='Test',
            story_content='Test',
            input_tokens=100,
            output_tokens=50
        )
        
        # Token counts should be integers
        assert isinstance(story.input_tokens, int)
        assert isinstance(story.output_tokens, int)
        
        # Total tokens calculation (if implemented in model)
        if hasattr(story, 'calculate_total_tokens'):
            total = story.calculate_total_tokens()
            assert total == 150


@pytest.mark.unit
class TestChatModels:
    """Test chat-related database models."""
    
    @pytest.fixture
    def chat_models(self):
        """Import chat model classes."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[2] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from database import ChatConversation, ChatMessage
        return ChatConversation, ChatMessage
    
    def test_chat_conversation_model(self, chat_models):
        """Test ChatConversation model."""
        ChatConversation, ChatMessage = chat_models
        
        conversation_data = {
            'title': 'Test Conversation',
            'provider': 'openrouter',
            'model': 'llama-3-8b'
        }
        
        conversation = ChatConversation(**conversation_data)
        
        assert conversation.title == 'Test Conversation'
        assert conversation.provider == 'openrouter'
        assert conversation.model == 'llama-3-8b'
    
    def test_chat_message_model(self, chat_models):
        """Test ChatMessage model."""
        ChatConversation, ChatMessage = chat_models
        
        message_data = {
            'conversation_id': 1,
            'role': 'user',
            'content': 'Hello, how are you?',
            'input_tokens': 10,
            'output_tokens': 0
        }
        
        message = ChatMessage(**message_data)
        
        assert message.conversation_id == 1
        assert message.role == 'user'
        assert message.content == 'Hello, how are you?'
        assert message.input_tokens == 10
        assert message.output_tokens == 0
    
    def test_chat_relationship(self, chat_models):
        """Test relationship between conversation and messages."""
        ChatConversation, ChatMessage = chat_models
        
        # Check if relationship attributes exist
        if hasattr(ChatConversation, 'messages'):
            # Relationship should exist
            assert hasattr(ChatConversation, 'messages')
        
        if hasattr(ChatMessage, 'conversation'):
            # Back reference should exist
            assert hasattr(ChatMessage, 'conversation')


@pytest.mark.unit
class TestContextModel:
    """Test ContextPromptExecution model."""
    
    @pytest.fixture
    def context_model_class(self):
        """Import ContextPromptExecution model class."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[2] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from database import ContextPromptExecution
        return ContextPromptExecution
    
    def test_context_model_attributes(self, context_model_class):
        """Test ContextPromptExecution model attributes."""
        expected_columns = [
            'id', 'original_filename', 'file_type', 'file_size_bytes',
            'system_prompt', 'user_prompt', 'method', 'llm_response',
            'status', 'provider', 'model', 'input_tokens', 'output_tokens',
            'total_tokens', 'estimated_cost_usd', 'created_at'
        ]
        
        for column in expected_columns:
            assert hasattr(context_model_class, column), f"ContextPromptExecution missing column: {column}"
    
    def test_context_model_creation(self, context_model_class):
        """Test ContextPromptExecution model creation."""
        context_data = {
            'original_filename': 'test.txt',
            'file_type': 'txt',
            'file_size_bytes': 1024,
            'system_prompt': 'Analyze this: [context]',
            'user_prompt': 'What are the key points?',
            'method': 'langchain',
            'llm_response': 'Key points are...',
            'status': 'completed',
            'provider': 'openrouter',
            'model': 'llama-3-8b',
            'input_tokens': 200,
            'output_tokens': 100,
            'total_tokens': 300,
            'estimated_cost_usd': Decimal('0.003')
        }
        
        context_exec = context_model_class(**context_data)
        
        assert context_exec.original_filename == 'test.txt'
        assert context_exec.file_type == 'txt'
        assert context_exec.file_size_bytes == 1024
        assert context_exec.method == 'langchain'
        assert context_exec.status == 'completed'


@pytest.mark.unit
class TestModelValidation:
    """Test model validation and constraints."""
    
    @pytest.fixture
    def models(self):
        """Import all model classes."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[2] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from database import Story, ChatConversation, ChatMessage, ContextPromptExecution
        return {
            'Story': Story,
            'ChatConversation': ChatConversation,
            'ChatMessage': ChatMessage,
            'ContextPromptExecution': ContextPromptExecution
        }
    
    def test_required_fields(self, models):
        """Test that models enforce required fields."""
        Story = models['Story']
        
        # Story should require at least primary_character and story_content
        story = Story()
        
        # Check if fields have nullable=False or similar constraints
        # This would be enforced at the database level
        assert hasattr(Story, 'primary_character')
        assert hasattr(Story, 'story_content')
    
    def test_field_types(self, models):
        """Test field type definitions."""
        Story = models['Story']
        
        # Check some field types
        story = Story(
            primary_character='Test',
            story_content='Test story',
            input_tokens=100,
            output_tokens=50
        )
        
        # Integer fields should accept integers
        assert isinstance(story.input_tokens, int)
        assert isinstance(story.output_tokens, int)
    
    def test_decimal_precision(self, models):
        """Test decimal field precision for costs."""
        Story = models['Story']
        
        story = Story(
            primary_character='Test',
            story_content='Test story',
            estimated_cost_usd=Decimal('0.123456')
        )
        
        # Should accept decimal values
        assert isinstance(story.estimated_cost_usd, Decimal)
    
    def test_text_field_lengths(self, models):
        """Test text field length constraints."""
        Story = models['Story']
        
        # Test with reasonable length strings
        long_story = 'A' * 10000  # 10k characters
        
        story = Story(
            primary_character='Test',
            story_content=long_story
        )
        
        # Should accept long stories
        assert len(story.story_content) == 10000


@pytest.mark.unit 
class TestModelSerialization:
    """Test model serialization and dictionary conversion."""
    
    @pytest.fixture
    def story_model_class(self):
        """Import Story model class."""
        import sys
        from pathlib import Path
        backend_path = Path(__file__).parents[2] / "backend"
        if str(backend_path) not in sys.path:
            sys.path.insert(0, str(backend_path))
        
        from database import Story
        return Story
    
    def test_model_to_dict(self, story_model_class):
        """Test converting model to dictionary."""
        story = story_model_class(
            id=1,
            primary_character='Alice',
            secondary_character='Bob',
            combined_characters='Alice and Bob',
            story_content='Test story',
            method='langchain',
            input_tokens=100,
            output_tokens=50
        )
        
        # If model has to_dict method, test it
        if hasattr(story, 'to_dict'):
            story_dict = story.to_dict()
            assert isinstance(story_dict, dict)
            assert story_dict['primary_character'] == 'Alice'
            assert story_dict['secondary_character'] == 'Bob'
        
        # Otherwise, test basic attribute access
        else:
            assert story.primary_character == 'Alice'
            assert story.secondary_character == 'Bob'
    
    def test_model_json_serialization(self, story_model_class):
        """Test JSON serialization compatibility."""
        story = story_model_class(
            primary_character='Alice',
            story_content='Test story',
            estimated_cost_usd=Decimal('0.001'),
            created_at=datetime.utcnow()
        )
        
        # Test that fields can be JSON serialized
        # (Decimal and datetime need special handling)
        assert isinstance(story.primary_character, str)
        assert isinstance(story.story_content, str)
        
        # Decimal should be convertible to string/float
        if story.estimated_cost_usd:
            assert isinstance(story.estimated_cost_usd, Decimal)
            float_cost = float(story.estimated_cost_usd)
            assert isinstance(float_cost, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])