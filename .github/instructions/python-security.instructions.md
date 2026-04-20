---
description: "Use when editing Python source code, security-sensitive modules, or dependency handling. Applies secure coding and validation expectations."
name: "Python Security and Quality"
applyTo: "**/*.py"
---

# Python Security and Quality

- Validate untrusted input at boundaries and fail closed on invalid data.
- Avoid dynamic code execution and shell invocation unless required and reviewed.
- Keep functions side-effect aware and explicit about file/network operations.
- Update unit tests for bug fixes and behavior changes.
- For Python edits, prefer this validation path when feasible:
  - `ruff check .`
  - `mypy src`
  - `pytest -q`
  - `bandit -r src/`
- Do not overstate security outcomes; align claim wording with project policy.
