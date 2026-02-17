# Automated Issue Management System

## Overview

The Project-AI repository now includes a comprehensive automated issue management system that handles triage, categorization, labeling, assignment, resolution, and closure of issues without manual intervention.

## Features

### 1. Automatic Issue Triage

Every new issue is automatically:

- **Categorized** into one of: security, bug, feature, documentation, or other
- **Labeled** with appropriate tags based on content analysis
- **Prioritized** as high, medium, or low priority
- **Commented** with triage information for transparency

### 2. Automatic Issue Resolution

The system attempts to automatically resolve issues when possible:

- **Security Issues**: Creates PRs to update vulnerable dependencies
- **False Positives**: Identifies and closes issues created by buggy workflows
- **Documentation Issues**: Attempts to fix simple documentation problems
- **Duplicate Issues**: Detects and closes duplicate issues

### 3. Automatic Issue Closing

Issues are automatically closed when:

- **Stale**: No activity for 30+ days (configurable, with exemptions)
- **False Positive**: Security scans reporting incorrect information
- **Duplicate**: Same issue already exists
- **Resolved**: Fix has been merged and verified

### 4. Monitoring and Reporting

The system provides:

- **Daily Summary Reports**: Statistics on open/closed issues
- **Category Breakdown**: Issues grouped by type
- **Priority Analysis**: Distribution of issue priorities
- **Resolution Metrics**: Time to resolution, auto-resolution rate

## Workflows

### Auto Issue Triage and Resolution (`auto-issue-triage.yml`)

**Triggers:**

- When issues are opened, reopened, or labeled
- Daily at 3 AM UTC (scheduled)
- Manual dispatch via GitHub Actions UI

**Actions:**

1. Fetches all open issues
1. Analyzes each issue's title and body
1. Detects category (security, bug, feature, documentation)
1. Determines priority (high, medium, low)
1. Applies appropriate labels
1. Identifies false positives and stale issues
1. Closes issues that should be auto-resolved
1. Adds triage comments for transparency
1. Generates summary report

**False Positive Detection:**
The system specifically detects security reports that incorrectly show "0 vulnerability(ies)" for all packages, which indicates a workflow bug rather than a real security scan result.

### Auto Security Fixes (`auto-security-fixes.yml`)

**Enhanced with Bug Fixes:**

- Now correctly counts actual vulnerabilities before creating issues
- Only reports packages that have vulnerabilities (not all packages)
- Includes fix versions in issue descriptions
- Provides detailed vulnerability information

**Workflow Fix Applied:**

- ✅ Only creates issues when vulnerabilities are actually found
- ✅ Filters to show only packages with vulnerabilities
- ✅ Includes CVE IDs and fix versions
- ✅ Prevents false positive reports

## Configuration

The automated system is configured via `.github/issue-automation-config.yml`:

### Key Configuration Options

```yaml

# Enable/disable the entire system

enabled: true

# Auto-labeling

auto_labeling:
  enabled: true

# Auto-closing

auto_closing:
  enabled: true
  stale_issues:
    days_inactive: 30
    warning_days: 7

# Auto-resolution

auto_resolution:
  enabled: true
  dependency_updates:
    enabled: true
    create_pr: true
```

### Customization

You can customize:

- **Keywords** for category detection
- **Labels** applied to each category
- **Priority levels** for different issue types
- **Stale issue threshold** (days)
- **Auto-assignment rules** (when team is configured)
- **Notification preferences**
- **Resolution strategies**

## Usage

### For Users Creating Issues

1. **Create an issue normally** - The system will automatically triage it
1. **Wait for triage comment** - The bot will categorize and label your issue
1. **Check for auto-resolution** - Simple issues may be auto-resolved with a PR
1. **Monitor for updates** - The system tracks progress automatically

### For Maintainers

#### Viewing Status

```bash

# View all open issues by label

gh issue list --label security
gh issue list --label bug
gh issue list --label enhancement

# View recently auto-closed issues

gh issue list --state closed --label automated

# View workflow runs

gh run list --workflow=auto-issue-triage.yml
```

#### Manual Triggering

```bash

# Trigger manual triage run

gh workflow run auto-issue-triage.yml

# Trigger security scan

gh workflow run auto-security-fixes.yml
```

#### Monitoring Reports

The system generates summary reports in GitHub Actions:

1. Go to **Actions** tab
1. Select **Auto Issue Triage and Resolution** workflow
1. Click on the latest run
1. View **Summary** section for statistics

### Disabling Automation

To temporarily disable:

```yaml

# In .github/issue-automation-config.yml

enabled: false
```

Or remove the workflow file:
```bash
rm .github/workflows/auto-issue-triage.yml
```

## Issue Categories

### Security Issues

- **Keywords**: security, vulnerability, CVE, exploit
- **Labels**: `security`, `dependencies`, `automated`
- **Priority**: High
- **Auto-resolution**: Yes (creates PRs to update dependencies)

### Bug Reports

- **Keywords**: bug, error, issue, problem, broken
- **Labels**: `bug`
- **Priority**: Medium
- **Auto-resolution**: Attempted for simple cases

### Feature Requests

- **Keywords**: feature, enhancement, request, improve
- **Labels**: `enhancement`
- **Priority**: Low
- **Auto-resolution**: No (requires design discussion)

### Documentation Issues

- **Keywords**: documentation, docs, readme, guide
- **Labels**: `documentation`
- **Priority**: Low
- **Auto-resolution**: Yes (for simple fixes)

## Resolution Strategies

### Security Issues

1. **Vulnerability Detection**: System checks pip-audit and safety reports
1. **Package Identification**: Identifies packages with vulnerabilities
1. **Fix Availability**: Checks for available fixed versions
1. **PR Creation**: Creates PR to update vulnerable packages
1. **Testing**: Runs tests on the PR
1. **Auto-merge**: Optional, based on configuration
1. **Issue Closure**: Closes original issue when fix is merged

### False Positive Issues

1. **Detection**: Analyzes issue body for "0 vulnerability(ies)" pattern
1. **Verification**: Checks if 80%+ of packages show 0 vulnerabilities
1. **Immediate Closure**: Closes issue with explanation
1. **Label Application**: Adds `false-positive` and `automated` labels
1. **Comment**: Explains why it was closed

### Stale Issues

1. **Age Check**: Identifies issues >30 days old
1. **Label Application**: Adds `stale` label
1. **Warning Period**: 7-day warning before closure
1. **Exemptions**: Security and critical issues never stale
1. **Closure**: Closes with reopen instructions

## Integration with Existing Workflows

The automated issue management system works alongside:

- **Dependabot**: Issues from Dependabot are automatically triaged
- **CodeQL**: Security alerts are automatically processed
- **Bandit**: Static analysis findings are tracked
- **CI/CD**: Test results influence auto-resolution decisions

## Metrics and Reporting

The system tracks:

- **Time to Triage**: How quickly issues are categorized
- **Time to Resolution**: How long it takes to resolve issues
- **Auto-resolution Rate**: Percentage of issues auto-resolved
- **False Positive Rate**: How many issues are false alarms
- **Category Distribution**: Breakdown of issue types
- **Priority Distribution**: High/medium/low issue counts

### Example Summary Report

```
📊 Issue Management Summary

Total Open Issues: 5
Issues Closed Today: 1

Open Issues by Category

- security: 2
- bug: 1
- enhancement: 2
- documentation: 0

Report generated at 2026-01-07T03:00:00Z
```

## Troubleshooting

### Issue Not Auto-Triaged

**Check:**

1. Workflow permissions are correct
1. Issue was created after workflow deployment
1. Issue is not a pull request

**Solution:**
```bash

# Manually trigger triage

gh workflow run auto-issue-triage.yml
```

### False Positive Not Detected

**Check:**

1. Issue body contains "0 vulnerability(ies)" text
1. At least 10 packages are listed
1. 80%+ show 0 vulnerabilities

**Solution:**
Manually close with label `false-positive`

### Security Issues Not Auto-Resolved

**Check:**

1. Fix versions available for vulnerabilities
1. Auto-resolution enabled in config
1. Tests pass on fix PR

**Solution:**
Check workflow logs for errors in dependency update step

## Best Practices

### For Issue Reporters

1. **Clear Titles**: Use descriptive titles with keywords
1. **Detailed Descriptions**: Include reproduction steps, error messages
1. **Labels**: The system will add labels, but you can add custom ones
1. **Check for Duplicates**: Search before creating new issues

### For Maintainers

1. **Review Auto-Closed Issues**: Periodically check auto-closed issues
1. **Tune Configuration**: Adjust thresholds based on project needs
1. **Monitor Metrics**: Track false positive and resolution rates
1. **Exempt Important Issues**: Use labels to prevent auto-closure
1. **Update Keywords**: Add project-specific keywords to config

## Security Considerations

- **Automated Fixes**: Security fixes create PRs for review, not direct commits
- **Test Coverage**: All auto-resolution PRs must pass tests
- **Human Oversight**: High-severity issues are flagged for manual review
- **Audit Trail**: All automated actions are logged and commented
- **Rollback**: Manual intervention can override any automated decision

## Support and Questions

- **Configuration Issues**: Check `.github/issue-automation-config.yml`
- **Workflow Errors**: View logs in Actions tab
- **Feature Requests**: Create issue with `enhancement` label
- **Bug Reports**: Create issue with `bug` label

## Version History

### v1.0.0 (2026-01-07)

- Initial release
- Automated triage and categorization
- False positive detection
- Stale issue handling
- Security workflow bug fixes
- Comprehensive configuration system

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Issues API](https://docs.github.com/en/rest/issues)
- [Repository Automation Documentation](.github/AUTOMATION.md)

---

**Last Updated**: 2026-01-07
**System Status**: ✅ Active
**Current Version**: 1.0.0
