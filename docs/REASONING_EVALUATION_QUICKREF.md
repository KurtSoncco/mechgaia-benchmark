# Reasoning Evaluation - Quick Reference

## Architecture Overview

```
Agent Submission
    ↓
Green Agent (Level1/2/3Task)
    ├─ Numerical Verification ────┐
    │  (existing logic)           │
    │                             ├→ Combined Score (70% num, 30% reasoning)
    ├─ Reasoning Extraction       │
    │  - Extract reasoning string │
    │  - Get reference solution   │
    │  - Get key concepts        │
    │                             │
    ├─ Reasoning Evaluation ──────┤
    │  (new logic)                │
    │  ├→ LLM Evaluator (if enabled)
    │  │  └→ Ollama/OpenAI/Claude
    │  └→ Semantic Evaluator (fallback)
    │     └→ Keyword + Concept matching
    │                             │
    └→ Metrics Collection ────────┘
       - Final Score
       - Numerical Score
       - Reasoning Score
       - Full Details
       - Database Storage
```

## Key Files

| File | Purpose | Key Changes |
|------|---------|-------------|
| `utils/reasoning_evaluator.py` | **NEW** - LLM-based evaluation | Multi-provider support, semantic analysis |
| `utils/semantic_similarity.py` | **NEW** - Fast evaluation | Keyword/concept detection, no LLM needed |
| `green_agents/green_agent_base.py` | Base agent class | Added reasoning evaluation pipeline |
| `green_agents/level1_stress_task.py` | Level 1 task | Added reference reasoning + concepts |
| `green_agents/level2_shaft_design_task.py` | Level 2 task | Added reference reasoning + concepts |
| `green_agents/level3_plate_optimization_task.py` | Level 3 task | Added reference reasoning + concepts |
| `metrics_system.py` | Metrics collection | Added numerical/reasoning scores |
| `config/llm_config.py` | Configuration | Added reasoning evaluator config |
| `docs/REASONING_EVALUATION_GUIDE.md` | **NEW** - Full guide | Complete documentation |
| `examples/reasoning_evaluation_example.py` | **NEW** - Examples | 5 practical examples |

## Environment Variables Reference

### Enable/Disable
```bash
REASONING_EVAL_ENABLED=true|false  # Default: true
```

### Provider Configuration
```bash
# Ollama (Local, Recommended)
REASONING_EVAL_PROVIDER=ollama
REASONING_EVAL_MODEL=neural-chat           # or mistral, llama2
REASONING_EVAL_BASE_URL=http://localhost:11434

# OpenAI
REASONING_EVAL_PROVIDER=openai
REASONING_EVAL_MODEL=gpt-3.5-turbo        # or gpt-4
REASONING_EVAL_API_KEY=sk-...

# Anthropic
REASONING_EVAL_PROVIDER=anthropic
REASONING_EVAL_MODEL=claude-3-sonnet
REASONING_EVAL_API_KEY=sk-ant-...
```

### LLM Parameters
```bash
REASONING_EVAL_TEMPERATURE=0.3              # 0.0-1.0, lower=consistent
REASONING_EVAL_MAX_TOKENS=500               # Response length
```

### Scoring Weights
```bash
REASONING_EVAL_NUMERICAL_WEIGHT=0.7         # 0.0-1.0
REASONING_EVAL_REASONING_WEIGHT=0.3         # Should sum to 1.0
```

## Quick Setup

### Setup 1: Ollama (Fastest to Setup)
```bash
# Install Ollama from https://ollama.ai

# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Pull model
ollama pull neural-chat

# Terminal 3: Set environment
export REASONING_EVAL_ENABLED=true
export REASONING_EVAL_PROVIDER=ollama
export REASONING_EVAL_MODEL=neural-chat

# Run evaluation
python examples/reasoning_evaluation_example.py
```

### Setup 2: OpenAI
```bash
export REASONING_EVAL_ENABLED=true
export REASONING_EVAL_PROVIDER=openai
export REASONING_EVAL_MODEL=gpt-3.5-turbo
export REASONING_EVAL_API_KEY=sk-...

python examples/reasoning_evaluation_example.py
```

### Setup 3: Semantic-Only (No Setup)
```python
from utils.semantic_similarity import get_semantic_evaluator

evaluator = get_semantic_evaluator()
score = evaluator.evaluate_similarity(agent_reasoning, ref_reasoning, task_level=1)
print(f"Score: {score.score}")
```

## Usage Patterns

### Pattern 1: Direct Task Evaluation
```python
from green_agents.level1_stress_task import Level1StressTask

task = Level1StressTask("task_id")
result = task.run_evaluation(submission)  # Returns combined score

print(f"Numerical: {result['numerical_score']:.2f}")
print(f"Reasoning: {result['reasoning_score']:.2f}")
print(f"Final: {result['final_score']:.2f}")
```

### Pattern 2: Separate Evaluations
```python
task = Level1StressTask("task_id")

# Verify numerical
numerical_result = task.verify_submission(submission)
numerical_score = task.calculate_final_score(numerical_result)['final_score']

# Evaluate reasoning
reasoning_result = task.evaluate_reasoning(submission)
reasoning_score = reasoning_result['score']

# Combine manually
final_score = 0.7 * numerical_score + 0.3 * reasoning_score
```

### Pattern 3: Custom Weights
```python
class MyTask(Level1StressTask):
    def calculate_final_score(self, score_details):
        # Your custom logic here
        # Return {"final_score": ..., "numerical_score": ..., ...}
        pass
```

### Pattern 4: Batch Processing
```python
from utils.reasoning_evaluator import get_reasoning_evaluator

evaluator = get_reasoning_evaluator()
results = evaluator.batch_evaluate([
    {
        "agent_reasoning": "...",
        "reference_reasoning": "...",
        "task_description": "...",
        "key_concepts": ["concept1", "concept2"],
        "task_level": 1
    },
    # ... more items
])

for score in results:
    print(f"{score.score:.2f} - {score.feedback}")
```

## Troubleshooting Matrix

| Problem | Cause | Solution |
|---------|-------|----------|
| "ReasoningEvaluator not available" | Missing imports | `pip install requests` |
| Connection refused (Ollama) | Ollama not running | `ollama serve` in terminal |
| API key invalid (OpenAI) | Wrong/missing API key | Check `REASONING_EVAL_API_KEY` |
| Response parsing fails | Wrong model output | Use semantic evaluator fallback |
| Very slow evaluation | Large token count | Reduce `REASONING_EVAL_MAX_TOKENS` |
| OOM error (GPU) | Model too large | Use smaller model (neural-chat) |
| Inconsistent scores | High temperature | Set `REASONING_EVAL_TEMPERATURE=0.3` |
| All reasoning scores = 1.0 | Evaluation disabled | Set `REASONING_EVAL_ENABLED=true` |

## Performance Tips

### Speed Optimization
1. Use semantic evaluator for initial screening
2. Use smaller models (neural-chat vs llama2)
3. Batch evaluate multiple submissions
4. Run LLM on GPU with sufficient memory

### Accuracy Optimization
1. Start with semantic evaluator baseline
2. Compare with LLM evaluation on sample
3. Adjust temperature for consistency (0.2-0.5)
4. Customize key concepts for your domain
5. Update reference reasoning as needed

### Cost Optimization (OpenAI)
1. Use gpt-3.5-turbo (not gpt-4)
2. Batch similar evaluations
3. Limit max_tokens to 300-500
4. Cache reference reasonings
5. Use semantic evaluator for cheaper initial pass

## Example Commands

```bash
# Run all examples
python examples/reasoning_evaluation_example.py

# Test Ollama connection
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"neural-chat","prompt":"test"}'

# Check configuration
python -c "from config.llm_config import get_config; print(get_config().get_reasoning_eval_config())"

# Upgrade database for reasoning scores
python -c "
import sqlite3
conn = sqlite3.connect('mechgaia_metrics.db')
cursor = conn.cursor()
try:
    cursor.execute('ALTER TABLE evaluations ADD COLUMN numerical_score REAL')
    cursor.execute('ALTER TABLE evaluations ADD COLUMN reasoning_score REAL')
    conn.commit()
    print('✓ Database upgraded')
except:
    print('✓ Columns already exist')
conn.close()
"
```

## Scoring Interpretation

### Score Components
- **Numerical Score** (0.0-1.0): Accuracy of calculation/result
- **Reasoning Score** (0.0-1.0): Quality of explanation
- **Final Score** (0.0-1.0): Weighted combination

### Reasoning Score Breakdown
- **Conceptual Alignment** (60% of reasoning score)
  - How well approach matches reference solution
  - Similar methodology and assumptions
  
- **Reasoning Quality** (40% of reasoning score)
  - Clarity and completeness of explanation
  - Logical flow and justification of steps

### Typical Score Distribution
- **Excellent** (0.9-1.0): Correct answer + clear, aligned reasoning
- **Good** (0.7-0.9): Correct answer + good reasoning or slightly off reasoning
- **Adequate** (0.5-0.7): Correct answer + weak reasoning or wrong answer + good reasoning
- **Poor** (0.3-0.5): Significant issues in either component
- **Failed** (<0.3): Major errors or missing submission

## Common Customizations

### Adjust Scoring Weights
```python
# In your evaluation handler
from config.llm_config import get_config

config = get_config()
config.set("reasoning_evaluator.numerical_weight", 0.8)  # 80% numerical
config.set("reasoning_evaluator.reasoning_weight", 0.2)  # 20% reasoning
```

### Add Task-Specific Concepts
```python
class MyTask(Level1StressTask):
    KEY_CONCEPTS = Level1StressTask.KEY_CONCEPTS + [
        "your custom concept",
        "another concept"
    ]
```

### Custom Reference Reasoning
```python
class MyTask(Level1StressTask):
    REFERENCE_REASONING = """
    Your custom reference reasoning here.
    Explain your solution approach step by step.
    """
```

## Integration Checklist

- [ ] Install dependencies: `pip install requests sentence-transformers torch`
- [ ] Configure LLM provider (Ollama/OpenAI/etc)
- [ ] Test evaluator: `python examples/reasoning_evaluation_example.py`
- [ ] Verify database schema updated with new columns
- [ ] Update task classes with reference reasoning
- [ ] Set environment variables in deployment
- [ ] Monitor evaluation latency in production
- [ ] Validate scoring on representative submissions
- [ ] Document custom configurations in your setup

## Support Resources

- **Full Guide**: `docs/REASONING_EVALUATION_GUIDE.md`
- **Examples**: `examples/reasoning_evaluation_example.py`
- **Source Code**: 
  - `utils/reasoning_evaluator.py`
  - `utils/semantic_similarity.py`
  - `green_agents/green_agent_base.py`
