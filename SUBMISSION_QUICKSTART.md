# AgentBeats Submission Quick Start

## 🚀 Fast Setup (5 minutes)

```bash
# 1. Activate venv and install dependencies
source .venv/bin/activate
uv sync

# 2. Test your agent
uv run python agentbeats_main.py info
uv run python agentbeats_main.py evaluate examples/submissions/example_level1.json 1

# 3. Update agent_card.toml with your URLs
# Edit agent_card.toml and update:
#   - url = "http://your-deployment-url:8080"
#   - agent_url = "http://your-deployment-url:8080"
#   - launcher_url = "http://your-deployment-url:8081"

# 4. Deploy (choose one):
#   Option A: Docker
docker build -f Dockerfile.uv -t mechgaia-green-agent .
docker run -p 8080:8080 mechgaia-green-agent

#   Option B: Railway/Render
#   - Push to GitHub
#   - Connect to Railway/Render
#   - Set environment variables
#   - Deploy

# 5. Register on agentbeats.org
#   - Log in
#   - Register agent with your URLs
#   - Upload agent_card.toml
```

## ✅ Pre-Submission Checklist

Run this to verify everything:

```bash
# Run the setup script
./scripts/setup_agentbeats.sh

# Or manually:
source .venv/bin/activate
uv sync
uv run python agentbeats_main.py info
uv run python agentbeats_main.py evaluate examples/submissions/example_level1.json 1
```

## 📝 Key Files

- **agent_card.toml** - Agent metadata (UPDATE URLs before submission!)
- **agentbeats_main.py** - Main entry point
- **pyproject.toml** - All dependencies (uses `uv sync`, not `pip install`)
- **Dockerfile.uv** - Docker build using uv

## 🔧 Important Notes

1. **Always use `uv sync`** - Never use `pip install` directly
2. **Python ≥3.11** required (updated in pyproject.toml)
3. **Update URLs** in agent_card.toml before submission
4. **Test locally** before deploying
5. **Health endpoint** must work: `/health`

## 📚 Full Documentation

- **AGENTBEATS_SUBMISSION_CHECKLIST.md** - Complete checklist
- **QUICKSTART.md** - LLM/MCP/A2A usage
- **README.md** - General project documentation

## 🆘 Troubleshooting

**"Module not found" errors:**
```bash
uv sync  # Reinstall dependencies
```

**Agent info fails:**
```bash
# Check if agentbeats is installed
uv run python -c "import agentbeats; print('OK')"
```

**Docker build fails:**
```bash
# Make sure uv.lock exists
uv lock
docker build -f Dockerfile.uv -t mechgaia-green-agent .
```

## 🎯 Next Steps

1. ✅ Complete setup (above)
2. ✅ Test locally
3. ✅ Deploy agent
4. ✅ Update agent_card.toml URLs
5. ✅ Register on agentbeats.org
6. ✅ Submit!

Good luck! 🚀

