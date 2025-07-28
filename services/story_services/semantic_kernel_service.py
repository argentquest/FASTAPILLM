from typing import List, Dict, Tuple, Any

from ..base_service import BaseService
from prompts.semantic_kernel_prompts import get_chat_messages
from logging_config import get_logger

logger = get_logger(__name__)

class SemanticKernelService(BaseService):
    """Story generation service using Semantic Kernel approach.
    
    This service implements story generation using Microsoft's Semantic
    Kernel framework approach. It uses structured prompts to generate
    cohesive stories featuring the provided characters.
    
    The service leverages the base class for API communication and adds
    Semantic Kernel-specific prompt engineering.
    
    Examples:
        >>> service = SemanticKernelService()
        >>> story, usage = await service.generate_story("Alice", "Bob")
        >>> print(f"Generated {len(story)} characters using {usage['total_tokens']} tokens")
    """
    
    async def generate_content(self, primary_input: str, secondary_input: str) -> Tuple[str, Dict[str, Any]]:
        """Generate content using Semantic Kernel prompts.
        
        Creates content featuring the two provided inputs using
        Semantic Kernel's prompt templates and structured approach.
        
        Args:
            primary_input: The main input parameter.
            secondary_input: The secondary input parameter.
            
        Returns:
            A tuple containing:
            - content: The generated content text
            - usage_info: Dictionary with token usage and timing information
            
        Raises:
            APIConnectionError: If unable to connect to the LLM API.
            APIRateLimitError: If API rate limits are exceeded.
            TimeoutError: If the API call exceeds the configured timeout.
            
        Examples:
            >>> service = SemanticKernelService()
            >>> content, usage = await service.generate_content("Alice", "Bob")
            >>> print(f"Generated {len(content)} characters using {usage['total_tokens']} tokens")
        """
        
        logger.info("Starting content generation",
                   service=self.service_name,
                   provider=self.provider_name,
                   primary_input=primary_input,
                   secondary_input=secondary_input)
        
        # Get the prompt messages
        messages = get_chat_messages(primary_input, secondary_input)
        
        # Generate the content
        content, usage_info = await self._call_api_with_retry(messages)
        
        logger.info("Content generation completed",
                   service=self.service_name,
                   content_length=len(content),
                   generation_time_ms=usage_info["execution_time_ms"],
                   input_tokens=usage_info["input_tokens"],
                   output_tokens=usage_info["output_tokens"],
                   total_tokens=usage_info["total_tokens"])
        
        return content, usage_info

    async def generate_story(self, primary_character: str, secondary_character: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a story using Semantic Kernel prompts (deprecated: use generate_content).
        
        This method provides backwards compatibility for existing story generation code.
        It delegates to the generic generate_content method.
        
        Args:
            primary_character: The main character's name for the story.
            secondary_character: The secondary character's name for the story.
            
        Returns:
            A tuple containing the generated story and usage information.
        """
        return await self.generate_content(primary_character, secondary_character)