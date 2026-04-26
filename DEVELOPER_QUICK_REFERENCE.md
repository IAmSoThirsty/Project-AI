---
title: "Developer Quick Reference"
id: developer-quick-reference
type: reference
version: 1.1.0
created_date: 2025-11-15
updated_date: 2026-04-20
status: active
author: "Development Team <projectaidevs@gmail.com>"
tags:
  - development
  - development/python
  - development/testing
  - development/tooling
  - development/ci-cd
  - operations
  - operations/deployment
  - reference
  - guide
  - quickstart
area:
  - development
  - operations
audience:
  - developer
  - contributor
priority: p0
related_to:
  - "[[README]]"
  - "[[ARCHITECTURE_QUICK_REF]]"
  - "[[DESKTOP_APP_QUICKSTART]]"
  - "[[CONTRIBUTING]]"
  - "[[COPILOT_MANDATORY_GUIDE]]"
  - "[[PROGRAM_SUMMARY]]"
  - "[[AGENT-084-LEARNING-PATHS]]"
depends_on:
  - "[[README]]"
what: "Essential command reference for daily development tasks - environment setup (.env keys), running desktop UI/tests, linting (ruff/isort/black), CI pipeline, secrets management, and troubleshooting data/ directory issues"
who: "Developers executing common development workflows - quick command lookup without reading full documentation"
when: "During development for command syntax, setting up new environments, debugging linting/test failures, configuring CI"
where: "Root directory as frequently-accessed command reference - complements detailed guides with essential commands only"
why: "Eliminates need to search documentation for common commands, provides correct module invocation pattern (python -m src.app.main), documents required .env keys (OPENAI_API_KEY, HUGGINGFACE_API_KEY, FERNET_KEY), prevents secrets in git"
---

# Developer Quick Reference

Essential commands for development. For comprehensive development patterns, see [[COPILOT_MANDATORY_GUIDE]].

---

## Environment Setup

Create `.env` in repository root with required keys (do NOT commit):

```bash
OPENAI_API_KEY=sk-...           # From https://platform.openai.com/api-keys
HUGGINGFACE_API_KEY=hf_...      # From https://huggingface.co/settings/tokens
FERNET_KEY=<generated_key>      # Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Learn More**: [[COPILOT_MANDATORY_GUIDE]] → Environment Setup for complete configuration details

---

## Running the Application

### Desktop UI

```bash
python -m src.app.main
```

**Important**: Always use `python -m src.app.main`, NOT `python src/app/main.py` (breaks imports)

**Learn More**:
- Installation: [[DESKTOP_APP_QUICKSTART]]
- GUI Architecture: [[PROGRAM_SUMMARY]] → GUI Architecture
- Integration Patterns: [[INTEGRATION_GUIDE]]

### Tests

```bash
pytest -v                        # Run all tests with verbose output
pytest tests/test_ai_systems.py  # Run specific test file
pytest -k "test_persona"         # Run tests matching pattern
pytest --cov=src                 # Run with coverage report
```

**Learn More**:
- Testing Strategy: [[ARCHITECTURE_QUICK_REF]] → Testing Strategy
- Test Patterns: [[PROGRAM_SUMMARY]] → Testing section
- Test Coverage Matrix: [[ARCHITECTURE_QUICK_REF]] → Test Coverage Matrix

---

## Linting & Formatting

```bash
# Linting
ruff check .                     # Check for issues
ruff check . --fix              # Auto-fix issues

# Formatting
isort src tests --profile black  # Sort imports
black src tests                  # Format code

# Pre-commit hooks
pre-commit install              # Install hooks
pre-commit run --all-files      # Run all hooks
```

**Configuration**: See `pyproject.toml` for ruff/black/isort settings

**Learn More**:
- Development Workflows: [[COPILOT_MANDATORY_GUIDE]] → Development Workflows
- Code Quality: [[.github/instructions/codacy.instructions.md]]
- Import Organization: [[COPILOT_MANDATORY_GUIDE]] → Import Organization

---

## CI/CD

GitHub Actions will automatically run on PRs:
- ✅ Linting (ruff)
- ✅ Tests (pytest)
- ✅ Type checking (mypy)
- ✅ Security audit (pip-audit)
- ✅ Codacy analysis
- ✅ Docker smoke test

**Workflows**: See `.github/workflows/` for pipeline details

**Learn More**:
- CI Pipeline: [[docs/developer/deployment/DEPLOYMENT_GUIDE]]
- Production Deployment: [[INFRASTRUCTURE_PRODUCTION_GUIDE]]
- Automated Workflows: [[COPILOT_MANDATORY_GUIDE]] → Automated Workflows

---

## Docker

```bash
# Development
docker-compose up                # Start dev environment
docker-compose down              # Stop environment

# Production build
docker build -t project-ai:latest .
docker run -p 8000:8000 project-ai:latest
```

**Learn More**:
- Docker Details: [[PROGRAM_SUMMARY]] → Deployment Workflows
- Production Kubernetes: [[INFRASTRUCTURE_PRODUCTION_GUIDE]]
- Container Architecture: [[COPILOT_MANDATORY_GUIDE]] → Deployment Workflows

---

## Secrets Management

**Critical**: Do NOT commit secrets to repository

- **Local Development**: Use `.env` file (already in `.gitignore`)
- **CI/CD**: Use GitHub Secrets
- **Production**: Use secure secret store (Vault, AWS Secrets Manager, etc.)

**Learn More**:
- Security Overview: [[SECURITY]]
- Secrets Best Practices: [[PROGRAM_SUMMARY]] → Security Layers
- Password Security: [[COPILOT_MANDATORY_GUIDE]] → Password Security

---

## Troubleshooting

### Persistence Failures

If data persistence fails on a fresh clone:

```bash
mkdir -p data/ai_persona data/memory data/learning_requests
```

The application will create these directories at runtime, but pre-creating them can prevent issues.

**Learn More**:
- Data Persistence Pattern: [[ARCHITECTURE_QUICK_REF]] → State Persistence
- Data Directory Structure: [[PROGRAM_SUMMARY]] → Data Persistence
- Persistence Gotchas: [[COPILOT_MANDATORY_GUIDE]] → Critical Gotchas → Data directory creation

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**: Always run from project root with `python -m src.app.main`

**Learn More**: [[COPILOT_MANDATORY_GUIDE]] → Module Imports

### GUI Not Responding

**Problem**: GUI freezes during long operations

**Solution**: Use `QTimer` for delays, never `threading.Thread`

**Learn More**:
- PyQt6 Threading: [[ARCHITECTURE_QUICK_REF]] → Threading in PyQt6
- GUI Patterns: [[COPILOT_MANDATORY_GUIDE]] → PyQt6 threading
- Integration Guide: [[INTEGRATION_GUIDE]]

---

## 🎓 Learn More

**First-time setup?** Follow [[DESKTOP_APP_QUICKSTART]] to get the application running.

**Need architecture overview?** See [[ARCHITECTURE_QUICK_REF]] for visual diagrams and data flows.

**Contributing code?** Read [[COPILOT_MANDATORY_GUIDE]] for comprehensive development patterns and gotchas.

**Deep-dive into implementation?** Explore [[PROGRAM_SUMMARY]] for complete 600+ line architecture documentation.

**Navigate all docs?** Check [[AGENT-084-LEARNING-PATHS]] for complete learning paths from quickstart to expert.

---

**Version**: 1.1.0  
**Status**: Production Ready  
**Last Updated**: 2026-04-20
