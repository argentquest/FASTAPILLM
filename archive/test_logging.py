#!/usr/bin/env python3
"""
Test script to generate sample log entries for testing the log viewer
"""

from logging_config import configure_logging, get_logger
from config import settings
import time
import random

# Configure logging
configure_logging(
    debug=settings.debug_mode,
    log_file_path=settings.log_file_path,
    log_level=settings.log_level,
    rotation_hours=settings.log_rotation_hours,
    retention_days=settings.log_retention_days
)

logger = get_logger(__name__)

def generate_test_logs():
    """Generate various types of log entries for testing"""
    
    # Simulate application startup
    logger.info("Test log generation started", 
               test_session_id="test-12345",
               environment="testing")
    
    # Simulate story generation requests
    for i in range(5):
        request_id = f"req-{random.randint(1000, 9999)}"
        
        logger.info("Story generation started",
                   service_name="semantic_kernel",
                   primary_character="Santa Claus",
                   secondary_character="Rudolph",
                   request_id=request_id)
        
        # Simulate processing time
        time.sleep(0.1)
        
        logger.info("Story generation completed successfully",
                   service_name="semantic_kernel",
                   story_length=1247,
                   total_time_ms=2341.56,
                   ai_generation_time_ms=2100.34,
                   input_tokens=150,
                   output_tokens=300,
                   total_tokens=450,
                   tokens_per_second=23.4,
                   request_id=request_id)
    
    # Simulate some chat interactions
    for i in range(3):
        conv_id = random.randint(100, 999)
        request_id = f"chat-{random.randint(1000, 9999)}"
        
        logger.info("Chat message processing started",
                   method="langchain",
                   message_length=45,
                   conversation_id=conv_id,
                   request_id=request_id)
        
        time.sleep(0.05)
        
        logger.info("Chat message processing completed",
                   service="langchain",
                   conversation_id=conv_id,
                   total_time_ms=1876.45,
                   ai_generation_time_ms=1654.32,
                   tokens_per_second=18.7,
                   total_tokens=234,
                   request_id=request_id)
    
    # Simulate some validation events
    logger.warning("Character name too long",
                  field_name="primary_character",
                  length=150,
                  max_allowed=100)
    
    logger.warning("Suspicious input patterns detected",
                  field_name="secondary_character", 
                  patterns=["sql_injection"],
                  input_preview="'; DROP TABLE users; --")
    
    # Simulate database operations
    logger.info("Database transaction committed successfully",
               transaction_id=140234567890123,
               new_objects=2,
               dirty_objects=1,
               transaction_time_ms=12.34)
    
    # Simulate some errors
    logger.error("Story generation failed",
                service_name="langgraph",
                error="Connection timeout",
                error_type="TimeoutError",
                error_time_ms=30000.0,
                request_id="req-error-1")
    
    logger.error("Database transaction failed, rolling back",
                transaction_id=140234567890124,
                error="duplicate key value violates unique constraint",
                error_type="IntegrityError")
    
    # Simulate configuration validation
    logger.info("LLM provider validated successfully", provider="azure")
    
    # Simulate security events
    logger.warning("Large conversation context detected",
                  conversation_id=456,
                  total_context_chars=8500,
                  message_count=25)
    
    logger.debug("Loading Alembic configuration")
    logger.debug("Retrieving service instance", service_name="semantic_kernel")
    
    logger.info("Test log generation completed",
               total_entries_generated=20,
               test_session_id="test-12345")

if __name__ == "__main__":
    generate_test_logs()
    print("✅ Test log entries generated successfully!")
    print("📁 Check logs/app.log to see the entries")
    print("🌐 Visit http://localhost:8000/logs to view them in the web interface")