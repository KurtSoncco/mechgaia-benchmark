# MechGAIA: A Green Agent and Benchmark for Mechanical Engineering Design

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)

MechGAIA is a novel benchmark designed to assess the capabilities of AI agents in solving mechanical engineering design and analysis problems. It extends the general reasoning and tool-use evaluation concepts from benchmarks like GAIA into the specialized domain of engineering.

This repository contains the implementation of the **MechGAIA Green Agent**, which sets up evaluation environments, orchestrates tasks, and judges the performance of competing agents.

## 🚀 Core Features

-   **Domain-Specific Tasks**: Stress analysis, shaft design, and plate optimization.
-   **Multi-Modal Inputs**: Text, diagrams, and CAD files.
-   **Programmatic CAD Evaluation**: Integrates with **CadQuery**.
-   **AgentBeats Integration**: Fully compatible with the AgentBeats platform for competitive evaluation.

## 🛠️ Installation

This project uses [`uv`](https://github.com/astral-sh/uv) for fast, reproducible Python environments.

```bash
# Clone and setup
git clone https://github.com/KurtSoncco/mechgaia-benchmark.git
cd mechgaia-benchmark

# Install dependencies
uv sync --extra dev
```

## 🏁 How to Run

### Quick Start (Local Evaluation)

```bash
source .venv/bin/activate

# Level 1: Stress Analysis Task
python run_benchmark.py --task-level 1 --white-agent-path examples/submissions/example_level1.json
```

See `docs/TASK_INDEX.md` for details on all task levels.

### AgentBeats Platform

The agent is designed to run on the AgentBeats platform.

```bash
# Get agent info
python agentbeats_main.py info

# Run in interactive mode (platform standard)
python agentbeats_main.py
```

## 📚 Documentation

Detailed documentation has been moved to the `docs/` directory:

-   [Setup Guide](docs/AGENTBEATS_SETUP_COMPLETE.md)
-   [Submission Checklist](docs/AGENTBEATS_SUBMISSION_CHECKLIST.md)
-   [Task Index](docs/TASK_INDEX.md)
-   [Ollama Testing](docs/OLLAMA_TESTING.md)
-   [Render Deployment](docs/RENDER_DEPLOYMENT.md)

## 🌐 Deployment

Deploy to [Render](https://render.com) for free hosting:

```bash
# 1. Push to GitHub
git push origin main

# 2. Deploy to Render (see docs/RENDER_DEPLOYMENT.md)
# - Connect your GitHub repo
# - Render auto-detects render.yaml
# - Get your public URL

# 3. Update agent_card.toml with your URL
```

See [RENDER_DEPLOYMENT.md](docs/RENDER_DEPLOYMENT.md) for detailed instructions.

## 📄 License

MIT License
