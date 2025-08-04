export interface Story {
  id: string;
  primary_character: string;
  secondary_character: string;
  story: string;
  framework: string;
  created_at: string;
  transaction_guid?: string;
  request_id?: string;
  generation_time_ms?: number;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  estimated_cost_usd?: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface Conversation {
  id: string;
  title?: string;
  created_at: string;
  messages: ChatMessage[];
}

export interface CostEntry {
  id: string;
  framework: string;
  model: string;
  request_count: number;
  total_tokens: number;
  estimated_cost: number;
  date: string;
}

export interface CostSummary {
  total_requests: number;
  total_tokens: number;
  estimated_cost: number;
  avg_cost_per_request: number;
}

export interface ContextFile {
  id: string;
  name: string;
  size: number;
  upload_date: string;
}

export interface ContextExecution {
  id: number;
  llm_response: string;
  original_filename: string;
  file_type: string;
  processed_content_length: number;
  final_prompt_length: number;
  file_processing_time_ms: number;
  llm_execution_time_ms: number;
  total_execution_time_ms: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
  input_cost_per_1k_tokens: number;
  output_cost_per_1k_tokens: number;
  method: string;
  model: string;
  request_id?: string;
  created_at: string;
  // For list view
  framework?: string;
  prompt?: string;
  result?: string;
  files_used?: string[];
}

export type Framework = 'semantic-kernel' | 'langchain' | 'langgraph';

export interface ApiResponse<T> {
  data?: T;
  error?: {
    type: string;
    message: string;
    details?: any;
  };
}

export interface StoryGenerationRequest {
  primary_character: string;
  secondary_character: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ProviderInfo {
  provider: string;
  model: string;
  configured: boolean;
}