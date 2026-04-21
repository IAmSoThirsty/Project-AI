---
description: Shared utility modules and cross-cutting concerns in Project-AI
audience: developers
priority: P1
category: utilities
tags: [utilities, shared-modules, cross-cutting, reuse]
dependencies: [helper-functions, common-patterns]
related_systems: [encryption-utils, storage-utils, logger]
last_updated: 2026-04-20
---

# Shared Utilities Relationship Map

## Overview

This map documents shared utility modules that provide cross-cutting functionality across the Project-AI codebase, including encryption, storage, logging, and validation.

## Core Shared Modules

### 1. **utils/logger.py** - Logging Configuration

**Purpose**: Centralized logging setup with file and console handlers

**Implementation**:
```python
def setup_logger(
    name: str,
    level: str = "INFO",
    log_file: str = None
) -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Features:
    - Console handler (stdout)
    - Optional file handler
    - Standardized format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    - Automatic directory creation for log files
    """
```

**Default Logger**: `default_logger = setup_logger("project_ai")`

**Usage Pattern**:
```python
from utils.logger import setup_logger

logger = setup_logger(
    "my_module",
    level="DEBUG",
    log_file="logs/my_module.log"
)

logger.info("Module initialized")
logger.error("Operation failed: %s", error)
```

**Consumers**:
- `src/app/` modules → Use default logger or create custom
- `tests/` → Test-specific loggers with file output
- All new modules → Standard logging interface

**Features**:
- ✅ Automatic log directory creation (`Path.mkdir(parents=True)`)
- ✅ Dual output (console + file)
- ✅ ISO timestamp format
- ✅ Exception traceback support (`exc_info=True`)

---

### 2. **utils/validators.py** - Data Validation

**Purpose**: Domain-specific validation functions with security focus

**Core Validators**:
```python
- validate_actor(actor: str) -> bool           # human|agent|system
- validate_action(action: str) -> bool         # read|write|execute|mutate
- validate_target(target: str) -> bool         # Path validation + traversal check
- validate_verdict(verdict: str) -> bool       # allow|deny|degrade
- validate_intent(intent: dict) -> bool        # Complete intent validation
- sanitize_string(value: str, max_length: int = 1000) -> str
```

**ValidationError**: Custom exception for validation failures

**Security Features**:
```python
def validate_target(target: str) -> bool:
    """
    Security-focused path validation.
    
    Checks:
    - Not empty
    - Starts with /
    - No path traversal (..)
    """
    if not target:
        raise ValidationError("Target cannot be empty")
    
    if not target.startswith("/"):
        raise ValidationError("Target must start with /")
    
    if ".." in target:
        raise ValidationError("Path traversal not allowed")
    
    return True
```

**Usage Pattern**:
```python
from utils.validators import validate_intent, ValidationError

try:
    validate_intent({
        "actor": "human",
        "action": "read",
        "target": "/data/file.txt",
        "origin": "user-request"
    })
except ValidationError as e:
    logger.error("Invalid intent: %s", e)
```

**Consumers**:
- `src/app/audit/` → Audit event validation
- `src/app/governance/` → Intent validation
- `src/security/` → Security checks
- 15+ modules requiring domain validation

---

### 3. **utils/helpers.py** - Core Utilities

**Functions** (covered in detail in [01-helper-functions-map.md](./01-helper-functions-map.md)):
- `hash_data()` - SHA-256 hashing
- `get_timestamp()` - Unix timestamp
- `format_timestamp()` - ISO 8601 formatting
- `truncate_hash()` - Hash truncation
- `safe_get()` - Safe dictionary access

**Universal Usage**: 25+ modules depend on these utilities

---

### 4. **utils/storage/** - Storage Abstractions

#### 4.1 **ephemeral_storage.py** - In-Memory Storage

**Class**: `EphemeralStorage`

**Purpose**: Temporary, auto-wiping storage for sensitive data

**Features**:
```python
class EphemeralStorage:
    """
    Memory-only storage with TTL support.
    - Never writes to disk
    - Auto-wipes on shutdown
    - TTL expiration
    - Cleanup of expired items
    """
    
    Methods:
    - start() / stop()                          # Lifecycle
    - store(key, value, ttl=None)              # Store with TTL
    - retrieve(key) -> Any | None              # Get data
    - delete(key)                               # Explicit delete
    - cleanup_expired()                         # Remove expired
    - get_statistics() -> dict                  # Stats
```

**Usage Pattern**:
```python
from utils.storage.ephemeral_storage import EphemeralStorage

storage = EphemeralStorage({
    "ephemeral_mode": True,
    "memory_only": True,
    "auto_wipe_interval": 300  # 5 minutes
})

storage.start()
storage.store("session_token", token, ttl=3600)  # 1 hour TTL
token = storage.retrieve("session_token")
storage.stop()  # Auto-wipes all data
```

**Use Cases**:
- Session tokens (web interface)
- Temporary API keys
- Cache with TTL
- Sensitive computation results

**Consumers**:
- `src/app/interfaces/web/` → Session management
- `src/app/security/` → Temporary credentials
- Test fixtures → Isolated test data

---

#### 4.2 **privacy_vault.py** - Encrypted Vault

**Class**: `PrivacyVault`

**Purpose**: Encrypted storage with forensic resistance

**Features**:
```python
class PrivacyVault:
    """
    Encrypted vault using Fernet.
    - All data encrypted at rest
    - Secure wipe (3-pass overwrite)
    - Forensic resistance
    """
    
    Methods:
    - start(encryption_key: bytes = None)      # Init vault
    - stop()                                    # Secure wipe
    - store(key, value)                         # Encrypt & store
    - retrieve(key) -> str | None              # Decrypt & retrieve
    - delete(key)                               # Secure delete
    - list_keys() -> list                       # List vault keys
```

**Encryption**:
- Algorithm: Fernet (AES-128 + HMAC-SHA256)
- Key generation: `Fernet.generate_key()`
- Forensic resistance: 3-pass random overwrite before deletion

**Usage Pattern**:
```python
from utils.storage.privacy_vault import PrivacyVault
from cryptography.fernet import Fernet

vault = PrivacyVault({
    "privacy_vault_enabled": True,
    "encrypted": True,
    "forensic_resistance": True
})

# Option 1: Provide key
key = Fernet.generate_key()
vault.start(encryption_key=key)

# Option 2: Auto-generate key (remember to save it!)
vault.start()  # Generates new key

# Store encrypted data
vault.store("api_key", "sk-secret123456")
api_key = vault.retrieve("api_key")  # Decrypted

# Secure delete
vault.delete("api_key")  # 3-pass overwrite

vault.stop()  # Secure wipe all data
```

**Use Cases**:
- API keys storage
- Password vault
- Encrypted configuration
- PII (Personally Identifiable Information)

**Consumers**:
- `src/app/core/user_manager.py` → User credentials
- `src/app/core/location_tracker.py` → GPS history
- `src/app/security/` → Key management

---

### 5. **utils/encryption/** - Encryption Utilities

#### 5.1 **god_tier_encryption.py** - Multi-Layer Encryption

**Class**: `GodTierEncryption`

**Purpose**: Military-grade, quantum-resistant, 7-layer encryption

**Architecture**:
```
Layer 7: HMAC-SHA512 Authentication (500k iterations)
Layer 6: Quantum-Resistant Padding (256-768 bytes)
Layer 5: AES-256-GCM Double Encryption (rotated key)
Layer 4: ChaCha20-Poly1305
Layer 3: AES-256-GCM (military-grade)
Layer 2: Fernet (AES-128 + HMAC-SHA256)
Layer 1: SHA-512 Integrity Hash
```

**Methods**:
```python
class GodTierEncryption:
    def encrypt_god_tier(data: bytes) -> bytes:
        """7-layer encryption with quantum resistance."""
    
    def decrypt_god_tier(encrypted_data: bytes) -> bytes:
        """7-layer decryption with integrity checks."""
    
    def get_encryption_strength() -> dict:
        """Returns encryption spec details."""
```

**Encryption Strength**:
```python
{
    "tier": "GOD TIER",
    "layers": 7,
    "algorithms": [
        "Fernet (AES-128 + HMAC-SHA256)",
        "AES-256-GCM (military-grade)",
        "ChaCha20-Poly1305",
        "AES-256-GCM Double Encryption",
        "RSA-4096 (quantum-resistant)",
        "ECC-521 (highest elliptic curve)",
        "HMAC-SHA512 Authentication"
    ],
    "key_sizes": {
        "AES": "256-bit",
        "RSA": "4096-bit",
        "ECC": "521-bit",
        "ChaCha20": "256-bit"
    },
    "quantum_resistant": True,
    "perfect_forward_secrecy": True,
    "zero_knowledge": True,
    "authentication": "HMAC-SHA512 with 500,000 iterations",
    "key_derivation": "Scrypt with n=2^20"
}
```

**Usage Pattern**:
```python
from utils.encryption.god_tier_encryption import GodTierEncryption

encryptor = GodTierEncryption()

# Encrypt sensitive data
data = b"Top secret information"
encrypted = encryptor.encrypt_god_tier(data)

# Decrypt
decrypted = encryptor.decrypt_god_tier(encrypted)

# Get encryption info
info = encryptor.get_encryption_strength()
print(f"Encryption tier: {info['tier']}")  # GOD TIER
print(f"Layers: {info['layers']}")          # 7
```

**When to Use**:
- ✅ Critical secrets (master passwords, encryption keys)
- ✅ Long-term archived data (future quantum protection)
- ✅ Regulatory compliance (HIPAA, PCI-DSS)
- ❌ High-throughput data (use single-layer AES-256-GCM)
- ❌ Real-time encryption (too slow for streaming)

**Performance**: ~50-100ms per encryption (7 layers overhead)

**Consumers**:
- `src/app/core/command_override.py` → Master password protection
- `src/app/security/database_security.py` → Database encryption
- High-security modules requiring maximum protection

---

#### 5.2 **encrypted_logging.py** - Encrypted Logs

**Purpose**: Log encryption for audit trails

**Usage**: Secure audit logs that require encryption at rest

---

#### 5.3 **encrypted_network.py** - Network Encryption

**Purpose**: Encrypted network communication

**Usage**: Secure channel establishment for remote connections

---

#### 5.4 **doh_resolver.py** - DNS over HTTPS

**Purpose**: Encrypted DNS resolution

**Usage**: Privacy-preserving DNS queries

---

## Shared Utility Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│ Shared Utilities Dependency Graph                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  utils/logger.py ──────────────┐                           │
│    └── setup_logger() ─────────┼───→ 100+ modules          │
│                                │                            │
│  utils/validators.py ──────────┤                           │
│    ├── validate_actor() ───────┼───→ audit/governance      │
│    ├── validate_action() ──────┼───→ audit/governance      │
│    ├── validate_target() ──────┼───→ security/path_check   │
│    └── sanitize_string() ──────┼───→ 20+ modules           │
│                                │                            │
│  utils/helpers.py ─────────────┤                           │
│    ├── hash_data() ────────────┼───→ 25+ modules           │
│    ├── format_timestamp() ─────┼───→ audit/monitoring      │
│    └── safe_get() ─────────────┼───→ ai_systems/config     │
│                                │                            │
│  utils/storage/ ───────────────┤                           │
│    ├── ephemeral_storage.py ──┼───→ web/sessions          │
│    └── privacy_vault.py ───────┼───→ user_manager/keys     │
│                                │                            │
│  utils/encryption/ ────────────┤                           │
│    ├── god_tier_encryption.py ┼───→ security/critical      │
│    ├── encrypted_logging.py ──┼───→ audit/logs             │
│    └── doh_resolver.py ────────┼───→ browser/privacy       │
│                                │                            │
└────────────────────────────────┴─────────────────────────────┘
```

---

## Cross-Cutting Concerns

### 1. **Logging** (utils/logger.py)
- **Consumers**: 100+ modules
- **Pattern**: Module-level logger with file output
- **Standard**: ISO timestamp, structured messages

### 2. **Validation** (utils/validators.py)
- **Consumers**: 15+ modules
- **Pattern**: Domain validation with `ValidationError`
- **Security**: Path traversal prevention

### 3. **Encryption** (utils/encryption/)
- **Consumers**: Security-critical modules
- **Pattern**: Multi-layer encryption for max security
- **Use Cases**: Secrets, PII, audit logs

### 4. **Storage** (utils/storage/)
- **Consumers**: Web interface, security modules
- **Pattern**: Ephemeral (memory) or encrypted (vault)
- **Use Cases**: Sessions, credentials, sensitive data

---

## Integration Patterns

### Pattern 1: **Logger + Error Handler**
```python
from utils.logger import setup_logger
from app.gui.dashboard_utils import DashboardErrorHandler

logger = setup_logger(__name__)

try:
    risky_operation()
except Exception as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    DashboardErrorHandler.handle_exception(e, "Risky Operation")
```

### Pattern 2: **Validator + Sanitizer**
```python
from utils.validators import validate_target, sanitize_string

# Validate and sanitize user input
try:
    path = sanitize_string(user_input, max_length=500)
    validate_target(path)
except ValidationError as e:
    logger.error("Invalid path: %s", e)
```

### Pattern 3: **Encryption + Storage**
```python
from utils.storage.privacy_vault import PrivacyVault

vault = PrivacyVault(config)
vault.start(encryption_key=key)

# Data is automatically encrypted
vault.store("secret", sensitive_data)
```

---

## Reuse Metrics

| Module                      | Direct Consumers | Indirect Consumers | Pattern Adoption |
|-----------------------------|------------------|--------------------|------------------|
| utils/logger.py             | 100+             | All modules        | 100%             |
| utils/validators.py         | 15+              | 30+                | 95%              |
| utils/helpers.py            | 25+              | 50+                | 90%              |
| utils/storage/              | 5+               | 10+                | 60%              |
| utils/encryption/           | 8+               | 15+                | 70%              |

---

## Best Practices

### BP1: **Always Use Shared Logger**
```python
# ✅ CORRECT
from utils.logger import setup_logger
logger = setup_logger(__name__)

# ❌ WRONG
import logging
logger = logging.getLogger()  # Unconfigured logger
```

### BP2: **Validate Untrusted Input**
```python
# ✅ CORRECT
from utils.validators import validate_target, sanitize_string
safe_path = sanitize_string(user_path)
validate_target(safe_path)

# ❌ WRONG
os.path.join(base, user_path)  # Path traversal risk
```

### BP3: **Use Appropriate Encryption**
```python
# ✅ For critical secrets
from utils.encryption.god_tier_encryption import GodTierEncryption
encrypted = GodTierEncryption().encrypt_god_tier(master_key)

# ✅ For general encryption
from utils.storage.privacy_vault import PrivacyVault
vault.store("api_key", key)  # Fernet encryption (faster)

# ❌ WRONG: No encryption for sensitive data
with open("secrets.json", "w") as f:
    json.dump({"password": "..."}, f)  # Plain text!
```

---

## Related Documentation
- [Helper Functions Map](./01-helper-functions-map.md)
- [Common Patterns Map](./02-common-patterns-map.md)
- [Validation Utils Map](./09-validation-utils-map.md)
- [Crypto Utils Map](./07-crypto-utils-map.md)
