# Temporal Worker & Client - Comprehensive Documentation
## Project-AI Worker Infrastructure and Client Management

---

**Document Classification:** TIER-1 PRODUCTION SYSTEM  
**Version:** 1.0  
**Last Updated:** 2025-01-XX  
**Status:** PRODUCTION-READY | OPERATIONAL  
**Compliance:** Principal Architect Implementation Standard  
**Author:** AGENT-033 (Temporal Workflows Documentation Specialist)

---

## TABLE OF CONTENTS

### PART A: WORKER DOCUMENTATION
1. [Worker Overview](#worker-overview)
2. [Worker Architecture](#worker-architecture)
3. [Worker Configuration](#worker-configuration)
4. [Worker Deployment](#worker-deployment)
5. [Worker Operations](#worker-operations)
6. [Worker Monitoring](#worker-monitoring)

### PART B: CLIENT DOCUMENTATION
7. [Client Manager Overview](#client-manager-overview)
8. [Client Configuration](#client-configuration)
9. [Connection Management](#connection-management)
10. [Cloud Integration](#cloud-integration)
11. [Production Best Practices](#production-best-practices)

---

# PART A: WORKER DOCUMENTATION

## WORKER OVERVIEW

### Purpose

The Temporal Worker is a **long-running service** that polls Temporal Server for workflow and activity tasks, executes them, and reports results. Workers are the execution engine for all Temporal workflows in Project-AI.

### Key Concepts

**Worker:** Background process that executes workflows and activities  
**Task Queue:** Named queue where workers poll for tasks (`project-ai-tasks`)  
**Polling:** Workers continuously poll Temporal Server for tasks  
**Concurrency:** Workers execute multiple tasks in parallel

### Worker Responsibilities

```
┌─────────────────────────────────────────────────────────────┐
│                     TEMPORAL WORKER                          │
│                                                              │
│  1. Connect to Temporal Server                              │
│  2. Register workflows (5) and activities (20)              │
│  3. Poll task queue for workflow/activity tasks             │
│  4. Execute tasks in parallel (up to 50 concurrent)         │
│  5. Report results back to Temporal Server                  │
│  6. Handle graceful shutdown (SIGTERM/SIGINT)               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## WORKER ARCHITECTURE

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   TEMPORAL SERVER                            │
│                   (localhost:7233)                           │
└───────────────────┬─────────────────────────────────────────┘
                    │
                    │ gRPC Connection
                    │
┌───────────────────▼─────────────────────────────────────────┐
│              TEMPORAL WORKER PROCESS                         │
│              (src/app/temporal/worker.py)                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         TemporalClientManager                       │    │
│  │  - connect() / disconnect()                         │    │
│  │  - create_worker()                                  │    │
│  │  - run_worker()                                     │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────┐    │
│  │              Worker Instance                        │    │
│  │  - Task Queue: "project-ai-tasks"                  │    │
│  │  - Max Concurrent Activities: 50                   │    │
│  │  - Max Concurrent Workflows: 50                    │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│        ┌──────────┴──────────┐                              │
│        │                     │                              │
│  ┌─────▼──────┐      ┌──────▼──────┐                       │
│  │ WORKFLOWS  │      │ ACTIVITIES  │                       │
│  │   (5x)     │      │    (20x)    │                       │
│  │            │      │             │                       │
│  │ - AILearn  │      │ - validate  │                       │
│  │ - ImageGen │      │ - process   │                       │
│  │ - DataAnal │      │ - store     │                       │
│  │ - MemoryExp│      │ - ...       │                       │
│  │ - CrisisRes│      │             │                       │
│  └────────────┘      └─────────────┘                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Worker Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│ 1. STARTUP                                                   │
│    python -m src.app.temporal.worker                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. INITIALIZATION                                            │
│    ├─ Load configuration (host, namespace, task_queue)      │
│    ├─ Create TemporalClientManager                          │
│    └─ Setup signal handlers (SIGINT, SIGTERM)               │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. CONNECTION                                                │
│    ├─ await manager.connect()                               │
│    ├─ Connect to Temporal Server (gRPC)                     │
│    └─ Verify connection health                              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. WORKER CREATION                                           │
│    ├─ Collect all workflows (5)                             │
│    ├─ Collect all activities (20)                           │
│    ├─ Create worker instance                                │
│    └─ Register with task queue                              │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. RUNNING                                                   │
│    ├─ Poll for workflow tasks                               │
│    ├─ Poll for activity tasks                               │
│    ├─ Execute tasks concurrently (up to 50)                 │
│    └─ Report results to Temporal Server                     │
│    (Continues until shutdown signal)                         │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼ (SIGTERM/SIGINT)
┌─────────────────────────────────────────────────────────────┐
│ 6. GRACEFUL SHUTDOWN                                         │
│    ├─ Stop accepting new tasks                              │
│    ├─ Complete in-progress tasks                            │
│    ├─ Cancel worker task                                    │
│    └─ Disconnect from Temporal Server                       │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. EXIT                                                      │
│    sys.exit(exit_code)                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## WORKER CONFIGURATION

### Configuration File

**File:** `src/app/temporal/config.py`

```python
class TemporalConfig(BaseSettings):
    """Temporal.io configuration settings."""
    
    # Server Connection
    host: str = "localhost:7233"
    namespace: str = "default"
    task_queue: str = "project-ai-tasks"
    
    # Cloud Configuration
    cloud_namespace: str | None = None
    cloud_cert_path: Path | None = None
    cloud_key_path: Path | None = None
    cloud_api_key: str | None = None
    
    # Worker Configuration
    max_concurrent_activities: int = 50
    max_concurrent_workflows: int = 50
    worker_identity: str = "project-ai-worker"
    
    # Timeout Configuration (seconds)
    workflow_execution_timeout: int = 3600
    workflow_run_timeout: int = 1800
    activity_start_to_close_timeout: int = 300
    
    # Retry Policy
    max_retry_attempts: int = 3
    initial_retry_interval: int = 1
    max_retry_interval: int = 30
    
    class Config:
        env_prefix = "TEMPORAL_"
        env_file = ".env.temporal"
```

### Environment Variables

**File:** `.env.temporal` (optional)

```bash
# Server Connection
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=project-ai-tasks

# Worker Configuration
TEMPORAL_MAX_CONCURRENT_ACTIVITIES=50
TEMPORAL_MAX_CONCURRENT_WORKFLOWS=50
TEMPORAL_WORKER_IDENTITY=project-ai-worker

# Timeouts (seconds)
TEMPORAL_WORKFLOW_EXECUTION_TIMEOUT=3600
TEMPORAL_WORKFLOW_RUN_TIMEOUT=1800
TEMPORAL_ACTIVITY_START_TO_CLOSE_TIMEOUT=300

# Retry Policy
TEMPORAL_MAX_RETRY_ATTEMPTS=3
TEMPORAL_INITIAL_RETRY_INTERVAL=1
TEMPORAL_MAX_RETRY_INTERVAL=30

# Cloud Configuration (optional)
# TEMPORAL_CLOUD_NAMESPACE=my-namespace.a2b3c
# TEMPORAL_CLOUD_CERT_PATH=/path/to/cert.pem
# TEMPORAL_CLOUD_KEY_PATH=/path/to/key.pem
```

### Configuration Loading

```python
from app.temporal.config import get_temporal_config

# Load configuration
config = get_temporal_config()

# Access settings
print(config.host)  # "localhost:7233"
print(config.max_concurrent_activities)  # 50
print(config.is_cloud)  # False (if not using Temporal Cloud)
```

---

## WORKER DEPLOYMENT

### Local Development

**Start Worker (Development):**
```powershell
# Method 1: Direct execution
python -m src.app.temporal.worker

# Method 2: With environment file
python -m src.app.temporal.worker --env-file .env.temporal
```

**Output:**
```
2025-01-10 12:00:00 - INFO - Starting Project-AI Temporal Worker
2025-01-10 12:00:01 - INFO - Connected to Temporal server
2025-01-10 12:00:02 - INFO - Worker created with 5 workflows and 20 activities
2025-01-10 12:00:03 - INFO - Worker is running. Press Ctrl+C to stop.
```

### Production Deployment

#### Option 1: Systemd Service (Linux)

**File:** `/etc/systemd/system/temporal-worker.service`

```ini
[Unit]
Description=Project-AI Temporal Worker
After=network.target

[Service]
Type=simple
User=app-user
WorkingDirectory=/opt/project-ai
Environment="PYTHONPATH=/opt/project-ai"
ExecStart=/usr/bin/python3 -m src.app.temporal.worker
Restart=always
RestartSec=10

# Logging
StandardOutput=append:/var/log/temporal-worker/stdout.log
StandardError=append:/var/log/temporal-worker/stderr.log

# Graceful shutdown
KillSignal=SIGTERM
TimeoutStopSec=60

[Install]
WantedBy=multi-user.target
```

**Start Service:**
```bash
sudo systemctl start temporal-worker
sudo systemctl enable temporal-worker  # Auto-start on boot
sudo systemctl status temporal-worker
```

#### Option 2: Docker Container

**Dockerfile:** (Already exists in project root)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application
COPY src/ ./src/
COPY data/ ./data/

# Run worker
CMD ["python", "-m", "src.app.temporal.worker"]
```

**Docker Compose:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  temporal-worker:
    build: .
    container_name: project-ai-worker
    environment:
      - TEMPORAL_HOST=temporal-server:7233
      - TEMPORAL_NAMESPACE=default
      - TEMPORAL_MAX_CONCURRENT_ACTIVITIES=50
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    depends_on:
      - temporal-server
```

**Start Container:**
```powershell
docker-compose up -d temporal-worker
docker-compose logs -f temporal-worker
```

#### Option 3: Kubernetes Deployment

**File:** `k8s/temporal-worker-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: temporal-worker
  namespace: project-ai
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
        command: ["python", "-m", "src.app.temporal.worker"]
        env:
        - name: TEMPORAL_HOST
          value: "temporal-server.temporal.svc.cluster.local:7233"
        - name: TEMPORAL_NAMESPACE
          value: "default"
        - name: TEMPORAL_MAX_CONCURRENT_ACTIVITIES
          value: "50"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: temporal-worker-data
```

**Deploy:**
```bash
kubectl apply -f k8s/temporal-worker-deployment.yaml
kubectl get pods -n project-ai
kubectl logs -f deployment/temporal-worker -n project-ai
```

---

## WORKER OPERATIONS

### Starting the Worker

**Command:**
```powershell
python -m src.app.temporal.worker
```

**Verification:**
```powershell
# Check worker logs
Select-String -Path "logs/temporal-worker.log" -Pattern "Worker is running"

# Check Temporal UI
# Navigate to: http://localhost:8080
# Verify worker appears in "Workers" tab
```

### Stopping the Worker

**Graceful Shutdown:**
```powershell
# Send SIGTERM (Ctrl+C)
# Worker completes in-progress tasks, then exits

# Output:
# Received signal 2, initiating shutdown
# Worker stopped
# Worker shutdown complete
```

**Force Shutdown:**
```powershell
# Windows
Stop-Process -Name "python" -Force

# Linux
kill -9 <pid>
```

### Restarting the Worker

```powershell
# Systemd (Linux)
sudo systemctl restart temporal-worker

# Docker
docker-compose restart temporal-worker

# Manual
# 1. Stop worker (Ctrl+C)
# 2. Wait for graceful shutdown
# 3. Start worker again
python -m src.app.temporal.worker
```

### Scaling Workers

**Horizontal Scaling (Multiple Workers):**
```powershell
# Start multiple worker instances
# All workers poll the same task queue ("project-ai-tasks")
# Temporal distributes tasks across workers

# Terminal 1
python -m src.app.temporal.worker

# Terminal 2
python -m src.app.temporal.worker

# Terminal 3
python -m src.app.temporal.worker
```

**Configuration for Multiple Workers:**
```python
# worker1.py
manager = TemporalClientManager(worker_identity="worker-1")

# worker2.py
manager = TemporalClientManager(worker_identity="worker-2")

# worker3.py
manager = TemporalClientManager(worker_identity="worker-3")
```

**Vertical Scaling (Increase Concurrency):**
```python
# Increase max_concurrent_activities
worker = manager.create_worker(
    workflows=workflows,
    activities=activities,
    max_concurrent_activities=100,  # Increased from 50
    max_concurrent_workflow_tasks=100,
)
```

**Recommended Scaling Strategy:**

| Load | Workers | Concurrency/Worker | Total Concurrency |
|------|---------|-------------------|-------------------|
| Low | 1 | 50 | 50 |
| Medium | 2 | 50 | 100 |
| High | 3-5 | 100 | 300-500 |
| Very High | 5-10 | 100 | 500-1000 |

---

## WORKER MONITORING

### Health Checks

**Health Check Endpoint:**
```python
from app.temporal.client import TemporalClientManager

async def health_check():
    """Check worker health."""
    manager = TemporalClientManager()
    await manager.connect()
    
    is_healthy = await manager.health_check()
    if is_healthy:
        return {"status": "healthy", "worker": "running"}
    else:
        return {"status": "unhealthy", "worker": "connection_failed"}
```

**HTTP Health Check (for Kubernetes):**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    # Check worker health
    health_status = await health_check()
    return health_status
```

### Metrics

**Key Metrics to Monitor:**

| Metric | Description | Threshold | Action |
|--------|-------------|-----------|--------|
| **Worker Uptime** | Time since worker started | >99% | Alert if <99% |
| **Task Queue Depth** | Pending tasks in queue | <100 | Scale if >100 |
| **Activity Success Rate** | % of activities that succeed | >95% | Investigate if <95% |
| **Workflow Success Rate** | % of workflows that succeed | >98% | Alert if <98% |
| **Activity Duration** | P95 activity execution time | <timeout-10% | Increase timeout if close |
| **Worker CPU Usage** | Worker process CPU % | <80% | Scale if >80% |
| **Worker Memory Usage** | Worker process memory | <2GB | Scale if >2GB |

**Temporal UI Metrics:**
- Navigate to: `http://localhost:8080`
- View metrics in "Workflows" and "Task Queues" tabs

### Logging

**Log Levels:**
```python
# Configure logging in worker.py
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for verbose logging
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
```

**Log Locations:**
- **Development:** Console output
- **Production:** `/var/log/temporal-worker/` or `logs/temporal-worker.log`

**Log Rotation:**
```python
# Use RotatingFileHandler for log rotation
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    "logs/temporal-worker.log",
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
logger.addHandler(handler)
```

### Alerting

**Recommended Alerts:**

1. **Worker Down:**
   - Trigger: Worker process not running for >1 minute
   - Severity: CRITICAL
   - Action: Restart worker immediately

2. **High Task Queue Depth:**
   - Trigger: Queue depth >500 for >5 minutes
   - Severity: WARNING
   - Action: Scale workers

3. **High Failure Rate:**
   - Trigger: Workflow failure rate >5% for >10 minutes
   - Severity: WARNING
   - Action: Investigate failures

4. **Memory/CPU High:**
   - Trigger: Worker CPU >90% or Memory >80% for >5 minutes
   - Severity: WARNING
   - Action: Scale workers or optimize activities

---

# PART B: CLIENT DOCUMENTATION

## CLIENT MANAGER OVERVIEW

### Purpose

The `TemporalClientManager` class provides a **high-level interface** for connecting to Temporal Server, creating workers, and managing client lifecycle. It abstracts away low-level Temporal SDK details and provides a clean API for the application.

### Key Features

✅ **Connection Management:** Connect/disconnect to Temporal Server  
✅ **Worker Creation:** Create and configure workers  
✅ **Health Checks:** Verify server connection health  
✅ **Cloud Support:** TLS/mTLS for Temporal Cloud  
✅ **Context Manager:** Async context manager for resource cleanup

### Class API

```python
class TemporalClientManager:
    def __init__(
        self,
        target_host: str | None = None,
        namespace: str = "default",
        task_queue: str = "project-ai-tasks",
        tls_config: TLSConfig | None = None,
    )
    
    async def connect(self) -> Client
    async def disconnect(self)
    
    def create_worker(
        self,
        workflows: list,
        activities: list,
        max_concurrent_activities: int = 100,
        max_concurrent_workflow_tasks: int = 100,
    ) -> Worker
    
    async def run_worker(self, worker: Worker)
    async def health_check(self) -> bool
    
    @classmethod
    async def create_cloud_client(
        cls,
        namespace: str,
        client_cert_path: str,
        client_key_path: str,
        api_key: str | None = None,
    ) -> "TemporalClientManager"
```

---

## CLIENT CONFIGURATION

### Basic Configuration (Local)

```python
from app.temporal.client import TemporalClientManager

# Default configuration (localhost:7233)
manager = TemporalClientManager()

# Custom configuration
manager = TemporalClientManager(
    target_host="temporal-server:7233",
    namespace="production",
    task_queue="project-ai-prod-tasks"
)
```

### Environment-Based Configuration

```python
import os
from app.temporal.client import TemporalClientManager

manager = TemporalClientManager(
    target_host=os.getenv("TEMPORAL_HOST", "localhost:7233"),
    namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
    task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "project-ai-tasks"),
)
```

### Configuration with Pydantic Settings

```python
from app.temporal.config import get_temporal_config
from app.temporal.client import TemporalClientManager

config = get_temporal_config()

manager = TemporalClientManager(
    target_host=config.host,
    namespace=config.namespace,
    task_queue=config.task_queue,
)
```

---

## CONNECTION MANAGEMENT

### Connect to Temporal Server

```python
from app.temporal.client import TemporalClientManager

# Create manager
manager = TemporalClientManager()

# Connect to server
try:
    await manager.connect()
    print("Connected to Temporal server")
except ConnectionError as e:
    print(f"Failed to connect: {e}")
```

### Disconnect from Server

```python
# Disconnect (cleanup resources)
await manager.disconnect()
```

### Using Context Manager (Recommended)

```python
from app.temporal.client import TemporalClientManager

# Automatic connect/disconnect
async with TemporalClientManager() as manager:
    # Use manager here
    worker = manager.create_worker(workflows, activities)
    await manager.run_worker(worker)
# Automatically disconnects on exit
```

### Health Check

```python
# Check connection health
is_healthy = await manager.health_check()

if is_healthy:
    print("Connection is healthy")
else:
    print("Connection is unhealthy")
    # Attempt reconnection
    await manager.disconnect()
    await manager.connect()
```

---

## CLOUD INTEGRATION

### Temporal Cloud Setup

**Prerequisites:**
1. Temporal Cloud account and namespace
2. Client certificate and private key
3. Optional: API key for authentication

### Create Cloud Client

```python
from app.temporal.client import TemporalClientManager

# Create client for Temporal Cloud
manager = await TemporalClientManager.create_cloud_client(
    namespace="my-namespace.a2b3c",
    client_cert_path="/path/to/client-cert.pem",
    client_key_path="/path/to/client-key.pem",
    api_key="optional-api-key"
)

# Manager is already connected
worker = manager.create_worker(workflows, activities)
await manager.run_worker(worker)
```

### Cloud Configuration Files

**Environment Variables:**
```bash
TEMPORAL_CLOUD_NAMESPACE=my-namespace.a2b3c
TEMPORAL_CLOUD_CERT_PATH=/certs/client-cert.pem
TEMPORAL_CLOUD_KEY_PATH=/certs/client-key.pem
TEMPORAL_CLOUD_API_KEY=optional-api-key
```

**Code:**
```python
import os
from app.temporal.client import TemporalClientManager

manager = await TemporalClientManager.create_cloud_client(
    namespace=os.getenv("TEMPORAL_CLOUD_NAMESPACE"),
    client_cert_path=os.getenv("TEMPORAL_CLOUD_CERT_PATH"),
    client_key_path=os.getenv("TEMPORAL_CLOUD_KEY_PATH"),
    api_key=os.getenv("TEMPORAL_CLOUD_API_KEY")
)
```

### TLS Configuration (Custom)

```python
from temporalio.client import TLSConfig
from app.temporal.client import TemporalClientManager

# Load certificates
with open("client-cert.pem", "rb") as f:
    client_cert = f.read()
with open("client-key.pem", "rb") as f:
    client_key = f.read()

# Create TLS config
tls_config = TLSConfig(
    client_cert=client_cert,
    client_private_key=client_key,
)

# Create manager with TLS
manager = TemporalClientManager(
    target_host="my-namespace.tmprl.cloud:7233",
    namespace="my-namespace.a2b3c",
    tls_config=tls_config
)

await manager.connect()
```

---

## PRODUCTION BEST PRACTICES

### 1. Connection Pooling

**Pattern:** Reuse client connections across multiple worker instances

```python
# Create single client manager instance
manager = TemporalClientManager()
await manager.connect()

# Create multiple workers (share connection)
worker1 = manager.create_worker(workflows1, activities1)
worker2 = manager.create_worker(workflows2, activities2)

# Run workers concurrently
await asyncio.gather(
    manager.run_worker(worker1),
    manager.run_worker(worker2)
)
```

### 2. Graceful Shutdown

**Pattern:** Handle SIGTERM/SIGINT for graceful shutdown

```python
import signal
import asyncio

shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    print(f"Received signal {signum}, initiating shutdown")
    shutdown_event.set()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Run worker
worker_task = asyncio.create_task(manager.run_worker(worker))

# Wait for shutdown signal
await shutdown_event.wait()

# Cancel worker
worker_task.cancel()
try:
    await worker_task
except asyncio.CancelledError:
    print("Worker stopped gracefully")
```

### 3. Error Handling

**Pattern:** Retry connection failures with exponential backoff

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
async def connect_with_retry():
    manager = TemporalClientManager()
    await manager.connect()
    return manager

try:
    manager = await connect_with_retry()
except Exception as e:
    print(f"Failed to connect after retries: {e}")
    sys.exit(1)
```

### 4. Resource Limits

**Pattern:** Configure resource limits for workers

```python
worker = manager.create_worker(
    workflows=workflows,
    activities=activities,
    max_concurrent_activities=100,
    max_concurrent_workflow_tasks=50,
)

# Additional configuration (if needed)
# - Set activity timeouts
# - Configure retry policies
# - Set memory limits (Docker/K8s)
```

### 5. Monitoring and Observability

**Pattern:** Integrate with monitoring systems

```python
import logging
from prometheus_client import Counter, Histogram

# Prometheus metrics
workflow_counter = Counter('temporal_workflows_total', 'Total workflows executed')
workflow_duration = Histogram('temporal_workflow_duration_seconds', 'Workflow duration')

# Custom logger with structured logging
logger = logging.getLogger("temporal-worker")
logger.info(
    "Worker started",
    extra={
        "worker_id": manager.worker_identity,
        "task_queue": manager.task_queue,
        "max_activities": max_concurrent_activities
    }
)
```

### 6. Multi-Namespace Support

**Pattern:** Create workers for multiple namespaces

```python
# Production namespace
prod_manager = TemporalClientManager(
    namespace="production",
    task_queue="prod-tasks"
)
await prod_manager.connect()
prod_worker = prod_manager.create_worker(workflows, activities)

# Staging namespace
staging_manager = TemporalClientManager(
    namespace="staging",
    task_queue="staging-tasks"
)
await staging_manager.connect()
staging_worker = staging_manager.create_worker(workflows, activities)

# Run both workers
await asyncio.gather(
    prod_manager.run_worker(prod_worker),
    staging_manager.run_worker(staging_worker)
)
```

### 7. Security Hardening

**Production Security Checklist:**

✅ **TLS/mTLS:** Use TLS for all production connections  
✅ **Certificate Management:** Rotate certificates regularly  
✅ **Least Privilege:** Workers run with minimal permissions  
✅ **Network Segmentation:** Isolate Temporal network  
✅ **Audit Logging:** Enable comprehensive audit logs  
✅ **Secrets Management:** Use vault for API keys/certificates

**Example: Secure Production Configuration**

```python
from app.temporal.client import TemporalClientManager
from temporalio.client import TLSConfig
import boto3

# Load secrets from AWS Secrets Manager
secrets_client = boto3.client('secretsmanager')
cert_secret = secrets_client.get_secret_value(SecretId='temporal-client-cert')
key_secret = secrets_client.get_secret_value(SecretId='temporal-client-key')

# Create TLS config
tls_config = TLSConfig(
    client_cert=cert_secret['SecretString'].encode(),
    client_private_key=key_secret['SecretString'].encode(),
)

# Create secure manager
manager = TemporalClientManager(
    target_host="secure-temporal.company.com:7233",
    namespace="production",
    tls_config=tls_config
)
```

---

## TROUBLESHOOTING

### Issue 1: Connection Refused

**Symptom:**
```
ConnectionError: Unable to connect to Temporal at localhost:7233
```

**Causes:**
1. Temporal Server not running
2. Incorrect host/port
3. Firewall blocking connection

**Resolution:**
```powershell
# Check Temporal Server is running
docker ps | Select-String temporal

# Verify port is accessible
Test-NetConnection -ComputerName localhost -Port 7233

# Start Temporal Server (if not running)
temporal server start-dev
```

### Issue 2: Worker Not Receiving Tasks

**Symptom:** Worker starts but no tasks are executed

**Causes:**
1. Incorrect task queue name
2. Workflows not registered
3. No workflows being started

**Resolution:**
```python
# Verify task queue name matches
print(f"Worker task queue: {manager.task_queue}")
print(f"Workflow task queue: project-ai-tasks")
# These must match!

# Verify workflows registered
print(f"Registered workflows: {len(workflows)}")

# Check Temporal UI for workflow executions
# Navigate to: http://localhost:8080
```

### Issue 3: High Memory Usage

**Symptom:** Worker memory usage grows unbounded

**Causes:**
1. Too many concurrent activities
2. Memory leaks in activity code
3. Large data being held in memory

**Resolution:**
```python
# Reduce concurrency
worker = manager.create_worker(
    workflows=workflows,
    activities=activities,
    max_concurrent_activities=25,  # Reduced from 50
)

# Review activity code for memory leaks
# Use memory profiler: memory_profiler

# Implement chunked processing for large data
```

### Issue 4: Activities Timing Out

**Symptom:** Activities consistently timeout

**Causes:**
1. Timeout too short for activity
2. External API slowness
3. Network latency

**Resolution:**
```python
# Increase activity timeout
result = await workflow.execute_activity(
    "slow_activity",
    request,
    start_to_close_timeout=timedelta(minutes=15),  # Increased
)

# Add retry policy with longer intervals
retry_policy = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=10),
    maximum_interval=timedelta(minutes=2),
)
```

---

## APPENDIX

### Worker Deployment Checklist

**Pre-Deployment:**
- [ ] Temporal Server is running and accessible
- [ ] Configuration files are correct (host, namespace, task_queue)
- [ ] All workflows and activities are registered
- [ ] Environment variables are set
- [ ] Certificates are valid (for cloud deployments)

**Deployment:**
- [ ] Worker starts without errors
- [ ] Worker logs show "Connected to Temporal server"
- [ ] Worker appears in Temporal UI "Workers" tab
- [ ] Test workflow execution succeeds

**Post-Deployment:**
- [ ] Monitoring is enabled
- [ ] Alerts are configured
- [ ] Log rotation is set up
- [ ] Health checks are passing
- [ ] Backup/disaster recovery plan is documented

### Performance Tuning

**Worker Performance Tuning:**

| Parameter | Default | Low Load | High Load | Notes |
|-----------|---------|----------|-----------|-------|
| `max_concurrent_activities` | 50 | 25 | 100-200 | Adjust based on CPU/memory |
| `max_concurrent_workflow_tasks` | 50 | 25 | 50-100 | Workflows are lightweight |
| Number of workers | 1 | 1 | 3-10 | Horizontal scaling |

**Activity Timeout Tuning:**

| Activity Type | Default | Low Traffic | High Traffic |
|---------------|---------|-------------|--------------|
| Validation | 30s | 30s | 10s |
| Processing | 5min | 10min | 5min |
| API Calls | 10min | 15min | 5min |
| Storage | 30s | 1min | 30s |

### Related Documentation


### Cross-References

- [[relationships/temporal/03_TEMPORAL_INTEGRATION.md|03 Temporal Integration]]
- `WORKFLOWS_COMPREHENSIVE.md` - Workflow patterns and examples
- `ACTIVITIES_COMPREHENSIVE.md` - Activity implementation guide
- `WORKFLOW_GOVERNANCE.md` - Governance integration details

---

**END OF DOCUMENT**


---

## 🔗 Source Code References

This documentation references the following Temporal source files:

- [[temporal/__init__.py]] - Implementation file
