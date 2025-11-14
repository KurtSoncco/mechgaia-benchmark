# MechGAIA: A Green Agent and Benchmark for Mechanical Engineering Design

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)

MechGAIA is a novel benchmark designed to assess the capabilities of AI agents in solving mechanical engineering design and analysis problems<sup>[6]</sup>. It extends the general reasoning and tool-use evaluation concepts from benchmarks like GAIA into the specialized domain of engineering[cite: 4, 41].

This repository contains the implementation of the **MechGAIA Green Agent**, which sets up evaluation environments, orchestrates tasks, and judges the performance of competing agents on their ability to solve challenges in stress analysis, thermal conduction, and programmatic CAD modification[cite: 7, 21].

## 🚀 Core Features

-   **Domain-Specific Tasks**: Problems covering a typical undergraduate mechanical engineering curriculum, including stress, deflection, and heat transfer analysis[cite: 22, 23, 45].
-   **Multi-Modal Inputs**: Agents are evaluated on their ability to interpret problems from text, diagrams, and CAD files[cite: 8, 43].
-   **Programmatic CAD Evaluation**: Integrates with **CadQuery** to assess agents on their ability to programmatically generate and modify 3D models to meet design constraints<sup>[24]</sup>.
-   **Automated Verification**: The Green Agent uses a sandboxed environment to run agent-submitted code, parse results, and assign scores based on numerical accuracy, constraint satisfaction, and physical feasibility[cite: 9, 74].
-   **LLM Provider Abstraction**: Plug-and-play support for OpenAI, Anthropic (Claude), Deepseek, local Ollama models, and any OpenAI-compatible API via the new `llm_providers/` package.
-   **Model Context Protocol (MCP)**: Built-in MCP server and client so LLMs can call MechGAIA tools safely.
-   **Agent-to-Agent (A2A) Communication**: Reusable protocol plus HTTP/WebSocket transports for orchestrating multi-agent workflows.
-   **Local LLM Leaderboard**: `test_ollama_leaderboard.py` benchmarks small Ollama models and tracks scores without API keys.

---

## 🛠️ Installation

This project uses [`uv`](https://github.com/astral-sh/uv) for fast, reproducible Python environments.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/KurtSoncco/mechgaia-benchmark.git](https://github.com/KurtSoncco/mechgaia-benchmark.git)
    cd mechgaia-benchmark
    ```

2.  **Create and activate a virtual environment (Python 3.11+):**
    ```bash
    pyenv install 3.11.9       # or use your preferred Python 3.11 build
    pyenv local 3.11.9
    uv venv
    source .venv/bin/activate
    ```

3.  **Install all dependencies (including dev extras):**
    ```bash
    uv sync --extra dev
    ```

---

## 🏁 How to Run the Benchmark

The MechGAIA benchmark is now fully implemented and ready to use! Here's how to evaluate white agents:

### Quick Start

1. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Run a benchmark evaluation:**
   ```bash
   # Level 1: Stress Analysis Task
   python run_benchmark.py --task-level 1 --white-agent-path examples/submissions/example_level1.json
   
   # Level 2: Shaft Design Task
   python run_benchmark.py --task-level 2 --white-agent-path examples/submissions/example_level2.json
   
   # Level 3: Plate Optimization Task
   python run_benchmark.py --task-level 3 --white-agent-path examples/submissions/example_level3.json
   ```

### Task Levels

#### Level 1: Stress Analysis
- **Objective**: Calculate maximum bending stress in a steel rod
- **Skills Tested**: Basic mechanics, numerical computation
- **Submission Format**: JSON with numerical answer and Python code

#### Level 2: Shaft Design
- **Objective**: Select material and calculate minimum shaft diameter
- **Skills Tested**: Material selection, power transmission, constraint satisfaction
- **Submission Format**: JSON with material choice and diameter calculation

#### Level 3: Plate Optimization
- **Objective**: Optimize mounting plate geometry for reduced deflection
- **Skills Tested**: CAD modification, structural optimization, multi-objective design
- **Submission Format**: JSON with path to modified CAD file

### Creating Your Own White Agent

1. **Study the task requirements** by examining the example submissions in `examples/submissions/`
2. **Create your submission** following the required JSON format
3. **Run the evaluation** using the benchmark runner

### Advanced Usage

```bash
# Save results to a file
python run_benchmark.py --task-level 1 --white-agent-path your_agent.json --output results.json

# Enable verbose output
python run_benchmark.py --task-level 1 --white-agent-path your_agent.json --verbose

# Get help
python run_benchmark.py --help
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_mechgaia.py -v

# Run with coverage
pytest tests/ --cov=agents --cov=utils
```

---

## 🤖 AgentBeats Platform Integration

The MechGAIA green agent is fully integrated with the AgentBeats SDK for platform deployment and evaluation.

### AgentBeats Features

- **Platform Integration**: Full AgentBeats SDK compatibility
- **Automated Deployment**: Docker and deployment scripts included
- **Configuration Management**: Flexible configuration system
- **Health Monitoring**: Built-in health checks and monitoring
- **Multi-Level Support**: All three benchmark levels supported

### AgentBeats Usage

#### 1. **Agent Information**
```bash
# Get agent information
python agentbeats_main.py info
```

#### 2. **Direct Evaluation**
```bash
# Evaluate submissions directly
python agentbeats_main.py evaluate examples/submissions/example_level1.json 1
python agentbeats_main.py evaluate examples/submissions/example_level2.json 2
python agentbeats_main.py evaluate examples/submissions/example_level3.json 3
```

#### 3. **Platform Deployment**
```bash
# Deploy to AgentBeats platform
agentbeats deploy \
    --agent-card agent_card.toml \
    --entry-point agentbeats_main.py \
    --name "MechGAIA-Green-Agent" \
    --version "0.1.0"
```

#### 4. **Docker Deployment**
```bash
# Build and run with Docker
docker build -t mechgaia-green-agent .
docker run -p 8080:8080 mechgaia-green-agent

# Or use Docker Compose
docker-compose up -d
```

#### 5. **Deployment Scripts**
```bash
# Full deployment preparation
./scripts/deploy.sh all

# Deploy to AgentBeats platform
./scripts/deploy.sh deploy
```

### AgentBeats Configuration

The agent can be configured using environment variables:

```bash
export AGENTBEATS_HOST=localhost
export AGENTBEATS_PORT=8080
export LAUNCHER_HOST=localhost
export LAUNCHER_PORT=8081
```

### AgentBeats State Format

The agent expects state in the following format:

```json
{
  "task_level": 1,
  "white_agent_submission": {
    "answer_pa": 31830000,
    "reasoning_code": "result = 31830000"
  },
  "task_id": "mechgaia_level_1"
}
```

### AgentBeats Response Format

The agent returns evaluation results in this format:

```json
{
  "final_score": 1.0,
  "details": {
    "numerical_accuracy": 1.0,
    "code_executes": 1.0
  },
  "agent_name": "MechGAIA-Green-Agent",
  "agent_version": "0.1.0",
  "platform": "AgentBeats",
  "task_level": 1,
  "task_id": "mechgaia_level_1"
}
```

## References

[6] Mechanical Engineering Principles, Example Source.
[24] CadQuery Documentation.

---

## 🧠 LLM Provider Quick Start

The `llm_providers/` module exposes a unified interface that works with hosted APIs **and** local models.

```bash
# Install optional SDKs as needed (only if you use those providers)
uv pip install openai anthropic
```

```python
from llm_providers import get_llm_provider, LLMMessage, MessageRole

provider = get_llm_provider("ollama", model="phi", base_url="http://localhost:11434")
messages = [LLMMessage(role=MessageRole.USER, content="What is 2+2?")]
response = provider.chat(messages)
print(response.content)
```

More examples live in `examples/llm_usage_example.py` and the comprehensive [`QUICKSTART.md`](QUICKSTART.md).

---

## 🧰 Model Context Protocol (MCP)

The new `mcp/` package lets you expose MechGAIA tools to any MCP-compliant LLM (OpenAI GPTs, Claude, etc.).

Key components:
- `mcp/server.py`: register tools/resources and expose them over JSON-RPC
- `mcp/client.py`: connect to MCP servers from the green agent or scripts
- `MCP_A2A_INTEGRATION.md`: full protocol guide with examples

Use [`examples/mcp_example.py`](examples/mcp_example.py) to spin up a sample MCP server/client pair.

---

## 🔄 Agent-to-Agent (A2A) Protocol

Need agents to coordinate? The `a2a/` package adds a lightweight protocol plus transport implementations:

- `a2a/agent.py`: base agent with message routing + action handlers
- `a2a/transport.py`: HTTP & WebSocket transports (async, based on `aiohttp`)
- `a2a/broker.py`: discovery/routing broker

See [`examples/a2a_example.py`](examples/a2a_example.py) for runnable demos.

---

## 🧪 Local LLM Leaderboard (Ollama)

Prefer offline testing? The new `test_ollama_leaderboard.py` script:

1. Generates submissions with local Ollama models (phi, llama2, mistral, etc.)
2. Evaluates them with the MechGAIA green agent
3. Tracks scores in `ollama_leaderboard.json`

```bash
# Start Ollama
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
ollama pull phi   # small model (~1.6GB)

# Run tests
uv run python test_ollama_leaderboard.py --models phi --task-level 1
uv run python test_ollama_leaderboard.py --show-leaderboard
```

Full instructions live in [`OLLAMA_TESTING.md`](OLLAMA_TESTING.md).

---

## 📄 Submission Checklist & Guides

- [`AGENTBEATS_SUBMISSION_CHECKLIST.md`](AGENTBEATS_SUBMISSION_CHECKLIST.md): Step-by-step prep
- [`SUBMISSION_QUICKSTART.md`](SUBMISSION_QUICKSTART.md): 5-minute version
- [`AGENTBEATS_SETUP_COMPLETE.md`](AGENTBEATS_SETUP_COMPLETE.md): What’s already configured

Use the helper script to stage all essential files before committing:

```bash
./scripts/prepare_commit.sh
git commit -m "Add LLM providers, MCP, A2A support and Ollama testing"
git push
```
