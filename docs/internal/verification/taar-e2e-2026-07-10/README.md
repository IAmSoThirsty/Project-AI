# TAAR E2E Verification Bundle — 2026-07-10

Portable, third-party-verifiable proof of the TAAR (Thirsty's Active
Agent Runner) end-to-end run executed on 2026-07-10 against
`packages/taar` at Beginnings commit `e53bf2e7` (upstream source SHA
`7b51966317f64c7b1fe277e0db0935c5e460704c`).

## What this proves

- 44 registered agents, 0 registry validation errors; 21 readers and
  22 writers driven through the governed executor, plus the
  quarantine-class phantom pass (see `bundle.json` → `runs`).
- 22 hash-sealed evidence bundles, every embedded `evidence_hash`
  recomputable from the artifact itself.
- 20 writer outputs, each citing a `source_evidence_hash` that
  resolves to a bundled evidence artifact.
- 95 append-only audit records, each individually sealed; the 3
  admission denials (fail-closed policy behavior, not failures) are
  extracted with their reasons and seals in `bundle.json` →
  `audit.denials`.
- Redaction held: the planted fake `ghp_` token (identified only by
  its SHA-256) appears in **zero** TAAR-produced artifacts; the secret
  report carries only the redacted fragment `ghp_...7Ii8`.
- Repository-cleanliness receipts for both the Beginnings tree and the
  read-only upstream source repo.

## Contents

| Path | Contents |
|---|---|
| `bundle.json` | Master machine-readable manifest: registry snapshot hashes, full facility manifest, evidence/output/report hashes, audit chain head, denials, run table, redaction assertions, invocation metadata, cleanliness receipts |
| `SEAL.json` | SHA-256 of every bundle file + a head hash over the sorted manifest |
| `registry/` | Byte-exact snapshot of the 5 registry YAMLs that governed the run |
| `evidence/<agent>/<run>/evidence.yaml` | The 22 sealed evidence bundles |
| `outputs/<agent>/<run>/output.yaml` | The 20 writer output records |
| `reports/`, `digests/` | The 18 Markdown reports + 2 digests, byte-exact |
| `audit/` | The append-only audit JSONL, byte-exact |
| `harness/taar_e2e.py` | The exact harness that drove the swarm (its SHA-256 is recorded in `bundle.json` → `invocation.harness_sha256`) |
| `harness/verify_bundle.py` | Standalone verifier (Python 3.12+, PyYAML only) |
| `harness/build_bundle.py` | How `bundle.json` and all hashes were computed from the facility (for audit; not re-runnable without the facility) |
| `harness/seal_bundle.py` | How `SEAL.json` was produced |

The planted secret input file (`config_backup.py`) is deliberately NOT
included; it is identified by SHA-256 in `bundle.json` → `redaction`.

## How to verify (no access to this repo required)

```
python harness/verify_bundle.py [path-to-this-directory]
```

The verifier recomputes: (1) every file hash against `SEAL.json` and
the seal head; (2) every evidence hash from canonical JSON (sorted
keys, compact separators, `evidence_hash` field removed — the same
construction TAAR uses); (3) output→evidence linkage; (4) every audit
record seal and the chain head; (5) the redaction assertions. Exit
code 0 means every section passed.

## How to reproduce the run

1. Check out Project-AI Beginnings at commit `e53bf2e7` or later;
   `uv sync --frozen --all-extras --all-packages`.
2. Run `harness/taar_e2e.py` (adjust the two absolute paths at the
   top), then the phantom pass and Workflow Guardian commands listed
   in `bundle.json` → `invocation.passes`.
3. Expect identical *structure*: same agent set, same
   statuses/denial reasons, same classifications, same redaction
   property, and `workflows scan` exiting 1 on the dangerous example's
   critical findings. Run-specific values (run IDs, timestamps, and
   therefore evidence/output/audit hashes) will differ by design —
   evidence bundles embed timestamps.

## Honest notes

- The audit **chain head** is computed by this bundle over the ordered
  per-record seals (`h0 = 64×'0'; h_i = sha256(h_{i-1} + seal_i)`).
  TAAR itself seals each record individually but does not chain them;
  the chain is a bundle-level construction, documented so it can be
  recomputed independently.
- The 3 denials are TAAR's fail-closed admission working as designed:
  two writers were refused SECRET evidence without a declared
  secret-handling task, and the phantom writer was refused before its
  reader had produced evidence (it succeeded after the phantom pass).
- `taar workflows scan` exiting 1 is by design (critical findings
  present in the planted dangerous workflow); it also surfaced real
  findings in this repo's own `ci.yaml`/`publish.yaml`.
- This directory is byte-preserved evidence: the repo's ruff, ruff
  format, mypy, and whitespace/EOF pre-commit hooks all exclude
  `docs/internal/verification/` (same treatment as `packages/_staging`
  and the other reference dirs) so the sealed artifacts — including the
  exact harness that ran and the Markdown hard-break trailing spaces —
  stay hash-stable rather than being rewritten by tooling.
