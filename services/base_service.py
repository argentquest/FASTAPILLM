from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union, Tuple
import asyncio
import time
from openai import AsyncOpenAI, APIError, APIConnectionError, RateLimitError
import httpx

from config import settings
from logging_config import get_logger
from pricing import calculate_cost, get_model_pricing
from exceptions import (
    APIKeyError,
    APIConnectionError as CustomAPIConnectionError,
    APIRateLimitError,
    TimeoutError
)

logger = get_logger(__name__)

class BaseService(ABC):
    """Base class for all AI generation services.
    
    This abstract base class provides common functionality for AI
    generation services including:
    - Client initialization for custom OpenAI-compatible providers
    - Connection pooling and retry logic
    - Error handling and logging
    - Token usage tracking
    
    Subclasses must implement the generate_story method.
    
    Attributes:
        service_name: The name of the service class.
        provider_name: The custom provider name.
    """
    
    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None
        self.service_name = self.__class__.__name__
        self.provider_name = settings.provider_name
        
    @property
    def client(self) -> AsyncOpenAI:
        """Lazy initialization of OpenAI client.
        
        Creates the client on first access to avoid initialization
        overhead during service creation.
        
        Returns:
            An AsyncOpenAI client instance.
            
        Raises:
            APIKeyError: If client initialization fails.
        """
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    def _create_client(self) -> AsyncOpenAI:
        """Create OpenAI client with connection pooling.
        
        Initializes the client for the custom provider
        with optimized connection settings for performance.
        
        Returns:
            A configured AsyncOpenAI client.
            
        Raises:
            APIKeyError: If client initialization fails.
            NotImplementedError: If custom API type is not supported.
            
        Examples:
            >>> client = self._create_client()
            >>> isinstance(client, AsyncOpenAI)
            True
        """
        try:
            # Create httpx client with connection pooling
            http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.openai_timeout),
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10,
                )
            )
            
            # Provider (e.g., Tachyon, Ollama, LM Studio)
            # HEADERS CONFIGURATION: To change provider headers, update PROVIDER_HEADERS in .env
            # Examples:
            # - OpenRouter: {"HTTP-Referer": "http://localhost:8000", "X-Title": "App Name"}
            # - Tachyon/Standard: {} (empty - uses default Authorization header)
            # - Custom Auth: {"X-API-Key": "your-key", "Authorization": "Bearer token"}
            headers = settings.provider_headers or {}
            
            if settings.provider_api_type == "openai":
                # Use OpenAI-compatible client
                # The headers defined above are passed to ALL API calls made by this client
                client = AsyncOpenAI(
                    api_key=settings.provider_api_key,  # Sent as Authorization: Bearer {key}
                    base_url=settings.provider_api_base_url,
                    http_client=http_client,
                    max_retries=0,
                    default_headers=headers  # ← HEADERS ARE SET HERE for all requests
                )
            else:
                # For non-OpenAI compatible APIs, we'd need a custom implementation
                raise NotImplementedError(
                    f"Provider API type '{settings.provider_api_type}' is not yet implemented. "
                    "Currently only 'openai' compatible APIs are supported."
                )
            
            logger.info("Provider client created",
                       service=self.service_name,
                       provider=settings.provider_name,
                       base_url=settings.provider_api_base_url,
                       model=settings.provider_model)
            
            return client
        except Exception as e:
            logger.error(f"Failed to create {settings.provider_name} client",
                        service=self.service_name,
                        error=str(e))
            raise APIKeyError(f"Failed to initialize {settings.provider_name} client")
    
    async def _call_api_with_retry(self, messages: list[Dict[str, str]], **kwargs) -> tuple[str, Dict[str, Any]]:
        """Call OpenAI API with retry logic.
        
        Implements exponential backoff retry strategy for handling
        transient connection errors and API failures.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            **kwargs: Additional parameters passed to the API call.
            
        Returns:
            A tuple of (response_content, usage_info) where usage_info
            contains token counts and execution time.
            
        Raises:
            APIConnectionError: If all retry attempts fail.
            APIError: If the API returns an error after all retries.
            
        Examples:
            >>> response, usage = await self._call_api_with_retry(
            ...     [{"role": "user", "content": "Tell me a story"}]
            ... )
        """
        max_attempts = 3
        base_wait = 2  # seconds
        
        for attempt in range(max_attempts):
            try:
                return await self._call_api(messages, **kwargs)
            except (APIConnectionError, APIError) as e:
                if attempt == max_attempts - 1:
                    logger.error("All retry attempts failed",
                                service=self.service_name,
                                attempts=max_attempts,
                                error=str(e))
                    raise
                
                wait_time = base_wait * (2 ** attempt)  # Exponential backoff
                logger.warning("Retrying API call",
                              service=self.service_name,
                              attempt=attempt + 1,
                              wait_time=wait_time,
                              error=str(e))
                await asyncio.sleep(wait_time)
    
    async def _call_api(self, messages: list[Dict[str, str]], **kwargs) -> tuple[str, Dict[str, Any]]:
        """Call OpenAI API.
        
        Makes the actual API call to the configured LLM provider with
        proper error handling and usage tracking.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            **kwargs: Optional parameters:
                - temperature: Controls randomness (0-2). Defaults to 0.7.
                - max_tokens: Maximum tokens to generate. Defaults to 500.
                
        Returns:
            A tuple containing:
            - response_content: The generated text response
            - usage_info: Dictionary with token counts and timing:
                - input_tokens: Number of tokens in the prompt
                - output_tokens: Number of tokens in the response
                - total_tokens: Sum of input and output tokens
                - execution_time_ms: API call duration in milliseconds
                
        Raises:
            TimeoutError: If the API call exceeds the timeout.
            APIRateLimitError: If rate limits are exceeded.
            CustomAPIConnectionError: For connection failures.
            APIError: For other API errors.
            
        Examples:
            >>> content, usage = await self._call_api(
            ...     [{"role": "system", "content": "You are a storyteller"},
            ...      {"role": "user", "content": "Tell me about Alice"}],
            ...     temperature=0.8,
            ...     max_tokens=1000
            ... )
        """
        try:
            # Set default parameters based on provider
            model = settings.provider_model
            
            params = {
                "model": model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 500),
                "timeout": settings.openai_timeout
            }
            
            # Make API call
            logger.debug(f"Calling {settings.provider_name} API",
                        service=self.service_name,
                        model=model,
                        message_count=len(messages))
            
            start_time = time.time()
            response = await asyncio.wait_for(
                self.client.chat.completions.create(**params),
                timeout=settings.openai_timeout
            )
            execution_time_ms = (time.time() - start_time) * 1000
            
            content = response.choices[0].message.content
            
            # Extract token usage from response
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            total_tokens = response.usage.total_tokens if response.usage else 0
            
            # Calculate cost information using pricing module
            input_cost, output_cost, total_cost = calculate_cost(model, input_tokens, output_tokens)
            pricing = get_model_pricing(model)
            
            # Prepare comprehensive usage information including costs
            usage_info = {
                # Token usage information
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                
                # Cost information (converted to float for JSON serialization)
                "estimated_cost_usd": float(total_cost),
                "input_cost": float(input_cost),
                "output_cost": float(output_cost),
                "input_cost_per_1k_tokens": float(pricing["input_cost_per_1k"]),
                "output_cost_per_1k_tokens": float(pricing["output_cost_per_1k"]),
                
                # Performance metrics
                "execution_time_ms": round(execution_time_ms, 2)
            }
            
            logger.info("API call successful",
                       service=self.service_name,
                       provider=settings.provider_name,
                       model=model,
                       response_length=len(content) if content else 0,
                       execution_time_ms=usage_info["execution_time_ms"],
                       input_tokens=usage_info["input_tokens"],
                       output_tokens=usage_info["output_tokens"],
                       total_tokens=usage_info["total_tokens"],
                       estimated_cost_usd=usage_info["estimated_cost_usd"])
            
            return content or "", usage_info
            
        except asyncio.TimeoutError:
            logger.error("API call timed out",
                        service=self.service_name,
                        timeout=settings.openai_timeout)
            raise TimeoutError(f"API call timed out after {settings.openai_timeout} seconds")
        
        except RateLimitError as e:
            logger.error("API rate limit exceeded",
                        service=self.service_name,
                        error=str(e))
            raise APIRateLimitError("API rate limit exceeded. Please try again later.")
        
        except APIConnectionError as e:
            logger.error("API connection failed",
                        service=self.service_name,
                        error=str(e))
            raise CustomAPIConnectionError(f"Failed to connect to API: {str(e)}")
        
        except APIError as e:
            logger.error("API error occurred",
                        service=self.service_name,
                        error=str(e),
                        error_type=type(e).__name__)
            raise CustomAPIConnectionError(f"API error: {str(e)}")
        
        except Exception as e:
            logger.error("Unexpected error in API call",
                        service=self.service_name,
                        error=str(e),
                        error_type=type(e).__name__)
            raise
    
    @abstractmethod
    async def generate_content(self, primary_input: str, secondary_input: str) -> Tuple[str, Dict[str, Any]]:
        """Generate content with the given inputs.
        
        Abstract method that must be implemented by subclasses to generate
        content using their specific approach (Semantic Kernel, LangChain, etc.).
        
        Args:
            primary_input: The main input parameter.
            secondary_input: The secondary input parameter.
            
        Returns:
            A tuple containing:
            - content: The generated content text
            - usage_info: Dictionary with token usage and timing information
            
        Raises:
            Any exceptions from the underlying API calls.
        """
        pass
    
    # Backwards compatibility alias for story generation
    async def generate_story(self, primary_character: str, secondary_character: str) -> Tuple[str, Dict[str, Any]]:
        """Generate a story with the given characters (deprecated: use generate_content).
        
        This method provides backwards compatibility for existing story generation code.
        New implementations should use generate_content() instead.
        
        Args:
            primary_character: The main character's name.
            secondary_character: The secondary character's name.
            
        Returns:
            A tuple containing the generated story and usage information.
        """
        return await self.generate_content(primary_character, secondary_character)
    
    async def close(self):
        """Clean up resources.
        
        Closes the HTTP client connection if it exists. Should be called
        when the service is no longer needed to free up resources.
        
        Examples:
            >>> service = SomeStoryService()
            >>> try:
            ...     # Use service
            ... finally:
            ...     await service.close()
        """
        if self._client and hasattr(self._client, '_client'):
            await self._client._client.aclose()
            logger.info("Client connection closed", service=self.service_name)