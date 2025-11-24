# Quick Start Guide: Using LLM Providers, MCP, and A2A

This guide shows you how to quickly get started with the new LLM, MCP, and A2A features.

## Installation

First, install the required dependencies:

```bash
# Core dependencies (already in pyproject.toml)
uv sync

# Optional: Install LLM provider SDKs as needed
pip install openai          # For OpenAI
pip install anthropic       # For Claude/Anthropic
# Ollama: Run via Docker (see below)
# Deepseek: Uses requests (already installed)
```

## 1. Using LLM Providers

### Quick Example: OpenAI

```python
from llm_providers import get_llm_provider, LLMMessage, MessageRole

# Set your API key (or use environment variable)
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

# Create provider
provider = get_llm_provider(
    provider="openai",
    model="gpt-4"
)

# Send a message
messages = [
    LLMMessage(role=MessageRole.USER, content="What is 2+2?")
]

response = provider.chat(messages)
print(response.content)
```

### Quick Example: Ollama (Local Models)

```bash
# Start Ollama (if not running)
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Pull a model
ollama pull llama2
```

```python
from llm_providers import get_llm_provider, LLMMessage, MessageRole

# Use Ollama (no API key needed!)
provider = get_llm_provider(
    provider="ollama",
    model="llama2",
    base_url="http://localhost:11434"
)

messages = [LLMMessage(role=MessageRole.USER, content="Hello!")]
response = provider.chat(messages)
print(response.content)
```

### Quick Example: Claude/Anthropic

```python
import os
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

from llm_providers import get_llm_provider, LLMMessage, MessageRole

provider = get_llm_provider(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022"
)

messages = [LLMMessage(role=MessageRole.USER, content="Hello!")]
response = provider.chat(messages)
print(response.content)
```

## 2. Using MCP (Model Context Protocol)

### Step 1: Create an MCP Server with Tools

```python
from mcp import MCPServer, MCPTool
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# Create server
server = MCPServer(name="My Tools Server")

# Define a tool
def calculator(args):
    expression = args.get("expression", "")
    try:
        result = eval(expression)  # In production, use a safe evaluator!
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

# Register tool
calculator_tool = MCPTool(
    name="calculator",
    description="Evaluate mathematical expressions",
    input_schema={
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Math expression"}
        },
        "required": ["expression"]
    },
    handler=calculator
)
server.register_tool(calculator_tool)

# Create HTTP handler
class MCPHandler(BaseHTTPRequestHandler):
    def __init__(self, mcp_server, *args, **kwargs):
        self.mcp_server = mcp_server
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        if self.path == "/mcp":
            length = int(self.headers["Content-Length"])
            data = self.rfile.read(length)
            response = self.mcp_server.handle_json(data.decode())
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        pass

# Start server
def handler_factory(*args, **kwargs):
    return MCPHandler(server, *args, **kwargs)

httpd = HTTPServer(("localhost", 8000), handler_factory)
print("MCP Server running on http://localhost:8000")
httpd.serve_forever()
```

### Step 2: Use MCP Client

```python
from mcp import MCPClient

# Connect to server
client = MCPClient("http://localhost:8000")
client.initialize()

# List available tools
tools = client.list_tools()
print(f"Available tools: {[t['name'] for t in tools]}")

# Call a tool
result = client.call_tool("calculator", {"expression": "2 + 2 * 3"})
print(result)
```

### Step 3: Integrate MCP with LLM

```python
from llm_providers import get_llm_provider, LLMMessage, MessageRole
from mcp import MCPClient
import json

# Get tools from MCP server
client = MCPClient("http://localhost:8000")
client.initialize()
tools = client.list_tools()

# Convert to LLM function format
llm_tools = [{
    "type": "function",
    "function": {
        "name": tool["name"],
        "description": tool["description"],
        "parameters": tool["inputSchema"]
    }
} for tool in tools]

# Use LLM with tools
provider = get_llm_provider(provider="openai", model="gpt-4")
messages = [
    LLMMessage(role=MessageRole.USER, content="Calculate 15 * 23 + 7")
]

response = provider.chat(messages, tools=llm_tools)

# If LLM calls a tool, execute it
if response.tool_calls:
    for tool_call in response.tool_calls:
        tool_name = tool_call["function"]["name"]
        tool_args = json.loads(tool_call["function"]["arguments"])
        result = client.call_tool(tool_name, tool_args)
        print(f"Tool {tool_name} returned: {result}")
```

## 3. Using A2A (Agent-to-Agent Communication)

### Basic Agent Setup

```python
import asyncio
from a2a import A2AAgent, HTTPTransport, A2ARequest

# Create agent
agent = A2AAgent(
    agent_id="agent-1",
    agent_name="Calculator Agent",
    transport=HTTPTransport(base_url="http://localhost:8080", port=8080),
    capabilities=["calculations"]
)

# Register action handler
async def handle_calculate(request: A2ARequest):
    params = request.payload.get("parameters", {})
    expression = params.get("expression", "")
    try:
        result = eval(expression)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

agent.register_action_handler("calculate", handle_calculate)

# Start agent
async def main():
    await agent.start()
    print("Agent started. Listening on port 8080...")
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await agent.stop()

asyncio.run(main())
```

### Two Agents Communicating

**Agent 1 (Calculator):**
```python
import asyncio
from a2a import A2AAgent, HTTPTransport

agent1 = A2AAgent(
    agent_id="calculator",
    agent_name="Calculator",
    transport=HTTPTransport(port=8080),
    capabilities=["arithmetic"]
)

async def handle_calc(request):
    params = request.payload.get("parameters", {})
    a, b = params.get("a", 0), params.get("b", 0)
    op = params.get("operation", "add")
    return {"result": a + b if op == "add" else a * b}

agent1.register_action_handler("calculate", handle_calc)
await agent1.start()
print("Calculator agent ready")
```

**Agent 2 (Client):**
```python
import asyncio
from a2a import A2AAgent, HTTPTransport

agent2 = A2AAgent(
    agent_id="client",
    agent_name="Client Agent",
    transport=HTTPTransport(port=8081),
)

async def main():
    await agent2.start()
    
    # Send request to calculator
    response = await agent2.send_request(
        receiver_id="calculator",
        action="calculate",
        parameters={"a": 5, "b": 3, "operation": "add"}
    )
    
    print(f"Result: {response.payload}")
    await agent2.stop()

asyncio.run(main())
```

## 4. Integration with MechGAIA

### Enhance Green Agent with LLM

```python
from agents.green_agent_base import MechGAIABaseGreenAgent
from llm_providers import get_llm_provider, LLMMessage, MessageRole
from config import get_config

class LLMEnhancedGreenAgent(MechGAIABaseGreenAgent):
    def __init__(self, task_id):
        super().__init__(task_id)
        
        # Get LLM from config
        config = get_config()
        llm_config = config.get_llm_config()
        
        self.llm = get_llm_provider(
            provider=llm_config.get("provider", "openai"),
            model=llm_config.get("model", "gpt-4"),
            api_key=llm_config.get("api_key"),
        )
    
    def verify_submission(self, submission_data):
        # Use LLM to help verify
        prompt = f"""
        Verify this mechanical engineering submission:
        {submission_data}
        
        Check for:
        1. Numerical accuracy
        2. Unit consistency
        3. Physical feasibility
        """
        
        messages = [LLMMessage(role=MessageRole.USER, content=prompt)]
        response = self.llm.chat(messages)
        
        # Process LLM response and return score details
        # ... your verification logic ...
        
        return {
            "llm_verification": response.content,
            "numerical_accuracy": 1.0,  # Your scoring logic
        }
```

### Use Configuration File

Create `mechgaia_config.json`:

```json
{
  "llm": {
    "provider": "ollama",
    "model": "llama2",
    "base_url": "http://localhost:11434",
    "temperature": 0.7
  },
  "mcp": {
    "enabled": true,
    "server_url": "http://localhost:8000"
  },
  "a2a": {
    "enabled": true,
    "agent_id": "mechgaia-green-agent",
    "port": 8080
  }
}
```

Then use it:

```python
from config import get_config
from llm_providers import get_llm_provider

config = get_config()
llm_config = config.get_llm_config()

provider = get_llm_provider(
    provider=llm_config["provider"],
    model=llm_config["model"],
    base_url=llm_config.get("base_url"),
)
```

## 5. Environment Variables

Set these in your shell or `.env` file:

```bash
# LLM Configuration
export LLM_PROVIDER=ollama          # or openai, anthropic, deepseek
export LLM_MODEL=llama2            # Model name
export OPENAI_API_KEY=sk-...       # For OpenAI
export ANTHROPIC_API_KEY=sk-...    # For Anthropic
export OLLAMA_BASE_URL=http://localhost:11434

# MCP Configuration
export MCP_ENABLED=true
export MCP_SERVER_URL=http://localhost:8000

# A2A Configuration
export A2A_ENABLED=true
export A2A_AGENT_ID=my-agent
export A2A_PORT=8080
```

## 6. Running Examples

```bash
# LLM examples
python examples/llm_usage_example.py

# MCP examples
python examples/mcp_example.py

# A2A examples (requires async)
python examples/a2a_example.py
```

## Common Use Cases

### Use Case 1: Local Development with Ollama

```python
# No API keys needed!
provider = get_llm_provider("ollama", "llama2")
response = provider.chat([LLMMessage(role=MessageRole.USER, content="Hello")])
```

### Use Case 2: Production with OpenAI

```python
import os
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

provider = get_llm_provider("openai", "gpt-4")
# Use provider...
```

### Use Case 3: Multi-Agent System

```python
# Agent 1: Specialized calculator
# Agent 2: LLM-powered assistant
# Agent 3: Data processor
# They communicate via A2A protocol
```

## Troubleshooting

**Ollama not working?**
```bash
# Check if running
curl http://localhost:11434/api/tags

# Start if needed
docker start ollama
```

**Import errors?**
```bash
# Install missing packages
pip install openai anthropic aiohttp requests
```

**Port conflicts?**
- Change ports in configuration
- Use different ports for different agents

## Next Steps

1. Try the examples in `examples/` directory
2. Read `MCP_A2A_INTEGRATION.md` for detailed documentation
3. Integrate with your existing MechGAIA agents
4. Create custom MCP tools for your domain
5. Build multi-agent systems with A2A

