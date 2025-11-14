"""
LLM Provider Abstraction Layer

This module provides a unified interface for interacting with various LLM providers
including OpenAI, Anthropic, Ollama, Deepseek, and other open-source models.
"""

from .base import LLMProvider, LLMMessage, LLMResponse, MessageRole
from .factory import get_llm_provider, list_available_providers
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .ollama_provider import OllamaProvider
from .deepseek_provider import DeepseekProvider
from .generic_provider import GenericProvider

__all__ = [
    "LLMProvider",
    "LLMMessage",
    "LLMResponse",
    "MessageRole",
    "get_llm_provider",
    "list_available_providers",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "DeepseekProvider",
    "GenericProvider",
]

