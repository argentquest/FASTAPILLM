import axios from 'axios';
import type {
  Story,
  Conversation,
  ChatMessage,
  CostEntry,
  CostSummary,
  ContextFile,
  ContextExecution,
  Framework,
  StoryGenerationRequest,
  ChatRequest,
  ProviderInfo
} from '../types';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 60000, // 60 seconds for long-running requests
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const timestamp = new Date().toISOString();
    console.group(`🔄 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    console.log(`⏰ Time: ${timestamp}`);
    console.log(`📤 Headers:`, config.headers);
    if (config.data) {
      console.log(`📦 Request Data:`, config.data);
    }
    console.groupEnd();
    
    // Add request timing
    (config as any).metadata = { startTime: Date.now() };
    return config;
  },
  (error) => {
    console.error('❌ Request Setup Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    const duration = Date.now() - (response.config as any).metadata?.startTime;
    const timestamp = new Date().toISOString();
    
    console.group(`✅ API Response: ${response.status} ${response.config.url}`);
    console.log(`⏰ Time: ${timestamp}`);
    console.log(`⚡ Duration: ${duration}ms`);
    console.log(`📊 Status: ${response.status} ${response.statusText}`);
    console.log(`📥 Response Data:`, response.data);
    console.groupEnd();
    
    return response;
  },
  (error) => {
    const duration = error.config ? Date.now() - (error.config as any).metadata?.startTime : 0;
    const timestamp = new Date().toISOString();
    
    console.group(`❌ API Error: ${error.response?.status || 'Network'} ${error.config?.url || 'Unknown'}`);
    console.log(`⏰ Time: ${timestamp}`);
    console.log(`⚡ Duration: ${duration}ms`);
    console.log(`🚨 Error Type:`, error.name);
    console.log(`📄 Error Message:`, error.message);
    if (error.response) {
      console.log(`📊 Response Status:`, error.response.status);
      console.log(`📥 Response Data:`, error.response.data);
    }
    console.log(`🔧 Full Error:`, error);
    console.groupEnd();
    
    return Promise.reject(error);
  }
);

// Story API
export const storyApi = {
  generate: async (framework: Framework, data: StoryGenerationRequest): Promise<Story> => {
    const response = await api.post(`/api/${framework}`, data);
    return response.data;
  },

  getAll: async (): Promise<Story[]> => {
    const response = await api.get('/api/stories?limit=100'); // Get more stories
    // Map backend StoryList to frontend Story format
    return response.data.map((item: any) => ({
      id: item.id.toString(),
      primary_character: item.primary_character,
      secondary_character: item.secondary_character,
      story: item.story_preview,
      framework: item.framework,
      created_at: item.created_at
    }));
  },

  getById: async (id: string): Promise<Story> => {
    const response = await api.get(`/api/stories/${id}`);
    // Map backend StoryDB to frontend Story format
    const item = response.data;
    return {
      id: item.id.toString(),
      primary_character: item.primary_character,
      secondary_character: item.secondary_character,
      story: item.story_content,
      framework: item.method,
      created_at: item.created_at
    };
  },

  searchByCharacter: async (character: string): Promise<Story[]> => {
    const response = await api.get(`/api/stories/search/characters?character=${encodeURIComponent(character)}`);
    // Map backend StoryList to frontend Story format
    return response.data.map((item: any) => ({
      id: item.id.toString(),
      primary_character: item.primary_character,
      secondary_character: item.secondary_character,
      story: item.story_preview,
      framework: item.framework,
      created_at: item.created_at
    }));
  },

  deleteAll: async (): Promise<{ message: string; deleted_count: number }> => {
    const response = await api.delete('/api/stories');
    return response.data;
  },
};

// Chat API
export const chatApi = {
  getConversations: async (): Promise<Conversation[]> => {
    const response = await api.get('/api/chat/conversations');
    return response.data;
  },

  getConversation: async (id: string): Promise<Conversation> => {
    const response = await api.get(`/api/chat/conversations/${id}`);
    return response.data;
  },

  sendMessage: async (framework: Framework, data: ChatRequest): Promise<ChatMessage> => {
    const response = await api.post(`/api/chat/${framework}`, data);
    // The API returns { conversation: {...}, message: {...} }
    // We need to extract just the message
    return response.data.message || response.data;
  },

  deleteConversation: async (id: string): Promise<void> => {
    await api.delete(`/api/chat/conversations/${id}`);
  },

  deleteAllConversations: async (): Promise<{ message: string; deleted_count: number }> => {
    const response = await api.delete('/api/chat/conversations');
    return response.data;
  },
};

// Cost API
export const costApi = {
  getUsage: async (startDate?: string, endDate?: string): Promise<{
    usage_data: CostEntry[];
    summary: CostSummary;
  }> => {
    // Calculate days between dates, default to 30
    let days = 30;
    if (startDate && endDate) {
      const start = new Date(startDate);
      const end = new Date(endDate);
      days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
    }
    
    const response = await api.get(`/api/cost/usage?days=${days}`);
    const data = response.data;
    
    // Map backend CostUsageResponse to frontend format
    return {
      usage_data: data.daily_usage.map((day: any) => ({
        id: day.date,
        framework: 'Multiple',
        model: 'Multiple',
        request_count: day.request_count,
        total_tokens: day.total_tokens,
        estimated_cost: day.total_cost_usd,
        date: day.date
      })),
      summary: {
        total_requests: data.summary.total_requests,
        total_tokens: data.summary.total_tokens,
        estimated_cost: data.summary.total_cost_usd,
        avg_cost_per_request: data.summary.average_cost_per_request
      }
    };
  },

  clearAll: async (): Promise<{ message: string; deleted_count: number }> => {
    const response = await api.delete('/api/cost/usage');
    return response.data;
  },

  getTransactions: async (days: number = 30): Promise<any> => {
    const response = await api.get(`/api/cost/transactions?days=${days}`);
    return response.data;
  },
};

// Context API
export const contextApi = {
  uploadFiles: async (files: FileList): Promise<any> => {
    // Upload files one by one since backend expects single file
    const uploadPromises = Array.from(files).map(async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/api/context/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    });
    
    const results = await Promise.all(uploadPromises);
    return { message: `Uploaded ${results.length} file(s) successfully`, results };
  },

  getFiles: async (): Promise<ContextFile[]> => {
    const response = await api.get('/api/context/files');
    return response.data;
  },

  deleteFile: async (id: string): Promise<void> => {
    await api.delete(`/api/context/files/${id}`);
  },

  executePrompt: async (data: {
    framework: Framework;
    prompt: string;
    file_ids: string[];
    userPrompt?: string;
  }): Promise<ContextExecution> => {
    const requestData = {
      file_ids: data.file_ids, // Now supports multiple files
      method: data.framework, // 'framework' -> 'method'
      system_prompt: data.prompt,
      user_prompt: data.userPrompt || 'Please analyze and respond based on the context provided.'
    };
    const response = await api.post('/api/context/execute', requestData);
    return response.data;
  },

  getExecutions: async (): Promise<ContextExecution[]> => {
    const response = await api.get('/api/context/executions');
    return response.data;
  },
};

// System API
export const systemApi = {
  getProviderInfo: async (): Promise<ProviderInfo> => {
    const response = await api.get('/api/provider');
    return response.data;
  },

  healthCheck: async (): Promise<{ status: string; timestamp: number }> => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;