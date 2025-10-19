# MechGAIA: A Green Agent and Benchmark for Mechanical Engineering Design

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)

[cite_start]MechGAIA is a novel benchmark designed to assess the capabilities of AI agents in solving mechanical engineering design and analysis problems[cite: 6]. [cite_start]It extends the general reasoning and tool-use evaluation concepts from benchmarks like GAIA into the specialized domain of engineering[cite: 4, 41].

[cite_start]This repository contains the implementation of the **MechGAIA Green Agent**, which sets up evaluation environments, orchestrates tasks, and judges the performance of competing agents on their ability to solve challenges in stress analysis, thermal conduction, and programmatic CAD modification[cite: 7, 21].

## 🚀 Core Features

-   [cite_start]**Domain-Specific Tasks**: Problems covering a typical undergraduate mechanical engineering curriculum, including stress, deflection, and heat transfer analysis[cite: 22, 23, 45].
-   [cite_start]**Multi-Modal Inputs**: Agents are evaluated on their ability to interpret problems from text, diagrams, and CAD files[cite: 8, 43].
-   [cite_start]**Programmatic CAD Evaluation**: Integrates with **CadQuery** to assess agents on their ability to programmatically generate and modify 3D models to meet design constraints[cite: 24].
-   [cite_start]**Automated Verification**: The Green Agent uses a sandboxed environment to run agent-submitted code, parse results, and assign scores based on numerical accuracy, constraint satisfaction, and physical feasibility[cite: 9, 74].

---

## 🛠️ Installation

This project uses `uv` for fast and efficient package management.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/mechgaia-benchmark.git](https://github.com/your-username/mechgaia-benchmark.git)
    cd mechgaia-benchmark
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    pyenv local 3.11
    uv venv
    source .venv/bin/activate
    ```

3.  **Install all dependencies:**
    ```bash
    uv sync -extra dev
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