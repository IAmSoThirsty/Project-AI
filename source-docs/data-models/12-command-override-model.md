# Command Override Data Model

**Module**: `src/app/core/command_override.py` [[src/app/core/command_override.py]], `src/app/core/ai_systems.py` [[src/app/core/ai_systems.py]] (CommandOverride class)  
**Storage**: `data/command_override_config.json`  
**Persistence**: JSON with audit logging  
**Schema Version**: 2.0

---

## Overview

The Command Override system implements 10+ safety protocols with SHA-256 password protection, audit logging, and time-limited activation for emergency system control.

### Key Features

- **Master Password Protection**: SHA-256 hashing with salt
- **10+ Safety Protocols**: Lockout, time limits, audit trail, IP tracking, etc.
- **Audit Logging**: Complete record of all override operations
- **Time-Limited Activation**: Auto-deactivation after timeout
- **Emergency Access**: Break-glass mechanism for critical situations

---

## Schema Structure

### Command Override Config

**File**: `data/command_override_config.json`

```json
{
  "master_password_hash": "sha256:a3f7b8c2d1e4f5g6...",
  "override_active": false,
  "activation_timestamp": null,
  "deactivation_timestamp": null,
  "activated_by": null,
  "activation_reason": null,
  "timeout_seconds": 300,
  "max_failed_attempts": 5,
  "failed_attempts": 0,
  "locked_until": null,
  "audit_log": [
    {
      "timestamp": "2024-01-20T14:30:00Z",
      "event": "activation_attempt",
      "user": "admin",
      "success": true,
      "reason": "emergency_system_repair",
      "ip_address": "192.168.1.100"
    },
    {
      "timestamp": "2024-01-20T14:35:00Z",
      "event": "deactivation",
      "user": "admin",
      "duration_seconds": 300,
      "commands_executed": 5
    }
  ],
  "metadata": {
    "schema_version": "2.0",
    "last_updated": "2024-01-20T14:35:00Z"
  }
}
```

---

## Field Specifications

### Config Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `master_password_hash` | string | Yes | SHA-256 hash of master password (with salt) |
| `override_active` | boolean | Yes | Current override status |
| `activation_timestamp` | datetime\|null | Yes | When override was activated |
| `deactivation_timestamp` | datetime\|null | Yes | When override was deactivated |
| `activated_by` | string\|null | Yes | User who activated override |
| `activation_reason` | string\|null | Yes | Reason for activation |
| `timeout_seconds` | integer | Yes | Auto-deactivation timeout (default: 300) |
| `max_failed_attempts` | integer | Yes | Lockout threshold (default: 5) |
| `failed_attempts` | integer | Yes | Current failed attempt count |
| `locked_until` | datetime\|null | Yes | Lockout expiration timestamp |
| `audit_log` | array | Yes | Complete history of override operations |

### Audit Log Entry

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | datetime | Event timestamp |
| `event` | string | Event type ("activation_attempt", "deactivation", "timeout", etc.) |
| `user` | string | User performing action |
| `success` | boolean | Whether operation succeeded |
| `reason` | string | Justification for action (activation only) |
| `ip_address` | string | Source IP address (if available) |

---

## Password System

### Password Hashing (SHA-256 + Salt)

```python
import hashlib

def _hash_password(self, password: str) -> str:
    """Hash password with SHA-256 and salt."""
    salt = self.config.get("password_salt", "project_ai_override_salt")
    salted = f"{password}{salt}"
    hash_digest = hashlib.sha256(salted.encode()).hexdigest()
    return f"sha256:{hash_digest}"

def _verify_password(self, password: str) -> bool:
    """Verify password against stored hash."""
    provided_hash = self._hash_password(password)
    stored_hash = self.config.get("master_password_hash")
    return provided_hash == stored_hash
```

**Note**: Extended system in `command_override.py` uses more advanced hashing (consider migrating to Argon2 or bcrypt).

---

## 10 Safety Protocols

### 1. Password Protection

```python
def activate(self, password: str, user: str, reason: str) -> tuple[bool, str]:
    """Activate override with password verification."""
    if not self._verify_password(password):
        self._log_failed_attempt(user)
        return False, "Invalid master password"
    
    # Activate override
    self._set_override_active(True, user, reason)
    return True, "Override activated"
```

### 2. Account Lockout

```python
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 minutes

def _log_failed_attempt(self, user: str):
    """Log failed attempt and lockout if threshold reached."""
    self.config["failed_attempts"] += 1
    
    if self.config["failed_attempts"] >= MAX_FAILED_ATTEMPTS:
        lockout_until = datetime.now() + timedelta(seconds=LOCKOUT_DURATION)
        self.config["locked_until"] = lockout_until.isoformat()
        self._save_config()
        logger.warning("Override system locked due to failed attempts")
```

### 3. Time-Limited Activation

```python
TIMEOUT_SECONDS = 300  # 5 minutes default

def _check_timeout(self):
    """Auto-deactivate if timeout exceeded."""
    if not self.config["override_active"]:
        return
    
    activation_time = datetime.fromisoformat(self.config["activation_timestamp"])
    elapsed = (datetime.now() - activation_time).total_seconds()
    
    if elapsed >= self.config["timeout_seconds"]:
        self._auto_deactivate("timeout_exceeded")
```

### 4. Audit Logging

```python
def _log_audit_event(self, event: str, user: str, **kwargs):
    """Log audit event."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": event,
        "user": user,
        **kwargs
    }
    self.config["audit_log"].append(entry)
    self._save_config()
```

### 5. Activation Reason Required

```python
def activate(self, password: str, user: str, reason: str) -> tuple[bool, str]:
    """Activate with mandatory reason."""
    if not reason or len(reason) < 10:
        return False, "Activation reason required (min 10 characters)"
    
    # Proceed with activation
    ...
```

### 6. Manual Deactivation Tracking

```python
def deactivate(self, user: str) -> tuple[bool, str]:
    """Manually deactivate override."""
    if not self.config["override_active"]:
        return False, "Override not active"
    
    # Calculate duration
    activation_time = datetime.fromisoformat(self.config["activation_timestamp"])
    duration = (datetime.now() - activation_time).total_seconds()
    
    self._log_audit_event(
        "deactivation",
        user,
        duration_seconds=duration,
        commands_executed=self._get_command_count()
    )
    
    self._set_override_active(False)
    return True, "Override deactivated"
```

### 7. IP Address Tracking

```python
def _get_client_ip(self) -> str:
    """Get client IP address (from request context)."""
    # In GUI: use local IP
    # In web: use request.remote_addr
    return "127.0.0.1"  # Placeholder

def activate(self, password: str, user: str, reason: str) -> tuple[bool, str]:
    """Activate with IP tracking."""
    ip_address = self._get_client_ip()
    
    self._log_audit_event(
        "activation_attempt",
        user,
        success=True,
        reason=reason,
        ip_address=ip_address
    )
    ...
```

### 8. Failed Attempt Reset on Success

```python
def activate(self, password: str, user: str, reason: str) -> tuple[bool, str]:
    """Reset failed attempts on successful activation."""
    if self._verify_password(password):
        self.config["failed_attempts"] = 0
        self._save_config()
        ...
```

### 9. Lockout Expiration Check

```python
def _is_locked_out(self) -> bool:
    """Check if override system is locked."""
    locked_until = self.config.get("locked_until")
    if not locked_until:
        return False
    
    expiration = datetime.fromisoformat(locked_until)
    if datetime.now() < expiration:
        return True
    
    # Lockout expired, clear it
    self.config["locked_until"] = None
    self.config["failed_attempts"] = 0
    self._save_config()
    return False
```

### 10. Persistence Across Restarts

All state persisted to `command_override_config.json`:
- Active/inactive status
- Activation timestamp (for timeout calculation)
- Failed attempt count
- Lockout expiration
- Complete audit log

---

## Usage Examples

### Activate Override

```python
from app.core.ai_systems import CommandOverride

override = CommandOverride(data_dir="data")

success, message = override.activate(
    password="master_password_123",
    user="admin",
    reason="Emergency system repair - database corruption detected"
)

if success:
    print("Override activated. System safety checks bypassed.")
else:
    print(f"Activation failed: {message}")
```

### Check Override Status

```python
if override.is_active():
    print("Override currently active")
    print(f"Activated by: {override.config['activated_by']}")
    print(f"Reason: {override.config['activation_reason']}")
else:
    print("Override inactive")
```

### Deactivate Override

```python
success, message = override.deactivate(user="admin")
if success:
    print("Override deactivated. Safety checks restored.")
```

### View Audit Log

```python
audit_log = override.get_audit_log()

for entry in audit_log:
    print(f"[{entry['timestamp']}] {entry['event']} by {entry['user']}")
    if entry.get("reason"):
        print(f"  Reason: {entry['reason']}")
```

---

## Security Considerations

### Password Security

**Current**: SHA-256 + salt  
**Recommended**: Migrate to Argon2 or bcrypt for better resistance to brute force.

```python
# Future improvement
from argon2 import PasswordHasher

ph = PasswordHasher()
password_hash = ph.hash("master_password_123")
is_valid = ph.verify(password_hash, "master_password_123")
```

### Audit Log Integrity

**Current**: Stored in same file as config (vulnerable to tampering)  
**Recommended**: Separate immutable audit log with HMAC signatures.

### Multi-Factor Authentication

**Future Enhancement**: Require MFA (TOTP) in addition to master password.

---

## Extended Override System

**File**: `src/app/core/command_override.py` [[src/app/core/command_override.py]]

**Additional Features**:
- Advanced password hashing (Argon2)
- Multiple override levels (Level 1-5)
- Emergency contact notifications
- Automatic security incident reporting
- Geo-fencing restrictions
- Biometric authentication support (planned)

---

## Testing Strategy

### Unit Tests

```python
def test_activate_deactivate():
    override = CommandOverride(data_dir="data/test")
    override.set_master_password("test_password")
    
    success, _ = override.activate("test_password", "admin", "Test reason")
    assert success
    assert override.is_active()
    
    success, _ = override.deactivate("admin")
    assert success
    assert not override.is_active()

def test_lockout_after_failed_attempts():
    override = CommandOverride(data_dir="data/test")
    override.set_master_password("correct_password")
    
    # 5 failed attempts
    for _ in range(5):
        override.activate("wrong_password", "attacker", "Test")
    
    # Should be locked out
    assert override._is_locked_out()
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `governance.py` | Uses override for emergency governance bypass |
| `user_manager.py` | Admin users can activate override |
| `telemetry.py` | Logs override events |
| `emergency_alert.py` | Triggers alerts on override activation |

---

## Future Enhancements

1. **Argon2 Password Hashing**: Replace SHA-256 with Argon2
2. **Multi-Factor Authentication**: TOTP/U2F support
3. **Immutable Audit Log**: Blockchain or append-only log
4. **Emergency Contact Notifications**: SMS/email on activation
5. **Biometric Authentication**: Fingerprint/face recognition

---

**Last Updated**: 2024-01-20  
**Schema Version**: 2.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/command_override.py]]
