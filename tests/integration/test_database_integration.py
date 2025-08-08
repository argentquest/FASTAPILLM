"""
Integration tests for database operations and data consistency.

Tests database integration across all models and services with real database operations.
"""

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from decimal import Decimal
import tempfile
import os


@pytest.mark.integration
class TestDatabaseModelIntegration:
    """Test database model integration and relationships."""
    
    def test_story_model_crud_operations(self, integration_db):
        """Test Story model CRUD operations with real database."""
        with integration_db() as db:
            # Create
            story = Story(
                primary_character="Alice",
                secondary_character="Bob",
                combined_characters="Alice and Bob",
                story_content="Once upon a time...",
                method="langchain",
                generation_time_ms=1500.0,
                input_tokens=100,
                output_tokens=50,
                total_tokens=150,
                request_id="test_crud_001",
                transaction_guid="12345678-1234-5678-9abc-123456789012",
                provider="openrouter",
                model="llama-3-8b",
                estimated_cost_usd=Decimal('0.0015'),
                input_cost_per_1k_tokens=Decimal('0.001'),
                output_cost_per_1k_tokens=Decimal('0.002')
            )
            
            db.add(story)
            db.commit()
            
            # Verify creation
            assert story.id is not None
            assert story.created_at is not None
            
            story_id = story.id
        
        # Read in new session
        with integration_db() as db:
            retrieved_story = db.query(Story).filter_by(id=story_id).first()
            
            assert retrieved_story is not None
            assert retrieved_story.primary_character == "Alice"
            assert retrieved_story.secondary_character == "Bob"
            assert retrieved_story.story_content == "Once upon a time..."
            assert retrieved_story.method == "langchain"
            assert retrieved_story.total_tokens == 150
            assert retrieved_story.estimated_cost_usd == Decimal('0.0015')
            assert retrieved_story.provider == "openrouter"
            assert retrieved_story.model == "llama-3-8b"
            
            # Update
            retrieved_story.story_content = "Updated story content..."
            retrieved_story.generation_time_ms = 2000.0
            db.commit()
        
        # Verify update in new session
        with integration_db() as db:
            updated_story = db.query(Story).filter_by(id=story_id).first()
            assert updated_story.story_content == "Updated story content..."
            assert updated_story.generation_time_ms == 2000.0
            
            # Delete
            db.delete(updated_story)
            db.commit()
        
        # Verify deletion
        with integration_db() as db:
            deleted_story = db.query(Story).filter_by(id=story_id).first()
            assert deleted_story is None
    
    def test_chat_conversation_and_messages_relationship(self, integration_db):
        """Test ChatConversation and ChatMessage relationship."""
        with integration_db() as db:
            # Create conversation
            conversation = ChatConversation(
                title="Test Integration Conversation",
                method="langchain",
                provider="openrouter",
                model="llama-3-8b",
                transaction_guid="conv-12345678-1234-5678-9abc-123456789012"
            )
            
            db.add(conversation)
            db.flush()  # Get ID without committing
            
            conv_id = conversation.id
            
            # Create messages
            messages_data = [
                ("user", "Hello, how are you?"),
                ("assistant", "I'm doing well, thank you for asking!"),
                ("user", "Can you help me with something?"),
                ("assistant", "Of course! What do you need help with?")
            ]
            
            created_messages = []
            for i, (role, content) in enumerate(messages_data):
                message = ChatMessage(
                    conversation_id=conv_id,
                    role=role,
                    content=content,
                    generation_time_ms=500.0 if role == "assistant" else None,
                    input_tokens=len(content.split()) * 2,  # Rough estimate
                    output_tokens=len(content.split()) * 2 if role == "assistant" else 0,
                    total_tokens=len(content.split()) * 2,
                    request_id=f"chat_msg_{i:03d}",
                    transaction_guid=f"msg-{i:03d}-12345678-1234-5678-9abc-123456789012",
                    estimated_cost_usd=Decimal('0.0001') if role == "assistant" else Decimal('0.00005')
                )
                
                db.add(message)
                created_messages.append(message)
            
            db.commit()
        
        # Test relationship in new session
        with integration_db() as db:
            # Load conversation with messages via relationship
            conversation = db.query(ChatConversation).filter_by(id=conv_id).first()
            
            assert conversation is not None
            assert len(conversation.messages) == 4
            
            # Verify message order and content
            messages = sorted(conversation.messages, key=lambda m: m.id)
            assert messages[0].role == "user"
            assert messages[0].content == "Hello, how are you?"
            assert messages[1].role == "assistant"
            assert messages[1].content == "I'm doing well, thank you for asking!"
            
            # Test back reference
            for message in messages:
                assert message.conversation.id == conv_id
                assert message.conversation.title == "Test Integration Conversation"
            
            # Test cascade delete
            db.delete(conversation)
            db.commit()
        
        # Verify cascade deletion
        with integration_db() as db:
            remaining_messages = db.query(ChatMessage).filter_by(conversation_id=conv_id).all()
            assert len(remaining_messages) == 0
    
    def test_context_prompt_execution_model(self, integration_db):
        """Test ContextPromptExecution model with real database operations."""
        with integration_db() as db:
            execution = ContextPromptExecution(
                original_filename="test_document.pdf",
                file_type="pdf",
                file_size_bytes=1024*50,  # 50KB
                processed_content_length=800,
                system_prompt="Analyze this document: [context]",
                user_prompt="What are the main topics discussed?",
                final_prompt_length=850,
                llm_response="The document discusses project architecture, database design, and API implementation.",
                method="langchain",
                provider="openrouter",
                model="llama-3-8b",
                file_processing_time_ms=200.0,
                llm_execution_time_ms=1800.0,
                total_execution_time_ms=2000.0,
                input_tokens=200,
                output_tokens=75,
                total_tokens=275,
                estimated_cost_usd=Decimal('0.00275'),
                input_cost_per_1k_tokens=Decimal('0.001'),
                output_cost_per_1k_tokens=Decimal('0.002'),
                request_id="context_integration_001",
                transaction_guid="ctx-12345678-1234-5678-9abc-123456789012",
                user_ip="192.168.1.100",
                status="completed"
            )
            
            db.add(execution)
            db.commit()
            
            exec_id = execution.id
        
        # Verify in new session
        with integration_db() as db:
            retrieved = db.query(ContextPromptExecution).filter_by(id=exec_id).first()
            
            assert retrieved is not None
            assert retrieved.original_filename == "test_document.pdf"
            assert retrieved.file_type == "pdf"
            assert retrieved.file_size_bytes == 1024*50
            assert retrieved.method == "langchain"
            assert retrieved.status == "completed"
            assert retrieved.total_tokens == 275
            assert retrieved.estimated_cost_usd == Decimal('0.00275')
            assert retrieved.total_execution_time_ms == 2000.0


@pytest.mark.integration
class TestDatabaseTransactionIntegration:
    """Test database transaction handling and consistency."""
    
    def test_transaction_rollback_on_error(self, integration_db):
        """Test transaction rollback when errors occur."""
        initial_count = 0
        
        # Get initial story count
        with integration_db() as db:
            initial_count = db.query(Story).count()
        
        # Attempt transaction that should fail
        try:
            with integration_db() as db:
                # Add valid story
                story1 = Story(
                    primary_character="Valid",
                    secondary_character="Character",
                    combined_characters="Valid and Character",
                    story_content="Valid story",
                    method="langchain"
                )
                db.add(story1)
                
                # Add invalid story (this should cause a constraint violation)
                story2 = Story(
                    primary_character=None,  # This should violate NOT NULL constraint
                    secondary_character="Invalid",
                    combined_characters="Invalid story",
                    story_content="This should fail",
                    method="langchain"
                )
                db.add(story2)
                
                # Force flush to trigger constraint check
                db.flush()
        except Exception:
            pass  # Expected to fail
        
        # Verify rollback - count should be unchanged
        with integration_db() as db:
            final_count = db.query(Story).count()
            assert final_count == initial_count
    
    def test_concurrent_database_access(self, integration_db):
        """Test concurrent database access scenarios."""
        import threading
        import time
        
        results = []
        errors = []
        
        def create_story(thread_id):
            try:
                with integration_db() as db:
                    story = Story(
                        primary_character=f"Thread{thread_id}",
                        secondary_character="Character",
                        combined_characters=f"Thread{thread_id} and Character",
                        story_content=f"Story from thread {thread_id}",
                        method="langchain",
                        request_id=f"concurrent_{thread_id:03d}"
                    )
                    db.add(story)
                    
                    # Simulate some processing time
                    time.sleep(0.1)
                    
                    db.commit()
                    results.append(story.id)
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")
        
        # Create multiple threads
        threads = []
        num_threads = 5
        
        for i in range(num_threads):
            thread = threading.Thread(target=create_story, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert len(results) == num_threads
        
        # Verify all stories were created
        with integration_db() as db:
            concurrent_stories = db.query(Story).filter(Story.request_id.like("concurrent_%")).all()
            assert len(concurrent_stories) == num_threads
    
    def test_database_connection_pooling(self, integration_db):
        """Test database connection pooling behavior."""
        session_ids = []
        
        # Create multiple sessions rapidly
        for i in range(10):
            with integration_db() as db:
                # Get connection info (this is database-specific)
                result = db.execute(text("SELECT 1 as test_connection")).first()
                assert result.test_connection == 1
                session_ids.append(id(db))
        
        # Verify sessions were created and cleaned up properly
        assert len(session_ids) == 10
        # Session objects should be different (not reused inappropriately)
        assert len(set(session_ids)) == 10


@pytest.mark.integration 
class TestDatabaseMigrationIntegration:
    """Test database schema migrations and compatibility."""
    
    def test_database_schema_matches_models(self, integration_db):
        """Test that database schema matches SQLAlchemy model definitions."""
        with integration_db() as db:
            # Test Story table structure
            story_columns = db.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'stories'
                ORDER BY column_name
            """)).fetchall() if hasattr(db.bind.dialect, 'name') and db.bind.dialect.name == 'postgresql' else []
            
            # For SQLite, use a different approach
            if not story_columns:
                story_columns = db.execute(text("PRAGMA table_info(stories)")).fetchall()
            
            # Should have some columns
            assert len(story_columns) > 0
            
            # Test basic table existence
            story_count = db.execute(text("SELECT COUNT(*) FROM stories")).scalar()
            assert isinstance(story_count, int)
            
            chat_conv_count = db.execute(text("SELECT COUNT(*) FROM chat_conversations")).scalar()
            assert isinstance(chat_conv_count, int)
            
            chat_msg_count = db.execute(text("SELECT COUNT(*) FROM chat_messages")).scalar()  
            assert isinstance(chat_msg_count, int)
            
            context_count = db.execute(text("SELECT COUNT(*) FROM context_prompt_executions")).scalar()
            assert isinstance(context_count, int)
    
    def test_model_constraints_and_indexes(self, integration_db):
        """Test database constraints and indexes work correctly."""
        with integration_db() as db:
            # Test unique constraints and indexes
            # This is more of a smoke test to ensure constraints are working
            
            # Create story with specific transaction_guid
            guid = "test-guid-12345678-1234-5678-9abc-123456789012"
            story = Story(
                primary_character="Test",
                secondary_character="Character", 
                combined_characters="Test and Character",
                story_content="Test story",
                method="test",
                transaction_guid=guid
            )
            db.add(story)
            db.commit()
            
            # Verify the record was created with the GUID index
            retrieved = db.query(Story).filter_by(transaction_guid=guid).first()
            assert retrieved is not None
            assert retrieved.transaction_guid == guid


@pytest.mark.integration
class TestDatabasePerformanceIntegration:
    """Test database performance characteristics."""
    
    def test_bulk_insert_performance(self, integration_db):
        """Test bulk insert operations performance."""
        import time
        
        num_records = 100
        stories = []
        
        for i in range(num_records):
            story = Story(
                primary_character=f"Hero{i:03d}",
                secondary_character=f"Companion{i:03d}",
                combined_characters=f"Hero{i:03d} and Companion{i:03d}",
                story_content=f"This is story number {i} with some content to make it realistic.",
                method="langchain" if i % 2 == 0 else "semantic-kernel",
                input_tokens=100 + i,
                output_tokens=50 + i//2,
                total_tokens=150 + i + i//2,
                estimated_cost_usd=Decimal(str(0.001 + i * 0.00001)),
                request_id=f"bulk_{i:05d}"
            )
            stories.append(story)
        
        # Measure bulk insert time
        start_time = time.time()
        
        with integration_db() as db:
            db.add_all(stories)
            db.commit()
        
        insert_time = time.time() - start_time
        
        # Performance assertion - should insert 100 records reasonably quickly
        assert insert_time < 5.0, f"Bulk insert took too long: {insert_time:.2f}s"
        
        # Verify all records were inserted
        with integration_db() as db:
            bulk_count = db.query(Story).filter(Story.request_id.like("bulk_%")).count()
            assert bulk_count == num_records
    
    def test_query_performance_with_indexes(self, integration_db):
        """Test query performance with indexed columns."""
        import time
        
        # Insert test data first
        with integration_db() as db:
            stories = []
            for i in range(50):
                story = Story(
                    primary_character=f"QueryHero{i:03d}",
                    secondary_character=f"QueryCompanion{i:03d}",
                    combined_characters=f"QueryHero{i:03d} and QueryCompanion{i:03d}",
                    story_content=f"Query test story {i}",
                    method="langchain",
                    transaction_guid=f"query-test-{i:03d}-1234-5678-9abc-123456789012",
                    request_id=f"query_test_{i:05d}"
                )
                stories.append(story)
            
            db.add_all(stories)
            db.commit()
        
        # Test indexed query performance
        start_time = time.time()
        
        with integration_db() as db:
            # Query by transaction_guid (indexed)
            results = db.query(Story).filter(Story.transaction_guid.like("query-test-%")).all()
            
        query_time = time.time() - start_time
        
        # Should be fast with index
        assert query_time < 1.0, f"Indexed query took too long: {query_time:.2f}s"
        assert len(results) == 50
    
    def test_database_cleanup_and_maintenance(self, integration_db):
        """Test database cleanup operations."""
        # Create some test data
        with integration_db() as db:
            # Add stories with old dates
            old_date = datetime.now() - timedelta(days=365)
            
            for i in range(10):
                story = Story(
                    primary_character=f"OldHero{i}",
                    secondary_character=f"OldCompanion{i}",
                    combined_characters=f"OldHero{i} and OldCompanion{i}",
                    story_content=f"Old story {i}",
                    method="langchain",
                    request_id=f"old_story_{i:03d}",
                    created_at=old_date
                )
                db.add(story)
            
            db.commit()
        
        # Test cleanup operation
        with integration_db() as db:
            initial_count = db.query(Story).filter(Story.request_id.like("old_story_%")).count()
            assert initial_count == 10
            
            # Simulate cleanup (delete old records)
            deleted_count = db.query(Story).filter(
                Story.request_id.like("old_story_%"),
                Story.created_at < datetime.now() - timedelta(days=30)
            ).delete(synchronize_session=False)
            
            db.commit()
            
            assert deleted_count == 10
            
            final_count = db.query(Story).filter(Story.request_id.like("old_story_%")).count()
            assert final_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])