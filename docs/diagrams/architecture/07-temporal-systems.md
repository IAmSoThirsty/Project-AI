# Temporal Systems Architecture

```mermaid
graph TB
    subgraph "Temporal Client Layer"
        APP[Application Code<br/>Desktop/Web/API]
        CLIENT[Temporal Client<br/>Python SDK]
    end

    subgraph "Workflow Layer"
        WF_ENGINE[Workflow Engine<br/>Deterministic Execution]
        
        subgraph "Core Workflows"
            LEARNING_WF[Learning Request<br/>Workflow]
            IMAGE_WF[Image Generation<br/>Workflow]
            DATA_WF[Data Analysis<br/>Workflow]
            SECURITY_WF[Security Audit<br/>Workflow]
        end
        
        subgraph "Long-Running Workflows"
            MONITORING_WF[24/7 Monitoring<br/>Workflow]
            BACKUP_WF[Daily Backup<br/>Workflow]
            SYNC_WF[Cloud Sync<br/>Workflow]
            HEALTH_WF[Health Check<br/>Workflow]
        end
        
        WF_STATE[Workflow State<br/>Event Sourcing]
    end

    subgraph "Activity Layer"
        ACT_ENGINE[Activity Engine<br/>Side Effects]
        
        subgraph "Core Activities"
            OPENAI_ACT[OpenAI API Call<br/>Retry Logic]
            DB_ACT[Database Write<br/>Transaction]
            FILE_ACT[File Operation<br/>Atomic Write]
            EMAIL_ACT[Send Email<br/>SMTP]
        end
        
        subgraph "Governance Activities"
            VALIDATE_ACT[Governance Validation<br/>FourLaws Check]
            AUDIT_ACT[Audit Logging<br/>Immutable Trail]
            ENCRYPT_ACT[Encryption<br/>Fernet]
        end
        
        ACT_QUEUE[Activity Task Queue<br/>Priority Scheduling]
    end

    subgraph "Worker Layer"
        WORKER_POOL[Worker Pool<br/>Horizontal Scaling]
        
        WORKER1[Worker 1<br/>Workflows + Activities]
        WORKER2[Worker 2<br/>Activities Only]
        WORKER3[Worker 3<br/>Long-Running]
        
        HEARTBEAT[Heartbeat Monitor<br/>Liveness Check]
    end

    subgraph "Temporal Server (Self-Hosted)"
        FRONTEND[Frontend Service<br/>gRPC API]
        HISTORY[History Service<br/>Event Store]
        MATCHING[Matching Service<br/>Task Distribution]
        WORKER_SVC[Worker Service<br/>Workflow Execution]
    end

    subgraph "Persistence Layer"
        POSTGRES[PostgreSQL<br/>Event Storage]
        ELASTICSEARCH[Elasticsearch<br/>Visibility]
        CASSANDRA[Cassandra (Optional)<br/>High Scale]
    end

    subgraph "Governance Integration"
        FOUR_LAWS[FourLaws Validator<br/>Pre-Activity Hook]
        AUDIT_LOG[Audit Logger<br/>Post-Activity Hook]
        POLICY[Policy Engine<br/>Workflow Permissions]
    end

    subgraph "Monitoring & Observability"
        METRICS[Prometheus Metrics<br/>Workflow/Activity Stats]
        TRACES[Jaeger Tracing<br/>Distributed Trace]
        DASHBOARD[Temporal UI<br/>Web Dashboard]
        ALERTS[Alert Manager<br/>Failure Notifications]
    end

    %% Client to Workflows
    APP --> CLIENT
    CLIENT --> WF_ENGINE
    WF_ENGINE --> LEARNING_WF
    WF_ENGINE --> IMAGE_WF
    WF_ENGINE --> DATA_WF
    WF_ENGINE --> SECURITY_WF
    WF_ENGINE --> MONITORING_WF
    WF_ENGINE --> BACKUP_WF
    WF_ENGINE --> SYNC_WF
    WF_ENGINE --> HEALTH_WF

    %% Workflows to Activities
    LEARNING_WF --> VALIDATE_ACT
    LEARNING_WF --> OPENAI_ACT
    LEARNING_WF --> AUDIT_ACT
    
    IMAGE_WF --> VALIDATE_ACT
    IMAGE_WF --> OPENAI_ACT
    IMAGE_WF --> FILE_ACT
    
    DATA_WF --> VALIDATE_ACT
    DATA_WF --> DB_ACT
    DATA_WF --> FILE_ACT
    
    SECURITY_WF --> VALIDATE_ACT
    SECURITY_WF --> AUDIT_ACT
    SECURITY_WF --> EMAIL_ACT
    
    MONITORING_WF --> VALIDATE_ACT
    MONITORING_WF --> AUDIT_ACT
    
    BACKUP_WF --> ENCRYPT_ACT
    BACKUP_WF --> FILE_ACT
    
    SYNC_WF --> ENCRYPT_ACT
    SYNC_WF --> DB_ACT

    %% Activity Execution
    VALIDATE_ACT --> ACT_ENGINE
    OPENAI_ACT --> ACT_ENGINE
    DB_ACT --> ACT_ENGINE
    FILE_ACT --> ACT_ENGINE
    EMAIL_ACT --> ACT_ENGINE
    AUDIT_ACT --> ACT_ENGINE
    ENCRYPT_ACT --> ACT_ENGINE
    
    ACT_ENGINE --> ACT_QUEUE

    %% Worker Execution
    ACT_QUEUE --> WORKER_POOL
    WORKER_POOL --> WORKER1
    WORKER_POOL --> WORKER2
    WORKER_POOL --> WORKER3
    
    WORKER1 --> HEARTBEAT
    WORKER2 --> HEARTBEAT
    WORKER3 --> HEARTBEAT

    %% Temporal Server Communication
    CLIENT --> FRONTEND
    WORKER_POOL --> FRONTEND
    FRONTEND --> HISTORY
    FRONTEND --> MATCHING
    FRONTEND --> WORKER_SVC
    
    HISTORY --> WF_STATE
    MATCHING --> ACT_QUEUE

    %% Persistence
    HISTORY --> POSTGRES
    FRONTEND --> ELASTICSEARCH
    WORKER_SVC --> POSTGRES

    %% Governance Hooks
    FOUR_LAWS -.validates.-> VALIDATE_ACT
    AUDIT_LOG -.logs.-> AUDIT_ACT
    POLICY -.enforces.-> WF_ENGINE

    %% Monitoring
    WF_ENGINE --> METRICS
    ACT_ENGINE --> METRICS
    WORKER_POOL --> METRICS
    
    FRONTEND --> TRACES
    WORKER_POOL --> TRACES
    
    METRICS --> DASHBOARD
    TRACES --> DASHBOARD
    
    METRICS --> ALERTS
    HISTORY --> ALERTS

    %% Styling
    classDef clientClass fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef workflowClass fill:#065f46,stroke:#10b981,stroke-width:2px,color:#fff
    classDef activityClass fill:#7c2d12,stroke:#f97316,stroke-width:2px,color:#fff
    classDef workerClass fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#fff
    classDef serverClass fill:#dc2626,stroke:#ef4444,stroke-width:3px,color:#fff
    classDef persistClass fill:#0c4a6e,stroke:#0ea5e9,stroke-width:2px,color:#fff
    classDef govClass fill:#991b1b,stroke:#f87171,stroke-width:2px,color:#fff
    classDef monitorClass fill:#581c87,stroke:#c084fc,stroke-width:2px,color:#fff

    class APP,CLIENT clientClass
    class WF_ENGINE,LEARNING_WF,IMAGE_WF,DATA_WF,SECURITY_WF,MONITORING_WF,BACKUP_WF,SYNC_WF,HEALTH_WF,WF_STATE workflowClass
    class ACT_ENGINE,OPENAI_ACT,DB_ACT,FILE_ACT,EMAIL_ACT,VALIDATE_ACT,AUDIT_ACT,ENCRYPT_ACT,ACT_QUEUE activityClass
    class WORKER_POOL,WORKER1,WORKER2,WORKER3,HEARTBEAT workerClass
    class FRONTEND,HISTORY,MATCHING,WORKER_SVC serverClass
    class POSTGRES,ELASTICSEARCH,CASSANDRA persistClass
    class FOUR_LAWS,AUDIT_LOG,POLICY govClass
    class METRICS,TRACES,DASHBOARD,ALERTS monitorClass
```

## Temporal Workflow System

### Core Concepts

**Workflows**: Deterministic, long-running business logic

```python
# src/app/temporal/workflows.py
from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta

@workflow.defn
class LearningRequestWorkflow:
    """Long-running workflow for learning approval"""
    
    @workflow.run
    async def run(self, request: dict) -> dict:
        """
        Workflow execution:
        1. Validate with governance
        2. Call OpenAI for learning path
        3. Request human approval
        4. Store approved knowledge
        """
        
        # Step 1: Governance validation (activity)
        is_valid = await workflow.execute_activity(
            validate_governance,
            request,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        
        if not is_valid:
            return {"status": "denied", "reason": "Governance validation failed"}
        
        # Step 2: Generate learning path (activity with retry)
        learning_path = await workflow.execute_activity(
            generate_learning_path,
            request["topic"],
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=30),
                maximum_attempts=5
            )
        )
        
        # Step 3: Wait for human approval (signal)
        await workflow.wait_condition(lambda: self.approval_received)
        
        # Step 4: Store knowledge (activity)
        stored = await workflow.execute_activity(
            store_knowledge,
            learning_path,
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        return {"status": "approved", "knowledge_id": stored["id"]}
    
    @workflow.signal
    def approve(self):
        """Signal to approve learning request"""
        self.approval_received = True
    
    @workflow.signal
    def deny(self):
        """Signal to deny learning request"""
        self.approval_received = False
        workflow.continue_as_new()  # Restart workflow
```

**Activities**: Side-effectful operations with retry logic

```python
# src/app/temporal/activities.py
from temporalio import activity
import openai

@activity.defn
async def validate_governance(request: dict) -> bool:
    """Activity: Validate request against FourLaws"""
    from app.core.ai_systems import FourLaws
    
    four_laws = FourLaws()
    is_allowed, reason = four_laws.validate_action(
        request["action"],
        request.get("context", {})
    )
    
    if not is_allowed:
        activity.logger.warning(f"Governance denied: {reason}")
    
    return is_allowed

@activity.defn
async def generate_learning_path(topic: str) -> dict:
    """Activity: Call OpenAI to generate learning path"""
    activity.logger.info(f"Generating learning path for: {topic}")
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a learning path generator."
            }, {
                "role": "user",
                "content": f"Create a learning path for: {topic}"
            }]
        )
        
        return {
            "topic": topic,
            "path": response.choices[0].message.content,
            "model": "gpt-4"
        }
    except Exception as e:
        activity.logger.error(f"OpenAI API error: {e}")
        raise  # Temporal will retry based on RetryPolicy

@activity.defn
async def store_knowledge(knowledge: dict) -> dict:
    """Activity: Store knowledge in database"""
    from app.core.ai_systems import MemoryExpansionSystem
    
    memory = MemoryExpansionSystem()
    knowledge_id = memory.add_knowledge(
        content=knowledge["path"],
        category="learning_paths",
        metadata={"topic": knowledge["topic"]}
    )
    
    return {"id": knowledge_id, "stored_at": datetime.now().isoformat()}
```

### Worker Configuration

**Multi-Worker Deployment**

```python
# src/app/temporal/worker.py
from temporalio.client import Client
from temporalio.worker import Worker

async def main():
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Create workers for different task queues
    workflow_worker = Worker(
        client,
        task_queue="workflows",
        workflows=[
            LearningRequestWorkflow,
            ImageGenerationWorkflow,
            DataAnalysisWorkflow,
            SecurityAuditWorkflow
        ],
        activities=[
            validate_governance,
            generate_learning_path,
            store_knowledge,
            generate_image,
            analyze_data,
            audit_security
        ]
    )
    
    # Long-running worker (different queue)
    monitoring_worker = Worker(
        client,
        task_queue="monitoring",
        workflows=[
            MonitoringWorkflow,
            BackupWorkflow,
            SyncWorkflow,
            HealthCheckWorkflow
        ],
        activities=[
            check_health,
            create_backup,
            sync_to_cloud,
            send_alert
        ]
    )
    
    # Run workers concurrently
    await asyncio.gather(
        workflow_worker.run(),
        monitoring_worker.run()
    )

if __name__ == "__main__":
    asyncio.run(main())
```

### Workflow Patterns

**1. Saga Pattern (Compensating Transactions)**

```python
@workflow.defn
class DataAnalysisSaga:
    """Saga pattern for multi-step data analysis with rollback"""
    
    @workflow.run
    async def run(self, analysis_request: dict) -> dict:
        compensations = []
        
        try:
            # Step 1: Load data
            data = await workflow.execute_activity(load_data, ...)
            compensations.append(lambda: delete_temp_data(data["temp_id"]))
            
            # Step 2: Transform data
            transformed = await workflow.execute_activity(transform_data, data)
            compensations.append(lambda: revert_transformation(transformed["id"]))
            
            # Step 3: Analyze
            results = await workflow.execute_activity(analyze, transformed)
            
            # Step 4: Store results
            stored = await workflow.execute_activity(store_results, results)
            
            return stored
        
        except Exception as e:
            # Rollback all completed steps
            for compensation in reversed(compensations):
                await workflow.execute_activity(compensation)
            raise
```

**2. Parent-Child Workflows**

```python
@workflow.defn
class ParentWorkflow:
    """Orchestrates multiple child workflows"""
    
    @workflow.run
    async def run(self, tasks: list[dict]) -> list[dict]:
        # Start child workflows in parallel
        child_handles = []
        for task in tasks:
            handle = await workflow.start_child_workflow(
                ChildWorkflow.run,
                task,
                id=f"child-{task['id']}"
            )
            child_handles.append(handle)
        
        # Wait for all to complete
        results = await asyncio.gather(*[
            handle.result() for handle in child_handles
        ])
        
        return results

@workflow.defn
class ChildWorkflow:
    """Individual task execution"""
    
    @workflow.run
    async def run(self, task: dict) -> dict:
        result = await workflow.execute_activity(process_task, task)
        return result
```

**3. Cron Workflows (Scheduled)**

```python
@workflow.defn
class DailyBackupWorkflow:
    """Runs daily at 2 AM UTC"""
    
    @workflow.run
    async def run(self) -> dict:
        # Create backup
        backup_path = await workflow.execute_activity(
            create_backup,
            start_to_close_timeout=timedelta(hours=1)
        )
        
        # Encrypt backup
        encrypted_path = await workflow.execute_activity(
            encrypt_file,
            backup_path
        )
        
        # Upload to cloud
        cloud_url = await workflow.execute_activity(
            upload_to_s3,
            encrypted_path
        )
        
        # Send notification
        await workflow.execute_activity(
            send_email,
            {
                "to": "admin@project-ai.com",
                "subject": "Daily Backup Complete",
                "body": f"Backup uploaded to {cloud_url}"
            }
        )
        
        return {"backup_url": cloud_url}

# Start cron workflow
client = await Client.connect("localhost:7233")
await client.start_workflow(
    DailyBackupWorkflow.run,
    id="daily-backup",
    task_queue="monitoring",
    cron_schedule="0 2 * * *"  # Daily at 2 AM UTC
)
```

### Governance Integration

**Pre-Activity Governance Hook**

```python
# src/app/temporal/governance_integration.py
from temporalio.worker import WorkflowInterceptor, ActivityInboundInterceptor

class GovernanceInterceptor(ActivityInboundInterceptor):
    """Intercept all activities for governance validation"""
    
    async def execute_activity(self, input):
        # Extract activity parameters
        activity_name = input.activity_name
        args = input.args
        
        # Validate with FourLaws
        from app.core.ai_systems import FourLaws
        four_laws = FourLaws()
        
        is_allowed, reason = four_laws.validate_action(
            activity_name,
            context={"args": args}
        )
        
        if not is_allowed:
            raise ConstitutionalViolation(
                f"Activity {activity_name} denied: {reason}"
            )
        
        # Proceed with activity execution
        result = await super().execute_activity(input)
        
        # Audit log successful execution
        audit_log.record({
            "activity": activity_name,
            "args": args,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        return result

# Register interceptor in worker
worker = Worker(
    client,
    task_queue="workflows",
    workflows=[...],
    activities=[...],
    interceptors=[GovernanceInterceptor()]
)
```

### Monitoring & Observability

**Prometheus Metrics**

```python
# Expose Temporal metrics
from prometheus_client import Counter, Histogram, start_http_server

workflow_starts = Counter(
    'temporal_workflow_starts_total',
    'Total workflow starts',
    ['workflow_type']
)

workflow_duration = Histogram(
    'temporal_workflow_duration_seconds',
    'Workflow execution duration',
    ['workflow_type']
)

activity_failures = Counter(
    'temporal_activity_failures_total',
    'Total activity failures',
    ['activity_name', 'error_type']
)

# Start metrics server
start_http_server(9090)
```

**Jaeger Tracing**

```python
# Distributed tracing integration
from opentelemetry import trace
from opentelemetry.exporter.jaeger import JaegerExporter
from temporalio.contrib.opentelemetry import TracingInterceptor

# Configure Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Add tracing interceptor
worker = Worker(
    client,
    task_queue="workflows",
    workflows=[...],
    activities=[...],
    interceptors=[TracingInterceptor()]
)
```

### Deployment Architecture

**Self-Hosted Temporal Server**

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgresql:
    image: postgres:14
    environment:
      POSTGRES_USER: temporal
      POSTGRES_PASSWORD: temporal
      POSTGRES_DB: temporal
    volumes:
      - temporal_postgres:/var/lib/postgresql/data

  elasticsearch:
    image: elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - temporal_elasticsearch:/usr/share/elasticsearch/data

  temporal:
    image: temporalio/auto-setup:1.22.0
    depends_on:
      - postgresql
      - elasticsearch
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=temporal
      - POSTGRES_PWD=temporal
      - POSTGRES_SEEDS=postgresql
      - DYNAMIC_CONFIG_FILE_PATH=config/dynamicconfig/development.yaml
      - ENABLE_ES=true
      - ES_SEEDS=elasticsearch
      - ES_VERSION=v8
    ports:
      - "7233:7233"  # gRPC
    volumes:
      - ./temporal-config:/etc/temporal/config/dynamicconfig

  temporal-ui:
    image: temporalio/ui:2.10.0
    depends_on:
      - temporal
    environment:
      - TEMPORAL_ADDRESS=temporal:7233
    ports:
      - "8080:8080"

volumes:
  temporal_postgres:
  temporal_elasticsearch:
```

### Integration with Main Application

**Desktop Integration**

```python
# src/app/main.py
from temporalio.client import Client

async def init_temporal():
    """Initialize Temporal client"""
    global temporal_client
    temporal_client = await Client.connect("localhost:7233")

# In LeatherBookDashboard
async def request_learning(self, topic: str):
    """Start learning request workflow"""
    handle = await temporal_client.start_workflow(
        LearningRequestWorkflow.run,
        {"topic": topic, "user": self.username},
        id=f"learning-{topic}-{datetime.now().timestamp()}",
        task_queue="workflows"
    )
    
    # Show workflow ID to user
    self.show_message(f"Learning request started: {handle.id}")
    
    # Optionally wait for result
    result = await handle.result()
    self.show_message(f"Learning complete: {result}")
```

**Web API Integration**

```python
# web/backend/app/routes.py
from temporalio.client import Client

@app.post("/api/learning-request")
async def create_learning_request(request: dict):
    """Start learning workflow from web API"""
    client = await Client.connect("localhost:7233")
    
    handle = await client.start_workflow(
        LearningRequestWorkflow.run,
        request,
        id=f"web-learning-{request['user_id']}-{time.time()}",
        task_queue="workflows"
    )
    
    return {
        "workflow_id": handle.id,
        "status": "started"
    }

@app.get("/api/learning-request/{workflow_id}")
async def get_learning_status(workflow_id: str):
    """Query workflow status"""
    client = await Client.connect("localhost:7233")
    
    handle = client.get_workflow_handle(workflow_id)
    description = await handle.describe()
    
    return {
        "workflow_id": workflow_id,
        "status": description.status,
        "start_time": description.start_time,
        "execution_time": description.execution_time
    }
```

## Benefits of Temporal Integration

1. **Reliability**: Automatic retries, timeouts, and failure handling
2. **Durability**: Workflow state persisted across crashes
3. **Scalability**: Horizontal scaling of workers
4. **Observability**: Built-in metrics, tracing, and UI
5. **Governance**: Pre/post-activity hooks for validation
6. **Long-Running**: Workflows can run for days/weeks/months
7. **Saga Pattern**: Built-in support for compensating transactions
8. **Versioning**: Deploy new workflow versions without downtime
