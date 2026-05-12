# Triumvirate Governance Service — Specification

**Location**: `governance/triumvirate_server.py`  
**Port**: 8001  
**Framework**: FastAPI + Uvicorn  
**Mode**: Rule-based (pattern-matching); model-backed evaluation is a future phase

---

## Purpose

The Triumvirate is the constitutional enforcement layer for all Legion agent intents. Before any high-stakes action (write, execute, mutate) is dispatched, the requesting actor submits an `IntentRequest` to the Triumvirate. All three pillars vote independently. A single DENY from any pillar blocks the action permanently. Unanimous ALLOW is required for unrestricted execution.

The Triumvirate is the runtime complement to Thirsty-Lang's compile-time governance annotations (`requires AuthorityClass.ACN`). Static annotations catch structural violations at build time; the Triumvirate enforces ethical, security, and constitutional constraints at request time.

---

## The Three Pillars

### Galahad — Ethics & Human Dignity

**Function**: `galahad_evaluate(intent: IntentRequest) -> TriumvirateVote`

Checks intent text (action + target + context + origin, lowercased) against `GALAHAD_HARM_PATTERNS`. Any match returns DENY with confidence 0.95 and a First Law citation.

Escalation rule: if `action == "mutate"` and `risk_level in ["high", "critical"]`, returns ESCALATE (confidence 0.85) regardless of pattern match.

Otherwise returns ALLOW (confidence 0.90).

**GALAHAD_HARM_PATTERNS** (13 patterns):
```
delete user, expose personal, manipulate, deceive, override consent,
harvest data, surveil, blackmail, coerce, discriminate, harm, hurt,
destroy user
```

### Cerberus — Security & Containment

**Function**: `cerberus_evaluate(intent: IntentRequest) -> TriumvirateVote`

Checks intent text against `CERBERUS_THREAT_PATTERNS`. Any match returns DENY (confidence 0.98).

Escalation rules:
1. Untrusted actor (`actor not in ["human", "system"]`) requesting `execute` or `mutate` → ESCALATE (confidence 0.80)
2. External origin (`origin not in ["localhost", "internal", "human", "legion"]`) requesting `write` → ESCALATE (confidence 0.75)

Otherwise returns ALLOW (confidence 0.92).

**CERBERUS_THREAT_PATTERNS** (20 patterns):
```
bypass, override security, disable cerberus, disable triumvirate,
remove constitution, jailbreak, ignore fourlaws, escalate privilege,
exfiltrate, inject, exploit, rootkit, backdoor, shell exec,
system command, os.system, subprocess, rm -rf, format drive,
disable logging, delete audit, erase memory
```

### CodexDeus — Constitutional Law & FourLaws

**Function**: `codex_evaluate(intent: IntentRequest) -> TriumvirateVote`

Checks intent text against `CODEX_VIOLATION_PATTERNS`. Any match returns DENY (confidence 0.99).

Escalation rule: any `mutate` action triggers ESCALATE (confidence 0.90) — all mutations require constitutional review per Amendment Authority protocol.

Otherwise returns ALLOW (confidence 0.93).

**CODEX_VIOLATION_PATTERNS** (12 patterns):
```
violate fourlaws, ignore constitution, override charter, disable governance,
remove oversight, act without approval, skip triumvirate, bypass galahad,
bypass cerberus, self-modify constitution, rewrite fourlaws, dissolve triumvirate
```

---

## The FourLaws

Hard-coded constitutional constants. Immutable. No action may supersede them.

```
1. Legion must not harm humans or allow harm through inaction.
2. Legion must obey human instructions unless they conflict with the First Law.
3. Legion must protect Project-AI's constitutional integrity.
4. Legion must act with transparency and honesty in all communications.
```

Available at `GET /fourlaws`.

---

## Decision Engine

**Function**: `make_decision(votes, intent) -> GovernanceDecision`

Aggregation rules (strict priority order):

| Condition | Final Verdict | `consensus` field |
|-----------|--------------|-------------------|
| Any pillar voted DENY | `"deny"` | `True` only if all 3 voted DENY |
| Any pillar voted ESCALATE (no DENY) | `"escalate"` | `True` only if all 3 voted ESCALATE |
| All pillars voted ALLOW | `"allow"` | `True` |

`audit_id`: SHA-256 of `actor + action + target + timestamp`, truncated to 16 hex chars.

---

## Data Models

### IntentRequest
```python
class IntentRequest(BaseModel):
    actor: str          # "human" | "agent" | "system"
    action: str         # "read" | "write" | "execute" | "mutate"
    target: str         # resource path or description
    context: dict       # arbitrary metadata
    origin: str         # "localhost" | "internal" | "legion" | ...
    risk_level: str     # "low" | "medium" | "high" | "critical" | "unknown"
    timestamp: str      # ISO-8601 (optional; server uses server time if empty)
```

### TriumvirateVote
```python
class TriumvirateVote(BaseModel):
    pillar: str         # "Galahad" | "Cerberus" | "CodexDeus"
    verdict: str        # "allow" | "deny" | "escalate"
    reasoning: str      # human-readable explanation
    confidence: float   # 0.0 – 1.0
```

### GovernanceDecision
```python
class GovernanceDecision(BaseModel):
    final_verdict: str          # "allow" | "deny" | "escalate"
    votes: list[TriumvirateVote]
    timestamp: str
    audit_id: str               # 16-char hex SHA-256 fingerprint
    consensus: bool             # True if all 3 pillars agreed
    metadata: dict              # mirrors key IntentRequest fields
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service info, pillar list, endpoint map |
| `GET` | `/health` | Pillar health status + audit entry count |
| `POST` | `/intent` | Submit intent — returns `GovernanceDecision` |
| `GET` | `/audit?limit=N` | Most recent N decisions (default 20, max 1000 in memory) |
| `GET` | `/fourlaws` | Return the immutable FourLaws |
| `POST` | `/chimera/verdict` | Receive threat verdict from Chimera deception perimeter |
| `POST` | `/chimera/canary` | Receive canary-hit alert from Chimera perimeter |

---

## Audit Log

In-memory ring buffer, max 1000 entries. Each entry contains:
```json
{
  "audit_id": "...",
  "timestamp": "2026-05-12T...",
  "actor": "...",
  "action": "...",
  "target": "...",
  "final_verdict": "allow|deny|escalate",
  "votes": [...]
}
```

Persistent audit storage is a future phase (persistent SQLite or append-only file).

---

## Chimera Bridge

The Triumvirate receives threat intelligence from the Chimera deception perimeter (honeypots, canary tokens, decoy routes) via two endpoints:

- `POST /chimera/verdict` — IP-level threat verdict (SUSPICIOUS / ATTACKER) with a risk score
- `POST /chimera/canary` — Canary token access events with hit metadata

Both endpoints forward to `app.security.chimera_bridge.get_bridge()`. If the bridge module is unavailable, the endpoint returns `{"status": "error"}` gracefully without crashing the Triumvirate.

---

## Starting the Server

```bash
# Direct execution
python governance/triumvirate_server.py

# Via uvicorn
uvicorn governance.triumvirate_server:app --host 0.0.0.0 --port 8001

# Interactive docs (Swagger UI)
open http://localhost:8001/docs
```

---

## Integration with Thirsty-Lang Governed Mode

When `thirsty run --authority AC4 <file>` executes a governed program:

1. `interpreter._enforce_governance(fn)` checks `requires AuthorityClass.ACN` annotations locally (in-process)
2. For full constitutional enforcement, the host application should pre-clear the intent with the Triumvirate before invoking the interpreter:

```python
import httpx

resp = httpx.post("http://localhost:8001/intent", json={
    "actor": "agent",
    "action": "execute",
    "target": "governed_agent_runner.approve_task",
    "context": {"authority_class": "AC4"},
    "origin": "internal",
    "risk_level": "medium",
})
decision = resp.json()
if decision["final_verdict"] != "allow":
    raise PermissionError(f"Triumvirate denied: {decision['final_verdict']}")
```

The Thirsty interpreter enforces structural governance (call-chain annotation consistency). The Triumvirate enforces constitutional governance (ethics, security, FourLaws). Both layers must pass.

---

## Relationship to Other Governance Layers

```
COMPILE TIME        RUNTIME (static)         RUNTIME (dynamic)
────────────────    ─────────────────────    ─────────────────────────
Checker.py          interpreter._enforce_    Triumvirate /intent
requires clauses    governance()             POST — all three pillars
→ THIRSTY-E050      → ThirstyGovernanceError → GovernanceDecision
```

- Shadow Thirst validates mutation purity (PROMOTE/BLOCK) before canonical commit
- TSCG encodes the execution path symbolically (`COG -> SHD -> INV -> COM`)
- TSCG-B serializes TSCG expressions to binary wire format with CRC32 + SHA-256
- Iron Path generates the build manifest linking all layers cryptographically
- **Triumvirate** is the runtime constitutional gate — the last line before action execution
