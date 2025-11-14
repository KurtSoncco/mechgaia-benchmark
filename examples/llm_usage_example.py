"""
Example usage of LLM providers with MechGAIA.

This example demonstrates how to use different LLM providers
(OpenAI, Anthropic, Ollama, Deepseek) with the MechGAIA system.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from llm_providers import get_llm_provider, LLMMessage, MessageRole
from config import get_config


def example_openai():
    """Example using OpenAI provider."""
    print("=== OpenAI Example ===")
    
    # Set your API key
    # os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    
    try:
        provider = get_llm_provider(
            provider="openai",
            model="gpt-4",
        )
        
        messages = [
            LLMMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
            LLMMessage(role=MessageRole.USER, content="What is 2+2?"),
        ]
        
        response = provider.chat(messages)
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
        print(f"Usage: {response.usage}")
    except Exception as e:
        print(f"Error: {e}")


def example_anthropic():
    """Example using Anthropic (Claude) provider."""
    print("\n=== Anthropic/Claude Example ===")
    
    # Set your API key
    # os.environ["ANTHROPIC_API_KEY"] = "your-api-key-here"
    
    try:
        provider = get_llm_provider(
            provider="anthropic",
            model="claude-3-5-sonnet-20241022",
        )
        
        messages = [
            LLMMessage(role=MessageRole.USER, content="What is 2+2?"),
        ]
        
        response = provider.chat(messages)
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
    except Exception as e:
        print(f"Error: {e}")


def example_ollama():
    """Example using Ollama provider (local models)."""
    print("\n=== Ollama Example ===")
    
    # Make sure Ollama is running locally
    # docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
    # ollama pull llama2
    
    try:
        provider = get_llm_provider(
            provider="ollama",
            model="llama2",
            base_url="http://localhost:11434",
        )
        
        messages = [
            LLMMessage(role=MessageRole.USER, content="What is 2+2?"),
        ]
        
        response = provider.chat(messages)
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
    except Exception as e:
        print(f"Error: {e}")


def example_deepseek():
    """Example using Deepseek provider."""
    print("\n=== Deepseek Example ===")
    
    # Set your API key
    # os.environ["DEEPSEEK_API_KEY"] = "your-api-key-here"
    
    try:
        provider = get_llm_provider(
            provider="deepseek",
            model="deepseek-chat",
        )
        
        messages = [
            LLMMessage(role=MessageRole.USER, content="What is 2+2?"),
        ]
        
        response = provider.chat(messages)
        print(f"Response: {response.content}")
        print(f"Model: {response.model}")
    except Exception as e:
        print(f"Error: {e}")


def example_with_config():
    """Example using configuration system."""
    print("\n=== Configuration Example ===")
    
    config = get_config()
    llm_config = config.get_llm_config()
    
    print(f"Provider: {llm_config.get('provider')}")
    print(f"Model: {llm_config.get('model')}")
    
    try:
        provider = get_llm_provider(
            provider=llm_config.get("provider", "openai"),
            model=llm_config.get("model", "gpt-4"),
            api_key=llm_config.get("api_key"),
            base_url=llm_config.get("base_url"),
        )
        
        messages = [
            LLMMessage(role=MessageRole.USER, content="Hello!"),
        ]
        
        response = provider.chat(messages)
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("LLM Provider Usage Examples\n")
    print("Note: Make sure to set appropriate API keys or have Ollama running locally.\n")
    
    # Uncomment the example you want to run:
    # example_openai()
    # example_anthropic()
    # example_ollama()
    # example_deepseek()
    # example_with_config()
    
    print("\nTo run examples, uncomment the desired function call above.")

