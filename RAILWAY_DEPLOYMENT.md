# Railway Deployment Guide for MechGAIA

## 🚀 Free Deployment with Railway

### Step 1: Prepare Your Repository
```bash
# Make sure your code is on GitHub
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Step 2: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Connect your repository

### Step 3: Configure Railway Deployment

Create `railway.json` in your project root:
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile.uv"
  },
  "deploy": {
    "startCommand": "uv run python agentbeats_main.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### Step 4: Environment Variables
Set these in Railway dashboard:
```
AGENTBEATS_HOST=0.0.0.0
AGENTBEATS_PORT=8080
REDIS_URL=redis://localhost:6379
PYTHONPATH=/app
```

### Step 5: Deploy
Railway will automatically:
- Build your Docker image
- Deploy your service
- Give you a URL like: `https://mechgaia-agent-production.up.railway.app`

## 🔧 Alternative: Render Deployment

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

### Step 2: Create Web Service
- **Build Command**: `pip install uv && uv sync --frozen`
- **Start Command**: `uv run python agentbeats_main.py`
- **Environment**: `Python 3.11`

### Step 3: Set Environment Variables
```
AGENTBEATS_HOST=0.0.0.0
AGENTBEATS_PORT=8080
```

## 💡 Pro Tips

### For Free Tiers:
- Use SQLite instead of PostgreSQL (already configured)
- Redis is optional (system works without it)
- Monitor your usage to stay within limits

### For Production:
- Use PostgreSQL for better performance
- Add Redis for real-time features
- Set up monitoring and alerts
- Use a custom domain
