# CI/CD Quick Reference Card

## 🚀 Quick Start

### Deploy Optimized Workflow

```bash

# The optimized-ci-master.yml is ready to use

# Enable it by committing to your repository

git add .github/workflows/optimized-ci-master.yml
git commit -m "feat: add optimized CI/CD master workflow"
git push
```

### Monitor Workflow Health

```bash

# List recent workflow runs

gh run list --limit 10

# View specific workflow runs

gh run list --workflow=optimized-ci-master.yml

# Check cache usage

gh cache list

# View workflow logs

gh run view <run-id> --log
```

## 📊 Workflow Categories

| Type | Files | Purpose |
|------|-------|---------|
| **CI** | ci.yml, format-and-fix.yml | Code quality, testing |
| **Security** | bandit.yml, codeql.yml, security-secret-scan.yml, dependency-review.yml | Security scans |
| **Deploy** | deploy.yml, production-deployment.yml | Staging/production |
| **Auto** | stale.yml, doc-code-alignment.yml, etc. | Repository automation |
| **Build** | nextjs.yml, generate-sbom.yml | Builds and SBOM |
| **New** | **optimized-ci-master.yml** | **Optimized master pipeline** |

## ⚡ Performance Optimizations

### Enabled by Default

- ✅ **Smart change detection** (skip unchanged files)
- ✅ **Parallel job execution** (lint + test + security)
- ✅ **Aggressive caching** (pip, npm, Docker)
- ✅ **Parallel testing** (pytest-xdist)
- ✅ **Fast linting** (Ruff instead of multiple tools)
- ✅ **Concurrency groups** (cancel outdated runs)

### Expected Results

- **Before**: 8-12 minutes
- **After**: <5 minutes
- **Improvement**: 60-75% reduction

## 🔒 Security Scans (Every PR)

| Tool | Target | Runtime | Status |
|------|--------|---------|--------|
| Bandit | Python code | <1 min | ✅ |
| CodeQL | Python + JS | 2-3 min | ✅ |
| TruffleHog | Secrets | <1 min | ✅ |
| pip-audit | Dependencies | <1 min | ✅ |
| Trivy | Containers | 1-2 min | ✅ |

**Total**: <10 minutes (parallel)

## 📦 Deployment Pipeline

### Staging Deployment

```yaml

# Automatically triggered on push to main

git push origin main
```

### Production Deployment

```yaml

# Tag a release

git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Or use workflow_dispatch

gh workflow run production-deployment.yml
```

## 🛠️ Troubleshooting

### Workflow Failing?

```bash

# Check recent failures

gh run list --status failure --limit 5

# View logs for specific run

gh run view <run-id> --log-failed
```

### Cache Not Working?

```bash

# List caches

gh cache list

# Delete old caches

gh cache delete --all

# Or delete specific cache

gh cache delete <cache-id>
```

### Slow Workflow?

1. Check if change detection is working (should skip jobs)
2. Verify cache hit rates (look for "Cache restored" in logs)
3. Check for sequential job dependencies (should be parallel)
4. Review test execution time: `pytest --durations=10`

## 📈 Key Metrics to Track

| Metric | Target | Alert If |
|--------|--------|----------|
| CI Runtime | <10 min | >15 min |
| Success Rate | >95% | <90% |
| Cache Hit Rate | >80% | <60% |
| Security Scans | 0 HIGH | >0 CRITICAL |

## 🔧 Common Commands

### Workflow Management

```bash

# List all workflows

gh workflow list

# View workflow runs

gh run list --workflow=optimized-ci-master.yml

# Re-run failed jobs

gh run rerun <run-id> --failed

# Cancel running workflow

gh run cancel <run-id>

# Download artifacts

gh run download <run-id>
```

### Cache Management

```bash

# View cache size

gh cache list

# Delete cache by key

gh cache delete <cache-key>

# Delete all caches

gh cache delete --all
```

### Security Scanning

```bash

# Run Bandit locally

bandit -r src/ --severity-level high

# Run CodeQL locally (requires CodeQL CLI)

codeql database create db --language=python
codeql database analyze db --format=sarif-latest --output=results.sarif

# Run pip-audit locally

pip install pip-audit
pip-audit
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **CICD_ARCHITECTURE_REPORT.md** | Complete analysis |
| **WORKFLOW_OPTIMIZATION_GUIDE.md** | Speed improvements |
| **PIPELINE_MONITORING.md** | Health tracking |
| **CICD_EXECUTIVE_SUMMARY.md** | Executive overview |

## 🚨 Emergency Procedures

### Rollback Deployment

```bash

# Production deployment includes automatic rollback

# Manual rollback if needed:

cd k8s
./deploy.sh production rollback
```

### Disable Workflow

```bash

# Temporarily disable a workflow

gh workflow disable <workflow-id>

# Re-enable

gh workflow enable <workflow-id>
```

### Emergency Fixes

```bash

# Skip CI for emergency hotfix (use sparingly!)

git commit -m "hotfix: critical bug [skip ci]"
```

## 🎯 Best Practices

1. ✅ **Always run CI before merging**
2. ✅ **Monitor workflow execution times**
3. ✅ **Fix security findings immediately**
4. ✅ **Keep dependencies up to date**
5. ✅ **Review failed runs promptly**
6. ✅ **Use protected branches** (main, develop)
7. ✅ **Require status checks** before merge

## 📞 Support

### Issues Found?

1. Check workflow logs: `gh run view <run-id> --log`
2. Review recent changes: `git log --oneline -10`
3. Check GitHub Actions status: https://www.githubstatus.com/
4. Create issue with workflow run link

### Performance Degradation?

1. Check cache hit rates
2. Review job execution times
3. Look for sequential job dependencies
4. Verify change detection is working

## ✅ Status: PRODUCTION READY

All workflows validated and optimized. Ready for deployment.

**Last Updated**: 2026-04-10  
**Version**: 1.0  
**Architect**: CI/CD Systems Architect
