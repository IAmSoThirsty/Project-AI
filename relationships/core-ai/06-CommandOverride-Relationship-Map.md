---
title: "[[relationships/core-ai/06-CommandOverride-Relationship-Map.md|CommandOverride system]] - Core Relationship Map"
agent: AGENT-052
mission: Core AI Relationship Mapping
created: 2026-04-20
last_verified: 2026-04-20
review_cycle: Monthly
status: Active
stakeholder_review_required: Security, Ethics, Legal, C-Level
---

# [[relationships/core-ai/06-CommandOverride-Relationship-Map.md|CommandOverride system]] - Comprehensive Relationship Map

## Executive Summary

[[src/app/core/command_override.py]] is the **privileged safety protocol control system** enabling authorized users to bypass content filters, rate limiting, and (critically) safety protocols. It implements master password authentication, comprehensive audit logging, and 10+ safety protocols. **WARNING**: This system grants full control over all safety mechanisms.

---

## 1. WHAT: Component Functionality & Boundaries

### Core Responsibilities

1. **Master Password Authentication**
   - Set: `set_password(password)` → hashes with bcrypt/PBKDF2 (one-time only)
   - Verify: `verify_password(password)` → constant-time comparison (timing attack resistant)
   - Strength Validation: Minimum 8 chars, uppercase, lowercase, digit, special char
   - Lockout: 5 failed attempts → 15-minute lockout (account lockout protection)
   - Hash Storage: Bcrypt ($2y$ format) or PBKDF2 fallback (100k iterations)

2. **Safety Protocol Control**
   - 10 Protocols: content_filter, prompt_safety, data_validation, rate_limiting, user_approval, api_safety, ml_safety, plugin_sandbox, cloud_encryption, emergency_only
   - Toggle: `toggle_protocol(protocol_name, enabled, password)` → requires auth
   - Master Override: `activate_master_override(password)` → disables ALL protocols
   - Persistent State: `data/command_override_config.json`

3. **Audit Logging**
   - File: `data/command_override_audit.log`
   - Entries: `[timestamp] STATUS: action | Details: details`
   - Events: password set, auth success/failure, protocol toggle, master override activation
   - Immutable: Append-only log (no deletion, rotation only)

4. **Account Lockout Protection**
   - Failed Attempts Counter: `self.failed_auth_attempts`
   - Lockout Duration: 15 minutes (900 seconds)
   - Reset: Successful auth resets counter to 0
   - Persistence: Lockout state saved to config.json

5. **Two Implementations**
   - **Simplified** (`ai_systems.py` lines 1052-1193): Basic override system in main module
   - **Extended** (`command_override.py`): Full-featured with 10 protocols + lockout

### Boundaries & Limitations

- **Does NOT**: Implement multi-user authentication (single master password)
- **Does NOT**: Provide role-based access control (all-or-nothing)
- **Does NOT**: Support time-limited overrides (permanent until toggled off)
- **Does NOT**: Integrate with external auth systems (no LDAP, OAuth)
- **Does NOT**: Provide password recovery (lost password = locked out permanently)

### Data Structure

```python
# Extended System (command_override.py)
{
    "master_password_hash": "$2y$12$...",  # Bcrypt hash
    "safety_protocols": {
        "content_filter": True,
        "prompt_safety": True,
        "data_validation": True,
        "rate_limiting": True,
        "user_approval": True,
        "api_safety": True,
        "ml_safety": True,
        "plugin_sandbox": True,
        "cloud_encryption": True,
        "emergency_only": True
    },
    "failed_auth_attempts": 0,
    "auth_locked_until": None  # or ISO timestamp
}

# Simplified System (ai_systems.py)
{
    "active_overrides": {
        "content_filter_1745240600.123": {
            "type": "content_filter",
            "reason": "Administrative bypass",
            "created": "2026-04-20T14:30:00.123456"
        }
    },
    "audit_log": [
        {
            "action": "override_granted",
            "type": "content_filter",
            "timestamp": "2026-04-20T14:30:00.123456",
            "corr": "abc123..."
        }
    ]
}
```

---

## 2. WHO: Stakeholders & Decision-Makers

### Primary Stakeholders

| Stakeholder | Role | Authority Level | Decision Power |
|------------|------|----------------|----------------|
| **C-Level Executives** | Override authorization | CRITICAL | Who gets master password |
| **Security Team** | Security design | CRITICAL | Veto power on changes |
| **Ethics Board** | Override policy | CRITICAL | Defines acceptable overrides |
| **Legal/Compliance** | Regulatory alignment | HIGH | Can mandate audit requirements |
| **Core Developers** | Implementation | IMPLEMENTATION | Bug fixes only (no policy changes) |

### User Classes

1. **Master Password Holders**
   - CEO/CTO (crisis management)
   - Security Lead (incident response)
   - Ethics Board Chair (policy enforcement)
   - **NOT**: Regular users (would bypass safety entirely)

2. **Auditors**
   - Security team ([[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] review)
   - Compliance officers (regulatory audit)
   - Forensic investigators (incident analysis)
   - External auditors (third-party compliance)

3. **Observers**
   - Ethics board (periodic review)
   - Legal team (liability assessment)
   - Board of directors (oversight)

### Maintainer Responsibilities

- **Code Owners**: @security-team, @c-level
- **Review Requirements**: 2 security + 1 C-level approval
- **Change Frequency**: Annually or emergency only
- **On-Call**: 24/7 security escalation path (master password holders)

---

## 3. WHEN: Lifecycle & Review Cycle

### Creation & Evolution

| Date | Event | Version | Changes |
|------|-------|---------|---------|
| 2024-Q2 | Initial Implementation | 1.0.0 | Basic password + override |
| 2024-Q4 | Audit Logging | 1.2.0 | Added comprehensive [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]] |
| 2025-Q2 | 10 Protocol System | 1.5.0 | Extended from 3 to 10 protocols |
| 2025-Q4 | Account Lockout | 1.8.0 | Protection against brute force |
| 2026-Q1 | Timing Attack Fix | 1.9.0 | Constant-time password comparison |
| 2026-Q2 | Password Strength | 2.0.0 | Mandatory complexity requirements |

### Review Schedule

- **Daily**: [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] monitoring (automated alerts on usage)
- **Weekly**: Security team review (who used overrides, why)
- **Monthly**: Ethics board review (were overrides justified?)
- **Quarterly**: Full security audit (penetration testing)
- **Annually**: C-level review (should system exist?)

### Lifecycle Stages

```mermaid
graph LR
    A[System Init] --> B{Password Set?}
    B -->|No| C[Await set_password()]
    B -->|Yes| D[Load Config]
    C --> E[Password Set]
    E --> D
    D --> F[System Armed]
    
    F --> G[Override Request]
    G --> H{Password Correct?}
    H -->|No| I[Log Failure]
    I --> J{5+ Failures?}
    J -->|Yes| K[Lockout 15 min]
    J -->|No| G
    K --> L[Wait Lockout]
    L --> G
    H -->|Yes| M[Reset Failures]
    M --> N[Grant Override]
    N --> O[Log Success]
    O --> P[Protocols Disabled]
    P --> Q{Re-Enable?}
    Q -->|Yes| R[Toggle Protocol]
    Q -->|No| P
    R --> F
```

### Persistence Triggers

- **Password Set**: `set_password()` → `_save_config()`
- **Override Toggle**: `toggle_protocol()` → `_save_config()`
- **Auth Attempt**: `verify_password()` → `_save_config()` (if lockout triggered)
- **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]]**: Real-time append to audit.log (no buffering)

---

## 4. WHERE: File Paths & Integration Points

### Source Code Locations

```
Extended Implementation (Primary):
  src/app/core/command_override.py
    - Lines 1-250: Full [[src/app/core/ai_systems.py]] class
    - Lines 29-117: Initialization, config load/save
    - Lines 118-200: Password management (bcrypt/PBKDF2)
    - Lines 201-250: Protocol toggling, audit logging

Simplified Implementation (Legacy):
  src/app/core/ai_systems.py
    - Lines 1044-1050: OverrideType enum
    - Lines 1052-1193: [[src/app/core/ai_systems.py]] class
    - Lines 1069-1119: Password hashing (argon2/PBKDF2)
    - Lines 1135-1177: request_override() method

Test Suite:
  tests/test_command_override.py (if exists)
  tests/test_security_override.py (security-focused tests)
```

### Integration Points

```python
# Direct Consumers (import CommandOverrideSystem)
# NOTE: Very few integrations by design (high-security component)
src/app/gui/admin_panel.py (if exists - admin UI)
src/app/core/governance/pipeline.py (governance enforcement)

# Dependency Graph
[[src/app/core/ai_systems.py]]
  ├── passlib.hash.bcrypt (password hashing, optional)
  ├── hashlib.pbkdf2_hmac (fallback hashing)
  ├── secrets.compare_digest (timing attack prevention)
  ├── _atomic_write_json() (config persistence)
  └── [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] (append-only file)

# Integration Pattern (minimal exposure)
# Most code should NOT know override system exists
# Only admin interfaces and emergency workflows
```

### Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│ CRISIS SCENARIO: AI refusing critical command               │
│ - Example: Emergency shutdown during runaway process        │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ ADMIN: Access override system via hidden admin panel        │
│ - Enters master password                                    │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ override_system.toggle_protocol(                            │
│   "user_approval", enabled=False, password="<master>"       │
│ )                                                            │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ LOCKOUT CHECK                                                │
│ - if auth_locked_until: check if expired                    │
│ - if still locked: return (False, "Locked until...")        │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────────┐
│ PASSWORD VERIFICATION                                        │
│ - _verify_bcrypt_or_pbkdf2(stored_hash, password)           │
│ - secrets.compare_digest() for timing attack resistance     │
└──────────────────────┬───────────────────────────────────────┘
                       ↓
                   ┌───┴────┐
                   │VALID?  │
                   └───┬────┘
            ┌──────────┴──────────┐
            ↓                     ↓
    ┌───────────────┐     ┌──────────────┐
    │ SUCCESS       │     │ FAILURE      │
    │ - Reset       │     │ - Increment  │
    │   failed_     │     │   failed_    │
    │   attempts    │     │   attempts   │
    │   to 0        │     │ - If 5+:     │
    │ - Toggle      │     │   Lockout    │
    │   protocol    │     │   15 min     │
    │ - Log audit   │     │ - Log audit  │
    └───────┬───────┘     └──────┬───────┘
            ↓                    ↓
    ┌───────────────┐     ┌──────────────┐
    │ PROTOCOL OFF  │     │ ACCESS DENIED│
    │ - user_approval│     │ - Return     │
    │   bypassed    │     │   error      │
    │ - AI executes │     └──────────────┘
    │   critical    │
    │   command     │
    └───────────────┘
            ↓
    ┌───────────────┐
    │ RE-ENABLE     │
    │ - After crisis│
    │ - toggle_     │
    │   protocol    │
    │   (True)      │
    └───────────────┘
```

### Environment Dependencies

- **Python Version**: 3.11+ (type hints)
- **Required Packages**: 
  - `passlib` (bcrypt hashing, CRITICAL)
  - `cryptography` (for secure random, optional)
- **Fallback**: PBKDF2 with hashlib (if passlib unavailable)
- **Configuration**: 
  - `data_dir` (default: "data")
  - Config: `data/command_override_config.json`
  - Audit: `data/command_override_audit.log`

---

## 5. WHY: Problem Solved & Design Rationale

### Problem Statement

**Challenge**: How do we provide emergency control over safety systems without:
1. Creating exploitable backdoors
2. Enabling regular users to bypass safety
3. Losing [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]] for accountability
4. Allowing brute force attacks
5. Introducing timing attack vectors

**Requirements**:
1. Strong authentication (master password)
2. Comprehensive audit logging (immutable)
3. Granular control (per-protocol vs. all-or-nothing)
4. Attack resistance (lockout, timing attack prevention)
5. Emergency access (for critical scenarios)

### Design Rationale

#### Why Master Password Instead of Multi-User Auth?
- **Decision**: Single master password shared among C-level executives
- **Rationale**: 
  - Simplicity: No user database, roles, permissions
  - Emergency: Any authorized person can act in crisis
  - Accountability: [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] shows what was done (not who)
- **Tradeoff**: Cannot attribute actions to individuals

#### Why Bcrypt vs. Argon2?
- **Decision**: Prefer passlib bcrypt, fallback to PBKDF2
- **Rationale**: 
  - Bcrypt: Industry standard, battle-tested, wide support
  - PBKDF2: Stdlib fallback (no external dependencies)
  - NOT Argon2: Optional dependency, complexity
- **Tradeoff**: Argon2 has better memory-hardness (but bcrypt sufficient)

#### Why 15-Minute Lockout?
- **Decision**: 5 failed attempts → 15 minute lockout
- **Rationale**: 
  - Brute force: 5 attempts = 5 guesses per 15 min = ~400/day (infeasible)
  - Balance: Short enough for legitimate retry, long enough to deter attacks
  - Reset: Lockout state persists across restarts
- **Tradeoff**: Legitimate user locked out (but security > convenience)

#### Why 10 Protocols Instead of All-Or-Nothing?
- **Decision**: Granular protocol toggles vs. master override only
- **Rationale**: 
  - Precision: Disable only necessary protocol (e.g., rate limiting for load test)
  - Safety: Don't disable content_filter to bypass rate_limiting
  - Audit: Clear intent (log shows which protocol, why)
- **Tradeoff**: More complex UI/API (but safer)

### Architectural Tradeoffs

| Decision | Benefit | Cost | Mitigation |
|----------|---------|------|------------|
| Single master password | Simple, emergency access | No user attribution | [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] + policy |
| Bcrypt hashing | Slow brute force, proven | Computation cost | Acceptable for rare operation |
| 15-minute lockout | Brute force protection | UX friction | Policy: careful password entry |
| 10 protocols | Granular control | Complex state space | Clear documentation, GUI |

### Alternative Approaches Considered

1. **Hardware Token (YubiKey)** (REJECTED)
   - Would eliminate password attacks
   - Con: Hardware dependency, lost token = locked out

2. **Time-Limited Overrides** (CONSIDERED FOR FUTURE)
   - Would auto-revert overrides after N minutes
   - Blocked by: complexity, emergency scenarios need indefinite override

3. **Approval Workflow (2-Person Rule)** (CONSIDERED FOR FUTURE)
   - Would require 2 password holders to approve override
   - Blocked by: emergency response delay

4. **Biometric Authentication** (REJECTED)
   - Would eliminate password memory burden
   - Con: Hardware dependency, privacy concerns

---

## 6. Dependency Graph (Technical)

### Upstream Dependencies (What CommandOverride Needs)

```python
# Standard Library
import os, json, hashlib, base64, secrets, logging, time
from datetime import datetime, timedelta
from typing import Any, Dict

# External Packages (preferred)
from passlib.hash import bcrypt  # Bcrypt hashing (fallback if unavailable)

# Internal Modules
from app.core.ai_systems import _atomic_write_json  # Config persistence
from app.core.telemetry import send_event  # Optional telemetry
```

### Downstream Dependencies (Who Needs CommandOverride)

```
┌─────────────────────────────────────────┐
│  CommandOverride (Emergency Control)    │
└────────────────┬────────────────────────┘
                 │
        ┌────────┴─────────┬──────────────┬──────────────┐
        ↓                  ↓              ↓              ↓
┌───────────────┐  ┌──────────────┐  ┌─────────┐  ┌──────────────┐
│ Admin Panel   │  │ Governance   │  │ CLI     │  │ Monitoring   │
│ (hidden UI)   │  │ Pipeline     │  │ (admin  │  │ Dashboard    │
│               │  │ (policy)     │  │  mode)  │  │ (audit view) │
└───────────────┘  └──────────────┘  └─────────┘  └──────────────┘
        │                  │              │              │
        └──────────────────┴──────────────┴──────────────┘
                                    │
                          ┌─────────┴─────────┐
                          ↓                   ↓
                  ┌───────────────┐   ┌─────────────────┐
                  │ Crisis        │   │ Compliance      │
                  │ Management    │   │ Audit           │
                  └───────────────┘   └─────────────────┘
```

### Cross-Module Communication

```python
# Typical Call Stack (Emergency Override)
1. Admin opens hidden admin panel (URL: /admin/override?token=...)
2. AdminPanel → override_system.get_protocol_status() → display states
3. Admin clicks "Disable Content Filter" → enters master password
4. AdminPanel → override_system.toggle_protocol("content_filter", False, password)
5. [[src/app/core/ai_systems.py]].toggle_protocol() →
     - Check lockout: if locked, return (False, "Locked until...")
     - Verify password: _verify_bcrypt_or_pbkdf2()
     - If invalid: increment failed_attempts, save, log, return False
     - If valid: reset failed_attempts, toggle protocol, save, log, return True
6. AdminPanel → display "Content filter disabled" (green banner)
7. AI systems → check if override_system.is_protocol_active("content_filter")
8. AI proceeds without content filtering (emergency bypass active)
```

---

## 7. Stakeholder Matrix

| Stakeholder Group | Interest | Influence | Engagement Strategy |
|------------------|----------|-----------|---------------------|
| **C-Level** | CRITICAL (authorization) | CRITICAL (master password) | Annual review, crisis drills |
| **Security Team** | CRITICAL (design) | HIGH (implementation veto) | Weekly [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] review, quarterly penetration test |
| **Ethics Board** | CRITICAL (policy) | HIGH (override veto) | Monthly review, emergency response policy |
| **Legal/Compliance** | HIGH (regulatory) | HIGH (audit requirements) | Quarterly compliance audit, incident reports |
| **Core Developers** | LOW (maintenance) | LOW (bug fixes only) | On-demand, no policy changes allowed |

---

## 8. Risk Assessment & Mitigation

### CRITICAL RISKS (System Disables All Safety)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Master Password Leak** | LOW | CATASTROPHIC | Password rotation, [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] monitoring, incident response |
| **Brute Force Attack** | LOW | HIGH | 15-min lockout, strong password requirements, alert on 3+ failures |
| **Timing Attack (password)** | LOW | HIGH | secrets.compare_digest(), constant-time operations |
| **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] Tampering** | LOW | CATASTROPHIC | File integrity monitoring, append-only, off-system backup |
| **Override Forgotten (left disabled)** | MEDIUM | HIGH | Automated alerts, dashboard monitoring, re-enable checklist |

### Incident Response (CRITICAL SYSTEM)

```
1. Master Password Compromised → 
   - Immediate rotation (all password holders notified)
   - [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] forensic analysis (what was accessed?)
   - Incident report to legal/ethics board
   - Post-mortem + enhanced monitoring

2. Unauthorized Override Detected →
   - Immediate revoke (re-enable all protocols)
   - Lockdown mode (disable override system)
   - Security investigation
   - Legal/law enforcement notification if malicious

3. [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] Deleted/Tampered →
   - Restore from off-system backup
   - File integrity violation = security breach
   - Full system audit
   - External forensic investigation

4. Override Left Enabled (forgotten) →
   - Automated alert after 1 hour
   - Dashboard warning (red banner)
   - Email notification to password holders
   - Escalation to C-level after 4 hours
```

---

## 9. Integration Checklist for New Consumers

**WARNING: This system should have MINIMAL integrations.**

When integrating [[src/app/core/command_override.py]] (rare):

- [ ] Verify you have security team approval (mandatory)
- [ ] Import `[[src/app/core/ai_systems.py]]` from `app.core.command_override`
- [ ] Instantiate with `data_dir` (testing: isolated tempdir)
- [ ] **NEVER** expose to regular users (admin UI only)
- [ ] Check protocol status: `is_protocol_active(protocol_name)`
- [ ] Handle lockout gracefully (show remaining time)
- [ ] Log all integration points (security audit)
- [ ] Add security tests (brute force, timing attack)
- [ ] Document emergency use cases only
- [ ] Implement auto-re-enable after N hours (if applicable)

---

## 10. Future Roadmap

### Planned Enhancements (Q1 2027)

1. **Two-Person Rule**: Require 2 password holders to approve override
2. **Time-Limited Overrides**: Auto-revert after N minutes
3. **Hardware Token Support**: YubiKey integration (optional)
4. **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] Encryption**: Tamper-evident logging with HMAC

### Research Areas

- Zero-knowledge proof authentication (eliminate password storage)
- Blockchain-based [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] (immutable, distributed)
- AI-powered anomaly detection (unusual override patterns)

### NOT Planned (Policy Decisions)

- Multi-user authentication (complexity risk)
- Remote override (network attack surface)
- Override marketplace (absurd and dangerous)

---

## 10. API Reference Card

### Constructor
```python
[[src/app/core/ai_systems.py]](data_dir: str = "data")
```

### Core Methods
```python
# Password Management
set_password(password: str) -> bool  # One-time only
verify_password(password: str) -> bool  # Constant-time comparison
_validate_master_password_strength(password: str) -> (bool, str)

# Protocol Control (Extended System)
toggle_protocol(protocol_name: str, enabled: bool, password: str) -> (bool, str)
is_protocol_active(protocol_name: str) -> bool
get_all_protocol_states() -> dict

# Master Override (Simplified System)
request_override(password: str, override_type: OverrideType, reason: str) -> (bool, str)
is_override_active(override_type: OverrideType) -> bool

# Status
get_statistics() -> dict  # {active_overrides, audit_entries, password_set}
```

### State Files
```
data/command_override_config.json  # Master password hash + protocol states
data/command_override_audit.log    # Immutable [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]]
```

### Thread Safety
- ⚠️ CRITICAL: NOT thread-safe (admin operations only, single-threaded)
- ⚠️ CRITICAL: No concurrent access (file locking not implemented)

---

## Related Systems

### Core AI Integration
- **[[relationships/core-ai/01-FourLaws-Relationship-Map.md|FourLaws]]**: Can be overridden (CATASTROPHIC RISK)
- **[[relationships/core-ai/02-AIPersona-Relationship-Map.md|AIPersona]]**: Personality modifications possible under override
- **[[relationships/core-ai/03-[[relationships/core-ai/03-MemoryExpansionSystem-Relationship-Map.md|MemoryExpansionSystem]]-Relationship-Map|MemoryExpansion]]**: Emergency memory access
- **[[relationships/core-ai/04-[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]]-Relationship-Map|LearningRequest]]**: Learning approval bypass
- **[[relationships/core-ai/05-[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]-Relationship-Map|[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]]]**: Plugin sandbox disable

### Governance Integration
- **[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW|Pipeline System]]]]**: Override can bypass all governance phases
- **[[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md|Policy Enforcement]]**: All PEPs can be disabled
- **[[relationships/governance/03_AUTHORIZATION_FLOWS.md|[[relationships/governance/03_AUTHORIZATION_FLOWS|authorization flows]]]]**: RBAC bypass capability
- **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|[[relationships/governance/04_AUDIT_TRAIL_GENERATION|audit trail]]]]**: All override actions MUST be logged
- **[[relationships/governance/05_SYSTEM_INTEGRATION_MATRIX.md|Integration Matrix]]**: Override dependency mapping

### Constitutional Integration
- **[[relationships/constitutional/01_constitutional_systems_overview.md|[[relationships/constitutional/01_constitutional_systems_overview|Constitutional AI]]]]**: Constitutional override (emergency only)
- **[[relationships/constitutional/02_enforcement_chains.md|[[relationships/constitutional/02_enforcement_chains|enforcement chains]]]]**: Enforcement bypass mechanism
- **[[relationships/constitutional/03_ethics_validation_flows.md|[[relationships/constitutional/03_ethics_validation_flows|ethics validation]]]]**: Validation bypass capability

---

## Document Metadata

- **Author**: AGENT-052 (Core AI Relationship Mapping Specialist)
- **Review Date**: 2026-04-20
- **Next Review**: 2026-05-20 (Monthly)
- **Approvers**: CEO, CTO, CISO, Ethics Board Chair, Legal Counsel
- **Classification**: **CONFIDENTIAL** - Restricted Distribution
- **Version**: 1.0.0
- **Related Documents**: 
  - [[relationships/core-ai/01-FourLaws-Relationship-Map.md]] - Ethics override (CRITICAL)
  - [[relationships/core-ai/02-AIPersona-Relationship-Map.md]] - Personality override
  - [[relationships/core-ai/03-[[relationships/core-ai/03-MemoryExpansionSystem-Relationship-Map.md|MemoryExpansionSystem]]-Relationship-Map]] - Memory access
  - [[relationships/core-ai/04-[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]]-Relationship-Map]] - Learning bypass
  - [[relationships/core-ai/05-[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]-Relationship-Map]] - Plugin controls
  - [[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md]] - Governance bypass
  - [[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md]] - PEP disablement
  - [[relationships/governance/03_AUTHORIZATION_FLOWS.md]] - Authorization bypass
  - [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md]] - Mandatory audit logging
  - [[relationships/constitutional/01_constitutional_systems_overview.md]] - Constitutional override
  - [[relationships/constitutional/02_enforcement_chains.md]] - Enforcement bypass
  - `SECURITY.md`
  - `INCIDENT_RESPONSE_PLAN.md`
  - `MASTER_PASSWORD_POLICY.md`
  - `AUDIT_LOG_RETENTION_POLICY.md`

---

## CRITICAL SECURITY NOTICE

**This document describes a system that can disable all safety protections.**

- Master password must be stored in secure location (e.g., password manager, HSM)
- Access to this document itself is restricted (C-level + security team only)
- Unauthorized access to override system = immediate security incident
- Regular audits required to ensure system not misused
- Consider disabling in production unless absolutely necessary

**If you're reading this and shouldn't be, report to security immediately.**

---

## Related Documentation

- [[source-docs/core/01-ai_systems.md]]
- [[source-docs/core/02-command_override.md]]


---

## RELATED SYSTEMS

### GUI Integration ([[../gui/00_MASTER_INDEX|GUI Master Index]])

| GUI Component | Override Operation | Access Level | Documentation |
|---------------|-------------------|--------------|---------------|
| Admin Panel (Hidden) | Master password input | **C-LEVEL ONLY** | CONFIDENTIAL |
| [[../gui/06_IMAGE_GENERATION_RELATIONSHIPS\|ImageGeneration]] | Content filter bypass | Admin password required | Section 4 (override) |
| [[../gui/03_HANDLER_RELATIONSHIPS\|DashboardHandlers]] | Protocol toggle UI | Admin panel only | Future implementation |
| God Tier Command Panel | Emergency controls | **RESTRICTED ACCESS** | CONFIDENTIAL |

⚠️ **WARNING**: Override GUI is intentionally hidden from regular users. Exposure violates security policy.

### Agent Integration ([[../agents/README|Agents Overview]])

| Agent System | Override Impact | Emergency Protocol | Documentation |
|--------------|-----------------|-------------------|---------------|
| [[../agents/VALIDATION_CHAINS#validation-bypass-prevention\|Validation Chain]] | **BYPASSES ALL LAYERS** | Skips ValidatorAgent, OversightAgent, Four Laws | ⚠️ CATASTROPHIC RISK |
| [[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation\|Four Laws]] | **DISABLED** | Ethics checks inactive | Section 9.1 (bypass prevention) |
| [[../agents/AGENT_ORCHESTRATION#privilege-escalation-prevention\|CognitionKernel]] | Override detection | Logs override state in ExecutionContext | Section 8.2 (privilege escalation) |
| [[../agents/PLANNING_HIERARCHIES\|PlannerAgent]] | Unrestricted planning | Can plan dangerous operations | Section 5 (constraints) |

### Security Measures

- **Master Password**: Bcrypt hashed, 15-min lockout after 5 failures
- **Audit Trail**: Immutable append-only log, tamper-evident
- **Time-Limited**: Auto-reactivate protocols after emergency window

⚠️ **CLASSIFICATION**: This section is **CONFIDENTIAL**. Unauthorized access must be reported to Security Team immediately.

---

**Generated by:** AGENT-052: Core AI Relationship Mapping Specialist  
**Enhanced by:** AGENT-078: GUI & Agent Cross-Links Specialist  
**Classification:** CONFIDENTIAL - C-Level + Security Team Only  
**Status:** ✅ Cross-linked with GUI and Agent systems (RESTRICTED DISTRIBUTION)
