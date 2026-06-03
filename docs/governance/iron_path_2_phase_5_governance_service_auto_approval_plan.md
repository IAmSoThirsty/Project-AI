# Iron Path 2.0 Phase 5: GovernanceService Auto-Approval Plan

Status: planning only. Do not implement until authorized.

## Scope

Phase 5 addresses only the fallback approval path in
`src/app/core/services/governance_service.py`.

Known stop condition:

- `GovernanceService._auto_approve()` can approve low-risk or routine actions
  when neither a Triumvirate nor a legacy governance system is configured.

Out of scope for Phase 5 unless separately authorized:

- Execution router hardening
- Capability bridge
- Audit spine implementation
- ExecutionGate internals
- EvidenceBundle schema
- GovernanceOutcome schema
- Pipeline, OctoReflex, and IronPathExecutor authority paths
- CognitionKernel's separate internal low-risk/default approval logic
- Canonical replay

## Files Inspected

- `src/app/core/services/governance_service.py`
- `src/app/core/governance.py`
- `src/app/core/governance_kernel.py`
- `src/app/core/execution_gate.py`
- `src/app/core/evidence_bundle.py`
- `src/app/governance/audit_manager.py`
- `src/app/core/cognition_kernel.py`
- `src/app/core/services/execution_service.py`
- `src/app/core/services/README.md`
- `src/app/core/shadow_execution_plane.py`
- `src/app/core/super_kernel.py`
- `tests/test_modular_services.py`
- `tests/test_cognition_kernel.py`
- `tests/test_governance_contract.py`
- `tests/test_execution_gate_enforcement.py`
- `tests/test_audit_manager.py`

## 1. Current `_auto_approve()` Behavior

`GovernanceService.evaluate_action()` chooses one of three paths:

1. `self.triumvirate` present: call `_evaluate_with_triumvirate()`.
2. `self.governance_system` present: call `_evaluate_with_governance_system()`.
3. Neither present: call `_auto_approve()`.

`_auto_approve()` currently:

- Treats `action.risk_level in ["low", "routine"]` as approvable.
- Returns a `Decision` with `approved=True` for low/routine risk.
- Returns a `Decision` with `approved=False` for other risk levels.
- Logs a warning through the standard logger.
- Does not call `ExecutionGate`.
- Does not call `EvidenceBundleWriter`.
- Does not call `AuditManager`.
- Does not reach `SovereignAuditLog`.
- Is recorded only by `_record_decision()` into `self.decision_log`, an
  in-memory list, and increments `approval_count` or `block_count`.

The returned `Decision` can be consumed by callers as an authorization. That is
the parallel-authority risk.

## 2. Conditions That Trigger Auto-Approval

The fallback is reached when all are true:

- `GovernanceService` is instantiated without `triumvirate`.
- `GovernanceService` is instantiated without `governance_system`.
- `evaluate_action(action, context, ...)` is called.
- `_auto_approve()` sees `action.risk_level` as `"low"` or `"routine"`.

The fallback blocks rather than approves when:

- `action.risk_level` is not `"low"` or `"routine"`.

Current tests construct this exact no-governance service with:

- `service = GovernanceService()`
- low-risk action in `tests/test_modular_services.py::test_auto_approve_low_risk`
- high-risk action in
  `tests/test_modular_services.py::test_block_high_risk_without_governance`

## 3. Whether Approval Reaches ExecutionGate

No.

`GovernanceService._auto_approve()` returns a `Decision` directly. No call path
from `_auto_approve()` reaches:

- `src/app/core/execution_router.py`
- `src/app/core/execution_gate.py`
- `GovernanceKernel.evaluate_action()`
- `ExecutionGate._emit_evidence_bundle()`

`CognitionKernel.enforce()` currently performs a router dry-run before its own
internal governance check, but that is not a `GovernanceService._auto_approve()`
receipt and does not make the service fallback itself safe.

## 4. Whether Approval Creates EvidenceBundle

No.

EvidenceBundle creation happens in:

- `ExecutionGate._emit_evidence_bundle()`
- Phase 4 router pre-gate hardening helper
- Direct tests of `EvidenceBundleWriter`

`GovernanceService` does not import or call `EvidenceBundleWriter`, and
`_auto_approve()` decisions are not attached to an EvidenceBundle `bundle_id`.

## 5. Whether Approval Reaches AuditManager Or SovereignAuditLog

No.

`GovernanceKernel._approve()` and `_reject()` now route through
`AuditManager.log_governance_decision()`, which can reach `SovereignAuditLog`
when sovereign mode is enabled.

`GovernanceService._auto_approve()` does not call:

- `get_audit_manager()`
- `AuditManager.log_governance_event()`
- `AuditManager.log_governance_decision()`
- `SovereignAuditLog`

The only durable-ish record is process-local `self.decision_log`, which is lost
on restart and is not cryptographic.

## 6. Current Tests Covering This Behavior

Direct GovernanceService tests:

- `tests/test_modular_services.py::TestGovernanceService::test_auto_approve_low_risk`
  currently expects `approved is True` and reason contains `"Auto-approved"`.
- `tests/test_modular_services.py::TestGovernanceService::test_block_high_risk_without_governance`
  expects `approved is False` for high risk.
- `tests/test_modular_services.py::TestGovernanceService::test_get_statistics`
  and `test_get_recent_decisions` verify in-memory decision tracking.

Related tests:

- `tests/test_cognition_kernel.py::TestCognitionKernel::test_low_risk_auto_approval`
  covers CognitionKernel's separate internal low-risk auto-approval path, not
  `GovernanceService._auto_approve()`.
- `tests/test_audit_manager.py` verifies AuditManager operational and sovereign
  decision logging, plus GovernanceKernel's AuditManager integration.
- `tests/test_governance_contract.py` verifies EvidenceBundle validity and
  contract outcomes, but does not assert anything about GovernanceService
  auto-approval.
- `tests/test_execution_gate_enforcement.py` verifies ExecutionGate behavior,
  not GovernanceService fallback behavior.

Coverage gap:

- No test currently proves that `GovernanceService._auto_approve()` reaches
  ExecutionGate, EvidenceBundle, AuditManager, or SovereignAuditLog.
- No test currently proves that low/routine no-governance service fallback is
  non-authoritative.

## 7. Proposed Repair Options

### Option A: Disable Auto-Approval

Change `_auto_approve()` so it never returns `approved=True`.

Behavior:

- Low/routine no-governance fallback returns `approved=False`.
- Reason says governance is unavailable and the decision is fail-closed.
- Existing `_record_decision()` still records the decision in memory.

Pros:

- Smallest behavior change.
- Eliminates the positive parallel authority immediately.
- Does not touch ExecutionGate, EvidenceBundle schema, AuditManager, router,
  capability bridge, pipeline, OctoReflex, or IronPathExecutor.
- Keeps `GovernanceService` aligned with "governance observes, never executes."

Cons:

- Does not itself create an EvidenceBundle.
- Does not itself reach AuditManager/SovereignAuditLog.
- Changes existing tests that expect low-risk auto-approval.
- Leaves a local deny decision that is still only in memory.

### Option B: Route Through ExecutionGate/EvidenceBundle/AuditManager

When no governance is configured, call a canonical dry-run path before returning
a decision.

Possible shapes:

- Direct `ExecutionGate.execute(...)` with a no-op executor.
- Better, but broader, call `execution_router.execute(...)` with a no-op
  executor so RuntimeEnforcer, StateRegister, trust/adversarial, invariants, and
  ExecutionGate all run.

Pros:

- Produces EvidenceBundle/observability if the gate path is reached.
- Reaches `GovernanceKernel`, whose approval/denial path uses AuditManager.
- Converts fallback approval into a receipt-producing path.

Cons:

- Makes `GovernanceService` another gate/router caller.
- Risks broadening execution authority topology instead of shrinking it.
- A no-op gate execution is not the actual downstream effect.
- Could duplicate receipts when a caller already performed router/gate dry-run.
- May require careful recursion/caller-map tests.
- Touching this path before execution-authority consolidation may create a new
  direct gate entry that bypasses the Phase 4 router pre-gate hardening unless
  the router is used instead of `ExecutionGate` directly.

### Option C: Downgrade To Non-Authoritative Recommendation

Keep `_auto_approve()` as a local classifier, but make it unable to authorize
execution.

Behavior:

- Low/routine fallback returns `approved=False`.
- Reason says "non-authoritative recommendation only" or "governance
  unavailable; authoritative approval required".
- Optional metadata remains inside the existing `Decision` fields only; no
  public schema change.
- High-risk fallback remains denied.

Pros:

- Eliminates positive authority.
- Makes the service fallback explicitly advisory.
- Avoids a new direct ExecutionGate/router caller.
- Avoids public schema changes.
- Keeps implementation scoped to `governance_service.py` and tests.

Cons:

- Like Option A, does not create EvidenceBundle by itself.
- Existing auto-approve tests must change.
- Callers that relied on low-risk service fallback must provide explicit
  Triumvirate/governance system or route through the canonical execution path.

## 8. Recommended Repair

Recommended Phase 5 repair: **Option C, implemented as fail-closed
non-authoritative fallback.**

Concrete recommendation:

- Rename behavior in comments/reasoning from auto-approval to
  non-authoritative fallback.
- Keep the private method if needed for compatibility, but make it return
  `approved=False` for all no-governance cases.
- For low/routine actions, use a reason such as:
  `"Governance unavailable: low-risk recommendation is non-authoritative; canonical approval required"`.
- For high-risk actions, keep denial semantics with a reason that governance is
  required.
- Do not add fields to `Decision`.
- Do not change `GovernanceOutcome`.
- Do not change `EvidenceBundle`.
- Do not touch ExecutionGate.
- Do not touch AuditManager internals.

Why this is recommended:

- The immediate risk is an unreceipted positive authority. Removing positive
  approval is safer than adding a new gate caller from an advisory service.
- `GovernanceService` documentation says governance observes and never executes.
  Routing a no-op execution through the gate from this service blurs that
  boundary.
- ExecutionGate/EvidenceBundle/AuditManager wiring should remain on canonical
  execution paths. GovernanceService fallback should stop pretending to be a
  substitute for those paths.

Follow-up coordination item:

- CognitionKernel has a separate internal low-risk/default approval path in
  `_check_governance()`. It is not the same as
  `GovernanceService._auto_approve()`, but it is an adjacent authority concern.
  Do not repair it in Phase 5 unless the scope is explicitly expanded.

## 9. Tests Required Before Implementation

Run before implementation from a clean tree:

```powershell
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_modular_services.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_cognition_kernel.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_governance_contract.py tests/test_evidence_bundle.py tests/test_governance_observability.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_audit_manager.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_execution_gate_enforcement.py -v
```

Do not run `canonical/replay.py` unless separately authorized.

New or updated tests required:

1. `GovernanceService()` with no Triumvirate/governance system and low risk
   returns `approved=False`.
2. Low-risk no-governance reason explicitly says non-authoritative or canonical
   approval required.
3. Routine no-governance action also returns `approved=False`.
4. High-risk no-governance action remains blocked.
5. `approval_count` does not increment for no-governance fallback.
6. `block_count` increments for no-governance fallback.
7. `decision_log` still records the fallback decision for local visibility.
8. Triumvirate path still approves when Triumvirate approves.
9. Legacy governance_system path still approves when legacy system allows.
10. No test requires adding public fields to `Decision`.
11. No test requires changing EvidenceBundle or GovernanceOutcome schemas.
12. A direct assertion should document that this service fallback does not
    produce an EvidenceBundle and is therefore not an approval source.

If Phase 5 instead chooses Option B, additional tests are required:

- Router/gate dry-run is called exactly once.
- EvidenceBundle is produced for allowed and denied fallback evaluations.
- AuditManager receives the GovernanceKernel decision.
- No direct ExecutionGate call bypasses Phase 4 router hardening.
- No duplicate receipt is produced when caller already routed through the
  canonical execution path.

## 10. Stop Conditions Before Implementation

Stop before implementation if any of these are true:

- The repair requires changing `Decision` public schema.
- The repair requires changing `GovernanceOutcome`.
- The repair requires changing EvidenceBundle schema or valid outcomes.
- The repair requires touching `ExecutionGate`.
- The repair requires touching router hardening.
- The repair requires touching capability bridge files.
- The repair requires touching audit spine internals.
- The repair requires modifying pipeline, OctoReflex, or IronPathExecutor.
- The repair requires solving CognitionKernel's separate auto-approval path in
  the same commit.
- Tests demand that `GovernanceService()` with no governance keeps approving
  low-risk or routine actions.
- A caller cannot tolerate fail-closed no-governance fallback and no explicit
  authoritative replacement is provided.

## 11. Exact Implementation Sequence

Recommended Option C sequence:

1. Confirm clean working tree.
2. Run the required baseline tests.
3. Update or add focused tests in `tests/test_modular_services.py`:
   - change low-risk no-governance expectation from approved to denied
   - add routine no-governance denied case
   - assert non-authoritative reason
   - assert counters and decision_log behavior
4. Run `tests/test_modular_services.py` and confirm the new tests fail against
   current code.
5. Modify only `src/app/core/services/governance_service.py`:
   - update `_auto_approve()` comments/docstring to describe fail-closed
     non-authoritative fallback
   - return `approved=False` for low/routine no-governance cases
   - keep high-risk blocked
   - avoid importing ExecutionGate, EvidenceBundle, or AuditManager
6. Run focused tests:
   - `tests/test_modular_services.py -v`
7. Run governance regressions:
   - `tests/test_cognition_kernel.py -v`
   - `tests/test_governance_contract.py tests/test_evidence_bundle.py tests/test_governance_observability.py -v`
   - `tests/test_audit_manager.py -v`
   - `tests/test_execution_gate_enforcement.py -v`
8. Run `git diff --check`.
9. Run `git status --short`.

## Implementation Authorization Assessment

Phase 5 implementation is safe to authorize if the authorized repair is the
router/gate-neutral Option C: fail-closed, non-authoritative fallback in
`GovernanceService` only, plus focused tests.

Exact blockers before authorization:

- Confirm that changing `tests/test_modular_services.py::test_auto_approve_low_risk`
  from approval to fail-closed denial is acceptable.
- Confirm that Phase 5 should not also fix CognitionKernel's separate low-risk
  auto-approval/default approval path.
- Confirm whether the method name `_auto_approve()` may remain as compatibility
  plumbing or should be renamed in a later cleanup phase.
