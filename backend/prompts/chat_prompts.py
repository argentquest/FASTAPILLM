"""
Chat prompt management for different AI frameworks.

This module provides functions to load and manage chat system prompts
for different AI services (Semantic Kernel, LangChain, LangGraph).
"""

from pathlib import Path
from .prompt_utils import load_prompt_file


def get_semantic_kernel_chat_prompt() -> str:
    """
    Load the Semantic Kernel chat system prompt.
    
    Returns:
        String content of the Semantic Kernel chat system prompt.
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist.
        IOError: If there's an error reading the file.
        
    Examples:
        >>> prompt = get_semantic_kernel_chat_prompt()
        >>> "creative writing" in prompt.lower()
        True
    """
    prompt_dir = Path(__file__).parent / "semantic_kernel"
    return load_prompt_file("semantic_kernel_chat_system_prompt.txt", prompt_dir)


def get_langchain_chat_prompt() -> str:
    """
    Load the LangChain chat system prompt.
    
    Returns:
        String content of the LangChain chat system prompt.
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist.
        IOError: If there's an error reading the file.
        
    Examples:
        >>> prompt = get_langchain_chat_prompt()
        >>> "LangChain" in prompt
        True
    """
    prompt_dir = Path(__file__).parent / "langchain"
    return load_prompt_file("langchain_chat_system_prompt.txt", prompt_dir)


def get_langgraph_chat_prompt() -> str:
    """
    Load the LangGraph chat system prompt.
    
    Returns:
        String content of the LangGraph chat system prompt.
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist.
        IOError: If there's an error reading the file.
        
    Examples:
        >>> prompt = get_langgraph_chat_prompt()
        >>> "LangGraph" in prompt
        True
    """
    prompt_dir = Path(__file__).parent / "langgraph"
    return load_prompt_file("langgraph_chat_system_prompt.txt", prompt_dir)


def get_chat_prompt_by_service(service_name: str) -> str:
    """
    Get chat prompt for a specific service by name.
    
    Args:
        service_name: Name of the service ("semantic_kernel", "langchain", or "langgraph").
        
    Returns:
        String content of the appropriate chat system prompt.
        
    Raises:
        ValueError: If service_name is not recognized.
        FileNotFoundError: If the prompt file doesn't exist.
        IOError: If there's an error reading the file.
        
    Examples:
        >>> prompt = get_chat_prompt_by_service("langchain")
        >>> "LangChain" in prompt
        True
        >>> get_chat_prompt_by_service("invalid")
        ValueError: Unknown service: invalid
    """
    service_map = {
        "semantic_kernel": get_semantic_kernel_chat_prompt,
        "langchain": get_langchain_chat_prompt,
        "langgraph": get_langgraph_chat_prompt
    }
    
    if service_name not in service_map:
        raise ValueError(f"Unknown service: {service_name}. Available services: {list(service_map.keys())}")
    
    return service_map[service_name]()