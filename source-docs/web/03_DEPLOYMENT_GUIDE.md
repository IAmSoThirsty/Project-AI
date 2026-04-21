---
type: deployment-guide
module: web
tags: [deployment, docker, production, github-pages, vercel, nginx]
created: 2026-04-20
status: production
related_systems: [flask-backend, nextjs-frontend, infrastructure]
stakeholders: [devops-team, platform-team, security-team]
platform: web
dependencies: [docker, nginx, github-actions, vercel-cli]
---

# Web Deployment Guide

**Purpose:** Production deployment strategies for Project-AI web application  
**Targets:** GitHub Pages, Vercel, Docker, VPS (Nginx)  
**Requirements:** Docker 24+, Node.js 18+, Python 3.11+

---

## Table of Contents

1. [Deployment Architecture](#deployment-architecture)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [GitHub Pages Deployment](#github-pages-deployment)
5. [Vercel Deployment](#vercel-deployment)
6. [VPS Deployment (Nginx)](#vps-deployment-nginx)
7. [Environment Configuration](#environment-configuration)
8. [Security Hardening](#security-hardening)
9. [Monitoring & Logging](#monitoring--logging)
10. [Troubleshooting](#troubleshooting)

---

## Deployment Architecture

### Multi-Tier Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Load Balancer / CDN                      │
│                    (Cloudflare / AWS ALB)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐           ┌────▼─────┐
    │ Frontend │           │ Frontend │
    │ (Next.js)│           │ (Next.js)│
    │  Port 80 │           │  Port 80 │
    └────┬─────┘           └────┬─────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   API Gateway / Proxy │
         │       (Nginx)         │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   Flask Backend       │
         │   (Gunicorn)          │
         │   Port 5000           │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   Core Systems        │
         │   (Python modules)    │
         └───────────────────────┘
```

### Deployment Options Comparison

| Feature | GitHub Pages | Vercel | Docker (VPS) | Bare Metal (VPS) |
|---------|-------------|--------|--------------|------------------|
| **Cost** | Free | Free tier | $5-10/mo | $5-10/mo |
| **Static Frontend** | ✅ | ✅ | ✅ | ✅ |
| **Backend Support** | ❌ | ✅ (serverless) | ✅ | ✅ |
| **Custom Domain** | ✅ | ✅ | ✅ | ✅ |
| **SSL/TLS** | ✅ (auto) | ✅ (auto) | Manual | Manual |
| **CI/CD** | ✅ (Actions) | ✅ (auto) | Manual | Manual |
| **Scalability** | High | Very High | Medium | Low |
| **Complexity** | Low | Low | Medium | High |

**Recommendation:** 
- **Development/Demo:** GitHub Pages (frontend only)
- **Production (hobby):** Vercel (full-stack)
- **Production (enterprise):** Docker on VPS (full control)

---

## Local Development Setup

### Prerequisites

```bash
# Required software
node --version   # 18.0.0+
npm --version    # 9.0.0+
python --version # 3.11+
docker --version # 24.0.0+
```

### Backend Setup

```bash
# Clone repository
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run backend
cd web/backend
python app.py
# Backend running on http://localhost:5000
```

### Frontend Setup

```bash
# Navigate to web directory
cd web

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env (NEXT_PUBLIC_API_URL=http://localhost:5000)

# Run frontend
npm run dev
# Frontend running on http://localhost:3000
```

### Verify Setup

```bash
# Test backend
curl http://localhost:5000/api/status
# Expected: {"status":"ok","component":"web-backend"}

# Test frontend
# Open browser: http://localhost:3000
# Expected: Login page with "Backend Online" indicator
```

---

## Docker Deployment

### Single Container (Development)

**Dockerfile (Backend):**
```dockerfile
FROM python:3.11-slim AS backend

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY web/backend/ ./web/backend/

# Create data directory
RUN mkdir -p data logs

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:5000/api/status')"

# Run with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web.backend.app:app"]
```

**Dockerfile (Frontend):**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Install dependencies
COPY web/package*.json ./
RUN npm ci

# Copy source code
COPY web/ ./

# Build static export
RUN npm run build

# Production image
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/out /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose (Production)

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: project-ai-backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: project-ai-frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - app-network
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro

networks:
  app-network:
    driver: bridge

volumes:
  data:
  logs:
```

### Deploy with Docker Compose

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart
```

### Docker Health Checks

```bash
# Check backend health
curl http://localhost:5000/api/status

# Check container health
docker ps
# Look for "(healthy)" status

# View health check logs
docker inspect project-ai-backend --format='{{json .State.Health}}'
```

---

## GitHub Pages Deployment

### Automated Deployment (GitHub Actions)

**File:** `.github/workflows/nextjs.yml`

```yaml
name: Deploy Next.js to GitHub Pages

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 18
          cache: 'npm'
          cache-dependency-path: web/package-lock.json

      - name: Install dependencies
        working-directory: ./web
        run: npm ci

      - name: Build with Next.js
        working-directory: ./web
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: https://api.your-domain.com

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./web/out

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

### Manual Deployment

```bash
# Build static export
cd web
npm run build

# The ./out/ directory contains the static site

# Deploy to gh-pages branch (using gh-pages package)
npm install -g gh-pages
gh-pages -d out

# Or manually
git checkout gh-pages
cp -r out/* .
git add .
git commit -m "Deploy frontend"
git push origin gh-pages
```

### GitHub Pages Configuration

1. Go to repository **Settings** → **Pages**
2. **Source:** Deploy from branch
3. **Branch:** `gh-pages` / `root`
4. **Custom domain:** (optional) `your-domain.com`
5. **Enforce HTTPS:** ✅ Enabled

**Note:** GitHub Pages only serves static files. Backend must be hosted separately (Heroku, Railway, Render).

---

## Vercel Deployment

### Automated Deployment (Git Integration)

**1. Connect Repository:**
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Link project
cd web
vercel link
```

**2. Configure Project:**

**File:** `vercel.json`

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "out",
  "framework": "nextjs",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://your-backend.com/api/:path*"
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        }
      ]
    }
  ]
}
```

**3. Deploy:**
```bash
# Deploy to production
vercel --prod

# Deploy to preview
vercel
```

### Environment Variables (Vercel)

**Dashboard:** Project Settings → Environment Variables

```bash
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_APP_NAME=Project-AI
NEXT_PUBLIC_ENV=production
```

### Vercel Serverless Functions (Optional)

**File:** `api/status.ts`

```typescript
import type { VercelRequest, VercelResponse } from '@vercel/node';

export default function handler(req: VercelRequest, res: VercelResponse) {
  res.status(200).json({ status: 'ok', component: 'vercel-backend' });
}
```

---

## VPS Deployment (Nginx)

### Server Setup (Ubuntu 22.04)

**1. Initial Setup:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3-pip python3-venv
sudo apt install -y nodejs npm
sudo apt install -y nginx certbot python3-certbot-nginx
sudo apt install -y git curl

# Create app user
sudo useradd -m -s /bin/bash projectai
sudo su - projectai
```

**2. Clone Repository:**
```bash
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# Setup backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd web
npm ci
npm run build
```

**3. Systemd Service (Backend):**

**File:** `/etc/systemd/system/project-ai-backend.service`

```ini
[Unit]
Description=Project-AI Flask Backend
After=network.target

[Service]
Type=notify
User=projectai
Group=projectai
WorkingDirectory=/home/projectai/Project-AI
Environment="PATH=/home/projectai/Project-AI/venv/bin"
ExecStart=/home/projectai/Project-AI/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:5000 \
    --access-logfile /var/log/project-ai/access.log \
    --error-logfile /var/log/project-ai/error.log \
    web.backend.app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable project-ai-backend
sudo systemctl start project-ai-backend
sudo systemctl status project-ai-backend
```

**4. Nginx Configuration:**

**File:** `/etc/nginx/sites-available/project-ai`

```nginx
# Upstream backend
upstream backend {
    server 127.0.0.1:5000;
}

# HTTP → HTTPS redirect
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';" always;

    # Frontend (static files)
    root /home/projectai/Project-AI/web/out;
    index index.html;

    # API proxy
    location /api/ {
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

    # Frontend routes (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Static assets caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    gzip_vary on;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}
```

**Enable Site:**
```bash
sudo ln -s /etc/nginx/sites-available/project-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**5. SSL Certificate (Let's Encrypt):**
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
# Auto-renewal is configured via cron
```

---

## Environment Configuration

### Production Environment Variables

**Backend (`.env`):**
```bash
# Flask
FLASK_ENV=production
SECRET_KEY=<generate-with-python-secrets.token_urlsafe(32)>
DEBUG=False

# API Keys
OPENAI_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...

# Security
FERNET_KEY=<generate-with-cryptography.fernet.Fernet.generate_key()>

# Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:pass@localhost:5432/projectai

# Email (for emergency alerts)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
```

**Frontend (`.env`):**
```bash
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_APP_NAME=Project-AI
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENV=production
```

### Secrets Management

**Using Docker Secrets:**
```bash
# Create secrets
echo "sk-..." | docker secret create openai_api_key -

# Use in docker-compose.yml
services:
  backend:
    secrets:
      - openai_api_key
    environment:
      - OPENAI_API_KEY_FILE=/run/secrets/openai_api_key

secrets:
  openai_api_key:
    external: true
```

**Using GitHub Actions Secrets:**
```yaml
# .github/workflows/deploy.yml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

---

## Security Hardening

### 1. Firewall Configuration (UFW)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. Fail2Ban (Brute Force Protection)

```bash
sudo apt install fail2ban

# Configure
sudo nano /etc/fail2ban/jail.local
```

```ini
[sshd]
enabled = true
maxretry = 3
bantime = 3600

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 5
```

### 3. Regular Updates

```bash
# Auto-updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

### 4. Database Security

```bash
# PostgreSQL (if used)
sudo -u postgres psql
ALTER USER projectai WITH PASSWORD 'strong-random-password';
REVOKE ALL ON DATABASE projectai FROM PUBLIC;
```

---

## Monitoring & Logging

### Application Logging

**Backend:**
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/backend.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)
handler.setFormatter(logging.Formatter(
    '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
```

**Nginx Access Logs:**
```bash
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Health Monitoring

**Uptime Monitoring:**
- [UptimeRobot](https://uptimerobot.com) (free, 50 monitors)
- [Pingdom](https://www.pingdom.com)

**Application Monitoring:**
- [Sentry](https://sentry.io) (error tracking)
- [Prometheus](https://prometheus.io) + [Grafana](https://grafana.com)

**Example: Sentry Integration:**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment="production"
)
```

---

## Troubleshooting

### Issue: Backend Not Starting

**Symptom:** Service fails to start

**Solution:**
```bash
# Check logs
sudo journalctl -u project-ai-backend -n 50

# Check port
sudo lsof -i :5000

# Test manually
cd /home/projectai/Project-AI
source venv/bin/activate
python web/backend/app.py
```

### Issue: Nginx 502 Bad Gateway

**Symptom:** API requests return 502 error

**Solution:**
```bash
# Check backend is running
curl http://127.0.0.1:5000/api/status

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart services
sudo systemctl restart project-ai-backend
sudo systemctl reload nginx
```

### Issue: SSL Certificate Renewal Fails

**Symptom:** Certificate expires, HTTPS broken

**Solution:**
```bash
# Renew manually
sudo certbot renew --force-renewal

# Check auto-renewal
sudo certbot renew --dry-run

# View cron job
sudo crontab -l
```

### Issue: Docker Container Crashes

**Symptom:** Container exits unexpectedly

**Solution:**
```bash
# View logs
docker logs project-ai-backend

# Check health
docker inspect project-ai-backend --format='{{json .State.Health}}'

# Restart
docker-compose restart backend
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Run all tests (`pytest -v`)
- [ ] Run linting (`ruff check .`)
- [ ] Update version in `package.json`
- [ ] Update `CHANGELOG.md`
- [ ] Tag release (`git tag v1.0.0`)
- [ ] Build Docker images locally
- [ ] Test Docker containers locally

### Production Deployment

- [ ] Set all environment variables
- [ ] Generate secure `SECRET_KEY`
- [ ] Configure CORS whitelist (remove `localhost`)
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Configure rate limiting
- [ ] Set up monitoring (Sentry, Uptime Robot)
- [ ] Configure logging
- [ ] Set up backups (daily database dumps)
- [ ] Test all endpoints
- [ ] Load testing (optional)

### Post-Deployment

- [ ] Verify health check (`/api/status`)
- [ ] Test authentication flow
- [ ] Test AI features (chat, image gen)
- [ ] Monitor logs for errors
- [ ] Set up alerts (email/Slack)
- [ ] Document deployment in wiki

---

## Related Documentation

- [Flask Backend API](./01_FLASK_BACKEND_API.md)
- [React Frontend](./02_REACT_FRONTEND.md)
- [Security Best Practices](./04_SECURITY_PRACTICES.md)
- [Docker Configuration](../infrastructure/DOCKER.md)

---

**Last Updated:** 2026-04-20  
**Maintainer:** DevOps Team  
**Review Cycle:** Monthly
