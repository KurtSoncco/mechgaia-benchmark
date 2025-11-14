"""
Ollama provider implementation for local/open-source models.
"""

import json
import requests
from typing import Any, Dict, List, Optional
from .base import LLMProvider, LLMMessage, LLMResponse, MessageRole


class OllamaProvider(LLMProvider):
    """Ollama provider for local LLM models."""
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs
    ):
        super().__init__(model, api_key, base_url, **kwargs)
        self.base_url = base_url or "http://localhost:11434"
    
    def chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request to Ollama."""
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg.role.value,
                "content": msg.content,
            })
        
        # Prepare request
        request_data = {
            "model": self.model,
            "messages": ollama_messages,
            "options": {
                "temperature": temperature,
                **kwargs.get("options", {}),
            },
            **{k: v for k, v in kwargs.items() if k != "options"},
        }
        
        if max_tokens:
            request_data["options"]["num_predict"] = max_tokens
        
        # Make request
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=request_data,
                timeout=kwargs.get("timeout", 300),
            )
            response.raise_for_status()
            # Handle both single JSON response and streaming response
            try:
                result = response.json()
            except json.JSONDecodeError:
                # If response is not valid JSON, try to parse as streaming
                # For non-streaming requests, this shouldn't happen, but handle it
                text = response.text.strip()
                if text:
                    # Try to parse first line as JSON
                    lines = text.split('\n')
                    for line in lines:
                        if line.strip():
                            try:
                                result = json.loads(line)
                                break
                            except json.JSONDecodeError:
                                continue
                    else:
                        raise RuntimeError(f"Could not parse Ollama response: {text[:200]}")
                else:
                    raise RuntimeError("Empty response from Ollama")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama API request failed: {e}")
        
        # Extract response
        content = result.get("message", {}).get("content", "")
        
        return LLMResponse(
            content=content,
            model=result.get("model", self.model),
            usage={
                "prompt_tokens": result.get("prompt_eval_count", 0),
                "completion_tokens": result.get("eval_count", 0),
                "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0),
            },
            finish_reason=result.get("done_reason"),
            metadata={"done": result.get("done", True)},
        )
    
    def stream_chat(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        """Send a streaming chat completion request to Ollama."""
        # Convert messages to Ollama format
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg.role.value,
                "content": msg.content,
            })
        
        request_data = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                **kwargs.get("options", {}),
            },
            **{k: v for k, v in kwargs.items() if k != "options"},
        }
        
        if max_tokens:
            request_data["options"]["num_predict"] = max_tokens
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=request_data,
                stream=True,
                timeout=kwargs.get("timeout", 300),
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            content = chunk["message"]["content"]
                            if content:
                                yield LLMResponse(
                                    content=content,
                                    model=chunk.get("model", self.model),
                                    metadata={"done": chunk.get("done", False)},
                                )
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ollama streaming request failed: {e}")
    
    def list_models(self) -> List[str]:
        """List available Ollama models."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
            return [model["name"] for model in result.get("models", [])]
        except Exception:
            # Return common models if API call fails
            return [
                "llama2",
                "llama3",
                "mistral",
                "mixtral",
                "codellama",
                "phi",
                "neural-chat",
            ]
    
    def supports_tools(self) -> bool:
        """Ollama may support tools depending on model."""
        # Some newer models support tools, but it's model-dependent
        return False

