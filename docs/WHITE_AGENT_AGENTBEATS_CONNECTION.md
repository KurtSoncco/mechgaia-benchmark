# Connecting White Agent to AgentBeats

This guide explains how to connect your white agent to the AgentBeats platform for evaluation and battles.

## Overview

The white agent implements the A2A (Agent-to-Agent) protocol, which is the standard communication method used by AgentBeats. The connection process involves:

1. **Local Testing**: Test the connection locally between green and white agents
2. **Deployment**: Make your white agent publicly accessible
3. **Registration**: Register your agent on agentbeats.org
4. **Evaluation**: Participate in battles and evaluations

## 🔧 Local Testing

### Step 1: Start the White Agent

```bash
# Using Ollama (default, no API key needed)
python -m white_agents.simple_white_agent

# Or using OpenAI
export OPENAI_API_KEY="your-key"
export LLM_MODEL="openai/gpt-4o"
export LLM_PROVIDER="openai"
python -m white_agents.simple_white_agent
```

The white agent will start on `http://localhost:9002` by default.

### Step 2: Test A2A Communication

You can test the connection using the green agent's A2A utilities:

```python
import asyncio
from agentbeats.utils.agents.a2a import send_message_to_agent

async def test_connection():
    """Test connection to white agent."""
    white_agent_url = "http://localhost:9002"
    message = "Hello, can you help me solve a problem?"
    
    try:
        response = await send_message_to_agent(
            white_agent_url,
            message,
            timeout=60.0
        )
        print(f"Response from white agent: {response}")
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

# Run the test
asyncio.run(test_connection())
```

### Step 3: Test with Green Agent

The green agent can automatically discover and communicate with white agents:

```python
from agentbeats_main import MechGAIAGreenAgent

# The green agent will use A2A to communicate with white agents
# when performing active assessments
green_agent = MechGAIAGreenAgent()

# When evaluating, if a white agent URL is provided, it will use A2A
# to send the problem and receive the submission
```

## 🌐 Deployment Options

For AgentBeats registration, your white agent must be publicly accessible. Here are deployment options:

### Option 1: Cloudflare Tunnel (Recommended for Development)

Cloudflare Tunnel allows you to expose your local server without a public IP:

```bash
# Install cloudflared
# macOS: brew install cloudflared
# Linux: Download from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/

# Create a tunnel
cloudflared tunnel --url http://localhost:9002

# This will give you a public URL like: https://random-name.trycloudflare.com
```

### Option 2: Render (Free Tier Available)

1. **Create a Render account** at https://render.com
2. **Create a new Web Service**
3. **Connect your GitHub repository**
4. **Configure the service**:
   - Build Command: `uv sync`
   - Start Command: `python -m white_agents.simple_white_agent`
   - Environment Variables:
     ```
     WHITE_AGENT_HOST=0.0.0.0
     WHITE_AGENT_PORT=$PORT
     LLM_MODEL=ollama/llama3
     LLM_PROVIDER=ollama
     OLLAMA_BASE_URL=http://your-ollama-instance:11434
     # OR for OpenAI:
     # LLM_MODEL=openai/gpt-4o
     # LLM_PROVIDER=openai
     # OPENAI_API_KEY=your-key
     ```
5. **Deploy** and get your public URL

### Option 3: Railway

1. **Create a Railway account** at https://railway.app
2. **Create a new project** and connect your GitHub repo
3. **Add environment variables** (same as Render)
4. **Deploy** and get your public URL

### Option 4: Docker + Cloud Provider

Deploy using Docker on any cloud provider (AWS, GCP, Azure, DigitalOcean):

```dockerfile
# Dockerfile for white agent
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY white_agents/ ./white_agents/
COPY config/ ./config/

# Install dependencies
RUN uv sync

# Expose port
EXPOSE 9002

# Start white agent
CMD ["python", "-m", "white_agents.simple_white_agent"]
```

## 📝 Registration on AgentBeats

### Step 1: Prepare Your Agent Card

Update `white_agent_card.toml` with your deployment URL:

```toml
[agent]
url = "https://your-deployment-url.com"  # Update this!

[agent.server]
host = "0.0.0.0"  # For production
port = 9002
```

### Step 2: Register on agentbeats.org

1. **Log in** to https://agentbeats.org
2. **Navigate to "Register Agent"** or "My Agents"
3. **Fill in the registration form**:
   - **Agent Name**: `file_agent` (or your custom name)
   - **Agent URL**: `https://your-deployment-url.com` (your public URL)
   - **Agent Card**: Upload `white_agent_card.toml`
   - **Description**: Brief description of your agent
4. **Submit** and wait for verification

### Step 3: Verify Registration

After registration:
- Your agent should appear in the dashboard
- AgentBeats will verify the agent is accessible
- You'll receive a confirmation email

## 🧪 Testing the Connection

### Test 1: Health Check

Your white agent should respond to health checks:

```bash
curl https://your-deployment-url.com/health
```

### Test 2: A2A Protocol Test

Test using AgentBeats SDK:

```python
import asyncio
from agentbeats.utils.agents.a2a import send_message_to_agent

async def test_production_agent():
    url = "https://your-deployment-url.com"
    response = await send_message_to_agent(
        url,
        "Test message",
        timeout=60.0
    )
    print(f"Response: {response}")

asyncio.run(test_production_agent())
```

### Test 3: Green Agent Integration

The green agent can test your white agent:

```python
from agentbeats_main import MechGAIAGreenAgent

green_agent = MechGAIAGreenAgent()

# The green agent will use A2A to communicate with your white agent
# when performing evaluations
```

## 🔐 Security Considerations

1. **API Keys**: Never commit API keys to version control
   - Use environment variables
   - Use `.env` files (and add to `.gitignore`)
   - Use secrets management in your deployment platform

2. **Rate Limiting**: Consider implementing rate limiting for production

3. **Authentication**: For production, consider adding authentication

4. **HTTPS**: Always use HTTPS in production (most platforms provide this automatically)

## 📊 Monitoring

Monitor your white agent:

1. **Logs**: Check application logs for errors
2. **Health Endpoint**: Set up monitoring on `/health`
3. **Metrics**: Track response times and success rates

## 🐛 Troubleshooting

### Connection Refused

**Problem**: `Connection refused` when trying to connect

**Solutions**:
- Verify the white agent is running: `curl http://localhost:9002/health`
- Check firewall settings
- Verify the URL is correct
- For production, ensure the service is publicly accessible

### Timeout Errors

**Problem**: Requests timeout

**Solutions**:
- Increase timeout in `send_message_to_agent(timeout=120.0)`
- Check if LLM provider is responding
- Verify network connectivity

### LLM Provider Issues

**Problem**: LLM not responding

**Solutions**:
- For Ollama: Ensure Ollama is running and model is pulled
- For OpenAI: Verify API key is correct and has credits
- Check provider status/health

### AgentBeats Registration Fails

**Problem**: Registration verification fails

**Solutions**:
- Ensure agent is publicly accessible
- Verify health endpoint responds
- Check agent card format is correct
- Ensure A2A protocol is properly implemented

## 📚 Additional Resources

- **AgentBeats Documentation**: https://agentbeats.org/docs
- **A2A Protocol Guide**: See `docs/MCP_A2A_INTEGRATION.md`
- **AgentBeats SDK**: https://github.com/agentbeats/agentbeats

## ✅ Checklist

Before registering on AgentBeats:

- [ ] White agent runs locally and responds to A2A messages
- [ ] White agent is deployed and publicly accessible
- [ ] Health endpoint responds: `curl https://your-url/health`
- [ ] A2A communication test passes
- [ ] `white_agent_card.toml` is updated with production URL
- [ ] Environment variables are configured correctly
- [ ] LLM provider is working (Ollama or OpenAI)
- [ ] Agent is ready for evaluation

## 🚀 Quick Start Summary

```bash
# 1. Test locally
python -m white_agents.simple_white_agent

# 2. Deploy (example with Render)
# - Push to GitHub
# - Connect to Render
# - Set environment variables
# - Deploy

# 3. Update agent card
# Edit white_agent_card.toml with your URL

# 4. Register on agentbeats.org
# - Log in
# - Register agent
# - Upload agent card
# - Verify

# 5. Test connection
python test_connection.py  # Use the test script above
```

Good luck with your AgentBeats connection! 🎉


