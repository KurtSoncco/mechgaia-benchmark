"""
Deepseek provider implementation.
"""

import os
import requests
from typing import Any, Dict, List, Optional
from .base import LLMProvider, LLMMessage, LLMResponse, MessageRole


class DeepseekProvider(LLMProvider):
    """Deepseek API provider."""
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        super().__init__(model, api_key, base_url, **kwargs)
        self.base_url = base_url or "https://api.deepseek.com"
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        
        if not self.api_key:
            raise ValueError("Deepseek API key is required. Set DEEPSEEK_API_KEY environment variable.")
    
    def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request to Deepseek."""
        # Convert messages to Deepseek format (OpenAI-compatible)
        deepseek_messages = []
        for msg in messages:
            message_dict = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.name:
                message_dict["name"] = msg.name
            deepseek_messages.append(message_dict)
        
        # Prepare request
        request_data = {
            "model": self.model,
            "messages": deepseek_messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            request_data["max_tokens"] = max_tokens
        
        if tools:
            request_data["tools"] = tools
        
        # Make request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json=request_data,
                headers=headers,
                timeout=kwargs.get("timeout", 300),
            )
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Deepseek API request failed: {e}")
        
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
        """Send a streaming chat completion request to Deepseek."""
        # Convert messages to Deepseek format
        deepseek_messages = []
        for msg in messages:
            message_dict = {
                "role": msg.role.value,
                "content": msg.content,
            }
            if msg.name:
                message_dict["name"] = msg.name
            deepseek_messages.append(message_dict)
        
        request_data = {
            "model": self.model,
            "messages": deepseek_messages,
            "temperature": temperature,
            "stream": True,
            **kwargs
        }
        
        if max_tokens:
            request_data["max_tokens"] = max_tokens
        
        if tools:
            request_data["tools"] = tools
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
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
            raise RuntimeError(f"Deepseek streaming request failed: {e}")
    
    def list_models(self) -> List[str]:
        """List available Deepseek models."""
        return [
            "deepseek-chat",
            "deepseek-coder",
            "deepseek-reasoner",
        ]
    
    def supports_tools(self) -> bool:
        """Deepseek supports tool calling."""
        return True

