# Phase J2.2 Discovery + Sub-Phase Plan — atlas audit_trail (Explanation Chain)

**Status:** DISCOVERY + PLAN (no code written yet)
**Authority:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Prior:** `docs/internal/PHASE_J2_1_DISCOVERY.md`, `docs/internal/STAGE_19_5J2_1_ACCEPTANCE.md`
**Mission statement (user 2026-06-25):**
> "This system needs to explain, prove, replay why reality was allowed to continue."

**Date:** 2026-06-25
**Source-of-truth:** `T:\00-Active\Project-AI-main\atlas\audit\trail.py`
**Target:** Extend canonical `packages/atlas/` with audit trail module

---

## 0. Why this mission

The user's mission statement describes the **explanation chain**: every
decision that affects "reality" must have a rationale (explain), every
claim must be cryptographically verifiable (prove), and every event
must be reconstructable from immutable records (replay).

The phrase "why reality was allowed to continue" is the key insight: at
every boundary where the system could have **stopped/denied/halted**, it
instead **allowed**. That allow-decision must itself be auditable.

The canonical atlas currently lacks a dedicated audit trail. The legacy
atlas had `atlas/audit/trail.py` (450 LOC) which provided exactly this
functionality. This sub-phase ports it.

---

## 1. The three properties of the explanation chain

### 1.1 Explain (rationale)
Every allow/deny decision must include WHY:
- Which rule was evaluated?
- What was the input state?
- What was the output?
- What evidence was considered?

### 1.2 Prove (cryptographic verifiability)
Every audit record must be hash-chained:
- Each record contains `prev_hash` linking to the previous record
- Each record has its own `record_hash` from canonical content
- Tampering with any record invalidates the chain from that point on

### 1.3 Replay (reconstructability)
Given the chain, must be able to:
- Reconstruct any decision given its inputs
- Verify chain integrity
- Detect gaps or tampering
- Re-execute decisions deterministically (or document why not)

---

## 2. Legacy surface inventory

`T:\00-Active\Project-AI-main\atlas\audit\trail.py` (450 LOC) exports:

| Class/Enum | Purpose |
|---|---|
| `AuditLevel` | Severity levels: INFORMATIONAL, STANDARD, HIGH_PRIORITY, CRITICAL, EMERGENCY |
| `AuditCategory` | Categories: SYSTEM, DATA, GOVERNANCE, SECURITY, OPERATION, VALIDATION, CONFIGURATION, STACK |
| `AuditEvent` | Immutable record: timestamp, level, category, actor, action, resource, outcome, prev_hash, record_hash |
| `AuditTrail` | Append-only ledger with hash chain |
| `get_audit_trail()` | Singleton factory (legacy DI pattern) |

**External dependencies:** stdlib only (hashlib, json, threading, logging)

**Key features:**
- Append-only (no edit, no delete)
- Hash-chained (each record has prev_hash + record_hash)
- Tamper detection (verify_chain returns bool + list of issues)
- Thread-safe append (lock around append)
- Persistence (save to JSONL file, load from JSONL file)
- Singleton accessor (legacy pattern; canonical will use factory)

---

## 3. Architectural decisions

### D1: Singleton vs factory pattern

**Decision:** Factory function `get_audit_trail()` (legacy compat).

**Rationale:** Matches legacy API. Multiple trails can exist (e.g., one
per session) if needed; singleton is the default.

### D2: Hash chain algorithm

**Decision:** SHA-256 over canonical JSON (sort_keys=True, no spaces).

**Rationale:** Same algorithm used elsewhere in the framework. Tampering
with any record invalidates the chain.

### D3: Persistence format

**Decision:** JSONL (one JSON object per line).

**Rationale:** Append-friendly, line-oriented, no embedded newlines.

### D4: Thread safety

**Decision:** `threading.Lock` around append + verify.

**Rationale:** Standard pattern. Production-grade safety.

### D5: Integration with existing audit chain

**Decision:** Add a callback `execution.submit_action` that records each
allow/deny decision to the audit trail.

**Rationale:** Makes the "why reality was allowed to continue" question
answerable: the audit trail shows every decision point with rationale.

### D6: Subordination notice

**Decision:** Each audit record includes SUBORDINATION_NOTICE field.

**Rationale:** Consistency with atlas.sensitivity and atlas.analysis
patterns.

### D7: Subordination contract

The audit trail itself is subordinate — it records decisions, it does
not make them. The audit record's `subordination_notice` field documents
this.

---

## 4. Architectural invariants (AGENTS.md v3)

audit module must respect:
- **Downward-only deps**: atlas imports only kernel + stdlib. No upward.
- **Canonical types**: kernel.JsonScalar, kernel.JsonValue for JSON.
- **Fail-closed**: AuditTrailError on invalid input.
- **Pluggable seams**: storage backend interface (in-memory, JSONL).
- **Deterministic**: same events → same hashes.
- **Audit chain**: hash chain must verify end-to-end.
- **Strict typing**: mypy --strict clean.

---

## 5. Sub-phase plan (J2.2 wave)

### Phase J2.2.0 — Audit trail source (~400 LOC)

**Scope:** Single source file `packages/atlas/src/atlas/audit.py`
+ update `packages/atlas/src/atlas/__init__.py` to re-export.
**New source files:** 1
**Tasks:**
1. `AuditLevel` enum (5 levels, StrEnum)
2. `AuditCategory` enum (8 categories, StrEnum)
3. `AuditEvent` frozen dataclass with hash chain fields
4. `AuditTrail` class with append + verify_chain + save + load
5. `get_audit_trail()` factory function
6. `AuditTrailError` exception
7. `AuditChainVerification` dataclass for verification results
8. Update `__init__.py` with re-exports

### Phase J2.2.1 — Audit trail tests (~300 LOC, ~25 tests)

**Scope:** Test file `packages/atlas/tests/test_audit.py`
**New test files:** 1
**Tasks:**
1. AuditLevel + AuditCategory enum tests
2. AuditEvent validation (timestamp, hash format, etc.)
3. AuditTrail append (basic, sequence numbers)
4. AuditTrail hash chain integrity (verify_chain pass)
5. AuditTrail tamper detection (modify record, verify fails)
6. AuditTrail save/load round-trip
7. AuditTrail thread safety
8. AuditTrail verify_chain reports detailed issues
9. Factory function returns singleton or new instance
10. Subordination notice binding

### Phase J2.2.2 — Integration test (~150 LOC, ~8 tests)

**Scope:** Cross-package integration test
`tests/test_atlas_audit_integration.py`
**New test files:** 1
**Tasks:**
1. Atlas.record() emits audit event to trail
2. ExecutionGate.submit_action() emits audit event
3. Audit chain shows full decision rationale end-to-end
4. Tamper detection across full chain
5. Save → reload → verify chain still passes
6. Multi-threaded append preserves chain
7. Audit replay reconstructs decision sequence

### Phase J2.2.3 — Acceptance doc + commit

**Scope:** `docs/internal/STAGE_19_5J2_2_ACCEPTANCE.md` + commit
**Tasks:**
1. All gates green (pytest, mypy --strict, ruff check, ruff format)
2. CONTINUITY_MAP updated
3. Commit + push

---

## 6. File count summary

| Sub-phase | Source files | Test files | Init modify | Other |
|---|---|---|---|---|
| J2.2.0 | 1 | 0 | 1 | 0 |
| J2.2.1 | 0 | 1 | 0 | 0 |
| J2.2.2 | 0 | 1 | 0 | 0 |
| J2.2.3 | 0 | 0 | 0 | 1 (acceptance doc) |
| **Total** | **1** | **2** | **1** | **1** |

Estimated: ~400 source LOC + ~300 test LOC + ~150 integration LOC + 1 doc.

---

## 7. Risk assessment

1. **Hash chain collisions**: SHA-256 collisions are computationally
   infeasible. No risk in practice.
2. **Concurrent append**: threading.Lock handles this. Tested.
3. **Storage backend**: JSONL works but is file-bound. Future: pluggable
   backend Protocol (in-memory, SQLite, etc.).
4. **Performance**: O(n) verify_chain. Acceptable for n < 10^6 records.
5. **Replay determinism**: depends on inputs being deterministic. Audit
   trail stores the inputs; replay uses them.

---

## 8. Subordination contract

```
SUBORDINATION_NOTICE = (
    "ATLAS output is analytical evidence only; it is not a decision, "
    "authority grant, or actuation."
)
```

Each audit record includes this notice as a frozen field. The audit
trail itself is subordinate — it records decisions, it does not make
them.

---

## 9. Recommended authorization scope

> "Proceed with Phase J2.2.0 (source code only, ~400 LOC). Stop and
> produce J2.2.1 plan before writing tests."

This preserves the wave-bounded pattern from J2.1.

---

## 10. Self-report (v3 §35)

```
Mode: governance system (planning — Phase J2.2 audit trail discovery)
Created: docs/internal/PHASE_J2_2_DISCOVERY.md (this file)
Modified: None.
Verified: legacy audit/trail.py inventoried (450 LOC, 8 classes/enums).
Failed: None.
Not verified: thread safety under high concurrency (deferred to J2.2.1).
Risks: hash chain collisions (infeasible), performance at scale
  (deferred to benchmark phase), storage backend flexibility (deferred
  to future Protocol).
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on J2.2.0)
Remaining:
  - User authorization to start Phase J2.2.0 (source code)
  - Per-sub-phase "go" for J2.2.1, J2.2.2, J2.2.3 thereafter
```

---

## 11. Connection to broader mission

This sub-phase is the **foundation of the explanation chain** in the
canonical atlas. With this in place:

- Every atlas operation can be audited
- Every allow/deny decision has a recorded rationale
- Every event can be replayed from immutable records
- The "why was reality allowed to continue?" question becomes answerable

This is the most consequential single sub-phase for the system's
trustworthiness and auditability.
