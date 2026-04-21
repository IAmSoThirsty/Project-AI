---
title: "Governance Systems Overview - 8 Core Systems"
type: governance_relationships
scope: cross-system
created: 2025-06-01
audience: [developers, auditors, security]
tags: [governance, architecture, enforcement, relationships]
---

# Governance Systems Overview

## Executive Summary

Project-AI implements **8 interconnected governance systems** that form a comprehensive enforcement and compliance framework. Each system has distinct responsibilities while maintaining tight integration points for defense-in-depth security.

## The 8 Core Governance Systems

### 1. **[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|Pipeline System]]** (`src/app/core/governance/pipeline.py`)
**Purpose**: Universal enforcement layer for ALL requests
**Authority**: Central coordinator
**Key Function**: 6-phase request processing (Validate → Simulate → Gate → Execute → Commit → Log)

### 2. **RBAC (Role-Based Access Control)** (`src/app/core/access_control.py`)
**Purpose**: User role management and permission enforcement
**Authority**: User-level authorization
**Key Function**: Role assignment, permission checking, access grants

### 3. **Audit System** (`src/app/governance/audit_log.py`)
**Purpose**: Cryptographic [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]] with SHA-256 chaining
**Authority**: Forensic accountability
**Key Function**: Immutable logging, tamper detection, compliance reporting

### 4. **Sovereign Data** (`governance/sovereign_data/`, `governance/sovereign_verifier.py`)
**Purpose**: Third-party verifiable compliance bundles
**Authority**: Independent verification
**Key Function**: Cryptographic proof generation, hash chain validation

### 5. **TARL (Temporal Authorization Runtime Language)** (`kernel/tarl_gate.py`)
**Purpose**: Policy-as-code enforcement with escalation
**Authority**: Codex-backed decision engine
**Key Function**: Context-aware policy evaluation, automatic escalation

### 6. **Action Registry** (embedded in `pipeline.py`)
**Purpose**: Whitelist of all valid system actions
**Authority**: Action validation
**Key Function**: Prevents unknown/malicious action execution

### 7. **Rate Limiting** (embedded in `pipeline.py`)
**Purpose**: Request throttling per user/action/source
**Authority**: Resource protection
**Key Function**: Time-windowed request counting, DOS prevention

### 8. **Quotas** (`src/app/core/tier_governance_policies.py`)
**Purpose**: Resource allocation and tier constraints
**Authority**: Capacity management
**Key Function**: Cross-tier blocking, resource budgets, escalation paths

## System Interaction Map

```
┌─────────────────────────────────────────────────────────────────┐
│                        REQUEST ENTRY POINT                       │
│              (Web/Desktop/CLI/Agent/Temporal)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│ [1] [[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW.md|Pipeline System]] - Universal Enforcement Layer               │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Phase 1: VALIDATE                                           │ │
│ │  ├─► [6] Action Registry Check (whitelist validation)      │ │
│ │  ├─► Input Sanitization (XSS, injection prevention)        │ │
│ │  └─► Schema Validation                                      │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Phase 2: SIMULATE                                           │ │
│ │  ├─► Impact Analysis (state changes, resource usage)       │ │
│ │  ├─► Risk Assessment (failure prediction)                  │ │
│ │  └─► [8] Quota Pre-Check (resource availability)           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Phase 3: GATE (Authorization)                               │ │
│ │  ├─► [2] RBAC: User permission check                       │ │
│ │  ├─► Four Laws Compliance (ethics framework)               │ │
│ │  ├─► [7] Rate Limiting: Throttle check                     │ │
│ │  ├─► [8] Quotas: Resource budget check                     │ │
│ │  └─► [5] TARL: Policy evaluation & escalation              │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Phase 4: EXECUTE                                            │ │
│ │  └─► Actual operation with rollback capability             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Phase 5: COMMIT                                             │ │
│ │  └─► State persistence with atomic transactions            │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Phase 6: LOG                                                │ │
│ │  ├─► [3] Audit: Cryptographic logging (SHA-256 chain)      │ │
│ │  └─► [4] Sovereign Data: Compliance bundle update          │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## [[relationships/governance/03_AUTHORIZATION_FLOWS.md|authorization flows]]

```
User Request
    │
    ├─► [1] Pipeline: Validate (Action Registry + Schema)
    │       │
    │       ├─ REJECT → [3] Audit: Log rejection → Response
    │       │
    │       └─ PASS → [1] Pipeline: Simulate
    │                   │
    │                   └─► [1] Pipeline: Gate
    │                           │
    │                           ├─► [2] RBAC: Check user.role
    │                           │       │
    │                           │       ├─ NO ROLE → REJECT
    │                           │       └─ HAS ROLE → Continue
    │                           │
    │                           ├─► [7] Rate Limit: Check history
    │                           │       │
    │                           │       ├─ EXCEEDED → REJECT
    │                           │       └─ OK → Continue
    │                           │
    │                           ├─► [8] Quotas: Check budget
    │                           │       │
    │                           │       ├─ EXHAUSTED → REJECT
    │                           │       └─ AVAILABLE → Continue
    │                           │
    │                           └─► [5] TARL: Evaluate policy
    │                                   │
    │                                   ├─ DENY → REJECT
    │                                   ├─ ESCALATE → Codex review
    │                                   └─ ALLOW → Execute
    │
    └─► [1] Pipeline: Execute
            │
            ├─► [1] Pipeline: Commit
            │
            └─► [3] Audit: Log success + [4] Sovereign: Update bundle
```

## Data Flow: [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]] Generation

```
Action Executed
    │
    ├─► [1] Pipeline: _log() called with context + result
    │       │
    │       └─► [3] Audit System: log_event()
    │               │
    │               ├─► Load last hash from audit_log.yaml
    │               ├─► Compute SHA-256(event_data + prev_hash)
    │               ├─► Append to YAML (immutable chain)
    │               │
    │               └─► [4] Sovereign Data: Update compliance bundle
    │                       │
    │                       ├─► Add event to bundle
    │                       ├─► Sign with Ed25519 private key
    │                       ├─► Update hash chain
    │                       └─► Persist to sovereign_data/artifacts/
```

## Cross-System Dependencies

### Primary Dependencies (Required for Operation)

```
[1] Pipeline
    ├─ REQUIRES → [6] Action Registry (embedded)
    ├─ REQUIRES → [2] RBAC (user.role lookup)
    ├─ REQUIRES → [7] Rate Limiting (embedded)
    ├─ REQUIRES → [8] Quotas (tier policies)
    ├─ REQUIRES → [5] TARL (policy evaluation)
    ├─ REQUIRES → [3] Audit (logging)
    └─ REQUIRES → [4] Sovereign Data (compliance)

[5] TARL Gate
    ├─ REQUIRES → TarlRuntime (policy engine)
    ├─ REQUIRES → CodexDeus (escalation handler)
    └─ INTEGRATES → [1] Pipeline (called during Gate phase)

[8] Quotas (Tier Governance)
    ├─ REQUIRES → [3] Audit (block logging)
    ├─ REQUIRES → [2] RBAC (tier assignments)
    └─ INTEGRATES → [1] Pipeline (quota checks)

[3] Audit System
    └─ INTEGRATES → [4] Sovereign Data (compliance bundles)

[2] RBAC
    └─ STANDALONE (single responsibility: role management)

[4] Sovereign Data
    └─ STANDALONE (independent verification capability)

[6] Action Registry
    └─ EMBEDDED in [1] Pipeline (VALID_ACTIONS constant)

[7] Rate Limiting
    └─ EMBEDDED in [1] Pipeline (_check_rate_limit function)
```

### Integration Points by Layer

**Layer 1: Request Entry**
- All sources (web/desktop/CLI/agent/temporal) → [1] Pipeline

**Layer 2: Validation**
- [1] Pipeline → [6] Action Registry
- [1] Pipeline → Input validators

**Layer 3: Authorization**
- [1] Pipeline → [2] RBAC (role lookup)
- [1] Pipeline → [7] Rate Limiting (throttle check)
- [1] Pipeline → [8] Quotas (resource check)
- [1] Pipeline → [5] TARL (policy evaluation)

**Layer 4: Execution**
- [1] Pipeline → Action handlers

**Layer 5: Accountability**
- [1] Pipeline → [3] Audit (logging)
- [3] Audit → [4] Sovereign Data (compliance)

## Key Enforcement Points

### [[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md|Policy Enforcement Points]] (PEPs)

1. **Action Registry PEP** (Phase 1: Validate)
   - Location: `pipeline.py:150-154`
   - Function: `_validate()` → Action whitelist check
   - Rejection: Raises `ValueError` if action not in `VALID_ACTIONS`

2. **RBAC PEP** (Phase 3: Gate)
   - Location: `pipeline.py:394-395` → `_check_user_permissions()`
   - Function: Role-based authorization
   - Rejection: Raises `PermissionError` if insufficient role

3. **Rate Limiting PEP** (Phase 3: Gate)
   - Location: `pipeline.py:392` → `_check_rate_limit()`
   - Function: Time-windowed request counting
   - Rejection: Raises `PermissionError` if limit exceeded

4. **Quota PEP** (Phase 3: Gate)
   - Location: `pipeline.py:398` → `_check_resource_quotas()`
   - Function: Resource budget validation
   - Rejection: Raises `PermissionError` if quota exhausted

5. **TARL PEP** (Kernel Integration)
   - Location: `kernel/tarl_gate.py:18-37`
   - Function: Policy evaluation with escalation
   - Rejection: Raises `TarlEnforcementError` if denied/escalated

6. **Four Laws PEP** (Phase 3: Gate)
   - Location: `pipeline.py:376-389`
   - Function: Ethics framework validation
   - Rejection: Raises `PermissionError` if non-compliant

### Audit Capture Points (ACPs)

1. **Success Path**: `pipeline.py:115` → `_log(context, result, status="success")`
2. **Failure Path**: `pipeline.py:121` → `_log(context, None, status="error", error=...)`
3. **Health Reports**: `audit_log.py:98-134` → `log_event()`
4. **Tier Blocks**: `tier_governance_policies.py` → Audit integration

## Security Properties

### Defense-in-Depth Layers

**Layer 1: Input Validation**
- [6] Action Registry: Whitelist enforcement
- Input sanitization: XSS/injection prevention
- Schema validation: Type/structure checking

**Layer 2: Authorization**
- [2] RBAC: Role-based permissions
- [5] TARL: Policy-based decisions
- Four Laws: Ethics compliance

**Layer 3: Resource Protection**
- [7] Rate Limiting: DOS prevention
- [8] Quotas: Capacity management
- Tier governance: Cross-tier blocks

**Layer 4: Accountability**
- [3] Audit: Tamper-evident logging
- [4] Sovereign Data: Third-party verification
- SHA-256 chaining: Integrity protection

### Cryptographic Guarantees

1. **Audit Chain Integrity** (SHA-256)
   - Each event hash includes: event_data + previous_hash
   - Tampering breaks chain (detected by verifier)
   - Genesis event: first event has `prev_hash = "GENESIS"`

2. **Sovereign Bundle Signatures** (Ed25519)
   - Bundle signed with private key
   - Public key for independent verification
   - Timestamp attestation for temporal proof

3. **Compliance Proofs** (Merkle-style)
   - Hash chain provides cumulative proof
   - Selective disclosure possible
   - Third-party auditable without trust

## Failure Modes and Recovery

### System Failures

| System | Failure Mode | Impact | Recovery Strategy |
|--------|-------------|--------|-------------------|
| Pipeline | Crash during execution | Request fails, state rolled back | Retry with exponential backoff |
| RBAC | User store unavailable | All requests denied | Fallback to cached roles |
| Audit | Log write failure | Execution blocked (fail-closed) | Queue events, retry writes |
| Sovereign | Signing key unavailable | Compliance bundle not updated | Continue with audit-only mode |
| TARL | Policy engine timeout | Request denied (fail-closed) | Manual escalation to Codex |
| Rate Limiter | State corruption | Rate limits ignored | Rebuild from [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit log]] |
| Quotas | Tier state inconsistency | Conservative quotas applied | Tier 1 override capability |

### Bypass Prevention

**No Bypass Mechanisms:**
- Action Registry: No wildcard/prefix matching (strict equality)
- Rate Limiting: No role-based exemptions (admin rate limited)
- Audit: No "stealth mode" or logging disablement
- TARL: No policy override (escalation required)

**Controlled Bypass:**
- Command Override System: Master password + [[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|audit trail]]
- Emergency Mode: Tier 1 governance approval required
- Maintenance Windows: Pre-scheduled, logged, time-boxed

## Related Systems

### Core AI Integration
- **[[relationships/core-ai/01-FourLaws-Relationship-Map.md|FourLaws]]**: Integrated in Pipeline Phase 3 (Gate) as ethics PEP
- **[[relationships/core-ai/02-AIPersona-Relationship-Map.md|AIPersona]]**: All personality actions flow through Pipeline
- **[[relationships/core-ai/03-[[relationships/core-ai/03-MemoryExpansionSystem-Relationship-Map.md|MemoryExpansionSystem]]-Relationship-Map|MemoryExpansion]]**: Memory operations validated by Pipeline
- **[[relationships/core-ai/04-[[relationships/core-ai/04-LearningRequestManager-Relationship-Map.md|LearningRequestManager]]-Relationship-Map|LearningRequest]]**: Learning approval flows through governance
- **[[relationships/core-ai/05-[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]-Relationship-Map|[[relationships/core-ai/05-PluginManager-Relationship-Map.md|PluginManager]]]]**: Plugin operations validated by Pipeline
- **[[relationships/core-ai/06-CommandOverride-Relationship-Map.md|CommandOverride]]**: Emergency bypass of all governance systems

### Governance Systems (Internal Cross-Links)
- **[[relationships/governance/02_POLICY_ENFORCEMENT_POINTS.md|[[relationships/governance/02_POLICY_ENFORCEMENT_POINTS|Policy Enforcement Points]]]]**: 6 PEPs embedded in Pipeline phases
- **[[relationships/governance/03_AUTHORIZATION_FLOWS.md|[[relationships/governance/03_AUTHORIZATION_FLOWS|authorization flows]]]]**: Request authorization decision trees
- **[[relationships/governance/04_AUDIT_TRAIL_GENERATION.md|[[relationships/governance/04_AUDIT_TRAIL_GENERATION|audit trail]]]]**: Pipeline Phase 6 (Log) cryptographic logging
- **[[relationships/governance/05_SYSTEM_INTEGRATION_MATRIX.md|Integration Matrix]]**: Pipeline integration with all 8 governance systems

### Constitutional Integration
- **[[relationships/constitutional/01_constitutional_systems_overview.md|[[relationships/constitutional/01_constitutional_systems_overview|Constitutional AI]]]]**: Constitutional principles enforced through Pipeline
- **[[relationships/constitutional/02_enforcement_chains.md|[[relationships/constitutional/02_enforcement_chains|enforcement chains]]]]**: Hierarchical enforcement via Pipeline gates
- **[[relationships/constitutional/03_ethics_validation_flows.md|[[relationships/constitutional/03_ethics_validation_flows|ethics validation]]]]**: [[relationships/constitutional/03_ethics_validation_flows.md|ethics validation]] in Pipeline Phase 3

---

## Related Documentation

- **Implementation Details**: See individual system files
- **Integration Patterns**: `MULTI_PATH_GOVERNANCE_ARCHITECTURE.md`
- **Security Audit**: `SECURITY_VULNERABILITY_ASSESSMENT_REPORT.md`
- **Deployment**: `DESKTOP_CONVERGENCE_COMPLETE.md`
- **Core AI Systems**: [[relationships/core-ai/00-INDEX.md]]
- **Constitutional Framework**: [[relationships/constitutional/01_constitutional_systems_overview.md]]

---

**Document Status**: Production-ready, comprehensive mapping complete  
**Last Updated**: 2025-06-01  
**Maintained By**: AGENT-053 (Governance Relationship Mapping Specialist)
