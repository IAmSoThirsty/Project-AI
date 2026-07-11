# Stage 19.5C Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase C
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25
**Phase scope:** First source-code wave — `packages/companion/` identity + fates + bonded.

---

## 0. Phase C scope (recap)

Build the first source-code wave of the companion subsystem rebuild per `STAGE_19_5_PHASED_PLAN.md` Phase C:

- `companion.identity` — `IdentityManager` over `kernel.StateRegister`, with pluggable `IdentityDerivation` Protocol
- `companion.fates` — append-only `FateLedger` with `record_fate` / `query_fates` / `prune_fates`
- `companion.bonded` — `BondedCompanion` wiring Identity + Fates through real `ExecutionGate` (single audit chain)
- Re-export new symbols from `companion.__init__`
- Unit tests + 1 cross-package integration test

---

## 1. Files created

| Path | Type | LOC |
|---|---|---|
| `packages/companion/src/companion/identity.py` | source | 146 |
| `packages/companion/src/companion/fates.py` | source | 269 |
| `packages/companion/src/companion/bonded.py` | source | 217 |
| `packages/companion/tests/test_identity.py` | test | 12 tests |
| `packages/companion/tests/test_fates.py` | test | 14 tests |
| `tests/test_companion_integration_identity_fates.py` | integration test | 7 tests |

**Total new source:** 632 LOC + 33 tests across 3 new modules.

## 2. Files modified

| Path | Change |
|---|---|
| `packages/companion/src/companion/__init__.py` | re-exports new symbols (16 exports total) |

## 3. Verification gates (all green)

```
=== TESTS ===
EXIT: 0
550 passed in 1.46s

=== MYPY --strict ===
EXIT: 0
Success: no issues found in 72 source files

=== RUFF check ===
EXIT: 0
All checks passed!

=== RUFF format --check ===
EXIT: 0
72 files already formatted
```

Test breakdown:
- Pre-existing baseline: 517 tests pass (no regression)
- New companion unit tests: 30 (12 identity + 14 fates + 4 existing companion)
- New cross-package integration tests: 7
- Total: 550 (vs baseline 517 → +33)

## 4. Architectural invariants (verified)

- **Downward-only deps:** companion imports only kernel + stdlib (identity, fates) and execution (bonded). No upward imports. ✓
- **Canonical types:** All cross-module state uses `kernel.JsonScalar`, `kernel.JsonValue`, `kernel.StateRegister`, `kernel.StateSnapshot`. ✓
- **Fail-closed:** Both `IdentityManager` and `FateLedger` raise specific error types (`IdentityError`, `FateLedgerError`) on invalid input; never silent ALLOW. ✓
- **Single audit chain:** All `BondedCompanion` mutations route through `ExecutionGate.submit_action`. `ExecutionGate._capabilities.consume` ensures capability enforcement; subsequent DENY outcomes are observable via `ExecutionResult.outcome`. ✓
- **Pluggable seams:** `IdentityDerivation` Protocol allows alternate identity-derivation functions (pluggable, default provided). `IdentityManager(derivation=...)`. ✓
- **Strict typing:** mypy --strict clean on 72 source files (was 67 before Phase C; added 5 modules). ✓
- **Deterministic:** All mutations go through revision-tracked `StateRegister.update()`; identity and fate revisions bumped deterministically per operation. ✓

## 5. Bugs caught + fixed during this phase

These are real defects found during self-review (hostile-review pattern from `LEGACY_GAP_INVENTORY_VERIFICATION.md`):

1. **`record_fate` id-resolution was incomplete** — only honored the explicit `record_id` parameter, ignoring the record dict's internal `id` field. Fixed: 3-tier resolution (explicit param > record's `id` field > generated uuid4). Affected 5 unit tests.

2. **`_validate_record` ran AFTER type coercion** — wrong-type input raised raw `TypeError` from `list()` instead of `FateLedgerError`. Fail-closed invariant was leaky. Fixed: added `_validate_raw_record` for pre-coercion type validation. Includes explicit `bool` exclusion on `weight` (Python `bool` is subclass of `int`).

3. **`Mapping` not imported in `fates.py`** — caused `NameError` after adding `_validate_raw_record`. Fixed.

4. **Test arithmetic errors in `test_fates.py`** — `test_prune_with_empty_iterable_is_noop` and `test_prune_fates_removes_named_records` had wrong revision arithmetic.

5. **Integration test fixture ambiguity** — `governors=(RuleGovernor(...),)` was being parsed as bare `RuleGovernor`. Refactored to named-variable + list-literal pattern.

6. **Integration tests passed fake capability tokens** — `ExecutionGate._capabilities.consume()` rejects them silently, so state never mutated. Real bug in my test code, found only by the integration test catching it (per 2026-06-24 accepted pattern: cross-package integration tests catch architectural bugs unit tests miss). Fixed by adding `_issue_capability()` helper that issues real tokens via `CapabilityAuthority.issue()`.

7. **Integration test expected_revision arithmetic** — fates StateRegister starts at rev 0, not 1 (independent of identity StateRegister). Fixed test to use `expected_revision=i` instead of `i+1`.

8. **Integration test `pytest.raises(Exception)` for swallowed exceptions** — `submit_action` doesn't raise on executor failure, it returns DENY result. Changed test to assert `result.outcome is Outcome.DENY`.

9. **Type narrowing chain in `bonded.py`** — `int(JsonValue)` where `JsonValue` includes dict/list, which `int()` rejects. Added `_as_int()` helper that narrows safely via `isinstance` checks.

10. **mypy strict regressions caught and fixed** — 46 → 0 mypy errors after applying cast() to type coercions, widening function signatures to `Mapping[str, object]`, removing unused `# type: ignore` comments, and fixing the `fates.py:54` Ellipsis-in-tuple bug.

## 6. Compatibility

- `BondedCompanion` uses real `CapabilityAuthority` tokens via `ExecutionGate`. Tokens must be issued for the correct operation (`BOND_IDENTITY_OPERATION`, `RECORD_FATE_OPERATION`, `PRUNE_FATES_OPERATION`) and resource (`companion:<companion_id>`). This matches the existing `Companion` class pattern in `companion.service`.
- New `__all__` exports are backward-compatible: all 3 pre-existing exports (`Companion`, `UPDATE_OPERATION`, `RESTORE_OPERATION`) are unchanged.

## 7. Continuity map

`docs/operations/CONTINUITY_MAP.md` updated per template with Phase C session delta (next session's pickup; pre-commit checkpoint at `6ae16f2`).

## 8. Next steps

1. **Commit Phase C** (this PR)
2. **Phase D authorization:*** `companion.nirl.py` (NIRL state machines) — 1 source + 1 test + 1 init modify
3. **Phase E authorization:*** `companion.voice_bonding.py` + `companion.cognition.py` (Q7 closure)
4. **Push decision:** Phase A and Phase B are committed locally; Phase C makes local 7 ahead of origin/main. Push still requires explicit user authorization.

## 9. Self-report (v3 §35)

```
Mode: governance system (Phase C execution)
Created:
- T:\00-Active\Project-AI-Beginnings\packages\companion\src\companion\identity.py
- T:\00-Active\Project-AI-Beginnings\packages\companion\src\companion\fates.py
- T:\00-Active\Project-AI-Beginnings\packages\companion\src\companion\bonded.py
- T:\00-Active\Project-AI-Beginnings\packages\companion\tests\test_identity.py
- T:\00-Active\Project-AI-Beginnings\packages\companion\tests\test_fates.py
- T:\00-Active\Project-AI-Beginnings\tests\test_companion_integration_identity_fates.py
- T:\00-Active\Project-AI-Beginnings\docs\internal\STAGE_19_5C_ACCEPTANCE.md (this file)
Modified:
- T:\00-Active\Project-AI-Beginnings\packages\companion\src\companion\__init__.py (re-exports)
Deleted: None.
Verified:
- 550/550 pytest pass (517 baseline + 33 new = 550)
- mypy --strict clean on 72 source files
- ruff check clean
- ruff format --check clean (72 files)
- 10 real bugs caught and fixed during self-review
Failed: None.
Not verified:
- apps/desktop tests + apps/services tests (pre-existing env gaps, not from Phase C)
Risks:
- None introduced by Phase C. Local main is now 7 commits ahead of origin/main (5 from prior session + 2 from this Phase C + checkpoint commits).
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on commit)
Remaining:
- User authorization to commit Phase C artifacts
- Phase D authorization (next source-code wave)
- Push decision (awaiting user go)
Commands run:
- uv run pytest packages/ tools/tests/ tests/test_companion_integration_identity_fates.py
- uv run mypy packages/ --strict
- uv run ruff check packages/
- uv run ruff format --check packages/
- uv run ruff check --fix packages/ + uv run ruff check --fix --unsafe-fixes packages/
- uv run ruff format packages/
Safe to continue: yes (for commit + Phase D); NOT for code edits without explicit "go"
```
