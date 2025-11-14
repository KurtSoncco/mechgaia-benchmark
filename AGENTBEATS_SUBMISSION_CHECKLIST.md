# AgentBeats Green Agent Submission Checklist

This checklist ensures your MechGAIA green agent is ready for AgentBeats submission.

## ✅ Pre-Submission Checklist

### 1. Environment Setup
- [x] Python ≥3.11 (updated in pyproject.toml)
- [x] AgentBeats SDK installed via `uv sync`
- [x] Earthshaker runtime dependency added
- [x] All dependencies in `pyproject.toml` (not requirements.txt)

### 2. Agent Card Configuration
- [x] `agent_card.toml` exists and is valid
- [ ] **Update `url` field** with your deployment URL
- [ ] **Update `agent_url` and `launcher_url`** in `[agent.deployment]` section
- [x] Entry point specified: `agentbeats_main.py`
- [x] All capabilities listed
- [x] All task levels defined

### 3. Entry Point Verification
- [x] `agentbeats_main.py` exists and is executable
- [x] Implements AgentBeats SDK protocol
- [x] Handles A2A protocol for agent communication
- [x] Supports `info` command: `python agentbeats_main.py info`
- [x] Supports `evaluate` command: `python agentbeats_main.py evaluate <file> <level>`

### 4. Local Testing
```bash
# Activate venv and install dependencies
source .venv/bin/activate  # or: uv venv && source .venv/bin/activate
uv sync

# Test agent info
uv run python agentbeats_main.py info

# Test evaluation
uv run python agentbeats_main.py evaluate examples/submissions/example_level1.json 1
uv run python agentbeats_main.py evaluate examples/submissions/example_level2.json 2
uv run python agentbeats_main.py evaluate examples/submissions/example_level3.json 3
```

- [ ] All commands execute successfully
- [ ] Agent returns valid JSON responses
- [ ] Health endpoint works: `curl http://localhost:8080/health`

### 5. Docker Deployment
- [x] `Dockerfile` exists
- [x] `Dockerfile.uv` for uv-based builds
- [x] `docker-compose.yml` for local testing
- [ ] Docker image builds successfully: `docker build -t mechgaia-green-agent .`
- [ ] Container runs: `docker run -p 8080:8080 mechgaia-green-agent`
- [ ] Health check passes in container

### 6. Production Deployment
Choose one:
- [ ] **Remote Mode**: Deploy as web service (Railway, Render, etc.)
- [ ] **Hosted Mode**: Provide GitHub repo or Docker image

**For Remote Mode:**
- [ ] Service is publicly accessible
- [ ] Health endpoint responds: `https://your-url.com/health`
- [ ] Update `agent_card.toml` with production URLs
- [ ] Set environment variables (AGENTBEATS_HOST, PORT, etc.)

**For Hosted Mode:**
- [ ] GitHub repo is public and accessible
- [ ] Docker image is published (optional)
- [ ] README includes setup instructions

### 7. AgentBeats Registration
When agentbeats.org is available:
- [ ] Log in to agentbeats.org
- [ ] Register your agent with:
  - Agent URL: `http://YOUR_IP:8080/` or `https://your-url.com`
  - Launcher URL: `http://YOUR_IP:8081/` (if using launcher)
  - Agent Card: Upload `agent_card.toml`
- [ ] Verify agent appears in dashboard

### 8. Documentation
- [x] README.md includes:
  - [x] Installation instructions (using `uv sync`)
  - [x] Running instructions
  - [x] Testing instructions
  - [x] Deployment instructions
- [x] Agent card is complete
- [x] Example submissions in `examples/submissions/`

### 9. Code Quality
- [x] All imports work
- [x] No hardcoded paths
- [x] Environment variables used for configuration
- [x] Error handling implemented
- [x] Logging in place

## 🚀 Quick Start Commands

### Setup
```bash
# Create/activate venv
uv venv
source .venv/bin/activate

# Install all dependencies
uv sync

# Or install with dev dependencies
uv sync --extra dev
```

### Testing
```bash
# Test agent info
uv run python agentbeats_main.py info

# Test evaluation
uv run python agentbeats_main.py evaluate examples/submissions/example_level1.json 1

# Run tests
uv run pytest tests/ -v
```

### Docker
```bash
# Build
docker build -f Dockerfile.uv -t mechgaia-green-agent .

# Run
docker run -p 8080:8080 \
  -e AGENTBEATS_HOST=0.0.0.0 \
  -e AGENTBEATS_PORT=8080 \
  mechgaia-green-agent

# Test health
curl http://localhost:8080/health
```

### Production Deployment (Railway Example)
```bash
# Set environment variables in Railway dashboard:
# - AGENTBEATS_HOST=0.0.0.0
# - AGENTBEATS_PORT=$PORT
# - PYTHONPATH=/app

# Update agent_card.toml with Railway URL
# Then register on agentbeats.org
```

## 📝 Files to Update Before Submission

1. **agent_card.toml**:
   - Update `url` with your deployment URL
   - Update `agent_url` and `launcher_url` in `[agent.deployment]`

2. **Environment Variables** (if deploying):
   - `AGENTBEATS_HOST=0.0.0.0`
   - `AGENTBEATS_PORT=8080` (or `$PORT` for platforms like Railway)
   - `OPENAI_API_KEY` (if using OpenAI models)

## ✅ Final Verification

Before submitting, verify:
1. ✅ All dependencies install with `uv sync`
2. ✅ `agentbeats_main.py info` works
3. ✅ `agentbeats_main.py evaluate` works for all levels
4. ✅ Health endpoint responds
5. ✅ Docker builds and runs
6. ✅ Agent card has correct URLs
7. ✅ README is complete

## 📞 Support

If you encounter issues:
1. Check AgentBeats SDK documentation
2. Verify all dependencies are in `pyproject.toml`
3. Test locally before deploying
4. Check logs for error messages

## 🎯 Submission Steps

1. **Complete all checklist items above**
2. **Deploy your agent** (Remote or Hosted mode)
3. **Update agent_card.toml** with production URLs
4. **Register on agentbeats.org** when available
5. **Test end-to-end** with example submissions
6. **Submit!**

Good luck with your submission! 🚀

