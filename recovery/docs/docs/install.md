# Installation Guide

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, RHEL 8+), macOS 11+, Windows 10+ with WSL2
- **Python**: 3.9 or later
- **Node.js**: 16.x or later (for web components)
- **Docker**: 20.10+ (for containerized deployment)
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: Minimum 20GB available space

### Required Tools

```bash

# Ubuntu/Debian

sudo apt-get update
sudo apt-get install -y python3.9 python3-pip git build-essential

# macOS

brew install python@3.9 node git

# Windows (WSL2)

sudo apt-get update && sudo apt-get install -y python3.9 python3-pip git
```

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash

# Clone the repository

git clone https://github.com/sovereign/sovereign-governance-substrate.git
cd sovereign-governance-substrate

# Run the automated installer

./scripts/install.sh

# Verify installation

python -m src.sovereign --version
```

### Method 2: Manual Installation

#### Step 1: Clone Repository

```bash
git clone https://github.com/sovereign/sovereign-governance-substrate.git
cd sovereign-governance-substrate
```

#### Step 2: Create Virtual Environment

```bash

# Create virtual environment

python3.9 -m venv .venv

# Activate virtual environment

# Linux/macOS:

source .venv/bin/activate

# Windows:

.venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash

# Install Python dependencies

pip install --upgrade pip
pip install -r requirements.txt

# Install development dependencies (optional)

pip install -r requirements-dev.txt

# Install Node.js dependencies (for web UI)

npm install
```

#### Step 4: Configure Environment

```bash

# Copy example environment file

cp .env.example .env

# Edit configuration (use your preferred editor)

nano .env
```

**Required Environment Variables:**
```bash

# Core Configuration

SOVEREIGN_ENV=development
SECRET_KEY=your-secret-key-here

# Database

DATABASE_URL=postgresql://user:pass@localhost:5432/sovereign

# Security

SECURITY_LEVEL=high
ENABLE_AUDIT=true

# API

API_HOST=0.0.0.0
API_PORT=8000
```

#### Step 5: Initialize Database

```bash

# Run database migrations

python -m alembic upgrade head

# Seed initial data

python scripts/seed_database.py
```

#### Step 6: Verify Installation

```bash

# Run health check

python -m src.sovereign check

# Run test suite

pytest tests/
```

### Method 3: Docker Installation

#### Using Docker Compose (Recommended)

```bash

# Clone repository

git clone https://github.com/sovereign/sovereign-governance-substrate.git
cd sovereign-governance-substrate

# Build and start services

docker-compose up -d

# Check status

docker-compose ps

# View logs

docker-compose logs -f

# Access application

open http://localhost:8000
```

#### Using Dockerfile

```bash

# Build image

docker build -t sovereign-governance:latest .

# Run container

docker run -d \
  --name sovereign \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  sovereign-governance:latest

# Check logs

docker logs -f sovereign
```

### Method 4: Kubernetes Deployment

```bash

# Apply Kubernetes manifests

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check deployment status

kubectl get pods -n sovereign

# Access service

kubectl port-forward -n sovereign svc/sovereign-api 8000:8000
```

## Post-Installation Configuration

### Generate Security Keys

```bash

# Generate sovereign keypair

python scripts/rotate_sovereign_keypair.py --generate

# Initialize security context

python -m src.security.init_context
```

### Configure Governance Policies

```bash

# Load default policies

python scripts/load_policies.py --config config/policies/default.yaml

# Verify policy integrity

python -m src.governance.verify_policies
```

### Initialize Cognition System

```bash

# Download pre-trained models

python scripts/download_models.py

# Initialize cognition kernel

python -m src.cognition.init_kernel

# Verify cognition system

python -m src.cognition.validate
```

## Verification

### Run System Checks

```bash

# Comprehensive health check

python -m src.sovereign check --verbose

# Component verification

python verify_runtime_setup.py

# Security audit

python -m src.security.audit
```

### Access Web Interface

```bash

# Start the web server

python -m src.app.web

# Access at http://localhost:8000

# Default credentials: admin / changeme

```

### Run Example Workload

```bash

# Execute sample governance decision

python examples/governance_decision.py

# Run cognition inference

python examples/cognition_inference.py
```

## Troubleshooting

### Common Issues

#### Import Errors

```bash

# Problem: ModuleNotFoundError

# Solution: Ensure virtual environment is activated and dependencies installed

source .venv/bin/activate
pip install -r requirements.txt
```

#### Database Connection Errors

```bash

# Problem: Unable to connect to database

# Solution: Verify DATABASE_URL and PostgreSQL is running

docker-compose up -d postgres
python -m src.data.test_connection
```

#### Permission Errors

```bash

# Problem: Permission denied

# Solution: Fix ownership or run with appropriate permissions

sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

#### Port Already in Use

```bash

# Problem: Address already in use

# Solution: Change port in .env or stop conflicting process

lsof -i :8000

# or change API_PORT in .env

```

## Upgrading

### Upgrade to Latest Version

```bash

# Pull latest changes

git pull origin main

# Update dependencies

pip install -r requirements.txt --upgrade
npm install

# Run migrations

python -m alembic upgrade head

# Restart services

docker-compose restart
```

## Uninstalling

### Remove Installation

```bash

# Stop services

docker-compose down

# Remove virtual environment

deactivate
rm -rf .venv

# Remove data (CAUTION: This deletes all data!)

docker-compose down -v
```

## Next Steps

- Read the [Quick Start Guide](QUICKSTART.md)
- Review [Architecture Documentation](docs/architecture/)
- Explore [API Documentation](docs/api/)
- Join the [Community](https://community.sovereign.local)

## Support

- **Documentation**: https://docs.sovereign.local
- **GitHub Issues**: https://github.com/sovereign/issues
- **Community Forum**: https://community.sovereign.local
- **Email**: support@sovereign.local

---
*Generated by Fleet B Phase 2 Enhanced Documentation Generator*
