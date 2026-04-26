---
title: Governance CLI System
type: technical-reference
audience: [security-engineers, auditors]
classification: P0-Core
tags: [governance, cryptography, audit]
created: 2024-01-20
status: current
---

# Governance CLI System

**Cryptographic governance enforcement through CLI.**

## Core Components

- **IronPathExecutor** - Pipeline orchestration
- **SovereignRuntime** - Governance enforcement with Ed25519
- **AuditTrail** - Immutable SHA-256 hash chain
- **ComplianceBundle** - Tamper-evident audit packages

## Commands

```bash
# Execute sovereign pipeline
project-ai run pipeline.yaml

# Verify audit trail
project-ai verify-audit audit.jsonl

# Third-party verification
project-ai sovereign-verify --bundle compliance.json
```

## Cryptographic Guarantees

1. Immutability - Hash chain prevents modification
2. Authenticity - Ed25519 signatures
3. Non-repudiation - Signed actions
4. Tamper-evidence - Broken chain detection
5. Auditability - Complete action trail

---

**AGENT-038: CLI & Automation Documentation Specialist**
