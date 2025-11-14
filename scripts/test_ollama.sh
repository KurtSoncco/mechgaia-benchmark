#!/bin/bash
# Quick script to test Ollama models with MechGAIA

set -e

echo "🚀 Testing Ollama Models with MechGAIA Green Agent"
echo "=================================================="
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama is not running!"
    echo ""
    echo "Start Ollama with:"
    echo "  docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama"
    echo ""
    echo "Then pull some models:"
    echo "  ollama pull llama2"
    echo "  ollama pull mistral"
    echo "  ollama pull phi"
    exit 1
fi

echo "✅ Ollama is running"
echo ""

# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found. Creating one..."
    uv venv
    source .venv/bin/activate
    uv sync
fi

echo "📋 Available commands:"
echo ""
echo "1. Test specific models:"
echo "   uv run python test_ollama_leaderboard.py --models llama2 mistral --task-level 1"
echo ""
echo "2. Auto-detect and test all models:"
echo "   uv run python test_ollama_leaderboard.py --task-level 1"
echo ""
echo "3. Show leaderboard:"
echo "   uv run python test_ollama_leaderboard.py --show-leaderboard"
echo ""
echo "4. Test different task levels:"
echo "   uv run python test_ollama_leaderboard.py --task-level 2"
echo "   uv run python test_ollama_leaderboard.py --task-level 3"
echo ""

# Run a quick test if models are available
echo "🔍 Checking available models..."
MODELS=$(curl -s http://localhost:11434/api/tags | python3 -c "import sys, json; data=json.load(sys.stdin); print(' '.join([m['name'] for m in data.get('models', [])]))" 2>/dev/null || echo "")

if [ -n "$MODELS" ]; then
    echo "✅ Found models: $MODELS"
    echo ""
    echo "Running quick test with first model..."
    FIRST_MODEL=$(echo $MODELS | cut -d' ' -f1)
    uv run python test_ollama_leaderboard.py --models "$FIRST_MODEL" --task-level 1 2>&1 | tail -20
else
    echo "⚠️  No models found. Pull some models first:"
    echo "   ollama pull llama2"
fi


