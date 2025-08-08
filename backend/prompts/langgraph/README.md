# LangGraph Prompts

This directory contains the prompt templates used by the LangGraph workflow implementation.

## Files

- `langgraph_storyteller_system_prompt.txt` - System prompt for the initial story generation step
- `langgraph_initial_story_template.txt` - Template for creating the initial story draft
- `langgraph_editor_system_prompt.txt` - System prompt for the story enhancement step
- `langgraph_enhancement_template.txt` - Template for enhancing the initial story

## Template Variables

The prompt templates support these variables:
- `{primary_character}` - The first character name entered by the user
- `{secondary_character}` - The second character name entered by the user
- `{story}` - The initial story draft (used only in enhancement template)

## LangGraph Workflow

LangGraph uses a two-step process:

1. **Story Generation**: Uses storyteller system prompt + initial story template to create a basic story
2. **Story Enhancement**: Uses editor system prompt + enhancement template to improve the story with sensory details and emotional depth

## Editing

To customize the LangGraph story generation:
1. Edit the appropriate `.txt` file in this directory
2. Keep the template variables (`{primary_character}`, `{secondary_character}`, `{story}`) intact
3. Restart the application to apply changes

The prompts are loaded dynamically by `langgraph_prompts.py` when the application starts.