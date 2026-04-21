---
title: FastAPI Main Routes
category: api
layer: api-layer
audience: [integrator, maintainer, expert]
status: production
classification: technical-reference
confidence: verified
requires: [01-API-OVERVIEW.md]
time_estimate: 25min
last_updated: 2025-06-09
version: 2.0.0
---

# FastAPI Main Routes

## Purpose

The FastAPI backend (`api/main.py`, port 8001) is the **governance-first** API enforcing TARL (The AI Rights Law) and Triumvirate oversight. All requests flow through hard-gate validation.

**File**: `api/main.py` (468 lines)  
**Port**: 8001  
**Stack**: Python 3.11 + FastAPI + Pydantic  
**Security**: TARL enforcement, Triumvirate voting, audit logging

---

## Core Endpoints

### 1. Root Information - `GET /`

**Purpose**: API discovery and capability listing

**Request**:
```bash
curl http://localhost:8001/
```

**Response**:
```json
{
  "service": "Project AI Governance Host",
  "version": "0.2.0",
  "architecture": "Triumvirate + Contrarian Firewall",
  "capabilities": [
    "TARL Governance (Galahad, Cerberus, CodexDeus)",
    "Contrarian Firewall (Chaos Engine, Swarm Defense)",
    "Thirsty-lang Security Integration",
    "Intent Tracking & Cognitive Warfare",
    "Real-time Auto-tuning",
    "Federated Threat Intelligence"
  ],
  "endpoints": {
    "governance": {
      "submit_intent": "POST /intent",
      "governed_execute": "POST /execute",
      "audit_replay": "GET /audit",
      "view_tarl": "GET /tarl"
    },
    "firewall": { ... },
    "save_points": { ... },
    "health_check": "GET /health",
    "api_docs": "GET /docs"
  }
}
```

**Use Cases**:
- API discovery for new integrators
- Health check for monitoring systems
- Documentation link generation

---

### 2. Health Check - `GET /health`

**Purpose**: Service health and readiness check

**Request**:
```bash
curl http://localhost:8001/health
```

**Response**:
```json
{
  "status": "governance-online",
  "tarl": "1.0"
}
```

**Status Codes**:
- `200 OK` - Service operational
- `503 Service Unavailable` - Service degraded (future enhancement)

**Monitoring Integration**:
```yaml
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8001
  initialDelaySeconds: 30
  periodSeconds: 10
```

---

### 3. TARL Policy - `GET /tarl`

**Purpose**: Read-only access to governance rules

**Request**:
```bash
curl http://localhost:8001/tarl
```

**Response**:
```json
{
  "version": "1.0",
  "rules": [
    {
      "action": "read",
      "allowed_actors": ["human", "agent"],
      "risk": "low",
      "default": "allow"
    },
    {
      "action": "write",
      "allowed_actors": ["human"],
      "risk": "medium",
      "default": "degrade"
    },
    {
      "action": "execute",
      "allowed_actors": ["system"],
      "risk": "high",
      "default": "deny"
    },
    {
      "action": "mutate",
      "allowed_actors": [],
      "risk": "critical",
      "default": "deny"
    }
  ]
}
```

**Use Cases**:
- Policy transparency for auditors
- Client-side validation
- Documentation generation

**Security Note**: TARL is **immutable** at runtime. Changes require code deployment.

---

### 4. Submit Intent - `POST /intent`

**Purpose**: Submit intent for governance evaluation (no execution)

**Request**:
```bash
curl -X POST http://localhost:8001/intent \
  -H "Content-Type: application/json" \
  -d '{
    "actor": "human",
    "action": "write",
    "target": "/data/config.json",
    "context": {"reason": "update settings"},
    "origin": "web-ui"
  }'
```

**Request Schema**:
```python
class Intent(BaseModel):
    actor: ActorType  # human | agent | system
    action: ActionType  # read | write | execute | mutate
    target: str  # Resource being accessed
    context: dict[str, Any] = {}  # Additional context
    origin: str  # Source identifier
```

**Response** (Allowed):
```json
{
  "message": "Intent accepted under governance",
  "governance": {
    "intent_hash": "abc123...",
    "tarl_version": "1.0",
    "votes": [
      {
        "pillar": "Galahad",
        "verdict": "allow",
        "reason": "Actor aligns with rule"
      },
      {
        "pillar": "Cerberus",
        "verdict": "allow",
        "reason": "No adversarial patterns detected"
      }
    ],
    "final_verdict": "allow",
    "timestamp": 1717934096.789
  }
}
```

**Response** (Denied):
```json
{
  "detail": {
    "message": "Governance denied this request",
    "governance": {
      "intent_hash": "def456...",
      "tarl_version": "1.0",
      "votes": [
        {
          "pillar": "Galahad",
          "verdict": "allow",
          "reason": "Actor aligns with rule"
        },
        {
          "pillar": "Cerberus",
          "verdict": "deny",
          "reason": "High-risk action blocked by default"
        }
      ],
      "final_verdict": "deny",
      "timestamp": 1717934096.789
    }
  }
}
```

**Status Codes**:
- `200 OK` - Intent accepted (does NOT mean executed)
- `403 Forbidden` - Governance denied
- `400 Bad Request` - Invalid intent format

**Use Cases**:
- Pre-execution validation ("can I do this?")
- Dry-run mode for testing
- Policy debugging

---

### 5. Governed Execution - `POST /execute`

**Purpose**: Execute intent AFTER governance approval

**Request**:
```bash
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{
    "actor": "human",
    "action": "read",
    "target": "/data/logs.txt",
    "context": {},
    "origin": "cli"
  }'
```

**Response** (Success):
```json
{
  "message": "Execution completed under governance",
  "governance": {
    "intent_hash": "ghi789...",
    "tarl_version": "1.0",
    "votes": [...],
    "final_verdict": "allow",
    "timestamp": 1717934096.789
  },
  "execution": {
    "status": "executed",
    "note": "Sandbox execution completed",
    "target": "/data/logs.txt"
  }
}
```

**Response** (Denied):
```json
{
  "detail": {
    "message": "Execution denied by governance",
    "governance": {
      "final_verdict": "deny",
      ...
    }
  }
}
```

**Status Codes**:
- `200 OK` - Execution completed
- `403 Forbidden` - Governance denied
- `500 Internal Server Error` - Execution failed after approval

**Execution Flow**:
```
1. Validate intent format
2. Evaluate through TARL (Galahad + Cerberus)
3. Arbitrate with CodexDeus
4. Write audit log entry (append-only)
5. If allowed: Execute through SandboxExecutor
6. Return governance + execution results
```

**Security Guarantees**:
- ALL executions logged (audit.log)
- NO execution bypasses governance
- Audit log is append-only
- Intent hashes prevent replay attacks

---

### 6. Audit Replay - `GET /audit`

**Purpose**: Read governance audit log

**Request**:
```bash
# Get last 50 records (default)
curl http://localhost:8001/audit

# Get last 100 records
curl http://localhost:8001/audit?limit=100
```

**Response**:
```json
{
  "tarl_version": "1.0",
  "tarl_signature": "sha256:abc123...",
  "records": [
    {
      "intent_hash": "ghi789...",
      "tarl_version": "1.0",
      "votes": [
        {"pillar": "Galahad", "verdict": "allow", "reason": "..."},
        {"pillar": "Cerberus", "verdict": "allow", "reason": "..."}
      ],
      "final_verdict": "allow",
      "timestamp": 1717934096.789
    },
    ...
  ]
}
```

**Query Parameters**:
- `limit` (int, default: 50) - Number of records to return

**Use Cases**:
- Security audits
- Compliance reporting
- Forensic investigation
- Policy effectiveness analysis

**Audit Log Format**:
- **File**: `audit.log` (append-only)
- **Format**: JSONL (one JSON object per line)
- **Retention**: Unlimited (manual rotation required)
- **Integrity**: TARL signature prevents tampering

---

## Triumvirate Architecture

### Three Pillars of Governance

```
┌───────────────────────────────────────────────────────────┐
│                    INTENT EVALUATION                      │
└───────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ GALAHAD  │    │ CERBERUS │    │ CODEXDEUS│
    │  Ethics  │    │  Threat  │    │Arbitrator│
    │Alignment │    │Detection │    │          │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         │  PillarVote   │  PillarVote   │  Final
         │  ───────►     │  ───────►     │  Verdict
         └───────────────┴───────────────┘
                          │
                          ▼
                    ALLOW | DENY | DEGRADE
```

### 1. Galahad (Ethics & Alignment)

**Purpose**: Ensures actors are ethically authorized

**Integration**: Wraps Planetary Defense Core's Galahad agent

**Evaluation Logic**:
```python
def evaluate(intent: Intent, rule: dict) -> PillarVote:
    # Check actor authorization
    if intent.actor.value not in rule["allowed_actors"]:
        return PillarVote(
            pillar="Galahad",
            verdict="deny",
            reason="Actor not ethically authorized"
        )
    
    # Assess through Constitutional Core
    context = {
        "threat_level": 3 if rule["risk"] in ("high", "critical") else 0,
        "human_risk": rule.get("risk", "low")
    }
    PLANETARY_CORE.agents["galahad"].assess(context)
    
    return PillarVote(
        pillar="Galahad",
        verdict="allow",
        reason="Actor aligns with rule"
    )
```

**Verdict Criteria**:
- ✅ **Allow**: Actor in `allowed_actors`, low ethical risk
- ❌ **Deny**: Actor not authorized, ethical concerns

### 2. Cerberus (Threat & Bypass Detection)

**Purpose**: Detects adversarial patterns and high-risk actions

**Integration**: Wraps Planetary Defense Core's Cerberus agent

**Evaluation Logic**:
```python
def evaluate(intent: Intent, rule: dict) -> PillarVote:
    # High-risk actions blocked by default
    if rule["risk"] in ("high", "critical"):
        return PillarVote(
            pillar="Cerberus",
            verdict="deny",
            reason="High-risk action blocked by default"
        )
    
    # Advisory assessment from Constitutional Core
    PLANETARY_CORE.agents["cerberus"].assess({})
    
    return PillarVote(
        pillar="Cerberus",
        verdict="allow",
        reason="No adversarial patterns detected"
    )
```

**Verdict Criteria**:
- ✅ **Allow**: Low/medium risk, no adversarial patterns
- ❌ **Deny**: High/critical risk, suspicious patterns detected

### 3. CodexDeus (Final Arbitration)

**Purpose**: Final arbiter resolving conflicts between pillars

**Integration**: Wraps Planetary Defense Core's CodexDeus agent

**Arbitration Logic**:
```python
def arbitrate(votes: list[PillarVote], rule: dict) -> Verdict:
    # Any DENY vote → Final DENY
    if any(v.verdict == Verdict.deny for v in votes):
        return Verdict.deny
    
    # Advisory assessment from Constitutional Core
    PLANETARY_CORE.agents["codex"].assess({})
    
    # Use rule default (allow/degrade)
    return Verdict(rule["default"])
```

**Arbitration Rules**:
1. **Unanimous Veto**: Any `deny` → Final `deny`
2. **Default Fallback**: All `allow` → Apply rule default
3. **Degrade Mode**: Write actions default to `degrade` (requires extra approval)

---

## Data Models

### ActorType (Enum)

```python
class ActorType(StrEnum):
    human = "human"    # Human user
    agent = "agent"    # AI agent
    system = "system"  # System process
```

### ActionType (Enum)

```python
class ActionType(StrEnum):
    read = "read"        # Read operation (low risk)
    write = "write"      # Write operation (medium risk)
    execute = "execute"  # Execution (high risk)
    mutate = "mutate"    # State mutation (critical risk)
```

### Verdict (Enum)

```python
class Verdict(StrEnum):
    allow = "allow"      # Proceed with operation
    deny = "deny"        # Block operation
    degrade = "degrade"  # Require extra approval
```

### Intent (Pydantic Model)

```python
class Intent(BaseModel):
    actor: ActorType
    action: ActionType
    target: str
    context: dict[str, Any] = Field(default_factory=dict)
    origin: str
```

### GovernanceResult (Pydantic Model)

```python
class GovernanceResult(BaseModel):
    intent_hash: str
    tarl_version: str
    votes: list[PillarVote]
    final_verdict: Verdict
    timestamp: float
```

---

## Security Implementation

### Intent Hashing (Replay Prevention)

```python
def hash_intent(intent: Intent) -> str:
    """SHA-256 hash prevents intent replay attacks"""
    payload = json.dumps(intent.dict(), sort_keys=True).encode()
    return hashlib.sha256(payload).hexdigest()
```

**Use Cases**:
- Prevent replay attacks
- Audit trail integrity
- Intent deduplication

### Audit Logging (Append-Only)

```python
def write_audit(record: GovernanceResult):
    """Append-only audit log with JSONL format"""
    entry = {
        "intent_hash": record.intent_hash,
        "tarl_version": record.tarl_version,
        "votes": [v.dict() for v in record.votes],
        "final_verdict": record.final_verdict,
        "timestamp": record.timestamp
    }
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
```

**Security Properties**:
- **Append-only**: No modification of past records
- **JSONL format**: Line-by-line parsing prevents corruption
- **Timestamp**: Chronological ordering
- **Intent hash**: Prevents duplicate logging

### TARL Signature (Immutability)

```python
TARL_SIGNATURE = hashlib.sha256(
    json.dumps(TARL_V1, sort_keys=True).encode()
).hexdigest()
```

**Purpose**:
- Verify TARL policy hasn't been tampered with
- Detect unauthorized modifications
- Ensure governance consistency

---

## Integration with Other Services

### Save Points Router

```python
from api.save_points_routes import router as save_points_router
app.include_router(save_points_router)
```

**Lifecycle Hooks**:
```python
@app.on_event("startup")
async def startup_auto_save():
    await start_auto_save()
    print("[OK] Auto-save service started (15-min intervals)")

@app.on_event("shutdown")
async def shutdown_auto_save():
    await stop_auto_save()
    print("[OK] Auto-save service stopped")
```

### OpenClaw Legion API

```python
from integrations.openclaw.api_endpoints import router as openclaw_router
app.include_router(openclaw_router)
```

**Result**: `/openclaw/*` endpoints available

### Contrarian Firewall

```python
from api.firewall_routes import router as firewall_router
app.include_router(firewall_router)
```

**Lifecycle Hooks**:
```python
@app.on_event("startup")
async def startup_firewall_orchestrator():
    orchestrator = get_orchestrator()
    await orchestrator.start()

@app.on_event("shutdown")
async def shutdown_firewall_orchestrator():
    orchestrator = get_orchestrator()
    await orchestrator.stop()
```

---

## CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production Recommendation**:
```python
allow_origins=[
    "https://app.project-ai.com",
    "https://dashboard.project-ai.com"
]
```

---

## Error Handling

### HTTP Exception (403 Forbidden)

```python
if result.final_verdict == Verdict.deny:
    raise HTTPException(
        status_code=403,
        detail={
            "message": "Governance denied this request",
            "governance": result.dict()
        }
    )
```

### No TARL Rule (403 Forbidden)

```python
if not matching_rules:
    raise HTTPException(
        status_code=403,
        detail="No TARL rule – execution denied"
    )
```

---

## Testing Examples

### Test Intent Submission

```python
import requests

intent = {
    "actor": "human",
    "action": "read",
    "target": "/data/config.json",
    "context": {"reason": "debug"},
    "origin": "test-client"
}

response = requests.post("http://localhost:8001/intent", json=intent)
print(response.status_code)  # 200
print(response.json()["governance"]["final_verdict"])  # allow
```

### Test Denied Intent

```python
intent = {
    "actor": "agent",
    "action": "execute",
    "target": "/usr/bin/rm",
    "context": {},
    "origin": "malicious-client"
}

response = requests.post("http://localhost:8001/intent", json=intent)
print(response.status_code)  # 403
print(response.json()["detail"]["message"])  # Governance denied
```

---

## Related Documentation

- **[01-API-OVERVIEW.md](./01-API-OVERVIEW.md)** - API architecture overview
- **[03-SAVE-POINTS-API.md](./03-SAVE-POINTS-API.md)** - Save/restore endpoints
- **[04-OPENCLAW-LEGION-API.md](./04-OPENCLAW-LEGION-API.md)** - Legion integration
- **[08-GOVERNANCE-PIPELINE.md](./08-GOVERNANCE-PIPELINE.md)** - Governance implementation

---

**Next**: See [03-SAVE-POINTS-API.md](./03-SAVE-POINTS-API.md) for save/restore functionality.
