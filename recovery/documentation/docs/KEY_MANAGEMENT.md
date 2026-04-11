# Key Management System Documentation

## Overview

The Sovereign Vault Key Management System provides enterprise-grade cryptographic key lifecycle management with hardware security support. It implements industry best practices for key generation, derivation, rotation, storage, and emergency recovery.

## Architecture

### Components

1. **KeyManager** - Core key lifecycle management
2. **KeyStorage** - Secure storage with multiple backends
3. **KeyDerivation** - Cryptographic key derivation functions

### Key Hierarchy

```
Master Key (256-bit)
├── Encryption Keys
│   ├── File Encryption Keys
│   └── Volume Encryption Keys
├── Authentication Keys
│   ├── User Authentication
│   └── Service Authentication
├── Signing Keys
│   └── Digital Signatures
└── Session Keys
    └── Temporary Session Keys
```

## Key Types

### Master Keys

- 256-bit cryptographically secure random keys
- Root of trust for the key hierarchy
- Automatically rotated based on policy
- Protected by hardware security when available

### Derived Keys

- Generated from master keys using HKDF
- Contextual derivation (file path, service name, etc.)
- Inherit rotation policy from parent
- Maintain audit trail to parent key

### Specialized Keys

- **File Keys**: Per-file encryption keys
- **Session Keys**: Temporary keys for sessions
- **Authentication Keys**: User/service authentication
- **Signing Keys**: Digital signature operations

## Key Lifecycle

### States

1. **GENERATING** - Key is being created
2. **ACTIVE** - Key is in active use
3. **ROTATING** - Key is being rotated
4. **ARCHIVED** - Key rotated but preserved
5. **DESTROYED** - Key permanently destroyed
6. **COMPROMISED** - Key marked as compromised

### Lifecycle Flow

```
GENERATING → ACTIVE → ROTATING → ARCHIVED → DESTROYED
                ↓
           COMPROMISED
```

## Key Derivation Functions (KDF)

### Supported Algorithms

#### HKDF (HMAC-based KDF)

- RFC 5869 compliant
- SHA-256 and SHA-512 variants
- Best for deriving multiple keys from master key
- Fast and secure

```python
from vault.core.keys import KeyDerivation, KDFType, KDFParameters

kdf = KeyDerivation()
params = KDFParameters(
    salt=os.urandom(32),
    length=32,
    info=b"context:file:data.txt"
)

derived_key = kdf.derive_key(
    master_key,
    KDFType.HKDF_SHA256,
    params
)
```

#### PBKDF2 (Password-Based KDF)

- RFC 8018 compliant
- SHA-256 and SHA-512 variants
- 600,000+ iterations (OWASP 2024 recommendations)
- Best for password-based key derivation

```python
params = KDFParameters(
    salt=os.urandom(32),
    iterations=600000,
    length=32
)

key = kdf.derive_key(
    password,
    KDFType.PBKDF2_SHA256,
    params
)
```

#### Argon2

- Winner of Password Hashing Competition
- Argon2id (hybrid) and Argon2i variants
- Memory-hard algorithm (resistant to GPU attacks)
- Recommended parameters: 64 MiB memory, 3 iterations

```python
params = KDFParameters(
    salt=os.urandom(32),
    iterations=3,
    memory_cost=65536,  # 64 MiB
    parallelism=4,
    length=32
)

key = kdf.derive_key(
    password,
    KDFType.ARGON2ID,
    params
)
```

## Key Storage

### Storage Backends

#### Encrypted File Storage

- AES-256-GCM encryption
- Per-key encrypted files
- Automatic backup support
- Default backend

```python
from vault.core.keys import KeyStorage, StorageConfig, StorageBackend

config = StorageConfig(
    backend=StorageBackend.ENCRYPTED_FILE,
    storage_path=Path.home() / ".vault" / "keyring",
    backup_enabled=True
)

storage = KeyStorage(config)
storage.store_key("my_key", key_bytes)
```

#### System Keyring

- OS-native credential storage
- Uses Windows Credential Manager / macOS Keychain / Linux Secret Service
- Integrates with system security

```python
config = StorageConfig(
    backend=StorageBackend.SYSTEM_KEYRING
)

storage = KeyStorage(config)
```

#### TPM (Trusted Platform Module)

- Hardware-backed key storage
- Keys never leave TPM
- Windows 10+ and Linux with TPM 2.0
- Highest security level

```python
config = StorageConfig(
    backend=StorageBackend.TPM,
    require_hardware=True
)

storage = KeyStorage(config)
```

#### Hardware Tokens (YubiKey/FIDO2)

- Physical security key support
- FIDO2/WebAuthn compatible
- Requires user presence for operations

```python
config = StorageConfig(
    backend=StorageBackend.YUBIKEY,
    require_hardware=True
)

storage = KeyStorage(config)
```

## Key Rotation

### Automatic Rotation

Keys are automatically rotated based on:

- Age (default: 90 days)
- Usage count
- Policy requirements
- Security events

```python
from vault.core.keys import KeyManager

manager = KeyManager()

# Check which keys need rotation

keys_to_rotate = manager.check_rotation_needed()

for key_meta in keys_to_rotate:
    print(f"Key {key_meta.key_id} needs rotation (age: {age} days)")
```

### Manual Rotation

```python

# Rotate a master key

new_key, new_meta = manager.rotate_key(old_key_id)

# Rotate a derived key (requires master key)

new_key, new_meta = manager.rotate_key(
    old_derived_key_id,
    master_key=master_key
)
```

### Rotation Strategy

1. Generate new key version
2. Mark old key as ROTATING
3. Activate new key
4. Archive old key
5. Update dependent systems
6. Audit log all operations

## Emergency Recovery

### Recovery Procedures

#### Master Key Recovery

```python

# Generate recovery key during initial setup

recovery_key = os.urandom(32)  # Store securely offline

# Emergency recovery

recovered_key, metadata = manager.emergency_recovery(
    recovery_key,
    compromised_key_id
)
```

#### Key Rollback

```python

# Rollback to previous version

target_meta = manager.rollback_key(
    current_key_id,
    target_version=3  # Rollback to version 3
)
```

#### Backup and Restore

```python

# Backup all keys

backup_file = storage.backup_keys("emergency_backup")

# Restore from backup

restored_count = storage.restore_keys(backup_file)
print(f"Restored {restored_count} keys")
```

## Audit Logging

### Logged Events

- `KEY_GENERATED` - New key created
- `KEY_DERIVED` - Key derived from parent
- `KEY_ROTATED` - Key rotated to new version
- `KEY_ROLLBACK` - Key rolled back to previous version
- `KEY_DESTROYED` - Key permanently destroyed
- `KEY_COMPROMISED` - Key marked as compromised
- `KEY_RECOVERY` - Emergency recovery performed

### Accessing Audit Logs

```python

# Get all audit events

all_events = manager.get_audit_log()

# Filter by key

key_events = manager.get_audit_log(key_id="master_20240101_abc123")

# Filter by event type

rotations = manager.get_audit_log(event_type="KEY_ROTATED")

# Export to file

manager.export_audit_log(Path("audit_log.json"))
```

## CLI Usage

### Installation

The `vault-keys` CLI is located in `usb_installer/vault/bin/`:

```bash

# Make executable (Unix/Linux)

chmod +x usb_installer/vault/bin/vault-keys

# Add to PATH or use directly

python usb_installer/vault/bin/vault-keys --help
```

### Commands

#### Generate Master Key

```bash
vault-keys generate --rotation-days 90

# Output: ✓ Master key generated: master_20240315_a1b2c3d4

```

#### Derive Child Key

```bash
vault-keys derive master_20240315_a1b2c3d4 "file:/data/secret.txt" \
    --key-type file --length 32

# Output: ✓ Derived key created: file_20240315_e5f6g7h8

```

#### List Keys

```bash
vault-keys list
vault-keys list --type master
vault-keys list --status active
```

#### Key Information

```bash
vault-keys info master_20240315_a1b2c3d4

# Output:

# Key ID:           master_20240315_a1b2c3d4

# Type:             master

# Status:           active

# Version:          1

# Algorithm:        AES-256-GCM

# Key Length:       256 bits

# Created:          2024-03-15T10:30:00

# Expires:          2024-06-13T10:30:00

# Days until expiry: 89

```

#### Rotate Key

```bash
vault-keys rotate master_20240315_a1b2c3d4

# Output:

# ✓ Key rotated successfully

#   Old key: master_20240315_a1b2c3d4 (v1)

#   New key: master_20240315_i9j0k1l2 (v2)

```

#### Check Rotation Status

```bash
vault-keys check-rotation

# Output:

# ⚠️  2 key(s) need rotation:

#   • master_20240115_xyz789

#     Age: 95 days (rotation period: 90 days)

```

#### Backup Keys

```bash
vault-keys backup --name "pre-migration-backup"

# Output: ✓ Keys backed up to: /home/user/.vault/keys/backup/pre-migration-backup.vault

```

#### Restore Keys

```bash
vault-keys restore /path/to/backup.vault

# Output: ✓ Restored 15 keys from backup

```

#### Destroy Key

```bash
vault-keys destroy old_key_123 --reason "Compromised in security incident"

# Prompt: Are you sure you want to destroy key old_key_123? (yes/no): yes

# Output: ✓ Key destroyed: old_key_123

```

#### Audit Log

```bash
vault-keys audit --limit 20
vault-keys audit --key-id master_20240315_a1b2c3d4
vault-keys audit --event-type KEY_ROTATED --verbose
```

## Best Practices

### Security

1. **Hardware Security**: Use TPM or hardware tokens in production
2. **Backup Strategy**: Regular automated backups to secure offline storage
3. **Rotation Policy**: Rotate keys every 90 days or less
4. **Principle of Least Privilege**: Derive specialized keys for specific purposes
5. **Audit Everything**: Review audit logs regularly

### Key Management

1. **Master Key Protection**:
   - Generate master keys on secure, isolated systems
   - Store recovery keys offline in physically secure location
   - Use hardware security modules (TPM/YubiKey) when available

2. **Key Hierarchy**:
   - Use master keys only for derivation, not direct encryption
   - Derive purpose-specific keys (file, session, auth)
   - Maintain clear parent-child relationships

3. **Rotation**:
   - Automate rotation checks and notifications
   - Test rotation procedures regularly
   - Maintain rollback capability

4. **Incident Response**:
   - Document emergency recovery procedures
   - Practice recovery scenarios
   - Maintain offline backups

### Development

1. **Testing**: Always test in non-production environment first
2. **Monitoring**: Set up alerts for key expiration and rotation needs
3. **Documentation**: Document custom derivation contexts and key purposes
4. **Compliance**: Ensure key management meets regulatory requirements

## Security Considerations

### Threat Model

Protected against:

- ✅ Key extraction attacks
- ✅ Brute force attacks (Argon2 memory-hard)
- ✅ Rainbow table attacks (unique salts)
- ✅ Timing attacks (constant-time comparisons)
- ✅ Storage tampering (integrity verification)

### Cryptographic Guarantees

- **Confidentiality**: AES-256-GCM encryption
- **Integrity**: AEAD authentication tags
- **Forward Secrecy**: Key rotation and archival
- **Non-repudiation**: Comprehensive audit logging

### Compliance

Meets requirements for:

- NIST SP 800-57 (Key Management)
- FIPS 140-2 Level 2 (with TPM backend)
- PCI DSS 3.2 (Key Management)
- GDPR (Encryption and Key Management)

## Troubleshooting

### Common Issues

#### "cryptography library required"

```bash
pip install cryptography
```

#### "TPM not available on this system"

- Windows: Ensure TPM is enabled in BIOS
- Linux: Install `tpm2-tools` and `tpm2-pytss`

#### "No FIDO2 devices detected"

- Ensure hardware token is connected
- Install `fido2` library: `pip install fido2`

#### Key retrieval fails

- Verify storage backend is accessible
- Check file permissions on storage directory
- Ensure master encryption key is available

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all key operations will log debug information

```

## API Reference

### KeyManager

```python
class KeyManager:
    def __init__(self, metadata_dir: Optional[Path] = None)
    def generate_master_key(self, key_id: Optional[str] = None, 
                           rotation_period_days: int = 90) -> tuple[bytes, KeyMetadata]
    def derive_key(self, master_key: bytes, parent_key_id: str, context: str,
                   key_type: KeyType = KeyType.DERIVED, 
                   key_length: int = 32) -> tuple[bytes, KeyMetadata]
    def rotate_key(self, old_key_id: str, 
                   master_key: Optional[bytes] = None) -> tuple[bytes, KeyMetadata]
    def rollback_key(self, current_key_id: str, 
                     target_version: int) -> Optional[KeyMetadata]
    def destroy_key(self, key_id: str, reason: str = "")
    def mark_compromised(self, key_id: str, details: str = "")
    def emergency_recovery(self, recovery_key: bytes, 
                          key_id: str) -> tuple[bytes, KeyMetadata]
    def list_keys(self, key_type: Optional[KeyType] = None,
                  status: Optional[KeyStatus] = None) -> List[KeyMetadata]
    def check_rotation_needed(self) -> List[KeyMetadata]
    def get_audit_log(self, key_id: Optional[str] = None,
                      event_type: Optional[str] = None) -> List[AuditEvent]
```

### KeyStorage

```python
class KeyStorage:
    def __init__(self, config: Optional[StorageConfig] = None)
    def store_key(self, key_id: str, key_data: bytes,
                  metadata: Optional[Dict[str, Any]] = None) -> bool
    def retrieve_key(self, key_id: str) -> Optional[bytes]
    def delete_key(self, key_id: str) -> bool
    def list_keys(self) -> List[str]
    def backup_keys(self, backup_name: Optional[str] = None) -> Path
    def restore_keys(self, backup_file: Path) -> int
    def verify_integrity(self) -> bool
```

### KeyDerivation

```python
class KeyDerivation:
    def derive_key(self, password: Union[str, bytes], kdf_type: KDFType,
                   params: Optional[KDFParameters] = None) -> bytes
    def derive_hierarchy(self, master_key: bytes, context: str,
                        key_count: int = 1, key_length: int = 32) -> list[bytes]
    def derive_file_key(self, master_key: bytes, file_path: str,
                       salt: Optional[bytes] = None) -> tuple[bytes, bytes]
    def derive_session_key(self, master_key: bytes, session_id: str) -> bytes
    def verify_password(self, password: Union[str, bytes], stored_hash: bytes,
                       kdf_type: KDFType, params: KDFParameters) -> bool
```

## Examples

See `tests/vault/test_keys.py` for comprehensive examples of all functionality.

## License

Part of the Sovereign Governance Substrate - see main project LICENSE file.

## Support

For issues and questions, see the main project repository.
