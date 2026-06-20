# Stage 4 - Deterministic Duplicate Merge Acceptance

**Status:** COMPLETE
**Verified:** 2026-06-20

## Selection Policy

- SWR canonical base: `engines/sovereign_war_room`.
- Atlas canonical base: `engines/atlas`.
- Canonical content wins same-path conflicts.
- Alternate-only content is retained under `legacy_extras/` for later review.
- Generated caches and dependency directories are excluded.

## Acceptance

- [x] Merge tool uses the Stage 3 read-only source guard.
- [x] Staging reset is restricted to `packages/_staging/<name>`.
- [x] Every selected and conflicting file has a SHA-256 report entry.
- [x] Repeated execution produces identical staged-tree hashes.
- [x] Legacy state is unchanged before and after each merge.
- [x] Unit tests cover exclusion, stable hashing, and content binding.

Detailed counts and hashes are recorded in `STAGE_4_MERGE_REPORT.json`.
