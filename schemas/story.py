from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional, List
from datetime import datetime

from config import settings
from validation import validate_character_name


class StoryRequest(BaseModel):
    """Request model for story generation"""
    primary_character: str = Field(
        ...,
        min_length=settings.min_character_length,
        max_length=settings.max_character_length,
        description="Primary character in the story"
    )
    secondary_character: str = Field(
        ...,
        min_length=settings.min_character_length,
        max_length=settings.max_character_length,
        description="Secondary character in the story"
    )
    
    @field_validator('primary_character', 'secondary_character')
    @classmethod
    def validate_character(cls, v: str, info: ValidationInfo) -> str:
        """Validate and sanitize character names"""
        field_name = info.field_name.replace('_', ' ').title() if info.field_name else "character"
        return validate_character_name(v, field_name)
    
    @field_validator('secondary_character')
    @classmethod
    def characters_must_be_different(cls, v: str, info: ValidationInfo) -> str:
        """Ensure characters are different"""
        if info.data and 'primary_character' in info.data:
            if v.lower() == info.data['primary_character'].lower():
                raise ValueError("Primary and secondary characters must be different")
        return v


class StoryResponse(BaseModel):
    """Response model for story generation"""
    story: str = Field(..., description="Generated story content")
    combined_characters: str = Field(..., description="Combined character names")
    method: str = Field(..., description="AI framework used for generation")
    generation_time_ms: Optional[float] = Field(None, description="Time taken to generate the story")
    input_tokens: Optional[int] = Field(None, description="Number of input tokens used")
    output_tokens: Optional[int] = Field(None, description="Number of output tokens generated")
    total_tokens: Optional[int] = Field(None, description="Total tokens used")
    request_id: Optional[str] = Field(None, description="Unique request identifier")


class StoryDB(BaseModel):
    """Database representation of a story"""
    id: int
    primary_character: str
    secondary_character: str
    combined_characters: str
    story_content: str
    method: str
    provider: str
    model: str
    generation_time_ms: Optional[float]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    request_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class StoryList(BaseModel):
    """List view of a story with preview"""
    id: int
    primary_character: str
    secondary_character: str
    combined_characters: str
    story_preview: str
    method: str
    provider: str
    model: Optional[str]
    generation_time_ms: Optional[float]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    created_at: str