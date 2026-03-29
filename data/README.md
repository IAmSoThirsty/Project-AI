<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `data/` — Runtime Data & Persistent State

> **All runtime data, training datasets, audit logs, security data, and persistent state live here.**

## Directories

### Identity & Persona

| Directory | Purpose |
|---|---|
| `ai_persona/` | AI persona definitions |
| `ai_persona_appointed/` | Appointed persona configurations |

### Security & Threat Intelligence

| Directory | Purpose |
|---|---|
| `cerberus/` | Cerberus threat data and detection models |
| `security/` | Security event data |
| `anti_sovereign_tests/` | Anti-sovereignty test data |
| `comprehensive_security_tests/` | Comprehensive security test fixtures |
| `red_hat_expert_simulations/` | Red hat expert simulation data |
| `red_team_stress_tests/` | Red team stress test data |
| `osint/` | OSINT (Open Source Intelligence) data |
| `vectors/` | Attack vector definitions |

### Learning & Training

| Directory | Purpose |
|---|---|
| `training_datasets/` | Model training datasets |
| `datasets/` | General datasets |
| `autolearn/` | Auto-learning captured data |
| `continuous_learning/` | Continuous learning state |
| `learning/` | Learning module data |
| `learning_requests/` | Learning request queue |

### State & Memory

| Directory | Purpose |
|---|---|
| `memory/` | AGI memory store |
| `savepoints/` | State savepoints for rollback |
| `migrations/` | State migration scripts |

### Audit & Monitoring

| Directory | Purpose |
|---|---|
| `audit/` | Immutable audit log entries |
| `logs/` | Runtime logs |
| `monitoring/` | Monitoring data and metrics |

### Cryptographic

| Directory | Purpose |
|---|---|
| `genesis_keys/` | Genesis event cryptographic keys |
| `genesis_pins/` | Genesis pin validation data |
| `black_vault_secure/` | Encrypted vault storage |

### Scenarios & Demos

| Directory | Purpose |
|---|---|
| `tarl_protection/` | T.A.R.L. protection data |
| `tarl_vm/` | T.A.R.L. VM state |
| `sovereign_messages/` | Sovereign messaging data |
| `trading_hub/` | Trading hub data |
| `asl_assessments/` | ASL assessment records |
| `generated_tests/` | Auto-generated test data |
| `*_demo/` / `*_scenarios_demo/` | Demo scenario data |

## Important Notes

- **`audit/`** — Immutable. Entries cannot be modified or deleted.
- **`genesis_keys/`** — Cryptographic material. Handle with extreme care.
- **`black_vault_secure/`** — Encrypted at rest. Requires sovereign authorization to access.
