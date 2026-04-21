---
title: "[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]] - Core Relationship Map"
agent: AGENT-052
mission: Core AI Relationship Mapping
created: 2026-04-20
last_verified: 2026-04-20
review_cycle: Monthly
status: Active
stakeholder_review_required: Ethics, Security, Legal
---

# [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]] - Comprehensive Relationship Map

## Executive Summary

[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]] implements **human-in-the-loop learning governance**, managing AI requests to acquire new knowledge with approval workflows, [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] content filtering, and SQLite persistence. It ensures AI cannot autonomously learn harmful or denied content.

---

## 1. WHAT: Component Functionality & Boundaries

### Core Responsibilities

1. **Learning Request Lifecycle**
   - Create: `create_request(topic, description, priority)` → returns `req_id`
   - Approve: `approve_request(req_id, response)` → marks approved + triggers listeners
   - Deny: `deny_request(req_id, reason, to_vault=True)` → marks denied + optional vault
   - Status: PENDING → APPROVED/DENIED (enum-based state machine)

2. **[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] (Content Filtering)**
   - SHA-256 hashes of denied content
   - Blocks re-submission of denied topics
   - Persistent storage in SQLite `black_vault` table
   - Automatic addition on `deny_request(to_vault=True)`

3. **Approval Listener System**
   - `register_approval_listener(callback)` → callback invoked on approval
   - Async notification via bounded queue (200 max) + thread pool (4 workers)
   - Non-blocking: GUI/API don't wait for listeners
   - Use case: Trigger learning pipeline, update dashboards, send notifications

4. **Priority System**
   - Three levels: LOW (1), MEDIUM (2), HIGH (3)
   - Used for sorting/filtering (not automatic escalation)
   - Set at creation time, immutable

5. **Persistence**
   - SQLite database: `data/learning_requests/requests.db`
   - Two tables: `requests` (id, topic, description, priority, status, created, response, reason)
   - `black_vault` (hash)
   - Auto-save on `create_request()`, `approve_request()`, `deny_request()`
   - Legacy JSON migration on first load

### Boundaries & Limitations

- **Does NOT**: Execute learning (delegates to listeners)
- **Does NOT**: Validate content safety (only hash-based vault check)
- **Does NOT**: Support request editing (immutable once created)
- **Does NOT**: Implement approval routing (single approver model)
- **Does NOT**: Provide undo/restore functionality

### Data Structure

```python
# Request Object (in-memory dict)
{
    "topic": "Python asyncio",
    "description": "Learn async/await syntax and best practices",
    "priority": 2,  # RequestPriority.MEDIUM.value
    "status": "pending",  # RequestStatus enum value
    "created": "2026-04-20T14:30:00.123456",
    "response": None,  # Set on approval
    "reason": None,  # Set on denial
    "correlation_id": "abc123..."  # Added on approval (for tracing)
}

# SQLite Schema
CREATE TABLE requests (
    id TEXT PRIMARY KEY,
    topic TEXT,
    description TEXT,
    priority INTEGER,
    status TEXT,
    created TEXT,
    response TEXT,
    reason TEXT
);

CREATE TABLE black_vault (
    hash TEXT PRIMARY KEY
);
```

---

## 2. WHO: Stakeholders & Decision-Makers

### Primary Stakeholders

| Stakeholder | Role | Authority Level | Decision Power |
|------------|------|----------------|----------------|
| **Ethics Board** | Approval policy design | CRITICAL | Defines what AI can learn |
| **Security Team** | Vault management | HIGH | Can audit/purge vault |
| **Legal Compliance** | Regulatory alignment | OVERSIGHT | Can block learning categories |
| **Core Developers** | Implementation | IMPLEMENTATION | Bug fixes, features |
| **End Users** | Request creators | EXPERIENCE | Submit requests, see status |

### User Classes

1. **Request Creators**
   - End users (via GUI learning request panel)
   - AI systems (autonomous learning triggers)
   - Plugins (request learning for capabilities)

2. **Request Approvers**
   - System administrators (manual approval workflow)
   - Ethics reviewers (policy-based approval)
   - Automated approval bots (future: ML-based pre-screening)

3. **Listener Consumers**
   - Learning pipelines (`[[src/app/core/learning_paths.py]]`)
   - Continuous learning engine (`continuous_learning.py`)
   - Dashboard widgets (request status updates)
   - Telemetry systems (analytics)

### Maintainer Responsibilities

- **Code Owners**: @ethics-team, @core-ai-team
- **Review Requirements**: 1 ethics + 1 core developer
- **Change Frequency**: Monthly (policy), quarterly (features)
- **On-Call**: Business hours (non-critical)

---

## 3. WHEN: Lifecycle & Review Cycle

### Creation & Evolution

| Date | Event | Version | Changes |
|------|-------|---------|---------|
| 2024-Q4 | Initial Implementation | 1.0.0 | Basic approval workflow + JSON storage |
| 2025-Q2 | [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] System | 1.2.0 | SHA-256 content filtering |
| 2025-Q4 | SQLite Migration | 1.5.0 | Replaced JSON with database |
| 2026-Q1 | Async Listeners | 1.7.0 | Non-blocking notification system |
| 2026-Q2 | Correlation IDs | 1.8.0 | Request tracing for debugging |

### Review Schedule

- **Daily**: Automated tests (3 tests in test_ai_systems.py)
- **Weekly**: Pending request queue monitoring
- **Monthly**: Ethics review of denied requests (vault audit)
- **Quarterly**: Full approval policy review

### Lifecycle Stages

```mermaid
graph LR
    A[AI/User Creates Request] --> B{[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] Check}
    B -->|Blocked| C[Return Empty ID]
    B -->|Allowed| D[Generate req_id]
    D --> E[Save to SQLite]
    E --> F[Status: PENDING]
    F --> G{Human Review}
    G -->|Approve| H[approve_request()]
    G -->|Deny| I[deny_request()]
    H --> J[Trigger Listeners]
    H --> K[Status: APPROVED]
    I --> L{Add to Vault?}
    L -->|Yes| M[Hash → [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]]]
    L -->|No| N[Status: DENIED]
    M --> N
```

### State Persistence Triggers

- **On Create**: `create_request()` → `_save_requests()` (immediate)
- **On Approve**: `approve_request()` → `_save_requests()` (after listeners queued)
- **On Deny**: `deny_request()` → `_save_requests()` (after vault update)
- **No Periodic Saves**: All writes are transactional

---

## 4. WHERE: File Paths & Integration Points

### Source Code Locations

```
Primary Implementation:
  src/app/core/ai_systems.py
    - Lines 692-986: [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]] class
    - Lines 695-709: RequestStatus, RequestPriority enums
    - Lines 720-750: __init__, DB setup, JSON migration
    - Lines 769-824: _load_requests(), _save_requests()
    - Lines 886-965: create_request(), approve_request(), deny_request()
    - Lines 746-767: Approval listener system

Extended Learning Features:
  src/app/core/[[src/app/core/learning_paths.py]] (OpenAI-powered path generation)
  src/app/core/continuous_learning.py (ContinuousLearningEngine)
  src/app/core/advanced_learning_systems.py (ML-based screening)

Test Suite:
  tests/test_ai_systems.py
    - Lines 85-106: TestLearningRequests class (3 tests)
  tests/test_learning_requests_extended.py
  tests/test_integration_user_learning.py
```

### Integration Points

```python
# Direct Consumers (import [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]])
src/app/plugins/codex_adapter.py:14
src/app/gui/dashboard_main.py:21
src/app/core/governance/pipeline.py:749, 766

# Dependency Graph
[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]]
  ├── SQLite (requests.db)
  ├── ThreadPoolExecutor (listener notifications)
  ├── hashlib (SHA-256 for [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]])
  ├── DashboardMain (GUI approval interface)
  ├── GovernancePipeline (policy enforcement)
  └── ContinuousLearningEngine (approval listener)
```

### Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│ AI DETECTS KNOWLEDGE GAP                                     │
│ - Example: User asks about Rust programming                 │
│ - AI doesn't know Rust                                      │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ manager.create_request(                                      │
│   topic="Rust Programming",                                  │
│   description="Learn Rust syntax, ownership model...",       │
│   priority=RequestPriority.MEDIUM                            │
│ )                                                            │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] CHECK                                            │
│ - Hash description: SHA-256("Learn Rust...")                │
│ - Check: content_hash in self.black_vault?                  │
│ - If blocked: return "" (empty ID)                          │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ GENERATE req_id                                              │
│ - req_id = SHA-256(timestamp + topic)[:12]                  │
│ - Create request object with status=PENDING                 │
│ - Save to SQLite                                            │
│ - Return req_id                                             │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ HUMAN REVIEW (via GUI Dashboard)                            │
│ - Admin sees pending request in approval panel              │
│ - Reviews topic, description, priority                      │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
                   ┌───┴────┐
                   │APPROVE?│
                   └───┬────┘
            ┌──────────┴──────────┐
            ↓                     ↓
    ┌───────────────┐     ┌──────────────┐
    │ APPROVE       │     │ DENY         │
    │ - Status:     │     │ - Status:    │
    │   APPROVED    │     │   DENIED     │
    │ - Queue       │     │ - Add to     │
    │   listeners   │     │   vault      │
    └───────┬───────┘     └──────┬───────┘
            ↓                    ↓
    ┌───────────────┐     ┌──────────────┐
    │ LISTENERS     │     │ [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]]  │
    │ - Learning    │     │ - Hash stored│
    │   pipeline    │     │ - Future     │
    │   executes    │     │   requests   │
    │ - Dashboard   │     │   blocked    │
    │   updates     │     └──────────────┘
    └───────────────┘
```

### Environment Dependencies

- **Python Version**: 3.11+ (sqlite3 in stdlib)
- **Required Packages**: None (stdlib only)
- **Optional Dependencies**: `telemetry.py` (send_event, optional)
- **Configuration**: 
  - `data_dir` (constructor parameter, default: "data")
  - SQLite file: `{data_dir}/learning_requests/requests.db`

---

## 5. WHY: Problem Solved & Design Rationale

### Problem Statement

**Challenge**: How do we enable AI to learn autonomously while preventing:
1. Acquisition of harmful/illegal knowledge
2. Unvetted sources of information
3. Bias reinforcement through unchecked learning
4. Resource exhaustion (learning everything)

**Requirements**:
1. Human oversight for all learning requests
2. Permanent blocking of denied content ([[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]])
3. [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]] for compliance (who approved what, when)
4. Non-blocking approval workflow (don't freeze app)
5. Scalable to 1000s of requests

### Design Rationale

#### Why Human-in-the-Loop vs. Automated Approval?
- **Decision**: Manual approval required for all requests
- **Rationale**: 
  - AI cannot judge safety of learning material (alignment problem)
  - Ethics board must review edge cases
  - Legal liability for harmful content
- **Tradeoff**: Slower learning, requires human availability

#### Why [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] (SHA-256 Hashing)?
- **Decision**: Hash denied content instead of storing full text
- **Rationale**: 
  - Privacy: don't persist harmful content descriptions
  - Efficiency: O(1) lookup via hash table
  - Immutability: hashes prevent re-approval attempts
- **Tradeoff**: Cannot reverse-lookup original content (by design)

#### Why SQLite Instead of JSON?
- **Decision**: Migrated from JSON to SQLite in v1.5.0
- **Rationale**: 
  - ACID transactions (no partial writes)
  - Concurrent access (multiple threads/processes)
  - Indexes for fast queries (future: filter by priority)
  - Migration path: legacy JSON auto-migrated
- **Tradeoff**: Binary format (less human-readable than JSON)

#### Why Async Listener Notifications?
- **Decision**: Queue-based async notifications vs. synchronous callbacks
- **Rationale**: 
  - GUI doesn't freeze during approval (long-running learning pipelines)
  - Bounded queue (200 max) prevents memory exhaustion
  - Thread pool (4 workers) limits resource usage
- **Tradeoff**: Listeners cannot block approval (must handle async)

### Architectural Tradeoffs

| Decision | Benefit | Cost | Mitigation |
|----------|---------|------|------------|
| Human-in-the-loop | Safety guarantee | Slow learning | Batch approval workflows |
| [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] | Permanent blocking | Cannot audit reasons | External [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] |
| SQLite persistence | ACID + concurrency | Binary format | Backup scripts, export tools |
| Async listeners | Non-blocking UI | Complex error handling | Listener exception logging |

### Alternative Approaches Considered

1. **Automated Approval (ML Screening)** (REJECTED)
   - Would speed up learning
   - Con: Cannot reliably detect harmful content (adversarial examples)

2. **Content-Based Vault (Full Text)** (REJECTED)
   - Would enable audit of denied requests
   - Con: Privacy risk (storing harmful descriptions)

3. **Distributed Approval (Multi-Reviewer)** (CONSIDERED FOR FUTURE)
   - Would reduce single-approver bottleneck
   - Blocked by: approval routing complexity

4. **Time-Limited Approvals (TTL)** (CONSIDERED FOR FUTURE)
   - Would enable temporary learning (e.g., 30-day access)
   - Blocked by: requires expiration management

---

## 6. Dependency Graph (Technical)

### Upstream Dependencies (What [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]] Needs)

```python
# Standard Library
import os, json, sqlite3, hashlib, logging, queue, threading, uuid, time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor

# Internal Modules
from app.core.telemetry import send_event  # Optional (graceful fallback)

# Correlation ID Generation
from app.core.ai_systems import new_correlation_id
```

### Downstream Dependencies (Who Needs [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]])

```
┌─────────────────────────────────────────┐
│  [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]] (Governance)    │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴─────────┬──────────────┬──────────────┐
        ↓                  ↓              ↓              ↓
┌───────────────┐  ┌──────────────┐  ┌─────────┐  ┌──────────────┐
│ Dashboard     │  │ Governance   │  │ Plugins │  │ Continuous   │
│ (approval UI) │  │ Pipeline     │  │ (codex) │  │ Learning     │
└───────────────┘  └──────────────┘  └─────────┘  └──────────────┘
        │                  │              │              │
        └──────────────────┴──────────────┴──────────────┘
                                    │
                          ┌─────────┴─────────┐
                          ↓                   ↓
                  ┌───────────────┐   ┌─────────────────┐
                  │ Approval      │   │ Learning        │
                  │ Workflow      │   │ Execution       │
                  └───────────────┘   └─────────────────┘
```

### Cross-Module Communication

```python
# Typical Call Stack (Request → Approval → Execution)
1. AI detects knowledge gap → [[src/app/core/intelligence_engine.py]]
2. intelligence_engine → manager.create_request(
     topic="Kubernetes",
     description="Learn container orchestration...",
     priority=RequestPriority.HIGH
   )
3. [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]].create_request() →
     - Checks [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] (SHA-256 hash)
     - Generates req_id
     - Saves to SQLite
     - Returns req_id

4. Admin opens Dashboard → DashboardMain.py
5. DashboardMain → manager.get_pending() → [request objects]
6. Admin clicks "Approve" → manager.approve_request(req_id, "Approved for DevOps course")
7. [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]].approve_request() →
     - Updates status = APPROVED
     - Adds correlation_id
     - Queues notification: _notify_queue.put((req_id, request))
     - Saves to SQLite

8. Background _notify_worker thread →
     - Dequeues (req_id, request)
     - Iterates approval_listeners
     - Submits to ThreadPoolExecutor: cb(req_id, request)

9. ContinuousLearningEngine listener (registered at startup) →
     - Receives notification
     - Fetches learning materials (OpenAI, web scraping, etc.)
     - Updates knowledge base
     - Marks learning complete
```

---

## 7. Stakeholder Matrix

| Stakeholder Group | Interest | Influence | Engagement Strategy |
|------------------|----------|-----------|---------------------|
| **Ethics Board** | CRITICAL (approval policy) | HIGH (veto power) | Every request, quarterly policy review |
| **Security Team** | HIGH (vault management) | HIGH (audit authority) | Monthly vault audit, incident response |
| **Legal Compliance** | HIGH (regulatory) | HIGH (blocking authority) | Quarterly review, legal risk assessment |
| **Core Developers** | MEDIUM (maintenance) | MEDIUM (implementation) | On-demand, PR reviews |
| **End Users** | MEDIUM (learning speed) | LOW (indirect) | Feedback surveys, approval transparency |

---

## 8. Risk Assessment & Mitigation

### Critical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Harmful Content Approval** | LOW | CATASTROPHIC | Ethics review, multi-reviewer (future) |
| **[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] Bypass** | LOW | HIGH | Hash collision detection, audit logging |
| **Approval Bottleneck** | MEDIUM | MEDIUM | Batch approval tools, automated pre-screening |
| **SQLite Corruption** | LOW | MEDIUM | Daily backups, WAL mode (future) |
| **Listener Failure** | MEDIUM | LOW | Exception logging, retry mechanism |

### Incident Response

```
1. Harmful content approved → Emergency revoke, add to vault, ethics review
2. [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] bypass detected → Audit all requests, patch exploit
3. SQLite corruption → Restore from backup, investigate cause
4. Listener crash → Log exception, alert on-call, manual re-trigger
5. Post-mortem → Update approval policy, enhance safeguards
```

---

## 9. Integration Checklist for New Consumers

When integrating [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]]:

- [ ] Import `[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]]` from `app.core.ai_systems`
- [ ] Instantiate with `data_dir` (testing: use tempdir)
- [ ] Call `create_request()` for AI learning needs
- [ ] Register approval listener: `manager.register_approval_listener(callback)`
- [ ] Implement callback signature: `def callback(req_id: str, request: dict) -> None`
- [ ] Handle empty `req_id` ([[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] rejection)
- [ ] Do NOT cache `get_pending()` (query on-demand)
- [ ] Add tests for [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] rejection
- [ ] Document approval policy for your use case
- [ ] Implement graceful degradation if listener fails

---

## 10. Future Roadmap

### Planned Enhancements (Q1 2027)

1. **ML-Powered Pre-Screening**: Auto-approve low-risk requests (scikit-learn classifier)
2. **Multi-Reviewer Workflow**: Require N approvers for high-priority requests
3. **Time-Limited Approvals**: Temporary learning access with auto-expiration
4. **Vault Audit UI**: Dashboard for reviewing denied requests

### Research Areas

- [[relationships/constitutional/01_constitutional_systems_overview.md|Constitutional AI]] approval (automate ethics review)
- Federated learning governance (multi-org approval)
- Explainable approval decisions (why approved/denied)

### NOT Planned (Policy Decisions)

- Fully automated approval (safety risk)
- User-level approval authority (liability risk)
- Vault content export (privacy risk)

---

## 10. API Reference Card

### Constructor
```python
[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]](data_dir: str = "data")
```

### Core Methods
```python
# Request Management
create_request(topic: str, description: str, priority: RequestPriority = MEDIUM) → str
approve_request(req_id: str, response: str) → bool
deny_request(req_id: str, reason: str, to_vault: bool = True) → bool

# Query Methods
get_pending() → list[dict]  # Pending requests only
get_statistics() → dict  # {pending, approved, denied, vault_entries}

# Listener System
register_approval_listener(callback: Callable[[str, dict], None]) → None
```

### State Files
```
data/learning_requests/requests.db  # SQLite database
  - Table: requests (id, topic, description, priority, status, created, response, reason)
  - Table: black_vault (hash)
```

### Thread Safety
- ✅ Safe: `create_request()`, `approve_request()`, `deny_request()` (SQLite serializes writes)
- ✅ Safe: `register_approval_listener()` (append-only list)
- ⚠️ Caution: Listeners execute in separate threads (must be thread-safe)

---

## Related Systems

### Core AI Integration
- **[[relationships/core-ai/01-FourLaws-Relationship-Map.md|FourLaws]]**: Validates learning requests against ethics framework
- **[[relationships/core-ai/02-AIPersona-Relationship-Map.md|AIPersona]]**: Triggers continuous learning integration
- **[[relationships/core-ai/03-[[relationships/core-ai/03-MemoryExpansionSystem-Relationship-Map.md|MemoryExpansionSystem]]-Relationship-Map|MemoryExpansion]]**: Stores approved learning outcomes
- **[[relationships/core-ai/05-[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]-Relationship-Map|[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]]]**: Plugins can request learning
- **[[relationships/core-ai/06-CommandOverride-Relationship-Map.md|CommandOverride]]**: Emergency learning approval bypass

### Governance Integration
- **[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW|Pipeline System]]]]**: Learning requests flow through [[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|governance pipeline]]
- **[[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md|Policy Enforcement]]**: Human-in-the-loop approval enforcement
- **[[relationships/governance/03_AUTHORIZATION_FLOWS.md|[[relationships/governance/03_AUTHORIZATION_FLOWS|authorization flows]]]]**: Admin-level approval authorization
- **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|[[relationships/governance/04_AUDIT_TRAIL_GENERATION|audit trail]]]]**: All approvals/denials logged cryptographically
- **[[relationships/governance/05_SYSTEM_INTEGRATION_MATRIX.md|Integration Matrix]]**: Learning workflow dependencies

### Constitutional Integration
- **[[relationships/constitutional/01_constitutional_systems_overview.md|[[relationships/constitutional/01_constitutional_systems_overview|Constitutional AI]]]]**: Learning aligned with constitutional principles
- **[[relationships/constitutional/02_enforcement_chains.md|[[relationships/constitutional/02_enforcement_chains|enforcement chains]]]]**: [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] enforcement mechanism
- **[[relationships/constitutional/03_ethics_validation_flows.md|[[relationships/constitutional/03_ethics_validation_flows|ethics validation]]]]**: Content filtering workflows

---

## Document Metadata

- **Author**: AGENT-052 (Core AI Relationship Mapping Specialist)
- **Review Date**: 2026-04-20
- **Next Review**: 2026-05-20 (Monthly)
- **Approvers**: Ethics Board Chair, Security Lead, Core AI Lead
- **Classification**: Internal Technical Documentation
- **Version**: 1.0.0
- **Related Documents**: 
  - [[relationships/core-ai/01-FourLaws-Relationship-Map.md]] - [[relationships/constitutional/03_ethics_validation_flows.md|ethics validation]]
  - [[relationships/core-ai/02-AIPersona-Relationship-Map.md]] - Continuous learning trigger
  - [[relationships/core-ai/03-[[relationships/core-ai/03-MemoryExpansionSystem-Relationship-Map.md|MemoryExpansionSystem]]-Relationship-Map]] - Knowledge storage
  - [[relationships/core-ai/05-[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]-Relationship-Map]] - Plugin learning requests
  - [[relationships/core-ai/06-CommandOverride-Relationship-Map.md]] - Emergency override
  - [[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md]] - Governance integration
  - [[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md]] - Approval enforcement
  - [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md]] - Audit logging
  - [[relationships/constitutional/01_constitutional_systems_overview.md]] - Constitutional alignment
  - [[relationships/constitutional/02_enforcement_chains.md]] - [[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|Black Vault]] enforcement
  - [[relationships/constitutional/03_ethics_validation_flows.md]] - Content filtering
  - `LEARNING_REQUEST_IMPLEMENTATION.md`
  - `ETHICS_POLICY.md` (if exists)

---

## Related Documentation

- [[source-docs/core/01-ai_systems.md]]


---

## RELATED SYSTEMS

### GUI Integration ([[../gui/00_MASTER_INDEX|GUI Master Index]])

| GUI Component | Learning Operation | User Flow | Documentation |
|---------------|-------------------|-----------|---------------|
| [[../gui/03_HANDLER_RELATIONSHIPS\|DashboardHandlers]] | Learning path generation | Generate button → create_request() → approval | Section 3 (learning paths) |
| [[../gui/02_PANEL_RELATIONSHIPS\|ProactiveActionsPanel]] | Learning triggers | Action buttons → learning workflows | Section 3 (navigation) |
| [[../gui/01_DASHBOARD_RELATIONSHIPS\|Dashboard]] | Approval UI (future) | Admin panel for request approval | Planned feature |
| [[../gui/05_PERSONA_PANEL_RELATIONSHIPS\|PersonaPanel]] | Curiosity influence | High curiosity → more learning requests | [[02-AIPersona-Relationship-Map|AIPersona]] integration |

### Learning Request Workflow

```
User Clicks "Generate Learning Path" ([[../gui/03_HANDLER_RELATIONSHIPS#learning-path-generation|Handler]]) → 
_on_generate_learning_path(topic) → 
LearningRequestManager.create_request(topic, desc, priority) → 
SQLite Insert + Black Vault Check → 
Admin Approval (Dashboard UI - future) → 
approve_request(req_id) → 
Async Listeners Notify → 
[[../agents/PLANNING_HIERARCHIES|PlannerAgent]] Executes Learning
```

### Agent Integration ([[../agents/README|Agents Overview]])

| Agent System | Learning Role | Purpose | Documentation |
|--------------|---------------|---------|---------------|
| [[../agents/PLANNING_HIERARCHIES\|PlannerAgent]] | Learning execution | Decomposes learning into tasks | Section 2 (decomposition) |
| [[../agents/VALIDATION_CHAINS#layer-2-oversightagent-compliance-validation\|OversightAgent]] | Content compliance | Checks learning content policy | Layer 2 validation |
| [[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation\|Four Laws]] | Ethical learning | Prevents learning harmful content | Layer 3 validation |
| [[../agents/AGENT_ORCHESTRATION#councilhub-coordination\|CouncilHub]] | Approval routing | Multi-agent learning consensus | Section 2 (coordination) |

### Black Vault Integration

Protects against re-learning denied content:

```
Denied Learning Request → 
content_hash = SHA-256(content) → 
Black Vault Set.add(hash) → 
Persist to requests.db → 
Future Requests → Check Black Vault → 
Auto-Reject if Hash Match
```

See [[../agents/VALIDATION_CHAINS#validation-bypass-prevention|Validation Bypass Prevention]] for security details.

### Approval Workflow with Agents

```
AI Detects Knowledge Gap → 
create_request(topic, reason, priority) → 
[[../agents/VALIDATION_CHAINS#layer-2-oversightagent-compliance-validation|OversightAgent.check_policy()]] → 
[[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation|FourLaws.validate_action()]] → 
Dashboard Approval UI (Admin) → 
approve_request() OR deny_request() → 
If Approved: [[../agents/PLANNING_HIERARCHIES|PlannerAgent.schedule_learning()]] → 
Execute → Update [[02-AIPersona-Relationship-Map|AIPersona]] curiosity
```

### Priority Levels in Planning

| Priority | PlannerAgent Behavior | Documentation |
|----------|----------------------|---------------|
| CRITICAL | Immediate execution | [[../agents/PLANNING_HIERARCHIES#priority-based-execution|Priority Execution]] |
| HIGH | Next in queue | Same |
| MEDIUM | Standard scheduling | Same |
| LOW | Background learning | Same |

---

**Generated by:** AGENT-052: Core AI Relationship Mapping Specialist  
**Enhanced by:** AGENT-078: GUI & Agent Cross-Links Specialist  
**Status:** ✅ Cross-linked with GUI and Agent systems