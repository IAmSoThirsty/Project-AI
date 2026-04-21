---
title: "Governance System Integration Matrix"
type: governance_relationships
scope: integration
created: 2025-06-01
audience: [developers, architects]
tags: [integration, dependencies, api, interfaces]
---

# Governance System Integration Matrix

## Executive Summary

This document maps integration points, APIs, and dependencies between the 8 governance systems and the rest of Project-AI's architecture. It serves as a comprehensive reference for understanding how governance is woven into every layer of the system.

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   Web    │  │ Desktop  │  │   CLI    │  │  Agents  │        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼───────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────────┐
│                     ROUTING LAYER                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  route_request(source, context)                            │ │
│  │  - Normalizes request format                               │ │
│  │  - Adds tracing metadata                                   │ │
│  │  - Forwards to Pipeline                                    │ │
│  └────────────────────┬───────────────────────────────────────┘ │
└───────────────────────┼─────────────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────────────┐
│                   GOVERNANCE LAYER (Core)                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ [1] [[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|Pipeline System]] (enforce_pipeline)                     │ │
│  │  ├─ Phase 1: Validate                                      │ │
│  │  │   ├─► [6] Action Registry                               │ │
│  │  │   └─► Validators (sanitize, schema)                     │ │
│  │  ├─ Phase 2: Simulate                                      │ │
│  │  ├─ Phase 3: Gate                                          │ │
│  │  │   ├─► [2] RBAC (access_control.py)                      │ │
│  │  │   ├─► Four Laws (ai_systems.py)                         │ │
│  │  │   ├─► [7] Rate Limiting (embedded)                      │ │
│  │  │   ├─► [8] Quotas (tier_governance_policies.py)          │ │
│  │  │   └─► [5] TARL (kernel/tarl_gate.py)                    │ │
│  │  ├─ Phase 4: Execute                                       │ │
│  │  ├─ Phase 5: Commit                                        │ │
│  │  └─ Phase 6: Log                                           │ │
│  │      ├─► [3] Audit (audit_log.py)                          │ │
│  │      └─► [4] Sovereign Data (sovereign_runtime.py)         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────────────┐
│                   EXECUTION LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  AI Systems  │  │  Data Ops    │  │  System Ops  │          │
│  │  (AI engine) │  │  (Storage)   │  │  (Config)    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## System-to-System Integration Map

### Pipeline → All Other Systems

**Integration Type**: Central coordinator (hub)

```python
# Pipeline imports all governance systems
from app.core.access_control import get_access_control  # RBAC
from app.core.ai_systems import [[src/app/core/ai_systems.py]]                # Ethics
from app.governance.audit_log import AuditLog           # Audit
from app.core.tier_governance_policies import get_tier_enforcer  # Quotas
from kernel.tarl_gate import TarlGate                   # TARL
```

**Invocation Points:**

| Phase | System Called | Function | Purpose |
|-------|---------------|----------|---------|
| Validate | Action Registry | Inline check | Whitelist enforcement |
| Validate | Validators | `sanitize_payload()` | XSS/injection prevention |
| Gate | RBAC | `get_access_control().has_role()` | Role checking |
| Gate | Four Laws | `[[relationships/core-ai/01-FourLaws-Relationship-Map.md|FourLaws]].validate_action()` | Ethics compliance |
| Gate | Rate Limiting | `_check_rate_limit()` (inline) | Throttling |
| Gate | Quotas | `get_tier_enforcer().check_quota()` | Resource limits |
| Gate | TARL | `TarlGate.enforce()` | Policy evaluation |
| Log | Audit | `AuditLog().log_event()` | Cryptographic logging |
| Log | Sovereign Data | `SovereignRuntime.update_bundle()` | Compliance bundles |

---

### RBAC → User Manager

**Integration Type**: Data dependency

```python
# RBAC uses UserManager for role storage
from app.core.user_manager import UserManager

class AccessControlManager:
    def has_role(self, user: str, role: str) -> bool:
        # Check local storage first
        if user in self._users and role in self._users[user]:
            return True
        
        # Fallback to UserManager
        user_manager = UserManager()
        user_data = user_manager.users.get(user, {})
        return user_data.get("role") == role
```

**Data Flow:**
```
User Registration (user_manager.py)
    └─► Save to data/users.json {username: {role: "user"}}
        └─► RBAC reads from data/users.json or data/access_control.json
            └─► Pipeline Gate phase uses RBAC
```

---

### TARL → Codex Council

**Integration Type**: Escalation handler

```python
# TARL escalates to Codex for complex decisions
from src.cognition.codex.escalation import CodexDeus
from kernel.tarl_codex_bridge import TarlCodexBridge

class TarlGate:
    def __init__(self, runtime: TarlRuntime, codex: CodexDeus):
        self.codex_bridge = TarlCodexBridge(codex)
    
    def enforce(self, execution_context):
        decision = self.runtime.evaluate(execution_context)
        
        if decision.verdict == TarlVerdict.ESCALATE:
            # Send to Codex council for human review
            self.codex_bridge.handle(decision, execution_context)
            raise TarlEnforcementError(f"Escalated: {decision.reason}")
```

**Escalation Flow:**
```
TARL Policy Evaluation
    ├─ Deterministic? → ALLOW/DENY
    └─ Ambiguous? → ESCALATE
        └─► Codex Council (human review)
            ├─ Consensus required (3/5 council members)
            └─ Decision recorded in [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]]
```

---

### Audit → Sovereign Data

**Integration Type**: Data pipeline

```python
# [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] feeds into sovereign compliance bundles
from app.governance.audit_log import AuditLog

class SovereignRuntime:
    def generate_compliance_bundle(self):
        audit = AuditLog()
        events = audit.load_all_events()  # Import all logged events
        
        bundle = {
            "events": events,
            "hash_chain": audit.verify_chain(),
            "signature": self._sign_bundle(events),
        }
        
        return self._export_bundle(bundle)
```

**Data Flow:**
```
Action Executed
    └─► Pipeline Phase 6: Log
        └─► Audit: Append to audit_log.yaml (SHA-256 chained)
            └─► Sovereign Data: Periodically import events
                └─► Generate compliance bundle (signed ZIP)
                    └─► Third-party verifier can validate
```

---

### Quotas → Tier Enforcement

**Integration Type**: Policy enforcement

```python
# Quotas use tier governance policies
from app.core.tier_governance_policies import (
    PolicyLevel, BlockType, TierEnforcer
)

class ResourceQuotaManager:
    def check_quota(self, tier: int, action: str) -> dict:
        enforcer = TierEnforcer()
        
        # Check for active blocks
        if enforcer.is_blocked(tier):
            return {"allowed": False, "reason": "Tier blocked by Tier 2"}
        
        # Check resource budget
        usage = self._get_tier_usage(tier)
        quota = self._get_tier_quota(tier)
        
        if usage >= quota:
            return {"allowed": False, "reason": "Quota exceeded"}
        
        return {"allowed": True}
```

**Tier Hierarchy:**
```
Tier 1 (Governance)
    ├─ Can block Tier 2 and Tier 3
    ├─ Unlimited quotas
    └─ No rate limits

Tier 2 (Infrastructure)
    ├─ Can block Tier 3 temporarily (<5 min autonomous)
    ├─ High quotas (80% CPU, 16GB RAM)
    └─ Subject to rate limits

Tier 3 (Applications)
    ├─ Cannot block any tier
    ├─ Limited quotas (20% CPU, 4GB RAM)
    └─ Subject to rate limits and Tier 2 blocks
```

---

## API Reference

### Pipeline API

#### `enforce_pipeline(context: dict) -> Any`

**Purpose**: Execute 6-phase [[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|governance pipeline]]  
**Location**: `src/app/core/governance/pipeline.py`

**Input Context Schema:**
```python
{
    "source": str,           # "web" | "desktop" | "cli" | "agent" | "temporal"
    "action": str,           # Action from VALID_ACTIONS registry
    "payload": dict,         # Action-specific data
    "user": dict | None,     # {"username": str, "role": str} or None (resolved in Gate)
    "config": dict | None,   # Optional configuration overrides
}
```

**Returns**: Action result (type depends on action)

**Raises:**
- `ValueError`: Validation failure (Phase 1)
- `PermissionError`: Authorization failure (Phase 3)
- `RuntimeError`: Execution failure (Phase 4)

**Example:**
```python
from app.core.governance.pipeline import enforce_pipeline

result = enforce_pipeline({
    "source": "web",
    "action": "ai.chat",
    "payload": {"prompt": "Hello, AI!"},
    "user": {"username": "alice", "role": "user"},
})
# result = {"response": "Hello! How can I help you?"}
```

---

### RBAC API

#### `get_access_control() -> AccessControlManager`

**Purpose**: Get singleton RBAC manager  
**Location**: `src/app/core/access_control.py`

**Methods:**

##### `has_role(user: str, role: str) -> bool`
Check if user has a specific role.

```python
from app.core.access_control import get_access_control

access = get_access_control()
if access.has_role("alice", "admin"):
    print("Alice is an admin")
```

##### `grant_role(user: str, role: str) -> None`
Grant a role to a user.

```python
access.grant_role("bob", "integrator")
```

##### `revoke_role(user: str, role: str) -> None`
Revoke a role from a user.

```python
access.revoke_role("charlie", "admin")
```

**Storage**: `data/access_control.json`

---

### Audit API

#### `class AuditLog`

**Purpose**: Cryptographic audit logging  
**Location**: `src/app/governance/audit_log.py`

**Constructor:**
```python
from app.governance.audit_log import AuditLog

audit = AuditLog(log_file=Path("custom_audit.yaml"))  # Optional custom path
```

**Methods:**

##### `log_event(event_type: str, data: dict, severity: str = "info", user: str | None = None, source: str | None = None) -> str`

Log an event with cryptographic chaining.

```python
audit.log_event(
    event_type="custom_action",
    data={"key": "value"},
    severity="warning",
    user="alice",
    source="web",
)
# Returns: "a1b2c3..." (event hash)
```

##### `load_all_events() -> list[dict]`

Load all events from [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]].

```python
events = audit.load_all_events()
for event in events:
    print(event["event_type"], event["timestamp"])
```

##### `verify_chain() -> tuple[bool, list]`

Verify integrity of hash chain.

```python
is_valid, corrupt_events = audit.verify_chain()
if not is_valid:
    print(f"Tampering detected: {corrupt_events}")
```

---

### TARL API

#### `class TarlGate`

**Purpose**: Policy-as-code enforcement  
**Location**: `kernel/tarl_gate.py`

**Constructor:**
```python
from kernel.tarl_gate import TarlGate
from tarl import TarlRuntime
from src.cognition.codex.escalation import CodexDeus

runtime = TarlRuntime(policy_dir="tarl/policies")
codex = CodexDeus()
gate = TarlGate(runtime, codex)
```

**Methods:**

##### `enforce(execution_context: dict) -> TarlDecision`

Evaluate policies and enforce verdict.

```python
try:
    decision = gate.enforce({
        "action": "data.export",
        "user": {"username": "alice", "role": "user"},
        "data": {"classification": "confidential"},
    })
    print(f"Verdict: {decision.verdict}")
except TarlEnforcementError as e:
    print(f"Blocked: {e}")
```

**Verdicts:**
- `TarlVerdict.ALLOW`: Action permitted
- `TarlVerdict.DENY`: Action blocked
- `TarlVerdict.ESCALATE`: Requires human review

---

### Quotas API

#### `get_tier_enforcer() -> TierEnforcer`

**Purpose**: Get tier governance enforcer  
**Location**: `src/app/core/tier_governance_policies.py`

**Methods:**

##### `check_quota(tier: int, action: str, context: dict) -> dict`

Check resource quotas for tier.

```python
from app.core.tier_governance_policies import get_tier_enforcer

enforcer = get_tier_enforcer()
result = enforcer.check_quota(tier=3, action="ai.image", context={})

if not result["allowed"]:
    print(f"Quota exceeded: {result['reason']}")
```

##### `impose_block(tier: int, reason: str, duration: int = 300) -> None`

Impose temporary block on tier.

```python
enforcer.impose_block(tier=3, reason="resource_exhaustion", duration=300)
# Blocks Tier 3 for 5 minutes
```

##### `lift_block(tier: int) -> None`

Lift active block on tier.

```python
enforcer.lift_block(tier=3)
```

---

## Data Flow Diagrams

### Request Processing Flow

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│  Router Layer    │
│  Normalize ctx   │
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  Pipeline Phase 1: VALIDATE                  │
│  ├─ Action Registry: "ai.chat" ✓             │
│  ├─ Sanitize: HTML escape                    │
│  └─ Schema: Require "prompt" ✓               │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  Pipeline Phase 2: SIMULATE                  │
│  ├─ Impact: "medium"                         │
│  ├─ Resources: {network: "high"}             │
│  └─ Risk: "low"                              │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  Pipeline Phase 3: GATE (AUTHORIZATION)      │
│  ├─ RBAC: user.role == "user" ✓              │
│  ├─ Four Laws: No harm ✓                     │
│  ├─ Rate Limit: 5/30 requests ✓              │
│  ├─ Quotas: 12% of 20% CPU ✓                 │
│  └─ TARL: ALLOW ✓                            │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  Pipeline Phase 4: EXECUTE                   │
│  └─ AI Engine: Generate response             │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  Pipeline Phase 5: COMMIT                    │
│  └─ Memory: Save conversation                │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│  Pipeline Phase 6: LOG                       │
│  ├─ Audit: Append event (SHA-256 chain)      │
│  └─ Sovereign: Update bundle                 │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────┐
│  Return Result   │
└──────────────────┘
```

### Rate Limiting Data Flow

```
Request arrives
    │
    ├─► Build key: "{source}:{user}:{action}"
    │   Example: "web:alice:ai.chat"
    │
    ├─► Load request history from memory
    │   [{timestamp: 2025-01-01T10:00:00}, {timestamp: 2025-01-01T10:01:00}, ...]
    │
    ├─► Remove timestamps outside window
    │   Window: 60 seconds (for "ai.chat")
    │   Current time: 2025-01-01T10:02:00
    │   After cleanup: [{2025-01-01T10:01:00}, {2025-01-01T10:01:30}]
    │
    ├─► Count remaining requests: 2
    │
    ├─► Check against limit: 30/min
    │   2 < 30 → PASS
    │
    ├─► Record current timestamp
    │   [{2025-01-01T10:01:00}, {2025-01-01T10:01:30}, {2025-01-01T10:02:00}]
    │
    └─► Save updated history (in-memory)
```

### Audit Chain Data Flow

```
Event occurs
    │
    ├─► Load last_hash from audit_log.yaml
    │   last_hash = "a1b2c3..."
    │
    ├─► Build event data
    │   {
    │     timestamp: "2025-01-01T10:00:00Z",
    │     event_type: "action_executed",
    │     data: {...},
    │     prev_hash: "a1b2c3..."
    │   }
    │
    ├─► Compute hash = SHA-256(event_data + prev_hash)
    │   hash = "d4e5f6..."
    │
    ├─► Append to audit_log.yaml
    │   ---
    │   timestamp: ...
    │   prev_hash: a1b2c3...
    │   hash: d4e5f6...
    │   ---
    │
    └─► Update last_hash for next event
        last_hash = "d4e5f6..."
```

---

## Integration Testing

### Test Harness

**File**: `tests/test_governance_integration.py`

```python
import pytest
from app.core.governance.pipeline import enforce_pipeline

def test_full_pipeline_integration():
    """Test complete request flow through all governance systems."""
    
    # Setup: Create test user
    from app.core.access_control import get_access_control
    access = get_access_control()
    access.grant_role("test_user", "user")
    
    # Execute: Run through pipeline
    result = enforce_pipeline({
        "source": "test",
        "action": "ai.chat",
        "payload": {"prompt": "Hello"},
        "user": {"username": "test_user", "role": "user"},
    })
    
    # Assert: Result returned successfully
    assert result is not None
    
    # Verify: [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] contains event
    from app.governance.audit_log import AuditLog
    audit = AuditLog()
    events = audit.load_all_events()
    
    chat_events = [e for e in events if e["event_type"] == "action_executed"]
    assert len(chat_events) > 0
    assert chat_events[-1]["data"]["action"] == "ai.chat"
```

### Integration Test Matrix

| Test | Systems Under Test | Assertion |
|------|-------------------|-----------|
| `test_rbac_integration` | Pipeline + RBAC | Admin can delete users, regular user cannot |
| `test_rate_limit_integration` | Pipeline + Rate Limiting | 31st request in 1 minute is rejected |
| `test_quota_integration` | Pipeline + Quotas | Tier 3 blocked when Tier 2 imposes block |
| `test_audit_integration` | Pipeline + Audit + Sovereign | Events logged and included in compliance bundle |
| `test_tarl_integration` | Pipeline + TARL + Codex | Escalation triggers Codex review |
| `test_four_laws_integration` | Pipeline + Four Laws | Harmful action is blocked |

---

## Performance Considerations

### Overhead by Phase

| Phase | Average Latency | Overhead | Optimization |
|-------|----------------|----------|--------------|
| Validate | 2-5ms | Low | In-memory checks |
| Simulate | 1-3ms | Low | Prediction only |
| Gate (RBAC) | 1-2ms | Low | Cached roles |
| Gate (Rate Limit) | 3-5ms | Medium | In-memory state (Redis in prod) |
| Gate (TARL) | 5-20ms | Medium-High | Policy caching |
| Execute | Variable | N/A | Depends on action |
| Commit | 5-10ms | Medium | Async writes |
| Log | 10-20ms | Medium | Batched writes |

**Total Governance Overhead**: ~30-70ms per request (acceptable for most use cases)

### Scaling Strategies

**Horizontal Scaling:**
- Rate Limiting: Use Redis cluster (shared state)
- [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]]: Shard by date (one log file per day)
- RBAC: Cache roles in memory (TTL: 5 minutes)

**Vertical Scaling:**
- Pipeline: Multi-threaded (Python asyncio)
- TARL: Pre-compile policies (JIT evaluation)
- Audit: Async writes (queue + background worker)

---

## Related Systems

### Core AI Integration
- **[[relationships/core-ai/01-FourLaws-Relationship-Map.md|FourLaws]]**: Ethics framework integration point
- **[[relationships/core-ai/02-AIPersona-Relationship-Map.md|AIPersona]]**: Personality system dependencies
- **[[relationships/core-ai/03-[[relationships/core-ai/03-MemoryExpansionSystem-Relationship-Map.md|MemoryExpansionSystem]]-Relationship-Map|MemoryExpansion]]**: Knowledge storage integration
- **[[relationships/core-ai/04-[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]]-Relationship-Map|LearningRequest]]**: Learning workflow integration
- **[[relationships/core-ai/05-[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]-Relationship-Map|[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]]]**: Plugin system integration
- **[[relationships/core-ai/06-CommandOverride-Relationship-Map.md|CommandOverride]]**: Override system integration

### Governance Integration
- **[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW|Pipeline System]]]]**: All 8 governance systems mapped
- **[[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md|Policy Enforcement]]**: All 6 PEPs documented
- **[[relationships/governance/03_AUTHORIZATION_FLOWS.md|[[relationships/governance/03_AUTHORIZATION_FLOWS|authorization flows]]]]**: Authorization integration points
- **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|[[relationships/governance/04_AUDIT_TRAIL_GENERATION|audit trail]]]]**: Audit logging integration

### Constitutional Integration
- **[[relationships/constitutional/01_constitutional_systems_overview.md|[[relationships/constitutional/01_constitutional_systems_overview|Constitutional AI]]]]**: Constitutional framework
- **[[relationships/constitutional/02_enforcement_chains.md|[[relationships/constitutional/02_enforcement_chains|enforcement chains]]]]**: Ethics enforcement integration
- **[[relationships/constitutional/03_ethics_validation_flows.md|[[relationships/constitutional/03_ethics_validation_flows|ethics validation]]]]**: Validation workflow integration

---

**Document Status**: Production-ready, all integrations documented
**Last Updated**: 2025-06-01  
**Maintained By**: AGENT-053 (Governance Relationship Mapping Specialist)
