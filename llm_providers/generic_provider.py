"""
Generic provider for OpenAI-compatible APIs.
"""

import os
import requests
from typing import Any, Dict, List, Optional
from .base import LLMProvider, LLMMessage, LLMResponse, MessageRole


class GenericProvider(LLMProvider):
    """
    Generic provider for OpenAI-compatible APIs.
    Works with any API that follows OpenAI's chat completion format.
    """
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        super().__init__(model, api_key, base_url, **kwargs)
        
        if not base_url:
            raise ValueError("base_url is required for GenericProvider")
        
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.getenv("GENERIC_API_KEY")
    
    def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request to a generic OpenAI-compatible API."""
        # Convert messages to OpenAI format
        api_messages = []
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
            api_messages.append(message_dict)
        
        # Prepare request
        request_data = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            request_data["max_tokens"] = max_tokens
        
        if tools:
            request_data["tools"] = tools
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Make request
        try:
            endpoint = f"{self.base_url}/v1/chat/completions"
            response = requests.post(
                endpoint,
                json=request_data,
                headers=headers,
                timeout=kwargs.get("timeout", 300),
            )
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Generic API request failed: {e}")
        
        # Extract response
        choice = result["choices"][0]
        content = choice["message"].get("content", "")
        
        return LLMResponse(
            content=content,
            model=result.get("model", self.model),
            usage=result.get("usage"),
            finish_reason=choice.get("finish_reason"),
            tool_calls=choice["message"].get("tool_calls"),
            metadata={"response_id": result.get("id")},
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
        api_messages = []
        for msg in messages:
            message_dict = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.name:
                message_dict["name"] = msg.name
            api_messages.append(message_dict)
        
        request_data = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        
        if max_tokens:
            request_data["max_tokens"] = max_tokens
        
        if tools:
            request_data["tools"] = tools
        
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            endpoint = f"{self.base_url}/v1/chat/completions"
            response = requests.post(
                endpoint,
                json=request_data,
                headers=headers,
                stream=True,
                timeout=kwargs.get("timeout", 300),
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            import json
                            chunk = json.loads(data_str)
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield LLMResponse(
                                        content=content,
                                        model=chunk.get("model", self.model),
                                    )
                        except json.JSONDecodeError:
                            continue
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Generic streaming request failed: {e}")
    
    def list_models(self) -> List[str]:
        """List available models (if API supports it)."""
        try:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
            return [model["id"] for model in result.get("data", [])]
        except Exception:
            return [self.model]
    
    def supports_tools(self) -> bool:
        """Generic provider may support tools depending on the API."""
        return True

