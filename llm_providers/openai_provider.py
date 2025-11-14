"""
OpenAI provider implementation.
"""

import os
from typing import Any, Dict, List, Optional
from .base import LLMProvider, LLMMessage, LLMResponse, MessageRole

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI package not installed. Install with: pip install openai"
            )
        
        super().__init__(model, api_key, base_url, **kwargs)
        
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
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
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            message_dict = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.name:
                message_dict["name"] = msg.name
            if msg.tool_calls:
                message_dict["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id
            openai_messages.append(message_dict)
        
        # Prepare request
        request_params = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            request_params["max_tokens"] = max_tokens
        
        if tools:
            request_params["tools"] = tools
        
        # Make request
        response = self.client.chat.completions.create(**request_params)
        
        # Extract response
        choice = response.choices[0]
        content = choice.message.content or ""
        
        return LLMResponse(
            content=content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            } if response.usage else None,
            finish_reason=choice.finish_reason,
            tool_calls=[
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in (choice.message.tool_calls or [])
            ],
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
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            message_dict = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.name:
                message_dict["name"] = msg.name
            openai_messages.append(message_dict)
        
        request_params = {
            "model": self.model,
            "messages": openai_messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        
        if max_tokens:
            request_params["max_tokens"] = max_tokens
        
        if tools:
            request_params["tools"] = tools
        
        stream = self.client.chat.completions.create(**request_params)
        
        for chunk in stream:
            if chunk.choices:
                choice = chunk.choices[0]
                delta = choice.delta
                if delta.content:
                    yield LLMResponse(
                        content=delta.content,
                        model=chunk.model,
                        metadata={"chunk_id": chunk.id},
                    )
    
    def list_models(self) -> List[str]:
        """List available OpenAI models."""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data if "gpt" in model.id.lower()]
        except Exception:
            # Return common models if API call fails
            return [
                "gpt-4",
                "gpt-4-turbo",
                "gpt-4o",
                "gpt-3.5-turbo",
                "gpt-4o-mini",
            ]
    
    def supports_tools(self) -> bool:
        """OpenAI supports tool calling."""
        return True

