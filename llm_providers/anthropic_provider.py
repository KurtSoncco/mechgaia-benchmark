"""
Anthropic (Claude) provider implementation.
"""

import os
from typing import Any, Dict, List, Optional
from .base import LLMProvider, LLMMessage, LLMResponse, MessageRole

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) API provider."""
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic package not installed. Install with: pip install anthropic"
            )
        
        super().__init__(model, api_key, base_url, **kwargs)
        
        self.client = Anthropic(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            base_url=base_url,
        )
    
    def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request."""
        # Convert messages to Anthropic format
        anthropic_messages = []
        system_message = None
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            elif msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                anthropic_messages.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })
        
        # Prepare request
        request_params = {
            "model": self.model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4096,
            **kwargs
        }
        
        if system_message:
            request_params["system"] = system_message
        
        if tools:
            request_params["tools"] = tools
        
        # Make request
        response = self.client.messages.create(**request_params)
        
        # Extract response
        content = ""
        tool_calls = []
        
        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": block.input,
                    }
                })
        
        return LLMResponse(
            content=content,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            finish_reason=response.stop_reason,
            tool_calls=tool_calls if tool_calls else None,
            metadata={"response_id": response.id},
        )
    
    def stream_chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        """Send a streaming chat completion request."""
        # Convert messages to Anthropic format
        anthropic_messages = []
        system_message = None
        
        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_message = msg.content
            elif msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                anthropic_messages.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })
        
        request_params = {
            "model": self.model,
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4096,
            "stream": True,
            **kwargs
        }
        
        if system_message:
            request_params["system"] = system_message
        
        if tools:
            request_params["tools"] = tools
        
        stream = self.client.messages.create(**request_params)
        
        for event in stream:
            if event.type == "content_block_delta":
                if hasattr(event.delta, "text") and event.delta.text:
                    yield LLMResponse(
                        content=event.delta.text,
                        model=event.model,
                    )
    
    def list_models(self) -> List[str]:
        """List available Anthropic models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-haiku-20241022",
        ]
    
    def supports_tools(self) -> bool:
        """Anthropic supports tool calling."""
        return True

