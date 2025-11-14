"""
Simple usage examples - copy and run these!

This file contains minimal, runnable examples you can use immediately.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ============================================================================
# Example 1: Use Ollama (No API Key Needed!)
# ============================================================================

def example_ollama_simple():
    """Simplest example - use Ollama locally."""
    from llm_providers import get_llm_provider, LLMMessage, MessageRole
    
    # Make sure Ollama is running: docker run -d -p 11434:11434 ollama/ollama
    # Then: ollama pull llama2
    
    try:
        provider = get_llm_provider(
            provider="ollama",
            model="llama2",
            base_url="http://localhost:11434"
        )
        
        response = provider.chat([
            LLMMessage(role=MessageRole.USER, content="What is 2+2?")
        ])
        
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure Ollama is running: docker start ollama")


# ============================================================================
# Example 2: Use OpenAI (Requires API Key)
# ============================================================================

def example_openai_simple():
    """Simple OpenAI example."""
    import os
    from llm_providers import get_llm_provider, LLMMessage, MessageRole
    
    # Set your API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY environment variable first!")
        return
    
    try:
        provider = get_llm_provider(
            provider="openai",
            model="gpt-4"
        )
        
        response = provider.chat([
            LLMMessage(role=MessageRole.USER, content="Say hello in one sentence")
        ])
        
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")


# ============================================================================
# Example 3: Simple MCP Tool
# ============================================================================

def example_mcp_simple():
    """Simple MCP server example."""
    from mcp import MCPServer, MCPTool
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import json
    
    # Create server
    server = MCPServer()
    
    # Add a simple tool
    def add_numbers(args):
        a = args.get("a", 0)
        b = args.get("b", 0)
        return {"result": a + b}
    
    tool = MCPTool(
        name="add",
        description="Add two numbers",
        input_schema={
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        },
        handler=add_numbers
    )
    server.register_tool(tool)
    
    # HTTP handler
    class Handler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.server = server
            super().__init__(*args, **kwargs)
        
        def do_POST(self):
            if self.path == "/mcp":
                length = int(self.headers["Content-Length"])
                data = self.rfile.read(length)
                response = self.server.handle_json(data.decode())
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(response.encode())
        
        def log_message(self, *args):
            pass
    
    # Start server
    httpd = HTTPServer(("localhost", 8000), Handler)
    print("MCP Server running on http://localhost:8000")
    print("Test with: curl -X POST http://localhost:8000/mcp -d '{\"method\":\"tools/list\"}'")
    httpd.serve_forever()


# ============================================================================
# Example 4: Use MCP Client
# ============================================================================

def example_mcp_client_simple():
    """Simple MCP client example."""
    from mcp import MCPClient
    
    try:
        client = MCPClient("http://localhost:8000")
        client.initialize()
        
        tools = client.list_tools()
        print(f"Available tools: {[t['name'] for t in tools]}")
        
        # Call a tool
        result = client.call_tool("add", {"a": 5, "b": 3})
        print(f"5 + 3 = {result}")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure MCP server is running (see example_mcp_simple)")


# ============================================================================
# Example 5: Simple A2A Agent
# ============================================================================

async def example_a2a_simple():
    """Simple A2A agent example."""
    import asyncio
    from a2a import A2AAgent, HTTPTransport, A2ARequest
    
    # Create agent
    agent = A2AAgent(
        agent_id="simple-agent",
        agent_name="Simple Agent",
        transport=HTTPTransport(port=8080)
    )
    
    # Add handler
    async def handle_hello(request: A2ARequest):
        name = request.payload.get("parameters", {}).get("name", "World")
        return {"message": f"Hello, {name}!"}
    
    agent.register_action_handler("hello", handle_hello)
    
    # Start
    await agent.start()
    print("Agent started on port 8080")
    print("Send requests to: http://localhost:8080/a2a/request")
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await agent.stop()


# ============================================================================
# Example 6: LLM with Configuration
# ============================================================================

def example_with_config():
    """Use configuration system."""
    from config import get_config
    from llm_providers import get_llm_provider, LLMMessage, MessageRole
    
    # Load config
    config = get_config()
    llm_config = config.get_llm_config()
    
    print(f"Using provider: {llm_config.get('provider')}")
    print(f"Using model: {llm_config.get('model')}")
    
    try:
        provider = get_llm_provider(
            provider=llm_config.get("provider", "openai"),
            model=llm_config.get("model", "gpt-4"),
            api_key=llm_config.get("api_key"),
            base_url=llm_config.get("base_url"),
        )
        
        response = provider.chat([
            LLMMessage(role=MessageRole.USER, content="Hello!")
        ])
        
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error: {e}")


# ============================================================================
# Main - Run Examples
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Simple Usage Examples")
    print("=" * 60)
    print()
    print("Available examples:")
    print("  1. example_ollama_simple()      - Use Ollama (no API key)")
    print("  2. example_openai_simple()       - Use OpenAI (needs API key)")
    print("  3. example_mcp_simple()          - Start MCP server")
    print("  4. example_mcp_client_simple()   - Use MCP client")
    print("  5. example_a2a_simple()          - Start A2A agent (async)")
    print("  6. example_with_config()          - Use configuration")
    print()
    print("To run an example, uncomment it below or call it directly.")
    print()
    
    # Try to run the simplest example (Ollama) if available
    print("Attempting to run Ollama example (no API key needed)...")
    print("-" * 60)
    example_ollama_simple()
    
    print("\n" + "=" * 60)
    print("To run other examples, edit this file and uncomment them:")
    print("  - example_openai_simple()       # Needs OPENAI_API_KEY")
    print("  - example_mcp_simple()         # Starts MCP server")
    print("  - example_mcp_client_simple()  # Uses MCP client")
    print("  - example_with_config()         # Uses config system")
    print("=" * 60)

