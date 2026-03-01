<p align="right">
  [2026-03-01 10:00] <br>
  Productivity: Active
</p>
# Project Structure

**Last Updated**: 2026-02-20

This document describes the canonical directory layout of Project-AI.

---

## Root-Level Files

| File | Purpose |
|------|---------|
| `README.md` | Primary project documentation |
| `CHANGELOG.md` | Version history (Keep a Changelog format) |
| `CONTRIBUTING.md` | Contribution guidelines |
| `CODE_OF_CONDUCT.md` | Community standards |
| `SECURITY.md` | Security framework & responsible disclosure |
| `INSTALL.md` | Comprehensive installation guide |
| `DEVELOPER_QUICK_REFERENCE.md` | Quick API / component reference |
| `PRODUCTION_DEPLOYMENT.md` | Production deployment procedures |
| `PROJECT_STATUS.md` | Current system health & feature status |
| `PROJECT_STRUCTURE.md` | This file |
| `pyproject.toml` | Python package metadata & build config |
| `setup.py` | Legacy setuptools entry (defers to pyproject.toml) |
| `requirements.txt` | Runtime dependencies |
| `requirements-dev.txt` | Development & testing dependencies |
| `Dockerfile` | Multi-stage production Docker image |
| `docker-compose.yml` | Full-stack service orchestration |
| `run.py` | Top-level application entry point |

---

## Directory Layout

### `src/` â€” Source Code

```
src/
â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ main.thirsty    # Floor 1 Entry Point
â”‚   â”œâ”€â”€ bootstrap.thirsty # Floor 1 Orchestrator
â”‚   â”œâ”€â”€ arch_ledger.thirsty # TSCG Architectural Ledger
â”‚   â”œâ”€â”€ core/           # Core AI runtime (ai_systems, shadow_execution_plane,
â”‚   â”‚                   # shadow_resource_limiter, council_hub, â€¦)
â”‚   â”œâ”€â”€ agents/         # Agent subsystems (red_team, safety_guard,
â”‚   â”‚                   # jailbreak_bench, long_context, â€¦)
â”‚   â””â”€â”€ plugins/        # Plugin manager & built-in plugins
â”œâ”€â”€ cerberus/
â”‚   â””â”€â”€ sase/
â”‚       â””â”€â”€ governance/ # RBAC, key management, audit pipeline
â”œâ”€â”€ engines/            # (mirrors top-level engines/ for package imports)
â”œâ”€â”€ kernel/             # Thirsty's Kernel core modules
â”œâ”€â”€ tarl/               # TARL policy runtime, compiler, spec
â”œâ”€â”€ tarl_os/            # TARL OS bootstrap & scheduler
â””â”€â”€ shadow_thirst/      # Shadow Thirst language files (.thirsty sources)
                        # e.g. resource_limiter.thirsty
```

### `tests/` â€” Automated Tests

```
tests/
â”œâ”€â”€ test_shadow_execution.py    # Shadow dual-plane + resource limits (34 tests)
â”œâ”€â”€ test_tarl_productivity.py   # TARL cache & parallel evaluation tests
â”œâ”€â”€ test_head_of_security.py    # Security agent tests
â”œâ”€â”€ test_code_civilization.py   # Code civilization tests
â”œâ”€â”€ verify_security_agents.py   # Manual verification script (no pytest runner)
â””â”€â”€ manual/                     # Manual / interactive test scripts
```

### `engines/` â€” Standalone Engine Modules

Provides independently-runnable engine implementations that `src/` may import.

```
engines/
â”œâ”€â”€ cognition/
â”œâ”€â”€ memory/
â””â”€â”€ security/
```

### `adversarial_tests/` â€” Red Team & Adversarial Evaluation

```
adversarial_tests/
â”œâ”€â”€ galahad_model.py        # GalahadModel wrapper for red-team evaluation
â”œâ”€â”€ run_adversarial.py      # Test runner & reporting
â””â”€â”€ scenarios/              # Attack scenario definitions
```

### `docs/` â€” Documentation

```
docs/
â”œâ”€â”€ architecture/           # System architecture deep-dives
â”œâ”€â”€ developer/              # Developer guides, coverage reports, API docs
â”œâ”€â”€ executive/              # Whitepapers, business documentation
â”œâ”€â”€ governance/             # CodexDeus, licensing, policy documents
â”œâ”€â”€ legal/                  # License files & third-party notices
â”œâ”€â”€ operations/             # Operational runbooks and procedures
â”œâ”€â”€ security_compliance/    # Cerberus, threat model, ASL framework
â”œâ”€â”€ internal/
â”‚   â””â”€â”€ archive/            # Historical implementation summaries
â”‚       â””â”€â”€ ARCHIVE_INDEX.md
â””â”€â”€ archive/                # Deprecated root-level docs moved here
```

### `.github/` â€” CI/CD & Automation

```
.github/
â”œâ”€â”€ workflows/              # 20+ GitHub Actions workflows
â”‚   â”œâ”€â”€ ci.yml              # Comprehensive CI (Python 3.11, 3.12)
â”‚   â”œâ”€â”€ security.yml        # CodeQL + Bandit + pip-audit
â”‚   â”œâ”€â”€ dependabot.yml      # Automated dependency updates
â”‚   â””â”€â”€ â€¦
â””â”€â”€ CODEOWNERS
```

### `config/` â€” Configuration Files

Runtime configuration: JSON, YAML, stored prompts, jurisdiction loaders.

### `data/` â€” Data Storage

```
data/
â”œâ”€â”€ datasets/   # ML training and evaluation datasets
â””â”€â”€ logs/       # Runtime log files (gitignored)
```

### `k8s/` â€” Kubernetes Manifests

14 production-grade YAML files + Helm chart with Kustomize dev/staging/production overlays.

### `scripts/` â€” Operational Scripts

...

### `emergent-microservices/` â€” Production-Ready Extensions

Emergent-generated microservice extensions following the three-tier sovereignty model.

```
emergent-microservices/
â”œâ”€â”€ _common/                         # Shared FastAPI middleware, auth, & metrics
â”œâ”€â”€ ai-mutation-governance-firewall/  # Admission control & mutation gating
â”œâ”€â”€ autonomous-compliance/            # Compliance-as-Code engine
â”œâ”€â”€ autonomous-incident-reflex-system/ # Evidence preservation & policy reflex
â”œâ”€â”€ autonomous-negotiation-agent/      # Agent-to-agent bargaining logic
â”œâ”€â”€ trust-graph-engine/                # Distributed reputation & trust graph
â”œâ”€â”€ sovereign-data-vault/              # Encrypted self-sovereign storage
â””â”€â”€ verifiable-reality/                # Cryptographic proof & existence layer
```

### `desktop/` â€” Desktop UI (Electron/PyQt6)

React + Vite frontend served by the Electron shell. Tron-themed "Leather Book" interface.

---

## Key Entry Points

| Script | Purpose |
|--------|---------|
| `run.py` | Start the application |
| `scripts/start_api.py` | Start FastAPI backend |
| `scripts/tools/project_ai_cli.py` | Main CLI tool |
| `scripts/quickstart.py` | Quick setup check |

---

## Archive Policy

Root-level markdown files that are no longer current are moved to `docs/archive/`.
Historical implementation summaries are in `docs/internal/archive/` (indexed by `ARCHIVE_INDEX.md`).

