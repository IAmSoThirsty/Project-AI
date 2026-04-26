---
title: Security & Authentication
category: api
layer: security-layer
audience: [maintainer, expert]
status: production
classification: technical-reference
confidence: verified
requires: [01-API-OVERVIEW.md]
time_estimate: 20min
last_updated: 2025-06-09
version: 2.0.0
---

# Security & Authentication

## Purpose

Production-grade authentication using JWT tokens + Argon2id password hashing + MFA support.

**File**: `src/app/core/security/auth.py` (577 lines)

---

## Core Functions

### Password Hashing

```python
def hash_password(password: str) -> str:
    """
    Argon2id hashing (memory-hard, GPU-resistant)
    Replaces: Plaintext, SHA-256, bcrypt
    """
    from argon2 import PasswordHasher
    ph = PasswordHasher()
    return ph.hash(password)  # Includes salt

def verify_password(password: str, hash_value: str) -> bool:
    """Constant-time verification (timing attack resistant)"""
    from argon2 import PasswordHasher
    from argon2.exceptions import VerifyMismatchError
    
    ph = PasswordHasher()
    try:
        ph.verify(hash_value, password)
        return True
    except VerifyMismatchError:
        return False
```

---

### JWT Tokens

```python
def generate_jwt_token(username: str, role: str = "user") -> str:
    """
    Generate JWT token (24h expiration)
    Algorithm: HS256
    Secret: JWT_SECRET_KEY (environment variable)
    """
    import jwt
    from datetime import datetime, timedelta, timezone
    
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=24)
    
    payload = {
        "sub": username,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp())
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

def verify_jwt_token(token: str) -> TokenPayload | None:
    """
    Verify JWT token
    Checks:
    1. Blacklist (revoked tokens)
    2. Signature
    3. Expiration
    """
    if is_token_revoked(token):
        return None
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return TokenPayload(
            username=payload["sub"],
            role=payload.get("role", "user"),
            issued_at=datetime.fromtimestamp(payload["iat"]),
            expires_at=datetime.fromtimestamp(payload["exp"])
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
```

---

### Refresh Tokens

```python
def generate_refresh_token(username: str, role: str = "user") -> str:
    """
    Generate long-lived refresh token (30 days)
    Used to obtain new access tokens without re-authentication
    """
    expires = now + timedelta(days=30)
    payload = {
        "sub": username,
        "role": role,
        "exp": int(expires.timestamp()),
        "type": "refresh"  # Mark as refresh token
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")
    
    # Store in refresh token registry
    _refresh_token_store[token] = {
        "username": username,
        "issued_at": now,
        "expires_at": expires
    }
    
    return token

def refresh_access_token(refresh_token: str) -> tuple[str, str] | None:
    """
    Exchange refresh token for new access + refresh tokens
    Implements token rotation (old refresh token revoked)
    """
    if refresh_token not in _refresh_token_store:
        return None
    
    payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=["HS256"])
    username = payload["sub"]
    role = payload.get("role", "user")
    
    # Generate new tokens
    new_access_token = generate_jwt_token(username, role)
    new_refresh_token = generate_refresh_token(username, role)
    
    # Revoke old refresh token (rotation)
    revoke_token(refresh_token)
    
    return (new_access_token, new_refresh_token)
```

---

### Token Revocation

```python
def revoke_token(token: str) -> bool:
    """Add token to blacklist (logout)"""
    _token_blacklist.add(token)
    if token in _refresh_token_store:
        del _refresh_token_store[token]
    return True

def is_token_revoked(token: str) -> bool:
    """Check if token is revoked"""
    return token in _token_blacklist

def revoke_all_user_tokens(username: str) -> int:
    """Revoke all tokens for user (logout all sessions)"""
    tokens_to_revoke = [
        token for token, metadata in _refresh_token_store.items()
        if metadata["username"] == username
    ]
    
    for token in tokens_to_revoke:
        revoke_token(token)
    
    return len(tokens_to_revoke)
```

---

## MFA (Multi-Factor Authentication)

### Setup MFA

```python
def setup_mfa(username: str) -> dict:
    """
    Initialize TOTP (Time-based One-Time Password)
    Returns: QR code URL + backup codes
    """
    secret = generate_mfa_secret()  # Base32-encoded
    backup_codes = generate_mfa_backup_codes(count=10)
    
    _mfa_secrets[username] = {
        "secret": secret,
        "backup_codes": backup_codes,
        "enabled": False,  # Must verify first
        "created_at": datetime.now(timezone.utc)
    }
    
    # QR code URL for authenticator apps (Google Authenticator, Authy, etc.)
    qr_url = f"otpauth://totp/Project-AI:{username}?secret={secret}&issuer=Project-AI"
    
    return {
        "secret": secret,
        "qr_url": qr_url,
        "backup_codes": backup_codes
    }
```

### Verify MFA Code

```python
def verify_mfa_code(username: str, code: str) -> bool:
    """
    Verify 6-digit TOTP code or 8-digit backup code
    Uses time window to tolerate clock drift
    """
    if username not in _mfa_secrets:
        return False
    
    mfa_data = _mfa_secrets[username]
    
    # Check backup code (8 digits)
    if len(code) == 8 and code in mfa_data["backup_codes"]:
        mfa_data["backup_codes"].remove(code)  # One-time use
        return True
    
    # Verify TOTP (6 digits)
    if len(code) == 6:
        import pyotp
        totp = pyotp.TOTP(mfa_data["secret"])
        return totp.verify(code, valid_window=1)  # ±30 seconds
    
    return False
```

---

## Environment Configuration

**Required**:
```bash
JWT_SECRET_KEY=<generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'>
```

**Generation**:
```python
import secrets
print(secrets.token_urlsafe(32))
# Output: 'Xy9_k3mZ...' (44 chars)
```

---

## Security Properties

| Feature | Implementation | Protection |
|---------|---------------|------------|
| Password Storage | Argon2id | Memory-hard, GPU-resistant |
| Token Signature | HS256 (HMAC-SHA256) | Tampering prevention |
| Token Expiration | 24h (access), 30d (refresh) | Session hijacking mitigation |
| Token Revocation | Blacklist + rotation | Logout enforcement |
| MFA | TOTP (RFC 6238) | 2FA protection |
| Timing Attacks | Constant-time comparison | Side-channel resistance |

---

## Related Documentation
- **[01-API-OVERVIEW.md](./01-API-OVERVIEW.md)** - Architecture
- **[06-FLASK-WEB-BACKEND.md](./06-FLASK-WEB-BACKEND.md)** - Authentication endpoints
