# AI Provider Configuration Guide

This guide provides comprehensive information for configuring OpenAI-compatible AI providers with the AI Content Generation Platform.

## Table of Contents
- [Overview](#overview)
- [Quick Start](#quick-start)
- [Supported Providers](#supported-providers)
- [Configuration](#configuration)
- [Authentication Methods](#authentication-methods)
- [Environment Variables Reference](#environment-variables-reference)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

## Overview

The AI Content Generation Platform supports any OpenAI-compatible API, enabling use of local models, self-hosted services, and third-party providers. This includes:

- Local model servers (Ollama, LM Studio, vLLM)
- Self-hosted deployments (FastChat, LocalAI)
- Third-party services (Tachyon, custom deployments)
- Any service implementing the OpenAI API specification

## Quick Start

1. **Copy the configuration template**:
   ```bash
   cp .env.example .env
   ```

2. **Configure your provider settings** in the `.env` file

3. **Start the application**:
   ```bash
   python main.py
   ```

## Supported Providers

### 1. **Ollama** (Local)
Run LLMs locally on your machine with minimal setup.

```env
PROVIDER_API_BASE_URL=http://localhost:11434/v1
PROVIDER_MODEL=llama2
PROVIDER_NAME=Ollama Local
PROVIDER_API_KEY=not-needed
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

### 2. **LM Studio** (Desktop)
User-friendly desktop application for running local LLMs.

```env
PROVIDER_API_BASE_URL=http://localhost:1234/v1
PROVIDER_MODEL=local-model
PROVIDER_NAME=LM Studio
PROVIDER_API_KEY=not-needed
```

**Setup**:
1. Download LM Studio: https://lmstudio.ai
2. Download models through the UI
3. Start local server
4. Configure endpoint in settings

### 3. **vLLM** (High-Performance)
Production-grade inference server for high throughput.

```env
PROVIDER_API_BASE_URL=http://localhost:8000/v1
PROVIDER_MODEL=meta-llama/Llama-2-7b-chat-hf
PROVIDER_NAME=vLLM Server
PROVIDER_API_KEY=not-needed
```

**Setup**:
```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-chat-hf \
    --port 8000
```

### 4. **Tachyon LLM**
High-performance commercial LLM service.

```env
PROVIDER_API_BASE_URL=https://api.tachyon.ai/v1
PROVIDER_MODEL=tachyon-fast
PROVIDER_NAME=Tachyon LLM
PROVIDER_API_KEY=your-tachyon-api-key
```

**Setup**:
1. Sign up at https://tachyon.ai
2. Get API key from dashboard
3. Choose model: `tachyon-fast`, `tachyon-balanced`, `tachyon-creative`

### 5. **FastChat**
Multi-model serving platform with web UI.

```env
PROVIDER_API_BASE_URL=http://localhost:8000/v1
PROVIDER_MODEL=vicuna-7b-v1.5
PROVIDER_NAME=FastChat
PROVIDER_API_KEY=not-needed
```

### 6. **LocalAI**
OpenAI drop-in replacement for local models.

```env
PROVIDER_API_BASE_URL=http://localhost:8080/v1
PROVIDER_MODEL=gpt-3.5-turbo
PROVIDER_NAME=LocalAI
PROVIDER_API_KEY=not-needed
```

### 7. **Text Generation Inference** (Hugging Face)
Optimized inference server from Hugging Face.

```env
PROVIDER_API_BASE_URL=http://localhost:3000/v1
PROVIDER_MODEL=bigscience/bloom
PROVIDER_NAME=Text Generation Inference
PROVIDER_API_KEY=not-needed
```

## Configuration

### Basic Configuration

```env
# Required: Your API key for authentication
PROVIDER_API_KEY=your_api_key_here

# Required: Base URL for the API (must be OpenAI-compatible)
PROVIDER_API_BASE_URL=https://api.your-provider.com/v1

# Required: Model name/identifier
PROVIDER_MODEL=your-model-name

# Optional: Display name for your provider
PROVIDER_NAME=My Provider

# Optional: API compatibility type (default: "openai")
PROVIDER_API_TYPE=openai

# Optional: Additional HTTP headers (JSON format)
PROVIDER_HEADERS={}
```

### Advanced Configuration

For providers requiring special headers or authentication:

```env
# Bearer token authentication
PROVIDER_HEADERS={"Authorization": "Bearer your_token_here"}

# Custom header authentication
PROVIDER_HEADERS={"X-API-Key": "your_api_key", "X-Custom-Header": "value"}

# Multiple headers
PROVIDER_HEADERS={"X-API-Key": "key", "X-Region": "us-west", "X-Version": "v2"}
```

## Authentication Methods

Different providers use various authentication methods:

### 1. API Key in Headers (Default)
The API key is automatically sent as `Authorization: Bearer {api_key}`

### 2. Custom Headers
```env
PROVIDER_HEADERS={"X-API-Key": "your_api_key"}
```

### 3. Query Parameters
Include in the base URL:
```env
PROVIDER_API_BASE_URL=https://api.provider.com/v1?api_key=your_key
```

### 4. No Authentication (Local Models)
For local models, use a placeholder:
```env
PROVIDER_API_KEY=not-needed
```

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `PROVIDER_API_KEY` | API key for authentication | Yes | `sk-...` |
| `PROVIDER_API_BASE_URL` | Base URL for API calls | Yes | `https://api.provider.com/v1` |
| `PROVIDER_MODEL` | Model name/identifier | Yes | `llama2` |
| `PROVIDER_NAME` | Display name for provider | No | `My Provider` |
| `PROVIDER_API_TYPE` | API compatibility type | No | `openai` |
| `PROVIDER_HEADERS` | Additional HTTP headers | No | `{"X-Custom": "value"}` |
| `PROVIDER_API_VERSION` | API version (if needed) | No | `2024-01-01` |

### Application Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG_MODE` | Enable debug logging | `false` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |
| `DATABASE_URL` | Database connection | `sqlite:///./stories.db` |
| `OPENAI_TIMEOUT` | API timeout in seconds | `120` |
| `MAX_TOKENS` | Max tokens per request | `1000` |
| `TEMPERATURE` | Response randomness (0-2) | `0.7` |

## Troubleshooting

### Common Issues

#### Connection Errors
```
Error: Failed to connect to API
```
**Solutions**:
- Verify API endpoint URL is correct
- Check if the service is running (for local providers)
- Ensure firewall allows the connection
- Test with curl: `curl http://localhost:11434/v1/models`

#### Authentication Failures
```
Error: Invalid API key
```
**Solutions**:
- Double-check API key
- Verify header format in PROVIDER_HEADERS
- Check if provider requires different auth method
- For local models, use `PROVIDER_API_KEY=not-needed`

#### Model Not Found
```
Error: Model 'model-name' not found
```
**Solutions**:
- Verify exact model name with provider
- For Ollama: run `ollama list`
- For LM Studio: check loaded models in UI
- Ensure model is downloaded/deployed

#### Timeout Errors
```
Error: Request timeout
```
**Solutions**:
- Increase `OPENAI_TIMEOUT` in .env
- Check model size and hardware capabilities
- Reduce `MAX_TOKENS` for faster responses
- Consider using a smaller model

### Provider-Specific Issues

**Ollama**:
- Ensure Ollama service is running: `ollama serve`
- Model must be pulled first: `ollama pull model-name`
- Default port is 11434

**LM Studio**:
- Enable local server in settings
- Check server is started (green indicator)
- Verify port matches configuration

**vLLM**:
- Requires GPU with sufficient VRAM
- Check CUDA compatibility
- Monitor GPU memory usage

**Local Models**:
- Ensure sufficient RAM/VRAM
- Check CPU/GPU compatibility
- Monitor resource usage

## Security Best Practices

### API Key Management
1. **Never commit API keys** to version control
2. **Use environment variables** for all secrets
3. **Rotate keys regularly** for cloud providers
4. **Use placeholder keys** for local models

### Network Security
1. **Use HTTPS** for external providers
2. **Restrict local servers** to localhost only
3. **Implement firewall rules** for production
4. **Use VPN** for sensitive deployments

### Local Model Security
1. **Bind to localhost only** (127.0.0.1)
2. **Don't expose local servers** to internet
3. **Use authentication** if exposing internally
4. **Monitor access logs**

### Data Protection
1. **Review provider data policies**
2. **Understand data retention** for cloud services
3. **Keep sensitive data local** when possible
4. **Implement access controls**

---

For more information, see:
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Ollama Documentation](https://github.com/jmorganca/ollama)
- [LM Studio Guide](https://lmstudio.ai/docs)
- [vLLM Documentation](https://vllm.readthedocs.io/)