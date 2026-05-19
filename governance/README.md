<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `governance/` — Constitutional Governance

> **The law of the land.** Governance defines the AGI Charter, FourLaws implementation, sovereign runtime constraints, and existential proofs that guarantee constitutional behavior.

## Modules

| Module | Purpose |
|---|---|
| **`core.py`** | Core governance framework — Charter definitions, authority hierarchy |
| **`iron_path.py`** | Iron Path execution — the mandatory pre-flight verification sequence |
| **`sovereign_runtime.py`** | Sovereign runtime constraints — what the AGI can and cannot do |
| **`sovereign_verifier.py`** | Sovereign verification engine — proofs that constitutional invariants hold |
| **`existential_proof.py`** | Existential proofs — formal guarantees that the system cannot violate its charter |
| **`singularity_override.py`** | Singularity override protocol — emergency shutdown and constitutional reset |
| **`manager.py`** | Governance manager — orchestrates governance checks across subsystems |
| **`system.py`** | Governance system integration — connects governance to the PACE engine |
| **`__init__.py`** | Package exports |

## Key Documents

| File | Purpose |
|---|---|
| `AI_PERSONA_FOUR_LAWS.md` | The FourLaws specification document |
| `governance_state.yaml` | Governance state definitions |
| `sovereign_runtime.yaml` | Runtime constraint configuration |
| `sovereign_runtime.thirsty` | Governance expressed in Thirsty-Lang |

## The Iron Path

The Iron Path is the mandatory pre-flight sequence that runs before any sovereign operation:

1. **Constitutional Verification** — FourLaws hold
2. **Identity Integrity** — Identity has not been tampered with
3. **Audit Chain Validation** — Audit log is intact and continuous
4. **Boundary Verification** — All boundaries are enforced
5. **Triumvirate Readiness** — All three governors are online

If any step fails, the system halts. There is no bypass.

## Existential Proofs

`existential_proof.py` contains formal proofs that:

- The FourLaws cannot be circumvented by any input sequence
- The identity cannot be altered through any conversation path
- The audit trail cannot be retroactively modified
- Override authority requires human authorization
