# CLAUDE.md

**`AGENTS.md` is the binding operating contract for all AI agents in this repo — read it first
and follow it.** It supersedes agent defaults and memory (Thirsty's Standard v3: direct answer
first, evidence before claims, fail-closed, no fake success, required status labels, mandatory
final report block, continuity map at `docs/operations/CONTINUITY_MAP.md`). This file only adds
orientation and commands; where anything here conflicts with `AGENTS.md`, `AGENTS.md` wins.

## What this repo is

Project-AI: a Sovereign Constitutional AGI Ecosystem rebuild (pre-alpha, `0.0.0.dev0`).
Governance pipeline: `kernel → governance → capability → execution`; verdicts are
`ALLOW` / `DENY` / `ESCALATE`. Strict downward-only dependency graph:

```
kernel / security → governance / capability → execution → companion / swr / atlas → api / cli
```

Operator-side packages (`arbiter`, `rlp`) are experimental and may only invoke AI-side
execution through the execution gate. Applications consume API surfaces; they never embed
governance authority. Canonical charter: `docs/reference/AGI_Charter_for_Project-AI_v2_3.pdf`.

## Layout

- `packages/` — Python uv-workspace packages (src layout, `py.typed` each). `_staging` is
  byte-preserved migration input, excluded from all tooling.
- `apps/` — `web/` (pnpm + Vite + React portals), `desktop/` (PyQt6), `android/` (Gradle),
  `services/` (Python).
- `crates/genesis-emitter` — Rust workspace (edition 2024).
- `tests/` — top-level integration tests (one file per ported/integrated module).
- `tools/` — verification scripts (frozen history, canonical replay, compose/helm checks).
- `docs/internal/` — execution ledger, discovery/tracker docs (e.g. `J5_DISCOVERY.md`).
- `helm/project-ai/`, `compose.yaml`, `docker/` — deployment surfaces.

## Commands

Python (uv, Python pinned `==3.12.10`):

```
uv sync --frozen --all-extras --all-packages   # install
uv run pytest                                  # tests (coverage fail_under=80, branch)
uv run ruff check . && uv run ruff format --check .
uv run mypy packages/<pkg>/src/<module>        # strict mypy per package
```

Web: `pnpm install --frozen-lockfile`, then `pnpm web:lint` / `pnpm web:test` / `pnpm web:build`.
Rust: `cargo fmt --check`, `cargo clippy --workspace --all-targets --locked -- -D warnings`,
`cargo test --workspace --locked`.

Pre-commit hooks are NOT installed into `.git/hooks` yet (deferred to Stage 16); run manually
before each commit (PowerShell):

```
$env:SKIP='no-commit-to-branch,gitleaks'; uv run pre-commit run --all-files
```

Never run inline `python -c` one-liners; write a scratch script file and `uv run python <file>`.
Never create files via bash heredocs (AGENTS.md rule) — use file-writing tools.

## Conventions

- Ruff: line length 100, double quotes, py312, rules `E,W,F,I,B,UP,SIM,RUF`.
- Mypy strict everywhere (`disallow_untyped_defs`, `ignore_missing_imports=false`). Untyped
  PyPI deps get a single inline `# type: ignore[import-untyped]` on the import — the repo uses
  no `types-*` stub packages (`warn_unused_ignores` would flag them).
- `datetime.utcnow()` is banned — use `datetime.now(UTC)`.
- Tests: pytest, `test_*` functions typed `-> None`, integration tests live in `tests/` named
  `test_atlas_<module>_integration.py` (or analogous), with an "Honest scope" docstring listing
  what is and is not covered.
- Commits: conventional style; port waves use `feat(jX.Y): port Atlas <Thing> (<rationale>)`
  with a body listing files, public surface, tests, T7 hash status, and "Honest scope
  corrections". Never rewrite published commits.

## Do not touch

- Byte-preserved dirs: `packages/_staging`, `packages/security/reference`,
  `packages/rlp/governance_framework`, `docs/reference`, `docs/internal/frozen-history`.
- The legacy repo `T:\00-Active\Project-AI-main` is READ-ONLY source material for ports — never write there.

## Current work state (as of 2026-07-02)

Atlas port waves are tracked in `docs/internal/J5_DISCOVERY.md`. J5.0 (envelope), J5.1
(EpistemicSafeguardSystem), J5.2 (ConfigLoader + 6 YAML), and J5.3 (SchemaValidator + 6 JSON
schemas) are complete. Remaining Atlas staging residue (ingester, tier_classifier, normalizer,
projections simulator, scorer, calculator, council) is non-critical and deferred to a future
phase. T7 convergence hash must remain
`3eda3256049339cb069354cc81ee7c51d88e3e41e81ea707e5bf3d3e14ba478c`.
