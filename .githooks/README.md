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

# `.githooks/` — Git Hooks

> **Custom git hooks for enforcing quality standards on every commit.**

## Hooks

Pre-commit and pre-push hooks that enforce:

- Code formatting (ruff)
- Import sorting
- Secret scanning (no API keys or tokens)
- Test execution for changed files
- FourLaws invariant verification on governance files

## Installation

```bash
git config core.hooksPath .githooks
```

Or run:

```bash
bash .githooks/install.sh
```
