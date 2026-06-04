# Iron Path 2.0 Phase 8: Chimera Endpoint Forwarding Plan

Status: planning only. Do not implement until authorized.

## Context

Phase 7 closed the Chimera bridge as an observer/receipt-only path:

- `ChimeraBridge.receive_authenticated_event(...)` verifies HMAC-SHA256
  signatures, timestamp freshness, and event replay before recording a Chimera
  event.
- Accepted events stay non-authoritative.
- Accepted events can emit `GovernanceObservation` and relay through
  `AuditManager`.
- Chimera does not directly emit public `ALLOW`, `DENY`, or `HALT` decisions.
- Chimera does not call `ExecutionGate` or OctoReflex as a gate.

Commit context from Phase 7:

- Commit hook passed with the legacy `ALLOW_NON_VAULT_CHANGES=1` override.
- Pre-existing LFS warnings appeared during commit but were unrelated to the
  staged Phase 7 files.

Phase 8 is the endpoint adapter follow-up: wire the live Triumvirate HTTP
handlers so they forward the signed Chimera event envelope into the hardened
Phase 7 bridge without weakening fail-closed behavior.

## Files Inspected

- `AGENTS.md`
- `.github/instructions/mandatory-structured-generation-default.instructions.md`
- `governance/triumvirate_server.py`
- `src/app/main.py`
- `src/app/security/chimera_bridge.py`
- `src/app/security/chimera/chimera.py`
- `tests/test_chimera_runtime.py`
- `tests/test_governance_server.py`
- `tests/test_api.py`
- `src/app/core/governance_observability.py`
- `src/app/governance/audit_manager.py`
- `src/app/governance/sovereign_audit_log.py`
- `src/utf/docs/TRIUMVIRATE_SPEC.md`
- `docs/governance/iron_path_2_phase_7_chimera_wiring_plan.md`

## Requirements Contract

- Language/runtime: Python 3.12, existing FastAPI/Pydantic stack.
- Environment: Windows/PowerShell with `PYTHONPATH=src`.
- Input contract: inbound `POST /chimera/verdict` and `POST /chimera/canary`
  JSON payloads emitted by `src/app/security/chimera/chimera.py`, including
  signed event metadata.
- Output contract: HTTP transport response plus receipt-producing bridge result.
  No public governance decision schema changes.
- Security contract: fail closed on missing, invalid, stale, replayed, or
  malformed Chimera webhook authentication data.
- Authority contract: endpoint and Chimera bridge remain observer/receipt only.
  They may not directly allow, deny, halt, execute, or call OctoReflex as a gate.
- Dependency contract: use existing `ChimeraBridge.receive_authenticated_event`
  as the authentication and receipt boundary. Do not introduce a second
  signature verifier unless a test proves the bridge API cannot support the HTTP
  adapter.
- Edge cases: missing signature, invalid signature, stale timestamp, missing
  timestamp, replayed `event_id` or `nonce`, body/header mismatch, unsupported
  event type, malformed hits list, bridge unavailable, receipt degradation,
  existing drift/canary payload compatibility, and accidental public authority
  emission.

## 1. Current HTTP/Triumvirate Endpoint Path

Current live path:

1. `src/app/security/chimera/chimera.py` calls `_notify_governance(...)` or
   `_notify_canary(...)`.
2. The runtime builds a payload with `event`, `event_id`, `timestamp`, `ts`, and
   a HMAC-SHA256 `signature`.
3. The runtime also sends headers:
   - `X-Chimera-Event-Id`
   - `X-Chimera-Timestamp`
   - `X-Chimera-Signature`
4. The runtime posts to:
   - `WEBHOOK_URL + "/chimera/verdict"`
   - `WEBHOOK_URL + "/chimera/canary"`
5. `governance/triumvirate_server.py` exposes:
   - `POST /chimera/verdict`
   - `POST /chimera/canary`
6. Those endpoint handlers currently parse old payload models:
   - `ChimeraVerdictPayload`
   - `ChimeraCanaryPayload`
7. The handlers then call old bridge methods:
   - `get_bridge().receive_verdict(...)`
   - `get_bridge().receive_canary_hit(...)`

The Triumvirate server is started by `src/app/main.py` through
`_start_triumvirate_server()`, which imports `governance.triumvirate_server.app`
and runs it on `127.0.0.1:8001`.

## 2. Current Signed-Field Forwarding

The endpoint currently does not forward the Phase 7 signed envelope.

Current `ChimeraVerdictPayload` declares only:

- `ip`
- `verdict`
- `score`
- `sid`
- `path`
- `ts`

Current `ChimeraCanaryPayload` declares only:

- `ip`
- `sid`
- `hits`
- `ts`

Missing or unused at the endpoint boundary:

- `signature`
- `event`
- `event_id`
- `nonce`
- `timestamp`
- `X-Chimera-Signature`
- `X-Chimera-Event-Id`
- `X-Chimera-Timestamp`

The current handlers do not accept `Request`, do not read FastAPI headers, and
do not pass `ts` to the bridge. Any signed metadata supplied by the Phase 7
runtime is therefore dropped before it reaches `ChimeraBridge`.

## 3. Can The Endpoint Bypass Phase 7 Bridge Authentication?

The endpoint cannot successfully bypass the hardened bridge by using the old
direct bridge methods, because Phase 7 changed `receive_verdict(...)` and
`receive_canary_hit(...)` to require `authenticated=True`.

Current behavior after Phase 7:

- `POST /chimera/verdict` calls `receive_verdict(...)` without
  `authenticated=True`.
- `POST /chimera/canary` calls `receive_canary_hit(...)` without
  `authenticated=True`.
- The bridge raises `ChimeraWebhookAuthError("Missing authenticated Chimera
  envelope")`.
- The endpoint catches the exception and returns `{"status": "error",
  "detail": ...}`.

Concern:

- The endpoint currently returns a generic JSON error instead of a clear HTTP
  auth failure status.
- The endpoint does not use the signed envelope at all.
- This is fail-closed for receipts, but not yet wired for live signed event
  forwarding.

## 4. Required Signed-Field Contract

Recommended contract for Phase 8:

Required JSON fields for both endpoint paths:

- `event`: `threat_verdict` or `canary_hit`
- `event_id` or `nonce`
- `timestamp` or `ts`
- event payload fields:
  - verdict: `ip`, `verdict`, `score`, optional `sid`, optional `path`
  - canary: `ip`, optional `sid`, `hits`

Required signature source:

- Accept `X-Chimera-Signature` as the primary signature source.
- Accept body `signature` only as a compatibility fallback.
- If both header and body signature are present and differ after stripping an
  optional `sha256=` prefix, fail closed.

Required supporting headers:

- `X-Chimera-Event-Id` should match body `event_id` or `nonce` when present.
- `X-Chimera-Timestamp` should match body `timestamp` or `ts` when present.
- Header mismatch should fail closed.

Canonical verification boundary:

- Forward the full sanitized event dictionary and the selected signature to
  `ChimeraBridge.receive_authenticated_event(event, signature=...)`.
- Do not call `receive_verdict(..., authenticated=True)` directly from the
  endpoint. The bridge's authenticated-envelope method should be the only
  auth-to-receipt transition.
- Do not write to `GovernanceObservation`, `AuditManager`, or
  `SovereignAuditLog` directly from the endpoint.

## 5. Required Timestamp And Replay Behavior

Timestamp policy:

- Keep the Phase 7 bridge policy as the source of truth.
- Maximum allowed clock skew is 300 seconds.
- The endpoint may pre-check for missing fields, but freshness validation should
  remain in `ChimeraBridge._verify_event(...)` to avoid policy drift.
- The endpoint should not mutate timestamp values before signature verification.

Replay policy:

- Keep replay protection inside the bridge's bounded TTL cache.
- Require `event_id` or `nonce`.
- Repeated `event_id` or `nonce` within the replay window must be rejected.
- The endpoint should not introduce an independent replay cache unless a test
  proves the bridge cache cannot protect the HTTP path.

## 6. May The Endpoint Emit Authority Decisions?

No.

The Chimera endpoint may emit transport-level outcomes only, such as accepted or
rejected webhook ingestion. It must not emit public governance outcomes:

- no `ALLOW`
- no `DENY`
- no `HALT`
- no `ESCALATE` as a public governance decision

Chimera verdicts and canary hits remain non-authoritative observation and
receipt signals. They must not call `ExecutionGate`, `execution_router.py`,
`CognitionKernel`, `GovernanceService`, pipeline, OctoReflex, or
IronPathExecutor.

## 7. GovernanceObservation Reachability

Current bridge reachability:

- `ChimeraBridge.receive_authenticated_event(...)`
- `receive_verdict(...)` or `receive_canary_hit(...)` with
  `authenticated=True`
- `_emit_receipts(...)`
- `_emit_observation(...)`
- `app.core.governance_observability.build_observation(...)`
- `get_collector().record(...)`

Endpoint requirement:

- The endpoint should reach `GovernanceObservation` only through
  `receive_authenticated_event(...)`.
- The endpoint should not create a separate observation, because that would
  risk duplicate receipts and a second receipt policy.

## 8. AuditManager Reachability

Current bridge reachability:

- `ChimeraBridge.receive_authenticated_event(...)`
- `receive_verdict(...)` or `receive_canary_hit(...)` with
  `authenticated=True`
- `_emit_receipts(...)`
- `_emit_audit_manager_event(...)`
- `app.governance.audit_manager.get_audit_manager().log_security_event(...)`

`AuditManager` remains the public audit interface. In sovereign mode,
`AuditManager.log_security_event(...)` routes through `SovereignAuditLog`.

Endpoint requirement:

- The endpoint should reach `AuditManager` only through
  `receive_authenticated_event(...)`.
- The endpoint must not write directly to `SovereignAuditLog`.
- Receipt degradation should remain bridge-owned and non-authoritative.

## 9. Compatibility Impact On Existing Drift/Canary Payloads

Compatibility preserved:

- Phase 7 drift alert JSON compatibility fields remain bridge-owned:
  `source`, `event`, `ip`, `verdict`, `score`, `sid`, `path`, `timestamp`,
  `target_member`.
- Canary alert compatibility fields remain bridge-owned:
  `source`, `event`, `ip`, `sid`, `hits`, `hit_count`, `timestamp`,
  `target_member`, `severity`.
- The Chimera runtime already sends signed payload fields and `X-Chimera-*`
  headers.

Compatibility that intentionally changes:

- Old unsigned HTTP clients should fail closed.
- Tests that prove unsafe unauthenticated endpoint behavior should be updated to
  expect rejection.
- Existing bridge-level compatibility tests should remain valid because the
  endpoint should delegate to the same Phase 7 bridge path.

Potential mismatch to test:

- Runtime signature generation and bridge signature verification both canonical
  serialize sanitized fields. A Phase 8 endpoint must not strip or rewrite
  signed fields before verification.

## 10. Tests Required Before Implementation

Baseline tests before implementation:

```powershell
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_chimera_runtime.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_governance_server.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_api.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_governance_contract.py tests/test_evidence_bundle.py tests/test_audit_manager.py -v
```

New endpoint tests required, preferably in a focused file such as
`tests/test_chimera_endpoint_forwarding.py`:

1. `POST /chimera/verdict` rejects missing signature.
2. `POST /chimera/canary` rejects missing signature.
3. Invalid signature is rejected.
4. Stale timestamp older than 300 seconds is rejected.
5. Missing `event_id` and missing `nonce` are rejected.
6. Replayed `event_id` or `nonce` is rejected.
7. Header/body signature mismatch is rejected.
8. Header/body event ID mismatch is rejected.
9. Header/body timestamp mismatch is rejected.
10. Valid signed verdict is accepted and delegated through
    `receive_authenticated_event(...)`.
11. Valid signed canary is accepted and delegated through
    `receive_authenticated_event(...)`.
12. Valid signed verdict creates the existing drift alert compatibility fields.
13. Valid signed canary creates the existing canary alert compatibility fields.
14. Accepted endpoint event emits a `GovernanceObservation` through the bridge.
15. Accepted endpoint event relays through `AuditManager` through the bridge.
16. Receipt degradation remains non-authoritative.
17. Endpoint does not call `ExecutionGate`.
18. Endpoint does not call OctoReflex.
19. Endpoint does not emit public `ALLOW`, `DENY`, or `HALT`.
20. Endpoint does not write directly to `SovereignAuditLog`.

Validation after implementation:

```powershell
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_chimera_endpoint_forwarding.py tests/test_chimera_runtime.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_governance_server.py tests/test_api.py -v
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 -m pytest tests/test_governance_contract.py tests/test_evidence_bundle.py tests/test_audit_manager.py -v
```

Do not run `canonical/replay.py` unless separately authorized.

## 11. Stop Conditions Before Implementation

Stop before implementation if any of these are true:

- Phase 8 requires changing `ChimeraBridge` authentication semantics instead of
  using `receive_authenticated_event(...)`.
- Phase 8 requires accepting unsigned HTTP Chimera events.
- Phase 8 requires allowing stale or replayed events for compatibility.
- Phase 8 requires adding or changing a public `EvidenceBundle` outcome.
- Phase 8 requires changing `GovernanceOutcome`, `Decision`, or
  `ExecutionResult` public schemas.
- Phase 8 requires touching `ExecutionGate`, `execution_router.py`,
  `CognitionKernel`, `GovernanceService`, capability bridge files, pipeline,
  OctoReflex, or IronPathExecutor.
- Phase 8 requires direct `SovereignAuditLog` writes from the endpoint.
- Phase 8 requires Chimera to directly allow, deny, halt, or execute actions.
- Phase 8 cannot preserve existing drift/canary compatibility fields for
  accepted signed events.
- Tests cannot prove endpoint receipt reachability through both
  `GovernanceObservation` and `AuditManager`.

## 12. Recommended Implementation Scope

Recommended scope: endpoint adapter only.

Likely implementation files:

- `governance/triumvirate_server.py`
- `tests/test_chimera_endpoint_forwarding.py`

Do not modify unless a focused failing test proves it is required:

- `src/app/security/chimera_bridge.py`
- `src/app/security/chimera/chimera.py`
- `tests/test_chimera_runtime.py`

Do not modify in Phase 8:

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

Recommended sequence:

1. Add endpoint tests first and confirm they fail against the current endpoint.
2. Update Triumvirate Chimera endpoint models or handlers to preserve signed
   envelope fields.
3. Read `X-Chimera-*` headers and compare them against body values when both are
   present.
4. Select signature from header first, with body fallback only if header is
   absent.
5. Forward the full event dictionary to
   `get_bridge().receive_authenticated_event(event, signature=signature)`.
6. Convert `ChimeraWebhookAuthError` to explicit HTTP auth failure, without
   logging raw signatures or sensitive payloads.
7. Preserve existing success response compatibility where possible:
   - verdict: `{"status": "ok", "ip": ..., "verdict": ...}`
   - canary: `{"status": "ok", "ip": ..., "hits": ...}`
8. Keep receipt creation and degradation inside the bridge.
9. Run focused endpoint, Chimera runtime, governance server, API, contract,
   evidence bundle, and audit manager tests.
10. Run `git diff --check` and `git status --short`.

## Design

Endpoint data flow after Phase 8 should be:

```text
Chimera runtime
  -> signed JSON body + X-Chimera-* headers
  -> governance/triumvirate_server.py /chimera/* handler
  -> endpoint validates presence and header/body consistency
  -> ChimeraBridge.receive_authenticated_event(event, signature)
  -> bridge verifies HMAC, timestamp, and replay
  -> bridge records drift compatibility file
  -> bridge emits GovernanceObservation
  -> bridge relays through AuditManager
```

The endpoint should be a thin adapter. It should not make independent governance
decisions and should not duplicate bridge receipt logic.

## Pseudocode

```text
handler(request, payload):
    event = payload as plain dict
    signature = request.headers["X-Chimera-Signature"] or event["signature"]

    if signature missing:
        raise HTTP 401

    if header signature and body signature both exist but differ:
        raise HTTP 401

    if header event ID exists and body event_id/nonce exists but differs:
        raise HTTP 401

    if header timestamp exists and body timestamp/ts exists but differs:
        raise HTTP 401

    ensure event["event"] matches endpoint path

    try:
        result = get_bridge().receive_authenticated_event(event, signature=signature)
    except ChimeraWebhookAuthError:
        raise HTTP 401 or 403
    except unsupported/malformed event:
        raise HTTP 400
    except receipt/runtime failure:
        return transport error without authority decision

    return existing compatible success body plus optional non-authoritative receipt status
```

## Adversarial Self-Review

Risk: accepting a body signature fallback could permit proxy/header stripping to
hide an expected header.

Refinement: accept body fallback only because the current Phase 7 runtime sends
both body and header signatures. If production policy wants stricter behavior,
lock header-only before implementation.

Risk: copying header timestamp into the body could change the signed canonical
payload and hide malformed body data.

Refinement: require body `timestamp` or `ts`; use headers only for consistency
checks. The bridge verifies the body timestamp.

Risk: endpoint-side replay cache could drift from bridge replay policy.

Refinement: do not add endpoint replay storage. Let bridge verification own
replay protection.

Risk: endpoint success responses could be mistaken for governance authorization.

Refinement: keep responses transport-scoped and include no public governance
outcome fields. Tests must assert no `ALLOW`, `DENY`, or `HALT` appears.

## Implementation Authorization Assessment

Phase 8 is safe to authorize as a tests-first endpoint-adapter repair under the
recommended scope.

No source-level blocker was found. The bridge already has the required public
entry point, timestamp policy, replay cache, observation emission, and
`AuditManager` relay.

Exact contract decisions to lock before implementation:

1. Whether HTTP authentication failures should return `401 Unauthorized` or
   `403 Forbidden`. Recommended: `401` for missing/invalid authentication and
   `400` for structurally malformed payloads.
2. Whether body `signature` remains an accepted fallback. Recommended: accept as
   fallback for Phase 7 runtime compatibility, but fail closed if it conflicts
   with `X-Chimera-Signature`.
3. Whether headers are mandatory in production. Recommended: body fields are
   canonical; headers are consistency checks unless production explicitly locks
   header-only ingestion.

If those decisions are accepted, Phase 8 can proceed without touching
ExecutionGate, router, CognitionKernel, GovernanceService, OctoReflex,
capability bridge, public schemas, or sovereign audit internals.
