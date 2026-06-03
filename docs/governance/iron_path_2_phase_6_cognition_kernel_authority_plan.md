# Iron Path 2.0 Phase 6: CognitionKernel Authority Plan

Status: planning only. Do not implement until authorized.

## Scope

Phase 6 addresses only the authority behavior inside
`src/app/core/cognition_kernel.py`.

Known concern:

- `CognitionKernel._check_governance()` has a separate low-risk/default
  approval path that was not changed by Phase 5.

Out of scope for Phase 6 unless separately authorized:

- Phase 5 GovernanceService implementation
- Execution router hardening
- Capability authority bridge
- Audit spine internals
- ExecutionGate internals
- EvidenceBundle schema
- GovernanceOutcome schema
- Pipeline, OctoReflex, and IronPathExecutor authority consolidation
- Canonical replay

## Planning Contract

- Language/runtime: Python 3.12 in the existing Project-AI test harness.
- Environment: Windows/PowerShell with `PYTHONPATH=src`.
- Input contract: existing `CognitionKernel.process()` and `route()` tasks that
  produce `Action`, `ExecutionContext`, `Decision`, and `ExecutionResult`
  objects.
- Output contract for this phase: a plan only. No source behavior changes.
- Security constraints: no new public schemas, no silent authority expansion, no
  local approval when canonical governance is unavailable.
- Dependency constraints: prefer existing router, gate, audit, and evidence APIs;
  do not introduce a new governance dependency unless tests prove it is needed.
- Edge cases to cover before implementation: router exception, local governance
  exception, Triumvirate exception, no local governance, low-risk no-approval,
  high-risk requires-approval, blocked action commit, and existing approved
  local-governance path.

## Files Inspected

- `src/app/core/cognition_kernel.py`
- `tests/test_cognition_kernel.py`
- `src/app/core/services/governance_service.py`
- `src/app/core/services/README.md`
- `src/app/core/services/execution_service.py`
- `src/app/core/services/memory_logging_service.py`
- `src/app/core/governance_kernel.py`
- `src/app/core/execution_gate.py`
- `src/app/core/execution_router.py`
- `src/app/core/evidence_bundle.py`
- `src/app/governance/audit_manager.py`
- `src/app/governance/sovereign_audit_log.py`
- `src/app/core/kernel_integration.py`
- `src/app/core/governance/pipeline.py`
- `src/app/core/governance/iron_path_executor.py`
- `tests/test_modular_services.py`
- `tests/test_kernel_enhancements.py`
- `tests/test_governance_contract.py`
- `tests/test_execution_gate_enforcement.py`
- `tests/test_audit_manager.py`
- `tests/test_evidence_bundle.py`
- `tests/test_execution_router_hardening.py`
- `tests/test_governance_server.py`

## 1. Current CognitionKernel Approval/Default Behavior

`CognitionKernel.process()` currently creates an `ExecutionContext`, enters a
kernel context, and runs:

1. `enforce(context.proposed_action, context)`
2. `act(context.proposed_action, context)`
3. `reflect(context)`
4. `post_evaluate(context)`
5. `commit(context)`

`enforce()` performs three authority-related steps:

1. Builds a `PolicyEvaluationRequest`.
2. Attempts a canonical governance dry-run through
   `app.core.execution_router.execute(...)` with `executor_fn=lambda _ctx: None`.
3. Always falls through to local `_check_governance()` unless the router returns
   an explicit denial.

Important current behavior:

- If the router dry-run returns `allowed=False`, `enforce()` raises
  `ConstitutionalFault`.
- If the router dry-run raises any non-`ConstitutionalFault` exception,
  `enforce()` silently catches it and falls through to local governance.
- `_check_governance()` can then approve locally.
- `act()` executes the real action callable after local approval. The real
  action is not executed by `ExecutionGate`; only the dry-run no-op passed
  through the router/gate path.

`_check_governance()` currently chooses:

1. Low-risk shortcut:
   - If `requires_approval` is false or absent and `risk_level == "low"`,
     return `approved=True`.
   - Reason: `"Auto-approved (low risk, no approval required)"`.
   - This shortcut runs before `self.governance_system` and `self.triumvirate`,
     so it shadows configured local governance for low-risk no-approval actions.
2. Local governance system:
   - If `self.governance_system.validate_action(...)` exists and returns,
     use its `allowed` value.
   - If it raises, log the exception and continue.
3. Local Triumvirate:
   - If `self.triumvirate.process(...)` returns, use its `success` value.
   - If it raises, log the exception and continue.
4. Default approval:
   - If no previous path returned, log a warning and return `approved=True`.
   - Reason: `"No governance system configured (approved by default)"`.

`commit()` then records:

- in-process execution history,
- optional memory engine records,
- optional episodic memory,
- an IronPathExecutor decision record with request/response binding, hash chain,
  HMAC signature, and `decision_record_id`.

The IronPathExecutor decision record is a receipt, but it is not an
EvidenceBundle and is not the Phase 2 AuditManager/SovereignAuditLog path.

## 2. Conditions That Trigger Low-Risk/Default Approval

### Low-risk shortcut

The low-risk shortcut is triggered when:

- task or metadata has `requires_approval=False`, or omits it and defaults to
  false, and
- `risk_level == "low"`.

This applies to both:

- dict tasks with `_action_callable`, where `_interpret_input()` reads
  `user_input.get("requires_approval", False)` and
  `user_input.get("risk_level", "low")`,
- simple inputs, where `_interpret_input()` reads
  `metadata.get("requires_approval", False)` and
  `metadata.get("risk_level", "low")`.

Because the shortcut precedes local governance checks, it can approve even when
a `governance_system` or `triumvirate` is configured.

### Default approval

The default approval is triggered when:

- the low-risk shortcut does not return,
- no local `governance_system` is configured, or it lacks/raises from
  `validate_action(...)`,
- no local `triumvirate` is configured, or it raises from `process(...)`.

This means a high-risk or approval-required action can be approved by default if
local governance is absent or fails after the router dry-run is unavailable or
returns allow.

### Router exception interaction

The router dry-run is the only current path that can reach ExecutionGate before
local CognitionKernel governance. If that dry-run raises and is swallowed, the
subsequent low-risk/default local approval can continue without canonical
router/gate/evidence/audit coverage.

## 3. Whether The Path Reaches ExecutionGate

Partially, and not reliably.

ExecutionGate is reached only if the router dry-run succeeds far enough to call
`ExecutionGate.execute(...)`.

The real action callable is not executed inside `ExecutionGate`; the router
dry-run uses a no-op executor and then CognitionKernel later executes the
original callable in `act()`.

ExecutionGate is not reached when:

- `execution_router.execute(...)` import or call raises,
- a router precondition raises in a way not returned as a denial,
- tests monkeypatch `app.core.execution_router.execute` to return
  `(True, None)` without invoking the gate,
- local low-risk/default approval occurs after the router exception is
  swallowed.

Phase 6 should decide whether a successful no-op router/gate dry-run is
sufficient coverage for CognitionKernel execution. If actual callable execution
must occur inside ExecutionGate, stop and treat that as execution-authority
consolidation, not a small CognitionKernel fallback repair.

## 4. Whether The Path Creates EvidenceBundle

Partially, and not for the local approval itself.

EvidenceBundle can be produced by:

- `ExecutionGate._emit_evidence_bundle()` when the router dry-run reaches
  ExecutionGate,
- Phase 4 router precheck receipt helpers,
- direct `EvidenceBundleWriter` calls in tests.

CognitionKernel local `_check_governance()` does not import or call
`EvidenceBundleWriter`.

If the router dry-run is unavailable and the kernel falls back to local
approval, the approval has no EvidenceBundle. The subsequent IronPathExecutor
decision record is useful but is a different artifact type.

## 5. Whether The Path Reaches AuditManager/SovereignAuditLog

Partially, and not for the local approval itself.

AuditManager can be reached when:

- the router dry-run reaches ExecutionGate,
- ExecutionGate reaches `GovernanceKernel.evaluate_action(...)`,
- GovernanceKernel `_approve()` or `_reject()` calls
  `get_audit_manager().log_governance_decision(...)`,
- AuditManager is in sovereign mode and delegates to `SovereignAuditLog`.

CognitionKernel local `_check_governance()` does not call:

- `get_audit_manager()`,
- `AuditManager.log_governance_event(...)`,
- `AuditManager.log_governance_decision(...)`,
- `SovereignAuditLog`.

If router/gate is bypassed by exception, a local CognitionKernel approval can
continue without AuditManager or SovereignAuditLog.

## 6. Whether This Path Overlaps With GovernanceService

Yes. It overlaps conceptually and diverges behaviorally.

Overlap:

- Both define a governance `Decision`.
- Both classify mutation intent.
- Both can evaluate `governance_system` and Triumvirate-style authorities.
- Both historically had low-risk/no-governance positive fallback behavior.

Divergence:

- Phase 5 hardened `GovernanceService._auto_approve()` so no-governance
  fallback is fail-closed and non-authoritative.
- `CognitionKernel._check_governance()` still has its own low-risk
  `approved=True` shortcut and no-governance `approved=True` default.
- `CognitionKernel` does not instantiate or call `GovernanceService`.
- `src/app/core/services/README.md` documents an extracted-services shape, but
  the current `CognitionKernel.__init__()` signature still accepts
  `governance_system`, `triumvirate`, `memory_engine`, and related monolithic
  dependencies rather than `governance_service`, `execution_service`, or
  `memory_service`.

Phase 6 should not reopen Phase 5. It should either align CognitionKernel's
local fallback semantics with Phase 5 or explicitly route the kernel through a
canonical receipt-producing authority path.

## 7. Current Tests Covering This Behavior

Direct CognitionKernel tests:

- `tests/test_cognition_kernel.py::allow_canonical_router_for_kernel_unit_tests`
  monkeypatches `app.core.execution_router.execute` to return `(True, None)`.
  This means the test file does not verify real router, ExecutionGate,
  EvidenceBundle, AuditManager, or SovereignAuditLog coverage.
- `tests/test_cognition_kernel.py::TestCognitionKernel::test_low_risk_auto_approval`
  expects low-risk/no-approval execution to succeed and the governance reason to
  contain `"auto-approved"`.
- `tests/test_cognition_kernel.py::TestCognitionKernelWithoutSubsystems::test_kernel_without_subsystems`
  expects a kernel with no identity, memory, governance, reflection, or
  Triumvirate subsystems to execute a low-risk action successfully.
- `tests/test_cognition_kernel.py::TestExecutionTypes::*` uses
  `CognitionKernel()` without governance subsystems and expects low-risk actions
  across execution types to succeed.
- `tests/test_cognition_kernel.py::TestCognitionKernel::test_execution_blocked_by_governance`
  covers configured local governance denial for high-risk/approval-required
  actions.
- `tests/test_cognition_kernel.py::TestCognitionKernel::test_execution_with_triumvirate_approval`
  covers local Triumvirate approval when the local governance system is removed.

Related tests:

- `tests/test_modular_services.py` verifies Phase 5 `GovernanceService`
  fail-closed behavior, but not CognitionKernel's local fallback.
- `tests/test_execution_router_hardening.py` verifies Phase 4 router precheck
  receipts and degradation rules, but not CognitionKernel's catch-and-fallback
  behavior.
- `tests/test_execution_gate_enforcement.py` verifies ExecutionGate behavior,
  including capability Stage 6, but not CognitionKernel actual callable
  execution.
- `tests/test_audit_manager.py` verifies AuditManager operational/sovereign
  behavior and GovernanceKernel routing through AuditManager.
- `tests/test_governance_contract.py` and `tests/test_evidence_bundle.py`
  verify EvidenceBundle contract validity, not CognitionKernel local approval.
- `tests/test_kernel_enhancements.py` covers deterministic replay and fuzz
  harness support for CognitionKernel, not the authority fallback.

Coverage gaps:

- No direct test proves router exceptions fail closed in CognitionKernel.
- No direct test proves low-risk/no-approval uses configured local governance.
- No direct test proves no-governance high-risk/default fallback is denied.
- No direct test proves local governance/Triumvirate exceptions fail closed.
- No direct test proves a local CognitionKernel approval has an EvidenceBundle
  or AuditManager receipt.
- No direct test distinguishes router dry-run receipts from actual action
  execution receipts.

## 8. Proposed Repair Options

### Option A: Disable CognitionKernel local positive fallback

Change `_check_governance()` so local fallback never returns `approved=True`
without an explicit local authority decision.

Behavior:

- Remove or move the low-risk shortcut so it cannot shadow configured
  `governance_system` or `triumvirate`.
- If no local authority is configured, return `approved=False`.
- If local authority raises, return `approved=False` instead of falling through
  to default approval.
- Use an explicit reason such as:
  `"Governance unavailable: CognitionKernel local fallback is non-authoritative; canonical approval required"`.

Pros:

- Smallest CognitionKernel-local positive-authority repair.
- Aligns local kernel fallback with Phase 5 GovernanceService behavior.
- Does not touch Phase 5 implementation.
- Does not touch ExecutionGate, router, audit, capability, pipeline, OctoReflex,
  or IronPathExecutor.

Cons:

- Existing CognitionKernel tests expecting low-risk success must change.
- Does not itself create EvidenceBundle or AuditManager receipts.
- Leaves the router dry-run as the only canonical preflight receipt path.

### Option B: Require router dry-run availability and local explicit authority

Make `enforce()` fail closed if `execution_router.execute(...)` raises, and make
`_check_governance()` require an explicit local authority for approval.

Behavior:

- Router denial remains denial.
- Router exception becomes a `ConstitutionalFault`.
- Local low-risk/default fallback becomes non-authoritative deny.
- Configured `governance_system` and `triumvirate` remain valid local authority
  sources.
- Local authority exceptions fail closed.

Pros:

- Closes the "router unavailable, local fallback approves" path.
- Keeps repair scoped to CognitionKernel and tests.
- Preserves existing router/gate/evidence/audit path when it is reachable.
- Does not require public schema changes.

Cons:

- More behavior change than Option A because router exceptions now deny.
- Still does not put the actual action callable inside ExecutionGate.
- Requires careful tests to avoid masking router-deny behavior.

### Option C: Route actual CognitionKernel action execution through ExecutionGate

Replace the no-op dry-run with a gate-routed execution of the real callable, or
move `act()` behind an ExecutionGate executor wrapper.

Pros:

- Strongest answer to "does the actual action reach ExecutionGate".
- EvidenceBundle and AuditManager paths would correspond more closely to the
  real execution.

Cons:

- This is execution-authority consolidation, not a small fallback repair.
- It risks double execution if implemented incorrectly.
- It may require touching ExecutionGate/router semantics.
- It may require broad tests across agents, tools, services, and pipeline.

Phase 6 should stop if this option becomes required.

### Option D: Replace local logic with GovernanceService

Refactor CognitionKernel to delegate local governance checks to
`GovernanceService`.

Pros:

- Aligns CognitionKernel with Phase 5 behavior.
- Reduces duplicate governance decision logic over time.

Cons:

- Current `CognitionKernel.__init__()` does not accept `governance_service`.
- Service README and source constructor are not aligned.
- Refactor could be broader than the Phase 6 authority review needs.
- Still does not by itself solve ExecutionGate/EvidenceBundle/AuditManager
  coverage unless paired with router/gate decisions.

This should be deferred unless explicitly authorized as a service-consolidation
phase.

## 9. Recommended Repair

Recommended Phase 6 repair: **Option B as a tests-first, CognitionKernel-local
fail-closed repair.**

Concrete recommendation:

1. Do not touch Phase 5 `GovernanceService`.
2. Do not touch ExecutionGate, router hardening, audit spine, or capability
   bridge unless tests prove a direct dependency is required.
3. In `CognitionKernel.enforce()`:
   - keep router denial behavior unchanged,
   - change router exception handling from silent fallback to fail-closed
     `ConstitutionalFault`.
4. In `_check_governance()`:
   - remove the local positive low-risk shortcut as an authority source,
   - evaluate configured local `governance_system` and `triumvirate` before any
     fallback,
   - fail closed if configured local authorities raise,
   - make no-governance fallback `approved=False` for low, routine, medium,
     high, and unknown risk.
5. Preserve `Decision` schema and `ExecutionResult` schema.
6. Preserve DENY/ALLOW semantics for explicit local governance decisions.
7. Keep IronPathExecutor decision record creation in `commit()`.

Recommended reason strings:

- Low/routine no local authority:
  `"Governance unavailable: CognitionKernel low-risk fallback is non-authoritative; canonical approval required"`
- Local governance exception:
  `"Governance system failed closed: <error>"`
- Triumvirate exception:
  `"Triumvirate failed closed: <error>"`
- Router exception:
  `"Governance pipeline unavailable; failed closed: <error>"`

Why this is recommended:

- The immediate risk is positive authority without reliable canonical coverage.
- Failing closed is smaller and safer than adding a new ExecutionGate execution
  topology inside CognitionKernel.
- Phase 5 already established the same policy for GovernanceService fallback.
- Router/gate/evidence/audit coverage stays where it already lives.

Open coordination question:

- Is a successful no-op router dry-run sufficient for Phase 6, or must the
  actual callable execute inside ExecutionGate? If the latter, do not implement
  Phase 6 as a small repair; plan a separate execution-authority consolidation.

## 10. Tests Required Before Implementation

Run before implementation from a clean tree:

```powershell
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_cognition_kernel.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_modular_services.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_execution_router_hardening.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_execution_gate_enforcement.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_governance_contract.py tests/test_evidence_bundle.py tests/test_audit_manager.py -v
```

Do not run `canonical/replay.py` unless separately authorized.

New or updated tests required:

1. Router exception in `CognitionKernel.enforce()` denies and does not call the
   action callable.
2. Router explicit denial still denies and does not call the action callable.
3. Low-risk/no-approval action with no local governance denies as
   non-authoritative.
4. Low-risk/no-approval action with configured governance system calls that
   governance system instead of short-circuiting.
5. Configured governance system denial blocks low-risk/no-approval action.
6. High-risk/requires-approval action with no local governance denies instead
   of default-approving.
7. Governance system exception fails closed and does not fall through to default
   approval.
8. Triumvirate exception fails closed and does not fall through to default
   approval.
9. Triumvirate approval still allows when governance system is absent.
10. Governance system approval still allows when governance system is present.
11. Blocked CognitionKernel actions still commit a decision record.
12. No test requires changing `Decision`, `ExecutionResult`, EvidenceBundle, or
    GovernanceOutcome public schemas.
13. Tests explicitly document that local CognitionKernel fallback is not an
    AuditManager/SovereignAuditLog receipt source.
14. Tests distinguish router/gate preflight evidence from actual action
    execution.

Existing tests expected to change:

- `tests/test_cognition_kernel.py::TestCognitionKernel::test_low_risk_auto_approval`
  should become a fail-closed/non-authoritative test, or be split into explicit
  local-governance approval and no-governance denial cases.
- `tests/test_cognition_kernel.py::TestCognitionKernelWithoutSubsystems::test_kernel_without_subsystems`
  should no longer expect execution to proceed without any authority.
- `tests/test_cognition_kernel.py::TestExecutionTypes::*` should provide an
  explicit approving governance authority or assert fail-closed behavior.

## 11. Stop Conditions Before Implementation

Stop before implementation if any of these are true:

- The repair requires changing public `Decision` or `ExecutionResult` schemas.
- The repair requires changing EvidenceBundle schema or valid outcomes.
- The repair requires changing GovernanceOutcome.
- The repair requires touching Phase 5 `GovernanceService`.
- The repair requires touching ExecutionGate internals.
- The repair requires touching Phase 4 router hardening logic beyond
  CognitionKernel's call handling.
- The repair requires touching audit spine internals.
- The repair requires touching capability bridge files.
- The repair requires touching pipeline, OctoReflex, or IronPathExecutor
  authority paths.
- Tests require preserving `"Auto-approved (low risk, no approval required)"`
  as an authoritative allow reason.
- A caller cannot tolerate fail-closed no-governance CognitionKernel behavior
  and no canonical authority replacement is provided.
- The project decides that actual CognitionKernel callables must execute inside
  ExecutionGate in Phase 6.
- Canonical replay is requested implicitly rather than explicitly authorized.

## 12. Exact Implementation Sequence

Recommended Option B sequence:

1. Confirm clean working tree.
2. Run the baseline tests listed above.
3. Add or update focused tests in `tests/test_cognition_kernel.py`:
   - router exception fail-closed,
   - low-risk no-governance fail-closed,
   - low-risk configured governance no shortcut,
   - high-risk no-governance fail-closed,
   - local authority exception fail-closed,
   - existing local authority approvals still allow.
4. Run `tests/test_cognition_kernel.py -v` and confirm the new tests fail
   against current source.
5. Modify only `src/app/core/cognition_kernel.py`:
   - change router exception handling to fail closed,
   - move/remove the low-risk positive shortcut,
   - make no-governance fallback return `approved=False`,
   - make local authority exceptions return deny decisions,
   - preserve existing dataclasses and public result fields.
6. Run focused CognitionKernel tests.
7. Run modular service regression tests to confirm Phase 5 remains untouched.
8. Run router, gate, governance contract, evidence, and audit regressions.
9. Run `git diff --check`.
10. Run `git status --short`.

## Implementation Authorization Assessment

Phase 6 is safe to authorize only if the repair is constrained to
CognitionKernel local fallback hardening and focused tests.

Exact blockers before authorization:

- Confirm that existing CognitionKernel tests may change from low-risk default
  execution to fail-closed/non-authoritative behavior.
- Confirm whether a successful no-op router dry-run is sufficient for Phase 6.
  If actual callable execution must move inside ExecutionGate, Phase 6 is not
  safe as a small repair.
- Confirm that local governance and Triumvirate exceptions should fail closed
  instead of falling through to default approval.
- Confirm that Phase 6 should not refactor CognitionKernel to use
  `GovernanceService` directly.
