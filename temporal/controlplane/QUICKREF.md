# Control Plane Quick Reference

## Starting the Control Plane

```bash
# Start API server
uvicorn temporal.controlplane.api.server:app --host 0.0.0.0 --port 8000

# Start Kubernetes operator
python -m temporal.controlplane.operator.operator

# Open web dashboard
# Navigate to: temporal/controlplane/web/dashboard.html
```

## Common CLI Commands

### Deployments
```bash
# Create
controlplane deployment create --name app --type agent --image app:v1 --replicas 3

# List
controlplane deployment list

# Get details
controlplane deployment get <deployment-id>

# Update
controlplane deployment update <deployment-id> --image app:v2 --replicas 5

# Delete
controlplane deployment delete <deployment-id>

# Rollback
controlplane deployment rollback <deployment-id>
```

### Scaling
```bash
# Scale horizontally
controlplane scaling horizontal <deployment-id> --replicas 10

# Scale vertically
controlplane scaling vertical <deployment-id> --cpu 2000m --memory 4Gi

# Create autoscaling policy
controlplane scaling autoscale \
  --name policy-1 \
  --target <deployment-id> \
  --min 2 --max 20 \
  --metric cpu --value 75
```

### Monitoring
```bash
# Query metrics
controlplane monitoring metrics --metric cpu_usage --deployment <id>

# View logs
controlplane monitoring logs --deployment <id> --level error

# Check health
controlplane monitoring health <deployment-id>

# Dashboard
controlplane monitoring dashboard
```

### Agents
```bash
# Create
controlplane agent create --name worker --type worker --start

# List
controlplane agent list --state running

# Start/Stop/Restart
controlplane agent start <agent-id>
controlplane agent stop <agent-id>
controlplane agent restart <agent-id>

# Update
controlplane agent update <agent-id> --version 2.0.0

# Delete
controlplane agent delete <agent-id>
```

## API Quick Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Common Headers
```
Content-Type: application/json
Authorization: Bearer <token>  # If enabled
```

### Deployment Endpoints
```bash
POST   /deployments              # Create
GET    /deployments              # List
GET    /deployments/{id}         # Get
PUT    /deployments/{id}         # Update
DELETE /deployments/{id}         # Delete
POST   /deployments/{id}/rollback # Rollback
```

### Scaling Endpoints
```bash
POST   /scaling/{id}/horizontal       # Scale horizontally
POST   /scaling/{id}/vertical         # Scale vertically
POST   /scaling/policies              # Create policy
GET    /scaling/policies              # List policies
DELETE /scaling/policies/{id}         # Delete policy
GET    /scaling/history               # Get history
```

### Monitoring Endpoints
```bash
GET /monitoring/metrics              # Query metrics
GET /monitoring/logs                 # Query logs
GET /monitoring/traces               # Query traces
GET /monitoring/health/{id}          # Health status
GET /monitoring/dashboard            # Dashboard data
```

### Lifecycle Endpoints
```bash
POST   /agents                  # Create
GET    /agents                  # List
GET    /agents/{id}             # Get
PUT    /agents/{id}             # Update
DELETE /agents/{id}             # Delete
POST   /agents/{id}/start       # Start
POST   /agents/{id}/stop        # Stop
POST   /agents/{id}/restart     # Restart
```

## Kubernetes Resources

### Agent Resource
```yaml
apiVersion: temporal.controlplane.io/v1
kind: Agent
metadata:
  name: my-agent
spec:
  agentType: worker
  version: "1.0.0"
  replicas: 3
  image: app:latest
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
```

### Workflow Resource
```yaml
apiVersion: temporal.controlplane.io/v1
kind: Workflow
metadata:
  name: my-workflow
spec:
  workflowType: etl
  schedule: "0 */6 * * *"
  steps:
    - name: extract
      action: fetch
    - name: transform
      action: process
    - name: load
      action: store
```

## Configuration

### config.yaml
```yaml
server:
  host: 0.0.0.0
  port: 8000
  workers: 4

kubernetes:
  namespace: default

monitoring:
  enabled: true
  metrics:
    backend: prometheus
```

## Environment Variables

```bash
export CONTROLPLANE_HOST=0.0.0.0
export CONTROLPLANE_PORT=8000
export KUBECONFIG=~/.kube/config
export NAMESPACE=default
```

## Troubleshooting

### API server won't start
```bash
# Check if port is in use
netstat -an | grep 8000

# Check logs
tail -f logs/controlplane.log
```

### Can't connect to API
```bash
# Test connectivity
curl http://localhost:8000/health

# Check server status
ps aux | grep controlplane
```

### Agent won't start
```bash
# Check agent status
controlplane agent get <agent-id>

# View logs
controlplane monitoring logs --deployment <id> --level error
```

## Common Patterns

### Deploy and Scale
```bash
# 1. Create deployment
ID=$(controlplane deployment create --name app --type agent --image app:v1 | jq -r '.id')

# 2. Set up autoscaling
controlplane scaling autoscale --name app-scale --target $ID --min 2 --max 10

# 3. Monitor
controlplane monitoring metrics --metric cpu_usage --deployment $ID
```

### Blue/Green Deployment
```bash
# 1. Deploy green
controlplane deployment create --name app-green --type service --image app:v2

# 2. Test green
curl http://app-green/health

# 3. Switch traffic (manual DNS/ingress update)
# 4. Delete blue
controlplane deployment delete <blue-id>
```

### Canary Release
```bash
# 1. Deploy canary (10% traffic)
controlplane deployment create \
  --name app-canary \
  --type service \
  --image app:v2 \
  --replicas 1 \
  --strategy canary

# 2. Monitor metrics
controlplane monitoring metrics --metric error_rate --deployment <canary-id>

# 3. Promote or rollback
controlplane deployment update <main-id> --image app:v2  # Promote
# OR
controlplane deployment delete <canary-id>  # Rollback
```

## Metrics Available

- `cpu_usage` - CPU utilization percentage
- `memory_usage` - Memory usage in bytes
- `request_count` - Total request count
- `request_duration` - Request latency (ms)
- `error_rate` - Error percentage
- `active_connections` - Active connections
- `queue_depth` - Queue size
- `throughput` - Requests per second

## Support

- Documentation: `temporal/controlplane/README.md`
- Examples: `temporal/controlplane/EXAMPLES.md`
- API Docs: `http://localhost:8000/docs`
- Issues: GitHub Issues
