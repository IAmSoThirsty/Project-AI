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
