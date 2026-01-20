# Liara Temporal Agency - Quick Reference Guide

## Overview

The Liara Temporal Agency provides production-grade distributed agent mission management using Temporal.io workflows. This system replaces in-memory mission assignment with persistent, retry-enabled, horizontally-scalable orchestration.

## Architecture Components

### Workflows
- **CrisisResponseWorkflow**: Sequential mission phase execution with automatic retries
  - Location: `src/app/temporal/workflows.py`
  - Data Models: `CrisisRequest`, `CrisisResult`, `MissionPhase`

### Activities
- **validate_crisis_request**: Validate crisis request parameters
- **initialize_crisis_response**: Setup crisis tracking
- **perform_agent_mission**: Execute agent deployment (core activity)
- **log_mission_phase**: Log phase completion/failure
- **finalize_crisis_response**: Finalize crisis completion

Location: `src/app/temporal/activities.py`

### Workers
- **Main Worker**: `src/app/temporal/worker.py` (all workflows)
- **Liara Worker**: `cognition/liara/worker.py` (crisis workflows only)

Task Queue: `liara-crisis-tasks`

### Client
- **LiaraTemporalAgency**: High-level API for crisis management
  - Location: `cognition/liara/agency.py`
  - Methods:
    - `trigger_crisis_response()`: Start workflow
    - `get_crisis_status()`: Check status
    - `wait_for_crisis_completion()`: Wait for result

## Setup Instructions

### 1. Start Temporal Server

Using Docker Compose:
```bash
docker-compose up -d temporal temporal-postgresql
```

Using setup script:
```bash
python scripts/setup_temporal.py start
```

Verify server is running:
```bash
curl http://localhost:8233/api/v1/namespaces/default
```

### 2. Start Worker

Choose one:

**Dedicated Liara Worker** (recommended for production):
```bash
python cognition/liara/worker.py
```

**Main Worker** (includes all workflows):
```bash
python src/app/temporal/worker.py
```

Expected output:
```
INFO - Starting Liara Temporal Agency Worker
INFO - Connected to Temporal server
INFO - Liara worker created with 1 workflows and 5 activities
INFO - Task queue: liara-crisis-tasks
INFO - Liara worker is running. Press Ctrl+C to stop.
```

### 3. Trigger Workflows

#### Method 1: CLI Tool (Quickest)
```bash
# Trigger crisis response
python cognition/liara/cli.py trigger target-alpha recon secure extract cleanup

# Check status
python cognition/liara/cli.py status <workflow-id>

# Wait for completion
python cognition/liara/cli.py wait <workflow-id>
```

#### Method 2: Example Script
```bash
python examples/temporal/liara_crisis_example.py
```

#### Method 3: Python Code
```python
import asyncio
from cognition.liara.agency import LiaraTemporalAgency

async def main():
    async with LiaraTemporalAgency() as agency:
        missions = [
            {
                "phase_id": "phase-1",
                "agent_id": "agent-001",
                "action": "deploy",
                "target": "target-alpha",
                "priority": 1,
            }
        ]
        
        workflow_id = await agency.trigger_crisis_response(
            target_member="target-alpha",
            missions=missions,
            initiated_by="user-123",
        )
        
        result = await agency.wait_for_crisis_completion(workflow_id)
        print(f"Success: {result['success']}")

asyncio.run(main())
```

## Monitoring & Observability

### Temporal Web UI

Access: `http://localhost:8233`

Navigate to:
1. Namespaces → `default`
2. Workflows
3. Filter by:
   - Workflow Type: `CrisisResponseWorkflow`
   - Task Queue: `liara-crisis-tasks`

View details:
- Execution history
- Activity timings
- Retry attempts
- Input/output payloads
- Event timeline

### Persistent State

Crisis records saved to:
```
data/crises/crisis-<id>.json
```

Example record:
```json
{
  "crisis_id": "crisis-target-alpha-1234567890",
  "target": "target-alpha",
  "status": "completed",
  "started_at": "2026-01-16T10:30:00.000Z",
  "completed_at": "2026-01-16T10:35:00.000Z",
  "phases": [
    {
      "phase_id": "phase-1",
      "status": "completed",
      "timestamp": "2026-01-16T10:31:00.000Z"
    }
  ],
  "summary": {
    "completed_phases": 4,
    "failed_phases": 0,
    "total_phases": 4
  }
}
```

### Logs

Worker logs show:
- Workflow starts
- Activity executions
- Agent deployments
- Phase completions
- Errors and retries

Example log output:
```
INFO - AGENT DEPLOYMENT - Phase: recon-phase-1 | Agent: recon-agent-001 | Action: reconnaissance | Target: target-alpha
INFO - Agent recon-agent-001 deployed successfully for mission phase recon-phase-1
```

## Testing

### Unit Tests
```bash
# Test data models and activities (no Temporal server required)
pytest tests/temporal/test_liara_workflows.py -k "not integration"
```

### Integration Tests
```bash
# Requires running Temporal server
pytest tests/temporal/test_liara_workflows.py -m integration
```

### Manual Testing

1. Start Temporal server
2. Start worker in one terminal
3. Run example in another terminal
4. Monitor in Web UI
5. Check persistent state files

## Production Deployment

### Temporal Cloud

Configure for managed Temporal Cloud:
```python
agency = LiaraTemporalAgency(
    temporal_host="<namespace>.<account>.tmprl.cloud:7233",
    namespace="<namespace>.<account>",
    task_queue="liara-crisis-tasks",
)
```

### Horizontal Scaling

Deploy multiple workers:
```bash
# Deploy 5 workers for increased throughput
docker-compose up -d --scale temporal-worker=5
```

All workers connect to the same task queue for automatic work distribution.

### Monitoring

Key metrics to monitor:
- Workflow success/failure rates
- Activity execution times
- Task queue backlog depth
- Worker health status
- Retry counts

Access via:
- Temporal Web UI
- Temporal CLI: `temporal workflow list`
- Prometheus metrics (if configured)

### Retry Configuration

Default retry policy (configurable in workflows.py):
```python
retry_policy=RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=2),
    maximum_interval=timedelta(seconds=30),
)
```

Adjust based on:
- Mission criticality
- Expected failure rates
- Recovery time objectives

## Troubleshooting

### Worker won't start
- Check Temporal server is running: `curl http://localhost:8233`
- Verify network connectivity
- Check worker logs for connection errors

### Workflow not executing
- Verify worker is running and connected
- Check task queue name matches
- View workflow in Web UI for errors
- Check activity logs for failures

### Activities failing
- Review activity implementation
- Check retry policy configuration
- Verify data directory permissions
- Review activity logs for exceptions

### State not persisting
- Verify `data/crises/` directory exists and is writable
- Check activity `finalize_crisis_response` completed
- Review worker logs for file I/O errors

## FAQ

**Q: Can I run without Temporal server for testing?**
A: No, workflows require a running Temporal server. Use Docker Compose for local development.

**Q: How do I scale horizontally?**
A: Deploy multiple workers pointing to the same task queue. Temporal automatically distributes work.

**Q: What happens if a worker crashes mid-workflow?**
A: Temporal persists workflow state. When a new worker starts, it resumes from the last checkpoint.

**Q: Can I modify workflow code?**
A: Yes, but use versioning to handle in-flight workflows. See Temporal documentation on workflow versioning.

**Q: How do I integrate with existing systems?**
A: Activities can call any external API or service. Keep activities idempotent for safe retries.

## Resources

- **Temporal Documentation**: https://docs.temporal.io/
- **Python SDK Guide**: https://docs.temporal.io/dev-guide/python
- **Examples**: `examples/temporal/`
- **Tests**: `tests/temporal/test_liara_workflows.py`
- **Source Code**: `cognition/liara/` and `src/app/temporal/`
