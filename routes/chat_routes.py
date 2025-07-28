from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Optional, List
import time
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from schemas import ChatMessageRequest, ChatMessageResponse, ChatResponse, ChatConversationList, ChatConversationResponse
from services.chat_services import SemanticKernelChatService, LangChainChatService, LangGraphChatService
from logging_config import get_logger
from config import settings
from database import get_db, ChatConversation, ChatMessage, get_model_info

logger = get_logger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Service instances (lazy loaded)
_chat_services: Dict[str, Optional[object]] = {
    "semantic_kernel": None,
    "langchain": None,
    "langgraph": None
}

def get_chat_service(service_name: str):
    """Lazy load chat service instances.
    
    Creates and caches chat service instances on first use to avoid
    initialization overhead during startup.
    
    Args:
        service_name: The name of the service to retrieve.
            Must be one of: "semantic_kernel", "langchain", "langgraph".
            
    Returns:
        The requested chat service instance.
        
    Raises:
        KeyError: If an invalid service name is provided.
        
    Examples:
        >>> service = get_chat_service("langchain")
        >>> isinstance(service, LangChainChatService)
        True
    """
    if _chat_services[service_name] is None:
        logger.info(f"Initializing {service_name} chat service")
        if service_name == "semantic_kernel":
            _chat_services[service_name] = SemanticKernelChatService()
        elif service_name == "langchain":
            _chat_services[service_name] = LangChainChatService()
        elif service_name == "langgraph":
            _chat_services[service_name] = LangGraphChatService()
    return _chat_services[service_name]

def generate_conversation_title(first_message: str) -> str:
    """Generate a conversation title from the first message.
    
    Creates a concise title for a conversation based on the initial
    user message. Truncates long messages and adds ellipsis.
    
    Args:
        first_message: The first user message in the conversation.
        
    Returns:
        A title string of maximum 53 characters (50 + "...").
        
    Examples:
        >>> generate_conversation_title("Hello, how are you?")
        'Hello, how are you?'
        >>> generate_conversation_title("A" * 60)
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...'
    """
    # Take first 50 characters and add ellipsis if longer
    title = first_message.strip()[:50]
    if len(first_message) > 50:
        title += "..."
    return title

@router.post("/semantic-kernel", response_model=ChatResponse)
async def chat_semantic_kernel(
    request: ChatMessageRequest,
    request_obj: Request,
    db: Session = Depends(get_db)
):
    """Send a chat message using Semantic Kernel.
    
    Processes a chat message using Microsoft's Semantic Kernel framework.
    Maintains conversation history and context across messages.
    
    Args:
        request: Chat message request containing the message and optional
            conversation ID.
        request_obj: The FastAPI request object.
        db: Database session (injected).
        
    Returns:
        ChatResponse with the AI response and conversation details.
        
    Raises:
        HTTPException: 404 if specified conversation not found.
        
    Examples:
        New conversation:
        ```json
        {"message": "Hello, can you help me?"}
        ```
        
        Continue conversation:
        ```json
        {
            "message": "Tell me more about that.",
            "conversation_id": 123
        }
        ```
    """
    return await handle_chat_message(request, "semantic_kernel", "Semantic Kernel", request_obj, db)

@router.post("/langchain", response_model=ChatResponse)
async def chat_langchain(
    request: ChatMessageRequest,
    request_obj: Request,
    db: Session = Depends(get_db)
):
    """Send a chat message using LangChain.
    
    Processes a chat message using the LangChain framework with
    conversation memory and context management.
    
    Args:
        request: Chat message request containing the message and optional
            conversation ID.
        request_obj: The FastAPI request object.
        db: Database session (injected).
        
    Returns:
        ChatResponse with the AI response and conversation details.
        
    Raises:
        HTTPException: 404 if specified conversation not found.
    """
    return await handle_chat_message(request, "langchain", "LangChain", request_obj, db)

@router.post("/langgraph", response_model=ChatResponse)
async def chat_langgraph(
    request: ChatMessageRequest,
    request_obj: Request,
    db: Session = Depends(get_db)
):
    """Send a chat message using LangGraph.
    
    Processes a chat message using LangGraph's stateful conversation
    workflow with enhanced context management.
    
    Args:
        request: Chat message request containing the message and optional
            conversation ID.
        request_obj: The FastAPI request object.
        db: Database session (injected).
        
    Returns:
        ChatResponse with the AI response and conversation details.
        
    Raises:
        HTTPException: 404 if specified conversation not found.
    """
    return await handle_chat_message(request, "langgraph", "LangGraph", request_obj, db)

async def handle_chat_message(
    request: ChatMessageRequest,
    service_name: str,
    method_name: str,
    request_obj: Request,
    db: Session
) -> ChatResponse:
    """Common chat message handling logic.
    
    Handles the complete chat workflow including:
    - Loading or creating conversations
    - Managing conversation history
    - Generating AI responses
    - Persisting messages to database
    - Performance tracking
    
    Args:
        request: The chat message request.
        service_name: The internal service name (e.g., "langchain").
        method_name: The display name of the method (e.g., "LangChain").
        request_obj: The FastAPI request object for accessing request state.
        db: The database session.
        
    Returns:
        A ChatResponse containing the AI response, conversation details,
        and performance metrics.
        
    Raises:
        HTTPException: 404 if specified conversation not found.
        Any exceptions from the AI service.
        
    Examples:
        >>> response = await handle_chat_message(
        ...     request=ChatMessageRequest(message="Hello"),
        ...     service_name="langchain",
        ...     method_name="LangChain",
        ...     request_obj=request,
        ...     db=session
        ... )
    """
    start_time = time.time()
    request_id = getattr(request_obj.state, 'request_id', None)
    
    logger.info("Chat message processing started",
               method=service_name,
               message_length=len(request.message),
               conversation_id=request.conversation_id,
               has_existing_conversation=bool(request.conversation_id),
               request_id=request_id)
    
    # Get or create conversation
    conversation = None
    conversation_history = []
    db_load_start = time.time()
    
    if request.conversation_id:
        logger.debug("Loading existing conversation", 
                    conversation_id=request.conversation_id)
        
        # Load existing conversation
        conversation = db.query(ChatConversation).filter(
            ChatConversation.id == request.conversation_id
        ).first()
        
        if not conversation:
            logger.warning("Conversation not found", 
                          conversation_id=request.conversation_id,
                          request_id=request_id)
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Load conversation history
        messages = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conversation.id
        ).order_by(ChatMessage.created_at).all()
        
        conversation_history = [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]
        
        db_load_time = (time.time() - db_load_start) * 1000
        total_context_chars = sum(len(msg["content"]) for msg in conversation_history)
        
        logger.info("Conversation history loaded", 
                   conversation_id=request.conversation_id,
                   message_count=len(conversation_history),
                   total_context_chars=total_context_chars,
                   db_load_time_ms=round(db_load_time, 2),
                   request_id=request_id)
        
        # Warn about large contexts
        if total_context_chars > 8000:
            logger.warning("Large conversation context detected",
                          conversation_id=request.conversation_id,
                          total_context_chars=total_context_chars,
                          message_count=len(conversation_history),
                          request_id=request_id)
    else:
        logger.debug("Creating new conversation")
        
        # Create new conversation
        model_info = get_model_info()
        conversation = ChatConversation(
            title=generate_conversation_title(request.message),
            method=service_name,
            provider=model_info["provider"],
            model=model_info["model"]
        )
        db.add(conversation)
        db.flush()  # Get the ID
        
        db_load_time = (time.time() - db_load_start) * 1000
        logger.info("New conversation created", 
                   conversation_id=conversation.id,
                   title=conversation.title,
                   db_create_time_ms=round(db_load_time, 2),
                   request_id=request_id)
    
    # Save user message
    user_message = ChatMessage(
        conversation_id=conversation.id,
        role="user",
        content=request.message,
        request_id=getattr(request_obj.state, 'request_id', None)
    )
    db.add(user_message)
    
    # Generate AI response
    ai_start_time = time.time()
    logger.debug("Starting AI response generation", 
                service=service_name,
                context_length=len(conversation_history))
    
    service = get_chat_service(service_name)
    ai_response, usage_info = await service.send_message(request.message, conversation_history)
    
    ai_generation_time = (time.time() - ai_start_time) * 1000
    
    logger.info("AI response generated", 
               service=service_name,
               response_length=len(ai_response),
               ai_generation_time_ms=round(ai_generation_time, 2),
               input_tokens=usage_info["input_tokens"],
               output_tokens=usage_info["output_tokens"],
               total_tokens=usage_info["total_tokens"],
               tokens_per_second=round(usage_info["output_tokens"] / (ai_generation_time / 1000), 2) if ai_generation_time > 0 else 0,
               conversation_id=conversation.id,
               request_id=request_id)
    
    # Save messages to database
    db_save_start = time.time()
    logger.debug("Saving messages to database")
    
    # Save AI message with token information
    ai_message = ChatMessage(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_response,
        generation_time_ms=round(ai_generation_time, 2),
        input_tokens=usage_info["input_tokens"],
        output_tokens=usage_info["output_tokens"],
        total_tokens=usage_info["total_tokens"],
        request_id=request_id,
        # Cost tracking fields
        estimated_cost_usd=usage_info["estimated_cost_usd"],
        input_cost_per_1k_tokens=usage_info["input_cost_per_1k_tokens"],
        output_cost_per_1k_tokens=usage_info["output_cost_per_1k_tokens"]
    )
    db.add(ai_message)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(conversation)
    db.refresh(ai_message)
    
    db_save_time = (time.time() - db_save_start) * 1000
    total_time = (time.time() - start_time) * 1000
    
    # Load full conversation with messages for response
    full_conversation = db.query(ChatConversation).filter(
        ChatConversation.id == conversation.id
    ).first()
    
    # Final performance logging
    logger.info("Chat message processing completed", 
               service=service_name,
               conversation_id=conversation.id,
               message_id=ai_message.id,
               total_time_ms=round(total_time, 2),
               ai_generation_time_ms=round(ai_generation_time, 2),
               db_operations_time_ms=round((db_load_time if 'db_load_time' in locals() else 0) + db_save_time, 2),
               ai_percentage=round((ai_generation_time / total_time) * 100, 1) if total_time > 0 else 0,
               db_percentage=round(((db_load_time if 'db_load_time' in locals() else 0) + db_save_time) / total_time * 100, 1) if total_time > 0 else 0,
               tokens_per_second=round(usage_info["output_tokens"] / (ai_generation_time / 1000), 2) if ai_generation_time > 0 else 0,
               total_tokens=usage_info["total_tokens"],
               conversation_length=len(full_conversation.messages) if full_conversation else 0,
               request_id=request_id)
    
    return ChatResponse(
        conversation=ChatConversationResponse.from_orm(full_conversation),
        message=ChatMessageResponse.from_orm(ai_message),
        request_id=request_id
    )

@router.get("/conversations", response_model=List[ChatConversationList])
async def get_conversations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get list of chat conversations.
    
    Retrieves a paginated list of chat conversations ordered by
    most recently updated. Includes message count and last message
    preview for each conversation.
    
    Args:
        skip: Number of conversations to skip. Defaults to 0.
        limit: Maximum number of conversations to return. Defaults to 20.
        db: Database session (injected).
        
    Returns:
        List of ChatConversationList objects with conversation summaries.
        
    Examples:
        >>> GET /api/chat/conversations
        [
            {
                "id": 1,
                "title": "Hello, can you help me?",
                "method": "langchain",
                "message_count": 10,
                "last_message_preview": "Sure, I'd be happy to help...",
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:30:00"
            }
        ]
    """
    conversations = db.query(ChatConversation).order_by(
        desc(ChatConversation.updated_at)
    ).offset(skip).limit(limit).all()
    
    result = []
    for conv in conversations:
        # Get message count
        message_count = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conv.id
        ).count()
        
        # Get last message preview
        last_message = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conv.id
        ).order_by(desc(ChatMessage.created_at)).first()
        
        last_message_preview = None
        if last_message:
            preview = last_message.content[:100]
            if len(last_message.content) > 100:
                preview += "..."
            last_message_preview = preview
        
        result.append(ChatConversationList(
            id=conv.id,
            title=conv.title,
            method=conv.method,
            model=conv.model,
            message_count=message_count,
            last_message_preview=last_message_preview,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat()
        ))
    
    return result

@router.get("/conversations/{conversation_id}", response_model=ChatConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all messages.
    
    Retrieves complete conversation details including all messages
    in chronological order.
    
    Args:
        conversation_id: The unique identifier of the conversation.
        db: Database session (injected).
        
    Returns:
        ChatConversationResponse with full conversation history.
        
    Raises:
        HTTPException: 404 if conversation not found.
        
    Examples:
        >>> GET /api/chat/conversations/123
        {
            "id": 123,
            "title": "Technical discussion",
            "method": "langchain",
            "messages": [
                {"role": "user", "content": "What is Python?", ...},
                {"role": "assistant", "content": "Python is...", ...}
            ],
            ...
        }
    """
    conversation = db.query(ChatConversation).filter(
        ChatConversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ChatConversationResponse.from_orm(conversation)

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages.
    
    Permanently removes a conversation and all associated messages
    from the database. This action cannot be undone.
    
    Args:
        conversation_id: The unique identifier of the conversation to delete.
        db: Database session (injected).
        
    Returns:
        Success message confirming deletion.
        
    Raises:
        HTTPException: 404 if conversation not found.
        
    Examples:
        >>> DELETE /api/chat/conversations/123
        {"message": "Conversation deleted successfully"}
    """
    conversation = db.query(ChatConversation).filter(
        ChatConversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}