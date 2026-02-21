# Branch Protection Rules

This document outlines the recommended branch protection rules for the Project-AI repository to ensure code quality, security, and proper review processes.

## Overview

Branch protection rules are critical security controls that prevent unauthorized or unsafe changes to important branches. GitHub provides these features natively, and they should be configured in repository settings.

## Recommended Protection Rules

### Main Branch (`main`)

The `main` branch contains production-ready code and requires the strictest protections:

#### Required Settings

**Require pull request reviews before merging**
- ✅ Require approvals: **1 approval minimum**
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require review from Code Owners (when CODEOWNERS file is present)
- ✅ Require approval of the most recent reviewable push
- ❌ Allow specified actors to bypass required pull requests (only for emergencies)

**Require status checks to pass before merging**
- ✅ Require branches to be up to date before merging
- ✅ Required status checks:
  - `CodeQL Security Analysis / Analyze Code (python)`
  - `CodeQL Security Analysis / Analyze Code (javascript)`
  - `Dependency Review / Review Dependencies`
  - `Dependency Review / Python Dependency Audit`
  - Tests from monolith workflow (if applicable)
  - Linting checks

**Additional protections**
- ✅ Require conversation resolution before merging
- ✅ Require signed commits (recommended for high-security environments)
- ✅ Require linear history (optional, based on team preference)
- ✅ Include administrators (enforce rules on administrators too)
- ✅ Restrict pushes that create matching branches
- ✅ Allow force pushes: **Disabled**
- ✅ Allow deletions: **Disabled**

**Push restrictions**
- Limit who can push to matching branches to repository administrators only

### Develop Branch (`develop`)

The `develop` branch is used for integration and should have similar but slightly relaxed protections:

#### Required Settings

**Require pull request reviews before merging**
- ✅ Require approvals: **1 approval minimum**
- ✅ Dismiss stale pull request approvals when new commits are pushed
- ❌ Require review from Code Owners (optional)

**Require status checks to pass before merging**
- ✅ Require branches to be up to date before merging
- ✅ Required status checks:
  - `CodeQL Security Analysis / Analyze Code (python)`
  - `CodeQL Security Analysis / Analyze Code (javascript)`
  - `Dependency Review / Review Dependencies`
  - Core tests and linting

**Additional protections**
- ✅ Require conversation resolution before merging
- ✅ Include administrators
- ✅ Allow force pushes: **Disabled**
- ✅ Allow deletions: **Disabled**

### Release Branches (`release/**`)

Release branches require protection to prevent accidental modifications:

#### Required Settings

**Require pull request reviews before merging**
- ✅ Require approvals: **1 approval minimum**

**Require status checks to pass before merging**
- ✅ All security scans must pass
- ✅ All tests must pass

**Additional protections**
- ✅ Require linear history
- ✅ Include administrators
- ✅ Allow force pushes: **Disabled**
- ✅ Allow deletions: **Disabled**

### Feature and Fix Branches (`feature/**`, `fix/**`)

Feature and fix branches typically don't need protection rules as they are short-lived and merge into protected branches.

## Configuring Branch Protection Rules

### Via GitHub Web Interface

1. Navigate to repository **Settings**
2. Click **Branches** in the left sidebar
3. Click **Add branch protection rule**
4. Enter the branch name pattern (e.g., `main`)
5. Configure the settings as outlined above
6. Click **Create** to save the rule

### Via GitHub API (for automation)

```bash
# Example: Protect main branch
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/IAmSoThirsty/Project-AI/branches/main/protection \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": [
        "CodeQL Security Analysis / Analyze Code (python)",
        "Dependency Review / Review Dependencies"
      ]
    },
    "enforce_admins": true,
    "required_pull_request_reviews": {
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": true,
      "required_approving_review_count": 1
    },
    "restrictions": null,
    "required_linear_history": false,
    "allow_force_pushes": false,
    "allow_deletions": false,
    "required_conversation_resolution": true
  }'
```

### Via GitHub CLI

```bash
# Install GitHub CLI (gh) if not already installed
# https://cli.github.com/

# Protect main branch
gh api repos/IAmSoThirsty/Project-AI/branches/main/protection \
  --method PUT \
  --field required_status_checks[strict]=true \
  --field enforce_admins=true \
  --field required_pull_request_reviews[required_approving_review_count]=1 \
  --field required_pull_request_reviews[dismiss_stale_reviews]=true \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

## Status Check Requirements

The following GitHub Actions workflows provide status checks that should be required for branch protection:

### Security Checks (Critical)
- **CodeQL Security Analysis**: Detects security vulnerabilities in Python and JavaScript code
- **Dependency Review**: Scans for vulnerable dependencies in pull requests
- **Python Dependency Audit**: Uses pip-audit to find known vulnerabilities

### Quality Checks (Important)
- **Linting**: Ensures code style compliance
- **Type Checking**: Validates type annotations (mypy for Python)
- **Tests**: Ensures all tests pass

### Integration Checks (Recommended)
- **Build Validation**: Ensures code builds successfully
- **Coverage**: Maintains test coverage thresholds

## Rulesets (GitHub's New Feature)

GitHub now offers **Rulesets** as a more flexible alternative to branch protection rules. Consider migrating to rulesets for:

- Tag protection
- More granular control
- Better inheritance across branches
- Bypass permissions management

### Example Ruleset for Security

```yaml
# .github/rulesets/security-baseline.yml
name: Security Baseline
target: branch
enforcement: active

conditions:
  ref_name:
    include:
      - "~DEFAULT_BRANCH"
      - "refs/heads/develop"
      - "refs/heads/release/**"

rules:
  - type: pull_request
    parameters:
      required_approving_review_count: 1
      dismiss_stale_reviews_on_push: true
      require_code_owner_review: true
      require_last_push_approval: true

  - type: required_status_checks
    parameters:
      strict_required_status_checks_policy: true
      required_status_checks:
        - context: "CodeQL Security Analysis / Analyze Code (python)"
        - context: "Dependency Review / Review Dependencies"

  - type: non_fast_forward
    parameters: {}

  - type: deletion
    parameters: {}
```

## Emergency Bypass Procedures

In critical situations (e.g., security hotfixes), administrators may need to bypass branch protection:

### Process
1. **Document the reason** in a GitHub issue
2. **Use bypass permissions** (if granted)
3. **Create a post-merge PR** for review
4. **Update audit logs** with justification

### Best Practices
- Use bypass sparingly and only for genuine emergencies
- Always create a follow-up PR for team review
- Document the bypass in commit messages
- Notify the team via Slack/Discord/email

## Monitoring and Compliance

### Regular Audits
- Review branch protection settings monthly
- Check for unauthorized changes using GitHub audit log
- Verify all required status checks are operational

### Audit Commands

```bash
# List all protected branches
gh api repos/IAmSoThirsty/Project-AI/branches --jq '.[] | select(.protected == true) | .name'

# Get protection details for main branch
gh api repos/IAmSoThirsty/Project-AI/branches/main/protection --jq '.'

# Check audit log for protection changes
gh api repos/IAmSoThirsty/Project-AI/events --jq '.[] | select(.type == "ProtectionRuleEvent")'
```

### Alerts
Set up GitHub Actions to alert on:
- Branch protection rule changes
- Failed required status checks
- Bypass events

## References

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Rulesets Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)
- [GitHub Status Checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)
- [Project-AI Security Policy](../SECURITY.md)

---

**Last Updated**: 2026-02-21
**Maintained By**: Project-AI Security Team
**Review Frequency**: Monthly
