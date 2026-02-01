# 🏛️ Codex Deus Ultimate - Quick Reference

## At a Glance

**File:** `.github/workflows/codex-deus-ultimate.yml`  
**Lines:** 2,507  
**Jobs:** 55  
**Phases:** 15

---

## Quick Commands

### Trigger Manually
```bash
# Run full workflow
gh workflow run codex-deus-ultimate.yml

# Run only security phase
gh workflow run codex-deus-ultimate.yml -f run_phase=security

# Run only testing phase
gh workflow run codex-deus-ultimate.yml -f run_phase=testing

# Force release build
gh workflow run codex-deus-ultimate.yml -f force_release=true

# Skip tests
gh workflow run codex-deus-ultimate.yml -f skip_tests=true

# Custom coverage threshold
gh workflow run codex-deus-ultimate.yml -f coverage_threshold=85

# High severity only
gh workflow run codex-deus-ultimate.yml -f severity_threshold=high
```

### View Workflow Status
```bash
# List recent runs
gh run list --workflow=codex-deus-ultimate.yml

# View specific run
gh run view <run-id>

# Watch live
gh run watch

# View logs
gh run view <run-id> --log
```

### Download Artifacts
```bash
# List artifacts from run
gh run view <run-id> --json artifacts

# Download specific artifact
gh run download <run-id> -n python-test-reports-3.12-ubuntu-latest

# Download all artifacts
gh run download <run-id>
```

---

## Phase Overview

| Phase | Jobs | Key Actions |
|-------|------|-------------|
| 1. Initialization | 1 | Smart detection, execution plan |
| 2. Security Scanning | 4 | CodeQL, Bandit, Secrets, Dependencies |
| 3. AI Safety | 2 | JBB, Garak, model scanning |
| 4. Code Quality | 6 | Ruff, MyPy, Black, Super-Linter |
| 5. Testing | 6 | Python (matrix), Node, CLI, Integration, E2E |
| 6. Coverage | 1 | Enforce 80% Python, 75% JS |
| 7. Build | 4 | Wheel, Docker, Android, Desktop |
| 8. SBOM | 2 | Syft generation + Grype scanning |
| 9. Container Security | 4 | Trivy (3x), Checkov |
| 10. Auto-Fix | 3 | Lint fixes, dependency upgrades, issues |
| 11. PR Automation | 6 | Label, review, merge, triage, stale |
| 12. Release | 6 | Package, sign, publish (PyPI, Docker, GitHub) |
| 13. Post-Merge | 2 | Health check, conflict detection |
| 14. Cleanup | 3 | Artifacts, cache, repository |
| 15. Reporting | 4 | Summary, badges, metrics, notification |

---

## Trigger Patterns

### Automatic Triggers
- **Push** to main/develop/cerberus-integration/feature/*/fix/*/release/*
- **Pull Request** to main/develop/cerberus-integration
- **Release** published/created
- **Tag** v*.*.*
- **Schedule**: Every 6h (security), Daily 2AM/3AM, Weekly Sun 5AM, Weekly Mon 3AM
- **Issues** opened/labeled/reopened/edited/closed

### What Gets Skipped
- Markdown files (*.md)
- docs/ directory
- LICENSE files
- .gitignore

---

## Job Status Quick Check

```bash
# Check if specific phase succeeded
gh run view <run-id> --json jobs --jq '.jobs[] | select(.name | contains("Security")) | {name, conclusion}'

# Count failed jobs
gh run view <run-id> --json jobs --jq '[.jobs[] | select(.conclusion == "failure")] | length'

# List skipped jobs
gh run view <run-id> --json jobs --jq '.jobs[] | select(.conclusion == "skipped") | .name'
```

---

## Common Scenarios

### PR Gets Auto-Approved ✅
**Conditions:**
1. All tests pass
2. Linting passes
3. Security scans pass
4. PR not from fork

**Jobs:**
- `pr-auto-review` posts approval comment

### Dependabot PR Gets Auto-Merged 🤖
**Conditions:**
1. PR from dependabot[bot]
2. All tests pass
3. Security scans pass
4. Patch or minor version update

**Jobs:**
- `dependabot-auto-merge` auto-merges PR

### Linting Failures Get Fixed 🔧
**Conditions:**
1. Linting fails on PR
2. PR from same repo (not fork)

**Jobs:**
- `auto-fix-linting` runs Ruff --fix, Black, isort
- Commits fixes to PR branch

### Release Gets Published 🚀
**Conditions:**
1. Tag pushed (v*.*.*)
2. All tests/builds pass

**Jobs:**
1. `prepare-release` - Extract version, generate notes
2. `package-release` - Build for Linux/Windows/macOS
3. `sign-artifacts` - Cosign signing
4. `create-github-release` - Create GitHub Release
5. `publish-pypi` - Publish to PyPI
6. `publish-docker` - Push to ghcr.io

---

## Artifact Locations

### After Tests
- `python-test-reports-*` - JUnit XML + coverage
- `ruff-lint-reports` - Ruff JSON
- `mypy-type-reports` - Type checking

### After Security Scans
- `bandit-security-reports` - Bandit JSON/SARIF
- `secret-scanning-reports` - detect-secrets baseline
- `dependency-security-reports` - pip-audit + Safety

### After Builds
- `python-wheels` - .whl files
- `android-apk` - .apk files
- `desktop-build-*` - Platform executables

### After Release
- `sbom-files` - SPDX/CycloneDX + signatures
- `signed-release-artifacts` - All signed release files

### Reporting
- `status-badges` - Badge JSON
- `workflow-metrics` - Metrics dashboard

---

## Environment Variables

```bash
# Python
PYTHON_VERSION=3.12
PYTHON_VERSION_MATRIX=["3.11", "3.12"]

# Node
NODE_VERSION=20

# Java
JAVA_VERSION=17

# Go
GO_VERSION=1.21

# Thresholds
COVERAGE_THRESHOLD_PYTHON=80
COVERAGE_THRESHOLD_JS=75
SECURITY_SEVERITY_THRESHOLD=medium
```

---

## Conditional Logic

### Jobs Run When...

| Job | Condition |
|-----|-----------|
| Security scans | `should_run_security == 'true'` |
| AI adversarial tests | `has_ai_changes == 'true'` |
| Python tests | `should_run_tests == 'true'` |
| Node tests | `should_run_node == 'true'` |
| Docker build | `should_run_docker == 'true'` |
| Release jobs | `is_release == 'true'` |
| Auto-fix linting | Previous linting failed + PR event |
| Auto-fix deps | Scheduled (daily 3 AM) |
| Dependabot merge | PR from dependabot[bot] + tests pass |
| Post-merge check | Push to main |
| Cleanup jobs | Scheduled (weekly Sunday 5 AM) |

---

## Troubleshooting

### Workflow Didn't Run
1. Check branch name matches trigger patterns
2. Verify files changed not in `paths-ignore`
3. Check concurrency group (may have cancelled)

### Job Was Skipped
1. Check `if:` condition
2. Verify `needs:` dependencies succeeded
3. Review initialization outputs

### Tests Failed
1. Check test logs in job output
2. Download `python-test-reports-*` artifact
3. Review JUnit XML for details

### Security Scan Failed
1. Check SARIF uploads in Security tab
2. Download security report artifacts
3. Review specific tool output (Bandit/Trivy/etc)

### Release Didn't Publish
1. Verify tag format: `v1.2.3`
2. Check `prepare-release` job for version detection
3. Ensure all dependency jobs succeeded
4. Verify PyPI/Docker credentials configured

---

## Monitoring

### View Workflow Health
```bash
# Success rate last 10 runs
gh run list --workflow=codex-deus-ultimate.yml --limit 10 --json conclusion --jq '[.[] | .conclusion] | group_by(.) | map({conclusion: .[0], count: length})'

# Average duration
gh run list --workflow=codex-deus-ultimate.yml --limit 10 --json duration --jq '[.[].duration] | add / length / 60 | floor'

# Failed jobs last run
gh run view --json jobs --jq '.jobs[] | select(.conclusion == "failure") | .name'
```

### Check Security Status
```bash
# Open security alerts
gh api repos/:owner/:repo/code-scanning/alerts --jq 'length'

# Dependabot alerts
gh api repos/:owner/:repo/dependabot/alerts --jq 'length'
```

---

## Maintenance

### Update Python Version
1. Edit `env.PYTHON_VERSION: '3.12'`
2. Edit `env.PYTHON_VERSION_MATRIX: '["3.11", "3.12"]'`
3. Update composite action default if needed

### Change Coverage Threshold
1. Edit `env.COVERAGE_THRESHOLD_PYTHON: 80`
2. Or pass via workflow_dispatch input

### Add New Job
1. Add job definition under appropriate phase
2. Set `needs:` for dependencies
3. Add conditional `if:` based on initialization
4. Set `timeout-minutes`
5. Update Phase 15 reporting to include new job

### Temporarily Disable Job
```yaml
job-name:
  if: false  # Disable temporarily
```

---

## Best Practices

### For Contributors
1. Create PRs - workflow auto-validates
2. Wait for auto-approval if all gates pass
3. Review auto-fix commits if linting fails
4. Check coverage report in PR comments

### For Maintainers
1. Monitor workflow health weekly
2. Review stale issue/PR cleanup
3. Check security alerts from automated scans
4. Update dependencies from auto-fix PRs
5. Review release artifacts before publishing

### For Security
1. Check Security tab for SARIF uploads
2. Review dependency audit results
3. Monitor scheduled security scans
4. Triage auto-created security issues

---

## Quick Links

- **Workflow File:** `.github/workflows/codex-deus-ultimate.yml`
- **Summary Doc:** `CODEX_DEUS_ULTIMATE_SUMMARY.md`
- **Composite Actions:** `.github/actions/*/action.yml`
- **GitHub Actions:** https://github.com/PROJECT/actions/workflows/codex-deus-ultimate.yml

---

**Version:** 1.0.0  
**Last Updated:** 2024  
**Status:** Production Ready ✅

