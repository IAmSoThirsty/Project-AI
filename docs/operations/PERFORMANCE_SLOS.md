# Performance & SLOs

> **Scope:** operational targets and measurement approach for the
> Project-AI development stack. **Targets are TBD pending
> measurement.** This document establishes the measurement surface;
> concrete numbers land as they are observed in the field.

---

## 0. Why SLOs are TBD (not "guaranteed fast")

The development stack is a **governance substrate**, not a high-throughput
service. The system's correctness properties (fail-closed execution
gate, hash-chained audit, deterministic replay) matter more than raw
throughput. SLOs reflect this priority: **latency is bounded, not
minimized; correctness is enforced, not optimized**.

Targets below are initial working assumptions, to be revised after the
first production measurement pass.

---

## 1. API gateway (`packages/api`)

| Metric | Target | Measurement | Notes |
|---|---|---|---|
| `GET /health/live` p99 latency | < 10 ms | request log + histogram | Health endpoint must be cheap; failure here blocks the entire stack |
| Public route p99 latency | < 100 ms | request log | DOIs + replay status are static; atlas status is a constant |
| Protected route p99 latency (no audit write) | < 200 ms | request log | `/audit` is a read against the JSONL file |
| Protected route p99 latency (with audit write) | < 500 ms | request log + audit tail | Includes append + flush; bounded by the audit path's filesystem |
| Audit write success rate | > 99.99% | audit log + error counter | Failures must surface as 503 (not silent drop) |
| Cold-start time (container start → first /health/live 200) | < 30 s | `docker compose up` timing | Healthcheck has `start_period: 5s`; budget is 6× that |

**Measurement surface:** FastAPI middleware logs (add if missing);
`docker stats` for per-container memory + CPU; `tail -f
${PROJECT_AI_AUDIT_PATH}` for audit throughput.

---

## 2. Audit log growth

| Metric | Target | Notes |
|---|---|---|
| Audit record size | < 1 KB avg, < 4 KB p99 | A verdict or canary record should fit in a single JSONL line |
| Audit throughput | > 100 records/s sustained | Bounded by `PROJECT_AI_AUDIT_PATH` filesystem write speed |
| Audit retention (default) | indefinite in named volume | Operator must archive or rotate per `PRODUCTION_DEPLOY.md` §6 |

**Archival trigger:** when the named volume exceeds 80% of its
allocated size, copy `chimera-audit.jsonl` to the host, rename with
date suffix, and reset the volume. The chain link to the previous
archive is preserved by writing a `chain_continuation.json` manifest
at the head of the new file.

---

## 3. Atlas (`packages/atlas`)

| Metric | Target | Notes |
|---|---|---|
| Sensitivity analysis p99 | < 5 s for N=10 drivers, M=1024 samples | Sobol decomposition; scales with samples × drivers |
| Bayesian inference p99 | < 100 ms per posterior | Stdlib-only; small tables |
| Replay bundle hash computation | < 50 ms per bundle | SHA-256 over canonicalized JSON |
| Audit chain verification | < 1 s per 1000 records | Linear scan + hash |

**Measurement surface:** add timing decorators to the public API
methods if not present; the `test_*` integration tests already
measure these (use those as the dev baseline).

---

## 4. Execution gate (`packages/execution`)

| Metric | Target | Notes |
|---|---|---|
| `submit_action` p99 (allow path) | < 50 ms | Governance + capability + audit write |
| `submit_action` p99 (deny path) | < 10 ms | Deny short-circuits before executor |
| Fail-closed latency (exception → DENY) | < 5 ms | Exception catch + result construction |
| Audit chain advance per call | exactly 1 | A successful call appends exactly one record |

**Invariant:** the gate MUST NEVER be a bottleneck for the
`DENY` path. Denials should be cheap to encourage fail-closed
behavior.

---

## 5. CLI (`packages/cli`)

| Metric | Target | Notes |
|---|---|---|
| Command startup → first byte | < 200 ms | Typer startup + urllib request |
| Per-command exit (no error) | < 1 s total | For a healthy gateway |
| Per-command exit (auth error) | < 100 ms | CLI fails fast if token is missing |

---

## 6. CI gates

| Gate | Target | Notes |
|---|---|---|
| `uv run pytest` (full) | < 30 s | Currently ~2.5 s; budget 12× for larger tests |
| `uv run mypy --strict` | < 60 s | Linear in source-file count |
| `uv run ruff check` | < 5 s | |
| `uv run ruff format --check` | < 5 s | |
| `docker compose build` (all 7 services) | < 10 min cold, < 2 min warm | Bounded by `uv sync` and `cargo build` |
| `docker compose up` → all healthy | < 90 s | `start_period: 5s` × max-retries 12 ≈ 60s |

If any CI gate exceeds its target by 2×, open an issue and treat as
regression.

---

## 7. Memory envelope (per container)

| Service | Working set (MB) | Notes |
|---|---|---|
| `api` | 200 | FastAPI + 16 packages imported |
| `docs-portal`, `proof-portal` | 100 | nginx + static files |
| `swr`, `atlas`, `arbiter-rlp` | 200 | Python service hosts |
| `genesis` | 50 | Rust binary, single-threaded |

**OOM behavior:** if any container OOMs, the docker daemon kills it
and the healthcheck fails. See
`docs/runbooks/INCIDENT_RESPONSE.md` §"Service X is unhealthy" for
the diagnostic.

---

## 8. What is NOT measured (yet)

- **Cross-service request latency** (the `api` → internal adapter hop)
- **Long-tail replay-bundle verification** (e.g., a 1M-record audit chain)
- **Multi-tenant isolation** (the system is single-tenant by design)
- **Network policy effectiveness** (no NetworkPolicy chart values yet)

These are deferred until a production measurement pass is authorized.

---

## 9. Source of truth

This document is a **target**, not a measurement. To convert it to
measured SLOs, capture the corresponding metrics in
`docs/audit/measurements-YYYY-MM-DD.md` and update the Target column
with the observed percentile + headroom.

The CI gate timing is the only thing already measured; see
`docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md` for the canonical
recording.
