# HSM Key Management Integration

## Overview

The Key Management module provides HSM-backed cryptographic key management with automatic rotation, signing operations, and emergency revocation capabilities.

## Features

### 1. HSM-Backed Key Storage
- Hardware Security Module integration via PKCS#11
- Keys stored in tamper-resistant hardware
- Private keys never leave HSM boundary
- Configurable HSM slot selection

### 2. Cryptographic Operations
- **Key Generation**: Secure random key generation in HSM
- **Signing**: Hardware-accelerated cryptographic signing
- **Revocation**: Emergency key revocation protocol
- **Rotation**: Automatic 90-day key rotation

### 3. Key Types
- `ROOT_SIGNING`: Root-level signing authority
- `EVENT_SIGNING`: Event attestation signatures
- `MODEL_SIGNING`: Model integrity signatures
- `MERKLE_ANCHORING`: Merkle tree anchoring keys

## Usage

### Basic Setup

```python
from src.cerberus.sase.governance.key_management import (
    KeyManagementCeremony,
    KeyType,
    HSMInterface
)

# Initialize with HSM hardware
ceremony = KeyManagementCeremony(hsm_available=True)

# Or for development/testing
ceremony = KeyManagementCeremony(hsm_available=False)
```

### Signing Data

```python
# Sign data with specific key type
data = "transaction data to sign"
signature = ceremony.sign_data(KeyType.ROOT_SIGNING, data)

print(f"Signature: {signature}")
```

### Key Revocation

```python
# Emergency key revocation (immediately rotates to new key)
ceremony.revoke_compromised_key(KeyType.EVENT_SIGNING)

# Verify old key is revoked
old_key_id = "..."  # previous key ID
is_revoked = ceremony.hsm.is_revoked(old_key_id)
```

### Manual Key Rotation

```python
# Manually rotate a key
new_key = ceremony.rotate_key(KeyType.MODEL_SIGNING)

print(f"New key ID: {new_key.key_id}")
print(f"Expires at: {new_key.days_until_expiry()} days")
```

### Automatic Rotation

```python
# Check and perform automatic rotations (call periodically)
ceremony.check_rotation_needed()
```

### Query Key Status

```python
# Get active key information
key = ceremony.get_active_key(KeyType.MERKLE_ANCHORING)

print(f"Key ID: {key.key_id[:16]}...")
print(f"Created: {key.created_at}")
print(f"Expires in: {key.days_until_expiry()} days")
print(f"Revoked: {key.revoked}")
print(f"Expired: {key.is_expired()}")
print(f"HSM-backed: {key.hsm_backed}")
```

## Production HSM Integration

### Prerequisites

1. **Hardware HSM Device**
   - Supported: PKCS#11 compliant HSMs (e.g., Thales, nCipher, YubiHSM)
   - HSM drivers installed and configured
   - HSM initialized with proper permissions

2. **Python Dependencies**
   ```bash
   pip install PyKCS11
   ```

### Configuration

```python
# Initialize with hardware HSM
hsm = HSMInterface(
    hsm_available=True,
    hsm_slot=0  # HSM slot number
)

# Generate key in HSM
key_id = hsm.generate_key(KeyType.ROOT_SIGNING)

# Sign with HSM
signature = hsm.sign(key_id, "data to sign")

# Revoke compromised key
hsm.revoke_key(key_id)
```

### PKCS#11 Integration Notes

The current implementation includes placeholders for PKCS#11 integration:

```python
# Production code would use:
from PyKCS11 import PyKCS11Lib

pkcs11 = PyKCS11Lib()
pkcs11.load("/path/to/hsm/library.so")
session = pkcs11.openSession(slot_id)

# Key generation
template = [
    (PyKCS11.CKA_CLASS, PyKCS11.CKO_PRIVATE_KEY),
    (PyKCS11.CKA_KEY_TYPE, PyKCS11.CKK_RSA),
    (PyKCS11.CKA_PRIVATE, True),
    (PyKCS11.CKA_SIGN, True),
]
pub_key, priv_key = session.generateKeyPair(template)

# Signing
mechanism = PyKCS11.Mechanism(PyKCS11.CKM_SHA256_RSA_PKCS, None)
signature = session.sign(priv_key, data, mechanism)
```

## Error Handling

### Exception Hierarchy

```python
HSMError                    # Base exception
├── HSMConnectionError      # HSM connection failures
├── HSMSigningError        # Signing operation failures
└── HSMRevocationError     # Revocation failures
```

### Example Error Handling

```python
from src.cerberus.sase.governance.key_management import (
    HSMSigningError,
    HSMRevocationError
)

try:
    signature = ceremony.sign_data(KeyType.ROOT_SIGNING, data)
except HSMRevocationError:
    # Key is revoked, rotate and retry
    ceremony.rotate_key(KeyType.ROOT_SIGNING)
    signature = ceremony.sign_data(KeyType.ROOT_SIGNING, data)
except HSMSigningError as e:
    # HSM signing failed
    logger.error(f"Signing failed: {e}")
    raise
```

## Development Mode

When `hsm_available=False`, the system uses software-based cryptography:

- **Key Generation**: SHA256 with random entropy
- **Signing**: HMAC-SHA256
- **Revocation**: In-memory tracking
- **Storage**: Memory-only (non-persistent)

This mode is suitable for:
- Unit testing
- Development environments
- CI/CD pipelines
- Systems without HSM hardware

## Security Considerations

### Production Deployment

1. **Always use HSM in production** (`hsm_available=True`)
2. **Monitor key rotation** - ensure automatic rotation is working
3. **Audit revocations** - log all key revocation events
4. **HSM access control** - restrict HSM slot access
5. **Backup HSM keys** - follow HSM vendor backup procedures

### Key Rotation Schedule

- **Automatic**: Every 90 days
- **Manual**: Call `rotate_key()` when needed
- **Emergency**: Call `revoke_compromised_key()` for compromise

### Revocation Best Practices

1. Revoke immediately upon compromise detection
2. Maintain revocation list (CRL)
3. Monitor for attempts to use revoked keys
4. Audit all revocation events

## Testing

### Run Tests

```bash
# Run all HSM tests
pytest tests/test_key_management_hsm.py -v

# Run specific test class
pytest tests/test_key_management_hsm.py::TestHSMInterface -v

# Run with coverage
pytest tests/test_key_management_hsm.py --cov=src.cerberus.sase.governance.key_management
```

### Test Coverage

The test suite covers:
- ✅ HSM initialization (software and hardware modes)
- ✅ Key generation with uniqueness
- ✅ Signing operations
- ✅ Key revocation
- ✅ Revoked key usage prevention
- ✅ Error handling
- ✅ Full lifecycle operations
- ✅ Multiple concurrent operations

## Monitoring and Logging

All HSM operations are logged:

```python
# Key generation
logger.info("HSM key generated: %s -> %s", key_type, key_id)

# Signing operations
logger.debug("HSM signature created for key: %s", key_id)

# Revocations
logger.critical("KEY REVOKED: %s (Total revoked: %d)", key_id, count)

# Rotations
logger.warning("ROTATING KEY: %s", key_type)
logger.warning("Automatic rotation triggered: %s", key_type)
```

## Performance

- **Key Generation**: ~1-10ms (HSM-dependent)
- **Signing**: ~5-50ms (HSM-dependent)
- **Revocation**: ~1-5ms
- **Software Mode**: Sub-millisecond for all operations

## Future Enhancements

1. **Multi-HSM Support**: Distribute keys across multiple HSMs
2. **Key Backup**: Automated HSM key backup/restore
3. **CRL Publishing**: Automatic Certificate Revocation List updates
4. **Metrics**: Prometheus metrics for key operations
5. **Key Versioning**: Maintain multiple key versions
6. **Threshold Signatures**: Multi-party signing support

## Troubleshooting

### HSM Connection Issues

```python
# Check HSM availability
hsm = HSMInterface(hsm_available=True)
# If connection fails, check:
# - HSM driver installation
# - HSM slot configuration
# - User permissions
```

### Signing Failures

```python
# Common causes:
# 1. Revoked key - check is_revoked()
# 2. HSM hardware failure - check logs
# 3. Permissions - verify HSM access rights
```

### Performance Issues

```python
# If signing is slow:
# 1. Check HSM hardware health
# 2. Verify HSM driver version
# 3. Monitor HSM CPU/memory
# 4. Consider load balancing across HSMs
```

## References

- [PKCS#11 Standard](https://www.oasis-open.org/committees/pkcs11/)
- [PyKCS11 Documentation](https://github.com/LudovicRousseau/PyKCS11)
- [HSM Best Practices](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)

## License

Part of the Sovereign Governance Substrate - SASE L12 Key Management
