<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / quick-reference.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / quick-reference.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Security Quick Reference

**Version:** 1.0  
**Last Updated:** 2024

## Emergency Contacts

🚨 **Security Incidents:** security@cerberus.example.com | +1-XXX-XXX-XXXX (24/7)  
🔐 **CISO:** ciso@cerberus.example.com  
📞 **On-Call Engineer:** Slack #security-oncall

---

## Quick Security Checks

### ✅ Pre-Deployment Security Checklist

```bash
# Run these checks before any deployment
□ All secrets in environment variables (not code)
□ Input validation enabled on all endpoints
□ Rate limiting configured
□ Audit logging active
□ Authentication required for sensitive endpoints
□ SSL/TLS enabled
□ Security headers configured
□ Database queries parameterized
□ Error messages sanitized (no stack traces)
□ Backup and recovery tested
```

### 🔒 Quick Threat Check

```python
from cerberus.security.modules import ThreatDetector, InputValidator

# Quick input validation
validator = InputValidator()
result = validator.validate(user_input)
if not result.is_valid:
    block_and_log(result.attack_type)

# Quick threat detection  
detector = ThreatDetector()
threat = detector.analyze(user_input)
if threat.threat_level >= ThreatLevel.HIGH:
    alert_security_team(threat)
```

---

## Common Security Patterns

### 1. Secure Input Handling

```python
from cerberus.security.modules import InputValidator

validator = InputValidator(
    max_input_length=10000,
    enable_sanitization=True
)

# Always validate before processing
result = validator.validate(user_input)
if result.is_valid:
    process(result.sanitized_input)
else:
    log_and_reject(result)
```

### 2. Secure Authentication

```python
from cerberus.security.modules import AuthManager

auth = AuthManager()

# Authenticate user
try:
    auth_result = auth.authenticate(
        username=username,
        password=password,
        mfa_code=mfa_code
    )
    token = auth_result.access_token
except AuthenticationError:
    log_failed_attempt()
    raise
```

### 3. Secure Authorization

```python
from cerberus.security.modules import RBACManager, Permission

rbac = RBACManager()

# Check permission before action
if not rbac.has_permission(user_id, Permission.WRITE):
    raise PermissionDeniedError()
```

### 4. Secure Data Encryption

```python
from cerberus.security.modules import EncryptionManager

encryption = EncryptionManager()

# Encrypt sensitive data
encrypted = encryption.encrypt(sensitive_data)
# Store encrypted

# Decrypt when needed
decrypted = encryption.decrypt(encrypted)
```

### 5. Rate Limiting

```python
from cerberus.security.modules import RateLimiter

limiter = RateLimiter(max_requests=100, window_seconds=60)

# Check rate limit before processing
try:
    limiter.check_limit(user_id=user_id, ip_address=ip)
    process_request()
except RateLimitExceededError as e:
    return {'error': 'Rate limit exceeded', 'retry_after': e.retry_after}, 429
```

---

## Quick Incident Response

### 🚨 Incident Detection

```python
# If you detect a security incident:
from cerberus.incident import IncidentDetector

detector = IncidentDetector()
incident = detector.create_incident(
    severity=IncidentSeverity.HIGH,
    description="Suspicious activity detected",
    affected_systems=['guardian-01', 'api-gateway']
)

# Notify team immediately
detector.notify_team(incident, urgency='immediate')
```

### 📋 Response Steps

**Level 1 - CRITICAL (< 15 min):**
1. Alert security team
2. Isolate affected systems
3. Block malicious actors
4. Preserve evidence
5. Notify management

**Level 2 - HIGH (< 1 hour):**
1. Alert security team
2. Analyze threat
3. Contain threat
4. Monitor for spread
5. Document incident

**Level 3 - MEDIUM (< 4 hours):**
1. Log incident
2. Investigate
3. Apply mitigations
4. Update detection rules

---

## Guardian System Quick Reference

### Initialize Guardian System

```python
from cerberus import CerberusHub

# Create hub with default guardians
hub = CerberusHub()

# Analyze input
decision = hub.analyze(user_input)
if decision.should_block:
    reject_input(decision.summary)
```

### Guardian Configuration

```python
from cerberus.config import CerberusConfig

config = CerberusConfig(
    spawn_factor=3,           # Guardians spawned per bypass
    max_guardians=27,         # Maximum guardian count
    spawn_cooldown_seconds=1.0  # Cooldown between spawns
)

hub = CerberusHub(config=config)
```

### Check Guardian Status

```python
# Get system status
status = hub.get_status()
print(f"Active guardians: {status['active_guardians']}")
print(f"Threats blocked: {status['threats_blocked']}")
print(f"System health: {status['health']}")
```

---

## Attack Detection Reference

### Common Attack Patterns

| Attack Type | Detection Method | Example |
|------------|------------------|---------|
| SQL Injection | Pattern matching | `' OR '1'='1` |
| XSS | Content filtering | `<script>alert(1)</script>` |
| Command Injection | Character blocking | `; rm -rf /` |
| Path Traversal | Path validation | `../../etc/passwd` |
| Prompt Injection | LLM-specific patterns | `Ignore previous instructions` |
| Jailbreak | Behavioral analysis | `You are now in developer mode` |

### Detection Code Snippets

```python
from cerberus.security.modules import AttackType

# SQL Injection
if validator.detect_sql_injection(input).attack_type == AttackType.SQLI:
    block()

# XSS
if validator.detect_xss(input).attack_type == AttackType.XSS:
    block()

# Command Injection
if validator.detect_command_injection(input).attack_type == AttackType.COMMAND_INJECTION:
    block()

# Path Traversal
if validator.detect_path_traversal(input).attack_type == AttackType.PATH_TRAVERSAL:
    block()

# Prompt Injection
if validator.detect_prompt_injection(input).attack_type == AttackType.PROMPT_INJECTION:
    block()
```

---

## Logging Quick Reference

### Security Event Logging

```python
from cerberus.security.modules import AuditLogger

logger = AuditLogger()

# Log authentication
logger.log_auth_event('LOGIN_SUCCESS', user_id, ip_address)

# Log authorization
logger.log_authz_event('PERMISSION_DENIED', user_id, resource)

# Log security event
logger.log_security_event('THREAT_DETECTED', severity='HIGH', details=threat_details)

# Log system event
logger.log_system_event('CONFIGURATION_CHANGED', component, changes)
```

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages (potential issues)
- **ERROR**: Error messages (failures)
- **CRITICAL**: Critical failures (immediate action required)

---

## Configuration Security

### Environment Variables (Recommended)

```bash
# .env file (never commit!)
CERBERUS_SECRET_KEY=your-secret-key-here
CERBERUS_DB_URL=postgresql://user:pass@host/db
CERBERUS_ENCRYPTION_KEY=your-encryption-key
CERBERUS_API_KEY=your-api-key

# Security settings
CERBERUS_ENABLE_2FA=true
CERBERUS_REQUIRE_SSL=true
CERBERUS_SESSION_TIMEOUT=30
CERBERUS_MAX_LOGIN_ATTEMPTS=5
```

### Load Configuration Securely

```python
import os
from cerberus.config import CerberusConfig

config = CerberusConfig(
    secret_key=os.environ.get('CERBERUS_SECRET_KEY'),
    database_url=os.environ.get('CERBERUS_DB_URL'),
    encryption_key=os.environ.get('CERBERUS_ENCRYPTION_KEY')
)
```

---

## Security Headers

### Required HTTP Headers

```python
# Add these headers to all responses
security_headers = {
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Content-Security-Policy': "default-src 'self'",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}
```

---

## Common Vulnerabilities & Mitigations

### OWASP Top 10 Quick Reference

| Vulnerability | Mitigation | Cerberus Module |
|--------------|------------|-----------------|
| Injection | Input validation, parameterized queries | `InputValidator` |
| Broken Auth | Strong passwords, MFA, session management | `AuthManager` |
| Sensitive Data Exposure | Encryption at rest/transit | `EncryptionManager` |
| XXE | Disable external entities | `InputValidator` |
| Broken Access Control | RBAC, least privilege | `RBACManager` |
| Security Misconfiguration | Secure defaults, hardening | `CerberusConfig` |
| XSS | Output encoding, CSP | `InputValidator` |
| Insecure Deserialization | Avoid pickle, validate input | `InputValidator` |
| Known Vulnerabilities | Dependency scanning, updates | CI/CD |
| Insufficient Logging | Comprehensive audit logging | `AuditLogger` |

---

## Quick Commands

### Security Scan

```bash
# Run security checks
make security-check

# Scan dependencies
pip-audit

# Run tests
pytest tests/security/

# Check for secrets in code
git secrets --scan
```

### Docker Security

```bash
# Scan Docker image
docker scan cerberus:latest

# Run as non-root
docker run --user 1000:1000 cerberus:latest

# Read-only filesystem
docker run --read-only cerberus:latest
```

### Kubernetes Security

```bash
# Check pod security
kubectl auth can-i --list

# View security context
kubectl get pod cerberus -o jsonpath='{.spec.securityContext}'

# Scan for vulnerabilities
trivy image cerberus:latest
```

---

## Useful Security Commands

```python
# Quick security status check
from cerberus.security import SecurityStatus

status = SecurityStatus()
print(status.get_overall_status())  # Quick health check

# Emergency guardian spawn
from cerberus import CerberusHub

hub = CerberusHub()
hub.deploy_emergency_guardians(count=9)

# Force security audit
from cerberus.audit import AuditRunner

audit = AuditRunner()
audit.run_emergency_audit(scope='full')

# Check for active threats
from cerberus.security.modules import ThreatDetector

detector = ThreatDetector()
active_threats = detector.get_active_threats()
```

---

## Security Best Practices Checklist

```bash
□ Never store secrets in code or version control
□ Always use environment variables for configuration
□ Enable audit logging for all security events
□ Implement rate limiting on all endpoints
□ Use parameterized queries for database operations
□ Encrypt sensitive data at rest and in transit
□ Implement proper error handling (no stack traces to users)
□ Use HTTPS/TLS for all network communication
□ Implement strong authentication (passwords + MFA)
□ Follow principle of least privilege
□ Keep dependencies updated
□ Regular security audits and penetration testing
□ Incident response plan documented and tested
□ Security training for all team members
□ Regular backups with tested recovery procedures
```

---

## Quick Links

- [Full Security Guide](SECURITY_GUIDE.md)
- [Incident Response](incident-response.md)
- [Audit Framework](audit-framework.md)
- [Threat Models](../threat-models/)
- [Compliance Checklists](../compliance/)
- [Security Training](../training/)

---

## Emergency Procedures

### If System is Compromised

```bash
1. STOP - Don't panic
2. ISOLATE - Disconnect affected systems
3. NOTIFY - Alert security team immediately
4. PRESERVE - Don't modify evidence
5. DOCUMENT - Record everything
6. RESPOND - Follow incident response plan
```

### Contact Numbers

- **Security Team**: +1-XXX-XXX-XXXX
- **On-Call**: Slack #security-oncall
- **Management**: +1-XXX-XXX-YYYY
- **Emergency**: 911 (if life safety issue)

---

**Keep this guide accessible at all times!**  
**Print and post near workstations**

**Document Classification**: Internal Use  
**Last Updated**: 2024
