from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CostSummary(BaseModel):
    """Summary of cost usage across all services"""
    total_cost_usd: float = Field(..., description="Total cost across all requests")
    total_requests: int = Field(..., description="Total number of requests")
    total_tokens: int = Field(..., description="Total tokens used")
    average_cost_per_request: float = Field(..., description="Average cost per request")
    average_tokens_per_request: float = Field(..., description="Average tokens per request")


class CostByMethod(BaseModel):
    """Cost breakdown by AI method"""
    method: str = Field(..., description="AI method name (semantic_kernel, langchain, langgraph)")
    total_cost_usd: float = Field(..., description="Total cost for this method")
    request_count: int = Field(..., description="Number of requests using this method")
    total_tokens: int = Field(..., description="Total tokens used by this method")
    average_cost_per_request: float = Field(..., description="Average cost per request for this method")


class CostByModel(BaseModel):
    """Cost breakdown by AI model"""
    model: str = Field(..., description="AI model name")
    total_cost_usd: float = Field(..., description="Total cost for this model")
    request_count: int = Field(..., description="Number of requests using this model")
    total_tokens: int = Field(..., description="Total tokens used by this model")
    average_cost_per_request: float = Field(..., description="Average cost per request for this model")


class DailyCostUsage(BaseModel):
    """Daily cost usage statistics"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    total_cost_usd: float = Field(..., description="Total cost for this date")
    request_count: int = Field(..., description="Number of requests on this date")
    total_tokens: int = Field(..., description="Total tokens used on this date")


class RecentRequest(BaseModel):
    """Recent high-cost or notable requests"""
    id: int = Field(..., description="Request ID")
    type: str = Field(..., description="Request type (story or chat)")
    method: str = Field(..., description="AI method used")
    model: str = Field(..., description="AI model used")
    cost_usd: float = Field(..., description="Cost of this request")
    tokens_used: int = Field(..., description="Total tokens used")
    created_at: datetime = Field(..., description="When the request was made")
    primary_character: Optional[str] = Field(None, description="Primary character (for stories)")
    conversation_title: Optional[str] = Field(None, description="Conversation title (for chat)")


class CostUsageResponse(BaseModel):
    """Complete cost usage analytics response"""
    summary: CostSummary = Field(..., description="Overall cost summary")
    by_method: List[CostByMethod] = Field(..., description="Cost breakdown by AI method")
    by_model: List[CostByModel] = Field(..., description="Cost breakdown by AI model")
    daily_usage: List[DailyCostUsage] = Field(..., description="Daily cost usage over time")
    recent_requests: List[RecentRequest] = Field(..., description="Recent high-cost requests")
    date_range: str = Field(..., description="Date range for the analytics")