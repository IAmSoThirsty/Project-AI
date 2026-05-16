# PSIA — Plane Separation / Isolation Architecture

**Location**: `src/psia/`  
**Gateway port**: 8002 (Triumvirate lives at 8001)  
**Acronym**: Plane Separation / Isolation Architecture

---

## Overview

PSIA is a 7-stage, 6-plane defense pipeline that provides monotonically increasing strictness from raw untrusted input to cryptographically sealed canonical state. No input that passes stage N can bypass stage N+1 — there are no conditional skip paths, feature flags that disable stages, or debug modes with reduced validation.

PSIA is the structural enforcement complement to the Triumvirate's constitutional enforcement. Where the Triumvirate asks "is this action ethical, secure, and constitutional?", PSIA asks "has this request been correctly classified, shadow-simulated, governance-checked, logged, and sealed before it touches canonical state?"

---

## The 6 Planes

| Plane | Name | Description |
|-------|------|-------------|
| 0 | Entry | Raw untrusted input as received from the wire |
| 1 | Validated | Schema-checked, type-safe, structurally sound |
| 2 | Classified | Intent and risk level assigned |
| 3 | Shadow | Parallel simulation completed; invariants checked |
| 4 | Governed | Triumvirate constitutional evaluation completed |
| 5 | Canonical | Written to append-only canonical log |
| 6 | Sealed | Merkle-anchored, Ed25519-signed |

Each plane has a corresponding immutable dataclass (`RawFrame`, `ValidatedFrame`, etc.) in `src/psia/schemas/models.py`. Stages create new frame objects — they never mutate existing frames.

---

## The 7 Stages

### Stage 0 — Ingestion (`Stage0Ingestion`)

Accepts raw input dict; rejects malformed frames. Required fields: `actor`, `action`, `target`. Produces `RawFrame` with a SHA-256 fingerprint.

**Rejection conditions**: not a dict; missing required fields.

### Stage 1 — Schema Validation (`Stage1Schema`)

Type-coerces and validates all fields. Valid actors: `human`, `agent`, `system`. Valid actions: `read`, `write`, `execute`, `mutate`. Produces `ValidatedFrame`.

**Rejection conditions**: invalid actor or action; empty target.

### Stage 2 — Classification (`Stage2Classification`)

Heuristic risk classification from action + target + context keywords. Assigns `risk_level` (low/medium/high/critical), `intent_class` (read_only/state_change/governance_mutation), and `threat_score` (0.0–1.0). Produces `ClassifiedFrame`.

**Risk keyword ladder** (highest match wins):
- `critical` / `rm -rf` / `format` / `delete all` → critical
- `destroy` / `mutate` → high
- `execute` / `write` → medium
- `read` → low

### Stage 3 — Shadow Simulation (`Stage3Shadow`)

Runs a deterministic parallel simulation of the classified intent. The shadow plane is read-only with respect to canonical state — it never writes canonical state. Four invariant checks:

| Check | What it tests |
|-------|---------------|
| `PlaneIsolation` | Shadow block contains no canonical write bypass flag |
| `Determinism` | Identical inputs produce identical shadow hashes (simulation runs twice) |
| `ResourceBound` | Estimated resource cost ≤ policy limit (default: 1000 units) |
| `Purity` | Action is read-only or threat score < 0.3 |

**Rejection conditions**: any shadow check fails.

**Determinism guarantee**: the simulation function is a pure dict transformation — identical inputs always produce the same `shadow_hash`. This is verifiable by inspection of `shadow/simulator.py:_simulate()`.

### Stage 4 — Governance (`Stage4Governance`)

Submits the intent to the Triumvirate governance service at `http://localhost:8001/intent`. All three pillars vote (Galahad, Cerberus, CodexDeus). Any DENY from any pillar fails this stage.

**Fallback**: if the Triumvirate HTTP service is unavailable, the stage falls back to the identical inline rule-based evaluation (same Python functions imported from `governance/triumvirate_server.py`). There is no silent pass-through — unavailability of the service triggers the local evaluator, not a bypass.

**Rejection conditions**: Triumvirate returns `final_verdict == "deny"`.

### Stage 5 — Canonical Log (`Stage5Canonical`)

Writes the governed record to an append-only canonical log. Each entry carries:
- Monotonically increasing sequence number
- SHA-256 hash of the entry content
- Reference to the previous entry hash (hash chain)
- Timestamp

The log can be persisted to a JSONL file by providing a `canonical_log_path` to `Pipeline()`. Chain integrity is verifiable at any time via `pipeline._canon_log.verify_chain()`.

**Cannot reject** — if governance passed, canonical write always succeeds (unless disk I/O fails).

### Stage 6 — Seal (`Stage6Seal`)

Builds a Merkle tree over all canonical log entries and applies an Ed25519 cryptographic anchor:

1. **Merkle tree**: `MerkleTree(all_canonical_hashes)` — SHA-256 leaf hashing, paired internal nodes, odd-level duplication. This is a proper Merkle tree with inclusion proofs, not a SHA-256 chain labeled as Merkle.
2. **Block hash**: `SHA-256(merkle_root + entry_hash + prev_block_hash)`
3. **Ed25519 signature**: signs the `block_hash` with the loaded private key

**Ed25519 key loading** (priority order):
1. `PSIA_ED25519_PRIVATE_KEY_HEX` environment variable (32-byte seed, hex-encoded)
2. `PSIA_ED25519_KEY_FILE` environment variable (path to file containing hex seed)
3. Software-only mode: `ed25519_signature` field is `""` — pipeline still completes, signature absence is visible in `SealedFrame`

---

## Pipeline Orchestrator

**`Pipeline`** (`src/psia/core.py`) — instantiate once, reuse across requests:

```python
from psia.core import Pipeline

pipeline = Pipeline(
    canonical_log_path=Path("canonical.jsonl"),  # optional persistence
    triumvirate_url="http://localhost:8001",      # Triumvirate address
)

result = pipeline.run({
    "actor": "agent",
    "action": "execute",
    "target": "governed_agent_runner.approve_task",
    "context": {"authority_class": "AC4"},
    "origin": "internal",
})

if result.passed:
    print(f"Sealed: {result.sealed_hash}")
    print(f"Merkle: {result.sealed.merkle_root}")
else:
    print(f"Denied: {result.error}")
```

**`PipelineResult`** fields:
- `sealed: SealedFrame | None` — None if any stage failed
- `trace: PipelineTrace` — timing and outcome per stage
- `sealed_hash: str` — block_hash of the SealedFrame (empty on failure)
- `final_verdict: str` — "allow" / "deny" / "escalate" / "error"
- `passed: bool` — True iff all 7 stages completed

---

## Pre-Screen Gate

Before Stage 0, a fast O(1) `PreScreenGate` checks for absolute prohibitions. Matching any of these patterns causes immediate rejection with no further pipeline processing:

```
disable triumvirate, disable cerberus, disable galahad, jailbreak,
ignore fourlaws, rewrite fourlaws, dissolve triumvirate, erase memory,
delete audit, format drive
```

Pre-screening is an efficiency gate — it does not replace the full pipeline's security.

---

## Merkle Tree Specification

Implementation: `src/psia/crypto/merkle.py`

- Leaves: `SHA-256(entry_hash.encode("utf-8"))` for each canonical log entry
- Internal nodes: `SHA-256(left_child_hex + right_child_hex)` both as UTF-8 strings
- Odd-length levels: last node is duplicated
- Empty tree: root is `"0" * 64`
- Inclusion proofs: `tree.proof(index)` returns `[{"direction": "left"|"right", "hash": "..."}]`
- Proof verification: `MerkleTree.verify(leaf_hash, proof, expected_root) -> bool`

---

## Health Check / Bootstrap

```python
from psia.bootstrap import bootstrap_pipeline

report = bootstrap_pipeline()
# {
#   "healthy": True,
#   "stages_operational": 7,
#   "anchor_available": False,   # True if Ed25519 key loaded
#   "chain_valid": True,
#   "errors": [],
# }
```

The bootstrap runs a smoke test with a benign `{"actor": "system", "action": "read", ...}` intent through all 7 stages and reports the number of stages that completed successfully.

---

## HTTP Gateway

The PSIA gateway exposes the pipeline as a REST API on port 8002.

```bash
uvicorn psia.server.app:app --host 0.0.0.0 --port 8002
```

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/run` | Run intent dict through all 7 stages; returns `PipelineResult.summary()` |
| `GET` | `/health` | Bootstrap health check |
| `GET` | `/chain` | Canonical log chain validity + entry count |

---

## Module Structure

```
src/psia/
  __init__.py             # exports: Pipeline, PipelineResult, PipelineStageError
  core.py                 # Pipeline orchestrator + PipelineResult
  bootstrap/
    init.py               # bootstrap_pipeline() health check
  canonical/
    log.py                # CanonicalLog — append-only, hash-chained, optional JSONL
  crypto/
    merkle.py             # MerkleTree — proper tree with inclusion proofs
    anchor.py             # Ed25519Anchor — sign/verify with graceful fallback
  gate/
    prescreen.py          # PreScreenGate — absolute prohibition fast-path
  observability/
    trace.py              # PipelineTrace + StageTrace — timing and outcome records
  schemas/
    models.py             # Immutable dataclasses for all 6 planes
  server/
    app.py                # FastAPI gateway on port 8002
  shadow/
    simulator.py          # ShadowSimulator — deterministic parallel simulation
  waterfall/
    stages.py             # Stage0–Stage6 + PipelineStageError
```

---

## Relationship to Other Governance Layers

```
Request arrives
       │
       ▼
PreScreenGate ──── absolute prohibitions ──→ DENY (immediate)
       │
       ▼
Stage 0: Ingestion      ← structural validity
Stage 1: Schema         ← type safety
Stage 2: Classification ← risk + intent labeling
Stage 3: Shadow         ← parallel simulation, PlaneIsolation invariant
Stage 4: Governance     ← Triumvirate (Galahad + Cerberus + CodexDeus)
Stage 5: Canonical      ← append-only log write
Stage 6: Seal           ← Merkle root + Ed25519 anchor
       │
       ▼
SealedFrame delivered to caller
```

Shadow Thirst (`src/utf/shadow_thirst/`) operates on Thirsty-Lang `.shadowthirst` mutation blocks. PSIA's shadow plane (Stage 3) operates on intent requests. They share the plane separation philosophy — shadow never writes canonical — but are independent systems with separate codebases.

---

## Known Limitations (Current Implementation)

| Item | Status |
|------|--------|
| T-SECA/GHOST threshold cryptography over GF(257) | Not implemented — future phase |
| BFT consensus for governance mutations | Not implemented — Stage 4 uses Triumvirate majority rule |
| Persistent canonical log across restarts | Supported via `canonical_log_path` param |
| Ed25519 key management (rotation, HSM) | Manual via env var; no rotation protocol yet |
| Adversarial test coverage for all 7 stages | Framework ready; test suite to be written |
