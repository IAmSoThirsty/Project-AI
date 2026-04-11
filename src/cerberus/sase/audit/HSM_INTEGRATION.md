# HSM Integration Guide - Evidence Vault

## Overview

The Evidence Vault integrates with Hardware Security Modules (HSM) to provide cryptographic signing of Merkle root hashes with hardware-protected keys. This ensures audit trail integrity even if software systems are compromised.

## Supported HSM Types

### 1. Software HSM (Development/Testing)

**Use Case**: Development, testing, CI/CD environments

**Configuration**:
```python
from src.cerberus.sase.audit.evidence_vault import EvidenceVault

vault = EvidenceVault(
    hsm_type="software",
    hsm_config={
        "key": b"your_secret_key_32_bytes_long!!"  # Optional
    }
)
```

**Environment Variables**:
```bash
SASE_HSM_ENABLED=true
SASE_HSM_TYPE=software
```

**Security Notes**:
- ⚠️ **NOT FOR PRODUCTION USE**
- Uses HMAC-SHA256 with in-memory key
- No hardware protection
- Suitable for testing and development only

---

### 2. YubiHSM 2

**Use Case**: Production deployments requiring FIPS 140-2 Level 2 compliance

**Hardware Requirements**:
- YubiHSM 2 device (USB)
- YubiHSM Connector service running

**Installation**:
```bash
# Install YubiHSM Python library
pip install python-yubihsm

# Install YubiHSM Connector (download from Yubico)
# https://developers.yubico.com/YubiHSM2/Releases/
```

**Configuration**:
```python
vault = EvidenceVault(
    hsm_type="yubihsm",
    hsm_config={
        "connector_url": "http://localhost:12345",
        "auth_key_id": 1,
        "password": "your_auth_password",
        "signing_key_id": None,  # Auto-create if None
    }
)
```

**Environment Variables**:
```bash
SASE_HSM_ENABLED=true
SASE_HSM_TYPE=yubihsm
YUBIHSM_CONNECTOR_URL=http://localhost:12345
YUBIHSM_AUTH_KEY_ID=1
YUBIHSM_PASSWORD=your_password
```

**Setup Steps**:

1. **Install YubiHSM Connector**:
   ```bash
   # Download from Yubico and install
   # Start connector service
   yubihsm-connector
   ```

2. **Initialize YubiHSM** (first time):
   ```bash
   yubihsm-shell
   > connect
   > session open 1 password
   > put asymmetric 0 "SASE Signing Key" 1 sign-hmac hmac-sha256
   ```

3. **Run Application**:
   ```python
   vault = EvidenceVault(hsm_type="yubihsm", hsm_config={
       "password": "your_password"
   })
   ```

**Security Features**:
- FIPS 140-2 Level 2 certified
- Hardware-protected key storage
- Keys never leave the device
- Audit logging of all operations

---

### 3. AWS CloudHSM

**Use Case**: Cloud deployments on AWS requiring FIPS 140-2 Level 3 compliance

**Requirements**:
- AWS CloudHSM cluster provisioned
- CloudHSM client installed on application server
- Network connectivity to CloudHSM cluster

**Installation**:
```bash
# Install AWS SDK
pip install boto3

# Install CloudHSM client (on EC2 instance)
sudo yum install -y aws-cloudhsm-client
```

**Configuration**:
```python
vault = EvidenceVault(
    hsm_type="aws_cloudhsm",
    hsm_config={
        "cluster_id": "cluster-abcd1234",
        "user": "crypto_user",
        "password": "your_crypto_user_password",
        "key_handle": None,  # Auto-create if None
    }
)
```

**Environment Variables**:
```bash
SASE_HSM_ENABLED=true
SASE_HSM_TYPE=aws_cloudhsm
AWS_CLOUDHSM_CLUSTER_ID=cluster-abcd1234
AWS_CLOUDHSM_USER=crypto_user
AWS_CLOUDHSM_PASSWORD=your_password
```

**Setup Steps**:

1. **Provision CloudHSM Cluster** (AWS Console or CLI):
   ```bash
   aws cloudhsmv2 create-cluster \
       --hsm-type hsm1.medium \
       --subnet-ids subnet-12345678
   ```

2. **Initialize Cluster**:
   ```bash
   aws cloudhsmv2 initialize-cluster \
       --cluster-id cluster-abcd1234 \
       --signed-cert file://cluster.crt \
       --trust-anchor file://ca.crt
   ```

3. **Create Crypto User**:
   ```bash
   cloudhsm_mgmt_util
   > loginHSM CO admin password
   > createUser CU crypto_user password
   ```

4. **Run Application**:
   ```python
   vault = EvidenceVault(hsm_type="aws_cloudhsm", hsm_config={
       "cluster_id": "cluster-abcd1234",
       "user": "crypto_user",
       "password": "your_password"
   })
   ```

**Security Features**:
- FIPS 140-2 Level 3 certified
- Dedicated hardware HSM instances
- Full key lifecycle management
- CloudWatch integration for monitoring

---

## Usage Examples

### Basic Usage

```python
from src.cerberus.sase.audit.evidence_vault import EvidenceVault
import hashlib

# Initialize vault with HSM
vault = EvidenceVault(
    hsm_type="yubihsm",  # or "software", "aws_cloudhsm"
    hsm_config={
        "password": "your_password"
    }
)

# Generate sample event hashes
event_hashes = [
    hashlib.sha256(f"event_{i}".encode()).hexdigest()
    for i in range(10)
]

# Aggregate daily events and sign with HSM
date = "2026-04-11"
root_hash = vault.aggregate_daily_events(date, event_hashes)
print(f"Signed Merkle root: {root_hash}")

# Generate proof for specific event
proof = vault.generate_event_proof(event_hashes[0], date)
print(f"Cryptographic proof: {proof}")

# Verify proof
is_valid = vault.verify_proof(proof)
print(f"Proof valid: {is_valid}")
```

### Get HSM Information

```python
# Get HSM status and configuration
hsm_info = vault.get_hsm_info()
print(f"HSM Type: {hsm_info['hsm_type']}")
print(f"Initialized: {hsm_info['initialized']}")

if hsm_info['hsm_type'] == 'yubihsm':
    print(f"Signing Key ID: {hsm_info['signing_key_id']}")
```

### Error Handling

```python
try:
    vault = EvidenceVault(
        hsm_type="yubihsm",
        hsm_config={"password": "test"}
    )
except Exception as e:
    print(f"HSM initialization failed: {e}")
    # Vault automatically falls back to software HSM
    print(f"Current HSM type: {vault.hsm_signer.hsm_type}")
```

---

## Environment Configuration

### Development Environment

```bash
# .env.development
SASE_HSM_ENABLED=true
SASE_HSM_TYPE=software
```

### Production with YubiHSM

```bash
# .env.production
SASE_HSM_ENABLED=true
SASE_HSM_TYPE=yubihsm
YUBIHSM_CONNECTOR_URL=http://localhost:12345
YUBIHSM_AUTH_KEY_ID=1
YUBIHSM_PASSWORD=${YUBIHSM_PASSWORD}  # From secrets manager
```

### Production with AWS CloudHSM

```bash
# .env.production
SASE_HSM_ENABLED=true
SASE_HSM_TYPE=aws_cloudhsm
AWS_CLOUDHSM_CLUSTER_ID=cluster-abcd1234
AWS_CLOUDHSM_USER=crypto_user
AWS_CLOUDHSM_PASSWORD=${CLOUDHSM_PASSWORD}  # From AWS Secrets Manager
```

---

## Testing

### Run HSM Tests

```bash
# Run all HSM tests
pytest tests/test_evidence_vault_hsm.py -v

# Run specific test class
pytest tests/test_evidence_vault_hsm.py::TestSoftwareHSM -v

# Run with coverage
pytest tests/test_evidence_vault_hsm.py --cov=src.cerberus.sase.audit
```

### Mock HSM in CI/CD

The test suite uses mocks for YubiHSM and AWS CloudHSM to enable testing without hardware:

```python
# tests/test_evidence_vault_hsm.py
@patch("src.cerberus.sase.audit.evidence_vault.yubihsm")
def test_yubihsm_sign(mock_yubihsm):
    # Mock YubiHSM behavior
    mock_session = MagicMock()
    mock_session.sign_hmac.return_value = b"\x01\x02\x03\x04"
    # ... test continues
```

---

## Troubleshooting

### YubiHSM Issues

**Problem**: "Cannot connect to YubiHSM connector"

**Solution**:
1. Verify connector is running: `ps aux | grep yubihsm-connector`
2. Check connector URL: `curl http://localhost:12345/connector/status`
3. Restart connector: `yubihsm-connector &`

**Problem**: "Authentication failed"

**Solution**:
1. Verify auth key ID and password
2. Check YubiHSM audit logs
3. Reset authentication if needed (requires admin)

### AWS CloudHSM Issues

**Problem**: "Cluster not reachable"

**Solution**:
1. Verify security group allows CloudHSM ports (2223-2225)
2. Check VPC subnet configuration
3. Verify CloudHSM client is installed and configured

**Problem**: "User authentication failed"

**Solution**:
1. Verify user exists: `listUsers` in cloudhsm_mgmt_util
2. Reset password if needed: `changePswd CU username oldPassword newPassword`

### Fallback Behavior

The HSM implementation automatically falls back to software signing if hardware HSM initialization fails:

```python
# Automatic fallback on error
vault = EvidenceVault(hsm_type="yubihsm", hsm_config={})
# If YubiHSM fails, hsm_type becomes "software"
assert vault.hsm_signer.hsm_type == "software"
```

---

## Security Considerations

### Key Management

1. **Key Generation**:
   - Keys are generated inside the HSM
   - Keys never leave the HSM in plaintext
   - Use strong entropy sources

2. **Key Rotation**:
   - Plan for periodic key rotation
   - Keep old keys for signature verification
   - Update configuration after rotation

3. **Key Backup**:
   - YubiHSM: Use key wrapping for backup
   - AWS CloudHSM: Automatic backup to S3
   - Test restore procedures regularly

### Access Control

1. **Authentication**:
   - Use strong passwords/passphrases
   - Store credentials in secrets manager
   - Rotate credentials regularly

2. **Authorization**:
   - Limit HSM access to SASE application only
   - Use least-privilege principle
   - Audit all HSM operations

### Audit Logging

All HSM operations are logged:

```python
# HSM operations generate audit logs
logger.info("HSM: Initializing YubiHSM connection")
logger.info("YubiHSM initialized with key ID 42")
logger.warning("HSM signing failed: [error]")
```

---

## Performance Characteristics

### Signing Performance

| HSM Type | Operations/sec | Latency (ms) | Notes |
|----------|---------------|--------------|-------|
| Software | ~10,000 | <1 | Development only |
| YubiHSM 2 | ~200 | 5-10 | USB 2.0 latency |
| AWS CloudHSM | ~2,000 | 2-5 | Network latency |

### Optimization Tips

1. **Batch Operations**: Aggregate events before signing
2. **Connection Pooling**: Reuse HSM sessions
3. **Async Operations**: Use async signing for high throughput

---

## Migration Guide

### From Software to Hardware HSM

1. **Generate keys in new HSM**
2. **Configure application** with HSM settings
3. **Test signing** with sample data
4. **Deploy** to production
5. **Verify** audit trail continuity

### Between HSM Types

```python
# Old configuration
vault_old = EvidenceVault(hsm_type="yubihsm", ...)

# New configuration
vault_new = EvidenceVault(hsm_type="aws_cloudhsm", ...)

# Transition period: verify with both
signature_old = vault_old.hsm_signer.sign(data)
signature_new = vault_new.hsm_signer.sign(data)
```

---

## References

- [YubiHSM 2 Documentation](https://developers.yubico.com/YubiHSM2/)
- [AWS CloudHSM Documentation](https://docs.aws.amazon.com/cloudhsm/)
- [FIPS 140-2 Standards](https://csrc.nist.gov/publications/detail/fips/140/2/final)
- [NIST Guidelines on Key Management](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)

---

## Support

For HSM integration issues:

1. Check logs: `logs/sase_evidence_vault.log`
2. Review HSM status: `vault.get_hsm_info()`
3. Test with software HSM first
4. Contact support with HSM type and error details
