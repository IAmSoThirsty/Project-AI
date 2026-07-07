# Audit Log

Tamper-evident, hash-chained audit log for Project-AI's
execution-governance spine.

## What this is

A minimal, dependency-free audit log that:

- Records events as immutable dataclasses (`AuditEvent`)
- Chains events with SHA-256 hashes — each event's
  `event_hash` covers the JSON-serialized payload plus the
  `previous_hash` of the prior event
- Detects tampering: any modification to any past event
  invalidates the chain from that point forward
- Persists to JSONL files atomically (`FileAuditLog`)
- Verifies the full chain in O(n) time (`verify_chain()`)

## Public surface

  - `AuditEvent` — the event dataclass
  - `AuditLog` — in-memory append-only log
  - `FileAuditLog` — file-persisted `AuditLog`
  - `AuditVerification` — chain verification result
  - `AuditWriteError` — raised on persistence or chain
    integrity failures
  - `GENESIS_HASH` — the `"0" * 64` anchor for the first
    event in a chain

## Run it

```python
from audit import AuditLog, FileAuditLog
from datetime import datetime, timezone

# In-memory log
log = AuditLog()
log.append_event(
    decision_id="dec-1",
    actor_id="actor-1",
    action="test.echo",
    resource="resource-1",
    result="allow",
    reason="test allowed",
    event_type="decision",
    timestamp=datetime.now(timezone.utc),
)
assert log.verify_chain().valid is True

# File-persisted log
file_log = FileAuditLog("audit.jsonl")
file_log.append_event(
    decision_id="dec-2",
    actor_id="actor-2",
    action="test.echo",
    resource="resource-2",
    result="allow",
    reason="test allowed",
    event_type="decision",
    timestamp=datetime.now(timezone.utc),
)

# Reload and verify
reloaded = FileAuditLog("audit.jsonl")
assert reloaded.verify_chain().valid is True
```

## Port provenance

This package was recovered from
`T:\08-Archive\Project-AI-Canonical\project_ai\audit\chain.py`
(dated 2026-06-17) during the Phase B recovery. The
original file was 172 lines; the port preserves it 1:1
because it is the canonical implementation referenced by
`docs/SOURCE_BOUNDARY.md` and `docs/SALVAGE_LEDGER.md` as
"RAW VERIFIED" — the only file the archive's salvage ledger
explicitly authorizes as a source.

The only changes from the source:
  - Module path: `project_ai.audit.chain` → `audit.chain`
    (workspace-member-name, not `project_ai_audit`)
  - Imports rewritten: `from project_ai.*` → `from audit.*`
    (intra-package only; the audit module has no external
    non-stdlib dependencies)
  - PEP 561 marker (`py.typed`) added for downstream typing
  - `packages/audit/src` and `packages/audit/tests` added
    to `pyproject.toml [tool.mypy] exclude` (same pattern
    as the J2 scenario engine ports — audit source
    intentionally pre-dates 3.12 typing style)

The 17 tests in `test_governed_spine.py` (recovered with the
audit module, adapted to the new package layout) are
preserved as `tests/test_audit_chain.py` to verify the
behavior of the audit log in isolation. Integration with
`canonical`, `identity`, and the rest of the governance
spine lives in those packages' own tests.

## See also

- `packages/canonical/` — canonical state that consumes
  `AuditLog`
- `packages/identity/` — actor identity registry
- `packages/governance/` — the higher-level governance
  primitives (triumvirate, iron_path, asymmetric_security,
  constitutional_kernel) that build on this audit chain
