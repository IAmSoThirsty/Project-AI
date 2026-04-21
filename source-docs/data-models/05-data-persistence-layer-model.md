# Data Persistence Layer Model

**Module**: `src/app/core/data_persistence.py` [[src/app/core/data_persistence.py]]  
**Storage**: `data/.keys/` (key management), various encrypted data files  
**Persistence**: Encrypted binary files with versioning  
**Schema Version**: 1.0

---

## Overview

The Data Persistence Layer provides enterprise-grade encrypted state management with support for multiple encryption algorithms (AES-256-GCM, ChaCha20-Poly1305, Fernet), versioned configurations, automatic backup/recovery, and audit trail persistence.

### Key Features

- **Multi-Algorithm Encryption**: AES-256-GCM, ChaCha20-Poly1305, Fernet
- **Key Management**: Automatic key generation, rotation tracking, owner-only permissions
- **Versioned Configurations**: Semantic versioning with migration support
- **Atomic Operations**: Thread-safe writes with rollback capability
- **Backup & Recovery**: Automatic backups with configurable retention
- **Schema Validation**: JSON Schema-based data validation
- **Compression**: gzip support for large data files

---

## Encryption Algorithms

### Supported Algorithms

```python
from enum import Enum

class EncryptionAlgorithm(Enum):
    AES_256_GCM = "AES-256-GCM"           # Default, fastest
    CHACHA20_POLY1305 = "ChaCha20-Poly1305"  # Mobile-optimized
    FERNET = "Fernet"                     # Symmetric, timestamp-based
```

### Algorithm Comparison

| Algorithm | Key Size | Performance | Use Case |
|-----------|----------|-------------|----------|
| **AES-256-GCM** | 32 bytes | Fastest | Default, general-purpose |
| **ChaCha20-Poly1305** | 32 bytes | Fast (no AES-NI) | Mobile devices, ARM processors |
| **Fernet** | 32 bytes | Moderate | Timestamp validation, token-based auth |

---

## Schema Structure

### Encrypted Data File Format

**Binary Structure** (AES-256-GCM example):

```
[Algorithm ID: 1 byte]
[Key ID: 16 bytes]
[Nonce: 12 bytes]
[Ciphertext: variable length]
[Authentication Tag: 16 bytes]
```

**Metadata Sidecar** (`.meta.json`):

```json
{
  "algorithm": "AES-256-GCM",
  "key_id": "20240120",
  "version": "1.2.3",
  "created_at": "2024-01-20T14:00:00Z",
  "updated_at": "2024-01-20T14:30:00Z",
  "checksum": "sha256:a3f7b8c2d1e4f5g6h7i8j9k0l1m2n3o4",
  "compressed": false,
  "backup_count": 3
}
```

### Key Management Structure

**Master Key File**: `data/.keys/master.key` (32 bytes, 0600 permissions)

**Key Metadata**: `data/.keys/current_key_id` (text file)

```
20240120
```

**Key Rotation Log**: `data/.keys/last_rotation` (ISO 8601 timestamp)

```
2024-01-20T00:00:00Z
```

---

## Field Specifications

### DataVersion

```python
@dataclass
class DataVersion:
    major: int  # Breaking changes
    minor: int  # New features (backward compatible)
    patch: int  # Bug fixes
```

**Semantic Versioning**:
- **Major**: Incompatible schema changes (requires migration)
- **Minor**: New optional fields (backward compatible)
- **Patch**: Bug fixes, no schema changes

### Encryption Metadata

| Field | Type | Description |
|-------|------|-------------|
| `algorithm` | string | Encryption algorithm used |
| `key_id` | string | Key identifier (YYYYMMDD format) |
| `version` | string | Schema version (semver) |
| `created_at` | datetime | File creation timestamp |
| `updated_at` | datetime | Last modification timestamp |
| `checksum` | string | SHA-256 hash of plaintext data |
| `compressed` | boolean | Whether data is gzip-compressed |
| `backup_count` | integer | Number of backups retained |

---

## Encryption Operations

### Initialization

```python
from app.core.data_persistence import EncryptedStateManager, EncryptionAlgorithm

manager = EncryptedStateManager(
    data_dir="data",
    algorithm=EncryptionAlgorithm.AES_256_GCM,
    master_key=None,  # Auto-generate if not provided
    key_rotation_days=90
)
```

### Encrypt Data

```python
data = b"Sensitive information to encrypt"

encrypted_data, metadata = manager.encrypt_data(data)
# Returns: (bytes, {"key_id": "20240120", "algorithm": "AES-256-GCM"})
```

**AES-256-GCM Implementation**:

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_data(self, data: bytes) -> tuple[bytes, dict[str, str]]:
    with self._lock:
        if self.algorithm == EncryptionAlgorithm.AES_256_GCM:
            nonce = os.urandom(12)  # 96-bit nonce
            encrypted = self._cipher.encrypt(nonce, data, None)
            result = nonce + encrypted  # Prepend nonce
            
        metadata = {
            "key_id": self.current_key_id,
            "algorithm": self.algorithm.value
        }
        return result, metadata
```

### Decrypt Data

```python
decrypted_data = manager.decrypt_data(encrypted_data, metadata)
# Returns: bytes (original plaintext)
```

**AES-256-GCM Decryption**:

```python
def decrypt_data(self, data: bytes, metadata: dict[str, str]) -> bytes:
    with self._lock:
        if metadata["algorithm"] == "AES-256-GCM":
            nonce = data[:12]
            ciphertext = data[12:]
            plaintext = self._cipher.decrypt(nonce, ciphertext, None)
        return plaintext
```

---

## Versioned Configuration System

### Configuration Schema

```python
@dataclass
class ConfigVersion:
    version: DataVersion
    schema: dict[str, Any]
    migration_func: Callable[[dict], dict] | None = None
```

### Version Management

```python
class VersionedConfigManager:
    def __init__(self, config_file: str, current_version: DataVersion):
        self.config_file = config_file
        self.current_version = current_version
        self.migrations: dict[str, Callable] = {}
    
    def register_migration(self, from_version: str, to_version: str, migration_func: Callable):
        """Register a migration function between versions."""
        key = f"{from_version}->{to_version}"
        self.migrations[key] = migration_func
    
    def load_config(self) -> dict:
        """Load config and apply migrations if needed."""
        if not os.path.exists(self.config_file):
            return self._default_config()
        
        config = self._load_from_disk()
        stored_version = DataVersion.from_string(config.get("_version", "1.0.0"))
        
        if stored_version < self.current_version:
            config = self._migrate(config, stored_version, self.current_version)
        
        return config
```

### Migration Example

```python
def migrate_1_0_to_1_1(config: dict) -> dict:
    """Migration: Add new 'encryption_enabled' field."""
    config["encryption_enabled"] = True
    config["_version"] = "1.1.0"
    return config

def migrate_1_1_to_2_0(config: dict) -> dict:
    """Migration: Rename 'user_name' to 'username' (breaking change)."""
    if "user_name" in config:
        config["username"] = config.pop("user_name")
    config["_version"] = "2.0.0"
    return config

# Register migrations
config_manager.register_migration("1.0.0", "1.1.0", migrate_1_0_to_1_1)
config_manager.register_migration("1.1.0", "2.0.0", migrate_1_1_to_2_0)
```

---

## Backup & Recovery

### Automatic Backup Strategy

```python
def save_with_backup(self, filepath: str, data: dict, max_backups: int = 3):
    """Save data with automatic backup rotation."""
    # Create backup of existing file
    if os.path.exists(filepath):
        backup_path = self._create_backup(filepath)
        shutil.copy2(filepath, backup_path)
    
    # Save new data
    _atomic_write_json(filepath, data)
    
    # Rotate old backups
    self._rotate_backups(filepath, max_backups)

def _create_backup(self, filepath: str) -> str:
    """Generate timestamped backup filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{filepath}.{timestamp}.bak"
    return backup_name

def _rotate_backups(self, filepath: str, max_backups: int):
    """Keep only the N most recent backups."""
    backup_pattern = f"{filepath}.*.bak"
    backups = sorted(glob.glob(backup_pattern), reverse=True)
    
    for old_backup in backups[max_backups:]:
        os.remove(old_backup)
        logger.info("Removed old backup: %s", old_backup)
```

### Recovery

```python
def restore_from_backup(self, filepath: str, backup_index: int = 0) -> bool:
    """Restore data from backup (0 = most recent)."""
    backup_pattern = f"{filepath}.*.bak"
    backups = sorted(glob.glob(backup_pattern), reverse=True)
    
    if backup_index >= len(backups):
        logger.error("Backup index %d out of range", backup_index)
        return False
    
    backup_path = backups[backup_index]
    shutil.copy2(backup_path, filepath)
    logger.info("Restored from backup: %s", backup_path)
    return True
```

---

## Data Compression

### Compression Support

```python
import gzip

def save_compressed(self, filepath: str, data: bytes):
    """Save data with gzip compression."""
    compressed = gzip.compress(data, compresslevel=9)
    
    with open(filepath, 'wb') as f:
        f.write(compressed)
    
    # Save metadata
    meta = {
        "compressed": True,
        "original_size": len(data),
        "compressed_size": len(compressed),
        "compression_ratio": len(compressed) / len(data)
    }
    self._save_metadata(filepath, meta)

def load_compressed(self, filepath: str) -> bytes:
    """Load and decompress data."""
    with open(filepath, 'rb') as f:
        compressed = f.read()
    
    return gzip.decompress(compressed)
```

### Compression Decision Logic

```python
COMPRESSION_THRESHOLD = 10 * 1024  # 10KB

def should_compress(data: bytes) -> bool:
    """Determine if data should be compressed."""
    if len(data) < COMPRESSION_THRESHOLD:
        return False  # Too small, compression overhead not worth it
    
    # Sample compression ratio
    sample = data[:1024]
    compressed_sample = gzip.compress(sample)
    ratio = len(compressed_sample) / len(sample)
    
    return ratio < 0.8  # Compress if 20%+ savings
```

---

## Key Management

### Master Key Generation

```python
def _load_or_generate_master_key(self) -> bytes:
    """Load existing master key or generate new one."""
    key_file = self.keys_dir / "master.key"
    
    if key_file.exists():
        with open(key_file, "rb") as f:
            key = f.read()
        logger.info("Loaded existing master key")
    else:
        # Generate new master key
        if self.algorithm == EncryptionAlgorithm.FERNET:
            key = Fernet.generate_key()
        else:
            key = os.urandom(32)  # 256 bits
        
        # Save key with restrictive permissions
        with open(key_file, "wb") as f:
            f.write(key)
        key_file.chmod(0o600)  # Owner read/write only
        
        logger.info("Generated new master key")
    
    return key
```

### Key Rotation

```python
def rotate_key(self) -> bool:
    """Rotate encryption key (decrypt with old, encrypt with new)."""
    # Generate new key
    new_key = os.urandom(32)
    new_key_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save new key
    new_key_file = self.keys_dir / f"key_{new_key_id}.key"
    with open(new_key_file, "wb") as f:
        f.write(new_key)
    new_key_file.chmod(0o600)
    
    # Re-encrypt all data files with new key
    old_cipher = self._cipher
    self._cipher = self._initialize_cipher_with_key(new_key)
    
    for data_file in self._get_encrypted_files():
        try:
            # Decrypt with old key
            encrypted_data = self._read_file(data_file)
            plaintext = old_cipher.decrypt(encrypted_data)
            
            # Encrypt with new key
            new_encrypted, metadata = self.encrypt_data(plaintext)
            self._write_file(data_file, new_encrypted, metadata)
        except Exception as e:
            logger.error("Failed to rotate key for %s: %s", data_file, e)
            return False
    
    # Update key ID
    self.current_key_id = new_key_id
    self._save_key_rotation_time()
    
    logger.info("Key rotation completed: %s", new_key_id)
    return True
```

### Key Expiration Check

```python
def check_key_rotation_needed(self) -> bool:
    """Check if key rotation is due."""
    days_since_rotation = (datetime.now() - self.last_rotation).days
    return days_since_rotation >= self.key_rotation_days
```

---

## Audit Trail

### Audit Log Schema

```json
{
  "audit_log": [
    {
      "timestamp": "2024-01-20T14:30:00Z",
      "operation": "encrypt",
      "file": "data/users.json",
      "user": "admin",
      "key_id": "20240120",
      "success": true,
      "checksum": "sha256:a3f7b8c2..."
    },
    {
      "timestamp": "2024-01-20T14:35:00Z",
      "operation": "decrypt",
      "file": "data/users.json",
      "user": "admin",
      "key_id": "20240120",
      "success": true
    }
  ]
}
```

### Audit Logging

```python
def _log_audit_event(self, operation: str, filepath: str, success: bool, **kwargs):
    """Log audit event to audit trail."""
    event = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "file": filepath,
        "user": kwargs.get("user", "system"),
        "key_id": self.current_key_id,
        "success": success
    }
    event.update(kwargs)
    
    # Append to audit log
    audit_file = self.data_dir / "audit_trail.json"
    audit_log = self._load_audit_log()
    audit_log.append(event)
    
    _atomic_write_json(audit_file, {"audit_log": audit_log[-1000:]})  # Keep last 1000
```

---

## Usage Examples

### Basic Encryption/Decryption

```python
from app.core.data_persistence import EncryptedStateManager, EncryptionAlgorithm

manager = EncryptedStateManager(
    data_dir="data",
    algorithm=EncryptionAlgorithm.AES_256_GCM
)

# Encrypt data
sensitive_data = b"User credit card: 1234-5678-9012-3456"
encrypted, metadata = manager.encrypt_data(sensitive_data)

# Decrypt data
decrypted = manager.decrypt_data(encrypted, metadata)
assert decrypted == sensitive_data
```

### Versioned Configuration

```python
config_manager = VersionedConfigManager(
    config_file="data/app_config.json",
    current_version=DataVersion(2, 0, 0)
)

# Register migrations
config_manager.register_migration("1.0.0", "1.1.0", migrate_1_0_to_1_1)
config_manager.register_migration("1.1.0", "2.0.0", migrate_1_1_to_2_0)

# Load config (auto-migrates if needed)
config = config_manager.load_config()
```

### Backup and Recovery

```python
# Save with automatic backup
manager.save_with_backup("data/critical_state.json", state_data, max_backups=5)

# Restore from most recent backup
manager.restore_from_backup("data/critical_state.json", backup_index=0)

# Restore from older backup
manager.restore_from_backup("data/critical_state.json", backup_index=2)
```

---

## Performance Considerations

### Encryption Performance

| Algorithm | Encrypt (MB/s) | Decrypt (MB/s) | Overhead |
|-----------|----------------|----------------|----------|
| AES-256-GCM | 500 | 500 | Lowest |
| ChaCha20-Poly1305 | 350 | 350 | Low |
| Fernet | 150 | 150 | Moderate |

**Recommendation**: Use AES-256-GCM for production (hardware acceleration via AES-NI).

### Compression Trade-offs

- **CPU Cost**: 10-50ms per MB (compression level 9)
- **Storage Savings**: 30-70% for text data
- **Use Case**: Large JSON files (>10KB), log files, conversation history

---

## Security Considerations

### Key File Permissions

```python
# Unix permissions: Owner read/write only
key_file.chmod(0o600)

# Verify permissions
stat_info = os.stat(key_file)
assert stat_info.st_mode & 0o777 == 0o600
```

### Key Storage Best Practices

1. **Never commit keys to Git**: Add `data/.keys/` to `.gitignore`
2. **Use environment variables for prod**: Load master key from env var
3. **Rotate keys regularly**: Default 90 days, configurable
4. **Backup keys securely**: Separate encrypted backup of keys

### Algorithm Selection

- **AES-256-GCM**: Best for Intel/AMD CPUs (AES-NI support)
- **ChaCha20-Poly1305**: Best for ARM/mobile (no AES-NI)
- **Fernet**: Best for token-based systems (timestamp validation)

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `storage.py` | Higher-level storage abstraction (SQLite + JSON) |
| `cloud_sync.py` | Uses encryption for cloud data sync |
| `user_manager.py` | Encrypts sensitive user data |
| `location_tracker.py` | Encrypts location history |

---

## Future Enhancements

1. **Hardware Security Module (HSM)**: Integrate with HSM for key management
2. **Key Derivation Function (KDF)**: Derive encryption keys from user passwords
3. **Encrypted Indices**: Searchable encryption for encrypted data
4. **Multi-Key Support**: Per-user encryption keys
5. **Cloud KMS Integration**: AWS KMS, Azure Key Vault, Google Cloud KMS

---

## References

- **NIST SP 800-38D**: AES-GCM specification
- **RFC 7539**: ChaCha20-Poly1305 AEAD
- **Fernet Specification**: https://github.com/fernet/spec
- **Cryptography Library**: https://cryptography.io/

---

**Last Updated**: 2024-01-20  
**Schema Version**: 1.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/data_persistence.py]]
