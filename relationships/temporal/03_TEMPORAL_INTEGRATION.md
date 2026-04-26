# Temporal Integration Flows - Project-AI

## 📋 Document Metadata
- **Category**: Temporal Infrastructure
- **Last Updated**: 2025-01-21
- **Scope**: Integration patterns, client usage, worker deployment, and execution flows

## 🎯 Overview

This document maps how Temporal integrates with Project-AI's architecture, including client connections, worker registration, task queues, and cross-system interactions.

---

## 1️⃣ TEMPORAL ARCHITECTURE OVERVIEW

### System Components

```
┌─────────────────────────────────────────────────────┐
│                  Temporal Server                     │
│                  (localhost:7233)                    │
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │ Namespace  │  │ Task Queue │  │  Workflow  │   │
│  │  default   │  │  Management│  │   Engine   │   │
│  └────────────┘  └────────────┘  └────────────┘   │
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │   Event    │  │  Activity  │  │   State    │   │
│  │  History   │  │  Registry  │  │   Store    │   │
│  └────────────┘  └────────────┘  └────────────┘   │
└─────────────────────────────────────────────────────┘
         │                  │                  │
         │                  │                  │
         ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Temporal     │   │ Temporal     │   │ Temporal     │
│ Client       │   │ Worker       │   │ Worker       │
│              │   │ (Queue 1)    │   │ (Queue 2)    │
│ Application  │   │              │   │              │
│ Code         │   │ Activities   │   │ Activities   │
└──────────────┘   │ Workflows    │   │ Workflows    │
                   └──────────────┘   └──────────────┘
```

---

## 2️⃣ CLIENT INTEGRATION

### 2.1 Client Connection

**Location**: `src/integrations/temporal/client.py`  
**Class**: `TemporalClient`

#### Connection Flow
```
Application Startup
  │
  ├─→ Initialize TemporalClient(host, namespace, task_queue)
  │   ├─→ host: From TEMPORAL_HOST env (default: localhost:7233)
  │   ├─→ namespace: From TEMPORAL_NAMESPACE env (default: "default")
  │   └─→ task_queue: From TEMPORAL_TASK_QUEUE env (default: "project-ai-tasks")
  │
  ├─→ await client.connect()
  │   ├─→ Establishes connection to Temporal server
  │   ├─→ Validates namespace exists
  │   └─→ Returns connected Client instance
  │
  └─→ Client ready for workflow execution
```

#### Usage Example
```python
from src.integrations.temporal.client import TemporalClient

# Initialize
client = TemporalClient(
    host="localhost:7233",
    namespace="default",
    task_queue="project-ai-tasks"
)

# Connect
await client.connect()

# Start workflow
handle = await client.start_workflow(
    workflow=TriumvirateWorkflow.run,
    args=request,
    workflow_id="triumvirate-123",
    task_queue="project-ai-tasks"
)

# Wait for result
result = await handle.result()
```

---

### 2.2 Client Configuration

#### Environment Variables
```bash
# .env or environment
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=project-ai-tasks

# Optional: For cloud deployment
TEMPORAL_CLIENT_CERT=path/to/cert.pem
TEMPORAL_CLIENT_KEY=path/to/key.pem
```

#### Configuration Priority
1. Constructor parameters (highest)
2. Environment variables
3. Default values (lowest)

---

### 2.3 Client Context Manager

```python
async with TemporalClient() as client:
    # Client auto-connects on enter
    handle = await client.start_workflow(...)
    result = await handle.result()
    # Client auto-closes on exit
```

---

## 3️⃣ WORKER INTEGRATION

### 3.1 Worker Registration

**Location**: `src/integrations/temporal/worker.py`  
**Function**: `run_worker()`

#### Worker Startup Flow
```
Worker Process Start
  │
  ├─→ Load configuration from environment
  │   ├─→ TEMPORAL_HOST
  │   ├─→ TEMPORAL_NAMESPACE
  │   └─→ TEMPORAL_TASK_QUEUE
  │
  ├─→ Connect to Temporal server
  │   └─→ await Client.connect(host, namespace)
  │
  ├─→ Register workflows
  │   └─→ workflows=[ExampleWorkflow, TriumvirateWorkflow, ...]
  │
  ├─→ Register activities
  │   └─→ activities=[
  │       validate_input,
  │       simulate_ai_call,
  │       process_ai_task,
  │       run_triumvirate_pipeline,
  │       ...
  │   ]
  │
  ├─→ Create Worker instance
  │   └─→ Worker(client, task_queue, workflows, activities)
  │
  ├─→ Start worker (blocks)
  │   └─→ await worker.run()
  │
  └─→ Worker polls for tasks and executes
```

#### Worker Command
```bash
# Start worker
python -m src.integrations.temporal.worker

# Or with custom config
TEMPORAL_HOST=temporal.example.com python -m src.integrations.temporal.worker
```

---

### 3.2 Multiple Worker Deployment

#### Task Queue Specialization

```
┌─────────────────────────────────────────────────────┐
│          Task Queue: project-ai-tasks               │
│  ┌─────────────────────────────────────────────┐   │
│  │ Worker 1                                    │   │
│  │ - TriumvirateWorkflow                       │   │
│  │ - AILearningWorkflow                        │   │
│  │ - ImageGenerationWorkflow                   │   │
│  │ - DataAnalysisWorkflow                      │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│          Task Queue: security-agents                │
│  ┌─────────────────────────────────────────────┐   │
│  │ Worker 2                                    │   │
│  │ - RedTeamCampaignWorkflow                   │   │
│  │ - CodeSecuritySweepWorkflow                 │   │
│  │ - SafetyTestingWorkflow                     │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │ Worker 3 (Redundant)                        │   │
│  │ - Same workflows as Worker 2                │   │
│  │ - Load balancing / High availability        │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│     Task Queue: constitutional-enforcement          │
│  ┌─────────────────────────────────────────────┐   │
│  │ Worker 4                                    │   │
│  │ - ConstitutionalMonitoringWorkflow          │   │
│  │ - PolicyEnforcementWorkflow                 │   │
│  │ - PeriodicPolicyReview                      │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

#### Worker Scaling Strategy
- **project-ai-tasks**: 2-4 workers (general operations)
- **security-agents**: 2-3 workers (security operations)
- **constitutional-enforcement**: 1-2 workers (governance)

---

### 3.3 Worker Health & Monitoring

#### Health Checks
```python
# Worker exposes health metrics
GET /health
{
  "status": "healthy",
  "worker_id": "worker-1",
  "task_queue": "project-ai-tasks",
  "workflows_registered": 4,
  "activities_registered": 12,
  "uptime_seconds": 3600
}
```

#### Graceful Shutdown
```python
# Handles SIGTERM, SIGINT
try:
    await worker.run()
except KeyboardInterrupt:
    logger.info("Worker shutdown requested")
    # Worker completes in-flight tasks before exiting
```

---

## 4️⃣ TASK QUEUE ARCHITECTURE

### 4.1 Task Queue Mapping

| Task Queue | Purpose | Workflows | Workers |
|------------|---------|-----------|---------|
| `project-ai-tasks` | General AI operations | Triumvirate, Learning, Image Gen, Data Analysis | 2-4 |
| `security-agents` | Security operations | Red Team, Code Sweep, Safety Testing | 2-3 |
| `constitutional-enforcement` | Governance | Constitutional Monitoring, Policy Enforcement | 1-2 |
| `batch-processing` | Batch operations | Batch workflows (future) | 1-2 |

### 4.2 Task Queue Selection Logic

```python
def select_task_queue(workflow_type: str) -> str:
    """Select appropriate task queue for workflow."""
    
    if workflow_type in ["triumvirate", "learning", "image_gen", "data_analysis"]:
        return "project-ai-tasks"
    
    elif workflow_type in ["red_team", "code_sweep", "safety_test"]:
        return "security-agents"
    
    elif workflow_type in ["constitutional", "policy"]:
        return "constitutional-enforcement"
    
    else:
        return "project-ai-tasks"  # Default
```

---

## 5️⃣ INTEGRATION WITH PROJECT-AI SYSTEMS

### 5.1 Desktop Application Integration

**Location**: `src/app/main.py` → `LeatherBookInterface`

#### Flow: User Action → Temporal Workflow
```
User clicks "Generate Image" button
  │
  ├─→ GUI emits signal: image_gen_requested
  │
  ├─→ Handler: switch_to_image_generation()
  │   └─→ Shows ImageGenerationLeftPanel
  │
  ├─→ User enters prompt, selects style
  │
  ├─→ User clicks "Generate"
  │
  ├─→ ImageGenerationWorker (QThread)
  │   │
  │   ├─→ Initialize TemporalClient
  │   │
  │   ├─→ Start ImageGenerationWorkflow
  │   │   └─→ await client.start_workflow(
  │   │       workflow=ImageGenerationWorkflow.run,
  │   │       args=ImageGenerationRequest(prompt, style, size),
  │   │       workflow_id=f"image-gen-{uuid}",
  │   │       task_queue="project-ai-tasks"
  │   │   )
  │   │
  │   ├─→ Wait for result (async)
  │   │   └─→ result = await handle.result()
  │   │
  │   └─→ Emit signal: image_generated(image_path, metadata)
  │
  └─→ ImageGenerationRightPanel updates
      └─→ Displays generated image
```

#### Key Integration Points
1. **QThread for async**: Prevents UI blocking during workflow execution
2. **Signal-based communication**: Decouples GUI from workflow logic
3. **Temporal client per workflow**: Isolated connections

---

### 5.2 Web Application Integration

**Location**: `web/backend/` (Flask API)

#### Flow: API Request → Temporal Workflow
```
POST /api/generate-image
  │
  ├─→ Flask route handler
  │   └─→ @app.route('/api/generate-image', methods=['POST'])
  │
  ├─→ Validate request body
  │   └─→ {prompt, style, size, backend}
  │
  ├─→ Initialize TemporalClient (app-scoped)
  │
  ├─→ Start ImageGenerationWorkflow
  │   └─→ handle = await client.start_workflow(...)
  │
  ├─→ Option 1: Synchronous (wait for result)
  │   └─→ result = await handle.result()
  │   └─→ Return JSON response
  │
  └─→ Option 2: Asynchronous (return workflow_id)
      └─→ Return {workflow_id: "...", status: "running"}
      └─→ Client polls: GET /api/workflow/{workflow_id}/status
```

#### API Endpoints
```
POST   /api/workflow/start           # Start workflow
GET    /api/workflow/{id}/status     # Get workflow status
GET    /api/workflow/{id}/result     # Get workflow result
POST   /api/workflow/{id}/cancel     # Cancel workflow
```

---

### 5.3 CLI Integration

**Location**: `project_ai_cli.py` or `scripts/`

#### Flow: CLI Command → Temporal Workflow
```bash
$ project-ai security scan --repo . --generate-patches

CLI Parser
  │
  ├─→ Parse command: security scan
  ├─→ Parse options: --repo, --generate-patches
  │
  ├─→ Initialize TemporalClient
  │
  ├─→ Start CodeSecuritySweepWorkflow
  │   └─→ handle = await client.start_workflow(
  │       workflow=CodeSecuritySweepWorkflow.run,
  │       args=CodeSecuritySweepRequest(
  │           repo_path=".",
  │           generate_patches=True,
  │           create_sarif=True
  │       ),
  │       workflow_id=f"code-sweep-{timestamp}",
  │       task_queue="security-agents"
  │   )
  │
  ├─→ Show progress (await handle with updates)
  │   └─→ Poll workflow status every 5s
  │
  ├─→ Print result
  │   └─→ "Scan complete: 5 findings (2 critical)"
  │
  └─→ Exit with status code
```

---

## 6️⃣ CROSS-SYSTEM INTEGRATION FLOWS

### 6.1 Triumvirate → Temporal Integration

**Location**: `src/cognition/triumvirate.py` + `temporal/workflows/triumvirate_workflow.py`

#### Integration Pattern: Wrapper Activity
```
Triumvirate Pipeline (Direct Call)
  │
  └─→ triumvirate.process(input_data, context)
      ├─→ Cerberus: Validate input
      ├─→ Codex: ML inference
      ├─→ Galahad: Reasoning
      └─→ Cerberus: Enforce output

Triumvirate Pipeline (Temporal Workflow)
  │
  └─→ TriumvirateWorkflow.run(request)
      │
      └─→ Activity: run_triumvirate_pipeline(request)
          └─→ Calls: triumvirate.process(...)
```

**Why Wrap?**
- **Durability**: Workflow survives worker crashes
- **Retry Logic**: Automatic retries on failures
- **Observability**: Temporal tracks all executions
- **Timeout Enforcement**: Hard timeouts per stage

---

### 6.2 Security Agents → Temporal Integration

**Location**: `src/app/agents/` + `temporal/workflows/security_agent_workflows.py`

#### Integration Pattern: Multi-Stage Workflow
```
Security Agent (Direct Call)
  │
  └─→ agent.execute_attack(target)
      └─→ Single execution, no persistence

Security Agent (Temporal Workflow)
  │
  └─→ RedTeamCampaignWorkflow.run(request)
      │
      ├─→ Activity: create_forensic_snapshot
      │   └─→ Immutable state capture
      │
      ├─→ For each (persona, target):
      │   ├─→ Activity: run_red_team_attack
      │   ├─→ Activity: evaluate_attack
      │   └─→ Activity: trigger_incident (if critical)
      │
      ├─→ Activity: generate_sarif
      ├─→ Activity: upload_sarif
      └─→ Activity: notify_triumvirate
```

**Benefits**:
- **Campaign Orchestration**: Manages multiple attacks
- **Forensic Snapshots**: Immutable audit trail
- **Incident Automation**: Automatic ticket creation
- **SARIF Integration**: GitHub Security upload

---

### 6.3 Constitutional Governance → Temporal Integration

**Location**: `gradle-evolution/constitutional/temporal_law.py` + Temporal workflows

#### Integration Pattern: Policy Enforcement Workflow
```
Action Request
  │
  ├─→ TemporalLawEnforcer.enforce_with_timeout(action, metadata)
  │   │
  │   ├─→ Start PolicyEnforcementWorkflow
  │   │   └─→ workflow_id: f"enforce-{action}-{timestamp}"
  │   │
  │   ├─→ Workflow evaluates action against:
  │   │   ├─→ Active temporal laws (time-bounded)
  │   │   ├─→ Constitutional principles
  │   │   └─→ Risk levels
  │   │
  │   ├─→ Wait for result (with timeout)
  │   │
  │   └─→ Return: {allowed: bool, reason: str}
  │
  └─→ Application proceeds based on decision
```

#### Historical Query Pattern
```
Query: "What was the policy decision at 2025-01-20T10:00:00Z?"
  │
  ├─→ TemporalLawEnforcer.query_historical_decision(action, timestamp)
  │   │
  │   ├─→ Get workflow_id from cache
  │   │
  │   ├─→ Get workflow handle
  │   │
  │   ├─→ Query: get_decision_at_time(timestamp)
  │   │
  │   └─→ Return: Historical decision data
  │
  └─→ "Action was DENIED at that time due to risk level 5"
```

**Use Cases**:
- **Compliance Auditing**: Prove policy enforcement at specific times
- **Debugging**: Understand why action was allowed/denied
- **Forensics**: Investigate security incidents

---

## 7️⃣ DEPLOYMENT PATTERNS

### 7.1 Local Development

```bash
# Terminal 1: Start Temporal server
temporal server start-dev

# Terminal 2: Start worker
python -m src.integrations.temporal.worker

# Terminal 3: Run application
python -m src.app.main
```

---

### 7.2 Docker Compose Deployment

**Location**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  temporal:
    image: temporalio/auto-setup:latest
    ports:
      - "7233:7233"
    environment:
      - DB=postgresql
      - POSTGRES_HOST=postgres
    depends_on:
      - postgres

  postgres:
    image: postgres:14
    environment:
      - POSTGRES_PASSWORD=temporal
      - POSTGRES_USER=temporal

  worker:
    build: .
    command: python -m src.integrations.temporal.worker
    environment:
      - TEMPORAL_HOST=temporal:7233
    depends_on:
      - temporal

  app:
    build: .
    command: python -m src.app.main
    ports:
      - "8000:8000"
    environment:
      - TEMPORAL_HOST=temporal:7233
    depends_on:
      - temporal
      - worker
```

---

### 7.3 Kubernetes Deployment

```yaml
# temporal-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: temporal-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: temporal-worker
  template:
    metadata:
      labels:
        app: temporal-worker
    spec:
      containers:
      - name: worker
        image: project-ai:latest
        command: ["python", "-m", "src.integrations.temporal.worker"]
        env:
        - name: TEMPORAL_HOST
          value: "temporal-frontend.temporal:7233"
        - name: TEMPORAL_NAMESPACE
          value: "default"
        - name: TEMPORAL_TASK_QUEUE
          value: "project-ai-tasks"
```

---

## 8️⃣ ERROR HANDLING & RECOVERY

### 8.1 Connection Failures

```python
try:
    client = TemporalClient()
    await client.connect()
except ConnectionError as e:
    logger.error("Failed to connect to Temporal: %s", e)
    # Fallback: Use local execution
    result = local_execution(request)
```

---

### 8.2 Workflow Failures

```python
try:
    handle = await client.start_workflow(...)
    result = await handle.result()
except WorkflowFailureError as e:
    logger.error("Workflow failed: %s", e)
    # Compensating action
    await rollback_changes()
```

---

### 8.3 Worker Crashes

**Temporal Handles Automatically**:
1. Workflow execution pauses
2. Another worker picks up workflow from last checkpoint
3. Workflow resumes from last completed activity
4. No data loss due to event history

---

## 9️⃣ MONITORING & OBSERVABILITY

### 9.1 Temporal Web UI

```
http://localhost:8080

Features:
- View all workflows
- Inspect workflow history
- See activity executions
- Query workflow state
- Cancel/terminate workflows
```

---

### 9.2 Metrics Integration

```python
# Custom metrics
from temporalio.runtime import PrometheusConfig, Runtime, TelemetryConfig

runtime = Runtime(telemetry=TelemetryConfig(
    metrics=PrometheusConfig(bind_address="0.0.0.0:9090")
))

client = await Client.connect(
    "localhost:7233",
    runtime=runtime
)
```

**Metrics Exposed**:
- `temporal_workflow_started`
- `temporal_workflow_completed`
- `temporal_workflow_failed`
- `temporal_activity_execution_latency`

---

### 9.3 Logging Integration

```python
import logging

# Configure Temporal logging
logging.getLogger("temporalio").setLevel(logging.INFO)

# Activity logging
@activity.defn
async def my_activity():
    activity.logger.info("Activity started")
    # ...
    activity.logger.info("Activity completed")
```

---

## 🔟 SECURITY CONSIDERATIONS

### 10.1 Authentication

```python
# mTLS authentication for production
from temporalio.client import Client, TLSConfig

client = await Client.connect(
    "temporal.example.com:7233",
    namespace="production",
    tls=TLSConfig(
        client_cert=open("client.pem", "rb").read(),
        client_private_key=open("client-key.pem", "rb").read()
    )
)
```

---

### 10.2 Data Encryption

```python
# Custom data converter for encryption
from temporalio.converter import DataConverter, default

class EncryptedDataConverter(DataConverter):
    def encode(self, values):
        # Encrypt before sending to Temporal
        return encrypted_values
    
    def decode(self, values):
        # Decrypt when receiving from Temporal
        return decrypted_values

client = await Client.connect(
    "localhost:7233",
    data_converter=EncryptedDataConverter()
)
```

---

### 10.3 Access Control

```yaml
# Temporal Cloud: Namespace permissions
namespaces:
  - name: project-ai-prod
    permissions:
      - users: ["dev-team"]
        actions: ["read", "write"]
      - users: ["audit-team"]
        actions: ["read"]
```

---

## ♾️ TEMPORAL CLOUD INTEGRATION

### Migration to Temporal Cloud

```python
# Cloud connection
from temporalio.client import Client

client = await Client.connect(
    "your-namespace.tmprl.cloud:7233",
    namespace="your-namespace",
    tls=TLSConfig(
        client_cert=CLOUD_CERT,
        client_private_key=CLOUD_KEY
    )
)
```

**Benefits**:
- **Managed Infrastructure**: No server maintenance
- **High Availability**: Multi-region replication
- **Scalability**: Auto-scaling workers
- **Security**: Built-in encryption, authentication

---

## 🔗 INTEGRATION CHECKLIST

### ✅ New Workflow Integration
- [ ] Define workflow class with `@workflow.defn`
- [ ] Define request/result dataclasses
- [ ] Implement `@workflow.run` method
- [ ] Create activities with `@activity.defn`
- [ ] Register workflow in worker
- [ ] Register activities in worker
- [ ] Add to appropriate task queue
- [ ] Write integration tests
- [ ] Document workflow in `01_WORKFLOW_CHAINS.md`
- [ ] Document activities in `02_ACTIVITY_DEPENDENCIES.md`

### ✅ New Activity Integration
- [ ] Define activity function with `@activity.defn`
- [ ] Define input/output types
- [ ] Set `start_to_close_timeout`
- [ ] Configure `retry_policy`
- [ ] Use `activity.logger` for logging
- [ ] Handle exceptions gracefully
- [ ] Register in worker
- [ ] Write unit tests
- [ ] Document in `02_ACTIVITY_DEPENDENCIES.md`

---

## 🔗 Related Documentation

- **Workflow Chains**: See `01_WORKFLOW_CHAINS.md`
- **Activity Dependencies**: See `02_ACTIVITY_DEPENDENCIES.md`
- **Governance**: See `04_TEMPORAL_GOVERNANCE.md`

---

**End of Temporal Integration Flows Documentation**


---


---

## 📚 Related Documentation

### Cross-References

- [[source-docs/temporal/WORKER_CLIENT_COMPREHENSIVE.md|Worker Client Comprehensive]]

## 🔗 Source Code References

This documentation references the following Temporal source files:

- [[temporal/__init__.py]] - Implementation file
