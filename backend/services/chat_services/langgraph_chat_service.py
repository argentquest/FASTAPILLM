"""LangGraph chat service implementation."""

from typing import Dict, Any, Tuple
from .base_chat_service import ChatService
from prompts.chat_prompts import get_langgraph_chat_prompt


class LangGraphChatService(ChatService):
    """Chat service using LangGraph workflow approach.
    
    Provides conversational AI capabilities using LangGraph's structured
    workflow concepts. Emphasizes complex reasoning and multi-step
    thinking in creative writing tasks.
    
    Examples:
        >>> service = LangGraphChatService()
        >>> response, usage = await service.send_message(
        ...     "Plan a complex fantasy novel with multiple storylines"
        ... )
    """
    
    def _get_chat_system_prompt(self) -> str:
        """Get LangGraph-specific chat system prompt.
        
        Returns a system prompt that emphasizes LangGraph's strengths
        in structured reasoning and complex narrative development.
        Loads the prompt from external file for easier maintenance.
        
        Returns:
            A string containing the LangGraph-specific system prompt.
        """
        return get_langgraph_chat_prompt()

    async def generate_content(self, primary_input: str, secondary_input: str) -> Tuple[str, Dict[str, Any]]:
        """Generate content using LangGraph (for compatibility with base class).
        
        This method provides compatibility with the abstract base class but is
        not typically used in chat context. It generates content based on the provided inputs.
        
        Args:
            primary_input: The main input parameter.
            secondary_input: The secondary input parameter.
            
        Returns:
            A tuple of (content_text, usage_info).
        """
        # This method is not used in chat context, but required by abstract base class
        messages = [
            {"role": "system", "content": self._get_chat_system_prompt()},
            {"role": "user", "content": f"Please help me with {primary_input} and {secondary_input}."}
        ]
        return await self._call_api_with_retry(messages)

    async def generate_story(self, primary_character: str, secondary_character: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a story using LangGraph (for compatibility with base class).
        
        This method provides compatibility with the abstract base class.
        
        Args:
            primary_character: The main character's name.
            secondary_character: The secondary character's name.
            
        Returns:
            A tuple of (story_text, usage_info).
        """
        # This method is not used in chat context, but required by abstract base class
        messages = [
            {"role": "system", "content": self._get_chat_system_prompt()},
            {"role": "user", "content": f"Write a Christmas story featuring {primary_character} and {secondary_character}."}
        ]
        return await self._call_api_with_retry(messages)