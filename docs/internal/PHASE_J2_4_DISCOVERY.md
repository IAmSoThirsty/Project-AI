# Phase J2.4 Discovery — atlas graph construction (driver_engine_10d + graph builder + temporal graph)

**Status:** DISCOVERY + PLAN (no source code written yet)
**Authority:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J, J1 audit
**Date:** 2026-06-25
**Author:** Hermes (Quencher session)

---

## 0. Context

The J1 audit identified 9 feature gaps in canonical atlas. **3 of 9 closed**:
- J2.1: Sensitivity analysis ✅
- J2.2: Audit trail ✅
- J2.3: Bayesian inference ✅

**6 gaps remain**:
1. Graph construction (driver_engine_10d + graph builder + temporal graph) — **THIS PHASE**
2. Constitutional kernel integration
3. Failure surveillance
4. Sandbox (sludge_sandbox)
5. CLI / API surface
6. Replay system

J2.4 = Graph construction port. Path A1 per established pattern:
faithful port of legacy code with numpy (already a dep), no shortcuts.

---

## 1. Legacy code inventory

Total legacy graph code: **1,857 LOC across 3 files**

| File | LOC | Purpose |
|---|---|---|
| `atlas/core/graph/builder.py` | 718 | GraphBuilder: constructs influence graphs from entities, relationships, opinions. Calculates network metrics (centrality, pagerank, clustering), detects communities. |
| `atlas/core/graph/temporal_graph.py` | 605 | TemporalGraph: time-evolving graphs with snapshots, change detection, evolution tracking. |
| `atlas/core/drivers/driver_engine_10d.py` | 534 | DriverEngine10D: 10-dimensional driver analysis with PCA, correlations, sensitivities. |

### External deps (legacy)
- `atlas.audit.trail.AuditCategory`, `AuditLevel`, `AuditTrail`, `get_audit_trail`
- `atlas.config.loader.ConfigLoader`, `get_config_loader`
- `atlas.schemas.validator.SchemaValidator`, `get_schema_validator`
- `logging`, `datetime`, `collections`, `typing`

---

## 2. Canonical atlas current state

Existing modules:
- `analysis.py` (120 LOC): evidence-weighted posterior
- `service.py` (116 LOC): execution-gated persistence
- `sensitivity.py` (895 LOC): Sobol decomposition, stability, tipping
- `audit.py` (660 LOC): hash-chained audit trail
- `bayesian.py` (660 LOC): Bayesian inference

No existing graph or driver concept in canonical.

---

## 3. Port design

### Decision: Two new modules

| Module | LOC est | Purpose |
|---|---|---|
| `packages/atlas/src/atlas/graph.py` | ~700 | GraphBuilder + InfluenceGraph + metrics (centrality, pagerank, clustering) + community detection |
| `packages/atlas/src/atlas/temporal_graph.py` | ~600 | TemporalGraph + snapshot history + change detection |
| `packages/atlas/src/atlas/driver_engine.py` | ~500 | DriverEngine10D + 10-dimensional PCA + correlations + sensitivities |

Note: `driver_engine_10d.py` was the legacy name. In canonical, we'll name it just `driver_engine.py` since the dimension count is configurable.

### Public API additions

#### graph.py (~15 exports)
- `GraphError` (exception)
- `GraphNode` (frozen dataclass: node_id, attributes, weight)
- `GraphEdge` (frozen dataclass: source, target, weight, relation)
- `GraphMetrics` (frozen dataclass: centrality, pagerank, clustering, etc.)
- `Community` (frozen dataclass: nodes, modularity)
- `InfluenceGraph` (frozen dataclass: nodes, edges, metrics, communities)
- `GraphBuilder` (class: build_graph, add_node, add_edge, calculate_metrics, detect_communities)
- `compute_centrality` (function)
- `compute_pagerank` (function)
- `compute_clustering` (function)
- `detect_communities` (function)
- `get_graph_builder` (factory)
- `reset_graph_builder` (factory reset)
- `_GRAPH_NODE_HASH` etc constants

#### temporal_graph.py (~8 exports)
- `TemporalGraphError` (exception)
- `GraphSnapshot` (frozen dataclass: timestamp, graph, change_set)
- `TemporalChange` (frozen dataclass: change_type, node/edge, timestamp)
- `TemporalGraph` (frozen dataclass: snapshots, evolution)
- `compute_temporal_change` (function)
- `track_evolution` (function)
- `get_temporal_graph` (factory)
- `reset_temporal_graph` (factory reset)

#### driver_engine.py (~12 exports)
- `DriverEngineError` (exception)
- `DriverDimension` (frozen dataclass: name, weight, range)
- `DriverState` (frozen dataclass: dimensions, values)
- `DriverAnalysis` (frozen dataclass: pca_components, correlations, sensitivities)
- `DriverEngine` (class: analyze, project, correlate)
- `compute_pca` (function)
- `compute_correlation_matrix` (function)
- `compute_driver_sensitivities` (function)
- `get_driver_engine` (factory)
- `reset_driver_engine` (factory reset)

### Architectural invariants (matching J2.1/J2.2/J2.3)

- **Downward-only deps**: only `atlas.analysis` (SUBORDINATION_NOTICE) + `atlas.audit` + stdlib + numpy
- **Subordination notice bound** to all graph/temporal/driver hashes
- **Fail-closed**: every dataclass validates; respective Error on bad input
- **Pluggable audit**: optional `audit_trail: AuditTrail | None = None`
- **Deterministic**: same inputs → same outputs (graph hash, PCA components, etc.)
- **Strict typing**: mypy --strict clean
- **numpy usage**: typed arrays via `numpy.typing.NDArray[np.float64]`
- **Thread-safe**: tested with concurrent threads

### scipy dependency
The legacy code uses numpy for matrix operations. For canonical, we use **numpy only** (already a dep) — no scipy needed for graph ops (basic linear algebra + simple community detection). This keeps the dep footprint small.

### NetworkX dependency
The legacy graph code doesn't use NetworkX — it implements basic algorithms directly. Canonical will match: pure numpy implementation, no NetworkX.

---

## 4. Sub-phase plan

Given the **1857 LOC scope**, this is larger than J2.1 (895 LOC) or J2.3 (660 LOC). To stay within the "≤5 new source files per wave" rule, I'll split across **3 waves**:

### Wave 1: J2.4.0 — `graph.py` (J2.4.0a) + tests (J2.4.1a)
- Source: ~700 LOC
- Unit tests: ~30 tests (~600 LOC)
- Integration tests: ~8 tests (~300 LOC)
- Acceptance doc: ~150 LOC
- Commit: `feat(stage-19.5J2.4.0a): atlas graph builder`
- Wave 1 gates: 1340 + 38 = ~1378 tests

### Wave 2: J2.4.0b — `driver_engine.py` + tests
- Source: ~500 LOC
- Unit tests: ~25 tests (~500 LOC)
- Integration tests: ~6 tests (~200 LOC)
- Commit: `feat(stage-19.5J2.4.0b): atlas driver engine 10D`
- Wave 2 gates: 1378 + 31 = ~1409 tests

### Wave 3: J2.4.0c — `temporal_graph.py` + tests
- Source: ~600 LOC
- Unit tests: ~25 tests (~500 LOC)
- Integration tests: ~6 tests (~200 LOC)
- Acceptance doc: ~200 LOC
- Commit: `feat(stage-19.5J2.4.0c): atlas temporal graph`
- Wave 3 gates: 1409 + 31 = ~1440 tests

**Each wave's commit includes its own acceptance doc update.** Final closure doc after Wave 3.

---

## 5. Risk + decisions

### Risk 1: Larger scope than prior J2 phases
- **Decision**: split into 3 waves per "≤5 files per wave" rule
- Each wave independently gate-green
- No inter-wave dependencies (graph.py doesn't need driver_engine, etc.)

### Risk 2: PCA implementation correctness
- PCA via numpy.linalg.eig on covariance matrix
- Need to ensure deterministic ordering (sort by eigenvalue descending)
- **Decision**: use np.linalg.eigh (Hermitian) for symmetric matrices
- Document the convention in code

### Risk 3: PageRank iterative algorithm
- Power iteration method: convergence tolerance matters
- **Decision**: use np.linalg.matrix_norm for convergence check
- Default tolerance: 1e-6, max iterations: 100

### Risk 4: Community detection complexity
- Legacy uses simple label propagation
- **Decision**: implement modularity-based greedy (numpy + iterative)
- Or: implement simple Louvain-style with modularity scoring

### Risk 5: Graph hash determinism
- NetworkX graph hashes are NOT deterministic across runs
- We use canonical JSON representation + SHA-256 (matching audit pattern)
- **Decision**: same approach as audit.py

### Risk 6: Backward compat with existing atlas
- All existing tests must continue passing (1340 baseline)
- No changes to analysis.py, service.py, sensitivity.py, audit.py, bayesian.py
- **Decision**: zero-touch on existing modules

---

## 6. Honest disclosure

This is **discovery only**. NO source code has been written yet. Per
Thirstys standards + the established J2.1/J2.2/J2.3 pattern, source code
requires explicit "go J2.4.0a" authorization before I write anything.

The full legacy code (1857 LOC across 3 files) has been analyzed. The
port will be ~1800 LOC across 3 new modules (slight reduction by
stripping legacy's `ConfigLoader`/`SchemaValidator` deps which are
legacy-only concepts not relevant to canonical atlas).

---

## 7. Quality gates per sub-phase

Each sub-phase MUST end with all four canonical gates green via `uv run`:
- `uv run pytest`
- `uv run mypy packages/ --strict`
- `uv run ruff check packages/`
- `uv run ruff format --check packages/`

NO sub-phase will be left in a broken state. NO shortcuts. Per Thirstys
standards.

---

## 8. Alternative paths

If you'd prefer a smaller scope first, alternatives:

1. **J2.5 — Failure surveillance** (~400 LOC, easier, monitoring only)
2. **J2.6 — CLI / API surface** (~250 LOC, user-facing, low risk)
3. **J2.7 — Replay system** (~200 LOC, leverages existing audit replay)

Or stop here and tackle something different entirely.

---

## 9. Recommendation

Proceed with J2.4.0a (Wave 1: graph builder) first. It's the largest gap
and the foundation for several other features. Once it's solid, we can
decide on Wave 2/3 or pivot to a smaller gap.