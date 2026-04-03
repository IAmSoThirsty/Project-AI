<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `orchestrator/` — Service Orchestration

> **Bridges security tooling with the Cerberus perimeter.** The orchestrator connects external security services to Project-AI's internal threat defense infrastructure.

## Modules

| Module | Purpose |
|---|---|
| **`cerberus_security_interface.py`** | Direct interface to Cerberus threat detection — routes alerts, triggers containment, manages perimeter state |
| **`security_tools_service.py`** | Service wrapper for external security tools — SAST, DAST, dependency scanning, and supply chain verification |

## Role in the Architecture

```
External Security Tools
        │
        ↓
  security_tools_service.py
        │
        ↓
  cerberus_security_interface.py
        │
        ↓
  [Cerberus Perimeter] → [Triumvirate] → [Policy Engine]
```

The orchestrator is deliberately minimal — it does not make decisions. It translates external signals into Cerberus-compatible events and lets the Triumvirate govern the response.
