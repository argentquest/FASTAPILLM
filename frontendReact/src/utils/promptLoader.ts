// Import prompt files as raw text
import systemPromptText from '../prompts/systemPrompt.txt';
import userPromptText from '../prompts/userPrompt.txt';

export const prompts = {
  system: systemPromptText,
  user: userPromptText
};

export const loadPrompt = (type: 'system' | 'user'): string => {
  return prompts[type] || '';
};