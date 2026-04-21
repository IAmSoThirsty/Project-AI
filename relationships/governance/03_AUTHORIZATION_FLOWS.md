---
title: "[[relationships/governance/03_AUTHORIZATION_FLOWS.md|authorization flows]] - Multi-Path Governance"
type: governance_relationships
scope: authorization
created: 2025-06-01
audience: [security, developers]
tags: [authorization, flow, rbac, authentication]
---

# [[relationships/governance/03_AUTHORIZATION_FLOWS.md|authorization flows]]

## Executive Summary

This document maps all [[relationships/governance/03_AUTHORIZATION_FLOWS.md|authorization flows]] through the [[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|governance pipeline]], covering 5 execution paths:
1. **Web (Flask API)**
2. **Desktop (PyQt6)**
3. **CLI (Command-line)**
4. **Agents (Autonomous)**
5. **Temporal (Workflows)**

Each path converges on the universal [[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|Pipeline System]] for consistent governance.

## Universal Authorization Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXECUTION SOURCES                            │
├─────────────┬─────────────┬──────────┬────────────┬─────────────┤
│    Web      │   Desktop   │   CLI    │   Agents   │  Temporal   │
│  (Flask)    │  (PyQt6)    │  (Bash)  │ (Asyncio)  │ (Workflows) │
└──────┬──────┴──────┬──────┴────┬─────┴─────┬──────┴──────┬──────┘
       │             │           │            │             │
       │             │           │            │             │
       └─────────────┴───────────┴────────────┴─────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │   ROUTER LAYER         │
                     │  (route_request)       │
                     │  Normalizes context    │
                     └───────────┬────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │   [[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|Pipeline System]]      │
                     │  (enforce_pipeline)    │
                     │  6-phase governance    │
                     └───────────┬────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │   GATE PHASE           │
                     │  ├─ RBAC               │
                     │  ├─ Four Laws          │
                     │  ├─ Rate Limiting      │
                     │  ├─ Quotas             │
                     │  └─ TARL               │
                     └───────────┬────────────┘
                                 │
                     ┌───────────▼────────────┐
                     │   EXECUTION            │
                     │  (if authorized)       │
                     └────────────────────────┘
```

## Flow 1: Web Authorization (Flask API)

### Entry Point
- **File**: `src/app/interfaces/web/app.py`
- **Endpoint**: Various routes (`/api/chat`, `/api/login`, etc.)
- **Authentication**: JWT tokens in `Authorization` header

### Authorization Sequence

```
1. HTTP Request arrives at Flask endpoint
   ├─ Example: POST /api/chat
   └─ Headers: Authorization: Bearer <JWT>

2. JWT Verification (Middleware)
   ├─ Extract token from header
   ├─ Verify signature with secret key
   ├─ Check expiration
   │   ├─ Expired? → 401 Unauthorized
   │   └─ Valid? → Extract payload (username, role)
   └─ Attach user context to request

3. Build Pipeline Context
   └─ {
        "source": "web",
        "action": "ai.chat",
        "payload": {"prompt": "...", "token": "<JWT>"},
        "user": None  # Token verification happens in pipeline
      }

4. Route to Pipeline
   ├─ from app.core.runtime.router import route_request
   └─ result = route_request("web", context)

5. Pipeline Processing
   ├─ Phase 1: Validate
   │   ├─ Action Registry: "ai.chat" in VALID_ACTIONS? ✓
   │   ├─ Sanitize: Escape HTML in prompt
   │   └─ Schema: Require "prompt" field? ✓
   │
   ├─ Phase 2: Simulate
   │   ├─ Impact: "medium" (AI operation)
   │   ├─ Resources: network="high"
   │   └─ Risk: "low"
   │
   ├─ Phase 3: Gate (AUTHORIZATION HAPPENS HERE)
   │   ├─ Resolve User Context:
   │   │   ├─ Token in payload? YES
   │   │   ├─ Verify JWT → {username: "alice", role: "user"}
   │   │   └─ context["user"] = {username: "alice", role: "user"}
   │   │
   │   ├─ PEP-5: RBAC Check
   │   │   ├─ Action: "ai.chat"
   │   │   ├─ Required role: "user" or higher
   │   │   ├─ User role: "user"
   │   │   └─ ✓ PASS
   │   │
   │   ├─ PEP-6: Four Laws
   │   │   ├─ Does "ai.chat" harm humans? NO
   │   │   └─ ✓ PASS
   │   │
   │   ├─ PEP-7: Rate Limiting
   │   │   ├─ Key: "web:alice:ai.chat"
   │   │   ├─ Limit: 30 requests/min
   │   │   ├─ Current: 5 requests in window
   │   │   └─ ✓ PASS (under limit)
   │   │
   │   ├─ PEP-8: Quotas
   │   │   ├─ User tier: 3 (application)
   │   │   ├─ CPU budget: 20% available
   │   │   └─ ✓ PASS
   │   │
   │   └─ PEP-9: TARL
   │       ├─ Policy: allow "ai.chat" where user.authenticated
   │       ├─ user.authenticated? YES
   │       └─ ✓ ALLOW
   │
   ├─ Phase 4: Execute
   │   └─ Call AI chat handler → Response generated
   │
   ├─ Phase 5: Commit
   │   └─ Save conversation to memory
   │
   └─ Phase 6: Log
       └─ Audit: {action: "ai.chat", user: "alice", status: "success"}

6. Return Response
   └─ 200 OK with AI response
```

### Authentication Details

**JWT Structure:**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "username": "alice",
    "role": "user",
    "exp": 1735689600,  // Expiration timestamp
    "iat": 1735603200   // Issued at
  },
  "signature": "<HMAC-SHA256 signature>"
}
```

**Token Verification** (`src/app/core/security/auth.py`):
```python
from jwt import decode, InvalidTokenError

def verify_jwt_token(token: str) -> TokenPayload | None:
    try:
        payload = decode(token, SECRET_KEY, algorithms=["HS256"])
        return TokenPayload(
            username=payload["username"],
            role=payload["role"]
        )
    except InvalidTokenError:
        return None  # Invalid or expired
```

### Failure Scenarios

| Failure | Location | Response |
|---------|----------|----------|
| No token | Flask middleware | 401 Unauthorized |
| Invalid token | Pipeline Gate | PermissionError → 401 |
| Expired token | JWT verification | None → 401 |
| Insufficient role | RBAC PEP | PermissionError → 403 |
| Rate limit exceeded | Rate Limit PEP | PermissionError → 429 |
| Quota exhausted | Quota PEP | PermissionError → 402 |

### Security Properties

1. **Token-Based**: Stateless authentication (no server-side sessions)
2. **Short-Lived**: Tokens expire (default: 24 hours)
3. **Role-Embedded**: Role in token (no DB lookup per request)
4. **HTTPS-Only**: Tokens transmitted over TLS
5. **No Bypass**: All routes go through pipeline

---

## Flow 2: Desktop Authorization (PyQt6)

### Entry Point
- **File**: `src/app/gui/leather_book_interface.py`
- **Component**: `LeatherBookInterface` (main window)
- **Authentication**: Username/password at login

### Authorization Sequence

```
1. User logs in via GUI
   ├─ LeatherBookInterface.login_page
   ├─ Input: username, password
   └─ Button: "ENTER THE BOOK"

2. Login Action
   ├─ Signal: login_attempted.emit(username, password)
   └─ Handler: handle_login(username, password)

3. Build Pipeline Context
   └─ {
        "source": "desktop",
        "action": "user.login",
        "payload": {"username": username, "password": password},
        "user": {"username": username, "role": None}  # Role resolved later
      }

4. Route to Pipeline
   ├─ from app.core.runtime.router import route_request
   └─ result = route_request("desktop", context)

5. Pipeline Processing
   ├─ Phase 1: Validate
   │   ├─ Action: "user.login" in VALID_ACTIONS? ✓
   │   ├─ Required fields: ["username", "password"]? ✓
   │   └─ Sanitize: Escape special characters
   │
   ├─ Phase 2: Simulate
   │   ├─ Impact: "low"
   │   ├─ State changes: ["user_database"]
   │   └─ Risk: "medium" (authentication attempt)
   │
   ├─ Phase 3: Gate (AUTHORIZATION HAPPENS HERE)
   │   ├─ UserManager Password Verification:
   │   │   ├─ Load user from data/users.json
   │   │   ├─ Hash input password with bcrypt
   │   │   ├─ Compare with stored hash
   │   │   │   ├─ Match? → Resolve role
   │   │   │   └─ No match? → REJECT (invalid credentials)
   │   │   └─ context["user"]["role"] = "user" (or "admin")
   │   │
   │   ├─ PEP-5: RBAC Check
   │   │   ├─ Action: "user.login"
   │   │   ├─ Required role: None (public action)
   │   │   └─ ✓ PASS (login always allowed)
   │   │
   │   ├─ PEP-7: Rate Limiting
   │   │   ├─ Key: "desktop:alice:user.login"
   │   │   ├─ Limit: 5 requests/min
   │   │   ├─ Current: 2 requests
   │   │   └─ ✓ PASS (brute-force protection active)
   │   │
   │   └─ (Other PEPs not applicable for login)
   │
   ├─ Phase 4: Execute
   │   ├─ Create session token (in-memory, not JWT)
   │   └─ Store user context in LeatherBookInterface
   │
   ├─ Phase 5: Commit
   │   └─ Update last_login in users.json
   │
   └─ Phase 6: Log
       └─ Audit: {action: "user.login", user: "alice", status: "success"}

6. Post-Login Authorization
   ├─ GUI switches to dashboard page
   ├─ User context stored: self.current_user = {"username": "alice", "role": "user"}
   └─ Subsequent actions include user context

7. User Performs Action (e.g., "Generate Image")
   ├─ Button: "🎨 GENERATE IMAGES"
   ├─ Signal: actions_panel.image_gen_requested.emit()
   └─ Handler: switch_to_image_generation()

8. Build Pipeline Context for Action
   └─ {
        "source": "desktop",
        "action": "ai.image",
        "payload": {"prompt": "...", "style": "photorealistic"},
        "user": self.current_user  # {"username": "alice", "role": "user"}
      }

9. Route to Pipeline
   └─ result = route_request("desktop", context)

10. Pipeline Processing (Same as Web)
    ├─ Validate → Simulate → Gate
    ├─ RBAC: User has "user" role → ✓ PASS
    ├─ Rate Limiting: 10/hour → Check count → ✓ PASS
    └─ Execute → Image generated
```

### Authentication Details

**Password Hashing** (`src/app/core/user_manager.py`):
```python
import bcrypt

def _hash_and_store_password(username: str, password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    users[username]["password_hash"] = hashed.decode()

def verify_password(username: str, password: str) -> bool:
    stored_hash = users[username]["password_hash"].encode()
    return bcrypt.checkpw(password.encode(), stored_hash)
```

**Session Management:**
- **Storage**: In-memory (desktop app, no persistent sessions)
- **Lifetime**: Until app closed or logout
- **Context**: Stored in `LeatherBookInterface.current_user`

### Failure Scenarios

| Failure | Location | Response |
|---------|----------|----------|
| Invalid password | UserManager | Pipeline returns error → GUI shows "Invalid credentials" |
| Account locked | UserManager | Pipeline returns error → GUI shows "Account locked" |
| Rate limit exceeded | Rate Limit PEP | PermissionError → GUI shows "Too many attempts" |
| User not found | UserManager | Pipeline returns error → GUI shows "User not found" |

### Security Properties

1. **Bcrypt Hashing**: Password hashes salted and stretched
2. **No Plaintext**: Passwords never stored or logged
3. **Session Isolation**: Each app instance has separate session
4. **Rate Limited**: Brute-force protection (5 attempts/min)
5. **Account Lockout**: 5 failed attempts → 15-minute lockout

---

## Flow 3: CLI Authorization

### Entry Point
- **File**: `src/app/main.py` or `project_ai_cli.py`
- **Mode**: Command-line arguments
- **Authentication**: Config file or environment variables

### Authorization Sequence

```
1. CLI Invocation
   ├─ Command: python -m src.app.main --action ai.chat --prompt "Hello"
   └─ Or: project-ai chat "Hello"

2. Parse Arguments
   ├─ action = "ai.chat"
   ├─ prompt = "Hello"
   └─ user = os.environ.get("PROJECT_AI_USER", "cli_user")

3. Build Pipeline Context
   └─ {
        "source": "cli",
        "action": "ai.chat",
        "payload": {"prompt": "Hello"},
        "user": {"username": "cli_user", "role": "admin"}  # From config
      }

4. Route to Pipeline
   └─ result = route_request("cli", context)

5. Pipeline Processing
   ├─ Validate → Simulate → Gate (same as above)
   ├─ RBAC: CLI user has "admin" role (configured)
   └─ Execute → Print result to stdout

6. Output
   └─ CLI prints: "AI Response: ..."
```

### Authentication Details

**Config-Based Auth** (`config/cli_config.json`):
```json
{
  "default_user": {
    "username": "cli_user",
    "role": "admin",
    "api_key": "<optional for remote APIs>"
  }
}
```

**Environment Variables:**
```bash
export PROJECT_AI_USER=admin_user
export PROJECT_AI_ROLE=admin
```

### Security Properties

1. **Trusted Environment**: CLI runs on local machine (trusted)
2. **Config File Protection**: Read permissions restricted (chmod 600)
3. **No Network Auth**: No JWT/session (local execution)
4. **Full Governance**: Still goes through Pipeline (no bypass)

---

## Flow 4: Agent Authorization (Autonomous)

### Entry Point
- **File**: `src/app/agents/*.py` (various agent modules)
- **Trigger**: Scheduled tasks, event-driven
- **Authentication**: Service account

### Authorization Sequence

```
1. Agent Activation
   ├─ Scheduler triggers agent (e.g., cron job)
   ├─ Or: Event bus triggers agent (e.g., security alert)
   └─ Agent: DependencyAuditor, TarlProtector, etc.

2. Agent Self-Identification
   └─ {
        "username": "agent:dependency_auditor",
        "role": "integrator",  # Elevated privileges for automation
        "agent_type": "security"
      }

3. Build Pipeline Context
   └─ {
        "source": "agent",
        "action": "agent.execute",
        "payload": {"agent_type": "dependency_auditor", "task": "scan"},
        "user": {"username": "agent:dependency_auditor", "role": "integrator"}
      }

4. Route to Pipeline
   └─ result = route_request("agent", context)

5. Pipeline Processing
   ├─ Phase 1: Validate
   │   ├─ Action: "agent.execute" in VALID_ACTIONS? ✓
   │   └─ Required: agent_type, task? ✓
   │
   ├─ Phase 3: Gate
   │   ├─ RBAC: Agent has "integrator" role
   │   │   ├─ Can execute agents? YES (power_user tier)
   │   │   └─ ✓ PASS
   │   │
   │   ├─ Four Laws: Agent action safe?
   │   │   ├─ Task: "scan dependencies"
   │   │   ├─ Harmless? YES
   │   │   └─ ✓ PASS
   │   │
   │   └─ TARL: Agent policy
   │       ├─ allow "agent.execute" where agent.role == "integrator"
   │       └─ ✓ ALLOW
   │
   └─ Execute → Agent runs scan, generates report

6. Agent Output
   └─ Report written to [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]], alerts sent if vulnerabilities found
```

### Service Account Management

**Service Accounts** (`data/access_control.json`):
```json
{
  "agent:dependency_auditor": ["integrator", "security"],
  "agent:tarl_protector": ["integrator"],
  "agent:health_monitor": ["expert"],
  "system": ["integrator", "expert"]  // Default system account
}
```

### Security Properties

1. **Principle of Least Privilege**: Agents have only necessary roles
2. **Service Accounts**: Separate from user accounts ([[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]])
3. **Action Logging**: All agent actions logged with agent identifier
4. **Rate Limited**: Agents subject to rate limits (prevent runaway)
5. **No Escalation**: Agents cannot promote themselves

---

## Flow 5: Temporal Workflow Authorization

### Entry Point
- **File**: `src/app/temporal/governance_integration.py`
- **Function**: `validate_workflow_execution()`
- **Authentication**: Workflow context

### Authorization Sequence

```
1. Temporal Workflow Starts
   ├─ Workflow type: "ai_learning_workflow"
   ├─ Request: LearningRequest(category="security", content="...")
   └─ Context: {"user_id": "alice", "initiated_by": "web"}

2. Pre-Execution Governance Gate
   └─ await validate_workflow_execution(
        workflow_type="ai_learning",
        request=learning_request,
        context={"user_id": "alice"}
      )

3. Build Pipeline Context
   └─ {
        "source": "temporal",
        "action": "temporal.workflow.validate",
        "workflow_type": "ai_learning",
        "payload": {...},
        "user": {"username": "alice", "role": "user"}
      }

4. Route to Pipeline
   └─ result = route_request("temporal", context)

5. Pipeline Processing
   ├─ Validate → Simulate → Gate
   ├─ RBAC: User "alice" can request learning? ✓ PASS
   ├─ Rate Limiting: Learning requests rate-limited (10/hour)
   └─ TARL: Learning content requires review
       ├─ Policy: escalate "learning.request" where category=="security"
       ├─ Verdict: ESCALATE
       └─ Codex council notified for approval

6. Gate Result
   └─ {
        "allowed": False,  // Temporarily blocked pending approval
        "reason": "Escalated to Codex for review",
        "metadata": {"escalation_id": "ESC-12345"}
      }

7. Workflow Response
   ├─ If allowed: true → Workflow proceeds
   └─ If allowed: false → Workflow pauses or fails
       └─ Human approval workflow triggered
```

### Temporal-Specific Features

**Workflow Validation:**
- Pre-execution gate (before expensive workflow starts)
- Async validation (doesn't block Temporal worker)
- Result cached (avoid redundant checks)

**Activity Validation:**
- Each activity also validated independently
- Fine-grained authorization per activity
- Activity context includes workflow metadata

### Security Properties

1. **Fail-Closed**: Workflow denied if governance check fails
2. **Human-in-the-Loop**: Escalation for sensitive workflows
3. **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]]**: All workflow executions logged
4. **Resource Quotas**: Workflows count against user quotas
5. **Temporal Integration**: Seamless with existing Temporal workflows

---

## Cross-Path Authorization Consistency

### Shared Authorization Logic

All 5 paths use the **same** authorization logic:
1. **Same Pipeline**: `enforce_pipeline()` is universal
2. **Same PEPs**: All 9 PEPs applied identically
3. **Same Audit**: All actions logged to same [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]]
4. **Same Policies**: TARL policies consistent across paths

### Path-Specific Customizations

| Aspect | Web | Desktop | CLI | Agent | Temporal |
|--------|-----|---------|-----|-------|----------|
| Authentication | JWT | Password | Config | Service Account | Workflow Context |
| Session | Stateless | In-Memory | None | None | Workflow-Scoped |
| Rate Limiting | Per-user | Per-user | Per-user | Per-agent | Per-workflow |
| User Context | Token payload | In-memory | Config file | Service account | Workflow metadata |
| Failure Response | HTTP status | GUI error | Exit code | Log error | Workflow failure |

### Authorization Equivalence

**Guarantee**: Same user, same action → Same decision (regardless of path)

**Example:**
- Web: User "alice" executes "ai.chat" → ALLOWED
- Desktop: User "alice" executes "ai.chat" → ALLOWED (same decision)
- Temporal: User "alice" executes "ai.chat" → ALLOWED (same decision)

**Rate Limiting Consistency:**
- Shared rate limit state across all paths
- Key: `"{source}:{user}:{action}"` includes source, but limit enforced globally
- Example: 30 requests/min for "ai.chat" applies to web + desktop combined

---

## Authorization Decision Tree

```
Request arrives from any source
    │
    ├─► Normalize context (router)
    │   └─► Build {source, action, payload, user}
    │
    ├─► Pipeline: Validate
    │   ├─► Action in registry?
    │   │   ├─ NO → REJECT (400 Bad Request)
    │   │   └─ YES → Continue
    │   ├─► Payload sanitized?
    │   │   └─ YES → Continue (XSS prevented)
    │   ├─► Schema valid?
    │   │   ├─ NO → REJECT (422 Unprocessable)
    │   │   └─ YES → Continue
    │   └─► PASS → Simulate
    │
    ├─► Pipeline: Simulate
    │   ├─► Predict impact, resources, failures
    │   └─► PASS → Gate
    │
    ├─► Pipeline: Gate (AUTHORIZATION)
    │   │
    │   ├─► Resolve User Context
    │   │   ├─ Token verification (Web)
    │   │   ├─ Session lookup (Desktop)
    │   │   ├─ Config file (CLI)
    │   │   ├─ Service account (Agent)
    │   │   └─ Workflow metadata (Temporal)
    │   │
    │   ├─► PEP-5: RBAC
    │   │   ├─ User has required role?
    │   │   │   ├─ NO → REJECT (403 Forbidden)
    │   │   │   └─ YES → Continue
    │   │
    │   ├─► PEP-6: Four Laws
    │   │   ├─ Action violates ethics?
    │   │   │   ├─ YES → REJECT (451 Unavailable for Legal Reasons)
    │   │   │   └─ NO → Continue
    │   │
    │   ├─► PEP-7: Rate Limiting
    │   │   ├─ Limit exceeded?
    │   │   │   ├─ YES → REJECT (429 Too Many Requests)
    │   │   │   └─ NO → Continue (record timestamp)
    │   │
    │   ├─► PEP-8: Quotas
    │   │   ├─ Quota exhausted?
    │   │   │   ├─ YES → REJECT (402 Payment Required)
    │   │   │   └─ NO → Continue (decrement budget)
    │   │
    │   ├─► PEP-9: TARL
    │   │   ├─ Policy verdict?
    │   │   │   ├─ DENY → REJECT (403 Forbidden)
    │   │   │   ├─ ESCALATE → PAUSE (wait for approval)
    │   │   │   └─ ALLOW → Continue
    │   │
    │   └─► ALL CHECKS PASSED → Execute
    │
    ├─► Pipeline: Execute
    │   └─► Perform action (monitored)
    │
    ├─► Pipeline: Commit
    │   └─► Persist state changes (atomic)
    │
    └─► Pipeline: Log
        └─► [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]] (SHA-256 chained)
```

---

## Security Guarantees

### Cross-Path Consistency
✓ **Same decision** for same user/action across all paths  
✓ **Rate limits** enforced globally (not per-path)  
✓ **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]]** unified (all paths logged together)  
✓ **No bypass**: CLI/Agent/Desktop cannot skip governance

### Defense-in-Depth
✓ **9 PEPs**: Multiple layers of authorization  
✓ **Fail-closed**: Deny if any check fails  
✓ **Immutable**: Four Laws cannot be bypassed  
✓ **Escalation**: Human review for ambiguous cases

### Accountability
✓ **Full audit**: Every decision logged  
✓ **Tamper-evident**: SHA-256 chain prevents log modification  
✓ **Attribution**: User/agent identified for all actions  
✓ **Timestamped**: Precise timing for forensics

---

## Related Systems

### Core AI Integration
- **[[relationships/core-ai/01-FourLaws-Relationship-Map.md|FourLaws]]**: Ethics authorization in all flows
- **[[relationships/core-ai/02-AIPersona-Relationship-Map.md|AIPersona]]**: Personality-driven actions authorized
- **[[relationships/core-ai/03-[[relationships/core-ai/03-MemoryExpansionSystem-Relationship-Map.md|MemoryExpansionSystem]]-Relationship-Map|MemoryExpansion]]**: Memory access authorization
- **[[relationships/core-ai/04-[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]]-Relationship-Map|LearningRequest]]**: Admin-level learning approval
- **[[relationships/core-ai/05-[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]-Relationship-Map|[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]]]**: Plugin loading authorization
- **[[relationships/core-ai/06-CommandOverride-Relationship-Map.md|CommandOverride]]**: Master password authorization

### Governance Integration
- **[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW|Pipeline System]]]]**: Authorization in Pipeline Phase 3 (Gate)
- **[[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md|Policy Enforcement]]**: Authorization PEPs (RBAC, TARL, Rate, Quota)
- **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|[[relationships/governance/04_AUDIT_TRAIL_GENERATION|audit trail]]]]**: All authorization decisions logged
- **[[relationships/governance/05_SYSTEM_INTEGRATION_MATRIX.md|Integration Matrix]]**: RBAC + TARL integration

### Constitutional Integration
- **[[relationships/constitutional/01_constitutional_systems_overview.md|[[relationships/constitutional/01_constitutional_systems_overview|Constitutional AI]]]]**: Constitutional authorization principles
- **[[relationships/constitutional/02_enforcement_chains.md|[[relationships/constitutional/02_enforcement_chains|enforcement chains]]]]**: Authorization enforcement hierarchy
- **[[relationships/constitutional/03_ethics_validation_flows.md|[[relationships/constitutional/03_ethics_validation_flows|ethics validation]]]]**: Ethics-based authorization

---

**Document Status**: Production-ready, all flows documented
**Last Updated**: 2025-06-01  
**Maintained By**: AGENT-053 (Governance Relationship Mapping Specialist)

---

## Related Documentation

- [[source-docs/agents/governance_pipeline_integration.md]]
