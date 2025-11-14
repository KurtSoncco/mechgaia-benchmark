"""
Base classes for LLM providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum


class MessageRole(str, Enum):
    """Message roles for LLM conversations."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class LLMMessage:
    """Represents a message in an LLM conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    model: str
    usage: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the LLM provider.
        
        Args:
            model: Model name/identifier
            api_key: API key for authentication (if required)
            base_url: Base URL for the API (if custom)
            **kwargs: Additional provider-specific parameters
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.config = kwargs
    
    @abstractmethod
    def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Send a chat completion request.
        
        Args:
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            tools: Available tools/functions for the model
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLMResponse object with the model's response
        """
        pass
    
    @abstractmethod
    def stream_chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        """
        Send a streaming chat completion request.
        
        Args:
            messages: List of messages in the conversation
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            tools: Available tools/functions
            **kwargs: Additional parameters
            
        Yields:
            Chunks of LLMResponse objects as they arrive
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """
        List available models for this provider.
        
        Returns:
            List of model identifiers
        """
        pass
    
    def supports_tools(self) -> bool:
        """
        Check if this provider supports tool/function calling.
        
        Returns:
            True if tools are supported, False otherwise
        """
        return False
    
    def supports_streaming(self) -> bool:
        """
        Check if this provider supports streaming responses.
        
        Returns:
            True if streaming is supported, False otherwise
        """
        return True

