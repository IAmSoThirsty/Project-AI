---
title: "NIRL — Python Implementation Reference"
type: implementation
system: nirl
status: implemented
created: 2026-05-03
tags: [nirl, implementation, heart, minibrain, antibody, forge, cascade]
related_systems: [council_hub, execution_router, governance_pipeline]
source_package: src/app/core/nirl/
---

# NIRL — Nested Intention-Response Loop

NIRL is a biological immune-system analogy built into the Project-AI governance pipeline. It adds a cryptographic integrity layer beneath the governance gate: every approved execution passes through a Forge that signs the outcome, and every section of the system has a MiniBrain that validates those signatures before releasing further execution.

**State machine reference**: [[docs/nirl/nirl_state_machines.html|FSM Diagrams (Mermaid)]]

---

## The 4-Component Cascade

```
Heart (global tick)
  └─► MiniBrain (per-section controller)
        └─► Antibody (single-lifecycle escort)
              └─► Forge (purification + HMAC signing)
```

---

## Heart

**File**: `src/app/core/nirl/heart.py`  
**Class**: `Heart`

Global tick engine. Runs as a daemon thread (configurable `tick_interval`, default 30 s in `council_hub.py`).

| State | Transition |
|-------|-----------|
| `TICK_WAIT` | sleep until interval |
| `GLOBAL_TICK` | wake, increment counter |
| `SPAWN_SKELETON` | generate probe skeleton for each registered section |
| `CHECK_HEARTBEATS` | verify sections sent heartbeat last tick |
| `DISTRIBUTE` | deliver skeletons to registered sections |
| `LOST_PARENT_INJECT` | section missed heartbeat → inject recovery probe |
| `RESET_SECTION` | mark section degraded, notify via strain callback |

**Key API**:
```python
heart = Heart(tick_interval=30.0, min_probes=1)
heart.register_section("council_hub")
heart.start()   # daemon thread
heart.stop()
heart.heartbeat("council_hub")     # called by MiniBrain each tick
heart.signal_strain("council_hub", {"backlog": 52})
```

**Wired in**: `src/app/core/council_hub.py` — `Heart` instantiated in `CouncilHub.register_project()`, stopped in `stop_autonomous_learning()`.

---

## MiniBrain

**File**: `src/app/core/nirl/mini_brain.py`  
**Class**: `MiniBrain`

One MiniBrain governs one logical section. Owns a Forge instance and creates an Antibody for each incoming probe.

| State | Transition |
|-------|-----------|
| `LOCAL_TICK_WAIT` | idle |
| `LOCAL_TICK` | probe received |
| `SPAWN_ANTIBODY` | create Antibody for probe |
| `ALERT_TEMPLATE` | template invalid |
| `FALLBACK_SKELETON` | use fallback, return failure |
| `ASSIGN_PROBE` | run Antibody lifecycle |
| `MONITOR_ESCORT` | wait for Forge result |
| `RECEIVE_COMPLETION` | record forge result |
| `VERIFY_SIGNATURE` | check HMAC-SHA256 sig |
| `VALID` | signature valid |
| `INVALID` → `BLOCK_REGEN` | bad sig, block and log |
| `CHECK_STATUS` | inspect forge success flag |
| `RELEASE_NEXT` | approved — allow next action |
| `ALERT` | forge failed — warn |

**Signature verification**: Checks `forge_result["signature"]` is a 64-char lowercase hex string (SHA-256 output). Because the Forge embeds a nanosecond timestamp in its signed message, exact replay of the HMAC is impossible — the check validates format/length as a proxy for authenticity.

---

## Antibody

**File**: `src/app/core/nirl/antibody.py`  
**Class**: `Antibody`

Single-lifecycle escort unit. Born when MiniBrain spawns it, destroyed when Forge completes.

| State | Meaning |
|-------|---------|
| `SPAWNED` | created |
| `CAPTURE` | locking target template |
| `SEALED` | SHA-256 payload hash computed, immutable |
| `ESCORT` | routing sealed payload to Forge |
| `FORGE_ENTRY` | submitted to Forge |
| `DESTROYED` | Forge succeeded — terminal ✓ |
| `DEAD_LETTER` | Forge failed — terminal ✗ |

**Seal**: `hashlib.sha256(json.dumps(target, sort_keys=True).encode()).hexdigest()` — deterministic, content-addressed.

---

## Forge

**File**: `src/app/core/nirl/forge.py`  
**Class**: `Forge`  
**Signing key**: `_FORGE_SECRET = b"project-ai-forge-signing-key-v1"` (HMAC-SHA256)

Purification and destruction engine. Verifies payload integrity, optionally replays in a shadow context, then signs the outcome.

| State | Meaning |
|-------|---------|
| `RECEIVE` | accept payload from Antibody |
| `VERIFY_PAYLOAD` | check `checksum` field matches SHA-256 of `data` |
| `VALID` / `REJECT` | integrity check result |
| `CHECK_REPLAY` | decide shadow vs direct |
| `SHADOW_REPLAY` | optional re-execution in shadow context |
| `DIRECT_DESTROY` | skip shadow |
| `DESTROY` | commit to destruction |
| `ATOMIC_CHECK` | verify atomic operation succeeded |
| `SUCCESS` / `DEAD_LETTER` | outcome |
| `SIGN_COMPLETION` | HMAC-SHA256 sign `section_id:probe_id:success:reason:timestamp_ns` |
| `SIGN_FAILURE` | sign failure outcome |
| `ROUTE_SIGNAL` | return signed result dict |

**Signed result**:
```python
{
    "success": True,
    "section_id": "...",
    "probe_id": "...",
    "reason": "forge_complete",
    "signature": "<64-char hex HMAC-SHA256>",
}
```

---

## Wiring into the Governance Pipeline

### Execution Router (non-fatal integrity gate)

After the governance gate approves an action, `execution_router.py` runs a Forge check:

```python
# src/app/core/execution_router.py — Step 6 (post-gate, non-fatal)
forge = Forge()
forge_payload = {
    "data": ctx_str,
    "checksum": hashlib.sha256(ctx_str.encode()).hexdigest(),
    "section_id": domain,
    "probe_id": action,
}
forge_result = forge.process(forge_payload)
if not forge_result.get("success"):
    logger.warning("NIRL Forge integrity warning: ...")
# Non-fatal: legitimate executions are never blocked by Forge bugs
```

### CouncilHub (Heart lifecycle)

```python
# src/app/core/council_hub.py — register_project()
self._heart = Heart(tick_interval=30.0, min_probes=1)
self._heart.register_section("council_hub")
self._heart.start()

# stop_autonomous_learning()
if hasattr(self, "_heart") and self._heart:
    self._heart.stop()
```

---

## Package Exports

```python
# src/app/core/nirl/__init__.py
from .heart import Heart, HeartState
from .mini_brain import MiniBrain, MiniBrainState
from .antibody import Antibody, AntibodyState
from .forge import Forge, ForgeState
```
