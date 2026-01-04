# Project-AI Security Framework

## 🎯 Overview

This security framework implements a comprehensive, multi-phase secure AI deployment lifecycle for Project-AI. It provides defense-in-depth protection against modern attack vectors including injection attacks, data poisoning, privilege escalation, and adversarial AI attacks.

## ✨ Key Features

### 🛡️ Defense Layers

- **Environment Hardening**: Virtualenv validation, sys.path hardening, ASLR/SSP verification
- **Data Validation**: Secure XML/CSV/JSON parsing with XXE/injection prevention
- **AWS Integration**: PoLP IAM roles, Secrets Manager, S3 encryption, CloudWatch/SNS
- **Agent Security**: State encapsulation, numerical protection, plugin isolation
- **Database Security**: Parameterized queries, transaction management, audit logging
- **Web Security**: SOAP/HTTP security, capability tokens, rate limiting, HMAC signing
- **Monitoring**: Real-time threat detection, anomaly detection, incident response

### 🧪 Test Coverage

- **158 comprehensive tests** (157 passing, 1 skipped)
- Multi-vector attack scenarios (XSS, SQL injection, XXE, path traversal, etc.)
- Stress tests up to 10,000 concurrent operations
- Fuzzing framework with 4 strategies
- Concurrent access tests with up to 20 threads

### 📚 Documentation

- **Complete API Reference** - SECURITY_FRAMEWORK.md (22KB)
- **Deployment Guide** - DEPLOYMENT_GUIDE.md (21KB)
- **Quick Reference** - SECURITY_QUICKREF.md (9KB)
- **Working Example** - examples/security_integration.py (14KB)

### ✅ Standards Compliance

- ✅ OWASP Top 10 2021 (all 10 categories)
- ✅ NIST Cybersecurity Framework (6 functions)
- ✅ CERT Secure Coding Standards
- ✅ AWS Well-Architected Security Pillar
- ✅ CIS Benchmarks (IAM, S3, CloudWatch)

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "from app.security import EnvironmentHardening; print('✓ Security framework installed')"
```

### Basic Usage

```python
from app.security import (
    EnvironmentHardening,
    SecureDataParser,
    SecurityMonitor,
    SecureDatabaseManager,
)

# 1. Harden environment
hardening = EnvironmentHardening()
is_valid, issues = hardening.validate_environment()

# 2. Initialize monitoring
monitor = SecurityMonitor(
    region="us-east-1",
    sns_topic_arn="arn:aws:sns:us-east-1:123:security-alerts"
)

# 3. Parse data securely
parser = SecureDataParser()
result = parser.parse_json('{"data": "value"}')

if result.validated:
    print(f"Data: {result.data}")
else:
    print(f"Validation failed: {result.issues}")

# 4. Use secure database
db = SecureDatabaseManager("data/secure.db")
user_id = db.insert_user("alice", "hashed_password")
```

### Complete Integration Example

See [examples/security_integration.py](../examples/security_integration.py) for a fully working example that demonstrates:

- Environment hardening and validation
- Security monitoring with CloudWatch/SNS
- Secure data parsing and poisoning defense
- Database operations with audit logging
- Agent security and isolation
- Web security controls

Run it:

```bash
PYTHONPATH=src python examples/security_integration.py
```

## 📦 Components

### 1. Environment Hardening (`environment_hardening.py`)

Validates and hardens the runtime environment:

```python
hardening = EnvironmentHardening()

# Comprehensive validation
is_valid, issues = hardening.validate_environment()

# Apply fixes
hardening.harden_sys_path()
hardening.secure_directory_structure()

# Get detailed report
report = hardening.get_validation_report()
```

**Features**:

- Virtualenv detection
- sys.path security validation
- ASLR/SSP verification (Linux/Windows/macOS)
- Directory permission enforcement (0700)
- Data structure initialization

### 2. Data Validation (`data_validation.py`)

Secure parsing with attack detection:

```python
parser = SecureDataParser()
defense = DataPoisoningDefense()

# XML with XXE prevention
xml_result = parser.parse_xml(xml_data)

# CSV with injection detection
csv_result = parser.parse_csv(csv_data, schema={"name": "string", "age": "int"})

# Check for attacks
is_poisoned, patterns = defense.check_for_poison(user_input)
```

**Protections**:

- XXE (XML External Entity) prevention
- DTD blocking
- CSV formula injection detection
- SQL injection pattern detection
- XSS attack detection (10+ variants)
- Path traversal prevention
- Template injection blocking
- CRLF injection prevention

### 3. AWS Integration (`aws_integration.py`)

Secure cloud resource access:

```python
aws = AWSSecurityManager(region="us-east-1")

# Secrets Manager
secret = aws.get_secret("app-secrets")
aws.put_secret("api-key", {"key": "value"})

# S3 with encryption
aws.upload_to_s3("bucket", "key", data, encryption="AES256")
data = aws.download_from_s3("bucket", "key")

# IAM auditing
audit = aws.audit_iam_permissions()
is_secure = aws.validate_polp(required_permissions)

# Temporary credentials
creds = aws.get_temporary_credentials("role-arn", "session-name")
```

**Features**:

- IAM role-based authentication (no static credentials)
- Secrets Manager integration
- S3 encryption (AES-256)
- Permission auditing (PoLP validation)
- MFA delete support
- Temporary credential generation (STS)

### 4. Agent Security (`agent_security.py`)

Protect AI agents from adversarial attacks:

```python
from app.security.agent_security import (
    AgentEncapsulation,
    NumericalProtection,
    PluginIsolation,
    RuntimeFuzzer,
)

# State encapsulation
agent = AgentEncapsulation("agent_id")
agent.set_permissions(read=True, write=True, execute=False)
agent.set_state("weights", model_weights, caller="trainer")

# Numerical protection
protection = NumericalProtection()
safe_data = protection.clip_array(untrusted_data, min_val=-1e6, max_val=1e6)
clean_data = protection.remove_outliers(sensor_data, threshold=3.0)

# Plugin isolation
isolation = PluginIsolation(timeout=30)
result = isolation.execute_isolated(untrusted_plugin, args=(data,))

# Fuzzing
fuzzer = RuntimeFuzzer()
test_cases = fuzzer.fuzz_input("boundary_values", base_input)
```

**Features**:

- Thread-safe state encapsulation
- Access control (read/write/execute)
- Audit logging for all state access
- Numerical bounds checking
- Outlier detection and removal
- Safe division (zero handling)
- Process-based plugin isolation
- Timeout protection
- Runtime fuzzing (4 strategies)

### 5. Database Security (`database_security.py`)

SQL injection prevention:

```python
db = SecureDatabaseManager("data/secure.db")

# Parameterized operations
user_id = db.insert_user("alice", "hashed_password", "alice@example.com")
user = db.get_user("alice")
db.update_user(user_id, email="newemail@example.com")

# Audit logging
db.log_action(
    user_id=123,
    action="delete_data",
    resource="dataset_456",
    details={"reason": "user request"},
    ip_address="192.168.1.100"
)

# Transaction management
with db.transaction() as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ...")
    cursor.execute("UPDATE ...")
    # Auto-commit on success, rollback on error
```

**Features**:

- Parameterized queries (SQL injection prevention)
- Query validation (dangerous pattern detection)
- Transaction management with rollback
- Comprehensive audit logging
- Schema with foreign keys and constraints
- Agent state storage
- Knowledge base storage

### 6. Security Monitoring (`monitoring.py`)

Real-time threat detection:

```python
monitor = SecurityMonitor(
    region="us-east-1",
    sns_topic_arn="arn:aws:sns:us-east-1:123:alerts",
    cloudwatch_namespace="ProjectAI/Security"
)

# Log events
monitor.log_security_event(
    event_type="authentication_failure",
    severity="high",
    source="login_api",
    description="Failed login attempt",
    metadata={"username": "attacker", "ip": "1.2.3.4"}
)

# Threat signatures
monitor.add_threat_signature("APT29", ["evil.com", "malware_hash"])
matches = monitor.check_threat_signatures(network_traffic)

# Anomaly detection
anomalies = monitor.detect_anomalies(time_window=3600, threshold=10)

# Statistics
stats = monitor.get_event_statistics(time_window=3600)
```

**Features**:

- AWS CloudWatch integration (metrics)
- AWS SNS integration (alerting)
- Structured event logging
- Threat signature database
- Anomaly detection (threshold-based)
- Event statistics and reporting
- Export audit logs (JSON/CSV)

### 7. Web Security (`web_service.py`)

HTTP/SOAP security:

```python
from app.security.web_service import (
    SOAPClient,
    SecureWebHandler,
    RateLimiter,
    InputValidator,
)

# SOAP client
client = SOAPClient("https://api.example.com/soap", username="user", password="pass")
response = client.call("GetData", {"id": "123"})

# Capability tokens
handler = SecureWebHandler()
token = handler.generate_capability_token(["read", "write"])

if handler.check_capability(token, "read"):
    # Allow read operation
    data = read_data()

# Rate limiting
limiter = RateLimiter(max_requests=100, window=60)

if limiter.check_rate_limit(client_ip):
    # Process request
    process_request()
else:
    # Return 429 Too Many Requests
    return {"error": "Rate limit exceeded"}, 429

# Input validation
validator = InputValidator()

if validator.validate_input(user_input, "application/json"):
    # Safe to process
    result = process_input(user_input)
```

**Features**:

- SOAP over HTTP client
- SOAP envelope validation
- WS-Security authentication
- Capability-based access control
- Secure HTTP headers
- HMAC request signing
- Rate limiting (token bucket)
- Input validation
- Filename sanitization

## 🧪 Testing

### Run All Tests

```bash
# All security tests (158 tests)
pytest tests/test_security*.py -v

# Specific phases
pytest tests/test_security_phase1.py -v  # Environment & data (27 tests)
pytest tests/test_security_phase2.py -v  # Components (34 tests)
pytest tests/test_security_stress.py -v  # Stress tests (97 tests)

# With coverage
pytest tests/test_security*.py --cov=app.security --cov-report=html

# Parallel execution
pytest tests/test_security*.py -n auto
```

### Test Categories

| Category              | Tests | Description                                 |
| --------------------- | ----- | ------------------------------------------- |
| Environment           | 8     | Virtualenv, sys.path, ASLR/SSP, permissions |
| Data Parsing          | 30+   | XML, CSV, JSON with attack detection        |
| Poisoning Defense     | 30+   | XSS, SQL injection, path traversal, etc.    |
| Concurrent Operations | 15+   | Thread-safe operations up to 20 threads     |
| Numerical             | 10+   | Bounds checking, outlier removal            |
| Fuzzing               | 20+   | Multi-strategy fuzzing                      |
| Rate Limiting         | 5+    | Burst traffic, distributed attacks          |
| Monitoring            | 10+   | Event logging, anomaly detection            |
| Database              | 5+    | SQL injection prevention, transactions      |
| Web Security          | 10+   | SOAP, capability tokens, validation         |

## 📈 Performance

| Operation                    | Performance |
| ---------------------------- | ----------- |
| Parse 5,000 CSV rows         | < 1 second  |
| Parse 50-level nested JSON   | < 100ms     |
| Handle 20 concurrent threads | Safe        |
| Monitor 1,000 events/second  | Handled     |
| Process 100 DB ops/second    | Maintained  |
| Detect 18 attack patterns    | < 10ms      |

## 🔒 Attack Vectors Blocked

### Injection Attacks

- ✅ SQL Injection (`' OR '1'='1`, `UNION SELECT`, `DROP TABLE`)
- ✅ XXE (XML External Entity)
- ✅ XSS (10+ variants including script, img, svg, iframe, event handlers)
- ✅ CSV Injection (formula attacks: `=cmd`, `+cmd`, `-cmd`, `@cmd`)
- ✅ Template Injection (`{{...}}`, `${jndi:...}`)
- ✅ CRLF Injection (`%0d%0a`)

### Traversal & Access

- ✅ Path Traversal (`../../`, `..\\`, URL-encoded)
- ✅ Privilege Escalation (capability-based access control)
- ✅ Rate Limiting Bypass (token bucket algorithm)

### Data Attacks

- ✅ Data Poisoning (signature-based detection)
- ✅ Numerical Overflow (bounds checking, clipping)
- ✅ Adversarial ML Inputs (outlier removal, validation)

## 📚 Documentation

### Core Documentation

- **[SECURITY_FRAMEWORK.md](SECURITY_FRAMEWORK.md)** - Complete API reference with examples
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Step-by-step deployment procedures
- **[SECURITY_QUICKREF.md](SECURITY_QUICKREF.md)** - Quick reference guide

### Examples

- **[security_integration.py](../examples/security_integration.py)** - Complete working integration

### Additional Resources

- **Tests** - See `tests/test_security*.py` for usage examples
- **Standards** - OWASP, NIST, CERT compliance documentation

## 🚀 Deployment

### Development

```bash
# Create virtualenv
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/test_security*.py -v

# Run example
PYTHONPATH=src python examples/security_integration.py
```

### Production (AWS)

```bash
# Configure IAM role (no static credentials)
aws iam create-role --role-name ProjectAI-Role --assume-role-policy-document file://trust-policy.json

# Set up Secrets Manager
aws secretsmanager create-secret --name project-ai-secrets --secret-string file://secrets.json

# Enable CloudWatch
aws cloudwatch put-dashboard --dashboard-name ProjectAI-Security --dashboard-body file://dashboard.json

# Set up SNS alerts
aws sns create-topic --name security-alerts
aws sns subscribe --topic-arn arn:aws:sns:us-east-1:123:security-alerts --protocol email --notification-endpoint security@example.com

# Launch EC2 instance with IAM role
aws ec2 run-instances --image-id ami-xxx --iam-instance-profile Name=ProjectAI-Role
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete instructions.

## 🛠️ Configuration

### Environment Variables

```bash
# Required
FERNET_KEY=<generate using: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">

# AWS (use IAM roles in production)
AWS_REGION=us-east-1

# Monitoring
SECURITY_SNS_TOPIC=arn:aws:sns:us-east-1:123:security-alerts
CLOUDWATCH_NAMESPACE=ProjectAI/Security

# Application
DATABASE_PATH=data/secure.db
MAX_UPLOAD_SIZE=104857600  # 100MB
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: Tests failing

```bash
# Install all dependencies
pip install -r requirements.txt

# Check Python version (requires 3.12+)
python --version

# Run with verbose output
pytest tests/test_security_phase1.py -vv
```

**Issue**: CloudWatch metrics not appearing

```bash
# Check IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123:role/ProjectAI \
  --action-names cloudwatch:PutMetricData
```

**Issue**: Permission denied errors

```bash
# Fix directory permissions (Unix/Linux)
chmod 700 data/
chmod 600 data/*.db
```

## 🤝 Contributing

1. Run tests: `pytest tests/test_security*.py -v`
2. Check code style: `ruff check src/app/security/`
3. Update documentation as needed
4. Add tests for new features

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- OWASP for security best practices
- NIST for Cybersecurity Framework
- CERT for secure coding standards
- AWS for cloud security guidance

---

**Version**: 1.0.0  
**Last Updated**: 2025-12-31  
**Test Coverage**: 158 tests (157 passing, 1 skipped)  
**Code Size**: ~75KB security framework + ~47KB tests + ~43KB documentation
