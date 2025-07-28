from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from typing import Generator
import os
import time
from contextlib import contextmanager

from config import settings
from logging_config import get_logger

logger = get_logger(__name__)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./stories.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    echo=settings.debug_mode
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Database models
class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    primary_character = Column(String(100), nullable=False)
    secondary_character = Column(String(100), nullable=False)
    combined_characters = Column(String(200), nullable=False)
    story_content = Column(Text, nullable=False)
    method = Column(String(50), nullable=False)  # semantic_kernel, langchain, langgraph
    generation_time_ms = Column(Float)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)
    request_id = Column(String(50))
    provider = Column(String(50))  # azure, openrouter, custom
    model = Column(String(100))
    
    # Cost tracking fields
    estimated_cost_usd = Column(Numeric(precision=10, scale=6), nullable=True, comment="Estimated cost in USD for this request")
    input_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True, comment="Cost per 1000 input tokens used for calculation")
    output_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True, comment="Cost per 1000 output tokens used for calculation")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    method = Column(String(50), nullable=False)  # semantic_kernel, langchain, langgraph
    provider = Column(String(50))
    model = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    generation_time_ms = Column(Float)
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    total_tokens = Column(Integer)
    request_id = Column(String(50))
    
    # Cost tracking fields
    estimated_cost_usd = Column(Numeric(precision=10, scale=6), nullable=True, comment="Estimated cost in USD for this message")
    input_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True, comment="Cost per 1000 input tokens used for calculation")
    output_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True, comment="Cost per 1000 output tokens used for calculation")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to conversation
    conversation = relationship("ChatConversation", back_populates="messages")

class ContextPromptExecution(Base):
    __tablename__ = "context_prompt_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # File information
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    processed_content_length = Column(Integer, nullable=True)
    
    # Prompt information
    system_prompt = Column(Text, nullable=False)
    user_prompt = Column(Text, nullable=False)
    final_prompt_length = Column(Integer, nullable=True)
    
    # LLM response
    llm_response = Column(Text, nullable=True)
    method = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    
    # Performance metrics
    file_processing_time_ms = Column(Float, nullable=True)
    llm_execution_time_ms = Column(Float, nullable=True)
    total_execution_time_ms = Column(Float, nullable=True)
    
    # Token usage
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    
    # Cost tracking
    estimated_cost_usd = Column(Numeric(precision=10, scale=6), nullable=True)
    input_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True)
    output_cost_per_1k_tokens = Column(Numeric(precision=8, scale=6), nullable=True)
    
    # Request tracking
    request_id = Column(String(50), nullable=True)
    user_ip = Column(String(45), nullable=True)
    
    # Status tracking
    status = Column(String(20), nullable=False, default='completed')
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

# Dependency to get DB session
def get_db() -> Generator:
    """Get database session for dependency injection.
    
    This function is used by FastAPI's dependency injection system to
    provide database sessions to route handlers. It ensures proper
    session lifecycle management with automatic cleanup.
    
    Yields:
        Session: A SQLAlchemy database session.
        
    Raises:
        Any exceptions raised during database operations are logged
        and re-raised.
        
    Examples:
        >>> @app.get("/items")
        ... def get_items(db: Session = Depends(get_db)):
        ...     return db.query(Item).all()
    """
    logger.debug("Creating database session for dependency injection")
    db = SessionLocal()
    try:
        yield db
        logger.debug("Database session yielded successfully")
    except Exception as e:
        logger.error("Database session error in dependency", 
                    error=str(e), 
                    error_type=type(e).__name__)
        raise
    finally:
        db.close()
        logger.debug("Database session closed")

@contextmanager
def get_db_context():
    """Context manager for database sessions.
    
    Provides a database session with automatic transaction management,
    including commit on success and rollback on failure. Includes
    comprehensive logging of transaction details.
    
    Yields:
        Session: A SQLAlchemy database session with transaction support.
        
    Raises:
        Any exceptions raised during the context are logged, the
        transaction is rolled back, and the exception is re-raised.
        
    Examples:
        >>> with get_db_context() as db:
        ...     new_story = Story(primary_character="Alice")
        ...     db.add(new_story)
        ...     # Automatically committed on exit
        
        >>> with get_db_context() as db:
        ...     db.query(Story).filter_by(id=1).delete()
        ...     raise ValueError("Oops")
        ...     # Transaction rolled back due to exception
    """
    transaction_id = id(object())  # Simple transaction ID for logging
    logger.debug("Creating database transaction session", transaction_id=transaction_id)
    
    db = SessionLocal()
    start_time = time.time()
    
    try:
        yield db
        
        # Log transaction details before commit
        session_info = {
            "new_objects": len(db.new),
            "dirty_objects": len(db.dirty),
            "deleted_objects": len(db.deleted)
        }
        
        if session_info["new_objects"] > 0 or session_info["dirty_objects"] > 0 or session_info["deleted_objects"] > 0:
            logger.info("Committing database transaction", 
                       transaction_id=transaction_id,
                       **session_info)
        
        db.commit()
        transaction_time = (time.time() - start_time) * 1000
        
        logger.info("Database transaction committed successfully", 
                   transaction_id=transaction_id,
                   transaction_time_ms=round(transaction_time, 2),
                   **session_info)
                   
    except Exception as e:
        transaction_time = (time.time() - start_time) * 1000
        logger.error("Database transaction failed, rolling back", 
                    transaction_id=transaction_id,
                    error=str(e), 
                    error_type=type(e).__name__,
                    transaction_time_ms=round(transaction_time, 2))
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database transaction session closed", transaction_id=transaction_id)

def init_db():
    """Initialize database using Alembic migrations.
    
    Attempts to run Alembic migrations to set up the database schema.
    If Alembic fails (e.g., in development), falls back to using
    SQLAlchemy's create_all method.
    
    The function logs detailed information about the initialization
    process including timing and any errors encountered.
    
    Raises:
        Exception: If both Alembic migrations and the fallback
            create_all method fail.
            
    Examples:
        >>> init_db()  # Run during application startup
    """
    db_path = DATABASE_URL.split("///")[-1] if "///" in DATABASE_URL else DATABASE_URL
    logger.info("Starting database initialization", 
               database_url=db_path,
               database_provider="sqlite" if DATABASE_URL.startswith("sqlite") else "other")
    
    start_time = time.time()
    
    try:
        from alembic.config import Config
        from alembic import command
        
        logger.debug("Loading Alembic configuration")
        alembic_cfg = Config("alembic.ini")
        
        logger.info("Running database migrations")
        command.upgrade(alembic_cfg, "head")
        
        initialization_time = (time.time() - start_time) * 1000
        logger.info("Database migrations completed successfully", 
                   database_url=db_path,
                   initialization_time_ms=round(initialization_time, 2))
                   
    except Exception as e:
        initialization_time = (time.time() - start_time) * 1000
        logger.error("Failed to run database migrations", 
                    database_url=db_path,
                    error=str(e), 
                    error_type=type(e).__name__,
                    initialization_time_ms=round(initialization_time, 2))
        
        # Fallback to create_all if Alembic fails (useful for development)
        logger.warning("Attempting fallback database initialization with create_all")
        
        try:
            Base.metadata.create_all(bind=engine)
            fallback_time = (time.time() - start_time) * 1000
            logger.info("Fallback database initialization completed", 
                       database_url=db_path,
                       total_time_ms=round(fallback_time, 2))
        except Exception as fallback_error:
            logger.error("Fallback database initialization also failed", 
                        database_url=db_path,
                        error=str(fallback_error), 
                        error_type=type(fallback_error).__name__)
            raise

def get_model_info() -> dict:
    """Get current model information.
    
    Returns information about the currently configured
    provider and model based on the application settings.
    
    Returns:
        A dictionary containing:
        - provider: The provider name
        - model: The specific model being used
        
    Examples:
        >>> get_model_info()
        {'provider': 'LLM Provider', 'model': 'llama2'}
    """
    return {
        "provider": settings.provider_name,
        "model": settings.provider_model
    }