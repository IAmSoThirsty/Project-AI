# Infrastructure Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_DESKTOP[Developer Laptop<br/>Windows/macOS/Linux]
        DEV_VENV[Python venv<br/>Project Dependencies]
        DEV_NODE[Node.js<br/>Frontend Tools]
        DEV_DOCKER[Docker Desktop<br/>Local Services]
    end

    subgraph "CI/CD Pipeline (GitHub Actions)"
        GH_ACTIONS[GitHub Actions<br/>Workflow Runner]
        
        subgraph "Build Workflow"
            LINT[Ruff Linter<br/>Code Quality]
            TEST[pytest<br/>Unit/Integration]
            SECURITY[Bandit + Safety<br/>Security Scan]
            TYPE_CHECK[mypy<br/>Type Checking]
        end
        
        subgraph "Deploy Workflow"
            BUILD_IMAGE[Docker Build<br/>Multi-stage]
            PUSH_REGISTRY[Push to Registry<br/>GHCR/DockerHub]
            DEPLOY_PROD[Deploy Production<br/>Railway/Fly.io]
        end
        
        CODEQL[CodeQL Analysis<br/>Security Scanning]
        DEPENDABOT[Dependabot<br/>Dependency Updates]
    end

    subgraph "Container Registry"
        GHCR[GitHub Container<br/>Registry]
        DOCKERHUB[Docker Hub<br/>Public Images]
        ECR[AWS ECR<br/>Private Registry]
    end

    subgraph "Production Deployment (Docker)"
        NGINX[NGINX<br/>Reverse Proxy]
        
        subgraph "Application Tier"
            APP1[Desktop App<br/>Container 1]
            APP2[Web Backend<br/>Container 2]
            APP3[Worker Pool<br/>Container 3]
        end
        
        LOAD_BALANCER[Load Balancer<br/>Round Robin]
    end

    subgraph "Database Tier"
        PG_PRIMARY[PostgreSQL Primary<br/>Read/Write]
        PG_REPLICA1[PostgreSQL Replica 1<br/>Read-Only]
        PG_REPLICA2[PostgreSQL Replica 2<br/>Read-Only]
        PG_BACKUP[Automated Backups<br/>Daily Snapshots]
    end

    subgraph "Cache & Queue Tier"
        REDIS_PRIMARY[Redis Primary<br/>Session Cache]
        REDIS_REPLICA[Redis Replica<br/>Failover]
        RABBITMQ[RabbitMQ<br/>Task Queue]
    end

    subgraph "Temporal Infrastructure"
        TEMPORAL_FRONTEND[Temporal Frontend<br/>gRPC Server]
        TEMPORAL_HISTORY[Temporal History<br/>Event Store]
        TEMPORAL_MATCHING[Temporal Matching<br/>Task Distribution]
        TEMPORAL_WORKER[Temporal Workers<br/>3 Instances]
    end

    subgraph "Object Storage"
        S3_IMAGES[S3 Bucket<br/>Generated Images]
        S3_BACKUPS[S3 Bucket<br/>Encrypted Backups]
        S3_LOGS[S3 Bucket<br/>Log Archive]
    end

    subgraph "Monitoring & Observability"
        PROMETHEUS[Prometheus<br/>Metrics Collection]
        GRAFANA[Grafana<br/>Dashboards]
        JAEGER[Jaeger<br/>Distributed Tracing]
        ELASTICSEARCH[Elasticsearch<br/>Log Aggregation]
        KIBANA[Kibana<br/>Log Visualization]
    end

    subgraph "Security Infrastructure"
        WAF[Cloudflare WAF<br/>DDoS Protection]
        SSL_CERT[Let's Encrypt<br/>TLS Certificates]
        SECRETS[HashiCorp Vault<br/>Secret Management]
        FIREWALL[Cloud Firewall<br/>Network Security]
    end

    subgraph "External Services"
        OPENAI_API[OpenAI API<br/>GPT-4 + DALL-E]
        HUGGINGFACE[Hugging Face<br/>Stable Diffusion]
        GITHUB_API[GitHub API<br/>Security Resources]
        SMTP[SMTP Server<br/>SendGrid/Mailgun]
    end

    subgraph "DNS & CDN"
        ROUTE53[Route 53<br/>DNS Management]
        CLOUDFLARE[Cloudflare CDN<br/>Static Assets]
    end

    %% Development to CI/CD
    DEV_DESKTOP --> GH_ACTIONS
    GH_ACTIONS --> LINT
    GH_ACTIONS --> TEST
    GH_ACTIONS --> SECURITY
    GH_ACTIONS --> TYPE_CHECK
    GH_ACTIONS --> CODEQL
    DEPENDABOT --> GH_ACTIONS

    %% CI/CD to Registry
    BUILD_IMAGE --> PUSH_REGISTRY
    PUSH_REGISTRY --> GHCR
    PUSH_REGISTRY --> DOCKERHUB
    PUSH_REGISTRY -.enterprise.-> ECR

    %% Registry to Production
    GHCR --> DEPLOY_PROD
    DEPLOY_PROD --> NGINX

    %% NGINX to Application Tier
    NGINX --> LOAD_BALANCER
    LOAD_BALANCER --> APP1
    LOAD_BALANCER --> APP2
    LOAD_BALANCER --> APP3

    %% Application to Database
    APP1 --> PG_PRIMARY
    APP2 --> PG_PRIMARY
    APP3 --> PG_PRIMARY
    APP1 -.read.-> PG_REPLICA1
    APP2 -.read.-> PG_REPLICA2
    PG_PRIMARY --> PG_BACKUP

    %% Application to Cache/Queue
    APP1 --> REDIS_PRIMARY
    APP2 --> REDIS_PRIMARY
    APP3 --> RABBITMQ
    REDIS_PRIMARY --> REDIS_REPLICA

    %% Temporal Integration
    APP2 --> TEMPORAL_FRONTEND
    APP3 --> TEMPORAL_FRONTEND
    TEMPORAL_FRONTEND --> TEMPORAL_HISTORY
    TEMPORAL_FRONTEND --> TEMPORAL_MATCHING
    TEMPORAL_MATCHING --> TEMPORAL_WORKER
    TEMPORAL_HISTORY --> PG_PRIMARY

    %% Object Storage
    APP1 --> S3_IMAGES
    APP2 --> S3_IMAGES
    APP3 --> S3_BACKUPS
    PROMETHEUS --> S3_LOGS

    %% Monitoring
    APP1 --> PROMETHEUS
    APP2 --> PROMETHEUS
    APP3 --> PROMETHEUS
    PROMETHEUS --> GRAFANA
    
    APP1 --> JAEGER
    APP2 --> JAEGER
    TEMPORAL_FRONTEND --> JAEGER
    
    APP1 --> ELASTICSEARCH
    APP2 --> ELASTICSEARCH
    NGINX --> ELASTICSEARCH
    ELASTICSEARCH --> KIBANA

    %% Security
    WAF --> NGINX
    NGINX --> SSL_CERT
    APP1 --> SECRETS
    APP2 --> SECRETS
    FIREWALL --> NGINX

    %% External Services
    APP1 --> OPENAI_API
    APP2 --> OPENAI_API
    APP2 --> HUGGINGFACE
    APP2 --> GITHUB_API
    APP2 --> SMTP

    %% DNS & CDN
    ROUTE53 --> CLOUDFLARE
    CLOUDFLARE --> NGINX

    %% Styling
    classDef devClass fill:#065f46,stroke:#10b981,stroke-width:2px,color:#fff
    classDef ciClass fill:#ca8a04,stroke:#eab308,stroke-width:2px,color:#000
    classDef registryClass fill:#7c2d12,stroke:#f97316,stroke-width:2px,color:#fff
    classDef prodClass fill:#1e3a8a,stroke:#3b82f6,stroke-width:3px,color:#fff
    classDef dbClass fill:#2563eb,stroke:#3b82f6,stroke-width:2px,color:#fff
    classDef cacheClass fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#fff
    classDef temporalClass fill:#581c87,stroke:#c084fc,stroke-width:2px,color:#fff
    classDef storageClass fill:#0c4a6e,stroke:#0ea5e9,stroke-width:2px,color:#fff
    classDef monitorClass fill:#991b1b,stroke:#f87171,stroke-width:2px,color:#fff
    classDef securityClass fill:#dc2626,stroke:#ef4444,stroke-width:2px,color:#fff
    classDef externalClass fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#fff
    classDef dnsClass fill:#713f12,stroke:#fbbf24,stroke-width:2px,color:#fff

    class DEV_DESKTOP,DEV_VENV,DEV_NODE,DEV_DOCKER devClass
    class GH_ACTIONS,LINT,TEST,SECURITY,TYPE_CHECK,BUILD_IMAGE,PUSH_REGISTRY,DEPLOY_PROD,CODEQL,DEPENDABOT ciClass
    class GHCR,DOCKERHUB,ECR registryClass
    class NGINX,APP1,APP2,APP3,LOAD_BALANCER prodClass
    class PG_PRIMARY,PG_REPLICA1,PG_REPLICA2,PG_BACKUP dbClass
    class REDIS_PRIMARY,REDIS_REPLICA,RABBITMQ cacheClass
    class TEMPORAL_FRONTEND,TEMPORAL_HISTORY,TEMPORAL_MATCHING,TEMPORAL_WORKER temporalClass
    class S3_IMAGES,S3_BACKUPS,S3_LOGS storageClass
    class PROMETHEUS,GRAFANA,JAEGER,ELASTICSEARCH,KIBANA monitorClass
    class WAF,SSL_CERT,SECRETS,FIREWALL securityClass
    class OPENAI_API,HUGGINGFACE,GITHUB_API,SMTP externalClass
    class ROUTE53,CLOUDFLARE dnsClass
```

## Infrastructure Components

### Docker Multi-Stage Build

**Optimized Dockerfile** (`Dockerfile`)

```dockerfile
# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/
COPY data/ ./data/
COPY .env .env

# Add Python packages to PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app/src

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Run application
CMD ["python", "-m", "src.app.main"]
```

### CI/CD Pipeline (GitHub Actions)

**Main Workflow** (`.github/workflows/ci.yml`)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install ruff mypy
          pip install -r requirements.txt
      
      - name: Run Ruff
        run: ruff check .
      
      - name: Run mypy
        run: mypy src/

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-cov
          pip install -r requirements.txt
      
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install security tools
        run: pip install bandit safety
      
      - name: Run Bandit
        run: bandit -r src/ -f json -o bandit-report.json
      
      - name: Run Safety
        run: safety check --file requirements.txt

  build:
    needs: [lint, test, security]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          railway up --service backend
```

### Production Docker Compose

**Full Stack Deployment** (`docker-compose.prod.yml`)

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: always

  backend:
    image: ghcr.io/iamsothirsty/project-ai:latest
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/project_ai
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - redis
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  worker:
    image: ghcr.io/iamsothirsty/project-ai:latest
    command: python -m src.app.temporal.worker
    environment:
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@postgres:5432/project_ai
      - REDIS_URL=redis://redis:6379
      - TEMPORAL_URL=temporal:7233
    depends_on:
      - temporal
      - postgres
    deploy:
      replicas: 3
    restart: always

  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: project_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 2G
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  postgres_replica:
    image: postgres:14
    environment:
      POSTGRES_DB: project_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata
    command: postgres -c wal_level=replica
    volumes:
      - postgres_replica:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: always
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  temporal:
    image: temporalio/auto-setup:1.22.0
    environment:
      - DB=postgresql
      - POSTGRES_SEEDS=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PWD=${DB_PASSWORD}
      - ENABLE_ES=true
      - ES_SEEDS=elasticsearch
    depends_on:
      - postgres
      - elasticsearch
    ports:
      - "7233:7233"
    restart: always

  elasticsearch:
    image: elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    restart: always

  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    ports:
      - "9090:9090"
    restart: always

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    restart: always

  jaeger:
    image: jaegertracing/all-in-one:latest
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    restart: always

volumes:
  postgres_data:
  postgres_replica:
  redis_data:
  elasticsearch_data:
  prometheus_data:
  grafana_data:
```

### NGINX Configuration

**Reverse Proxy** (`nginx.conf`)

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        least_conn;
        server backend:5000 max_fails=3 fail_timeout=30s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

    server {
        listen 80;
        server_name project-ai.com www.project-ai.com;

        # Redirect to HTTPS
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name project-ai.com www.project-ai.com;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # API endpoints
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Auth endpoints (stricter rate limiting)
        location /api/auth/ {
            limit_req zone=auth_limit burst=5 nodelay;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # WebSocket support
        location /socket.io/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### Monitoring Configuration

**Prometheus** (`prometheus.yml`)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:9090']
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
  
  - job_name: 'temporal'
    static_configs:
      - targets: ['temporal:9090']
  
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']
```

### Secrets Management

**HashiCorp Vault Integration**

```python
# src/app/core/secrets.py
import hvac
import os

class SecretsManager:
    """Centralized secrets management using HashiCorp Vault"""
    
    def __init__(self):
        self.vault_url = os.getenv('VAULT_URL', 'http://localhost:8200')
        self.vault_token = os.getenv('VAULT_TOKEN')
        
        self.client = hvac.Client(
            url=self.vault_url,
            token=self.vault_token
        )
    
    def get_secret(self, path: str, key: str) -> str:
        """Retrieve secret from Vault"""
        secret = self.client.secrets.kv.v2.read_secret_version(path=path)
        return secret['data']['data'][key]
    
    def set_secret(self, path: str, data: dict):
        """Store secret in Vault"""
        self.client.secrets.kv.v2.create_or_update_secret(
            path=path,
            secret=data
        )

# Usage
secrets = SecretsManager()
openai_key = secrets.get_secret('project-ai/api-keys', 'openai')
```

## Deployment Strategies

### Blue-Green Deployment

```bash
# Deploy green environment
docker-compose -f docker-compose.green.yml up -d

# Run smoke tests
curl https://green.project-ai.com/health

# Switch traffic (update DNS/load balancer)
./scripts/switch-traffic.sh green

# Keep blue as rollback target
# If issues, switch back to blue immediately
```

### Canary Deployment

```yaml
# k8s/canary-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-canary
spec:
  replicas: 1  # 10% traffic
  selector:
    matchLabels:
      app: backend
      version: canary
  template:
    metadata:
      labels:
        app: backend
        version: canary
    spec:
      containers:
      - name: backend
        image: ghcr.io/iamsothirsty/project-ai:canary
```

### Rolling Update

```bash
# Update 1 replica at a time
docker service update \
  --update-parallelism 1 \
  --update-delay 30s \
  --rollback-monitor 60s \
  backend
```
