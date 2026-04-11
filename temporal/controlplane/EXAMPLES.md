# Control Plane API Examples

Example YAML manifests and configurations for the Control Plane.

## Agent Examples

### Basic Worker Agent

```yaml
apiVersion: temporal.controlplane.io/v1
kind: Agent
metadata:
  name: worker-agent
  namespace: production
  labels:
    app: worker
    environment: production
spec:
  agentType: worker
  version: "1.0.0"
  replicas: 3
  image: registry.example.com/worker-agent:1.0.0
  config:
    max_concurrent_tasks: 10
    timeout: 300
  resources:
    cpu: "500m"
    memory: "512Mi"
    limits:
      cpu: "1000m"
      memory: "1Gi"
```

### High-Performance Agent with Autoscaling

```yaml
apiVersion: temporal.controlplane.io/v1
kind: Agent
metadata:
  name: hpc-agent
  namespace: production
spec:
  agentType: compute
  version: "2.0.0"
  replicas: 5
  image: registry.example.com/hpc-agent:2.0.0
  resources:
    cpu: "2000m"
    memory: "4Gi"
    limits:
      cpu: "4000m"
      memory: "8Gi"
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 20
    targetCPU: 75
```

## Workflow Examples

### Scheduled Data Processing Workflow

```yaml
apiVersion: temporal.controlplane.io/v1
kind: Workflow
metadata:
  name: nightly-etl
  namespace: production
spec:
  workflowType: etl
  schedule: "0 2 * * *"  # Daily at 2 AM
  timeout: "4h"
  steps:
    - name: extract
      action: fetch_data
      params:
        source: s3://data-lake/raw/
        format: parquet
    - name: transform
      action: apply_transforms
      params:
        transformations:
          - clean_nulls
          - normalize_dates
          - deduplicate
    - name: load
      action: write_data
      params:
        destination: postgresql://warehouse/analytics
        mode: overwrite
```

### Real-time Event Processing Workflow

```yaml
apiVersion: temporal.controlplane.io/v1
kind: Workflow
metadata:
  name: event-processor
  namespace: production
spec:
  workflowType: stream-processing
  steps:
    - name: consume
      action: kafka_consume
      params:
        topic: events
        group: processors
    - name: validate
      action: validate_schema
      params:
        schema_registry: http://schema-registry:8081
    - name: enrich
      action: enrich_data
      params:
        lookup_service: http://enrichment-api:8080
    - name: publish
      action: kafka_produce
      params:
        topic: processed-events
  timeout: "continuous"
```

## Deployment Examples

### REST API Deployment

```json
{
  "name": "api-service",
  "deployment_type": "service",
  "image": "registry.example.com/api:latest",
  "replicas": 5,
  "strategy": "rolling_update",
  "environment": {
    "DATABASE_URL": "postgresql://db:5432/api",
    "REDIS_URL": "redis://cache:6379/0",
    "LOG_LEVEL": "INFO"
  },
  "resources": {
    "cpu": "1000m",
    "memory": "2Gi",
    "limits": {
      "cpu": "2000m",
      "memory": "4Gi"
    }
  },
  "labels": {
    "app": "api",
    "tier": "backend",
    "environment": "production"
  }
}
```

### Batch Job Deployment

```json
{
  "name": "batch-processor",
  "deployment_type": "agent",
  "image": "registry.example.com/batch:v1.5.0",
  "replicas": 10,
  "strategy": "recreate",
  "environment": {
    "BATCH_SIZE": "1000",
    "PARALLEL_WORKERS": "4",
    "OUTPUT_PATH": "/mnt/output"
  },
  "resources": {
    "cpu": "4000m",
    "memory": "8Gi",
    "limits": {
      "cpu": "8000m",
      "memory": "16Gi"
    }
  }
}
```

## Autoscaling Policy Examples

### CPU-based Autoscaling

```json
{
  "name": "cpu-autoscale-policy",
  "target_id": "deployment-123",
  "scaling_type": "horizontal",
  "min_replicas": 2,
  "max_replicas": 20,
  "target_metric": "cpu",
  "target_value": 70.0
}
```

### Memory-based Autoscaling

```json
{
  "name": "memory-autoscale-policy",
  "target_id": "deployment-456",
  "scaling_type": "horizontal",
  "min_replicas": 3,
  "max_replicas": 15,
  "target_metric": "memory",
  "target_value": 80.0
}
```

### Request-based Autoscaling

```json
{
  "name": "request-autoscale-policy",
  "target_id": "deployment-789",
  "scaling_type": "horizontal",
  "min_replicas": 5,
  "max_replicas": 50,
  "target_metric": "requests",
  "target_value": 1000.0
}
```

## CLI Usage Examples

### Complete Deployment Workflow

```bash
# 1. Create deployment
python -m temporal.controlplane.cli.commands deployment create \
  --name my-app \
  --type service \
  --image myapp:v1.0.0 \
  --replicas 3 \
  --strategy rolling_update

# 2. Set up autoscaling
python -m temporal.controlplane.cli.commands scaling autoscale \
  --name my-app-autoscale \
  --target <deployment-id> \
  --min 2 \
  --max 10 \
  --metric cpu \
  --value 75

# 3. Monitor deployment
python -m temporal.controlplane.cli.commands monitoring metrics \
  --metric cpu_usage \
  --deployment <deployment-id>

# 4. Check logs
python -m temporal.controlplane.cli.commands monitoring logs \
  --deployment <deployment-id> \
  --level error \
  --limit 50

# 5. Update to new version
python -m temporal.controlplane.cli.commands deployment update \
  <deployment-id> \
  --image myapp:v1.1.0

# 6. Rollback if needed
python -m temporal.controlplane.cli.commands deployment rollback \
  <deployment-id>
```

### Agent Lifecycle Management

```bash
# Create and start agent
python -m temporal.controlplane.cli.commands agent create \
  --name worker-1 \
  --type worker \
  --version 1.0.0 \
  --start

# List running agents
python -m temporal.controlplane.cli.commands agent list \
  --state running

# Restart agent
python -m temporal.controlplane.cli.commands agent restart <agent-id>

# Update agent version
python -m temporal.controlplane.cli.commands agent update \
  <agent-id> \
  --version 1.1.0 \
  --restart

# Stop agent gracefully
python -m temporal.controlplane.cli.commands agent stop <agent-id>

# Force stop if needed
python -m temporal.controlplane.cli.commands agent stop <agent-id> --force
```

## Docker Compose Example

```yaml
version: '3.8'

services:
  controlplane-api:
    image: controlplane/api:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/controlplane
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./config:/config
    command: uvicorn temporal.controlplane.api.server:app --host 0.0.0.0 --port 8000

  controlplane-operator:
    image: controlplane/operator:latest
    environment:
      - KUBECONFIG=/kubeconfig/config
      - NAMESPACE=default
    volumes:
      - ~/.kube:/kubeconfig:ro
    command: python -m temporal.controlplane.operator.operator

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=controlplane
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis-data:/data

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  postgres-data:
  redis-data:
  prometheus-data:
  grafana-data:
```

## Kubernetes Deployment Example

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: controlplane-api
  namespace: controlplane
spec:
  replicas: 3
  selector:
    matchLabels:
      app: controlplane-api
  template:
    metadata:
      labels:
        app: controlplane-api
    spec:
      containers:
      - name: api
        image: controlplane/api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: controlplane-secrets
              key: database-url
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: controlplane-api
  namespace: controlplane
spec:
  selector:
    app: controlplane-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```
