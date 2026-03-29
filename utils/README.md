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

# `utils/` — Shared Utilities

> **Common functions used across the entire codebase.** Logging, validation, and helper utilities.

## Modules

| Module | Purpose |
|---|---|
| **`logger.py`** | Centralized logging — structured log output, log levels, audit-compatible formatting |
| **`validators.py`** | Input validators — type checks, range validation, constitutional constraint verification |
| **`helpers.py`** | General helpers — string manipulation, file I/O wrappers, environment detection |
| **`__init__.py`** | Package exports |

## Usage

```python
from utils.logger import get_logger
from utils.validators import validate_input
from utils.helpers import safe_read_file

log = get_logger("my_module")
log.info("Starting operation")

# Validate before processing
validate_input(user_data, schema="sovereign_input")

# Safe file operations
content = safe_read_file("config/sovereign_runtime.yaml")
```
