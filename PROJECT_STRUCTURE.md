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

### `src/` — Source Code

```
src/
├── app/
│   ├── main.thirsty    # Floor 1 Entry Point
│   ├── bootstrap.thirsty # Floor 1 Orchestrator
│   ├── arch_ledger.thirsty # TSCG Architectural Ledger
│   ├── core/           # Core AI runtime (ai_systems, shadow_execution_plane,
│   │                   # shadow_resource_limiter, council_hub, …)
│   ├── agents/         # Agent subsystems (red_team, safety_guard,
│   │                   # jailbreak_bench, long_context, …)
│   └── plugins/        # Plugin manager & built-in plugins
├── cerberus/
│   └── sase/
│       └── governance/ # RBAC, key management, audit pipeline
├── engines/            # (mirrors top-level engines/ for package imports)
├── kernel/             # Thirsty's Kernel core modules
├── tarl/               # TARL policy runtime, compiler, spec
├── tarl_os/            # TARL OS bootstrap & scheduler
└── shadow_thirst/      # Shadow Thirst language files (.thirsty sources)
                        # e.g. resource_limiter.thirsty
```

### `tests/` — Automated Tests

```
tests/
├── test_shadow_execution.py    # Shadow dual-plane + resource limits (34 tests)
├── test_tarl_productivity.py   # TARL cache & parallel evaluation tests
├── test_head_of_security.py    # Security agent tests
├── test_code_civilization.py   # Code civilization tests
├── verify_security_agents.py   # Manual verification script (no pytest runner)
└── manual/                     # Manual / interactive test scripts
```

### `engines/` — Standalone Engine Modules

Provides independently-runnable engine implementations that `src/` may import.

```
engines/
├── cognition/
├── memory/
└── security/
```

### `adversarial_tests/` — Red Team & Adversarial Evaluation

```
adversarial_tests/
├── galahad_model.py        # GalahadModel wrapper for red-team evaluation
├── run_adversarial.py      # Test runner & reporting
└── scenarios/              # Attack scenario definitions
```

### `docs/` — Documentation

```
docs/
├── architecture/           # System architecture deep-dives
├── developer/              # Developer guides, coverage reports, API docs
├── executive/              # Whitepapers, business documentation
├── governance/             # CodexDeus, licensing, policy documents
├── legal/                  # License files & third-party notices
├── operations/             # Operational runbooks and procedures
├── security_compliance/    # Cerberus, threat model, ASL framework
├── internal/
│   └── archive/            # Historical implementation summaries
│       └── ARCHIVE_INDEX.md
└── archive/                # Deprecated root-level docs moved here
```

### `.github/` — CI/CD & Automation

```
.github/
├── workflows/              # 20+ GitHub Actions workflows
│   ├── ci.yml              # Comprehensive CI (Python 3.11, 3.12)
│   ├── security.yml        # CodeQL + Bandit + pip-audit
│   ├── dependabot.yml      # Automated dependency updates
│   └── …
└── CODEOWNERS
```

### `config/` — Configuration Files

Runtime configuration: JSON, YAML, stored prompts, jurisdiction loaders.

### `data/` — Data Storage

```
data/
├── datasets/   # ML training and evaluation datasets
└── logs/       # Runtime log files (gitignored)
```

### `k8s/` — Kubernetes Manifests

14 production-grade YAML files + Helm chart with Kustomize dev/staging/production overlays.

### `scripts/` — Operational Scripts

...

### `emergent-microservices/` — Production-Ready Extensions

Emergent-generated microservice extensions following the three-tier sovereignty model.

```
emergent-microservices/
├── _common/                         # Shared FastAPI middleware, auth, & metrics
├── ai-mutation-governance-firewall/  # Admission control & mutation gating
├── autonomous-compliance/            # Compliance-as-Code engine
├── autonomous-incident-reflex-system/ # Evidence preservation & policy reflex
├── autonomous-negotiation-agent/      # Agent-to-agent bargaining logic
├── trust-graph-engine/                # Distributed reputation & trust graph
├── sovereign-data-vault/              # Encrypted self-sovereign storage
└── verifiable-reality/                # Cryptographic proof & existence layer
```

### `desktop/` — Desktop UI (Electron/PyQt6)

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
