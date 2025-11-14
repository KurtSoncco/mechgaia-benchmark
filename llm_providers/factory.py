"""
Factory for creating LLM provider instances.
"""

import os
from typing import Dict, List, Optional, Type
from .base import LLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider
from .deepseek_provider import DeepseekProvider
from .generic_provider import GenericProvider


_PROVIDER_REGISTRY: Dict[str, Type[LLMProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "claude": AnthropicProvider,  # Alias
    "ollama": OllamaProvider,
    "deepseek": DeepseekProvider,
    "generic": GenericProvider,
}


def register_provider(name: str, provider_class: Type[LLMProvider]) -> None:
    """
    Register a new LLM provider.
    
    Args:
        name: Provider name identifier
        provider_class: Provider class implementation
    """
    _PROVIDER_REGISTRY[name.lower()] = provider_class


def list_available_providers() -> List[str]:
    """
    List all registered provider names.
    
    Returns:
        List of provider names
    """
    return list(_PROVIDER_REGISTRY.keys())


def get_llm_provider(
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> LLMProvider:
    """
    Create an LLM provider instance.
    
    Args:
        provider: Provider name (e.g., "openai", "anthropic", "ollama")
        model: Model name/identifier
        api_key: API key (can also be set via environment variable)
        base_url: Custom base URL for the API
        **kwargs: Additional provider-specific parameters
        
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider is not found or configuration is invalid
    """
    provider_lower = provider.lower()
    
    if provider_lower not in _PROVIDER_REGISTRY:
        available = ", ".join(list_available_providers())
        raise ValueError(
            f"Unknown provider '{provider}'. Available providers: {available}"
        )
    
    provider_class = _PROVIDER_REGISTRY[provider_lower]
    
    # Try to get API key from environment if not provided
    if api_key is None:
        env_key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "claude": "ANTHROPIC_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
        }
        env_key = env_key_map.get(provider_lower)
        if env_key:
            api_key = os.getenv(env_key)
    
    # Try to get base URL from environment if not provided
    if base_url is None:
        env_url_map = {
            "ollama": "OLLAMA_BASE_URL",
        }
        env_url = env_url_map.get(provider_lower)
        if env_url:
            base_url = os.getenv(env_url, "http://localhost:11434")
    
    return provider_class(model=model, api_key=api_key, base_url=base_url, **kwargs)

