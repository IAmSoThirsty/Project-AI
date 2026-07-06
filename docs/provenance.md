# Provenance

## What provenance covers

This document describes how to verify that:
1. The legacy source was frozen correctly before the rebuild.
2. Papers and reference documents match their declared SHA-256 hashes.
3. Merge operations (SWR, Atlas duplicates) are deterministic and reproducible.
4. Governance artifacts carry valid sovereign signatures.

## Frozen history chain (Stage -1.5)

The rebuild began with a complete SHA-256 chain-linked snapshot of the legacy
repository (`T:\00-Active\Project-AI-main`) stored in `docs/internal/frozen-history/`.

Each record contains:
- File path and SHA-256 hash
- Link to the previous record's hash (chain)
- Timestamp

### Verify

```bash
python tools/verify_frozen_history.py
```

Expected output:
```
Verified 2,264/2,264 chain links.
All hashes match.
```

If any record fails, the chain is broken — indicating either tampering or an
unexpected modification to the frozen-history directory.

## Paper corpus (Stage -1)

137 reference papers were ingested and SHA-256 verified. The manifest is at:
- `docs/reference/INGEST_MANIFEST.md` — all ingested files with hashes
- `docs/reference/INGEST_SKIPPED.md` — files excluded (reason documented)
- `docs/reference/DROPPED_FILES_MANIFEST.md` — files removed from the corpus
- `docs/reference/ORPHAN_PAPERS.md` — papers without a DOI match

DOI-to-file mappings are in `docs/reference/DOI_REGISTRY.md`.

Verify any paper:
```bash
python tools/ingest_papers.py --verify-only
```

## SWR and Atlas merge provenance (Stage 4)

The deterministic merge of SWR and Atlas duplicate sources produced a machine-
readable report:
- `docs/internal/STAGE_4_MERGE_REPORT.json` — merge decisions, hash comparison,
  and determinism proof for each file pair

Any re-run of the merge tool must produce the same report (byte-for-byte
identical output for the same inputs).

## Import reports (Stages 4.7–4.8)

Web security assets and governance framework assets were imported with
full hash verification:
- `docs/internal/STAGE_4_7_4_8_IMPORT_REPORT.json` — per-file import
  decisions and provenance hashes

## Genesis evidence chain

The genesis emitter produces an append-only SHA-256 linked record of governance
events. Each emitted record contains:

```json
{
  "sequence": 1,
  "timestamp": "...",
  "content_hash": "sha256:...",
  "previous_hash": "sha256:...",
  "record_hash": "sha256:..."
}
```

`previous_hash` is `0000...0000` (64 zeros) for the genesis record and links
to the prior record's `record_hash` for all subsequent records.

Verify the genesis emitter produces the same record for the same input:
```bash
echo '{"content":"test","authority":"operator"}' \
  | ./target/release/project-ai-genesis-emitter \
    0000000000000000000000000000000000000000000000000000000000000000
```

Identical inputs always produce identical `record_hash` output (deterministic).

## Rebuild ledger

The complete rebuild execution ledger is at `docs/internal/REBUILD_EXECUTION_PLAN.md`.
Each stage has a corresponding `STAGE_N_ACCEPTANCE.md` in `docs/internal/` that
records the exact evidence gathered at gate time.
