# Data Persistence Layer - Encrypted State Management

## Overview

The Data Persistence module (`src/app/core/data_persistence.py`) provides enterprise-grade encrypted state management with versioned configuration, automatic backup/recovery, and comprehensive security features for the God Tier Zombie Apocalypse Defense Engine.

**Location**: `src/app/core/data_persistence.py`  
**Lines of Code**: ~800  
**Key Features**: Multi-algorithm encryption, versioned config, audit trails, air-gapped operation  
**Dependencies**: cryptography (Fernet, AESGCM, ChaCha20Poly1305), json, gzip

---

## Architecture

### System Components

```
Data Persistence Layer
├── EncryptedStateManager
│   ├── Multi-algorithm encryption (AES-256-GCM, ChaCha20-Poly1305, Fernet)
│   ├── Key rotation (90-day default)
│   ├── Thread-safe operations
│   └── Metadata tracking
│
├── VersionedConfigurationSystem
│   ├── Semantic versioning
│   ├── Schema validation
│   ├── Migration support
│   └── Rollback capability
│
├── BackupManager
│   ├── Automatic backups
│   ├── Compression (gzip)
│   ├── Retention policy
│   └── Recovery procedures
│
└── AuditTrailPersistence
    ├── Immutable logs
    ├── Digital signatures
    ├── Tamper detection
    └── Compliance reporting
```

---

## Encryption Algorithms

### Supported Algorithms

```python
class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms"""
    AES_256_GCM = "AES-256-GCM"
    CHACHA20_POLY1305 = "ChaCha20-Poly1305"
    FERNET = "Fernet"
```

### Algorithm Comparison

| Algorithm | Security | Speed | Use Case |
|-----------|----------|-------|----------|
| **AES-256-GCM** | ⭐⭐⭐⭐⭐ | Fast | Production (hardware acceleration) |
| **ChaCha20-Poly1305** | ⭐⭐⭐⭐⭐ | Very Fast | Mobile/embedded systems |
| **Fernet** | ⭐⭐⭐⭐ | Fast | Simple use cases (symmetric+timestamp) |

---

## Core Components

### 1. EncryptedStateManager

**Purpose**: Transparent encryption/decryption of sensitive state data with key rotation support.

#### Initialization

```python
class EncryptedStateManager:
    def __init__(
        self,
        data_dir: str = "data",
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        master_key: bytes | None = None,
        key_rotation_days: int = 90,
    ):
```

**Parameters**:
- `data_dir`: Directory for encrypted data storage
- `algorithm`: Encryption algorithm (AES-256-GCM recommended)
- `master_key`: Master encryption key (auto-generated if None)
- `key_rotation_days`: Days between automatic key rotation (default: 90)

**Example**:
```python
# Initialize with default AES-256-GCM
manager = EncryptedStateManager("data/secure")

# Initialize with ChaCha20-Poly1305 for embedded systems
mobile_manager = EncryptedStateManager(
    "data/mobile",
    algorithm=EncryptionAlgorithm.CHACHA20_POLY1305
)

# Initialize with custom master key
custom_key = os.urandom(32)  # 256 bits
secure_manager = EncryptedStateManager(
    "data/secure",
    master_key=custom_key
)
```

---

#### Key Management

##### _load_or_generate_master_key()
```python
def _load_or_generate_master_key(self) -> bytes:
    """Load existing master key or generate new one."""
```

**File Location**: `{data_dir}/.keys/master.key`  
**Permissions**: 0o600 (owner read/write only)

**Key Generation**:
- **Fernet**: Uses `Fernet.generate_key()` (URL-safe base64)
- **AES/ChaCha20**: Uses `os.urandom(32)` (256 bits)

**Security**:
- Keys stored in hidden `.keys/` directory
- Directory permissions: 0o700 (owner only)
- File permissions: 0o600 (owner read/write only)

---

##### Key Rotation

```python
def rotate_key(self) -> bool:
    """
    Rotate encryption key.
    
    Steps:
    1. Generate new key
    2. Decrypt all data with old key
    3. Re-encrypt with new key
    4. Update key ID and rotation timestamp
    5. Archive old key (for recovery)
    """
```

**Rotation Trigger**:
- Manual: Call `rotate_key()`
- Automatic: When `last_rotation + key_rotation_days` expires

**Example**:
```python
manager = EncryptedStateManager(key_rotation_days=90)

# Check if rotation needed
days_since_rotation = (datetime.now() - manager.last_rotation).days
if days_since_rotation >= manager.key_rotation_days:
    manager.rotate_key()
```

---

#### Encryption/Decryption

##### encrypt_data()
```python
def encrypt_data(self, data: bytes) -> tuple[bytes, dict[str, str]]:
    """
    Encrypt data.
    
    Returns:
        Tuple of (encrypted_data, metadata)
    """
```

**Metadata Structure**:
```json
{
  "algorithm": "AES-256-GCM",
  "key_id": "20250124",
  "nonce_length": 12
}
```

**Example**:
```python
manager = EncryptedStateManager()

# Encrypt configuration
config_json = json.dumps({"setting": "value"})
encrypted, metadata = manager.encrypt_data(config_json.encode())

# Store encrypted data and metadata
save_to_file("config.enc", encrypted)
save_to_file("config.meta", json.dumps(metadata))
```

---

##### decrypt_data()
```python
def decrypt_data(self, encrypted_data: bytes, metadata: dict[str, str]) -> bytes:
    """
    Decrypt data using metadata.
    
    Args:
        encrypted_data: Encrypted bytes
        metadata: Encryption metadata (algorithm, key_id, etc.)
    
    Returns:
        Decrypted bytes
    """
```

**Example**:
```python
# Load encrypted data and metadata
encrypted = load_from_file("config.enc")
metadata = json.loads(load_from_file("config.meta"))

# Decrypt
decrypted = manager.decrypt_data(encrypted, metadata)
config = json.loads(decrypted.decode())
```

---

#### State Persistence

##### save_encrypted_state()
```python
def save_encrypted_state(self, state_id: str, state_data: dict[str, Any]) -> bool:
    """
    Save state with encryption.
    
    File Structure:
    - {data_dir}/{state_id}.enc (encrypted data)
    - {data_dir}/{state_id}.meta (metadata)
    
    Returns:
        bool: True if save successful
    """
```

**Example**:
```python
manager = EncryptedStateManager()

# Save governance state
governance_state = {
    "four_laws_enabled": True,
    "strictness": "high",
    "last_decision": "allow_action_x"
}

success = manager.save_encrypted_state("governance", governance_state)
if success:
    print("State saved securely")
```

---

##### load_encrypted_state()
```python
def load_encrypted_state(self, state_id: str) -> dict[str, Any] | None:
    """
    Load and decrypt state.
    
    Args:
        state_id: State identifier
    
    Returns:
        Decrypted state dictionary, or None if not found
    """
```

**Example**:
```python
# Load governance state
state = manager.load_encrypted_state("governance")
if state:
    print(f"Four Laws enabled: {state['four_laws_enabled']}")
else:
    print("State not found - using defaults")
```

---

### 2. Data Versioning

#### DataVersion Class

```python
@dataclass
class DataVersion:
    """Version information for data migration"""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __lt__(self, other: "DataVersion") -> bool:
        return (self.major, self.minor, self.patch) < (
            other.major, other.minor, other.patch
        )
    
    @classmethod
    def from_string(cls, version_str: str) -> "DataVersion":
        """Parse version string like '1.0.0'"""
        parts = version_str.split(".")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))
```

**Example**:
```python
v1 = DataVersion(1, 0, 0)
v2 = DataVersion(1, 2, 3)

print(v1 < v2)  # True
print(str(v2))  # "1.2.3"

v3 = DataVersion.from_string("2.0.0")
print(v3 > v2)  # True
```

---

#### Versioned Configuration System

```python
class VersionedConfigurationSystem:
    """
    Configuration system with versioning and migration support.
    """
    
    def __init__(self, config_dir: str = "data/config"):
        self.config_dir = Path(config_dir)
        self.current_version = DataVersion(1, 0, 0)
        self.migrations = {}  # version -> migration_function
```

**Schema Evolution**:
```python
config_system = VersionedConfigurationSystem()

# Register migration
def migrate_v1_to_v2(old_config: dict) -> dict:
    """Add new field 'feature_x'"""
    old_config["feature_x"] = {
        "enabled": False,
        "threshold": 0.8
    }
    return old_config

config_system.register_migration(
    DataVersion(1, 0, 0),
    DataVersion(2, 0, 0),
    migrate_v1_to_v2
)

# Load and auto-migrate
config = config_system.load_config("app_settings")
# If config is v1.0.0, automatically migrates to v2.0.0
```

---

### 3. Backup Manager

#### Automatic Backups

```python
class BackupManager:
    """
    Automatic backup with compression and retention policies.
    """
    
    def __init__(
        self,
        data_dir: str = "data",
        backup_dir: str = "data/backups",
        max_backups: int = 10,
        compress: bool = True
    ):
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.compress = compress
```

#### Creating Backups

```python
def create_backup(self, name: str = None) -> Path:
    """
    Create a backup of all data files.
    
    Returns:
        Path to backup file
    """
    if name is None:
        name = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    backup_file = self.backup_dir / f"backup_{name}"
    
    if self.compress:
        backup_file = backup_file.with_suffix(".tar.gz")
        # Create compressed tarball
        with tarfile.open(backup_file, "w:gz") as tar:
            tar.add(self.data_dir, arcname="data")
    else:
        # Copy directory
        shutil.copytree(self.data_dir, backup_file)
    
    # Enforce retention policy
    self._cleanup_old_backups()
    
    return backup_file
```

**Example**:
```python
backup_manager = BackupManager(max_backups=10)

# Create automatic backup
backup_path = backup_manager.create_backup()
print(f"Backup created: {backup_path}")

# Create named backup
important_backup = backup_manager.create_backup("pre_upgrade")
```

---

#### Backup Restoration

```python
def restore_backup(self, backup_file: Path, target_dir: Path = None) -> bool:
    """
    Restore data from backup.
    
    Args:
        backup_file: Path to backup file
        target_dir: Target directory (defaults to self.data_dir)
    
    Returns:
        bool: True if restoration successful
    """
    target_dir = target_dir or self.data_dir
    
    # Backup current data before restoration
    self.create_backup("pre_restore")
    
    # Extract backup
    if backup_file.suffix == ".gz":
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(target_dir.parent)
    else:
        shutil.rmtree(target_dir)
        shutil.copytree(backup_file, target_dir)
    
    return True
```

**Example**:
```python
# List available backups
backups = backup_manager.list_backups()
print("Available backups:")
for backup in backups:
    print(f"  - {backup.name} ({backup.stat().st_size} bytes)")

# Restore specific backup
latest_backup = backups[0]
backup_manager.restore_backup(latest_backup)
```

---

### 4. Audit Trail Persistence

#### Immutable Audit Log

```python
class AuditTrailPersistence:
    """
    Immutable audit trail with tamper detection.
    """
    
    def __init__(self, audit_dir: str = "data/audit"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        
        # Digital signature for tamper detection
        self.signature_key = self._load_or_generate_signature_key()
```

#### Recording Events

```python
def record_event(
    self,
    event_type: str,
    actor: str,
    action: str,
    details: dict[str, Any]
) -> str:
    """
    Record audit event with digital signature.
    
    Returns:
        Event ID (SHA-256 hash)
    """
    event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "actor": actor,
        "action": action,
        "details": details
    }
    
    # Generate unique event ID
    event_id = hashlib.sha256(
        json.dumps(event, sort_keys=True).encode()
    ).hexdigest()
    
    event["event_id"] = event_id
    
    # Sign event
    signature = self._sign_event(event)
    event["signature"] = signature
    
    # Append to immutable log
    self._append_to_log(event)
    
    return event_id
```

**Example**:
```python
audit = AuditTrailPersistence()

# Record governance decision
event_id = audit.record_event(
    event_type="governance_decision",
    actor="FourLaws",
    action="block_dangerous_action",
    details={
        "requested_action": "delete_critical_file",
        "reason": "Violates First Law (harm to humans)",
        "severity": "high"
    }
)

print(f"Event recorded: {event_id}")
```

---

#### Tamper Detection

```python
def verify_integrity(self) -> tuple[bool, list[str]]:
    """
    Verify integrity of audit trail.
    
    Returns:
        (is_valid, list_of_tampered_events)
    """
    tampered_events = []
    
    for event in self._read_all_events():
        # Verify signature
        expected_signature = self._sign_event(event)
        actual_signature = event.get("signature")
        
        if expected_signature != actual_signature:
            tampered_events.append(event["event_id"])
    
    return len(tampered_events) == 0, tampered_events
```

**Example**:
```python
# Verify audit log integrity
is_valid, tampered = audit.verify_integrity()

if is_valid:
    print("✓ Audit trail integrity verified")
else:
    print(f"✗ Tampered events detected: {tampered}")
```

---

## Usage Patterns

### Pattern 1: Secure Configuration Management

```python
class SecureConfigManager:
    def __init__(self):
        self.state_manager = EncryptedStateManager(
            "data/config",
            algorithm=EncryptionAlgorithm.AES_256_GCM
        )
        self.backup_manager = BackupManager(
            "data/config",
            "data/config_backups"
        )
        self.audit = AuditTrailPersistence("data/config_audit")
    
    def update_config(self, config_id: str, new_config: dict, actor: str):
        """Update configuration with audit trail and backup."""
        # Backup before changes
        self.backup_manager.create_backup(f"pre_{config_id}_update")
        
        # Load current config
        old_config = self.state_manager.load_encrypted_state(config_id)
        
        # Save new config
        self.state_manager.save_encrypted_state(config_id, new_config)
        
        # Record audit event
        self.audit.record_event(
            event_type="config_update",
            actor=actor,
            action=f"update_{config_id}",
            details={
                "old_config": old_config,
                "new_config": new_config,
                "changes": self._diff_configs(old_config, new_config)
            }
        )
```

---

### Pattern 2: Air-Gapped Operation

```python
class AirGappedDataManager:
    """Data management for offline/air-gapped systems."""
    
    def __init__(self):
        self.state_manager = EncryptedStateManager()
        self.backup_manager = BackupManager()
    
    def export_for_transfer(self, output_path: Path):
        """Export encrypted data bundle for physical transfer."""
        # Create backup
        backup = self.backup_manager.create_backup("export")
        
        # Encrypt backup with additional layer
        with open(backup, "rb") as f:
            data = f.read()
        
        encrypted, metadata = self.state_manager.encrypt_data(data)
        
        # Save to USB drive / physical media
        with open(output_path / "data.enc", "wb") as f:
            f.write(encrypted)
        
        with open(output_path / "data.meta", "w") as f:
            json.dump(metadata, f)
    
    def import_from_transfer(self, input_path: Path):
        """Import encrypted data bundle from physical transfer."""
        # Load encrypted bundle
        with open(input_path / "data.enc", "rb") as f:
            encrypted = f.read()
        
        with open(input_path / "data.meta") as f:
            metadata = json.load(f)
        
        # Decrypt
        decrypted = self.state_manager.decrypt_data(encrypted, metadata)
        
        # Extract and restore
        temp_backup = Path("temp_import_backup.tar.gz")
        temp_backup.write_bytes(decrypted)
        
        self.backup_manager.restore_backup(temp_backup)
        temp_backup.unlink()
```

---

## Security Best Practices

### 1. Key Storage

```python
# DO: Use secure key storage
key_file = Path(".keys/master.key")
key_file.chmod(0o600)  # Owner read/write only

# DON'T: Store keys in version control
# .gitignore should include:
.keys/
*.key
```

---

### 2. Key Rotation Schedule

```python
# Automatic rotation every 90 days
manager = EncryptedStateManager(key_rotation_days=90)

# Check and rotate if needed
def check_and_rotate():
    if manager.should_rotate_key():
        manager.rotate_key()
        audit.record_event(
            "key_rotation",
            "system",
            "rotate_encryption_key",
            {"reason": "scheduled_rotation"}
        )

# Schedule daily check
schedule.every().day.at("03:00").do(check_and_rotate)
```

---

### 3. Zero-Knowledge Architecture

```python
class ZeroKnowledgeStateManager(EncryptedStateManager):
    """State manager with client-side encryption."""
    
    def save_encrypted_state(
        self,
        state_id: str,
        state_data: dict[str, Any],
        user_passphrase: str
    ) -> bool:
        """Encrypt with user's passphrase (server never sees plaintext)."""
        # Derive key from passphrase
        salt = os.urandom(32)
        key = self._derive_key_from_passphrase(user_passphrase, salt)
        
        # Encrypt data
        cipher = Fernet(base64.urlsafe_b64encode(key))
        data_json = json.dumps(state_data)
        encrypted = cipher.encrypt(data_json.encode())
        
        # Save with salt
        self._save_to_file(state_id, {
            "salt": base64.b64encode(salt).decode(),
            "data": base64.b64encode(encrypted).decode()
        })
        
        return True
```

---

## Performance Optimization

### 1. Lazy Loading

```python
class LazyLoadedStateManager:
    def __init__(self):
        self._cache = {}
        self.state_manager = EncryptedStateManager()
    
    def get_state(self, state_id: str) -> dict:
        """Load state with caching."""
        if state_id not in self._cache:
            self._cache[state_id] = self.state_manager.load_encrypted_state(state_id)
        return self._cache[state_id]
    
    def invalidate_cache(self, state_id: str = None):
        """Invalidate cache for state_id or all states."""
        if state_id:
            self._cache.pop(state_id, None)
        else:
            self._cache.clear()
```

---

### 2. Batch Operations

```python
def save_multiple_states(states: dict[str, dict]) -> bool:
    """Save multiple states in batch."""
    manager = EncryptedStateManager()
    
    for state_id, state_data in states.items():
        manager.save_encrypted_state(state_id, state_data)
    
    return True
```

---

## Related Documentation

- **Storage Engine**: `source-docs/utilities/003-storage-engine.md`
- **Telemetry Manager**: `source-docs/utilities/004-telemetry-manager.md`
- **Security Resources**: `source-docs/core/security-resources.md`

---

**Last Updated**: 2025-01-24  
**Status**: Stable - Production Ready  
**Maintainer**: Security & Infrastructure Team
