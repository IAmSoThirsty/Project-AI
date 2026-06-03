# Iron Path 2.0 — Substrate Boot Order

**Generated:** 2026-06-03  
**Branch:** `substrate-consolidation`  
**HEAD SHA:** `e3913e6c9073f488ed2d82b1afeb039e1e46e616`  
**Status:** READ-ONLY ANALYSIS — no source behavior changed

---

## 1. Dependency Graph (Static — Module-Level Imports Only)

This graph shows module-level (non-lazy) import dependencies between constitutional substrates. Lazy imports (inside functions or try/except blocks) are listed separately in Section 4.

```
Edges: A → B means "A imports B at module top level (not lazy)"

sovereign_audit_log → genesis_continuity
governance_kernel   → constitutional_ledger
                    → event_spine
                    → fates
                    → governance (Triumvirate)
                    → governance_graph
runtime_enforcer    → acceptance_ledger
                    → jurisdiction_loader
audit_manager       → sovereign_audit_log
execution_gate      → governance_kernel
                    → mutation_binding
execution_router    → execution_gate
                    → invariant_engine
                    → nirl.forge
                    → waterfall_filter
                    → liara_bridge
                    → state_register
capability_authority → psia.crypto.ed25519_provider
                     → psia.schemas.capability
                     → psia.schemas.identity
invariants (psia)   → psia.schemas.identity
                    → psia.schemas.invariant
state_register      → .tscg_codec
policy_registry     → stdlib only
genesis_continuity  → stdlib only
governance.py       → stdlib only
evidence_bundle     → stdlib only (policy_registry is lazy)
iron_path_executor  → stdlib only
capability_token    → stdlib only
```

**Leaf nodes** (no dependencies on other substrates):
`genesis_continuity`, `policy_registry`, `governance.py`, `evidence_bundle`, `iron_path_executor`, `capability_token`, `invariants (psia)`, `capability_authority`

---

## 2. Topological Sort — Safe Boot Order

### Tier 0: No dependencies on other substrates (safe to initialize first)

| Boot Step | Substrate | Module Path | Why First |
|-----------|-----------|-------------|-----------|
| 0.1 | GenesisContinuityGuard | `src/app/governance/genesis_continuity.py` | stdlib only; file I/O to data/genesis_pins/; no imports at runtime. **Must precede SovereignAuditLog.** |
| 0.2 | PolicyRegistry | `src/app/core/policy_registry.py` | stdlib only; in-memory; no external deps |
| 0.3 | PSIA Invariants | `src/psia/invariants.py` | psia.schemas only; pure declaration; no side effects |
| 0.4 | CapabilityAuthority | `src/psia/canonical/capability_authority.py` | psia.crypto + psia.schemas only; no cross-deps into app.core |
| 0.5 | EvidenceBundle | `src/app/core/evidence_bundle.py` | stdlib only at module level; policy_registry is lazy |
| 0.6 | IronPathExecutor | `src/app/core/governance/iron_path_executor.py` | stdlib only; writes data/runtime/iron_path_decisions.jsonl |

### Tier 1: Depend on Tier 0 only

| Boot Step | Substrate | Module Path | Dependencies |
|-----------|-----------|-------------|-------------|
| 1.1 | ConstitutionalLedger | `src/app/core/constitutional_ledger.py` | stdlib + urllib |
| 1.2 | AcceptanceLedger | `src/app/governance/acceptance_ledger.py` | stdlib + sqlite3 + cryptography |
| 1.3 | Governance/Triumvirate | `src/app/core/governance.py` | stdlib only; no external governance calls |
| 1.4 | StateRegister | `src/app/core/state_register.py` | `.tscg_codec` (UTF stack); no governance imports |
| 1.5 | CapabilityToken (app) | `src/app/core/capability_token.py` | stdlib only; HMAC-SHA256 |

### Tier 2: Depend on Tier 0 + 1

| Boot Step | Substrate | Module Path | Dependencies |
|-----------|-----------|-------------|-------------|
| 2.1 | SovereignAuditLog | `src/app/governance/sovereign_audit_log.py` | `genesis_continuity` (Tier 0) + optional TSA/Merkle |
| 2.2 | GovernanceKernel | `src/app/core/governance_kernel.py` | `constitutional_ledger` (1.1), `governance` (1.3), `governance_graph`, `event_spine`, `fates` |
| 2.3 | RuntimeEnforcer | `src/app/governance/runtime_enforcer.py` | `acceptance_ledger` (1.2), `jurisdiction_loader` |
| 2.4 | PolicyDecision | `src/app/core/policy_decision.py` | lazy `policy_registry` (0.2) |

### Tier 3: Depend on Tier 0–2

| Boot Step | Substrate | Module Path | Dependencies |
|-----------|-----------|-------------|-------------|
| 3.1 | AuditManager | `src/app/governance/audit_manager.py` | `sovereign_audit_log` (2.1) |
| 3.2 | ExecutionGate | `src/app/core/execution_gate.py` | `governance_kernel` (2.2) + `mutation_binding` |

### Tier 4: Depend on Tier 0–3

| Boot Step | Substrate | Module Path | Dependencies |
|-----------|-----------|-------------|-------------|
| 4.1 | ExecutionRouter | `src/app/core/execution_router.py` | `execution_gate` (3.2), `state_register` (1.4), `invariant_engine`, `waterfall_filter`, `liara_bridge`, `nirl.forge` |

### Tier 5: Application entry points

| Boot Step | Substrate | Notes |
|-----------|-----------|-------|
| 5.1 | Domain modules (10) | All call `execution_router.execute()` |
| 5.2 | `runtime/router.py` + `pipeline.py` | Parallel path; calls `iron_path_executor` directly |
| 5.3 | `cognition_kernel.py` | Core kernel; calls execution_router and governance_service |

---

## 3. Boot Order Table

| Boot Step | Substrate | Dependency | Verification Command | Expected Receipt | Failure Mode | Safe Next Action |
|-----------|-----------|------------|---------------------|-----------------|--------------|-----------------|
| 0.1 | GenesisContinuityGuard | None | `py -3.12 -c "from app.governance.genesis_continuity import GenesisContinuityGuard; g = GenesisContinuityGuard(); g.check_or_pin('test-id', b'pk'); print('OK')"` | `data/genesis_pins/` directory created or verified | `GenesisDiscontinuityError` → system MUST freeze | Do not proceed; investigate key file |
| 0.2 | PolicyRegistry | None | `py -3.12 -c "from app.core.policy_registry import get_policy_registry; r = get_policy_registry(); print(r.active_version)"` | Version string printed (e.g., `1.0.0`) | `PermissionError` on governance weakening detection | Inspect default policy; check `POLICY_REGISTRY_SECRET` env var |
| 0.3 | PSIA Invariants | None | `py -3.12 -m pytest tests/test_psia_invariants.py -v` | All INV-ROOT-* tests pass | Import error on `psia.schemas` | Verify PYTHONPATH includes `src/` |
| 0.4 | CapabilityAuthority | psia.crypto, psia.schemas | `py -3.12 -m pytest tests/test_psia_canonical.py::test_capability_authority -v` | Issue/revoke/rotate tests pass with Ed25519 | `Ed25519Provider` key generation failure | Check `psia/crypto/ed25519_provider.py` |
| 0.5 | EvidenceBundle | None (policy_registry lazy) | `py -3.12 -m pytest tests/test_evidence_bundle.py -v` | 11 tests pass | Structural validation failure | Inspect `VALID_OUTCOMES` closed set |
| 0.6 | IronPathExecutor | None (stdlib) | `py -3.12 -m pytest tests/test_iron_path_executor.py -v` | All tests pass; `data/runtime/iron_path_decisions.jsonl` writable | `PermissionError` on JSONL path | Check `data/runtime/` directory permissions |
| 1.1 | ConstitutionalLedger | stdlib + urllib | `py -3.12 -c "from app.core.constitutional_ledger import get_ledger; l = get_ledger(); print(l)"` | Ledger instance printed; `data/ledger/` dir created | File I/O failure | Check `data/ledger/` writable |
| 1.2 | AcceptanceLedger | sqlite3 + cryptography | `py -3.12 -c "from app.governance.acceptance_ledger import get_acceptance_ledger; a = get_acceptance_ledger(); print('OK')"` | Instance created; SQLite DB initialized | `sqlite3.OperationalError` | Check `data/legal/` directory |
| 1.3 | Governance/Triumvirate | stdlib only | `py -3.12 -m pytest tests/ -k "four_laws or triumvirate" -v` | Scenario tests pass | Four Laws text mismatch (hardcoded) | Do not modify Four Laws text |
| 1.4 | StateRegister | tscg_codec | `py -3.12 -m pytest tests/test_state_register_continuity_hash.py -v` | Continuity hash tests pass | `~/.project_ai/state_register/` unwritable | Check home dir permissions |
| 1.5 | CapabilityToken (app) | stdlib only | `py -3.12 -m pytest tests/test_capability_tokens.py tests/test_replay_protection.py -v` | Token issue/verify/replay tests pass | `CAPABILITY_TOKEN_SECRET` dev default active — tests pass but production security is unverified | Verify `CAPABILITY_TOKEN_SECRET` env var is set to production value |
| 2.1 | SovereignAuditLog | genesis_continuity (0.1) | `py -3.12 -m pytest tests/test_sovereign_audit_log.py tests/test_12_vector_constitutional_break.py -v` | All vector break tests pass | `GenesisDiscontinuityError` on genesis mismatch | Verify genesis key files consistent |
| 2.2 | GovernanceKernel | constitutional_ledger (1.1), governance (1.3) | `py -3.12 -m pytest tests/test_governance_contract.py -v` | 23 contract tests pass | `governance_graph` missing domain → kernel may auto-approve | Verify governance_graph domain coverage |
| 2.3 | RuntimeEnforcer | acceptance_ledger (1.2) | `py -3.12 -m pytest tests/test_governance_pipeline_regressions.py -v` | Pipeline regression tests pass | Missing `data/legal/` directory → RuntimeEnforcer init fails → **silently bypassed** in execution_router | Verify `data/legal/` exists BEFORE execution_router boots |
| 2.4 | PolicyDecision | policy_registry (0.2) lazy | `py -3.12 -m pytest tests/ -k "policy_decision" -v` | Deny-default on registry unavailable | policy_registry unavailable → PolicyDecision still denies (fail-closed) | No action; fail-closed |
| 3.1 | AuditManager | sovereign_audit_log (2.1) | `py -3.12 -c "from app.governance.audit_manager import AuditManager; a = AuditManager(sovereign_mode=True); a.log_governance_event('boot', {}); print(a.get_statistics())"` | Event logged; statistics show 1 event | `sovereign_mode=True` requires writable data dir | Verify data dir; check genesis key exists |
| 3.2 | ExecutionGate | governance_kernel (2.2) | `py -3.12 -m pytest tests/test_execution_gate_enforcement.py -v` | Enforcement tests pass | Kernel unavailable → gate cannot initialize | Verify governance_kernel singleton ready |
| 4.1 | ExecutionRouter | execution_gate (3.2), state_register (1.4) | `py -3.12 -m pytest tests/test_iron_path.py -v` | Iron path tests pass | RuntimeEnforcer failure silently passed (see B-1) | **CRITICAL**: Verify RuntimeEnforcer initialized successfully BEFORE this step |
| 5.x | Domain modules | execution_router (4.1) | Integration tests per domain | Domain-specific receipts | Any exception in execution path | Diagnose per execution_gate exit code |

---

## 4. Lazy Import Map (Not in Boot Order, But Must Exist Before First Execution)

ExecutionGate loads these modules lazily on first call, not at import time:

| Stage | Lazy Import | Module | Must Exist Before First Call |
|-------|------------|--------|------------------------------|
| Stage 1 | `safe_allow_calibration` | `src/app/core/safe_allow_calibration.py` | Yes |
| Stage 2 | `policy_decision` | `src/app/core/policy_decision.py` | Yes (Tier 2.4) |
| Stage 3 | `execution_authorization` | `src/app/core/execution_authorization.py` | Yes |
| Stage 5 | `sovereign_runtime` | `src/governance/sovereign_runtime.py` | Yes (uses sys.path injection 4 levels up) |
| Stage 6 | `capability_token` | `src/app/core/capability_token.py` | Yes (Tier 1.5) |
| Stage 7 | `semantic_collision` | `src/app/core/semantic_collision.py` | Yes |
| Stage 8 | `invariant_severity` | `src/app/core/invariant_severity.py` | Yes |
| Stage 9 | `evidence_bundle` | `src/app/core/evidence_bundle.py` | Yes (Tier 0.5) |
| Denial | `chimera_bridge` | `src/app/security/chimera_bridge.py` | Yes (denial path) |
| Degraded | `degraded_mode` | `src/app/core/degraded_mode.py` | Yes (degraded path) |

> **Sovereign Runtime (Stage 5)** uses `sys.path` injection (`sys.path.insert(0, os.path.join(...)`) to locate `governance.sovereign_runtime`. This path injection pattern is fragile — if the directory structure changes, Stage 5 will fail with an `ImportError`. This must be documented and tracked.

---

## 5. Boot Constraints

Ordering constraints that must not be violated:

| Constraint | Reason |
|-----------|--------|
| `genesis_continuity` BEFORE `sovereign_audit_log` | Hard import dependency; SAL will fail with `ImportError` or unhandled exception if genesis_continuity is unavailable |
| `constitutional_ledger` BEFORE `governance_kernel` | Hard import dependency; kernel calls `get_ledger()` at initialization |
| `governance.py (Triumvirate)` BEFORE `governance_kernel` | Hard import dependency; kernel imports `GovernanceContext, Triumvirate` at module top |
| `acceptance_ledger` BEFORE `runtime_enforcer` | Hard import dependency; RuntimeEnforcer imports `get_acceptance_ledger` at top |
| `governance_kernel` BEFORE `execution_gate` | Hard import dependency; execution_gate imports `get_kernel` and calls it at Stage 0 |
| `execution_gate` BEFORE `execution_router` | Hard import dependency; execution_router imports `get_execution_gate` at top |
| `policy_registry` initialized BEFORE first execution_gate call | Policy registry must have an active version before `policy_decision.evaluate()` is called (Stage 2); fail-closed if missing, but denies every action |
| `data/legal/` directory EXISTS BEFORE `acceptance_ledger` init | AcceptanceLedger uses SQLite; if `data/legal/` is absent, init fails → RuntimeEnforcer fails → silently bypassed in execution_router |

---

## 6. Anti-Patterns (Things That Must Not Happen)

| Anti-Pattern | Risk |
|-------------|------|
| Calling `execution_gate.execute()` before `governance_kernel` is ready | `get_kernel()` call in Stage 0 will fail or use uninitialized state |
| Calling `execution_router.execute()` before verifying `data/legal/` exists | RuntimeEnforcer will fail silently (lines 50–51); PAGL and tier checks are erased |
| Assuming `genesis_continuity` pins survive interpreter restart | Module-level `_GENESIS_PINS` is process-wide; pins reset on every interpreter restart. Re-pinning required at each boot. |
| Calling `AuditManager(sovereign_mode=True)` before genesis keys exist | `SovereignAuditLog.__init__` calls `GenesisKeyPair.__init__` which generates keys if absent — this is a side effect that should happen at a deterministic boot step, not on first use |
| Starting execution flow before `RuntimeEnforcer` is verified ready | The current silent exception suppression means any init failure = unchecked execution. This must be treated as a pre-boot gate, not a runtime dependency. |
| Relying on `_auto_approve()` for any production action | This path bypasses Triumvirate entirely; decisions are not persisted; no EvidenceBundle produced |

---

## 7. Pre-Boot Checklist

Before starting the execution router, verify these conditions are met:

```
Environment Variables:
[ ] POLICY_REGISTRY_SECRET is set and not "dev-policy-secret"
[ ] CAPABILITY_TOKEN_SECRET is set and not "dev-secret-change-in-production"
[ ] PROJECT_AI_GENESIS_CONTINUITY_LOG is set (or default data/genesis_pins/ is writable)

File System:
[ ] data/genesis_pins/ exists and is writable
[ ] data/ledger/ exists and is writable
[ ] data/runtime/ exists and is writable (for iron_path_decisions.jsonl)
[ ] data/legal/ exists and is writable (for acceptance_ledger SQLite)
[ ] ~/.project_ai/state_register/ exists and is writable (for state_register JSON)

Key Material:
[ ] genesis_audit.key and genesis_audit.pub exist (SovereignAuditLog genesis keys)
[ ] genesis_id.txt exists (or will be generated at first boot)
[ ] Ed25519 keypair for CapabilityAuthority available (generated on first use if absent)

Policy:
[ ] policy_registry has active_version set (bootstrapped at first init)
[ ] acceptance_ledger has at least one INITIAL_MSA entry for system user

Invariants:
[ ] psia/invariants.py INV-ROOT-1 through INV-ROOT-9 loadable without import error
[ ] canonical/invariants.py 5 behavioral invariants loadable without import error
```

---

*Next report: [iron_path_2_repair_plan.md](iron_path_2_repair_plan.md)*
