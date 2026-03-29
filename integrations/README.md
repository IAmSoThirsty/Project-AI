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

# `integrations/` — External System Integrations

> **Bridges between Project-AI and external platforms, APIs, and systems.**

## Integrations

| Module | Files | Purpose |
|---|---:|---|
| **`openclaw/`** | 13 | OpenClaw API — Legion Ambassador interface, REST endpoints, message routing |
| **`thirsty_lang_complete/`** | 3 | Complete Thirsty-Lang integration — parser hooks, runtime bridging |
| **`thirstys_trading_hub/`** | 7 | Thirsty's Trading Hub — financial data, portfolio management, trade execution |

## OpenClaw API

The primary integration point for the Legion Ambassador:

```python
# Start OpenClaw API
from integrations.openclaw import start_api
start_api(host="0.0.0.0", port=8001)
```

### Endpoints

- `POST /openclaw/message` — Send a message to Legion
- `GET /openclaw/health` — Health check
- `GET /openclaw/status` — System status

## Usage

```python
from integrations import openclaw, thirsty_lang_complete, thirstys_trading_hub
```
