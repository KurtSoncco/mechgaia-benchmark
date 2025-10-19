#!/bin/bash
# Simple deployment script for uv-based projects

set -e

echo "🚀 Deploying MechGAIA Green Agent with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv sync --extra dev

# Run tests
echo "🧪 Running tests..."
uv run pytest tests/ -v

# Test the agent
echo "🤖 Testing agent..."
uv run python agentbeats_main.py info

echo "✅ Deployment preparation complete!"
echo ""
echo "🌐 Ready for cloud deployment:"
echo "1. Railway: Connect GitHub repo → Auto-deploy"
echo "2. Render: Connect GitHub repo → Auto-deploy" 
echo "3. Fly.io: flyctl launch → Auto-deploy"
echo ""
echo "📊 Your agent will be available at:"
echo "• AgentBeats endpoint: https://your-app.railway.app"
echo "• Health check: https://your-app.railway.app/health"
echo "• Agent info: https://your-app.railway.app/info"
