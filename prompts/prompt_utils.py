"""
Utility functions for loading and managing prompt files.
"""
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

def load_prompt_file(filename: str, prompt_dir: Optional[Path] = None) -> str:
    """
    Load prompt content from a .txt file.
    
    Args:
        filename: Name of the prompt file to load
        prompt_dir: Directory containing the prompt files (defaults to current directory)
    
    Returns:
        String content of the prompt file
        
    Raises:
        FileNotFoundError: If the prompt file doesn't exist
        IOError: If there's an error reading the file
    """
    if prompt_dir is None:
        prompt_dir = Path(__file__).parent
    
    file_path = prompt_dir / filename
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            logger.debug(f"Loaded prompt file: {filename} ({len(content)} characters)")
            return content
    except FileNotFoundError:
        logger.error(f"Prompt file not found: {filename} in {prompt_dir}")
        raise FileNotFoundError(f"Prompt file not found: {filename}")
    except IOError as e:
        logger.error(f"Error reading prompt file {filename}: {e}")
        raise IOError(f"Error reading prompt file {filename}: {e}")

def format_template(template: str, **kwargs) -> str:
    """
    Format a prompt template with the given variables.
    
    Args:
        template: Template string with {variable} placeholders
        **kwargs: Variables to substitute in the template
        
    Returns:
        Formatted string with variables substituted
        
    Raises:
        KeyError: If a required variable is missing
    """
    try:
        return template.format(**kwargs)
    except KeyError as e:
        logger.error(f"Missing variable in template: {e}")
        raise KeyError(f"Missing required variable in template: {e}")

def get_available_prompts(prompt_dir: Optional[Path] = None) -> Dict[str, Path]:
    """
    Get a dictionary of available prompt files.
    
    Args:
        prompt_dir: Directory to search for prompt files
        
    Returns:
        Dictionary mapping prompt names to file paths
    """
    if prompt_dir is None:
        prompt_dir = Path(__file__).parent
    
    prompt_files = {}
    for txt_file in prompt_dir.glob("*.txt"):
        prompt_files[txt_file.stem] = txt_file
    
    return prompt_files

def validate_template_variables(template: str, required_vars: list) -> bool:
    """
    Validate that a template contains all required variables.
    
    Args:
        template: Template string to validate
        required_vars: List of variable names that must be present
        
    Returns:
        True if all required variables are present, False otherwise
    """
    for var in required_vars:
        if f"{{{var}}}" not in template:
            logger.warning(f"Template missing required variable: {var}")
            return False
    return True