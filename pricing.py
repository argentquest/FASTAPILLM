# AI Provider Pricing Configuration Module
# Contains pricing information for different AI models and providers
# Used for calculating costs based on token usage

from typing import Dict, Tuple, Optional
from decimal import Decimal
import structlog

logger = structlog.get_logger(__name__)

# =============================================================================
# PROVIDER PRICING DATA
# =============================================================================
# Pricing is stored as cost per 1,000 tokens (standard industry format)
# All prices are in USD
# 
# Format: "provider/model": {
#     "input_cost_per_1k": cost for 1000 input tokens,
#     "output_cost_per_1k": cost for 1000 output tokens
# }
#
# Sources:
# - OpenRouter: https://openrouter.ai/models
# - OpenAI: https://openai.com/pricing
# - Last updated: 2025-07-28

PROVIDER_PRICING: Dict[str, Dict[str, Decimal]] = {
    # =================================================================
    # OPENROUTER MODELS
    # =================================================================
    
    # Meta Llama Models
    "meta-llama/llama-3-8b-instruct": {
        "input_cost_per_1k": Decimal("0.00018"),
        "output_cost_per_1k": Decimal("0.00018")
    },
    "meta-llama/llama-3-70b-instruct": {
        "input_cost_per_1k": Decimal("0.00081"),
        "output_cost_per_1k": Decimal("0.00081")
    },
    "meta-llama/llama-2-70b-chat": {
        "input_cost_per_1k": Decimal("0.00070"),
        "output_cost_per_1k": Decimal("0.00090")
    },
    
    # OpenAI Models (via OpenRouter)
    "openai/gpt-4-turbo-preview": {
        "input_cost_per_1k": Decimal("0.01000"),
        "output_cost_per_1k": Decimal("0.03000")
    },
    "openai/gpt-4": {
        "input_cost_per_1k": Decimal("0.03000"),
        "output_cost_per_1k": Decimal("0.06000")
    },
    "openai/gpt-3.5-turbo": {
        "input_cost_per_1k": Decimal("0.00150"),
        "output_cost_per_1k": Decimal("0.00200")
    },
    
    # Anthropic Models (via OpenRouter)
    "anthropic/claude-3-sonnet": {
        "input_cost_per_1k": Decimal("0.00300"),
        "output_cost_per_1k": Decimal("0.01500")
    },
    "anthropic/claude-3-haiku": {
        "input_cost_per_1k": Decimal("0.00025"),
        "output_cost_per_1k": Decimal("0.00125")
    },
    "anthropic/claude-3-opus": {
        "input_cost_per_1k": Decimal("0.01500"),
        "output_cost_per_1k": Decimal("0.07500")
    },
    
    # Google Models (via OpenRouter)
    "google/gemini-pro": {
        "input_cost_per_1k": Decimal("0.00025"),
        "output_cost_per_1k": Decimal("0.00050")
    },
    "google/gemini-flash-1.5": {
        "input_cost_per_1k": Decimal("0.00025"),
        "output_cost_per_1k": Decimal("0.00075")
    },
    
    # Mistral Models (via OpenRouter)
    "mistralai/mistral-7b-instruct": {
        "input_cost_per_1k": Decimal("0.00025"),
        "output_cost_per_1k": Decimal("0.00025")
    },
    "mistralai/mixtral-8x7b-instruct": {
        "input_cost_per_1k": Decimal("0.00024"),
        "output_cost_per_1k": Decimal("0.00024")
    },
    
    # =================================================================
    # FREE TIER MODELS (OpenRouter)
    # =================================================================
    # These models have free tiers but may have rate limits
    
    "meta-llama/llama-3-8b-instruct:free": {
        "input_cost_per_1k": Decimal("0.00000"),
        "output_cost_per_1k": Decimal("0.00000")
    },
    "mistralai/mistral-7b-instruct:free": {
        "input_cost_per_1k": Decimal("0.00000"),
        "output_cost_per_1k": Decimal("0.00000")
    },
    "google/gemini-flash-1.5:free": {
        "input_cost_per_1k": Decimal("0.00000"),
        "output_cost_per_1k": Decimal("0.00000")
    },
    
    # =================================================================
    # LOCAL MODELS (No cost)
    # =================================================================
    # Local models running on Ollama, LM Studio, etc. have no API costs
    
    "llama2": {
        "input_cost_per_1k": Decimal("0.00000"),
        "output_cost_per_1k": Decimal("0.00000")
    },
    "codellama": {
        "input_cost_per_1k": Decimal("0.00000"),
        "output_cost_per_1k": Decimal("0.00000")
    },
    "mistral": {
        "input_cost_per_1k": Decimal("0.00000"),
        "output_cost_per_1k": Decimal("0.00000")
    },
    "neural-chat": {
        "input_cost_per_1k": Decimal("0.00000"),
        "output_cost_per_1k": Decimal("0.00000")
    },
    
    # =================================================================
    # TACHYON MODELS (Estimated pricing)
    # =================================================================
    # Tachyon pricing may vary - these are estimates
    
    "tachyon-fast": {
        "input_cost_per_1k": Decimal("0.00100"),
        "output_cost_per_1k": Decimal("0.00100")
    },
    "tachyon-balanced": {
        "input_cost_per_1k": Decimal("0.00200"),
        "output_cost_per_1k": Decimal("0.00200")
    },
    "tachyon-creative": {
        "input_cost_per_1k": Decimal("0.00300"),
        "output_cost_per_1k": Decimal("0.00300")
    },
}

# Default pricing for unknown models (prevents errors)
DEFAULT_PRICING = {
    "input_cost_per_1k": Decimal("0.00000"),
    "output_cost_per_1k": Decimal("0.00000")
}


def get_model_pricing(model: str) -> Dict[str, Decimal]:
    """Get pricing information for a specific model.
    
    Returns pricing data for the specified model, including costs per
    1,000 tokens for both input and output. If the model is not found,
    returns default pricing (free) to prevent errors.
    
    Args:
        model (str): Model identifier (e.g., "meta-llama/llama-3-8b-instruct")
        
    Returns:
        Dict[str, Decimal]: Pricing information containing:
            - input_cost_per_1k: Cost per 1,000 input tokens
            - output_cost_per_1k: Cost per 1,000 output tokens
            
    Examples:
        >>> pricing = get_model_pricing("meta-llama/llama-3-8b-instruct")
        >>> print(f"Input: ${pricing['input_cost_per_1k']}/1k tokens")
        Input: $0.000180/1k tokens
        >>> 
        >>> # Unknown model returns free pricing
        >>> pricing = get_model_pricing("unknown-model")
        >>> print(f"Cost: ${pricing['input_cost_per_1k']}")
        Cost: $0.000000
    """
    pricing = PROVIDER_PRICING.get(model, DEFAULT_PRICING)
    
    if model not in PROVIDER_PRICING:
        logger.warning("Unknown model - using default (free) pricing",
                      model=model,
                      available_models=len(PROVIDER_PRICING))
    else:
        logger.debug("Retrieved pricing for model",
                    model=model,
                    input_cost=pricing["input_cost_per_1k"],
                    output_cost=pricing["output_cost_per_1k"])
    
    return pricing


def calculate_cost(
    model: str, 
    input_tokens: int, 
    output_tokens: int
) -> Tuple[Decimal, Decimal, Decimal]:
    """Calculate the cost for a specific API call.
    
    Calculates the monetary cost of an AI request based on token usage
    and model pricing. Returns both component costs and total cost.
    
    Args:
        model (str): Model identifier used for the request
        input_tokens (int): Number of input tokens consumed
        output_tokens (int): Number of output tokens generated
        
    Returns:
        Tuple[Decimal, Decimal, Decimal]: A tuple containing:
            - input_cost: Cost for input tokens
            - output_cost: Cost for output tokens  
            - total_cost: Combined cost (input + output)
            
    Examples:
        >>> # Calculate cost for a Llama 3 request
        >>> input_cost, output_cost, total = calculate_cost(
        ...     "meta-llama/llama-3-8b-instruct", 
        ...     1000,  # 1k input tokens
        ...     500    # 500 output tokens
        ... )
        >>> print(f"Total cost: ${total}")
        Total cost: $0.000270
        >>> 
        >>> # Free model returns zero cost
        >>> _, _, total = calculate_cost("llama2", 1000, 500)
        >>> print(f"Local model cost: ${total}")
        Local model cost: $0.000000
    """
    # Get pricing for the model
    pricing = get_model_pricing(model)
    
    # Calculate costs (convert tokens to thousands for pricing)
    input_cost = (Decimal(input_tokens) / 1000) * pricing["input_cost_per_1k"]
    output_cost = (Decimal(output_tokens) / 1000) * pricing["output_cost_per_1k"]
    total_cost = input_cost + output_cost
    
    logger.debug("Cost calculated for API request",
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                input_cost=float(input_cost),
                output_cost=float(output_cost),
                total_cost=float(total_cost))
    
    return input_cost, output_cost, total_cost


def get_cost_summary(model: str) -> Dict[str, any]:
    """Get a human-readable cost summary for a model.
    
    Returns pricing information in a format suitable for display
    in user interfaces or logging.
    
    Args:
        model (str): Model identifier
        
    Returns:
        Dict[str, any]: Cost summary containing:
            - model: Model name
            - input_cost_per_1k: Input cost per 1k tokens (as float)
            - output_cost_per_1k: Output cost per 1k tokens (as float)
            - is_free: Whether the model is free to use
            - cost_tier: Descriptive cost tier (free, cheap, moderate, expensive)
            
    Examples:
        >>> summary = get_cost_summary("meta-llama/llama-3-8b-instruct")
        >>> print(f"{summary['model']}: {summary['cost_tier']}")
        meta-llama/llama-3-8b-instruct: cheap
    """
    pricing = get_model_pricing(model)
    
    input_cost = float(pricing["input_cost_per_1k"])
    output_cost = float(pricing["output_cost_per_1k"])
    avg_cost = (input_cost + output_cost) / 2
    
    # Determine cost tier
    if avg_cost == 0:
        cost_tier = "free"
    elif avg_cost < 0.001:
        cost_tier = "cheap"
    elif avg_cost < 0.01:
        cost_tier = "moderate"
    else:
        cost_tier = "expensive"
    
    return {
        "model": model,
        "input_cost_per_1k": input_cost,
        "output_cost_per_1k": output_cost,
        "is_free": avg_cost == 0,
        "cost_tier": cost_tier,
        "average_cost_per_1k": avg_cost
    }