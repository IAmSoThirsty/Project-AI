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

### 🚨 Security Validation Claims Policy

**MANDATORY REQUIREMENT FOR ALL PULL REQUESTS:**

All PRs that claim "production-ready," "enterprise best practices," "complete forensic capability," "runtime enforcement," or any assertion of operational security **MUST** include direct runtime validation output for **ALL** of the following:

1. **Unsigned Image Admission Denial** - Evidence of deployment denial for unsigned images
2. **Signed Image Admission Success** - Evidence of successful deployment for signed images
3. **Privileged Container Denial** - Evidence of deployment denial for privileged containers
4. **Cross-Namespace/Lateral Communication Denial** - Evidence of network policy enforcement
5. **Log Deletion Prevention** - Evidence of log deletion prevention or detection

**If ANY of these validations are missing**, the PR MUST use safe framing language ONLY:

- "Implementation aligns with enterprise hardening patterns."
- "Validation tests confirm configuration correctness."
- "Full adversarial validation is ongoing."

**PRs that claim runtime enforcement without complete evidence will be rejected with no exceptions.**

**Complete Policy:** See [.github/SECURITY_VALIDATION_POLICY.md](.github/SECURITY_VALIDATION_POLICY.md) for detailed requirements, evidence format, and enforcement process.

**Rationale:** This policy ensures that security claims are backed by verifiable runtime evidence, preventing false assertions and maintaining trust in Project-AI's security posture.

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
