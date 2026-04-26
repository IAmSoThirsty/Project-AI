---
title: "Project-AI Security Policy"
id: security-policy
type: policy
version: 1.1.0
created_date: 2025-11-01
updated_date: 2026-01-28
status: active
author: "Security Team <projectaidevs@gmail.com>"
tags:
  - security
  - security/audit
  - security/cryptography
  - security/authentication
  - security/application
  - governance
  - governance/policy
  - operations
  - operations/monitoring
  - policy
area:
  - security
  - governance
  - operations
component:
  - constitutional-ai
  - governance-engine
  - tarl
audience:
  - security
  - developer
  - architect
  - public
priority: p0
related_to:
  - "[[README]]"
  - "[[CONTRIBUTING]]"
  - "[[CODE_OF_CONDUCT]]"
what: "Security vulnerability reporting policy, supported version matrix, and comprehensive security architecture documentation including 8-layer defense system (HTTP gateway, intent validation, TARL enforcement, Triumvirate voting, formal invariants, security guards, audit logging, fail-closed defaults)"
who: "Security researchers, contributors, users - anyone discovering or needing to understand Project-AI security mechanisms"
when: "IMMEDIATELY when security vulnerability discovered - reference when understanding security architecture or deploying to production"
where: "Root directory as canonical security disclosure policy - referenced in security advisories and vulnerability reports"
why: "Provides responsible disclosure channel, documents multi-layer constitutional security architecture (TARL + Cerberus + Galahad voting), tracks known security notes (e.g., example keys in git history), establishes 48-hour response SLA"
---

# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in Project-AI, please report it by emailing the maintainers or using GitHub's private security advisory feature. **Do not create a public issue.**

We aim to respond to security reports within 48 hours and will work with you to understand and resolve the issue promptly.

## Security Features

Project-AI implements multiple layers of security:

1. **HTTP Gateway** - CORS validation, request sanitization
2. **Intent Validation** - Type checking and schema validation
3. **TARL Enforcement** - Hard policy gate at entry
4. **Triumvirate Voting** - Multi-pillar consensus (Galahad, Cerberus, CodexDeus)
5. **Formal Invariants** - Provable mathematical constraints
6. **Security Guards** - Hydra (expansion prevention), Boundary (network protection), Policy (action whitelisting)
7. **Audit Logging** - Immutable cryptographic trail with intent hashing
8. **Fail-Closed Default** - Deny execution unless explicitly allowed

## Audit Trail & Compliance

Project-AI implements **comprehensive cryptographic audit trails** for all security-critical operations:

### Audit Trail Implementations

1. **[[src/app/governance/audit_log]]** - SHA-256 hash-chained audit log (SOC2, GDPR)
   - Cryptographic tamper detection
   - YAML append-only format
   - Chain verification: `verify_chain()`

2. **[[src/app/audit/tamperproof_log]]** - Immutable event logging (SOC2, HIPAA)
   - Append-only operations
   - Integrity verification
   - JSON export for compliance

3. **[[atlas/audit/trail]]** - ATLAS audit trail system (SOC2, GDPR, HIPAA)
   - Event categorization (8 types)
   - Severity levels (5 levels)
   - JSONL format with statistics

4. **[[src/app/security/advanced/privacy_ledger]]** - Privacy event tracking (GDPR, HIPAA)
   - Data subject rights logging
   - Consent management
   - Access logging (Article 15, 164.312(b))

5. **[[src/app/core/command_override]]** - Privileged access auditing (SOC2, ISO 27001)
   - Master password authentication
   - Override tracking for 10+ safety protocols
   - Failed authentication attempts

6. **[[src/app/security/monitoring]]** - Security event monitoring (SOC2, ISO 27001)
   - Real-time threat detection
   - Incident classification
   - Alert generation

**Complete Audit Documentation:** [[AGENT-091-AUDIT-TRAIL-MATRIX]]

### Compliance Coverage

- ✅ **SOC2** - CC6.1, CC6.2, CC7.2, CC7.3, CC8.1 (100% coverage)
- ✅ **GDPR** - Articles 15, 17, 20, 22, 30, 32 (100% coverage)
- ✅ **HIPAA** - 164.308(a)(1)(ii)(D), 164.312(b) (100% coverage)
- ✅ **ISO 27001** - A.9.4.1, A.9.4.2, A.12.1.2, A.12.4.1, A.16.1.2 (100% coverage)
- ✅ **AI Act** - Articles 12, 13, 14 (100% coverage)

**Cryptographic Coverage:** 80% (12/15 implementations with SHA-256 hash chaining)

See [[AGENT-091-AUDIT-TRAIL-MATRIX]] for complete traceability matrix.

---

## Known Security Notes

### Example/Test Keys in Git History

**Commit:** `9134791530f193bde79d2afddeefd2342e0c5e90`  
**Date:** 2026-01-28 21:05:59 UTC  
**Files Affected:**

- `data/sovereign_messages_ai/identity.json`
- `data/sovereign_messages_multi_ai/identity.json`
- `data/sovereign_messages_multi_alice/identity.json`
- `data/sovereign_messages_multi_bob/identity.json`
- `data/sovereign_messages_multi_charlie/identity.json`
- `data/sovereign_messages_user/identity.json`

**Status:** Files removed from HEAD (current working tree is clean)  
**Classification:** Example/test RSA private keys only  
**Risk Level:** LOW - These are demonstration keys for the sovereign messaging integration example  
**Recommendation:** Generate new cryptographic keys for any production deployment

**Important:** These keys were never used in production and were only included as examples to demonstrate the sovereign messaging feature. If you are deploying Project-AI in a production environment, you must generate your own unique keys using:

```python
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Generate new key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Export private key
pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
```

## Security Best Practices

### API Key Management

- Never commit `.env` files to version control
- Use environment variables for all sensitive configuration
- Rotate API keys regularly
- Use different keys for development, staging, and production

### Deployment Security

- Enable HTTPS/TLS for all API endpoints
- Configure CORS properly for your domain
- Use strong `SECRET_KEY` values (32+ characters, cryptographically random)
- Enable rate limiting on public endpoints
- Review and update `CORS_ORIGINS` to only allow trusted domains

### Audit and Monitoring

- Regularly review `audit.log` for suspicious activity
- Enable comprehensive logging (set `LOG_LEVEL=INFO` or `DEBUG`)
- Monitor Triumvirate governance decisions for denied requests
- Set up alerts for repeated policy violations

### Third-Party Dependencies

- Regularly update dependencies: `pip install --upgrade -r requirements.txt`
- Run security scans: `pip-audit` and `safety check`
- Review GitHub Dependabot alerts
- Subscribe to security advisories for critical dependencies

## Compliance

Project-AI implements security controls aligned with:

- **ASL-3 (AI Safety Level 3)**: 30+ security controls
- **NIST AI RMF**: AI Risk Management Framework
- **OWASP LLM Top 10**: Protection against AI-specific vulnerabilities
- **OWASP Testing Guide v4**: Comprehensive security testing

## Security Testing

The project includes:

- 2,000+ adversarial red team tests
- 315+ OWASP-compliant tests (expanding to 1,500+)
- Automated security scanning via GitHub Actions
- CodeQL analysis
- Container security scanning (Trivy)
- Cloud configuration checks (Checkov)

## Contact

For security concerns, please contact the project maintainers through GitHub's security advisory system.

**Last Updated:** 2026-02-05
