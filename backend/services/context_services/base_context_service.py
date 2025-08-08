from typing import Tuple, Dict, Any
from ..base_ai_service import BaseAIService
try:
    from logging_config import get_logger
except ImportError:
    from ...logging_config import get_logger

logger = get_logger(__name__)

class BaseContextService(BaseAIService):
    """Base service for context prompt execution.
    
    This service is designed for executing prompts with file context,
    not for story generation. It uses direct prompt execution without
    story-specific formatting.
    """
    
    # BaseAIService doesn't have abstract methods to implement
    
    async def execute_prompt(self, system_prompt: str, user_prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Execute a context prompt directly without story generation formatting.
        
        Args:
            system_prompt: The system prompt containing context
            user_prompt: The user's question or request
            
        Returns:
            Tuple of (response_content, usage_info)
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        logger.info("Executing context prompt",
                   service=self.service_name,
                   system_prompt_length=len(system_prompt),
                   user_prompt_length=len(user_prompt))
        
        return await self._call_api(messages)