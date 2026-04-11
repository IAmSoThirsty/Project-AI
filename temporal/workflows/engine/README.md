# Workflow Orchestration Engine

A comprehensive workflow orchestration engine for complex agent coordination with Temporal.io integration.

## Features

### 🔄 DAG-Based Execution
- **Directed Acyclic Graphs**: Define workflows as DAGs with dependency management
- **Parallel Execution**: Automatically execute independent tasks in parallel
- **Topological Sorting**: Efficient execution ordering with level-based parallelism
- **Cycle Detection**: Automatic validation to prevent circular dependencies

### 🔀 Conditional Logic
- **If/Else Branching**: Dynamic workflow paths based on runtime conditions
- **Complex Conditions**: Support for AND, OR, NOT operations
- **Variable Resolution**: Access context variables and nested paths
- **Loop Constructs**: For-each, while, and do-while loops

### 🔁 Retry Mechanisms
- **Exponential Backoff**: Configurable backoff strategies
- **Custom Retry Policies**: Per-task retry configuration
- **Circuit Breakers**: Prevent cascading failures
- **Timeout Management**: Operation-level timeout controls

### 🛡️ Failure Recovery
- **Checkpoint/Restore**: Workflow state persistence
- **Compensating Transactions**: Automatic rollback actions
- **Partial Failure Handling**: Continue execution on non-critical failures
- **Recovery Strategies**: Retry, skip, rollback, compensate, or fail

### ⚡ Temporal.io Integration
- **Durable Execution**: Long-running workflows that survive process restarts
- **Event Sourcing**: Complete workflow history and replay capability
- **Scalability**: Distributed execution across multiple workers

## Architecture

```
temporal/workflows/engine/
├── __init__.py              # Package exports
├── dag.py                   # DAG executor
├── conditionals.py          # Conditional logic interpreter
├── retry.py                 # Retry strategies and circuit breakers
├── recovery.py              # Failure recovery framework
├── workflow_engine.py       # Main orchestration engine
└── examples/                # Example workflows
    ├── __init__.py
    ├── build_pipeline.py    # CI/CD pipeline example
    ├── security_scan.py     # Security scanning workflow
    └── deployment.py        # Blue-green deployment
```

## Quick Start

### Basic Workflow

```python
import asyncio
from temporal.workflows.engine import (
    WorkflowEngine,
    WorkflowDefinition,
    DAG,
    DAGNode,
)

# Define tasks
async def task_a(context, metadata):
    return {"result": "A"}

async def task_b(context, metadata):
    return {"result": "B"}

# Create DAG
dag = DAG(name="simple_workflow")
dag.add_node(DAGNode(id="task_a", task=task_a))
dag.add_node(DAGNode(id="task_b", task=task_b, dependencies=["task_a"]))

# Create workflow
workflow_def = WorkflowDefinition(
    name="simple_workflow",
    dag=dag,
)

# Execute
engine = WorkflowEngine()
execution = await engine.execute(workflow_def)
print(f"Status: {execution.status}")
```

### Workflow with Retry and Recovery

```python
from temporal.workflows.engine import (
    RetryPolicy,
    BackoffStrategy,
    RecoveryStrategy,
    RecoveryAction,
)

# Define retry policy
retry_policies = {
    "task_a": RetryPolicy(
        max_attempts=3,
        initial_interval_ms=1000,
        backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
    ),
}

# Define recovery strategy
recovery_strategies = {
    "task_a": RecoveryStrategy(
        name="skip_on_failure",
        action=RecoveryAction.SKIP,
    ),
}

# Create workflow with policies
workflow_def = WorkflowDefinition(
    name="resilient_workflow",
    dag=dag,
    retry_policies=retry_policies,
    recovery_strategies=recovery_strategies,
)
```

### Conditional Execution

```python
from temporal.workflows.engine import (
    Condition,
    ConditionalBranch,
    ConditionalLogic,
    ConditionOperator,
)

# Define conditional logic
conditional_logic = {
    "decision_node": ConditionalLogic(
        branches=[
            ConditionalBranch(
                condition=Condition(
                    operator=ConditionOperator.GT,
                    left="$score",
                    right=80,
                ),
                action="high_score_path",
            ),
            ConditionalBranch(
                condition=Condition(
                    operator=ConditionOperator.GT,
                    left="$score",
                    right=50,
                ),
                action="medium_score_path",
            ),
        ],
        default_action="low_score_path",
    ),
}

workflow_def = WorkflowDefinition(
    name="conditional_workflow",
    dag=dag,
    conditional_logic=conditional_logic,
)
```

## Example Workflows

### 1. Build Pipeline

A complete CI/CD pipeline with parallel testing:

```python
from temporal.workflows.engine.examples import create_build_pipeline

workflow_def = create_build_pipeline()
engine = WorkflowEngine()

context = {
    "branch": "main",
    "run_tests": True,
}

execution = await engine.execute(workflow_def, context)
```

**Features:**
- Parallel unit and integration tests
- Docker image building
- Artifact publishing
- Automatic retry on transient failures
- Skip non-critical test failures

### 2. Security Scan

Comprehensive security scanning with auto-remediation:

```python
from temporal.workflows.engine.examples import create_security_scan_workflow

workflow_def = create_security_scan_workflow()
engine = WorkflowEngine()

context = {
    "target": "myapp:latest",
    "auto_remediate_enabled": True,
}

execution = await engine.execute(workflow_def, context)
```

**Features:**
- Parallel SAST, DAST, dependency, container, and license scans
- Circuit breakers for external scan services
- Conditional auto-remediation based on severity
- Comprehensive reporting

### 3. Deployment

Blue-green deployment with health checks and rollback:

```python
from temporal.workflows.engine.examples import create_deployment_workflow

workflow_def = create_deployment_workflow()
engine = WorkflowEngine()

context = {
    "environment": "production",
    "version": "1.2.0",
}

execution = await engine.execute(workflow_def, context)
```

**Features:**
- Database backup and migrations
- Blue-green deployment strategy
- Health checks and smoke tests
- Conditional traffic switching
- Automatic rollback on failures
- Compensating transactions

## Advanced Features

### Circuit Breakers

Prevent cascading failures with circuit breaker pattern:

```python
from temporal.workflows.engine import CircuitBreaker

circuit_breaker = CircuitBreaker(
    failure_threshold=5,      # Open after 5 failures
    success_threshold=2,      # Close after 2 successes
    timeout_seconds=60,       # Wait 60s before retry
)

workflow_def = WorkflowDefinition(
    name="workflow",
    dag=dag,
    circuit_breakers={
        "external_service": circuit_breaker,
    },
)
```

### Checkpointing

Enable checkpoint-based recovery:

```python
from pathlib import Path

engine = WorkflowEngine(
    checkpoint_storage_path=Path("./checkpoints"),
)

workflow_def = WorkflowDefinition(
    name="workflow",
    dag=dag,
    checkpoint_enabled=True,
    checkpoint_frequency=5,  # Checkpoint every 5 nodes
)

# Resume from checkpoint
execution = await engine.resume_from_checkpoint(
    workflow_def,
    checkpoint_id="workflow_2026-04-11T01:48:00",
)
```

### Loop Constructs

Implement iterative workflows:

```python
from temporal.workflows.engine.conditionals import LoopConstruct, Condition, ConditionOperator

# For-each loop
loop = LoopConstruct(
    loop_type="foreach",
    items=[1, 2, 3, 4, 5],
)

# While loop
loop = LoopConstruct(
    loop_type="while",
    condition=Condition(
        operator=ConditionOperator.LT,
        left="$counter",
        right=10,
    ),
    max_iterations=100,
)
```

### Temporal Integration

Run workflows with Temporal.io:

```python
from temporalio.client import Client
from temporal.workflows.engine.workflow_engine import TemporalWorkflow

# Connect to Temporal
client = await Client.connect("localhost:7233")

# Start workflow
result = await client.execute_workflow(
    TemporalWorkflow.run,
    {
        "name": "my_workflow",
        "dag": {...},  # Serialized workflow definition
    },
    id="workflow-123",
    task_queue="workflow-tasks",
)
```

## Configuration

### Retry Policy Options

```python
RetryPolicy(
    max_attempts=3,              # Maximum retry attempts
    initial_interval_ms=100,     # Initial backoff interval
    max_interval_ms=10000,       # Maximum backoff interval
    backoff_coefficient=2.0,     # Backoff multiplier
    backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
    non_retryable_errors=[       # Errors that shouldn't be retried
        "ValueError",
        "AuthenticationError",
    ],
    timeout_ms=30000,            # Operation timeout
)
```

### Recovery Strategy Options

```python
RecoveryStrategy(
    name="my_recovery",
    action=RecoveryAction.RETRY,      # RETRY, SKIP, ROLLBACK, COMPENSATE, FAIL
    max_retries=3,
    checkpoint_frequency=5,
    compensating_action=my_compensating_function,
    rollback_steps=["step1", "step2"],
)
```

### Workflow Definition Options

```python
WorkflowDefinition(
    name="my_workflow",
    dag=dag,
    description="Workflow description",
    max_parallel=10,              # Max parallel tasks
    fail_fast=False,              # Stop on first failure
    checkpoint_enabled=True,      # Enable checkpointing
    checkpoint_frequency=5,       # Checkpoint every N nodes
    retry_policies={...},
    recovery_strategies={...},
    conditional_logic={...},
    circuit_breakers={...},
)
```

## Monitoring and Metrics

Access execution metrics:

```python
execution = await engine.execute(workflow_def, context)

print(f"Status: {execution.status}")
print(f"Duration: {execution.end_time - execution.start_time}")
print(f"Metrics: {execution.metrics}")
print(f"Checkpoints: {execution.checkpoints}")

# Individual node results
for node_id, result in execution.result["node_results"].items():
    print(f"{node_id}: {result['status']} ({result['duration_seconds']}s)")
```

## Testing

Run the example workflows:

```bash
# Build pipeline
python -m temporal.workflows.engine.examples.build_pipeline

# Security scan
python -m temporal.workflows.engine.examples.security_scan

# Deployment
python -m temporal.workflows.engine.examples.deployment
```

## Best Practices

1. **Keep Tasks Idempotent**: Tasks should be safe to retry
2. **Use Checkpoints**: Enable checkpointing for long-running workflows
3. **Configure Timeouts**: Set appropriate timeouts for all operations
4. **Handle Failures Gracefully**: Use recovery strategies for expected failures
5. **Monitor Circuit Breakers**: Track circuit breaker state for external dependencies
6. **Test Workflows**: Validate workflows before production deployment
7. **Use Conditional Logic**: Implement dynamic workflows based on runtime conditions
8. **Leverage Parallelism**: Use DAG dependencies to maximize parallel execution

## API Reference

See individual module documentation:
- `dag.py`: DAG structure and executor
- `conditionals.py`: Conditional logic and loops
- `retry.py`: Retry policies and circuit breakers
- `recovery.py`: Failure recovery and checkpoints
- `workflow_engine.py`: Main orchestration engine

## License

Part of the Sovereign Governance Substrate project.
