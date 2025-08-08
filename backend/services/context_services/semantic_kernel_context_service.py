from .base_context_service import BaseContextService
from logging_config import get_logger

logger = get_logger(__name__)

class SemanticKernelContextService(BaseContextService):
    """Context prompt execution service using Semantic Kernel approach.
    
    This service executes context prompts directly without story generation.
    It uses the base API call method for direct prompt execution.
    """
    pass  # Inherits execute_prompt method from base class