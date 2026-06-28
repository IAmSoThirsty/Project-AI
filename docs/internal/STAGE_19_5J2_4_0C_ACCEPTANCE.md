# Stage 19.5J2.4.0c Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Discovery:** `docs/internal/PHASE_J2_4_DISCOVERY.md`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-28

---

## 0. Phase J2.4.0c scope

Brings the third graph-construction wave to canonical Atlas:

- `TemporalNodeType`
- `TemporalEdgeType`
- `TemporalNode`
- `TemporalEdge`
- `GraphSnapshot`
- `TemporalChange`
- `TemporalEvolution`
- `TemporalChainVerification`
- `TemporalGraph`
- deterministic snapshot hashes with `SUBORDINATION_NOTICE` bound
- Merkle-style snapshot chain verification
- temporal edge weight decay
- ordered weighted adjacency matrices
- snapshot-to-snapshot change detection
- evolution tracking across snapshot sequences
- optional `AuditTrail` integration for init, node addition, edge addition,
  snapshot creation, and fail-closed operation failures

This closes Wave 3 of the J2.4 graph-construction gap. J2.4 is now locally
closed across graph builder, driver engine 10D, and temporal graph.

---

## 1. Files created/modified

| Path | Type |
|---|---|
| `packages/atlas/src/atlas/temporal_graph.py` | source (new) |
| `packages/atlas/src/atlas/__init__.py` | public exports updated |
| `packages/atlas/tests/test_temporal_graph.py` | unit tests (new) |
| `tests/test_atlas_temporal_graph_integration.py` | integration tests (new) |
| `packages/atlas/README.md` | package documentation updated |
| `CHANGELOG.md` | unreleased development checkpoint updated |
| `docs/internal/PHASE_J2_4_DISCOVERY.md` | wave status updated |
| `docs/internal/STAGE_19_5_SESSION_LEDGER.md` | next-session state updated |
| `docs/internal/STAGE_19_5J2_4_0C_ACCEPTANCE.md` | this file |
| `docs/operations/CONTINUITY_MAP.md` | continuity entry updated |

---

## 2. Verification gates

Red test evidence before source implementation:

```text
python -m pytest packages/atlas/tests/test_temporal_graph.py tests/test_atlas_temporal_graph_integration.py
ModuleNotFoundError: No module named 'atlas'
```

Plain `python -m pytest` does not load the uv workspace packages here.
The repo-standard red run then failed on the intended missing temporal exports:

```text
uv run python -m pytest packages/atlas/tests/test_temporal_graph.py tests/test_atlas_temporal_graph_integration.py
ImportError: cannot import name 'GraphSnapshot' from 'atlas'
```

Executed before this acceptance file was written:

```text
uv run python -m pytest packages/atlas/tests/test_temporal_graph.py tests/test_atlas_temporal_graph_integration.py -q
15 passed in 0.44s

uv run pytest packages/atlas/tests tests/test_atlas_graph_integration.py tests/test_atlas_driver_engine_integration.py tests/test_atlas_temporal_graph_integration.py tests/test_atlas_audit_integration.py tests/test_atlas_bayesian_integration.py tests/test_atlas_sensitivity_integration.py -q
396 passed in 1.08s

uv run mypy packages/atlas/src/atlas/temporal_graph.py packages/atlas/tests/test_temporal_graph.py tests/test_atlas_temporal_graph_integration.py --strict
Success: no issues found in 3 source files

uv run ruff check packages/atlas/src/atlas/temporal_graph.py packages/atlas/src/atlas/__init__.py packages/atlas/tests/test_temporal_graph.py tests/test_atlas_temporal_graph_integration.py
All checks passed!

uv run ruff format --check packages/atlas/src/atlas/temporal_graph.py packages/atlas/src/atlas/__init__.py packages/atlas/tests/test_temporal_graph.py tests/test_atlas_temporal_graph_integration.py
4 files already formatted
```

Full repo gates executed after the temporal implementation:

```text
uv run ruff check .
All checks passed!

uv run ruff format --check .
178 files already formatted

uv run mypy --ignore-missing-imports packages/kernel/src packages/security/src packages/governance/src packages/capability/src packages/execution/src packages/companion/src packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src packages/api/src packages/cli/src apps/desktop/src apps/services/src tools
Success: no issues found in 89 source files

uv run python -m pytest -q --tb=short
1406 passed in 4.90s

QT_QPA_PLATFORM=offscreen uv run python -m pytest -q --tb=short --cov=kernel --cov=security --cov=governance --cov=capability --cov=execution --cov=companion --cov=swr --cov=atlas --cov=arbiter_gov --cov=rlp --cov=project_ai_api --cov=project_ai_cli --cov=project_ai_desktop --cov=project_ai_services --cov-branch --cov-report=term-missing --cov-fail-under=80
1406 passed, 90.15% branch coverage, threshold 80%

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
GitHub Actions CI run 28326886242
Commit: 876ba1309e0d8a5a866928ecd4c6094b17778eb5
Conclusion: success
URL: https://github.com/IAmSoThirsty/Project-AI/actions/runs/28326886242
```

Expanded strict mypy over all Atlas sources was also tried:

```text
uv run mypy packages/atlas/src packages/atlas/tests tests/test_atlas_temporal_graph_integration.py --strict
packages\atlas\src\atlas\sensitivity.py:39: error: Library stubs not installed for "scipy.linalg"
packages\atlas\src\atlas\sensitivity.py:39: error: Library stubs not installed for "scipy"
```

Classification: environment/dependency issue and not blocking current task.
The temporal graph targeted strict mypy passed, and the CI-shaped mypy command
with `--ignore-missing-imports` passed on 89 source files.

---

## 3. Public API added

| Symbol | Purpose |
|---|---|
| `TEMPORAL_GRAPH_ALGORITHM` | canonical temporal graph hash algorithm identifier |
| `GENESIS_SNAPSHOT_HASH` | initial snapshot chain hash |
| `TemporalGraphError` | fail-closed temporal graph exception |
| `TemporalNodeType` | canonical temporal node enum |
| `TemporalEdgeType` | canonical temporal edge enum |
| `TemporalNode` | source-backed graph node |
| `TemporalEdge` | source-backed temporal edge with decay |
| `GraphSnapshot` | deterministic snapshot with counts and hash linkage |
| `TemporalChange` | added/removed/changed node or edge delta |
| `TemporalEvolution` | adjacent snapshot evolution record |
| `TemporalChainVerification` | snapshot chain verification result |
| `TemporalGraph` | mutable builder/history surface for temporal snapshots |
| `compute_snapshot_hash` | canonical snapshot hash helper |
| `compute_temporal_changes` | snapshot diff helper |
| `track_evolution` | snapshot sequence evolution helper |
| `get_temporal_graph` | singleton factory |
| `reset_temporal_graph` | singleton reset |

---

## 4. Architectural invariants verified

- **Downward-only deps:** `atlas.temporal_graph` imports only `atlas.analysis`,
  `atlas.audit`, stdlib, and numpy.
- **Fail-closed:** missing source hashes, invalid hash casing, duplicate nodes
  or edges, unknown edge endpoints, invalid source tiers, invalid weights, and
  invalid snapshot chains raise or report `TemporalGraphError` /
  `TemporalChainVerification`.
- **Subordination:** every public result dataclass carries
  `SUBORDINATION_NOTICE`; snapshot hash bodies include that notice.
- **Deterministic:** nodes and edges are canonicalized by ID before hash,
  snapshot, adjacency, and change-detection output.
- **Audit-visible:** init, node addition, edge addition, snapshot creation, and
  failed edge/node/snapshot operations emit hash-chained `AuditTrail` events
  when a trail is attached.
- **Legacy-compatible semantics:** time-evolving graph snapshots, source-backed
  inclusion, weight decay, change detection, and evolution tracking are ported
  from `packages/_staging/atlas/core/graph/temporal_graph.py`; legacy config
  and schema-validator dependencies were intentionally not ported.

---

## 5. Remaining J2 work

- J2.4 graph construction is locally closed.
- Implementation commit `876ba1309e0d8a5a866928ecd4c6094b17778eb5` passed
  GitHub Actions CI in run `28326886242`.
- Remaining J1 audit gaps now move to the next open item: J2.5 constitutional
  kernel integration, unless the user pivots.

Safe to continue: yes.
