# Stage 2 - Root Workspace Acceptance

**Status:** COMPLETE
**Verified:** 2026-06-20

## Deliverables

- `pyproject.toml` defines an empty Hatch/uv meta-package.
- `uv.lock` locks the development environment and is intentionally tracked.
- Package metadata is `project-ai==0.0.0.dev0`, Python `==3.12.10`, MIT.
- `gitleaks` remains a pre-commit/CI binary and is not declared as a pip dependency.
- `pypdf` supports deterministic paper-evidence extraction.

## Acceptance

- [x] `uv sync --extra dev --python 3.12.10` exits 0.
- [x] `uv lock --check` exits 0.
- [x] `uv sync --extra dev --check` reports no changes.
- [x] Installed metadata reports `project-ai==0.0.0.dev0`.
- [x] `uv build` creates a source distribution and an empty-platform wheel.
- [x] Stage -1 tooling tests pass (3/3).
- [x] Ruff passes for Stage -1 tooling.
- [x] strict MyPy passes for the Stage -1 generator.

Build output under `dist/` is ignored and is not committed.
