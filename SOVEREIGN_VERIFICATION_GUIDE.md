# Sovereign Verification System - Quick Start Guide

## Overview

The Sovereign Verification System enables **third-party auditors** to independently verify Project-AI's compliance bundles without trusting the provider. This makes **trust portable** through cryptography.

## Key Command

```bash
python project_ai_cli.py sovereign-verify --bundle compliance_bundle.json
```

## What It Verifies

1. **Hash Chain Validation**
   - Cryptographically verifies every audit block (SHA-256)
   - Checks blockchain-style hash chain linkage
   - Detects any tampering in the audit trail
   - Reports: X/Y blocks verified

2. **Signature Authority Map**
   - Verifies Ed25519 signatures
   - Maps all signing authorities
   - Provides public key fingerprint
   - Reports: X/Y signatures verified

3. **Policy Resolution Trace**
   - Traces all policy decisions through audit log
   - Counts passed/failed resolutions
   - Provides timeline of enforcement
   - Reports: X policy resolutions

4. **Timestamped Attestation**
   - Generates unique attestation ID
   - Includes verification timestamp
   - Creates verification hash
   - Provides independent proof certificate

## Usage Examples

### Basic Verification
```bash
python project_ai_cli.py sovereign-verify --bundle compliance_bundle.json
```

### With Report Export
```bash
python project_ai_cli.py sovereign-verify \
  --bundle compliance.zip \
  --output verification_report.json
```

### Third-Party Auditor Workflow

**Step 1:** Receive compliance bundle
```bash
# Auditor receives: compliance_bundle.json or compliance.zip
```

**Step 2:** Run verification
```bash
python project_ai_cli.py sovereign-verify \
  --bundle compliance_bundle.json \
  --output audit_verification.json
```

**Step 3:** Review results
- ✅ Hash Chain: PASS/FAIL
- ✅ Signatures: X/Y verified
- ✅ Policy Trace: X resolutions
- ✅ Attestation: Independent proof

**Step 4:** Save report
```bash
# Detailed JSON report saved to audit_verification.json
# Share with stakeholders as cryptographic proof
```

## Output Structure

```
================================================================================
SOVEREIGN VERIFICATION SYSTEM
================================================================================

1. Hash Chain Validation: PASS (41/41 blocks)
2. Signature Authority Map: PASS (14/14 signatures)
3. Policy Resolution Trace: PASS (12 resolutions)
4. Timestamped Attestation: 28bbc6ff...

================================================================================
SUMMARY
================================================================================
Overall Status: PASS
Bundle Version: 1.0.0
Total Audit Blocks: 41
Blocks Verified: 41
Signatures Verified: 14
Policy Resolutions: 12
================================================================================
```

## Verification Report

The `--output` flag saves a detailed JSON report:

```json
{
  "verification_timestamp": "2026-02-03T22:09:02.620679",
  "overall_status": "pass",
  "checks": {
    "hash_chain_validation": {
      "status": "pass",
      "details": {
        "total_blocks": 41,
        "blocks_verified": 41,
        "chain_integrity": "intact"
      }
    },
    "signature_authority_mapping": {
      "status": "pass",
      "details": {
        "public_key_fingerprint": "f9e001262157f123",
        "signatures_verified": 14
      },
      "authorities": {
        "pipeline_executor": {
          "occurrences": 12,
          "verified": 12
        }
      }
    },
    "policy_resolution_trace": {
      "status": "pass",
      "details": {
        "total_resolutions": 12,
        "passed_resolutions": 12,
        "failed_resolutions": 0
      }
    }
  },
  "attestation": {
    "attestation_id": "28bbc6ffb444b5b9bfe976d143a09d3c...",
    "timestamp": "2026-02-03T22:09:02.620679",
    "verifier": "Project-AI Sovereign Verifier v1.0.0",
    "verification_hash": "711ea21267d6687bf4603264756c3364...",
    "cryptographic_proof": {
      "algorithm": "Ed25519",
      "public_key_fingerprint": "f9e001262157f123",
      "total_blocks_verified": 41,
      "total_signatures_verified": 14
    }
  }
}
```

## Why This Matters

### Before: Trust-Based
- "We have policies" (documentation)
- "Trust us" (promise)
- "We're compliant" (claim)

### After: Cryptography-Based
- "Verify independently" (cryptography)
- "Check the hash chain" (SHA-256)
- "Validate the signatures" (Ed25519)
- "Review the attestation" (proof)

## Key Benefits

1. **Independent Verification**
   - Third parties can verify without provider access
   - All verification is cryptographic
   - No trust assumptions

2. **Tamper Detection**
   - Hash chain breaks if modified
   - Signatures fail if content changes
   - Immediate detection

3. **Portable Trust**
   - Auditors don't need to trust provider
   - Cryptographic proofs are self-evident
   - Attestation proves verification occurred

4. **Compliance Ready**
   - Export detailed reports
   - Share with stakeholders
   - Regulatory submission ready

## Files Involved

- **Verifier:** `governance/sovereign_verifier.py`
- **CLI:** `project_ai_cli.py` (sovereign-verify command)
- **Tests:** `tests/test_sovereign_verifier.py`
- **Docs:** `SOVEREIGN_RUNTIME.md`

## Exit Codes

- `0` - Verification PASSED
- `1` - Verification FAILED
- `2` - Verification WARNING

## Complete Workflow Example

```bash
# Step 1: Generate compliance bundle
python project_ai_cli.py run examples/sovereign-demo.yaml

# Step 2: Verify bundle (third-party auditor)
BUNDLE=$(find governance/sovereign_data/artifacts -name "compliance_bundle.json" | head -1)
python project_ai_cli.py sovereign-verify \
  --bundle "$BUNDLE" \
  --output verification_report.json

# Step 3: Review report
cat verification_report.json | python -m json.tool

# Step 4: Share attestation with stakeholders
# The verification_report.json contains cryptographic proof
```

## Trust Is Now Portable

**Problem:** How do third-party auditors verify without trusting the provider?

**Solution:** Cryptographic verification with portable trust.

**Command:**
```bash
project-ai sovereign-verify --bundle compliance.zip
```

**Result:**
- ✅ Hash chain verified (SHA-256)
- ✅ Signatures verified (Ed25519)
- ✅ Policy trace complete
- ✅ Attestation generated
- ✅ Trust is portable

**This is not documentation. This is cryptographic proof.**
