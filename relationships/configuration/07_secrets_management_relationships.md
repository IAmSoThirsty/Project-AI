# Secrets Management System Relationships

**System:** Secrets Management  
**Core Files:**
- `.env` [[.env]] - Plaintext secrets storage (gitignored)
- `src/app/core/user_manager.py` [[src/app/core/user_manager.py]] - Fernet encryption key management
- `src/app/core/command_override.py` [[src/app/core/command_override.py]] - Password hashing (SHA-256, bcrypt)
- `cryptography.fernet` - Symmetric encryption
- `passlib` - Password hashing library

**Last Updated:** 2025-04-20  
**Mission:** AGENT-065 Configuration Systems Relationship Mapping

---


## Navigation

**Location**: `relationships\configuration\07_secrets_management_relationships.md`

**Parent**: [[relationships\configuration\README.md]]


## Secrets Architecture Overview

> **Security Framework**: All secrets management follows [[../security/01_security_system_overview.md|Security System Overview]] and [[../security/02_threat_models.md|Threat Models]]

Project-AI uses **three distinct secret management patterns**:

1. **Environment Variables** → API keys, encryption keys (plaintext in .env) → [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]]
2. **Password Hashing** → User passwords (pbkdf2_sha256, bcrypt) → [[../security/03_defense_layers.md|Defense Layers]]
3. **Fernet Encryption** → Data encryption (symmetric encryption) → [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]]

**No centralized secrets vault** - secrets scattered across patterns.

---

## Secret Type 1: API Keys (Environment Variables)

### Storage Location

```
.env (Plaintext, Gitignored)
├── OPENAI_API_KEY=sk-...           # OpenAI services
├── DEEPSEEK_API_KEY=sk-...         # DeepSeek AI
├── HUGGINGFACE_API_KEY=hf_...      # Hugging Face models
├── SECRET_KEY=<urlsafe-32>         # Session signing
└── WIKI_TASKS_BEARER_TOKEN=<token> # MCP authentication
```

### Access Pattern

```python
import os
from dotenv import load_dotenv

# Load secrets from .env
load_dotenv()

# Access (plaintext)
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = OpenAI(api_key=api_key)
```

### Security Profile

> **Encryption Standards**: See [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] for detailed encryption architecture

| Aspect | Status | Risk Level |
|--------|--------|-----------|
| **Encryption at Rest** | ❌ No → [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] | HIGH |
| **Gitignore Protection** | ✅ Yes | LOW |
| **File Permissions** | ⚠️ Not validated → [[../security/03_defense_layers.md|Defense Layers]] | MEDIUM |
| **Rotation Mechanism** | ❌ No → [[../security/07_security_metrics.md|Security Metrics]] | HIGH |
| **Audit Trail** | ❌ No → [[../monitoring/01-logging-system.md|Logging System]] | HIGH |

---

## Secret Type 2: Encryption Keys (Fernet)

### File: `src/app/core/user_manager.py` [[src/app/core/user_manager.py]]

```python
from cryptography.fernet import Fernet
import os

def _setup_cipher(self):
    """Setup Fernet cipher from environment or generate new key."""
    env_key = os.getenv("FERNET_KEY")
    if env_key:
        try:
            key = env_key.encode()
            self.cipher_suite = Fernet(key)  # ← Load from env
        except Exception:
            # Invalid key format - fall back to runtime
            self.cipher_suite = Fernet(Fernet.generate_key())
    else:
        # No env key - generate runtime-only key (lost on restart!)
        self.cipher_suite = Fernet(Fernet.generate_key())
```

### Key Generation

```python
# Generate Fernet key (run once, add to .env)
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())  # Output: 32-byte base64-encoded key
```

**Example:**
```bash
FERNET_KEY=mP9kL3vX2nQ5rT8wY6zA1bC4dF7gH0jK_I9M8sN5oP2=
```

### Security Profile

| Aspect | Status | Risk Level |
|--------|--------|-----------|
| **Key Storage** | ❌ Plaintext in .env | HIGH |
| **Key Rotation** | ❌ No mechanism | HIGH |
| **Graceful Degradation** | ✅ Generates runtime key if missing | MEDIUM |
| **Key Loss Impact** | 🔴 **CRITICAL** - All encrypted data unrecoverable | CRITICAL |

---

## Secret Type 3: User Passwords (Hashed)

### File: `src/app/core/user_manager.py` [[src/app/core/user_manager.py]]

```python
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],  # Primary: pbkdf2, Legacy: bcrypt
    deprecated="auto"                      # Auto-migrate old hashes
)

def create_user(self, username: str, password: str, is_admin: bool = False):
    """Create user with hashed password."""
    # Hash password before storage
    password_hash = pwd_context.hash(password)
    
    self.users[username] = {
        "password_hash": password_hash,  # ← Stored as hash, not plaintext
        "is_admin": is_admin,
        "account_locked": False,
        "failed_attempts": 0
    }
    self.save_users()

def verify_password(self, username: str, password: str) -> bool:
    """Verify password using constant-time comparison."""
    user = self.users.get(username)
    if not user:
        return False
    
    stored_hash = user.get("password_hash")
    # Constant-time verification (timing attack protection)
    return pwd_context.verify(password, stored_hash)
```

### Password Storage Format

```json
{
  "admin": {
    "password_hash": "$pbkdf2-sha256$29000$...",  ← Not reversible
    "is_admin": true,
    "account_locked": false,
    "failed_attempts": 0
  }
}
```

### Security Profile

> **Password Security**: Follows [[../security/03_defense_layers.md|Defense Layers]] best practices

| Aspect | Status | Risk Level |
|--------|--------|-----------|
| **Hash Algorithm** | ✅ pbkdf2_sha256 (NIST approved) → [[../security/01_security_system_overview.md|Security Overview]] | LOW |
| **Salt** | ✅ Automatic (per-password) | LOW |
| **Iterations** | ✅ 29,000+ (adaptive) | LOW |
| **Timing Attack Protection** | ✅ Constant-time verification → [[../security/02_threat_models.md|Threat Models]] | LOW |
| **Rainbow Table Resistance** | ✅ Salted hashes | LOW |

---

## Secret Type 4: Master Override Password (Command Override)

### File: `src/app/core/command_override.py` [[src/app/core/command_override.py]]

```python
import hashlib
try:
    from passlib.hash import bcrypt as _bcrypt
except:
    _bcrypt = None

def set_master_password(self, password: str) -> bool:
    """Set master password for command override."""
    # Prefer bcrypt if available, fall back to SHA-256
    if _bcrypt:
        self.master_password_hash = _bcrypt.hash(password)
    else:
        # Legacy: SHA-256 (not recommended for passwords!)
        self.master_password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    self._save_config()
    self._audit_log("Master password set")
    return True

def authenticate_master(self, password: str) -> bool:
    """Authenticate master password."""
    if not self.master_password_hash:
        return False
    
    # Verify based on hash type
    if _bcrypt and self.master_password_hash.startswith("$2"):
        # bcrypt hash
        return _bcrypt.verify(password, self.master_password_hash)
    else:
        # SHA-256 hash (legacy, timing attack vulnerable!)
        return self.master_password_hash == hashlib.sha256(password.encode()).hexdigest()
```

### Security Profile

> **Master Password Security**: See [[../security/03_defense_layers.md|Defense Layers]] for override system details

| Aspect | Status | Risk Level |
|--------|--------|-----------|
| **Hash Algorithm** | ⚠️ bcrypt (preferred) or SHA-256 (fallback) → [[../security/02_threat_models.md|Threat Models]] | MEDIUM |
| **Timing Attack Protection** | ❌ SHA-256 path vulnerable → [[../security/01_security_system_overview.md|Security Overview]] | HIGH |
| **Salt** | ✅ bcrypt auto-salts | LOW (bcrypt) |
| **Migration Path** | ✅ Auto-upgrades to bcrypt | LOW |
| **Audit Logging** | ✅ All override actions logged → [[../security/07_security_metrics.md|Security Metrics]] | LOW |

**Critical**: SHA-256 fallback is **not suitable** for password hashing!

---

## Encryption Use Cases

### 1. User Data Encryption (UserManager)

```python
# Encrypt sensitive user data
encrypted_data = self.cipher_suite.encrypt(data.encode())

# Decrypt on retrieval
decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode()
```

**Uses Fernet key from environment.**

### 2. Location History Encryption

File: `src/app/core/location_tracker.py` [[src/app/core/location_tracker.py]]

```python
from cryptography.fernet import Fernet
import os

class LocationTracker:
    def __init__(self):
        # Load Fernet key for encryption
        fernet_key = os.getenv("FERNET_KEY")
        if fernet_key:
            self.cipher = Fernet(fernet_key.encode())
        else:
            # Generate runtime key (NOT PERSISTENT!)
            self.cipher = Fernet(Fernet.generate_key())
    
    def save_location(self, location_data: dict):
        """Encrypt and save location data."""
        location_json = json.dumps(location_data)
        encrypted = self.cipher.encrypt(location_json.encode())
        # Store encrypted bytes
```

### 3. Cloud Sync Encryption

File: `src/app/core/cloud_sync.py` [[src/app/core/cloud_sync.py]]

```python
from cryptography.fernet import Fernet

class CloudSync:
    def __init__(self):
        self.cipher = Fernet(Fernet.generate_key())  # ← New key per instance!
    
    def encrypt_before_upload(self, data: bytes) -> bytes:
        """Encrypt data before cloud upload."""
        return self.cipher.encrypt(data)
```

**Critical**: Generates **new key per instance** - data unrecoverable after restart!

---

## Secrets Lifecycle

```
Secret Generation
    ↓
┌─────────────────────────────────────┐
│  1. API Keys (Manual)               │
│     - Obtain from provider          │
│     - Add to .env manually          │
│     - No automated provisioning     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  2. Fernet Keys (Conditional)       │
│     - Load from FERNET_KEY env var  │
│     - OR generate runtime key       │
│     - Runtime keys lost on restart  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  3. Passwords (User-Provided)       │
│     - User creates password         │
│     - Hash via passlib              │
│     - Store hash in users.json      │
└─────────────────────────────────────┘
    ↓
Secret Usage (Runtime)
    ↓
Secret Expiration/Rotation
    ↓
❌ NO ROTATION MECHANISM
```

---

## Secrets Storage Locations

> **Data Persistence**: See [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] and [[../data/04-BACKUP-RECOVERY.md|Backup & Recovery]]

| Secret Type | Storage Location | Format | Gitignored |
|------------|------------------|--------|-----------|
| **API Keys** | `.env` [[.env]] | Plaintext → [[../security/02_threat_models.md|Threat Models]] | ✅ Yes |
| **Fernet Key** | `.env` [[.env]] or runtime | Plaintext or transient → [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] | ✅ Yes |
| **User Passwords** | `data/users.json` | pbkdf2_sha256 hash → [[../security/03_defense_layers.md|Defense Layers]] | ⚠️ No (should be) |
| **Master Password** | `data/command_override_config.json` | bcrypt/SHA-256 hash → [[../security/07_security_metrics.md|Security Metrics]] | ⚠️ No (should be) |

---

## Secrets Access Control

### File Permissions (Recommended but Not Enforced)

```bash
# .env should be 0600 (-rw-------)
chmod 600 .env

# users.json should be 0600
chmod 600 data/users.json

# Validation code (NOT IMPLEMENTED):
import os
import stat

def validate_secrets_permissions():
    files = [".env", "data/users.json", "data/command_override_config.json"]
    for filepath in files:
        if os.path.exists(filepath):
            st = os.stat(filepath)
            mode = st.st_mode & 0o777
            if mode != 0o600:
                logger.error(f"{filepath} has insecure permissions: {oct(mode)}")
```

---

## Secrets in Transit

> **Transport Security**: See [[../security/01_security_system_overview.md|Security Overview]] for TLS/HTTPS standards

### HTTPS/TLS for API Keys

```python
# OpenAI client uses HTTPS automatically → [[../security/03_defense_layers.md|Defense Layers]]
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# API key sent over TLS to api.openai.com
```

### Local Encryption (Fernet)

> **Encryption at Rest**: See [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]]

```python
# Data encrypted before writing to disk
encrypted_data = cipher.encrypt(plaintext.encode())
with open("data/encrypted.bin", "wb") as f:
    f.write(encrypted_data)
```

---

## Secrets Rotation (NOT IMPLEMENTED)

### Recommended Pattern: API Key Rotation

```python
class SecretsRotator:
    """Automated secrets rotation (NOT IMPLEMENTED)."""
    
    def rotate_api_key(self, provider: str):
        """Rotate API key for provider."""
        # 1. Generate new key via provider API
        new_key = provider_api.create_key()
        
        # 2. Update .env file
        update_env_file("OPENAI_API_KEY", new_key)
        
        # 3. Reload environment
        load_dotenv(override=True)
        
        # 4. Revoke old key (after grace period)
        time.sleep(3600)  # 1 hour grace period
        provider_api.revoke_key(old_key)
        
        # 5. Audit log rotation
        audit_log.log("API key rotated", provider=provider)
```

### Recommended Pattern: Fernet Key Rotation

```python
class FernetKeyRotator:
    """Rotate Fernet encryption keys (NOT IMPLEMENTED)."""
    
    def rotate_key(self, old_key: bytes, new_key: bytes):
        """Rotate Fernet key while re-encrypting data."""
        old_cipher = Fernet(old_key)
        new_cipher = Fernet(new_key)
        
        # Re-encrypt all encrypted data
        for file_path in find_encrypted_files():
            with open(file_path, "rb") as f:
                encrypted_data = f.read()
            
            # Decrypt with old key
            plaintext = old_cipher.decrypt(encrypted_data)
            
            # Re-encrypt with new key
            re_encrypted = new_cipher.encrypt(plaintext)
            
            # Overwrite file
            with open(file_path, "wb") as f:
                f.write(re_encrypted)
        
        # Update .env with new key
        update_env_file("FERNET_KEY", new_key.decode())
```

---

## Secrets Logging (Security Risk)

### Current Risk: API Keys in Logs

```python
# BAD: API key might appear in logs
logger.debug(f"Connecting to OpenAI with key: {api_key}")

# GOOD: Mask secrets in logs
logger.debug(f"Connecting to OpenAI with key: {api_key[:7]}***")
```

### Recommended: Secret Redaction Filter

```python
import logging
import re

class SecretRedactionFilter(logging.Filter):
    """Redact secrets from log messages."""
    
    PATTERNS = [
        r'sk-[a-zA-Z0-9]{48}',      # OpenAI keys
        r'hf_[a-zA-Z0-9]{34}',      # Hugging Face keys
        r'[A-Za-z0-9+/]{43}=',      # Fernet keys (base64)
    ]
    
    def filter(self, record):
        if hasattr(record, 'msg'):
            for pattern in self.PATTERNS:
                record.msg = re.sub(pattern, '***REDACTED***', record.msg)
        return True

# Apply to all loggers
for handler in logging.root.handlers:
    handler.addFilter(SecretRedactionFilter())
```

---

## Integration with External Secrets Managers

### Pattern: AWS Secrets Manager (NOT IMPLEMENTED)

```python
import boto3

class AWSSecretsManager:
    """Load secrets from AWS Secrets Manager."""
    
    def __init__(self):
        self.client = boto3.client('secretsmanager')
    
    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from AWS."""
        response = self.client.get_secret_value(SecretId=secret_name)
        return response['SecretString']

# Usage:
secrets = AWSSecretsManager()
openai_key = secrets.get_secret("project-ai/openai-api-key")
```

### Pattern: HashiCorp Vault (NOT IMPLEMENTED)

```python
import hvac

class VaultSecretsManager:
    """Load secrets from HashiCorp Vault."""
    
    def __init__(self, url: str, token: str):
        self.client = hvac.Client(url=url, token=token)
    
    def get_secret(self, path: str, key: str) -> str:
        """Retrieve secret from Vault."""
        secret = self.client.secrets.kv.v2.read_secret_version(path=path)
        return secret['data']['data'][key]

# Usage:
vault = VaultSecretsManager("http://localhost:8200", vault_token)
fernet_key = vault.get_secret("project-ai/encryption", "fernet_key")
```

---

## Secrets Security Checklist

### ✅ Implemented

- [x] API keys in .env (gitignored)
- [x] Password hashing (pbkdf2_sha256, bcrypt)
- [x] Fernet encryption for sensitive data
- [x] Constant-time password verification
- [x] Auto-salting in password hashes

### ❌ Missing

- [ ] .env file permission validation
- [ ] Secrets encryption at rest
- [ ] Automated key rotation
- [ ] Secrets audit trail
- [ ] Integration with secrets managers (Vault, AWS, Azure)
- [ ] Secret redaction in logs
- [ ] Key derivation from master password
- [ ] Multi-key encryption (key wrapping)
- [ ] Secrets expiration/TTL

---

## Related Systems

### Configuration Systems
- [Environment Variables](./06_environment_variables_relationships.md)
- [Environment Manager](./02_environment_manager_relationships.md)
- [Config Loader](./01_config_loader_relationships.md)
- [Settings Validator](./03_settings_validator_relationships.md)

### Cross-System Dependencies
- [[../security/01_security_system_overview.md|Security System Overview]] - Comprehensive secrets security framework
- [[../security/02_threat_models.md|Threat Models]] - API key and password threat modeling
- [[../security/03_defense_layers.md|Defense Layers]] - Master password and hash algorithm selection
- [[../security/07_security_metrics.md|Security Metrics]] - Secrets rotation audit and compliance
- [[../data/02-ENCRYPTION-CHAINS.md|Encryption Chains]] - Fernet key encryption architecture
- [[../data/01-PERSISTENCE-PATTERNS.md|Persistence Patterns]] - Secrets storage patterns
- [[../data/04-BACKUP-RECOVERY.md|Backup & Recovery]] - Secrets backup and key recovery
- [[../data/00-DATA-INFRASTRUCTURE-OVERVIEW.md|Data Infrastructure]] - Secure data directory management
- [[../monitoring/01-logging-system.md|Logging System]] - Secret redaction and audit logging
