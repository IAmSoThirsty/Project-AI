# Stage -1 — Paper Ingest + Downloads Copy — Acceptance

**Status:** COMPLETE (evidence backfill verified 2026-06-20)
**Date:** 2026-06-19
**Stage:** -1 of 26 (preceded by Stage -1.5 Frozen History)

## Deliverables

### 1. Frozen-history file (from Stage -1.5)
- `docs/internal/frozen-history/PROJECT-AI_FROZEN_HISTORY.md`
- 2.37 MB, 2264 commit sections, chain INTACT (verified)
- Tool: `tools/freeze_history.py` + `tools/verify_frozen_history.py`

### 2. Paper corpus (from `Documents\Thirsty's Projects LLC\Project-AI Papers\`)
- **137 files copied** (95 root + 50 Drafts + 5 Final Papers + Zenodo), all byte-identical to source (verified by SHA-256 round-trip)
- 6 files skipped (security/sensitive/non-project artifacts)
- Layout:
  - `docs/reference/papers/` — 95 root files
  - `docs/reference/drafts/` — Drafts/ + Final Papers/
  - `docs/reference/zenodo/` — Zenodo records
  - `docs/reference/attestations/` — 3rd-party AI attestations (chatgpt/claude/gemini/grok)
  - `docs/reference/legal/` — patent/portfolio/legal docs
- Manifest: `docs/reference/INGEST_MANIFEST.md`
- Skipped: `docs/reference/INGEST_SKIPPED.md`

### 3. Canonical Charter (from `Downloads\`)
- `docs/reference/AGI_Charter_for_Project-AI_v2_3.pdf` (576 KB, v2.3 dated Jun 17 — canonical)
- Supersedes: v2.2 (Downloads) and v1.0 (Papers/) — both omitted by design

### 4. Operator-side governance drafts (from `Downloads\`)
- `packages/arbiter/src/arbiter/arbiter_gov.py` (40 KB, 6 primitives)
- `packages/arbiter/tests/test_arbiter_gov.py` (12 KB, **12/12 tests pass** verified)
- `packages/rlp/src/rlp/rlp.py` (64 KB, RLP v4 I1-I12, imports clean)
- Status: **EXPERIMENTAL/DRAFT** — these will be wrapped into proper packages in Stages 4.5/4.6

### 5. Wiki, publication, and disposition evidence
- `docs/index/wiki-pointer-map.md` — all 192 legacy wiki files classified
- `docs/internal/vault-stub-index.md` — pointer-only vault files retained as evidence
- `docs/reference/PUBLICATION_TIMELINE.md` — source-linked timeline
- `docs/reference/DOI_REGISTRY.md` — source-linked 21-publication registry
- `docs/audit/wiki-vs-papers-discrepancies.md` — DOI sets agree 21/21
- `docs/reference/GENESIS.md` — owner-defined three-part Genesis composite
- `docs/reference/ORPHAN_PAPERS.md` — submitted-paper status and hashes
- `docs/reference/MERGE_PROVENANCE.md` — byte-hash provenance inventory
- `docs/reference/DROPPED_FILES_MANIFEST.md` — all 5,276 tracked legacy paths classified without deletion
- Generator: `tools/backfill_stage_minus_one.py` (repeat-run output is byte-deterministic)

## Skipped Files (with reasons)

| File | Reason |
|---|---|
| `Microsoft.Services.Store.winmd` | Non-Project Windows Store artifact |
| `namecheap-order-201285708.pdf` | Personal receipt |
| `namecheap-order-202585328.pdf` | Personal receipt |
| `pull-secret.txt` | Contains Kubernetes pull secret — DO NOT COMMIT |
| `security_items_gh_IAmSoThirsty.csv` | Security audit data — sensitive |
| `Unity_lic.alf` | Proprietary Unity license — redistribution rights unclear |

## Acceptance Checks

- [x] All copied files byte-identical to source (137/137 SHA-256 verified)
- [x] No file > 18 MB (largest is `Thirstysystems Technical Showcase Website Research Report.pdf` at 17.7 MB, well under GitHub's 100 MB/file limit)
- [x] Frozen-history chain intact (2264/2264 sections verified by `verify_frozen_history.py`)
- [x] arbiter_gov test suite passes (12/12)
- [x] rlp.py imports without errors
- [x] Charter v2.3 is canonical (v2.2 and v1.0 NOT copied)
- [x] Skipped files have documented reasons in `INGEST_SKIPPED.md`
- [x] Legacy wiki indexed (192/192 files)
- [x] Wiki and text-readable corpus DOI sets agree (21/21)
- [x] Legacy tracked paths classified (5,276/5,276)
- [x] Stage -1 evidence generator is deterministic across repeated runs
- [x] Legacy HEAD, status, and dirty-file hashes unchanged during evidence generation

## What Was NOT Done (deferred to later stages)

- Did NOT yet wrap arbiter_gov/rlp as proper installable Python packages (Stage 4.5/4.6)
- Did NOT split OMPT.md into website files (Stage 4.7)
- Did NOT integrate governance framework 0722 (Stage 4.8)
- Did NOT alter permissions or files in T:\00-Active\Project-AI-main; Stage 3 records the soft-freeze boundary

## Ready For

Stage 2: Root pyproject and uv workspace. Stage 0/1 are accepted in separate evidence records without rewriting history.
