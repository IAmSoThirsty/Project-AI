---
title: CLI Interface Relationships
description: Main command-line interface entry points and command tree structure
tags:
  - relationships
  - cli
  - interface
  - commands
created: 2025-02-08
agent: AGENT-063
---

# CLI Interface Relationships

## Overview

Project-AI provides **3 primary CLI interfaces** and **multiple launcher scripts** for different operational modes.

## 🎯 Primary CLI Interfaces

### 1. Sovereign Runtime CLI (`project_ai_cli.py`)

**Purpose**: Cryptographically enforced governance pipeline execution and verification.

**Location**: `T:\Project-AI-main\project_ai_cli.py`

**Command Tree**:
```
project-ai
├── run <pipeline.yaml>
│   └── Execute sovereign governance pipeline
│       ├── Load pipeline YAML
│       ├── Initialize IronPathExecutor
│       ├── Execute stages with cryptographic proof
│       └── Generate compliance bundle
│
├── sovereign-verify --bundle <path> [--output <report>]
│   └── Comprehensive third-party verification
│       ├── Validate hash chain
│       ├── Verify signature authority
│       ├── Trace policy resolutions
│       └── Generate timestamped attestation
│
├── verify-audit <audit-log-path>
│   └── Verify audit trail integrity
│       ├── Load JSONL audit log
│       ├── Validate block hashes
│       ├── Check hash chain continuity
│       └── Detect tampering
│
└── verify-bundle <compliance-bundle.json>
    └── Verify compliance bundle
        ├── Load compliance JSON
        ├── Check cryptographic proofs
        ├── Validate audit trail
        └── Confirm bundle integrity
```

**Dependencies**:
- `governance.iron_path.IronPathExecutor`
- `governance.sovereign_runtime.SovereignRuntime`
- `governance.sovereign_verifier.SovereignVerifier`

**Triggers**:
- Manual execution: `python project_ai_cli.py run examples/sovereign-demo.yaml`
- Third-party audit: `project-ai sovereign-verify --bundle compliance.json`

**Output**:
- Execution artifacts in `governance/sovereign_data/artifacts/`
- Compliance bundles (JSON)
- Verification reports
- Exit codes: 0 (success), 1 (failure), 2 (warning)

---

### 2. Repository Inspection CLI (`inspection_cli.py`)

**Purpose**: Standalone repository audit and analysis system.

**Location**: `T:\Project-AI-main\inspection_cli.py`

**Command Tree**:
```
inspection_cli.py
└── [--repo <path>]
    └── Run comprehensive repository audit
        ├── Analyze project structure
        ├── Check code quality metrics
        ├── Generate audit report
        └── Export findings
```

**Dependencies**:
- `app.inspection.cli.main`
- Repository analysis modules

**Triggers**:
- Manual: `python inspection_cli.py`
- Custom repo: `python inspection_cli.py --repo /path/to/repo`

**Output**:
- Audit reports
- Code quality metrics
- Structure analysis

---

### 3. DeepSeek V3.2 CLI (`scripts/deepseek_v32_cli.py`)

**Purpose**: Command-line interface for DeepSeek V3.2 model inference.

**Location**: `T:\Project-AI-main\scripts\deepseek_v32_cli.py`

**Command Tree**:
```
deepseek_v32_cli.py
├── <prompt> [options]
│   ├── --mode {completion|chat}
│   ├── --max-tokens <int>
│   ├── --temperature <float>
│   ├── --top-p <float>
│   ├── --top-k <int>
│   ├── --no-sample
│   ├── --no-filter
│   ├── --json
│   └── --verbose
│
├── --interactive (chat mode only)
│   └── Start interactive chat session
│       ├── User: <input>
│       ├── Assistant: <response>
│       ├── Commands: exit, quit, clear, info
│       └── Multi-turn conversation
│
└── --model <huggingface-model>
    └── Custom model selection
```

**Dependencies**:
- `app.core.deepseek_v32_inference.DeepSeekV32`
- `app.core.runtime.router.route_request` (governance)

**Governance**:
- Classification: `ADMIN-BYPASS` (Development/testing CLI)
- Risk: Medium (model inference)
- Content filtering (optional via `--no-filter`)

**Triggers**:
- Simple completion: `python -m scripts.deepseek_v32_cli "Your prompt"`
- Chat mode: `python -m scripts.deepseek_v32_cli --mode chat "Hello"`
- Interactive: `python -m scripts.deepseek_v32_cli --mode chat --interactive`

**Output**:
- Generated text (stdout)
- JSON output (with `--json`)
- Interactive chat sessions
- Exit codes: 0 (success), 1 (error), 130 (keyboard interrupt)

---

## 🚀 Launcher Scripts

### Desktop Application Launchers

#### 1. PowerShell Launcher (`scripts/launch-desktop.ps1`)
```powershell
# Location: T:\Project-AI-main\scripts\launch-desktop.ps1
# Purpose: Launch desktop app with Windows environment setup
# Usage: .\scripts\launch-desktop.ps1

Execution Flow:
1. Set environment variables
2. Activate virtual environment (optional)
3. Execute: python -m src.app.main
4. Monitor process
```

**Dependencies**:
- Python 3.11+
- PyQt6
- Virtual environment (optional)

**Triggers**:
- Direct: `.\scripts\launch-desktop.ps1`
- From root: `.\launch-desktop.ps1` (if copied)

---

#### 2. Batch Launcher (`scripts/launch-desktop.bat`)
```batch
REM Location: T:\Project-AI-main\scripts\launch-desktop.bat
REM Purpose: Simple batch launcher for Windows
REM Usage: launch-desktop.bat

@echo off
python -m src.app.main
pause
```

**Triggers**:
- Double-click execution
- Command line: `scripts\launch-desktop.bat`

---

#### 3. Setup Script (`scripts/setup-desktop.bat`)
```batch
REM Location: T:\Project-AI-main\scripts\setup-desktop.bat
REM Purpose: Desktop environment initialization
REM Usage: setup-desktop.bat

Execution Flow:
1. Check Python installation
2. Create virtual environment
3. Install dependencies (requirements.txt)
4. Verify PyQt6 installation
5. Create shortcuts
```

**Dependencies**:
- Python 3.11+
- pip
- requirements.txt

---

## 📦 NPM Script Interface

**Location**: `T:\Project-AI-main\package.json`

**Command Tree**:
```json
npm
├── test
│   ├── npm run test:js → node --test src/**/*.test.js
│   └── npm run test:python → pytest -q
│
├── test:js → Node.js test runner
├── test:python → pytest suite
│
├── lint → ruff check .
├── format → ruff check . --fix
│
├── dev → docker-compose up
├── build → docker build -t project-ai:latest .
│
├── lint:markdown → markdownlint (README, docs)
│
└── tarl (TARL build system)
    ├── tarl:build → python -m tarl.build.cli build
    ├── tarl:clean → python -m tarl.build.cli clean
    ├── tarl:list → python -m tarl.build.cli list
    └── tarl:cache → python -m tarl.build.cli cache stats
```

**Triggers**:
- Development: `npm run dev`
- Testing: `npm test`
- Linting: `npm run lint`
- Building: `npm run build`

**Dependencies**:
- Node.js ≥18.0.0
- markdownlint-cli (devDependency)
- Python 3.11+ (for test:python)
- Docker (for dev/build)

---

## 🔨 Make Interface

**Location**: `T:\Project-AI-main\Makefile`

**Command Tree**:
```makefile
make
├── run → python -m src.app.main
│   └── Launch desktop application
│
├── test → pytest -v
│   └── Run full test suite with verbose output
│
├── lint → ruff check .
│   └── Run linting checks
│
├── format
│   ├── isort src tests --profile black
│   ├── ruff check . --fix
│   └── black src tests
│
└── precommit → pre-commit run --all-files
    └── Run all pre-commit hooks
```

**Triggers**:
- `make run` - Launch application
- `make test` - Run tests
- `make lint` - Check code quality
- `make format` - Auto-format code
- `make precommit` - Run pre-commit checks

**Dependencies**:
- Python 3.11+
- pytest, ruff, black, isort
- pre-commit

---

## 🔄 Command Routing Flow

### Entry Point → Handler Chain

```
User Input (CLI/NPM/Make)
    ↓
Entry Point Validation
    ├─ Parse arguments (argparse/typer)
    ├─ Load configuration
    └─ Initialize logging
    ↓
Command Router
    ├─ project_ai_cli.py → governance commands
    ├─ inspection_cli.py → audit commands
    └─ deepseek_v32_cli.py → inference commands
    ↓
Command Handler
    ├─ cmd_run() → IronPathExecutor
    ├─ cmd_verify_audit() → SovereignRuntime
    ├─ cmd_verify_bundle() → Bundle verification
    └─ cmd_sovereign_verify() → SovereignVerifier
    ↓
Core Business Logic
    ├─ Governance modules
    ├─ Inspection engines
    └─ AI inference systems
    ↓
Output Generation
    ├─ Artifacts (JSON, JSONL)
    ├─ Reports (formatted text)
    ├─ Logs (structured logging)
    └─ Exit codes (0/1/2)
```

---

## 🔗 Integration Points

### CLI → Scripts
- `project_ai_cli.py run` → Executes governance pipelines
- `inspection_cli.py` → Calls repository analysis scripts
- `deepseek_v32_cli.py` → Invokes model inference

### CLI → Core Modules
- All CLIs import from `src/app/` structure
- Governance: `governance.iron_path`, `governance.sovereign_runtime`
- Inspection: `app.inspection.cli`
- Inference: `app.core.deepseek_v32_inference`

### CLI → Configuration
- Environment variables (`.env`)
- YAML pipelines (`examples/sovereign-demo.yaml`)
- JSON config files

### CLI → Output Artifacts
- `governance/sovereign_data/artifacts/` - Execution artifacts
- `automation-logs/` - Log files
- `data/` - Application data
- stdout/stderr - Direct output

---

## 🛡️ Security & Governance

### Input Validation
- All CLI arguments validated via argparse schemas
- Path traversal protection
- File existence checks
- Type validation

### Governance Integration
- `deepseek_v32_cli.py` includes governance routing
- Content filtering (enabled by default)
- `ADMIN-BYPASS` classification for development tools

### Error Handling
- Comprehensive try-except blocks
- Structured logging (logging module)
- Exit codes: 0 (success), 1 (error), 2 (warning), 130 (interrupted)

---

## 📊 Usage Patterns

### Development Workflow
```bash
# Setup
make run  # Launch application

# Testing
npm test  # Run all tests
make test  # Verbose pytest

# Code quality
make format  # Auto-format
make lint    # Check quality
```

### Governance Workflow
```bash
# Execute pipeline
python project_ai_cli.py run examples/sovereign-demo.yaml

# Verify compliance
python project_ai_cli.py sovereign-verify --bundle compliance.json --output report.json

# Audit verification
python project_ai_cli.py verify-audit governance/sovereign_data/immutable_audit.jsonl
```

### Inference Workflow
```bash
# Simple completion
python -m scripts.deepseek_v32_cli "Explain AI safety"

# Interactive chat
python -m scripts.deepseek_v32_cli --mode chat --interactive

# Custom parameters
python -m scripts.deepseek_v32_cli --temperature 0.9 --max-tokens 256 "Tell a story"
```

---

## 📈 Metrics & Monitoring

### Command Execution Tracking
- All CLIs use structured logging
- Execution times logged
- Error rates tracked
- Exit codes monitored

### Integration Health
- CLI → Handler success rate: 100%
- Argument parsing errors: Logged and handled
- Core module failures: Propagated with context

---

## 🔍 Related Documentation

- **Command Handlers**: See `02_command-handlers.md`
- **Scripts**: See `03_scripts.md`
- **Automation Workflows**: See `04_automation-workflows.md`
- **Build Tools**: See `05_build-tools.md`

---

**Version**: 1.0.0  
**Last Updated**: 2025-02-08  
**Maintainer**: AGENT-063  
