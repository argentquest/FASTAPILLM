"""
MCP Server for AI Story Generator

This module implements a standalone MCP (Model Context Protocol) server that provides
AI story generation tools following FastMCP best practices from https://gofastmcp.com.

The server exposes:

Tools (4):
- generate_story_semantic_kernel: Generate stories using Microsoft's Semantic Kernel
- generate_story_langchain: Generate stories using LangChain framework  
- generate_story_langgraph: Generate stories using LangGraph with advanced editing
- list_frameworks: List all available AI frameworks with descriptions

Resources (2):
- data://config: Server configuration and version information
- stories/recent/{limit}: Recent generated stories (pending DB integration)

Prompts (6):
- classic_adventure_story: Adventure story prompts with customizable settings
- mystery_story: Mystery/detective story prompts
- sci_fi_story: Science fiction story prompts
- fantasy_quest_story: Fantasy quest story prompts
- comedy_story: Humorous story prompts
- story_prompt_list: List of creative story ideas

The server is designed to run independently from the main FastAPI application,
following FastMCP best practices for clean separation of concerns.

Features:
- Comprehensive request tracking with unique IDs
- Performance monitoring and timing metrics
- Detailed error handling and logging
- Cost tracking per story generation
- FastMCP 2.0 compatibility with prompts support

Usage:
    # Run standalone
    python mcp_server.py
    
    # Or with FastMCP CLI
    fastmcp run backend.mcp_server:mcp

Example:
    from fastmcp import Client
    client = Client(mcp)
    async with client:
        # Call a tool
        result = await client.call_tool("list_frameworks", {})
        
        # Get a prompt
        prompt = await client.get_prompt("classic_adventure_story", 
                                        {"primary_character": "Alice", 
                                         "secondary_character": "Bob"})
        print(prompt)
"""

from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent
from pydantic import Field
from typing import Dict, Any, List
import asyncio
import sys
import os
import time
from datetime import datetime
import uuid

from logging_config import get_logger
from transaction_context import transaction_context, get_current_transaction_guid
from retry_utils import retry_all_errors, retry_api_calls, retry_database_ops
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
@retry_all_errors
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
@retry_all_errors
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
@retry_all_errors
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
@retry_all_errors
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

# MCP Resource: Config/Version
@mcp.resource("data://config")
def get_config() -> Dict[str, Any]:
    """Get configuration and version information for the MCP server.
    
    Returns server metadata including version, capabilities, and configuration.
    This resource provides static information about the MCP server instance.
    
    Returns:
        Dict containing:
        - version: Server version number
        - name: Server name
        - capabilities: List of available capabilities
        - framework_count: Number of supported AI frameworks
        - created_at: ISO timestamp of server start time
    """
    return {
        "version": "1.0.0",
        "name": "AI Story Generator MCP Server",
        "capabilities": [
            "story_generation",
            "multi_framework_support",
            "cost_tracking",
            "performance_monitoring"
        ],
        "framework_count": 3,
        "frameworks": ["semantic_kernel", "langchain", "langgraph"],
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

# MCP Resource: Recent Stories
@mcp.resource("stories/recent/{limit}")
@retry_database_ops
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

# MCP Prompts: Story Generation Prompts
@mcp.prompt(
    name="classic_adventure_story",
    description="Generate a classic adventure story prompt with two characters",
    tags={"story", "adventure", "creative"}
)
def classic_adventure_story(
    primary_character: str = Field(description="The main protagonist of the story"),
    secondary_character: str = Field(description="The supporting character or companion"),
    setting: str = Field(default="enchanted forest", description="The story setting")
) -> str:
    """Creates a prompt for generating a classic adventure story."""
    return (
        f"Write an engaging adventure story featuring {primary_character} as the main protagonist "
        f"and {secondary_character} as their companion. Set the story in a {setting}. "
        f"Include elements of mystery, friendship, and personal growth. "
        f"The story should be suitable for all ages with vivid descriptions and dialogue."
    )

@mcp.prompt(
    name="mystery_story", 
    description="Generate a mystery story prompt with investigation elements",
    tags={"story", "mystery", "detective"}
)
def mystery_story(
    detective: str = Field(description="The detective or investigator character"),
    suspect: str = Field(description="The mysterious character involved in the case"),
    location: str = Field(default="old mansion", description="Where the mystery takes place")
) -> PromptMessage:
    """Creates a prompt for generating a mystery story."""
    content = (
        f"Create a compelling mystery story where {detective} must investigate a puzzling case "
        f"involving {suspect} at a {location}. Include clues, red herrings, and a surprising "
        f"revelation. The story should build suspense while maintaining logical consistency."
    )
    return PromptMessage(
        role="user",
        content=TextContent(type="text", text=content)
    )

@mcp.prompt(
    name="sci_fi_story",
    description="Generate a science fiction story prompt",
    tags={"story", "sci-fi", "futuristic"}
)
def sci_fi_story(
    protagonist: str = Field(description="The main character"),
    companion: str = Field(description="The companion or crew member"),
    technology: str = Field(default="time travel", description="The key technology or concept")
) -> str:
    """Creates a prompt for generating a sci-fi story."""
    return (
        f"Write a thought-provoking science fiction story starring {protagonist} and {companion}. "
        f"The story should revolve around {technology} and explore its implications. "
        f"Include futuristic elements, ethical dilemmas, and imaginative world-building."
    )

@mcp.prompt(
    name="fantasy_quest_story",
    description="Generate a fantasy quest story prompt",
    tags={"story", "fantasy", "quest", "magic"}
)
def fantasy_quest_story(
    hero: str = Field(description="The hero of the quest"),
    mentor: str = Field(description="The wise mentor or guide"),
    artifact: str = Field(default="Crystal of Power", description="The magical item to find")
) -> str:
    """Creates a prompt for generating a fantasy quest story."""
    return (
        f"Craft an epic fantasy quest where {hero}, guided by the wise {mentor}, "
        f"must find the legendary {artifact}. Include magical creatures, challenging trials, "
        f"and the hero's personal transformation throughout their journey."
    )

@mcp.prompt(
    name="comedy_story",
    description="Generate a humorous story prompt",
    tags={"story", "comedy", "humor"}
)
def comedy_story(
    character1: str = Field(description="The first comedic character"),
    character2: str = Field(description="The second comedic character"),
    situation: str = Field(default="cooking competition", description="The funny situation")
) -> PromptMessage:
    """Creates a prompt for generating a comedy story."""
    content = (
        f"Write a hilarious story about {character1} and {character2} who find themselves in "
        f"a {situation}. Include misunderstandings, slapstick moments, witty dialogue, "
        f"and an unexpectedly heartwarming conclusion."
    )
    return PromptMessage(
        role="user",
        content=TextContent(type="text", text=content)
    )

@mcp.prompt(
    name="story_prompt_list",
    description="Get a list of creative story prompts for various genres",
    tags={"story", "prompts", "ideas"}
)
def story_prompt_list() -> List[str]:
    """Returns a list of creative story prompts."""
    return [
        "A time traveler accidentally changes a minor historical event with major consequences",
        "Two rival chefs must work together to save their restaurant from closing",
        "A child discovers their imaginary friend is actually from another dimension",
        "An AI develops emotions and must navigate human relationships",
        "A retired superhero is forced back into action by an unexpected threat",
        "Two strangers wake up with swapped abilities and must find each other",
        "A librarian discovers that certain books are portals to other worlds",
        "A ghost and a living person become roommates and solve mysteries together"
    ]

# Following FastMCP best practice - include __main__ block
if __name__ == "__main__":
    logger.info("Starting AI Story Generator MCP Server",
                pid=os.getpid(),
                working_dir=os.getcwd(),
                python_path=sys.executable)
    
    # Log available tools and resources
    logger.info("MCP Server tools registered",
                tools=["generate_story_semantic_kernel", 
                      "generate_story_langchain", 
                      "generate_story_langgraph",
                      "list_frameworks"])
    
    logger.info("MCP Server resources registered",
                resources=["data://config", "stories/recent/{limit}"])
    
    logger.info("MCP Server prompts registered",
                prompts=["classic_adventure_story", "mystery_story", "sci_fi_story",
                        "fantasy_quest_story", "comedy_story", "story_prompt_list"])
    
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