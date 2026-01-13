# Temporal.io Integration Setup Guide

## Overview

This guide covers the complete setup of Temporal.io workflow orchestration for Project-AI. This integration was originally developed in the **"Expert space waddle"** workspace and has been synced to this repository for team collaboration and production deployment.

## What is Temporal.io?

Temporal is a durable execution platform that guarantees workflow completion even in the face of failures, timeouts, or infrastructure issues. For Project-AI, Temporal provides:

- **Durable Execution**: Long-running AI operations (learning, image generation) continue reliably
- **Automatic Retries**: Failed activities retry automatically with configurable policies
- **Workflow Versioning**: Safe deployment of workflow changes without disrupting running instances
- **Distributed Coordination**: Multiple workers process tasks in parallel
- **Visibility**: Web UI for monitoring workflows and debugging issues

## Architecture

### Components

1. **Temporal Server**: Core orchestration engine (runs in Docker)
2. **PostgreSQL**: Persistence layer for workflow state
3. **Workers**: Python processes that execute workflows and activities
4. **Client**: Python code that starts workflows (integrated into Project-AI)

### Workflows

Project-AI includes four main workflows:

1. **AILearningWorkflow**: Handles learning requests with Black Vault checks and approval
2. **ImageGenerationWorkflow**: Orchestrates image generation with content filtering
3. **DataAnalysisWorkflow**: Manages data analysis pipeline from load to visualization
4. **MemoryExpansionWorkflow**: Processes conversations and extracts memories

### Activities

Each workflow is composed of atomic activities:

- **Learning Activities**: validate_learning_content, check_black_vault, process_learning_request, store_knowledge
- **Image Activities**: check_content_safety, generate_image, store_image_metadata
- **Data Activities**: validate_data_file, load_data, perform_analysis, generate_visualizations
- **Memory Activities**: extract_memory_information, store_memories, update_memory_indexes

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+
- Project-AI dependencies installed (see requirements.txt)

### Quick Start (Local Development)

1. **Initialize Temporal configuration**:
   ```bash
   python scripts/setup_temporal.py init
   ```

2. **Start Temporal server**:
   ```bash
   python scripts/setup_temporal.py start
   ```

   This starts:
   - Temporal server on `localhost:7233` (gRPC)
   - Temporal Web UI on `http://localhost:8233`
   - PostgreSQL database for persistence

3. **Start worker**:
   ```bash
   python scripts/setup_temporal.py worker
   ```

4. **Verify services**:
   ```bash
   python scripts/setup_temporal.py status
   ```

### Alternative: Docker Compose

Start all services together:

```bash
docker-compose up -d temporal temporal-postgresql temporal-worker
```

### Alternative: Standalone Worker

Run worker directly (for development):

```bash
cd src
PYTHONPATH=. python -m app.temporal.worker
```

## Configuration

### Environment Variables

Create `.env.temporal` file (copy from `.env.temporal.example`):

```bash
# Local Temporal Server
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=project-ai-tasks

# Worker Configuration
TEMPORAL_MAX_CONCURRENT_ACTIVITIES=50
TEMPORAL_MAX_CONCURRENT_WORKFLOWS=50

# Timeout Configuration (seconds)
TEMPORAL_WORKFLOW_EXECUTION_TIMEOUT=3600
TEMPORAL_ACTIVITY_START_TO_CLOSE_TIMEOUT=300
```

### Temporal Cloud (Production)

For Temporal Cloud deployment:

1. Sign up at https://temporal.io/cloud
2. Create a namespace (e.g., `project-ai.a2b3c`)
3. Download client certificates
4. Update `.env.temporal`:

```bash
TEMPORAL_CLOUD_NAMESPACE=project-ai.a2b3c
TEMPORAL_CLOUD_CERT_PATH=/path/to/client-cert.pem
TEMPORAL_CLOUD_KEY_PATH=/path/to/client-key.pem
```

5. Connect using cloud configuration:

```python
from app.temporal.client import TemporalClientManager

manager = await TemporalClientManager.create_cloud_client(
    namespace="project-ai.a2b3c",
    client_cert_path="/path/to/client-cert.pem",
    client_key_path="/path/to/client-key.pem",
)
```

## Usage Examples

### Starting a Workflow

```python
import asyncio
from app.temporal.client import TemporalClientManager
from app.temporal.workflows import (
    AILearningWorkflow,
    LearningRequest,
    LearningResult,
)

async def run_learning_workflow():
    # Connect to Temporal
    manager = TemporalClientManager()
    await manager.connect()
    
    # Start workflow
    handle = await manager.client.start_workflow(
        AILearningWorkflow.run,
        LearningRequest(
            content="Python best practices for error handling",
            source="documentation",
            category="programming",
            user_id="user123",
        ),
        id=f"learning-workflow-{timestamp}",
        task_queue="project-ai-tasks",
    )
    
    # Wait for result
    result: LearningResult = await handle.result()
    
    if result.success:
        print(f"Learning completed: {result.knowledge_id}")
    else:
        print(f"Learning failed: {result.error}")
    
    await manager.disconnect()

asyncio.run(run_learning_workflow())
```

### Querying Workflow Status

```python
# Get workflow handle
handle = manager.client.get_workflow_handle(
    workflow_id="learning-workflow-123"
)

# Query workflow state
result = await handle.result()

# Check if workflow is running
is_running = await handle.query("is_running")
```

### Canceling a Workflow

```python
handle = manager.client.get_workflow_handle(
    workflow_id="learning-workflow-123"
)

# Cancel the workflow
await handle.cancel()
```

## Monitoring

### Web UI

Access the Temporal Web UI at http://localhost:8233 to:

- View all workflows and their status
- See workflow history and events
- Debug failures with stack traces
- Monitor worker health

### Programmatic Monitoring

```python
# List workflows
async for workflow in manager.client.list_workflows():
    print(f"Workflow {workflow.id}: {workflow.status}")

# Get workflow history
handle = manager.client.get_workflow_handle("workflow-id")
async for event in handle.fetch_history():
    print(event)
```

## Troubleshooting

### Worker Not Processing Tasks

1. Check worker is running:
   ```bash
   docker-compose ps temporal-worker
   ```

2. Check worker logs:
   ```bash
   docker-compose logs -f temporal-worker
   ```

3. Verify task queue matches:
   - Worker: `TEMPORAL_TASK_QUEUE=project-ai-tasks`
   - Client: `task_queue="project-ai-tasks"`

### Connection Refused

1. Verify Temporal server is running:
   ```bash
   docker-compose ps temporal
   ```

2. Check server health:
   ```bash
   curl http://localhost:8233
   ```

3. Check server logs:
   ```bash
   docker-compose logs temporal
   ```

### Workflow Stuck

1. Check in Web UI for error details
2. Verify activities have appropriate timeouts
3. Check worker logs for activity failures
4. Use workflow history to identify stuck activity

### Database Issues

1. Check PostgreSQL is running:
   ```bash
   docker-compose ps temporal-postgresql
   ```

2. Reset database (⚠️ destroys all workflow data):
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

## Integration with Project-AI

### From GUI

The Leather Book interface can trigger workflows:

```python
# In dashboard_handlers.py
async def on_generate_image(self, prompt: str):
    manager = TemporalClientManager()
    await manager.connect()
    
    handle = await manager.client.start_workflow(
        ImageGenerationWorkflow.run,
        ImageGenerationRequest(
            prompt=prompt,
            style=self.style_selector.currentText(),
            backend="huggingface",
        ),
        id=f"image-gen-{datetime.now().timestamp()}",
        task_queue="project-ai-tasks",
    )
    
    result = await handle.result()
    if result.success:
        self.display_image(result.image_path)
```

### From CLI

```bash
# Start a workflow via CLI
python -c "
from app.temporal.workflows import AILearningWorkflow
import asyncio
# ... workflow code
"
```

## Performance Tuning

### Worker Configuration

Adjust concurrent task limits in `.env.temporal`:

```bash
# More parallel activities (for CPU-bound tasks)
TEMPORAL_MAX_CONCURRENT_ACTIVITIES=100

# More parallel workflows (for I/O-bound tasks)
TEMPORAL_MAX_CONCURRENT_WORKFLOWS=100
```

### Retry Policies

Customize retry behavior in workflow definitions:

```python
from temporalio.common import RetryPolicy

retry_policy = RetryPolicy(
    maximum_attempts=5,
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(minutes=2),
    backoff_coefficient=2.0,
)

result = await workflow.execute_activity(
    activity_name,
    args,
    retry_policy=retry_policy,
)
```

### Activity Timeouts

Configure activity timeouts based on expected duration:

```python
# Quick activities (< 1 minute)
start_to_close_timeout=timedelta(seconds=30)

# Medium activities (< 5 minutes)
start_to_close_timeout=timedelta(minutes=5)

# Long activities (image generation, data analysis)
start_to_close_timeout=timedelta(minutes=30)
```

## Migration from Workspace

This integration was developed in the **"Expert space waddle"** workspace and has been fully migrated to this repository. All workflow definitions, activities, configurations, and documentation are now version-controlled and reproducible.

## Next Steps

1. Review workflow definitions in `src/app/temporal/workflows.py`
2. Examine activity implementations in `src/app/temporal/activities.py`
3. Customize configuration in `.env.temporal`
4. Integrate workflows into your application code
5. Deploy to production using Temporal Cloud

## Resources

- [Temporal Documentation](https://docs.temporal.io/)
- [Python SDK Guide](https://docs.temporal.io/dev-guide/python)
- [Temporal Cloud](https://temporal.io/cloud)
- [Temporal Community](https://community.temporal.io/)

## Support

For issues specific to Project-AI's Temporal integration:
- Check troubleshooting section above
- Review logs: `docker-compose logs temporal-worker`
- Consult Temporal Web UI: http://localhost:8233
- Open a GitHub issue with logs and workflow ID
