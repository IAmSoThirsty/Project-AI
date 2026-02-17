# Automated Workflows Guide

This document describes the automated workflows configured for the Project-AI repository to handle pull requests and security alerts.

## Overview

The automation system consists of five main components:

1. **Security Orchestrator** - Comprehensive automated security resolution (NEW)
1. **Pull Request Automation** - Auto-review and merge safe PRs
1. **Security Alert Automation** - Monitor and fix security vulnerabilities
1. **Dependency Management** - Automated dependency updates via Dependabot
1. **Code Security Scanning** - Continuous security analysis

## Security Orchestrator (NEW)

### Comprehensive Security Automation (`security-orchestrator.yml`)

**Status**: ✅ ACTIVE - Zero manual approval required

**Purpose**: Complete automated security issue resolution system that handles ALL security-related items without human intervention.

**Triggers**:

- Every 6 hours (continuous monitoring)
- Manual dispatch via GitHub Actions UI
- Repository dispatch on security alerts
- Push to main (dependency changes)
- Pull requests to main

**What it does**:

1. **Comprehensive Scanning**:
   - Dependency vulnerabilities (pip-audit)
   - Code security issues (Bandit)
   - Secret exposure (detect-secrets)
   - Severity assessment and triage

1. **Automatic Remediation**:
   - Upgrades vulnerable dependencies
   - Creates tracking issues for code security
   - Alerts on secret exposure
   - Verifies all fixes applied

1. **Zero-Approval Deployment**:
   - Creates PRs with `auto-merge` label
   - Automatically merges after CI passes
   - No manual review required
   - Post-merge verification

1. **Compliance Reporting**:
   - Generates security compliance reports
   - Confirms zero outstanding issues
   - Tracks remediation history

**Key Features**:

- 🤖 Fully automated - no manual intervention
- 🔄 Continuous - runs every 6 hours
- ✅ Zero-approval - security fixes auto-merge
- 📊 Comprehensive reporting
- 🛡️ Complete coverage of security issues

**Usage**:
```bash

# Manually trigger comprehensive security scan

gh workflow run security-orchestrator.yml

# View security compliance status

gh run list --workflow=security-orchestrator.yml

# Download compliance report

gh run download <RUN-ID> -n security-compliance-report
```

**Documentation**: See `.github/SECURITY_AUTOMATION.md` for complete details.

## Pull Request Automation

### Auto PR Handler (`auto-pr-handler.yml`)

**Triggers:**

- When PRs are opened, synchronized, or reopened
- Targets PRs from `dependabot[bot]` or with `auto-merge` label

**What it does:**

1. **Auto Review**:
   - Runs linting checks with `ruff`
   - Executes test suite with `pytest`
   - Comments on PR with check results
   - Auto-approves if all checks pass

1. **Auto Merge (Dependabot)**:
   - Automatically merges patch and minor version updates
   - Requires manual review for major version updates
   - Uses squash merge strategy
   - Comments on major updates to alert maintainers

**Usage:**
```bash

# To enable auto-merge on your PR (use with caution):

gh pr edit <PR-NUMBER> --add-label "auto-merge"

# View workflow runs:

gh run list --workflow=auto-pr-handler.yml
```

## Security Alert Automation

### Auto Security Fixes (`auto-security-fixes.yml`)

**Triggers:**

- Daily at 2 AM UTC (scheduled)
- Manual dispatch via GitHub Actions UI
- Repository dispatch events

**What it does:**

1. **Dependency Scanning**:
   - Runs `pip-audit` to check for known vulnerabilities
   - Runs `safety` for additional vulnerability detection
   - Creates detailed JSON reports

1. **Issue Creation**:
   - Automatically creates GitHub issues for vulnerabilities
   - Labels: `security`, `dependencies`, `automated`
   - Includes detailed findings and remediation steps

1. **Auto-fixing**:
   - Attempts to upgrade vulnerable packages
   - Creates PRs with security fixes
   - Branch: `security/auto-fix-dependencies`

1. **CodeQL Monitoring**:
   - Checks for open CodeQL alerts
   - Creates issues for high severity findings
   - Links to specific alert details

**Reports Generated:**

- `pip-audit-report.json` - Detailed vulnerability data
- `safety-report.json` - Safety check results
- Workflow artifacts available for 90 days

**Usage:**
```bash

# Manually trigger security scan:

gh workflow run auto-security-fixes.yml

# View security issues:

gh issue list --label security,automated

# Download security reports:

gh run download <RUN-ID> -n security-reports
```

### Auto Bandit Fixes (`auto-bandit-fixes.yml`)

**Triggers:**

- Weekly on Mondays at 3 AM UTC
- Manual dispatch via GitHub Actions UI

**What it does:**

1. **Static Analysis**:
   - Scans Python code with Bandit security linter
   - Categorizes findings by severity (High/Medium/Low)
   - Generates SARIF format for GitHub Security tab

1. **Issue Creation**:
   - Creates detailed issues for security findings
   - Limits report to top 5 high and medium severity issues
   - Includes CWE IDs and file locations

1. **Report Upload**:
   - SARIF results to GitHub Security tab
   - JSON reports as workflow artifacts
   - Markdown summary with categorized findings

**Reports Generated:**

- `bandit-report.json` - Complete findings
- `bandit-report.sarif` - SARIF format for Security tab
- `bandit-summary.txt` - Quick stats
- `bandit-details.md` - Formatted detailed report

**Usage:**
```bash

# Manually trigger Bandit scan:

gh workflow run auto-bandit-fixes.yml

# View Bandit issues:

gh issue list --label security,bandit,automated

# View security alerts in browser:

gh browse --security
```

## Dependency Management

### Dependabot Configuration (`dependabot.yml`)

**Package Ecosystems Monitored:**

1. **Python (pip)** - Daily updates
   - Directory: `/`
   - Max open PRs: 10
   - Labels: `dependencies`, `python`, `automated`

1. **npm (web/frontend)** - Weekly updates
   - Directory: `/web/frontend`
   - Max open PRs: 5
   - Labels: `dependencies`, `javascript`, `automated`

1. **npm (root)** - Weekly updates
   - Directory: `/`
   - Test runners and dev tools

1. **GitHub Actions** - Weekly updates
   - Directory: `/`
   - Max open PRs: 5
   - Labels: `dependencies`, `github-actions`, `automated`

1. **Docker** - Weekly updates
   - Directory: `/`
   - Max open PRs: 3
   - Labels: `dependencies`, `docker`, `automated`

**Security Update Grouping:**
All security updates are grouped together for efficient processing.

**Commit Message Convention:**

- Prefix: `⬆️`
- Includes scope for easier changelog generation

**Usage:**
```bash

# View Dependabot PRs:

gh pr list --author "dependabot[bot]"

# Manually trigger Dependabot:

# (Not possible via CLI, use GitHub UI: Insights > Dependency graph > Dependabot)

```

## Existing Security Workflows

### CodeQL Analysis (`codeql.yml`)

- **Triggers**: Push/PR to main, cerberus-integration
- **Language**: Python
- **Action**: Uploads results to GitHub Security tab

### Bandit Security Scan (`bandit.yml`)

- **Triggers**: Push to main, PRs, weekly schedule
- **Action**: Scans for Python security issues
- **Enforcement**: Fails workflow on security findings

### CI Pipeline (`ci.yml`)

- **Matrix Testing**: Python 3.11 and 3.12
- **Checks**: Linting, type checking, tests, coverage
- **Security**: pip-audit, pre-commit hooks
- **Docker**: Build and smoke test

## Workflow Architecture

```
┌─────────────────────┐
│   Pull Request      │
│   (opened/updated)  │
└──────────┬──────────┘
           │
           ├─────────────────────┐
           │                     │
           ▼                     ▼
  ┌────────────────┐    ┌───────────────┐
  │  Auto Review   │    │  Dependabot   │
  │   - Lint       │    │  Metadata     │
  │   - Test       │    │               │
  │   - Comment    │    │               │
  └────────┬───────┘    └───────┬───────┘
           │                    │
           └──────────┬─────────┘
                      │
                      ▼
            ┌─────────────────┐
            │  Auto Approve   │
            │  (if passing)   │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Auto Merge     │
            │  (patch/minor)  │
            └─────────────────┘
```

```
┌─────────────────────┐
│   Daily/Weekly      │
│   Scheduled Scan    │
└──────────┬──────────┘
           │
           ├───────────────────┬───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐
  │  pip-audit +   │  │    Bandit      │  │    CodeQL     │
  │  safety scan   │  │  Static Scan   │  │   Analysis    │
  └────────┬───────┘  └────────┬───────┘  └───────┬───────┘
           │                   │                   │
           ├───────────────────┼───────────────────┘
           │
           ▼
  ┌────────────────────┐
  │  Create Issue      │
  │  with findings     │
  └────────┬───────────┘
           │
           ▼
  ┌────────────────────┐
  │  Attempt Auto-Fix  │
  │  (if possible)     │
  └────────┬───────────┘
           │
           ▼
  ┌────────────────────┐
  │  Create Fix PR     │
  │  for review        │
  └────────────────────┘
```

## Permissions

All automated workflows require these GitHub permissions:

- `contents: write` - To create PRs and push fixes
- `pull-requests: write` - To review and merge PRs
- `issues: write` - To create tracking issues
- `security-events: read/write` - To access and upload security data

## Best Practices

### For Developers

1. **Review Auto-Created Issues**:
   - Check for `security` and `automated` labels daily
   - Prioritize high severity findings
   - Close issues after verification

1. **Monitor Dependabot PRs**:
   - Even auto-merged PRs should be reviewed post-merge
   - Major updates require manual testing
   - Check changelog for breaking changes

1. **Use Workflow Artifacts**:
   - Download detailed reports for complex issues
   - Share JSON reports with security team if needed
   - Archive reports for compliance

1. **Manual Intervention**:
   - Use `auto-merge` label sparingly
   - Disable auto-merge by removing label if concerns arise
   - Comment on auto-created issues with additional context

### For Maintainers

1. **Workflow Configuration**:
   - Adjust scan schedules in workflow files if needed
   - Modify PR limits in `dependabot.yml` based on team capacity
   - Update reviewer lists in `dependabot.yml`

1. **Security Thresholds**:
   - Configure severity levels in Bandit workflow
   - Adjust CodeQL query suites if false positives occur
   - Fine-tune pip-audit filters

1. **Monitoring**:
   - Check GitHub Actions usage monthly
   - Review security tab regularly
   - Set up notifications for security issues

## Troubleshooting

### Workflows Not Running

**Check:**

- Workflow permissions in repository settings
- Branch protection rules not blocking auto-merge
- Required secrets are configured (if any)

**Fix:**
```bash

# View workflow status:

gh workflow view auto-pr-handler.yml

# View recent runs:

gh run list --workflow=auto-pr-handler.yml --limit 10

# View specific run logs:

gh run view <RUN-ID> --log
```

### Auto-Merge Not Working

**Common Issues:**

1. Branch protection requires reviews (expected for major updates)
1. Status checks not passing
1. Workflow permissions insufficient

**Check Status:**
```bash

# View PR checks:

gh pr checks <PR-NUMBER>

# View PR merge eligibility:

gh pr view <PR-NUMBER> --json mergeable,mergeStateStatus
```

### Security Scans Finding Too Many Issues

**Options:**

1. Create `.bandit` config to exclude false positives
1. Add `# nosec` comments for known safe code
1. Adjust severity thresholds in workflow files
1. Configure skip lists for specific tests

### Dependabot PRs Not Created

**Check:**

1. `dependabot.yml` syntax is valid
1. Package ecosystem is supported
1. Open PR limit not reached
1. Dependencies are actually outdated

**Validate Config:**
```bash

# Validate YAML syntax:

python3 -c "import yaml; yaml.safe_load(open('.github/dependabot.yml'))"

# View Dependabot alerts:

gh api repos/:owner/:repo/dependabot/alerts
```

## Maintenance

### Regular Tasks

**Weekly:**

- Review auto-created security issues
- Check Dependabot PR merge success rate
- Verify workflow execution times

**Monthly:**

- Review GitHub Actions usage and costs
- Update workflow configurations if needed
- Clean up old workflow artifacts

**Quarterly:**

- Audit security scan findings trends
- Update documentation
- Review and update excluded patterns

### Updating Workflows

When modifying workflows:

1. Test changes in a fork first
1. Validate YAML syntax
1. Check permissions are adequate
1. Monitor first few runs after deployment
1. Document changes in commit messages

## Integration with Development Process

### Pre-Commit

```bash

# Install pre-commit hooks (recommended):

pre-commit install

# Run manually:

pre-commit run --all-files
```

### Local Security Scanning

```bash

# Run Bandit locally before pushing:

bandit -r src/ -f screen

# Run pip-audit locally:

pip-audit

# Run safety check:

safety check
```

### CI/CD Pipeline

The automated workflows complement the existing CI pipeline:

1. CI runs on every push/PR (fast feedback)
1. Security scans run on schedule (comprehensive checks)
1. Dependabot runs daily/weekly (proactive updates)
1. Auto-merge activates post-CI success (efficiency)

## Support and Questions

- **Documentation**: Check `.github/copilot-instructions.md`
- **Issues**: Create issue with `question` label
- **Workflow Logs**: Available in Actions tab for 90 days
- **Security Concerns**: Create issue with `security` label

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [pip-audit Documentation](https://github.com/pypa/pip-audit)

---

**Last Updated**: 2025-12-18
**Maintained By**: Project-AI Team
