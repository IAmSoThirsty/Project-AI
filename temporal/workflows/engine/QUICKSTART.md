# Workflow Orchestration Engine - Quick Start Guide

## Installation

The workflow orchestration engine is located in `temporal/workflows/engine/`.

```python
from temporal.workflows.engine import (
    WorkflowEngine,
    WorkflowDefinition,
    DAG,
    DAGNode,
    RetryPolicy,
    RecoveryStrategy,
    ConditionalLogic,
    # ... other imports
)
```

## 5-Minute Quick Start

### 1. Define Your Tasks

```python
async def task_a(context, metadata):
    """Your first task"""
    return {"status": "completed", "data": "result from A"}

async def task_b(context, metadata):
    """Your second task"""
    # Access results from previous tasks via context
    return {"status": "completed", "data": "result from B"}
```

### 2. Create a Workflow

```python
from temporal.workflows.engine import WorkflowEngine, WorkflowDefinition, DAG, DAGNode

# Create DAG
dag = DAG(name="my_workflow")

# Add nodes
dag.add_node(DAGNode(id="task_a", task=task_a))
dag.add_node(DAGNode(id="task_b", task=task_b, dependencies=["task_a"]))

# Create workflow definition
workflow_def = WorkflowDefinition(
    name="my_workflow",
    dag=dag,
    description="My first workflow",
)

# Execute
engine = WorkflowEngine()
execution = await engine.execute(workflow_def, {"input": "data"})

print(f"Status: {execution.status}")
print(f"Result: {execution.result}")
```

### 3. Add Retry Logic

```python
from temporal.workflows.engine import RetryPolicy, BackoffStrategy

workflow_def = WorkflowDefinition(
    name="my_workflow",
    dag=dag,
    retry_policies={
        "task_a": RetryPolicy(
            max_attempts=3,
            initial_interval_ms=1000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
        ),
    },
)
```

### 4. Add Failure Recovery

```python
from temporal.workflows.engine import RecoveryStrategy, RecoveryAction

workflow_def = WorkflowDefinition(
    name="my_workflow",
    dag=dag,
    recovery_strategies={
        "task_a": RecoveryStrategy(
            name="skip_on_failure",
            action=RecoveryAction.SKIP,
        ),
    },
)
```

### 5. Add Conditional Logic

```python
from temporal.workflows.engine import (
    Condition,
    ConditionalBranch,
    ConditionalLogic,
    ConditionOperator,
)

workflow_def = WorkflowDefinition(
    name="my_workflow",
    dag=dag,
    conditional_logic={
        "decision_task": ConditionalLogic(
            branches=[
                ConditionalBranch(
                    condition=Condition(
                        operator=ConditionOperator.GT,
                        left="$score",
                        right=80,
                    ),
                    action="high_score_path",
                ),
            ],
            default_action="low_score_path",
        ),
    },
)
```

## Pre-Built Example Workflows

### Use Case 1: CI/CD Pipeline

```python
from temporal.workflows.engine.examples import create_build_pipeline

workflow_def = create_build_pipeline()
engine = WorkflowEngine()

context = {
    "branch": "main",
    "run_tests": True,
    "publish_to": "production",
}

execution = await engine.execute(workflow_def, context)
```

**What it does:**
- Checks out code
- Installs dependencies (with retry)
- Compiles code
- Runs unit & integration tests in parallel
- Builds Docker image
- Publishes artifacts
- Sends notifications

### Use Case 2: Security Scanning

```python
from temporal.workflows.engine.examples import create_security_scan_workflow

workflow_def = create_security_scan_workflow()
engine = WorkflowEngine()

context = {
    "target": "myapp:latest",
    "auto_remediate_enabled": True,
    "severity_threshold": "high",
}

execution = await engine.execute(workflow_def, context)
```

**What it does:**
- Runs 5 parallel scans (SAST, DAST, dependency, container, license)
- Aggregates vulnerabilities
- Conditionally runs auto-remediation
- Generates security report

### Use Case 3: Blue-Green Deployment

```python
from temporal.workflows.engine.examples import create_deployment_workflow

workflow_def = create_deployment_workflow()
engine = WorkflowEngine()

context = {
    "environment": "production",
    "version": "1.2.0",
    "previous_version": "1.1.0",
}

execution = await engine.execute(workflow_def, context)
```

**What it does:**
- Validates prerequisites
- Backs up database
- Runs migrations
- Deploys to blue environment
- Health checks & smoke tests
- Conditionally switches traffic
- Monitors metrics
- Rolls back if needed

## Common Patterns

### Pattern 1: Parallel Execution

```python
# Create tasks with no dependencies to run in parallel
dag = DAG(name="parallel_workflow")

for i in range(5):
    dag.add_node(DAGNode(
        id=f"parallel_task_{i}",
        task=my_task,
        metadata={"index": i},
    ))

# Add a final aggregation task
dag.add_node(DAGNode(
    id="aggregate",
    task=aggregate_results,
    dependencies=[f"parallel_task_{i}" for i in range(5)],
))
```

### Pattern 2: Error Handling

```python
async def compensating_action(context):
    """Undo changes made by failed task"""
    # Restore database, cleanup resources, etc.
    return {"compensated": True}

recovery_strategies = {
    "critical_task": RecoveryStrategy(
        name="compensate_on_failure",
        action=RecoveryAction.COMPENSATE,
        compensating_action=compensating_action,
    ),
}
```

### Pattern 3: Circuit Breaker

```python
from temporal.workflows.engine import CircuitBreaker

circuit_breakers = {
    "external_api_task": CircuitBreaker(
        failure_threshold=5,      # Open after 5 failures
        success_threshold=2,      # Close after 2 successes
        timeout_seconds=60,       # Wait 60s before retry
    ),
}

workflow_def = WorkflowDefinition(
    name="my_workflow",
    dag=dag,
    circuit_breakers=circuit_breakers,
)
```

### Pattern 4: Checkpointing

```python
from pathlib import Path

# Create engine with checkpoint storage
engine = WorkflowEngine(
    checkpoint_storage_path=Path("./checkpoints"),
)

# Enable checkpointing in workflow
workflow_def = WorkflowDefinition(
    name="my_workflow",
    dag=dag,
    checkpoint_enabled=True,
    checkpoint_frequency=5,  # Checkpoint every 5 nodes
)

# Resume from checkpoint
execution = await engine.resume_from_checkpoint(
    workflow_def,
    checkpoint_id="my_workflow_2026-04-11T01:48:00",
)
```

## Configuration Reference

### RetryPolicy

```python
RetryPolicy(
    max_attempts=3,                    # Max retry attempts
    initial_interval_ms=100,           # Initial backoff
    max_interval_ms=10000,             # Max backoff
    backoff_coefficient=2.0,           # Backoff multiplier
    backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
    non_retryable_errors=["ValueError"],  # Don't retry these
    timeout_ms=30000,                  # Operation timeout
)
```

### RecoveryStrategy

```python
RecoveryStrategy(
    name="my_strategy",
    action=RecoveryAction.RETRY,      # RETRY, SKIP, ROLLBACK, COMPENSATE, FAIL
    max_retries=3,
    compensating_action=my_function,   # For COMPENSATE action
    rollback_steps=["task1", "task2"], # For ROLLBACK action
)
```

### WorkflowDefinition

```python
WorkflowDefinition(
    name="my_workflow",
    dag=dag,
    description="Workflow description",
    retry_policies={...},              # Per-task retry policies
    recovery_strategies={...},         # Per-task recovery strategies
    conditional_logic={...},           # Per-task conditional logic
    circuit_breakers={...},            # Per-task circuit breakers
    max_parallel=10,                   # Max parallel tasks
    fail_fast=False,                   # Stop on first failure?
    checkpoint_enabled=True,           # Enable checkpointing?
    checkpoint_frequency=5,            # Checkpoint every N nodes
)
```

## Monitoring

### Access Metrics

```python
execution = await engine.execute(workflow_def, context)

# Overall metrics
print(f"Duration: {execution.metrics['duration_seconds']}s")
print(f"Completed: {execution.metrics['completed_nodes']}")
print(f"Failed: {execution.metrics['failed_nodes']}")

# Per-node metrics
for node_id, result in execution.result["node_results"].items():
    print(f"{node_id}: {result['status']} ({result['duration_seconds']}s)")
    if result['error']:
        print(f"  Error: {result['error']}")
```

### Execution Log

```python
# Access detailed execution log
for entry in execution.result["execution_log"]:
    print(f"{entry['node_id']}: {entry['status']} at {entry['start_time']}")
```

## Testing

### Unit Test Example

```python
import pytest
from temporal.workflows.engine import WorkflowEngine, WorkflowDefinition, DAG, DAGNode

@pytest.mark.asyncio
async def test_my_workflow():
    dag = DAG(name="test")
    dag.add_node(DAGNode(id="task1", task=lambda ctx, meta: {"result": "ok"}))
    
    workflow_def = WorkflowDefinition(name="test", dag=dag)
    engine = WorkflowEngine()
    
    execution = await engine.execute(workflow_def)
    
    assert execution.status.value == "completed"
    assert execution.result["status"] == "completed"
```

## Integration with Temporal.io

### Use with Temporal Workflow

```python
from temporalio import workflow
from temporal.workflows.engine.workflow_engine import TemporalWorkflow

@workflow.defn
class MyTemporalWorkflow:
    @workflow.run
    async def run(self, workflow_def_dict):
        # Workflow runs with Temporal durability
        result = await TemporalWorkflow().run(workflow_def_dict)
        return result
```

## Troubleshooting

### Issue: Task keeps failing
**Solution:** Check retry policy and add proper error handling

```python
retry_policies = {
    "failing_task": RetryPolicy(
        max_attempts=5,
        initial_interval_ms=2000,
        backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
    ),
}
```

### Issue: Workflow stuck
**Solution:** Check for missing dependencies or circular references

```python
# Validate DAG before execution
try:
    workflow_def.validate()
except ValueError as e:
    print(f"Validation error: {e}")
```

### Issue: Need to resume after crash
**Solution:** Use checkpointing

```python
engine = WorkflowEngine(checkpoint_storage_path=Path("./checkpoints"))
workflow_def.checkpoint_enabled = True

# Resume from latest checkpoint
execution = await engine.resume_from_checkpoint(
    workflow_def,
    checkpoint_id="auto",  # Use latest
)
```

## Next Steps

1. **Explore Examples**: Check `examples/` directory for complete workflows
2. **Read Architecture**: See `ARCHITECTURE.md` for design details
3. **Integration Guide**: See `INTEGRATION.py` for integration patterns
4. **Run Tests**: `pytest test_engine.py -v`
5. **Customize**: Extend with your own tasks and workflows

## Support

For more information:
- Full Documentation: `README.md`
- Architecture Details: `ARCHITECTURE.md`
- Integration Examples: `INTEGRATION.py`
- Implementation Summary: `IMPLEMENTATION_SUMMARY.md`
