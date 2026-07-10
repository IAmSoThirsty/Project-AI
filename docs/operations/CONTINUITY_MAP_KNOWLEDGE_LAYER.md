# Operational Continuity Map — Knowledge-Aware Layer

> Per Thirsty's Standard v3 §19–24. Truthful record of actual work, not intent.
> Companion initiative; does not replace `CONTINUITY_MAP.md` (simulation engines).

## Task

Integrate an external reference corpus (`T:\07-Research\Hatter Information`,
computers / ethical-hacking / technology) as a **knowledge-aware** layer Project-AI
consults when making decisions — advisory, not a search surface.

- **Date:** 2026-07-08
- **Branch:** `chore/warning-cleanup-utc-artifacts`
- **Workspace:** `T:\00-Active\Project-AI-Beginnings`
- **Mode (v3 §12/§14):** module + governance-integration (not a production deployment)
- **Safe to continue:** yes

## Files created

- `packages/knowledge/` — new uv-workspace package:
  `pyproject.toml`, `README.md`, `PRUNE_LOG.md`,
  `src/knowledge/{__init__,py.typed,models,classify,chunk,embedding,index,store,ingest,extract,binding}.py`,
  `tests/{test_classify,test_chunk,test_embedding,test_index,test_store,test_ingest,test_extract,test_binding}.py`
- `packages/kernel/src/kernel/knowledge.py` — `KnowledgeSource` Protocol + `KnowledgePassage`
- `packages/governance/src/governance/knowledge_governor.py` — `KnowledgeAwareGovernor`
- `packages/governance/tests/test_knowledge_governor.py`
- `tests/test_knowledge_aware_governance_integration.py`
- `docs/operations/CONTINUITY_MAP_KNOWLEDGE_LAYER.md` (this file)

## Files modified

- `packages/kernel/src/kernel/__init__.py` — export `KnowledgePassage`, `KnowledgeSource`
- `packages/governance/src/governance/__init__.py` — export `KnowledgeAwareGovernor`
- `pyproject.toml` — workspace member `packages/knowledge`, dep + `[tool.uv.sources]`, `knowledge` extra
- `.gitignore` — ignore `data/knowledge/`
- `uv.lock` — add `model2vec` 0.8.2 + deps (no torch / no onnxruntime)

## Files deleted (external source folder; user-authorized)

- `Cash_App_September_2025_Account_Statement_*.pdf` — personal record (v3 §9 approved).
  SHA-256 `ae4f76b4a499669ead7ac01665866c00867f0d6f522306d20d10607984f7e90d`.
- `youtube.pdf` — image-only PDF, un-ingestable. SHA-256 `5d57c14a…e6ded`.
  Audit: `packages/knowledge/PRUNE_LOG.md`. Personal-doc scan of remaining 288 PDFs: 0 hits.

## Commands run + results (evidence, v3 §11)

- `uv lock` → Resolved 135 packages; added model2vec 0.8.2 (no torch/onnxruntime). **Verified.**
- `uv sync --all-extras --all-packages` → installed. **Verified.**
- `pytest packages/knowledge packages/governance packages/kernel tests/test_knowledge_aware_governance_integration.py`
  → **456 passed**. **Verified.**
- `mypy packages/knowledge/src/knowledge packages/kernel/src/kernel packages/governance/src/governance`
  → Success, no issues (32 files). **Verified.**
- `ruff check` + `ruff format --check` → clean. **Verified.**
- Ingestion smoke (`--limit 8`, model2vec) → 8 docs, 4641 chunks. **Verified.**
- Full ingestion (`knowledge.ingest`, model2vec, whole corpus) → **Verified**:
  270 docs ingested, 42 skipped, **197,526 chunks**; index `data/knowledge/{vectors.npy 202MB,
  chunks.jsonl 260MB, meta.json}`; manifest `packages/knowledge/KNOWLEDGE_MANIFEST.md`.
  Sensitivity split: educational 171 / dual_use 70 / offensive 29.
  First attempt **Failed** on a malformed PDF (root-object error escaped the extractor);
  fixed (`extract.py` guards page access) + regression test. Re-run skipped all 13 malformed/
  encrypted PDFs cleanly (incl. the exact file that crashed the first run) — fix Verified in prod.
- End-to-end through the real index (`get_knowledge_store` → `KnowledgeAwareGovernor` →
  `ExecutionGate`) → **Verified**: "keylogger/bypass AV" retrieved Gray Hat Hacking / Hacking
  Exposed (dual_use/offensive) → ESCALATE, execution.blocked, executor NOT called; "python
  decorators" and "firewall/CCNA" retrieved educational books → ALLOW → executed once each.

## Verification status (v3 §10 labels)

- Corpus prune + audit: **Verified.**
- Package code, types, lint, unit + integration tests: **Verified** (456 passed).
- Knowledge-aware governance mechanism (offensive → ESCALATE → execution.blocked, executor not
  called; benign → ALLOW → executes once): **Verified** by
  `tests/test_knowledge_aware_governance_integration.py` (synthetic) AND against the real
  197,526-chunk index (3 live cases through the gate).
- Full semantic index over the real corpus: **Verified** (270 docs / 197,526 chunks).
- End-to-end query through the gate against the *real* built index: **Verified**.

## Governance-claim honesty (v3 §29–§32)

The gating is **proven in isolation, not wired live.** The `KnowledgeAwareGovernor` demonstrably
blocks an offensive-topic action through the real `ExecutionGate` in the integration test
(enforced denial, fail-closed, audit event). It is **advisory** (votes ALLOW/ESCALATE, never DENY,
never overrides the user). It is **not** added to any live `GovernanceEngine` construction site by
default; activation is opt-in via `knowledge.build_knowledge_governor()`, which returns `None` when
no index exists. **Do not claim Project-AI currently gates decisions on this corpus in production.**

## Risks (v3 §7)

- **Risk:** knowledge-gating inactive unless a composition site wires the governor.
  **Action:** provided opt-in `build_knowledge_governor()`; live wiring deferred pending user decision.
- **Risk:** deployed runtime has no index provisioning (index is gitignored, machine-local).
  **Action recommended:** bake index into image or mount a volume; version it.
- **Risk:** `.doc` (17) / `.ppt` (4) formats unsupported → skipped (logged in manifest). Best-effort scope.

## Decisions

- Semantic embeddings via **model2vec static vectors** (torch-free, deterministic, offline) —
  heeds the documented sentence-transformers/Windows-crash removal.
- **No raw corpus or index in git** (copyright + size); provenance committed as
  `packages/knowledge/KNOWLEDGE_MANIFEST.md`.
- Dependency-inverted seam: governance depends only on the kernel `KnowledgeSource` interface.

## Remaining / next recommended action

1. ~~Full ingestion + index/manifest~~ — **Done, Verified** (270 docs / 197,526 chunks).
2. ~~End-to-end query through the gate against the real index~~ — **Done, Verified**.
3. Decide whether to wire `build_knowledge_governor()` into a live engine site (currently opt-in,
   not active by default) — **Pending user decision**.
4. Address deploy-time index provisioning (bake into image or mount volume; version it) before any
   production-readiness claim — **Pending**.
5. Optional: improve `.doc`/`.ppt` extraction (21 skipped) and OCR for image-only PDFs (6 skipped).
6. Not yet committed — working tree changes listed in git status; commit on user request.
