# Production Documentation Gap Audit

**Status:** DISCOVERY + DRIVE-PLAN (envelope)
**Date:** 2026-06-30
**Authority:** User directive ("get the job done and fill in the gap")
**Scope:** Operator-facing documentation only (not internal stage records — those are exhaustive)
**Method:** Read every operator-facing doc, every API route, every CLI command, every package README, then enumerate the gap to a clean cold-operator install.

---

## 0. What is already in good shape (NOT a gap)

The repo already has, and is not lacking:

| Doc | Location | State |
|---|---|---|
| Operator guide (prereqs, all commands, service endpoints) | `docs/operator.md` | **SOLID** — 100+ lines, env vars, all services |
| Architecture (dep graph, all 12 packages, 7 services, governance model) | `docs/architecture.md` | **SOLID** — ASCII dep graph, package table, app table |
| Security (fail-closed gate, capability tokens, container hardening) | `docs/security.md` | **SOLID** — full trust model, container hardening table |
| Provenance (frozen history SHA-256, paper ingest) | `docs/provenance.md` | **SOLID** — all verification commands |
| Pre-deployment checklist (gates, evidence) | `docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md` | **SOLID** — 140 lines, all gates listed |
| Dev stack runbook | `docs/runbooks/DEVELOPMENT_STACK_RUNBOOK.md` | **SOLID** — 115 lines, start/verify/stop |
| `.env.example` (token, URL, smoke flag) | `.env.example` | **SOLID** |
| 145 reference papers with SHA-256 provenance | `docs/reference/` | **SOLID** |
| 50+ internal stage acceptance records | `docs/internal/STAGE_*_ACCEPTANCE.md` | **SOLID** (internal, not operator-facing) |
| App READMEs (desktop, services, android) | `apps/*/README.md` | **SOLID** for those 3 |

I overstated the gap in the previous turn. The above are real and good.

---

## 1. What is genuinely missing for production deployment

A cold operator (someone with `git clone` access and zero context) cannot
deploy this repo without consulting source. Specifically:

### 1a. **README.md is not a deployment entry point**

- Current `README.md` is 105 lines of project vision, status, and pointers.
- It does NOT say "here is the 5-command install/deploy sequence."
- A new operator would read it and have to dig into `docs/operator.md`.
- **Fix:** add a top-level "Quickstart (5 commands from fresh clone to deployed dev stack)" section to `README.md` that points to `docs/operator.md` for the full version.

### 1b. **No API reference (per-endpoint documentation)**

The API has 8 routes. None of them are documented as a reference:

| Route | Method | Auth | Purpose | Body | Response |
|---|---|---|---|---|---|
| `/health/live` | GET | public | liveness | — | `{status, version}` |
| `/dois` | GET | public | DOI catalog | — | `{dois: [...]}` |
| `/replay/status` | GET | public | canonical replay status | — | `{replay, ...}` |
| `/atlas/status` | GET | public | atlas subordination notice | — | `{subordination_notice}` |
| `/audit` | GET | bearer | last N audit records | `?limit=` | `{events: [...]}` |
| `/chimera/verdict` | POST | bearer | relay verdict | `{action_id, verdict, source}` | `{event, hash}` |
| `/chimera/canary` | POST | bearer | relay canary hit | `{canary_value, context}` | `{event, hash}` |
| `/atlas/sludge` | POST | bearer | generate SS-only narrative | `{rs_snapshot, archetypes?}` | `{hash, narrative}` |

- **Fix:** `docs/api/API_REFERENCE.md` with per-route table, curl examples, error responses (401/422/503).

### 1c. **No CLI reference**

The CLI has these commands:

| Command | Auth | Purpose |
|---|---|---|
| `project-ai version` | none | Print version |
| `project-ai health` | none | GET `/health/live` |
| `project-ai dois` | none | GET `/dois` |
| `project-ai replay` | none | GET `/replay/status` |
| `project-ai atlas-status` | none | GET `/atlas/status` |
| `project-ai atlas-sludge` | bearer | POST `/atlas/sludge` |
| `project-ai audit` | bearer | GET `/audit` |
| `project-ai verdict` | bearer | POST `/chimera/verdict` |
| `project-ai canary` | bearer | POST `/chimera/canary` (via `--value-file`) |

- **Fix:** `docs/cli/CLI_REFERENCE.md` with per-command table, examples, env vars, exit codes.

### 1d. **Per-package READMEs are stubs (16 packages, 11 are 6-9 lines)**

```
api: 27 lines  (good)
arbiter: 8 lines  (stub)
atlas: 15 lines  (acceptable, has content)
capability: 6 lines  (stub)
cerberus: 31 lines  (good)
cli: 21 lines  (acceptable)
companion: 6 lines  (stub)
execution: 6 lines  (stub)
governance: 16 lines  (acceptable)
hydra_50: 29 lines  (good)
kernel: 7 lines  (stub)
rlp: 8 lines  (stub)
security: 9 lines  (stub)
swr: 6 lines  (stub)
tarl: 24 lines  (acceptable)
temporal: 36 lines  (good)
```

- **Fix:** expand each stub README to ~15-25 lines with: purpose, key public API, dependency contract (downward-only), when-to-use, link to source-of-truth doc.

### 1e. **No architecture diagram (visual)**

The dep graph is in ASCII. A new operator needs to see the layered structure. Two options:
- Add a Mermaid diagram to `docs/architecture.md` (renders in GitHub + GitLab)
- Or commit an SVG to `docs/architecture/dep-graph.svg`

**Fix:** add a Mermaid `graph TD` block in `docs/architecture.md` after the ASCII table.

### 1f. **No incident response runbook (production only — dev runbook exists)**

`docs/runbooks/DEVELOPMENT_STACK_RUNBOOK.md` covers happy-path dev. Production needs:
- "Service X is unhealthy — what do I check?"
- "Audit chain is broken — what's the recovery?"
- "Capability token rejected — what's the diagnostic?"
- "Compose service won't start — what's the order of operations?"

**Fix:** `docs/runbooks/INCIDENT_RESPONSE.md` with the 5-7 most likely incidents, each with: symptom, diagnostic command, root cause, fix, postmortem template.

### 1g. **No Helm/K8s deploy guide**

`helm/project-ai/` exists. `docs/operator.md` says "helm template" for validation only. There is no:
- "How to install in a real cluster"
- "How to set the bearer token as a secret"
- "How to expose the API"

**Fix:** `docs/deployment/HELM_DEPLOY.md` with: prerequisites, namespace, secret creation, install command, post-install verification, uninstall.

### 1h. **No "Production Deploy" runbook (separate from Pre-Deployment Checklist)**

`PRE_DEPLOYMENT_CHECKLIST.md` is the gate. But there's no "what to actually do to deploy." Cold operator still has to read compose.yaml + Dockerfile + operator.md.

**Fix:** `docs/deployment/PRODUCTION_DEPLOY.md` with the concrete sequence: image build, registry push, environment setup, deploy command, smoke test, rollback procedure.

### 1i. **No performance / SLO doc**

No documented targets for:
- API p99 latency
- Audit write throughput
- Atlas replay time
- Memory envelope per service

**Fix:** `docs/operations/PERFORMANCE_SLOS.md` (even if targets are "TBD pending measurement") so operators know what to monitor.

### 1j. **No environment variable reference**

`.env.example` exists but is a flat list. There's no doc that says:
- What each env var does
- What type / default / required-flag
- Which service consumes it

**Fix:** expand `docs/operator.md` (or new `docs/deployment/ENVIRONMENT_VARIABLES.md`) with the full env-var table.

---

## 2. Drive plan (per Thirstys standards: ≤5 files per wave)

The above 10 gaps fit in **3 staged commits**, each gated green:

### Wave 1: Operator-facing references (3 files new, 1 file modified)

- `docs/api/API_REFERENCE.md` (NEW) — per-route table, curl examples, error responses
- `docs/cli/CLI_REFERENCE.md` (NEW) — per-command table, examples, exit codes
- `docs/runbooks/INCIDENT_RESPONSE.md` (NEW) — 5-7 most-likely incidents with diagnostics
- `README.md` (MODIFY) — add "Quickstart (5 commands)" section

**Risk:** Low — pure documentation, no code touched, no API surface change.
**Effort:** ~400-600 lines of new doc.

### Wave 2: Per-package README expansion (16 files modified)

- Expand each stub README (11 packages) to 15-25 lines
- Update the 5 acceptable/good ones only if they now link to the new API/CLI/incident docs

**Risk:** Low — README changes only.
**Effort:** ~150 lines of new content across 11 files.

### Wave 3: Deployment + observability docs (4 files new, 2 files modified)

- `docs/deployment/HELM_DEPLOY.md` (NEW)
- `docs/deployment/PRODUCTION_DEPLOY.md` (NEW)
- `docs/deployment/ENVIRONMENT_VARIABLES.md` (NEW)
- `docs/operations/PERFORMANCE_SLOS.md` (NEW) — even with TBD targets
- `docs/architecture.md` (MODIFY) — add Mermaid diagram
- `docs/operator.md` (MODIFY) — link to all the new docs

**Risk:** Low — documentation only.
**Effort:** ~500-800 lines of new doc.

---

## 3. What is NOT in scope (out-of-scope for this pass)

- **Source code integration** (6 scenario engines, SWR, atlas staging residue, integrations) — separate work, separate decisions
- **Internal stage records** (already exhaustive)
- **Reference papers** (already complete with SHA-256)
- **CI workflow docs** (workflow files exist; whether they need prose docs is a separate audit)

---

## 4. Acceptance criteria (per wave)

Each wave ships only if:

- All 4 canonical gates green via `uv run` (pytest, mypy --strict full scope, ruff check, ruff format --check)
- Working tree clean
- Local + origin in sync after each commit
- One commit per wave with semantic message
- A short `STAGE_*_WAVE*_ACCEPTANCE.md` per wave capturing the diff

**NO code in these waves. NO source touched. NO pytest changes (test count stays at 1347).**

---

## 5. Honest disclosure

This is **discovery + drive-plan only**. NO doc files have been written
beyond this envelope. The 1347-test baseline is preserved. Working tree
clean at HEAD `c4e4fb3f`.

The previous turn overstated the gap — the repo has real operator
docs, not stubs. This audit corrects that. The remaining gaps are
narrower and more specific.
