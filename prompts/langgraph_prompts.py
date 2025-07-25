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

def get_storyteller_system_prompt() -> str:
    """Get the storyteller system prompt for LangGraph"""
    return _load_prompt_file("langgraph/langgraph_storyteller_system_prompt.txt")

def get_initial_story_template() -> str:
    """Get the initial story template for LangGraph"""
    return _load_prompt_file("langgraph/langgraph_initial_story_template.txt")

def get_editor_system_prompt() -> str:
    """Get the editor system prompt for LangGraph"""
    return _load_prompt_file("langgraph/langgraph_editor_system_prompt.txt")

def get_enhancement_template() -> str:
    """Get the enhancement template for LangGraph"""
    return _load_prompt_file("langgraph/langgraph_enhancement_template.txt")

def get_initial_messages(primary_character: str, secondary_character: str) -> list:
    """Get formatted initial messages for LangGraph story generation"""
    return [
        SystemMessage(content=get_storyteller_system_prompt()),
        HumanMessage(content=get_initial_story_template().format(
            primary_character=primary_character,
            secondary_character=secondary_character
        ))
    ]

def get_enhancement_messages(story: str) -> list:
    """Get formatted enhancement messages for LangGraph story editing"""
    return [
        SystemMessage(content=get_editor_system_prompt()),
        HumanMessage(content=get_enhancement_template().format(story=story))
    ]