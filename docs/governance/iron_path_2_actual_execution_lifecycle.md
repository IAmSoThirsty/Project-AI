# Iron Path 2.0 — Actual Execution Lifecycle

**Generated:** 2026-06-03  
**Branch:** `substrate-consolidation`  
**HEAD SHA:** `e3913e6c9073f488ed2d82b1afeb039e1e46e616`  
**Status:** READ-ONLY ANALYSIS — no source behavior changed

---

## 1. The Intended Canonical Lifecycle

Per the Iron Path 2.0 mission specification, the intended execution lifecycle is:

```
pipeline.py
  → governance_kernel.py
    → execution_gate.py
      → evidence_bundle.py         [pre-execution authorization proof]
      → audit_manager.py
          → sovereign_audit_log.py
      → iron_path_executor.py
      → execution_result
      → evidence_bundle.py         [post-execution outcome proof]
      → audit_manager.py
          → sovereign_audit_log.py
```

**Semantic rule from mission spec:**
- Audit does NOT call execution.
- Execution EMITS audit records before and after execution.
- Every governed action must produce:
  1. Pre-execution EvidenceBundle
  2. Audit record of authorization decision
  3. Execution result OR denied/halted result
  4. Post-execution EvidenceBundle
  5. Audit record of actual outcome

---

## 2. The Actual Execution Path

### 2A. Primary Runtime Entry: `execution_router.execute()`

`src/app/core/execution_router.py` is documented as "The ONLY legal execution path in the system." It is called by 10 domain modules and `cognition_kernel.py`.

```
execution_router.execute(domain, action, context, executor_fn)
  │
  ├─ [Step 1] waterfall_filter.filter(context)
  │     Result: HARD BLOCK on deny — returns (False, reason) immediately
  │     Audit on deny: none produced here
  │
  ├─ [Step 2] liara_ttl_check(context) + get_liara_context()
  │     Result: HARD — auto-revokes expired crisis roles, enriches context
  │
  ├─ [Step 2.5] runtime_enforcer.enforce(EnforcementContext)    ← SILENCEABLE
  │     try:
  │       from app.governance.runtime_enforcer import ...
  │       result = get_runtime_enforcer().enforce(ctx)
  │       if result.verdict == "deny": return False, reason
  │     except Exception:
  │       pass  ← lines 50–51: ANY exception silently discarded
  │     Checks: PAGL prohibitions, consent, tier entitlements, sovereign restrictions
  │     Risk: import failure, init failure, or any exception = silent bypass
  │
  ├─ [Step 3] state_register.get_temporal_context()              ← SILENCEABLE
  │     try:
  │       sr = get_state_register()
  │       temporal = sr.get_temporal_context()
  │       context = {**context, "_temporal": temporal}
  │     except Exception:
  │       pass  ← lines 58–59: temporal context silently omitted
  │     Risk: context flows to gate without temporal anti-gaslighting data
  │
  ├─ [Step 3.5] TrustScoringEngine + AdversarialPatternRegistry  ← SILENCEABLE
  │     try:
  │       from app.core.tarl_operational_extensions import ...
  │       _trust_score, _ = TrustScoringEngine().calculate_trust_score(...)
  │       _adv_flags = AdversarialPatternRegistry().detect_patterns(...)
  │       context = {**context, "_trust_score": ..., "_adversarial_flags": ...}
  │     except Exception:
  │       pass  ← lines 74–75: trust and adversarial context silently omitted
  │     Risk: execution proceeds without trust scoring data
  │
  ├─ [Step 4] invariant_engine.validate(context)                 ← HARD
  │     try:
  │       invariant_engine.validate(context)
  │     except Exception as exc:
  │       return False, str(exc)  ← lines 81–82: NOT silenced; hard fail
  │     Checks: all loaded invariants against context
  │
  └─ [Step 5] execution_gate.execute(domain, action, context, executor_fn)  ← HARD GATE
        │  [not wrapped in try/except — hard failure propagates to caller]
        │
        ├─ Stage 0: governance_kernel.evaluate_action()
        │     → Triumvirate.evaluate_action() [rule-based: Four Laws + 3 councils]
        │     → cognition.triumvirate.Triumvirate.process() [ML Triumvirate, swallows all exceptions]
        │     → governance_graph.must_consult_domains()
        │     → governance_graph.get_authority_chain()
        │     → event_spine.publish() [async veto, can_be_vetoed=True]
        │     → fates.remember() [FATES logging]
        │     → constitutional_ledger.attest()
        │     → AuditLog().log_event()  ← BYPASS: not AuditManager/SovereignAuditLog
        │
        ├─ Stage 1: safe_allow_calibration [fail-closed → DEGRADED_READ_ONLY]
        ├─ Stage 2: policy_decision.evaluate() → policy_registry.is_action_permitted()
        ├─ Stage 3: execution_authorization [fail-closed]
        ├─ Stage 4: mutation_binding.verify() [HARD FAIL on mutation governance violation]
        ├─ Stage 5: sovereign_runtime [fail-closed]
        ├─ Stage 6: capability_token.verify() ← DUAL AUTHORITY: HMAC-SHA256 only
        │              [CapabilityAuthority / Ed25519 NOT called here]
        ├─ Stage 7: semantic_collision.detect()
        ├─ Stage 8: invariant_severity engine
        │
        ├─ executor_fn(context) ← actual work executes here
        │
        └─ Stage 9: evidence_bundle (pre + post) + governance_observability
                    ← bundles written to in-memory ring buffer ONLY
                    ← NOT written to AuditManager / SovereignAuditLog
                    ← NOT persisted to disk

  └─ [Step 6] nirl_forge.process() [post-gate, NON-FATAL]
        Failure: logged as warning, not returned to caller
```

### 2B. Parallel Entry: `pipeline.py::enforce_pipeline()`

A separate execution path exists through `src/app/core/governance/pipeline.py`. This path is reached from `src/app/runtime/router.py` and does NOT pass through `execution_router.execute()`.

```
runtime/router.py
  → governance/pipeline.py::enforce_pipeline(action, context, executor)
      Phase 1: _validate(action, context)
        → FourLaws.validate_action()
        → ACTION_REGISTRY strict check (no wildcard bypass)
      Phase 2: _simulate(action, context)
      Phase 3: _gate(action, context)
        → _enforce_mutation_governance_binding()
            → get_iron_path_executor().bind_mutation()  ← DIRECT to IronPathExecutor
                                                           (NOT through ExecutionGate)
        → _check_rate_limit()
        → _check_user_permissions()
        → _check_resource_quotas()
      Phase 4: _execute(action, context, executor)
        → action-type dispatch (temporal, agent, ai, or generic)
      Phase 5: _commit(action, context, result)
        → [STUB] rollback logged but not implemented (line ~1091: "# In production: implement rollback here")
      Phase 6: _log(action, context, result)
```

> **This path calls `iron_path_executor` directly without going through `execution_gate.execute()`.** The 9-stage gate (including EvidenceBundle production at Stage 9) is NOT invoked on this path. All ALLOW/DENY decisions made in pipeline.py Phase 3 are not subject to the ExecutionGate's authority chain validation.

---

## 3. Divergence Table: Intended vs Actual

| # | Intended | Actual | Severity | File:Line |
|---|----------|--------|----------|-----------|
| D-1 | Every governed action passes through `pipeline.py → execution_gate.py` | `execution_router.py` is the primary entry; `pipeline.py` is a parallel entry that bypasses ExecutionGate | HIGH | `execution_router.py:1`, `runtime/router.py` |
| D-2 | RuntimeEnforcer failure = DENY | RuntimeEnforcer failure = silent pass | CRITICAL | `execution_router.py:50–51` |
| D-3 | StateRegister failure = DENY | StateRegister failure = silent pass | HIGH | `execution_router.py:58–59` |
| D-4 | TrustScoring failure = DENY | TrustScoring failure = silent pass | MEDIUM | `execution_router.py:74–75` |
| D-5 | Audit writes through `audit_manager → sovereign_audit_log` | `governance_kernel` writes to `AuditLog()` directly (lower tier, non-sovereign) | HIGH | `governance_kernel.py:~139–200` |
| D-6 | EvidenceBundle persisted to durable store | EvidenceBundle stored only in in-memory ring buffer (max 10,000; lost on restart) | HIGH | `evidence_bundle.py:_EVIDENCE_STORE` |
| D-7 | Triumvirate decisions audited | `governance.py Triumvirate._log_decision()` writes to in-memory list only | HIGH | `governance.py:_log_decision()` |
| D-8 | `AuditManager` is the sole audit write path | `AuditManager` has 1 production caller (`shadow_execution_plane.py`); main path bypasses it | HIGH | `audit_manager.py`, `shadow_execution_plane.py` |
| D-9 | `capability_authority.py` is the canonical token issuer | `capability_token.py` (HMAC-SHA256, dev secret) is called at Stage 6; `capability_authority.py` has zero production callers | HIGH | `execution_gate.py:Stage 6`, `capability_authority.py` |
| D-10 | `governance_manager.py` governs proposal lifecycle | `governance_manager.py` is fully stubbed; all 4 lifecycle methods are non-functional | MEDIUM | `governance_manager.py` |
| D-11 | `acceptance_ledger.py` is verified before execution | `runtime_enforcer.py` imports `acceptance_ledger` but RuntimeEnforcer can be silently bypassed in `execution_router` | HIGH | `execution_router.py:50–51` |
| D-12 | IronPathExecutor is downstream of ExecutionGate | `pipeline.py` calls IronPathExecutor directly in Phase 3, bypassing the gate | HIGH | `pipeline.py:~Phase 3` |

---

## 4. Silent Bypass Annotation

Three `except Exception: pass` blocks in `execution_router.py` can silently disable enforcement.

### Bypass B-1: RuntimeEnforcer (lines 50–51)

```python
# execution_router.py lines 37–51
try:
    from app.governance.runtime_enforcer import get_runtime_enforcer, EnforcementContext
    _enforce_ctx = EnforcementContext(
        user_id=context.get("user_id", "anonymous"),
        action=action,
        is_commercial=context.get("is_commercial", False),
        is_government=context.get("is_government", False),
        metadata=context,
    )
    _enforce_result = get_runtime_enforcer().enforce(_enforce_ctx)
    if _enforce_result.verdict == "deny":
        return False, f"RuntimeEnforcer denied: {_enforce_result.reason}"
except Exception:
    pass  # ← LINE 50–51
```

**What is bypassed:** PAGL prohibitions, consent requirements, tier entitlements, sovereign/commercial restrictions, and `acceptance_ledger` consultation. If `acceptance_ledger` data (e.g., missing INITIAL_MSA) would trigger a deny, that deny is suppressed.

**Trigger conditions:** Any `ImportError`, `AttributeError`, `FileNotFoundError`, `sqlite3.OperationalError`, or any unhandled exception in RuntimeEnforcer or its dependencies. A missing `data/legal/` directory is sufficient to trigger this bypass.

**Audit produced:** None. The bypass produces no EvidenceBundle, no log entry, no observable trace.

### Bypass B-2: StateRegister (lines 58–59)

```python
# execution_router.py lines 53–59
try:
    sr = get_state_register()
    temporal = sr.get_temporal_context()
    context = {**context, "_temporal": temporal}
except Exception:
    pass  # ← LINE 58–59
```

**What is bypassed:** Temporal context injection. The `_temporal` field (human gap data, session continuity hash, branch protection state) is not added to the context.

**Impact:** ExecutionGate stages that rely on `_temporal` for anti-gaslighting or branch-conflict detection receive incomplete context.

### Bypass B-3: TrustScoring / Adversarial Pattern Detection (lines 74–75)

```python
# execution_router.py lines 61–75
try:
    from app.core.tarl_operational_extensions import (
        TrustScoringEngine, AdversarialPatternRegistry,
    )
    _trust_score, _ = TrustScoringEngine().calculate_trust_score(...)
    _adv_flags = AdversarialPatternRegistry().detect_patterns(...)
    context = {**context, "_trust_score": ..., "_adversarial_flags": ...}
except Exception:
    pass  # ← LINE 74–75
```

**What is bypassed:** Trust score injection and adversarial pattern flags. The canonical `TrustThresholdInvariant` in `canonical/invariants.py` (validated by CI) checks `decisions` for destructive operations being authorized under low trust — but if no trust score is present in context, this invariant may not correctly detect violations.

### Contrast: Non-Silenced Gates

```python
# execution_router.py lines 77–82 — NOT silenced
invariant_engine = get_invariant_engine()
try:
    invariant_engine.validate(context)
except Exception as exc:
    return False, str(exc)  # ← returns False — hard fail
```

```python
# execution_router.py lines 84–86 — NOT silenced
gate = get_execution_gate()
gate_ok, gate_result = gate.execute(domain, action, context, executor_fn)
# any exception propagates to caller
```

The invariant engine and ExecutionGate are the only two hard gates that cannot be silenced by the current implementation.

---

## 5. GovernanceService `_auto_approve()` Path

`src/app/core/services/governance_service.py` contains a fallback approval path that operates as parallel implicit authority.

**Trigger conditions:**
- `GovernanceService` is instantiated without a `triumvirate` argument AND without a `governance_system` argument
- The action being evaluated has `risk_level in ["low", "routine"]`

**Behavior:** Returns `Decision(approved=True, reason="Auto-approved: routine/low-risk action", risk_level=...)` without consulting any governance council.

**Audit produced:** Appended to `self.decision_log` (in-memory dict). Not persisted. Not written to AuditManager. Not written to SovereignAuditLog.

**Where this path is active:** `cognition_kernel.py` uses `GovernanceService` in certain evaluation paths where the risk level is pre-classified as low before reaching the Triumvirate.

**Why this is a critical gap:** Any action classified as low-risk by the caller can bypass Triumvirate consultation entirely with no cryptographic trace. The auto-approve decision is not an EvidenceBundle, not auditable after restart, and not subject to any invariant check.

---

## 6. GovernanceKernel Audit Bypass

`governance_kernel.py` calls `app.governance.audit_log.AuditLog().log_event(...)` directly — not through `audit_manager.AuditManager`.

This means:
- Governance approval/denial decisions are logged to a lower-tier audit system
- The sovereign log (Ed25519-signed, Merkle-anchored, TSA-timestamped) does NOT receive a record of each Triumvirate decision
- There is no cryptographic chain of custody from governance decision → sovereign audit record

The intended path (per mission spec) is:

```
governance_kernel → audit_manager.log_governance_event() → sovereign_audit_log.log_event()
```

The actual path is:

```
governance_kernel → AuditLog().log_event()   [direct, non-sovereign]
```

---

## 7. Summary: What Is Hardened vs What Is Silenceable

### Hardened (cannot be bypassed by exception)

| Component | Hardening Mechanism |
|-----------|---------------------|
| `waterfall_filter` | Returns `(False, reason)` on deny — no exception path |
| `liara_ttl_check` | Direct call, no exception wrapper |
| `invariant_engine.validate()` | `except Exception as exc: return False, str(exc)` |
| `execution_gate.execute()` | Not wrapped; exception propagates to caller |
| ExecutionGate Stage 4: mutation_binding | `GovernanceBindingError` raised on violation — HARD FAIL |
| IronPathExecutor `evaluate_policy()` | Default-deny; conservative allow only for registry actions |

### Silenceable (can be disabled by exception)

| Component | Silence Mechanism | Impact if Silenced |
|-----------|------------------|--------------------|
| `runtime_enforcer.enforce()` | `except Exception: pass` line 50–51 | PAGL/consent/tier checks erased |
| `state_register.get_temporal_context()` | `except Exception: pass` line 58–59 | Anti-gaslighting context lost |
| `TrustScoringEngine` + `AdversarialPatternRegistry` | `except Exception: pass` line 74–75 | Trust/adversarial context lost |
| ML Triumvirate in `governance_kernel` | `except Exception: pass` on ML path | Only rule-based Triumvirate consults |
| NIRL Forge (post-gate) | `except Exception: logger.exception(...)` | Integrity warning suppressed |

### Structurally Bypassed (not on main execution path)

| Component | How It's Bypassed |
|-----------|------------------|
| `AuditManager` / `SovereignAuditLog` | Main path writes to `AuditLog()` directly |
| `CapabilityAuthority` (Ed25519) | ExecutionGate Stage 6 uses `CapabilityTokenService` (HMAC) |
| `ExecutionGate` (from pipeline.py path) | `runtime/router.py → pipeline.py` calls IronPathExecutor directly |
| `GovernanceManager` lifecycle | Fully stubbed; no callers; not wired to runtime enforcement |

---

## 8. Stop Conditions Active

The following stop conditions (per mission spec) are currently triggered:

| Stop Condition | Evidence | Location |
|----------------|----------|----------|
| Any audit write bypasses `audit_manager.py` | `governance_kernel.py` calls `AuditLog()` directly | `governance_kernel.py:~139–200` |
| Any execution path bypasses ExecutionGate | `pipeline.py` calls `iron_path_executor` directly | `pipeline.py Phase 3` |
| Any old token issuer remains active without compatibility-only constraints | `capability_token.py` (HMAC) is the active issuer; `capability_authority.py` (Ed25519) is unused | `execution_gate.py Stage 6` |
| Any code path executes without canonical lifecycle | `_auto_approve()` path executes without EvidenceBundle | `governance_service.py:344–386` |

These stop conditions block implementation work. They must be resolved (or explicitly scoped as shim-first) before any wiring work begins.

---

*Next report: [iron_path_2_receipts_convergence_map.md](iron_path_2_receipts_convergence_map.md)*
