# Stage 11 Acceptance: Atlas And Genesis

**Status:** ACCEPTED FOR DEVELOPMENT

## Atlas

- [x] Evidence-weighted analysis is deterministic and side-effect free.
- [x] Every projection includes a non-authority/subordination notice.
- [x] Agency claims without high-tier evidence receive a conservative penalty.
- [x] Simulation-stack projections have zero real-world legitimacy weight.
- [x] Projection persistence requires governance `ALLOW` and exact Atlas scope.
- [x] Ruff and strict MyPy pass.
- [x] Tests: `4 passed`; branch coverage: `100.00%`.
- [x] Wheel and source distribution build at `0.0.0.dev0`.

## Genesis

- [x] Stable Rust GNU toolchain: `rustc 1.96.0`, `cargo 1.96.0`.
- [x] Repository toolchain includes `rustfmt` and `clippy`.
- [x] Canonical BTreeMap JSON records bind sequence, event, payload, and prior hash.
- [x] Verification detects payload tampering and malformed input fails closed.
- [x] `cargo fmt --check` passes.
- [x] `cargo clippy --workspace --all-targets -- -D warnings` passes.
- [x] `cargo test --workspace`: `2 passed`.
- [x] CLI smoke emits sequence 1 with a 64-character record hash.

Cargo uses SemVer `0.0.0-dev0`; crate metadata records the canonical repository
development version `0.0.0.dev0`. An incremental-cache finalization attempt on
`T:` reported access denied, but Clippy, compilation, tests, and CLI execution
all completed. Generated `target/` content is ignored.

Atlas staging provenance is recorded in `STAGE_11_SOURCE_MAP.md`.
