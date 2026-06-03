# Iron Path 2.0 Phase 3 Capability Authority Compatibility Bridge Plan

Status: planning only. Do not implement Phase 3 from this document without an
explicit follow-up authorization.

## Requirements Contract

Language and runtime:
- Python 3.12 on Windows/PowerShell with `PYTHONPATH=src`.

Inputs:
- ExecutionGate Stage 6 reads `context["_capability_token"]`.
- Legacy tokens are `app.core.capability_token.CapabilityToken` instances.
- Canonical tokens are `psia.schemas.capability.CapabilityToken` instances or
  validated dictionaries with the same schema.
- Required action comes from `ExecutionGate.execute(domain, action, context, ...)`.
- Legacy required scope comes from `context["required_scope"]`.
- Canonical resource should come from `context["required_resource"]` or
  `context["resource"]`; if neither is present for a canonical token, the
  bridge must fail closed.

Outputs:
- Stage 6 must continue to produce `(ok: bool, reason: str)` verification
  results before `ExecutionGate` emits an evidence bundle or executes.
- Existing `ExecutionGate.execute(...) -> tuple[bool, Any]` behavior must remain
  unchanged outside the audit/authorization reason text for capability failures.

Constraints:
- No public schema changes.
- No abrupt replacement of legacy HMAC validation.
- No capability-token issuance during ExecutionGate validation.
- Canonical Ed25519 verification must fail closed for unknown, expired,
  replayed, wrong-scope, revoked, malformed, or bad-signature tokens.
- Legacy compatibility must be explicit and must not silently allow the
  `dev-secret-change-in-production` default secret.

Edge cases:
- Missing token where token is required.
- Token object has neither legacy nor canonical shape.
- Canonical token is well formed but unknown to the authority.
- Canonical token signature was produced by a different authority key.
- Canonical token is expired, revoked, replayed, wrong-scope, or malformed.
- Legacy token is valid but `CAPABILITY_TOKEN_SECRET` is missing or default.
- Legacy token is expired, replayed, wrong action, wrong scope, wrong context,
  wrong policy hash, or bad HMAC.

## 1. Current Capability Authority Path

Current execution path:

```text
ExecutionGate.execute()
  Stage 6
    context["_capability_token"]
    app.core.capability_token.CapabilityTokenService.verify(...)
```

`src/app/core/capability_token.py` is the active issuer and validator on the
ExecutionGate path. It signs an app-local dataclass token using HMAC-SHA256 and
consumes token IDs in an in-process `_USED_TOKENS` set.

The intended canonical authority is present but not wired into this path:

```text
src/psia/canonical/capability_authority.py
  CapabilityAuthority.issue(...)
  CapabilityAuthority.revoke(...)
  CapabilityAuthority.is_valid(...)
  CapabilityAuthority.verify_token_signature(...)
```

The canonical token schema lives in `src/psia/schemas/capability.py`.

## 2. Current ExecutionGate Stage 6 Behavior

`src/app/core/execution_gate.py` Stage 6 currently:
- Reads `cap_token = context.get("_capability_token")`.
- Determines whether a token is required via `_requires_capability_token(...)`.
- Denies protected execution when a required token is missing.
- Imports `CapabilityTokenService` from `app.core.capability_token`.
- Calls `cts.verify(cap_token, action, required_scope=..., current_context_hash=..., current_policy_hash=...)`.
- Emits a denial evidence bundle and returns
  `"CapabilityToken rejected: {reason}"` when verification fails.
- Emits a denial evidence bundle and returns
  `"CapabilityToken verification failed closed: {exc}"` on verification errors.

Stage 6 does not currently:
- Detect canonical Ed25519 token schema.
- Call `CapabilityAuthority`.
- Check canonical token revocation on the ExecutionGate path.
- Check canonical token replay on the ExecutionGate path.
- Enforce canonical resource/action scope on the ExecutionGate path.

## 3. Legacy HMAC Token Behavior

`src/app/core/capability_token.py`:
- Mints `CapabilityToken` dataclass instances.
- Uses env var `CAPABILITY_TOKEN_SECRET`.
- Falls back to the default string `dev-secret-change-in-production`.
- Signs the token's JSON payload excluding `signature` with HMAC-SHA256.
- Rejects replayed tokens using process-local `_USED_TOKENS`.
- Rejects expired tokens.
- Rejects invalid signatures.
- Rejects wrong action.
- Rejects wrong scope.
- Rejects context hash mismatch.
- Rejects stale policy hash.
- Consumes the token ID on success.

Existing receipts:
- `tests/test_capability_tokens.py` covers valid, expired, replay, wrong action,
  wrong scope, context hash, policy hash, bad signature, field presence, and
  serialization.
- `tests/test_replay_protection.py` covers token consumption and replay audit
  logging.
- `tests/test_governance_contract.py` covers expired/replayed capability tokens
  as a governance contract point.

Gap:
- No test currently proves `ExecutionGate` Stage 6 rejects the dev-default
  secret.
- No test currently makes legacy compatibility an explicit bridge decision.

## 4. Canonical Ed25519 CapabilityAuthority Behavior

`src/psia/canonical/capability_authority.py`:
- Creates an Ed25519 keypair at authority initialization.
- Issues `psia.schemas.capability.CapabilityToken` records.
- Signs `CapabilityToken.compute_hash()` with Ed25519.
- Stores issued tokens in `_tokens`.
- Records revoked IDs in `_revoked`.
- Maintains an audit list and revocation list.
- Supports `issue`, `revoke`, `rotate`, `is_revoked`, `is_valid`,
  `get_token`, and `verify_token_signature`.

`src/psia/schemas/capability.py`:
- Defines resource/action scopes with glob resource matching.
- Defines token delegation and binding fields.
- Computes token hashes excluding `signature`.
- Exposes `covers(action, resource)`.

Existing receipts:
- `tests/test_psia_canonical.py` covers issue, self-issuance block, excessive
  scope block, revoke, idempotent revoke, rotate, expiry, active count, audit
  log, get token, delegation policy, and revocation list.
- `tests/test_psia_gate.py` covers PSIA `CapabilityHead` allow, token not
  found, revoked, expired, scope mismatch, resource mismatch, subject mismatch,
  and open mode.
- `tests/test_psia_schemas.py` covers canonical token round trip, hash
  determinism, scope action/resource matching, and token coverage.
- `tests/test_psia_integration.py` covers issue/revoke and storing issued token
  metadata in a canonical store.

Gap:
- No production ExecutionGate path exercises `CapabilityAuthority`.
- `CapabilityAuthority` is process-local. A bridge must use the same authority
  instance that issued the token or a key-store/public-key resolver. Creating a
  fresh authority during verification will make valid tokens unverifiable.
- Canonical authority has revocation and expiry checks, but no built-in
  one-time-use replay consumption on the ExecutionGate path.

## 5. Compatibility Bridge Design

Add a small adapter rather than replacing Stage 6 directly with canonical
authority calls.

Recommended new module:

```text
src/app/core/capability_authority_bridge.py
```

Responsibilities:
- Provide `CapabilityAuthorityBridge.verify(...) -> tuple[bool, str]`.
- Accept only the Stage 6 verification inputs.
- Detect legacy HMAC tokens versus canonical Ed25519 tokens.
- Dispatch legacy tokens to `CapabilityTokenService.verify(...)` only when
  explicit compatibility conditions are met.
- Dispatch canonical tokens to a configured `CapabilityAuthority`.
- Maintain bridge-level replay protection for canonical token IDs.
- Fail closed for malformed or unknown token shapes.

Proposed data flow:

```text
ExecutionGate Stage 6
  -> get_capability_authority_bridge().verify(
       token=cap_token,
       action=action,
       required_scope=context.get("required_scope", []),
       resource=context.get("required_resource") or context.get("resource", ""),
       current_context_hash=context_hash,
       current_policy_hash=policy_hash_val,
       actor=context.get("actor") or domain,
     )
  -> existing ExecutionGate denial/evidence behavior
```

Legacy HMAC compatibility:
- Explicitly identify app-core HMAC tokens by dataclass shape.
- Require a non-default `CAPABILITY_TOKEN_SECRET`.
- Optionally require `context["capability_token_format"] == "legacy_hmac"` or
  bridge config `allow_legacy_hmac=True` during the compatibility window.
- Preserve the existing `CapabilityTokenService.verify(...)` checks and replay
  consumption.
- Return a reason that identifies the legacy path without changing ALLOW/DENY
  semantics.

Canonical Ed25519 validation:
- Parse/validate token as `psia.schemas.capability.CapabilityToken`.
- Require a configured authority provider; do not instantiate a fresh authority
  per verification.
- Require `authority.get_token(token.token_id)` to exist, or require an
  explicitly documented public-key lookup if the implementation chooses detached
  verification.
- Verify `authority.verify_token_signature(token)`.
- Verify `authority.is_valid(token.token_id)`.
- Verify `not authority.is_revoked(token.token_id)`.
- Verify the token has not been consumed by the bridge replay store.
- Verify `token.covers(action, resource)`.
- Verify `token.subject` matches the actor or a documented delegable subject
  rule.
- Consume the canonical token ID only after all checks pass.

Fail-closed behavior:
- Unknown token shape: deny.
- Canonical token without resource: deny.
- No authority provider: deny.
- Default legacy HMAC secret: deny.
- Any parse/signature/revocation/replay/scope exception: deny.

## 6. Files That Would Need Modification

Likely source modifications during Phase 3 implementation:
- `src/app/core/execution_gate.py`
  - Replace Stage 6 direct `CapabilityTokenService` call with the bridge call.
  - Preserve missing-token behavior and existing evidence bundle behavior.
- `src/app/core/capability_authority_bridge.py`
  - New narrow adapter module.
- `src/app/core/capability_token.py`
  - Prefer no behavioral changes. If unavoidable, only add a query/helper for
    default-secret detection; otherwise the bridge can inspect env directly.
- `src/psia/canonical/capability_authority.py`
  - Prefer no changes. If unavoidable, only add a safe authority provider or
    verifier helper after stopping for approval.
- `src/psia/schemas/capability.py`
  - No planned changes.

Likely test modifications/additions:
- `tests/test_capability_authority_bridge.py`
  - New bridge unit tests.
- `tests/test_execution_gate_enforcement.py`
  - Add Stage 6 bridge integration tests for ExecutionGate.
- `tests/test_governance_contract.py`
  - Extend capability-token-scoped contract to mention canonical bridge
    behavior after implementation.
- `tests/test_capability_tokens.py`
  - Keep legacy HMAC service tests; set non-default secret where needed if the
    bridge or service starts enforcing default-secret blocking.
- `tests/test_replay_protection.py`
  - Keep legacy replay tests; add canonical replay coverage in bridge tests.

## 7. Tests That Must Exist Before Implementation

Before touching Stage 6, Phase 3 should have failing tests or test plans for:
- Bridge accepts a valid canonical Ed25519 token issued by the configured
  `CapabilityAuthority`.
- Bridge denies expired canonical tokens.
- Bridge denies replayed canonical tokens.
- Bridge denies wrong-scope canonical tokens.
- Bridge denies revoked canonical tokens.
- Bridge denies malformed tokens.
- Bridge preserves explicit legacy HMAC compatibility behavior.
- Bridge denies legacy HMAC tokens when the secret is the dev default or absent.
- ExecutionGate Stage 6 routes through the bridge and preserves executor
  execution/non-execution semantics.
- Existing HMAC token service tests continue to pass for direct service
  compatibility unless Phase 3 explicitly changes that contract.

## 8. New Tests Required

Required new receipt tests:

1. Valid Ed25519 token accepted
   - Issue a token using a shared `CapabilityAuthority`.
   - Pass that token through the bridge with matching action/resource/actor.
   - Assert `(True, "OK" or equivalent)`.

2. Expired token denied
   - Issue with zero/negative TTL or mutate expiry into the past.
   - Assert deny and reason mentions expiry.

3. Replayed token denied
   - Verify the same canonical token twice through the bridge.
   - Assert first pass allows and second pass denies.

4. Wrong-scope token denied
   - Issue token for a different action or resource.
   - Assert deny and reason mentions scope/resource.

5. Revoked token denied
   - Issue then revoke through the same `CapabilityAuthority`.
   - Assert bridge denies.

6. Malformed token denied
   - Pass dicts/objects missing canonical and legacy required fields.
   - Assert fail-closed denial, not exception leakage.

7. Legacy HMAC token compatibility behavior explicit
   - Set a non-default `CAPABILITY_TOKEN_SECRET`.
   - Mint a legacy HMAC token.
   - Enable legacy compatibility explicitly.
   - Assert bridge accepts it and consumes replay through the existing service.

8. Dev-default secret behavior blocked or clearly fail-closed
   - Ensure `CAPABILITY_TOKEN_SECRET` is absent or equals
     `dev-secret-change-in-production`.
   - Attempt legacy HMAC bridge verification.
   - Assert deny before execution.

ExecutionGate integration tests:
- Protected action with valid canonical token executes.
- Protected action with revoked canonical token does not execute.
- Protected action with replayed canonical token does not execute on second use.
- Protected action with default-secret legacy token does not execute.
- Missing-token behavior remains unchanged.
- Degraded read-only behavior remains unchanged.

## 9. Stop Conditions Before Implementation

Stop before modifying code if any of these are true:
- The bridge requires changing `psia.schemas.capability.CapabilityToken`.
- The bridge requires changing public `ExecutionGate.execute(...)` signature.
- The implementation cannot access the same `CapabilityAuthority` instance or a
  valid authority public-key resolver.
- Canonical token replay prevention cannot be implemented without global
  mutable state that tests cannot isolate.
- Default legacy secret fail-closed behavior would break existing direct
  `CapabilityTokenService` tests without an explicit compatibility decision.
- Scope mapping from ExecutionGate context to canonical `resource` is ambiguous.
- Capability migration work expands into unrelated authority paths.
- Any ALLOW/DENY behavior outside Stage 6 changes.
- Any implementation path touches canonical replay or Phase 4+ substrate work.

## 10. Recommended Implementation Sequence

1. Add failing bridge unit tests in `tests/test_capability_authority_bridge.py`.
2. Add failing ExecutionGate Stage 6 integration tests in
   `tests/test_execution_gate_enforcement.py`.
3. Implement `src/app/core/capability_authority_bridge.py` with dependency
   injection for authority and replay store.
4. Add a `get_capability_authority_bridge()` singleton only after unit tests use
   direct injection.
5. Wire `ExecutionGate` Stage 6 to the bridge with the smallest replacement of
   the existing `CapabilityTokenService` block.
6. Preserve legacy HMAC direct service behavior; make bridge compatibility
   explicit and reject default-secret bridge use.
7. Run the focused tests:
   - `py -3.12 -m pytest tests/test_capability_authority_bridge.py -v`
   - `py -3.12 -m pytest tests/test_execution_gate_enforcement.py -v`
   - `py -3.12 -m pytest tests/test_capability_tokens.py tests/test_replay_protection.py -v`
   - `py -3.12 -m pytest tests/test_governance_contract.py -v`
   - `py -3.12 -m pytest tests/test_psia_canonical.py tests/test_psia_gate.py tests/test_psia_schemas.py -v`
8. Run the Phase 2 audit validation set again to ensure audit routing did not
   regress.
9. Run `git diff --check` and `git status --short`.
10. Do not run `canonical/replay.py` unless separately authorized.

## Implementation Safety Assessment

Implementation is not safe as an abrupt replacement of HMAC Stage 6 validation.
It is safe to authorize only as a narrow compatibility-bridge implementation
after the Phase 3 tests above are added first.

Exact blockers before implementation:
- No existing bridge test proves a canonical Ed25519 token can pass through
  ExecutionGate Stage 6.
- No current ExecutionGate test covers canonical token expiry, replay, scope,
  revocation, malformed input, or dev-default HMAC fail-closed behavior.
- The canonical authority is process-local; Phase 3 must decide how Stage 6 gets
  the same authority instance or a key resolver.
- Canonical resource mapping from `ExecutionGate` context must be explicit.
- Legacy HMAC compatibility mode and dev-default secret rejection must be
  defined before changing Stage 6.
