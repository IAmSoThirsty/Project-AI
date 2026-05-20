# Implementation Backlog

Date: 2026-05-19
Baseline tag: post-recovery-clean-baseline-20260519
Pytest collection: 8,633 tests / 0 errors

All items below correspond to test files isolated in `tests/conftest.py`.
Removing a file from `collect_ignore` is the acceptance gate for each item.

---

## Priority 1 — App Sub-Modules (~30 tests, 4 test files in subdirs)

These are internal modules the tests were written to cover but were never
implemented. Each entry lists the module path to create and the tests that
become collectable once it exists.

### Governance

| Module to implement | Tests unblocked |
|---------------------|-----------------|
| ~~`src/app/governance/sovereign_audit_log.py`~~ | ~~test_sovereign_audit_log~~ DONE (2026-05-20) — remaining: test_12_vector_constitutional_break, test_attack_simulation_suite, test_external_merkle_anchor, test_tsa_integration, manual/test_12_vector_break_suite, manual/test_sovereign_manual |
| ~~`src/app/governance/audit_manager.py`~~ | ~~manual/test_audit_integration~~ DONE (2026-05-20) |
| ~~`src/app/governance/company_pricing.py`~~ | ~~test_company_pricing~~ DONE (2026-05-20) |
| ~~`src/app/governance/government_pricing.py`~~ | ~~test_government_pricing, test_government_pricing_manual~~ DONE (2026-05-20) |

### Security

| Module to implement | Tests unblocked |
|---------------------|-----------------|
| `src/app/security/immutable_audit_log.py` | test_immutable_audit_log |
| `src/app/security/tseca_ghost_protocol.py` | test_tseca_ghost_protocol |
| `src/security/asymmetric_security.py` | test_asymmetric_security_coverage, test_security_comprehensive |

### Vault

| Module to implement | Tests unblocked |
|---------------------|-----------------|
| `src/app/vault/core/vault.py` | test_vault_comprehensive |

### Pipeline

| Module to implement | Tests unblocked |
|---------------------|-----------------|
| `src/app/pipeline/signal_flows.py` | test_signal_flows_100_percent, test_signal_flows_complete_coverage |

### Infrastructure

| Module to implement | Tests unblocked |
|---------------------|-----------------|
| `src/app/core/exceptions.py` | test_cathedral_infrastructure |
| `src/app/personal_agent.py` | test_personal_agent |

### Miniature Office

| Module to implement | Tests unblocked |
|---------------------|-----------------|
| `src/app/miniature_office/agent_lounge.py` | test_agent_lounge |
| `src/app/miniature_office/meta_security_dept.py` | test_meta_security_dept |
| `src/app/miniature_office/repair_crew.py` | test_repair_crew |

### Cerberus SASE

| Module to implement | Tests unblocked |
|---------------------|-----------------|
| `src/cerberus/sase/policy/containment.py` | test_containment |
| `src/cerberus/sase/core/substrate.py` | test_substrate |
| `src/cerberus/sase/core/normalization.py` | sase/core/test_normalization |

### Cognition / Monitoring

| Module to implement | Tests unblocked |
|---------------------|-----------------|
| `src/cognition/reasoning_matrix.py` | test_reasoning_matrix, test_cognition_comprehensive |
| `src/monitoring/entropy_slope.py` (or `monitoring/entropy_slope.py` on sys.path) | test_entropy_slope |

### Repo Scan Contract

| Module to implement | Tests unblocked |
|---------------------|-----------------|
| `repo_scan_contract.py` at repo root (or add its directory to pythonpath) | test_repo_scan_contract |

---

## Priority 2 — PSIA Package (18 tests)

Protocol for Sovereign Intelligence Auditing. No `psia` package exists anywhere
in the repository. These tests document the intended behavior of a complete
Byzantine fault-tolerant governance auditing system.

Do not create stubs. Write the real package or leave these isolated.

Sub-modules required (from test imports):

```
psia/
  bootstrap/genesis.py
  canonical/capability_authority.py
  concurrency.py
  crypto/ed25519_provider.py
  events.py
  gate/capability_head.py
  gate/quorum_engine.py
  invariants.py
  liveness.py
  observability/autoimmune_dampener.py
  schemas/capability.py
  server/governance_server.py
  shadow/operational_semantics.py
  threat_model.py
```

Tests that become collectable: test_psia_bootstrap, test_psia_canonical,
test_psia_comprehensive, test_psia_concurrency, test_psia_gate,
test_psia_integration, test_psia_invariants, test_psia_liveness,
test_psia_observability, test_psia_schemas, test_psia_threat_model,
test_psia_waterfall, test_bft_deployed, test_ed25519_crypto,
test_formal_properties, test_governance_server, test_rfc3161,
test_shadow_operational_semantics.

---

## Priority 3 — Shadow Thirst UTF Planned Sub-Modules (2 tests)

The `shadow_thirst` package exists at `src/utf/shadow_thirst/`. Two Tier 4
sub-modules are planned but not yet written.

| Sub-module to implement | Tests unblocked |
|-------------------------|-----------------|
| `src/utf/shadow_thirst/bytecode.py` | test_shadow_thirst |
| `src/utf/shadow_thirst/type_system.py` | test_shadow_thirst_type_system |

---

## Priority 4 — PyQt6 / Platform GUI Tests (2 tests)

These tests require Qt6 system libraries. They are not broken — they are
environment-gated.

| Condition to re-enable | Tests unblocked |
|------------------------|-----------------|
| Running on a Qt6-capable host with `pip install PyQt6` | test_leather_book_smoke, gui_e2e/test_launch_and_login |

No implementation work required. Remove from `collect_ignore` on a desktop
environment where Qt6 is installed.

---

## Priority 5 — Atlas Optional Dependency Unblock

Atlas is registered and isolated. The unblock path is installing its optional
scientific dependencies (scipy, networkx, or others identified during Atlas
test collection) and removing Atlas test files from any isolation lists once
they collect cleanly.

---

## Priority 6 — Optional SWR Activation Review

Sovereign War Room is import-safe and smoke-verified at the baseline tag.
The activation contract is defined. Activation is a deliberate future decision,
not a recovery task. Review the contract before enabling.

---

## How to re-enable a test file

1. Implement the missing module.
2. Remove the corresponding entry from `tests/conftest.py` `collect_ignore`.
3. Run `pytest --collect-only -q --tb=no` and confirm the file collects.
4. Run the tests and confirm they pass.
5. Commit.
