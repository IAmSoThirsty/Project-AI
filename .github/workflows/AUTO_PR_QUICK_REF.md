# Automated PR System - Quick Reference

## 🚀 Quick Start

The repository automatically creates and manages PRs for all non-main branches. No manual intervention needed!

## 📋 Daily Operations

### What Happens Automatically?

1. **Every Day at 2 AM UTC**: System scans for branches without PRs
2. **New PRs Created**: Automatically creates PRs for discovered branches
3. **Checks Run**: Linting, tests, and security scans execute
4. **Auto-Fix**: Issues are automatically fixed where possible
5. **Auto-Merge**: PRs passing all checks are automatically merged
6. **Reports**: Summary reports posted as issues

### What Requires Manual Action?

⚠️ **Only when conflicts exist:**

- PRs with merge conflicts get labeled `needs-manual-review`
- You'll be notified via PR comment
- Resolve conflicts, push, and automation continues

## 🏷️ Label Guide

| Label | What It Means | Your Action |
|-------|---------------|-------------|
| `auto-merge` | Will merge when checks pass | None - automatic |
| `conflicts` | Has merge conflicts | Resolve manually |
| `needs-manual-review` | Requires human attention | Review and fix |
| `automated` | Created by automation | None - informational |

## 🎛️ Manual Controls

### Create PRs for All Branches Now

```bash
gh workflow run auto-create-branch-prs.yml
```

### Create PR for Specific Branch

```bash
gh workflow run auto-create-branch-prs.yml -f target_branch=feature/my-feature
```

### Check Automation Status

```bash
# View recent runs
gh run list --workflow=auto-create-branch-prs.yml --limit 5

# View auto-created PRs
gh pr list --label "auto-created"

# View PRs needing attention
gh pr list --label "needs-manual-review"
```

### Stop Auto-Merge for Specific PR

```bash
gh pr edit <PR_NUMBER> --remove-label "auto-merge"
```

## 🔍 Monitoring

### View Summary Reports

```bash
gh issue list --label "summary" --limit 5
```

### View Alerts

```bash
gh issue list --label "workflow-failure"
```

### Check Workflow Logs

```bash
gh run view <RUN_ID> --log
```

## 🛠️ Troubleshooting

### PR Not Created?

**Check:**

- Does branch already have an open PR?
- Is branch name `main` or starts with `dependabot/`?
- Run manually: `gh workflow run auto-create-branch-prs.yml -f target_branch=YOUR_BRANCH`

### Checks Failing?

**Check:**

- View PR comments for details
- Auto-fix should run automatically
- If auto-fix fails, check workflow logs
- Fix manually and push - automation continues

### Conflicts Not Resolving?

**Manual resolution needed:**

```bash
git checkout your-branch
git merge main
# Resolve conflicts in editor
git add .
git commit -m "chore: resolve merge conflicts"
git push
```

## 📊 System Health

### Check Overall Status

```bash
# Recent workflow runs
gh run list --limit 10

# Open automated PRs
gh pr list --label "automated"

# Success rate (last 10 runs)
gh run list --workflow=auto-create-branch-prs.yml --limit 10 --json conclusion
```

## ⚙️ Configuration

### Adjust Schedule

Edit `.github/workflows/auto-create-branch-prs.yml`:

```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours
```

### Exclude Branches

Edit branch filtering in workflow:

```javascript
.filter(name => {
  if (name === 'main') return false;
  if (name.startsWith('wip/')) return false;  // Add exclusions
  // ...
})
```

## 🎯 Best Practices

1. **Let It Run**: Trust the automation for standard changes
2. **Monitor Labels**: Check `needs-manual-review` PRs daily
3. **Review Reports**: Read daily summary issues
4. **Quick Fixes**: For conflicts, fix quickly to unblock automation
5. **Test Locally**: Before pushing to branches, test locally

## 📞 Getting Help

1. **Check Logs**: `gh run view <RUN_ID> --log`
2. **View Documentation**: `.github/workflows/AUTO_PR_SYSTEM.md`
3. **Create Issue**: Use `automation` label
4. **Check Summary**: Review daily summary issues

## 🔑 Key Files

- **Main Workflow**: `.github/workflows/auto-create-branch-prs.yml`
- **Documentation**: `.github/workflows/AUTO_PR_SYSTEM.md`
- **This Guide**: `.github/workflows/AUTO_PR_QUICK_REF.md`

## 📈 Expected Results

- **~40+ branches** processed initially
- **Daily PRs created** for new branches
- **Auto-merge rate**: ~80% (conflicts require manual review)
- **Time to merge**: Minutes to hours (depending on check duration)

---

**Need more details?** See [AUTO_PR_SYSTEM.md](./AUTO_PR_SYSTEM.md)
