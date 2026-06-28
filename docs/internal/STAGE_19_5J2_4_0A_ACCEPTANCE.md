# Stage 19.5J2.4.0a Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Discovery:** `docs/internal/PHASE_J2_4_DISCOVERY.md`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-28

---

## 0. Phase J2.4.0a scope

Brings the first graph-construction wave to canonical Atlas:

- `GraphBuilder`
- `GraphNode`
- `GraphEdge`
- `GraphMetrics`
- `Community`
- `InfluenceGraph`
- centrality, PageRank, clustering, density, average-degree, and connected
  component community detection
- deterministic graph hash with `SUBORDINATION_NOTICE` bound into the canonical
  hash body
- optional `AuditTrail` integration for graph construction and fail-closed
  construction failures

This closes Wave 1 of the J1 graph-construction gap. J2.4 is not fully closed
until the remaining planned driver-engine and temporal-graph waves are either
implemented or explicitly deferred.

---

## 1. Files created/modified

| Path | Type |
|---|---|
| `packages/atlas/src/atlas/graph.py` | source (new) |
| `packages/atlas/src/atlas/__init__.py` | public exports updated |
| `packages/atlas/tests/test_graph.py` | unit tests (new) |
| `tests/test_atlas_graph_integration.py` | integration tests (new) |
| `packages/atlas/README.md` | package documentation updated |
| `CHANGELOG.md` | unreleased development checkpoint updated |
| `docs/internal/STAGE_19_5_SESSION_LEDGER.md` | next-session state updated |
| `docs/internal/STAGE_19_5J2_4_0A_ACCEPTANCE.md` | this file |
| `docs/operations/CONTINUITY_MAP.md` | continuity entry updated |

---

## 2. Verification gates

Executed before this acceptance file was written:

```text
uv run pytest packages/atlas/tests/test_graph.py tests/test_atlas_graph_integration.py -q
24 passed in 0.46s

uv run pytest packages/atlas/tests tests/test_atlas_graph_integration.py tests/test_atlas_audit_integration.py tests/test_atlas_bayesian_integration.py tests/test_atlas_sensitivity_integration.py -q
357 passed in 0.74s

uv run mypy packages/atlas/src/atlas/graph.py packages/atlas/tests/test_graph.py tests/test_atlas_graph_integration.py --strict
Success: no issues found in 3 source files

uv run ruff check packages/atlas/src/atlas/graph.py packages/atlas/src/atlas/__init__.py packages/atlas/tests/test_graph.py tests/test_atlas_graph_integration.py
All checks passed!

uv run ruff format --check packages/atlas/src/atlas/graph.py packages/atlas/src/atlas/__init__.py packages/atlas/tests/test_graph.py tests/test_atlas_graph_integration.py
4 files already formatted
```

Full repo gates executed after this acceptance file was created:

```text
uv run ruff check .
All checks passed!

uv run ruff format --check .
172 files already formatted

uv run mypy --ignore-missing-imports packages/kernel/src packages/security/src packages/governance/src packages/capability/src packages/execution/src packages/companion/src packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src packages/api/src packages/cli/src apps/desktop/src apps/services/src tools
Success: no issues found in 87 source files

uv run pytest -q --tb=short
1367 passed in 4.11s

QT_QPA_PLATFORM=offscreen uv run pytest -q --tb=short --cov=kernel --cov=security --cov=governance --cov=capability --cov=execution --cov=companion --cov=swr --cov=atlas --cov=arbiter_gov --cov=rlp --cov=project_ai_api --cov=project_ai_cli --cov=project_ai_desktop --cov=project_ai_services --cov-branch --cov-report=term-missing --cov-fail-under=80
1367 passed, 91.07% branch coverage, threshold 80%

uv run python tools/canonical_replay.py
canonical replay: 5/5 invariants passed

uv run python tools/verify_frozen_history.py
CHAIN INTACT. 2264 sections verified.

SKIP=no-commit-to-branch,gitleaks uv run pre-commit run --all-files
passed all non-skipped hooks
```

Coverage emitted the existing warning that `arbiter_gov` was not imported.
Classification: not blocking current task; the coverage command exited 0 and
remained above threshold.

---

## 3. Public API added

| Symbol | Purpose |
|---|---|
| `GraphError` | fail-closed graph exception |
| `GraphNode` | frozen validated node |
| `GraphEdge` | frozen validated directed weighted edge |
| `GraphMetrics` | centrality/PageRank/clustering/density aggregate |
| `Community` | connected component with cohesion |
| `InfluenceGraph` | immutable graph result with deterministic SHA-256 |
| `GraphBuilder` | builds graphs from dataclasses or legacy mapping input |
| `compute_centrality` | in/out/total/normalized degree centrality |
| `compute_pagerank` | weighted directed PageRank with dangling-node handling |
| `compute_clustering` | directed neighbor clustering coefficient |
| `detect_communities` | deterministic connected-component communities |
| `compute_graph_hash` | canonical graph hash helper |
| `get_graph_builder` | singleton factory |
| `reset_graph_builder` | singleton reset |

---

## 4. Architectural invariants verified

- **Downward-only deps:** `atlas.graph` imports only `atlas.analysis`,
  `atlas.audit`, and stdlib.
- **Fail-closed:** invalid nodes, edges, graph shape, PageRank parameters,
  unknown edge endpoints, duplicate nodes, and empty graphs raise `GraphError`.
- **Subordination:** every public result dataclass carries
  `SUBORDINATION_NOTICE`; the graph hash body includes that notice.
- **Deterministic:** nodes/edges/communities are canonical-sorted; identical
  unordered input produces identical `InfluenceGraph` values and graph hashes.
- **Audit-visible:** init, successful build, and failed build paths emit
  hash-chained `AuditTrail` events when a trail is attached.
- **Legacy-compatible input:** `GraphBuilder.build_graph()` accepts legacy
  entity/relationship/opinion mapping shapes from
  `packages/_staging/atlas/core/graph/builder.py`.

---

## 5. Bugs caught during red/green work

1. Missing `atlas.graph` exports caused the expected red import failure.
2. Initial clustering test undercounted closed neighborhoods; corrected to
   match the legacy directed-neighbor algorithm.
3. Initial legacy-mapping test assumed input edge order; corrected to assert
   semantic edge relation mapping because canonical output is sorted.
4. Ruff caught unsorted `__all__`, an unused import, tuple-concatenation nits,
   and formatting drift before acceptance.

---

## 6. Remaining J2.4 work

- J2.4.0b: `driver_engine.py` 10-dimensional driver analysis.
- J2.4.0c: `temporal_graph.py` snapshot/change/evolution tracking.

Safe to continue: yes.
