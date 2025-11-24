# Render Deployment Guide

This guide walks you through deploying the MechGAIA Green Agent to Render.

## Prerequisites

- GitHub account
- Render account (free tier available at [render.com](https://render.com))
- Git repository with your code

## Quick Deploy

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### Step 2: Connect to Render

1. Go to [render.com](https://render.com) and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your `mechgaia-benchmark` repository

### Step 3: Configure Service

Render will auto-detect the `render.yaml` configuration. Verify:

- **Name**: `mechgaia-green-agent`
- **Environment**: Docker
- **Dockerfile**: `Dockerfile.uv`
- **Health Check**: `/health`

### Step 4: Set Environment Variables (Optional)

Add any custom variables in the Render dashboard:
- `AGENTBEATS_HOST` - Your AgentBeats host (if needed)
- `OPENAI_API_KEY` - If using OpenAI provider

### Step 5: Deploy

Click **"Create Web Service"** and Render will:
1. Build your Docker image
2. Deploy the container
3. Provide a public URL (e.g., `https://mechgaia-green-agent.onrender.com`)

## Post-Deployment

### Test Your Deployment

```bash
curl https://your-app.onrender.com/health
curl https://your-app.onrender.com/info
```

### Update agent_card.toml

Update the URLs in `agent_card.toml`:

```toml
[agent]
url = "https://your-app.onrender.com"

[agent.deployment]
agent_url = "https://your-app.onrender.com"
launcher_url = "https://your-app.onrender.com"
```

## Important Notes

### Free Tier Limitations

- ⚠️ **Spin Down**: Free tier spins down after 15 minutes of inactivity
- ⏱️ **Cold Start**: Takes ~30 seconds to wake up
- 💾 **Hours**: 750 hours/month free

### Keeping It Alive (Optional)

For constant availability, consider:
1. Upgrading to paid tier ($7/month)
2. Using a service like [UptimeRobot](https://uptimerobot.com) to ping every 14 minutes

## Deployment Architecture

```
GitHub Repo → Render Build → Docker Container → Public URL
     ↓              ↓               ↓              ↓
  render.yaml  Dockerfile.uv    Your Agent     HTTPS
```

## Troubleshooting

### Build Fails

Check the build logs in Render dashboard. Common issues:
- Missing dependencies in `pyproject.toml`
- Docker build errors

### Health Check Fails

Ensure your agent's `/health` endpoint returns HTTP 200:
```bash
curl -v https://your-app.onrender.com/health
```

### Agent Not Responding

Check Render logs:
1. Go to your service dashboard
2. Click "Logs" tab
3. Look for startup errors

## Next Steps

1. ✅ Deploy to Render
2. ✅ Test endpoints
3. ✅ Update `agent_card.toml`
4. ✅ Submit to AgentBeats platform

Good luck! 🚀
