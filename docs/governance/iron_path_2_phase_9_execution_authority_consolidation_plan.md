# Iron Path 2.0 Phase 9: Execution Authority Consolidation Plan

Status: planning only. No source behavior is changed by this document.

Phase 9 goal: identify every path found in this pass that can execute, approve
execution, deny execution, halt execution, escalate execution, or produce
execution-like receipts outside the canonical `execution_router -> ExecutionGate`
path. Implementation is not authorized by this plan until the blockers and stop
conditions below are resolved.

Canonical target for Phase 9:

```text
caller -> src/app/core/execution_router.py::execute()
       -> src/app/core/execution_gate.py::ExecutionGate.execute()
       -> executor_fn(context)
       -> EvidenceBundle + GovernanceObservation
       -> GovernanceKernel audit through AuditManager where applicable
```

## 1. All current execution entry points

| Entry point | Current path | Authority or receipt behavior | Phase 9 classification |
|---|---|---|---|
| `src/app/core/execution_router.py::execute()` | Runs Waterfall, Liara, RuntimeEnforcer, StateRegister, trust/adversarial context, invariant checks, then `get_execution_gate().execute(...)`. | Canonical wrapper. Can return deny/degraded before gate. Emits router precheck EvidenceBundle and GovernanceObservation on fail-closed/degraded prechecks. | Canonical target. |
| `src/app/core/execution_gate.py::ExecutionGate.execute()` | Runs GovernanceKernel, SafeAllow, PolicyDecision, ExecutionAuthorization, binding, sovereign runtime binding, capability bridge, semantic collision, invariant severity, then calls `executor_fn(context)`. | Executes the callable. Emits EvidenceBundle and GovernanceObservation for final allow/deny/halt/escalate outcomes. Reports denials to Chimera. | Canonical gate, but direct callers bypass router prechecks. |
| Domain subsystem command methods in `src/app/domains/*.py` | `execute_command()` methods import `app.core.execution_router.execute` and pass `_dispatch` callables. | Reach canonical router before local dispatch. | Currently aligned, but should stay covered by direct-router tests. |
| `src/app/core/cognition_kernel.py::process()` / `route()` | Calls `execution_router.execute(..., executor_fn=lambda _ctx: None)` as a no-op dry-run, then `act()` executes `action.callable(...)` locally. | Reaches router and gate for dry-run only. Actual callable execution happens outside ExecutionGate. Commits IronPathExecutor decision records. | Parallel execution risk remaining after Phase 6. |
| `src/app/core/runtime/router.py::route_request()` | Called by web, desktop, CLI, agent, and Temporal integration paths. Delegates to `governance.pipeline.enforce_pipeline(context)`. | Does not reach `execution_router.py`. Returns success/error wrapper. | Parallel router risk. |
| `src/app/core/governance/pipeline.py::enforce_pipeline()` | Validates, simulates, gates, executes, commits, and logs. `_execute()` directly dispatches `agent.*`, `ai.*`, auth, persona, learning, codex, agents, ecosystem, and Temporal actions. | Can deny through validation/gate exceptions and can execute real operations outside ExecutionGate. Writes local runtime audit logs. Writes IronPathExecutor allow records for hard/governance mutations. | Major parallel authority path. |
| `src/app/interfaces/web/app.py` | Flask routes call `route_request(source="web", ...)`. | Live HTTP/API entry into runtime router and pipeline. | Parallel entry through runtime router. |
| `src/app/interfaces/desktop/adapter.py` | Desktop adapter calls `route_request(source="desktop", ...)`. | Live desktop entry into runtime router and pipeline. | Parallel entry through runtime router. |
| `src/app/interfaces/cli/main.py` | CLI calls `route_request(source="cli", ...)`. | Live CLI entry into runtime router and pipeline. | Parallel entry through runtime router. |
| `src/app/interfaces/agents/adapter.py` | Agent adapter calls `route_request(source="agent", ...)`. | Live agent entry into runtime router and pipeline. | Parallel entry through runtime router. |
| `src/app/temporal/governance_integration.py` | Calls `route_request("temporal", {"action": "temporal.workflow.validate", ...})`. | Temporal governance validation reaches runtime router and pipeline, not canonical router. | Parallel entry through runtime router. |
| `src/app/core/services/execution_service.py::execute_action()` | Assumes pre-approval and calls `_execute()`, which calls `action.callable(*args, **kwargs)`. | Direct callable execution outside ExecutionGate. Currently found only in modular service tests during this pass. | Dormant/test-only unless later wired, but must be fenced. |
| `src/app/core/services/governance_service.py::evaluate_action()` | Returns `Decision(approved=...)` from Triumvirate, governance system, or fail-closed fallback. | Approval/denial source only. No execution, no EvidenceBundle, no AuditManager. Phase 5 removed auto-approval authority fallback. | Non-executing authority component; callers must not treat it as complete execution authority. |
| `src/app/core/octoreflex.py::validate_action()` | Rule violations call `_enforce_violation()` and `_gate()`, which calls `get_execution_gate().execute(..., lambda _ctx: None)`. | Can classify WARN/BLOCK/TERMINATE/ESCALATE. Directly reaches ExecutionGate with a no-op executor, bypassing router prechecks. | Enforcement receipt path that bypasses canonical router. |
| `src/app/security/chimera_bridge.py::receive_authenticated_event()` | Signed webhook intake routes to `receive_verdict()` or `receive_canary_hit()`. | Observer/receipt only. Emits GovernanceObservation and AuditManager security events. Writes drift alerts. Does not call ExecutionGate or OctoReflex. | Observer-only, keep out of authority. |
| `governance/triumvirate_server.py::evaluate_intent()` | `/intent` computes Galahad, Cerberus, CodexDeus votes and persists SQLite audit records. | Can return final verdict `allow`, `deny`, or `escalate`; does not execute. Does not emit EvidenceBundle or AuditManager. | Governance decision service, not execution path. |
| `governance/triumvirate_server.py::chimera_verdict()` / `chimera_canary()` | Validates signed Chimera fields and delegates to `ChimeraBridge.receive_authenticated_event(...)`. | Observer/receipt endpoint only after Phase 8. | Observer-only. |
| `src/app/core/governance/iron_path_executor.py` | Provides policy evaluation, mutation binding, `record_decision()`, `record_commit_receipt()`, `record_arbiter_ruling()`, `record_im_moment()`, and `compensate()`. | Can produce allow/deny-like immutable decision records outside ExecutionGate. Does not execute callables. | Receipt authority risk. |
| `governance/iron_path.py::IronPathExecutor.execute()` | Standalone sovereign demonstration executor that runs pipeline stages and writes artifacts/audit/compliance bundles. | Executes demo stages and produces cryptographic artifacts outside ExecutionGate. | Dormant/test/demo path unless invoked directly. |
| `src/app/core/super_kernel.py::process()` / `route()` | Performs internal governance check, optional RBAC, then calls registered subordinate `instance.process(...)`. | Can auto-approve low-risk memory/perspective operations and auto-approve when no governance is configured. Executes subordinate kernels outside canonical router. | Major parallel authority candidate outside Phase 2-8 repairs. |
| `src/app/core/security_operations_center.py::_execute_action()` | Executes remediation actions such as block IP, kill process, isolate system, revoke access, alert, log. | Security response execution outside ExecutionGate. Some methods currently look stub-like, but the path is an authority surface. | Parallel security authority candidate. |
| `src/app/security/advanced/dos_trap.py::_execute_action()` | Executes emergency response actions including kill switch, wipe secrets, isolate, sanitize RAM, and shutdown branches. | Emergency halt/destructive response path outside ExecutionGate. Some branches require config/manual behavior. | High-risk parallel emergency authority candidate. |
| `src/app/core/planetary_defense_monolith.py::execute_action()` | Separate constitutional core action executor with Four Laws checks and `authorized_by` metadata. | Claims to be its own "ONLY way" path and executes outside canonical router. | Separate legacy authority candidate. |

## 2. Which paths reach execution_router

Confirmed current paths reaching `src/app/core/execution_router.py::execute()`:

| Caller | Reaches router? | Notes |
|---|---:|---|
| Domain modules under `src/app/domains/` | Yes | `agi_safeguards`, `biomedical_defense`, `continuous_improvement`, `deep_expansion`, `command_control`, `ethics_governance`, `supply_logistics`, `situational_awareness`, `survivor_support`, and `tactical_edge_ai` import `_gov_execute`. |
| `src/app/core/cognition_kernel.py::enforce()` | Yes | Dry-run only with `executor_fn=lambda _ctx: None`; actual `act()` happens later outside gate. |
| `src/app/core/execution_router.py::execute()` direct tests | Yes | `tests/test_execution_router_hardening.py` exercises router precheck behavior. |

Confirmed current paths not reaching `execution_router.py`:

| Caller | Current path |
|---|---|
| Web, desktop, CLI, agent, and Temporal adapters | `route_request()` -> `governance.pipeline.enforce_pipeline()` |
| `governance.pipeline.enforce_pipeline()` | Internal validate/simulate/gate/execute pipeline |
| `ExecutionService.execute_action()` | Direct callable execution |
| `OctoReflex._gate()` | Direct `ExecutionGate.execute(...)` |
| `SuperKernel.process()` | Internal governance/RBAC -> subordinate `process()` |
| `SecurityOperationsCenter` and `DoSTrap` response paths | Internal action dispatch |
| `PlanetaryDefenseMonolith.execute_action()` | Separate constitutional core |
| `governance/iron_path.py` standalone executor | Internal stage executor |

## 3. Which paths reach ExecutionGate

| Path | Reaches ExecutionGate? | Via router? | Notes |
|---|---:|---:|---|
| `execution_router.execute()` | Yes | Yes | Canonical path. |
| Domain module `_gov_execute(...)` calls | Yes | Yes | The dispatched callable executes inside `ExecutionGate.execute()`. |
| CognitionKernel dry-run | Yes | Yes | Uses no-op executor; actual callable remains outside gate. |
| OctoReflex `_gate()` | Yes | No | Direct gate call, no-op executor, bypassing router prechecks. |
| Runtime router/pipeline | No | No | Pipeline has its own gate and direct execution. |
| ExecutionService | No | No | Direct callable execution. |
| GovernanceService | No | No | Decision-only. |
| Chimera bridge/endpoints | No | No | Observer-only by Phase 7/8 tests. |
| Triumvirate `/intent` | No | No | Decision service and SQLite audit only. |
| SuperKernel | No | No | Internal governance and subordinate `process()`. |
| Security response modules | No | No | Internal remediation dispatch. |
| PlanetaryDefenseMonolith | No | No | Separate core. |

## 4. Which paths execute callables outside ExecutionGate

| Path | Evidence | Concern |
|---|---|---|
| `CognitionKernel.act()` | Calls `action.callable(*action.args, **action.kwargs)` after no-op router dry-run. | Router/gate evidence does not include the actual callable result or actual executor side effect. |
| `ExecutionService._execute()` | Calls `action.callable(*action.args, **action.kwargs)`. | Assumes pre-approval by GovernanceService; no canonical gate receipt. |
| `governance.pipeline._execute()` | Directly dispatches actions to AI orchestrator, auth, persona, learning, codex, agents, ecosystem, and Temporal handlers. | Parallel execution path for web/desktop/CLI/agent/Temporal entry points. |
| `SuperKernel.process()` | Calls registered subordinate `instance.process(...)`. | Its own governance checks can approve without canonical router/gate. |
| `governance/iron_path.py::IronPathExecutor.execute()` | Executes configured demo stages. | Stage execution and proof artifacts are outside ExecutionGate. |
| `SecurityOperationsCenter._execute_action()` | Calls remediation action handlers. | Security response authority outside canonical execution path. |
| `DoSTrap._execute_action()` | Calls kill switch, wipe, isolate, sanitize, shutdown branches. | Emergency authority outside canonical execution path. |
| `PlanetaryDefenseMonolith.execute_action()` | Separate action execution API. | Separate constitutional core with independent authority claims. |

## 5. Which paths produce EvidenceBundle

| Path | Produces EvidenceBundle? | Notes |
|---|---:|---|
| `ExecutionGate._emit_evidence_bundle()` | Yes | Emits for many deny outcomes and final `ALLOW`, with GovernanceObservation. |
| `execution_router._emit_router_precheck_receipt()` | Yes | Emits for pre-gate `DENY` and `DEGRADED_READ_ONLY` precheck receipts. |
| CognitionKernel dry-run path | Indirectly | Dry-run can cause router/gate bundles, but not actual callable execution bundle. |
| Runtime router/pipeline | No | Writes local runtime logs, not EvidenceBundle. |
| ExecutionService | No | No bundle or observation. |
| GovernanceService | No | In-memory decision log only. |
| Chimera bridge | No | Uses GovernanceObservation with `bundle_id="chimera:..."`, but does not build an EvidenceBundle. |
| Triumvirate server | No | SQLite governance audit only. |
| IronPathExecutor decision ledger | No | Separate immutable decision record schema. |
| `governance/iron_path.py` | No | Produces compliance bundle/artifacts, not `EvidenceBundle`. |
| SuperKernel | No | Execution history only. |

## 6. Which paths produce GovernanceObservation

| Path | Produces GovernanceObservation? | Notes |
|---|---:|---|
| `ExecutionGate._emit_evidence_bundle()` | Yes | Builds observation from final outcome and bundle id. |
| `execution_router._emit_router_precheck_receipt()` | Yes | Builds observation for router precheck deny/degraded receipts. |
| `ChimeraBridge._emit_governance_observation()` | Yes | Observer-only `security.chimera` observation; canary uses observation outcome `ESCALATE`. |
| Runtime router/pipeline | No | Local audit log only. |
| CognitionKernel actual `act()` | No | Only dry-run path can emit through router/gate. |
| ExecutionService | No | No observation. |
| GovernanceService | No | No observation. |
| Triumvirate server | No | SQLite audit only. |
| IronPathExecutor | No | Decision ledger only. |
| SuperKernel | No | In-memory execution history. |

## 7. Which paths reach AuditManager/SovereignAuditLog

| Path | AuditManager? | SovereignAuditLog reachable? | Notes |
|---|---:|---:|---|
| `GovernanceKernel._approve()` / `_deny()` | Yes | Yes, through AuditManager sovereign mode | Phase 2 audit spine routes governance decisions through AuditManager. |
| `ChimeraBridge._emit_audit_manager_event()` | Yes | Yes, through AuditManager sovereign mode | Phase 7/8 observer receipts use `log_security_event()`. |
| `ExecutionGate` Stage 5 | No | No, not this class | Uses `governance.sovereign_runtime.SovereignRuntime.audit_log(...)`, a separate audit surface. |
| `governance/iron_path.py` | No | No, not this class | Uses `SovereignRuntime.audit_log(...)`, not AuditManager/SovereignAuditLog. |
| Runtime router/pipeline | No | No | Writes `data/runtime/governance_audit.log` and state changes. |
| Triumvirate server | No | No | Writes SQLite audit database. |
| CognitionKernel | Indirect via dry-run only | Indirect via dry-run only | Actual commit uses IronPathExecutor records, not AuditManager. |
| IronPathExecutor decision ledger | No | No | HMAC/hash-chained decision log, separate from AuditManager. |

## 8. Which paths write IronPathExecutor records

| Path | Record type |
|---|---|
| `CognitionKernel._record_decision_chain()` | `record_commit_receipt()` for allow-like post evaluation, `record_arbiter_ruling(decision="deny")` otherwise. |
| `governance.pipeline._enforce_mutation_governance_binding()` | `record_decision(decision="allow")` for `hardMutation` and `governanceMutation` after binding. |
| Direct callers of `src/app/core/governance/iron_path_executor.py` | `record_decision()`, `record_commit_receipt()`, `record_arbiter_ruling()`, `record_im_moment()`, and `compensate()`. |

Concern: `record_commit_receipt()`, `record_im_moment()`, and `compensate()` all record `decision="allow"` outside ExecutionGate. They may be intended as receipts, but Phase 9 must make that non-authoritative status explicit or route their authority source back to canonical execution receipts.

## 9. Which paths can deny, allow, halt, or escalate

| Path | Allow | Deny/block | Halt/escalate | Notes |
|---|---:|---:|---:|---|
| `execution_router.execute()` | Through gate | Yes, router prechecks and gate result | Indirect through gate | Canonical wrapper. |
| `ExecutionGate.execute()` | Yes | Yes | Yes, via invariant severity outcome mapping | Canonical gate, but direct callers skip router prechecks. |
| `GovernanceKernel.evaluate_action()` | Yes | Yes | Not directly observed in this pass | Stage 0 authority inside ExecutionGate. |
| `GovernanceService.evaluate_action()` | Yes through configured Triumvirate/governance system | Yes, including fallback | Not directly | Phase 5 no-governance fallback denies. |
| `governance.pipeline._gate()` / `_execute()` | Allows by reaching `_execute()` | Raises validation/gate errors | Not formal public outcomes | Parallel pipeline authority. |
| `OctoReflex.validate_action()` | No execution allow | BLOCK/TERMINATE enforcement levels | ESCALATE enforcement level | Direct gate receipt with no-op executor. |
| `Triumvirate /intent` | final verdict `allow` | final verdict `deny` | final verdict `escalate` | No execution. |
| `ChimeraBridge` | No public allow | No public deny | Observation/escalation record only | Observer-only by locked Phase 7/8 constraints. |
| `IronPathExecutor` | Policy/evidence records can say allow | Policy/evidence records can say deny | Not public GovernanceOutcome | Receipt authority risk. |
| `SuperKernel` | Yes, including auto-approval fallback | Yes through governance/RBAC errors | Not observed | Major parallel authority candidate. |
| Security response modules | Yes, executes response actions | Can skip/not execute | Kill switch/shutdown/isolate branches | Emergency authority outside gate. |
| PlanetaryDefenseMonolith | Yes, separate executor | LawViolation/MoralCertainty errors | Not observed | Separate constitutional core. |

## 10. Which paths are observer-only

| Path | Evidence |
|---|---|
| `src/app/security/chimera_bridge.py::receive_authenticated_event()` | Docstring states observer/receipt only; implementation emits drift alerts, GovernanceObservation, and AuditManager security events. |
| `governance/triumvirate_server.py` Chimera endpoints | Validate signed Chimera fields and delegate to ChimeraBridge. Tests assert no ExecutionGate/OctoReflex calls and no public allow/deny/halt. |
| `src/app/core/governance_observability.py` | Collector records observations only. |
| `src/app/core/evidence_bundle.py` | Stores proof bundles only; does not execute or decide. |

## 11. Which paths are dormant/test-only

| Path | Evidence from this pass | Risk if activated |
|---|---|---|
| `src/app/core/services/execution_service.py` | Direct instantiation/calls found in `tests/test_modular_services.py`; no source caller found in `src/app`. | Would execute pre-approved callables outside ExecutionGate if wired. |
| `governance/iron_path.py` | Invoked by `python -m governance.iron_path <pipeline.yaml>` and tests such as `tests/test_iron_path.py` / `tests/test_sovereign_verifier.py`. | Standalone stage executor and artifact trail outside canonical route. |
| `src/app/core/planetary_defense_monolith.py` | Tested by `tests/test_planetary_defense_monolith.py`; source exports `execute_constitutional_action(...)`. | Separate action authority if called by runtime code. |
| `SuperKernel` | Has tests and bootstrap registration, but the live caller map needs a dedicated pass. | Can execute subordinate kernels with its own auto-approval fallback. |

These should not be treated as harmless solely because they appear test-heavy. Phase 9 implementation should either prove no production caller exists or fence them explicitly.

## 12. Remaining parallel-authority risks

1. `governance.pipeline.enforce_pipeline()` remains a full validate/gate/execute pipeline outside `execution_router -> ExecutionGate`.
2. Web, desktop, CLI, agent, and Temporal interfaces enter `runtime.router -> governance.pipeline`, not the canonical router.
3. CognitionKernel performs a canonical no-op dry-run, then executes the real callable outside ExecutionGate.
4. OctoReflex sends enforcement events directly to ExecutionGate, bypassing router prechecks that Phase 4 hardened.
5. `ExecutionService` is dormant/test-only in this pass, but its public service API can execute pre-approved callables outside ExecutionGate.
6. `SuperKernel` has independent auto-approval paths and executes subordinate kernels outside the canonical route.
7. `IronPathExecutor` records allow-like commit, im_moment, and compensating-action records that may be mistaken for execution authority.
8. `governance/iron_path.py` produces proof artifacts and executes standalone stages outside the canonical route.
9. Security emergency response modules can halt/isolate/kill/wipe outside the canonical route.
10. `PlanetaryDefenseMonolith` contains a separate constitutional action executor with independent authority language.
11. Multiple audit/receipt planes still exist: EvidenceBundle/GovernanceObservation, AuditManager/SovereignAuditLog, SovereignRuntime audit, Triumvirate SQLite audit, runtime local logs, and IronPathExecutor decision log.

## 13. Recommended consolidation target

Recommended target: one executable authority path and several explicitly
non-authoritative receipt paths.

| Category | Target rule |
|---|---|
| Executable caller | Must call `execution_router.execute(...)` unless formally classified as emergency break-glass or test-only. |
| ExecutionGate callers | Only `execution_router.execute(...)` should call `ExecutionGate.execute(...)` for normal governed execution. |
| CognitionKernel | Keep local cognition orchestration, but move the actual callable execution into the router/gate executor function or return a non-authoritative recommendation. |
| Runtime router and pipeline | Convert to adapter/planner surfaces that call `execution_router.execute(...)` for actual execution, or retire as a legacy router. |
| OctoReflex | Route enforcement receipts through `execution_router.execute(...)` with explicit enforcement-only metadata, or classify as observer-only with no direct gate call. |
| ExecutionService | Make private/test-only or require it to call `execution_router.execute(...)` before any callable execution. |
| IronPathExecutor records | Preserve as immutable receipts, but add metadata/tests proving they are not public execution approvals unless tied to a canonical EvidenceBundle/ExecutionGate decision. |
| Chimera | Keep observer/receipt only; no changes needed unless later implementation touches receipt correlation. |
| Triumvirate | Keep decision service; decisions must be consumed by ExecutionGate/GovernanceKernel, not by direct executors. |
| Emergency/security paths | Decide break-glass policy: either route through canonical gate with explicit emergency outcome or keep as sealed manual/emergency exception with separate tests and receipts. |

## 14. Tests required before implementation

Existing focused tests to keep in the baseline:

- `tests/test_execution_router_hardening.py`
- `tests/test_execution_gate_enforcement.py`
- `tests/test_governance_contract.py`
- `tests/test_evidence_bundle.py`
- `tests/test_audit_manager.py`
- `tests/test_cognition_kernel.py`
- `tests/test_modular_services.py`
- `tests/test_governance_pipeline_regressions.py`
- `tests/test_iron_path_executor.py`
- `tests/test_iron_path.py`
- `tests/test_governance_observability.py`
- `tests/test_governance_server.py`
- `tests/test_chimera_runtime.py`
- `tests/test_chimera_endpoint_forwarding.py`
- `tests/test_super_kernel.py`
- `tests/test_planetary_defense_monolith.py`

New tests required before or with implementation:

1. Web route calls canonical `execution_router.execute()` and does not reach `governance.pipeline._execute()` directly.
2. Desktop adapter calls canonical router for execution actions.
3. CLI calls canonical router for execution actions.
4. Agent adapter calls canonical router for execution actions.
5. Temporal governance integration calls canonical router or is classified validation-only.
6. Pipeline `_execute()` cannot execute mutating/protected actions unless invoked through canonical router context.
7. CognitionKernel real callable executes inside the `executor_fn` passed to `execution_router.execute()`, not after a no-op dry-run.
8. CognitionKernel denied router result does not call the action callable.
9. OctoReflex enforcement no longer calls ExecutionGate directly, or direct call is covered by an explicit exception test.
10. ExecutionService cannot execute unless wrapped by canonical router or marked test-only.
11. IronPathExecutor allow-like records include canonical decision linkage or explicit `non_authoritative_receipt` metadata.
12. SuperKernel no-governance fallback fails closed or routes through canonical router.
13. SuperKernel low-risk auto-approval cannot execute without canonical router receipt.
14. Security emergency response paths are either routed through canonical gate or classified break-glass with explicit manual/config tests.
15. PlanetaryDefenseMonolith cannot act as a live runtime authority without canonical routing.
16. Audit correlation test links canonical EvidenceBundle, GovernanceObservation, AuditManager event, and any IronPathExecutor record for one successful execution.
17. Negative test proves no public ALLOW/DENY/HALT outcome is emitted by observer-only Chimera paths.
18. Regression test proves Phase 2-8 behavior remains unchanged for audit spine, capability bridge, router hardening, GovernanceService fallback, CognitionKernel fail-closed behavior, Chimera bridge intake, and Chimera endpoint forwarding.

## 15. Stop conditions before implementation

Stop before implementing if any of the following remain undecided:

1. Whether Phase 9 may modify `governance.pipeline.enforce_pipeline()` and runtime/interface adapters.
2. Whether CognitionKernel actual callable execution must move inside the ExecutionGate `executor_fn`.
3. Whether `ExecutionService` should be retired, made private/test-only, or routed through the canonical router.
4. Whether OctoReflex direct `ExecutionGate` calls are allowed as enforcement-only exceptions or must route through `execution_router`.
5. Whether `SuperKernel` is in Phase 9 scope or deferred to a later cognition/TARL consolidation phase.
6. Whether security emergency response modules are in Phase 9 scope or must be labeled break-glass exceptions.
7. Whether standalone `governance/iron_path.py` remains a demo/test artifact or must be fenced from production paths.
8. Whether IronPathExecutor allow-like records require schema metadata changes. If public schema changes are unavoidable, stop.
9. Whether multiple audit planes must be correlated in Phase 9 or only mapped.
10. Any required change touches TARL/cognition consolidation, web client work, OctoReflex behavior beyond call routing, or canonical replay execution without explicit authorization.

## 16. Exact implementation sequence

Recommended implementation order, once authorized:

1. Commit this plan separately before any source changes.
2. Add caller-map tests that fail against current runtime/interface/pipeline behavior.
3. Add CognitionKernel tests proving actual callable execution is inside the canonical router/gate path.
4. Add OctoReflex direct-gate regression tests reflecting the locked decision for enforcement-only routing.
5. Add ExecutionService dormant/test-only or router-wrapper tests.
6. Add IronPathExecutor receipt-linkage tests.
7. Add SuperKernel authority tests if SuperKernel is authorized in Phase 9; otherwise add a deferral/fence test.
8. Add break-glass tests for security emergency response paths if those are authorized in Phase 9; otherwise record explicit out-of-scope exceptions.
9. Implement the runtime router/interface adapter change first so live web/desktop/CLI/agent/Temporal traffic enters `execution_router.execute()`.
10. Convert or fence `governance.pipeline._execute()` so it cannot execute protected actions as a parallel authority.
11. Move CognitionKernel actual callable execution into the canonical `executor_fn`, or downgrade CognitionKernel output to non-authoritative recommendation.
12. Resolve OctoReflex direct gate behavior according to the locked decision.
13. Resolve ExecutionService according to the locked decision.
14. Add receipt correlation metadata only if it does not require public schema changes; otherwise stop.
15. Run focused test groups first, then the full Phase 9 validation suite.
16. Run `git diff --check` and `git status --short`.

Implementation safety assessment: Phase 9 is not safe to authorize as a code
change yet. It is safe to authorize only after the stop-condition decisions above
are locked, especially the runtime router/pipeline target, CognitionKernel actual
execution target, OctoReflex direct-gate policy, SuperKernel scope, and emergency
security-response scope.
