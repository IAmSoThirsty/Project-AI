# Stage -1 — Paper Ingest + Downloads Copy — Acceptance

**Status:** COMPLETE
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

## What Was NOT Done (deferred to later stages)

- Did NOT commit anything to git (per user directive — only commit when safe)
- Did NOT yet wrap arbiter_gov/rlp as proper installable Python packages (Stage 4.5/4.6)
- Did NOT split OMPT.md into website files (Stage 4.7)
- Did NOT integrate governance framework 0722 (Stage 4.8)
- Did NOT make old repo T:\Project-AI-main read-only (Stage 3)
- Did NOT run the wiki scrape (separate sub-stage before Stage 0)

## Ready For

Stage 0: Bootstrap (T:\Project-AI-Beginnings\) — initial commit + root config files.