# Temporal.io Workflow Examples

This directory contains example scripts demonstrating how to use Temporal.io workflows in Project-AI.

## Prerequisites

1. Start Temporal server:

   ```bash
   python scripts/setup_temporal.py start
   ```

1. Start Temporal worker:

   ```bash
   python scripts/setup_temporal.py worker
   ```

## Examples

### 1. Learning Workflow (`learning_workflow_example.py`)

Demonstrates the AI learning workflow with content validation and Black Vault checks.

```bash
cd /path/to/Project-AI
PYTHONPATH=src python examples/temporal/learning_workflow_example.py
```

**Features:**

- Content validation
- Black Vault filtering
- Knowledge extraction and storage
- Durable execution (survives crashes)

### 2. Image Generation (`image_generation_example.py`)

Shows how to generate images with automatic retries and content filtering.

```bash
PYTHONPATH=src python examples/temporal/image_generation_example.py
```

**Features:**

- Content safety checks
- Automatic retries on failure
- Long-running task support (10+ minutes)
- Metadata tracking

### 3. Batch Workflows (`batch_workflows_example.py`)

Demonstrates running multiple workflows in parallel for batch processing.

```bash
PYTHONPATH=src python examples/temporal/batch_workflows_example.py
```

**Features:**

- Parallel workflow execution
- Aggregated results
- Efficient resource utilization

## Monitoring

View workflow execution in the Temporal Web UI:

- **URL**: http://localhost:8233
- **Namespace**: default
- **Task Queue**: project-ai-tasks

## Troubleshooting

### Worker not processing tasks

Check that the worker is running:
```bash
docker-compose logs temporal-worker
```

### Connection refused

Verify Temporal server is running:
```bash
docker-compose ps temporal
```

### Example fails immediately

Ensure PYTHONPATH includes `src`:
```bash
export PYTHONPATH=src
```

## Creating Your Own Workflows

1. Define workflow in `src/app/temporal/workflows.py`
1. Implement activities in `src/app/temporal/activities.py`
1. Register in worker (`src/app/temporal/worker.py`)
1. Create client code following the examples above

See `docs/TEMPORAL_SETUP.md` for detailed documentation.
