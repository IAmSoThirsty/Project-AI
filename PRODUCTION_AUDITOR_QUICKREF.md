# Production Auditor Quick Reference

## One-Liner Commands

```bash
# Full audit with report
python -m app.agents.production_auditor

# Quick go/no-go check
python -m app.agents.production_auditor --quick

# JSON output for CI/CD
python -m app.agents.production_auditor --json > audit-result.json

# Audit different project
python -m app.agents.production_auditor --project-root /path/to/project
```

## Exit Codes

- `0` - Deployment ready (no blockers)
- `1` - Deployment blocked (fix issues first)

## 12-Point Checklist

| # | Category | Critical Checks |
|---|----------|----------------|
| 1 | Runtime Startup | Main entry point exists, no hardcoded values |
| 2 | Docker Container | Non-root user, HEALTHCHECK present |
| 3 | Health Endpoints | `/health`, `/ready`, `/live` with real checks |
| 4 | Env Vars & Secrets | `.env` gitignored, no hardcoded keys |
| 5 | Logging & Audit | Acceptance ledger exists, audit.log present |
| 6 | Error Handling | Fail-closed behavior, exceptions raised |
| 7 | Dependency Pinning | All packages pinned with `==` |
| 8 | CI Gates | Test, lint, security workflows present |
| 9 | Test Coverage | Tests for critical paths exist |
| 10 | Evidence Manifest | Coverage reports, CI reports, audit logs |
| 11 | Release Consistency | Version file, CHANGELOG.md |
| 12 | Governance Enforcement | No theater, real blocking, 5/5 invariants |

## Severity Levels

- **CRITICAL** - Blocks deployment
- **HIGH** - Fix before production
- **MEDIUM** - Recommended improvement
- **LOW** - Nice to have

## Governance Theater Patterns (Auto-Detected)

```python
# ❌ BLOCKED - Logs but doesn't enforce
logger.info("BLOCK: Action denied")
return True

# ❌ BLOCKED - Silent failure
except Exception:
    pass

# ❌ BLOCKED - Fake health check
return {"status": "healthy"}, 200
```

## Python API

```python
from app.agents.production_auditor import ProductionAuditor

# Full audit
auditor = ProductionAuditor(project_root=".")
result = auditor.audit_production_readiness()

if result['deployment_ready']:
    print("✅ DEPLOY")
else:
    for blocker in result['blockers']:
        print(f"❌ {blocker['check']}: {blocker['message']}")

# Quick check
quick = auditor.verify_deployment_readiness()
print(quick['recommendation'])  # "DEPLOY" or "FIX BLOCKERS FIRST"
```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Production Readiness Audit
  run: |
    python -m app.agents.production_auditor --json > audit.json
    python -m app.agents.production_auditor --quick
  continue-on-error: false  # Fail build if not ready
```

### Pre-Deployment Gate

```bash
#!/bin/bash
# pre-deploy.sh

if python -m app.agents.production_auditor --quick; then
    echo "✅ Deployment approved"
    exit 0
else
    echo "❌ Deployment blocked - see PRODUCTION_AUDIT_REPORT.md"
    exit 1
fi
```

## Common Fixes

### Fix: Container runs as root
```dockerfile
# Add to Dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### Fix: Unpinned dependencies
```bash
# Pin all packages
pip freeze > requirements.txt
```

### Fix: Missing health endpoint
```python
# Add to triumvirate_server.py
@app.route("/health")
def health():
    redis_ok = redis.ping()
    kernel_ok = kernel.is_alive()
    return {"status": "healthy" if all([redis_ok, kernel_ok]) else "unhealthy"}
```

### Fix: Governance theater
```python
# BEFORE (theater)
logger.info("BLOCK: Action denied")
return True

# AFTER (enforcement)
logger.error("BLOCK: Action denied")
raise Exception("Action blocked by governance")
```

## Verification After Fixes

```bash
# 1. Run canonical replay
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 canonical/replay.py

# 2. Run tests
pytest -v --cov=src/app/core --cov-report=html

# 3. Security scan
bandit -r src/ -f json -o ci-reports/bandit.json

# 4. Re-audit
python -m app.agents.production_auditor --quick
```

## Report Location

- **Generated Report:** `PRODUCTION_AUDIT_REPORT.md` (project root)
- **Includes:** Blockers, warnings, verification commands, evidence checklist

## Support

- **Documentation:** `src/app/agents/PRODUCTION_AUDITOR.md`
- **Tests:** `tests/test_production_auditor.py`
- **Source:** `src/app/agents/production_auditor.py`

---

**Principle:** Explicit failure over misleading success.
