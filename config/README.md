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

# `config/` — Configuration Management

> **Centralized runtime configuration for every subsystem.** All YAML, JSON, and Python-based configs flow through here.

## Files

| File | Purpose |
|---|---|
| `top_config.windows.example.json` | Windows-specific top-level configuration template |
| `sovereign_runtime.yaml` | Sovereign runtime settings — identity phase, policy mode, capability limits |
| `governance_state.yaml` | Governance state definitions — Triumvirate thresholds, FourLaw enforcement levels |
| `security_hardening.yaml` | Security hardening profile — Cerberus sensitivity, threat response levels |
| `memory_optimization.yaml` | Memory optimization parameters — cache sizes, GC thresholds |
| `frame_config.yaml` | Frame configuration — display and UI rendering settings |
| `*.py` | Python-based config loaders and validators |

## Usage

Configuration files are loaded at engine boot via `PACEEngine(config={...})`. The config dict is passed down to each subsystem:

```python
from project_ai.engine import PACEEngine

# Load with custom config
engine = PACEEngine({
    "identity": {...},
    "state": {...},
    "capabilities": {...},
    "skills": {...},
})
```

## Precedence

1. **Hardcoded defaults** (in each subsystem)
2. **YAML/JSON config files** (this directory)
3. **Environment variables** (`PROJECT_AI_*` prefix)
4. **Runtime overrides** (passed via API or CLI)
