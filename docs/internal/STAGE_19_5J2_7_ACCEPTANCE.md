# Stage 19.5J2.7 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Discovery source:** `packages/_staging/atlas/sandbox/sludge_sandbox.py`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-28

---

## 0. Phase J2.7 scope

Brings the legacy Sludge sandbox concept into canonical Atlas as isolated
fictional narrative generation:

- `NarrativeArchetype`
- `SludgeNarrative`
- `SludgeSandbox`
- `SludgeSandboxError`
- `compute_sludge_snapshot_hash`
- `get_sludge_sandbox`
- `reset_sludge_sandbox`
- deterministic Sludge narrative IDs
- Reality Stack source snapshot hashing
- SS-only Sludge output
- mandatory fiction banner and decision-prohibition watermark
- no numeric probabilities in generated narrative branches
- no Reality Stack source text copied into fictional branches
- no default filesystem writes during sandbox construction
- optional hash-chained `AuditTrail` events
- contamination detection for Sludge markers in non-SS payloads

This closes the J2.7 sandbox gap locally. It does not claim operating-system
process isolation, VM/container sandboxing, or production deployment. It proves
canonical Atlas now has a fail-closed Sludge isolation layer for fictional
outputs.

---

## 1. Files created/modified

| Path | Type |
|---|---|
| `packages/atlas/src/atlas/sludge_sandbox.py` | source (new) |
| `packages/atlas/src/atlas/__init__.py` | public exports updated |
| `packages/atlas/tests/test_sludge_sandbox.py` | unit tests (new) |
| `packages/atlas/README.md` | package documentation updated |
| `CHANGELOG.md` | unreleased checkpoint updated |
| `docs/internal/STAGE_19_5_SESSION_LEDGER.md` | current status updated |
| `docs/internal/STAGE_19_5J2_7_ACCEPTANCE.md` | this file |
| `docs/operations/CONTINUITY_MAP.md` | continuity entry updated |

---

## 2. Verification gates

Red test evidence before source implementation:

```text
uv run python -m pytest packages/atlas/tests/test_sludge_sandbox.py -q
ImportError: cannot import name 'NarrativeArchetype' from 'atlas'
```

Executed before this acceptance file was written:

```text
uv run python -m pytest packages/atlas/tests/test_sludge_sandbox.py -q
10 passed in 0.37s

uv run python -m pytest packages/atlas/tests/test_sludge_sandbox.py packages/atlas/tests -q
359 passed in 0.86s

uv run mypy packages/atlas/src/atlas/sludge_sandbox.py packages/atlas/tests/test_sludge_sandbox.py --strict
Success: no issues found in 2 source files

uv run ruff check packages/atlas/src/atlas/sludge_sandbox.py packages/atlas/src/atlas/__init__.py packages/atlas/tests/test_sludge_sandbox.py
All checks passed!

uv run ruff format --check packages/atlas/src/atlas/sludge_sandbox.py packages/atlas/src/atlas/__init__.py packages/atlas/tests/test_sludge_sandbox.py
3 files already formatted

uv run ruff check .
All checks passed!

uv run ruff format --check .
185 files already formatted

uv run mypy --ignore-missing-imports packages/kernel/src packages/security/src packages/governance/src packages/capability/src packages/execution/src packages/companion/src packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src packages/api/src packages/cli/src apps/desktop/src apps/services/src tools
Success: no issues found in 92 source files

uv run python -m pytest -q --tb=short
1451 passed in 3.79s

QT_QPA_PLATFORM=offscreen uv run python -m pytest -q --tb=short --cov=kernel --cov=security --cov=governance --cov=capability --cov=execution --cov=companion --cov=swr --cov=atlas --cov=arbiter_gov --cov=rlp --cov=project_ai_api --cov=project_ai_cli --cov=project_ai_desktop --cov=project_ai_services --cov-branch --cov-report=term-missing --cov-fail-under=80
1451 passed, 89.30% branch coverage, threshold 80%

uv run python tools/canonical_replay.py
canonical replay: 5/5 invariants passed

uv run python tools/verify_frozen_history.py
CHAIN INTACT. 2264 sections verified.
```

Coverage emitted the existing warning that `arbiter_gov` was not imported.
Classification: not blocking current task; the coverage command exited 0 and
remained above threshold.

---

## 3. Architectural invariants verified

- **SS-only output:** `SludgeNarrative` rejects any stack except `SS`.
- **Source provenance without content leakage:** generated narratives include
  only the canonical RS snapshot hash, not copied RS text or numeric values.
- **No hidden filesystem mutation:** canonical sandbox construction does not
  create a default Sludge data directory.
- **Fail-closed validation:** non-RS snapshots, empty snapshots, invalid hashes,
  non-empty type violations, and Sludge markers in non-SS payloads raise
  `SludgeSandboxError`.
- **Audit-visible:** initialization and narrative generation can append
  hash-chained `AuditTrail` events.
- **Deterministic:** same RS snapshot and archetype set produce the same
  narrative ID and branches.

---

## 4. Remaining J2 work

- J2.7 sandbox is locally closed.
- The next open J1 audit gap after J2.7 is J2.8 CLI / API surface, unless the
  user pivots.

Safe to continue: yes.
