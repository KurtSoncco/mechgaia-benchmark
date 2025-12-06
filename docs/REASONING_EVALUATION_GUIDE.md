# MechGAIA Reasoning Evaluation Implementation Guide

## Overview

This implementation adds semantic reasoning evaluation to the MechGAIA benchmark. Instead of only checking numerical correctness, the system now evaluates the quality of agent reasoning by comparing it against reference solutions using an LLM instance.

## Components Implemented

### 1. **Reasoning Evaluator Module** (`utils/reasoning_evaluator.py`)
- **Purpose**: Compares agent reasoning with reference solutions
- **Providers Supported**:
  - Ollama (local, recommended for benchmarking)
  - OpenAI (cloud-based)
  - Anthropic/Claude (cloud-based)
  - Generic HTTP endpoints

**Key Features**:
- Evaluates conceptual alignment (60% weight)
- Evaluates reasoning quality (40% weight)
- Identifies key concepts mentioned in reasoning
- Batch evaluation support
- Graceful fallback on errors

**Configuration**:
```python
config = {
    "provider": "ollama",  # or "openai", "anthropic"
    "model": "neural-chat",  # Model name
    "base_url": "http://localhost:11434",  # For Ollama
    "temperature": 0.3,  # Lower = more consistent
    "max_tokens": 500,
    "enabled": True
}
```

### 2. **Semantic Similarity Evaluator** (`utils/semantic_similarity.py`)
- **Purpose**: Lightweight, LLM-free reasoning evaluation
- **Approach**: Keyword matching, concept detection, structure analysis
- **Use Cases**:
  - Fallback when LLM unavailable
  - Fast pre-screening of reasoning
  - Deterministic evaluation (no randomness)

**Features**:
- Technical keyword extraction
- Concept coverage analysis
- Structure similarity detection
- Optional sentence embeddings (if transformers available)
- No API calls required

### 3. **Updated Base Agent** (`green_agents/green_agent_base.py`)
- **New Methods**:
  - `evaluate_reasoning()`: Main reasoning evaluation method
  - `get_reference_reasoning()`: Override to provide reference solution
  - `get_key_concepts()`: Override to specify concepts to check
  - `_extract_reasoning()`: Extract reasoning from submission

- **Updated Scoring**:
  - Combines numerical and reasoning scores
  - Configurable weights (default: 70% numerical, 30% reasoning)
  - Returns detailed breakdown in results

### 4. **Task-Specific Updates**

#### Level 1 (Stress Calculation)
- Reference reasoning explaining beam theory, flexure formula
- Key concepts: bending stress, moment of inertia, neutral axis, flexure formula
- Weight: 70% numerical accuracy, 30% reasoning quality

#### Level 2 (Shaft Design)
- Reference reasoning covering torque calculation, material selection
- Key concepts: torque, power transmission, safety factor, torsion formula
- Checks material database selection + stress constraint satisfaction

#### Level 3 (Plate Optimization)
- Reference reasoning on optimization strategies, FEA approach
- Key concepts: finite element analysis, deflection reduction, design iteration
- Evaluates parametric design methodology

### 5. **Metrics System Updates** (`metrics_system.py`)
- Extended `EvaluationResult` with:
  - `numerical_score`: Numerical accuracy component
  - `reasoning_score`: Reasoning quality component
- Updated database schema to store separate scores
- Enables per-component performance tracking

### 6. **Configuration System** (`config/llm_config.py`)
- New reasoning evaluator configuration section
- Environment variable support:
  - `REASONING_EVAL_ENABLED`: Enable/disable evaluation
  - `REASONING_EVAL_PROVIDER`: Select LLM provider
  - `REASONING_EVAL_MODEL`: Model name
  - `REASONING_EVAL_BASE_URL`: For Ollama/custom endpoints
  - `REASONING_EVAL_TEMPERATURE`: LLM temperature
  - `REASONING_EVAL_MAX_TOKENS`: Response length
  - `REASONING_EVAL_NUMERICAL_WEIGHT`: Numerical score weight
  - `REASONING_EVAL_REASONING_WEIGHT`: Reasoning score weight

## Quick Start

### Option 1: Using Ollama (Recommended for Benchmarking)

```bash
# 1. Install and run Ollama
# Download from: https://ollama.ai
# Run: ollama serve

# 2. Pull a model (in another terminal)
ollama pull neural-chat  # Fast, ~4GB
# or
ollama pull mistral  # More capable, ~5GB

# 3. Configure environment
export REASONING_EVAL_ENABLED=true
export REASONING_EVAL_PROVIDER=ollama
export REASONING_EVAL_MODEL=neural-chat
export REASONING_EVAL_BASE_URL=http://localhost:11434

# 4. Run evaluation
python agentbeats_main.py
```

### Option 2: Using OpenAI

```bash
export REASONING_EVAL_ENABLED=true
export REASONING_EVAL_PROVIDER=openai
export REASONING_EVAL_MODEL=gpt-3.5-turbo
export REASONING_EVAL_API_KEY=sk-...
```

### Option 3: Semantic-Only (No LLM Required)

```python
from utils.semantic_similarity import get_semantic_evaluator

evaluator = get_semantic_evaluator()
score = evaluator.evaluate_similarity(
    agent_reasoning="...",
    reference_reasoning="...",
    task_level=1
)
print(f"Score: {score.score:.2f}")
```

## Usage Example

### Basic Evaluation

```python
from green_agents.level1_stress_task import Level1StressTask
from datetime import datetime

# Create task instance
task = Level1StressTask(task_id="demo_level1")

# Prepare agent submission
submission = {
    "answer_pa": 31.83e6,
    "reasoning_code": """
import math
P = 100  # N
L = 1.0  # m
d = 0.02  # m
M = (P * L) / 4
I = (math.pi * d**4) / 64
c = d / 2
stress = (M * c) / I
print(f"Maximum bending stress: {stress:.2e} Pa")
    """
}

# Run evaluation
result = task.run_evaluation(submission)

print(f"Final Score: {result['final_score']:.2f}")
print(f"  Numerical: {result['numerical_score']:.2f}")
print(f"  Reasoning: {result['reasoning_score']:.2f}")
print(f"Details: {result['details']}")
```

### Custom Reasoning Weights

```python
class CustomLevel1(Level1StressTask):
    def calculate_final_score(self, score_details):
        # Custom: 50% numerical, 50% reasoning
        numerical_scores = [
            v for k, v in score_details.items()
            if isinstance(v, (int, float)) and k != "reasoning"
        ]
        numerical_score = sum(numerical_scores) / len(numerical_scores)
        
        reasoning_data = score_details.get("reasoning")
        reasoning_score = reasoning_data.get("score", 1.0) if reasoning_data else 1.0
        
        final_score = 0.5 * numerical_score + 0.5 * reasoning_score
        
        return {
            "final_score": final_score,
            "numerical_score": numerical_score,
            "reasoning_score": reasoning_score,
            "details": score_details
        }
```

### Batch Evaluation

```python
from utils.reasoning_evaluator import get_reasoning_evaluator

evaluator = get_reasoning_evaluator()

evaluations = [
    {
        "agent_reasoning": "...",
        "reference_reasoning": "...",
        "task_description": "Calculate stress...",
        "key_concepts": ["bending stress", "moment of inertia"],
        "task_level": 1
    },
    # ... more evaluations
]

results = evaluator.batch_evaluate(evaluations)
for i, score in enumerate(results):
    print(f"Evaluation {i}: {score.score:.2f} - {score.feedback}")
```

## Performance Considerations

### Ollama (Recommended)
- **Pros**: Local, free, no API calls, fast
- **Cons**: Requires local GPU/CPU, startup time
- **Typical Response Time**: 5-30 seconds per evaluation
- **Models**: neural-chat (fast), mistral (better quality), llama2

### OpenAI
- **Pros**: High quality, reliable
- **Cons**: API costs (~$0.001-0.01 per evaluation), internet required
- **Typical Response Time**: 2-5 seconds
- **Recommended Model**: gpt-3.5-turbo (cost-effective)

### Semantic-Only
- **Pros**: Instant, deterministic, free
- **Cons**: Less nuanced evaluation
- **Response Time**: <100ms
- **Quality**: 70-80% correlation with LLM evaluation

## Troubleshooting

### Issue: "ReasoningEvaluator not available"
**Solution**: Ensure dependencies installed:
```bash
pip install requests sentence-transformers torch
```

### Issue: Ollama connection refused
**Solution**: 
```bash
# Check if Ollama is running
curl http://localhost:11434/api/status

# Start Ollama
ollama serve
```

### Issue: LLM response parsing fails
**Solution**: Check model's response format. Use semantic evaluator as fallback:
```python
from utils.semantic_similarity import get_semantic_evaluator
evaluator = get_semantic_evaluator()
# Will not fail, but less nuanced
```

### Issue: API rate limits (OpenAI)
**Solution**: Implement retry logic:
```python
import time
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential())
def evaluate_with_retry(reasoning, reference):
    return evaluator.evaluate_reasoning(reasoning, reference, "task", ["concept"])

score = evaluate_with_retry(agent_reasoning, ref_reasoning)
```

## Database Migration

If upgrading existing installation:

```python
import sqlite3

db_path = "mechgaia_metrics.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add new columns to evaluations table
try:
    cursor.execute("ALTER TABLE evaluations ADD COLUMN numerical_score REAL")
    cursor.execute("ALTER TABLE evaluations ADD COLUMN reasoning_score REAL")
    conn.commit()
    print("Database upgraded successfully")
except sqlite3.OperationalError as e:
    print(f"Columns may already exist: {e}")

conn.close()
```

## Integration with AgentBeats

The reasoning evaluator integrates seamlessly with AgentBeats:

```python
# In agentbeats_main.py or your evaluation handler
from green_agents.level1_stress_task import Level1StressTask
from datetime import datetime
from metrics_system import MetricsCollector, EvaluationResult

task = Level1StressTask("task_1")
result_dict = task.run_evaluation(submission_path)

# Create metrics result
metrics_result = EvaluationResult(
    agent_id="agent_123",
    agent_name="TestAgent",
    task_level=1,
    task_id="task_1",
    final_score=result_dict["final_score"],
    numerical_score=result_dict.get("numerical_score"),
    reasoning_score=result_dict.get("reasoning_score"),
    details=result_dict["details"],
    timestamp=datetime.now(),
    submission_data=submission,
    evaluation_time_ms=elapsed_ms,
)

# Store in database
collector = MetricsCollector()
collector.record_evaluation(metrics_result)
```

## Best Practices

1. **Start with semantic evaluation** for fast iteration
2. **Validate with small LLM** (neural-chat) before scaling
3. **Cache reference reasonings** to avoid repeated storage
4. **Monitor evaluation latency** in production
5. **Test with diverse agent reasoning** during development
6. **Set reasonable temperature** (0.3-0.5 for reproducibility)
7. **Regularly review concept lists** for relevance
8. **Document custom scoring weights** in your task classes

## Future Enhancements

- [ ] Multi-model ensemble for robust evaluation
- [ ] Fine-tuned models specific to mechanical engineering
- [ ] Streaming evaluation for large reasoning documents
- [ ] Concept extraction and validation pipeline
- [ ] Automated reference reasoning generation
- [ ] Evaluation confidence scores
- [ ] Comparison analytics dashboard

## References

- **Ollama**: https://ollama.ai
- **Sentence Transformers**: https://www.sbert.net
- **OpenAI API**: https://platform.openai.com/docs
- **Anthropic API**: https://docs.anthropic.com
