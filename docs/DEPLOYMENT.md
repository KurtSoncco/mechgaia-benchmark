# MechGAIA Production Deployment Guide

This guide covers deploying the MechGAIA green agent with full metrics collection and leaderboard functionality.

## 🚀 Quick Start

### 1. **Prerequisites**
```bash
# Install Docker and Docker Compose
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (optional)
sudo usermod -aG docker $USER
```

### 2. **Deploy to Production**
```bash
# Clone the repository
git clone https://github.com/KurtSoncco/mechgaia-benchmark.git
cd mechgaia-benchmark

# Deploy with production configuration
./scripts/deploy_production.sh production deploy
```

### 3. **Access the System**
- **MechGAIA Agent**: http://localhost:8080
- **Leaderboard API**: http://localhost:8000
- **Dashboard**: http://localhost:8000/dashboard
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## 📊 Metrics and Leaderboard

### **Metrics Collection**
The system automatically collects:
- Evaluation scores and details
- Agent performance statistics
- Task-level analytics
- Response times and success rates

### **Leaderboard Features**
- **Real-time Updates**: Redis-powered live leaderboard
- **Multiple Rankings**: Total score, best score, evaluation count
- **Agent Statistics**: Detailed performance history
- **Task Analytics**: Level-specific performance metrics

### **API Endpoints**
```bash
# Get leaderboard
curl http://localhost:8000/leaderboard

# Get agent statistics
curl http://localhost:8000/agent/sample_agent_1/stats

# Get task statistics
curl http://localhost:8000/task/1/stats

# Record evaluation
curl -X POST http://localhost:8000/evaluation \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "test_agent",
    "agent_name": "Test Agent",
    "task_level": 1,
    "task_id": "mechgaia_level_1",
    "final_score": 0.95,
    "details": {"numerical_accuracy": 1.0, "code_executes": 0.9}
  }'
```

## 🔧 Management Commands

### **Service Management**
```bash
# Check service status
./scripts/deploy_production.sh production status

# View logs
./scripts/deploy_production.sh production logs

# Restart services
./scripts/deploy_production.sh production restart

# Stop all services
./scripts/deploy_production.sh production stop
```

### **Database Management**
```bash
# Access PostgreSQL
docker exec -it mechgaia-postgres psql -U mechgaia -d mechgaia

# Access Redis
docker exec -it mechgaia-redis redis-cli

# Backup database
docker exec mechgaia-postgres pg_dump -U mechgaia mechgaia > backup.sql

# Restore database
docker exec -i mechgaia-postgres psql -U mechgaia -d mechgaia < backup.sql
```

## 🌐 AgentBeats Integration

### **Deploy to AgentBeats Platform**
```bash
# Register with AgentBeats
agentbeats register \
  --agent-card agent_card.toml \
  --entry-point agentbeats_main.py \
  --name "MechGAIA-Green-Agent" \
  --version "0.1.0"

# Deploy to platform
agentbeats deploy \
  --agent-card agent_card.toml \
  --entry-point agentbeats_main.py \
  --host your-agentbeats-host.com \
  --port 8080
```

### **AgentBeats Configuration**
```bash
# Environment variables
export AGENTBEATS_HOST=your-agentbeats-host.com
export AGENTBEATS_PORT=8080
export LAUNCHER_HOST=your-launcher-host.com
export LAUNCHER_PORT=8081
export REDIS_URL=redis://your-redis-host:6379
```

## 📈 Monitoring and Analytics

### **Health Monitoring**
```bash
# Check all services
curl http://localhost:8000/health
curl http://localhost:8080/health

# Database health
docker exec mechgaia-postgres pg_isready -U mechgaia

# Redis health
docker exec mechgaia-redis redis-cli ping
```

### **Performance Metrics**
```bash
# View container resource usage
docker stats

# Check disk usage
docker system df

# View service logs
docker-compose logs -f leaderboard-api
docker-compose logs -f mechgaia-green-agent
```

### **Custom Analytics**
```python
# Example: Custom analytics script
from metrics_system import metrics_collector

# Get top performers
leaderboard = metrics_collector.get_leaderboard(limit=10)

# Get task statistics
task_stats = metrics_collector.get_task_level_stats(1)

# Get agent history
agent_stats = metrics_collector.get_agent_stats("agent_123")
```

## 🔒 Security Considerations

### **Production Security**
```bash
# Enable HTTPS (update nginx.conf)
# Generate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# Update environment variables
export POSTGRES_PASSWORD=your_secure_password
export REDIS_PASSWORD=your_redis_password
```

### **Access Control**
```bash
# Restrict database access
# Update docker-compose.prod.yml with proper credentials
# Use environment variables for sensitive data
```

## 🚀 Scaling and Performance

### **Horizontal Scaling**
```yaml
# Scale services in docker-compose.prod.yml
services:
  mechgaia-green-agent:
    deploy:
      replicas: 3
  
  leaderboard-api:
    deploy:
      replicas: 2
```

### **Load Balancing**
```nginx
# Update nginx.conf for load balancing
upstream mechgaia_agent {
    server mechgaia-green-agent-1:8080;
    server mechgaia-green-agent-2:8080;
    server mechgaia-green-agent-3:8080;
}
```

## 📋 Troubleshooting

### **Common Issues**
```bash
# Service won't start
docker-compose logs service-name

# Database connection issues
docker exec mechgaia-postgres pg_isready -U mechgaia

# Redis connection issues
docker exec mechgaia-redis redis-cli ping

# Port conflicts
sudo netstat -tulpn | grep :8080
```

### **Performance Issues**
```bash
# Check resource usage
docker stats

# Monitor logs for errors
docker-compose logs -f --tail=100

# Check database performance
docker exec mechgaia-postgres psql -U mechgaia -d mechgaia -c "SELECT * FROM pg_stat_activity;"
```

## 📚 Additional Resources

- **AgentBeats Documentation**: https://agentbeats.org/docs
- **Docker Compose Reference**: https://docs.docker.com/compose/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Redis Documentation**: https://redis.io/documentation

## 🆘 Support

For issues and questions:
- **GitHub Issues**: https://github.com/KurtSoncco/mechgaia-benchmark/issues
- **Email**: kurtwal98@berkeley.edu
- **Documentation**: See README.md for detailed usage instructions
