# Automated Branch-to-Main PR System

## Overview

This repository implements a fully automated system for creating, reviewing, testing, and merging pull requests from all active non-main branches to the main branch. This automation ensures that all branches are kept up-to-date and integrated with minimal manual intervention.

## Architecture

The automation system consists of three interconnected workflows:

### 1. Auto-Create Branch PRs (`auto-create-branch-prs.yml`)

**Purpose**: Automatically discovers non-main branches and creates pull requests for them.

**Triggers**:

- **Daily Schedule**: Runs at 2 AM UTC every day
- **Manual Dispatch**: Can be triggered manually for all branches or a specific branch
- **Push Events**: Triggers when new branches are pushed (except main and dependabot branches)
- **PR Closure**: Re-runs after PRs are closed to check for new branches

**Process**:

1. Discovers all branches without open PRs
1. Checks each branch for merge conflicts with main
1. Identifies branches with merge conflicts and marks them for manual resolution
1. Merges main into conflict-free branches to keep them updated
1. Generates descriptive PR titles and bodies
1. Creates PRs with appropriate labels (`automated`, `auto-created`, `auto-merge`)
1. Generates summary reports

**Conflict Handling**:

- Detects merge conflicts between branch heads and the `main` branch
- Labels conflicted PRs with `conflicts` and `needs-manual-review`
- Non-conflicted PRs get `auto-merge` and `ready-for-review` labels
- Merges main into conflict-free branches (with `[skip ci]` to prevent re-triggering)

### 2. Comprehensive PR Automation (`comprehensive-pr-automation.yml`)

**Purpose**: Manages the review, testing, and merging process for all PRs (including auto-created ones).

**Triggers**:

- PR opened, synchronized, reopened, or ready for review
- Manual workflow dispatch

**Process**:

1. **Run Checks**: Executes linting (ruff), tests (pytest), and security audits
1. **Auto-Fix**: Automatically fixes linting issues if checks fail
1. **Verify Fixes**: Re-runs all checks after auto-fixes
1. **Auto-Merge**: Enables auto-merge for PRs that pass all checks
1. **Post-Merge Validation**: Validates main branch health after merge

**Key Features**:

- Auto-fixes linting issues with ruff, black, and isort
- Runs security checks with pip-audit and bandit
- Creates detailed comments on PR status
- Automatically approves PRs that pass all checks
- Enables auto-merge for approved PRs

### 3. Auto PR Handler (`auto-pr-handler.yml`)

**Purpose**: Provides additional safety checks and handles special cases (Dependabot, security PRs).

**Triggers**:

- PR opened, synchronized, or reopened

**Process**:

- Runs linting and tests
- Auto-fixes issues
- Comments on PR with results
- Approves PRs that pass checks
- Special handling for Dependabot and security PRs

## Workflow Integration

```
┌─────────────────────────────────────────────────────────────┐
│  1. Branch Discovery & PR Creation                          │
│  (auto-create-branch-prs.yml)                               │
│                                                              │
│  • Discovers branches without PRs                           │
│  • Creates PRs automatically                                │
│  • Labels: automated, auto-created, auto-merge              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  2. Automated Review & Testing                              │
│  (comprehensive-pr-automation.yml + auto-pr-handler.yml)    │
│                                                              │
│  • Runs linting (ruff)                                      │
│  • Runs tests (pytest)                                      │
│  • Security checks (pip-audit, bandit)                      │
│  • Auto-fixes issues                                        │
│  • Re-runs checks after fixes                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  3. Auto-Merge (if all checks pass)                         │
│                                                              │
│  • Approves PR                                              │
│  • Enables auto-merge                                       │
│  • Waits for branch protection requirements                 │
│  • Merges to main                                           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  4. Post-Merge Validation                                   │
│                                                              │
│  • Validates main branch health                             │
│  • Checks for conflicts                                     │
│  • Runs tests on main                                       │
│  • Generates summary report                                 │
│  • Creates alerts if issues detected                        │
└─────────────────────────────────────────────────────────────┘
```

## Labels and Their Meanings

| Label | Meaning | Applied By |
|-------|---------|------------|
| `automated` | PR created by automation | auto-create-branch-prs.yml |
| `auto-created` | PR was auto-created from branch discovery | auto-create-branch-prs.yml |
| `auto-merge` | PR is eligible for automatic merging | auto-create-branch-prs.yml |
| `ready-for-review` | PR has no conflicts and is ready for automated review | auto-create-branch-prs.yml |
| `conflicts` | PR has merge conflicts with main | auto-create-branch-prs.yml |
| `needs-manual-review` | PR requires human intervention | auto-create-branch-prs.yml |
| `security` | Security-related changes | manual or auto-security-fixes.yml |

## Manual Controls

### Trigger Auto-Creation for All Branches

```bash

# Via GitHub CLI

gh workflow run auto-create-branch-prs.yml

# Via GitHub UI

# Go to Actions → Auto-Create Branch PRs → Run workflow

```

### Trigger Auto-Creation for Specific Branch

```bash
gh workflow run auto-create-branch-prs.yml -f target_branch=feature/my-branch
```

### Trigger Comprehensive PR Automation

```bash
gh workflow run comprehensive-pr-automation.yml
```

### Disable Auto-Merge for a Specific PR

Remove the `auto-merge` label from the PR:

```bash
gh pr edit <PR_NUMBER> --remove-label "auto-merge"
```

## Branch Protection Rules

For the automation to work optimally, configure these branch protection rules for `main`:

1. **Require pull request reviews before merging**: Optional (automation provides approval)
1. **Require status checks to pass**: ✅ Required
   - Select: `lint`, `test`, `Run All Required Checks`
1. **Require branches to be up to date**: ✅ Required
1. **Allow auto-merge**: ✅ Required

## Summary Reports

The system generates several types of summary reports:

### 1. Daily Summary Issue

Created daily with:

- Number of branches discovered
- Number of PRs created
- List of created PRs with links
- Status of each PR (conflicted or ready)

### 2. Post-Merge Validation Report

Created as a comment on each merged PR with:

- Main branch health status
- Conflict detection results
- Test suite status
- Linting status

### 3. Workflow Failure Alerts

Created as issues when workflows fail:

- Timestamp of failure
- Link to failed workflow run
- Urgently labeled for quick response

## Monitoring and Maintenance

### Check Automation Status

```bash

# List recent workflow runs

gh run list --workflow=auto-create-branch-prs.yml --limit 10

# View specific run details

gh run view <RUN_ID>

# View logs

gh run view <RUN_ID> --log
```

### View Auto-Created PRs

```bash

# List all auto-created PRs

gh pr list --label "auto-created"

# List PRs with conflicts

gh pr list --label "conflicts"

# List PRs ready for merge

gh pr list --label "auto-merge"
```

### View Summary Reports

```bash

# List summary issues

gh issue list --label "summary"

# List workflow failure alerts

gh issue list --label "workflow-failure"
```

## Conflict Resolution

When the automation detects merge conflicts:

1. PR is created with `conflicts` and `needs-manual-review` labels
1. A comment is added explaining the situation
1. Manual intervention is required:

```bash

# Clone and checkout the branch

git checkout <branch-name>

# Merge main

git merge main

# Resolve conflicts manually

# ... edit files ...

# Commit and push

git add .
git commit -m "chore: resolve merge conflicts"
git push

# The PR will automatically re-run checks

```

## Troubleshooting

### PRs Not Being Created

**Check**:

1. Workflow is enabled in repository settings
1. Workflow has necessary permissions (contents: write, pull-requests: write)
1. Branch doesn't already have an open PR
1. Branch is not protected (main, dependabot branches are excluded)

### Auto-Merge Not Working

**Check**:

1. All required checks have passed
1. Branch protection rules allow auto-merge
1. PR has `auto-merge` label
1. No manual "Changes requested" reviews exist

### Checks Failing

**Check**:

1. View workflow logs: `gh run view <RUN_ID> --log`
1. Check if auto-fix ran: Look for "auto-fix" commits
1. Review test failures in pytest output
1. Check linting errors in ruff output

## Customization

### Change Schedule Frequency

Edit `.github/workflows/auto-create-branch-prs.yml`:

```yaml
schedule:

  - cron: '0 */6 * * *'  # Every 6 hours instead of daily

```

### Exclude Certain Branches

Edit the branch filtering logic in `auto-create-branch-prs.yml`:

```javascript
.filter(name => {
  if (name === 'main') return false;
  if (name.startsWith('experimental/')) return false;  // Add custom exclusions
  // ...
})
```

### Adjust Parallel Processing

Edit the `max-parallel` setting:

```yaml
strategy:
  max-parallel: 10  # Process more branches simultaneously
```

## Security Considerations

1. **Token Permissions**: Workflows use `GITHUB_TOKEN` with minimal required permissions
1. **Branch Protection**: Main branch is protected from direct pushes
1. **Security Checks**: All PRs undergo security audits (pip-audit, bandit)
1. **Approval Required**: PRs must pass all checks before merging
1. **Audit Trail**: All automation actions are logged and traceable

## Cost Considerations

- Daily runs process all branches without PRs
- Each branch triggers multiple workflow runs
- Approximate GitHub Actions minutes per day: 50-100 (for 40+ branches)
- **Free tier**: Stays within free tier limits (2000 minutes/month for public repos, 2000 minutes/month for private repos on free plan)
- **Paid accounts**: Enterprise/Team accounts have higher limits and different pricing. Check your organization's specific limits and costs at: <https://github.com/pricing>
- **Optimization tip**: Adjust the schedule frequency based on your branch activity to optimize minute usage

## Future Enhancements

Potential improvements to consider:

1. **Intelligent Scheduling**: Run more frequently for active branches
1. **Dependency-Aware Merging**: Merge in dependency order
1. **Automatic Rebase**: Rebase branches instead of merge
1. **Slack/Email Notifications**: Alert on conflicts or failures
1. **Analytics Dashboard**: Track merge velocity and success rates
1. **Automatic Branch Cleanup**: Delete merged branches after successful merge

## Support

For issues or questions:

1. Check workflow logs: `gh run view <RUN_ID> --log`
1. Review summary issues created by automation
1. Check workflow failure alerts
1. Create an issue with the `automation` label
