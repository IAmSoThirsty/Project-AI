# Temporal Configuration Module

**Module**: `src/app/temporal/config.py` [[src/app/temporal/config.py]]  
**Purpose**: Temporal.io workflow configuration with Pydantic settings management  
**Classification**: Workflow Configuration  
**Priority**: P1 - Integration Services

---

## Overview

The Temporal Configuration Module provides Pydantic-based configuration for Temporal.io workflow orchestration including server connection, worker configuration, timeout policies, and retry strategies. It supports both local Temporal server and Temporal Cloud with TLS authentication.

### Key Characteristics

- **Framework**: Pydantic Settings for type-safe configuration
- **Environment**: `.env.temporal` file + `TEMPORAL_` prefix env vars
- **Modes**: Local server and Temporal Cloud
- **Validation**: Automatic type validation and conversion
- **Singleton**: Global config instance pattern

---

## Architecture

### Class Structure

```python
class TemporalConfig(BaseSettings):
    """Temporal.io configuration settings."""
    
    # Server Connection
    host: str
    namespace: str
    task_queue: str
    
    # Cloud Configuration
    cloud_namespace: str | None
    cloud_cert_path: Path | None
    cloud_key_path: Path | None
    cloud_api_key: str | None
    
    # Worker Configuration
    max_concurrent_activities: int
    max_concurrent_workflows: int
    worker_identity: str
    
    # Timeout Configuration
    workflow_execution_timeout: int
    workflow_run_timeout: int
    activity_start_to_close_timeout: int
    
    # Retry Policy
    max_retry_attempts: int
    initial_retry_interval: int
    max_retry_interval: int
```

---

## Configuration Settings

### Server Connection

```python
# Local Temporal server
host: str = "localhost:7233"
namespace: str = "default"
task_queue: str = "project-ai-tasks"
```

**Usage**:
- `host`: Temporal server address (hostname:port)
- `namespace`: Logical isolation boundary
- `task_queue`: Queue name for worker task distribution

### Cloud Configuration

```python
# Temporal Cloud settings
cloud_namespace: str | None = None
cloud_cert_path: Path | None = None
cloud_key_path: Path | None = None
cloud_api_key: str | None = None
```

**Cloud Setup**:
```python
# Example: my-namespace.a2b3c
cloud_namespace = "my-company.tmprl.cloud"
cloud_cert_path = Path("certs/client.pem")
cloud_key_path = Path("certs/client.key")
cloud_api_key = "your-api-key"
```

### Worker Configuration

```python
max_concurrent_activities: int = 50
max_concurrent_workflows: int = 50
worker_identity: str = "project-ai-worker"
```

**Tuning**:
- `max_concurrent_activities`: Limit parallel activity executions
- `max_concurrent_workflows`: Limit parallel workflow tasks
- `worker_identity`: Identifier for logging/monitoring

### Timeout Configuration

```python
# All timeouts in seconds
workflow_execution_timeout: int = 3600  # 1 hour
workflow_run_timeout: int = 1800        # 30 minutes
activity_start_to_close_timeout: int = 300  # 5 minutes
```

**Timeout Hierarchy**:
1. **Workflow Execution Timeout**: Maximum time for entire workflow (including retries)
2. **Workflow Run Timeout**: Maximum time for single workflow run
3. **Activity Timeout**: Maximum time for single activity execution

### Retry Policy

```python
max_retry_attempts: int = 3
initial_retry_interval: int = 1   # seconds
max_retry_interval: int = 30      # seconds
```

**Retry Behavior**:
- Exponential backoff from `initial_retry_interval`
- Capped at `max_retry_interval`
- Maximum `max_retry_attempts` retries

---

## Core API

### Initialization

```python
# Automatic initialization from environment
config = TemporalConfig()

# Manual initialization with overrides
config = TemporalConfig(
    host="temporal.example.com:7233",
    namespace="production",
    max_concurrent_activities=100
)
```

### Properties

```python
@property
def is_cloud(self) -> bool:
    """Check if using Temporal Cloud.
    
    Returns:
        True if cloud_namespace is set, False otherwise
    """

def get_connection_string(self) -> str:
    """Get connection string for logging.
    
    Returns:
        Human-readable connection description
    
    Examples:
        "Temporal Server: localhost:7233"
        "Temporal Cloud: my-namespace.tmprl.cloud"
    """
```

### Global Instance

```python
def get_temporal_config() -> TemporalConfig:
    """Get the Temporal configuration instance.
    
    Returns:
        Singleton TemporalConfig instance
    
    Pattern: Lazy initialization singleton
    """

def reload_temporal_config() -> TemporalConfig:
    """Reload the Temporal configuration from environment.
    
    Returns:
        New TemporalConfig instance
    
    Use Case: Reload after environment changes
    """
```

---

## Environment Configuration

### Environment File (.env.temporal)

```bash
# .env.temporal

# Server Connection
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=project-ai-tasks

# Cloud Configuration (optional)
# TEMPORAL_CLOUD_NAMESPACE=my-namespace.tmprl.cloud
# TEMPORAL_CLOUD_CERT_PATH=certs/client.pem
# TEMPORAL_CLOUD_KEY_PATH=certs/client.key
# TEMPORAL_CLOUD_API_KEY=your-api-key

# Worker Configuration
TEMPORAL_MAX_CONCURRENT_ACTIVITIES=50
TEMPORAL_MAX_CONCURRENT_WORKFLOWS=50
TEMPORAL_WORKER_IDENTITY=project-ai-worker

# Timeout Configuration (seconds)
TEMPORAL_WORKFLOW_EXECUTION_TIMEOUT=3600
TEMPORAL_WORKFLOW_RUN_TIMEOUT=1800
TEMPORAL_ACTIVITY_START_TO_CLOSE_TIMEOUT=300

# Retry Policy
TEMPORAL_MAX_RETRY_ATTEMPTS=3
TEMPORAL_INITIAL_RETRY_INTERVAL=1
TEMPORAL_MAX_RETRY_INTERVAL=30
```

### Environment Variables

```bash
# Override specific settings
export TEMPORAL_HOST=temporal-prod:7233
export TEMPORAL_NAMESPACE=production
export TEMPORAL_MAX_CONCURRENT_ACTIVITIES=100
```

**Priority**: Environment variables > .env.temporal > defaults

---

## Configuration Patterns

### Pattern 1: Local Development

```python
# .env.temporal
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=development
TEMPORAL_TASK_QUEUE=dev-tasks
TEMPORAL_MAX_CONCURRENT_ACTIVITIES=10
TEMPORAL_MAX_CONCURRENT_WORKFLOWS=10

# Load config
config = get_temporal_config()
assert not config.is_cloud
```

### Pattern 2: Temporal Cloud

```python
# .env.temporal
TEMPORAL_CLOUD_NAMESPACE=my-company.tmprl.cloud
TEMPORAL_CLOUD_CERT_PATH=certs/prod-client.pem
TEMPORAL_CLOUD_KEY_PATH=certs/prod-client.key
TEMPORAL_NAMESPACE=production
TEMPORAL_TASK_QUEUE=prod-tasks

# Load config
config = get_temporal_config()
assert config.is_cloud
```

### Pattern 3: Environment-Specific Config

```python
# Development
if os.getenv("ENVIRONMENT") == "development":
    config = TemporalConfig(
        host="localhost:7233",
        namespace="dev",
        max_concurrent_activities=10
    )

# Production
elif os.getenv("ENVIRONMENT") == "production":
    config = TemporalConfig(
        cloud_namespace=os.getenv("TEMPORAL_CLOUD_NS"),
        cloud_cert_path=Path("certs/prod.pem"),
        max_concurrent_activities=100
    )
```

### Pattern 4: Worker Initialization

```python
from temporalio.client import Client
from temporalio.worker import Worker
from src.app.temporal.config import get_temporal_config

async def create_worker():
    config = get_temporal_config()
    
    # Create client
    if config.is_cloud:
        client = await Client.connect(
            config.cloud_namespace,
            tls=TLSConfig(
                client_cert=config.cloud_cert_path,
                client_private_key=config.cloud_key_path
            )
        )
    else:
        client = await Client.connect(config.host)
    
    # Create worker
    worker = Worker(
        client,
        task_queue=config.task_queue,
        workflows=[MyWorkflow],
        activities=[my_activity],
        max_concurrent_activities=config.max_concurrent_activities,
        max_concurrent_workflow_tasks=config.max_concurrent_workflows
    )
    
    return worker
```

---

## Timeout Strategies

### Strategy 1: Short-Running Workflows

```python
# Configuration for quick workflows (< 5 minutes)
config = TemporalConfig(
    workflow_execution_timeout=300,  # 5 minutes
    workflow_run_timeout=120,        # 2 minutes
    activity_start_to_close_timeout=30  # 30 seconds
)
```

### Strategy 2: Long-Running Workflows

```python
# Configuration for batch processing (hours)
config = TemporalConfig(
    workflow_execution_timeout=86400,  # 24 hours
    workflow_run_timeout=3600,         # 1 hour
    activity_start_to_close_timeout=300  # 5 minutes
)
```

### Strategy 3: Real-Time Workflows

```python
# Configuration for latency-sensitive workflows
config = TemporalConfig(
    workflow_execution_timeout=60,  # 1 minute
    workflow_run_timeout=30,        # 30 seconds
    activity_start_to_close_timeout=5  # 5 seconds
)
```

---

## Retry Strategies

### Strategy 1: Aggressive Retry

```python
# Retry quickly for transient failures
config = TemporalConfig(
    max_retry_attempts=10,
    initial_retry_interval=1,
    max_retry_interval=10
)
```

### Strategy 2: Conservative Retry

```python
# Retry slowly to avoid overwhelming downstream
config = TemporalConfig(
    max_retry_attempts=3,
    initial_retry_interval=30,
    max_retry_interval=300
)
```

### Strategy 3: No Retry

```python
# Fail fast for idempotent operations
config = TemporalConfig(
    max_retry_attempts=0
)
```

---

## Usage Examples

### Example 1: Basic Client

```python
from temporalio.client import Client
from src.app.temporal.config import get_temporal_config

async def connect_temporal():
    config = get_temporal_config()
    client = await Client.connect(config.host, namespace=config.namespace)
    return client
```

### Example 2: Worker with Config

```python
from temporalio.worker import Worker
from src.app.temporal.config import get_temporal_config

async def run_worker():
    config = get_temporal_config()
    client = await Client.connect(config.host)
    
    worker = Worker(
        client,
        task_queue=config.task_queue,
        workflows=[ProcessingWorkflow],
        activities=[process_data],
        max_concurrent_activities=config.max_concurrent_activities,
        identity=config.worker_identity
    )
    
    await worker.run()
```

### Example 3: Workflow with Timeouts

```python
from temporalio import workflow
from src.app.temporal.config import get_temporal_config

@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self) -> str:
        config = get_temporal_config()
        
        # Use config timeout for activity
        result = await workflow.execute_activity(
            my_activity,
            start_to_close_timeout=timedelta(
                seconds=config.activity_start_to_close_timeout
            ),
            retry_policy=RetryPolicy(
                maximum_attempts=config.max_retry_attempts,
                initial_interval=timedelta(seconds=config.initial_retry_interval),
                maximum_interval=timedelta(seconds=config.max_retry_interval)
            )
        )
        
        return result
```

---

## Testing

### Unit Testing

```python
import pytest
from src.app.temporal.config import TemporalConfig, get_temporal_config

def test_default_config():
    config = TemporalConfig()
    assert config.host == "localhost:7233"
    assert config.namespace == "default"
    assert config.task_queue == "project-ai-tasks"

def test_cloud_detection():
    config = TemporalConfig(cloud_namespace="test.tmprl.cloud")
    assert config.is_cloud is True

def test_local_detection():
    config = TemporalConfig()
    assert config.is_cloud is False

def test_connection_string():
    config = TemporalConfig()
    assert "localhost:7233" in config.get_connection_string()

def test_env_override(monkeypatch):
    monkeypatch.setenv("TEMPORAL_HOST", "custom:7233")
    config = TemporalConfig()
    assert config.host == "custom:7233"
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_client_connection():
    config = get_temporal_config()
    client = await Client.connect(config.host, namespace=config.namespace)
    
    # Verify connection
    await client.list_workflows()
    
    await client.close()
```

---

## Security Considerations

### 1. TLS Certificates

**For Temporal Cloud**:
```bash
# Store certificates securely
chmod 600 certs/client.key
chmod 644 certs/client.pem

# Never commit to version control
echo "certs/" >> .gitignore
```

### 2. API Keys

**Environment Variables**:
```bash
# Never hardcode API keys
export TEMPORAL_CLOUD_API_KEY=your-key

# Use secret management
aws secretsmanager get-secret-value --secret-id temporal-api-key
```

### 3. Namespace Isolation

**Production Separation**:
```python
# Development namespace
config_dev = TemporalConfig(namespace="development")

# Production namespace
config_prod = TemporalConfig(namespace="production")
```

---

## Troubleshooting

### Issue: Connection Refused

**Symptom**: Cannot connect to Temporal server

**Solutions**:
```bash
# Check Temporal server is running
docker ps | grep temporal

# Start Temporal dev server
temporal server start-dev

# Verify host/port
telnet localhost 7233
```

### Issue: Cloud Authentication Failed

**Symptom**: TLS handshake error

**Solutions**:
```bash
# Verify certificate paths
ls -la certs/client.pem certs/client.key

# Check certificate validity
openssl x509 -in certs/client.pem -text -noout

# Verify cloud namespace
echo $TEMPORAL_CLOUD_NAMESPACE
```

### Issue: Worker Not Picking Up Tasks

**Symptom**: Tasks queued but not executed

**Solutions**:
```python
# Verify task queue name matches
config = get_temporal_config()
print(f"Worker queue: {config.task_queue}")

# Check worker identity
print(f"Worker identity: {config.worker_identity}")

# Increase concurrency
config.max_concurrent_activities = 100
```

---

## Best Practices

1. **Use Environment Files**: Store config in `.env.temporal`
2. **Separate Environments**: Different namespaces for dev/staging/prod
3. **Secure Certificates**: Proper permissions on TLS certs
4. **Tune Concurrency**: Match worker capacity to workload
5. **Set Appropriate Timeouts**: Balance responsiveness vs resource usage
6. **Retry Strategy**: Choose based on failure characteristics
7. **Monitor Workers**: Use worker_identity for tracking
8. **Validate Config**: Check is_cloud before client creation
9. **Reload on Change**: Use reload_temporal_config() after updates
10. **Log Connection**: Log get_connection_string() at startup

---

## Related Modules

- **Temporal Client**: `src/app/temporal/client.py` [[src/app/temporal/client.py]] - Client wrapper
- **Temporal Activities**: `src/app/temporal/activities.py` [[src/app/temporal/activities.py]] - Activity definitions
- **Core Config**: `src/app/core/config.py` [[src/app/core/config.py]] - Application configuration
- **Settings Manager**: `config/settings_manager.py` - General settings

---

## Future Enhancements

1. **Dynamic Config**: Hot reload configuration
2. **Config Validation**: Pre-flight validation
3. **Multiple Workers**: Support multiple worker configurations
4. **Metrics Config**: Configure Prometheus metrics
5. **Tracing Config**: OpenTelemetry tracing settings
6. **Advanced Retry**: Per-activity retry policies
7. **Rate Limiting**: Configure workflow rate limits
8. **Archival Config**: Configure history archival
9. **Search Attributes**: Configure custom search attributes
10. **Namespace Admin**: Namespace creation and management


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/temporal/config.py]]
