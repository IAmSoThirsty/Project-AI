# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in Thirsty's Waterfall, please report it responsibly:

1. **DO NOT** create a public GitHub issue for security vulnerabilities
2. Email the security team at: security@thirstyswaterfall.example (or create a private security advisory)
3. Include detailed information about the vulnerability
4. Allow reasonable time for a fix before public disclosure

## Secret Management

### Overview

Thirsty's Waterfall implements comprehensive security features requiring proper secret management. **Never hardcode secrets in source code.**

### Guidelines

#### ✅ DO:

- Load secrets from environment variables
- Use secure vault systems (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault, etc.)
- Rotate secrets regularly (minimum every 90 days, or immediately if compromised)
- Use different secrets for dev/staging/production environments
- Generate cryptographically secure random values (minimum 256 bits / 32 bytes)
- Store secrets encrypted at rest
- Use minimal privilege principle (only grant access to secrets that are needed)
- Audit secret access and usage
- Revoke old secrets after rotation
- Use `.env` files locally (ensure they're in `.gitignore`)

#### ❌ DON'T:

- Hardcode secrets in source code
- Commit secrets to version control
- Share secrets via email, chat, or other insecure channels
- Log secret values (even debug logs)
- Store secrets in plain text files
- Use weak or predictable values
- Reuse secrets across environments
- Include secrets in error messages or stack traces

### Secret Types

This project uses several types of secrets:

1. **Cryptographic Keys**
   - Master encryption keys
   - Signing keys
   - Root keys
   - Must be at least 256 bits (32 bytes)
   - Must be cryptographically random

2. **Authentication Credentials**
   - User passwords
   - API tokens
   - Service account credentials
   - OAuth client secrets

3. **Hardware Security Module (HSM) Secrets**
   - TPM sealing keys
   - Secure enclave keys
   - HSM PIN codes
   - Hardware attestation keys

4. **VPN & Network Secrets**
   - VPN shared secrets
   - TLS certificates and private keys
   - DNS-over-HTTPS credentials

### Implementation

#### Loading Secrets from Environment

```python
import os

# Correct way to handle secrets

encryption_key = os.environ.get('MASTER_ENCRYPTION_KEY')
if not encryption_key:
    raise ValueError("MASTER_ENCRYPTION_KEY environment variable not set")

# For optional demo values, generate securely if not provided

import secrets
demo_key = os.environ.get('DEMO_KEY', secrets.token_bytes(32))
```

#### Generating Secure Random Values

```python
import secrets

# Generate random bytes (for keys)

key = secrets.token_bytes(32)  # 32 bytes = 256 bits

# Generate random hex string (for tokens)

token = secrets.token_hex(32)  # 64 character hex string

# Generate URL-safe base64 string

url_token = secrets.token_urlsafe(32)
```

#### Secret Rotation Procedure

1. **Generate New Secret**

   ```bash
   python -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
   ```

2. **Update Secret in Vault/Environment**
   - Update in secret management system
   - Update environment variables in all environments
   - Update CI/CD secrets

3. **Deploy New Secret**
   - Deploy to production with zero-downtime strategy
   - Support both old and new secret temporarily if needed
   - Monitor for errors

4. **Revoke Old Secret**
   - After confirming new secret works, revoke old one
   - Update documentation
   - Audit to ensure old secret is completely removed

5. **Document Rotation**
   - Record date of rotation
   - Record reason for rotation (scheduled vs. emergency)
   - Update incident log if rotation was due to exposure

### CI/CD Integration

#### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v3
      - name: Install dependencies

        run: pip install -r requirements.txt

      - name: Run tests

        env:

          # Load secrets from GitHub Secrets

          MASTER_ENCRYPTION_KEY: ${{ secrets.MASTER_ENCRYPTION_KEY }}
          API_TOKEN: ${{ secrets.API_TOKEN }}
        run: python -m unittest discover tests
```

#### GitLab CI Example

```yaml
test:
  script:

    - pip install -r requirements.txt
    - python -m unittest discover tests

  variables:

    # Use GitLab CI/CD variables (masked)

    MASTER_ENCRYPTION_KEY: $MASTER_ENCRYPTION_KEY
    API_TOKEN: $API_TOKEN
```

### Examples and Demos

Demo files (in `examples/`) may need to demonstrate functionality without requiring production secrets:

1. **Generate Random Demo Values**: Generate cryptographically secure random values at runtime
2. **Check Environment First**: Allow setting via environment variables
3. **Clear Documentation**: Clearly document that values are for demo/testing only
4. **Never Use in Production**: Include warnings that demo patterns should not be used in production

See `examples/dos_trap_demo.py` for a reference implementation.

### Verification

#### Check for Hardcoded Secrets

```bash

# Search for potential hardcoded secrets

grep -r "password\|secret\|key.*=" --include="*.py" thirstys_waterfall/

# Search for hardcoded bytes that might be keys

grep -r "b'[a-zA-Z0-9_]*'" --include="*.py" thirstys_waterfall/

# Use automated tools

pip install detect-secrets
detect-secrets scan --baseline .secrets.baseline
```

#### Audit Checklist

- [ ] No hardcoded secrets in source code
- [ ] All secrets loaded from environment or vault
- [ ] `.env` files in `.gitignore`
- [ ] Secret rotation procedures documented
- [ ] CI/CD uses encrypted secrets
- [ ] Different secrets for each environment
- [ ] Secrets are at least 256 bits (32 bytes)
- [ ] Regular rotation schedule established
- [ ] Access to secrets is logged and audited
- [ ] Secrets never logged or exposed in errors

## Incident Response

### If a Secret is Exposed

1. **Immediate Actions** (within 1 hour):
   - Revoke the exposed secret immediately
   - Generate and deploy a new secret
   - Review access logs for unauthorized usage
   - Document the incident

2. **Investigation** (within 24 hours):
   - Determine scope of exposure (who had access, how long exposed)
   - Check for evidence of compromise
   - Review related secrets that may need rotation
   - Update security monitoring

3. **Remediation** (within 48 hours):
   - Rotate all potentially affected secrets
   - Review and improve secret management practices
   - Update documentation and training
   - Conduct security review

4. **Post-Incident** (within 1 week):
   - Complete incident report
   - Share lessons learned with team
   - Implement preventive measures
   - Update security policies if needed

## Security Features

### DOS Trap Mode

The DOS (Denial of Service) Trap Mode provides comprehensive system compromise detection:

- Rootkit detection
- Kernel hook monitoring
- Memory anomaly detection
- Process injection detection
- Automatic secret wiping on compromise
- Hardware-backed security

### Hardware Root of Trust

Integration with hardware security modules:

- TPM (Trusted Platform Module)
- Secure Enclaves
- Hardware Security Modules (HSM)
- All using dynamically generated, hardware-derived secrets

### Kill Switch

Global kill switch for emergency shutdown:

- Coordinates all system components
- Wipes secrets from memory
- Disables network interfaces
- Performs secure data sanitization

## Compliance

This project implements security best practices aligned with:

- **OWASP Top 10**: Protection against common vulnerabilities
- **CWE-798**: No hard-coded credentials
- **CWE-321**: Use of hard-coded cryptographic key (mitigated)
- **NIST SP 800-132**: Password-based key derivation
- **NIST SP 800-57**: Cryptographic key management
- **PCI DSS**: Payment card industry security standards
- **GDPR**: Data protection and privacy
- **SOC 2**: Security, availability, and confidentiality

## Security Tools

Recommended tools for security verification:

- **detect-secrets**: Find secrets in code
- **bandit**: Python security linter
- **safety**: Check dependencies for vulnerabilities
- **trivy**: Container vulnerability scanner
- **git-secrets**: Prevent committing secrets
- **GitGuardian**: Automated secret detection
- **Snyk**: Dependency vulnerability scanning

## Regular Security Audits

Schedule regular security audits:

1. **Weekly**: Automated dependency scanning
2. **Monthly**: Secret rotation review
3. **Quarterly**: Full security audit
4. **Annually**: Penetration testing
5. **After incidents**: Security review and lessons learned

## Contact

For security concerns, contact:

- Security Team: security@thirstyswaterfall.example
- Project Maintainer: maintainer@thirstyswaterfall.example

---

**Last Updated**: 2026-02-03
**Version**: 1.0
