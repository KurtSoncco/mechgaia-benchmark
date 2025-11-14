# Ollama Testing and Leaderboard Guide

This guide shows how to test Ollama LLM models with the MechGAIA green agent and maintain a simple leaderboard.

## 🚀 Quick Start

### 1. Start Ollama

```bash
# Start Ollama server
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# Pull some small models
ollama pull llama2      # ~3.8GB
ollama pull mistral     # ~4.1GB
ollama pull phi         # ~1.6GB (smallest)
ollama pull neural-chat # ~3.8GB
```

### 2. Test Models

```bash
# Activate venv
source .venv/bin/activate

# Test specific models
uv run python test_ollama_leaderboard.py --models llama2 mistral --task-level 1

# Auto-detect and test all available models
uv run python test_ollama_leaderboard.py --task-level 1

# Test different task levels
uv run python test_ollama_leaderboard.py --task-level 2
uv run python test_ollama_leaderboard.py --task-level 3
```

### 3. View Leaderboard

```bash
# Show current leaderboard
uv run python test_ollama_leaderboard.py --show-leaderboard
```

## 📊 Leaderboard Features

The leaderboard tracks:
- **Average Score**: Average score across all evaluations
- **Best Score**: Highest score achieved
- **Worst Score**: Lowest score achieved
- **Total Evaluations**: Number of times model was tested
- **Task Scores**: Scores per task level

## 🎯 Example Usage

### Test Multiple Models

```bash
# Test 3 models on Level 1
uv run python test_ollama_leaderboard.py \
    --models llama2 mistral phi \
    --task-level 1
```

### Test All Available Models

```bash
# Auto-detect and test all models
uv run python test_ollama_leaderboard.py --task-level 1
```

### Custom Ollama URL

```bash
# If Ollama is on a different host/port
uv run python test_ollama_leaderboard.py \
    --ollama-url http://192.168.1.100:11434 \
    --task-level 1
```

## 📈 Leaderboard Output

```
================================================================================
OLLAMA MODEL LEADERBOARD
================================================================================
Rank   Model                     Avg Score    Best     Evaluations
--------------------------------------------------------------------------------
1      llama2                    0.8500       1.0000   5
2      mistral                   0.7200       0.9000   3
3      phi                       0.6500       0.8000   4
================================================================================
Total evaluations: 12
Last updated: 2024-01-15T10:30:00
```

## 🔧 Advanced Usage

### Test Specific Task Levels

```bash
# Level 1: Stress Analysis
uv run python test_ollama_leaderboard.py --task-level 1

# Level 2: Shaft Design
uv run python test_ollama_leaderboard.py --task-level 2

# Level 3: Plate Optimization
uv run python test_ollama_leaderboard.py --task-level 3
```

### Custom Leaderboard File

```bash
# Use a different leaderboard file
uv run python test_ollama_leaderboard.py \
    --leaderboard-file custom_leaderboard.json \
    --task-level 1
```

## 📝 Leaderboard File Format

The leaderboard is stored as JSON:

```json
{
  "models": {
    "llama2": {
      "total_evaluations": 5,
      "total_score": 4.25,
      "average_score": 0.85,
      "task_scores": {
        "level_1": [0.8, 0.9, 0.85, 0.8, 0.9]
      },
      "best_score": 0.9,
      "worst_score": 0.8
    }
  },
  "evaluations": [...],
  "last_updated": "2024-01-15T10:30:00"
}
```

## 🐛 Troubleshooting

### Ollama Not Running

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
docker start ollama
# or
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### No Models Available

```bash
# List available models
ollama list

# Pull models
ollama pull llama2
ollama pull mistral
```

### Connection Errors

```bash
# Check Ollama URL
curl http://localhost:11434/api/tags

# Use custom URL if needed
uv run python test_ollama_leaderboard.py \
    --ollama-url http://your-ollama-host:11434
```

## 🎓 Small Model Recommendations

For testing, these small models work well:

1. **phi** (~1.6GB) - Smallest, fastest
2. **llama2** (~3.8GB) - Good balance
3. **mistral** (~4.1GB) - Better performance
4. **neural-chat** (~3.8GB) - Good for conversations

## 📊 Integration with Green Agent

The test script:
1. Uses Ollama LLM to generate submissions
2. Evaluates submissions with the green agent
3. Tracks scores in the leaderboard
4. Provides detailed statistics

## 🔄 Continuous Testing

You can set up a cron job or script to test models regularly:

```bash
#!/bin/bash
# test_daily.sh
source .venv/bin/activate
uv run python test_ollama_leaderboard.py --task-level 1
uv run python test_ollama_leaderboard.py --show-leaderboard
```

## 📚 Next Steps

1. Test different models
2. Compare performance across task levels
3. Analyze which models work best for mechanical engineering tasks
4. Use results to improve the green agent's evaluation criteria

Happy testing! 🚀


