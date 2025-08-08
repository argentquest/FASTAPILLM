# LangChain Prompts

This directory contains the prompt templates used by the LangChain framework implementation.

## Files

- `langchain_system_prompt.txt` - System prompt that defines the AI's role as a creative storyteller
- `langchain_user_prompt_template.txt` - User prompt template with story generation guidelines

## Template Variables

The user prompt template supports these variables:
- `{primary_character}` - The first character name entered by the user
- `{secondary_character}` - The second character name entered by the user

## Editing

To customize the LangChain story generation:
1. Edit the appropriate `.txt` file in this directory
2. Keep the template variables (`{primary_character}`, `{secondary_character}`) intact
3. Restart the application to apply changes

The prompts are loaded dynamically by `langchain_prompts.py` when the application starts.