# Iron Path 2.0 - Phase 1 Annotation Report

**Date:** 2026-06-03
**Scope:** Phase 1 annotations only.
**Behavior change:** None intended. This pass added comments and this report only.

## 1. Files Changed

| File | Stop condition |
|---|---|
| `src/app/core/governance_kernel.py` | Audit path writes directly to `AuditLog()` |
| `src/app/core/capability_token.py` | Active legacy HMAC capability authority |
| `src/psia/canonical/capability_authority.py` | Canonical Ed25519 authority is not wired |
| `src/psia/schemas/capability.py` | Canonical capability schema is not the active authority |
| `src/app/core/execution_gate.py` | Stage 6 uses legacy `CapabilityTokenService` |
| `src/app/core/services/governance_service.py` | `_auto_approve()` parallel authority |
| `src/app/governance/runtime_enforcer.py` | Zero-bypass claim contradicted by router bypass |
| `src/app/core/execution_router.py` | Execution authority fragmentation and silent bypasses |
| `src/app/governance/genesis_continuity.py` | Core substrate has unresolved working-tree modifications |
| `src/app/core/governance/pipeline.py` | Pipeline path calls `IronPathExecutor` directly |
| `src/app/core/octoreflex.py` | OctoReflex calls `ExecutionGate` directly |
| `src/app/core/governance/iron_path_executor.py` | Mutation binding can be reached outside canonical lifecycle |
| `src/app/core/runtime/router.py` | Runtime router sends requests to the pipeline fragment |

## 2. Exact Annotations Added

Every source annotation uses the required marker:

```text
IRON_PATH_2_PHASE_1_ANNOTATION_ONLY
IRON_PATH_2_STOP_CONDITION: <short name>
Current behavior: <plain factual statement>
Required before Phase 2+: <what must be repaired later>
Do not change behavior in Phase 1.
```

| File | `IRON_PATH_2_STOP_CONDITION` | Current behavior annotation | Required before Phase 2+ annotation |
|---|---|---|---|
| `src/app/core/governance_kernel.py` | `audit path direct AuditLog approval write` | `governance_kernel.py writes approval events directly through AuditLog(), so AuditManager and SovereignAuditLog are not reached on this normal kernel path.` | `Route governance audit writes through audit_manager.py, with sovereign-grade events reaching sovereign_audit_log.py.` |
| `src/app/core/governance_kernel.py` | `audit path direct AuditLog denial write` | `governance_kernel.py writes denial events directly through AuditLog(), so AuditManager and SovereignAuditLog are not reached on this normal kernel path.` | `Route governance audit writes through audit_manager.py, with sovereign-grade events reaching sovereign_audit_log.py.` |
| `src/app/core/capability_token.py` | `active legacy HMAC capability authority` | `capability_token.py is the active HMAC-SHA256 token issuer/validator and can fall back to a dev-default secret.` | `Introduce a compatibility bridge before wiring canonical Ed25519 CapabilityAuthority; prove fail-closed behavior for expired, replayed, wrong-scope, revoked, legacy, and malformed tokens.` |
| `src/psia/canonical/capability_authority.py` | `canonical capability authority not wired` | `CapabilityAuthority is the intended Ed25519 authority, but production execution paths do not call it.` | `Wire it through a compatibility bridge with tests for expired, replayed, wrong-scope, revoked, legacy, and malformed tokens.` |
| `src/psia/schemas/capability.py` | `canonical capability schema not active authority` | `this Ed25519-backed schema supports the intended canonical authority, but ExecutionGate validates the legacy app.core capability token path.` | `Add a compatibility bridge before canonical authority migration and prove fail-closed handling for invalid token states.` |
| `src/app/core/execution_gate.py` | `ExecutionGate legacy capability validation` | `Stage 6 validates _capability_token with app.core.capability_token.CapabilityTokenService instead of the canonical Ed25519 CapabilityAuthority.` | `Introduce a compatibility bridge before canonical authority migration and prove fail-closed behavior for expired, replayed, wrong-scope, revoked, legacy, and malformed tokens.` |
| `src/app/core/services/governance_service.py` | `auto-approval parallel authority` | `_auto_approve() can approve low-risk or routine actions when no Triumvirate or governance system is configured, without producing the canonical EvidenceBundle path.` | `Disable it, route it through ExecutionGate/EvidenceBundle/audit_manager, or constrain it as explicitly non-authoritative.` |
| `src/app/governance/runtime_enforcer.py` | `RuntimeEnforcer zero-bypass claim contradicted` | `execution_router.py can silently pass RuntimeEnforcer failures, so this module's zero-bypass claim is not system-wide true.` | `Replace silent router bypass with fail-closed behavior or an EvidenceBundle-producing BYPASS_RECORDED outcome.` |
| `src/app/core/execution_router.py` | `execution authority fragmentation` | `execution_router.py is one execution authority fragment, while pipeline.py and OctoReflex can enter governance through other paths.` | `Build a caller-map-driven consolidation so no execution path bypasses ExecutionGate unless explicitly classified as test-only or non-authoritative.` |
| `src/app/core/execution_router.py` | `silent RuntimeEnforcer bypass` | `any RuntimeEnforcer import, init, or enforcement exception is silently ignored and execution continues without a RuntimeEnforcer receipt.` | `Replace silent pass with fail-closed behavior or an EvidenceBundle-producing BYPASS_RECORDED outcome.` |
| `src/app/core/execution_router.py` | `silent StateRegister context bypass` | `any StateRegister exception is silently ignored and execution continues without temporal context.` | `Replace silent pass with fail-closed behavior or an EvidenceBundle-producing BYPASS_RECORDED outcome.` |
| `src/app/core/execution_router.py` | `silent trust/adversarial context bypass` | `trust scoring or adversarial pattern failures are silently ignored and execution continues without those context signals.` | `Replace silent pass with fail-closed behavior or an EvidenceBundle-producing BYPASS_RECORDED outcome.` |
| `src/app/governance/genesis_continuity.py` | `genesis continuity working-tree state unresolved` | `genesis_continuity.py has unstaged modifications, so this core substrate's current state is not clean.` | `The user must decide whether to keep, commit, or revert the existing modifications, then baseline tests must be re-run.` |
| `src/app/core/governance/pipeline.py` | `pipeline execution authority fragment` | `pipeline.py calls IronPathExecutor directly for mutation binding instead of entering through execution_router.py and the full ExecutionGate wrapper.` | `Use a caller-map-driven consolidation so no authoritative execution path bypasses ExecutionGate unless explicitly test-only or non-authoritative.` |
| `src/app/core/octoreflex.py` | `OctoReflex direct gate authority fragment` | `OctoReflex calls ExecutionGate directly, bypassing the execution_router wrapper and its pre-gate RuntimeEnforcer, StateRegister, and trust/adversarial context steps.` | `Use a caller-map-driven consolidation so direct gate calls are either routed through the canonical wrapper or classified as explicit enforcement-only exceptions.` |
| `src/app/core/governance/iron_path_executor.py` | `IronPathExecutor direct binding authority fragment` | `bind_mutation() can be reached directly from pipeline.py, so mutation binding may occur outside the full execution_router plus ExecutionGate lifecycle.` | `Consolidate callers so this executor is downstream of the canonical authority path or explicitly scoped as non-authoritative.` |
| `src/app/core/runtime/router.py` | `runtime router pipeline authority fragment` | `runtime router sends requests to governance.pipeline.enforce_pipeline(), which is a parallel path from execution_router.py.` | `Use a caller-map-driven consolidation so router traffic reaches the canonical ExecutionGate lifecycle or is explicitly classified as non-authoritative.` |

## 3. Stop Condition Mapping

| Stop condition | Files annotated |
|---|---|
| Audit path stop condition | `src/app/core/governance_kernel.py` |
| Capability authority stop condition | `src/app/core/capability_token.py`, `src/psia/canonical/capability_authority.py`, `src/psia/schemas/capability.py`, `src/app/core/execution_gate.py` |
| Auto-approval parallel authority stop condition | `src/app/core/services/governance_service.py` |
| RuntimeEnforcer zero-bypass false claim stop condition | `src/app/governance/runtime_enforcer.py`, `src/app/core/execution_router.py` |
| Repo cleanliness stop condition | `src/app/governance/genesis_continuity.py` |
| Execution authority fragmentation notice | `src/app/core/execution_router.py`, `src/app/core/governance/pipeline.py`, `src/app/core/octoreflex.py`, `src/app/core/governance/iron_path_executor.py`, `src/app/core/runtime/router.py` |

## 4. Phase 1 Confirmations

- No runtime behavior changed.
- No imports changed.
- No function signatures changed.
- No schemas changed.
- No authority path changed.
- No cryptographic logic changed.
- No deletion occurred.
- No refactor occurred.
- No formatter was run.
- No baseline tests were run in this annotation-only pass.
- Phases 2-5 remain blocked.

`src/app/governance/genesis_continuity.py` already had unstaged logic changes before this pass. The Phase 1 change to that file is the stop-condition comment only.

## 5. Prerequisites Before Phase 2

1. Resolve `src/app/governance/genesis_continuity.py` working-tree state.
2. Re-run baseline tests on the current tree.
3. Formally acknowledge all five active stop conditions.
4. Review the Phase 1 diff.
5. Commit Phase 1 annotations separately.

## 6. Suggested First Phase 2 Target

`src/app/core/governance_kernel.py` -> `src/app/governance/audit_manager.py` -> `src/app/governance/sovereign_audit_log.py`

This targets the audit path stop condition first without replacing token validation or changing execution routing.
