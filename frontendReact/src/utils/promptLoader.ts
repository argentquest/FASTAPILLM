// Import prompt files as raw text
import systemPromptText from '../prompts/systemPrompt.txt?raw';
import userPromptText from '../prompts/userPrompt.txt?raw';

export const prompts = {
  system: systemPromptText,
  user: userPromptText
};

export const loadPrompt = (type: 'system' | 'user'): string => {
  return prompts[type] || '';
};