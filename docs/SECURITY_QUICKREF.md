# Security Framework Quick Reference

## 🎯 Quick Start

```python
from app.security import (
    EnvironmentHardening,
    SecureDataParser,
    SecurityMonitor,
    SecureDatabaseManager,
)

# 1. Harden environment
hardening = EnvironmentHardening()
hardening.validate_environment()

# 2. Initialize monitoring
monitor = SecurityMonitor()

# 3. Parse data securely
parser = SecureDataParser()
result = parser.parse_json('{"data": "value"}')

# 4. Use secure database
db = SecureDatabaseManager("data/secure.db")
```

## 📊 Test Coverage

| Category | Tests | Status |
|----------|-------|--------|
| Environment Hardening | 8 | ✅ |
| Data Parsing | 30+ | ✅ |
| Data Poisoning Defense | 30+ | ✅ |
| Concurrent Operations | 15+ | ✅ |
| Numerical Adversaries | 10+ | ✅ |
| Fuzzing | 20+ | ✅ |
| Rate Limiting | 5+ | ✅ |
| Monitoring | 10+ | ✅ |
| Database Stress | 5+ | ✅ |
| **Total** | **158** | **✅ 157 passing** |

## 🛡️ Attack Vectors Blocked

### XSS (10+ variants)
- `<script>alert(1)</script>`
- `<img src=x onerror=alert(1)>`
- `<svg/onload=alert(1)>`
- `<iframe src=javascript:alert(1)>`
- Event handlers: `onload`, `onerror`, `onfocus`, `onstart`

### SQL Injection
- `' OR '1'='1`
- `UNION SELECT`
- `DROP TABLE`
- SQL comments: `--`, `/**/`

### XXE (XML External Entity)
- `<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>`
- DTD declarations
- External entity references

### Path Traversal
- `../../etc/passwd`
- `..\\..\\..\\windows\\win.ini`
- URL encoded: `%2e%2e%2f`

### Other
- CSV injection: `=cmd`, `+cmd`, `-cmd`, `@cmd`
- Template injection: `{{7*7}}`, `${jndi:...}`
- CRLF injection: `%0d%0a`

## 🔧 Component Reference

### Environment Hardening
```python
from app.security import EnvironmentHardening

hardening = EnvironmentHardening()
is_valid, issues = hardening.validate_environment()

if not is_valid:
    hardening.harden_sys_path()
    hardening.secure_directory_structure()
```

### Data Parsing
```python
from app.security import SecureDataParser

parser = SecureDataParser()

# XML with XXE protection
result = parser.parse_xml(xml_data)

# CSV with injection detection
result = parser.parse_csv(csv_data, schema={"name": "string", "age": "int"})

# JSON with schema validation
result = parser.parse_json(json_data, schema={...})
```

### Data Poisoning Defense
```python
from app.security import DataPoisoningDefense

defense = DataPoisoningDefense()

# Check for malicious patterns
is_poisoned, patterns = defense.check_for_poison(user_input)

# Sanitize input
clean = defense.sanitize_input(dirty_input)

# Blacklist malicious content
defense.add_poison_signature(attack_data)
```

### AWS Integration
```python
from app.security import AWSSecurityManager

aws = AWSSecurityManager(region="us-east-1")

# Get secret
secret = aws.get_secret("app-secrets")

# Upload to S3 with encryption
aws.upload_to_s3("bucket", "key", data, encryption="AES256")

# Audit permissions
audit = aws.audit_iam_permissions()

# Validate PoLP
aws.validate_polp(["s3:GetObject", "s3:PutObject"])
```

### Agent Security
```python
from app.security import AgentEncapsulation
from app.security.agent_security import NumericalProtection

# Encapsulate agent state
agent = AgentEncapsulation("agent_id")
agent.set_permissions(read=True, write=True, execute=False)
agent.set_state("key", value, caller="system")

# Protect numerical operations
protection = NumericalProtection()
safe_array = protection.clip_array(untrusted_data)
clean_data = protection.remove_outliers(sensor_data)
```

### Database Security
```python
from app.security import SecureDatabaseManager

db = SecureDatabaseManager("data/secure.db")

# Parameterized insert (SQL injection safe)
user_id = db.insert_user("alice", "hashed_password")

# Parameterized select
user = db.get_user("alice")

# Audit logging
db.log_action(user_id=123, action="login", ip_address="192.168.1.1")
```

### Security Monitoring
```python
from app.security import SecurityMonitor

monitor = SecurityMonitor(
    region="us-east-1",
    sns_topic_arn="arn:aws:sns:us-east-1:123:security-alerts",
    cloudwatch_namespace="ProjectAI/Security"
)

# Log event
monitor.log_security_event(
    event_type="authentication_failure",
    severity="high",
    source="login_api",
    description="Failed login attempt"
)

# Add threat signature
monitor.add_threat_signature("APT29", ["evil.com", "malware_hash"])

# Detect anomalies
anomalies = monitor.detect_anomalies(time_window=3600, threshold=10)
```

### Web Security
```python
from app.security.web_service import (
    SecureWebHandler,
    RateLimiter,
    InputValidator,
    SOAPClient,
)

# Capability-based access
handler = SecureWebHandler()
token = handler.generate_capability_token(["read", "write"])
if handler.check_capability(token, "read"):
    # Allow operation
    pass

# Rate limiting
limiter = RateLimiter(max_requests=100, window=60)
if limiter.check_rate_limit(client_ip):
    # Process request
    pass

# Input validation
validator = InputValidator()
if validator.validate_input(user_input, "application/json"):
    # Safe to process
    pass

# SOAP client
client = SOAPClient("https://api.example.com/soap")
response = client.call("GetData", {"id": "123"})
```

## 📚 Documentation

- **[SECURITY_FRAMEWORK.md](SECURITY_FRAMEWORK.md)** - Complete API reference (22KB)
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Step-by-step deployment (21KB)
- **[examples/security_integration.py](../examples/security_integration.py)** - Working example (14KB)

## 🧪 Running Tests

```bash
# All security tests (158 tests)
pytest tests/test_security*.py -v

# With coverage
pytest tests/test_security*.py --cov=app.security --cov-report=html

# Specific category
pytest tests/test_security_phase1.py -v  # Environment & data
pytest tests/test_security_phase2.py -v  # AWS, agents, DB, monitoring
pytest tests/test_security_stress.py -v  # Multi-vector stress tests

# Parallel execution
pytest tests/test_security*.py -n auto
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Run full test suite: `pytest tests/test_security*.py`
- [ ] Validate environment: `EnvironmentHardening().validate_environment()`
- [ ] Configure AWS IAM roles (no static credentials)
- [ ] Set up Secrets Manager for sensitive data
- [ ] Configure CloudWatch dashboards
- [ ] Set up SNS topic for alerts

### Post-Deployment
- [ ] Verify CloudWatch metrics
- [ ] Test SNS alerting
- [ ] Validate HTTPS/TLS
- [ ] Enable S3 versioning and MFA delete
- [ ] Review audit logs

### Ongoing
- [ ] Review logs weekly
- [ ] Monitor dashboards daily
- [ ] Update threat signatures monthly
- [ ] Rotate secrets quarterly
- [ ] Run penetration tests annually

## 🔒 Standards Compliance

### OWASP Top 10 2021
✅ A01: Broken Access Control  
✅ A02: Cryptographic Failures  
✅ A03: Injection  
✅ A04: Insecure Design  
✅ A05: Security Misconfiguration  
✅ A06: Vulnerable Components  
✅ A07: Authentication Failures  
✅ A08: Software/Data Integrity  
✅ A09: Logging Failures  
✅ A10: SSRF  

### NIST Cybersecurity Framework
✅ Identify - Asset Management  
✅ Protect - Access Control, Data Security  
✅ Detect - Anomaly Detection, Monitoring  
✅ Respond - Incident Response, Alerting  
✅ Recover - Backups, Versioning  

### Other Standards
✅ CERT Secure Coding (Python)  
✅ AWS Well-Architected Security Pillar  
✅ CIS Benchmarks (IAM, S3, CloudWatch)  

## 📈 Performance

| Operation | Performance |
|-----------|-------------|
| Parse 5,000 CSV rows | < 1 second |
| Parse 50-level nested JSON | < 100ms |
| 20 concurrent threads | Safe |
| 1,000 events/second | Monitored |
| 100 database ops/second | Handled |

## 🐛 Troubleshooting

### Issue: CloudWatch metrics not appearing
```bash
# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123:role/ProjectAI \
  --action-names cloudwatch:PutMetricData
```

### Issue: Tests failing
```bash
# Ensure dependencies installed
pip install -r requirements.txt

# Check Python version (requires 3.11+)
python --version

# Run with verbose output
pytest tests/test_security_phase1.py -v --tb=short
```

### Issue: Permission errors
```bash
# On Unix/Linux, ensure proper permissions
chmod 700 data/
chmod 600 data/*.db
```

## 💡 Best Practices

1. **Never use static AWS credentials** - Use IAM roles
2. **Always validate input** - Never trust user data
3. **Log security events** - Enable CloudWatch and SNS
4. **Monitor anomalies** - Set appropriate thresholds
5. **Rotate secrets regularly** - Quarterly minimum
6. **Test security controls** - Run full test suite before deployment
7. **Review audit logs** - Weekly minimum
8. **Keep dependencies updated** - Monthly review
9. **Use parameterized queries** - Prevent SQL injection
10. **Enable MFA on critical resources** - S3 MFA delete

## 📞 Support

For issues or questions:
- Review documentation in `docs/`
- Check test examples in `tests/`
- See working integration in `examples/security_integration.py`

---

**Version**: 1.0  
**Last Updated**: 2025-12-31  
**Test Coverage**: 158 tests (157 passing, 1 skipped)
