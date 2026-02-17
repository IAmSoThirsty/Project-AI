# Project-AI Threat Model

**Version**: 1.0.0 **Last Updated**: 2026-02-08 **Status**: Active **Scope**: Monolithic Architecture, TARL Policy Runtime, Governance Surfaces

______________________________________________________________________

## Executive Summary

This threat model explicitly scopes Project-AI's security boundaries, attack surfaces, and intentional non-defenses. It is designed for adversarial review by security researchers, enterprise security teams, and compliance auditors.

**Key Principle**: We control the narrative of risk instead of defending blindly.

______________________________________________________________________

## System Architecture Overview

### Core Components

1. **Monolithic Core** (`src/app/`)

   - 6 AI systems in single process
   - PyQt6 GUI interface
   - Direct filesystem access
   - Local process execution

1. **TARL Policy Runtime** (`tarl/`)

   - Two distinct subsystems:
     - Policy/Governance TARL (v2.0)
     - Language Runtime VM (v1.0.0)
   - Constitutional kernel with immutable constraints
   - Bytecode compilation and execution

1. **Governance Layer**

   - Triumvirate oversight (Galahad, Cerberus, Codex)
   - Command override system with master password
   - Four Laws ethics framework
   - Audit logging with hash chains

1. **Data Persistence**

   - JSON-based state files in `data/`
   - Fernet encryption for sensitive data
   - bcrypt password hashing
   - Git-tracked configuration

______________________________________________________________________

## Attack Surface Analysis

### 1. Desktop Application Attack Surface

**Surface**: PyQt6 GUI running as user process

#### Attack Vectors

- **UI Input Injection**: Malicious input via text fields, file pickers
- **File System Access**: Arbitrary file read/write within user permissions
- **Process Execution**: Can spawn subprocesses (by design)
- **Memory Manipulation**: PyQt6 vulnerabilities, Python interpreter exploits

#### Mitigations

- ✅ Input validation on all user inputs
- ✅ Sandboxed plugin execution
- ✅ Resource limits enforced
- ✅ Exception handling prevents crashes
- ⚠️ Runs with user privileges (intentional - not a service)

#### Risk Level: **MEDIUM**

*Rationale*: Local attack only, requires user to run malicious code

______________________________________________________________________

### 2. TARL Runtime Attack Surface

**Surface**: Bytecode VM executing TARL policy code

#### Attack Vectors

- **Bytecode Injection**: Crafted bytecode bypassing constitutional checks
- **Resource Exhaustion**: Infinite loops, memory bombs
- **Constitutional Bypass**: Exploiting gaps in axiom enforcement
- **Type Confusion**: VM type system vulnerabilities

#### Mitigations

- ✅ Constitutional kernel validates ALL operations before execution
- ✅ Bytecode signing and verification
- ✅ Resource limits (execution timeout, memory caps)
- ✅ Immutable axioms cannot be overridden
- ✅ Stack-based VM with bounded operations

#### Risk Level: **LOW**

*Rationale*: Defense-in-depth with constitutional guarantees

______________________________________________________________________

### 3. Data Persistence Attack Surface

**Surface**: JSON files in `data/` directory

#### Attack Vectors

- **JSON Injection**: Malformed JSON corrupting state
- **File Permission Escalation**: Modifying files outside data directory
- **State Tampering**: Direct modification of state files
- **Backup/Recovery Exploits**: Restoring malicious state

#### Mitigations

- ✅ JSON validation on load
- ✅ File permissions restricted to user
- ✅ State integrity checks via hash chains
- ✅ Audit logging of all state changes
- ⚠️ No encryption at rest for non-sensitive data (performance trade-off)

#### Risk Level: **MEDIUM**

*Rationale*: Local access required, mitigated by file permissions

______________________________________________________________________

### 4. Web API Attack Surface (Optional Component)

**Surface**: Flask API endpoints (if deployed)

#### Attack Vectors

- **API Injection**: SQL injection, command injection via API
- **Authentication Bypass**: Weak authentication, session hijacking
- **CSRF**: Cross-site request forgery
- **Rate Limiting**: DoS via API flooding

#### Mitigations

- ✅ Input sanitization on all endpoints
- ✅ JWT-based authentication
- ✅ CORS configuration
- ✅ Rate limiting middleware
- ⚠️ TLS termination at reverse proxy (deployment responsibility)

#### Risk Level: **HIGH** (if exposed to internet)

*Rationale*: Network-accessible, requires robust deployment

______________________________________________________________________

### 5. Governance Bypass Attack Surface

**Surface**: Command override system, master password

#### Attack Vectors

- **Master Password Brute Force**: Weak password cracking
- **Override Audit Log Tampering**: Modifying audit trail
- **Constitutional Kernel Bypass**: Exploiting governance gaps
- **Replay Attacks**: Reusing captured override commands

#### Mitigations

- ✅ SHA-256 hashed master password
- ✅ Immutable audit log with hash chains
- ✅ Constitutional kernel enforces limits even on overrides
- ✅ Time-limited override tokens
- ⚠️ Master password is ultimate override (by design)

#### Risk Level: **HIGH** (if master password compromised)

*Rationale*: Intentional backdoor for emergency use

______________________________________________________________________

## Trust Boundaries

### Boundary 1: User ↔ Application

- **Trust**: User trusts application with local file access
- **Assumption**: User is running on their own machine
- **Protection**: Application cannot escalate beyond user privileges

### Boundary 2: Application ↔ TARL Runtime

- **Trust**: Application trusts TARL runtime for policy enforcement
- **Assumption**: TARL constitutional kernel is non-bypassable
- **Protection**: All policy decisions validated by kernel

### Boundary 3: Plugin ↔ Core System

- **Trust**: Core system does NOT trust plugins
- **Assumption**: Plugins may be malicious
- **Protection**: Sandboxed execution, resource limits, API restrictions

### Boundary 4: External APIs ↔ Application

- **Trust**: Application does NOT trust external APIs
- **Assumption**: External services may be compromised
- **Protection**: API response validation, timeout enforcement, error handling

______________________________________________________________________

## Intentional Non-Defenses

> **Critical**: These are conscious design decisions, not oversights.

### 1. **No Privilege Separation**

- **Reason**: Desktop application runs as user process
- **Impact**: Malicious code has full user file access
- **Mitigation**: User education, code review, plugin sandboxing
- **Alternative Rejected**: Running as separate service (complexity cost)

### 2. **Master Password Override**

- **Reason**: Emergency override required for catastrophic failures
- **Impact**: Compromised master password bypasses all safeguards
- **Mitigation**: Strong password requirements, audit logging
- **Alternative Rejected**: No override mechanism (operational risk)

### 3. **JSON-Based State Storage**

- **Reason**: Human-readable, debuggable, version-controllable
- **Impact**: State files can be manually edited (corruption risk)
- **Mitigation**: Validation on load, integrity checks
- **Alternative Rejected**: Binary format (debugging cost)

### 4. **Monolithic Architecture**

- **Reason**: Simplified deployment, deterministic behavior
- **Impact**: Single point of failure, no process isolation
- **Mitigation**: Defense-in-depth, constitutional guarantees
- **Alternative Rejected**: Microservices (complexity cost)

### 5. **Local Inference Only**

- **Reason**: Privacy-first design, no cloud dependency
- **Impact**: Cannot defend against local model poisoning
- **Mitigation**: Model integrity checks, source verification
- **Alternative Rejected**: Cloud-based AI (privacy cost)

______________________________________________________________________

## Threat Scenarios

### Scenario 1: Malicious Plugin Installation

**Attacker Goal**: Execute arbitrary code via plugin **Attack Path**: User installs compromised plugin **Impact**: File access within user permissions, data exfiltration **Likelihood**: MEDIUM (requires social engineering) **Mitigation**: Plugin sandboxing, permission prompts, code signing

### Scenario 2: Master Password Compromise

**Attacker Goal**: Bypass all governance controls **Attack Path**: Phishing, keylogging, weak password **Impact**: COMPLETE control override, audit log tampering **Likelihood**: LOW (requires targeted attack) **Mitigation**: Strong password policy, 2FA (planned), audit monitoring

### Scenario 3: TARL Bytecode Exploit

**Attacker Goal**: Bypass constitutional constraints **Attack Path**: Crafted bytecode exploiting VM bug **Impact**: Policy bypass, unauthorized operations **Likelihood**: VERY LOW (constitutional kernel defense-in-depth) **Mitigation**: Bytecode validation, constitutional kernel, formal verification (planned)

### Scenario 4: State File Corruption

**Attacker Goal**: Corrupt application state **Attack Path**: Direct file modification, malformed JSON **Impact**: Application crash, data loss **Likelihood**: MEDIUM (local access required) **Mitigation**: JSON validation, integrity checks, backups

### Scenario 5: Web API Exploitation (Deployment)

**Attacker Goal**: Remote code execution **Attack Path**: API injection, authentication bypass **Impact**: Server compromise, data breach **Likelihood**: HIGH (if poorly deployed) **Mitigation**: Security hardening guide, TLS, WAF, rate limiting

______________________________________________________________________

## Security Controls Inventory

### Implemented Controls

| Control                 | Type       | Effectiveness | Coverage            |
| ----------------------- | ---------- | ------------- | ------------------- |
| Constitutional Kernel   | Preventive | HIGH          | TARL Runtime        |
| Audit Logging           | Detective  | HIGH          | All operations      |
| Input Validation        | Preventive | MEDIUM        | All user inputs     |
| bcrypt Password Hashing | Preventive | HIGH          | User authentication |
| Fernet Encryption       | Preventive | HIGH          | Sensitive data      |
| Plugin Sandboxing       | Preventive | MEDIUM        | Plugin execution    |
| Resource Limits         | Preventive | MEDIUM        | Runtime protection  |
| Hash Chain Integrity    | Detective  | HIGH          | Audit logs          |
| JSON Validation         | Preventive | MEDIUM        | State persistence   |
| Exception Handling      | Resilience | HIGH          | Error conditions    |

### Planned Controls

- 2FA for master password
- Formal verification of TARL VM
- Binary signing for releases
- Automated vulnerability scanning
- Dependency SBOM monitoring
- Reproducible builds

______________________________________________________________________

## Compliance & Standards

### Applicable Standards

- ✅ OWASP Top 10 (2021) - Mitigations documented
- ✅ CWE Top 25 - Coverage analysis complete
- ⚠️ NIST 800-53 - Partial compliance (desktop app)
- ⚠️ ISO 27001 - Controls mapped

### Out of Scope

- PCI-DSS (no payment processing)
- HIPAA (no PHI storage - unless user-configured)
- FedRAMP (not government deployment)
- SOC 2 Type II (no hosted service)

______________________________________________________________________

## Incident Response

### Severity Levels

**Critical (P0)**: Master password compromise, TARL VM exploit **High (P1)**: Plugin sandbox escape, authentication bypass **Medium (P2)**: State corruption, resource exhaustion **Low (P3)**: Minor validation gaps, logging issues

### Response Procedures

1. **Detection**: Audit log monitoring, anomaly detection
1. **Containment**: Immediate shutdown, state backup
1. **Investigation**: Audit log analysis, forensics
1. **Remediation**: Patch deployment, state recovery
1. **Post-Mortem**: Root cause analysis, documentation

### Contact

- **Security Team**: security@project-ai.dev
- **Bug Bounty**: (coming soon)

______________________________________________________________________

## Risk Acceptance

### Accepted Risks

| Risk                       | Justification               | Monitoring            |
| -------------------------- | --------------------------- | --------------------- |
| Local privilege escalation | User process by design      | Audit logs            |
| State file tampering       | User owns data              | Integrity checks      |
| Master password compromise | Emergency override required | Failed login tracking |
| Monolithic architecture    | Simplified deployment       | Health monitoring     |
| JSON state storage         | Debuggability priority      | Validation on load    |

______________________________________________________________________

## Review & Updates

**Review Frequency**: Quarterly **Next Review**: 2026-05-08 **Owner**: @IAmSoThirsty **Approvers**: Security Team, Architecture Team

### Change Log

| Date       | Version | Changes              |
| ---------- | ------- | -------------------- |
| 2026-02-08 | 1.0.0   | Initial threat model |

______________________________________________________________________

## Conclusion

This threat model provides explicit boundaries for security assessment. It acknowledges intentional design trade-offs and focuses defensive resources on high-impact risks.

**Key Takeaway**: Project-AI prioritizes privacy, auditability, and determinism over defense-in-depth isolation. This is a conscious architecture decision optimizing for single-user desktop deployment.

For adversarial review or security research:

- See `docs/security_compliance/SECURITY_REVIEW_GUIDE.md`
- Contact: security@project-ai.dev

______________________________________________________________________

**Maintained by**: Security & Architecture Teams **Classification**: Public **Distribution**: Unlimited
