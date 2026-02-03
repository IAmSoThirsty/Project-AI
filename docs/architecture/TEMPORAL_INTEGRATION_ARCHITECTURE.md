# Temporal Integration Architecture

## Overview

This document describes the Temporal integration architecture for Project-AI.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Application Layer                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐      ┌──────────────────┐                │
│  │   GUI/CLI        │      │   Web Backend    │                │
│  │   (PyQt6)        │      │   (Flask)        │                │
│  └────────┬─────────┘      └────────┬─────────┘                │
│           │                         │                            │
│           └────────────┬────────────┘                            │
│                        │                                         │
│              ┌─────────▼──────────┐                             │
│              │  AI Controller     │                             │
│              │  (service layer)   │                             │
│              └─────────┬──────────┘                             │
│                        │                                         │
└────────────────────────┼─────────────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────────────┐
│                    Temporal Integration                           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Temporal Client (client.py)                    │ │
│  │  - Connection management                                    │ │
│  │  - Workflow starting                                        │ │
│  │  - Status queries                                           │ │
│  └──────────────────────┬─────────────────────────────────────┘ │
│                         │                                         │
│  ┌──────────────────────▼──────────────────────────────────────┐│
│  │              Workflows (workflows/)                          ││
│  │  ┌────────────────────────────────────────────────────────┐ ││
│  │  │  ExampleWorkflow                                        │ ││
│  │  │  - Multi-step orchestration                             │ ││
│  │  │  - Error handling & retries                             │ ││
│  │  │  - State management                                     │ ││
│  │  └──────────────────┬──────────────────────────────────────┘ ││
│  │                     │                                         ││
│  │  ┌──────────────────▼──────────────────────────────────────┐ ││
│  │  │  Activities (activities/)                                │ ││
│  │  │  - validate_input: Input validation                     │ ││
│  │  │  - simulate_ai_call: AI processing                      │ ││
│  │  │  - process_ai_task: Result processing                   │ ││
│  │  └─────────────────────────────────────────────────────────┘ ││
│  └──────────────────────────────────────────────────────────────┘│
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Worker (worker.py)                             │ │
│  │  - Registers workflows & activities                         │ │
│  │  - Polls for work                                           │ │
│  │  - Executes tasks                                           │ │
│  └──────────────────────┬─────────────────────────────────────┘ │
│                         │                                         │
└─────────────────────────┼───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                    Temporal Server                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────┐    ┌────────────────────┐              │
│  │  Temporal Core     │    │  PostgreSQL DB     │              │
│  │  - Workflow Engine │◄───┤  - State Storage   │              │
│  │  - Activity Queue  │    │  - Event History   │              │
│  └────────────────────┘    └────────────────────┘              │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Web UI (localhost:8233)                                    │ │
│  │  - Workflow monitoring                                      │ │
│  │  - Debugging & inspection                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Component Descriptions

### Application Layer

- **GUI/CLI**: User interfaces (PyQt6 desktop app, CLI tools)
- **Web Backend**: Flask API server
- **AI Controller**: High-level service that coordinates AI operations

### Temporal Integration Layer

#### Client (`src/integrations/temporal/client.py`)

- Manages connection to Temporal server
- Provides helper methods to start workflows
- Handles connection lifecycle

#### Workflows (`src/integrations/temporal/workflows/`)

- **ExampleWorkflow**: Demonstrates multi-step AI processing
  - Step 1: Validate input
  - Step 2: Call AI system
  - Step 3: Process results
- Durable: Survives crashes and restarts
- Automatic retries with exponential backoff

#### Activities (`src/integrations/temporal/activities/`)

- **validate_input**: Validates request data before processing
- **simulate_ai_call**: Simulates AI API call (replace with real AI)
- **process_ai_task**: Processes AI results and updates state

#### Worker (`src/integrations/temporal/worker.py`)

- Connects to Temporal server
- Registers workflows and activities
- Polls task queue for work
- Executes workflows and activities

### Temporal Server (Docker)

- **Temporal Core**: Workflow orchestration engine
- **PostgreSQL**: Persistent storage for workflow state
- **Web UI**: Browser-based monitoring at http://localhost:8233

## Data Flow

### Starting a Workflow

```
1. Application → AI Controller
   controller.process_ai_request(data="...", user_id="...")

2. AI Controller → Temporal Client
   client.start_workflow(ExampleWorkflow, args=WorkflowInput(...))

3. Temporal Client → Temporal Server
   POST /api/v1/namespaces/default/workflows

4. Temporal Server → Worker
   Task dispatched to worker via task queue

5. Worker → Workflow
   ExampleWorkflow.run() starts executing

6. Workflow → Activities
   - execute_activity(validate_input)
   - execute_activity(simulate_ai_call)
   - execute_activity(process_ai_task)

7. Workflow → Temporal Server
   Workflow result stored

8. Temporal Server → AI Controller
   Result returned to caller

9. AI Controller → Application
   WorkflowOutput returned with success/result
```

## Key Features

### Durability

- Workflows survive process crashes
- State is checkpointed after each step
- Can resume from last checkpoint

### Retries

- Automatic retry with exponential backoff
- Configurable retry policies per activity
- Failed activities don't fail entire workflow

### Observability

- Full execution history in Temporal Web UI
- Detailed logs at each step
- Query workflow state programmatically

### Scalability

- Horizontal scaling by adding workers
- Workers can be distributed across machines
- Load balancing handled by Temporal

## Extending the Integration

### Adding a New Workflow

1. Create workflow file in `src/integrations/temporal/workflows/`
1. Define workflow class with `@workflow.defn`
1. Implement `@workflow.run` method
1. Register in worker.py

### Adding a New Activity

1. Create activity in `src/integrations/temporal/activities/`
1. Decorate with `@activity.defn`
1. Implement async function
1. Register in worker.py

### Integration with Existing Code

The AI Controller provides a clean interface:

```python
from app.service.ai_controller import AIController

# Use in existing code
controller = AIController()
result = await controller.process_ai_request(
    data=user_input,
    user_id=current_user.id
)

if result.success:
    # Handle success
    process_result(result.result)
else:
    # Handle error
    log_error(result.error)
```

## Configuration

### Environment Variables

```bash
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=project-ai-tasks
```

### Docker Compose

The integration is pre-configured in `docker-compose.yml`:

- Temporal server on port 7233 (gRPC)
- Web UI on port 8233
- PostgreSQL for persistence
- Automatic worker startup

## Monitoring

### Web UI

- Visit http://localhost:8233
- View all workflow executions
- Inspect execution history
- Debug failures

### Logs

- Worker logs: `docker-compose logs temporal-worker`
- Server logs: `docker-compose logs temporal`

### Metrics

- Temporal exposes Prometheus metrics
- Integration with existing monitoring stack

## Production Considerations

### High Availability

- Run multiple workers for redundancy
- Use Temporal Cloud for managed service
- Configure PostgreSQL for HA

### Security

- Use mTLS for production
- Configure namespace-level permissions
- Secure PostgreSQL connections

### Performance

- Tune worker concurrency
- Configure activity timeouts appropriately
- Monitor task queue depth

## References

- [Temporal Documentation](https://docs.temporal.io/docs/python)
- [Sample Workflows](https://github.com/temporalio/samples-python)
- [Best Practices](https://docs.temporal.io/docs/python/best-practices)
