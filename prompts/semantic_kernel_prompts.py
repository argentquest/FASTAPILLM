import os
from pathlib import Path

def _load_prompt_file(filename: str) -> str:
    """Load prompt content from a .txt file"""
    prompt_dir = Path(__file__).parent
    file_path = prompt_dir / filename
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found: {filename}")

def get_system_message() -> str:
    """Get the system message for Semantic Kernel"""
    return _load_prompt_file("semantic_kernel/semantic_kernel_system_prompt.txt")

def get_user_message_template() -> str:
    """Get the user message template for Semantic Kernel"""
    return _load_prompt_file("semantic_kernel/semantic_kernel_user_message_template.txt")

def get_chat_messages(primary_character: str, secondary_character: str) -> list:
    """Get formatted chat messages for Semantic Kernel"""
    return [
        {"role": "system", "content": get_system_message()},
        {"role": "user", "content": get_user_message_template().format(
            primary_character=primary_character,
            secondary_character=secondary_character
        )}
    ]