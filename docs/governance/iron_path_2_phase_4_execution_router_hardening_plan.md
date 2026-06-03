# Iron Path 2.0 Phase 4: Execution Router Silent Bypass Hardening Plan

Status: planning only. Do not implement until authorized.

## Scope

Phase 4 addresses only the silent failure handling inside
`src/app/core/execution_router.py`.

Authorized planning target:

- RuntimeEnforcer failure handling
- StateRegister temporal context failure handling
- Trust scoring and adversarial pattern failure handling

Out of scope for Phase 4:

- ExecutionGate behavior
- Capability authority bridge
- Audit spine wiring
- `pipeline.py`
- OctoReflex
- IronPathExecutor
- Execution authority consolidation
- Canonical replay

## Files Inspected

- `src/app/core/execution_router.py`
- `src/app/governance/runtime_enforcer.py`
- `src/app/core/state_register.py`
- `src/app/core/tarl_operational_extensions.py`
- `src/app/core/evidence_bundle.py`
- `src/app/core/governance_observability.py`
- `src/app/core/execution_gate.py`
- `src/app/core/governance_outcomes.py`
- `src/app/core/degraded_mode.py`
- `tests/test_evidence_bundle.py`
- `tests/test_governance_contract.py`
- `tests/test_governance_observability.py`
- `tests/test_degraded_mode.py`
- `tests/test_state_register_continuity_hash.py`
- `tests/test_execution_gate_enforcement.py`
- `tests/test_api.py`
- `tests/test_time_trust.py`

No dedicated `tests/test_execution_router.py` or direct router hardening test
file was found.

## 1. Current Silent Bypass Paths

| Path | Current code shape | What disappears |
| --- | --- | --- |
| RuntimeEnforcer | `try: get_runtime_enforcer().enforce(...)` followed by `except Exception: pass` | Import, singleton construction, ledger access, and enforcement exceptions disappear. Execution continues without a RuntimeEnforcer receipt. |
| StateRegister temporal context | `try: get_state_register().get_temporal_context()` followed by `except Exception: pass` | StateRegister construction and temporal context exceptions disappear. Execution continues without `_temporal`. |
| Trust/adversarial context | `try: TrustScoringEngine().calculate_trust_score(...)` and `AdversarialPatternRegistry().detect_patterns(...)` followed by `except Exception: pass` | Trust scoring and adversarial scan exceptions disappear. Execution continues without `_trust_score` or `_adversarial_flags`. |

## 2. Exact Current Failure Behavior

### RuntimeEnforcer

Current behavior:

1. Router builds `EnforcementContext`.
2. Router calls `get_runtime_enforcer().enforce(...)`.
3. If the enforcer returns `verdict == "deny"`, execution is denied.
4. If any exception occurs before or during enforcement, the exception is
   swallowed.
5. Invariant checks and `ExecutionGate.execute(...)` still run.
6. The executor may run if later gates allow it.

This contradicts RuntimeEnforcer's local fail-closed posture. The enforcer
itself denies on some internal check errors, but router-level import, init, or
call failures are silent.

### StateRegister Temporal Context

Current behavior:

1. Router calls `get_state_register()`.
2. Router calls `sr.get_temporal_context()`.
3. On success, router adds `"_temporal": temporal` to context.
4. If any exception occurs, the exception is swallowed.
5. Later gates receive context without `_temporal`.
6. The executor may run if later gates allow it.

Important distinction: `StateRegister.get_temporal_context()` returns
`{"error": "No active session"}` when no session is active. That is not an
exception and is currently still injected into context. Phase 4 should not
silently reinterpret this as an exception without a test-backed decision.

### Trust Scoring And Adversarial Pattern Detection

Current behavior:

1. Router imports `TrustScoringEngine` and `AdversarialPatternRegistry`.
2. Router computes a default trust score for the current user.
3. Router scans `context["payload"]` for adversarial patterns.
4. On success, router adds `_trust_score` and `_adversarial_flags`.
5. If either trust scoring or adversarial scanning raises, the exception is
   swallowed.
6. Later gates receive no trust/adversarial signals.
7. The executor may run if later gates allow it.

Detected adversarial flags are currently only context enrichment in this router.
Changing the semantics of detected flags is not part of Phase 4.

## 3. Proposed Repair For Each Bypass

Phase 4 should not add a new public governance outcome unless explicitly
authorized. `EvidenceBundleValidator` and `GovernanceOutcome` currently accept:

- `ALLOW`
- `DENY`
- `CLARIFY`
- `HUMAN_APPROVAL_REQUIRED`
- `DEGRADED_READ_ONLY`
- `HALT`
- `ESCALATE`

`BYPASS_RECORDED` is not currently a valid `EvidenceBundle.final_outcome`.
Using it as a literal final outcome would be a schema and contract change.

### Router-local receipt helper

Smallest safe future implementation:

- Add a small private helper inside `execution_router.py` only.
- The helper emits an `EvidenceBundle` and a `GovernanceObservation` for
  pre-gate router failures.
- Use existing valid final outcomes only:
  - `DENY` for fail-closed paths.
  - `DEGRADED_READ_ONLY` for explicitly safe degraded paths.
- Put router-specific details in observability metadata, such as:
  - `router_precheck`
  - `failure_source`
  - `failure_mode`
  - `bypass_recorded: true`
  - `non_authoritative_warning: true`
- If evidence emission fails on a degraded path, fail closed. Degraded
  continuation without a receipt would reproduce the original problem.

If the project requires a literal `BYPASS_RECORDED` final outcome, stop before
implementation and authorize an EvidenceBundle/GovernanceOutcome contract
change with dedicated tests.

### RuntimeEnforcer

Recommended repair: fail closed.

Behavior:

- Any RuntimeEnforcer import, singleton init, context construction, or
  `enforce(...)` exception returns:
  - `False`
  - reason beginning with `RuntimeEnforcer failed closed:`
- The executor must not be called.
- Emit a pre-gate EvidenceBundle with `final_outcome="DENY"`.
- Emit a GovernanceObservation with metadata identifying the RuntimeEnforcer
  precheck failure.

Rationale:

RuntimeEnforcer covers consent, PAGL prohibitions, sovereign use, commercial
license, and tier checks. It is authoritative enough that unavailability must
not become implicit permission.

### StateRegister Temporal Context

Recommended repair: block protected execution, degrade only for explicit
read-only actions.

Behavior:

- If `get_state_register()` or `get_temporal_context()` raises and the action is
  mutating, high-impact, government, commercial, protected by capability token,
  or context says `requires_continuity`, return `False` and do not call the
  executor.
- Emit a pre-gate EvidenceBundle with `final_outcome="DENY"`.
- If the action is explicitly read-only by `classify_action_mutability(...)`,
  may continue only as a recorded degraded path:
  - inject `_temporal` with an explicit unavailable marker
  - inject a router bypass marker
  - set reduced-authority context metadata
  - emit `final_outcome="DEGRADED_READ_ONLY"` evidence or ensure the later gate
    emits an equivalent receipt
- If mutability classification itself fails, fail closed.

Rationale:

Temporal continuity is part of the constitutional substrate. A missing temporal
receipt should not authorize state-changing execution. Read-only diagnostics can
continue only when the degraded state is visible and receipted.

### Trust Scoring And Adversarial Pattern Detection

Recommended repair: fail closed for protected or payload-bearing execution;
degrade only for low-risk read-only diagnostics.

Behavior:

- If trust/adversarial enrichment fails for mutating, protected, high-impact,
  government, commercial, or payload-bearing actions, return `False` and do not
  call the executor.
- Emit a pre-gate EvidenceBundle with `final_outcome="DENY"`.
- If the action is explicitly read-only and has no meaningful payload, degraded
  continuation may be allowed only with:
  - `_trust_score_unavailable: true`
  - `_adversarial_flags_unavailable: true`
  - router bypass metadata
  - `DEGRADED_READ_ONLY` evidence/observation
- If only one of trust scoring or adversarial scanning fails, record the exact
  failed subcomponent and keep the successful signal.
- Do not add new blocking behavior for successfully detected adversarial flags
  in Phase 4; that is a separate authority decision.

Rationale:

The trust/adversarial step is enrichment today, but silently removing it from a
payload-bearing or mutating request creates invisible risk drift. Low-risk
read-only diagnostics may degrade safely if the missing signal is recorded.

## 4. Paths That Should Block Execution

Block before `ExecutionGate.execute(...)` and do not call `executor_fn` when:

- RuntimeEnforcer raises for any governed request.
- StateRegister temporal context raises for:
  - mutating actions
  - high-impact actions
  - government or commercial actions
  - actions requiring capability tokens
  - contexts marked `requires_continuity`
  - unknown mutability
- Trust/adversarial enrichment raises for:
  - mutating actions
  - protected actions
  - high-impact actions
  - government or commercial actions
  - payload-bearing actions
  - unknown mutability
- Evidence/observability emission fails on any degraded-continuation path.

## 5. Paths That May Degrade Safely

Degrade only when all of the following are true:

- Action is explicitly read-only.
- Context is not high-impact, government, commercial, or protected.
- Context does not require continuity.
- Missing subsystem is not RuntimeEnforcer.
- Router can emit a receipt using existing outcomes.
- The degraded state is injected into context for later gates and audit.

Candidate degraded paths:

- StateRegister exception during an explicit read-only status or inspection
  action.
- Trust/adversarial exception during an explicit read-only diagnostic action
  with no meaningful payload.

## 6. EvidenceBundle And Audit Requirements

Pre-gate router denials and degraded continuations happen before ExecutionGate
Stage 9, so the router needs its own narrow receipt emission path unless the
request is allowed to reach the gate.

Required receipt properties:

- EvidenceBundle is produced for each pre-gate deny.
- GovernanceObservation is produced for each pre-gate deny or degraded router
  continuation.
- `final_outcome` uses only currently valid outcomes.
- Failure source is visible in observation metadata.
- Request hash is deterministic and does not include raw sensitive payloads.
- Denied paths never call `executor_fn`.
- Degraded paths include explicit context markers.
- Evidence emission failures are not swallowed when execution would otherwise
  continue.

Do not use literal `BYPASS_RECORDED` as an EvidenceBundle final outcome unless
the governance outcome contract is updated and tested.

## 7. Tests Required Before Implementation

Run these before implementation from a clean tree:

```powershell
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_execution_gate_enforcement.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_governance_contract.py tests/test_evidence_bundle.py tests/test_governance_observability.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_degraded_mode.py tests/test_state_register_continuity_hash.py tests/test_time_trust.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_api.py -v
```

Do not run `canonical/replay.py` unless separately authorized.

## 8. New Tests Required

Create a focused router hardening test file, for example
`tests/test_execution_router_hardening.py`.

Required tests:

1. RuntimeEnforcer import or lookup failure denies execution and does not call
   the executor.
2. RuntimeEnforcer `enforce(...)` exception denies execution and records
   pre-gate evidence.
3. RuntimeEnforcer explicit deny behavior remains unchanged.
4. StateRegister exception denies mutating execution and does not call the
   executor.
5. StateRegister exception on explicit read-only action records degraded
   evidence and passes explicit degraded markers to the gate.
6. StateRegister `{"error": "No active session"}` success path remains explicit
   context, not a silent exception.
7. Mutability classification failure during StateRegister handling fails
   closed.
8. Trust scoring failure denies payload-bearing or mutating execution.
9. Adversarial registry failure denies payload-bearing or mutating execution.
10. Trust/adversarial failure on explicit low-risk read-only diagnostic action
    records degraded markers and evidence.
11. Partial trust/adversarial failure preserves the successful signal and
    records the failed subcomponent.
12. Successful router path still injects `_temporal`, `_trust_score`, and
    `_adversarial_flags`.
13. Router degraded paths do not use invalid EvidenceBundle outcomes.
14. Evidence emission failure prevents degraded continuation.
15. `ExecutionGate.execute(...)` is not reached on fail-closed pre-gate
    failures.

Regression tests to keep passing:

- `tests/test_execution_gate_enforcement.py`
- `tests/test_governance_contract.py`
- `tests/test_evidence_bundle.py`
- `tests/test_governance_observability.py`
- `tests/test_degraded_mode.py`
- `tests/test_state_register_continuity_hash.py`
- `tests/test_api.py`

## 9. Files That Would Need Modification

Likely implementation files:

- `src/app/core/execution_router.py`
- `tests/test_execution_router_hardening.py`

Possible only if required by tests and explicitly authorized:

- `tests/test_governance_contract.py`
- `tests/test_evidence_bundle.py`
- `tests/test_governance_observability.py`

Do not modify in Phase 4 without separate authorization:

- `src/app/core/execution_gate.py`
- `src/app/core/capability_authority_bridge.py`
- `src/app/core/capability_token.py`
- `src/psia/canonical/capability_authority.py`
- `src/app/core/governance/pipeline.py`
- `src/app/core/octoreflex.py`
- `src/app/core/governance/iron_path_executor.py`
- audit spine files from Phase 2

## 10. Stop Conditions Before Implementation

Stop before implementation if any of these are true:

- A literal `BYPASS_RECORDED` EvidenceBundle outcome is required.
- The repair requires changing `GovernanceOutcome` or EvidenceBundle public
  schema without explicit authorization.
- The repair requires touching ExecutionGate, capability bridge, audit manager,
  pipeline, OctoReflex, or IronPathExecutor.
- The implementation cannot determine mutating versus read-only behavior with
  existing `classify_action_mutability(...)`.
- RuntimeEnforcer unavailability is proposed to degrade instead of fail closed.
- Degraded continuation cannot produce evidence.
- Tests would need to alter ALLOW/DENY semantics outside the three router
  precheck failure paths.
- A detected adversarial flag policy change becomes necessary.
- Canonical replay is requested implicitly rather than explicitly authorized.

## 11. Recommended Implementation Sequence

1. Confirm clean working tree.
2. Run the required baseline tests listed above.
3. Add `tests/test_execution_router_hardening.py` with failing tests for the
   three silent bypass classes.
4. Add the smallest private receipt helper in `execution_router.py`.
5. Replace RuntimeEnforcer `except Exception: pass` with fail-closed deny and
   receipt emission.
6. Replace StateRegister `except Exception: pass` with block-or-degrade logic
   using existing mutability classification.
7. Replace trust/adversarial `except Exception: pass` with block-or-degrade
   logic and explicit context markers.
8. Keep successful injection behavior unchanged.
9. Run focused router hardening tests.
10. Run existing governance contract, evidence, observability, degraded mode,
    StateRegister, ExecutionGate, and API tests.
11. Run `git diff --check` and `git status --short`.

## Implementation Authorization Assessment

Phase 4 is technically safe to authorize only as a tests-first,
router-local change that uses existing governance outcomes and does not touch
ExecutionGate or the capability/audit authority paths.

Remaining blockers before authorization:

- Decide whether `BYPASS_RECORDED` is only observation metadata or a new public
  final outcome. The current contract does not allow it as a final outcome.
- Confirm that RuntimeEnforcer failures must fail closed for every governed
  request.
- Confirm the proposed degraded set for StateRegister and trust/adversarial
  failures is acceptable.
- Add direct router tests before source changes.
