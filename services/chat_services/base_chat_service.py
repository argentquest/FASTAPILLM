"""Base chat service for conversational AI capabilities."""

from typing import List, Dict, Any
from ..base_service import BaseService
from prompts.chat_prompts import get_semantic_kernel_chat_prompt
from logging_config import get_logger

logger = get_logger(__name__)


class ChatService(BaseService):
    """Base chat service that extends story generation for conversational use.
    
    This service extends the base story service to provide conversational
    AI capabilities. It maintains conversation context and provides
    specialized prompts for creative writing assistance.
    
    The service handles conversation history and context management,
    allowing for coherent multi-turn conversations.
    
    Attributes:
        conversation_context: List to store conversation context (currently unused).
        
    Examples:
        >>> service = ChatService()
        >>> response, usage = await service.send_message(
        ...     "Tell me a story about dragons",
        ...     [{"role": "user", "content": "Hi there!"},
        ...      {"role": "assistant", "content": "Hello! How can I help?"}]
        ... )
    """
    
    def __init__(self):
        super().__init__()
        self.conversation_context = []
    
    async def send_message(self, message: str, conversation_history: List[Dict[str, str]] = None) -> tuple[str, Dict[str, Any]]:
        """Send a message and get AI response with conversation context.
        
        Processes a user message within the context of an ongoing conversation,
        maintaining coherence across multiple turns.
        
        Args:
            message: The user's message text.
            conversation_history: Optional list of previous messages in the format
                [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}].
                Defaults to None for new conversations.
                
        Returns:
            A tuple containing:
            - response: The AI's response text
            - usage_info: Dictionary with token usage and performance metrics:
                - input_tokens: Tokens in the full conversation context
                - output_tokens: Tokens in the AI response
                - total_tokens: Sum of input and output tokens
                - execution_time_ms: API call duration in milliseconds
                
        Raises:
            APIConnectionError: If unable to connect to the LLM API.
            APIRateLimitError: If API rate limits are exceeded.
            TimeoutError: If the API call exceeds the configured timeout.
            
        Examples:
            >>> # New conversation
            >>> response, usage = await service.send_message("Hello!")
            
            >>> # Continue conversation
            >>> history = [
            ...     {"role": "user", "content": "Hello!"},
            ...     {"role": "assistant", "content": "Hi there! How can I help?"}
            ... ]
            >>> response, usage = await service.send_message(
            ...     "Can you help me write a story?", history
            ... )
        """
        
        # Build conversation context
        messages = []
        
        # Add system message for chat context
        system_message = {
            "role": "system", 
            "content": self._get_chat_system_prompt()
        }
        messages.append(system_message)
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        logger.info("Sending chat message",
                   service=self.service_name,
                   message_length=len(message),
                   context_length=len(messages))
        
        # Call the API with conversation context
        response, usage_info = await self._call_api_with_retry(messages)
        
        logger.info("Chat response generated",
                   service=self.service_name,
                   response_length=len(response),
                   input_tokens=usage_info["input_tokens"],
                   output_tokens=usage_info["output_tokens"],
                   total_tokens=usage_info["total_tokens"],
                   execution_time_ms=usage_info["execution_time_ms"])
        
        return response, usage_info
    
    def _get_chat_system_prompt(self) -> str:
        """Get the system prompt for chat context.
        
        Returns the base system prompt that defines the AI assistant's
        role and capabilities in chat conversations. Loads the prompt
        from external file for easier maintenance.
        
        Returns:
            A string containing the system prompt that establishes the
            AI's personality and specialization in creative writing.
            
        Examples:
            >>> service = ChatService()
            >>> prompt = service._get_chat_system_prompt()
            >>> "creative writing" in prompt.lower()
            True
        """
        return get_semantic_kernel_chat_prompt()