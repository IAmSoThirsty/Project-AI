# Sovereign Vault Integration — Wave L5 Acceptance

**Date:** 2026-07-14
**Package:** `packages/sovereign-vault` (import name `sovereign_vault`)
**Source:** `T:\00-Active\sovereign_vault` (27/27 tests passing upstream)
**Integration model:** Option A — workspace package, deps from PyPI (cryptography 49.0.0 already in lock; pynacl 1.6.2 added)

## What was built

- `packages/sovereign-vault/src/sovereign_vault/` — 17 modules ported verbatim, then
  made mypy `--strict` clean (see changes below).
- `packages/sovereign-vault/tests/test_vault.py` — 27 tests, all passing.
- `packages/sovereign-vault/deploy/vault.service` — systemd hardening unit (copied).
- `packages/sovereign-vault/README.md`, `py.typed`.
- `packages/sovereign-vault/pyproject.toml` — hatchling, `project-ai-sovereign-vault`,
  deps cryptography + pynacl, requires-python `==3.12.10`.
- Root `pyproject.toml` — registered in 3 places: `[project].dependencies`,
  `[tool.uv.sources]`, `[tool.uv.workspace].members`.
- `.github/workflows/ci.yaml` — added to mypy step + pytest `--cov=sovereign_vault`.
- `.pre-commit-config.yaml` — added `sovereign-vault` to mypy files pattern.
- `pyproject.toml` per-file-ignores for the ported tests (intentional unpacking/structure).

## Acceptance checks (all green)

| Gate | Command | Result |
|---|---|---|
| Import | `uv run python -c "import sovereign_vault"` | OK (v0.1.0) |
| Tests | `uv run pytest packages/sovereign-vault/tests -q` | 27 passed |
| ruff check | `uv run ruff check packages/sovereign-vault` | All checks passed |
| ruff format | `uv run ruff format --check packages/sovereign-vault` | 18 files formatted |
| mypy strict | `uv run mypy packages/sovereign-vault/src --strict` | Success, 0 issues / 17 files |

## Source edits required for strict typing (behavior-preserving)

- Added precise type params: `dict[str, object]`, `dict[str, IndexEntry]`,
  `dict[str, ExposureEntry]`, `dict[TamperEvent, TamperResponse]`, `list[RecoveryApproval]`,
  `list[dict[str, object]]`, `tuple[RecoveryApprover, ...]`, `tuple[bytes, ...]`,
  `set[bytes]`, `set[str]`.
- Added missing return annotations: `__post_init__`, `__del__`, `__exit__` params
  (`: object`), `report_tamper -> TamperResponse`, `regenerate_component -> RegenerationRecord`,
  `release` is a `@contextlib.contextmanager` yielding `SecureBuffer` (mirrors
  `ObjectReleaseManager.release`).
- `vault.release()` now delegates via `with self._release_manager.release(...) as buf: yield buf`.
- `release.py`: `transfer_via_memfd` is platform-guarded — `import fcntl` + `fcntl.fcntl`
  only reached on Linux (`hasattr(os, "memfd_create")`); one `type: ignore[attr-defined]`
  for the platform-gated C call. `mlock`/`munlock` already no-op off Linux.
- Lint: `raise ... from e` (B904), `contextlib.suppress` (SIM105), merged nested `if` (SIM102).

## Risk notes

- `pynacl` was NOT in `uv.lock` before; `uv lock` resolved `pynacl==1.6.2` and `uv sync`
  built the package cleanly. No new mypy override needed (pynacl is only referenced
  indirectly via `cryptography`; the package imports `cryptography` directly).
- The ported `vault.py` `release()` signature changed from returning `SealedObjectRef`
  to a context manager yielding `SecureBuffer` — this matches the documented design
  (decrypt into locked memory, zeroize on exit) and the upstream `ObjectReleaseManager`.

## Next

Part 2 (governance framework residual) remains: DPR package, governance-agent package
(reconcile vs `packages/governance`), TS adapters, corpus/docs ingest, continuity map.
