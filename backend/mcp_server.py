"""
MCP Server for AI Story Generator

This module implements a standalone MCP (Model Context Protocol) server that provides
AI story generation tools following FastMCP best practices from https://gofastmcp.com.

The server exposes four main tools:
- generate_story_semantic_kernel: Generate stories using Microsoft's Semantic Kernel
- generate_story_langchain: Generate stories using LangChain framework  
- generate_story_langgraph: Generate stories using LangGraph with advanced editing
- list_frameworks: List all available AI frameworks with descriptions

The server is designed to run independently from the main FastAPI application,
following FastMCP best practices for clean separation of concerns.

Features:
- Comprehensive request tracking with unique IDs
- Performance monitoring and timing metrics
- Detailed error handling and logging
- Cost tracking per story generation
- FastMCP 2.0 compatibility

Usage:
    # Run standalone
    python mcp_server.py
    
    # Or with FastMCP CLI
    fastmcp run backend.mcp_server:mcp

Example:
    from fastmcp import Client
    client = Client(mcp)
    async with client:
        result = await client.call_tool("list_frameworks", {})
        print(result)
"""

from fastmcp import FastMCP
from typing import Dict, Any
import asyncio
import sys
import os
import time
from datetime import datetime
import uuid

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logging_config import get_logger
from transaction_context import transaction_context, get_current_transaction_guid
from services.story_services import (
    SemanticKernelService,
    LangChainService,
    LangGraphService
)

# Initialize logger
logger = get_logger(__name__)

# Create FastMCP instance
mcp = FastMCP("AI Story Generator MCP Server")

# Log server initialization
logger.info("MCP Server initialized", 
            server_name="AI Story Generator MCP Server",
            fastmcp_version=getattr(FastMCP, '__version__', 'unknown'),
            python_version=sys.version)

@mcp.tool
async def generate_story_semantic_kernel(
    primary_character: str,
    secondary_character: str
) -> Dict[str, Any]:
    """Generate a story using Semantic Kernel framework."""
    # Generate transaction GUID and set context for the entire operation
    transaction_guid = str(uuid.uuid4())
    
    with transaction_context(transaction_guid):
        start_time = time.time()
        request_id = f"sk_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash((primary_character, secondary_character)) % 10000}"
        
        logger.info("MCP Tool invoked: generate_story_semantic_kernel",
                    request_id=request_id,
                    primary=primary_character,
                    secondary=secondary_character,
                    framework="semantic_kernel")
        
        try:
            # Create service instance
            logger.debug("Creating SemanticKernelService instance", request_id=request_id)
            service = SemanticKernelService()
            
            # Generate story and usage info
            logger.debug("Calling service.generate_story", 
                        request_id=request_id,
                        service_class="SemanticKernelService")
            
            result, usage_info = await service.generate_story(
                primary_character=primary_character,
                secondary_character=secondary_character
            )
            
            logger.debug("Story generation completed",
                        request_id=request_id,
                        story_length=len(result),
                        usage_info=usage_info)
            
            # Return structured response with transaction GUID
            response_data = {
                "id": None,  # Will be assigned when saved to DB
                "story": result,
                "primary_character": primary_character,
                "secondary_character": secondary_character,
                "framework": "semantic_kernel",
                "model": usage_info.get("model", "unknown"),
                "total_tokens": usage_info.get("total_tokens", 0),
                "estimated_cost_usd": usage_info.get("estimated_cost_usd", 0),
                "generation_time_ms": usage_info.get("execution_time_ms", 0),
                "transaction_guid": transaction_guid  # Return to MCP client
            }
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info("MCP Tool completed successfully",
                       request_id=request_id,
                       tool="generate_story_semantic_kernel",
                       elapsed_time_ms=elapsed_time,
                       tokens=response_data["total_tokens"],
                       cost_usd=response_data["estimated_cost_usd"])
            
            return response_data
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error("MCP Tool failed",
                        request_id=request_id,
                        tool="generate_story_semantic_kernel",
                        error=str(e),
                        error_type=type(e).__name__,
                        elapsed_time_ms=elapsed_time,
                        exc_info=True)
            raise Exception(f"Story generation failed: {str(e)}")

@mcp.tool
async def generate_story_langchain(
    primary_character: str,
    secondary_character: str
) -> Dict[str, Any]:
    """Generate a story using LangChain framework."""
    # Generate transaction GUID and set context for the entire operation
    transaction_guid = str(uuid.uuid4())
    
    with transaction_context(transaction_guid):
        start_time = time.time()
        request_id = f"lc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash((primary_character, secondary_character)) % 10000}"
        
        logger.info("MCP Tool invoked: generate_story_langchain",
                    request_id=request_id,
                    primary=primary_character,
                    secondary=secondary_character,
                    framework="langchain")
        
        try:
            # Create service instance
            logger.debug("Creating LangChainService instance", request_id=request_id)
            service = LangChainService()
            
            # Generate story and usage info
            logger.debug("Calling service.generate_story", 
                        request_id=request_id,
                        service_class="LangChainService")
            
            result, usage_info = await service.generate_story(
                primary_character=primary_character,
                secondary_character=secondary_character
            )
            
            logger.debug("Story generation completed",
                        request_id=request_id,
                        story_length=len(result),
                        usage_info=usage_info)
            
            # Return structured response with transaction GUID
            response_data = {
                "id": None,
                "story": result,
                "primary_character": primary_character,
                "secondary_character": secondary_character,
                "framework": "langchain",
                "model": usage_info.get("model", "unknown"),
                "total_tokens": usage_info.get("total_tokens", 0),
                "estimated_cost_usd": usage_info.get("estimated_cost_usd", 0),
                "generation_time_ms": usage_info.get("execution_time_ms", 0),
                "transaction_guid": transaction_guid  # Return to MCP client
            }
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info("MCP Tool completed successfully",
                       request_id=request_id,
                       tool="generate_story_langchain",
                       elapsed_time_ms=elapsed_time,
                       tokens=response_data["total_tokens"],
                       cost_usd=response_data["estimated_cost_usd"])
            
            return response_data
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error("MCP Tool failed",
                        request_id=request_id,
                        tool="generate_story_langchain",
                        error=str(e),
                        error_type=type(e).__name__,
                        elapsed_time_ms=elapsed_time,
                        exc_info=True)
            raise Exception(f"Story generation failed: {str(e)}")

@mcp.tool
async def generate_story_langgraph(
    primary_character: str,
    secondary_character: str
) -> Dict[str, Any]:
    """Generate a story using LangGraph framework with advanced editing."""
    # Generate transaction GUID and set context for the entire operation
    transaction_guid = str(uuid.uuid4())
    
    with transaction_context(transaction_guid):
        start_time = time.time()
        request_id = f"lg_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash((primary_character, secondary_character)) % 10000}"
        
        logger.info("MCP Tool invoked: generate_story_langgraph",
                    request_id=request_id,
                    primary=primary_character,
                    secondary=secondary_character,
                    framework="langgraph")
        
        try:
            # Create service instance
            logger.debug("Creating LangGraphService instance", request_id=request_id)
            service = LangGraphService()
            
            # Generate story and usage info
            logger.debug("Calling service.generate_story", 
                        request_id=request_id,
                        service_class="LangGraphService")
            
            result, usage_info = await service.generate_story(
                primary_character=primary_character,
                secondary_character=secondary_character
            )
            
            logger.debug("Story generation completed",
                        request_id=request_id,
                        story_length=len(result),
                        usage_info=usage_info)
            
            # Return structured response with transaction GUID
            response_data = {
                "id": None,
                "story": result,
                "primary_character": primary_character,
                "secondary_character": secondary_character,
                "framework": "langgraph",
                "model": usage_info.get("model", "unknown"),
                "total_tokens": usage_info.get("total_tokens", 0),
                "estimated_cost_usd": usage_info.get("estimated_cost_usd", 0),
                "generation_time_ms": usage_info.get("execution_time_ms", 0),
                "transaction_guid": transaction_guid  # Return to MCP client
            }
            
            elapsed_time = (time.time() - start_time) * 1000
            logger.info("MCP Tool completed successfully",
                       request_id=request_id,
                       tool="generate_story_langgraph",
                       elapsed_time_ms=elapsed_time,
                       tokens=response_data["total_tokens"],
                       cost_usd=response_data["estimated_cost_usd"])
            
            return response_data
            
        except Exception as e:
            elapsed_time = (time.time() - start_time) * 1000
            logger.error("MCP Tool failed",
                        request_id=request_id,
                        tool="generate_story_langgraph",
                        error=str(e),
                        error_type=type(e).__name__,
                        elapsed_time_ms=elapsed_time,
                        exc_info=True)
            raise Exception(f"Story generation failed: {str(e)}")

@mcp.tool
async def list_frameworks() -> Dict[str, Any]:
    """List available AI frameworks for story generation."""
    # Generate transaction GUID and set context for the entire operation
    transaction_guid = str(uuid.uuid4())
    
    with transaction_context(transaction_guid):
        start_time = time.time()
        request_id = f"list_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info("MCP Tool invoked: list_frameworks", request_id=request_id)
        
        frameworks_data = {
            "frameworks": [
                {
                    "name": "semantic_kernel",
                    "description": "Microsoft's Semantic Kernel framework",
                    "features": ["Plugin-based architecture", "Native functions", "Semantic functions"]
                },
                {
                    "name": "langchain", 
                    "description": "LangChain framework for LLM applications",
                    "features": ["Chain composition", "Prompt templates", "Memory management"]
                },
                {
                    "name": "langgraph",
                    "description": "LangGraph framework with advanced editing",
                    "features": ["Graph-based workflows", "State management", "Multi-step editing"]
                }
            ],
            "transaction_guid": transaction_guid  # Return to MCP client
        }
        
        elapsed_time = (time.time() - start_time) * 1000
        logger.info("MCP Tool completed successfully",
                   request_id=request_id,
                   tool="list_frameworks",
                   elapsed_time_ms=elapsed_time,
                   frameworks_count=len(frameworks_data["frameworks"]))
        
        return frameworks_data

# MCP Resource: Recent Stories
@mcp.resource("stories/recent/{limit}")
async def get_recent_stories(limit: int = 10) -> Dict[str, Any]:
    """Get recent generated stories from the database.
    
    Retrieves the most recently generated stories with full metadata
    including token usage, costs, and generation times. Stories are
    ordered by creation timestamp in descending order.
    
    Args:
        limit: Maximum number of stories to return (1-100). Defaults to 10.
               
    Returns:
        Dict containing:
        - stories: List of story objects with metadata (currently empty)
        - message: Status message about database integration
        - limit: The applied limit value
        - total_count: Total stories available (when DB integrated)
        
    Note: 
        Currently returns placeholder data. Database integration is pending.
        Once implemented, this will provide access to the stories database
        with proper filtering and pagination support.
        
    Example:
        # Future implementation will return:
        {
            "stories": [
                {
                    "id": "story_123",
                    "primary_character": "Alice", 
                    "secondary_character": "Bob",
                    "framework": "langchain",
                    "story": "Once upon a time...",
                    "created_at": "2024-08-04T12:00:00Z",
                    "tokens": 500,
                    "cost_usd": 0.001
                }
            ],
            "total_count": 150,
            "limit": 10,
            "message": "Successfully retrieved recent stories"
        }
    """
    # TODO: Implement database integration
    # This would connect to the same database used by the FastAPI application
    # to retrieve story records with full metadata
    return {
        "stories": [],
        "message": "Database integration pending - stories will be available once connected to main application database",
        "limit": limit,
        "total_count": 0
    }

# Following FastMCP best practice - include __main__ block
if __name__ == "__main__":
    logger.info("Starting AI Story Generator MCP Server",
                pid=os.getpid(),
                working_dir=os.getcwd(),
                python_path=sys.executable)
    
    # Log available tools
    logger.info("MCP Server tools registered",
                tools=["generate_story_semantic_kernel", 
                      "generate_story_langchain", 
                      "generate_story_langgraph",
                      "list_frameworks"])
    
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("MCP Server shutdown requested via keyboard interrupt")
    except Exception as e:
        logger.error("MCP Server crashed",
                    error=str(e),
                    error_type=type(e).__name__,
                    exc_info=True)
        raise
    finally:
        logger.info("MCP Server shutdown complete")