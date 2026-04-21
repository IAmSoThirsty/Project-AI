---
title: CLI & Automation Relationship Index
description: Master index for all CLI and automation system relationships
tags:
  - relationships
  - cli
  - automation
  - index
created: 2025-02-08
agent: AGENT-063
status: complete
---

# CLI & Automation Relationship Index

**Mission**: Document relationships for 12 CLI/automation systems covering command flows, automation chains, and script dependencies.

**Agent**: AGENT-063: CLI & Automation Relationship Mapping Specialist

## 📋 System Coverage

This relationship mapping covers **12 critical CLI/automation systems**:

1. **CLI Interface** - Main command-line entry points
2. **Command Handlers** - Command routing and execution
3. **Scripts** - Automation scripts (PowerShell, Shell, Python)
4. **Automation Workflows** - GitHub Actions orchestration
5. **Build Tools** - Multi-platform build systems
6. **Linting** - Code quality enforcement (Ruff, ESLint, Markdownlint)
7. **Type Checking** - Static type validation
8. **Code Quality** - Quality gates and metrics
9. **Pre-commit Hooks** - Git pre-commit automation
10. **Post-deploy Hooks** - Deployment validation
11. **Validation Scripts** - Data/structure validation
12. **Migration Tools** - Schema and data migrations

## 📁 Relationship Map Files

| File | System | Description |
|------|--------|-------------|
| `01_cli-interface.md` | CLI Interface | Main CLI entry points and command trees |
| `02_command-handlers.md` | Command Handlers | Command routing and execution patterns |
| `03_scripts.md` | Scripts | Script dependencies and automation chains |
| `04_automation-workflows.md` | Automation Workflows | GitHub Actions workflow relationships |
| `05_build-tools.md` | Build Tools | Build system dependencies and flows |
| `06_linting.md` | Linting | Linting tool chains and configurations |
| `07_type-checking.md` | Type Checking | Type validation workflows |
| `08_code-quality.md` | Code Quality | Quality gates and enforcement |
| `09_pre-commit-hooks.md` | Pre-commit Hooks | Git hook chains |
| `10_post-deploy-hooks.md` | Post-deploy Hooks | Deployment validation chains |
| `11_validation-scripts.md` | Validation Scripts | Validation dependencies |
| `12_migration-tools.md` | Migration Tools | Migration orchestration |
| `13_command-flow-diagram.md` | All Systems | Visual command flow diagrams |
| `14_automation-chains.md` | All Systems | Cross-system automation chains |

## 🔗 Key Relationships

### Command Flow Hierarchy
```
User Input
  ├─> CLI Interface (project_ai_cli.py, inspection_cli.py)
  │   └─> Command Handlers (argparse routing)
  │       ├─> Core Modules (governance, inspection, etc.)
  │       └─> Scripts (automation, deployment)
  │
  ├─> NPM Scripts (package.json)
  │   ├─> Test Runners (pytest, node:test)
  │   ├─> Linting (ruff, markdownlint)
  │   └─> Build Tools (docker, tarl)
  │
  └─> Make Targets (Makefile)
      ├─> Python CLI (python -m src.app.main)
      ├─> Testing (pytest -v)
      └─> Pre-commit (pre-commit run)
```

### Automation Chain Flow
```
Git Event → Pre-commit Hooks → GitHub Actions → Build → Deploy → Post-deploy Validation
    ↓              ↓                  ↓            ↓       ↓              ↓
 Linting    Type Checking      Security Scans   SBOM   Monitoring   Health Checks
    ↓              ↓                  ↓            ↓       ↓              ↓
 Auto-fix   Validation        Auto-remediation  Sign   Alerts      Rollback
```

## 🎯 Critical Integration Points

### 1. CLI → Script Integration
- **project_ai_cli.py** → governance pipelines
- **inspection_cli.py** → repository audit
- **deepseek_v32_cli.py** → model inference

### 2. NPM → Build Integration
- `npm run test` → pytest + node:test
- `npm run build` → docker-compose
- `npm run lint` → ruff + markdownlint

### 3. GitHub Actions → Script Integration
- `codex-deus-ultimate.yml` → comprehensive workflow
- Security scans → auto-remediation scripts
- Build jobs → deployment scripts

### 4. Pre-commit → Validation Chain
- `.pre-commit-config.yaml` → black, ruff, isort
- Hooks → detect-secrets, check-yaml
- Validation → pre-commit-root-structure.sh

## 📊 Dependency Matrix

| System | Depends On | Triggers |
|--------|------------|----------|
| CLI Interface | argparse, typer | Command handlers, scripts |
| Command Handlers | Core modules | Business logic, APIs |
| Scripts | Python, PowerShell, Bash | Automation tasks, builds |
| GitHub Actions | Scripts, tools | Security scans, builds, deploys |
| Build Tools | Gradle, Docker, npm | Platform artifacts |
| Linting | Ruff, ESLint | Auto-fixes, quality gates |
| Pre-commit | Git hooks | Linting, validation |
| Validation | Schema validators | Error reporting |

## 🔄 Circular Dependencies (NONE DETECTED)

All systems maintain **acyclic dependency graphs**:
- CLI → Handlers → Core (one-way)
- GitHub Actions → Scripts (one-way)
- Pre-commit → Linting (one-way)
- Build → Deploy (one-way)

## 🚀 Execution Entry Points

### Primary Entry Points
1. **Desktop Application**: `python -m src.app.main`
2. **Sovereign Runtime**: `python project_ai_cli.py run <pipeline>`
3. **Repository Inspection**: `python inspection_cli.py`
4. **NPM Scripts**: `npm run <command>`
5. **Make Targets**: `make <target>`
6. **GitHub Actions**: Automatic on push/PR

### Development Entry Points
- `scripts/launch-desktop.ps1` - Windows desktop launcher
- `scripts/launch-desktop.bat` - Windows batch launcher
- `scripts/setup-desktop.bat` - Desktop environment setup
- `docker-compose up` - Containerized deployment

## 📈 Automation Coverage

### Automated Tasks
- ✅ Code linting (pre-commit, GitHub Actions)
- ✅ Type checking (mypy, pyrightconfig)
- ✅ Security scanning (bandit, CodeQL, trivy)
- ✅ Testing (pytest, node:test)
- ✅ Build automation (multi-platform)
- ✅ SBOM generation
- ✅ Deployment validation
- ✅ Metadata enrichment

### Manual Tasks (Require Approval)
- Release publishing
- Production deployment
- Major version upgrades
- Manual security patches

## 🔍 Quick Navigation

- **For CLI command structure**: See `01_cli-interface.md`
- **For script dependencies**: See `03_scripts.md`
- **For GitHub Actions workflows**: See `04_automation-workflows.md`
- **For build processes**: See `05_build-tools.md`
- **For quality gates**: See `08_code-quality.md`
- **For visual diagrams**: See `13_command-flow-diagram.md`

---

**Version**: 1.0.0  
**Last Updated**: 2025-02-08  
**Maintainer**: AGENT-063  
