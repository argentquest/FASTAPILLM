# Popular OpenRouter models for story generation
# See https://openrouter.ai/models for full list

OPENROUTER_MODELS = {
    # OpenAI Models
    "openai/gpt-4-turbo-preview": "GPT-4 Turbo (Latest)",
    "openai/gpt-4": "GPT-4",
    "openai/gpt-3.5-turbo": "GPT-3.5 Turbo",
    "openai/gpt-3.5-turbo-16k": "GPT-3.5 Turbo 16K",
    
    # Anthropic Models
    "anthropic/claude-3-opus": "Claude 3 Opus",
    "anthropic/claude-3-sonnet": "Claude 3 Sonnet",
    "anthropic/claude-3-haiku": "Claude 3 Haiku",
    "anthropic/claude-2.1": "Claude 2.1",
    "anthropic/claude-2": "Claude 2",
    
    # Google Models
    "google/gemini-pro": "Gemini Pro",
    "google/gemini-pro-vision": "Gemini Pro Vision",
    "google/palm-2-codechat-bison": "PaLM 2 Code Chat",
    "google/palm-2-chat-bison": "PaLM 2 Chat",
    
    # Meta Models
    "meta-llama/llama-2-70b-chat": "Llama 2 70B Chat",
    "meta-llama/llama-2-13b-chat": "Llama 2 13B Chat",
    "meta-llama/codellama-34b-instruct": "Code Llama 34B",
    
    # Mistral Models
    "mistralai/mistral-7b-instruct": "Mistral 7B Instruct",
    "mistralai/mixtral-8x7b-instruct": "Mixtral 8x7B",
    
    # Other Popular Models
    "nousresearch/nous-hermes-2-mixtral-8x7b-dpo": "Nous Hermes 2 Mixtral",
    "gryphe/mythomax-l2-13b": "MythoMax 13B",
    "jondurbin/airoboros-l2-70b": "Airoboros 70B",
    "undi95/toppy-m-7b": "Toppy M 7B",
    "teknium/openhermes-2.5-mistral-7b": "OpenHermes 2.5",
}

# Recommended models for story generation
STORY_GENERATION_MODELS = [
    "openai/gpt-4-turbo-preview",
    "anthropic/claude-3-opus",
    "anthropic/claude-3-sonnet",
    "google/gemini-pro",
    "mistralai/mixtral-8x7b-instruct",
]