# Iron Path 2.0 — Phased Repair Plan

**Generated:** 2026-06-03  
**Branch:** `substrate-consolidation`  
**HEAD SHA:** `e3913e6c9073f488ed2d82b1afeb039e1e46e616`  
**Status:** READ-ONLY ANALYSIS — no source behavior changed  
**Scope:** This is a pre-implementation plan only. No code has been modified.

---

## Executive Summary

Static analysis of the constitutional substrate on branch `substrate-consolidation` identified:

- **8 critical authority conflicts** requiring architectural repair
- **5 receipt gaps** requiring new tests or persistence wiring
- **3 dev-secret defaults** that make cryptographic receipts meaningless in non-production environments
- **2 fully silenceable enforcement gates** (RuntimeEnforcer, StateRegister) that can be disabled by any initialization exception
- **1 fully stubbed governance lifecycle module** (GovernanceManager)
- **1 parallel unaudited authority path** (_auto_approve() in GovernanceService)

None of these are build-breaking. All affect governance integrity, auditability, and constitutional correctness. The repair plan is phased so that each phase produces a verifiable receipt before the next phase begins.

---

## Phase 1 — Annotations Only (No Behavior Change)

**Purpose:** Document the known gaps in the codebase without changing any behavior. Every annotation is a written stop condition that must be resolved before implementation proceeds.

**Safety:** No tests should change. No behavior changes. Diff shows only comment additions.

### 1.1 Annotate execution_router.py Silent Bypasses

**File:** `src/app/core/execution_router.py`  
**Lines:** 50–51, 58–59, 74–75

Add `# IRON-PATH-RISK` comments above each `except Exception: pass` block explaining the bypass risk and the intended fix.

```python
# IRON-PATH-RISK: Silent bypass. If RuntimeEnforcer fails to initialize or raises
# any exception, PAGL prohibitions, consent requirements, tier entitlements, and
# sovereign restrictions are completely unenforced for this request. No EvidenceBundle
# is produced. No audit record is created. The bypass is invisible to all monitors.
# Phase 3 fix: replace with try-except that emits EvidenceBundle(outcome="BYPASS_RECORDED")
# and logs at WARNING before continuing. Never silently pass a governance failure.
except Exception:
    pass
```

Apply equivalent comments to lines 58–59 (StateRegister) and 74–75 (TrustScoring).

**Tests required before:** None (annotations only)  
**Tests required after:** Confirm no test changes; `git diff --stat` should show only `execution_router.py`  
**Receipt produced:** Annotated codebase on branch  
**Rollback:** `git revert` on annotation commit

### 1.2 Document _auto_approve() in governance_service.py

**File:** `src/app/core/services/governance_service.py`  

Add `# IRON-PATH-RISK` comment above `_auto_approve()`:

```python
# IRON-PATH-RISK: This path bypasses Triumvirate consultation entirely.
# Triggered when GovernanceService is instantiated without a triumvirate or
# governance_system (e.g., degraded mode, test harness without mocks, cognition_kernel
# in some evaluation paths). Any action with risk_level in ["low", "routine"] is
# approved without governance council review. Decision is written to in-memory dict
# only — not persisted, not auditable, not linked to an EvidenceBundle.
# Phase 3 fix: inject a minimum-stub Triumvirate that denies all non-read actions
# unless the system is in explicitly declared degraded mode.
```

**Tests required before/after:** None (annotations only)

### 1.3 Document invariant seal placeholder in psia/invariants.py

**File:** `src/psia/invariants.py`, line 14

```python
_SIG = Signature(
    alg="ed25519",
    kid="genesis-root-key",
    sig="governance-sealed",  # IRON-PATH-NOTE: This is NOT a real Ed25519 signature.
    # "governance-sealed" is a string sentinel indicating the invariants are intended
    # to be signed by the genesis root key, but no actual cryptographic signing has
    # occurred. Phase 4 fix: sign each INV-ROOT-* with a real Ed25519 keypair registered
    # in CapabilityAuthority's key_store under kid="genesis-root-key".
)
```

**Tests required before/after:** None (annotations only)

---

## Phase 2 — Wiring (Connect Existing Infrastructure)

**Purpose:** Connect existing, tested substrates to the execution path where they are already structurally expected but not yet wired.

**Constraint:** Each wiring step must have a test that verifies the new connection before the next step begins.

### 2.1 Wire AuditManager into GovernanceKernel

**File:** `src/app/core/governance_kernel.py`  
**Authority path affected:** governance decisions → audit record  
**Current:** `AuditLog().log_event(...)` called directly (non-sovereign, lower tier)  
**Intended:** `audit_manager.AuditManager(sovereign_mode=True).log_governance_event(...)` called instead

**Compatibility shim needed:** None. AuditManager already exists and wraps SovereignAuditLog. The only change is replacing the direct `AuditLog()` call with an `AuditManager` singleton call.

**Tests required before change:**
- `tests/test_governance_contract.py` must pass (23 tests)
- `tests/test_sovereign_audit_log.py` must pass (verifies SAL behavior)

**Tests required after change:**
- New test: `test_governance_kernel_writes_to_audit_manager()` — after `evaluate_action()`, assert that `AuditManager.get_statistics()['total_events'] > 0`
- Existing `tests/test_governance_contract.py` must still pass

**Receipt generated:** SovereignAuditLog event record for each GovernanceKernel decision  
**Rollback:** Revert `governance_kernel.py` change; governance_kernel falls back to AuditLog() directly

### 2.2 Enable sovereign_mode=True in Production Callers

**Files affected:** Any code that instantiates `AuditManager` or where AuditManager is newly wired  
**Authority path affected:** audit writes → sovereign log  
**Current:** `AuditManager` defaults to `sovereign_mode=False`; no crypto trail  
**Intended:** Production execution paths use `sovereign_mode=True`

**Note:** This step depends on 2.1 being complete and genesis key files existing (`data/` writable, genesis keys generated at Tier 0 boot step 0.1 equivalent).

**Tests required before:** `data/genesis_pins/` directory writable in test environment  
**Tests required after:** `test_audit_manager_sovereign_mode()` — log event, call `generate_proof_bundle()`, verify Ed25519 signature present

### 2.3 Wire capability_authority.py to ExecutionGate Stage 6 (Dual-Verify)

**File:** `src/app/core/execution_gate.py` Stage 6  
**Authority path affected:** capability token validation  
**Current:** Stage 6 calls `CapabilityTokenService` (HMAC-SHA256, dev default secret)  
**Intended:** Stage 6 accepts both HMAC tokens (legacy) AND Ed25519 tokens (issued by `CapabilityAuthority`)

**Compatibility shim needed:** Yes. Dual-verify shim:
```
# Accept token if either verifier validates it:
#   1. CapabilityTokenService.verify(token) [HMAC — existing]
#   2. CapabilityAuthority.is_valid(token_id) [Ed25519 — new]
# Both must not raise; dual-verify period lasts until all HMAC tokens are expired/rotated.
```

**This does NOT remove capability_token.py.** HMAC tokens continue to work. Ed25519 tokens are added as a valid alternative.

**Tests required before:** `tests/test_capability_tokens.py` must pass  
**Tests required after:** New test verifying Ed25519 token accepted at Stage 6; old HMAC token still accepted

---

## Phase 3 — Harden (Close Bypass Windows)

**Purpose:** Replace silent bypass patterns with fail-auditable patterns. Every failure must produce a record.

**Constraint:** No change may silence a failure without first emitting a `BYPASS_RECORDED` EvidenceBundle and a WARNING log.

### 3.1 Fix execution_router.py Silent Passes

**File:** `src/app/core/execution_router.py`  
**Lines:** 50–51, 58–59, 74–75  
**Authority path affected:** RuntimeEnforcer, StateRegister, TrustScoring

Replace each `except Exception: pass` with:

```python
except Exception as _bypass_exc:
    logger.warning(
        "IRON-PATH-BYPASS: %s failed (%s) — recording bypass event; execution continues",
        "RuntimeEnforcer",  # substitute component name per block
        type(_bypass_exc).__name__,
    )
    # Emit a BYPASS_RECORDED EvidenceBundle so the bypass is auditable
    try:
        from app.core.evidence_bundle import EvidenceBundleWriter
        _bypass_bundle = EvidenceBundleWriter().build(
            executor_id="execution_router",
            action=action,
            domain=domain,
            final_outcome="BYPASS_RECORDED",
            denial_reason=f"Component failure: {type(_bypass_exc).__name__}: {_bypass_exc}",
        )
        # This does NOT stop execution — the bypass is recorded, not blocked
        # Phase 4 will evaluate whether bypass_count > threshold triggers HALT
    except Exception:
        logger.debug("EvidenceBundle production failed during bypass recording (non-fatal)")
```

**Tests required before:** Existing execution path tests must pass  
**Tests required after:**
- New test: simulate RuntimeEnforcer ImportError → verify BYPASS_RECORDED bundle in evidence store
- New test: simulate RuntimeEnforcer returning deny → verify execution blocked (existing behavior)
- Both tests must pass

**Receipt generated:** `EvidenceBundle(final_outcome="BYPASS_RECORDED")` per silenced component failure  
**Rollback:** Revert to `except Exception: pass`; behavior regresses to silent bypass

### 3.2 Rotate Dev Secrets

**Files:** `src/app/core/policy_registry.py`, `src/app/core/capability_token.py`

Add pre-init assertions that reject dev-default secrets in production:

```python
# policy_registry.py
_SIGN_SECRET = os.environ.get("POLICY_REGISTRY_SECRET", "dev-policy-secret")
if _SIGN_SECRET == "dev-policy-secret":
    import warnings
    warnings.warn(
        "POLICY_REGISTRY_SECRET is using the dev default. "
        "Set POLICY_REGISTRY_SECRET env var before production use. "
        "All HMAC signatures produced with this key are cryptographically invalid in production.",
        RuntimeWarning,
        stacklevel=2,
    )
```

**Tests required after:** Test that production deployment with env var set does not trigger warning  
**Receipt generated:** Warning in logs if dev secret is active — now observable

### 3.3 Make CapabilityToken Replay Store Durable

**File:** `src/app/core/capability_token.py`  
**Current:** `_USED_TOKENS: set[str]` — in-process, bounded at 10,000  
**Intended:** Durable store (Redis SET with TTL matching token expiry, or SQLite for single-node)

This is the highest-effort item in Phase 3. A compatibility shim is required:

```
# Shim: attempt Redis connection; fall back to in-process set with WARNING
# If Redis unavailable: log WARNING "REPLAY_PREVENTION_DEGRADED: in-process store active; tokens
# issued in previous process lifetime will not be detected as replays"
```

**Tests required before:** `tests/test_replay_protection.py` must pass  
**Tests required after:** Test that token used in process A is rejected in process B (requires Redis in test env)

---

## Phase 4 — Seal (Cryptographic Completeness)

**Purpose:** Replace placeholder cryptographic seals with real ones. Every seal must be machine-verifiable.

### 4.1 Replace Invariant Placeholder Signature

**File:** `src/psia/invariants.py`  
**Current:** `sig="governance-sealed"` (string literal)  
**Intended:** Real Ed25519 signature over each invariant's canonical serialization

**Implementation approach:**
1. Generate a stable Ed25519 keypair designated as the governance root key
2. Register it in `CapabilityAuthority`'s key_store under `kid="genesis-root-key"`
3. For each `INV-ROOT-*`, compute `canonical_bytes = json.dumps(inv_definition_dict, sort_keys=True).encode()`
4. Sign with governance root key using `Ed25519Provider.sign(canonical_bytes)`
5. Replace `sig="governance-sealed"` with `sig=base64.b64encode(signature).decode()`

**Compatibility shim needed:** Yes. Add `verify_invariant_seal()` function to `invariants.py` that checks `Signature.sig != "governance-sealed"` before verifying — allows both old (placeholder) and new (real) seals during transition.

**Tests required before:** `tests/test_psia_invariants.py` must pass  
**Tests required after:** New test: `verify_invariant_seal(INV_ROOT_1)` returns True with governance root key

### 4.2 Link EvidenceBundle to ConstitutionalLedger

**Files:** `src/app/core/constitutional_ledger.py`, `src/app/core/evidence_bundle.py`, `src/app/core/governance_kernel.py`  

Add `bundle_id: str | None` field to `LedgerEntry`. When `governance_kernel.attest()` is called, pass the `EvidenceBundle.bundle_id` from Stage 9 so the ledger record is linked.

**Tests required before:** `tests/test_governance_contract.py` must pass  
**Tests required after:** New test verifying ledger entry has `bundle_id` pointing to a bundle in the evidence store

### 4.3 Resolve GovernanceManager: Wire or Deprecate

**File:** `src/app/governance/governance_manager.py`  
**Decision required:** Is GovernanceManager the intended multi-stakeholder proposal system (active development target), or is it a dead module to be deprecated?

Option A — Wire: Connect proposal lifecycle to `policy_registry`, `audit_manager`, and `execution_gate`. Proposal approval becomes the mechanism for `policy_registry.register_policy()` calls.

Option B — Deprecate: Mark with `# DEPRECATED: This module is not wired into any runtime path. Governance proposals are handled via [alternative mechanism]. Do not add callers.`

This decision must be made explicitly by the project owner before implementation proceeds.

**Tests required for Option A:** Full lifecycle test suite for create → vote → quorum → execute  
**Tests required for Option B:** Confirm no existing tests rely on GovernanceManager behavior

---

## Phase 5 — Verify (Receipt Completeness)

**Purpose:** Close the test and receipt gaps identified in the Receipts Convergence Map.

### 5.1 Add test_acceptance_ledger.py

**File to create:** `tests/test_acceptance_ledger.py`  
**Coverage needed:**
- Ed25519 signature round-trip on AcceptanceEntry
- SQLite backend: append-only (delete attempt returns error)
- RFC3161 timestamp anchor (mock TSA endpoint or local TSA)
- INITIAL_MSA entry creation and validation

### 5.2 Add test_deterministic_replay.py

**File to create:** `tests/test_deterministic_replay.py`  
**Coverage needed:**
- Import `DeterministicReplayTool` from `src/app/core/deterministic_replay.py`
- Write a known execution context to the decision log
- Verify replay produces identical output
- Verify that a tampered log entry is detected

### 5.3 Preserve Canonical Execution Trace History

**File affected:** `canonical/replay.py`  
**Current:** `canonical/execution_trace.json` is overwritten on every run  
**Intended:** Preserve last N traces in `canonical/trace_history/` for regression comparison

Add to `cicd.yml`:
```yaml
- name: Preserve trace history
  run: |
    mkdir -p canonical/trace_history
    cp canonical/execution_trace.json \
       canonical/trace_history/trace_$(date +%Y%m%dT%H%M%S).json
```

### 5.4 Add Triumvirate Decision Persistence

**Files:** `src/app/core/governance.py`, `src/app/core/governance_kernel.py`  
**Current:** `governance.py Triumvirate._log_decision()` writes to in-memory list only  
**Intended:** Connect `_log_decision()` through `audit_manager.log_governance_event()` after 2.1 is complete

This is a downstream dependency of Phase 2.1 — do not implement before AuditManager is wired into GovernanceKernel.

---

## Repair Priority Matrix

| Priority | Issue | Phase | Files Changed | Risk | Effort |
|----------|-------|-------|---------------|------|--------|
| 1 | RuntimeEnforcer silent bypass | 3.1 | `execution_router.py` | CRITICAL | Low |
| 2 | _auto_approve() unaudited authority | 1.2, 3.1 | `governance_service.py`, `execution_router.py` | CRITICAL | Low (annotation), Medium (fix) |
| 3 | AuditManager not wired into main path | 2.1 | `governance_kernel.py` | HIGH | Medium |
| 4 | Dev secrets in policy_registry and capability_token | 3.2 | `policy_registry.py`, `capability_token.py` | HIGH | Low |
| 5 | capability_authority not wired to execution_gate | 2.3 | `execution_gate.py`, `capability_authority.py` | HIGH | Medium |
| 6 | AuditManager sovereign_mode=False default | 2.2 | Multiple callers | HIGH | Low |
| 7 | Invariant seal is placeholder | 1.3, 4.1 | `invariants.py` + key generation | HIGH | High |
| 8 | capability_token replay store not durable | 3.3 | `capability_token.py` | HIGH | High |
| 9 | GovernanceManager stubbed | 4.3 | `governance_manager.py` | MEDIUM | High |
| 10 | Triumvirate decisions not persisted | 5.4 | `governance.py` | MEDIUM | Medium |
| 11 | AcceptanceLedger no test suite | 5.1 | new test file | MEDIUM | Low |
| 12 | DeterministicReplay not wired, no tests | 5.2 | new test file | MEDIUM | Medium |

---

## Stop Conditions

The following conditions must cause implementation to stop immediately:

| Stop Condition | Current State |
|----------------|---------------|
| ExecutionGate behavior is ambiguous | NOT triggered — gate is clear (9 stages, ALLOW/DENY/HALT) |
| Any DENY path fails to produce EvidenceBundle | NOT triggered — Stage 9 produces bundle on all exit paths |
| Any HALT path fails to produce EvidenceBundle | NOT triggered — Stage 9 covers HALT |
| Any audit write bypasses audit_manager.py without justification | **TRIGGERED** — governance_kernel writes to AuditLog() directly |
| Any token validation accepts unclear authority | **TRIGGERED** — capability_token.py (HMAC, dev secret) is the active issuer; authority chain unclear |
| Any old token issuer remains active without compatibility-only constraints | **TRIGGERED** — capability_token.py has no compatibility-only constraint annotation |
| Any policy YAML acts as independent enforcement | VERIFY NEEDED — check `src/psia/policies/` for standalone YAML enforcement |
| Any code path executes without canonical lifecycle | **TRIGGERED** — _auto_approve() in governance_service.py |
| Any schema change required before receipt mapping complete | NOT triggered — no schema changes in this plan |
| Any caller map is incomplete | NOT triggered — caller maps are complete as of this analysis |
| Any test artifact contradicts documentation | **TRIGGERED** — RuntimeEnforcer docstring "Zero bypass" contradicted by execution_router.py:50–51 |
| Any "production ready" claim lacks machine-verifiable proof | **TRIGGERED** — multiple "production ready" claims in docs without machine-verifiable receipts for main execution path |

**Active stop conditions that block implementation from starting:**

1. **Audit bypass active** (C-3): `governance_kernel → AuditLog()` must be fixed or explicitly documented as accepted-risk before any new governance features are added. Phase 2.1 is the remediation.

2. **Token authority fragmented** (C-4): Two independent token issuers (HMAC vs Ed25519) with no explicit compatibility layer. Phase 2.3 adds the dual-verify shim.

3. **Auto-approve path unaudited** (C-2): Must be annotated (Phase 1.2) and hardened (Phase 3.1 downstream) before any new governance policies are added.

4. **genesis_continuity.py modified unstaged**: This core substrate has uncommitted changes. The repo state is not clean. Implementation MUST NOT proceed until `genesis_continuity.py` is either committed + tested or its changes are explicitly reviewed.

---

*Next report: [IRON_PATH_2_CONSTITUTIONAL_SUBSTRATE_ACTIVATION.md](IRON_PATH_2_CONSTITUTIONAL_SUBSTRATE_ACTIVATION.md)*
