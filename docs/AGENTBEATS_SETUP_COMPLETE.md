# ✅ AgentBeats Setup Complete!

Your MechGAIA green agent is now configured for AgentBeats submission using `uv` and `pyproject.toml`.

## ✅ What Was Updated

1. **pyproject.toml**:
   - ✅ Python version requirement: `>=3.11`
   - ✅ All dependencies use `uv sync` (no more `pip install`)
   - ✅ AgentBeats SDK included
   - ✅ Earthshaker noted as optional (requires Python 3.13+)

2. **agent_card.toml**:
   - ✅ Added `url` and `entrypoint` fields
   - ✅ Added `[agent.deployment]` section with URLs
   - ✅ Updated Python version to `>=3.11`

3. **Documentation**:
   - ✅ Created `AGENTBEATS_SUBMISSION_CHECKLIST.md` - Complete checklist
   - ✅ Created `SUBMISSION_QUICKSTART.md` - Quick reference
   - ✅ Created `scripts/setup_agentbeats.sh` - Automated setup script

## ✅ Verified Working

```bash
# Dependencies install correctly
uv sync  # ✅ Works!

# Agent info command works
uv run python agentbeats_main.py info  # ✅ Works!
```

## 📝 Next Steps (Before Submission)

### 1. Update URLs in agent_card.toml

Edit `agent_card.toml` and update:
```toml
[agent]
url = "http://YOUR_DEPLOYMENT_URL:8080"  # Update this!

[agent.deployment]
agent_url = "http://YOUR_DEPLOYMENT_URL:8080"  # Update this!
launcher_url = "http://YOUR_DEPLOYMENT_URL:8081"  # Update this!
```

### 2. Test Locally

```bash
# Activate venv
source .venv/bin/activate

# Test agent
uv run python agentbeats_main.py info
uv run python agentbeats_main.py evaluate examples/submissions/example_level1.json 1
```

### 3. Deploy Your Agent

**Option A: Docker**
```bash
docker build -f Dockerfile.uv -t mechgaia-green-agent .
docker run -p 8080:8080 mechgaia-green-agent
```

**Option B: Railway/Render**
- Push to GitHub
- Connect to Railway/Render
- Set environment variables
- Deploy

### 4. Register on AgentBeats

When agentbeats.org is available:
1. Log in
2. Register your agent with:
   - Agent URL: Your deployment URL
   - Launcher URL: Your launcher URL (if using)
   - Upload `agent_card.toml`

## 📚 Documentation Files

- **AGENTBEATS_SUBMISSION_CHECKLIST.md** - Complete step-by-step checklist
- **SUBMISSION_QUICKSTART.md** - Quick reference guide
- **QUICKSTART.md** - LLM/MCP/A2A usage guide
- **MCP_A2A_INTEGRATION.md** - Detailed MCP/A2A documentation

## 🔧 Important Notes

1. **Always use `uv sync`** - Never use `pip install` directly
2. **Python ≥3.11** required
3. **Update URLs** in agent_card.toml before submission
4. **Earthshaker** is optional (requires Python 3.13+)
5. **Test locally** before deploying

## 🤖 Simple White Agent

The repository includes a simple white agent implementation (`white_agents/simple_white_agent.py`) that can be used for testing. This agent implements the A2A protocol and uses litellm for LLM interactions.

### Environment Variables

The white agent can be configured using the following environment variables:

**LLM Configuration:**
- `LLM_MODEL`: Model to use (default: `ollama/llama3`)
  - For Ollama: `ollama/llama3`, `ollama/mistral`, etc.
  - For OpenAI: `openai/gpt-4o`, `gpt-4o`, etc.
- `LLM_PROVIDER`: Provider name (default: `ollama`)
  - Options: `ollama`, `openai`, etc.
- `LLM_TEMPERATURE`: Temperature for LLM (default: `0.0`)
- `OPENAI_API_KEY`: OpenAI API key (required if using OpenAI)
- `OLLAMA_BASE_URL`: Base URL for Ollama (default: `http://localhost:11434`)

**White Agent Server Configuration:**
- `WHITE_AGENT_HOST`: Host to bind to (default: `localhost`)
- `WHITE_AGENT_PORT`: Port to bind to (default: `9002`)

### Using Ollama (No API Key Required)

```bash
# Set environment variables (or use .env file)
export LLM_MODEL="ollama/llama3"
export LLM_PROVIDER="ollama"
export OLLAMA_BASE_URL="http://localhost:11434"

# Start the white agent
python -m white_agents.simple_white_agent
```

Make sure Ollama is running locally:
```bash
# Install Ollama from https://ollama.ai
# Pull a model
ollama pull llama3
```

### Using OpenAI

```bash
# Set environment variables (or use .env file)
export LLM_MODEL="openai/gpt-4o"
export LLM_PROVIDER="openai"
export OPENAI_API_KEY="your-api-key-here"

# Start the white agent
python -m white_agents.simple_white_agent
```

### Starting the White Agent

**Option 1: Direct execution**
```bash
python -m white_agents.simple_white_agent
```

**Option 2: Using the integration function**
```python
from run_benchmark import start_simple_white_agent

# Start in background thread
thread = start_simple_white_agent(background=True)

# Or start blocking
start_simple_white_agent(background=False)
```

**Option 3: Using configuration**
```python
from config.white_agent_config import get_white_agent_config
from white_agents.simple_white_agent import start_white_agent

config = get_white_agent_config()
start_white_agent(
    host=config.get("agent.host"),
    port=config.get("agent.port")
)
```

### Testing the White Agent

Once the white agent is running, you can test it using the green agent's A2A communication:

```python
from agentbeats.utils.agents.a2a import send_message_to_agent
import asyncio

async def test_white_agent():
    response = await send_message_to_agent(
        "http://localhost:9002",
        "Hello, can you help me solve a problem?",
        timeout=60.0
    )
    print(response)

asyncio.run(test_white_agent())
```

Or use the smoke tests:
```bash
uv run pytest tests/test_simple_white_agent.py -v
```

## 🚀 Quick Commands

```bash
# Setup
source .venv/bin/activate
uv sync

# Test green agent
uv run python agentbeats_main.py info
uv run python agentbeats_main.py evaluate examples/submissions/example_level1.json 1

# Start white agent (for testing)
# Using Ollama (default, no API key needed)
python -m white_agents.simple_white_agent

# Using OpenAI (requires OPENAI_API_KEY)
export OPENAI_API_KEY="your-key"
export LLM_MODEL="openai/gpt-4o"
export LLM_PROVIDER="openai"
python -m white_agents.simple_white_agent

# Deploy
docker build -f Dockerfile.uv -t mechgaia-green-agent .
docker run -p 8080:8080 mechgaia-green-agent
```

## ✅ Ready for Submission!

Your agent is configured and ready. Just:
1. Update URLs in agent_card.toml
2. Deploy your agent
3. Register on agentbeats.org
4. Submit!

Good luck! 🎉

