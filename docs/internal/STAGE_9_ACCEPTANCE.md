# Stage 9 Acceptance: Companion

**Status:** ACCEPTED FOR DEVELOPMENT

- [x] Package depends only on execution and kernel layers below it.
- [x] Companion identity is stable and cannot be changed through state updates.
- [x] State uses revision checks and SHA-256 integrity snapshots.
- [x] State updates require a governance `ALLOW` and an exact scoped capability.
- [x] State restoration is also an execution-gated action.
- [x] Governance denial, wrong scope, and revision conflict preserve prior state.
- [x] Foreign-identity snapshots are rejected before restoration.
- [x] Ruff and strict MyPy pass.
- [x] Tests: `4 passed`; branch coverage: `100.00%`.
- [x] Kernel-through-companion integration suite: `46 passed`.
- [x] Wheel and source distribution build successfully at `0.0.0.dev0`.

Legacy provenance is recorded in `STAGE_9_SOURCE_MAP.md`. Voice, visual, and
autonomous surfaces remain explicitly outside this development package.
