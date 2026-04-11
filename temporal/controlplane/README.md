# Temporal Control Plane

Comprehensive control plane API for deployment and lifecycle management of cloud infrastructure.

## Overview

The Temporal Control Plane provides a complete solution for managing cloud infrastructure with:

- **RESTful API**: Full-featured API for all control plane operations
- **Deployment Management**: Deploy and manage agents, workflows, and services
- **Scaling Controls**: Horizontal and vertical scaling with autoscaling policies
- **Monitoring**: Query metrics, logs, and distributed traces
- **Lifecycle Management**: Start, stop, restart, and update agents
- **Kubernetes Operators**: Custom operators for automated lifecycle management
- **CLI Tool**: Command-line interface for all operations
- **Web Dashboard**: Browser-based management interface

## Architecture

```
temporal/controlplane/
├── api/                    # REST API implementation
│   ├── deployment.py      # Deployment API
│   ├── scaling.py         # Scaling API
│   ├── monitoring.py      # Monitoring API
│   ├── lifecycle.py       # Lifecycle API
│   └── server.py          # FastAPI server
├── operator/              # Kubernetes operator
│   ├── crd.py            # Custom Resource Definitions
│   ├── controller.py     # Resource controllers
│   └── operator.py       # Main operator
├── cli/                   # CLI tool
│   └── commands.py       # CLI commands
├── web/                   # Web UI
│   └── dashboard.html    # Dashboard interface
└── specs/                 # OpenAPI specifications
    └── openapi.yaml      # API specification
```

## Quick Start

### 1. Install Dependencies

```bash
pip install fastapi uvicorn click requests pydantic
```

### 2. Start the API Server

```bash
# From the repository root
python -m temporal.controlplane.api.server

# Or using uvicorn directly
uvicorn temporal.controlplane.api.server:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000/api/v1
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 3. Use the CLI

```bash
# Create a deployment
python -m temporal.controlplane.cli.commands deployment create \
  --name my-agent \
  --type agent \
  --image myapp:latest \
  --replicas 3

# List deployments
python -m temporal.controlplane.cli.commands deployment list

# Scale horizontally
python -m temporal.controlplane.cli.commands scaling horizontal deploy-123 --replicas 5

# Create autoscaling policy
python -m temporal.controlplane.cli.commands scaling autoscale \
  --name my-policy \
  --target deploy-123 \
  --min 2 \
  --max 10 \
  --metric cpu \
  --value 80

# View metrics
python -m temporal.controlplane.cli.commands monitoring metrics --metric cpu_usage

# Create an agent
python -m temporal.controlplane.cli.commands agent create \
  --name my-agent \
  --type worker \
  --start

# Start/stop/restart agent
python -m temporal.controlplane.cli.commands agent start agent-123
python -m temporal.controlplane.cli.commands agent stop agent-123
python -m temporal.controlplane.cli.commands agent restart agent-123
```

### 4. Access the Web Dashboard

Open `temporal/controlplane/web/dashboard.html` in a browser, or serve it with:

```bash
python -m http.server 8080 --directory temporal/controlplane/web
```

Then navigate to: http://localhost:8080/dashboard.html

## API Reference

### Deployment API

#### Create Deployment
```http
POST /api/v1/deployments
Content-Type: application/json

{
  "name": "my-deployment",
  "deployment_type": "agent",
  "image": "myapp:latest",
  "replicas": 3,
  "strategy": "rolling_update",
  "environment": {
    "ENV": "production"
  },
  "resources": {
    "cpu": "500m",
    "memory": "1Gi"
  }
}
```

#### List Deployments
```http
GET /api/v1/deployments?deployment_type=agent&status=deployed
```

#### Update Deployment
```http
PUT /api/v1/deployments/{deployment_id}
Content-Type: application/json

{
  "image": "myapp:v2",
  "replicas": 5
}
```

#### Rollback Deployment
```http
POST /api/v1/deployments/{deployment_id}/rollback?revision=2
```

### Scaling API

#### Horizontal Scaling
```http
POST /api/v1/scaling/{deployment_id}/horizontal
Content-Type: application/json

{
  "replicas": 5
}
```

#### Vertical Scaling
```http
POST /api/v1/scaling/{deployment_id}/vertical
Content-Type: application/json

{
  "cpu": "1000m",
  "memory": "2Gi"
}
```

#### Create Autoscaling Policy
```http
POST /api/v1/scaling/policies
Content-Type: application/json

{
  "name": "cpu-autoscale",
  "target_id": "deploy-123",
  "scaling_type": "horizontal",
  "min_replicas": 2,
  "max_replicas": 10,
  "target_metric": "cpu",
  "target_value": 80.0
}
```

### Monitoring API

#### Query Metrics
```http
GET /api/v1/monitoring/metrics?metric_name=cpu_usage&deployment_id=deploy-123&aggregation=avg
```

#### Query Logs
```http
GET /api/v1/monitoring/logs?deployment_id=deploy-123&level=error&limit=100
```

#### Query Traces
```http
GET /api/v1/monitoring/traces?deployment_id=deploy-123&min_duration=100
```

#### Health Status
```http
GET /api/v1/monitoring/health/{deployment_id}
```

### Lifecycle API

#### Create Agent
```http
POST /api/v1/agents
Content-Type: application/json

{
  "name": "worker-agent",
  "agent_type": "worker",
  "version": "1.0.0",
  "config": {
    "max_tasks": 10
  },
  "auto_start": true
}
```

#### Start/Stop/Restart Agent
```http
POST /api/v1/agents/{agent_id}/start
POST /api/v1/agents/{agent_id}/stop?graceful=true
POST /api/v1/agents/{agent_id}/restart
```

#### Update Agent
```http
PUT /api/v1/agents/{agent_id}
Content-Type: application/json

{
  "version": "1.1.0",
  "config": {
    "max_tasks": 20
  },
  "restart": true
}
```

## Kubernetes Operator

### Install CRDs

```bash
python -m temporal.controlplane.operator.operator
```

### Deploy Agent Resource

```yaml
apiVersion: temporal.controlplane.io/v1
kind: Agent
metadata:
  name: my-agent
spec:
  agentType: worker
  version: "1.0.0"
  replicas: 3
  image: myapp:latest
  resources:
    cpu: "500m"
    memory: "1Gi"
    limits:
      cpu: "1000m"
      memory: "2Gi"
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPU: 80
```

### Deploy Workflow Resource

```yaml
apiVersion: temporal.controlplane.io/v1
kind: Workflow
metadata:
  name: my-workflow
spec:
  workflowType: data-processing
  schedule: "0 */6 * * *"  # Every 6 hours
  steps:
    - name: fetch-data
      action: fetch
      params:
        source: s3://bucket/data
    - name: process-data
      action: process
      params:
        algorithm: ml-model
    - name: store-results
      action: store
      params:
        destination: s3://bucket/results
  timeout: "2h"
```

## CLI Commands

### Deployment Commands
- `deployment create` - Create new deployment
- `deployment list` - List deployments
- `deployment get <id>` - Get deployment details
- `deployment delete <id>` - Delete deployment
- `deployment rollback <id>` - Rollback deployment

### Scaling Commands
- `scaling horizontal <id> --replicas <n>` - Scale horizontally
- `scaling vertical <id> --cpu <cpu> --memory <mem>` - Scale vertically
- `scaling autoscale` - Create autoscaling policy

### Monitoring Commands
- `monitoring metrics --metric <name>` - Query metrics
- `monitoring logs` - Query logs
- `monitoring health <id>` - Get health status
- `monitoring dashboard` - View dashboard data

### Agent Commands
- `agent create` - Create new agent
- `agent list` - List agents
- `agent start <id>` - Start agent
- `agent stop <id>` - Stop agent
- `agent restart <id>` - Restart agent
- `agent delete <id>` - Delete agent

## Configuration

### Environment Variables

```bash
# API Server
export CONTROLPLANE_HOST=0.0.0.0
export CONTROLPLANE_PORT=8000
export CONTROLPLANE_LOG_LEVEL=INFO

# Kubernetes
export KUBECONFIG=/path/to/kubeconfig
export NAMESPACE=default

# Monitoring
export METRICS_ENABLED=true
export LOGS_ENABLED=true
export TRACES_ENABLED=true
```

### API Server Configuration

Create `config.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 8000
  workers: 4
  log_level: INFO

database:
  url: postgresql://user:pass@localhost/controlplane
  pool_size: 10

monitoring:
  metrics_backend: prometheus
  logs_backend: elasticsearch
  traces_backend: jaeger

security:
  api_key_required: true
  cors_origins:
    - http://localhost:3000
    - https://app.example.com
```

## Features

### Deployment Strategies

- **Recreate**: Terminate old version, then deploy new version
- **Rolling Update**: Gradually replace old version with new version
- **Blue/Green**: Deploy new version alongside old, then switch traffic
- **Canary**: Deploy new version to subset of instances for testing

### Autoscaling

- **Horizontal Pod Autoscaling**: Scale replicas based on metrics
- **Vertical Pod Autoscaling**: Adjust resource limits
- **Custom Metrics**: Scale based on application-specific metrics
- **Schedule-based**: Scale at specific times

### Monitoring

- **Metrics**: CPU, memory, requests, latency, custom metrics
- **Logs**: Structured logging with filtering and search
- **Traces**: Distributed tracing across services
- **Health Checks**: Liveness, readiness, and startup probes

### Lifecycle Management

- **Graceful Shutdown**: Proper cleanup before termination
- **Rolling Restarts**: Restart with zero downtime
- **Version Updates**: Update agent versions seamlessly
- **Configuration Updates**: Apply config changes with optional restart

## Best Practices

1. **Resource Limits**: Always set resource requests and limits
2. **Health Checks**: Implement liveness and readiness probes
3. **Autoscaling**: Use autoscaling for production workloads
4. **Monitoring**: Monitor key metrics and set up alerts
5. **Graceful Shutdown**: Handle SIGTERM properly
6. **Rolling Updates**: Use rolling updates for zero downtime
7. **Backups**: Regular backups of configuration and state

## Troubleshooting

### API Server Won't Start
- Check port 8000 is available
- Verify dependencies are installed
- Check logs for error messages

### Deployment Stuck in Pending
- Check resource availability
- Verify image can be pulled
- Check node selector constraints

### High Memory Usage
- Review resource limits
- Check for memory leaks
- Enable vertical autoscaling

### Slow API Responses
- Check database connection pool
- Review query performance
- Enable caching

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/example/controlplane/issues
- Documentation: https://docs.example.com/controlplane
- Community: https://community.example.com
