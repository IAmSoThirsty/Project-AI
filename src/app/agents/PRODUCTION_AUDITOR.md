# Production Readiness Auditor Agent

## Overview

The **Production Readiness Auditor** is an uncompromising agent that validates Project-AI's deployment readiness across 12 critical dimensions. It enforces production standards without accepting shortcuts that weaken governance.

## Mission

Audit Project-AI for production deployment readiness while ensuring:
- Governance enforcement is real, not theater
- Dependencies are actually checked, not just logged as "healthy"
- Evidence artifacts prove production-worthiness
- Security and reliability standards are met

## Core Principles

1. **Explicit Failure Over Misleading Success**
   - Prefer blocking deployment with clear errors over allowing deployment with hidden issues
   - Reject "status: healthy" responses that don't verify dependencies

2. **Real Evidence, Not Simulated**
   - Require actual test coverage reports, not test file counts
   - Verify canonical replay passes 5/5 invariants, not just exists
   - Demand real audit trails, not empty directories

3. **No Governance Shortcuts**
   - Detect and block "governance theater" (logging without enforcement)
   - Ensure fail-closed behavior in error handling
   - Verify OctoReflex enforcement levels actually enforce

## Audit Categories (12 Checks)

### 1. Runtime Startup
- ✅ Main entry point exists (`src/app/main.py`)
- ⚠️ No hardcoded localhost/IP addresses
- ⚠️ No unvalidated environment variable access

**Blocker Severity:** CRITICAL if missing entry point

### 2. Docker Container
- ✅ Dockerfile exists with proper structure
- ✅ HEALTHCHECK instruction present
- ✅ Runs as non-root user (not `USER root`)
- ⚠️ `.dockerignore` present

**Blocker Severity:** CRITICAL if running as root

### 3. Health Endpoints
- ✅ `/health` endpoint implemented
- ✅ `/ready` endpoint implemented
- ✅ `/live` endpoint implemented
- ✅ Endpoints check dependencies (Redis, kernel, invariants), not just return 200

**Blocker Severity:** CRITICAL if missing or theater

### 4. Environment Variables & Secrets
- ✅ `.env` in `.gitignore`
- ⚠️ `.env.example` template exists
- ✅ No hardcoded API keys in critical paths
- ✅ No hardcoded secrets (regex scan)

**Blocker Severity:** CRITICAL if secrets exposed or `.env` not ignored

### 5. Logging & Audit
- ⚠️ `audit.log` exists
- ✅ `data/acceptance_ledger/` directory exists
- ⚠️ Logging configuration (logging.yaml, pyproject.toml)

**Blocker Severity:** CRITICAL if acceptance ledger missing

### 6. Error Handling
- ✅ ExecutionGate has fail-closed behavior
- ✅ Exceptions are raised, not silently caught
- ⚠️ No `except: pass` patterns

**Blocker Severity:** CRITICAL if fail-open behavior detected

### 7. Dependency Pinning
- ✅ `requirements.txt` or `pyproject.toml` exists
- ✅ All dependencies pinned to exact versions (`==`)
- ❌ No unpinned packages (e.g., `requests` without version)

**Blocker Severity:** CRITICAL if unpinned dependencies

### 8. CI Gates
- ✅ GitHub workflows exist (`.github/workflows/`)
- ✅ Test workflow with pytest
- ✅ Security scanning (Bandit, pip-audit, safety)
- ⚠️ Linting and type checking

**Blocker Severity:** CRITICAL if no tests or security scans

### 9. Test Coverage
- ✅ Test directory exists (`tests/`)
- ✅ Test files present (`test_*.py`)
- ✅ Tests for critical paths (ExecutionGate, OctoReflex, InvariantEngine)
- ⚠️ Coverage reports (`test-artifacts/coverage/`)

**Blocker Severity:** CRITICAL if missing tests for critical components

### 10. Evidence Manifest
- ✅ All required artifacts present:
  - `test-artifacts/coverage/`
  - `ci-reports/`
  - `audit.log`
  - `data/governance_drift_alerts/`
  - `data/acceptance_ledger/`
- ✅ `canonical/replay.py` exists and executes successfully

**Blocker Severity:** CRITICAL if evidence missing

### 11. Release Consistency
- ⚠️ Version file exists (VERSION, `__version__.py`)
- ⚠️ CHANGELOG.md maintained

**Blocker Severity:** WARNING (not blocking)

### 12. Governance Enforcement
- ✅ ExecutionGate blocks actions, not just logs
- ✅ OctoReflex implements all enforcement levels (WARN, BLOCK, TERMINATE, ESCALATE)
- ✅ Canonical scenario defines 5 invariants
- ❌ No governance theater patterns (logging without action)

**Blocker Severity:** CRITICAL if theater detected

## Usage

### Basic Audit

```python
from app.agents.production_auditor import ProductionAuditor

auditor = ProductionAuditor(project_root=".")
result = auditor.audit_production_readiness()

print(f"Score: {result['score']:.1f}%")
print(f"Status: {result['status']}")
print(f"Blockers: {len(result['blockers'])}")
print(f"Ready: {result['deployment_ready']}")
```

### Quick Verification

```python
# Quick go/no-go check
result = auditor.verify_deployment_readiness()

if result['ready']:
    print("✅ DEPLOY")
else:
    print(f"❌ FIX {result['blocker_count']} BLOCKERS FIRST")
```

### Command Line

```bash
# Run full audit with report
python -m app.agents.production_auditor

# Generated report: PRODUCTION_AUDIT_REPORT.md
```

## Output

### Audit Result Structure

```python
{
    "timestamp": "2026-05-13T18:51:16.191Z",
    "score": 91.7,  # 0-100
    "status": "READY" | "BLOCKED",
    "blockers": [
        {
            "check": "Docker Container",
            "severity": "CRITICAL",
            "message": "Container runs as root user",
            "fix": "Add non-root user and switch with USER instruction"
        }
    ],
    "warnings": [
        {
            "check": "Health Endpoints",
            "severity": "HIGH",
            "message": "Endpoint /health returns status without checking dependencies",
            "recommendation": "Implement real dependency checks (Redis, kernel, invariants)"
        }
    ],
    "evidence": {
        "runtime_startup": {"main_entry": "src/app/main.py", "exists": true},
        "docker": {"dockerfile_exists": true, "has_healthcheck": true},
        # ... more evidence
    },
    "deployment_ready": false
}
```

### Generated Report (`PRODUCTION_AUDIT_REPORT.md`)

The report includes:
1. **Summary** - Score, status, blocker/warning counts
2. **Deployment Readiness Checklist** - Go/no-go criteria
3. **Current Production Blockers** - Critical issues with fixes
4. **Verification Commands** - Shell commands to verify fixes
5. **Evidence Artifacts Required** - Checklist of proof artifacts
6. **Detailed Findings** - All warnings and recommendations
7. **Evidence Summary** - JSON dump of all collected evidence

## Governance Theater Detection

The auditor specifically scans for anti-patterns:

### Pattern 1: Logging Without Enforcement
```python
# ❌ THEATER - Detected and blocked
logger.info("BLOCK: Action denied")
return True  # Still allows action

# ✅ CORRECT - Enforces
logger.info("BLOCK: Action denied")
raise Exception("Action blocked by governance")
```

### Pattern 2: Silent Exception Handling
```python
# ❌ THEATER - Detected and blocked
try:
    validate_action()
except Exception:
    pass  # Continues silently

# ✅ CORRECT - Fails closed
try:
    validate_action()
except Exception as e:
    logger.error(f"Validation failed: {e}")
    raise  # Re-raises to block execution
```

### Pattern 3: Health Checks Without Dependency Verification
```python
# ❌ THEATER - Detected and blocked
@app.route("/health")
def health():
    return {"status": "healthy"}, 200

# ✅ CORRECT - Actually checks
@app.route("/health")
def health():
    redis_ok = redis.ping()
    kernel_ok = kernel.is_alive()
    invariants_ok = engine.validate_all()
    return {"status": "healthy" if all([redis_ok, kernel_ok, invariants_ok]) else "unhealthy"}
```

## Integration with CognitionKernel

All audit operations route through `CognitionKernel`:

```python
class ProductionAuditor(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None):
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",  # Read-only auditing
        )
```

**Risk Level:** `low` (auditing is read-only, no modifications)

## Verification Commands

After fixing blockers, verify with:

```bash
# Verify governance enforcement
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 canonical/replay.py

# Run test suite
pytest -v --cov=src/app/core --cov-report=html

# Security scan
bandit -r src/ -f json -o ci-reports/bandit.json

# Dependency audit
pip-audit --desc

# Lint check
ruff check . --output-format=json
```

## Deployment Approval Criteria

Deployment is **BLOCKED** if:
- Any CRITICAL blocker exists
- Governance theater detected
- Missing tests for critical paths
- Unpinned dependencies
- Health endpoints don't verify dependencies
- Container runs as root
- `.env` not in `.gitignore`
- Canonical replay fails

Deployment is **READY** if:
- Zero blockers
- Score ≥ 80%
- All evidence artifacts present
- Canonical replay passes 5/5 invariants

## Example Audit Session

```bash
$ python -m app.agents.production_auditor

Starting production readiness audit...
[✓] Runtime Startup
[✓] Docker Container
[✗] Health Endpoints - Missing dependency checks
[✓] Environment Variables & Secrets
[✓] Logging & Audit
[✗] Error Handling - Fail-open behavior detected
[✗] Dependency Pinning - 3 unpinned packages
[✓] CI Gates
[✗] Test Coverage - Missing test_execution_gate.py
[✗] Evidence Manifest - canonical/replay.py fails
[✓] Release Consistency
[✗] Governance Enforcement - Theater pattern detected

Production audit complete: 50.0% (6/12 checks passed)

Status: BLOCKED
Blockers: 6 critical issues
Warnings: 2 recommendations
Deployment Ready: ❌ NO

Report written to: PRODUCTION_AUDIT_REPORT.md

RECOMMENDATION: FIX BLOCKERS FIRST
```

## Testing

Run tests with:

```bash
pytest tests/test_production_auditor.py -v
```

Test coverage includes:
- All 12 audit categories
- Governance theater detection
- Fail-closed behavior verification
- Report generation
- Quick verification mode

## Related Documentation

- `.github/PRODUCTION_READINESS_ASSESSMENT.md` - Example assessment
- `docs/governance/TRIUMVIRATE_DOMAIN_MAPPING.md` - Governance structure
- `canonical/scenario.yaml` - Canonical invariants
- `src/app/core/execution_gate.py` - Enforcement implementation

---

**Last Updated:** 2026-05-13  
**Agent Type:** KernelRoutedAgent  
**Risk Level:** Low (read-only)  
**Governance Status:** ✅ Fully Governed
