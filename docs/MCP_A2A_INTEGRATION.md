# MCP and A2A Integration Guide

This guide explains how to use the Model Context Protocol (MCP) and Agent-to-Agent (A2A) communication features in MechGAIA.

## Overview

MechGAIA now supports:
- **Multiple LLM Providers**: OpenAI, Anthropic (Claude), Ollama, Deepseek, and generic OpenAI-compatible APIs
- **MCP (Model Context Protocol)**: Standardized tool integration for LLMs
- **A2A (Agent-to-Agent)**: Direct communication between agents

## LLM Providers

### Supported Providers

1. **OpenAI** - GPT-4, GPT-3.5, GPT-4o, etc.
2. **Anthropic** - Claude 3.5 Sonnet, Claude 3 Opus, etc.
3. **Ollama** - Local open-source models (Llama, Mistral, etc.)
4. **Deepseek** - Deepseek Chat, Deepseek Coder
5. **Generic** - Any OpenAI-compatible API

### Basic Usage

```python
from llm_providers import get_llm_provider, LLMMessage, MessageRole

# Use OpenAI
provider = get_llm_provider(
    provider="openai",
    model="gpt-4",
    api_key="your-api-key"  # or set OPENAI_API_KEY env var
)

messages = [
    LLMMessage(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
    LLMMessage(role=MessageRole.USER, content="What is 2+2?"),
]

response = provider.chat(messages)
print(response.content)
```

### Using Ollama (Local Models)

```python
# Make sure Ollama is running: docker run -d -p 11434:11434 ollama/ollama
# Pull a model: ollama pull llama2

provider = get_llm_provider(
    provider="ollama",
    model="llama2",
    base_url="http://localhost:11434"
)

response = provider.chat(messages)
```

### Configuration

Use environment variables or configuration file:

```bash
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4
export OPENAI_API_KEY=your-key
```

Or use the configuration system:

```python
from config import get_config

config = get_config()
llm_config = config.get_llm_config()

provider = get_llm_provider(
    provider=llm_config["provider"],
    model=llm_config["model"],
    api_key=llm_config.get("api_key"),
)
```

## MCP (Model Context Protocol)

MCP provides a standardized way for LLMs to interact with external tools and resources.

### Setting Up an MCP Server

```python
from mcp import MCPServer, MCPTool

# Create server
server = MCPServer(name="My MCP Server")

# Define a tool
def calculator_handler(args: dict) -> dict:
    expression = args.get("expression", "")
    result = eval(expression)  # Use safe evaluator in production
    return {"result": result}

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
    handler=calculator_handler
)

server.register_tool(calculator_tool)
```

### Using MCP Client

```python
from mcp import MCPClient

client = MCPClient("http://localhost:8000")
client.initialize()

# List available tools
tools = client.list_tools()

# Call a tool
result = client.call_tool("calculator", {"expression": "2 + 2"})
print(result)
```

### Integrating MCP with LLMs

```python
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

# Use with LLM
provider = get_llm_provider(provider="openai", model="gpt-4")
response = provider.chat(messages, tools=llm_tools)

# Execute tool calls
if response.tool_calls:
    for tool_call in response.tool_calls:
        result = client.call_tool(
            tool_call["function"]["name"],
            json.loads(tool_call["function"]["arguments"])
        )
```

## A2A (Agent-to-Agent Communication)

A2A enables direct communication between agents for collaboration.

### Creating Agents

```python
from a2a import A2AAgent, HTTPTransport

# Create agent
agent = A2AAgent(
    agent_id="agent-1",
    agent_name="My Agent",
    transport=HTTPTransport(base_url="http://localhost:8080", port=8080),
    capabilities=["calculations", "analysis"]
)
```

### Registering Action Handlers

```python
async def handle_calculate(request: A2ARequest) -> dict:
    params = request.payload.get("parameters", {})
    expression = params.get("expression", "")
    result = eval(expression)
    return {"result": result}

agent.register_action_handler("calculate", handle_calculate)
```

### Agent Communication

```python
# Start agent
await agent.start()

# Send request to another agent
response = await agent.send_request(
    receiver_id="agent-2",
    action="calculate",
    parameters={"expression": "2 + 2"}
)

print(response.payload)

# Send notification
await agent.send_notification(
    receiver_id="agent-2",
    payload={"message": "Task completed"}
)

await agent.stop()
```

### LLM-Powered Agent

```python
from llm_providers import get_llm_provider, LLMMessage, MessageRole

# Create LLM agent
llm_agent = A2AAgent(
    agent_id="llm-agent",
    agent_name="LLM Assistant",
    transport=HTTPTransport(base_url="http://localhost:8081", port=8081)
)

provider = get_llm_provider(provider="openai", model="gpt-4")

async def handle_llm_request(request: A2ARequest) -> dict:
    params = request.payload.get("parameters", {})
    prompt = params.get("prompt", "")
    
    messages = [LLMMessage(role=MessageRole.USER, content=prompt)]
    response = provider.chat(messages)
    
    return {"response": response.content}

llm_agent.register_action_handler("process", handle_llm_request)
await llm_agent.start()
```

## Configuration

### Environment Variables

```bash
# LLM Configuration
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4
export OPENAI_API_KEY=your-key

# For Ollama
export OLLAMA_BASE_URL=http://localhost:11434

# MCP Configuration
export MCP_ENABLED=true
export MCP_SERVER_URL=http://localhost:8000

# A2A Configuration
export A2A_ENABLED=true
export A2A_AGENT_ID=mechgaia-agent
export A2A_PORT=8080
```

### Configuration File

Create `mechgaia_config.json`:

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 4096
  },
  "mcp": {
    "enabled": true,
    "server_url": "http://localhost:8000"
  },
  "a2a": {
    "enabled": true,
    "agent_id": "mechgaia-agent",
    "transport": "http",
    "port": 8080
  }
}
```

## Examples

See the `examples/` directory for complete examples:
- `llm_usage_example.py` - LLM provider usage
- `mcp_example.py` - MCP server and client
- `a2a_example.py` - Agent-to-agent communication

## Installation

Install optional dependencies as needed:

```bash
# For OpenAI
pip install openai

# For Anthropic
pip install anthropic

# For A2A (required)
pip install aiohttp

# All providers need requests
pip install requests
```

## Integration with MechGAIA

You can integrate LLM providers, MCP, and A2A with existing MechGAIA agents:

```python
from agents.green_agent_base import MechGAIABaseGreenAgent
from llm_providers import get_llm_provider
from mcp import MCPClient

class LLMEnhancedGreenAgent(MechGAIABaseGreenAgent):
    def __init__(self, task_id):
        super().__init__(task_id)
        self.llm = get_llm_provider(provider="openai", model="gpt-4")
        self.mcp_client = MCPClient("http://localhost:8000")
        self.mcp_client.initialize()
    
    def verify_submission(self, submission_data):
        # Use LLM to verify submission
        messages = [
            LLMMessage(
                role=MessageRole.USER,
                content=f"Verify this submission: {submission_data}"
            )
        ]
        response = self.llm.chat(messages)
        # Process response...
```

## Best Practices

1. **API Keys**: Store API keys in environment variables, not in code
2. **Error Handling**: Always wrap LLM calls in try-except blocks
3. **Rate Limiting**: Be mindful of API rate limits
4. **Tool Safety**: Validate and sanitize inputs to MCP tools
5. **Agent IDs**: Use unique, descriptive agent IDs for A2A
6. **Transport**: Choose appropriate transport (HTTP for simple, WebSocket for real-time)

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `docker ps | grep ollama`
- Check port: `curl http://localhost:11434/api/tags`

### MCP Server Not Responding
- Verify server is running and accessible
- Check CORS settings if accessing from browser

### A2A Communication Fails
- Ensure agents are started before sending requests
- Check network connectivity and ports
- Verify agent IDs match

## Next Steps

- Explore the example files in `examples/`
- Integrate LLM providers with your agents
- Set up MCP tools for domain-specific tasks
- Create multi-agent systems with A2A

