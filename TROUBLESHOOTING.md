# Troubleshooting Guide

This guide covers common issues and their solutions.

## Startup Issues

### Pydantic V2 Compatibility Error

**Error:** `PydanticUserError: The 'field' and 'config' parameters are not available in Pydantic V2`

**Solution:** Ensure you're using Pydantic V2 (2.5.3+):
```bash
pip install "pydantic>=2.5.3"
pip install "pydantic-settings>=2.0.0"
```

### Missing Environment Variables

**Error:** `ValueError: Azure provider requires AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME`

**Solution:** 
1. Copy the appropriate `.env` example file:
   ```bash
   cp .env.example .env  # For Azure OpenAI
   cp .env.openrouter.example .env  # For OpenRouter
   cp .env.custom.example .env  # For custom providers
   ```
2. Fill in your API credentials

### Prompt File Not Found

**Error:** `FileNotFoundError: Prompt file not found: semantic_kernel/semantic_kernel_system_prompt.txt`

**Solution:** Ensure all prompt files exist in their subdirectories:
```bash
# Check prompt structure
ls -la prompts/*/
```

If files are missing, regenerate them or restore from backup.

## Runtime Issues

### API Connection Errors

**Error:** `APIConnectionError: Failed to connect to API`

**Solutions:**
1. Check your internet connection
2. Verify API endpoint URLs are correct
3. Ensure API keys are valid and have proper permissions
4. Check if the API service is operational

### Rate Limiting

**Error:** `APIRateLimitError: API rate limit exceeded`

**Solution:** 
- Wait for the rate limit window to reset
- Consider upgrading your API plan for higher limits
- Implement request throttling in your usage

### Model Not Found

**Error:** `Model 'your-model-name' not found`

**Solutions:**
1. Verify the model name is correct for your provider
2. Check if you have access to the specified model
3. For custom providers, ensure the model is deployed and available

## Configuration Issues

### Invalid Provider Configuration

**Error:** `ValueError: LLM provider must be 'azure', 'openrouter', or 'custom'`

**Solution:** Set `LLM_PROVIDER` to one of the supported values:
```env
LLM_PROVIDER=azure        # For Azure OpenAI
LLM_PROVIDER=openrouter   # For OpenRouter
LLM_PROVIDER=custom       # For custom providers
```

### Custom Headers Format Error

**Error:** `ValueError: CUSTOM_HEADERS must be valid JSON`

**Solution:** Ensure `CUSTOM_HEADERS` is valid JSON:
```env
# Correct format
CUSTOM_HEADERS={"Authorization": "Bearer token", "X-Custom": "value"}

# Incorrect format
CUSTOM_HEADERS={Authorization: Bearer token}  # Missing quotes
```

## Testing

### Run Startup Test

To verify the application can start without errors:
```bash
python test_startup.py
```

### Run Unit Tests

To run the test suite:
```bash
pytest tests/
```

### Check Prompt Loading

To verify prompt files load correctly:
```bash
python -c "from prompts.semantic_kernel_prompts import get_chat_messages; print('OK')"
```

## Getting Help

1. Check the application logs for detailed error messages
2. Verify your environment configuration matches the examples
3. Ensure all dependencies are installed with correct versions
4. Test with a simple configuration first, then add complexity

## Common Environment Variables

```env
# Required for all providers
LLM_PROVIDER=azure

# Azure OpenAI (if using Azure)
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment

# OpenRouter (if using OpenRouter)
OPENROUTER_API_KEY=your-key
OPENROUTER_MODEL=openai/gpt-4-turbo-preview

# Custom Provider (if using custom)
CUSTOM_API_KEY=your-key
CUSTOM_API_BASE_URL=https://api.example.com/v1
CUSTOM_MODEL=your-model
```