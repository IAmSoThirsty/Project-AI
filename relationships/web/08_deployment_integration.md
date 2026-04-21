# Deployment & Integration Relationships

**System:** Multi-Environment Deployment Architecture  
**Targets:** Development, Docker, Production  
**Integration:** Desktop (PyQt6) + Web (Next.js + Flask)  

## Deployment Architecture

### Multi-Interface Platform

```
Project-AI Platform
├─ Desktop Interface (PyQt6)
│  ├─ Leather Book UI
│  ├─ Direct core system access
│  └─ Local deployment only
│
└─ Web Interface (Next.js + Flask)
   ├─ Frontend: Next.js 14 (Port 3000)
   ├─ Backend: Flask API (Port 5000)
   ├─ Governance: Unified pipeline
   └─ Deployment: Dev, Docker, Vercel, Cloud
```

## Development Environment

### Local Development Setup

**Prerequisites:**
```bash
# Python 3.11+
python --version

# Node.js 20+
node --version

# Environment variables
cp web/.env.example web/.env.local
# Edit: OPENAI_API_KEY, HUGGINGFACE_API_KEY
```

### Backend Setup (Flask)

```bash
# Install dependencies
pip install -r requirements.txt

# Or use Poetry
poetry install

# Start Flask dev server
python web/backend/app.py
# Runs on http://0.0.0.0:5000
```

**Flask Development Configuration:**
```python
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  # All interfaces
        port=5000,       # Standard Flask port
        debug=True       # Hot reload, detailed errors
    )
```

### Frontend Setup (Next.js)

```bash
# Install dependencies
cd web
npm install

# Start Next.js dev server
npm run dev
# Runs on http://localhost:3000
```

**Next.js Development Features:**
- Hot Module Replacement (HMR)
- Fast Refresh (component-level reload)
- Error overlay
- TypeScript type checking

### Desktop Interface (PyQt6)

```bash
# Start desktop application
python -m src.app.main

# Or use launcher scripts
.\launch-desktop.bat
.\launch-desktop.ps1
```

**Desktop vs. Web:**
- Desktop: Direct access to core systems
- Web: Routed through governance pipeline
- Both: Share same core business logic

## Docker Deployment

### Docker Compose Setup

**File:** `docker-compose.yml` (root) or `web/docker-compose.yml`

```yaml
version: '3.8'

services:
  # Flask Backend
  backend:
    build:
      context: .
      dockerfile: web/backend/Dockerfile
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./data:/app/data  # Persistent data
      - ./logs:/app/logs  # Log files
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Next.js Frontend
  frontend:
    build:
      context: web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:5000
    depends_on:
      - backend
    restart: unless-stopped

  # PostgreSQL Database (Future)
  # postgres:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: projectai
  #     POSTGRES_USER: projectai
  #     POSTGRES_PASSWORD: ${DB_PASSWORD}
  #   volumes:
  #     - postgres-data:/var/lib/postgresql/data
  #   restart: unless-stopped

# volumes:
#   postgres-data:
```

### Docker Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

### Backend Dockerfile

**Location:** `web/backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY web/backend /app/web/backend
COPY src/app/core /app/src/app/core
COPY src/app/agents /app/src/app/agents
COPY src/app/governance /app/src/app/governance

# Create data directories
RUN mkdir -p /app/data /app/logs

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:5000/api/status || exit 1

# Run application
CMD ["python", "web/backend/app.py"]
```

### Frontend Dockerfile

**Location:** `web/Dockerfile`

```dockerfile
# Multi-stage build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .

# Build Next.js app
RUN npm run build

# Production image
FROM node:20-alpine

WORKDIR /app

# Copy built assets
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package*.json ./

# Install production dependencies only
RUN npm ci --only=production

# Expose port
EXPOSE 3000

# Run Next.js in production mode
CMD ["npm", "start"]
```

## Production Deployment

### Cloud Deployment Options

#### Option 1: Vercel (Frontend) + Railway (Backend)

**Vercel (Next.js):**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd web
vercel --prod
```

**vercel.json:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://backend.railway.app/api/$1"
    }
  ],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://backend.railway.app"
  }
}
```

**Railway (Flask):**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**railway.toml:**
```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "gunicorn --bind 0.0.0.0:$PORT web.backend.app:app"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[env]
OPENAI_API_KEY = "${OPENAI_API_KEY}"
HUGGINGFACE_API_KEY = "${HUGGINGFACE_API_KEY}"
```

#### Option 2: AWS (Full Stack)

**Architecture:**
```
AWS Cloud
├─ Frontend: S3 + CloudFront (static Next.js export)
├─ Backend: ECS Fargate (containerized Flask)
├─ Database: RDS PostgreSQL (future)
├─ Storage: S3 (user data, images)
└─ Load Balancer: ALB (traffic distribution)
```

**Terraform Configuration (Example):**
```hcl
# ECS Fargate for Flask backend
resource "aws_ecs_service" "backend" {
  name            = "projectai-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 5000
  }
}

# CloudFront for Next.js frontend
resource "aws_cloudfront_distribution" "frontend" {
  origin {
    domain_name = aws_s3_bucket.frontend.bucket_regional_domain_name
    origin_id   = "frontend"
  }

  enabled             = true
  default_root_object = "index.html"

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "frontend"

    forwarded_values {
      query_string = false
      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
  }
}
```

#### Option 3: DigitalOcean App Platform

**app.yaml:**
```yaml
name: projectai
region: nyc1

services:
  - name: backend
    dockerfile_path: web/backend/Dockerfile
    source_dir: /
    github:
      repo: IAmSoThirsty/Project-AI
      branch: main
      deploy_on_push: true
    http_port: 5000
    instance_count: 2
    instance_size: basic-xs
    envs:
      - key: OPENAI_API_KEY
        scope: RUN_TIME
        type: SECRET
      - key: HUGGINGFACE_API_KEY
        scope: RUN_TIME
        type: SECRET
    health_check:
      http_path: /api/status

  - name: frontend
    dockerfile_path: web/Dockerfile
    source_dir: web
    github:
      repo: IAmSoThirsty/Project-AI
      branch: main
      deploy_on_push: true
    http_port: 3000
    instance_count: 1
    instance_size: basic-xs
    envs:
      - key: NEXT_PUBLIC_API_URL
        value: ${backend.PUBLIC_URL}
```

### Production Backend Configuration

**Gunicorn (Production WSGI Server):**
```bash
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --threads 2 \
         --timeout 300 \
         --keep-alive 5 \
         --log-level info \
         --access-logfile - \
         --error-logfile - \
         web.backend.app:app
```

**Worker Calculation:**
```
Workers = (2 × CPU cores) + 1
Threads = 2-4 per worker

Example (2 CPUs):
Workers = (2 × 2) + 1 = 5
Threads = 2
Total = 10 concurrent requests
```

**Nginx Reverse Proxy (Optional):**
```nginx
server {
    listen 80;
    server_name api.projectai.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Environment Variables

**Production `.env`:**
```bash
# API Keys
OPENAI_API_KEY=sk-proj-...
HUGGINGFACE_API_KEY=hf_...

# Security
JWT_SECRET_KEY=<generated_secret>  # Use: python -c "import secrets; print(secrets.token_hex(32))"
FERNET_KEY=<generated_key>  # Use: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Flask
FLASK_ENV=production
FLASK_DEBUG=0

# Database (future)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Monitoring
SENTRY_DSN=https://...@sentry.io/...
LOG_LEVEL=INFO
```

## Integration Patterns

### Desktop ↔ Web Core Integration

**Shared Core Systems:**
- `src/app/core/` - All business logic
- `src/app/agents/` - AI agents
- `src/app/governance/` - Governance pipeline

**Desktop Path:**
```
PyQt6 GUI → Direct system calls → Core systems → State
```

**Web Path:**
```
React UI → Flask API → Runtime Router → Governance → Core systems → State
```

**Unified State:**
- Desktop: `data/` directory (JSON files)
- Web: Same `data/` directory
- Both interfaces share same data files

### State Synchronization

**Challenge:** Desktop and web share same files  
**Solution:** File-level locking + atomic writes

```python
import fcntl  # Unix file locking

def save_users(self, users: dict) -> None:
    """Save users with file locking."""
    with open(self.users_file, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
        try:
            json.dump(users, f, indent=2)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Unlock
```

**Windows Alternative:**
```python
import msvcrt  # Windows file locking

def save_users(self, users: dict) -> None:
    """Save users with file locking (Windows)."""
    with open(self.users_file, 'w') as f:
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
        try:
            json.dump(users, f, indent=2)
        finally:
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
```

### API Gateway Pattern (Future)

**Architecture:**
```
Client (Web/Mobile/Desktop)
  ↓
API Gateway (Kong/Traefik)
  ├─ Rate limiting
  ├─ Authentication
  ├─ Load balancing
  └─ Monitoring
     ↓
Flask Backend (multiple instances)
```

## Monitoring & Logging

### Application Logging

**Flask Logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/flask.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

**Structured Logging (Production):**
```python
import structlog

logger = structlog.get_logger()
logger.info("request_received",
    method="POST",
    path="/api/auth/login",
    user="admin",
    ip="192.168.1.100"
)
```

### Monitoring Stack (Production)

**Prometheus + Grafana:**
```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.route('/api/auth/login', methods=['POST'])
@REQUEST_DURATION.time()
def login():
    REQUEST_COUNT.labels(method='POST', endpoint='/api/auth/login').inc()
    # ... login logic ...

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### Error Tracking

**Sentry Integration:**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,  # 10% of transactions
    environment="production",
)
```

## CI/CD Pipeline

### GitHub Actions Workflow

**File:** `.github/workflows/deploy.yml`

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest
      
      - name: Run linter
        run: ruff check .

  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Vercel
        run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

## Performance Optimization

### Backend Optimization

**Caching:**
```python
from functools import lru_cache
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379'})

@cache.memoize(timeout=300)  # Cache for 5 minutes
def get_ai_response(prompt: str) -> str:
    return openai.ChatCompletion.create(...)
```

**Connection Pooling:**
```python
import redis

redis_pool = redis.ConnectionPool(host='localhost', port=6379, max_connections=10)
redis_client = redis.Redis(connection_pool=redis_pool)
```

### Frontend Optimization

**Next.js Static Generation:**
```typescript
export async function generateStaticParams() {
  // Generate static pages at build time
  return [{ locale: 'en' }, { locale: 'es' }];
}
```

**Image Optimization:**
```typescript
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="Project-AI"
  width={200}
  height={200}
  priority
  loading="eager"
/>
```

## Related Systems

- **Desktop Interface:** `src/app/main.py`, `src/app/gui/`
- **Flask Backend:** `web/backend/app.py`
- **Next.js Frontend:** `web/app/`, `web/components/`
- **Core Systems:** `src/app/core/`
- **Governance:** `src/app/governance/`

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-XX  
**Maintainer:** Project-AI Team
