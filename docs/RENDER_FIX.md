# Render Deployment Fix - Quick Guide

## The Problem

Your agent was exiting immediately because it was waiting for stdin input (which doesn't exist in a web container).

## The Solution

Modified `agentbeats_main.py` to:
- **Detect web service mode** (no stdin available)
- **Stay alive** by sleeping instead of waiting for input
- **Keep health server running** continuously

## Deploy the Fix

```bash
# 1. Commit the fix
git add agentbeats_main.py
git commit -m "Fix: Keep agent alive in web service mode"
git push origin main

# 2. Render will auto-deploy (takes ~2-3 minutes)

# 3. Test your deployment
curl https://mechgaia-benchmark.onrender.com/health
curl https://mechgaia-benchmark.onrender.com/info
```

## Expected Logs (After Fix)

```
2025-11-24 XX:XX:XX - MechGAIA - INFO - Initialized MechGAIA-Green-Agent v0.1.0
2025-11-24 XX:XX:XX - MechGAIA - INFO - Supported levels: [1, 2, 3]
2025-11-24 XX:XX:XX - MechGAIA - INFO - Health server starting on 0.0.0.0:8080
2025-11-24 XX:XX:XX - MechGAIA - INFO - MechGAIA Green Agent started successfully
2025-11-24 XX:XX:XX - MechGAIA - INFO - Running in web service mode (no stdin detected)
2025-11-24 XX:XX:XX - MechGAIA - INFO - Health server is active and ready to handle requests
# ← Agent stays running here (doesn't exit!)
```

## How It Works

The agent now detects if stdin is available:
- **Web Service Mode** (Render, Docker): Stays alive, serves health endpoints
- **Interactive Mode** (Local testing): Reads from stdin as before

Your agent is now ready for production! 🚀
