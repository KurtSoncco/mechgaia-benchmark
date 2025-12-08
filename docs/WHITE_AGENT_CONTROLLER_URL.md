# White Agent Controller URL Setup

When submitting your white agent to AgentBeats, you may need to provide a **Controller URL** (also called Launcher URL). This guide explains what it is and how to set it up.

## What is the Controller URL?

The **Controller URL** (or Launcher URL) is an optional service that AgentBeats uses to:
- Launch and manage agent instances
- Handle agent lifecycle (start, stop, restart)
- Provide a standardized interface for agent communication

For **white agents**, the Controller URL is typically **optional** - you can usually just provide the agent URL directly. However, if AgentBeats requires it, here's how to set it up.

## Option 1: Use Agent URL as Controller URL (Simplest)

If AgentBeats allows it, you can use your white agent URL as both the Agent URL and Controller URL:

```
Agent URL: https://your-white-agent.com
Controller URL: https://your-white-agent.com
```

This works because the white agent A2A server can handle both agent requests and controller requests.

## Option 2: Set Up a Separate Launcher Service

If AgentBeats requires a separate controller/launcher service, you can:

### Using the AgentBeats Launcher Image

Deploy the official AgentBeats launcher service:

```yaml
# docker-compose.yml
services:
  white-agent:
    # Your white agent service
    ports:
      - "9002:9002"
  
  launcher:
    image: agentbeats/launcher:latest
    container_name: white-agent-launcher
    ports:
      - "8081:8081"
    environment:
      - AGENT_URL=http://white-agent:9002
      - LAUNCHER_PORT=8081
    depends_on:
      - white-agent
```

Then your URLs would be:
```
Agent URL: https://your-white-agent.com
Controller URL: https://your-launcher.com
```

### Using Your Own Launcher

You can also use the `launcher.py` from this repository:

```bash
# Start launcher pointing to your white agent
export AGENT_URL=http://localhost:9002
export LAUNCHER_PORT=8081
python launcher.py
```

## Option 3: White Agent Only (No Controller)

For white agents, you typically **don't need a separate controller**. The white agent A2A server is sufficient. When registering on AgentBeats:

1. **Agent URL**: Your white agent's public URL (e.g., `https://your-white-agent.com`)
2. **Controller URL**: 
   - Leave blank if possible
   - Or use the same URL as Agent URL
   - Or use `N/A` if the field is required but not applicable

## Quick Setup Guide

### For Local Testing

```bash
# Terminal 1: Start white agent
python -m white_agents.simple_white_agent

# Terminal 2: Start launcher (optional)
export AGENT_URL=http://localhost:9002
python launcher.py
```

Your URLs:
- Agent URL: `http://localhost:9002`
- Controller URL: `http://localhost:8081` (if using launcher)

### For Production Deployment

#### Using Render/Railway/etc.

**Deploy White Agent:**
1. Deploy your white agent service
2. Get public URL: `https://your-white-agent.onrender.com`

**Deploy Launcher (if needed):**
1. Create a new service for the launcher
2. Use Docker image: `agentbeats/launcher:latest`
3. Set environment variable: `AGENT_URL=https://your-white-agent.onrender.com`
4. Get launcher URL: `https://your-launcher.onrender.com`

**Register on AgentBeats:**
- Agent URL: `https://your-white-agent.onrender.com`
- Controller URL: `https://your-launcher.onrender.com` (or same as agent URL)

#### Using Docker Compose

```yaml
version: '3.8'
services:
  white-agent:
    build: .
    ports:
      - "9002:9002"
    environment:
      - WHITE_AGENT_HOST=0.0.0.0
      - WHITE_AGENT_PORT=9002
  
  launcher:
    image: agentbeats/launcher:latest
    ports:
      - "8081:8081"
    environment:
      - AGENT_URL=http://white-agent:9002
```

## Updating white_agent_card.toml

If you're using a launcher, update your agent card:

```toml
[agent]
url = "https://your-white-agent.com"

[agent.deployment]
agent_url = "https://your-white-agent.com"
controller_url = "https://your-launcher.com"  # Optional
launcher_url = "https://your-launcher.com"    # Alternative name
```

## Testing the Controller URL

Test that your controller/launcher is working:

```bash
# Health check
curl https://your-launcher.com/health

# Info endpoint
curl https://your-launcher.com/info

# Launch endpoint
curl https://your-launcher.com/launch
```

## Common Issues

### "Controller URL is required"

If AgentBeats requires a Controller URL but you don't have one:
1. Use the same URL as your Agent URL
2. Set up a simple launcher service
3. Contact AgentBeats support for white agent-specific guidance

### "Controller not responding"

- Verify the launcher service is running
- Check firewall/network settings
- Ensure the launcher can reach your agent URL
- Check logs for errors

### "Agent URL not accessible from controller"

- Ensure both services are on the same network (for Docker)
- Use public URLs for both (for cloud deployments)
- Verify DNS/domain resolution

## Recommendation for White Agents

**For most white agents, you can simply:**
1. Deploy your white agent with a public URL
2. Use that same URL for both Agent URL and Controller URL
3. The A2A server handles everything needed

The separate launcher is mainly needed for:
- Complex agent architectures
- Multiple agent instances
- Advanced lifecycle management

## Example: Complete Setup

```bash
# 1. Deploy white agent
# Get URL: https://my-white-agent.onrender.com

# 2. Update white_agent_card.toml
[agent]
url = "https://my-white-agent.onrender.com"

[agent.deployment]
agent_url = "https://my-white-agent.onrender.com"
controller_url = "https://my-white-agent.onrender.com"  # Same URL

# 3. Register on AgentBeats
# Agent URL: https://my-white-agent.onrender.com
# Controller URL: https://my-white-agent.onrender.com
```

## Need Help?

- Check AgentBeats documentation: https://agentbeats.org/docs
- See `docs/WHITE_AGENT_AGENTBEATS_CONNECTION.md` for general connection guide
- Contact AgentBeats support for platform-specific requirements


