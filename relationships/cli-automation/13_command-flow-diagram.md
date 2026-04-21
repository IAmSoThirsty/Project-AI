---
title: Command Flow Diagrams
description: Visual representations of CLI/automation command flows and execution chains
tags:
  - relationships
  - diagrams
  - command-flow
  - visualization
created: 2025-02-08
agent: AGENT-063
---

# Command Flow Diagrams

## Overview

Visual representations of command execution paths, automation chains, and integration flows across Project-AI's CLI and automation systems.

---

## 🎯 Master Command Flow

### Complete System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INPUT LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Terminal Commands          IDE Actions          Git Operations      │
│  ├─ python -m src.app.main  ├─ Run Debug        ├─ git commit      │
│  ├─ npm run <script>        ├─ Run Tests        ├─ git push         │
│  ├─ make <target>           └─ Format Code      └─ git tag          │
│  └─ project-ai <cmd>                                                 │
│                                                                       │
└───────────────────────┬─────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CLI INTERFACE LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  project_ai_cli.py    inspection_cli.py    deepseek_v32_cli.py     │
│  ├─ run               ├─ audit            ├─ completion            │
│  ├─ sovereign-verify  └─ analyze          ├─ chat                  │
│  ├─ verify-audit                          └─ interactive           │
│  └─ verify-bundle                                                   │
│                                                                       │
│  package.json (NPM)   Makefile            .pre-commit-config.yaml  │
│  ├─ test             ├─ run               ├─ black                 │
│  ├─ lint             ├─ test              ├─ ruff                  │
│  ├─ build            ├─ lint              ├─ isort                 │
│  └─ tarl:*           └─ format            └─ detect-secrets        │
│                                                                       │
└───────────────────────┬─────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    COMMAND HANDLER LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Argument Parsing    Command Routing       Validation               │
│  ├─ argparse        ├─ cmd_run()          ├─ Path checks           │
│  ├─ typer           ├─ cmd_verify_*()     ├─ Type validation       │
│  └─ subcommands     └─ main()             └─ Permission checks     │
│                                                                       │
└───────────────────────┬─────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     EXECUTION LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Core Modules        Scripts                Automation              │
│  ├─ IronPath        ├─ build_production    ├─ GitHub Actions       │
│  ├─ Sovereign       ├─ deploy_complete     ├─ Pre-commit hooks     │
│  ├─ DeepSeekV32     ├─ run_e2e_tests       └─ Scheduled jobs       │
│  └─ Inspection      └─ add-metadata                                 │
│                                                                       │
└───────────────────────┬─────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       OUTPUT LAYER                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Artifacts           Logs                  Reports                  │
│  ├─ Build outputs   ├─ Structured logs    ├─ Test results          │
│  ├─ SBOM files      ├─ Audit trails       ├─ Coverage reports      │
│  ├─ Compliance      ├─ Error logs         ├─ Security scans        │
│  └─ Releases        └─ Debug traces       └─ Metric dashboards     │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 CLI Command Execution Flows

### 1. Sovereign Runtime Execution Flow

```
$ project-ai run examples/sovereign-demo.yaml

    ↓
[project_ai_cli.py]
    ├─ Parse arguments: args.pipeline = "examples/sovereign-demo.yaml"
    └─ Route to: cmd_run(args)
        ↓
[cmd_run(args)]
    ├─ Log execution start
    ├─ Create IronPathExecutor(pipeline_path=args.pipeline)
    └─ Execute: result = executor.execute()
        ↓
[IronPathExecutor.execute()]
    ├─ Load pipeline YAML
    ├─ Validate pipeline structure
    ├─ Execute stages sequentially:
    │   ├─ data_preparation
    │   ├─ model_training
    │   ├─ agent_chain
    │   ├─ audit_export
    │   ├─ promotion
    │   └─ rollback (if needed)
    ├─ Generate cryptographic proofs
    ├─ Create audit trail (immutable_audit.jsonl)
    └─ Build compliance bundle
        ↓
[cmd_run(args) - Result Handling]
    ├─ Check result["status"]
    ├─ If "completed":
    │   ├─ Log success metrics
    │   ├─ Display artifact paths
    │   ├─ Show compliance bundle location
    │   └─ Exit(0)
    └─ If "failed":
        ├─ Log error details
        └─ Exit(1)
        ↓
[Output]
    ├─ governance/sovereign_data/artifacts/<execution_id>/
    │   ├─ stage_*.json (each stage artifact)
    │   ├─ execution_summary.json
    │   └─ compliance_bundle.json
    ├─ governance/sovereign_data/immutable_audit.jsonl
    └─ Exit code: 0 or 1
```

---

### 2. Desktop Application Launch Flow

```
$ python -m src.app.main
   OR
$ .\scripts\launch-desktop.ps1

    ↓
[launch-desktop.ps1] (if used)
    ├─ Set environment variables
    ├─ Check Python installation
    ├─ Activate virtual environment (.venv)
    └─ Execute: python -m src.app.main
        ↓
[Python Entry Point]
    └─ python -m src.app.main
        ├─ Import app.main module
        └─ Execute __main__ block
            ↓
[src/app/main.py]
    ├─ Import PyQt6
    ├─ Create QApplication
    ├─ Initialize LeatherBookInterface
    │   ├─ Setup dual-page layout (Tron + Dashboard)
    │   ├─ Load AI systems (FourLaws, Persona, Memory, etc.)
    │   └─ Setup signal connections
    ├─ Show main window
    └─ app.exec() (event loop)
        ↓
[Desktop Application]
    ├─ User login page (Tron theme)
    ├─ Dashboard (6 zones)
    │   ├─ Stats Panel
    │   ├─ Actions Panel
    │   ├─ AI Head
    │   ├─ Chat Panel
    │   └─ Response Panel
    └─ Interactive AI assistant
        ↓
[User Interaction Loop]
    └─ Event loop until application exit
```

---

### 3. NPM Script Execution Flow

```
$ npm run test

    ↓
[package.json]
    └─ "test": "npm run test:js && npm run test:python"
        ↓
[Sequential Execution]
    ├─ Step 1: npm run test:js
    │   └─ "test:js": "node --test src/**/*.test.js"
    │       ├─ Discover test files (src/**/*.test.js)
    │       ├─ Execute Node.js test runner
    │       └─ Report results
    │           ↓
    └─ Step 2: npm run test:python (if test:js succeeds)
        └─ "test:python": "pytest -q"
            ├─ Discover test files (tests/test_*.py)
            ├─ Execute pytest with quiet mode
            └─ Report results
                ↓
[Exit Codes]
    ├─ Both pass → Exit(0)
    └─ Either fails → Exit(1)
```

---

### 4. Make Target Execution Flow

```
$ make format

    ↓
[Makefile]
    └─ format target:
        ├─ isort src tests --profile black
        ├─ ruff check . --fix
        └─ black src tests
            ↓
[Sequential Formatting]
    ├─ Step 1: isort
    │   ├─ Sort imports in src/ and tests/
    │   ├─ Group: stdlib, third-party, local
    │   └─ Use black-compatible profile
    │       ↓
    ├─ Step 2: ruff
    │   ├─ Lint all Python files
    │   ├─ Auto-fix safe violations (--fix)
    │   └─ Report unfixable issues
    │       ↓
    └─ Step 3: black
        ├─ Format all Python files (src/, tests/)
        ├─ Apply PEP 8 style (line length 88)
        └─ Modify files in-place
            ↓
[Output]
    ├─ Formatted Python files
    ├─ Summary: X files reformatted, Y files left unchanged
    └─ Exit(0) if successful
```

---

## 🌊 Automation Chains

### 1. Git Commit → Pre-commit → Push Chain

```
Developer makes changes
    ↓
$ git add .
$ git commit -m "Add feature"
    ↓
[Pre-commit Hooks Triggered]
    ├─ black → Format Python files
    ├─ ruff → Lint + auto-fix
    ├─ isort → Sort imports
    ├─ end-of-file-fixer → Add EOF newlines
    ├─ trailing-whitespace → Remove trailing spaces
    ├─ check-yaml → Validate YAML
    ├─ check-added-large-files → Block large files
    ├─ check-merge-conflict → Detect merge markers
    ├─ mixed-line-ending → Fix CRLF/LF
    └─ detect-secrets → Scan for secrets
        ↓
[Hook Results]
    ├─ All pass → Commit created
    │   └─ $ git push
    │       ↓
    │       [GitHub Actions Triggered]
    │           └─ Codex Deus Ultimate workflow
    │
    └─ Any fail → Commit blocked
        ├─ Auto-fixes applied (if available)
        ├─ Developer reviews changes
        ├─ $ git add . (stage fixes)
        └─ $ git commit -m "Add feature" (retry)
            ↓
[After Push]
    └─ GitHub Actions workflow execution
        (See "GitHub Actions Workflow Chain" below)
```

---

### 2. GitHub Actions Workflow Chain

```
$ git push origin feature/new-feature
    ↓
[GitHub: Receive Push Event]
    ↓
[Codex Deus Ultimate Workflow]
    │
    ├─ Phase 1: Initialization & Smart Detection
    │   ├─ Checkout code
    │   ├─ Setup Python, Node.js
    │   └─ Detect changed files (python_changed, javascript_changed, etc.)
    │       ↓
    ├─ Phase 2: Pre-Flight Security (conditional)
    │   ├─ Secret detection
    │   ├─ Dependency vulnerability scan
    │   └─ CodeQL analysis
    │       ↓
    ├─ Phase 3: AI Safety (if AI code changed)
    │   ├─ Adversarial testing
    │   ├─ Constitutional validation
    │   └─ Model security scan
    │       ↓
    ├─ Phase 4: Code Quality & Linting
    │   ├─ Ruff (Python)
    │   ├─ ESLint (JavaScript)
    │   ├─ Markdownlint (Docs)
    │   └─ mypy (Type checking)
    │       ↓
    ├─ Phase 5: Testing Matrix
    │   ├─ Python 3.11, 3.12 (pytest)
    │   ├─ Node.js 18, 20 (node:test)
    │   ├─ E2E tests
    │   └─ Integration tests
    │       ↓
    ├─ Phase 6: Coverage Enforcement
    │   ├─ Generate coverage reports
    │   ├─ Check threshold (80%)
    │   └─ Post PR comment
    │       ↓
    ├─ Phase 7: Build (if tests pass)
    │   ├─ Docker image
    │   ├─ Android APK
    │   ├─ Desktop app
    │   └─ Python package
    │       ↓
    ├─ Phase 8: SBOM Generation
    │   ├─ Generate CycloneDX SBOM
    │   ├─ Generate SPDX SBOM
    │   └─ Sign artifacts
    │       ↓
    ├─ Phase 9: Container Security
    │   ├─ Trivy scan
    │   └─ Grype scan
    │       ↓
    ├─ Phase 10: Auto-Fix (if failures)
    │   ├─ Apply security patches
    │   ├─ Fix linting violations
    │   └─ Create auto-fix PR
    │       ↓
    └─ Phase 15: Reporting
        ├─ Generate unified report
        ├─ Update dashboards
        └─ Notify team (if failures)
            ↓
[Workflow Result]
    ├─ All pass → PR mergeable ✅
    │   └─ Human review
    │       └─ Merge to main
    │           └─ Phase 13: Post-merge validation
    │
    └─ Any fail → PR blocked ❌
        ├─ Auto-fix PR created (if possible)
        └─ Developer manual fix required
```

---

### 3. Release Build & Deployment Chain

```
Developer tags release: v1.2.3
    ↓
$ git tag v1.2.3
$ git push origin v1.2.3
    ↓
[GitHub: Tag Push Event]
    ↓
[Codex Deus: Release Phase]
    │
    ├─ Phases 1-9: Full validation
    │   (Security, linting, testing, building, scanning)
    │       ↓
    ├─ Phase 12: Release Management
    │   ├─ Create GitHub Release
    │   │   ├─ Tag: v1.2.3
    │   │   ├─ Attach artifacts:
    │   │   │   ├─ project-ai-v1.2.3.tar.gz
    │   │   │   ├─ legion_mini-v1.2.3.apk
    │   │   │   ├─ desktop-v1.2.3.exe
    │   │   │   └─ SBOMs (CycloneDX, SPDX)
    │   │   └─ Generate release notes
    │   │       ↓
    │   ├─ Publish to PyPI (optional)
    │   │   └─ twine upload dist/*
    │   │       ↓
    │   └─ Deploy to Production
    │       ├─ Execute: scripts/deploy_complete.ps1
    │       ├─ Deploy monitoring stack
    │       └─ Run post-deploy validation
    │           ↓
[Post-Deploy Validation]
    ├─ Health checks
    ├─ Smoke tests
    ├─ Performance benchmarks
    └─ Monitoring setup
        ↓
[Release Complete]
    ├─ GitHub Release published
    ├─ Artifacts available for download
    ├─ Production deployment verified
    └─ Monitoring active
```

---

### 4. Build Production Multi-Platform Chain

```
$ .\scripts\build_production.ps1 -All
    ↓
[build_production.ps1]
    ├─ Set JAVA_HOME for Gradle
    ├─ Parameters: -Desktop, -Android, -Portable, -All
    └─ Execute builds based on flags
        ↓
[Parallel Build Execution]
    │
    ├─ Android Build (if -Android or -All)
    │   ├─ .\gradlew.bat :legion_mini:assembleDebug
    │   ├─ .\gradlew.bat :legion_mini:assembleRelease
    │   └─ Output: android/legion_mini/build/outputs/apk/
    │       ├─ legion_mini-debug.apk
    │       └─ legion_mini-release.apk
    │           ↓
    ├─ Desktop Build (if -Desktop or -All)
    │   ├─ cd desktop
    │   ├─ npm install
    │   ├─ npm run build
    │   └─ Output: desktop/dist/
    │       └─ project-ai-desktop.exe
    │           ↓
    └─ Portable Build (if -Portable or -All)
        ├─ Package scripts/
        ├─ Include launchers
        ├─ Create archive
        └─ Output: builds/portable/
            └─ project-ai-portable.zip
                ↓
[Build Complete]
    ├─ Android APKs: android/legion_mini/build/outputs/apk/
    ├─ Desktop executable: desktop/dist/
    ├─ Portable package: builds/portable/
    └─ Build summary logged
```

---

## 📊 Conditional Execution Flows

### 1. Smart Change Detection Flow

```
GitHub Actions triggered
    ↓
[Detect Changes Job]
    ├─ Compare with base branch
    ├─ Identify changed file paths
    └─ Set output variables:
        ├─ python_changed: true/false
        ├─ javascript_changed: true/false
        ├─ docker_changed: true/false
        └─ security_changed: true/false
            ↓
[Conditional Job Execution]
    ├─ python_changed == true
    │   ├─ Run: Ruff linting
    │   ├─ Run: Python tests (pytest)
    │   └─ Run: mypy type checking
    │
    ├─ javascript_changed == true
    │   ├─ Run: ESLint
    │   └─ Run: Node.js tests
    │
    ├─ docker_changed == true
    │   ├─ Run: Docker build
    │   └─ Run: Trivy scan
    │
    └─ security_changed == true (always run on main)
        ├─ Run: CodeQL
        ├─ Run: Bandit
        └─ Run: Dependency scans
            ↓
[Optimization Result]
    └─ Only run necessary jobs (save CI time)
```

---

## 🔍 Error Handling & Recovery Flows

### 1. Auto-Fix Workflow

```
CI Phase 4: Linting fails
    ↓
[Linting Failure Detected]
    ├─ ruff check . → Exit code 1
    ├─ Violations logged
    └─ Trigger Phase 10: Auto-fix
        ↓
[Auto-Fix Execution]
    ├─ Run: ruff check . --fix
    ├─ Commit fixes:
    │   ├─ Author: github-actions[bot]
    │   └─ Message: "chore: auto-fix linting violations"
    ├─ Push to branch
    └─ Re-trigger workflow
        ↓
[Retry Workflow]
    ├─ Re-run linting
    └─ If pass → Continue
        If fail → Manual intervention needed
```

---

## 🎯 Entry Point Summary

### All Possible Entry Points

```
Command Line Entry Points:
├─ python -m src.app.main (Desktop app)
├─ python project_ai_cli.py <cmd> (Sovereign CLI)
├─ python inspection_cli.py (Audit CLI)
├─ python -m scripts.deepseek_v32_cli (Model inference)
├─ npm run <script> (NPM scripts)
├─ make <target> (Make targets)
├─ .\scripts\launch-desktop.ps1 (Windows launcher)
└─ .\scripts\launch-desktop.bat (Batch launcher)

Automated Entry Points:
├─ git commit → Pre-commit hooks
├─ git push → GitHub Actions workflows
├─ Scheduled cron → Maintenance workflows
└─ GitHub Events → Issue/PR automation

Build Entry Points:
├─ .\scripts\build_production.ps1 (Multi-platform)
├─ .\scripts\build_release.sh (Docker + tests)
└─ docker-compose up (Containerized)
```

---

**Version**: 1.0.0  
**Last Updated**: 2025-02-08  
**Maintainer**: AGENT-063  
