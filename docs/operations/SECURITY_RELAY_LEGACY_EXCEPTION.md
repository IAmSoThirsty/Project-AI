# Security-Relay Legacy Artifact Exception (Owner-Approved, Immutable)

- **Decision date:** 2026-07-24 UTC
- **Owner:** Jeremy Karrick (sole repository owner)
- **Branch:** `agent/production-readiness-2026-07-19`
- **Status:** Approved — artifacts frozen, chain-invalid by design

## Decision

The three security-relay audit artifacts listed below are granted an owner-approved
**immutable legacy exception**. They remain byte-for-byte unchanged, remain chain-invalid
under the authoritative verifier, and are **not evidence of a valid relay chain**. No
regeneration, no supersession, and no verifier code change is authorized. This exception
resolves the open *disposition* blocker only; it does not make any chain valid.

## Scope

Exactly these three artifacts, pinned by raw-byte SHA-256 (computed 2026-07-24, before and
after verifier runs — identical both times):

| Artifact | Producers | Git status | Bytes | Lines | Line endings | SHA-256 |
| --- | --- | --- | --- | --- | --- | --- |
| `.project-ai/automation/audit/2026-07-11.audit.jsonl` | automation monitor agents (`heartbeat-reader`, `runaway-reader`, `lock-reader`, `phantom-reader`, …) | untracked, gitignored (`.gitignore:76` rule `.project-ai/`) | 234,165 | 731 | CRLF | `735B6519793967FED22BF796A7BE106AF17A5F7409A1FD73977D55B2C88CED10` |
| `.project-ai/automation/audit/2026-07-12.audit.jsonl` | automation monitor agents (same family) | untracked, gitignored (`.gitignore:76`) | 174,392 | 518 | CRLF | `0079F7DC03EF3659DE5ED74BF67CA120F021EC64D2A4DA2774CAB7FB0DA21E35` |
| `docs/internal/verification/taar-e2e-2026-07-10/audit/2026-07-10.audit.jsonl` | TAAR E2E reader/writer agents (`git-status-reader`, `governance-reader`, `*-report-writer`, …) | tracked, clean in `git status` | 32,869 | 95 | LF | `E3C7B7C4E82F3EED154A9EE8981905D70B09487D03D533F81C5FA24085DE27B6` |

Line counts are `splitlines()` counts; every file ends with a complete final line and a
trailing newline.

## Observed failure mode (Verified 2026-07-24)

Command and observed result for each artifact:

```
uv run python tools/verify_security_relay.py <artifact>
# stderr: FAIL: security relay chain invalid (1 events)
# exit code: 1
```

All three exited `1` with that exact stderr line. `(1 events)` means verification failed at
record 1, not that the file holds one event.

Mechanism: every parseable record in all three artifacts uses the legacy schema
`agent_id, classification, event_type, hash, message, run_id, status, task_id, timestamp`.
Zero records carry `previous_hash` or `event` (confirmed by a per-line structural scan of all
three files). `AppendOnlyAuditRelay.verified_snapshot()`
(`packages/security/src/security/bridge.py:62-84`) requires the first record's
`previous_hash` to equal the 64-zero genesis hash; with the key absent, verification fails at
record 1.

Additional structural findings from the per-line `json.loads` scan:

- `2026-07-11.audit.jsonl`: 692 of 731 lines parse; **39 lines are corrupted interior lines**
  (unterminated strings / extra data), e.g. lines 39, 45, 53, 54, 56.
- `2026-07-12.audit.jsonl`: 497 of 518 lines parse; **21 corrupted interior lines**, e.g.
  lines 25, 68, 96, 151, 279.
- `2026-07-10.audit.jsonl` (TAAR): all 95 lines parse cleanly; zero corruption.

Correction to earlier reporting: the prior handoff described "truncated final records" in the
two automation artifacts. That did not reproduce — the final line of each file is complete.
The observed defect is interior line corruption plus the legacy schema, as recorded above.

## Verifier boundary

`AppendOnlyAuditRelay.verify()` is authoritative only for artifacts produced by
`AppendOnlyAuditRelay.append()`, which writes `event` / `previous_hash` / `timestamp` and a
canonical SHA-256 body `hash` chained from the 64-zero genesis value. The three artifacts
above predate that schema and are outside the verifier's domain of validity. The passing unit
tests (`tools/tests/test_verify_security_relay.py`, `tools/tests/test_verify_audit_chain.py`)
validate the current implementation; they say nothing about these legacy artifacts.

## Why regeneration was rejected

1. `docs/runbooks/INCIDENT_RESPONSE.md` (lines 72-73) prohibits "regenerating" a chain to
   clear a verification error — a regenerated chain would erase the tamper-evidence property
   the relay exists to provide.
2. Regenerating compliant JSONL from legacy records would fabricate provenance: the new
   `previous_hash` chain would attest to an append-order history that was never actually
   recorded.
3. The TAAR artifact's exact bytes (sha256 `e3c7b7c4…`, 32,869 bytes) are already pinned
   inside the sealed evidence bundle
   `docs/internal/verification/taar-e2e-2026-07-10/bundle.json` — the bytes are frozen,
   independently corroborated evidence.

## Explicit non-claims (fail-closed)

- This exception does **not** make any relay chain valid.
- It satisfies **no** prerequisite of `tools/verify_pre_deployment.py`; all nine externally
  controlled prerequisites remain unresolved and fail-closed.
- The repository remains **not production-ready**; deployment and publication remain
  prohibited.

## Tamper-detection / future re-verification

Re-verify the frozen state at any time:

```powershell
Get-FileHash -Algorithm SHA256 .project-ai\automation\audit\2026-07-11.audit.jsonl
Get-FileHash -Algorithm SHA256 .project-ai\automation\audit\2026-07-12.audit.jsonl
Get-FileHash -Algorithm SHA256 docs\internal\verification\taar-e2e-2026-07-10\audit\2026-07-10.audit.jsonl
uv run python tools/verify_security_relay.py <each artifact>   # expected: exit 1
```

Expected results: the three SHA-256 values in the scope table, and verifier exit `1` for each.
**Any hash mismatch, or an unexpected exit `0`, is a tamper/regeneration alarm** requiring
owner investigation per `docs/runbooks/INCIDENT_RESPONSE.md` — exit 0 on these artifacts
could only mean the bytes were rewritten.

Note: instantiating the verifier calls `Path.touch()` on the artifact
(`packages/security/src/security/bridge.py:35`), so mtime may change on each run; content
bytes never do (proven by identical pre-/post-run hashes on 2026-07-24).

## Final report

- **Mode:** owner disposition recording (documentation only)
- **Created:** `docs/operations/SECURITY_RELAY_LEGACY_EXCEPTION.md` (this file)
- **Modified:** none by this file; companion updates recorded in
  `PRODUCTION_READINESS_STATUS.md`, `PRODUCTION_HANDOFF_REPORT.md`, `CONTINUITY_MAP.md`
- **Deleted:** none
- **Verified:** three SHA-256 pins (pre/post verifier, identical); three verifier runs exit 1
  with `security relay chain invalid (1 events)`; per-line structural scan of all three
  artifacts; git identity (`git ls-files --error-unmatch` for the tracked artifact,
  `git check-ignore -v` for the two gitignored artifacts)
- **Failed (expected and documented):** the three chain verifications — exit 1 by design
  under this exception
- **Not verified:** nothing in scope of this record
- **Safe to continue:** yes for local non-deployment work; no for production deployment or
  publication
