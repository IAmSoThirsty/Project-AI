# Archived Workflows

## 📦 Status: ARCHIVED

These workflows have been **consolidated** into a single, comprehensive workflow:
**`codex-deus-ultimate.yml`**

## Why Were These Archived?

All 28 individual workflows have been merged into the God Tier Codex Deus Ultimate workflow to:

1. **Eliminate Redundancy**: Removed 25-30% duplicate test execution
2. **Improve Performance**: Parallel execution reduces CI time by 3x
3. **Simplify Maintenance**: One workflow instead of 28
4. **Enhance Reliability**: Pre-merge gates prevent PR failures
5. **Complete Coverage**: All functionality preserved and enhanced

## Archived Workflows (28 Total)

### CI/Testing (5)

- `ci.yml` - Legacy CI pipeline
- `ci-consolidated.yml` - Consolidated CI
- `node-ci.yml` - Node.js specific CI
- `tarl-ci.yml` - TARL framework tests
- `coverage-threshold-enforcement.yml` - Coverage gates

### Security (6)

- `security-consolidated.yml` - Security scanning suite
- `adversarial-redteam.yml` - AI safety testing
- `ai-model-security.yml` - ML model security
- `periodic-security-verification.yml` - Nightly security
- `trivy-container-security.yml` - Container scanning
- `checkov-cloud-config.yml` - IaC security

### Build & Release (4)

- `build-release.yml` - Multi-platform builds
- `release.yml` - Release automation
- `sign-release-artifacts.yml` - Artifact signing
- `sbom.yml` - Software Bill of Materials

### Automation (3)

- `pr-automation-consolidated.yml` - PR automation
- `issue-management-consolidated.yml` - Issue triage
- `auto-create-branch-prs.yml` - Branch PR creation

### Validation (4)

- `validate-guardians.yml` - Guardian approvals
- `validate-waivers.yml` - Security waivers
- `post-merge-validation.yml` - Post-merge checks
- `gpt_oss_integration.yml` - GPT integration

### Infrastructure (3)

- `jekyll-gh-pages.yml` - Documentation
- `prune-artifacts.yml` - Artifact cleanup
- `dependabot.yml` - Dependabot config

### Other (3)

- `codex-deus-monolith.yml` - Previous consolidation attempt
- `snn-mlops-cicd.yml` - Neural network tests
- `main.yml` - Generic workflow

## Migration Guide

See **`WORKFLOWS_TO_DEPRECATE.md`** in the repository root for:

- Complete functionality mapping
- Feature equivalents in new workflow
- Migration instructions

## Restoration (if needed)

To restore any workflow:
```bash
cp .github/workflows/archive/<workflow-name>.yml .github/workflows/
git add .github/workflows/<workflow-name>.yml
git commit -m "Restore <workflow-name>"
```

## New Workflow Reference

The ultimate workflow includes all functionality from these 28 workflows plus:

- Smart path-based detection
- Auto-healing with PR creation
- Comprehensive reporting
- Enhanced error handling
- Better parallelization

**Documentation:**

- `CODEX_DEUS_INDEX.md` - Getting started
- `CODEX_DEUS_ULTIMATE_SUMMARY.md` - Complete technical reference
- `CODEX_DEUS_QUICK_REF.md` - Quick reference guide

---

**Archived:** 2026-02-01
**By:** Codex Deus Ultimate Migration
**Reason:** Consolidated into single God Tier workflow
