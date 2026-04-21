# User Management System

**Module:** `src/app/core/user_manager.py`  
**Type:** Core Infrastructure  
**Dependencies:** passlib, cryptography (Fernet), json  
**Related Modules:** cloud_sync.py, data_persistence.py

---

## Overview

The User Management System provides secure user authentication, profile management, and account security with bcrypt/PBKDF2 password hashing, account lockout protection, and password policy enforcement.

### Core Features

- **Secure Password Hashing**: PBKDF2-SHA256 (primary) + bcrypt (fallback)
- **Account Lockout**: 5 failed attempts → 15-minute lockout
- **Password Policies**: 8+ chars, mixed case, digits, special characters
- **Timing Attack Protection**: Constant-time authentication
- **Automatic Migration**: Plaintext → hashed passwords on load
- **Path Traversal Protection**: Safe filename validation

---

## Architecture

```
UserManager
├── Authentication (constant-time, lockout protection)
├── Password Management (PBKDF2/bcrypt hashing, strength validation)
├── User CRUD (create, read, update, delete)
├── Profile Management (persona, preferences, role, approved status)
└── Lockout Management (failed attempts tracking, manual unlock)
```

---

## Core Classes

### UserManager

```python
from app.core.user_manager import UserManager

# Initialize (loads users from users.json)
manager = UserManager(
    users_file="users.json",
    data_dir="data"
)

# Create user with password policy validation
success = manager.create_user(
    username="admin",
    password="SecureP@ss123",  # Must meet policy
    persona="professional",
    preferences={"language": "en", "style": "casual"}
)

# Authenticate user (constant-time, lockout protection)
success, message = manager.authenticate("admin", "SecureP@ss123")
if success:
    print(f"Authenticated: {manager.current_user}")
else:
    print(f"Auth failed: {message}")

# Get user data (password_hash excluded)
user_data = manager.get_user_data("admin")
# Returns: {"persona": "professional", "preferences": {...}, "role": "user", ...}

# Update user
manager.update_user("admin", role="admin", approved=True)

# Change password
manager.set_password("admin", "NewSecureP@ss456")

# Delete user
manager.delete_user("admin")
```

---

## Password Security

### Hashing Algorithms

**Primary: PBKDF2-SHA256**
```python
# Configuration
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto"
)

# Properties
- Algorithm: PBKDF2-HMAC-SHA256
- Iterations: 29,000 (default)
- Salt: 16 bytes (auto-generated)
- Output: 32 bytes
- Format: $pbkdf2-sha256$29000$salt$hash
```

**Fallback: bcrypt**
```python
# Used for legacy compatibility
- Algorithm: bcrypt (Blowfish-based)
- Cost Factor: 12 (default)
- Salt: 16 bytes
- Format: $2b$12$salt$hash
```

### Password Policy

```python
def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Requirements:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    # ... (similar checks for lowercase, digit, special char)
    
    return True, ""

# Usage
is_valid, error_msg = manager.validate_password_strength("weak")
if not is_valid:
    print(f"Password rejected: {error_msg}")
```

---

## Account Lockout Protection

### Lockout Policy

```python
# Configuration (hardcoded in authenticate method)
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes (seconds)

# Lockout flow
1. Failed login → increment failed_attempts counter
2. 5 failed attempts → set locked_until = time.time() + 900
3. Login attempts during lockout → rejected with remaining time
4. After 15 minutes → lockout cleared automatically
5. Successful login → reset failed_attempts to 0
```

### Lockout Management

```python
# Check if account is locked
is_locked, time_remaining = manager.is_account_locked("admin")
if is_locked:
    print(f"Account locked for {time_remaining} seconds")

# Manually unlock account (admin function)
success = manager.unlock_account("admin")
if success:
    print("Account unlocked successfully")
```

### Lockout Data Structure

```json
{
  "admin": {
    "password_hash": "$pbkdf2-sha256$...",
    "failed_attempts": 3,
    "locked_until": 1713624900.0,
    "persona": "professional",
    "preferences": {"language": "en"},
    "role": "user",
    "approved": true
  }
}
```

---

## Constant-Time Authentication

### Timing Attack Prevention

```python
def authenticate(self, username, password):
    """
    Constant-time authentication prevents username enumeration via timing.
    
    Implementation:
    1. Always perform password verification (even for non-existent users)
    2. Use valid dummy hash for non-existent users
    3. Add random delay (10-30ms) to mask timing differences
    """
    # Valid dummy hash (always same computation time)
    DUMMY_HASH = "$pbkdf2-sha256$29000$dw4hRAhhjBECACBkTOkdAw$J32CKKL8HKxGKBCenxbzNJE1mq8.rpQCu8brEd2o8Fw"
    
    # Get user or use dummy data
    user_exists = username in self.users
    user = self.users.get(username, {
        "password_hash": DUMMY_HASH,
        "failed_attempts": 0,
        "locked_until": None
    })
    
    # Always verify password (constant-time)
    is_valid = pwd_context.verify(password, user["password_hash"])
    
    # Add random delay (10-30ms)
    time.sleep(secrets.SystemRandom().uniform(0.01, 0.03))
    
    # Only proceed if user exists AND password valid
    if user_exists and is_valid:
        # Success path
        ...
    elif user_exists:
        # Failed login (increment counter)
        ...
    else:
        # Non-existent user (return generic error)
        return False, "Invalid credentials"
```

**Why Constant-Time Matters:**
```python
# ❌ Timing attack vulnerable
if username not in users:
    return False  # Fast path (50μs)
if not verify_password(password):
    return False  # Slow path (100ms)

# Attacker can distinguish:
# - Fast response → user doesn't exist
# - Slow response → user exists, wrong password

# ✅ Constant-time (always ~100ms + random 10-30ms)
user = users.get(username, dummy_user)  # Same path always
is_valid = verify_password(password, user.hash)  # Always verify
time.sleep(random(0.01, 0.03))  # Add noise
```

---

## User Data Structure

```json
{
  "admin": {
    "password_hash": "$pbkdf2-sha256$29000$...",
    "persona": "professional",
    "preferences": {
      "language": "en",
      "style": "casual"
    },
    "location_active": false,
    "approved": true,
    "role": "admin",
    "failed_attempts": 0,
    "locked_until": null,
    "profile_picture": "uploads/admin_avatar.png",
    "telemetry_consent": true
  },
  "user2": {
    "password_hash": "$pbkdf2-sha256$29000$...",
    "persona": "friendly",
    "preferences": {
      "language": "es",
      "style": "formal"
    },
    "location_active": true,
    "approved": false,
    "role": "user",
    "failed_attempts": 0,
    "locked_until": null
  }
}
```

**Field Descriptions:**
- `password_hash`: PBKDF2 or bcrypt hash (never plaintext)
- `persona`: AI personality preset ("friendly", "professional", "technical")
- `preferences`: User-specific settings (language, UI style, theme)
- `location_active`: Location tracking consent
- `approved`: Account approval status (for moderation)
- `role`: User role ("user", "admin", "moderator")
- `failed_attempts`: Failed login counter (for lockout)
- `locked_until`: Unix timestamp (null if not locked)
- `profile_picture`: Path to avatar image
- `telemetry_consent`: Analytics opt-in

---

## Path Traversal Protection

```python
from app.security.path_security import safe_path_join, validate_filename

# Filename validation (prevents path traversal)
validate_filename("users.json")     # ✅ Valid
validate_filename("../etc/passwd")  # ❌ Raises ValueError

# Safe path joining
safe_path = safe_path_join("data", "users.json")
# Returns: "data/users.json"

unsafe_path = safe_path_join("data", "../etc/passwd")
# Raises: ValueError (path traversal attempt)
```

**Implementation:**
```python
def validate_filename(filename: str) -> None:
    """Validate filename doesn't contain path separators."""
    if '/' in filename or '\\' in filename:
        raise ValueError(f"Invalid filename: {filename}")

def safe_path_join(base_dir: str, filename: str) -> str:
    """Safely join paths and validate result is within base_dir."""
    validate_filename(filename)
    full_path = os.path.abspath(os.path.join(base_dir, filename))
    base_path = os.path.abspath(base_dir)
    
    if not full_path.startswith(base_path):
        raise ValueError("Path traversal attempt detected")
    
    return full_path
```

---

## Migration System

### Plaintext to Hashed Passwords

```python
# Automatic migration on UserManager initialization
def _migrate_plaintext_passwords(self):
    """Migrate plaintext passwords to hashed versions."""
    migrated = False
    for username, user_data in self.users.items():
        if "password" in user_data and "password_hash" not in user_data:
            # Hash plaintext password
            pw = user_data.get("password")
            if pw and self._hash_and_store_password(username, pw):
                migrated = True
    
    if migrated:
        self.save_users()

# Hash and store (with fallback)
def _hash_and_store_password(self, username, password):
    try:
        # Primary: PBKDF2-SHA256
        pw_hash = pwd_context.hash(password)
        self.users[username]["password_hash"] = pw_hash
        self.users[username].pop("password", None)
        return True
    except Exception:
        # Fallback: PBKDF2 directly
        try:
            fallback_hash = pbkdf2_sha256.hash(password)
            self.users[username]["password_hash"] = fallback_hash
            self.users[username].pop("password", None)
            return True
        except Exception:
            return False
```

**Migration Example:**
```json
// Before migration (users.json)
{
  "admin": {
    "password": "plaintext123",  // ❌ Insecure
    "persona": "professional"
  }
}

// After migration (automatic on load)
{
  "admin": {
    "password_hash": "$pbkdf2-sha256$29000$...",  // ✅ Secure
    "persona": "professional",
    "failed_attempts": 0,
    "locked_until": null
  }
}
```

---

## Integration Examples

### With AI Systems

```python
from app.core.user_manager import UserManager
from app.core.ai_systems import AIPersona

manager = UserManager()
persona = AIPersona()

# Authenticate and load persona
success, msg = manager.authenticate("admin", "password")
if success:
    user_data = manager.get_user_data("admin")
    persona.load_preset(user_data["persona"])
```

### With Location Tracker

```python
from app.core.user_manager import UserManager
from app.core.location_tracker import LocationTracker

manager = UserManager()
tracker = LocationTracker()

# Check location permission
user_data = manager.get_user_data("admin")
if user_data.get("location_active", False):
    location = tracker.get_location_from_ip()
```

### With Telemetry

```python
from app.core.user_manager import UserManager
from app.core.telemetry import send_event

manager = UserManager()

# Track authentication with telemetry consent
success, msg = manager.authenticate("admin", "password")
user_data = manager.get_user_data("admin")

if user_data.get("telemetry_consent", False):
    send_event("user_login" if success else "login_failed", {
        "username": "admin",
        "message": msg
    })
```

---

## Testing

```python
import unittest
import tempfile
import os
from app.core.user_manager import UserManager

class TestUserManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = UserManager(
            users_file="test_users.json",
            data_dir=self.temp_dir
        )
    
    def test_create_user(self):
        """Test user creation with password policy."""
        success = self.manager.create_user(
            username="test_user",
            password="SecureP@ss123"
        )
        self.assertTrue(success)
    
    def test_weak_password_rejected(self):
        """Test password policy enforcement."""
        success = self.manager.create_user(
            username="test_user",
            password="weak"
        )
        self.assertFalse(success)
    
    def test_authentication(self):
        """Test user authentication."""
        self.manager.create_user("test_user", "SecureP@ss123")
        success, msg = self.manager.authenticate("test_user", "SecureP@ss123")
        self.assertTrue(success)
    
    def test_account_lockout(self):
        """Test account lockout after failed attempts."""
        self.manager.create_user("test_user", "SecureP@ss123")
        
        # 5 failed attempts
        for _ in range(5):
            self.manager.authenticate("test_user", "wrong_password")
        
        # 6th attempt should be locked
        success, msg = self.manager.authenticate("test_user", "SecureP@ss123")
        self.assertFalse(success)
        self.assertIn("locked", msg.lower())
```

---

## Configuration

### Environment Variables

```bash
# Fernet key for optional encryption
export FERNET_KEY="your-base64-fernet-key"
```

### Password Policy Configuration

```python
# Modify in user_manager.py
MIN_PASSWORD_LENGTH = 8
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_DIGIT = True
REQUIRE_SPECIAL_CHAR = True
SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
```

### Lockout Policy Configuration

```python
# Modify in authenticate() method
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900  # 15 minutes
```

---

## Security Best Practices

1. **Never Log Passwords**
   ```python
   # ❌ BAD
   logger.info(f"User {username} logged in with password {password}")
   
   # ✅ GOOD
   logger.info(f"User {username} authenticated successfully")
   ```

2. **Use Secure Password Generation**
   ```python
   import secrets
   import string
   
   def generate_secure_password(length=16):
       alphabet = string.ascii_letters + string.digits + "!@#$%^&*()"
       return ''.join(secrets.choice(alphabet) for _ in range(length))
   ```

3. **Implement Rate Limiting**
   ```python
   # Add to authenticate() method
   from app.core.rate_limiter import RateLimiter
   
   rate_limiter = RateLimiter(max_attempts=10, window_seconds=300)
   if not rate_limiter.allow_request(username):
       return False, "Too many authentication attempts. Try again later."
   ```

---

## Troubleshooting

### "User not found" vs "Invalid credentials"
```python
# Both return generic "Invalid credentials" to prevent username enumeration
# This is intentional for security (constant-time authentication)
```

### "Account locked" Message
```python
# Wait 15 minutes or use admin unlock
manager.unlock_account("username")
```

### Password Policy Errors
```python
# Test password strength before creation
is_valid, error_msg = manager.validate_password_strength("TestP@ss123")
if not is_valid:
    print(f"Password rejected: {error_msg}")
```

---

**Last Updated:** 2026-04-20  
**Module Version:** 1.0.0  
**Author:** AGENT-036 (Data & Infrastructure Documentation Specialist)
