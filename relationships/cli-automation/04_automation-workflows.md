---
title: Automation Workflows Relationships
description: GitHub Actions workflow orchestration and relationships
tags:
  - relationships
  - github-actions
  - workflows
  - ci-cd
created: 2025-02-08
agent: AGENT-063
---

# Automation Workflows Relationships

## Overview

Project-AI uses **GitHub Actions** for comprehensive CI/CD automation through a consolidated **"God Tier"** monolithic workflow architecture.

## 🏛️ Primary Workflow: Codex Deus Ultimate

**File**: `.github/workflows/codex-deus-ultimate.yml`

**Purpose**: Consolidated workflow replacing 28 individual workflows with zero redundancy.

### Workflow Architecture

```
Codex Deus Ultimate (86.4 KB)
├─ Phase 1: Initialization & Smart Detection
├─ Phase 2: Pre-Flight Security Scanning
├─ Phase 3: AI Safety & Model Security
├─ Phase 4: Code Quality & Linting
├─ Phase 5: Comprehensive Testing Matrix
├─ Phase 6: Coverage Enforcement & Reporting
├─ Phase 7: Build & Compilation (Multi-Platform)
├─ Phase 8: SBOM Generation & Signing
├─ Phase 9: Container Security Scanning
├─ Phase 10: Auto-Fix & Remediation
├─ Phase 11: PR/Issue Automation
├─ Phase 12: Release Management
├─ Phase 13: Post-Merge Validation
├─ Phase 14: Cleanup & Maintenance
└─ Phase 15: Comprehensive Reporting
```

---

## 🎯 Workflow Triggers

### Push Events
```yaml
on:
  push:
    branches:
      - main
      - develop
      - cerberus-integration
      - 'copilot/**'
      - 'feature/**'
      - 'fix/**'
      - 'release/**'
    paths-ignore:
      - '**.md'
      - 'docs/**'
    tags:
      - 'v*.*.*'
```

**Triggers**: Code changes on main branches, feature branches, and version tags

**Excludes**: Documentation-only changes

---

### Pull Request Events
```yaml
  pull_request:
    branches: [main, develop, cerberus-integration]
    types: [opened, synchronize, reopened, ready_for_review, labeled]
  
  pull_request_target:
    types: [opened, synchronize, reopened]
```

**Triggers**: PR lifecycle events (open, update, reopen, review)

**Security**: Uses `pull_request_target` for external contributors

---

### Scheduled Events
```yaml
  schedule:
    - cron: '0 */6 * * *'    # Every 6 hours - Security monitoring
    - cron: '0 2 * * *'      # Daily 2 AM - Security scans
    - cron: '0 3 * * *'      # Daily 3 AM - Issue triage
    - cron: '0 5 * * 0'      # Weekly Sunday - Cleanup
    - cron: '0 3 * * 1'      # Weekly Monday - Verification
```

**Triggers**: Automated maintenance, security scans, artifact cleanup

**Frequency**: Hourly to weekly based on task

---

### Manual Dispatch
```yaml
  workflow_dispatch:
    inputs:
      run_phase:
        description: 'Which phase to run'
        type: choice
        options:
          - all
          - security
          - testing
          - build
          - release
```

**Triggers**: Manual workflow execution with phase selection

**Use Case**: Targeted workflow runs (e.g., only security phase)

---

## 🔄 Workflow Phases

### Phase 1: Initialization & Smart Detection

**Purpose**: Detect changes and skip unnecessary jobs

**Jobs**:
- **setup**: Environment initialization
- **detect-changes**: Path-based change detection

**Outputs**:
- `python_changed`: Boolean
- `javascript_changed`: Boolean
- `docker_changed`: Boolean
- `security_changed`: Boolean

**Relationships**:
- **Enables**: Conditional job execution
- **Optimizes**: CI runtime by skipping unrelated jobs

---

### Phase 2: Pre-Flight Security Scanning

**Purpose**: Security checks before code review

**Jobs**:
- **secrets-detection**: Detect leaked secrets
- **dependency-scan**: Audit dependencies for vulnerabilities
- **codeql-analysis**: Static code analysis

**Tools**:
- detect-secrets
- pip-audit, npm audit
- GitHub CodeQL

**Relationships**:
- **Calls**: `scripts/run_security_worker.py`
- **Generates**: SARIF reports → GitHub Security tab
- **Blocks**: PRs with critical vulnerabilities

---

### Phase 3: AI Safety & Model Security

**Purpose**: Validate AI code changes against safety policies

**Jobs**:
- **adversarial-testing**: Run red team tests on AI changes
- **constitutional-validation**: Verify FourLaws compliance
- **model-security**: Scan model artifacts

**Conditional**: Only runs if AI code changed

**Relationships**:
- **Calls**: `adversarial_tests/run_all_tests.py`
- **Validates**: Constitutional AI implementation
- **Reports**: AI safety metrics

---

### Phase 4: Code Quality & Linting

**Purpose**: Enforce code quality standards

**Jobs**:
- **ruff-lint**: Python linting
- **eslint**: JavaScript/TypeScript linting
- **markdownlint**: Documentation linting
- **mypy**: Python type checking

**Auto-fix**:
- Creates auto-fix commits for formatting issues
- Runs `ruff check . --fix`
- Commits via GitHub Actions bot

**Relationships**:
- **Uses**: `pyproject.toml` configuration
- **Enforces**: Code style consistency
- **Generates**: Auto-fix PRs

---

### Phase 5: Comprehensive Testing Matrix

**Purpose**: Multi-platform, multi-version testing

**Jobs**:
- **test-python**: Python 3.11, 3.12
- **test-javascript**: Node.js 18, 20
- **test-e2e**: End-to-end tests
- **test-integration**: Integration tests

**Matrix Strategy**:
```yaml
strategy:
  matrix:
    python-version: [3.11, 3.12]
    os: [ubuntu-latest, windows-latest]
```

**Relationships**:
- **Calls**: `npm run test`, `pytest -v`
- **Executes**: `scripts/run_e2e_tests.ps1`
- **Generates**: Test reports, coverage

---

### Phase 6: Coverage Enforcement & Reporting

**Purpose**: Maintain code coverage thresholds

**Jobs**:
- **coverage-python**: Python coverage (80% threshold)
- **coverage-javascript**: JavaScript coverage
- **coverage-report**: Generate unified report

**Enforcement**:
- Fails if coverage drops below 80%
- Posts coverage comment on PRs
- Uploads coverage to Codecov

**Relationships**:
- **Depends**: Phase 5 (testing)
- **Generates**: `test-artifacts/coverage.json`
- **Posts**: PR comments with coverage delta

---

### Phase 7: Build & Compilation (Multi-Platform)

**Purpose**: Build artifacts for all platforms

**Jobs**:
- **build-docker**: Docker image builds
- **build-android**: Android APK (Legion Mini)
- **build-desktop**: Electron desktop app
- **build-python**: Python package

**Artifacts**:
- Docker images → Container registry
- APKs → GitHub releases
- Desktop executables → GitHub releases
- Python wheels → PyPI (optional)

**Relationships**:
- **Calls**: `scripts/build_production.ps1`
- **Uses**: `Dockerfile`, `build.gradle`
- **Uploads**: Build artifacts to GitHub

---

### Phase 8: SBOM Generation & Signing

**Purpose**: Generate Software Bill of Materials and sign artifacts

**Jobs**:
- **generate-sbom**: Create SBOM (CycloneDX, SPDX)
- **sign-artifacts**: Sign releases with GPG

**Tools**:
- CycloneDX
- SPDX generator
- GPG signing

**Relationships**:
- **Depends**: Phase 7 (builds)
- **Generates**: SBOM files
- **Signs**: Release artifacts

---

### Phase 9: Container Security Scanning

**Purpose**: Scan Docker images for vulnerabilities

**Jobs**:
- **trivy-scan**: Trivy container scanning
- **grype-scan**: Grype vulnerability scanning

**Thresholds**:
- Fail on HIGH/CRITICAL vulnerabilities
- Warning on MEDIUM

**Relationships**:
- **Depends**: Phase 7 (docker build)
- **Generates**: SARIF reports
- **Uploads**: GitHub Security tab

---

### Phase 10: Auto-Fix & Remediation

**Purpose**: Automatically fix security/quality issues

**Jobs**:
- **auto-fix-security**: Apply security patches
- **auto-fix-linting**: Fix linting violations
- **dependency-update**: Update vulnerable deps

**Relationships**:
- **Triggered by**: Phase 2, 4, 9 failures
- **Generates**: Auto-fix PRs
- **Labels**: `auto-fix`, `security`

---

### Phase 11: PR/Issue Automation

**Purpose**: Automate PR/issue lifecycle

**Jobs**:
- **pr-labeling**: Auto-label PRs by path
- **issue-triage**: Auto-assign and prioritize
- **pr-review**: Auto-approve Dependabot PRs

**Relationships**:
- **Uses**: `.github/labeler.yml`
- **Calls**: GitHub GraphQL API
- **Manages**: PR/issue lifecycle

---

### Phase 12: Release Management

**Purpose**: Automated release publishing

**Jobs**:
- **create-release**: Create GitHub release
- **publish-pypi**: Publish to PyPI
- **publish-npm**: Publish to npm
- **deploy-production**: Deploy to production

**Conditional**: Only on version tags (`v*.*.*`)

**Relationships**:
- **Depends**: All previous phases pass
- **Calls**: `scripts/deploy_complete.ps1`
- **Publishes**: Release artifacts

---

### Phase 13: Post-Merge Validation

**Purpose**: Verify merge quality

**Jobs**:
- **validate-main**: Ensure main branch health
- **regression-tests**: Run regression suite
- **performance-benchmarks**: Performance tests

**Triggers**: After merge to main

**Relationships**:
- **Validates**: Merge success
- **Reports**: Merge quality metrics

---

### Phase 14: Cleanup & Maintenance

**Purpose**: Repository maintenance

**Jobs**:
- **prune-artifacts**: Delete old artifacts (> 90 days)
- **close-stale**: Close stale issues/PRs
- **cache-cleanup**: Clear old caches

**Schedule**: Weekly (Sunday 5 AM)

**Relationships**:
- **Manages**: Repository hygiene
- **Frees**: Storage space

---

### Phase 15: Comprehensive Reporting

**Purpose**: Generate unified reports

**Jobs**:
- **generate-report**: Unified CI/CD report
- **slack-notify**: Notify team (optional)
- **dashboard-update**: Update metrics dashboard

**Relationships**:
- **Aggregates**: All phase results
- **Generates**: `ci-reports/unified-report.json`
- **Notifies**: Team on failures

---

## 🔗 Workflow Dependencies

### Sequential Dependencies
```
Phase 1 (Init) → Phase 2 (Security) → Phase 4 (Linting)
    ↓                                       ↓
Phase 3 (AI Safety)                    Phase 5 (Testing)
    ↓                                       ↓
                                       Phase 6 (Coverage)
                                            ↓
                                       Phase 7 (Build)
                                            ↓
                                       Phase 8 (SBOM)
                                            ↓
                                       Phase 9 (Container Scan)
                                            ↓
                        Phase 10 (Auto-fix) ← failures
                                            ↓
                                       Phase 12 (Release)
                                            ↓
                                       Phase 13 (Post-merge)
```

### Parallel Jobs
- Phases 2, 3, 4 run in parallel (if changes detected)
- Phase 5 tests run in matrix (parallel)
- Phase 7 builds run in parallel

---

## 📊 Additional Workflows

### `validate-metadata.yml`
**Purpose**: Validate YAML frontmatter in docs

**Trigger**: Push to docs/, wiki/

**Jobs**:
1. Run `scripts/automation/validate-tags.ps1`
2. Check taxonomy compliance
3. Report violations

---

### `enforce-root-structure.yml`
**Purpose**: Enforce root directory structure

**Trigger**: Push to root

**Jobs**:
1. Run `scripts/hooks/pre-commit-root-structure.sh`
2. Reject root file additions
3. Comment on PR

---

### `doc-code-alignment.yml`
**Purpose**: Ensure docs match code

**Trigger**: Push to src/, docs/

**Jobs**:
1. Extract code examples from docs
2. Validate against actual code
3. Report mismatches

---

### `generate-sbom.yml`
**Purpose**: Daily SBOM generation

**Trigger**: Daily schedule

**Jobs**:
1. Generate CycloneDX SBOM
2. Generate SPDX SBOM
3. Upload to repository

---

## 🔄 Workflow Chains

### PR Validation Chain
```
PR opened
    ↓
Codex Deus: Phases 1-6
    ├─ Security scans
    ├─ Linting
    └─ Testing
    ↓
Auto-fix (if needed)
    ↓
Human review (if passes)
    ↓
Merge
    ↓
Post-merge validation
```

### Release Chain
```
Version tag pushed (v1.2.3)
    ↓
Codex Deus: All phases
    ├─ Security → Linting → Testing → Coverage
    ├─ Build all platforms
    ├─ Generate SBOM
    ├─ Sign artifacts
    └─ Container scan
    ↓
Create GitHub release
    ↓
Publish to PyPI/npm
    ↓
Deploy to production
    ↓
Post-deploy validation
```

---

## 🛡️ Security Integration

### Secrets Management
- GitHub Secrets for credentials
- OIDC token for cloud deployments
- No secrets in workflow files

### Dependency Scanning
- Daily pip-audit + npm audit
- Auto-update minor/patch versions
- Manual review for major updates

### Code Scanning
- CodeQL (Python, JavaScript)
- Bandit (Python security)
- Trivy (container vulnerabilities)

---

## 📈 Workflow Metrics

### Execution Times (Typical)
- **PR validation**: 10-15 minutes
- **Full workflow (all phases)**: 30-45 minutes
- **Security-only**: 5-8 minutes
- **Build-only**: 15-20 minutes

### Success Rates
- **Main branch**: > 95% pass rate
- **PR validation**: > 90% pass rate
- **Auto-fix success**: > 80% fix rate

---

## 🔍 Related Documentation

- **Scripts**: See `03_scripts.md`
- **Build Tools**: See `05_build-tools.md`
- **Pre-commit Hooks**: See `09_pre-commit-hooks.md`

---

**Version**: 1.0.0  
**Last Updated**: 2025-02-08  
**Maintainer**: AGENT-063  
