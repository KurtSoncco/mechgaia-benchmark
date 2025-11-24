#!/bin/bash
# Script to prepare files for git commit

set -e

echo "🧹 Preparing codebase for git commit..."
echo ""

# Add .gitignore first
echo "📝 Adding .gitignore..."
git add .gitignore

# Add core new features
echo "📦 Adding LLM providers..."
git add llm_providers/

echo "📦 Adding MCP protocol..."
git add mcp/

echo "📦 Adding A2A communication..."
git add a2a/

echo "📦 Adding configuration system..."
git add config/

# Add testing tools
echo "🧪 Adding Ollama testing..."
git add test_ollama_leaderboard.py

# Add examples
echo "📚 Adding examples..."
git add examples/llm_usage_example.py
git add examples/mcp_example.py
git add examples/a2a_example.py
git add examples/simple_usage.py

# Add scripts
echo "🔧 Adding scripts..."
git add scripts/setup_agentbeats.sh
git add scripts/test_ollama.sh

# Add documentation
echo "📖 Adding documentation..."
git add MCP_A2A_INTEGRATION.md
git add OLLAMA_TESTING.md
git add QUICKSTART.md
git add AGENTBEATS_SUBMISSION_CHECKLIST.md
git add SUBMISSION_QUICKSTART.md
git add AGENTBEATS_SETUP_COMPLETE.md
git add CLEANUP_SUMMARY.md

# Add updated configuration files
echo "⚙️  Adding updated config files..."
git add pyproject.toml
git add agent_card.toml
git add uv.lock

# Show status
echo ""
echo "✅ Files staged for commit:"
echo ""
git status --short

echo ""
echo "📋 Ready to commit!"
echo ""
echo "Suggested commit message:"
echo "  git commit -m \"Add LLM providers, MCP, A2A support and Ollama testing\""
echo ""
echo "Or review changes first:"
echo "  git status"
echo "  git diff --cached"

