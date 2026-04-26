# User Management Data Model

**Module**: `src/app/core/user_manager.py` [[src/app/core/user_manager.py]]  
**Storage**: `data/users.json`  
**Persistence**: JSON with atomic file operations  
**Schema Version**: 2.0 (with password hashing migration)

---

## Overview

The User Management system handles user profiles, authentication, and encrypted data storage. It uses **passlib** for secure password hashing with pbkdf2_sha256 as the primary scheme (bcrypt as fallback for legacy compatibility) and **Fernet** for encryption of sensitive user data.

### Key Features

- Secure password hashing (pbkdf2_sha256/bcrypt)
- Automatic migration from plaintext to hashed passwords
- Fernet-based encryption for sensitive data
- Account lockout protection against brute force
- Path traversal protection via `safe_path_join`
- Atomic file operations via `_atomic_write_json`

---

## Schema Structure

### User Document

```json
{
  "username": {
    "username": "string",
    "password_hash": "string (pbkdf2_sha256 or bcrypt hash)",
    "email": "string (optional)",
    "role": "string (admin|user)",
    "created_at": "ISO 8601 timestamp",
    "last_login": "ISO 8601 timestamp",
    "failed_attempts": "integer",
    "locked_until": "ISO 8601 timestamp | null",
    "preferences": {
      "theme": "string",
      "notifications": "boolean",
      "language": "string"
    }
  }
}
```

### Example

```json
{
  "admin": {
    "username": "admin",
    "password_hash": "$pbkdf2-sha256$29000$...",
    "email": "admin@example.com",
    "role": "admin",
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T14:22:10Z",
    "failed_attempts": 0,
    "locked_until": null,
    "preferences": {
      "theme": "dark",
      "notifications": true,
      "language": "en"
    }
  }
}
```

---

## Field Specifications

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `username` | string | Yes | Unique user identifier (key in JSON) |
| `password_hash` | string | Yes | pbkdf2_sha256 or bcrypt hash of password |
| `email` | string | No | User email address |
| `role` | string | Yes | User role: "admin" or "user" |
| `created_at` | datetime | Yes | Account creation timestamp |
| `last_login` | datetime | No | Last successful login timestamp |
| `failed_attempts` | integer | Yes | Count of consecutive failed login attempts |
| `locked_until` | datetime\|null | Yes | Account lockout expiration (null if not locked) |
| `preferences` | object | No | User-specific settings |

---

## Password Hashing

### Hash Generation

```python
from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
)

# Hash password
password_hash = pwd_context.hash("user_password")
```

### Hash Verification

```python
# Verify password
is_valid = pwd_context.verify("user_password", stored_hash)
```

### Migration Logic

On initialization, `UserManager` automatically migrates plaintext passwords:

```python
def _migrate_plaintext_passwords(self):
    migrated = False
    for uname, udata in self.users.items():
        if (
            isinstance(udata, dict)
            and "password" in udata
            and "password_hash" not in udata
        ):
            plaintext_pw = udata["password"]
            hashed = pwd_context.hash(plaintext_pw)
            udata["password_hash"] = hashed
            del udata["password"]
            migrated = True
    if migrated:
        self.save_users()
```

---

## Encryption System

### Fernet Key Management

```python
from cryptography.fernet import Fernet

# Key source priority:
# 1. Explicit argument
# 2. FERNET_KEY environment variable
# 3. Generated runtime key

env_key = os.getenv("FERNET_KEY")
if env_key:
    cipher_suite = Fernet(env_key.encode())
else:
    cipher_suite = Fernet(Fernet.generate_key())
```

### Encryption Operations

```python
# Encrypt data
encrypted = cipher_suite.encrypt(json.dumps(data).encode())

# Decrypt data
decrypted = json.loads(cipher_suite.decrypt(encrypted).decode())
```

---

## Account Lockout System

### Lockout Configuration

```python
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 300  # 5 minutes
```

### Lockout Logic

```python
def _ensure_lockout_fields(self):
    for uname, udata in self.users.items():
        if isinstance(udata, dict):
            udata.setdefault("failed_attempts", 0)
            udata.setdefault("locked_until", None)
```

**Lockout Trigger**: After 5 failed login attempts, account locks for 5 minutes.

**Reset**: Successful login resets `failed_attempts` to 0.

---

## CRUD Operations

### Create User

```python
user_manager.create_user(
    username="johndoe",
    password="secure_password_123",
    email="john@example.com",
    role="user"
)
```

**Internals**:
1. Hash password with pbkdf2_sha256
2. Create user document with lockout fields
3. Save to `users.json` with atomic write
4. **Never stores plaintext password**

### Authenticate User

```python
is_authenticated = user_manager.authenticate("johndoe", "secure_password_123")
```

**Flow**:
1. Check if account locked (`locked_until > now`)
2. Verify password hash with `pwd_context.verify()`
3. On success: Reset `failed_attempts`, update `last_login`
4. On failure: Increment `failed_attempts`, lock if >= 5

### Update User

```python
user_manager.update_user("johndoe", {
    "email": "newemail@example.com",
    "preferences": {"theme": "light"}
})
```

### Delete User

```python
user_manager.delete_user("johndoe")
```

---

## Data Persistence

### File Path Security

```python
from app.security.path_security import safe_path_join, validate_filename

# Prevents path traversal
validate_filename(users_file)  # Raises if contains ../ or /
self.users_file = safe_path_join(data_dir, users_file)
```

### Atomic Writes

Uses `_atomic_write_json` from `ai_systems.py`:

```python
def save_users(self):
    _atomic_write_json(self.users_file, self.users)
```

**Guarantees**:
- Write to temporary file first
- File-level locking (5-second timeout)
- Atomic `os.replace()` to prevent corruption
- Automatic cleanup of temp files

---

## Thread Safety

- **File-level locking** via `_acquire_lock()` during writes
- Lock file: `{users_file}.lock`
- Stale lock detection (30-second timeout)
- Dead process reclamation

---

## Migration Guide

### V1 to V2 (Plaintext to Hashed Passwords)

**Automatic Migration**:

`UserManager` detects plaintext passwords on initialization and automatically migrates:

```python
# Old format (V1)
{
  "admin": {
    "username": "admin",
    "password": "plaintext123",  # ❌ Insecure
    "role": "admin"
  }
}

# New format (V2) - after migration
{
  "admin": {
    "username": "admin",
    "password_hash": "$pbkdf2-sha256$29000$...",  # ✅ Secure
    "role": "admin"
  }
}
```

**No manual intervention required** - migration happens on first load.

---

## Security Best Practices

### Password Policy

1. **Minimum Length**: 8 characters (enforced in GUI)
2. **Hashing**: pbkdf2_sha256 with 29,000 iterations
3. **Salt**: Automatic per-password salt via passlib
4. **Legacy Support**: bcrypt verification for old hashes

### Encryption Key Management

1. **Environment Variable**: Store `FERNET_KEY` in `.env` [[.env]] file
2. **Key Rotation**: Generate new key with `Fernet.generate_key()`
3. **Key Storage**: Never commit `.env` [[.env]] to version control

```bash
# .env file
FERNET_KEY=<base64-encoded-32-byte-key>
```

### Account Lockout

- **Brute Force Protection**: 5 attempts = 5-minute lockout
- **Distributed Attack Mitigation**: Lockout persists across restarts
- **Manual Unlock**: Admin can reset `failed_attempts` and `locked_until`

---

## Usage Examples

### Creating Admin User

```python
from app.core.user_manager import UserManager

manager = UserManager(data_dir="data")

# Create admin with hashed password
manager.create_user(
    username="admin",
    password="super_secure_password",
    email="admin@company.com",
    role="admin"
)
```

### Login Flow

```python
# User enters credentials
username = "admin"
password = "super_secure_password"

# Authenticate
if manager.authenticate(username, password):
    manager.current_user = username
    print("Login successful!")
else:
    print("Invalid credentials or account locked")
```

### Check Account Status

```python
user = manager.get_user("admin")
if user:
    if user.get("locked_until"):
        print(f"Account locked until: {user['locked_until']}")
    else:
        print(f"Failed attempts: {user['failed_attempts']}/5")
```

---

## Testing Strategy

### Isolated Testing

All tests use `tempfile.TemporaryDirectory()` to avoid polluting production data:

```python
import tempfile
from app.core.user_manager import UserManager

def test_user_creation():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = UserManager(data_dir=tmpdir)
        manager.create_user("testuser", "password123")
        assert "testuser" in manager.users
```

### Test Coverage

- ✅ User creation with password hashing
- ✅ Authentication success/failure
- ✅ Account lockout after 5 failures
- ✅ Lockout expiration
- ✅ Plaintext password migration
- ✅ Encryption/decryption
- ✅ Path traversal protection

---

## Performance Considerations

### Hash Computation Cost

- **pbkdf2_sha256**: ~100ms per hash (29,000 iterations)
- **Login Latency**: Acceptable for authentication use case
- **Bulk Operations**: Avoid hashing in tight loops

### File I/O Optimization

- **Read-heavy**: Users loaded once at startup
- **Write-heavy**: Atomic writes with locking prevent corruption
- **Caching**: In-memory `self.users` dict for fast lookups

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `ai_systems.py` | Provides `_atomic_write_json` for safe persistence |
| `app.security.path_security` | Validates filenames and paths |
| `cloud_sync.py` | Syncs encrypted user data to cloud |
| `telemetry.py` | Logs user authentication events |

---

## Future Enhancements

1. **Multi-Factor Authentication (MFA)**: TOTP support
2. **Password Expiry**: Force password change after N days
3. **Session Management**: JWT tokens for web version
4. **Audit Log**: Track all user modifications
5. **Role Permissions**: Granular permission system beyond admin/user

---

## References

- **Passlib Documentation**: https://passlib.readthedocs.io/
- **Fernet Specification**: https://github.com/fernet/spec
- **OWASP Authentication**: https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication

---

**Last Updated**: 2024-01-20  
**Schema Version**: 2.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/user_manager.py]]
