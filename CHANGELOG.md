# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Stage -1.5: Frozen history (SHA-256 chain-linked snapshot of T:\Project-AI-main)
- Stage -1: Paper ingest + Downloads copy (137 files, all SHA-256 verified)
- Operator-side governance drafts: arbiter_gov (12/12 tests pass) + rlp.py
- AGI Charter v2.3 (canonical) in `docs/reference/`
- Stage 18 local acceptance evidence for the development checkpoint.
- Stage 19 and Stage 19.5 development evidence, including Atlas gap discovery,
  legacy-coverage inventory, and session-ledger corrections.
- Atlas J2.4.0a graph-builder wave: deterministic influence graph
  construction, metrics, communities, graph hashes, audit events, and tests.
- Atlas J2.4.0b driver-engine wave: 10-dimensional normalization, derived
  metrics, PCA, correlations, sensitivities, analysis hashes, audit events,
  and tests.
- Atlas J2.4.0c temporal-graph wave: source-backed temporal nodes and edges,
  deterministic snapshots, Merkle-style chain verification, adjacency matrices,
  change detection, evolution tracking, audit events, and tests.
- Governance J2.5 constitutional-kernel integration: legacy constitutional
  checks ported as canonical `InvariantEngine` invariants with execution-gate
  denial tests.
- Atlas J2.6 failure-surveillance wave: canonical anomaly detection, health
  summaries, local abort-condition reporting, local kill-switch state,
  audit-visible events, and tests.
- Atlas J2.7 Sludge sandbox wave: canonical SS-only fictional narrative
  artifacts, source snapshot hashing, no default filesystem writes,
  contamination checks, audit-visible events, and tests.
- J2.8 CLI / API surface: public Atlas status route, protected Atlas Sludge
  gateway route, gateway-only `atlas-status` and `atlas-sludge` CLI commands,
  audit relay evidence, and tests.
- Atlas J2.9 replay-system wave: canonical replay bundles, deterministic
  bundle hashes, fail-closed bundle verification, reconstruction summaries,
  explicit save/load operations, audit-visible replay events, and tests.
- Pre-deployment output: executable `tools/verify_pre_deployment.py`, non-secret
  `.env.example`, development stack runbook, and deployment-readiness checklist
  tied to the real Compose, Helm, CI, environment, replay, and continuity
  surfaces.

### Changed
- Root project documentation now describes the current `0.0.0.dev0`
  development checkpoint instead of the early two-stage bootstrap state.
- CI action pins were updated to current full-SHA-pinned Node 24 action
  runtimes while preserving the full-SHA policy.
- Kubernetes CI validation now uses offline Helm-render verification instead of
  a client dry-run path that could depend on active cluster discovery.

### Fixed
- GitHub Actions development CI was repaired after pre-commit, Linux desktop,
  Linux temp-path, Kubernetes dry-run, mypy, and lint failures.
- GitHub Actions Node.js 20 deprecation annotations were cleared.

### Verified
- GitHub Actions CI passed on J2.9 implementation commit
  `176990f08b6c403befccee43b350d6874e733507` in run `28362042896`.
- GitHub Actions CI passed on the latest J2.9 docs/evidence commit
  `22ad10aa49f24e5045ffd4493a6e92f9cb615b7a` in run `28362260186`.
- Local pre-deployment gates passed across Python, web, Rust, Helm, Compose
  health/security, and Android debug build surfaces.
- GitHub Actions CI passed on pre-deployment output commit
  `6fdb658f76008b393e7a6c2b42814bb9f995e5e7` in run `28367849567`.
- No version tag, GitHub Release, package publication, image publication, or
  deployment was created for this checkpoint.

### Security
- Black Box: AI's private inner space — only the AI accesses. Cannot be shared.
- Personality Core (sovereign selfhood) acts WITHIN constitutional governance.
- ExecutionGate: intersection of Core stance + Charter verdict.

## [0.1.0] - 2025-11-08

### Added
- Initial commit of T:\Project-AI-main (pre-rebuild, frozen reference)
