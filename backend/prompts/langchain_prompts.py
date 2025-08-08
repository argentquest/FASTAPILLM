from langchain.schema import SystemMessage, HumanMessage
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

def get_system_prompt() -> str:
    """Get the system prompt for LangChain"""
    return _load_prompt_file("langchain/langchain_system_prompt.txt")

def get_user_prompt_template() -> str:
    """Get the user prompt template for LangChain"""
    return _load_prompt_file("langchain/langchain_user_prompt_template.txt")

def get_langchain_messages(primary_character: str, secondary_character: str) -> list:
    """Get formatted LangChain messages"""
    return [
        SystemMessage(content=get_system_prompt()),
        HumanMessage(content=get_user_prompt_template().format(
            primary_character=primary_character,
            secondary_character=secondary_character
        ))
    ]