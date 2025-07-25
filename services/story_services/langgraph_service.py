from typing import TypedDict, Tuple, Dict, Any

from ..base_service import BaseService
from prompts.langgraph_prompts import get_initial_messages, get_enhancement_messages
from logging_config import get_logger

logger = get_logger(__name__)

class GenerationState(TypedDict):
    """Type definition for LangGraph content generation state.
    
    Defines the structure of state data that flows through the
    LangGraph workflow during content generation.
    
    Attributes:
        primary_input: The main input parameter.
        secondary_input: The secondary input parameter.
        content: The final enhanced content.
        draft_content: The initial content draft.
    """
    primary_input: str
    secondary_input: str
    content: str
    draft_content: str

# Backwards compatibility alias for story generation
StoryState = GenerationState

class LangGraphService(BaseService):
    """Content generation service using LangGraph workflow.
    
    This service implements a two-stage content generation workflow using
    LangGraph concepts:
    1. Initial content draft generation
    2. Content enhancement and refinement
    
    This approach allows for more controlled and iterative content development,
    resulting in higher quality outputs through the multi-step process.
    
    Examples:
        >>> service = LangGraphService()
        >>> content, usage = await service.generate_content("Luke", "Leia")
        >>> print(f"Enhanced content: {len(content)} chars, {usage['total_tokens']} tokens")
    """
    
    async def generate_content(self, primary_input: str, secondary_input: str) -> Tuple[str, Dict[str, Any]]:
        """Generate content using LangGraph two-step process.
        
        Implements a sophisticated two-stage content generation workflow:
        1. Creates an initial content draft using basic prompts
        2. Enhances the draft with additional details and improvements
        
        This approach typically produces higher quality content than single-pass
        generation by allowing for iterative refinement.
        
        Args:
            primary_input: The main input parameter.
            secondary_input: The secondary input parameter.
            
        Returns:
            A tuple containing:
            - content: The final enhanced content text
            - usage_info: Combined usage metrics from both API calls:
                - input_tokens: Total tokens from both prompt phases
                - output_tokens: Total tokens generated across both phases
                - total_tokens: Sum of all input and output tokens
                - execution_time_ms: Combined execution time for both phases
                
        Raises:
            APIConnectionError: If unable to connect to the LLM API.
            APIRateLimitError: If API rate limits are exceeded.
            TimeoutError: If any API call exceeds the configured timeout.
            
        Examples:
            >>> service = LangGraphService()
            >>> content, usage = await service.generate_content(
            ...     "Frodo Baggins",
            ...     "Gandalf"
            ... )
            >>> print(f"Draft->Enhanced: {usage['total_tokens']} tokens used")
            >>> print(content[:150] + "...")
            "The Shire was peaceful that morning when Frodo Baggins encountered the old wizard Gandalf..."
        """
        logger.info("Generating content with LangGraph",
                   primary_input=primary_input,
                   secondary_input=secondary_input)
        
        # Step 1: Generate initial content
        initial_messages = get_initial_messages(primary_input, secondary_input)
        dict_messages = [
            {"role": "system", "content": initial_messages[0].content},
            {"role": "user", "content": initial_messages[1].content}
        ]
        
        logger.debug("Generating initial content draft")
        draft_content, draft_usage = await self._call_api_with_retry(dict_messages)
        
        # Step 2: Enhance the content
        enhancement_messages = get_enhancement_messages(draft_content)
        dict_messages = [
            {"role": "system", "content": enhancement_messages[0].content},
            {"role": "user", "content": enhancement_messages[1].content}
        ]
        
        logger.debug("Enhancing content draft", draft_length=len(draft_content))
        enhanced_content, enhancement_usage = await self._call_api_with_retry(dict_messages)
        
        # Combine usage information from both API calls
        combined_usage = {
            "input_tokens": draft_usage["input_tokens"] + enhancement_usage["input_tokens"],
            "output_tokens": draft_usage["output_tokens"] + enhancement_usage["output_tokens"],
            "total_tokens": draft_usage["total_tokens"] + enhancement_usage["total_tokens"],
            "execution_time_ms": draft_usage["execution_time_ms"] + enhancement_usage["execution_time_ms"]
        }
        
        logger.info("Content generated successfully with LangGraph",
                   draft_length=len(draft_content),
                   final_length=len(enhanced_content),
                   total_input_tokens=combined_usage["input_tokens"],
                   total_output_tokens=combined_usage["output_tokens"],
                   total_tokens=combined_usage["total_tokens"],
                   total_execution_time_ms=combined_usage["execution_time_ms"])
        
        return enhanced_content, combined_usage

    async def generate_story(self, primary_character: str, secondary_character: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a story using LangGraph two-step process (deprecated: use generate_content).
        
        This method provides backwards compatibility for existing story generation code.
        It delegates to the generic generate_content method.
        
        Args:
            primary_character: The main character's name for the story.
            secondary_character: The secondary character's name for the story.
            
        Returns:
            A tuple containing the generated story and usage information.
        """
        return await self.generate_content(primary_character, secondary_character)