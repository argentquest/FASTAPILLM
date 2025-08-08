"""
Database Test Fixtures

Provides database-related fixtures for testing ORM models and database operations.
"""

import pytest
from datetime import datetime
from typing import Generator, List
from sqlalchemy.orm import Session


@pytest.fixture
def story_factory(db_session: Session):
    """Factory for creating story records in the database."""
    def _create_story(
        primary_character: str = "Test Character",
        secondary_character: str = "Test Secondary",
        setting: str = "Test Setting",
        genre: str = "Test Genre",
        tone: str = "Test Tone",
        length: str = "medium",
        generated_story: str = "This is a test story.",
        provider: str = "test_provider",
        model: str = "test-model",
        input_tokens: int = 100,
        output_tokens: int = 50,
        **kwargs
    ):
        from backend.database import Story
        
        story = Story(
            primary_character=primary_character,
            secondary_character=secondary_character,
            setting=setting,
            genre=genre,
            tone=tone,
            length=length,
            generated_story=generated_story,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            estimated_cost_usd=0.001 * (input_tokens + output_tokens) / 1000,
            **kwargs
        )
        
        db_session.add(story)
        db_session.commit()
        db_session.refresh(story)
        return story
    
    return _create_story


@pytest.fixture
def chat_conversation_factory(db_session: Session):
    """Factory for creating chat conversation records."""
    def _create_conversation(
        title: str = "Test Conversation",
        provider: str = "test_provider", 
        model: str = "test-model",
        **kwargs
    ):
        from backend.database import ChatConversation
        
        conversation = ChatConversation(
            title=title,
            provider=provider,
            model=model,
            **kwargs
        )
        
        db_session.add(conversation)
        db_session.commit() 
        db_session.refresh(conversation)
        return conversation
    
    return _create_conversation


@pytest.fixture
def chat_message_factory(db_session: Session):
    """Factory for creating chat message records."""
    def _create_message(
        conversation_id: int,
        role: str = "user",
        content: str = "Test message",
        input_tokens: int = 10,
        output_tokens: int = 0,
        **kwargs
    ):
        from backend.database import ChatMessage
        
        message = ChatMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            **kwargs
        )
        
        db_session.add(message)
        db_session.commit()
        db_session.refresh(message)
        return message
    
    return _create_message


@pytest.fixture
def context_execution_factory(db_session: Session):
    """Factory for creating context prompt execution records.""" 
    def _create_execution(
        original_filename: str = "test.txt",
        file_type: str = "txt",
        file_size_bytes: int = 1024,
        system_prompt: str = "Test system prompt with [context]",
        user_prompt: str = "Test user prompt",
        method: str = "langchain",
        llm_response: str = "Test response",
        status: str = "completed",
        **kwargs
    ):
        from backend.database import ContextPromptExecution
        
        execution = ContextPromptExecution(
            original_filename=original_filename,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            method=method,
            llm_response=llm_response,
            status=status,
            provider="test_provider",
            model="test-model",
            input_tokens=100,
            output_tokens=50,
            total_tokens=150,
            estimated_cost_usd=0.0015,
            **kwargs
        )
        
        db_session.add(execution)
        db_session.commit()
        db_session.refresh(execution)
        return execution
    
    return _create_execution


@pytest.fixture
def populated_database(
    db_session: Session,
    story_factory,
    chat_conversation_factory,
    chat_message_factory,
    context_execution_factory
):
    """Create a database populated with sample data for testing."""
    # Create stories
    story1 = story_factory(
        primary_character="Alice",
        secondary_character="Bob", 
        setting="Forest",
        genre="Adventure"
    )
    story2 = story_factory(
        primary_character="Charlie",
        setting="Space Station",
        genre="Sci-Fi"
    )
    
    # Create chat conversation with messages
    conversation = chat_conversation_factory(title="Test Chat")
    message1 = chat_message_factory(
        conversation_id=conversation.id,
        role="user",
        content="Hello"
    )
    message2 = chat_message_factory(
        conversation_id=conversation.id,
        role="assistant", 
        content="Hello! How can I help you?"
    )
    
    # Create context execution
    execution = context_execution_factory(
        original_filename="sample.txt",
        method="langchain"
    )
    
    return {
        "stories": [story1, story2],
        "conversations": [conversation],
        "messages": [message1, message2],
        "executions": [execution]
    }


@pytest.fixture
def clean_database(db_session: Session):
    """Ensure database is clean before test."""
    from backend.database import Story, ChatConversation, ChatMessage, ContextPromptExecution
    
    # Clean up any existing data
    db_session.query(ChatMessage).delete()
    db_session.query(ChatConversation).delete()
    db_session.query(Story).delete()
    db_session.query(ContextPromptExecution).delete()
    db_session.commit()
    
    yield db_session
    
    # Clean up after test
    db_session.query(ChatMessage).delete()
    db_session.query(ChatConversation).delete() 
    db_session.query(Story).delete()
    db_session.query(ContextPromptExecution).delete()
    db_session.commit()


@pytest.fixture
def database_transaction_test():
    """Test database transactions and rollbacks."""
    def _test_transaction(db_session: Session, model_class, test_data: dict):
        """Test transaction behavior with a model."""
        # Start transaction
        initial_count = db_session.query(model_class).count()
        
        try:
            # Create record
            record = model_class(**test_data)
            db_session.add(record)
            db_session.flush()  # Don't commit yet
            
            # Verify record exists in transaction
            assert db_session.query(model_class).count() == initial_count + 1
            
            # Simulate error and rollback
            raise Exception("Test rollback")
            
        except Exception:
            db_session.rollback()
            
            # Verify rollback worked
            assert db_session.query(model_class).count() == initial_count
    
    return _test_transaction