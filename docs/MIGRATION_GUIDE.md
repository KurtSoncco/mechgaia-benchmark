# Migration Guide: Adding Reasoning Evaluation to Existing Installation

## Overview

This guide helps you upgrade an existing MechGAIA installation to include reasoning evaluation.

## Pre-Migration Checklist

- [ ] Backup existing database: `cp mechgaia_metrics.db mechgaia_metrics.db.backup`
- [ ] Note current Python version (requires 3.11+)
- [ ] Check disk space (new code ~2MB, dependencies ~500MB)
- [ ] Review current scoring weights and thresholds

## Step-by-Step Migration

### Step 1: Update Dependencies

```bash
# Install new optional dependencies
pip install requests sentence-transformers torch

# Or update requirements.txt
pip install -r requirements.txt --upgrade
```

**Optional but recommended - Install Ollama**:
```bash
# macOS
brew install ollama

# Linux/Windows
# Download from https://ollama.ai

# Start Ollama service
ollama serve

# In another terminal, pull a model
ollama pull neural-chat
```

### Step 2: Update Database Schema

**Automatic migration** (recommended):
```python
# Run this script once
python -c "
import sqlite3
from pathlib import Path

db_path = 'mechgaia_metrics.db'
if not Path(db_path).exists():
    print('Database does not exist, will be created automatically')
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('ALTER TABLE evaluations ADD COLUMN numerical_score REAL')
        cursor.execute('ALTER TABLE evaluations ADD COLUMN reasoning_score REAL')
        conn.commit()
        print('✓ Database upgraded successfully')
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e):
            print('✓ Columns already exist')
        else:
            raise
    finally:
        conn.close()
"
```

**Manual migration**:
```bash
sqlite3 mechgaia_metrics.db
> ALTER TABLE evaluations ADD COLUMN numerical_score REAL;
> ALTER TABLE evaluations ADD COLUMN reasoning_score REAL;
> .quit
```

### Step 3: Update Configuration

**Option A: Use environment variables**
```bash
# Add to your .env file or shell profile
export REASONING_EVAL_ENABLED=true
export REASONING_EVAL_PROVIDER=ollama
export REASONING_EVAL_MODEL=neural-chat
export REASONING_EVAL_BASE_URL=http://localhost:11434

# For OpenAI instead:
# export REASONING_EVAL_PROVIDER=openai
# export REASONING_EVAL_MODEL=gpt-3.5-turbo
# export REASONING_EVAL_API_KEY=sk-...
```

**Option B: Use configuration file**
```json
// mechgaia_config.json
{
  "reasoning_evaluator": {
    "enabled": true,
    "provider": "ollama",
    "model": "neural-chat",
    "base_url": "http://localhost:11434",
    "temperature": 0.3,
    "max_tokens": 500,
    "numerical_weight": 0.7,
    "reasoning_weight": 0.3
  }
}
```

**Option C: Disable reasoning evaluation (backward compatible)**
```bash
export REASONING_EVAL_ENABLED=false
```

### Step 4: Test the Installation

```bash
# Run the example script
python examples/reasoning_evaluation_example.py

# Expected output should show 5 examples running successfully
# Example 1: Semantic-Only Reasoning Evaluation ✓
# Example 2: LLM-Based Reasoning Evaluation (optional)
# Example 3: Full Task Evaluation ✓
# Example 4: Batch Reasoning Evaluation ✓
# Example 5: Custom Scoring Weights ✓
```

### Step 5: Verify Backward Compatibility

```python
# Test that old evaluation code still works
from green_agents.level1_stress_task import Level1StressTask

task = Level1StressTask("test_task")
submission = {
    "answer_pa": 31.83e6,
    "reasoning_code": "import math; print(31.83e6)"
}

result = task.run_evaluation(submission)
print(f"✓ Backward compatible: {result['final_score']:.2f}")
```

## Migration Validation

Run these checks to ensure successful migration:

```bash
# 1. Check Python version
python --version  # Should be 3.11+

# 2. Check dependencies
python -c "import requests; import torch; print('✓ Dependencies OK')"

# 3. Check database
python -c "
import sqlite3
conn = sqlite3.connect('mechgaia_metrics.db')
cursor = conn.cursor()
cursor.execute(\"PRAGMA table_info(evaluations)\")
columns = {row[1] for row in cursor.fetchall()}
required = {'numerical_score', 'reasoning_score'}
if required.issubset(columns):
    print('✓ Database schema updated')
else:
    print('✗ Database missing columns:', required - columns)
conn.close()
"

# 4. Check configuration
python -c "
from config.llm_config import get_config
config = get_config()
rc = config.get_reasoning_eval_config()
print(f'✓ Reasoning evaluator configured: {rc[\"provider\"]}/{rc[\"model\"]}')
"

# 5. Check Ollama (if using Ollama)
curl -s http://localhost:11434/api/status && echo '✓ Ollama is running'
```

## Rollback Procedure

If you need to revert to the previous version:

```bash
# 1. Restore database backup
cp mechgaia_metrics.db.backup mechgaia_metrics.db

# 2. Disable reasoning evaluation
export REASONING_EVAL_ENABLED=false

# 3. The system will still work but won't evaluate reasoning
#    Scores will be 100% numerical accuracy only
```

## Breaking Changes

**None!** This upgrade is fully backward compatible:
- Existing code continues to work
- Reasoning evaluation is optional
- Can be disabled with `REASONING_EVAL_ENABLED=false`
- Database schema extended but not changed

## Performance Impact

**Before Migration**:
- Evaluation time: 1-5 seconds per submission (numerical only)

**After Migration** (with reasoning evaluation):
- Semantic only: +100ms (fast)
- Ollama: +10-30 seconds
- OpenAI: +2-5 seconds
- Can be disabled to keep original performance

**Recommendation**: Start with semantic evaluation and test before deploying with LLM.

## Configuration Migration

If upgrading from an older version:

```python
# Old approach (direct in code)
numerical_weight = 1.0
reasoning_weight = 0.0

# New approach (configuration)
export REASONING_EVAL_NUMERICAL_WEIGHT=1.0
export REASONING_EVAL_REASONING_WEIGHT=0.0

# Or in config file
config.set("reasoning_evaluator.numerical_weight", 1.0)
```

## Monitoring After Migration

Track these metrics post-migration:

```python
# 1. Verify evaluation latency
import time
start = time.time()
result = task.run_evaluation(submission)
elapsed = time.time() - start
print(f"Evaluation took {elapsed:.2f} seconds")

# 2. Check score distribution
score = result['final_score']
print(f"Score breakdown:")
print(f"  Numerical: {result.get('numerical_score', 'N/A')}")
print(f"  Reasoning: {result.get('reasoning_score', 'N/A')}")
print(f"  Final: {score}")

# 3. Monitor database growth
# Select count(*) from evaluations;
```

## Common Migration Issues

### Issue 1: Import Error
```
ImportError: cannot import name 'ReasoningEvaluator'
```
**Solution**: Ensure new files are in place
```bash
ls -la utils/reasoning_evaluator.py
ls -la utils/semantic_similarity.py
```

### Issue 2: Database Locked
```
sqlite3.OperationalError: database is locked
```
**Solution**: 
```bash
# Stop all existing evaluations
# Close any open database connections
pkill -f "python.*evaluation"
# Then try migration again
```

### Issue 3: Ollama Connection Failed
```
ConnectionError: Failed to connect to http://localhost:11434
```
**Solution**:
```bash
# Start Ollama if not running
ollama serve

# Or disable reasoning evaluation
export REASONING_EVAL_ENABLED=false
```

### Issue 4: API Key Invalid
```
AuthenticationError: Invalid API key
```
**Solution**: Check environment variable
```bash
echo $REASONING_EVAL_API_KEY  # Should not be empty
# Update if needed
export REASONING_EVAL_API_KEY=sk-...
```

## Post-Migration Testing

### Quick Test
```bash
python examples/reasoning_evaluation_example.py
```

### Integration Test
```python
from green_agents.level1_stress_task import Level1StressTask
from metrics_system import MetricsCollector
from datetime import datetime

# Create test submission
submission = {
    "answer_pa": 31.83e6,
    "reasoning_code": "print(31.83e6)"
}

# Evaluate
task = Level1StressTask("test_1")
result = task.run_evaluation(submission)

# Record in database
from metrics_system import EvaluationResult
eval_result = EvaluationResult(
    agent_id="test_agent",
    agent_name="TestAgent",
    task_level=1,
    task_id="test_1",
    final_score=result['final_score'],
    numerical_score=result.get('numerical_score'),
    reasoning_score=result.get('reasoning_score'),
    details=result['details'],
    timestamp=datetime.now(),
    submission_data=submission,
    evaluation_time_ms=100
)

collector = MetricsCollector()
collector.record_evaluation(eval_result)

print("✓ Migration test successful!")
```

## Phased Rollout Strategy

### Phase 1: Semantic Evaluation (Week 1)
- Enable reasoning evaluation with semantic-only approach
- No LLM setup required
- Low performance impact
- Validate concept detection accuracy

### Phase 2: Test with LLM (Week 2)
- Set up Ollama on test server
- Run sample evaluations
- Compare LLM vs semantic scores
- Tune weights if needed

### Phase 3: Production Deployment (Week 3+)
- Deploy Ollama to production
- Roll out to all evaluations
- Monitor performance and latency
- Collect feedback from users

## Verification Checklist

After migration:
- [ ] Database schema updated successfully
- [ ] New files present: `reasoning_evaluator.py`, `semantic_similarity.py`
- [ ] Base agent class has new methods
- [ ] Task classes have reference reasoning
- [ ] Configuration system updated
- [ ] Examples run successfully
- [ ] Old evaluations still work (backward compatibility)
- [ ] New scores visible in database
- [ ] Performance acceptable for your use case
- [ ] Documentation accessible and clear

## Getting Help

If you encounter issues:

1. **Check documentation**:
   - `docs/REASONING_EVALUATION_GUIDE.md` - Full guide
   - `docs/REASONING_EVALUATION_QUICKREF.md` - Quick reference
   - `docs/IMPLEMENTATION_SUMMARY.md` - Implementation details

2. **Run examples**:
   - `python examples/reasoning_evaluation_example.py`

3. **Test components individually**:
   - Semantic evaluator (no dependencies needed)
   - LLM evaluator with Ollama
   - Integration with existing code

4. **Review logs**:
   - Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
   - Check LLM provider output

## Success Criteria

Your migration is successful when:
- [x] All tests pass
- [x] Existing evaluations work unchanged
- [x] New reasoning scores appear in database
- [x] Performance is acceptable
- [x] Documentation is accessible
- [x] Team understands the new features

## Next Steps

After successful migration:
1. Gradually enable reasoning evaluation for tasks
2. Monitor evaluation quality and latency
3. Tune scoring weights for your use case
4. Collect feedback from evaluators
5. Consider task-specific customizations
6. Plan for continuous improvement

---

**Estimated migration time**: 30 minutes to 2 hours depending on setup choices

**Questions?** See the full guides in `docs/` directory
