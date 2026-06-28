# Stage 19.5J2.5 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Discovery:** `docs/internal/PHASE_J2_5_DISCOVERY.md`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-28

---

## 0. Phase J2.5 scope

Brings constitutional-kernel checks into the canonical execution path:

- `ViolationType`
- `PARAMETER_BOUNDS`
- `ConstitutionalKernel`
- `constitutional_state_hash`
- `get_constitutional_kernel`
- `reset_constitutional_kernel`
- denial of sludge-to-Reality-Stack state
- denial of narrative probability without evidence
- denial of unaudited projection inputs
- denial of agency claims without TierA/TierB evidence
- denial of projection/simulation/timeline state without deterministic seed
- denial of state hash mismatch
- denial of influence-graph hash/lineage drift
- denial of out-of-bounds parameters and drivers
- denial of temporal skew and non-monotonic timestep progression
- execution-gate proof that a constitutional invariant denial prevents
  capability consumption and executor invocation

This closes the J2.5 constitutional-kernel integration gap locally. It does not
claim full constitutional governance for every future doctrine; it proves the
legacy kernel checks now execute through the current governance/execution gate.

---

## 1. Files created/modified

| Path | Type |
|---|---|
| `packages/governance/src/governance/constitutional_kernel.py` | source (new) |
| `packages/governance/src/governance/__init__.py` | public exports updated |
| `packages/governance/tests/test_constitutional_kernel.py` | unit tests (new) |
| `tests/test_constitutional_kernel_execution_integration.py` | integration tests (new) |
| `packages/governance/README.md` | package documentation updated |
| `CHANGELOG.md` | unreleased checkpoint updated |
| `docs/internal/PHASE_J2_5_DISCOVERY.md` | discovery/design record |
| `docs/internal/STAGE_19_5_SESSION_LEDGER.md` | current status updated |
| `docs/internal/STAGE_19_5J2_5_ACCEPTANCE.md` | this file |
| `docs/operations/CONTINUITY_MAP.md` | continuity entry updated |

---

## 2. Verification gates

Red test evidence before source implementation:

```text
uv run python -m pytest packages/governance/tests/test_constitutional_kernel.py tests/test_constitutional_kernel_execution_integration.py
ImportError: cannot import name 'ConstitutionalKernel' from 'governance'
```

Executed before this acceptance file was written:

```text
uv run python -m pytest packages/governance/tests/test_constitutional_kernel.py tests/test_constitutional_kernel_execution_integration.py -q
14 passed in 0.09s

uv run python -m pytest packages/governance/tests packages/execution/tests tests/test_constitutional_kernel_execution_integration.py -q
406 passed in 0.51s

uv run mypy packages/governance/src/governance/constitutional_kernel.py packages/governance/tests/test_constitutional_kernel.py tests/test_constitutional_kernel_execution_integration.py --strict
Success: no issues found in 3 source files

uv run mypy packages/governance/src packages/governance/tests packages/execution/tests tests/test_constitutional_kernel_execution_integration.py --strict
Success: no issues found in 18 source files

uv run ruff check packages/governance/src packages/governance/tests packages/execution/tests tests/test_constitutional_kernel_execution_integration.py
All checks passed!

uv run ruff format --check packages/governance/src packages/governance/tests packages/execution/tests tests/test_constitutional_kernel_execution_integration.py
18 files already formatted
```

Full repo gates executed after implementation:

```text
uv run ruff check .
All checks passed!

uv run ruff format --check .
181 files already formatted

uv run mypy --ignore-missing-imports packages/kernel/src packages/security/src packages/governance/src packages/capability/src packages/execution/src packages/companion/src packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src packages/api/src packages/cli/src apps/desktop/src apps/services/src tools
Success: no issues found in 90 source files

uv run python -m pytest -q --tb=short
1420 passed in 6.19s

QT_QPA_PLATFORM=offscreen uv run python -m pytest -q --tb=short --cov=kernel --cov=security --cov=governance --cov=capability --cov=execution --cov=companion --cov=swr --cov=atlas --cov=arbiter_gov --cov=rlp --cov=project_ai_api --cov=project_ai_cli --cov=project_ai_desktop --cov=project_ai_services --cov-branch --cov-report=term-missing --cov-fail-under=80
1420 passed, 89.92% branch coverage, threshold 80%

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
GitHub Actions CI run 28330827940
Commit: a87c5594ce767ffb6ca49e71d6bde4d60c2dc0f8
Conclusion: success
URL: https://github.com/IAmSoThirsty/Project-AI/actions/runs/28330827940
```

---

## 3. Architectural invariants verified

- **Single execution path:** Constitutional checks plug into
  `kernel.InvariantEngine`; `GovernanceEngine` evaluates them before governors;
  `ExecutionGate` denies before capability consumption or executor invocation.
- **Fail-closed:** Invalid constitutional state returns CRITICAL
  `InvariantViolation` objects. `GovernanceEngine` converts these into DENY
  decisions.
- **Evidence-bound:** Denials are included in `GovernanceResult` and
  `EvidenceBundle` hashes.
- **No parallel authority:** The module does not issue capabilities, execute
  actions, mutate state, or bypass existing governance.
- **Deterministic hashing:** `constitutional_state_hash()` normalizes nested
  JSON-like state and quantizes floats before SHA-256 hashing.
- **Stateful temporal guard:** Kernel instances enforce monotonic timestep
  progression and declared timestep jumps.

---

## 4. Remaining J2 work

- J2.5 constitutional-kernel integration is locally closed.
- Implementation commit `a87c5594ce767ffb6ca49e71d6bde4d60c2dc0f8`
  passed GitHub Actions CI in run `28330827940`.
- The next open J1 audit gap is J2.6 failure surveillance, unless the user
  pivots.

Safe to continue: yes.
