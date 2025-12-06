# System Requirements & Verification

## Prerequisites

### Python
- **Required**: Python 3.11 or higher
- **Recommended**: Python 3.11+ with virtual environment

```bash
python --version  # Should output 3.11.x or higher
```

### Operating System
- **Supported**: Linux, macOS, Windows (with PowerShell or WSL)
- **Storage**: 500MB minimum for dependencies
- **RAM**: 4GB minimum (8GB+ recommended for LLM models)

## Installation Instructions

### 1. Update Python Packages

```bash
# Update pip
python -m pip install --upgrade pip

# Install required dependencies
pip install requests>=2.31.0

# Install optional dependencies
pip install sentence-transformers torch
```

### 2. Optional: Install Ollama

**macOS**:
```bash
brew install ollama
brew services start ollama  # Auto-start on login
```

**Linux**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
systemctl --user start ollama  # Start service
```

**Windows**:
```
Download installer from https://ollama.ai
Run the installer
ollama serve  # Start in terminal
```

### 3. Pull LLM Model (Ollama only)

```bash
# In another terminal
ollama pull neural-chat    # Recommended (4GB, fast)
# or
ollama pull mistral        # Alternative (5GB, better quality)
# or
ollama pull llama2         # Alternative (7GB, most capable)
```

## Verification Steps

### Verify Python Installation

```bash
python -c "
import sys
print(f'✓ Python {sys.version}')
print(f'✓ Executable: {sys.executable}')

import sqlite3
print('✓ sqlite3 available')

import json
print('✓ json available')
"
```

### Verify MechGAIA Installation

```bash
python -c "
from green_agents.level1_stress_task import Level1StressTask
print('✓ Level1 task available')

from green_agents.level2_shaft_design_task import Level2ShaftDesignTask
print('✓ Level2 task available')

from green_agents.level3_plate_optimization_task import Level3PlateOptimizationTask
print('✓ Level3 task available')
"
```

### Verify Reasoning Evaluator

```bash
python -c "
from utils.reasoning_evaluator import get_reasoning_evaluator
evaluator = get_reasoning_evaluator()
print(f'✓ Reasoning evaluator available')
print(f'  Provider: {evaluator.provider}')
print(f'  Model: {evaluator.model}')
print(f'  Enabled: {evaluator.enabled}')
"
```

### Verify Semantic Evaluator

```bash
python -c "
from utils.semantic_similarity import get_semantic_evaluator
evaluator = get_semantic_evaluator()
print('✓ Semantic evaluator available')
print(f'  Using embeddings: {evaluator.use_embeddings}')
"
```

### Verify Configuration System

```bash
python -c "
from config.llm_config import get_config
config = get_config()
print('✓ Configuration system available')
rc = config.get_reasoning_eval_config()
print(f'  Provider: {rc.get(\"provider\", \"not configured\")}')
print(f'  Enabled: {rc.get(\"enabled\", False)}')
"
```

### Verify Database

```bash
python -c "
from metrics_system import MetricsCollector
collector = MetricsCollector()
print('✓ Metrics system available')
"
```

## Provider-Specific Verification

### Ollama Verification

```bash
# Check if Ollama is running
curl -s http://localhost:11434/api/status

# Expected output should be successful (no error)

# Check model availability
curl -s http://localhost:11434/api/tags

# Should show: neural-chat or other models
```

### OpenAI Verification

```bash
python -c "
import os
api_key = os.getenv('REASONING_EVAL_API_KEY')
if not api_key:
    print('✗ REASONING_EVAL_API_KEY not set')
else:
    print(f'✓ API key configured: {api_key[:20]}...')
    
try:
    from openai import OpenAI
    print('✓ OpenAI library available')
except ImportError:
    print('✗ OpenAI library not installed: pip install openai')
"
```

### Anthropic Verification

```bash
python -c "
import os
api_key = os.getenv('REASONING_EVAL_API_KEY')
if not api_key:
    print('✗ REASONING_EVAL_API_KEY not set')
else:
    print(f'✓ API key configured: {api_key[:20]}...')

try:
    from anthropic import Anthropic
    print('✓ Anthropic library available')
except ImportError:
    print('✗ Anthropic library not installed: pip install anthropic')
"
```

## Full System Verification Script

Save this as `verify_system.py`:

```python
#!/usr/bin/env python3
"""Complete system verification for MechGAIA reasoning evaluation."""

import sys
import os
from pathlib import Path

def check_python_version():
    """Verify Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"✗ Python {version.major}.{version.minor} is too old (need 3.11+)")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_imports():
    """Verify all required imports."""
    required = [
        ('json', 'JSON support'),
        ('sqlite3', 'SQLite database'),
        ('requests', 'HTTP library'),
    ]
    
    optional = [
        ('torch', 'PyTorch (for embeddings)'),
        ('sentence_transformers', 'Sentence transformers (for embeddings)'),
        ('openai', 'OpenAI library'),
        ('anthropic', 'Anthropic library'),
    ]
    
    print("\nRequired modules:")
    all_ok = True
    for module_name, description in required:
        try:
            __import__(module_name)
            print(f"  ✓ {description}")
        except ImportError:
            print(f"  ✗ {module_name} not found: pip install {module_name}")
            all_ok = False
    
    print("\nOptional modules:")
    for module_name, description in optional:
        try:
            __import__(module_name)
            print(f"  ✓ {description}")
        except ImportError:
            print(f"  ○ {module_name} not found (optional)")
    
    return all_ok

def check_mechgaia_modules():
    """Verify MechGAIA modules."""
    modules = [
        ('green_agents.level1_stress_task', 'Level1StressTask'),
        ('green_agents.level2_shaft_design_task', 'Level2ShaftDesignTask'),
        ('green_agents.level3_plate_optimization_task', 'Level3PlateOptimizationTask'),
        ('utils.reasoning_evaluator', 'ReasoningEvaluator'),
        ('utils.semantic_similarity', 'SemanticSimilarityEvaluator'),
        ('metrics_system', 'MetricsCollector'),
        ('config.llm_config', 'LLMConfig'),
    ]
    
    print("\nMechGAIA modules:")
    all_ok = True
    for module_name, class_name in modules:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✓ {module_name}.{class_name}")
        except (ImportError, AttributeError) as e:
            print(f"  ✗ {module_name}.{class_name}: {e}")
            all_ok = False
    
    return all_ok

def check_configuration():
    """Verify configuration system."""
    try:
        from config.llm_config import get_config
        config = get_config()
        
        print("\nConfiguration:")
        rc = config.get_reasoning_eval_config()
        print(f"  Enabled: {rc.get('enabled', 'not set')}")
        print(f"  Provider: {rc.get('provider', 'not set')}")
        print(f"  Model: {rc.get('model', 'not set')}")
        
        # Check environment overrides
        if os.getenv('REASONING_EVAL_ENABLED'):
            print(f"  [ENV] REASONING_EVAL_ENABLED={os.getenv('REASONING_EVAL_ENABLED')}")
        if os.getenv('REASONING_EVAL_PROVIDER'):
            print(f"  [ENV] REASONING_EVAL_PROVIDER={os.getenv('REASONING_EVAL_PROVIDER')}")
        
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False

def check_ollama():
    """Check Ollama connection if Ollama provider is configured."""
    try:
        import requests
        from config.llm_config import get_config
        
        config = get_config()
        rc = config.get_reasoning_eval_config()
        
        if rc.get('provider') != 'ollama':
            print("\nOllama:")
            print("  ○ Not configured (using different provider)")
            return True
        
        url = f"{rc.get('base_url', 'http://localhost:11434')}/api/status"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            print("\nOllama:")
            print(f"  ✓ Running at {rc.get('base_url')}")
            
            # Check model
            tags_url = f"{rc.get('base_url')}/api/tags"
            tags_response = requests.get(tags_url, timeout=2)
            if tags_response.status_code == 200:
                models = tags_response.json().get('models', [])
                print(f"  ✓ {len(models)} models available")
                for model in models[:3]:
                    print(f"    - {model.get('name', 'unknown')}")
            return True
        else:
            print("\nOllama:")
            print(f"  ✗ HTTP {response.status_code}")
            return False
    except requests.ConnectionError:
        print("\nOllama:")
        print("  ✗ Connection refused at http://localhost:11434")
        print("     Start Ollama: ollama serve")
        return False
    except Exception as e:
        print("\nOllama:")
        print(f"  ✗ Error: {e}")
        return False

def check_database():
    """Verify database and schema."""
    try:
        import sqlite3
        
        if not Path('mechgaia_metrics.db').exists():
            print("\nDatabase:")
            print("  ○ mechgaia_metrics.db not found (will be created on first evaluation)")
            return True
        
        conn = sqlite3.connect('mechgaia_metrics.db')
        cursor = conn.cursor()
        
        # Check schema
        cursor.execute("PRAGMA table_info(evaluations)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        
        required_cols = ['final_score', 'numerical_score', 'reasoning_score']
        missing = [c for c in required_cols if c not in columns]
        
        print("\nDatabase:")
        print(f"  ✓ mechgaia_metrics.db exists")
        
        if missing:
            print(f"  ⚠ Missing columns: {missing}")
            print(f"    Run migration script to add columns")
            return False
        else:
            print(f"  ✓ Schema updated with reasoning scores")
            return True
            
    except Exception as e:
        print("\nDatabase:")
        print(f"  ✗ Error: {e}")
        return False

def main():
    """Run all verification checks."""
    print("=" * 60)
    print("MechGAIA Reasoning Evaluation - System Verification")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Modules", check_imports),
        ("MechGAIA Modules", check_mechgaia_modules),
        ("Configuration", check_configuration),
        ("Ollama (if configured)", check_ollama),
        ("Database", check_database),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\nError in {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ System is ready for reasoning evaluation!")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

Run verification:
```bash
python verify_system.py
```

## Troubleshooting

### Issue: Import errors
```
ModuleNotFoundError: No module named 'requests'
```
**Solution**: `pip install requests>=2.31.0`

### Issue: Ollama not responding
```
requests.exceptions.ConnectionError: [Errno 111] Connection refused
```
**Solution**: Start Ollama: `ollama serve`

### Issue: Model not found
```
Error: model not found
```
**Solution**: Pull model: `ollama pull neural-chat`

### Issue: Database locked
```
sqlite3.OperationalError: database is locked
```
**Solution**: Close all connections and try again

### Issue: Out of memory
```
torch.cuda.OutOfMemoryError
```
**Solution**: Use smaller model or reduce batch size

## Performance Tuning

### For Faster Evaluation
```bash
export REASONING_EVAL_PROVIDER=semantic  # Use semantic-only
export REASONING_EVAL_MODEL=neural-chat  # Smaller model
export REASONING_EVAL_MAX_TOKENS=300     # Shorter responses
```

### For Better Quality
```bash
export REASONING_EVAL_PROVIDER=ollama
export REASONING_EVAL_MODEL=mistral      # More capable model
export REASONING_EVAL_TEMPERATURE=0.3    # More consistent
```

### For Cost Optimization (OpenAI)
```bash
export REASONING_EVAL_MODEL=gpt-3.5-turbo  # Cheaper than gpt-4
export REASONING_EVAL_MAX_TOKENS=300       # Shorter responses
```

## Support

- **Documentation**: See `docs/` directory
- **Examples**: Run `python examples/reasoning_evaluation_example.py`
- **Quick Reference**: `docs/REASONING_EVALUATION_QUICKREF.md`
- **Full Guide**: `docs/REASONING_EVALUATION_GUIDE.md`

## Success Indicators

You're ready to use reasoning evaluation when:
- ✓ All verification checks pass
- ✓ Python 3.11+ installed
- ✓ Required modules importable
- ✓ MechGAIA modules loadable
- ✓ (Optional) Ollama running and models available
- ✓ Database schema updated
- ✓ Configuration accessible
