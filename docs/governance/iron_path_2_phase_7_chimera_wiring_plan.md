# Iron Path 2.0 Phase 7: Chimera Full Wiring Plan

Status: planning only. Do not implement until authorized.

## Scope

Phase 7 reviews Chimera as a deception-perimeter bridge for:

- drift detection,
- canary escalation,
- audit relay,
- governance observation,
- denial-signal feedback to the perimeter.

Primary safety question:

- Can Chimera become a receipt-producing observation and escalation bridge
  without becoming a new Project-AI approval, denial, halt, or execution
  authority?

Out of scope for Phase 7 unless separately authorized:

- TARL or cognition consolidation
- ExecutionGate behavior changes
- Execution router hardening changes
- Capability bridge changes
- Phase 2 audit spine rewrites
- Phase 3 capability authority changes
- Phase 4 router precheck behavior changes
- Phase 5 GovernanceService fallback changes
- Phase 6 CognitionKernel fallback changes
- Pipeline, OctoReflex, or IronPathExecutor authority consolidation
- Web client work
- Canonical replay

## Planning Contract

- Language/runtime: Python 3.12 in the existing Project-AI test harness.
- Environment: Windows/PowerShell with `PYTHONPATH=src`.
- Input contract: Chimera perimeter events, bridge webhook payloads, Chimera
  audit JSONL rows, and ExecutionGate governance denial metadata.
- Output contract for this phase: this plan only. No source behavior changes.
- Security constraints: no new public EvidenceBundle outcomes, no unreceipted
  authority, no unauthenticated production webhook ingestion, no hidden
  ExecutionGate/router bypass.
- Dependency constraints: prefer existing `ChimeraBridge`,
  `GovernanceObservation`, `EvidenceBundle`, `AuditManager`, and
  `AcceptanceLedger` APIs; do not invent a second audit system.
- Edge cases to cover before implementation: unsigned webhooks, replayed
  webhooks, malformed payloads, bridge write failures, audit relay failures,
  canary escalation errors, denial-signal feedback loops, and benign verdicts.

## Files Inspected

- `.github/instructions/mandatory-structured-generation-default.instructions.md`
- `AGENTS.md`
- `src/app/security/chimera/chimera.py`
- `src/app/security/chimera/chimera.env.template`
- `src/app/security/chimera/__init__.py`
- `src/app/security/chimera_bridge.py`
- `governance/triumvirate_server.py`
- `src/utf/docs/TRIUMVIRATE_SPEC.md`
- `src/app/core/execution_gate.py`
- `src/app/core/execution_router.py`
- `src/app/core/cognition_kernel.py`
- `src/app/core/services/governance_service.py`
- `src/app/core/evidence_bundle.py`
- `src/app/core/governance_observability.py`
- `src/app/core/governance_drift_monitor.py`
- `src/app/core/octoreflex.py`
- `src/cognition/codex/escalation.py`
- `src/app/governance/audit_manager.py`
- `src/app/governance/sovereign_audit_log.py`
- `src/app/governance/acceptance_ledger.py`
- `tests/test_chimera_runtime.py`
- `tests/test_audit_manager.py`
- `tests/test_audit_log.py`
- `tests/test_immutable_audit_log.py`
- `tests/test_evidence_bundle.py`
- `tests/test_governance_observability.py`
- `tests/test_execution_gate_enforcement.py`
- `tests/test_execution_router_hardening.py`
- `tests/test_cognition_kernel.py`
- `tests/test_modular_services.py`
- `docs/governance/iron_path_2_boot_order.md`
- `docs/governance/iron_path_2_phase_4_execution_router_hardening_plan.md`
- `docs/governance/iron_path_2_phase_5_governance_service_auto_approval_plan.md`
- `docs/governance/iron_path_2_phase_6_cognition_kernel_authority_plan.md`

## 1. Current Chimera Modules And Entry Points

| Entry point | Path | Current role |
| --- | --- | --- |
| Chimera perimeter runtime | `src/app/security/chimera/chimera.py` | Stdlib HTTP/HTTPS deception perimeter, canary registry/scanner, classifier, proxy/local decoy responder, HMAC/sha3_256 JSONL audit writer, CLI. |
| Chimera env template | `src/app/security/chimera/chimera.env.template` | Runtime configuration, including `CHIMERA_WEBHOOK_URL`, `CHIMERA_WEBHOOK_SCORE_MIN`, and `CHIMERA_GOVERNANCE_DENY_DIR`. |
| Project-AI bridge | `src/app/security/chimera_bridge.py` | Receives Chimera verdicts/canary hits, writes drift alerts, reports governance denials back to Chimera, and relays Chimera audit JSONL into the AcceptanceLedger. |
| Triumvirate webhook endpoints | `governance/triumvirate_server.py` | Exposes `POST /chimera/verdict` and `POST /chimera/canary`, forwarding payloads to `get_bridge()`. |
| ExecutionGate denial signal | `src/app/core/execution_gate.py` | On Stage 0 GovernanceKernel denial, calls `get_bridge().report_governance_denial(...)` with IP/domain/action/reason. |
| Audit relay start method | `src/app/security/chimera_bridge.py` | `start_audit_relay(chimera_audit_path)` tails a Chimera audit JSONL file and ships events to AcceptanceLedger. |
| Current test coverage | `tests/test_chimera_runtime.py` | Covers denial-boost file reads, canary rotation, proxy/local decision helper, bridge audit relay to AcceptanceLedger, and AcceptanceLedger audit-lock entries. |

Chimera's own runtime entry points are CLI-style commands in
`chimera.py`, including `serve`, `verify-audit`, `health`, `metrics-dump`,
`top-paths`, `canary-register`, `canary-rotate`, `canary-scan`,
`session-dump`, and `print-docs`.

## 2. Whether Chimera Is Currently Wired Or Dormant

Chimera is partially wired at source level and mostly dormant at runtime unless
explicitly configured.

Active source-level wiring:

- `chimera.py` can POST threat verdicts to
  `CHIMERA_WEBHOOK_URL + "/chimera/verdict"` when a score reaches
  `CHIMERA_WEBHOOK_SCORE_MIN`.
- `chimera.py` can POST canary hits to
  `CHIMERA_WEBHOOK_URL + "/chimera/canary"`.
- `triumvirate_server.py` exposes both Chimera endpoints and forwards to
  `ChimeraBridge`.
- `ChimeraBridge.receive_verdict()` writes `chimera_verdict_*.json` drift
  alerts for `SUSPICIOUS` and `ATTACKER` verdicts.
- `ChimeraBridge.receive_canary_hit()` writes `chimera_canary_*.json` drift
  alerts and then calls OctoReflex.
- `ExecutionGate._report_denial()` writes denial signal files via
  `ChimeraBridge.report_governance_denial(...)`.
- `ChimeraBridge._ship_to_ledger()` records Chimera audit events through
  `AcceptanceLedger.record_event(...)`.

Dormant or manually activated wiring:

- The Chimera webhooks are disabled unless `CHIMERA_WEBHOOK_URL` is set.
- The denial feedback boost in Chimera is disabled unless
  `CHIMERA_GOVERNANCE_DENY_DIR` is set.
- The audit relay is not auto-started by the inspected files; it runs only if
  `start_audit_relay(...)` is called.
- No inspected path wires Chimera events directly to `AuditManager` or
  `SovereignAuditLog`.
- No inspected path wires Chimera verdict/canary events directly to
  `GovernanceObservation`.
- No inspected path creates an EvidenceBundle directly inside
  `ChimeraBridge`.

## 3. Events And Signals Chimera Consumes

Chimera consumes:

- HTTP request metadata: method, path, query, body, headers, user agent,
  cookies, source IP, and session cookie.
- Canary tokens in request surfaces.
- Local canary registry state in the Chimera SQLite database.
- Local denial signal files in `CHIMERA_GOVERNANCE_DENY_DIR` matching
  `denial_*.json`.
- Environment configuration, including webhook URL, score threshold, audit path,
  database path, upstream proxy settings, metrics settings, and egress
  allowlist.

`ChimeraBridge` consumes:

- `SUSPICIOUS` and `ATTACKER` verdict payloads from `/chimera/verdict`.
- Canary-hit payloads from `/chimera/canary`.
- Chimera audit JSONL rows when `start_audit_relay(...)` is running.
- Governance denial information from ExecutionGate.

## 4. Events And Signals Chimera Emits

Chimera emits:

- HMAC/sha3_256 chained JSONL audit rows through `chimera.audit(...)`.
- Webhook threat verdicts to `/chimera/verdict`.
- Webhook canary-hit alerts to `/chimera/canary`.
- Proxy pass/error audit events.
- Canary serve/hit/surface-hit audit events.
- Session, universe, metric, and path-seen state in its SQLite database.
- Optional Prometheus-style metrics.
- Local proxy responses or local decoy responses, depending on classifier score,
  canary hits, handlers, and proxy configuration.

`ChimeraBridge` emits:

- `data/governance_drift_alerts/chimera_verdict_*.json` for suspicious or
  attacker verdicts.
- `data/governance_drift_alerts/chimera_canary_*.json` for canary hits.
- `data/chimera_signals/denial_*.json` for governance denial feedback to the
  Chimera perimeter.
- AcceptanceLedger `AUDIT_LOCK` entries through
  `AcceptanceLedger.record_event(...)` for relayed Chimera audit rows.
- OctoReflex validation calls for canary hits.

## 5. Whether Chimera Can Deny, Allow, Halt, Escalate, Or Only Observe

Within the Project-AI governance spine, Chimera verdicts currently observe and
record. They do not directly return `ALLOW`, `DENY`, `HALT`, or `ESCALATE` as
Project-AI governance outcomes.

Current behavior by path:

| Path | Current Project-AI authority effect |
| --- | --- |
| `receive_verdict(...)` | Observation-like drift alert only. It ignores verdicts other than `SUSPICIOUS` and `ATTACKER`; it does not call ExecutionGate, EvidenceBundle, AuditManager, or GovernanceObservation. |
| `receive_canary_hit(...)` | Drift alert plus OctoReflex validation call. This is not just passive observation because OctoReflex can route enforcement through ExecutionGate. |
| `report_governance_denial(...)` | Feedback signal to Chimera only. It should not change the already-computed ExecutionGate denial. |
| Chimera proxy/local response choice | Perimeter behavior only. It can proxy benign requests or serve decoys/tarpits locally, but this is not a Project-AI governance `ALLOW` or `DENY`. |
| Audit relay | Audit/receipt path only. It should not authorize or block execution. |

Phase 7 must preserve this boundary:

- Chimera may observe, attest, emit drift signals, and request escalation.
- Chimera must not become a direct approval source.
- Chimera verdicts must not directly deny, allow, halt, or execute actions.
- Canary hits may trigger escalation only through an explicitly receipted and
  tested path that does not bypass Phase 4 router safeguards by accident.

## 6. Whether Chimera Reaches EvidenceBundle

Directly: no.

No inspected Chimera or ChimeraBridge path imports or calls:

- `EvidenceBundleWriter`,
- `EvidenceBundleValidator`,
- `get_evidence_store()`,
- `ExecutionGate._emit_evidence_bundle()`,
- router precheck receipt helpers.

Indirectly: sometimes, depending on call path.

- If `ExecutionGate` denies at Stage 0, it calls `_report_denial(...)` and then
  emits an EvidenceBundle for the denial.
- If a canary hit triggers OctoReflex and OctoReflex routes to ExecutionGate,
  EvidenceBundle may be produced by ExecutionGate. This is indirect and not
  currently covered by Chimera-specific tests.

Important gap:

- Chimera-originated drift alerts and audit relay rows have no direct
  EvidenceBundle. They are currently file/ledger receipts, not canonical
  governed-request bundles.

Phase 7 recommendation:

- Do not add a new public EvidenceBundle outcome for Chimera.
- If Phase 7 needs an EvidenceBundle for canary escalation, use an existing
  outcome such as `ESCALATE`, `DENY`, or `HALT` only through an existing
  governed execution path.
- For pure observation verdicts, prefer `GovernanceObservation` and
  `AuditManager.log_security_event(...)`/`log_governance_event(...)` receipts
  rather than pretending a non-execution signal is an execution bundle.

## 7. Whether Chimera Reaches GovernanceObservation

Directly: no.

`governance_observability.py` exposes:

- `GovernanceObservation`,
- `build_observation(...)`,
- `get_collector().record(...)`.

Current router and gate paths already emit observations for governed requests.
`ChimeraBridge` does not call these APIs for verdicts, canary hits, denial
signals, or audit relay rows.

Phase 7 recommendation:

- Add tests first for direct Chimera-originated GovernanceObservation records.
- Use observations for non-authoritative Chimera verdict/canary metadata.
- Keep `final_outcome` within the existing valid set only if the event maps to a
  governed decision. For non-decision signals, record the authoritative outcome
  as metadata rather than adding a new public outcome.
- Include metadata such as `source="chimera"`, `event`, `verdict`, `score`,
  `ip_hash` or redacted IP, `sid_hash`, `path_hash`, and `bridge_authenticated`.

## 8. Whether Chimera Reaches AuditManager/SovereignAuditLog

Directly: no.

`ChimeraBridge` currently relays audit rows to `AcceptanceLedger`, not to
`AuditManager`.

Current audit paths:

- Chimera native audit: `chimera.audit(...)` writes HMAC/sha3_256 chained JSONL
  rows and supports `verify_audit()`.
- Bridge audit relay: `_ship_to_ledger(...)` calls
  `AcceptanceLedger().record_event(...)`.
- AcceptanceLedger entries are Ed25519-signed when cryptography is available,
  hash-chained, optionally timestamped when a TSA URL is provided, and recorded
  as `AcceptanceType.AUDIT_LOCK`.
- Phase 2 audit spine: `AuditManager.log_governance_decision(...)` can route to
  `SovereignAuditLog` in sovereign mode.

Gap:

- Chimera bridge events do not currently reach Phase 2 `AuditManager`.
- Therefore Chimera bridge events do not currently reach `SovereignAuditLog` in
  sovereign mode unless a separate path is added.

Phase 7 recommendation:

- Add a bridge-local audit call for Chimera-originated security/governance
  observations using `get_audit_manager().log_security_event(...)` or
  `log_governance_event(...)`.
- In sovereign mode, this should become reachable through existing
  `AuditManager` behavior without changing `SovereignAuditLog`.
- Preserve AcceptanceLedger relay as a separate Chimera audit-stream receipt,
  but do not claim it is the same as the Phase 2 sovereign audit path.

## 9. Whether Chimera Creates Any New Authority Path

Current source already contains two authority-adjacent paths:

1. Canary hit -> `ChimeraBridge.receive_canary_hit(...)` ->
   `OctoReflex.validate_action(...)` -> OctoReflex may call ExecutionGate.
2. Governance denial -> `ExecutionGate._report_denial(...)` ->
   `ChimeraBridge.report_governance_denial(...)` -> Chimera reads denial files
   and boosts source-IP score.

These are not direct Chimera approvals, but they can influence enforcement and
perimeter classification.

Risks:

- `POST /chimera/verdict` and `POST /chimera/canary` currently accept payload
  models without an inspected auth, HMAC signature, timestamp validation, or
  replay guard.
- `chimera.py` sends webhook payloads without a signature header.
- `receive_canary_hit(...)` can enter OctoReflex, and OctoReflex is already
  annotated as a direct ExecutionGate authority fragment that bypasses the
  `execution_router` wrapper.
- Bridge write failures are logged or swallowed, so receipt failure behavior is
  not consistently fail-closed or consistently observable.
- Audit relay failures return `False` or log warnings, but there is no durable
  dead-letter receipt.

Phase 7 should not authorize "full wiring" until these boundaries are tested.

Allowed Phase 7 authority shape:

- Chimera verdicts are non-authoritative observations.
- Chimera canary hits are escalation requests, not direct halts.
- Project-AI governance decisions remain with router/gate/kernel paths.
- Denial feedback to Chimera remains post-decision metadata.
- Audit relay remains receipt-only.

Disallowed Phase 7 authority shape:

- Chimera verdict directly sets `DENY`, `HALT`, `ESCALATE`, or `ALLOW` on a
  Project-AI execution.
- Chimera webhook payloads are accepted from unauthenticated sources in
  production mode.
- Chimera bypasses Phase 4 router prechecks for a new execution path.
- Chimera audit relay becomes a source of approval or denial.

## 10. Required Wiring Sequence

Recommended sequence for a safe Phase 7 implementation:

1. Add tests for the current bridge contract before changing behavior:
   verdict writes drift only, canary writes drift plus explicit escalation
   request, denial feedback is post-decision metadata, audit relay is
   receipt-only.
2. Add webhook authenticity tests:
   unsigned webhook denied, bad signature denied, stale timestamp denied,
   replayed nonce denied, malformed payload denied.
3. Add the smallest shared webhook-signing contract:
   Chimera signs payload bytes with a configured secret and timestamp/nonce;
   Triumvirate endpoint verifies before calling `ChimeraBridge`.
4. Add bridge-local `GovernanceObservation` emission for verdict and canary
   events.
5. Add bridge-local `AuditManager` logging for verdict and canary events,
   using existing AuditManager APIs and preserving sovereign-mode reachability.
6. Preserve existing drift-alert file emission for compatibility with current
   drift scans.
7. Keep AcceptanceLedger audit relay, but add tests that it remains receipt-only
   and does not call gate/router/kernel.
8. Review canary escalation:
   either make OctoReflex escalation explicitly observation/receipt-only for
   Phase 7, or route canary escalation through the existing canonical
   router/gate path with tests proving no Phase 4 prechecks are skipped.
9. Keep `ExecutionGate._report_denial()` behavior unchanged unless a test proves
   denial-signal emission itself needs a receipt. Do not change gate
   allow/deny semantics in Phase 7.
10. Run focused Chimera tests and audit/observability/gate/router regressions.

## 11. Tests Required Before Implementation

Run these before implementation from a clean tree:

```powershell
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_chimera_runtime.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_governance_observability.py tests/test_evidence_bundle.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_audit_manager.py tests/test_audit_log.py tests/test_immutable_audit_log.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_execution_gate_enforcement.py tests/test_execution_router_hardening.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_cognition_kernel.py tests/test_modular_services.py -v
```

Do not run `canonical/replay.py` unless separately authorized.

New or updated tests required:

1. `receive_verdict("BENIGN", ...)` does not write a drift alert and does not
   call AuditManager, EvidenceBundle, ExecutionGate, or OctoReflex.
2. `receive_verdict("SUSPICIOUS", ...)` writes a drift alert, emits a
   GovernanceObservation, and logs through AuditManager.
3. `receive_verdict("ATTACKER", ...)` writes a drift alert, emits a
   GovernanceObservation, and logs through AuditManager.
4. Verdict handling never returns or emits a public `ALLOW`, `DENY`, `HALT`, or
   `ESCALATE` decision by itself.
5. Canary hit writes a drift alert and emits a GovernanceObservation.
6. Canary hit escalation path is explicit and tested:
   either no direct ExecutionGate call, or only a canonical router/gate call
   with Phase 4 prechecks included.
7. Canary hit does not execute an action callable.
8. Governance denial feedback writes `denial_*.json` only when an IP is present
   and does not alter the ExecutionGate denial result.
9. Denial feedback write failure is visible in logs or an observation and does
   not change allow/deny semantics.
10. Audit relay valid JSONL row records an AcceptanceLedger `AUDIT_LOCK`.
11. Audit relay invalid JSONL row is skipped with a visible warning and does not
    stop the relay loop.
12. Audit relay AcceptanceLedger failure is reported and does not authorize or
    deny execution.
13. Chimera endpoint rejects unsigned payloads.
14. Chimera endpoint rejects invalid signatures.
15. Chimera endpoint rejects stale timestamps.
16. Chimera endpoint rejects replayed nonces or repeated event IDs.
17. Chimera endpoint accepts a valid signed verdict payload and calls
    `receive_verdict(...)` exactly once.
18. Chimera endpoint accepts a valid signed canary payload and calls
    `receive_canary_hit(...)` exactly once.
19. Sovereign audit mode makes a Chimera bridge event reachable through
    `SovereignAuditLog` via `AuditManager`.
20. No public EvidenceBundle or GovernanceOutcome schema changes are required.

## 12. Stop Conditions Before Implementation

Stop before implementation if any of these are true:

- Chimera verdicts are expected to directly deny, allow, halt, or approve
  Project-AI execution.
- Webhook authentication, timestamp validation, and replay protection are not
  authorized for production-facing endpoints.
- The repair requires adding a new public EvidenceBundle outcome.
- The repair requires changing `GovernanceOutcome`.
- The repair requires changing EvidenceBundle public schema.
- The repair requires changing ExecutionGate allow/deny behavior.
- The repair requires changing Phase 4 router precheck behavior.
- The repair requires touching capability bridge files.
- The repair requires touching Phase 5 GovernanceService fallback behavior.
- The repair requires touching Phase 6 CognitionKernel fallback behavior.
- Canary escalation must keep using OctoReflex direct-to-gate behavior without
  an explicit receipt and authority-boundary test.
- Audit relay must become an authority source instead of a receipt source.
- Chimera needs TARL, cognition, pipeline, OctoReflex, or IronPathExecutor
  consolidation to be safe.
- Canonical replay is requested implicitly rather than explicitly authorized.

## 13. Recommended Phase 7 Implementation Scope

Recommended scope: bridge-local observer and receipt hardening only.

Likely implementation files:

- `src/app/security/chimera/chimera.py`
- `src/app/security/chimera_bridge.py`
- `governance/triumvirate_server.py`
- `tests/test_chimera_runtime.py`
- a new focused endpoint/auth test file if needed, for example
  `tests/test_chimera_bridge_endpoints.py`

Possible support-only test files:

- `tests/test_governance_observability.py`
- `tests/test_audit_manager.py`
- `tests/test_execution_gate_enforcement.py`
- `tests/test_execution_router_hardening.py`

Do not modify in Phase 7 without separate authorization:

- `src/app/core/execution_gate.py`
- `src/app/core/execution_router.py`
- `src/app/core/cognition_kernel.py`
- `src/app/core/services/governance_service.py`
- `src/app/core/capability_authority_bridge.py`
- `src/app/core/capability_token.py`
- `src/psia/canonical/capability_authority.py`
- `src/app/core/governance/pipeline.py`
- `src/app/core/octoreflex.py`
- `src/app/core/governance/iron_path_executor.py`
- EvidenceBundle public schema
- GovernanceOutcome public schema

Recommended implementation shape:

1. Keep Chimera verdicts non-authoritative.
2. Add signed webhook verification before endpoint forwarding.
3. Add bridge-local observations for Chimera-originated signals.
4. Add bridge-local AuditManager receipts for Chimera-originated signals.
5. Preserve drift alert files as compatibility output.
6. Preserve AcceptanceLedger relay as a separate audit-stream receipt.
7. Treat canary escalation as an escalation request with an explicit receipt,
   not a direct authority decision.
8. Avoid ExecutionGate/router/cognition/governance-service source changes.

## Implementation Authorization Assessment

Phase 7 full wiring is not safe to authorize yet as an unrestricted
implementation.

Phase 7 is safe to authorize only as a tests-first, bridge-local observer and
receipt hardening repair under these constraints:

- Chimera webhook payloads must be authenticated and replay-protected before
  being treated as governance input.
- Chimera verdicts must remain non-authoritative observations.
- Canary escalation must not create a silent direct authority path.
- Chimera bridge events must get explicit GovernanceObservation and AuditManager
  receipts if the project wants them to participate in the Phase 2 audit spine.
- No public schema changes are required.
- Existing ExecutionGate, router, capability bridge, GovernanceService,
  CognitionKernel, pipeline, OctoReflex, and IronPathExecutor behavior must not
  be changed in Phase 7.

Exact blockers before authorization:

1. Decide the webhook authentication contract:
   header names, signing algorithm, timestamp window, replay nonce/event ID, and
   fail-closed behavior.
2. Decide the canary escalation boundary:
   keep it observation-only in Phase 7, or route it through a canonical
   router/gate path with tests proving Phase 4 prechecks are not skipped.
3. Decide whether Chimera bridge events must reach both
   `GovernanceObservation` and `AuditManager`, or whether one receipt layer is
   sufficient for Phase 7.
4. Decide whether existing drift alert JSON files remain compatibility output
   after direct observation/audit receipts are added.
5. Add tests proving Chimera never emits a direct public governance decision.
