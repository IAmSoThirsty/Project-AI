# Stage 19.5J2.9 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Discovery source:** `packages/_staging/atlas/verification/replay_system.py`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-29

---

## 0. Phase J2.9 scope

Brings the preserved legacy Atlas replay-bundle concept into canonical Atlas as
deterministic, subordinate replay verification:

- `ReplayBundle`
- `ReplayVerification`
- `ReplaySummary`
- `ReplaySystem`
- `ReplaySystemError`
- `compute_replay_bundle_hash`
- `get_replay_system`
- `reset_replay_system`
- canonical replay bundle hashing
- fail-closed bundle/hash validation
- deterministic reconstruction summary
- explicit save/load bundle operations
- no default filesystem writes during system construction
- optional audit event emission through `AuditTrail`

This closes the J2.9 replay system gap locally. It does not claim production
deployment, public hosting, package publication, or remote CI success until the
implementation commit is pushed and GitHub Actions reports success.

---

## 1. Files created/modified

| Path | Type |
|---|---|
| `packages/atlas/src/atlas/replay_system.py` | source (new) |
| `packages/atlas/src/atlas/__init__.py` | public exports updated |
| `packages/atlas/tests/test_replay_system.py` | unit tests (new) |
| `packages/atlas/README.md` | package documentation updated |
| `CHANGELOG.md` | unreleased checkpoint updated |
| `docs/internal/STAGE_19_5_SESSION_LEDGER.md` | current status updated |
| `docs/internal/FINAL_PEER_REVIEW.md` | historical snapshot correction updated |
| `docs/internal/STAGE_19_5J2_9_ACCEPTANCE.md` | this file |
| `docs/operations/CONTINUITY_MAP.md` | continuity entry updated |

---

## 2. Verification gates

Red test evidence before source implementation:

```text
uv run python -m pytest packages/atlas/tests/test_replay_system.py -q
ImportError: cannot import name 'ReplayBundle' from 'atlas'
```

Executed before this acceptance file was written:

```text
uv run python -m pytest packages/atlas/tests/test_replay_system.py -q
8 passed in 0.43s

uv run python -m pytest packages/atlas/tests/test_replay_system.py packages/atlas/tests -q
367 passed in 0.70s

uv run ruff check packages/atlas/src/atlas/replay_system.py packages/atlas/src/atlas/__init__.py packages/atlas/tests/test_replay_system.py
All checks passed!

uv run ruff format --check packages/atlas/src/atlas/replay_system.py packages/atlas/src/atlas/__init__.py packages/atlas/tests/test_replay_system.py
3 files already formatted

uv run mypy packages/atlas/src/atlas/replay_system.py packages/atlas/tests/test_replay_system.py --strict
Success: no issues found in 2 source files

uv run ruff check .
All checks passed!

uv run ruff format --check .
187 files already formatted

uv run mypy --ignore-missing-imports packages/kernel/src packages/security/src packages/governance/src packages/capability/src packages/execution/src packages/companion/src packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src packages/api/src packages/cli/src apps/desktop/src apps/services/src tools
Success: no issues found in 93 source files

uv run python -m pytest -q --tb=short
1464 passed in 4.50s

QT_QPA_PLATFORM=offscreen uv run python -m pytest -q --tb=short --cov=kernel --cov=security --cov=governance --cov=capability --cov=execution --cov=companion --cov=swr --cov=atlas --cov=arbiter_gov --cov=rlp --cov=project_ai_api --cov=project_ai_cli --cov=project_ai_desktop --cov=project_ai_services --cov-branch --cov-report=term-missing --cov-fail-under=80
1464 passed, 88.47% branch coverage, threshold 80%

uv run python tools/canonical_replay.py
canonical replay: 5/5 invariants passed

uv run python tools/verify_frozen_history.py
CHAIN INTACT. 2264 sections verified.
```

Coverage emitted the existing warning that `arbiter_gov` was not imported.
Classification: not blocking current task; the coverage command exited 0 and
remained above threshold.

Remote CI after commit/push:

```text
Pending until the J2.9 implementation commit is pushed.
```

---

## 3. Architectural invariants verified

- **Deterministic:** bundle hash and reconstruction summary hash are stable for
  identical bundle contents.
- **Tamper-evident:** mismatched stored bundle hashes fail closed.
- **Subordinate:** replay summaries carry the canonical Atlas subordination
  notice and do not grant authority.
- **No hidden filesystem mutation:** `ReplaySystem(bundle_dir=...)` does not
  create the directory until `save_bundle()` is explicitly called.
- **Portable:** bundles save/load as JSON, preserving the canonical hash.
- **Audit-visible:** replay can append `atlas.replay_bundle` validation events
  to `AuditTrail`.

---

## 4. Remaining J2 work

- J2.9 replay system is closed locally.
- All J1 audit gaps are now closed locally.
- Remote CI remains pending until this implementation is committed and pushed.

Safe to continue: yes.
