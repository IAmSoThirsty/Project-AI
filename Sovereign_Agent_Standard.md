# Sovereign Agent Standard

## Purpose

This document defines the minimum operational standard for authored agent and
tooling assets in this repository.

## Canonical rules

1. All meaningful mutation flows through `CognitionKernel`.
2. Tooling surfaces such as `.agent/`, `.agents/`, `.antigravity/`,
   `.codacy/`, `.devcontainer/`, `Claude/`, and `Codex/` are source assets,
   not caches.
3. `workspace/`, `output/`, `tmp/`, `.venv-linux/`, and `.env.wsl` are
   local-only and must stay out of git.
4. Private keys and generated runtime artifacts do not belong in the repo.
5. Recovery should use allowlisted paths, not blanket staging.

## Verification baseline

- `python Verify-SovereignLoaders.py`
- `python scripts/verify/verify_thirsty_interpreter.py`
- Repo-local smoke tests for the affected runtime surface

## Operational posture

- Preserve existing user changes.
- Avoid duplicate mirrors of the source tree.
- Keep authored documentation concise and directly actionable.
