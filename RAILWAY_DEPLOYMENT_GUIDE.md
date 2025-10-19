# Railway Deployment Guide for MechGAIA Green Agent

## 🚀 **Overview**

You need to deploy two separate services on Railway:

1. **Agent Service**: Main MechGAIA green agent (`agentbeats_main.py`)
2. **Launcher Service**: AgentBeats launcher service (`launcher.py`)

## 📋 **Prerequisites**

- GitHub repository with your code
- Railway account (free tier available)
- Both services will be deployed from the same repository

## 🔧 **Step 1: Deploy Agent Service**

### **1.1 Create New Railway Project**
1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository

### **1.2 Configure Agent Service**
1. **Project Name**: `mechgaia-agent` (or similar)
2. **Dockerfile**: Use `Dockerfile.uv`
3. **Railway Config**: Use `railway.json`

### **1.3 Set Environment Variables**
In Railway dashboard, add these environment variables:

```
AGENTBEATS_HOST=0.0.0.0
AGENTBEATS_PORT=8080
PYTHONPATH=/app
REDIS_URL=""
```

### **1.4 Deploy**
1. Railway will automatically build and deploy
2. Note the deployment URL (e.g., `https://mechgaia-agent-production.up.railway.app`)

## 🔧 **Step 2: Deploy Launcher Service**

### **2.1 Create Second Railway Project**
1. Go to Railway dashboard
2. Click "New Project" again
3. Select "Deploy from GitHub repo"
4. Choose the same repository

### **2.2 Configure Launcher Service**
1. **Project Name**: `mechgaia-launcher` (or similar)
2. **Dockerfile**: Use `Dockerfile.launcher`
3. **Railway Config**: Use `railway-launcher.json`

### **2.3 Set Environment Variables**
In Railway dashboard, add these environment variables:

```
LAUNCHER_HOST=0.0.0.0
LAUNCHER_PORT=8081
AGENT_URL=https://your-agent-url.up.railway.app
PYTHONPATH=/app
```

**Important**: Replace `your-agent-url` with the actual URL from Step 1.4

### **2.4 Deploy**
1. Railway will automatically build and deploy
2. Note the deployment URL (e.g., `https://mechgaia-launcher-production.up.railway.app`)

## 🧪 **Step 3: Testing Both Services**

### **3.1 Test Agent Service**
```bash
# Test health endpoint
curl https://your-agent-url.up.railway.app/health

# Test agent info
curl https://your-agent-url.up.railway.app/info
```

Expected response:
```json
{
  "status": "healthy",
  "agent_name": "MechGAIA-Green-Agent",
  "version": "0.1.0",
  "timestamp": "2024-10-19T18:35:34.447896+00:00",
  "supported_levels": [1, 2, 3]
}
```

### **3.2 Test Launcher Service**
```bash
# Test launcher health
curl https://your-launcher-url.up.railway.app/health

# Test launcher info
curl https://your-launcher-url.up.railway.app/info
```

Expected response:
```json
{
  "status": "healthy",
  "service": "launcher",
  "agent_available": true,
  "agent_url": "https://your-agent-url.up.railway.app",
  "timestamp": "2024-10-19T18:35:34.447896+00:00"
}
```

## 📝 **Step 4: AgentBeats Registration**

Use these URLs for AgentBeats registration:

- **Agent URL**: `https://your-agent-url.up.railway.app`
- **Launcher URL**: `https://your-launcher-url.up.railway.app`

## 🔧 **Alternative: Single Repository with Multiple Services**

If you prefer to manage both services in a single Railway project:

### **Option A: Use Railway's Multi-Service Feature**
1. Create one Railway project
2. Add both services as separate deployments
3. Configure each with its respective Dockerfile and environment variables

### **Option B: Use Docker Compose on Railway**
1. Create a single Railway project
2. Use `docker-compose.yml` for both services
3. Railway will deploy both services automatically

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Port Configuration**:
   - Agent service should use port 8080
   - Launcher service should use port 8081
   - Railway automatically sets `PORT` environment variable

2. **Environment Variables**:
   - Make sure `AGENT_URL` in launcher points to the correct agent URL
   - Verify all environment variables are set correctly

3. **Health Checks**:
   - Both services should respond to `/health` endpoint
   - Check Railway logs if health checks fail

4. **Build Issues**:
   - Ensure all files are committed to GitHub
   - Check that Dockerfiles are in the root directory
   - Verify uv.lock file is present

### **Debugging Commands**
```bash
# Check agent service logs
railway logs --service mechgaia-agent

# Check launcher service logs
railway logs --service mechgaia-launcher

# Test connectivity between services
curl https://your-agent-url.up.railway.app/health
curl https://your-launcher-url.up.railway.app/health
```

## 💰 **Cost Considerations**

### **Railway Free Tier**
- **Monthly Credits**: $5 worth of usage
- **Services**: Up to 2 services
- **Bandwidth**: 100GB/month
- **Storage**: 1GB

### **Optimization Tips**
1. **Use smaller Docker images**: Optimize Dockerfiles
2. **Implement health checks**: Prevent unnecessary restarts
3. **Monitor usage**: Check Railway dashboard regularly
4. **Scale down when not in use**: Pause services if needed

## 📊 **Monitoring**

### **Railway Dashboard**
- Monitor CPU and memory usage
- Check deployment logs
- View service health status
- Monitor bandwidth usage

### **Custom Monitoring**
- Health check endpoints provide service status
- Agent service reports supported levels and capabilities
- Launcher service reports agent connectivity

## 🔄 **Updates and Maintenance**

### **Updating Services**
1. Push changes to GitHub
2. Railway automatically redeploys
3. Test both services after updates
4. Update environment variables if needed

### **Rolling Back**
1. Use Railway's deployment history
2. Revert to previous working deployment
3. Check logs for issues

---

**Last Updated**: October 2024  
**Version**: 0.1.0  
**Contact**: kurtwal98@berkeley.edu
