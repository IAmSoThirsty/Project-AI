---
title: CLI Interface Overview
type: technical-guide
audience: [developers, devops, system-administrators]
classification: P0-Core
tags: [cli, command-line, interface, tooling]
created: 2024-01-20
last_verified: 2024-01-20
status: current
related_systems: [automation, build-system, deployment]
---

# CLI Interface Overview

**Complete command-line interface documentation for Project-AI.**

## Executive Summary

Project-AI provides a comprehensive CLI ecosystem with three layers:
1. **Sovereign Runtime CLI** - Cryptographic governance enforcement (`project-ai`)
2. **Python Package CLI** - Desktop application launcher (`project-ai` entry point)
3. **Build Automation** - Multi-platform build orchestration (Gradle, npm, Make)

---

## Architecture

### Layer 1: Sovereign Runtime CLI

**Entry Point:** `project_ai_cli.py`  
**Installation:** `pip install -e .` creates `project-ai` command

#### Core Commands

```bash
# Run sovereign demonstration pipeline
project-ai run examples/sovereign-demo.yaml

# Comprehensive third-party verification
project-ai sovereign-verify --bundle compliance_bundle.json
project-ai sovereign-verify --bundle compliance.zip --output report.json

# Verify audit trail integrity
project-ai verify-audit governance/sovereign_data/immutable_audit.jsonl

# Verify compliance bundle
project-ai verify-bundle governance/sovereign_data/artifacts/*/compliance_bundle.json
```

#### Command Details

| Command | Purpose | Output |
|---------|---------|--------|
| `run` | Execute sovereign pipeline with cryptographic enforcement | Artifacts + audit trail |
| `sovereign-verify` | Comprehensive third-party auditor verification | JSON verification report |
| `verify-audit` | Validate audit trail hash chain integrity | Pass/fail with issues |
| `verify-bundle` | Verify compliance bundle cryptographic proofs | Pass/fail with issues |

**Key Features:**
- ✅ Cryptographic proof generation (Ed25519 signatures)
- ✅ Immutable audit trail validation (hash chain)
- ✅ Role-based signature authority mapping
- ✅ Policy resolution tracing
- ✅ Timestamped attestation generation

### Layer 2: Desktop Application CLI

**Entry Point:** `src/app/main.py`  
**Installation:** Multiple launch methods

#### Launch Methods

```bash
# Method 1: Python module (recommended)
python -m src.app.main

# Method 2: Console script (after pip install -e .)
project-ai

# Method 3: Direct launch scripts
.\scripts\launch-desktop.ps1       # PowerShell
.\scripts\launch-desktop.bat       # Batch
```

**Critical:** Always use `python -m src.app.main` for imports to work correctly. PYTHONPATH must include `src/` for `from app.core import ...` imports.

### Layer 3: Build System CLI

#### Make (POSIX Systems)

```bash
make run         # Launch desktop application
make test        # Run pytest test suite
make lint        # Run ruff linter
make format      # Format code (isort + ruff + black)
make precommit   # Run pre-commit hooks
```

#### npm Scripts

```bash
npm test              # Run JS + Python tests
npm run test:js       # Run Node.js tests
npm run test:python   # Run pytest (quiet mode)
npm run lint          # Run ruff linter
npm run format        # Auto-fix with ruff
npm run dev           # Start Docker Compose stack
npm run build         # Build Docker image
npm run lint:markdown # Lint markdown files
```

#### TARL Build System

```bash
npm run tarl:build   # Build TARL artifacts
npm run tarl:clean   # Clean build cache
npm run tarl:list    # List registered targets
npm run tarl:cache   # Show cache statistics
```

---

## Installation & Setup

### Prerequisites

```bash
# Required
Python 3.11+
Node.js 18+
Git

# Optional (for full features)
Docker
Gradle 7.5+
```

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/IAmSoThirsty/Project-AI
cd Project-AI

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
source .venv/bin/activate   # Linux/macOS

# 3. Install package in editable mode
pip install -e .

# 4. Install development dependencies
pip install -r requirements-dev.txt

# 5. Install Node.js dependencies (optional, for testing/linting)
npm install

# 6. Verify installation
project-ai --help        # Sovereign CLI
python -m src.app.main   # Desktop application
pytest --version         # Test framework
```

---

## Environment Configuration

### Required Environment Variables

Create `.env` file in project root:

```bash
# OpenAI API (for GPT models and DALL-E)
OPENAI_API_KEY=sk-...

# Hugging Face (for Stable Diffusion)
HUGGINGFACE_API_KEY=hf_...

# Encryption (generate with Fernet.generate_key())
FERNET_KEY=<32-byte-key>

# Email Alerts (optional)
SMTP_USERNAME=<optional>
SMTP_PASSWORD=<optional>
```

### Generate Fernet Key

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

---

## Common Workflows

### Development Workflow

```bash
# 1. Launch desktop application
python -m src.app.main

# 2. Run tests
pytest -v

# 3. Lint code
ruff check .

# 4. Auto-fix issues
ruff check . --fix

# 5. Format code
black src tests
```

### Production Build Workflow

```bash
# Build all platforms
.\scripts\build_production.ps1 -All

# Build specific platform
.\scripts\build_production.ps1 -Desktop
.\scripts\build_production.ps1 -Android

# Create portable USB installer
.\scripts\create_portable_usb.ps1
```

### Docker Workflow

```bash
# Start all services
docker-compose up

# Build custom image
docker build -t project-ai:latest .

# Run health checks
docker-compose exec cerberus python scripts/healthcheck.py
```

---

## CLI Design Patterns

### Error Handling

All CLI commands follow consistent error handling:

```python
import sys
import logging

logger = logging.getLogger(__name__)

def cmd_example(args):
    try:
        # Operation
        result = perform_operation(args)
        
        if result["status"] == "success":
            logger.info("✅ Operation successful")
            sys.exit(0)
        else:
            logger.error("❌ Operation failed: %s", result.get("error"))
            sys.exit(1)
    except Exception as e:
        logger.error("Fatal error: %s", e)
        sys.exit(1)
```

### Logging Pattern

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
```

### Argument Parsing Pattern

```python
import argparse

parser = argparse.ArgumentParser(
    description="Project-AI CLI",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog="""
Examples:
  project-ai run pipeline.yaml
  project-ai verify-audit audit.jsonl
    """
)

subparsers = parser.add_subparsers(dest="command")

# Add subcommands
run_parser = subparsers.add_parser("run", help="Run pipeline")
run_parser.add_argument("pipeline", help="Path to pipeline YAML")

args = parser.parse_args()
```

---

## Exit Codes

| Exit Code | Meaning | Usage |
|-----------|---------|-------|
| 0 | Success | Operation completed successfully |
| 1 | General error | Command failed or validation error |
| 2 | Warning | Operation completed with warnings |

---

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
# Use module invocation
python -m src.app.main

# Or set PYTHONPATH
export PYTHONPATH="${PWD}/src:${PYTHONPATH}"
python src/app/main.py
```

### Virtual Environment Issues

**Problem:** Commands not found after installation

**Solution:**
```bash
# Deactivate and reactivate
deactivate
.venv\Scripts\Activate.ps1

# Reinstall in editable mode
pip install -e .
```

### Permission Errors (Windows)

**Problem:** PowerShell script execution blocked

**Solution:**
```powershell
# Allow script execution (admin required)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass
powershell -ExecutionPolicy Bypass -File script.ps1
```

---

## Best Practices

### ✅ DO

- Use `python -m src.app.main` for consistent imports
- Always activate virtual environment before running commands
- Use `--dry-run` flags to preview changes
- Check exit codes in automation scripts
- Use verbose flags (`-v`, `--verbose`) for debugging

### ❌ DON'T

- Don't use `python src/app/main.py` (breaks imports)
- Don't install packages globally (use virtual environment)
- Don't skip environment variable configuration
- Don't ignore exit codes in scripts
- Don't run production commands without testing in dry-run mode

---

## Performance Considerations

### CLI Response Times

| Operation | Target | Typical |
|-----------|--------|---------|
| `project-ai run` | <30s | 5-15s |
| `project-ai sovereign-verify` | <10s | 2-5s |
| `project-ai verify-audit` | <5s | 1-2s |
| `python -m src.app.main` | <10s | 3-7s |

### Optimization Tips

1. **Use parallel execution** for batch operations
2. **Enable caching** for repeated operations
3. **Use `--quiet` flags** to reduce output overhead
4. **Run lint/format** on changed files only (use `git diff`)

---

## Security Considerations

### Credential Management

- **NEVER** commit `.env` files to version control
- Use environment variables for secrets
- Rotate API keys regularly
- Use Fernet encryption for sensitive data storage

### Audit Trail Integrity

- Verify audit trails before accepting compliance bundles
- Validate hash chain integrity with `verify-audit`
- Check signature authorities with `sovereign-verify`
- Store compliance bundles in tamper-evident storage

---

## Related Documentation

- **[02-AUTOMATION-SCRIPTS.md](./02-AUTOMATION-SCRIPTS.md)** - PowerShell automation scripts
- **[03-BUILD-SYSTEM.md](./03-BUILD-SYSTEM.md)** - Gradle, npm, Make build systems
- **[04-SOVEREIGN-CLI.md](./04-SOVEREIGN-CLI.md)** - Cryptographic governance CLI
- **[05-DESKTOP-LAUNCHER.md](./05-DESKTOP-LAUNCHER.md)** - Desktop application launcher

---

**AGENT-038: CLI & Automation Documentation Specialist**  
*Comprehensive command-line interface documentation.*
