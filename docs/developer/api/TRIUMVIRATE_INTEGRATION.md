# Triumvirate Production Integration

## Overview

This integration adds production-ready features to Project-AI through the Triumvirate architecture:

- **Codex Engine**: ML model inference with GPU/CPU fallback
- **Galahad Engine**: Reasoning and arbitration with curiosity metrics
- **Cerberus Engine**: Policy enforcement with allow-all production default
- **Semantic Memory**: SentenceTransformer-based vector search (>10k records)
- **Temporal Workflows**: Durable orchestration with configurable timeouts/retries
- **Telemetry System**: Event correlation IDs and rich payloads

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Triumvirate                          │
│                                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │ Cerberus│───▶│  Codex  │───▶│ Galahad │───▶Output  │
│  │ Validate│    │Inference│    │Reasoning│            │
│  └─────────┘    └─────────┘    └─────────┘            │
│       │                              │                  │
│       └──────────────────────────────┘                  │
│              Output Enforcement                         │
└─────────────────────────────────────────────────────────┘
```

## Installation

### 1. Install Dependencies

```bash
# Core dependencies
pip install temporalio sentence-transformers transformers torch spacy

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### 2. Environment Configuration

Create or update `.env` file:

```bash
# Codex Engine Configuration
export CODEX_FULL_ENGINE=1              # Enable full ML engine (0 for lightweight)
export CODEX_ENABLE_GPU=1               # Enable GPU support (0 for CPU only)
export CODEX_FALLBACK_CPU=1             # Fallback to CPU if GPU fails
export CODEX_MODEL_PATH=gpt2            # Model to load
export CODEX_DEVICE=auto                # Device selection (auto/cuda/cpu)
export CODEX_ADAPTER=auto               # Adapter type (auto/huggingface/pytorch/dummy)

# Memory Configuration
export MEMORY_SIZE=10000                # Maximum memory records

# Temporal Configuration
export TEMPORAL_HOST=localhost:7233     # Temporal server address
export TEMPORAL_NAMESPACE=default       # Temporal namespace
export TEMPORAL_TASK_QUEUE=triumvirate-prod  # Task queue name
```

### 3. Start Temporal Server (Optional for Development)

```bash
# Using Docker
docker run -p 7233:7233 temporalio/auto-setup:latest

# Or use Temporal Cloud (production)
# https://temporal.io/cloud
```

## Usage

### Direct Python API

```python
from src.cognition.triumvirate import Triumvirate

# Initialize
triumvirate = Triumvirate()

# Process input
result = triumvirate.process(
    input_data="What is machine learning?",
    context={"user_id": "user123"}
)

print(f"Success: {result['success']}")
print(f"Output: {result['output']}")
print(f"Correlation ID: {result['correlation_id']}")
```

### Temporal Workflow

```python
from temporalio.client import Client
from temporal.workflows.triumvirate_workflow import (
    TriumvirateRequest,
    TriumvirateWorkflow
)

# Connect to Temporal
client = await Client.connect("localhost:7233")

# Execute workflow
result = await client.execute_workflow(
    TriumvirateWorkflow.run,
    TriumvirateRequest(
        input_data="Process this input",
        timeout_seconds=300,
        max_retries=3
    ),
    id="triumvirate-workflow-1",
    task_queue="triumvirate-prod"
)
```

## Running the Temporal Worker

### Option 1: Using temporalio CLI

```bash
python -m temporalio.worker \
    --task-queue triumvirate-prod \
    temporal.workflows.triumvirate_workflow.TriumvirateWorkflow \
    temporal.workflows.activities.run_triumvirate_pipeline
```

### Option 2: Custom Worker Script

Create `worker.py`:

```python
import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from temporal.workflows.triumvirate_workflow import (
    TriumvirateWorkflow,
    TriumvirateStepWorkflow
)
from temporal.workflows import activities

async def main():
    client = await Client.connect("localhost:7233")
    
    worker = Worker(
        client,
        task_queue="triumvirate-prod",
        workflows=[TriumvirateWorkflow, TriumvirateStepWorkflow],
        activities=[
            activities.run_triumvirate_pipeline,
            activities.validate_input_activity,
            activities.run_codex_inference,
            activities.run_galahad_reasoning,
            activities.enforce_output_policy,
            activities.record_telemetry,
        ]
    )
    
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
```

Run with:

```bash
python worker.py
```

## Testing

Run the complete test suite:

```bash
# All tests
pytest tests/test_complete_system.py -v

# Specific test categories
pytest tests/test_complete_system.py::TestModelAdapter -v
pytest tests/test_complete_system.py::TestMemoryAdapter -v
pytest tests/test_complete_system.py::TestTriumvirate -v

# Test contradiction detection
pytest tests/test_complete_system.py::test_contradiction_detection_e2e -v

# Test full integration
pytest tests/test_complete_system.py::test_full_system_integration -v
```

## Component Details

### Codex Engine

**Features:**

- GPU/CPU automatic detection and fallback
- Model loading error handling
- Environment-based configuration
- Graceful degradation in lightweight mode

**Configuration:**
```python
from src.cognition.codex.engine import CodexConfig, CodexEngine

config = CodexConfig(
    model_path="gpt2",
    device="auto",
    enable_gpu=True,
    enable_full_engine=True,
    fallback_to_cpu=True
)

engine = CodexEngine(config)
```

### Galahad Engine

**Features:**

- Multi-input reasoning
- Contradiction detection
- Arbitration strategies (weighted, majority, unanimous)
- Curiosity metrics for exploration
- Explanation generation

**Example:**
```python
from src.cognition.galahad.engine import GalahadEngine

engine = GalahadEngine()

# Detect contradictions
result = engine.reason(["yes", "no"])
print(f"Contradictions: {result['contradictions']}")
print(f"Explanation: {result['explanation']}")
```

### Cerberus Engine

**Features:**

- Configurable policy modes (production, strict, custom)
- Pre-persistence validation
- Output enforcement
- Policy statistics tracking

**Example:**
```python
from src.cognition.cerberus.engine import CerberusEngine, CerberusConfig

config = CerberusConfig(mode="production")
engine = CerberusEngine(config)

# Enforce output
result = engine.enforce_output("Some output data")
print(f"Allowed: {result['allowed']}")
```

### Semantic Memory

**Features:**

- SentenceTransformer embeddings
- Efficient vector similarity search
- Scalable to >10k records
- Automatic persistence

**Example:**
```python
from src.cognition.adapters.memory_adapter import MemoryAdapter

memory = MemoryAdapter(max_records=10000)

# Add memories
memory.add_memory("Python is a programming language")
memory.add_memory("Machine learning uses neural networks")

# Search
results = memory.search("coding", top_k=5)
for result in results:
    print(f"[{result['similarity']:.2f}] {result['content']}")
```

## Production Deployment

### Recommended Environment Variables

```bash
# Production
export CODEX_FULL_ENGINE=1
export CODEX_ENABLE_GPU=1
export CODEX_FALLBACK_CPU=1
export MEMORY_SIZE=50000
export TEMPORAL_TASK_QUEUE=triumvirate-prod

# Development
export CODEX_FULL_ENGINE=0
export CODEX_ENABLE_GPU=0
export MEMORY_SIZE=1000
export TEMPORAL_TASK_QUEUE=triumvirate-dev
```

### Monitoring

Access telemetry events:

```python
triumvirate = Triumvirate()
triumvirate.process("input")

# Get telemetry
events = triumvirate.get_telemetry(limit=100)
for event in events:
    print(f"{event['timestamp']}: {event['event_type']}")
```

### Scaling

- **Horizontal**: Run multiple Temporal workers
- **Vertical**: Increase worker resources (GPU memory, CPU cores)
- **Memory**: Adjust `MEMORY_SIZE` based on available RAM
- **Temporal**: Use Temporal Cloud for managed scaling

## Troubleshooting

### GPU Not Available

```bash
# Force CPU mode
export CODEX_ENABLE_GPU=0
export CODEX_DEVICE=cpu
```

### Model Loading Fails

```bash
# Use lightweight mode
export CODEX_FULL_ENGINE=0

# Or specify different model
export CODEX_MODEL_PATH=distilgpt2
```

### Memory Issues

```bash
# Reduce memory size
export MEMORY_SIZE=1000
```

### Temporal Connection Issues

```bash
# Check Temporal server
export TEMPORAL_HOST=localhost:7233

# Verify server is running
docker ps | grep temporal
```

## API Reference

### Triumvirate.process()

```python
def process(
    self,
    input_data: Any,
    context: dict | None = None,
    skip_validation: bool = False
) -> dict
```

**Returns:**
```python
{
    "success": bool,
    "output": Any,
    "correlation_id": str,
    "duration_ms": float,
    "pipeline": {
        "validation": dict,
        "codex": dict,
        "galahad": dict,
        "cerberus": dict
    },
    "metadata": dict
}
```

## License

Same as Project-AI (MIT)

## Support

For issues, please create a GitHub issue with:

- Environment details (OS, Python version, GPU)
- Configuration (env vars)
- Error messages and logs
- Steps to reproduce
