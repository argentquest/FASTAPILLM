# AI Provider Configuration Guide

This guide provides comprehensive information for configuring different AI providers with the AI Content Generation Platform. The platform supports three main provider types: Azure OpenAI, OpenRouter, and Custom/Third-Party providers.

## Table of Contents
- [Provider Overview](#provider-overview)
- [Quick Start](#quick-start)
- [Azure OpenAI](#azure-openai)
- [OpenRouter](#openrouter)
- [Custom Providers](#custom-providers)
- [Environment Variables Reference](#environment-variables-reference)
- [Provider Comparison](#provider-comparison)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

## Provider Overview

The AI Content Generation Platform supports multiple AI providers through a unified interface:

- **Azure OpenAI**: Enterprise-grade deployment with data privacy and SLA guarantees
- **OpenRouter**: Multi-model access through a single API with pay-per-use pricing
- **Custom Providers**: Any OpenAI-compatible API including local and third-party services

### Environment Templates

We provide provider-specific templates for easy configuration:

```bash
.env.example           # Generic template with all options
.env.azure.example     # Azure OpenAI specific configuration
.env.openrouter.example # OpenRouter specific configuration
.env.custom.example    # Custom/third-party provider configuration
```

## Quick Start

1. **Choose your provider**:
   - Azure OpenAI: Enterprise features, requires Azure subscription
   - OpenRouter: Easy setup, multiple models, pay-per-use
   - Custom: Local models or third-party services

2. **Copy the appropriate template**:
   ```bash
   # For Azure OpenAI
   cp .env.azure.example .env

   # For OpenRouter
   cp .env.openrouter.example .env

   # For custom providers
   cp .env.custom.example .env
   ```

3. **Configure your settings** in the `.env` file

4. **Start the application**:
   ```bash
   python main.py
   ```

## Azure OpenAI

### Overview
Azure OpenAI provides enterprise-grade AI capabilities with enhanced security, compliance, and support. It's ideal for production deployments requiring data privacy and SLA guarantees.

### Prerequisites
- Azure subscription
- Approved access to Azure OpenAI service
- Deployed model in Azure OpenAI Studio

### Configuration

```env
LLM_PROVIDER=azure
AZURE_OPENAI_API_KEY=your_azure_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Setup Steps

1. **Apply for Azure OpenAI access**:
   - Visit: https://aka.ms/oai/access
   - Complete the application form
   - Wait for approval (typically 1-2 business days)

2. **Create Azure OpenAI resource**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Create new "Azure OpenAI" resource
   - Select region and pricing tier

3. **Deploy a model**:
   - Navigate to Azure OpenAI Studio: https://oai.azure.com
   - Deploy a model (e.g., GPT-4, GPT-3.5-Turbo)
   - Note the deployment name (not the model name)

4. **Get credentials**:
   - Azure Portal → Your OpenAI Resource → Keys and Endpoint
   - Copy the endpoint URL and one of the API keys

### Available Models
- **GPT-4**: Most capable model for complex tasks
- **GPT-4-32k**: Extended context window for longer documents
- **GPT-3.5-Turbo**: Fast and cost-effective for most tasks
- **GPT-3.5-Turbo-16k**: Extended context for GPT-3.5

### Key Benefits
- **Data Privacy**: Your data stays within your Azure tenant
- **Compliance**: SOC 2, ISO 27001, HIPAA eligible
- **SLA**: 99.9% uptime guarantee
- **Support**: Enterprise support options
- **Regional Deployment**: Deploy in your preferred Azure region

## OpenRouter

### Overview
OpenRouter provides unified access to multiple AI models through a single API, including models from OpenAI, Anthropic, Google, Meta, and more. It's perfect for experimentation and comparing different models.

### Configuration

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=openai/gpt-4-turbo-preview
OPENROUTER_SITE_URL=http://localhost:8000
OPENROUTER_APP_NAME=AI Content Platform
```

### Setup Steps

1. **Create account**:
   - Sign up at https://openrouter.ai
   - Verify your email

2. **Add credits**:
   - Add payment method
   - Purchase credits (pay-as-you-go)

3. **Generate API key**:
   - Visit https://openrouter.ai/keys
   - Create new API key
   - Copy and save securely

4. **Choose model**:
   - Browse models: https://openrouter.ai/models
   - Check pricing and capabilities
   - Select model identifier

### Popular Models

#### General Purpose
- `openai/gpt-4-turbo-preview` - Latest GPT-4 with 128k context
- `openai/gpt-3.5-turbo` - Fast and affordable
- `anthropic/claude-3-sonnet` - Balanced performance
- `google/gemini-pro` - Google's latest model

#### Specialized Use Cases
- **Creative Writing**: `anthropic/claude-3-sonnet`
- **Code Generation**: `openai/gpt-4-turbo-preview`
- **Fast Responses**: `anthropic/claude-3-haiku`
- **Long Context**: `anthropic/claude-3-sonnet-200k`
- **Open Source**: `meta-llama/llama-2-70b-chat`

### Model Pricing Guide
- **Budget**: GPT-3.5-Turbo (~$0.002/1k tokens)
- **Balanced**: Claude 3 Haiku (~$0.003/1k tokens)
- **Premium**: GPT-4 Turbo (~$0.03/1k tokens)
- **Ultra**: Claude 3 Opus (~$0.06/1k tokens)

### Key Benefits
- **Model Variety**: Access 50+ models from different providers
- **No Commitment**: Pay only for what you use
- **Easy Switching**: Change models with one line
- **Transparent Pricing**: See costs upfront
- **Usage Analytics**: Built-in tracking and reporting

## Custom Providers

### Overview
The platform supports any OpenAI-compatible API, enabling use of local models, self-hosted services, and third-party providers.

### Configuration

```env
LLM_PROVIDER=custom
CUSTOM_API_KEY=your_api_key_here
CUSTOM_API_BASE_URL=https://api.your-provider.com/v1
CUSTOM_MODEL=your-model-name
CUSTOM_PROVIDER_NAME=Your Provider Name
CUSTOM_API_TYPE=openai
CUSTOM_HEADERS={}
```

### Supported Providers

#### 1. **Tachyon LLM**
High-performance commercial LLM service.

```env
CUSTOM_API_BASE_URL=https://api.tachyon.ai/v1
CUSTOM_MODEL=tachyon-fast
CUSTOM_PROVIDER_NAME=Tachyon LLM
```

**Setup**:
1. Sign up at https://tachyon.ai
2. Get API key from dashboard
3. Choose model: `tachyon-fast`, `tachyon-balanced`, `tachyon-creative`

#### 2. **Ollama** (Local)
Run LLMs locally on your machine.

```env
CUSTOM_API_BASE_URL=http://localhost:11434/v1
CUSTOM_MODEL=llama2
CUSTOM_PROVIDER_NAME=Ollama Local
```

**Setup**:
1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama2`
3. Start server: `ollama serve`

**Popular Models**:
- `llama2` - Meta's Llama 2
- `codellama` - Code-focused model
- `mistral` - Efficient 7B model
- `neural-chat` - Intel's chat model

#### 3. **LM Studio** (Desktop)
User-friendly desktop application for local LLMs.

```env
CUSTOM_API_BASE_URL=http://localhost:1234/v1
CUSTOM_MODEL=local-model
CUSTOM_PROVIDER_NAME=LM Studio
```

**Setup**:
1. Download LM Studio: https://lmstudio.ai
2. Download models through the UI
3. Start local server
4. Configure endpoint in settings

#### 4. **vLLM** (High-Performance)
Production-grade inference server.

```env
CUSTOM_API_BASE_URL=http://localhost:8000/v1
CUSTOM_MODEL=meta-llama/Llama-2-7b-chat-hf
CUSTOM_PROVIDER_NAME=vLLM Server
```

**Setup**:
```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-chat-hf \
    --port 8000
```

#### 5. **FastChat**
Multi-model serving platform.

```env
CUSTOM_API_BASE_URL=http://localhost:8000/v1
CUSTOM_MODEL=vicuna-7b-v1.5
CUSTOM_PROVIDER_NAME=FastChat
```

#### 6. **LocalAI**
OpenAI drop-in replacement for local models.

```env
CUSTOM_API_BASE_URL=http://localhost:8080/v1
CUSTOM_MODEL=gpt-3.5-turbo
CUSTOM_PROVIDER_NAME=LocalAI
```

#### 7. **Text Generation Inference** (Hugging Face)
Optimized inference server from Hugging Face.

```env
CUSTOM_API_BASE_URL=http://localhost:3000/v1
CUSTOM_MODEL=bigscience/bloom
CUSTOM_PROVIDER_NAME=Text Generation Inference
```

### Authentication Methods

Different providers use various authentication methods:

#### Bearer Token (Most Common)
```env
CUSTOM_HEADERS={"Authorization": "Bearer your_api_key"}
```

#### Custom Header
```env
CUSTOM_HEADERS={"X-API-Key": "your_api_key"}
```

#### Query Parameter
```env
CUSTOM_API_BASE_URL=https://api.provider.com/v1?api_key=your_key
```

#### Basic Authentication
```env
CUSTOM_HEADERS={"Authorization": "Basic base64_encoded_credentials"}
```

## Environment Variables Reference

### Provider Selection
| Variable | Description | Options |
|----------|-------------|---------|
| `LLM_PROVIDER` | Select the AI provider | `azure`, `openrouter`, `custom` |

### Azure OpenAI Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key | `abc123...` |
| `AZURE_OPENAI_ENDPOINT` | Your resource endpoint | `https://myresource.openai.azure.com/` |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Your model deployment name | `gpt-4` |
| `AZURE_OPENAI_API_VERSION` | API version to use | `2024-02-15-preview` |

### OpenRouter Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | `sk-or-...` |
| `OPENROUTER_MODEL` | Model identifier | `openai/gpt-4-turbo-preview` |
| `OPENROUTER_SITE_URL` | Your site URL (optional) | `http://localhost:8000` |
| `OPENROUTER_APP_NAME` | Your app name (optional) | `My App` |

### Custom Provider Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `CUSTOM_API_KEY` | API key for authentication | `your-key` |
| `CUSTOM_API_BASE_URL` | Base URL for API calls | `https://api.provider.com/v1` |
| `CUSTOM_MODEL` | Model name/identifier | `model-name` |
| `CUSTOM_PROVIDER_NAME` | Display name for provider | `My Provider` |
| `CUSTOM_API_TYPE` | API compatibility type | `openai` |
| `CUSTOM_HEADERS` | Additional HTTP headers | `{"X-Custom": "value"}` |

### Application Settings
| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG_MODE` | Enable debug logging | `false` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `DATABASE_URL` | Database connection string | `sqlite:///./stories.db` |
| `OPENAI_TIMEOUT` | API timeout in seconds | `120` |
| `MAX_TOKENS` | Max tokens per request | `1000` |
| `TEMPERATURE` | Response randomness (0-2) | `0.7` |

## Provider Comparison

| Feature | Azure OpenAI | OpenRouter | Custom |
|---------|--------------|------------|---------|
| **Setup Complexity** | Medium | Easy | Varies |
| **Cost Model** | Pay-per-use + Committed | Pay-per-use | Varies |
| **Model Selection** | Limited to deployed | 50+ models | Provider-specific |
| **Data Privacy** | Excellent | Standard | Self-controlled |
| **SLA** | 99.9% | Best effort | Self-managed |
| **Support** | Enterprise | Community | Varies |
| **Best For** | Production | Experimentation | Special needs |

### When to Use Each Provider

**Azure OpenAI**:
- Production deployments
- Regulated industries
- Enterprise requirements
- Data sovereignty needs
- Consistent performance requirements

**OpenRouter**:
- Development and testing
- Model comparison
- Rapid prototyping
- Multi-model applications
- Cost optimization

**Custom Providers**:
- Local development
- Air-gapped environments
- Specialized models
- Cost control
- Custom requirements

## Troubleshooting

### Common Issues

#### Connection Errors
```
Error: Failed to connect to API
```
**Solutions**:
- Verify API endpoint URL
- Check network connectivity
- Ensure service is running (for local providers)
- Verify firewall settings

#### Authentication Failures
```
Error: Invalid API key
```
**Solutions**:
- Double-check API key
- Ensure proper header format
- Verify key hasn't expired
- Check provider-specific auth requirements

#### Model Not Found
```
Error: Model 'model-name' not found
```
**Solutions**:
- Verify exact model name
- Check model availability
- Ensure model is deployed (Azure)
- Pull model first (Ollama)

#### Timeout Errors
```
Error: Request timeout
```
**Solutions**:
- Increase `OPENAI_TIMEOUT`
- Check model performance
- Reduce `MAX_TOKENS`
- Use faster model

### Provider-Specific Issues

**Azure OpenAI**:
- Deployment vs model name confusion
- Regional availability
- Quota limitations
- API version compatibility

**OpenRouter**:
- Credit balance
- Model availability
- Rate limiting
- Usage tracking

**Custom Providers**:
- API compatibility
- Response format
- Missing usage data
- Local resource limits

## Security Best Practices

### API Key Management
1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Rotate keys regularly**
4. **Use separate keys** for dev/prod
5. **Monitor key usage**

### Network Security
1. **Use HTTPS** for all external providers
2. **Implement firewall rules** for local providers
3. **Use VPN** for sensitive deployments
4. **Monitor network traffic**
5. **Implement rate limiting**

### Data Protection
1. **Review provider data policies**
2. **Understand data retention**
3. **Implement access controls**
4. **Audit API usage**
5. **Encrypt sensitive data**

### Compliance Considerations
1. **Azure OpenAI**: SOC 2, ISO 27001, HIPAA eligible
2. **OpenRouter**: Review terms of service
3. **Custom**: Your responsibility
4. **Local Models**: Full control and responsibility

---

For more information, see:
- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)