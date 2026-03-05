<!--                                         [2026-03-04 09:48] -->
<!--                                        Productivity: Active -->
# 🔧 Repository Configuration Guide

This guide walks through configuring repository settings for the sovereign CI/CD pipeline as specified in `docs/REPOSITORY_HARDENING.md`.

## 🚨 Important: Manual Configuration Required

**Note**: The configuration script `scripts/configure-repository.sh` requires **admin access** to the repository. GitHub Actions workflows run with limited permissions and cannot modify repository settings. This configuration must be performed manually by a repository administrator.

## 📋 Configuration Checklist

### Prerequisites

✅ **Required**:

- Repository admin access
- GitHub CLI (`gh`) installed and authenticated
- Read `docs/REPOSITORY_HARDENING.md` thoroughly

### Step 1: Run Configuration Check

First, check the current configuration status:

```bash
./scripts/configure-repository.sh --check-only
```

This will report:

- Branch protection status for `main` and `release` branches
- Security features status
- Actions permissions
- Required labels
- CODEOWNERS file presence

### Step 2: Branch Protection Settings

Navigate to: **Settings → Branches → Branch protection rules**

#### For `main` and `release` branches

**Pull Request Requirements:**

1. ✅ Require pull request before merging
   - Minimum approvals: **2**
   - Dismiss stale reviews: **Yes**
   - Require review from Code Owners: **Yes**

**Status Check Requirements:**

1. ✅ Require status checks to pass before merging
   - Require branches to be up to date: **Yes**
   - Required checks:
     - `🛡️ Sovereign Pipeline - Full Trust Chain`
     - `Unit Tests` (if applicable)
     - `Canonical Scenario Replay` (if applicable)
     - `Adversarial Security Suite` (if applicable)
     - `SBOM Generation` (if applicable)

**Additional Restrictions:**

1. ✅ Require signed commits: **Yes**
1. ✅ Require linear history: **Yes**
1. ✅ Require conversation resolution: **Yes**
1. ✅ Do not allow bypassing settings: **Yes**
1. ✅ Restrict who can push: **Admins only**

### Step 3: Security Features

Navigate to: **Settings → Security → Code security and analysis**

Enable all security features:

1. ✅ Dependency graph
1. ✅ Dependabot alerts
1. ✅ Dependabot security updates
1. ✅ Code scanning (CodeQL)
1. ✅ Secret scanning
1. ✅ Secret scanning push protection

### Step 4: Actions Permissions

Navigate to: **Settings → Actions → General**

Configure:

1. **Actions permissions**: Allow select actions and reusable workflows

1. **Allowed actions pattern**:

   ```
   actions/checkout@*,
   actions/setup-python@*,
   actions/upload-artifact@*,
   docker/login-action@*,
   docker/build-push-action@*,
   docker/setup-buildx-action@*,
   docker/metadata-action@*,
   actions/attest-build-provenance@*
   ```

1. **Workflow permissions**: Read repository contents and packages permissions

1. **Allow GitHub Actions to create PRs**: Yes

### Step 5: Required Labels

Navigate to: **Settings → Issues → Labels**

Create these labels if they don't exist:

| Label             | Color     | Description                   |
| ----------------- | --------- | ----------------------------- |
| `security`        | `#b60205` | Security-related issues/PRs   |
| `supply-chain`    | `#d93f0b` | Supply chain security         |
| `auto-merge`      | `#0e8a16` | Auto-approve after tests pass |
| `breaking-change` | `#d73a4a` | Breaking API changes          |
| `release`         | `#0075ca` | Release preparation           |
| `canonical`       | `#5319e7` | Canonical scenario changes    |
| `triumvirate`     | `#fbca04` | Triumvirate system changes    |

Or run the automated script (requires admin):

```bash
./scripts/configure-repository.sh
```

### Step 6: Verify CODEOWNERS

Ensure `/CODEOWNERS` or `/.github/CODEOWNERS` exists and is properly configured.

Current file location: `/CODEOWNERS` ✅

Review and update owners as needed for your team structure.

### Step 7: Package Registry Configuration

Navigate to: **Settings → Packages**

If packages are published:

1. Set package visibility (Public or Private)
1. Ensure workflows have write access
1. Set delete/restore protection to admin only

## 🧪 Testing the Configuration

After configuration:

1. **Test Branch Protection**:

   ```bash

   # Try to push directly to main (should fail)

   git checkout main
   git commit --allow-empty -m "test: branch protection"
   git push  # Expected: rejection
   ```

1. **Test PR Workflow**:

   - Create a test branch
   - Open a PR to main
   - Verify required checks run
   - Verify 2 approvals are required
   - Test that force push is blocked

1. **Test Pipeline**:

   ```bash

   # Push to a feature branch

   git checkout -b test/pipeline
   git commit --allow-empty -m "test: pipeline"
   git push -u origin test/pipeline
   ```

   Then create a PR and watch the pipeline run.

## 🔍 Verification Commands

Check configuration status:

```bash

# Check branch protection

gh api /repos/IAmSoThirsty/Project-AI/branches/main/protection | jq '.'

# Check security features

gh api /repos/IAmSoThirsty/Project-AI/vulnerability-alerts

# Check Actions permissions

gh api /repos/IAmSoThirsty/Project-AI/actions/permissions | jq '.'

# List labels

gh api /repos/IAmSoThirsty/Project-AI/labels | jq '.[].name'
```

## 📊 Expected Outcomes

After proper configuration:

1. ✅ Direct pushes to `main` blocked
1. ✅ PRs require 2 approvals
1. ✅ Pipeline runs on all PRs
1. ✅ Unsigned commits rejected
1. ✅ Security scanning active
1. ✅ Dependabot updates enabled
1. ✅ Build provenance attestation working

## 🚨 Troubleshooting

### "gh: Resource not accessible by integration"

- This means the current token doesn't have admin access
- Must authenticate as a repository admin: `gh auth login`

### Branch protection not enforcing

- Verify you don't have "Allow admins to bypass" enabled
- Check that the branch name exactly matches (case-sensitive)

### Required checks not showing

- The check name must exactly match the workflow job name
- Check workflow has run at least once to appear in the list

### Signed commits failing

- Developers need to configure GPG keys
- See: <https://docs.github.com/en/authentication/managing-commit-signature-verification>

## 📖 Reference Documents

- `docs/REPOSITORY_HARDENING.md` - Complete hardening requirements
- `scripts/configure-repository.sh` - Automated configuration script
- `.github/workflows/project-ai-monolith.yml` - Sovereign pipeline definition

## ✅ Final Verification

Run the complete verification:

```bash
./scripts/configure-repository.sh --check-only
```

All checks should pass with ✅ green checkmarks.

______________________________________________________________________

**Last Updated**: 2026-03-03 **Version**: 2.1.0 **Status**: ✅ Verified & Locked
