# Data Persistence Error Handling Documentation

**Component**: Data Layer Error Recovery  
**Last Updated**: 2025-01-23  
**Maintainer**: Error Handling Documentation Specialist  

---

## Overview

Data persistence errors fall into three categories: **transient** (retry-able), **permanent** (fail-fast), and **corruption** (recovery required). This document covers error handling for file I/O, database operations, encryption failures, and data migration.

---

## Core Data Persistence Components

### EncryptedStateManager

**Module**: `src/app/core/data_persistence.py`  
**Lines**: 75-100  
**Purpose**: Encrypted state management with error recovery

```python
class EncryptedStateManager:
    """
    Encrypted State Management System
    
    Provides transparent encryption/decryption of sensitive state data with
    support for multiple encryption algorithms and key rotation.
    """
    
    def __init__(
        self,
        data_dir: str = "data",
        algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM,
        master_key: bytes | None = None,
        key_rotation_days: int = 90,
    ):
        """Initialize encrypted state manager."""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.algorithm = algorithm
        self.key_rotation_days = key_rotation_days
        
        # Initialize encryption
        self._setup_encryption(master_key)
        
        # Thread safety
        self._lock = threading.Lock()
```

**Supported Algorithms**:
- `AES-256-GCM` (default, authenticated encryption)
- `ChaCha20-Poly1305` (high-performance, authenticated)
- `Fernet` (symmetric encryption, key derivation)

---

## Error Categories and Strategies

### Category 1: Transient Errors (Retry-able)

**Examples**:
- File locked by another process
- Network drive temporarily unavailable
- Disk I/O timeout
- Database connection pool exhausted

**Strategy**: Exponential backoff retry with max attempts

```python
import time
import logging
from typing import Callable, TypeVar, Any

logger = logging.getLogger(__name__)

T = TypeVar('T')

class TransientError(Exception):
    """Raised for transient errors that should be retried."""
    pass

def retry_on_transient_error(
    func: Callable[..., T],
    max_attempts: int = 3,
    base_delay: float = 0.5,
    backoff_multiplier: float = 2.0,
    max_delay: float = 10.0,
    transient_exceptions: tuple = (IOError, OSError, PermissionError),
) -> T:
    """Retry function on transient errors with exponential backoff."""
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except transient_exceptions as e:
            last_exception = e
            
            if attempt == max_attempts - 1:
                logger.error(
                    "Max retry attempts (%d) reached: %s",
                    max_attempts, e
                )
                raise TransientError(f"Operation failed after {max_attempts} attempts") from e
            
            delay = min(base_delay * (backoff_multiplier ** attempt), max_delay)
            logger.warning(
                "Transient error on attempt %d/%d: %s. Retrying in %.2fs",
                attempt + 1, max_attempts, e, delay
            )
            time.sleep(delay)
    
    # Should never reach here, but for type safety
    raise TransientError("Unexpected retry loop exit") from last_exception
```

**Usage Example**:
```python
def save_user_data(user_id: str, data: dict):
    """Save user data with retry on transient errors."""
    def _save():
        with open(f"data/users/{user_id}.json", "w") as f:
            json.dump(data, f)
    
    try:
        retry_on_transient_error(_save, max_attempts=3)
        logger.info("User data saved: %s", user_id)
    except TransientError as e:
        logger.error("Failed to save user data: %s", e)
        raise PersistenceError(f"Could not save data for user {user_id}")
```

---

### Category 2: Permanent Errors (Fail-Fast)

**Examples**:
- Disk full
- Invalid file path
- Corrupted data file (unrecoverable)
- Permission denied (insufficient privileges)

**Strategy**: Fail immediately, log error, notify user

```python
class PermanentPersistenceError(Exception):
    """Raised for permanent errors that should not be retried."""
    pass

def load_config_file(config_path: str) -> dict:
    """Load configuration file with fail-fast on permanent errors."""
    try:
        if not os.path.exists(config_path):
            logger.error("Config file not found: %s", config_path)
            raise PermanentPersistenceError(
                f"Configuration file not found: {config_path}"
            )
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return config
    
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in config file: %s", e)
        raise PermanentPersistenceError(
            f"Configuration file corrupted: {config_path}"
        ) from e
    
    except PermissionError as e:
        logger.error("Permission denied for config file: %s", e)
        raise PermanentPersistenceError(
            f"Insufficient permissions to read config: {config_path}"
        ) from e
```

---

### Category 3: Corruption Errors (Recovery Required)

**Examples**:
- Incomplete write (power failure)
- File truncation
- Invalid encryption header
- Schema mismatch

**Strategy**: Attempt recovery from backup, fallback to defaults

```python
def load_state_with_recovery(state_file: str, backup_file: str) -> dict:
    """Load state with automatic recovery from backup."""
    # Try loading primary state file
    try:
        with open(state_file, 'r') as f:
            state = json.load(f)
        logger.info("State loaded from primary file")
        return state
    
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning("Primary state file corrupted: %s", e)
        
        # Attempt recovery from backup
        if os.path.exists(backup_file):
            try:
                with open(backup_file, 'r') as f:
                    state = json.load(f)
                logger.info("State recovered from backup")
                
                # Restore primary from backup
                shutil.copy(backup_file, state_file)
                logger.info("Primary state file restored from backup")
                
                return state
            
            except Exception as backup_error:
                logger.error("Backup recovery failed: %s", backup_error)
        
        # Both primary and backup failed - use defaults
        logger.warning("Using default state (all recovery attempts failed)")
        return get_default_state()
```

---

## File Operations with Error Handling

### Atomic Write Pattern

**Problem**: Crash during write leaves partial/corrupted file  
**Solution**: Write to temp file, then atomic rename

```python
import os
import tempfile
import json
from pathlib import Path

def atomic_write_json(filepath: str, data: dict) -> None:
    """Write JSON data atomically to prevent corruption."""
    filepath = Path(filepath)
    
    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to temporary file in same directory
    with tempfile.NamedTemporaryFile(
        mode='w',
        dir=filepath.parent,
        delete=False,
        suffix='.tmp'
    ) as tmp_file:
        tmp_path = tmp_file.name
        json.dump(data, tmp_file, indent=2)
    
    try:
        # Atomic rename (overwrites existing file)
        os.replace(tmp_path, filepath)
        logger.debug("Atomic write completed: %s", filepath)
    except Exception as e:
        # Cleanup temp file on failure
        try:
            os.unlink(tmp_path)
        except:
            pass
        logger.error("Atomic write failed: %s", e)
        raise
```

**Usage in AI Systems**:
```python
def _save_state(self):
    """Save AI persona state with atomic write."""
    state = {
        "traits": self.traits,
        "mood": self.mood,
        "interaction_count": self.interaction_count,
        "last_updated": datetime.now().isoformat(),
    }
    
    state_file = os.path.join(self.data_dir, "ai_persona", "state.json")
    
    try:
        atomic_write_json(state_file, state)
        logger.debug("AI persona state saved")
    except Exception as e:
        logger.error("Failed to save AI persona state: %s", e)
        # Non-critical: state will be rebuilt from interactions
```

---

### Backup Before Modify Pattern

```python
def modify_with_backup(
    filepath: str,
    modifier: Callable[[dict], dict]
) -> dict:
    """Modify file contents with automatic backup."""
    filepath = Path(filepath)
    backup_path = filepath.with_suffix(filepath.suffix + '.backup')
    
    # Create backup of existing file
    if filepath.exists():
        try:
            shutil.copy(filepath, backup_path)
            logger.debug("Backup created: %s", backup_path)
        except Exception as e:
            logger.error("Backup creation failed: %s", e)
            raise PersistenceError("Cannot create backup before modification")
    
    # Load existing data
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    
    # Apply modification
    try:
        modified_data = modifier(data)
        atomic_write_json(str(filepath), modified_data)
        logger.info("File modified successfully: %s", filepath)
        return modified_data
    
    except Exception as e:
        logger.error("Modification failed: %s", e)
        
        # Restore from backup
        if backup_path.exists():
            shutil.copy(backup_path, filepath)
            logger.info("Restored from backup after modification failure")
        
        raise PersistenceError("File modification failed") from e
    
    finally:
        # Cleanup old backups (keep only latest)
        try:
            if backup_path.exists():
                os.unlink(backup_path)
        except:
            pass
```

---

## Encryption Error Handling

### Encryption Failures

```python
from cryptography.fernet import Fernet, InvalidToken

class EncryptionError(Exception):
    """Raised when encryption/decryption fails."""
    pass

def encrypt_data(data: bytes, cipher_suite: Fernet) -> bytes:
    """Encrypt data with error handling."""
    try:
        encrypted = cipher_suite.encrypt(data)
        return encrypted
    except Exception as e:
        logger.error("Encryption failed: %s", e)
        raise EncryptionError("Failed to encrypt data") from e

def decrypt_data(encrypted_data: bytes, cipher_suite: Fernet) -> bytes:
    """Decrypt data with error handling."""
    try:
        decrypted = cipher_suite.decrypt(encrypted_data)
        return decrypted
    
    except InvalidToken as e:
        logger.error("Decryption failed: invalid token or corrupted data")
        raise EncryptionError(
            "Decryption failed: data may be corrupted or key is incorrect"
        ) from e
    
    except Exception as e:
        logger.error("Decryption failed: %s", e)
        raise EncryptionError("Failed to decrypt data") from e
```

---

### Key Rotation Error Handling

```python
def rotate_encryption_key(
    old_cipher: Fernet,
    new_cipher: Fernet,
    data_files: list[str]
) -> dict[str, bool]:
    """Rotate encryption key across multiple files."""
    results = {}
    failed_files = []
    
    for filepath in data_files:
        try:
            # Read and decrypt with old key
            with open(filepath, 'rb') as f:
                encrypted_data = f.read()
            decrypted_data = old_cipher.decrypt(encrypted_data)
            
            # Re-encrypt with new key
            new_encrypted_data = new_cipher.encrypt(decrypted_data)
            
            # Atomic write
            with tempfile.NamedTemporaryFile(
                dir=os.path.dirname(filepath),
                delete=False
            ) as tmp_file:
                tmp_file.write(new_encrypted_data)
                tmp_path = tmp_file.name
            
            os.replace(tmp_path, filepath)
            
            results[filepath] = True
            logger.info("Key rotation successful: %s", filepath)
        
        except Exception as e:
            results[filepath] = False
            failed_files.append(filepath)
            logger.error("Key rotation failed for %s: %s", filepath, e)
    
    if failed_files:
        raise EncryptionError(
            f"Key rotation failed for {len(failed_files)} files: {failed_files}"
        )
    
    return results
```

---

## Database Error Handling

### SQLite Specific Errors

```python
import sqlite3

class DatabaseError(Exception):
    """Base class for database errors."""
    pass

class DatabaseConnectionError(DatabaseError):
    """Database connection failed."""
    pass

class DatabaseLockError(DatabaseError):
    """Database is locked by another process."""
    pass

def execute_with_retry(
    db_path: str,
    query: str,
    params: tuple = (),
    max_attempts: int = 3
) -> list:
    """Execute SQLite query with retry on lock errors."""
    for attempt in range(max_attempts):
        try:
            with sqlite3.connect(db_path, timeout=10.0) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.fetchall()
        
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                if attempt < max_attempts - 1:
                    delay = 0.5 * (2 ** attempt)
                    logger.warning(
                        "Database locked, retry %d/%d in %.1fs",
                        attempt + 1, max_attempts, delay
                    )
                    time.sleep(delay)
                else:
                    logger.error("Database locked after %d attempts", max_attempts)
                    raise DatabaseLockError(
                        f"Database locked: {db_path}"
                    ) from e
            else:
                logger.error("Database error: %s", e)
                raise DatabaseError(f"Database operation failed") from e
        
        except sqlite3.DatabaseError as e:
            logger.error("Database corrupted: %s", e)
            raise DatabaseError(f"Database corrupted: {db_path}") from e
```

---

## Data Migration Error Handling

### Version Migration Pattern

```python
from dataclasses import dataclass

@dataclass
class DataVersion:
    """Version information for data migration."""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    @classmethod
    def from_string(cls, version_str: str) -> "DataVersion":
        """Parse version string like '1.0.0'."""
        parts = version_str.split(".")
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))

class MigrationError(Exception):
    """Raised when data migration fails."""
    pass

def migrate_data(
    data: dict,
    from_version: DataVersion,
    to_version: DataVersion
) -> dict:
    """Migrate data between versions with error handling."""
    current_version = from_version
    
    # Create backup before migration
    backup_data = json.dumps(data)
    
    try:
        # Apply migrations sequentially
        while current_version < to_version:
            next_version = get_next_version(current_version)
            migrator = get_migrator(current_version, next_version)
            
            logger.info(
                "Migrating data: %s -> %s",
                current_version, next_version
            )
            
            data = migrator(data)
            current_version = next_version
        
        logger.info("Data migration completed: %s", to_version)
        return data
    
    except Exception as e:
        logger.error("Data migration failed: %s", e)
        
        # Restore from backup
        try:
            restored_data = json.loads(backup_data)
            logger.info("Data restored from backup after migration failure")
            return restored_data
        except:
            logger.critical("Backup restoration failed!")
            raise MigrationError(
                f"Migration failed and backup restoration failed"
            ) from e
```

---

## UserManager Error Patterns

### Password Migration

**Module**: `src/app/core/user_manager.py`  
**Lines**: 92-107  

```python
def _migrate_plaintext_passwords(self):
    """Migrate plaintext passwords to hashed versions."""
    migrated = False
    for uname, udata in self.users.items():
        if (
            isinstance(udata, dict)
            and "password" in udata
            and "password_hash" not in udata
        ):
            try:
                # Hash the plaintext password
                plaintext = udata["password"]
                udata["password_hash"] = pwd_context.hash(plaintext)
                del udata["password"]
                migrated = True
                logger.info("Migrated password for user: %s", uname)
            except Exception as e:
                logger.error(
                    "Failed to migrate password for %s: %s",
                    uname, e
                )
                # Skip this user, continue with others
    
    if migrated:
        self.save_users()
        logger.info("Password migration completed")
```

**Key Points**:
- Fail gracefully per-user (don't abort entire migration)
- Log each migration attempt
- Save after successful migration
- Skip users with migration errors

---

### Configuration Loading with Fallback

```python
def _setup_cipher(self):
    """Setup Fernet cipher from environment or generate new key."""
    env_key = os.getenv("FERNET_KEY")
    if env_key:
        try:
            key = env_key.encode()
            self.cipher_suite = Fernet(key)
            logger.info("Cipher initialized from environment")
        except Exception as e:
            logger.warning(
                "Invalid FERNET_KEY in environment: %s. "
                "Using runtime-generated key.",
                e
            )
            self.cipher_suite = Fernet(Fernet.generate_key())
    else:
        logger.info("No FERNET_KEY found, using runtime-generated key")
        self.cipher_suite = Fernet(Fernet.generate_key())
```

**Strategy**: Graceful degradation with logging
- Try environment variable first
- Fall back to runtime key generation
- Log decision for audit trail

---

## Command Override System Persistence

### Audit Log Error Handling

**Module**: `src/app/core/command_override.py`  
**Lines**: 107-131  

```python
def _init_audit_log(self) -> None:
    """Initialize the audit log file."""
    try:
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.audit_log):
            with open(self.audit_log, "w", encoding="utf-8") as f:
                f.write("=== Command Override System Audit Log ===\n")
                f.write(f"Initialized: {datetime.now().isoformat()}\n\n")
    except Exception as e:
        print(f"Error initializing audit log: {e}")
        # Continue operation (audit log is non-critical for startup)

def _log_action(self, action: str, details: str = "", success: bool = True) -> None:
    """Log an action to the audit log."""
    try:
        timestamp = datetime.now().isoformat()
        status = "SUCCESS" if success else "FAILED"
        log_entry = f"[{timestamp}] {status}: {action}"
        if details:
            log_entry += f" | Details: {details}"
        log_entry += "\n"
        
        with open(self.audit_log, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error writing to audit log: {e}")
        # Continue operation (logging failure shouldn't block action)
```

**Strategy**: Non-blocking audit
- Audit failures don't block operations
- Print to stderr (visible but non-fatal)
- Continue execution after audit error

---

## Testing Data Persistence Errors

### Test Structure

```python
import pytest
import tempfile
import os

@pytest.fixture
def temp_data_dir():
    """Create temporary data directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

def test_atomic_write_prevents_corruption(temp_data_dir):
    """Test that atomic write prevents partial writes."""
    filepath = os.path.join(temp_data_dir, "test.json")
    data = {"key": "value"}
    
    # Simulate crash during write by mocking os.replace
    with patch('os.replace', side_effect=IOError("Simulated crash")):
        with pytest.raises(IOError):
            atomic_write_json(filepath, data)
    
    # Original file should not exist (or be unchanged if it did)
    assert not os.path.exists(filepath)

def test_transient_error_retry(temp_data_dir):
    """Test retry mechanism for transient errors."""
    filepath = os.path.join(temp_data_dir, "test.json")
    
    call_count = 0
    def flaky_write():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise IOError("Transient error")
        with open(filepath, 'w') as f:
            json.dump({"success": True}, f)
    
    retry_on_transient_error(flaky_write, max_attempts=5)
    
    # Should have retried 3 times
    assert call_count == 3
    
    # File should be written successfully
    assert os.path.exists(filepath)
```

---

## Best Practices

### ✅ Always Create Parent Directories

```python
# Before any file write
os.makedirs(os.path.dirname(filepath), exist_ok=True)
```

### ✅ Use Atomic Writes for Critical Data

```python
# Critical: user data, state, config
atomic_write_json(filepath, data)

# Non-critical: logs, temp files
with open(filepath, 'w') as f:
    json.dump(data, f)
```

### ✅ Log All Persistence Errors

```python
try:
    save_data(data)
except Exception as e:
    logger.error("Data persistence failed: %s", e, exc_info=True)
    # Handle or re-raise
```

### ✅ Validate Data After Load

```python
data = load_json(filepath)
if not validate_schema(data):
    logger.error("Loaded data failed schema validation")
    raise DataCorruptionError("Invalid data schema")
```

---

## References

- **Data Persistence**: `src/app/core/data_persistence.py`
- **User Manager**: `src/app/core/user_manager.py`
- **AI Systems State**: `src/app/core/ai_systems.py` - `_save_state()` methods
- **Command Override**: `src/app/core/command_override.py` - Audit logging

---

**Next Steps**:
1. Implement automated backup system with rotation
2. Add data corruption detection checksums
3. Create data recovery CLI tool
4. Document disaster recovery procedures
