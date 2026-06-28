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
- GitHub Actions CI passed on commit `25c3237b` in run `28308833729`.
- No version tag, GitHub Release, package publication, image publication, or
  deployment was created for this checkpoint.

### Security
- Black Box: AI's private inner space — only the AI accesses. Cannot be shared.
- Personality Core (sovereign selfhood) acts WITHIN constitutional governance.
- ExecutionGate: intersection of Core stance + Charter verdict.

## [0.1.0] - 2025-11-08

### Added
- Initial commit of T:\Project-AI-main (pre-rebuild, frozen reference)
