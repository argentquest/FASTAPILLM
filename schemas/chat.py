from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessageRequest(BaseModel):
    """Request model for sending a chat message"""
    message: str = Field(..., min_length=1, max_length=2000, description="The message content")
    conversation_id: Optional[int] = Field(None, description="ID of existing conversation, or None for new")


class ChatMessageResponse(BaseModel):
    """Response model for chat message"""
    id: int
    role: str
    content: str
    generation_time_ms: Optional[float]
    input_tokens: Optional[int]
    output_tokens: Optional[int] 
    total_tokens: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ChatConversationResponse(BaseModel):
    """Response model for chat conversation"""
    id: int
    title: str
    method: str
    provider: Optional[str]
    model: Optional[str]
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessageResponse]

    class Config:
        from_attributes = True


class ChatConversationList(BaseModel):
    """List view of chat conversations"""
    id: int
    title: str
    method: str
    provider: Optional[str]
    message_count: int
    last_message_preview: Optional[str]
    created_at: str
    updated_at: str


class ChatResponse(BaseModel):
    """Response model for chat API"""
    conversation: ChatConversationResponse
    message: ChatMessageResponse
    request_id: Optional[str]