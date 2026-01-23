# Triumvirate Quick Start Guide

## 5-Minute Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# 1. Install core dependencies
pip install temporalio sentence-transformers transformers torch spacy

# 2. Download spaCy model (optional, for NLP features)
python -m spacy download en_core_web_sm

# 3. Set environment variables (optional)
export CODEX_FULL_ENGINE=0     # Lightweight mode for quick testing
export MEMORY_SIZE=1000
```

### Quick Test

```bash
# Run the demo
python examples/triumvirate_demo.py

# Run tests
pytest tests/test_complete_system.py -v
```

## Basic Usage

### 1. Simple Processing

```python
from src.cognition.triumvirate import Triumvirate

# Initialize
triumvirate = Triumvirate()

# Process input
result = triumvirate.process("What is AI?")

print(f"Success: {result['success']}")
print(f"Output: {result['output']}")
```

### 2. Contradiction Detection

```python
from src.cognition.galahad.engine import GalahadEngine

engine = GalahadEngine()

# Detect contradictions
result = engine.reason([
    "System is secure",
    "System has vulnerabilities"
])

print(f"Contradictions: {len(result['contradictions'])}")
```

### 3. Semantic Memory

```python
from src.cognition.adapters.memory_adapter import MemoryAdapter

memory = MemoryAdapter()

# Add and search
memory.add_memory("Python is a programming language")
results = memory.search("coding", top_k=5)
```

### 4. Policy Enforcement

```python
from src.cognition.cerberus.engine import CerberusEngine

engine = CerberusEngine()  # Production mode (allow-all)

# Enforce policies
result = engine.enforce_output("Some output")
print(f"Allowed: {result['allowed']}")
```

## Temporal Workflows

### Start Temporal Server

```bash
# Option 1: Docker
docker run -p 7233:7233 temporalio/auto-setup:latest

# Option 2: Temporal CLI
temporal server start-dev
```

### Run Worker

```bash
export TEMPORAL_TASK_QUEUE=triumvirate-prod

python -m temporalio.worker \
    --task-queue triumvirate-prod \
    temporal.workflows.triumvirate_workflow.TriumvirateWorkflow \
    temporal.workflows.activities.run_triumvirate_pipeline
```

### Execute Workflow

```python
from temporalio.client import Client
from temporal.workflows.triumvirate_workflow import (
    TriumvirateRequest,
    TriumvirateWorkflow
)

# Connect and execute
client = await Client.connect("localhost:7233")

result = await client.execute_workflow(
    TriumvirateWorkflow.run,
    TriumvirateRequest(input_data="Process this"),
    id="my-workflow",
    task_queue="triumvirate-prod"
)

print(f"Result: {result.success}")
```

## Configuration

### Environment Variables

```bash
# Codex Engine
export CODEX_FULL_ENGINE=1              # Enable full ML engine
export CODEX_ENABLE_GPU=1               # Enable GPU
export CODEX_FALLBACK_CPU=1             # Fallback to CPU if GPU fails
export CODEX_MODEL_PATH=gpt2            # Model to load
export CODEX_DEVICE=auto                # auto/cuda/cpu
export CODEX_ADAPTER=auto               # auto/huggingface/pytorch/dummy

# Memory
export MEMORY_SIZE=10000                # Max memory records

# Temporal
export TEMPORAL_HOST=localhost:7233
export TEMPORAL_NAMESPACE=default
export TEMPORAL_TASK_QUEUE=triumvirate-prod
```

### Programmatic Configuration

```python
from src.cognition.triumvirate import Triumvirate, TriumvirateConfig
from src.cognition.codex.engine import CodexConfig
from src.cognition.galahad.engine import GalahadConfig
from src.cognition.cerberus.engine import CerberusConfig

# Configure each engine
codex_config = CodexConfig(
    enable_full_engine=True,
    enable_gpu=True,
    fallback_to_cpu=True
)

galahad_config = GalahadConfig(
    reasoning_depth=3,
    enable_curiosity=True,
    arbitration_strategy="weighted"
)

cerberus_config = CerberusConfig(
    mode="production",
    enforce_on_output=True
)

# Initialize with config
config = TriumvirateConfig(
    codex_config=codex_config,
    galahad_config=galahad_config,
    cerberus_config=cerberus_config,
    enable_telemetry=True
)

triumvirate = Triumvirate(config)
```

## Common Use Cases

### 1. Production API Endpoint

```python
from flask import Flask, request, jsonify
from src.cognition.triumvirate import Triumvirate

app = Flask(__name__)
triumvirate = Triumvirate()

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    result = triumvirate.process(
        input_data=data['input'],
        context={'user_id': data.get('user_id')}
    )
    return jsonify(result)
```

### 2. Batch Processing

```python
triumvirate = Triumvirate()

inputs = ["input1", "input2", "input3"]
results = []

for inp in inputs:
    result = triumvirate.process(inp)
    results.append(result)
    
# Check failures
failures = [r for r in results if not r['success']]
print(f"Failed: {len(failures)}/{len(inputs)}")
```

### 3. Monitoring and Telemetry

```python
triumvirate = Triumvirate()

# Process
triumvirate.process("input")

# Get telemetry
events = triumvirate.get_telemetry(limit=100)

# Analyze
for event in events:
    if event['event_type'] == 'error':
        print(f"Error: {event['payload']}")
```

## Troubleshooting

### Issue: GPU not available

```bash
# Solution: Use CPU mode
export CODEX_ENABLE_GPU=0
export CODEX_DEVICE=cpu
```

### Issue: Model loading fails

```bash
# Solution: Use lightweight mode
export CODEX_FULL_ENGINE=0
```

### Issue: Memory errors

```bash
# Solution: Reduce memory size
export MEMORY_SIZE=1000
```

### Issue: Import errors

```bash
# Solution: Check PYTHONPATH
export PYTHONPATH=/path/to/Project-AI:$PYTHONPATH
```

## Next Steps

1. Read full documentation: `TRIUMVIRATE_INTEGRATION.md`
1. Run demos: `python examples/triumvirate_demo.py`
1. Explore tests: `tests/test_complete_system.py`
1. Check API reference in documentation
1. Join community discussions

## Resources

- Full Documentation: `TRIUMVIRATE_INTEGRATION.md`
- Demo Scripts: `examples/triumvirate_demo.py`
- Test Suite: `tests/test_complete_system.py`
- Temporal Docs: <https://docs.temporal.io/>
- Project Repository: <https://github.com/IAmSoThirsty/Project-AI>

## Support

For issues:

1. Check documentation
1. Run tests to verify setup
1. Check environment variables
1. Create GitHub issue with details
