# Deployment Architecture - Project-AI

## Overview

Project-AI supports multiple deployment models from standalone desktop applications to distributed cloud deployments. This document covers all deployment scenarios, infrastructure requirements, and operational procedures.

## Deployment Models

```
┌──────────────────────────────────────────────────────────────┐
│               DEPLOYMENT MODEL SPECTRUM                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Standalone     →     Docker Local    →     Cloud Hosted    │
│  (Desktop App)        (Compose)             (Kubernetes)     │
│                                                              │
│  • Single User        • Multi-User         • Multi-Tenant   │
│  • No Server          • Local Network      • Global Scale   │
│  • SQLite/File        • PostgreSQL         • Distributed DB │
│  • 1 Process          • 5-10 Containers    • 50+ Pods       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Deployment Model 1: Standalone Desktop

### Architecture

```
┌────────────────────────────────────────┐
│         Desktop Application            │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │   PyQt6 GUI (Leather Book)       │ │
│  └────────────┬─────────────────────┘ │
│               ↓                        │
│  ┌──────────────────────────────────┐ │
│  │   Application Core               │ │
│  │   • CognitionKernel              │ │
│  │   • GovernanceTriumvirate        │ │
│  │   • MemoryEngine                 │ │
│  │   • Agent System (30+ agents)    │ │
│  └────────────┬─────────────────────┘ │
│               ↓                        │
│  ┌──────────────────────────────────┐ │
│  │   Local Storage                  │ │
│  │   • SQLite or PostgreSQL         │ │
│  │   • JSON files (data/)           │ │
│  │   • Logs (logs/)                 │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

### Installation

**Windows**:
```powershell
# Clone repository
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run application
python -m src.app.main

# Or use launcher
.\launch-desktop.bat
```

**macOS/Linux**:
```bash
# Clone repository
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
nano .env  # Add your API keys

# Run application
python -m src.app.main
```

### System Requirements

**Minimum**:
- OS: Windows 10, macOS 10.15, Ubuntu 20.04
- CPU: 2 cores @ 2.0 GHz
- RAM: 4GB
- Storage: 2GB free space
- Python: 3.11+

**Recommended**:
- OS: Windows 11, macOS 13+, Ubuntu 22.04
- CPU: 4 cores @ 2.5 GHz
- RAM: 8GB
- Storage: 10GB free space (for logs and memory)
- Python: 3.12
- GPU: Optional (for image generation)

### Configuration

`config/desktop.yaml`:
```yaml
application:
  name: "Project-AI Desktop"
  version: "1.0.0"
  mode: "standalone"

storage:
  database:
    type: "sqlite"
    path: "data/project_ai.db"
  
  files:
    data_dir: "data/"
    logs_dir: "logs/"
    temp_dir: "temp/"

memory:
  hot_storage_days: 90
  enable_archival: false  # Archival disabled in standalone mode

governance:
  enable_all_checks: true
  require_approval: true
  
agents:
  max_concurrent: 5
  timeout_seconds: 60

api_keys:
  openai: "${OPENAI_API_KEY}"
  huggingface: "${HUGGINGFACE_API_KEY}"
```

## Deployment Model 2: Docker Compose (Local/Development)

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    DOCKER COMPOSE STACK                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  app           │  │  api           │  │  gui          │ │
│  │  (Main Logic)  │  │  (Flask REST)  │  │  (Optional)   │ │
│  │  Port: -       │  │  Port: 5000    │  │  Port: -      │ │
│  └───────┬────────┘  └───────┬────────┘  └───────┬───────┘ │
│          │                   │                   │          │
│          └───────────────────┼───────────────────┘          │
│                              ↓                               │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  postgres      │  │  redis         │  │  rabbitmq     │ │
│  │  (Database)    │  │  (Cache)       │  │  (Queue)      │ │
│  │  Port: 5432    │  │  Port: 6379    │  │  Port: 5672   │ │
│  └────────────────┘  └────────────────┘  └───────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  minio         │  │  prometheus    │  │  grafana      │ │
│  │  (Object Store)│  │  (Metrics)     │  │  (Dashboard)  │ │
│  │  Port: 9000    │  │  Port: 9090    │  │  Port: 3000   │ │
│  └────────────────┘  └────────────────┘  └───────────────┘ │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐                    │
│  │  temporal      │  │  jaeger        │                    │
│  │  (Workflows)   │  │  (Tracing)     │                    │
│  │  Port: 7233    │  │  Port: 16686   │                    │
│  └────────────────┘  └────────────────┘                    │
└──────────────────────────────────────────────────────────────┘
```

### Docker Compose Configuration

`docker-compose.yml`:
```yaml
version: '3.8'

services:
  # Main application
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: project-ai-app
    environment:
      - DATABASE_URL=postgresql://project_ai:password@postgres:5432/project_ai
      - REDIS_URL=redis://redis:6379/0
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
      - MINIO_ENDPOINT=minio:9000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
      - rabbitmq
      - minio
    networks:
      - project-ai-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Flask REST API
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: project-ai-api
    command: ["flask", "run", "--host=0.0.0.0", "--port=5000"]
    environment:
      - FLASK_APP=src.app.api:create_app
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://project_ai:password@postgres:5432/project_ai
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - postgres
      - redis
    networks:
      - project-ai-network
    restart: unless-stopped

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: project-ai-postgres
    environment:
      - POSTGRES_USER=project_ai
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=project_ai
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - project-ai-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U project_ai"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: project-ai-redis
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"
    networks:
      - project-ai-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # RabbitMQ Message Queue
  rabbitmq:
    image: rabbitmq:3-management-alpine
    container_name: project-ai-rabbitmq
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"  # Management UI
    networks:
      - project-ai-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  # MinIO Object Storage
  minio:
    image: minio/minio:latest
    container_name: project-ai-minio
    command: server /data --console-address ":9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - minio-data:/data
    ports:
      - "9000:9000"
      - "9001:9001"  # Console UI
    networks:
      - project-ai-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Prometheus Metrics
  prometheus:
    image: prom/prometheus:latest
    container_name: project-ai-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - project-ai-network
    restart: unless-stopped

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    container_name: project-ai-grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/etc/grafana/dashboards/project-ai.json
    volumes:
      - ./monitoring/grafana/dashboards:/etc/grafana/dashboards
      - ./monitoring/grafana/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
      - grafana-data:/var/lib/grafana
    ports:
      - "3000:3000"
    networks:
      - project-ai-network
    depends_on:
      - prometheus
    restart: unless-stopped

  # Temporal Workflow Engine
  temporal:
    image: temporalio/auto-setup:latest
    container_name: project-ai-temporal
    environment:
      - DB=postgresql
      - DB_PORT=5432
      - POSTGRES_USER=project_ai
      - POSTGRES_PWD=password
      - POSTGRES_SEEDS=postgres
    ports:
      - "7233:7233"
    networks:
      - project-ai-network
    depends_on:
      - postgres
    restart: unless-stopped

  # Jaeger Distributed Tracing
  jaeger:
    image: jaegertracing/all-in-one:latest
    container_name: project-ai-jaeger
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"  # UI
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    networks:
      - project-ai-network
    restart: unless-stopped

networks:
  project-ai-network:
    driver: bridge

volumes:
  postgres-data:
  redis-data:
  rabbitmq-data:
  minio-data:
  prometheus-data:
  grafana-data:
```

### Deployment Steps

```bash
# 1. Clone repository
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# 2. Create .env file
cat > .env <<EOF
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...
EOF

# 3. Start all services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f app

# 6. Initialize database
docker-compose exec postgres psql -U project_ai -f /docker-entrypoint-initdb.d/init.sql

# 7. Access services
# API: http://localhost:5000
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
# RabbitMQ: http://localhost:15672 (guest/guest)
# MinIO: http://localhost:9001 (minioadmin/minioadmin)
# Jaeger: http://localhost:16686

# 8. Stop all services
docker-compose down

# 9. Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v
```

### Health Checks

```bash
# Check all services health
docker-compose ps

# Check specific service
docker-compose logs app

# Check database connection
docker-compose exec postgres pg_isready -U project_ai

# Check Redis
docker-compose exec redis redis-cli ping

# Check API
curl http://localhost:5000/health

# Check metrics endpoint
curl http://localhost:5000/metrics
```

## Deployment Model 3: Production (Cloud/Kubernetes)

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                           │
│                     (Multi-Region)                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Load Balancer / Ingress                     │  │
│  │  (NGINX, HAProxy, or Cloud LB)                           │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                         │
│         ┌─────────────┴─────────────┐                          │
│         ↓                           ↓                          │
│  ┌─────────────┐             ┌─────────────┐                  │
│  │  API Pods   │             │  GUI Pods   │                  │
│  │  (3+ replicas)            │  (Optional) │                  │
│  └──────┬──────┘             └─────────────┘                  │
│         │                                                       │
│         ↓                                                       │
│  ┌───────────────────────────────────────────┐                │
│  │        Service Mesh (Istio/Linkerd)       │                │
│  └───────────────────────────────────────────┘                │
│         │                                                       │
│    ┌────┴────────┬──────────────┬──────────────┐              │
│    ↓             ↓              ↓              ↓              │
│ ┌────────┐  ┌────────┐  ┌─────────┐  ┌──────────┐           │
│ │Cognition  │Governance │ Memory  │  │ Execution │           │
│ │ Service│  │ Service│  │ Service │  │  Service  │           │
│ │        │  │        │  │         │  │           │           │
│ │3 replicas │3 replicas │2 replicas│  │5 replicas │           │
│ └────────┘  └────────┘  └─────────┘  └──────────┘           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Data Tier (Managed Services)                │  │
│  │                                                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │  PostgreSQL  │  │    Redis     │  │   RabbitMQ   │  │  │
│  │  │  (RDS/Cloud) │  │  (ElastiCache)  │  (Cloud MQ)  │  │  │
│  │  │  + Replicas  │  │  + Cluster   │  │  + HA        │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  │                                                          │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │     S3       │  │  Prometheus  │  │    Jaeger    │  │  │
│  │  │  (Storage)   │  │  (Metrics)   │  │   (Traces)   │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Kubernetes Manifests

`k8s/namespace.yaml`:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: project-ai
  labels:
    name: project-ai
    environment: production
```

`k8s/api-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: project-ai-api
  namespace: project-ai
  labels:
    app: project-ai
    component: api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: project-ai
      component: api
  template:
    metadata:
      labels:
        app: project-ai
        component: api
    spec:
      containers:
      - name: api
        image: project-ai/api:1.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 5000
          name: http
          protocol: TCP
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: project-ai-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: project-ai-secrets
              key: redis-url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: project-ai-secrets
              key: openai-api-key
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: config
        configMap:
          name: project-ai-config
      - name: logs
        emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: component
                  operator: In
                  values:
                  - api
              topologyKey: kubernetes.io/hostname
```

`k8s/api-service.yaml`:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: project-ai-api
  namespace: project-ai
  labels:
    app: project-ai
    component: api
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 5000
    protocol: TCP
    name: http
  selector:
    app: project-ai
    component: api
```

`k8s/api-hpa.yaml`:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: project-ai-api-hpa
  namespace: project-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: project-ai-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 30
      selectPolicy: Max
```

`k8s/ingress.yaml`:
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: project-ai-ingress
  namespace: project-ai
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/cors-allow-origin: "*"
spec:
  tls:
  - hosts:
    - api.project-ai.dev
    secretName: project-ai-tls
  rules:
  - host: api.project-ai.dev
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: project-ai-api
            port:
              number: 80
```

### Deployment Commands

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create secrets
kubectl create secret generic project-ai-secrets \
  --namespace=project-ai \
  --from-literal=database-url='postgresql://...' \
  --from-literal=redis-url='redis://...' \
  --from-literal=openai-api-key='sk-...'

# 3. Create config map
kubectl create configmap project-ai-config \
  --namespace=project-ai \
  --from-file=config/production.yaml

# 4. Deploy application
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
kubectl apply -f k8s/api-hpa.yaml

# 5. Deploy ingress
kubectl apply -f k8s/ingress.yaml

# 6. Check deployment status
kubectl get pods -n project-ai
kubectl get svc -n project-ai
kubectl get ingress -n project-ai

# 7. Check logs
kubectl logs -f -n project-ai -l component=api

# 8. Scale manually
kubectl scale deployment project-ai-api --replicas=5 -n project-ai

# 9. Rolling update
kubectl set image deployment/project-ai-api \
  api=project-ai/api:1.1.0 -n project-ai

# 10. Rollback
kubectl rollout undo deployment/project-ai-api -n project-ai
```

## Infrastructure as Code (Terraform)

`terraform/main.tf`:
```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

# EKS Cluster
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "project-ai-cluster"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = {
    general = {
      desired_size = 3
      min_size     = 2
      max_size     = 10

      instance_types = ["t3.xlarge"]
      capacity_type  = "ON_DEMAND"
    }
  }
}

# RDS PostgreSQL
module "db" {
  source = "terraform-aws-modules/rds/aws"

  identifier = "project-ai-db"

  engine            = "postgres"
  engine_version    = "15.3"
  instance_class    = "db.t3.large"
  allocated_storage = 100

  db_name  = "project_ai"
  username = "project_ai"
  password = var.db_password

  multi_az               = true
  backup_retention_period = 30
  backup_window          = "03:00-06:00"
  maintenance_window     = "Mon:00:00-Mon:03:00"

  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}

# ElastiCache Redis
module "redis" {
  source = "terraform-aws-modules/elasticache/aws"

  cluster_id      = "project-ai-redis"
  engine          = "redis"
  engine_version  = "7.0"
  node_type       = "cache.t3.medium"
  num_cache_nodes = 2

  parameter_group_name = "default.redis7"

  automatic_failover_enabled = true
}

# S3 Buckets
resource "aws_s3_bucket" "storage" {
  bucket = "project-ai-storage"
}

resource "aws_s3_bucket" "archives" {
  bucket = "project-ai-archives"
}
```

## Monitoring and Observability

### Prometheus Configuration

`monitoring/prometheus.yml`:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'project-ai-api'
    static_configs:
      - targets: ['app:5000']
    metrics_path: '/metrics'
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/alerts/*.yml'
```

## Performance Characteristics

### Deployment Comparison

| Metric | Standalone | Docker Compose | Kubernetes |
|--------|-----------|----------------|------------|
| Setup Time | 5 min | 10 min | 30 min |
| Users | 1 | 10-100 | 1000+ |
| Availability | - | 95% | 99.9% |
| Scalability | None | Vertical | Horizontal |
| Cost | $0 | $50/mo | $500+/mo |

## Related Documentation

- [Docker Compose Details](./docker_compose.md)
- [Production Topology](./production_topology.md)
- [Development Environment](./development_environment.md)
- [Kubernetes Deployment](./kubernetes_deployment.md)
