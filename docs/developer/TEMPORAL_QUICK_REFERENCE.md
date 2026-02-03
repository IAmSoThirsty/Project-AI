# Temporal Integration Quick Reference

Quick reference guide for using the Temporal integration in Project-AI.

## 🚀 Quick Start (30 seconds)

```bash
# 1. Start Temporal server
docker-compose up -d temporal temporal-postgresql

# 2. Start worker (in another terminal)
cd /path/to/Project-AI
export PYTHONPATH=/path/to/Project-AI/src
python -m integrations.temporal.worker

# 3. Run a workflow (in Python)
from app.service.ai_controller import process_ai_request
result = await process_ai_request("Your input here")
```

## 📖 Common Tasks

### Start a Workflow

```python
from app.service.ai_controller import AIController

controller = AIController()
result = await controller.process_ai_request(
    data="Process this data",
    user_id="user123"
)
print(f"Success: {result.success}")
```

### Check Workflow Status

```python
status = await controller.get_workflow_status("workflow-id-123")
print(f"Status: {status['status']}")
```

### Run Worker Locally

```bash
export TEMPORAL_HOST=localhost:7233
python -m integrations.temporal.worker
```

### View Workflows in Web UI

Open browser: http://localhost:8233

## 🔧 Configuration

### Environment Variables

```bash
# .env file
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=project-ai-tasks
```

### Custom Configuration

```python
from integrations.temporal.client import TemporalClient

client = TemporalClient(
    host="custom-host:7233",
    namespace="custom-namespace",
    task_queue="custom-queue"
)
```

## 📝 Code Examples

### Example 1: Simple Request

```python
import asyncio
from app.service.ai_controller import process_ai_request

async def main():
    result = await process_ai_request("Explain AI")
    print(result.result if result.success else result.error)

asyncio.run(main())
```

### Example 2: With User Context

```python
from app.service.ai_controller import AIController

async def process_user_request(user_id: str, data: str):
    controller = AIController()
    try:
        result = await controller.process_ai_request(
            data=data,
            user_id=user_id,
            workflow_id=f"user-{user_id}-request"
        )
        return result
    finally:
        await controller.close()
```

### Example 3: Direct Workflow Usage

```python
from integrations.temporal.client import TemporalClient
from integrations.temporal.workflows.example_workflow import (
    ExampleWorkflow,
    WorkflowInput
)

async def main():
    async with TemporalClient() as client:
        handle = await client.start_workflow(
            workflow=ExampleWorkflow.run,
            args=WorkflowInput(data="test", user_id="user123"),
            workflow_id="my-workflow-123"
        )
        result = await handle.result()
        print(result)
```

## 🎯 Creating Custom Workflows

### Step 1: Define Workflow

```python
# src/integrations/temporal/workflows/my_workflow.py
from dataclasses import dataclass
from datetime import timedelta
from temporalio import workflow

@dataclass
class MyInput:
    data: str

@dataclass
class MyOutput:
    success: bool
    result: str

@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self, input_data: MyInput) -> MyOutput:
        # Your workflow logic
        result = await workflow.execute_activity(
            my_activity,
            input_data.data,
            start_to_close_timeout=timedelta(seconds=30)
        )
        return MyOutput(success=True, result=result)
```

### Step 2: Define Activities

```python
# src/integrations/temporal/activities/my_activities.py
from temporalio import activity

@activity.defn
async def my_activity(data: str) -> str:
    activity.logger.info(f"Processing: {data}")
    # Your activity logic
    return f"Processed: {data}"
```

### Step 3: Register in Worker

```python
# In worker.py, add to imports
from integrations.temporal.workflows.my_workflow import MyWorkflow
from integrations.temporal.activities.my_activities import my_activity

# In worker = Worker(...), add:
worker = Worker(
    client,
    task_queue=task_queue,
    workflows=[ExampleWorkflow, MyWorkflow],  # Add here
    activities=[validate_input, simulate_ai_call, my_activity],  # Add here
)
```

### Step 4: Use in AI Controller

```python
# Add method to ai_controller.py
async def my_custom_operation(self, data: str):
    handle = await self.temporal_client.start_workflow(
        workflow=MyWorkflow.run,
        args=MyInput(data=data),
        workflow_id=f"custom-{uuid.uuid4().hex[:8]}"
    )
    return await handle.result()
```

## 🔍 Debugging

### Check Server Status

```bash
docker-compose ps temporal
```

### View Worker Logs

```bash
docker-compose logs -f temporal-worker
```

### Check Activity Execution

```bash
# In Web UI at http://localhost:8233
# 1. Find your workflow
# 2. Click on it
# 3. View Event History
# 4. Inspect activity start/complete events
```

### Test Activity Locally

```python
import asyncio
from integrations.temporal.activities.core_tasks import validate_input

async def test():
    result = await validate_input("test data")
    print(f"Valid: {result}")

asyncio.run(test())
```

## 🐛 Troubleshooting

### Worker Not Starting

```bash
# Check if Temporal server is running
docker-compose ps temporal

# Check worker logs
docker-compose logs temporal-worker

# Verify PYTHONPATH
echo $PYTHONPATH
# Should include /path/to/Project-AI/src
```

### Workflow Not Executing

1. Verify worker is running: `docker-compose logs temporal-worker`
1. Check task queue matches: Worker and client must use same queue
1. Check Web UI for errors: http://localhost:8233

### Connection Refused

```bash
# Ensure Temporal is running
docker-compose up -d temporal

# Wait for it to be healthy
docker-compose ps temporal
# Should show "healthy" status
```

### Import Errors

```bash
# Set PYTHONPATH correctly
export PYTHONPATH=/path/to/Project-AI/src

# Or use absolute imports in Python
import sys
sys.path.insert(0, '/path/to/Project-AI/src')
```

## 📚 File Structure Reference

```
src/integrations/temporal/
├── __init__.py              # Module exports
├── client.py                # Temporal client wrapper
├── worker.py                # Worker entrypoint
├── workflows/
│   ├── __init__.py
│   └── example_workflow.py  # Example workflow
└── activities/
    ├── __init__.py
    └── core_tasks.py        # Core activities

src/app/service/
└── ai_controller.py         # High-level AI service

examples/
└── temporal_integration_demo.py  # Demo script

tests/
└── test_temporal_integration.py  # Integration tests

docs/
└── TEMPORAL_INTEGRATION_ARCHITECTURE.md  # Architecture docs
```

## 🔗 Resources

- **README.md**: Full Temporal integration guide
- **Architecture Doc**: `docs/TEMPORAL_INTEGRATION_ARCHITECTURE.md`
- **Demo Script**: `examples/temporal_integration_demo.py`
- **Tests**: `tests/test_temporal_integration.py`
- **Temporal Docs**: https://docs.temporal.io/docs/python
- **Samples**: https://github.com/temporalio/samples-python

## 💡 Tips & Best Practices

1. **Always use context managers** for clients:

   ```python
   async with TemporalClient() as client:
       # Use client
   ```

1. **Use unique workflow IDs** for idempotency:

   ```python
   workflow_id = f"user-{user_id}-{uuid.uuid4().hex[:8]}"
   ```

1. **Set appropriate timeouts** for activities:

   ```python
   start_to_close_timeout=timedelta(seconds=30)
   ```

1. **Use retry policies** for resilience:

   ```python
   retry_policy=RetryPolicy(
       initial_interval=timedelta(seconds=1),
       maximum_attempts=3
   )
   ```

1. **Log at each step** for debugging:

   ```python
   workflow.logger.info("Starting step 1...")
   activity.logger.info("Processing data...")
   ```

1. **Test activities independently** before workflows:

   ```python
   result = await validate_input("test")
   assert result is True
   ```

1. **Monitor the Web UI** during development:
   - http://localhost:8233
   - Inspect event history
   - Check activity retries
   - Debug failures

## 🎓 Learning Path

1. **Start with the demo**: Run `examples/temporal_integration_demo.py`
1. **Read the architecture**: `docs/TEMPORAL_INTEGRATION_ARCHITECTURE.md`
1. **Run the tests**: `pytest tests/test_temporal_integration.py -v`
1. **Modify example workflow**: Change `example_workflow.py`
1. **Create custom workflow**: Follow the guide above
1. **Integrate with your code**: Use `AIController`

## 🚨 Common Pitfalls

1. ❌ Forgetting to start worker → Workflows never execute
1. ❌ Wrong PYTHONPATH → Import errors
1. ❌ Mismatched task queue → Worker doesn't pick up work
1. ❌ Not waiting for Temporal to be healthy → Connection errors
1. ❌ Using blocking code in workflows → Workflows hang
1. ❌ Not setting timeouts → Activities run forever
1. ❌ Sharing mutable state → Non-deterministic workflows

## 📞 Getting Help

1. Check the Web UI: http://localhost:8233
1. View logs: `docker-compose logs temporal-worker`
1. Read the architecture doc: `docs/TEMPORAL_INTEGRATION_ARCHITECTURE.md`
1. Run the demo: `python examples/temporal_integration_demo.py`
1. Check tests: `pytest tests/test_temporal_integration.py -v`
1. Temporal docs: https://docs.temporal.io/docs/python
