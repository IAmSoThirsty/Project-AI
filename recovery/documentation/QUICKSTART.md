# Project-AI Quickstart Guide

**Goal:** Get from fresh clone to working demo in <30 minutes

---

## Prerequisites

- Python 3.11+ (3.12 recommended)
- Docker (optional, for containerized deployment)
- Git

---

## Quick Start (5 minutes)

```bash

# 1. Clone repository

git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# 2. Create virtual environment (Python 3.12)

python -m venv .venv

# Windows

.venv\Scripts\activate

# Linux/Mac

source .venv/bin/activate

# 3. Install dependencies

pip install -r requirements.txt

# 4. Verify installation

python --version  # Should show 3.11+
python src/app/cli.py --help

# 5. Run smoke tests

pytest tests/test_smoke.py -v

# Expected: 20/21 passing in <1 second

```

**✅ Success:** CLI shows help with 7 command groups

---

## Using the CLI

```bash

# Show version

python src/app/cli.py --version

# Health check

python src/app/cli.py health status

# User management

python src/app/cli.py user create --help

# System operations

python src/app/cli.py system status

# AI commands

python src/app/cli.py ai --help
```

---

## Docker Deployment (10 minutes)

```bash

# 1. Build image

docker build -t project-ai:latest .

# Build time: ~3 minutes

# 2. Run container

docker run -d --name project-ai project-ai:latest

# 3. Check logs

docker logs project-ai

# Expected: "Sovereign Substrate is now OPERATIONAL"

# 4. Cleanup

docker stop project-ai
docker rm project-ai
```

---

## Kubernetes Deployment (15 minutes)

```bash

# 1. Ensure kubectl configured

kubectl cluster-info

# 2. Apply minimal deployment

kubectl apply -f k8s/minimal-deploy.yaml

# 3. Verify deployment

kubectl get all -n project-ai

# 4. Check pod logs

kubectl logs -n project-ai -l app=project-ai

# 5. Port forward (optional)

kubectl port-forward -n project-ai svc/project-ai 8080:80

# 6. Cleanup

kubectl delete -f k8s/minimal-deploy.yaml
```

---

## Running Tests

```bash

# Smoke tests (fast)

pytest tests/test_smoke.py -v

# With coverage

pytest tests/test_smoke.py --cov=src

# Full test suite (slower, some may fail)

pytest tests/ --cov=src --cov-report=html

# Open htmlcov/index.html for coverage report

```

---

## Development Setup

```bash

# Install test dependencies

pip install -r requirements-test.txt

# Install development tools

pip install -r requirements-dev.txt

# Run linters

ruff check src/ tests/
black --check src/ tests/

# Fix formatting

black src/ tests/
```

---

## Project Structure

```
Project-AI/
├── src/
│   ├── app/
│   │   ├── cli.py          # Main CLI entry point ✅
│   │   ├── core/           # Core modules
│   │   └── ui/             # UI components
│   ├── cognition/          # AI orchestration ✅
│   ├── security/           # Security modules ✅
│   └── thirsty_lang/       # Custom language
├── tests/
│   └── test_smoke.py       # Fast verification tests ✅
├── k8s/                    # Kubernetes manifests ✅
├── Dockerfile              # Docker build ✅
└── requirements.txt        # Python dependencies
```

✅ = Verified working

---

## Common Issues

### Python Version Error

```
Error: Python 3.11+ required
Solution: Install Python 3.12 and recreate venv
```

### Import Errors

```
Error: ModuleNotFoundError
Solution: Ensure PYTHONPATH includes src/
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
```

### Docker Build Fails

```
Error: Dependency conflict
Solution: requirements.txt updated, pull latest and rebuild
```

---

## What Works Now

✅ CLI with 7 command groups
✅ Core module imports (cognition, governance, AI systems)
✅ Smoke tests (20/21 passing)
✅ Docker containerization
✅ Kubernetes deployment manifests
✅ 17% test coverage

---

## What's Experimental

⚠️ GUI application (encoding issues)
⚠️ Full test suite (31 files with import errors)
⚠️ Some advanced features (documented in code)

---

## Next Steps

1. **Explore CLI**: `python src/app/cli.py --help`
2. **Read Documentation**: See README.md, PRODUCTION_ROADMAP.md
3. **Run Tests**: `pytest tests/test_smoke.py -v`
4. **Deploy Docker**: `docker build -t project-ai .`
5. **Check Status**: See COMPLETION_MANIFEST.md for details

---

## Getting Help

- README.md - Project overview
- PRODUCTION_ROADMAP.md - Development plan
- TEST_SUITE_STATUS.md - Test status
- k8s/K8S_DEPLOYMENT_GUIDE.md - K8s deployment
- CONTRIBUTING.md - Contribution guide

---

**Time to working demo: <10 minutes** (CLI + smoke tests)
**Time to Docker: <15 minutes** (includes build)
**Time to K8s: <30 minutes** (includes setup)

**Last Updated:** 2026-04-09
