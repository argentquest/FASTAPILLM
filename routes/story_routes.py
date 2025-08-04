from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Optional, List
import time
from sqlalchemy.orm import Session

from schemas import StoryRequest, StoryResponse, StoryList, StoryDB
from services.story_services import SemanticKernelService, LangChainService, LangGraphService
from logging_config import get_logger
from config import settings
from database import get_db, Story, get_model_info
from transaction_context import get_current_transaction_guid

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["story"])

# Service instances (lazy loaded)
_services: Dict[str, Optional[object]] = {
    "semantic_kernel": None,
    "langchain": None,
    "langgraph": None
}

def get_service(service_name: str):
    """Lazy load service instances.
    
    Creates and caches service instances on first use to avoid
    initialization overhead during startup.
    
    Args:
        service_name: The name of the service to retrieve.
            Must be one of: "semantic_kernel", "langchain", "langgraph".
            
    Returns:
        The requested service instance.
        
    Raises:
        KeyError: If an invalid service name is provided.
        
    Examples:
        >>> service = get_service("langchain")
        >>> isinstance(service, LangChainService)
        True
    """
    if _services[service_name] is None:
        logger.info(f"Initializing {service_name} service")
        if service_name == "semantic_kernel":
            _services[service_name] = SemanticKernelService()
        elif service_name == "langchain":
            _services[service_name] = LangChainService()
        elif service_name == "langgraph":
            _services[service_name] = LangGraphService()
    return _services[service_name]

async def generate_story_handler(
    request: StoryRequest,
    service_name: str,
    method_name: str,
    request_obj: Request,
    db: Session
) -> StoryResponse:
    """Common story generation logic.
    
    Handles the complete story generation workflow including:
    - Service initialization
    - Story generation via AI service
    - Performance tracking
    - Database persistence
    - Response formatting
    
    Args:
        request: The story generation request with character names.
        service_name: The internal service name (e.g., "langchain").
        method_name: The display name of the method (e.g., "LangChain").
        request_obj: The FastAPI request object for accessing request state.
        db: The database session.
        
    Returns:
        A StoryResponse containing the generated story and metadata.
        
    Raises:
        Any exceptions from the AI service or database operations.
        
    Examples:
        >>> response = await generate_story_handler(
        ...     request=StoryRequest(primary_character="Alice", secondary_character="Bob"),
        ...     service_name="langchain",
        ...     method_name="LangChain",
        ...     request_obj=request,
        ...     db=session
        ... )
    """
    request_id = getattr(request_obj.state, 'request_id', None)
    
    logger.info("Story generation started", 
               service_name=service_name,
               method=method_name,
               primary_character=request.primary_character,
               secondary_character=request.secondary_character,
               request_id=request_id)
    
    start_time = time.time()
    db_start_time = None
    
    try:
        # Generate story
        logger.debug("Retrieving service instance", service_name=service_name)
        service = get_service(service_name)
        
        logger.debug("Starting story generation with AI service")
        story, usage_info = await service.generate_story(
            request.primary_character,
            request.secondary_character
        )
        
        ai_generation_time = (time.time() - start_time) * 1000
        
        logger.info("AI story generation completed", 
                   service_name=service_name,
                   story_length=len(story),
                   ai_generation_time_ms=round(ai_generation_time, 2),
                   input_tokens=usage_info["input_tokens"],
                   output_tokens=usage_info["output_tokens"],
                   total_tokens=usage_info["total_tokens"],
                   tokens_per_second=round(usage_info["output_tokens"] / (ai_generation_time / 1000), 2) if ai_generation_time > 0 else 0,
                   request_id=request_id)
        
        # Get model info
        model_info = get_model_info()
        
        # Save to database
        db_start_time = time.time()
        logger.debug("Saving story to database")
        
        story_record = Story(
            primary_character=request.primary_character,
            secondary_character=request.secondary_character,
            combined_characters=f"{request.primary_character} and {request.secondary_character}",
            story_content=story,
            method=service_name,
            generation_time_ms=round(ai_generation_time, 2),
            input_tokens=usage_info["input_tokens"],
            output_tokens=usage_info["output_tokens"],
            total_tokens=usage_info["total_tokens"],
            request_id=request_id,
            transaction_guid=get_current_transaction_guid(),  # Add transaction GUID
            provider=model_info["provider"],
            model=model_info["model"],
            # Cost tracking fields
            estimated_cost_usd=usage_info["estimated_cost_usd"],
            input_cost_per_1k_tokens=usage_info["input_cost_per_1k_tokens"],
            output_cost_per_1k_tokens=usage_info["output_cost_per_1k_tokens"]
        )
        
        db.add(story_record)
        db.commit()
        db.refresh(story_record)
        
        db_save_time = (time.time() - db_start_time) * 1000
        total_time = (time.time() - start_time) * 1000
        
        logger.info("Story generation completed successfully", 
                   service_name=service_name,
                   story_id=story_record.id,
                   story_length=len(story),
                   total_time_ms=round(total_time, 2),
                   ai_generation_time_ms=round(ai_generation_time, 2),
                   db_save_time_ms=round(db_save_time, 2),
                   ai_percentage=round((ai_generation_time / total_time) * 100, 1),
                   db_percentage=round((db_save_time / total_time) * 100, 1),
                   total_tokens=usage_info["total_tokens"],
                   cost_estimate_tokens=usage_info["total_tokens"],  # For cost tracking
                   request_id=request_id)
        
        return StoryResponse(
            id=story_record.id,
            story=story,
            primary_character=request.primary_character,
            secondary_character=request.secondary_character,
            framework=service_name,
            created_at=story_record.created_at.isoformat(),
            generation_time_ms=round(ai_generation_time, 2),
            input_tokens=usage_info["input_tokens"],
            output_tokens=usage_info["output_tokens"],
            total_tokens=usage_info["total_tokens"],
            request_id=request_id,
            transaction_guid=get_current_transaction_guid(),  # Include transaction GUID in response
            estimated_cost_usd=usage_info["estimated_cost_usd"],
            input_cost_per_1k_tokens=usage_info["input_cost_per_1k_tokens"],
            output_cost_per_1k_tokens=usage_info["output_cost_per_1k_tokens"]
        )
        
    except Exception as e:
        error_time = (time.time() - start_time) * 1000
        logger.error("Story generation failed", 
                    service_name=service_name,
                    error=str(e),
                    error_type=type(e).__name__,
                    error_time_ms=round(error_time, 2),
                    primary_character=request.primary_character,
                    secondary_character=request.secondary_character,
                    request_id=request_id)
        raise

@router.post("/semantic-kernel", response_model=StoryResponse)
async def generate_story_semantic_kernel(
    request: StoryRequest,
    request_obj: Request,
    db: Session = Depends(get_db)
):
    """Generate a story using Semantic Kernel approach.
    
    This endpoint uses Microsoft's Semantic Kernel framework to generate
    stories. It leverages semantic functions and native functions to
    create coherent narratives.
    
    Args:
        request: Story request containing primary and secondary character names.
        request_obj: The FastAPI request object.
        db: Database session (injected).
        
    Returns:
        StoryResponse with the generated story and metadata.
        
    Raises:
        HTTPException: If story generation fails.
        
    Examples:
        Request:
        ```json
        {
            "primary_character": "Alice",
            "secondary_character": "Bob"
        }
        ```
        
        Response:
        ```json
        {
            "story": "Once upon a time, Alice and Bob...",
            "combined_characters": "Alice and Bob",
            "method": "Semantic Kernel",
            "generation_time_ms": 1234.56,
            "input_tokens": 100,
            "output_tokens": 500,
            "total_tokens": 600,
            "request_id": "uuid-here"
        }
        ```
    """
    logger.info("Story generation request received",
               method="semantic-kernel",
               primary_character=request.primary_character,
               secondary_character=request.secondary_character)
    
    return await generate_story_handler(
        request,
        "semantic_kernel",
        "Semantic Kernel",
        request_obj,
        db
    )

@router.post("/langchain", response_model=StoryResponse)
async def generate_story_langchain(
    request: StoryRequest,
    request_obj: Request,
    db: Session = Depends(get_db)
):
    """Generate a story using LangChain framework.
    
    This endpoint uses the LangChain framework with prompt templates
    and chains to generate stories. It provides structured prompt
    engineering for consistent story output.
    
    Args:
        request: Story request containing primary and secondary character names.
        request_obj: The FastAPI request object.
        db: Database session (injected).
        
    Returns:
        StoryResponse with the generated story and metadata.
        
    Raises:
        HTTPException: If story generation fails.
        
    Examples:
        Request:
        ```json
        {
            "primary_character": "Sherlock Holmes",
            "secondary_character": "Dr. Watson"
        }
        ```
    """
    logger.info("Story generation request received",
               method="langchain",
               primary_character=request.primary_character,
               secondary_character=request.secondary_character)
    
    return await generate_story_handler(
        request,
        "langchain",
        "LangChain",
        request_obj,
        db
    )

@router.post("/langgraph", response_model=StoryResponse)
async def generate_story_langgraph(
    request: StoryRequest,
    request_obj: Request,
    db: Session = Depends(get_db)
):
    """Generate a story using LangGraph workflow.
    
    This endpoint uses LangGraph to create a multi-stage story generation
    workflow with outline creation and iterative story development.
    It provides more control over the story structure.
    
    Args:
        request: Story request containing primary and secondary character names.
        request_obj: The FastAPI request object.
        db: Database session (injected).
        
    Returns:
        StoryResponse with the generated story and metadata.
        
    Raises:
        HTTPException: If story generation fails.
        
    Examples:
        Request:
        ```json
        {
            "primary_character": "Harry Potter",
            "secondary_character": "Hermione Granger"
        }
        ```
    """
    logger.info("Story generation request received",
               method="langgraph",
               primary_character=request.primary_character,
               secondary_character=request.secondary_character)
    
    return await generate_story_handler(
        request,
        "langgraph",
        "LangGraph",
        request_obj,
        db
    )

@router.get("/stories", response_model=List[StoryList])
async def get_stories(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get list of generated stories.
    
    Retrieves a paginated list of previously generated stories,
    ordered by creation date (newest first).
    
    Args:
        skip: Number of stories to skip (for pagination). Defaults to 0.
        limit: Maximum number of stories to return. Defaults to 10.
        db: Database session (injected).
        
    Returns:
        List of StoryList objects with story previews and metadata.
        
    Examples:
        >>> # Get first 10 stories
        >>> GET /api/stories
        
        >>> # Get stories 10-20
        >>> GET /api/stories?skip=10&limit=10
    """
    stories = db.query(Story).order_by(Story.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        StoryList(
            id=story.id,
            primary_character=story.primary_character,
            secondary_character=story.secondary_character,
            combined_characters=story.combined_characters,
            story_preview=story.story_content[:200] + "..." if len(story.story_content) > 200 else story.story_content,
            framework=story.method,
            model=story.model,
            generation_time_ms=story.generation_time_ms,
            input_tokens=story.input_tokens,
            output_tokens=story.output_tokens,
            total_tokens=story.total_tokens,
            created_at=story.created_at.isoformat(),
            transaction_guid=story.transaction_guid,
            estimated_cost_usd=float(story.estimated_cost_usd) if story.estimated_cost_usd else None,
            input_cost_per_1k_tokens=float(story.input_cost_per_1k_tokens) if story.input_cost_per_1k_tokens else None,
            output_cost_per_1k_tokens=float(story.output_cost_per_1k_tokens) if story.output_cost_per_1k_tokens else None
        )
        for story in stories
    ]

@router.get("/stories/{story_id}", response_model=StoryDB)
async def get_story(
    story_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific story by ID.
    
    Retrieves the complete story content and all metadata for a
    specific story ID.
    
    Args:
        story_id: The unique identifier of the story.
        db: Database session (injected).
        
    Returns:
        Complete StoryDB object with full story content.
        
    Raises:
        HTTPException: 404 if story not found.
        
    Examples:
        >>> GET /api/stories/123
        {
            "id": 123,
            "primary_character": "Alice",
            "secondary_character": "Bob",
            "story_content": "Full story text...",
            ...
        }
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    return StoryDB.from_orm(story)

@router.get("/stories/search/characters", response_model=List[StoryList])
async def search_stories_by_characters(
    character: str,
    db: Session = Depends(get_db)
):
    """Search stories by character name.
    
    Searches for stories containing the specified character name in
    either the primary or secondary character fields. The search is
    case-insensitive and uses partial matching.
    
    Args:
        character: The character name to search for (partial match).
        db: Database session (injected).
        
    Returns:
        List of StoryList objects matching the search criteria,
        ordered by creation date (newest first).
        
    Examples:
        >>> GET /api/stories/search/characters?character=Alice
        [
            {
                "id": 1,
                "primary_character": "Alice",
                "secondary_character": "Bob",
                ...
            },
            {
                "id": 5,
                "primary_character": "Charlie",
                "secondary_character": "Alice in Wonderland",
                ...
            }
        ]
    """
    stories = db.query(Story).filter(
        (Story.primary_character.contains(character)) | 
        (Story.secondary_character.contains(character))
    ).order_by(Story.created_at.desc()).all()
    
    return [
        StoryList(
            id=story.id,
            primary_character=story.primary_character,
            secondary_character=story.secondary_character,
            combined_characters=story.combined_characters,
            story_preview=story.story_content[:200] + "..." if len(story.story_content) > 200 else story.story_content,
            framework=story.method,
            model=story.model,
            generation_time_ms=story.generation_time_ms,
            input_tokens=story.input_tokens,
            output_tokens=story.output_tokens,
            total_tokens=story.total_tokens,
            created_at=story.created_at.isoformat(),
            transaction_guid=story.transaction_guid,
            estimated_cost_usd=float(story.estimated_cost_usd) if story.estimated_cost_usd else None,
            input_cost_per_1k_tokens=float(story.input_cost_per_1k_tokens) if story.input_cost_per_1k_tokens else None,
            output_cost_per_1k_tokens=float(story.output_cost_per_1k_tokens) if story.output_cost_per_1k_tokens else None
        )
        for story in stories
    ]


@router.delete("/stories")
async def delete_all_stories(
    db: Session = Depends(get_db)
):
    """Delete all generated stories.
    
    Removes all stories from the database. This action cannot be undone.
    
    Returns:
        Dict with success message and count of deleted stories.
    """
    logger.info("Delete all stories request received")
    
    try:
        # Count stories before deletion
        story_count = db.query(Story).count()
        
        # Delete all stories
        db.query(Story).delete()
        db.commit()
        
        logger.info("All stories deleted successfully", deleted_count=story_count)
        
        return {
            "message": f"Successfully deleted {story_count} stories",
            "deleted_count": story_count
        }
        
    except Exception as e:
        db.rollback()
        logger.error("Failed to delete all stories", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete stories: {str(e)}"
        )
