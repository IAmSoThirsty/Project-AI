# Contributing

This is a single-owner project (`@IAmSoThirsty`). External contributions are
not currently accepted via PR. The source is public for reference and audit.

If you find a security issue, see `SECURITY.md`.

## For the owner

Every change goes through the rebuild execution ledger at
`docs/internal/REBUILD_EXECUTION_PLAN.md` (the active execution authority).

Each stage:
1. Produces its deliverable.
2. Runs its acceptance check.
3. Commits with a `[Stage N]` prefix.
4. Pushes to a feature branch.
5. After review, merges to `main`.

No stage skips acceptance.
