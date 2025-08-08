from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    file_id: str = Field(..., description="Unique identifier for the uploaded file")
    original_filename: str = Field(..., description="Original filename")
    file_type: str = Field(..., description="File extension (pdf, csv, txt, json)")
    file_size_bytes: int = Field(..., description="File size in bytes")
    processed_content_length: int = Field(..., description="Length of processed content")
    processing_time_ms: float = Field(..., description="Time taken to process the file")
    status: str = Field(..., description="Processing status (success, error)")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")


class ContextPromptRequest(BaseModel):
    """Request model for context prompt execution"""
    file_ids: List[str] = Field(..., min_items=1, description="IDs of the uploaded files to use as context")
    system_prompt: str = Field(..., min_length=1, description="System prompt containing [context] placeholder")
    user_prompt: str = Field(..., min_length=1, description="User's input prompt")
    method: str = Field(default="langchain", description="AI method to use (semantic_kernel, langchain, langgraph)")


class ContextPromptResponse(BaseModel):
    """Response model for context prompt execution"""
    id: int = Field(..., description="Execution ID")
    llm_response: str = Field(..., description="Generated response from LLM")
    
    # File information
    original_filename: str = Field(..., description="Original uploaded filename")
    file_type: str = Field(..., description="File type processed")
    processed_content_length: int = Field(..., description="Length of processed content")
    
    # Prompt information
    final_prompt_length: int = Field(..., description="Length of final assembled prompt")
    
    # Performance metrics
    file_processing_time_ms: float = Field(..., description="Time taken to process file")
    llm_execution_time_ms: float = Field(..., description="Time taken for LLM execution")
    total_execution_time_ms: float = Field(..., description="Total execution time")
    
    # Token usage and cost
    input_tokens: int = Field(..., description="Number of input tokens")
    output_tokens: int = Field(..., description="Number of output tokens")
    total_tokens: int = Field(..., description="Total tokens used")
    estimated_cost_usd: float = Field(..., description="Estimated cost in USD")
    input_cost_per_1k_tokens: float = Field(..., description="Cost per 1000 input tokens")
    output_cost_per_1k_tokens: float = Field(..., description="Cost per 1000 output tokens")
    
    # Metadata
    method: str = Field(..., description="AI method used")
    model: str = Field(..., description="Model used")
    request_id: Optional[str] = Field(None, description="Request tracking ID")
    created_at: datetime = Field(..., description="Execution timestamp")
    
    class Config:
        from_attributes = True


class ContextExecutionList(BaseModel):
    """List view of context prompt executions"""
    id: int
    original_filename: str
    file_type: str
    method: str
    model: Optional[str]
    estimated_cost_usd: Optional[float]
    total_tokens: Optional[int]
    total_execution_time_ms: Optional[float]
    created_at: str
    status: str