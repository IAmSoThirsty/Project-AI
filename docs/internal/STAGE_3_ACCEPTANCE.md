# Stage 3 - Legacy Soft-Freeze Acceptance

**Status:** COMPLETE
**Verified:** 2026-06-20

## Policy

`T:\Project-AI-main` is a read-only input to rebuild tooling. The boundary is
enforced in code and evidence; filesystem ACLs, Git configuration, repository
attributes, commits, and user files remain unchanged.

## Deliverables

- `tools/legacy_source_guard.py` rejects path escapes, legacy destinations,
  and non-read-only Git subcommands.
- `tools/capture_legacy_state.py` captures source state before and after and
  fails if the two snapshots differ.
- `docs/internal/LEGACY_SOURCE_STATE.json` records HEAD, origin, divergence,
  dirty-file hashes, and the frozen-history binding.

## Acceptance

- [x] Frozen history contains the captured legacy HEAD.
- [x] Frozen history has 2,264 commit sections.
- [x] Legacy state is identical before and after capture.
- [x] Guard tests reject source escape, missing source, legacy destination,
  and mutating Git commands.
- [x] No hard-freeze operation was performed.
