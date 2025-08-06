# Provider Configuration Guide

This guide explains how to configure FASTAPILLM to work with different AI providers.

## Supported Provider Types

### 1. OpenAI Provider (`PROVIDER_NAME=openai`)

Use this for any OpenAI-compatible API, including:
- OpenAI directly
- Azure OpenAI
- OpenRouter
- Ollama
- LM Studio
- Any OpenAI-compatible endpoint

**Basic Configuration:**
```env
PROVIDER_NAME=openai
PROVIDER_API_KEY=your-api-key
PROVIDER_API_BASE_URL=https://api.openai.com/v1
PROVIDER_MODEL=gpt-3.5-turbo
```

**Examples:**

**OpenRouter:**
```env
PROVIDER_NAME=openai
PROVIDER_API_KEY=sk-or-v1-your-key
PROVIDER_API_BASE_URL=https://openrouter.ai/api/v1
PROVIDER_MODEL=meta-llama/llama-3-8b-instruct
PROVIDER_HEADERS={"HTTP-Referer": "http://localhost:8000", "X-Title": "FASTAPILLM"}
```

**Ollama (Local):**
```env
PROVIDER_NAME=openai
PROVIDER_API_KEY=not-needed
PROVIDER_API_BASE_URL=http://localhost:11434/v1
PROVIDER_MODEL=llama2
```

### 2. Custom Provider (`PROVIDER_NAME=custom`)

Use this for providers that require special authentication, headers, or behavior.

**Basic Configuration:**
```env
PROVIDER_NAME=custom
PROVIDER_API_KEY=your-api-key
PROVIDER_API_BASE_URL=https://api.customprovider.com/v1
PROVIDER_MODEL=custom-model
```

**Extended Configuration (Custom Provider Only):**

When `PROVIDER_NAME=custom`, you can use these additional settings:

```env
# Authentication
CUSTOM_AUTH_TOKEN=oauth-token-xyz          # OAuth bearer token
CUSTOM_API_SECRET=secret-key-123           # API secret key
CUSTOM_CLIENT_ID=client-app-456            # OAuth client ID
CUSTOM_CLIENT_SECRET=client-secret-789     # OAuth client secret

# Endpoints
CUSTOM_AUTH_ENDPOINT=https://auth.customprovider.com/token
CUSTOM_TOKEN_ENDPOINT=https://api.customprovider.com/oauth/token

# Behavior Flags
CUSTOM_USE_OAUTH=true                      # Use OAuth instead of API key
CUSTOM_REQUIRE_SIGNATURE=false             # Require request signatures
CUSTOM_ENABLE_RETRY=true                   # Enable custom retry logic

# Metadata
CUSTOM_TENANT_ID=tenant-12345              # Multi-tenant identifier
CUSTOM_ENVIRONMENT=production              # Environment (production/staging/dev)
CUSTOM_API_VERSION=v2                      # API version
CUSTOM_VAR=custom-string-value             # Custom variable for provider-specific data

# Request Configuration
CUSTOM_MAX_TOKENS=4000                     # Override max tokens
CUSTOM_TEMPERATURE=0.7                     # Override temperature
CUSTOM_TIMEOUT_SECONDS=120                 # Custom timeout

# Additional Headers (JSON)
CUSTOM_EXTRA_HEADERS={"X-Region": "us-west", "X-Priority": "high"}

# Model Mapping (JSON) - Map standard models to custom names
CUSTOM_MODEL_MAPPING={"gpt-3.5-turbo": "custom-chat", "gpt-4": "custom-advanced"}
```

## Header Generation

Headers are automatically generated based on the provider type:

### OpenAI Provider
- Uses standard `Authorization: Bearer {api_key}` header
- AsyncOpenAI client handles this automatically
- Additional headers from `PROVIDER_HEADERS` are included

### Custom Provider
Headers are built dynamically based on settings:
- If `CUSTOM_USE_OAUTH=true`: Uses `Authorization: Bearer {CUSTOM_AUTH_TOKEN}`
- If `CUSTOM_USE_OAUTH=false`: Uses `X-API-Key: {api_key}`
- Adds all metadata headers (tenant, environment, version)
- Includes any `CUSTOM_EXTRA_HEADERS`

## Common Provider Configurations

### Azure OpenAI
```env
PROVIDER_NAME=openai
PROVIDER_API_KEY=your-azure-key
PROVIDER_API_BASE_URL=https://your-resource.openai.azure.com
PROVIDER_MODEL=deployment-name
PROVIDER_API_VERSION=2023-05-15
PROVIDER_HEADERS={"api-key": "your-azure-key"}
```

### Local LLM (Ollama)
```env
PROVIDER_NAME=openai
PROVIDER_API_KEY=not-needed
PROVIDER_API_BASE_URL=http://localhost:11434/v1
PROVIDER_MODEL=mistral
```

### Custom Enterprise Provider
```env
PROVIDER_NAME=custom
PROVIDER_API_KEY=primary-key
PROVIDER_API_BASE_URL=https://ai.company.com/api/v1
PROVIDER_MODEL=company-llm-large

# OAuth Configuration
CUSTOM_USE_OAUTH=true
CUSTOM_AUTH_TOKEN=bearer-token-from-oauth
CUSTOM_CLIENT_ID=webapp-client
CUSTOM_CLIENT_SECRET=webapp-secret

# Enterprise Settings
CUSTOM_TENANT_ID=company-division-1
CUSTOM_ENVIRONMENT=production
CUSTOM_API_VERSION=v2.1

# Custom Headers
CUSTOM_EXTRA_HEADERS={"X-Department": "Engineering", "X-Cost-Center": "AI-Research"}
```

## Troubleshooting

### Connection Issues
1. Verify `PROVIDER_API_BASE_URL` is correct and accessible
2. Check if API key is valid
3. Ensure any required headers are set in `PROVIDER_HEADERS`

### Authentication Errors
1. For OpenAI providers: Check `PROVIDER_API_KEY`
2. For custom providers: Verify OAuth settings if `CUSTOM_USE_OAUTH=true`
3. Check logs for specific authentication error messages

### Model Not Found
1. Verify `PROVIDER_MODEL` matches available models
2. For custom providers, check `CUSTOM_MODEL_MAPPING` configuration
3. Some providers require specific model naming conventions

## Adding New Custom Fields

To add more custom fields for your specific provider:

1. Edit `custom_settings.py`
2. Add new fields to `CustomProviderSettings` class:
   ```python
   custom_new_field: Optional[str] = Field(default=None, env="CUSTOM_NEW_FIELD")
   ```
3. Update `get_custom_headers()` method if the field affects headers
4. The new field will be automatically loaded from environment variables

## Security Notes

- Never commit `.env` files with real API keys
- Use environment-specific `.env` files for different deployments
- Sensitive headers are automatically masked in logs
- API keys and secrets are never logged in plain text