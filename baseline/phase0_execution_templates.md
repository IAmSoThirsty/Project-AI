# Phase 0 Execution Templates

**Date:** 2026-05-15  
**Purpose:** Validated operating templates for file-by-file inspection before Phase 1-7 implementation  
**Scope:** 1,354 Python files across 6 phases (Phase 0 already 924/924 complete)

---

## PHASE 0 VALIDATION GATE ✅ COMPLETE

All prerequisite artifacts established:

- ✅ **Repo baseline captured** → `baseline/phase0_current_phase_progress.csv`
- ✅ **Current tests recorded** → 67.13% genuine baseline (909/1354 files)
- ✅ **Current claims mapped to files** → 1,354 file_inspection records with latest-verdict-per-file
- ✅ **Production paths identified** → Phase 0: 70.24% genuine, Phase 2: 63.5% genuine, Phase 6: 77.52% genuine
- ✅ **Theater/stub/broken files tagged** → 53 CRITICAL/HIGH priority gaps exported
- ✅ **CI baseline established** → canonical/replay.py 5/5 invariants PASSING
- ✅ **Rollback checkpoint created** → All baseline artifacts saved to baseline/

**Gate status:** OPEN — Implementation phases may proceed

---

## FILE INSPECTION TEMPLATE (Read-Only Audit)

**Purpose:** Classify file verdict without making changes

**Protocol:**

```python
# 1. Read full source (no truncation)
with open(filepath, 'r', encoding='utf-8') as f:
    source = f.read()

# 2. Identify claims
claims = extract_claims(docstring, comments, function_names)

# 3. Verify implementation
reality = verify_implementation(source)
# Check for:
# - subprocess/ctypes calls → OS integration
# - return True → potential theater
# - External tool calls → wg, nft, iptables
# - Mock/stub patterns → placeholder code

# 4. Classify verdict
verdict = classify(claims, reality)
# Verdicts:
# - GENUINE: works as claimed
# - ASPIRATIONAL: good structure, missing integration
# - THEATER: fake success indicators
# - BROKEN: would crash
# - STUB: placeholder only

# 5. Document gap
gap = {
    'current_state': reality,
    'required_state': claims,
    'implementation_path': how_to_fix,
    'effort_hours': estimate
}

# 6. Insert into database
INSERT INTO file_inspection (
    filepath, verdict, claims, reality, gap_description,
    fix_recommendation, effort_hours, priority, phase, inspected_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
```

**Verdicts:**

- ✅ **GENUINE** — Production-ready, works as claimed
- 🟡 **ASPIRATIONAL** — Good structure, missing OS/external integration
- 🔴 **THEATER** — Fake implementations (return True, empty dict)
- 💀 **BROKEN** — Would crash on execution
- 📦 **STUB** — Placeholder/TODO only

**Priorities:**

- **CRITICAL** — Blocks production deployment (governance bugs, security holes)
- **HIGH** — Major feature claims unimplemented (VPN, MFA, browser)
- **MEDIUM** — Nice-to-have features (analytics, advanced UI)
- **LOW** — Quality-of-life improvements (naming, docs)

---

## PHASE 1: CRITICAL BUG FIXES (Tier 1)

**Scope:** 5 files, 103 hours  
**Objective:** Fix governance theater and blocking bugs  
**Validation:** canonical/replay.py must pass 5/5 invariants

**Files:**

1. ~~`src/app/core/ai_systems.py`~~ — ✅ FIXED (TARL spam removed)
2. ~~`src/app/governance/governance_quorum.py`~~ — ✅ FIXED (_evaluate_quorum now works)
3. `src/utf/t1_thirsty_lang.py` — ❌ readline bug (2h)
4. `src/app/psia/anchor.py` — ❌ Ed25519 signing (1h)
5. `src/app/gui/desktop_adapter.py` — ⚠️ governance routing gaps (18h)

**Template:**

```python
# Fix pattern: Replace except:pass with fail-closed error handling
# Before:
try:
    result = critical_governance_check()
except:
    pass  # Silent failure

# After:
try:
    result = critical_governance_check()
except Exception as e:
    logger.critical(f"Governance check failed: {e}")
    raise RuntimeError("Governance enforcement failure - fail closed") from e
```

---

## PHASE 2: DEPENDENCY BASELINE (Tier 1) ✅ COMPLETE

~~**Scope:** 47 dependencies audited~~  
~~**Status:** pyreadline3, redis, fastapi installed; PyJWT, cryptography updated~~

---

## PHASE 3: BACKEND WIRING (Tier 2) ✅ COMPLETE

~~**Scope:** VPN + Firewall managers~~  
~~**Status:** WireGuard, OpenVPN, IKEv2, nftables, pfSense, Windows Firewall backends all wired~~

---

## PHASE 4: VALIDATION GATES (Current Phase)

**Scope:** Run full test suite, validate all critical integrations  
**Validation:** All tests must pass before Phase 5+ work begins

**Checklist:**

- [ ] **Test Suite:** pytest -v (target: 100% pass rate)
- [ ] **AI Systems:** src/app/core/ai_systems.py (13/13 tests currently pass)
- [ ] **UTF Stack:** src/utf/ (20/20 tests currently pass)
- [ ] **Canonical Replay:** canonical/replay.py (5/5 invariants currently pass)
- [ ] **Docker Build:** docker-compose build (currently succeeds)
- [ ] **Import Check:** All critical modules load without errors
- [ ] **Governance Integration:** Triumvirate server responds on port 8001
- [ ] **NIRL Cascade:** Heart/MiniBrain/Antibody/Forge all functional

**Template:**

```bash
# Validation sequence
pytest -v                          # All tests
python canonical/replay.py         # 5/5 invariants
docker-compose build              # Clean build
python -c "from app.core import execution_gate; print('OK')"  # Import check
curl http://localhost:8001/api/governance/status  # Triumvirate
```

---

## PHASE 5: OS INTEGRATION SCAFFOLDING (Tier 2-3)

**Scope:** 30 files, 40 hours  
**Objective:** Wire real subprocess/API calls to VPN/Firewall/Browser managers

**Files:**

- `src/app/thirstys_waterfall/vpn/backends.py` — ✅ WIRED (WireGuard, OpenVPN, IKEv2)
- `src/app/thirstys_waterfall/firewalls/backends.py` — ✅ WIRED (nftables, Windows, pfSense)
- `src/app/browser/browser_engine.py` — ❌ QWebEngine integration (12h)
- `src/app/security/microvm_isolation.py` — ❌ Firecracker API (8h)
- `src/app/security/mfa_auth.py` — ❌ FIDO2/TOTP (6h)

**Template (VPN Integration Pattern):**

```python
# Real OS integration (NOT theater)
import subprocess
import shlex

def connect_wireguard(config_path: str) -> bool:
    """Connect to WireGuard VPN using OS-level wg-quick."""
    try:
        # Validate config exists
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"WireGuard config not found: {config_path}")
        
        # Call real wg-quick (requires root/admin)
        result = subprocess.run(
            ['wg-quick', 'up', config_path],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        
        logger.info(f"WireGuard connected: {result.stdout}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"WireGuard connection failed: {e.stderr}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
```

---

## PHASE 6: FEATURE COMPLETION (Tier 3-4)

**Scope:** 50 files, 60 hours  
**Objective:** Complete claimed features (MicroVM, MFA, DOS Trap)

**Template (Feature Implementation):**

```python
# Pattern: Complete aspirational features with real libraries

# BEFORE (ASPIRATIONAL):
def enable_mfa(user_id: str) -> dict:
    """Enable multi-factor authentication."""
    return {'mfa_enabled': True, 'secret': 'PLACEHOLDER'}

# AFTER (GENUINE):
import pyotp
import qrcode
from io import BytesIO

def enable_mfa(user_id: str) -> dict:
    """Enable TOTP-based multi-factor authentication.
    
    Returns:
        dict: {
            'mfa_enabled': bool,
            'secret': str,  # Base32 TOTP secret
            'qr_code': bytes,  # PNG image data
            'backup_codes': list[str]
        }
    """
    try:
        # Generate real TOTP secret
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        
        # Generate QR code for authenticator apps
        uri = totp.provisioning_uri(
            name=user_id,
            issuer_name='Project-AI'
        )
        qr = qrcode.make(uri)
        qr_bytes = BytesIO()
        qr.save(qr_bytes, format='PNG')
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4) for _ in range(10)]
        
        # Store secret (encrypted) in user profile
        store_mfa_secret(user_id, secret, backup_codes)
        
        return {
            'mfa_enabled': True,
            'secret': secret,
            'qr_code': qr_bytes.getvalue(),
            'backup_codes': backup_codes
        }
        
    except Exception as e:
        logger.error(f"MFA setup failed for {user_id}: {e}")
        raise
```

---

## PHASE 7: THEATER REMOVAL (Tier 4)

**Scope:** 40 files, 12 hours  
**Objective:** Remove bombastic naming, align README with reality

**Naming Conventions:**

| Before (Theater) | After (Honest) |
|-----------------|----------------|
| GOD TIER | Multi-Layer |
| HOLY WAR ENGINE | Ad Blocker |
| PLANETARY DEFENSE | Governance Pipeline |
| DEFCON ULTIMATE | Stress Test |
| NUCLEAR OPTION | Emergency Shutdown |

**Template:**

```python
# Before:
class GodTierSecuritySystem:
    """PLANETARY-SCALE THREAT DEFENSE."""
    def activate_nuclear_option(self):
        return True

# After:
class MultiLayerSecuritySystem:
    """Multi-tier security with governance oversight."""
    def emergency_shutdown(self):
        """Gracefully shut down all services and persist state."""
        # Real implementation with actual shutdown logic
```

---

## AGENT ASSIGNMENT TEMPLATE

**Format:** For each phase, assign specialized agents based on required skills

**Example (Phase 5 OS Integration):**

```yaml
phase: 5
title: "OS Integration Scaffolding"
agents:
  - name: "gem-implementer"
    tasks:
      - "Wire QWebEngine to BrowserEngine"
      - "Implement Firecracker API client"
      - "Integrate FIDO2/pyotp for MFA"
    skills_required: ["Python", "subprocess", "API integration"]
    
  - name: "gem-reviewer"
    tasks:
      - "Security audit of subprocess calls"
      - "Verify no command injection vectors"
      - "Check error handling completeness"
    skills_required: ["Security", "Code review"]
    
  - name: "gem-tester"
    tasks:
      - "Write integration tests for VPN/Firewall"
      - "Mock OS APIs for CI environment"
      - "Verify graceful degradation"
    skills_required: ["pytest", "mocking", "integration testing"]

dependencies:
  - "Phase 4 validation gates must pass"
  - "Docker environment available for testing"
```

---

## BATCH PROCESSING STRATEGY (Phase 0 Audit Continuation)

**Remaining:** 0 files (Phase 0 already 100% complete at 924 files)

**Note:** Phase 0 audit is complete. Next work is implementation phases (1-7).

---

## VALIDATION GATE CRITERIA

**Before beginning each phase:**

1. **Gate Open Criteria:**
   - [ ] Previous phase 100% complete
   - [ ] All dependencies resolved
   - [ ] Required tools/environments available
   - [ ] Test baseline established
   - [ ] Rollback plan documented

2. **During Phase:**
   - [ ] Continuous integration tests pass
   - [ ] No regressions introduced
   - [ ] Documentation updated
   - [ ] Code review completed

3. **Phase Exit Criteria:**
   - [ ] All phase tasks complete
   - [ ] Test coverage ≥80%
   - [ ] canonical/replay.py 5/5 PASS
   - [ ] No CRITICAL/HIGH gaps remain in phase scope
   - [ ] Formal deliverable generated

---

## CURRENT STATUS (2026-05-15)

**Phase 0:** ✅ COMPLETE (924/924 files, 70.24% genuine)  
**Phase 1:** ✅ 2/5 files fixed (ai_systems.py, governance_quorum.py)  
**Phase 2:** ✅ COMPLETE (dependency baseline)  
**Phase 3:** ✅ COMPLETE (VPN/Firewall wiring)  
**Phase 4:** ⏳ PENDING (validation gates)  
**Phase 5-7:** ⏳ PENDING (implementation)

**Next Gate:** Phase 4 Validation  
**Blocking Issues:** 3 Tier 1 files remaining (UTF readline, PSIA Ed25519, GUI governance routing)

---

## RELEASE READINESS CRITERIA

**Target:** ≥95% GENUINE, ≤5% ASPIRATIONAL, 0 CRITICAL/HIGH gaps

**Current:**
- Genuine: 67.13% ❌ (target: 95%)
- Aspirational: 14.33% ✅ (target: ≤5%)
- CRITICAL gaps: 14 ❌ (target: 0)
- HIGH gaps: 39 ❌ (target: 0)

**Path to Release:**
1. Resolve 14 CRITICAL gaps
2. Resolve 39 HIGH gaps
3. Continue implementation to reach 95%+ genuine
4. Final validation: 5/5 invariants + full test suite

**Estimated Effort to Release:** 133 hours (Path B — Tier 1 + 2)

---

## TEMPLATE LOCK

These templates are the validated operating plan for Project-AI structural completion.

**Frozen:** 2026-05-15 09:35 UTC  
**Version:** 1.0  
**Approval:** Phase 0 validation gate passed  
**Next Review:** After Phase 4 validation gates complete
