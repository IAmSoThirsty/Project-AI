# Temporal.io Workflow Orchestration

## Overview

Project-AI uses Temporal.io for durable workflow orchestration, enabling long-running, fault-tolerant business processes with automatic retries, versioning, and state management.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Temporal Architecture                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐                        ┌──────────────┐       │
│  │  Application │────────────────────────▶│   Temporal   │       │
│  │   (Client)   │  Start/Signal/Query     │   Frontend   │       │
│  └──────────────┘                        └──────┬───────┘       │
│                                                   │               │
│  ┌──────────────┐                        ┌──────▼───────┐       │
│  │   Workers    │◀───────────────────────│   History    │       │
│  │  (Execute    │   Task Assignment      │   Service    │       │
│  │  Activities) │                        └──────┬───────┘       │
│  └──────────────┘                               │               │
│         │                                ┌──────▼───────┐       │
│         │                                │   Matching   │       │
│         │                                │   Service    │       │
│         │                                └──────┬───────┘       │
│         │                                       │               │
│         └───────────────────────────────┬───────┘               │
│                                         │                       │
│                                 ┌───────▼────────┐              │
│                                 │   PostgreSQL   │              │
│                                 │  (Persistence) │              │
│                                 └────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Core Concepts

### Workflows
Durable functions that coordinate activities. Workflows are deterministic and automatically retried on failure.

### Activities
Individual units of work that can fail and be retried independently. Activities can perform non-deterministic operations like API calls.

### Task Queues
Logical groupings of work that workers poll for tasks to execute.

### Signals
External messages sent to running workflows to change their behavior.

### Queries
Synchronous calls to read workflow state without changing it.

## Deployment Configuration

### Docker Compose Deployment

```yaml
# docker-compose.temporal.yml
version: '3.8'

services:
  # PostgreSQL for Temporal persistence
  temporal-postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_PASSWORD: temporal
      POSTGRES_USER: temporal
      POSTGRES_DB: temporal
    volumes:
      - temporal_postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U temporal"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Temporal server (auto-setup)
  temporal:
    image: temporalio/auto-setup:1.22.0
    depends_on:
      temporal-postgres:
        condition: service_healthy
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=temporal
      - POSTGRES_PWD=temporal
      - POSTGRES_SEEDS=temporal-postgres
      - DYNAMIC_CONFIG_FILE_PATH=config/dynamicconfig/development-sql.yaml
    ports:
      - "7233:7233"  # gRPC frontend
      - "8233:8233"  # HTTP API
    volumes:
      - ./temporal/dynamicconfig:/etc/temporal/config/dynamicconfig
    healthcheck:
      test: ["CMD", "tctl", "--address", "temporal:7233", "cluster", "health"]
      interval: 10s
      timeout: 5s
      retries: 10

  # Temporal Web UI
  temporal-ui:
    image: temporalio/ui:2.20.0
    depends_on:
      temporal:
        condition: service_healthy
    environment:
      - TEMPORAL_ADDRESS=temporal:7233
      - TEMPORAL_CORS_ORIGINS=http://localhost:3000
    ports:
      - "8080:8080"

  # Temporal admin tools
  temporal-admin-tools:
    image: temporalio/admin-tools:1.22.0
    depends_on:
      temporal:
        condition: service_healthy
    environment:
      - TEMPORAL_CLI_ADDRESS=temporal:7233
    stdin_open: true
    tty: true

volumes:
  temporal_postgres_data:
```

### Kubernetes Deployment

```yaml
# temporal-deployment.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: temporal

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: temporal-config
  namespace: temporal
data:
  development-sql.yaml: |
    system.forceSearchAttributesCacheRefreshOnRead:
      - value: true
        constraints: {}
    limit.maxIDLength:
      - value: 255
        constraints: {}

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: temporal
  namespace: temporal
spec:
  replicas: 3
  selector:
    matchLabels:
      app: temporal
  template:
    metadata:
      labels:
        app: temporal
    spec:
      containers:
      - name: temporal
        image: temporalio/server:1.22.0
        env:
        - name: DB
          value: postgresql
        - name: DB_PORT
          value: "5432"
        - name: POSTGRES_SEEDS
          value: postgres-service
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: username
        - name: POSTGRES_PWD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: DYNAMIC_CONFIG_FILE_PATH
          value: /etc/temporal/config/dynamicconfig/development-sql.yaml
        ports:
        - containerPort: 7233
          name: frontend
        - containerPort: 8233
          name: http
        volumeMounts:
        - name: config
          mountPath: /etc/temporal/config/dynamicconfig
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - tctl --address temporal:7233 cluster health
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - tctl --address temporal:7233 cluster health
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: temporal-config

---
apiVersion: v1
kind: Service
metadata:
  name: temporal
  namespace: temporal
spec:
  type: ClusterIP
  selector:
    app: temporal
  ports:
  - port: 7233
    targetPort: 7233
    name: frontend
  - port: 8233
    targetPort: 8233
    name: http
```

## Python Client Configuration

```python
# src/app/temporal/__init__.py
from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker
import os

class TemporalClientFactory:
    """Factory for creating Temporal clients"""
    
    @staticmethod
    async def create_client(
        host: str = None,
        namespace: str = "default",
        use_tls: bool = False
    ) -> Client:
        """Create a Temporal client"""
        host = host or os.getenv("TEMPORAL_HOST", "localhost:7233")
        
        # TLS configuration for production
        tls_config = None
        if use_tls:
            tls_config = TLSConfig(
                client_cert=open(os.getenv("TEMPORAL_CLIENT_CERT")).read(),
                client_private_key=open(os.getenv("TEMPORAL_CLIENT_KEY")).read(),
                server_root_ca_cert=open(os.getenv("TEMPORAL_SERVER_CA")).read()
            )
        
        client = await Client.connect(
            host,
            namespace=namespace,
            tls=tls_config
        )
        
        return client
    
    @staticmethod
    async def create_worker(
        client: Client,
        task_queue: str,
        workflows: list,
        activities: list,
        max_concurrent_workflow_tasks: int = 100,
        max_concurrent_activities: int = 50
    ) -> Worker:
        """Create a Temporal worker"""
        return Worker(
            client,
            task_queue=task_queue,
            workflows=workflows,
            activities=activities,
            max_concurrent_workflow_tasks=max_concurrent_workflow_tasks,
            max_concurrent_activities=max_concurrent_activities
        )

# Usage
async def initialize_temporal():
    """Initialize Temporal client and workers"""
    client = await TemporalClientFactory.create_client(
        host="temporal:7233",
        namespace="project-ai"
    )
    
    return client
```

## Workflow Registration

```python
# src/app/temporal/workflows/registry.py
from temporalio import workflow
from typing import Dict, List, Type

class WorkflowRegistry:
    """Central registry for all workflows"""
    
    _workflows: Dict[str, Type] = {}
    
    @classmethod
    def register(cls, workflow_class: Type):
        """Register a workflow class"""
        cls._workflows[workflow_class.__name__] = workflow_class
        return workflow_class
    
    @classmethod
    def get_all_workflows(cls) -> List[Type]:
        """Get all registered workflows"""
        return list(cls._workflows.values())
    
    @classmethod
    def get_workflow(cls, name: str) -> Type:
        """Get workflow by name"""
        return cls._workflows.get(name)

# Decorator for registering workflows
def registered_workflow(cls):
    """Decorator to register a workflow"""
    WorkflowRegistry.register(cls)
    return workflow.defn(cls)
```

## Task Queue Configuration

```python
# src/app/temporal/task_queues.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class TaskQueueConfig:
    """Configuration for a task queue"""
    name: str
    max_concurrent_workflow_tasks: int
    max_concurrent_activities: int
    max_workers: int
    rate_limit: Optional[int] = None  # Tasks per second

class TaskQueues:
    """Central task queue definitions"""
    
    # High-priority workflows (image generation, AI inference)
    HIGH_PRIORITY = TaskQueueConfig(
        name="project-ai-high-priority",
        max_concurrent_workflow_tasks=100,
        max_concurrent_activities=50,
        max_workers=5,
        rate_limit=100
    )
    
    # Standard workflows (learning paths, data analysis)
    STANDARD = TaskQueueConfig(
        name="project-ai-standard",
        max_concurrent_workflow_tasks=50,
        max_concurrent_activities=25,
        max_workers=3,
        rate_limit=50
    )
    
    # Background tasks (cleanup, maintenance)
    BACKGROUND = TaskQueueConfig(
        name="project-ai-background",
        max_concurrent_workflow_tasks=10,
        max_concurrent_activities=5,
        max_workers=1,
        rate_limit=10
    )
    
    # Scheduled tasks (cron-like)
    SCHEDULED = TaskQueueConfig(
        name="project-ai-scheduled",
        max_concurrent_workflow_tasks=5,
        max_concurrent_activities=5,
        max_workers=1,
        rate_limit=None
    )
    
    @classmethod
    def get_all_queues(cls) -> List[TaskQueueConfig]:
        """Get all task queue configurations"""
        return [
            cls.HIGH_PRIORITY,
            cls.STANDARD,
            cls.BACKGROUND,
            cls.SCHEDULED
        ]
```

## Monitoring and Metrics

```python
# src/app/temporal/monitoring.py
from prometheus_client import Counter, Histogram, Gauge
from temporalio import workflow, activity
import functools
import time

# Workflow metrics
WORKFLOW_EXECUTIONS = Counter(
    'temporal_workflow_execution_count',
    'Total workflow executions',
    ['workflow_type', 'status']
)

WORKFLOW_DURATION = Histogram(
    'temporal_workflow_duration_seconds',
    'Workflow execution duration',
    ['workflow_type'],
    buckets=[1.0, 10.0, 60.0, 300.0, 1800.0, 3600.0]
)

ACTIVE_WORKFLOWS = Gauge(
    'temporal_active_workflows',
    'Number of active workflows',
    ['workflow_type']
)

# Activity metrics
ACTIVITY_EXECUTIONS = Counter(
    'temporal_activity_execution_count',
    'Total activity executions',
    ['activity_name', 'status']
)

ACTIVITY_DURATION = Histogram(
    'temporal_activity_duration_seconds',
    'Activity execution duration',
    ['activity_name'],
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0]
)

# Task queue metrics
TASK_QUEUE_DEPTH = Gauge(
    'temporal_task_queue_depth',
    'Number of tasks in queue',
    ['queue_name']
)

TASK_QUEUE_PROCESSED_RATE = Counter(
    'temporal_task_queue_processed_total',
    'Total tasks processed from queue',
    ['queue_name']
)

def track_workflow_metrics(f):
    """Decorator to track workflow metrics"""
    @functools.wraps(f)
    async def wrapper(self, *args, **kwargs):
        workflow_type = self.__class__.__name__
        start_time = time.time()
        
        ACTIVE_WORKFLOWS.labels(workflow_type=workflow_type).inc()
        status = "success"
        
        try:
            result = await f(self, *args, **kwargs)
            return result
        except Exception as e:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            WORKFLOW_DURATION.labels(workflow_type=workflow_type).observe(duration)
            WORKFLOW_EXECUTIONS.labels(workflow_type=workflow_type, status=status).inc()
            ACTIVE_WORKFLOWS.labels(workflow_type=workflow_type).dec()
    
    return wrapper

def track_activity_metrics(f):
    """Decorator to track activity metrics"""
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        activity_name = f.__name__
        start_time = time.time()
        status = "success"
        
        try:
            result = await f(*args, **kwargs)
            return result
        except Exception as e:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            ACTIVITY_DURATION.labels(activity_name=activity_name).observe(duration)
            ACTIVITY_EXECUTIONS.labels(activity_name=activity_name, status=status).inc()
    
    return wrapper
```

## Connection Pooling

```python
# src/app/temporal/connection_pool.py
from temporalio.client import Client
from typing import Optional
import asyncio

class TemporalConnectionPool:
    """Connection pool for Temporal clients"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self._pool: List[Client] = []
        self._available: asyncio.Queue = asyncio.Queue()
        self._lock = asyncio.Lock()
    
    async def get_client(self) -> Client:
        """Get a client from the pool"""
        if not self._available.empty():
            return await self._available.get()
        
        async with self._lock:
            if len(self._pool) < self.max_connections:
                client = await TemporalClientFactory.create_client()
                self._pool.append(client)
                return client
        
        # Wait for an available client
        return await self._available.get()
    
    async def release_client(self, client: Client):
        """Release a client back to the pool"""
        await self._available.put(client)
    
    async def close_all(self):
        """Close all connections in the pool"""
        for client in self._pool:
            await client.close()
        self._pool.clear()

# Global connection pool
_connection_pool: Optional[TemporalConnectionPool] = None

async def get_temporal_client() -> Client:
    """Get a Temporal client from the pool"""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = TemporalConnectionPool(max_connections=10)
    return await _connection_pool.get_client()

async def release_temporal_client(client: Client):
    """Release a Temporal client back to the pool"""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.release_client(client)
```

## Health Checks

```python
# src/app/temporal/health.py
from temporalio.client import Client
from typing import Dict
import asyncio

class TemporalHealthCheck:
    """Health check for Temporal connection"""
    
    def __init__(self, client: Client):
        self.client = client
    
    async def check_health(self) -> Dict:
        """Check Temporal server health"""
        try:
            # Try to describe the namespace
            await asyncio.wait_for(
                self.client.service.describe_namespace(namespace=self.client.namespace),
                timeout=5.0
            )
            return {
                "status": "healthy",
                "namespace": self.client.namespace,
                "host": self.client.service_client.options.host
            }
        except asyncio.TimeoutError:
            return {
                "status": "unhealthy",
                "error": "Connection timeout"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
```

## Related Documentation

- [Temporal Workflows](./temporal_workflows.md) - Workflow definitions and activities
- [Workflow Patterns](./workflow_patterns.md) - Saga pattern, compensation, retry policies
- [Task Queues](./task_queues.md) - Queue configuration, worker pools, rate limiting

## External Resources

- [Temporal Documentation](https://docs.temporal.io/)
- [Python SDK Documentation](https://python.temporal.io/)
- [Best Practices](https://docs.temporal.io/application-development/best-practices)
