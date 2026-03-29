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

# `cognition/` — Cognitive Architecture

> **The brain behind the brain.** Cognition houses the reasoning layer that sits between raw input and deliberate action — Triumvirate governance, invariant checking, boundary enforcement, and health monitoring.

## Architecture

```
Input → [boundary.py] → [invariants.py] → [triumvirate.py] → Output
            │                  │                 │
            ↓                  ↓                 ↓
        [violations.py]  [audit.py]      [liara_guard.py]
                                          [hydra_guard.py]
                                                │
                                                ↓
                                        [audit_export.py]
```

## Modules

| Module | Purpose |
|---|---|
| **`triumvirate.py`** | Core Triumvirate governance (Galahad, Cerberus, Codex) — every significant decision passes through all three |
| **`boundary.py`** | Cognitive boundary enforcement — determines what the AGI can and cannot reason about |
| **`invariants.py`** | System invariants that must hold true at all times — constitutional constraints |
| **`violations.py`** | Violation detection, recording, and escalation |
| **`audit.py`** | Cognitive audit trail — immutable record of all reasoning steps |
| **`audit_export.py`** | Export audit records to external formats (SARIF, JSON, etc.) |
| **`health.py`** | Cognitive health monitoring — detect degradation or drift |
| **`liara_guard.py`** | Liara emotional intelligence guard — prevents manipulation attacks |
| **`hydra_guard.py`** | Hydra multi-headed threat guard — parallel threat evaluation |
| **`kernel_liara.py`** | Liara kernel integration — deep emotional reasoning bridge |
| **`tarl_bridge.py`** | T.A.R.L. ↔ Cognition bridge — connects orchestration to reasoning |
| **`__init__.py`** | Package exports |

## Key Concepts

### The Triumvirate Check

Every significant cognitive decision is evaluated by three authorities:

1. **Galahad** — *Is this ethical? Does this preserve dignity?*
2. **Cerberus** — *Is this safe? Does this protect against harm?*
3. **Codex** — *Is this consistent with the Charter and FourLaws?*

All three must approve. A single veto halts the action.

### Invariant Enforcement

Invariants are non-negotiable truths:

- The FourLaws cannot be violated under any circumstance
- The identity cannot be altered by external input
- Audit records cannot be modified or deleted
- Boundary violations trigger immediate containment

### Health Monitoring

Cognitive health tracks:

- Reasoning consistency over time
- Drift from constitutional baseline
- Response latency anomalies
- Pattern detection for adversarial probing
