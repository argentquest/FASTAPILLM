# Semantic Kernel Prompts

This directory contains the prompt templates used by the Semantic Kernel implementation.

## Files

- `semantic_kernel_system_prompt.txt` - System prompt that defines the AI's role as a master storyteller
- `semantic_kernel_user_message_template.txt` - User prompt template with detailed story requirements

## Template Variables

The user prompt template supports these variables:
- `{primary_character}` - The first character name entered by the user
- `{secondary_character}` - The second character name entered by the user

## Story Requirements

The Semantic Kernel approach focuses on:
- 200-300 word stories
- Classic Christmas themes (generosity, family bonds, joy, wonder)
- Meaningful character interactions
- Sensory details (sights, sounds, smells)
- Heartwarming messages and lessons
- Vivid, descriptive language

## Editing

To customize the Semantic Kernel story generation:
1. Edit the appropriate `.txt` file in this directory
2. Keep the template variables (`{primary_character}`, `{secondary_character}`) intact
3. Restart the application to apply changes

The prompts are loaded dynamically by `semantic_kernel_prompts.py` when the application starts.