#!/bin/bash
# Setup script for AgentBeats submission
# Uses uv for dependency management

set -e

echo "🚀 Setting up MechGAIA Green Agent for AgentBeats Submission"
echo "================================================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed"
    echo "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed"

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies with uv sync..."
uv sync

# Install optional LLM provider dependencies if needed
echo ""
echo "💡 Optional: Install LLM provider SDKs if needed:"
echo "   uv pip install openai      # For OpenAI"
echo "   uv pip install anthropic   # For Anthropic/Claude"
echo ""

# Verify installation
echo "🧪 Verifying installation..."
if uv run python -c "import agentbeats; import earthshaker" 2>/dev/null; then
    echo "✅ AgentBeats SDK and Earthshaker installed"
else
    echo "❌ Error: AgentBeats dependencies not found"
    exit 1
fi

# Test agent
echo ""
echo "🧪 Testing agent..."
if uv run python agentbeats_main.py info > /dev/null 2>&1; then
    echo "✅ Agent info command works"
else
    echo "⚠️  Warning: Agent info command failed (this may be normal if dependencies are missing)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update agent_card.toml with your deployment URLs"
echo "2. Test locally: uv run python agentbeats_main.py info"
echo "3. Deploy your agent"
echo "4. Register on agentbeats.org"
echo ""
echo "See AGENTBEATS_SUBMISSION_CHECKLIST.md for full checklist"

