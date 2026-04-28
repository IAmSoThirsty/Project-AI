---
title: Sovereign Runtime CLI
type: technical-reference
audience: [security-engineers, auditors, compliance-officers]
classification: P0-Core
tags: [sovereign-runtime, cryptography, governance, audit-trail]
created: 2024-01-20
last_verified: 2024-01-20
status: current
related_systems: [governance, cryptography, audit-system]
---

# Sovereign Runtime CLI

**Cryptographically enforced governance through execution, not documentation.**

## Executive Summary

The Sovereign Runtime CLI (`project-ai`) provides command-line access to Project-AI's cryptographic governance enforcement system. It enables:
- **Sovereign Pipeline Execution** - Run governance-enforced workflows
- **Audit Trail Verification** - Validate immutable hash chain integrity
- **Compliance Bundle Generation** - Generate tamper-evident compliance packages
- **Third-Party Verification** - Comprehensive auditor verification tools

**Entry Point:** `project_ai_cli.py`  
**Installation:** `pip install -e .` creates `project-ai` command

---

## Architecture

### Cryptographic Governance Model

```
Pipeline Execution
    ↓
Config Snapshot (signed)
    ↓
Role Authorization (Ed25519)
    ↓
Policy Enforcement (TARL)
    ↓
Immutable Audit Trail (hash chain)
    ↓
Compliance Bundle (timestamped)
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **IronPathExecutor** | Pipeline orchestration | Python |
| **SovereignRuntime** | Governance enforcement | Ed25519 signatures |
| **AuditTrail** | Immutable log | SHA-256 hash chain |
| **ComplianceBundle** | Audit package | JSON + cryptographic proofs |
| **SovereignVerifier** | Third-party verification | Independent validation |

---

## Command Reference

### 1. run - Execute Sovereign Pipeline

**Purpose:** Execute a sovereign pipeline with cryptographic governance enforcement

**Syntax:**
```bash
project-ai run <pipeline-path>
```

**Arguments:**
- `pipeline-path` - Path to sovereign pipeline YAML file

**Example:**
```bash
project-ai run examples/sovereign-demo.yaml
```

**Output:**
```
================================================================================
PROJECT-AI SOVEREIGN RUNTIME
================================================================================
Pipeline: examples/sovereign-demo.yaml
================================================================================

[Stage 1/3] Snapshot Configuration
  ✓ Config signed: 3b5a7c9d...
  ✓ Role: system_admin
  ✓ Policy: allow_mutation

[Stage 2/3] Execute Actions
  ✓ Action: create_user
  ✓ Policy check: PASS (Asimov Law 1)
  ✓ Audit entry: Block 1 (hash: 8f2e1a4b...)

[Stage 3/3] Generate Compliance Bundle
  ✓ Artifacts directory: governance/sovereign_data/artifacts/exec_20240120_153045/
  ✓ Compliance bundle: compliance_bundle.json

================================================================================
✅ EXECUTION SUCCESSFUL
================================================================================
Execution ID: exec_20240120_153045
Stages Completed: 3
Artifacts Directory: governance/sovereign_data/artifacts/exec_20240120_153045/
Audit Trail Integrity: VALID

Generated Artifacts:
  • snapshot_config
    Hash: 3b5a7c9d8e1f4a2b7c6d9e0f1a2b3c4d
    Path: governance/sovereign_data/artifacts/exec_20240120_153045/snapshot_config.json

  • action_results
    Hash: 8f2e1a4b5c7d9e0f1a2b3c4d5e6f7a8b
    Path: governance/sovereign_data/artifacts/exec_20240120_153045/action_results.json

================================================================================

🔒 Cryptographic Proof Generated
   - Config snapshot signed: ✓
   - Role signatures verified: ✓
   - Policy bindings enforced: ✓
   - Audit trail immutable: ✓

📦 Compliance Bundle: governance/sovereign_data/artifacts/exec_20240120_153045/compliance_bundle.json
================================================================================
```

**Exit Codes:**
- `0` - Execution successful
- `1` - Execution failed (see error message)

---

### 2. sovereign-verify - Comprehensive Third-Party Verification

**Purpose:** Comprehensive verification for third-party auditors (recommended for audits)

**Syntax:**
```bash
project-ai sovereign-verify --bundle <bundle-path> [--output <report-path>]
```

**Arguments:**
- `--bundle` (required) - Path to compliance bundle (JSON or ZIP)
- `--output` (optional) - Path to save detailed verification report (JSON)

**Example:**
```bash
# Verify compliance bundle
project-ai sovereign-verify --bundle compliance_bundle.json

# Verify and save report
project-ai sovereign-verify \
    --bundle compliance_bundle.json \
  --output test-artifacts/verification_report.json
```

**Output:**
```
================================================================================
VERIFICATION RESULTS
================================================================================

✅ VERIFICATION PASSED

Hash Chain Validation:
  Status: PASS
  Blocks Verified: 125 / 125

Signature Authority Map:
  Status: PASS
  Algorithm: Ed25519
  Public Key Fingerprint: a3b5c7d9...
  Signatures Verified: 45 / 45
  Authorities:
    • system_admin: 30 occurrences, 30 verified
    • security_officer: 15 occurrences, 15 verified

Policy Resolution Trace:
  Status: PASS
  Total Resolutions: 78
  Passed: 78
  Failed: 0

Timestamped Attestation:
  Attestation ID: att_20240120_153045_a3b5c7...
  Timestamp: 2024-01-20T15:30:45Z
  Verifier: SovereignVerifier v1.0.0
  Verification Hash: f7e8d9c0b1a2...

================================================================================
SUMMARY
================================================================================
Bundle Version: 1.0.0
Total Audit Blocks: 125
Blocks Verified: 125
Signatures Verified: 45
Policy Resolutions: 78
Overall Status: PASS
================================================================================

📄 Full verification report saved to: test-artifacts/verification_report.json
```

**Exit Codes:**
- `0` - Verification passed
- `1` - Verification failed
- `2` - Verification passed with warnings

**Verification Report Structure:**
```json
{
  "overall_status": "pass",
  "checks": {
    "hash_chain_validation": {
      "status": "pass",
      "details": {
        "blocks_verified": 125,
        "total_blocks": 125
      },
      "issues": []
    },
    "signature_authority_mapping": {
      "status": "pass",
      "details": {
        "algorithm": "Ed25519",
        "public_key_fingerprint": "a3b5c7d9...",
        "signatures_verified": 45,
        "signatures_found": 45
      },
      "authorities": {
        "system_admin": {
          "occurrences": 30,
          "verified": 30
        }
      }
    },
    "policy_resolution_trace": {
      "status": "pass",
      "details": {
        "total_resolutions": 78,
        "passed_resolutions": 78,
        "failed_resolutions": 0
      }
    }
  },
  "attestation": {
    "attestation_id": "att_20240120_153045_a3b5c7...",
    "timestamp": "2024-01-20T15:30:45Z",
    "verifier": "SovereignVerifier v1.0.0",
    "verification_hash": "f7e8d9c0b1a2..."
  },
  "summary": {
    "bundle_version": "1.0.0",
    "total_audit_blocks": 125,
    "blocks_verified": 125,
    "signatures_verified": 45,
    "policy_resolutions": 78,
    "overall_status": "pass"
  }
}
```

---

### 3. verify-audit - Audit Trail Integrity Verification

**Purpose:** Verify audit trail hash chain integrity (lightweight verification)

**Syntax:**
```bash
project-ai verify-audit <audit-log-path>
```

**Arguments:**
- `audit-log-path` - Path to immutable audit log file (JSONL format)

**Example:**
```bash
project-ai verify-audit governance/sovereign_data/immutable_audit.jsonl
```

**Output:**
```
================================================================================
AUDIT TRAIL VERIFICATION
================================================================================
Audit Log: governance/sovereign_data/immutable_audit.jsonl
================================================================================

✅ AUDIT TRAIL INTEGRITY VERIFIED

All blocks have valid hashes
Hash chain is unbroken
No tampering detected

================================================================================
```

**Failed Verification Example:**
```
================================================================================
AUDIT TRAIL VERIFICATION
================================================================================
Audit Log: governance/sovereign_data/immutable_audit.jsonl
================================================================================

❌ AUDIT TRAIL INTEGRITY FAILED

Issues detected:
  • Block 15: Hash mismatch (expected: 8f2e1a4b..., actual: 9a3b2c5d...)
  • Block 23: Missing previous_hash reference
  • Block 45: Invalid hash format

================================================================================
```

**Exit Codes:**
- `0` - Audit trail integrity verified
- `1` - Audit trail integrity failed

**Audit Log Format (JSONL):**
```jsonl
{"block_id": 0, "timestamp": "2024-01-20T15:30:45Z", "action": "init", "hash": "genesis", "previous_hash": null}
{"block_id": 1, "timestamp": "2024-01-20T15:30:46Z", "action": "create_user", "hash": "8f2e1a4b...", "previous_hash": "genesis"}
{"block_id": 2, "timestamp": "2024-01-20T15:30:47Z", "action": "assign_role", "hash": "3b5a7c9d...", "previous_hash": "8f2e1a4b..."}
```

---

### 4. verify-bundle - Compliance Bundle Verification

**Purpose:** Verify compliance bundle cryptographic proofs

**Syntax:**
```bash
project-ai verify-bundle <bundle-path>
```

**Arguments:**
- `bundle-path` - Path to compliance bundle JSON file

**Example:**
```bash
project-ai verify-bundle governance/sovereign_data/artifacts/*/compliance_bundle.json
```

**Output:**
```
================================================================================
COMPLIANCE BUNDLE VERIFICATION
================================================================================
Bundle: governance/sovereign_data/artifacts/exec_20240120_153045/compliance_bundle.json
================================================================================

Bundle Version: 1.0.0
Generated At: 2024-01-20T15:30:48Z
Total Audit Blocks: 125

✅ BUNDLE INTEGRITY VERIFIED

All cryptographic proofs valid
Audit trail integrity confirmed
Bundle suitable for compliance review

================================================================================
```

**Exit Codes:**
- `0` - Bundle integrity verified
- `1` - Bundle integrity failed

**Compliance Bundle Structure:**
```json
{
  "version": "1.0.0",
  "generated_at": "2024-01-20T15:30:48Z",
  "execution_id": "exec_20240120_153045",
  "artifacts": {
    "snapshot_config": {
      "path": "snapshot_config.json",
      "hash": "3b5a7c9d8e1f4a2b7c6d9e0f1a2b3c4d",
      "signature": "a1b2c3d4..."
    },
    "action_results": {
      "path": "action_results.json",
      "hash": "8f2e1a4b5c7d9e0f1a2b3c4d5e6f7a8b"
    }
  },
  "audit_trail": {
    "total_blocks": 125,
    "first_block_hash": "genesis",
    "last_block_hash": "f7e8d9c0...",
    "hash_chain_valid": true
  },
  "integrity_verification": {
    "is_valid": true,
    "verified_at": "2024-01-20T15:30:48Z",
    "issues": []
  },
  "signatures": {
    "bundle_signature": "b2c3d4e5...",
    "signing_authority": "system_admin",
    "public_key_fingerprint": "a3b5c7d9..."
  }
}
```

---

## Pipeline Configuration

### Sovereign Pipeline YAML Format

```yaml
# examples/sovereign-demo.yaml
name: "Sovereign Demonstration Pipeline"
version: "1.0.0"
description: "Demonstrates cryptographically enforced governance"

roles:
  - name: system_admin
    permissions:
      - create_user
      - assign_role
      - modify_policy

policies:
  - id: asimov_law_1
    description: "AI must not harm humans"
    enforcement: strict
    
  - id: allow_mutation
    description: "Allow system state modifications"
    enforcement: strict

stages:
  - name: initialize
    actions:
      - type: snapshot_config
        config_path: governance/config.json
        
  - name: execute
    actions:
      - type: create_user
        user_id: test_user_001
        role: developer
        policy_check: asimov_law_1
        
      - type: assign_role
        user_id: test_user_001
        role: admin
        policy_check: allow_mutation
        
  - name: finalize
    actions:
      - type: generate_compliance_bundle
        output_dir: governance/sovereign_data/artifacts/
```

### Pipeline Execution Flow

```
1. Load Pipeline YAML
    ↓
2. Initialize SovereignRuntime
    ↓
3. Snapshot Configuration (signed)
    ↓
4. For each stage:
    a. Validate role authorization
    b. Enforce policy checks (TARL)
    c. Execute action
    d. Record to audit trail (hash chain)
    e. Generate artifact (if applicable)
    ↓
5. Verify Audit Trail Integrity
    ↓
6. Generate Compliance Bundle
    ↓
7. Sign Bundle (Ed25519)
    ↓
8. Return Execution Result
```

---

## Cryptographic Implementation

### Hash Chain Algorithm

```python
def compute_block_hash(block):
    """Compute SHA-256 hash of audit block."""
    content = f"{block['block_id']}{block['timestamp']}{block['action']}{block['previous_hash']}"
    return hashlib.sha256(content.encode()).hexdigest()

def verify_hash_chain(blocks):
    """Verify hash chain integrity."""
    for i in range(1, len(blocks)):
        expected_previous = blocks[i-1]['hash']
        actual_previous = blocks[i]['previous_hash']
        
        if expected_previous != actual_previous:
            return False, f"Block {i}: Hash chain broken"
    
    return True, "Hash chain valid"
```

### Ed25519 Signature Verification

```python
from cryptography.hazmat.primitives.asymmetric import ed25519

def verify_signature(public_key, message, signature):
    """Verify Ed25519 signature."""
    try:
        public_key.verify(signature, message)
        return True
    except InvalidSignature:
        return False
```

### Tamper Detection

```python
def detect_tampering(audit_log):
    """Detect tampering in audit log."""
    issues = []
    
    for i, block in enumerate(audit_log):
        # Verify hash matches content
        computed_hash = compute_block_hash(block)
        if computed_hash != block['hash']:
            issues.append(f"Block {i}: Hash mismatch")
        
        # Verify previous_hash linkage
        if i > 0:
            expected_previous = audit_log[i-1]['hash']
            if block['previous_hash'] != expected_previous:
                issues.append(f"Block {i}: Broken chain")
    
    return len(issues) == 0, issues
```

---

## Security Considerations

### Threat Model

| Threat | Mitigation | Verification |
|--------|-----------|--------------|
| **Unauthorized execution** | Ed25519 role signatures | `sovereign-verify --bundle` |
| **Audit log tampering** | SHA-256 hash chain | `verify-audit` |
| **Policy bypass** | TARL enforcement | Policy resolution trace |
| **Replay attacks** | Timestamp + nonce | Attestation verification |
| **Bundle forgery** | Bundle signature | `verify-bundle` |

### Cryptographic Guarantees

1. **Immutability** - Hash chain prevents retroactive modification
2. **Authenticity** - Ed25519 signatures prove action authorization
3. **Non-repudiation** - Signed actions cannot be denied
4. **Tamper-evidence** - Any modification breaks hash chain
5. **Auditability** - Complete action trail for forensics

---

## Best Practices

### ✅ DO

- **Always verify bundles** before accepting compliance evidence
- **Use `sovereign-verify`** for comprehensive third-party audits
- **Store audit logs** in tamper-evident storage (WORM drives, S3 Object Lock)
- **Rotate signing keys** regularly (Ed25519 keypair generation)
- **Test pipelines** in dry-run mode before production
- **Archive compliance bundles** for regulatory retention periods

### ❌ DON'T

- **Don't skip verification** - Always verify before trusting
- **Don't modify audit logs** - Any change breaks hash chain
- **Don't share private keys** - Use role-based signatures
- **Don't ignore warnings** - Investigate all verification issues
- **Don't trust unverified bundles** - Always run `verify-bundle`
- **Don't disable policy enforcement** - Undermines governance

---

## Troubleshooting

### Issue: "Hash chain validation failed"

**Cause:** Audit log has been modified or corrupted

**Solution:**
```bash
# Verify audit log integrity
project-ai verify-audit immutable_audit.jsonl

# Check for specific issues
project-ai sovereign-verify --bundle compliance_bundle.json --output report.json
grep "issues" report.json
```

### Issue: "Signature verification failed"

**Cause:** Invalid signature, key mismatch, or tampering

**Solution:**
```bash
# Verify public key fingerprint
project-ai sovereign-verify --bundle compliance_bundle.json | grep "Public Key Fingerprint"

# Compare with expected fingerprint from governance/keys/
cat governance/keys/public_key_fingerprint.txt
```

### Issue: "Policy resolution trace shows failures"

**Cause:** Action violated governance policies

**Solution:**
```bash
# Review policy resolution details
project-ai sovereign-verify --bundle compliance_bundle.json --output report.json
jq '.checks.policy_resolution_trace.details' report.json
```

---

## Related Documentation

- **[01-CLI-OVERVIEW.md](./01-CLI-OVERVIEW.md)** - CLI interface overview
- **[11-GOVERNANCE-SYSTEM.md](./11-GOVERNANCE-SYSTEM.md)** - Governance architecture
- **[12-AUDIT-TRAIL.md](./12-AUDIT-TRAIL.md)** - Immutable audit trail
- **[13-CRYPTOGRAPHY.md](./13-CRYPTOGRAPHY.md)** - Cryptographic implementation

---

**AGENT-038: CLI & Automation Documentation Specialist**  
*Cryptographically enforced governance through execution.*
