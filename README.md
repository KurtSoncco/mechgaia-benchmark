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

*(This section is a placeholder for when the benchmark runner is implemented).*

To evaluate a "white" agent, you will use the primary benchmark script. The script will orchestrate the Green Agent to present a task to the white agent and score its submitted solution.

```bash
# Example command (to be implemented)
python run_benchmark.py --task-level 1 --white-agent-path path/to/your/agent.py