"""
Content Generation Service Module

This module provides the abstract base class for content generation services.
It extends BaseAIService with the generate_content method signature that
all content generation services must implement.

This separation allows:
- Chat services to extend BaseAIService directly without generate_content
- Context services to extend BaseAIService directly without generate_content
- Only content/story generation services need to implement generate_content
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any

from .base_ai_service import BaseAIService
from logging_config import get_logger

logger = get_logger(__name__)


class ContentGenerationService(BaseAIService, ABC):
    """Abstract base class for content generation services.
    
    This class extends BaseAIService with the specific contract for
    content generation services. All services that generate stories,
    articles, or other content should inherit from this class.
    
    Subclasses must implement the generate_content method to provide
    framework-specific content generation logic.
    
    Examples:
        >>> class MyContentService(ContentGenerationService):
        ...     async def generate_content(self, primary_input: str, secondary_input: str):
        ...         # Implementation here
        ...         pass
    """
    
    @abstractmethod
    async def generate_content(self, primary_input: str, secondary_input: str) -> Tuple[str, Dict[str, Any]]:
        """Generate content with the given inputs.
        
        Abstract method that must be implemented by subclasses to generate
        content using their specific approach (Semantic Kernel, LangChain, etc.).
        
        Args:
            primary_input: The main input parameter (e.g., main character).
            secondary_input: The secondary input parameter (e.g., secondary character).
            
        Returns:
            A tuple containing:
            - content: The generated content text
            - usage_info: Dictionary with token usage and timing information:
                - input_tokens: Number of tokens in the prompt
                - output_tokens: Number of tokens in the response
                - total_tokens: Sum of input and output tokens
                - execution_time_ms: API call duration in milliseconds
                - estimated_cost_usd: Estimated cost in USD
                - input_cost: Cost for input tokens
                - output_cost: Cost for output tokens
            
        Raises:
            Any exceptions from the underlying API calls.
        """
        pass
    
