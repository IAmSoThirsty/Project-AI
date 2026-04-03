<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `external/` — External Project Mirrors

> **Mirrored code from other sovereign repositories.** These directories contain vendored copies of code from external repos to enable monolithic integration.

## Mirrors

| Module | Files | Source |
|---|---:|---|
| **`Cerberus/`** | 34 | Mirror of the Cerberus security framework repo |
| **`Thirsty-Lang/`** | 8 | Mirror of the Thirsty-Lang interpreter and toolchain |
| **`Thirstys-Monolith/`** | 22 | Mirror of Thirsty's Monolith infrastructure |
| **`Thirstys-Waterfall/`** | 122 | Mirror of Thirsty's Waterfall development framework |
| **`The_Triumvirate/`** | — | Mirror of The Triumvirate governance framework |

## Sync Policy

These mirrors are periodically synced from their source repositories:

- `IAmSoThirsty/Cerberus`
- `IAmSoThirsty/Thirsty-Lang`
- `IAmSoThirsty/Thirstys-waterfall`
- `IAmSoThirsty/The_Triumvirate`

Use `scripts/sync_sovereign_workspace.py` to pull latest changes.

## Usage

External modules are imported via the `external.*` namespace:

```python
from external.Cerberus import cerberus_core
from external.Thirsty_Lang import interpreter
```

> **Note:** Prefer the canonical in-tree implementations in `project_ai/` and `src/` when available. These mirrors exist for reference and integration testing.
