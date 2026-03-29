<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / REPOSITORY_HARDENING.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / REPOSITORY_HARDENING.md # -->
<!-- # ============================================================================ #

<!--                                         [2026-03-04 09:48] -->
<!--                                        Productivity: Active -->
# 🔒 Repository Hardening Configuration

This document outlines the **mandatory** repository settings required to maintain the sovereign CI/CD trust boundary model for Project-AI.

## ⚡ Quick Reference

**Security Level**: Maximum **Trust Model**: Zero-trust with explicit verification at every layer **Compliance**: Full supply chain integrity enforcement

______________________________________________________________________

## 🛡️ Branch Protection Rules

### Protected Branches

- `main`
- `release`

### Required Settings for Each Protected Branch

#### Pull Request Requirements

✅ **Require pull request before merging**

- Minimum approvals: **2**
- Dismiss stale pull request approvals when new commits are pushed: **Enabled**
- Require review from Code Owners: **Enabled**

#### Status Check Requirements

✅ **Require status checks to pass before merging**

- Require branches to be up to date before merging: **Enabled**

Required status checks:

- `🛡️ Sovereign Pipeline - Full Trust Chain`
- `Unit Tests`
- `Canonical Scenario Replay`
- `Adversarial Security Suite`
- `SBOM Generation`

#### Additional Restrictions

✅ **Require signed commits**: **Enabled** ✅ **Require linear history**: **Enabled** ✅ **Require conversation resolution before merging**: **Enabled** ✅ **Do not allow bypassing the above settings**: **Enabled** ✅ **Restrict who can push to matching branches**: **Enabled** (Admins only)

______________________________________________________________________

## 🔐 Repository Settings

### General Settings

Navigate to: `Settings > General`

| Setting                                | Value       | Purpose                   |
| -------------------------------------- | ----------- | ------------------------- |
| **Disable force push**                 | ✅ Enabled  | Prevent history rewriting |
| **Disable branch deletion**            | ✅ Enabled  | Protect release branches  |
| **Allow merge commits**                | ✅ Enabled  | Preserve full history     |
| **Allow squash merging**               | ⚠️ Optional | Clean commit history      |
| **Allow rebase merging**               | ❌ Disabled | Enforce linear history    |
| **Automatically delete head branches** | ✅ Enabled  | Cleanup after merge       |

### Security Settings

Navigate to: `Settings > Security > Code security and analysis`

| Feature                             | Status     | Configuration              |
| ----------------------------------- | ---------- | -------------------------- |
| **Dependency graph**                | ✅ Enabled | Always on                  |
| **Dependabot alerts**               | ✅ Enabled | All severities             |
| **Dependabot security updates**     | ✅ Enabled | Auto-create PRs            |
| **Code scanning (CodeQL)**          | ✅ Enabled | Weekly schedule            |
| **Secret scanning**                 | ✅ Enabled | Push protection            |
| **Secret scanning push protection** | ✅ Enabled | Block commits with secrets |

### Actions Settings

Navigate to: `Settings > Actions > General`

| Setting                                | Value                                             | Purpose                      |
| -------------------------------------- | ------------------------------------------------- | ---------------------------- |
| **Actions permissions**                | Allow select actions                              | Prevent unauthorized actions |
| **Workflow permissions**               | Read repository contents and packages permissions | Minimal privilege            |
| **Allow GitHub Actions to create PRs** | ✅ Enabled                                        | Auto-fix workflows           |

**Allowed Actions Pattern**:

```
actions/checkout@*
actions/setup-python@*
actions/upload-artifact@*
docker/login-action@*
docker/build-push-action@*
docker/setup-buildx-action@*
docker/metadata-action@*
actions/attest-build-provenance@*
```

______________________________________________________________________

## 📋 CODEOWNERS Configuration

Create or update `.github/CODEOWNERS`:

```

# Global owners

* @IAmSoThirsty

# Core system components

/src/cognition/                    @IAmSoThirsty
/src/cognition/galahad/            @IAmSoThirsty
/src/cognition/cerberus/           @IAmSoThirsty
/src/cognition/codex/              @IAmSoThirsty

# Security critical

/security/                         @IAmSoThirsty
/canonical/                        @IAmSoThirsty
/adversarial_tests/                @IAmSoThirsty
/tarl/                            @IAmSoThirsty

# Infrastructure

/.github/workflows/                @IAmSoThirsty
/deploy/                          @IAmSoThirsty
/Dockerfile*                      @IAmSoThirsty
/requirements*.txt                @IAmSoThirsty
/requirements.lock                @IAmSoThirsty

# Documentation

/docs/                            @IAmSoThirsty
```

______________________________________________________________________

## 🏷️ Required Labels

Create the following labels in `Settings > Issues > Labels`:

| Label             | Color     | Description                   |
| ----------------- | --------- | ----------------------------- |
| `security`        | `#b60205` | Security-related issues/PRs   |
| `supply-chain`    | `#d93f0b` | Supply chain security         |
| `auto-merge`      | `#0e8a16` | Auto-approve after tests pass |
| `breaking-change` | `#d73a4a` | Breaking API changes          |
| `release`         | `#0075ca` | Release preparation           |
| `canonical`       | `#5319e7` | Canonical scenario changes    |
| `triumvirate`     | `#fbca04` | Triumvirate system changes    |

______________________________________________________________________

## 📦 Package Registry Configuration

Navigate to: `Settings > Packages`

| Setting                   | Configuration                        |
| ------------------------- | ------------------------------------ |
| **Package visibility**    | Public (or Private with team access) |
| **Manage Actions access** | Write access for workflows           |
| **Delete protection**     | Admin only                           |
| **Restore protection**    | Admin only                           |

### GHCR Permission Model

| Action          | Required Permission | Enforcement   |
| --------------- | ------------------- | ------------- |
| Pull public     | None                | Open          |
| Pull private    | Read                | Token-based   |
| Push version    | Write               | Workflow only |
| Delete version  | Admin               | Manual only   |
| Restore version | Admin               | Manual only   |

**Critical**: Never allow automatic deletion of package versions.

______________________________________________________________________

## 🔑 Secrets Configuration

Navigate to: `Settings > Secrets and variables > Actions`

### Required Secrets

| Secret Name    | Purpose                 | Scope         |
| -------------- | ----------------------- | ------------- |
| `GITHUB_TOKEN` | Default - auto-provided | All workflows |

### Optional Secrets (for extended features)

| Secret Name             | Purpose                | When Required            |
| ----------------------- | ---------------------- | ------------------------ |
| `OPENAI_API_KEY`        | AI integration tests   | If running full AI tests |
| `HUGGINGFACE_API_KEY`   | Image generation tests | If testing image gen     |
| `KUBECONFIG_STAGING`    | Staging deployment     | If deploying to K8s      |
| `KUBECONFIG_PRODUCTION` | Production deployment  | If deploying to K8s      |

______________________________________________________________________

## ✅ Verification Checklist

Use this checklist to verify proper configuration:

### Branch Protection

- [ ] `main` branch has 2 required approvals
- [ ] `release` branch has 2 required approvals
- [ ] Signed commits required on both branches
- [ ] Linear history enforced
- [ ] Status checks required before merge
- [ ] Stale reviews dismissed on new commits
- [ ] CODEOWNERS approval required

### Security Features

- [ ] Dependabot alerts enabled
- [ ] Dependabot security updates enabled
- [ ] CodeQL scanning enabled
- [ ] Secret scanning enabled
- [ ] Secret push protection enabled
- [ ] Dependency graph enabled

### Actions Configuration

- [ ] Workflow permissions set to read
- [ ] Allowed actions list configured
- [ ] PR creation by actions enabled

### Registry Configuration

- [ ] GHCR package linked to repository
- [ ] Delete protection requires admin
- [ ] Workflow has write access

### Documentation

- [ ] CODEOWNERS file present
- [ ] Required labels created
- [ ] Branch protection documented
- [ ] Team aware of requirements

______________________________________________________________________

## 🚨 Enforcement Policy

**These settings are non-negotiable.** They form the trust boundary that ensures:

1. ✅ No malicious code can be merged without review
1. ✅ All commits are traceable to verified developers
1. ✅ All dependencies are audited
1. ✅ All builds are reproducible
1. ✅ All artifacts are authenticated
1. ✅ All deployments are auditable

**Bypassing these settings is a security incident.**

______________________________________________________________________

## 📞 Support

For questions about repository hardening:

1. Review this document
1. Check `.github/workflows/project-ai-monolith.yml`
1. Review the problem statement in issue/PR
1. Contact repository maintainers

______________________________________________________________________

## 📝 Configuration Template

Use this GitHub CLI command to apply settings programmatically:

```bash

# Enable branch protection

gh api -X PUT /repos/:owner/:repo/branches/main/protection \
  --input branch-protection.json

# Enable security features

gh api -X PATCH /repos/:owner/:repo \
  -f has_vulnerability_alerts=true \
  -f has_automated_security_fixes=true

# Configure actions permissions

gh api -X PUT /repos/:owner/:repo/actions/permissions \
  -f enabled=true \
  -f allowed_actions=selected
```

See `scripts/configure-repository.sh` for complete automation.

______________________________________________________________________

**Last Updated**: 2026-02-13 **Version**: 1.0.0 **Status**: ✅ Production Standard
