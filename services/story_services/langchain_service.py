from typing import List, Tuple, Dict, Any

from ..base_service import BaseService
from prompts.langchain_prompts import get_langchain_messages
from logging_config import get_logger
from retry_utils import retry_api_calls

logger = get_logger(__name__)

class LangChainService(BaseService):
    """Content generation service using LangChain framework.
    
    This service implements content generation using the LangChain framework
    approach. It leverages LangChain's prompt templates and message structures
    to create well-structured, engaging content.
    
    The service converts LangChain message objects to the standard dictionary
    format expected by the base class API methods.
    
    Examples:
        >>> service = LangChainService()
        >>> content, usage = await service.generate_content("Harry Potter", "Hermione")
        >>> print(f"Generated {len(content)} characters using {usage['total_tokens']} tokens")
    """
    
    @retry_api_calls
    async def generate_content(self, primary_input: str, secondary_input: str) -> Tuple[str, Dict[str, Any]]:
        """Generate content using LangChain prompts.
        
        Creates engaging content using the provided inputs with
        LangChain's prompt template system and structured message format.
        
        The method retrieves LangChain message objects from the prompt module,
        converts them to the standard dictionary format, and calls the base
        class API method.
        
        Args:
            primary_input: The main input parameter.
            secondary_input: The secondary input parameter.
            
        Returns:
            A tuple containing:
            - content: The generated content text
            - usage_info: Dictionary with token usage and performance metrics:
                - input_tokens: Number of tokens in the prompt
                - output_tokens: Number of tokens in the generated content
                - total_tokens: Sum of input and output tokens
                - execution_time_ms: Time taken for API call in milliseconds
                
        Raises:
            APIConnectionError: If unable to connect to the LLM API.
            APIRateLimitError: If API rate limits are exceeded.
            TimeoutError: If the API call exceeds the configured timeout.
            
        Examples:
            >>> service = LangChainService()
            >>> content, usage = await service.generate_content(
            ...     "Captain Picard",
            ...     "Data"
            ... )
            >>> print(content[:100] + "...")
            "Captain Picard stood on the bridge of the Enterprise, watching as Data analyzed..."
        """
        logger.info("Generating content with LangChain",
                   primary_input=primary_input,
                   secondary_input=secondary_input)
        
        # Get messages for the prompt
        messages = get_langchain_messages(primary_input, secondary_input)
        
        # Convert LangChain messages to dict format
        dict_messages = [
            {"role": "system", "content": messages[0].content},
            {"role": "user", "content": messages[1].content}
        ]
        
        # Call the API using base class method with retry
        content, usage_info = await self._call_api_with_retry(dict_messages)
        
        logger.info("Content generated successfully with LangChain",
                   content_length=len(content),
                   input_tokens=usage_info["input_tokens"],
                   output_tokens=usage_info["output_tokens"],
                   total_tokens=usage_info["total_tokens"],
                   execution_time_ms=usage_info["execution_time_ms"])
        
        return content, usage_info

    async def generate_story(self, primary_character: str, secondary_character: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a story using LangChain prompts (deprecated: use generate_content).
        
        This method provides backwards compatibility for existing story generation code.
        It delegates to the generic generate_content method.
        
        Args:
            primary_character: The main character's name for the story.
            secondary_character: The secondary character's name for the story.
            
        Returns:
            A tuple containing the generated story and usage information.
        """
        return await self.generate_content(primary_character, secondary_character)