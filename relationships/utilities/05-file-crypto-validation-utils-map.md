---
description: File I/O, Cryptography, and Validation utility relationships
audience: developers
priority: P1
category: utilities
tags: [file-utils, crypto-utils, validation, security]
dependencies: [shared-utilities]
related_systems: [encryption, storage]
last_updated: 2026-04-20
---

# File, Crypto & Validation Utils Relationship Map

## File Utilities

### 1. **JSON File Operations** (e2e/utils/test_helpers.py)

#### Core Functions:
```python
def load_json_file(file_path: Path) -> dict | list:
    """
    Load and parse a JSON file.
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If invalid JSON
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path) as f:
        return json.load(f)

def save_json_file(
    data: dict | list,
    file_path: Path,
    indent: int = 2
) -> None:
    """
    Save data to JSON file with automatic directory creation.
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "w") as f:
        json.dump(data, f, indent=indent)
```

**Safety Features**:
- ✅ Automatic directory creation
- ✅ Explicit error handling
- ✅ Pretty-printed JSON (indent=2)

**Reuse Pattern**: This pattern is replicated in `src/app/core/data_persistence.py` for production use

---

### 2. **Test File Management** (e2e/utils/test_helpers.py)

#### Functions:
```python
def create_test_file(
    directory: Path,
    filename: str,
    content: str
) -> Path:
    """Create a test file with content."""
    directory.mkdir(parents=True, exist_ok=True)
    file_path = directory / filename
    
    with open(file_path, "w") as f:
        f.write(content)
    
    return file_path

def cleanup_test_files(*file_paths: Path) -> None:
    """
    Clean up test files and directories.
    
    Handles both files and directories.
    """
    for file_path in file_paths:
        if file_path.exists():
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                import shutil
                shutil.rmtree(file_path)
```

**Usage in Tests**:
```python
# Create test files
test_file = create_test_file(
    Path("test_data"),
    "config.json",
    '{"mode": "test"}'
)

# Run tests
result = test_function(test_file)

# Cleanup
cleanup_test_files(test_file, Path("test_data"))
```

---

### 3. **Path Security** (utils/validators.py)

#### Validation:
```python
def validate_target(target: str) -> bool:
    """
    Validate target path for security.
    
    Checks:
    1. Not empty
    2. Starts with / (absolute path)
    3. No path traversal (..)
    """
    if not target:
        raise ValidationError("Target cannot be empty")
    
    if not target.startswith("/"):
        raise ValidationError("Target must start with /")
    
    if ".." in target:
        raise ValidationError("Path traversal not allowed")
    
    return True
```

**Security**: Prevents directory traversal attacks (`../../../etc/passwd`)

**Consumers**:
- `src/app/security/path_security.py` - Path validation
- `src/app/governance/` - Resource access validation

---

## Cryptography Utilities

### 1. **Hashing** (utils/helpers.py)

#### SHA-256 Hash:
```python
def hash_data(data: dict[str, Any]) -> str:
    """
    Create cryptographic hash of data.
    
    Process:
    1. Serialize to JSON (sorted keys for determinism)
    2. SHA-256 hash
    3. Return hex digest
    """
    serialized = json.dumps(data, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()
```

**Deterministic**: `sort_keys=True` ensures same hash for same data

**Usage**:
```python
from utils.helpers import hash_data

# Hash configuration
config_hash = hash_data({"mode": "prod", "level": 5})
# Always returns same hash for same config

# Detect changes
old_hash = hash_data(old_config)
new_hash = hash_data(new_config)
if old_hash != new_hash:
    logger.info("Configuration changed")
```

**Consumers**: 25+ modules (integrity, caching, change detection)

---

### 2. **Password Hashing** (src/app/core/security/auth.py)

#### Bcrypt:
```python
import bcrypt

def hash_password(password: str) -> str:
    """
    Hash password with bcrypt (salt + cost factor).
    
    Returns:
        Bcrypt hash string (includes salt)
    """
    salt = bcrypt.gensalt(rounds=12)  # Cost factor 12
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

**Security Features**:
- Salt: Prevents rainbow table attacks
- Cost factor 12: Computational cost (2^12 iterations)
- Timing-safe comparison

**Consumers**:
- `src/app/core/user_manager.py::UserManager` - User authentication
- `src/app/core/hydra_50_security.py` - Security system

---

### 3. **GOD TIER Encryption** (utils/encryption/god_tier_encryption.py)

#### 7-Layer Encryption:
```python
class GodTierEncryption:
    """
    Military-grade, quantum-resistant encryption.
    
    Layers:
    1. SHA-512 integrity hash
    2. Fernet (AES-128)
    3. AES-256-GCM
    4. ChaCha20-Poly1305
    5. AES-256-GCM (rotated key)
    6. Quantum-resistant padding
    7. HMAC-SHA512 authentication
    """
    
    def encrypt_god_tier(self, data: bytes) -> bytes:
        """7-layer encryption."""
        # See detailed implementation in shared-utilities-map.md
    
    def decrypt_god_tier(self, encrypted: bytes) -> bytes:
        """7-layer decryption with integrity checks."""
```

**Use Cases**:
- Master passwords
- Encryption keys
- Long-term archived secrets

**Performance**: ~50-100ms per operation (acceptable for secrets, not streaming)

---

### 4. **Fernet Encryption** (utils/storage/privacy_vault.py)

#### Simpler Encryption:
```python
from cryptography.fernet import Fernet

class PrivacyVault:
    def __init__(self):
        self._cipher = Fernet(Fernet.generate_key())
    
    def store(self, key: str, value: str):
        """Encrypt and store."""
        encrypted = self._cipher.encrypt(value.encode())
        self._vault[key] = encrypted
    
    def retrieve(self, key: str) -> str:
        """Decrypt and retrieve."""
        encrypted = self._vault[key]
        return self._cipher.decrypt(encrypted).decode()
```

**Use Cases**:
- API keys
- Session tokens
- General secrets

**Performance**: ~1-5ms per operation (suitable for frequent operations)

---

### 5. **Location Encryption** (src/app/core/location_tracker.py)

#### Specialized Encryption:
```python
class LocationTracker:
    def encrypt_location(self, location_data):
        """Encrypt GPS coordinates with Fernet."""
        json_data = json.dumps(location_data)
        return self.cipher.encrypt(json_data.encode())
    
    def decrypt_location(self, encrypted_data):
        """Decrypt GPS coordinates."""
        decrypted = self.cipher.decrypt(encrypted_data)
        return json.loads(decrypted.decode())
```

**Privacy**: GPS history encrypted at rest

---

## Validation Utilities

### 1. **Actor Validation** (utils/validators.py)

```python
def validate_actor(actor: str) -> bool:
    """
    Validate actor type.
    
    Valid actors: human, agent, system
    """
    valid_actors = ["human", "agent", "system"]
    if actor not in valid_actors:
        raise ValidationError(f"Invalid actor: {actor}")
    return True
```

**Domain**: Audit trail actor validation

---

### 2. **Action Validation** (utils/validators.py)

```python
def validate_action(action: str) -> bool:
    """
    Validate action type.
    
    Valid actions: read, write, execute, mutate
    """
    valid_actions = ["read", "write", "execute", "mutate"]
    if action not in valid_actions:
        raise ValidationError(f"Invalid action: {action}")
    return True
```

**Domain**: Governance action validation

---

### 3. **Input Validation** (src/app/gui/dashboard_utils.py)

#### GUI Validators:
```python
@staticmethod
def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format."""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if not username.isalnum():
        return False, "Username must be alphanumeric"
    return True, ""

@staticmethod
def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format."""
    if "@" not in email or "." not in email:
        return False, "Invalid email format"
    return True, ""

@staticmethod
def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    return True, ""
```

**Pattern**: Tuple return `(bool, str)` for user feedback

**Consumers**: All GUI modules with user input

---

### 4. **Intent Validation** (utils/validators.py)

```python
def validate_intent(intent: dict[str, Any]) -> bool:
    """
    Validate complete intent structure.
    
    Required fields:
    - actor
    - action
    - target
    - origin
    """
    required_fields = ["actor", "action", "target", "origin"]
    
    for field in required_fields:
        if field not in intent:
            raise ValidationError(f"Missing required field: {field}")
    
    validate_actor(intent["actor"])
    validate_action(intent["action"])
    validate_target(intent["target"])
    
    return True
```

**Composite Validation**: Orchestrates multiple validators

**Consumers**: `src/app/governance/` modules

---

## Utility Relationships

```
┌─────────────────────────────────────────────────────────────┐
│ File, Crypto & Validation Utils Ecosystem                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  File Utils                                                 │
│    ├── load_json_file() ─────────→ config/state loading    │
│    ├── save_json_file() ─────────→ config/state saving     │
│    ├── create_test_file() ───────→ test fixtures           │
│    └── cleanup_test_files() ─────→ test cleanup            │
│                                                              │
│  Crypto Utils                                               │
│    ├── hash_data() ──────────────→ integrity checks        │
│    ├── hash_password() ──────────→ user authentication     │
│    ├── GodTierEncryption ────────→ critical secrets        │
│    ├── Fernet (vault) ───────────→ general encryption      │
│    └── Location encryption ──────→ privacy (GPS)           │
│                                                              │
│  Validation Utils                                           │
│    ├── validate_actor() ─────────→ audit trails            │
│    ├── validate_action() ────────→ governance              │
│    ├── validate_target() ────────→ path security           │
│    ├── validate_intent() ────────→ composite validation    │
│    ├── validate_username() ──────→ GUI user input          │
│    ├── validate_email() ─────────→ GUI user input          │
│    └── validate_password() ──────→ GUI user input          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Patterns

### Pattern 1: **Load → Validate → Use**
```python
from e2e.utils.test_helpers import load_json_file
from utils.validators import validate_intent

# Load config
config = load_json_file(Path("config.json"))

# Validate
validate_intent(config["intent"])

# Use
process_intent(config["intent"])
```

### Pattern 2: **Hash → Compare**
```python
from utils.helpers import hash_data

# Hash old state
old_hash = hash_data(old_state)

# Modify state
new_state = modify(old_state)

# Detect changes
new_hash = hash_data(new_state)
if old_hash != new_hash:
    logger.info("State changed")
    save_state(new_state)
```

### Pattern 3: **Encrypt → Store → Retrieve → Decrypt**
```python
from utils.storage.privacy_vault import PrivacyVault

vault = PrivacyVault(config)
vault.start(encryption_key)

# Encrypt + store
vault.store("api_key", "sk-secret123")

# Retrieve + decrypt
api_key = vault.retrieve("api_key")
```

---

## Security Best Practices

### SP1: **Never Store Plaintext Passwords**
```python
# ✅ CORRECT
from app.core.security.auth import hash_password
hashed = hash_password(user_password)
save_user(username, hashed)

# ❌ WRONG
save_user(username, user_password)  # Plaintext!
```

### SP2: **Always Validate Paths**
```python
# ✅ CORRECT
from utils.validators import validate_target
validate_target(user_path)  # Raises on ".."
safe_read(user_path)

# ❌ WRONG
with open(user_path) as f:  # Path traversal risk
    data = f.read()
```

### SP3: **Use Appropriate Encryption**
```python
# ✅ Critical secrets (slow, max security)
encrypted = GodTierEncryption().encrypt_god_tier(master_key)

# ✅ General secrets (fast, good security)
vault.store("api_key", key)  # Fernet

# ❌ No encryption
with open("secrets.json", "w") as f:
    json.dump({"password": pw}, f)  # Plaintext!
```

---

## Related Documentation
- [Shared Utilities Map](./03-shared-utilities-map.md)
- [Helper Functions Map](./01-helper-functions-map.md)
- [Common Patterns Map](./02-common-patterns-map.md)
