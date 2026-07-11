# Governance Contract

**Version:** 1.0.0
**Branch:** 05-09-26-Structural-upgrades
**Status:** Binding

---

## Definition

The Governance Contract is the set of invariants that the system guarantees for every governed execution. A system that violates any point of this contract is not in a governed state — it must HALT or escalate to human review.

This contract is machine-verified by `tests/test_governance_contract.py`. All 10 points must pass before any release.

---

## The Ten Points

### 1. Admissible
Every request submitted for execution must first be evaluated against the current governance configuration. A request that has not been evaluated is inadmissible. No execution path bypasses admissibility check.

**Enforced by:** `ExecutionGate` stage 1 (kernel evaluation); `SafeAllowCalibrationLayer.evaluate()` returns `GovernanceResult` for every request without exception.

**Violation behavior:** Unevaluated requests are denied by construction — the gate has no "pass-through" mode.

---

### 2. Invariant-Preserving
Execution proceeds only when all registered invariants are satisfied at or below WARN severity. BLOCK, HALT, or ESCALATE severity invariants stop execution unconditionally.

**Enforced by:** `InvariantSeverity` ordinal comparison; `ExecutionGate` stage 8 (final invariant check).

**Violation behavior:** BLOCK → DENY. HALT → HALT (immediate stop). ESCALATE → ESCALATE (council required).

---

### 3. Continuity-Maintaining
The governance state chain is a hash-linked sequence. No execution may proceed if the predecessor hash does not match the current chain head. Forks are detected and immediately rejected.

**Enforced by:** `StateBranchingProtector.advance()` with threading.Lock; monotonic `global_sequence_number`; `BranchConflictError` on mismatch.

**Violation behavior:** `BranchConflictError` raised — execution does not proceed. Error message explicitly states: "HALT or ESCALATE. Council adjudication required."

---

### 4. Cryptographically Bound
Every policy authorization is signed. Every capability token is HMAC-authenticated. Every evidence bundle contains a content hash. Signature verification is mandatory — not advisory.

**Enforced by:** `PolicyRecord.verify_signature()`; `CapabilityTokenService.verify()` HMAC check; `EvidenceBundle.bundle_hash()`.

**Violation behavior:** Signature failure → DENY immediately; token HMAC failure → DENY; forged continuity invariant at HALT.

---

### 5. Auditable
Every governed execution — ALLOW, DENY, DEGRADED, HALT, ESCALATE, or any other outcome — produces an evidence bundle. There is no silent success and no silent failure.

**Enforced by:** `EvidenceBundleWriter.build()` called in `ExecutionGate._emit_evidence_bundle()` for all outcome paths; bundle includes outcome, reason, policy version, policy hash, timestamp, and content hash.

**Violation behavior:** If evidence bundle write fails, the failure is logged at CRITICAL severity. The outcome is still recorded in the observation collector.

---

### 6. Instance-Authorized
Policy-level permission (PolicyDecision) is necessary but not sufficient. Each specific execution instance must be separately authorized by a valid, non-replayed, non-expired, scope-matched capability token.

**Enforced by:** `ExecutionAuthorizationEvaluator` (separate from `PolicyDecisionEvaluator`); 8-guard chain in `execution_authorization.py`.

**Violation behavior:** Any guard failure → DENY with specific reason; no partial authorization.

---

### 7. Capability-Token-Scoped
Capability tokens are short-lived (TTL ≤ 300s), one-time-use, and bound to: action type, scope list, context hash, and policy hash. A token that matches on action but not scope, or that has been used before, is invalid.

**Enforced by:** `CapabilityTokenService.verify()` checks in order: replay → TTL → HMAC → action → scope → context_hash → policy_hash.

**Violation behavior:** Any binding mismatch → verification failure → DENY at authorization stage.

---

### 8. Policy-Version-Respecting
Execution is authorized against a specific policy version. If the active policy has changed since the authorization decision was made, the execution must be re-evaluated against the new policy. Stale policy hash bindings are rejected.

**Enforced by:** `ExecutionAuthorizationEvaluator` guard 8 (policy hash binding); `PolicyRegistry.human_gap_check()` for epochal capability expansions.

**Violation behavior:** Policy hash mismatch → DENY with `"policy_hash_binding_violation"` reason.

---

### 9. Evidence-Bundle-Producing
Evidence bundles are not optional instrumentation — they are a required output of governance. Every bundle includes: outcome, reason, action, context hash, policy version, policy hash, timestamp, audit chain hash (linking to predecessor bundle), and content hash of the bundle itself.

**Enforced by:** `EvidenceBundleWriter.build()` auto-populates policy metadata from active registry when not supplied by caller; `audit_chain_next` field links bundles into a chain.

**Violation behavior:** Missing required fields cause build to raise; caller must supply action and context at minimum.

---

### 10. Safely-Degrading
When full governance is unavailable (kernel degraded, TSA unavailable, registry partially failed), the system does not fail open. It enters a constrained degraded mode where only read-classified actions are permitted. Mutating actions require human approval. The system never silently permits more than its current governance capacity supports.

**Enforced by:** `GovernanceMode.DEGRADED`; `classify_action_mutability()`; `DegradedModeEvaluator.evaluate()`; `PERMITTED_OUTCOMES = {DEGRADED_READ_ONLY, CLARIFY, DENY}`; `LiaraFallbackAuthority.AUTHORITY_LEVEL = "REDUCED"`.

**Violation behavior:** Mutating action in degraded mode → `HUMAN_APPROVAL_REQUIRED` (never ALLOW).

---

## Contract Verification

```bash
# Verify all 10 contract points:
PYTHONPATH=src python -m pytest tests/test_governance_contract.py -v

# Full system verification (all 19 upgrade test files):
PYTHONPATH=src python -m pytest tests/test_safe_allow_calibration.py \
  tests/test_conversation_threat_register.py tests/test_threat_model.py \
  tests/test_authorization_separation.py tests/test_capability_tokens.py \
  tests/test_policy_registry.py tests/test_invariant_severity.py \
  tests/test_governance_mode.py tests/test_evidence_bundle.py \
  tests/test_degraded_mode.py tests/test_governance_liveness.py \
  tests/test_replay_protection.py tests/test_governance_observability.py \
  tests/test_policy_mutation_control.py tests/test_semantic_collision.py \
  tests/test_state_branching.py tests/test_genesis_reanchor.py \
  tests/test_time_trust.py tests/test_governance_contract.py -v
```

Expected: **186 passed, 0 failed.**

---

## Contract Amendments

Contract amendments require:
1. A failing test that demonstrates why the current contract is insufficient
2. A new or modified contract point with explicit enforcement mechanism
3. Updated `test_governance_contract.py` covering the new point
4. Human review sign-off before merge

The contract may only be strengthened. Amendments that weaken any existing point are rejected by the governance-weakening detection in `PolicyRegistry`.
