from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta

from schemas.cost import (
    CostUsageResponse, CostSummary, CostByMethod, CostByModel, 
    DailyCostUsage, RecentRequest
)
from pydantic import BaseModel
from typing import Literal
from database import get_db, Story, ChatMessage, ChatConversation, ContextPromptExecution
from logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/cost", tags=["cost"])


class Transaction(BaseModel):
    """Individual transaction details"""
    id: int
    type: Literal["story", "chat", "context"]
    method: str
    model: str
    created_at: datetime
    transaction_guid: Optional[str] = None
    request_id: Optional[str] = None
    primary_character: Optional[str] = None
    secondary_character: Optional[str] = None
    conversation_title: Optional[str] = None
    content_preview: Optional[str] = None
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    estimated_cost_usd: Optional[float]
    generation_time_ms: Optional[float]


class TransactionsResponse(BaseModel):
    """Response containing all transactions"""
    transactions: List[Transaction]
    total_cost: float
    transaction_count: int


@router.get("/usage", response_model=CostUsageResponse)
async def get_cost_usage(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get comprehensive cost usage analytics.
    
    Provides detailed cost analytics including:
    - Overall cost summary
    - Cost breakdown by AI method (semantic_kernel, langchain, langgraph)
    - Cost breakdown by AI model
    - Daily usage trends
    - Recent high-cost requests
    
    Args:
        days: Number of days to analyze (1-365). Defaults to 30.
        db: Database session (injected).
        
    Returns:
        CostUsageResponse with comprehensive cost analytics.
        
    Examples:
        >>> GET /api/cost/usage
        >>> GET /api/cost/usage?days=7  # Last 7 days
        >>> GET /api/cost/usage?days=90  # Last 3 months
    """
    logger.info("Cost usage analytics requested", days=days)
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    
    logger.debug("Analyzing cost data", 
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat())
    
    # Get story costs
    story_costs = db.query(
        func.coalesce(func.sum(Story.estimated_cost_usd), 0).label('total_cost'),
        func.count(Story.id).label('request_count'),
        func.coalesce(func.sum(Story.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            Story.created_at >= start_date,
            Story.created_at <= end_date,
            Story.estimated_cost_usd.isnot(None)
        )
    ).first()
    
    # Get chat costs
    chat_costs = db.query(
        func.coalesce(func.sum(ChatMessage.estimated_cost_usd), 0).label('total_cost'),
        func.count(ChatMessage.id).label('request_count'),
        func.coalesce(func.sum(ChatMessage.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            ChatMessage.created_at >= start_date,
            ChatMessage.created_at <= end_date,
            ChatMessage.role == 'assistant',  # Only count AI responses
            ChatMessage.estimated_cost_usd.isnot(None)
        )
    ).first()
    
    # Get context prompt costs
    context_costs = db.query(
        func.coalesce(func.sum(ContextPromptExecution.estimated_cost_usd), 0).label('total_cost'),
        func.count(ContextPromptExecution.id).label('request_count'),
        func.coalesce(func.sum(ContextPromptExecution.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            ContextPromptExecution.created_at >= start_date,
            ContextPromptExecution.created_at <= end_date,
            ContextPromptExecution.status == 'completed',
            ContextPromptExecution.estimated_cost_usd.isnot(None)
        )
    ).first()
    
    # Calculate overall summary
    total_cost = (float(story_costs.total_cost or 0) + 
                  float(chat_costs.total_cost or 0) + 
                  float(context_costs.total_cost or 0))
    total_requests = ((story_costs.request_count or 0) + 
                      (chat_costs.request_count or 0) + 
                      (context_costs.request_count or 0))
    total_tokens = ((story_costs.total_tokens or 0) + 
                    (chat_costs.total_tokens or 0) + 
                    (context_costs.total_tokens or 0))
    
    summary = CostSummary(
        total_cost_usd=round(total_cost, 6),
        total_requests=total_requests,
        total_tokens=total_tokens,
        average_cost_per_request=round(total_cost / total_requests, 6) if total_requests > 0 else 0.0,
        average_tokens_per_request=round(total_tokens / total_requests, 2) if total_requests > 0 else 0.0
    )
    
    logger.info("Cost summary calculated",
               total_cost_usd=summary.total_cost_usd,
               total_requests=summary.total_requests,
               total_tokens=summary.total_tokens)
    
    # Get cost breakdown by method
    story_by_method = db.query(
        Story.method,
        func.coalesce(func.sum(Story.estimated_cost_usd), 0).label('total_cost'),
        func.count(Story.id).label('request_count'),
        func.coalesce(func.sum(Story.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            Story.created_at >= start_date,
            Story.created_at <= end_date,
            Story.estimated_cost_usd.isnot(None)
        )
    ).group_by(Story.method).all()
    
    chat_by_method = db.query(
        ChatConversation.method,
        func.coalesce(func.sum(ChatMessage.estimated_cost_usd), 0).label('total_cost'),
        func.count(ChatMessage.id).label('request_count'),
        func.coalesce(func.sum(ChatMessage.total_tokens), 0).label('total_tokens')
    ).join(ChatMessage).filter(
        and_(
            ChatMessage.created_at >= start_date,
            ChatMessage.created_at <= end_date,
            ChatMessage.role == 'assistant',
            ChatMessage.estimated_cost_usd.isnot(None)
        )
    ).group_by(ChatConversation.method).all()
    
    context_by_method = db.query(
        ContextPromptExecution.method,
        func.coalesce(func.sum(ContextPromptExecution.estimated_cost_usd), 0).label('total_cost'),
        func.count(ContextPromptExecution.id).label('request_count'),
        func.coalesce(func.sum(ContextPromptExecution.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            ContextPromptExecution.created_at >= start_date,
            ContextPromptExecution.created_at <= end_date,
            ContextPromptExecution.status == 'completed',
            ContextPromptExecution.estimated_cost_usd.isnot(None)
        )
    ).group_by(ContextPromptExecution.method).all()
    
    # Combine method costs
    method_costs = {}
    for row in story_by_method:
        method_costs[row.method] = {
            'total_cost': float(row.total_cost or 0),
            'request_count': row.request_count or 0,
            'total_tokens': row.total_tokens or 0
        }
    
    for row in chat_by_method:
        if row.method in method_costs:
            method_costs[row.method]['total_cost'] += float(row.total_cost or 0)
            method_costs[row.method]['request_count'] += row.request_count or 0
            method_costs[row.method]['total_tokens'] += row.total_tokens or 0
        else:
            method_costs[row.method] = {
                'total_cost': float(row.total_cost or 0),
                'request_count': row.request_count or 0,
                'total_tokens': row.total_tokens or 0
            }
    
    for row in context_by_method:
        if row.method in method_costs:
            method_costs[row.method]['total_cost'] += float(row.total_cost or 0)
            method_costs[row.method]['request_count'] += row.request_count or 0
            method_costs[row.method]['total_tokens'] += row.total_tokens or 0
        else:
            method_costs[row.method] = {
                'total_cost': float(row.total_cost or 0),
                'request_count': row.request_count or 0,
                'total_tokens': row.total_tokens or 0
            }
    
    by_method = [
        CostByMethod(
            method=method,
            total_cost_usd=round(data['total_cost'], 6),
            request_count=data['request_count'],
            total_tokens=data['total_tokens'],
            average_cost_per_request=round(data['total_cost'] / data['request_count'], 6) if data['request_count'] > 0 else 0.0
        )
        for method, data in method_costs.items()
    ]
    by_method.sort(key=lambda x: x.total_cost_usd, reverse=True)
    
    # Get cost breakdown by model
    story_by_model = db.query(
        Story.model,
        func.coalesce(func.sum(Story.estimated_cost_usd), 0).label('total_cost'),
        func.count(Story.id).label('request_count'),
        func.coalesce(func.sum(Story.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            Story.created_at >= start_date,
            Story.created_at <= end_date,
            Story.estimated_cost_usd.isnot(None)
        )
    ).group_by(Story.model).all()
    
    chat_by_model = db.query(
        ChatConversation.model,
        func.coalesce(func.sum(ChatMessage.estimated_cost_usd), 0).label('total_cost'),
        func.count(ChatMessage.id).label('request_count'),
        func.coalesce(func.sum(ChatMessage.total_tokens), 0).label('total_tokens')
    ).join(ChatMessage).filter(
        and_(
            ChatMessage.created_at >= start_date,
            ChatMessage.created_at <= end_date,
            ChatMessage.role == 'assistant',
            ChatMessage.estimated_cost_usd.isnot(None)
        )
    ).group_by(ChatConversation.model).all()
    
    context_by_model = db.query(
        ContextPromptExecution.model,
        func.coalesce(func.sum(ContextPromptExecution.estimated_cost_usd), 0).label('total_cost'),
        func.count(ContextPromptExecution.id).label('request_count'),
        func.coalesce(func.sum(ContextPromptExecution.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            ContextPromptExecution.created_at >= start_date,
            ContextPromptExecution.created_at <= end_date,
            ContextPromptExecution.status == 'completed',
            ContextPromptExecution.estimated_cost_usd.isnot(None)
        )
    ).group_by(ContextPromptExecution.model).all()
    
    # Combine model costs
    model_costs = {}
    for row in story_by_model:
        if row.model:  # Skip null models
            model_costs[row.model] = {
                'total_cost': float(row.total_cost or 0),
                'request_count': row.request_count or 0,
                'total_tokens': row.total_tokens or 0
            }
    
    for row in chat_by_model:
        if row.model:  # Skip null models
            if row.model in model_costs:
                model_costs[row.model]['total_cost'] += float(row.total_cost or 0)
                model_costs[row.model]['request_count'] += row.request_count or 0
                model_costs[row.model]['total_tokens'] += row.total_tokens or 0
            else:
                model_costs[row.model] = {
                    'total_cost': float(row.total_cost or 0),
                    'request_count': row.request_count or 0,
                    'total_tokens': row.total_tokens or 0
                }
    
    for row in context_by_model:
        if row.model:  # Skip null models
            if row.model in model_costs:
                model_costs[row.model]['total_cost'] += float(row.total_cost or 0)
                model_costs[row.model]['request_count'] += row.request_count or 0
                model_costs[row.model]['total_tokens'] += row.total_tokens or 0
            else:
                model_costs[row.model] = {
                    'total_cost': float(row.total_cost or 0),
                    'request_count': row.request_count or 0,
                    'total_tokens': row.total_tokens or 0
                }
    
    by_model = [
        CostByModel(
            model=model,
            total_cost_usd=round(data['total_cost'], 6),
            request_count=data['request_count'],
            total_tokens=data['total_tokens'],
            average_cost_per_request=round(data['total_cost'] / data['request_count'], 6) if data['request_count'] > 0 else 0.0
        )
        for model, data in model_costs.items()
    ]
    by_model.sort(key=lambda x: x.total_cost_usd, reverse=True)
    
    # Get daily usage (last 14 days for better visualization)
    daily_days = min(days, 14)
    daily_start = end_date - timedelta(days=daily_days)
    
    # Story daily costs
    story_daily = db.query(
        func.date(Story.created_at).label('date'),
        func.coalesce(func.sum(Story.estimated_cost_usd), 0).label('total_cost'),
        func.count(Story.id).label('request_count'),
        func.coalesce(func.sum(Story.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            Story.created_at >= daily_start,
            Story.created_at <= end_date,
            Story.estimated_cost_usd.isnot(None)
        )
    ).group_by(func.date(Story.created_at)).all()
    
    # Chat daily costs
    chat_daily = db.query(
        func.date(ChatMessage.created_at).label('date'),
        func.coalesce(func.sum(ChatMessage.estimated_cost_usd), 0).label('total_cost'),
        func.count(ChatMessage.id).label('request_count'),
        func.coalesce(func.sum(ChatMessage.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            ChatMessage.created_at >= daily_start,
            ChatMessage.created_at <= end_date,
            ChatMessage.role == 'assistant',
            ChatMessage.estimated_cost_usd.isnot(None)
        )
    ).group_by(func.date(ChatMessage.created_at)).all()
    
    # Combine daily costs
    daily_costs = {}
    for row in story_daily:
        # SQLite date() function returns string, not date object
        date_str = str(row.date) if isinstance(row.date, str) else row.date.strftime('%Y-%m-%d')
        daily_costs[date_str] = {
            'total_cost': float(row.total_cost or 0),
            'request_count': row.request_count or 0,
            'total_tokens': row.total_tokens or 0
        }
    
    for row in chat_daily:
        # SQLite date() function returns string, not date object
        date_str = str(row.date) if isinstance(row.date, str) else row.date.strftime('%Y-%m-%d')
        if date_str in daily_costs:
            daily_costs[date_str]['total_cost'] += float(row.total_cost or 0)
            daily_costs[date_str]['request_count'] += row.request_count or 0
            daily_costs[date_str]['total_tokens'] += row.total_tokens or 0
        else:
            daily_costs[date_str] = {
                'total_cost': float(row.total_cost or 0),
                'request_count': row.request_count or 0,
                'total_tokens': row.total_tokens or 0
            }
    
    # Fill in missing dates with zero costs
    current_date = daily_start.date()
    end_date_only = end_date.date()
    daily_usage = []
    
    while current_date <= end_date_only:
        date_str = current_date.strftime('%Y-%m-%d')
        if date_str in daily_costs:
            daily_usage.append(DailyCostUsage(
                date=date_str,
                total_cost_usd=round(daily_costs[date_str]['total_cost'], 6),
                request_count=daily_costs[date_str]['request_count'],
                total_tokens=daily_costs[date_str]['total_tokens']
            ))
        else:
            daily_usage.append(DailyCostUsage(
                date=date_str,
                total_cost_usd=0.0,
                request_count=0,
                total_tokens=0
            ))
        current_date += timedelta(days=1)
    
    # Get recent high-cost requests (top 10)
    recent_stories = db.query(Story).filter(
        and_(
            Story.created_at >= start_date,
            Story.created_at <= end_date,
            Story.estimated_cost_usd.isnot(None)
        )
    ).order_by(desc(Story.estimated_cost_usd)).limit(5).all()
    
    recent_chats = db.query(ChatMessage, ChatConversation.title).join(
        ChatConversation
    ).filter(
        and_(
            ChatMessage.created_at >= start_date,
            ChatMessage.created_at <= end_date,
            ChatMessage.role == 'assistant',
            ChatMessage.estimated_cost_usd.isnot(None)
        )
    ).order_by(desc(ChatMessage.estimated_cost_usd)).limit(5).all()
    
    recent_context = db.query(ContextPromptExecution).filter(
        and_(
            ContextPromptExecution.created_at >= start_date,
            ContextPromptExecution.created_at <= end_date,
            ContextPromptExecution.status == 'completed',
            ContextPromptExecution.estimated_cost_usd.isnot(None)
        )
    ).order_by(desc(ContextPromptExecution.estimated_cost_usd)).limit(5).all()
    
    recent_requests = []
    
    # Add story requests
    for story in recent_stories:
        recent_requests.append(RecentRequest(
            id=story.id,
            type="story",
            method=story.method,
            model=story.model or "unknown",
            cost_usd=float(story.estimated_cost_usd),
            tokens_used=story.total_tokens or 0,
            created_at=story.created_at,
            primary_character=story.primary_character,
            conversation_title=None
        ))
    
    # Add chat requests
    for message, conv_title in recent_chats:
        recent_requests.append(RecentRequest(
            id=message.id,
            type="chat",
            method=message.conversation.method,
            model=message.conversation.model or "unknown",
            cost_usd=float(message.estimated_cost_usd),
            tokens_used=message.total_tokens or 0,
            created_at=message.created_at,
            primary_character=None,
            conversation_title=conv_title
        ))
    
    # Add context prompt requests
    for context in recent_context:
        recent_requests.append(RecentRequest(
            id=context.id,
            type="context",
            method=context.method,
            model=context.model or "unknown",
            cost_usd=float(context.estimated_cost_usd),
            tokens_used=context.total_tokens or 0,
            created_at=context.created_at,
            primary_character=context.original_filename,  # Use filename as identifier
            conversation_title=None
        ))
    
    # Sort by cost and take top 10
    recent_requests.sort(key=lambda x: x.cost_usd, reverse=True)
    recent_requests = recent_requests[:10]
    
    logger.info("Cost usage analytics completed",
               methods_analyzed=len(by_method),
               models_analyzed=len(by_model),
               daily_points=len(daily_usage),
               recent_requests=len(recent_requests))
    
    return CostUsageResponse(
        summary=summary,
        by_method=by_method,
        by_model=by_model,
        daily_usage=daily_usage,
        recent_requests=recent_requests,
        date_range=date_range
    )


@router.get("/summary", response_model=CostSummary)
async def get_cost_summary(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get a quick cost summary.
    
    Provides just the overall cost summary without detailed breakdowns.
    Useful for dashboard widgets or quick cost checks.
    
    Args:
        days: Number of days to analyze (1-365). Defaults to 30.
        db: Database session (injected).
        
    Returns:
        CostSummary with basic cost metrics.
    """
    logger.info("Cost summary requested", days=days)
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get story costs
    story_costs = db.query(
        func.coalesce(func.sum(Story.estimated_cost_usd), 0).label('total_cost'),
        func.count(Story.id).label('request_count'),
        func.coalesce(func.sum(Story.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            Story.created_at >= start_date,
            Story.created_at <= end_date,
            Story.estimated_cost_usd.isnot(None)
        )
    ).first()
    
    # Get chat costs
    chat_costs = db.query(
        func.coalesce(func.sum(ChatMessage.estimated_cost_usd), 0).label('total_cost'),
        func.count(ChatMessage.id).label('request_count'),
        func.coalesce(func.sum(ChatMessage.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            ChatMessage.created_at >= start_date,
            ChatMessage.created_at <= end_date,
            ChatMessage.role == 'assistant',
            ChatMessage.estimated_cost_usd.isnot(None)
        )
    ).first()
    
    # Get context prompt costs
    context_costs = db.query(
        func.coalesce(func.sum(ContextPromptExecution.estimated_cost_usd), 0).label('total_cost'),
        func.count(ContextPromptExecution.id).label('request_count'),
        func.coalesce(func.sum(ContextPromptExecution.total_tokens), 0).label('total_tokens')
    ).filter(
        and_(
            ContextPromptExecution.created_at >= start_date,
            ContextPromptExecution.created_at <= end_date,
            ContextPromptExecution.status == 'completed',
            ContextPromptExecution.estimated_cost_usd.isnot(None)
        )
    ).first()
    
    # Calculate summary
    total_cost = (float(story_costs.total_cost or 0) + 
                  float(chat_costs.total_cost or 0) + 
                  float(context_costs.total_cost or 0))
    total_requests = ((story_costs.request_count or 0) + 
                      (chat_costs.request_count or 0) + 
                      (context_costs.request_count or 0))
    total_tokens = ((story_costs.total_tokens or 0) + 
                    (chat_costs.total_tokens or 0) + 
                    (context_costs.total_tokens or 0))
    
    return CostSummary(
        total_cost_usd=round(total_cost, 6),
        total_requests=total_requests,
        total_tokens=total_tokens,
        average_cost_per_request=round(total_cost / total_requests, 6) if total_requests > 0 else 0.0,
        average_tokens_per_request=round(total_tokens / total_requests, 2) if total_requests > 0 else 0.0
    )


@router.delete("/usage")
async def clear_all_cost_data(
    db: Session = Depends(get_db)
):
    """Clear all cost tracking data.
    
    Removes all cost data from stories, chat messages, and context executions.
    This action cannot be undone.
    
    Returns:
        Dict with success message and count of cleared records.
    """
    logger.info("Clear all cost data request received")
    
    try:
        # Count records before deletion
        story_count = db.query(Story).count()
        chat_message_count = db.query(ChatMessage).count()
        chat_conversation_count = db.query(ChatConversation).count()
        context_count = db.query(ContextPromptExecution).count()
        total_count = story_count + chat_message_count + chat_conversation_count + context_count
        
        # Delete all records with cost data
        # For conversations, let cascade handle the messages automatically
        deleted_conversations = db.query(ChatConversation).delete()
        deleted_contexts = db.query(ContextPromptExecution).delete()
        deleted_stories = db.query(Story).delete()
        
        db.commit()
        
        # After commit, count remaining records to verify complete deletion
        remaining_stories = db.query(Story).count()
        remaining_conversations = db.query(ChatConversation).count()
        remaining_messages = db.query(ChatMessage).count()
        remaining_contexts = db.query(ContextPromptExecution).count()
        
        actual_deleted = deleted_conversations + deleted_contexts + deleted_stories
        
        logger.info("All cost data cleared successfully", 
                   stories_deleted=deleted_stories,
                   chat_conversations_deleted=deleted_conversations,
                   contexts_deleted=deleted_contexts,
                   total_deleted=actual_deleted,
                   remaining_stories=remaining_stories,
                   remaining_conversations=remaining_conversations,
                   remaining_messages=remaining_messages,
                   remaining_contexts=remaining_contexts)
        
        if remaining_stories == 0 and remaining_conversations == 0 and remaining_messages == 0 and remaining_contexts == 0:
            return {
                "message": f"Successfully cleared all cost records (Stories: {deleted_stories}, Conversations: {deleted_conversations}, Contexts: {deleted_contexts})",
                "deleted_count": actual_deleted
            }
        else:
            return {
                "message": f"Partially cleared cost records. Remaining: {remaining_stories + remaining_conversations + remaining_messages + remaining_contexts} records",
                "deleted_count": actual_deleted,
                "warning": f"Some records remain: Stories: {remaining_stories}, Conversations: {remaining_conversations}, Messages: {remaining_messages}, Contexts: {remaining_contexts}"
            }
        
    except Exception as e:
        db.rollback()
        logger.error("Failed to clear cost data", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cost data: {str(e)}"
        )


@router.get("/transactions", response_model=TransactionsResponse)
async def get_all_transactions(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get all individual transactions (not aggregated by day).
    
    Returns all AI API calls with their costs as individual transactions.
    """
    logger.info("All transactions requested", days=days)
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    transactions = []
    
    # Get all stories
    stories = db.query(Story).filter(
        and_(
            Story.created_at >= start_date,
            Story.created_at <= end_date,
            Story.estimated_cost_usd.isnot(None)
        )
    ).order_by(desc(Story.created_at)).all()
    
    for story in stories:
        transactions.append(Transaction(
            id=story.id,
            type="story",
            method=story.method,
            model=story.model or "unknown",
            created_at=story.created_at,
            transaction_guid=story.transaction_guid,
            request_id=story.request_id,
            primary_character=story.primary_character,
            secondary_character=story.secondary_character,
            content_preview=story.story_content[:100] + "..." if story.story_content else None,
            input_tokens=story.input_tokens,
            output_tokens=story.output_tokens,
            total_tokens=story.total_tokens,
            estimated_cost_usd=float(story.estimated_cost_usd) if story.estimated_cost_usd else 0,
            generation_time_ms=story.generation_time_ms
        ))
    
    # Get all chat messages
    chat_messages = db.query(ChatMessage, ChatConversation).join(
        ChatConversation
    ).filter(
        and_(
            ChatMessage.created_at >= start_date,
            ChatMessage.created_at <= end_date,
            ChatMessage.role == 'assistant',
            ChatMessage.estimated_cost_usd.isnot(None)
        )
    ).order_by(desc(ChatMessage.created_at)).all()
    
    for msg, conv in chat_messages:
        transactions.append(Transaction(
            id=msg.id,
            type="chat",
            method=conv.method,
            model=conv.model or "unknown",
            created_at=msg.created_at,
            transaction_guid=msg.transaction_guid,
            request_id=msg.request_id,
            conversation_title=conv.title,
            content_preview=msg.content[:100] + "..." if msg.content else None,
            input_tokens=msg.input_tokens,
            output_tokens=msg.output_tokens,
            total_tokens=msg.total_tokens,
            estimated_cost_usd=float(msg.estimated_cost_usd) if msg.estimated_cost_usd else 0,
            generation_time_ms=msg.generation_time_ms
        ))
    
    # Get all context executions
    context_executions = db.query(ContextPromptExecution).filter(
        and_(
            ContextPromptExecution.created_at >= start_date,
            ContextPromptExecution.created_at <= end_date,
            ContextPromptExecution.status == 'completed',
            ContextPromptExecution.estimated_cost_usd.isnot(None)
        )
    ).order_by(desc(ContextPromptExecution.created_at)).all()
    
    for context in context_executions:
        transactions.append(Transaction(
            id=context.id,
            type="context",
            method=context.method,
            model=context.model or "unknown",
            created_at=context.created_at,
            transaction_guid=context.transaction_guid,
            request_id=context.request_id,
            primary_character=context.original_filename,
            content_preview=context.llm_response[:100] + "..." if context.llm_response else None,
            input_tokens=context.input_tokens,
            output_tokens=context.output_tokens,
            total_tokens=context.total_tokens,
            estimated_cost_usd=float(context.estimated_cost_usd) if context.estimated_cost_usd else 0,
            generation_time_ms=context.total_execution_time_ms
        ))
    
    # Sort all transactions by date
    transactions.sort(key=lambda x: x.created_at, reverse=True)
    
    # Calculate total cost
    total_cost = sum(t.estimated_cost_usd for t in transactions)
    
    logger.info("Transactions fetched",
               transaction_count=len(transactions),
               total_cost=total_cost)
    
    return TransactionsResponse(
        transactions=transactions,
        total_cost=round(total_cost, 6),
        transaction_count=len(transactions)
    )
