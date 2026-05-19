<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / SYSTEM_MANIFEST.md # -->
<!-- # ============================================================================ # -->
# ============================================================================ #

               #
# COMPLIANCE: Sovereign-Native / Thirsty-Lang v4.0                             #
# ============================================================================ #


<!-- # Date: 2026-03-14 | Time: 00:00 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<div align="center">

# 🛡️ PROJECT-AI — SYSTEM MANIFEST & INVENTORY

![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)
![Branch](https://img.shields.io/badge/Branch-dry--run--main--merge--edition--v1--cts5--prod-blue?style=for-the-badge)
![Files](https://img.shields.io/badge/Tracked_Files-4963-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Comprehensive repository inventory — every directory, every component, every file class.**

| Field | Value |
|-------|-------|
| **Origin** | `https://github.com/IAmSoThirsty/Project-AI.git` |
| **Branch** | `dry-run-main-merge-edition-v1-cts5-prod` |
| **HEAD** | `b2757196 — audit: apply full repository audit corrections` |
| **Generated** | 2026-03-14 00:00 MST |

</div>

---

## 📑 Table of Contents

- [Root Files Inventory](#-root-files-inventory)
- [Directory Manifest](#-directory-manifest)
- [Submodules](#-submodules)
- [Configuration & Build Systems](#-configuration--build-systems)
- [CI/CD & GitHub](#-cicd--github)
- [Source Code](#-source-code)
- [Documentation](#-documentation)
- [Security & Governance](#-security--governance)
- [Infrastructure & Deployment](#-infrastructure--deployment)
- [Testing & Quality](#-testing--quality)
- [External & Integrations](#-external--integrations)
- [Assets & Media](#-assets--media)

---

## 📄 Root Files Inventory

### Core Project Files

| File | Purpose | Status |
|------|---------|--------|
| `README.md` (76 KB) | Primary project documentation | ✅ Active |
| `The_Guide_Book.md` (47 KB) | Comprehensive project guide | ✅ Active |
| `CONTRIBUTING.md` (24 KB) | Contribution guidelines | ✅ Active |
| `SECURITY.md` (12 KB) | Security policy & reporting | ✅ Active |
| `INSTALL.md` (10 KB) | Installation instructions | ✅ Active |
| `PRODUCTION_DEPLOYMENT.md` (7 KB) | Deployment runbook | ✅ Active |
| `TECHNICAL_SPECIFICATION.md` (6 KB) | Technical spec | ✅ Active |
| `CODE_OF_CONDUCT.md` (5 KB) | Community code of conduct | ✅ Active |
| `TAMS_SUPREME_SPECIFICATION.md` (3 KB) | TAMS system spec | ✅ Active |
| `SESSION_NOTES.md` (2 KB) | Session notes | ✅ Active |
| `CHANGELOG.md` (2 KB) | Release changelog | ✅ Active |
| `DEVELOPER_QUICK_REFERENCE.md` (1 KB) | Dev quick-ref card | ✅ Active |
| `DIRECTORY_INDEX.md` (9 KB) | Directory layout guide | ✅ Active |
| `LICENSE` (1 KB) | MIT License | ✅ Active |

### Build & Packaging

| File | Purpose | Status |
|------|---------|--------|
| `pyproject.toml` (4 KB) | Python project config (PEP 621) | ✅ Active |
| `setup.cfg` (1 KB) | Legacy Python packaging | ✅ Active |
| `requirements.txt` (2 KB) | Python runtime deps | ✅ Active |
| `requirements-dev.txt` | Python dev deps | ✅ Active |
| `requirements.in` | Pip-compile input | ✅ Active |
| `requirements.lock` (122 KB) | Locked dependency tree | ✅ Active |
| `MANIFEST.in` (3 KB) | Python sdist manifest | ✅ Active |
| `package.json` (2 KB) | Node.js project config | ✅ Active |
| `package-lock.json` (43 KB) | Node lockfile | ✅ Active |
| `build.gradle.kts` (70 KB) | Gradle Kotlin DSL build | ✅ Active |
| `settings.gradle.kts` (5 KB) | Gradle settings | ✅ Active |
| `gradle.properties` (6 KB) | Gradle properties | ✅ Active |
| `gradlew` / `gradlew.bat` | Gradle wrappers | ✅ Active |
| `Makefile` (1 KB) | Make targets | ✅ Active |
| `build-installer.ps1` (3 KB) | Windows installer builder | ✅ Active |
| `build_orchestrator.py` (4 KB) | Build orchestration script | ✅ Active |
| `build_report.json` (14 KB) | Last build report | ✅ Active |
| `RELEASE_MANIFEST.json` | Release metadata | ✅ Active |

### Docker

| File | Purpose | Status |
|------|---------|--------|
| `Dockerfile` (1 KB) | Standard container | ✅ Active |
| `Dockerfile.sovereign` (1 KB) | Sovereign edition container | ✅ Active |
| `docker-compose.yml` (6 KB) | Primary compose stack | ✅ Active |
| `docker-compose.override.yml` (1 KB) | Local dev overrides | ✅ Active |
| `docker-compose.monitoring.yml` (1 KB) | Monitoring stack | ✅ Active |
| `.dockerignore` | Docker build exclusions | ✅ Active |

### Entrypoints & Scripts

| File | Purpose | Status |
|------|---------|--------|
| `boot_sovereign.py` (6 KB) | Sovereign ignition sequence | ✅ Active |
| `start.ps1` (6 KB) | Windows startup script | ✅ Active |
| `Project-AI.ps1` (1 KB) | PowerShell launcher | ✅ Active |
| `FIX_WORKSTATION.ps1` | Heart Restore workstation verifier | ✅ Active |
| `Master-Sovereign-Launch-Sequence.ps1` (3 KB) | Master launch script | ✅ Active |
| `fix_mem.py` (2 KB) | Memory fix utility | ✅ Active |
| `test_gui.py` (1 KB) | GUI test entrypoint | ✅ Active |
| `WORKSPACE_STATUS_REPORT.md` | Universal command center | ✅ NEW |

### Config / Tooling

| File | Purpose | Status |
|------|---------|--------|
| `.pre-commit-config.yaml` | Pre-commit hooks (black, ruff, isort, detect-secrets) | ✅ Active |
| `.eslintrc.json` (1 KB) | ESLint config (JS/TS) | ✅ Active |
| `.prettierrc` | Prettier formatting | ✅ Active |
| `.bandit` (1 KB) | Bandit security scanner config | ✅ Active |
| `.markdownlint.yaml` | Markdown lint rules | ✅ Active |
| `.gitattributes` (4 KB) | Git attribute mappings | ✅ Active |
| `.gitignore` (4 KB) | Tracked ignore rules | ✅ Active |
| `.gitmodules` (1 KB) | Submodule declarations | ✅ Active |
| `.python-version` | Python version pin (3.12) | ✅ Active |
| `taar.toml` (8 KB) | TAAR agent config | ✅ Active |
| `Project-AI.code-workspace` (6 KB) | VS Code workspace | ✅ Active |
| `IDE_Work_Spaces/project-ai-control-plane.code-workspace` | Compact Heart Restore control-plane workspace | ✅ Active |
| `Project-AI.spec` / `ProjectAI.spec` | PyInstaller spec files | ✅ Active |

---

## 📂 Directory Manifest

> Top-level directories sorted by tracked file count (approximate from `ls-files`).

### Core Source & Engine

| Directory | Files | Description | Status |
|-----------|-------|-------------|--------|
| `src/` | ~718 | **Primary source tree** — app core, AI systems, identity, governance (optimizer v2.5), persona, memory, learning, plugins, GUI, web API | ✅ Active |
| `engines/` | ~218 | AI/ML engine implementations — inference, training, model management | ✅ Active |
| `cognition/` | ~18 | Cognitive processing modules — reasoning, decision, awareness | ✅ Active |
| `kernel/` | ~26 | Low-level kernel/runtime primitives | ✅ Active |
| `project_ai/` | ~47 | Python package root (`project_ai` importable module) | ✅ Active |
| `orchestrator/` | ~16 | Task/workflow orchestration layer | ✅ Active |

### Documentation

| Directory | Files | Description | Status |
|-----------|-------|-------------|--------|
| `docs/` | ~552 | **All documentation** — architecture, security, governance, API, changelogs, guides, AGI charter | ✅ Active |
| `man/` | ~1 | Man-page style references | ✅ Active |

### Testing & Quality

| Directory | Files | Description | Status |
|-----------|-------|-------------|--------|
| `adversarial_tests/` | ~310 | Adversarial/red-team test suites | ✅ Active |
| `tests/` | ~240 | Unit, integration, and system tests | ✅ Active |
| `e2e/` | ~30 | End-to-end test suites | ✅ Active |
| `benchmarks/` | ~5 | Performance benchmarks | ✅ Active |
| `test-artifacts/` | ~2 | Test fixture artifacts | ✅ Active |
| `test-data/` | ~2 | Test data fixtures | ✅ Active |
| `validation_evidence/` | ~1 | Validation proof artifacts | ✅ Active |

### Security & Governance

| Directory | Files | Description | Status |
|-----------|-------|-------------|--------|
| `security/` | ~607 | Security tooling, policies, pen-testing tools (incl. submodule) | ✅ Active |
| `governance/` | ~56 | Governance framework, audit logs, compliance | ✅ Active |
| `policies/` | ~5 | Organizational policies | ✅ Active |
| `h323_sec_profile/` (Archived) | — | Moved to `archive/history/timeline/` | 📦 Archived |

### Infrastructure & Deployment

| Directory | Files | Description | Status |
|-----------|-------|-------------|--------|
| `emergent-microservices/` (Archived) | — | Moved to `archive/history/timeline/` | 📦 Archived |
| `.github/` | ~94 | GitHub workflows, issue templates, PR templates, CODEOWNERS | ✅ Active |
| `k8s/` | ~77 | Kubernetes manifests & Helm values | ✅ Active |
| `deploy/` | ~43 | Deployment scripts & configs | ✅ Active |
| `helm/` | ~19 | Helm chart definitions | ✅ Active |
| `terraform/` | ~2 | Infrastructure-as-code (Terraform) | ✅ Active |
| `monitoring/` | ~6 | Monitoring & observability configs | ✅ Active |
| `ci-reports/` | ~5 | CI build/test reports | ✅ Active |
| `temporal/` | ~9 | Temporal.io workflow definitions | ✅ Active |
| `octoreflex/` | ~67 | OctoReflex eBPF agent (Go) | ✅ Active |

### Platform Targets

| Directory | Files | Description | Status |
|-----------|-------|-------------|--------|
| `android/` (Archived) | — | Moved to `archive/history/timeline/` | 📦 Archived |
| `desktop/` | ~31 | Desktop app (Electron/Tauri) | ✅ Active |
| `web/` | ~41 | Web frontend | ✅ Active |
| `unity/` (Archived) | — | Moved to `archive/history/timeline/` | 📦 Archived |
| `usb_installer/` (Archived) | — | Moved to `archive/history/timeline/` | 📦 Archived |

### Language & DSL

| Directory | Files | Description | Status |
|-----------|-------|-------------|--------|
| `tarl/` | ~33 | **T.A.R.L.** compiler/runtime | ✅ Active |
| `tarl_os/` | ~38 | TARL OS layer (`.thirsty` placeholder files) | ✅ Active |
| `linguist-submission/` | ~18 | GitHub Linguist language submission | ✅ Active |
| `taar/` | ~11 | TAAR (Thirsty's Active Agent Runner) | ✅ Active |

### Integrations & APIs

| Directory | Files | Description | Status |
|-----------|-------|-------------|--------|
| `integrations/` | ~45 | Third-party integration modules | ✅ Active |
| `api/` | ~15 | API definitions & OpenAPI specs | ✅ Active |
| `plugins/` | ~1 | Plugin framework | ✅ Active |

### External / Vendored

| Directory | Files | Description | Status |
|-----------|-------|-------------|--------|
| `external/` | ~465 | **Git submodules** — Cerberus, Thirsty-Lang, etc. | ✅ Active |

### Build & Tooling

| Directory | Files | Description | Status |
|-----------|-------|-------------|--------|
| `scripts/` | ~113 | Utility scripts (PS1, Bash, Python) | ✅ Active |
| `tools/` | ~22 | Developer tooling | ✅ Active |
| `utils/` | ~13 | Shared utility modules | ✅ Active |
| `IDE_Work_Spaces/` | ~2 | Focused IDE workspace wiring for Heart Restore validation | ✅ Active |
| `gradle/` | ~4 | Gradle wrapper JAR & properties | ✅ Active |
| `gradle-evolution/` | ~42 | Gradle build evolution/history | ✅ Active |
| `config/` | ~39 | Application & environment configs | ✅ Active |

### Other

| Directory | Files | Description | Status |
|-----------|-------|-------------|--------|
| `archive/` | ~330 | **System Archive** — Legacy assets, aspirational logic | ✅ Active |
| `EditionV1` (Archived) | — | Moved to `archive/history/timeline/` | 📦 Archived |
| `emergent-microservices` (Archived) | — | Moved to `archive/history/timeline/` | 📦 Archived |
| `hardware_schematics/` (Archived) | — | Moved to `archive/history/timeline/` | 📦 Archived |
| `logs/` | ~1 | Log directory (gitkeep) | ✅ Active |
| `.codacy/` | — | Codacy config | ✅ Active |
| `.devcontainer/` | — | Dev container setup | ✅ Active |
| `.githooks/` | — | Custom git hooks | ✅ Active |
| `.vscode/` | — | VS Code settings | ✅ Active |
| `.agent/` / `.agents/` | — | Agent workflows & configs | ✅ Active |

---

## 🔗 Submodules

| Submodule | Path | URL | Status |
|-----------|------|-----|--------|
| Cerberus | `external/Cerberus` | `IAmSoThirsty/Cerberus` | ✅ Initialized |
| Thirsty-Lang | `external/Thirsty-Lang` | `IAmSoThirsty/Thirsty-Lang.git` | ✅ Initialized |
| Thirstys-Monolith | `external/Thirstys-Monolith` | `IAmSoThirsty/Thirstys-Monolith.git` | ✅ Initialized |
| Thirstys-Waterfall | `external/Thirstys-Waterfall` | `IAmSoThirsty/Thirstys-Waterfall.git` | ⚡ `v1.0.0-4-g931f47b` |
| The_Triumvirate | `external/The_Triumvirate` | `IAmSoThirsty/The_Triumvirate.git` | ✅ Initialized |
| Penetration-Testing-Tools | `security/penetration-testing-tools` | `mgeeky/Penetration-Testing-Tools.git` | ✅ `heads/master` |

---

## ⚙️ Configuration & Build Systems

### Language Runtimes

| Runtime | Version | Config Source |
|---------|---------|---------------|
| Python | **3.12** | `.python-version`, `pyproject.toml`, `gradle.properties`, `Dockerfile.sovereign` |
| Node.js | 20.11.0 | `gradle.properties` |
| Go | 1.22 | `Dockerfile.sovereign` (OctoReflex builder) |
| Gradle | wrapper | `gradle/wrapper/gradle-wrapper.properties` |

### Build Targets

| Target | Tool | Entrypoint |
|--------|------|------------|
| Python package | pip / pyproject.toml | `pyproject.toml` |
| Windows installer | PyInstaller | `build-installer.ps1`, `Project-AI.spec` |
| Docker image | Docker | `Dockerfile`, `Dockerfile.sovereign` |
| Android APK | Gradle | `android/`, `build.gradle.kts` |
| Desktop app | Electron/Tauri | `desktop/` |
| Web frontend | npm | `web/`, `package.json` |
| Unity build | Unity Editor | `unity/` |
| Helm chart | Helm | `helm/` |
| K8s deploy | kubectl/kustomize | `k8s/` |
| Terraform | Terraform CLI | `terraform/` |

### Linting & Formatting

| Tool | Config | Scope |
|------|--------|-------|
| Black | `.pre-commit-config.yaml` | Python formatting |
| Ruff (v0.9.2) | `.pre-commit-config.yaml` | Python linting |
| isort | `.pre-commit-config.yaml` | Import sorting |
| ESLint | `.eslintrc.json` | JS/TS linting |
| Prettier | `.prettierrc` | JS/TS formatting |
| Bandit | `.bandit` | Python security |
| detect-secrets | `.pre-commit-config.yaml` | Secret scanning |
| markdownlint | `.markdownlint.yaml` | Markdown style |

---

## 🚀 CI/CD & GitHub

### Workflows (`.github/workflows/`)

| Workflow | Purpose |
|----------|---------|
| `monolith.yml` | Monolith CI pipeline |
| `sign-release-artifacts.yml` | Release signing |
| `sbom.yml` | Software Bill of Materials |
| `ai-model-security.yml` | AI model security scans |
| `periodic-security-verification.yml` | Scheduled security verification |
| `validate-waivers.yml` | Security waiver validation |
| `validate-guardians.yml` | Guardian approval enforcement |
| `enforce-root-structure.yml` | Root structure enforcement |
| `doc-code-alignment.yml` | Doc/code alignment checks |
| *(+ additional workflows)* | |

### GitHub Config

| File | Purpose |
|------|---------|
| `.github/CODEOWNERS` | Code ownership (all → `@IAmSoThirsty`) |
| `.github/pull_request_template.md` | PR template |
| `.github/security-waivers.yml` | Security waiver definitions |
| `.github/ISSUE_TEMPLATE/` | Issue templates |
| `.github/FUNDING.yml` | Sponsor config |

---

## 🔐 Security & Governance

| Component | Location | Description |
|-----------|----------|-------------|
| Security Framework | `SECURITY.md`, `docs/SECURITY_FRAMEWORK.md` | Policy & incident response |
| Threat Model | `docs/security/THREAT_MODEL_SECURITY_WORKFLOWS.md` | Threat modeling |
| Governance | `governance/` | Audit logs, compliance framework |
| Policies | `policies/` | Organizational policies |
| CODEOWNERS | `.github/CODEOWNERS` | Approval gates |
| Pen-Testing | `security/penetration-testing-tools/` | Third-party security tools |
| H.323 Profile | `h323_sec_profile/` | Protocol security profiles |
| CodeQL | `codeql-custom-queries-python/` | Custom CodeQL queries |
| Bandit | `.bandit` | Python security scanner |
| detect-secrets | `.pre-commit-config.yaml` | Pre-commit secret scanning |

---

## 📊 Repository Statistics

| Metric | Value |
|--------|-------|
| **Total tracked files** | 4,963 |
| **Top-level directories** | 71 |
| **Top-level files** | 62 |
| **Git submodules** | 6 |
| **Python version** | 3.12 |
| **Node.js version** | 20.11.0 |
| **Total README size** | 76 KB |
| **Largest build file** | `build.gradle.kts` (70 KB) |
| **Locked deps file** | `requirements.lock` (122 KB) |

---

## 🏗️ Architecture Overview

```text
Project-AI/
├── src/                    # Sovereign Source (interpreted via Native Bridge)
│   ├── app/
│   │   └── core/           # Native logic & Host Bridges (thirsty_native_bridge.py)
│   └── foundation/         # Thirsty-Lang Specifications (THIRSTY_LANG_SPEC.thirsty)
├── engines/                # AI/ML engine implementations
├── cognition/              # Cognitive processing pipeline
├── kernel/                 # Runtime kernel primitives
├── tarl/                   # T.A.R.L. native compiler/runtime
├── docs/                   # All documentation (incl. sovereignty manifesto)
├── sovereign_core.tscgb    # Final TSCG-B Binary Encapsulation (v3.5)
└── ...
── tests/                  # Unit/integration tests
├── adversarial_tests/      # Red-team test suites
├── e2e/                    # End-to-end tests
├── external/               # Git submodules (Cerberus, Thirsty-Lang, etc.)
├── scripts/                # Utility scripts
├── tools/                  # Developer tools
├── .github/                # CI/CD workflows, templates, CODEOWNERS
└── EditionV1/              # Edition V1 release package
```

---

### 🛡️ Sovereign Documentation Standard — Master Tier

### *Generated by Project-AI System Audit • 2026-03-10*
