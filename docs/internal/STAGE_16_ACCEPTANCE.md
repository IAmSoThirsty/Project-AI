# Stage 16 CI Acceptance

**Status:** accepted

## Deliverable

`.github/workflows/ci.yaml` — four-job workflow covering Python, Rust, Node, and
Compose validation. Equivalent checks pass locally from this commit.

## Four Jobs

| Job | Steps |
|---|---|
| `python` | ruff check · ruff format --check · mypy · pytest |
| `rust` | cargo fmt --check · cargo clippy -D warnings · cargo test |
| `node` | pnpm install --frozen-lockfile · web:lint · web:test · web:build |
| `compose` | docker compose config --quiet |

## Local Equivalent Evidence

### Python

```
$ uv run ruff check .
All checks passed!

$ uv run ruff format --check .
81 files already formatted

$ uv run mypy --ignore-missing-imports packages/*/src apps/desktop/src apps/services/src
Success: no issues found in 50 source files

$ uv run pytest -q --tb=short
117 passed in 1.06s
```

Note: 7 files in `tools/` were reformatted by `ruff format` at the start of this stage
(freeze_history.py, ingest_papers.py, merge_legacy_duplicates.py, verify_frozen_history.py,
and three others) — all one-shot tools that had not previously been touched by the
formatter. Format gate is now clean.

### Rust

```
$ cargo fmt --check
(no output — clean)

$ cargo clippy --locked -- -D warnings
Finished `dev` profile in 0.06s

$ cargo test --locked
test result: ok. 3 passed; 0 failed
```

`RUSTUP_TOOLCHAIN=stable` set as workflow env — same rationale as Stage 15
genesis.Dockerfile fix: `rust-toolchain.toml` pins `stable-x86_64-pc-windows-gnu`
which is rejected on Linux CI runners.

### Node

```
$ pnpm web:lint
(no output — clean)

$ pnpm web:test
Test Files  1 passed (1)
Tests       2 passed (2)

$ pnpm web:build
✓ built in 188ms
```

### Compose

```
$ docker compose config --quiet
(no output — clean)
```

## Workflow Validation

```
$ python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yaml')); print('YAML valid')"
YAML valid
```
