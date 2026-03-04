<!--                                         [2026-03-03 13:45] -->
<!--                                        Productivity: Active -->
# Automation Quick Reference

⚡ **Fast reference for Project-AI automated workflows**

## 🤖 What's Automated?

### Pull Requests

- ✅ **Auto-review** all PRs with lint + tests
- ✅ **Auto-approve** PRs that pass checks
- ✅ **Auto-merge** Dependabot patch/minor updates
- ✅ **Comment** with check results

### Security Scanning

- 🔍 **Daily** dependency scans (pip-audit, safety)
- 🔍 **Weekly** code scans (Bandit)
- 🔍 **Continuous** CodeQL analysis
- 🔍 **Auto-create issues** for findings
- 🔍 **Auto-fix PRs** when possible

### Dependencies

- 📦 **Daily** Python updates
- 📦 **Weekly** npm, GitHub Actions, Docker updates
- 📦 **Grouped** security updates
- 📦 **Auto-labeled** by type

## 🚀 Quick Commands

```bash

# View active workflows

gh workflow list

# Manually trigger security scan

gh workflow run auto-security-fixes.yml

# Manually trigger Bandit scan

gh workflow run auto-bandit-fixes.yml

# View recent workflow runs

gh run list --limit 10

# View Dependabot PRs

gh pr list --author "dependabot[bot]"

# View security issues

gh issue list --label security,automated

# Enable auto-merge on your PR

gh pr edit <PR-NUMBER> --add-label "auto-merge"
```

## 📊 Workflow Schedule

| Workflow | Trigger | Frequency |
|----------|---------|-----------|
| Auto PR Handler | PR events | On PR activity |
| Auto Security Fixes | Scheduled | Daily @ 2 AM UTC |
| Auto Bandit Fixes | Scheduled | Weekly (Mon @ 3 AM) |
| CodeQL | Push/PR | On code changes |
| Bandit | Push/PR | On code changes |
| CI Pipeline | Push/PR | On code changes |
| Dependabot (Python) | Scheduled | Daily @ 2 AM |
| Dependabot (npm) | Scheduled | Weekly @ 3 AM |
| Dependabot (Actions) | Scheduled | Weekly @ 4 AM |
| Dependabot (Docker) | Scheduled | Weekly @ 5 AM |

## 🔧 When to Intervene

### Auto-merge Not Working?

```bash

# Check PR status

gh pr checks <PR-NUMBER>

# Check merge eligibility

gh pr view <PR-NUMBER> --json mergeable
```

### Too Many Security Issues?

```bash

# View Bandit report locally

bandit -r src/ -f screen

# Check specific package

pip-audit --desc <package-name>
```

### Workflow Failed?

```bash

# View logs

gh run view <RUN-ID> --log

# Re-run failed jobs

gh run rerun <RUN-ID> --failed
```

## 🏷️ Labels Used

- `auto-merge` - Enable auto-merge for PR
- `security` - Security-related issue
- `automated` - Created by automation
- `dependencies` - Dependency update
- `python` - Python dependency
- `javascript` - npm dependency
- `github-actions` - GitHub Actions update
- `docker` - Docker update
- `bandit` - Bandit finding
- `codeql` - CodeQL finding

## 📂 Key Files

| File | Purpose |
|------|---------|
| `.github/workflows/auto-pr-handler.yml` | PR automation |
| `.github/workflows/auto-security-fixes.yml` | Security scanning |
| `.github/workflows/auto-bandit-fixes.yml` | Bandit scanning |
| `.github/dependabot.yml` | Dependabot config |
| `.github/AUTOMATION.md` | Full documentation |
| `.github/scripts/test-automation.sh` | Validation script |

## 🛠️ Local Testing

```bash

# Validate automation setup

./.github/scripts/test-automation.sh

# Run security scans locally

bandit -r src/ -f screen
pip-audit
safety check

# Run linting

ruff check .

# Run tests

pytest -v
```

## 📖 Full Documentation

For complete details, workflows, troubleshooting, and architecture diagrams, see:

- [.github/AUTOMATION.md](.github/AUTOMATION.md) - Complete guide
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution workflow
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Copilot context

## 🆘 Support

- 📝 **Issues**: GitHub Issues with `question` label
- 🔒 **Security**: GitHub Issues with `security` label
- 📊 **Logs**: GitHub Actions tab (90 day retention)
- 📚 **Docs**: `.github/AUTOMATION.md`

---

**Quick Access**: Bookmark this page for fast reference!
**Last Updated**: 2025-12-18
