"""
Production-grade authentication: JWT tokens + argon2 password hashing.

Replaces:
    - Plaintext passwords → argon2-cffi
    - Predictable tokens → PyJWT with expiration
"""

from __future__ import annotations

import logging
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Constants
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
JWT_REFRESH_EXPIRATION_DAYS = 30

# CRITICAL: JWT secret MUST be set in environment for production
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable not set. "
        "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )

# Token blacklist (in-memory for now, use Redis in production)
_token_blacklist: set[str] = set()
_refresh_token_store: dict[str, dict] = {}  # {refresh_token: {username, issued_at, expires_at}}


@dataclass
class TokenPayload:
    """JWT token payload structure."""

    username: str
    role: str
    issued_at: datetime
    expires_at: datetime


def hash_password(password: str) -> str:
    """
    Hash password using argon2id (secure, memory-hard algorithm).

    Replaces plaintext and weak SHA-256 hashing.

    Args:
        password: Plain text password

    Returns:
        Argon2 hash string (includes salt, can be stored directly)
    """
    try:
        from argon2 import PasswordHasher

        ph = PasswordHasher()
        return ph.hash(password)
    except ImportError:
        logger.error("argon2-cffi not installed - falling back to bcrypt")
        import bcrypt

        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hash_value: str) -> bool:
    """
    Verify password against argon2 hash.

    Args:
        password: Plain text password to verify
        hash_value: Stored argon2 hash

    Returns:
        True if password matches, False otherwise
    """
    try:
        from argon2 import PasswordHasher
        from argon2.exceptions import VerifyMismatchError

        ph = PasswordHasher()
        try:
            ph.verify(hash_value, password)
            return True
        except VerifyMismatchError:
            return False
    except ImportError:
        logger.error("argon2-cffi not installed - falling back to bcrypt")
        import bcrypt

        return bcrypt.checkpw(password.encode(), hash_value.encode())


def generate_jwt_token(username: str, role: str = "user") -> str:
    """
    Generate JWT token with expiration.

    Replaces predictable token-{uuid} pattern with secure JWT.

    Args:
        username: User identifier
        role: User role (user, admin, superuser)

    Returns:
        JWT token string
    """
    try:
        import jwt
    except ImportError:
        raise RuntimeError(
            "PyJWT not installed. Run: pip install pyjwt"
        )

    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=JWT_EXPIRATION_HOURS)

    payload = {
        "sub": username,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    logger.info(f"Generated JWT for user: {username}, expires: {expires}")

    return token


def verify_jwt_token(token: str) -> TokenPayload | None:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token string

    Returns:
        TokenPayload if valid, None if invalid/expired/revoked
    """
    try:
        import jwt
    except ImportError:
        raise RuntimeError(
            "PyJWT not installed. Run: pip install pyjwt"
        )

    # Check token blacklist (revocation)
    if is_token_revoked(token):
        logger.warning("JWT token has been revoked")
        return None

    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )

        return TokenPayload(
            username=payload["sub"],
            role=payload.get("role", "user"),
            issued_at=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        return None


def generate_refresh_token(username: str, role: str = "user") -> str:
    """
    Generate a long-lived refresh token.
    
    Refresh tokens can be exchanged for new access tokens without re-authentication.
    
    Args:
        username: User identifier
        role: User role
        
    Returns:
        Refresh token string (JWT)
    """
    try:
        import jwt
    except ImportError:
        raise RuntimeError("PyJWT not installed. Run: pip install pyjwt")
    
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=JWT_REFRESH_EXPIRATION_DAYS)
    
    payload = {
        "sub": username,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
        "type": "refresh"  # Mark as refresh token
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    # Store refresh token metadata
    _refresh_token_store[token] = {
        "username": username,
        "issued_at": now,
        "expires_at": expires
    }
    
    logger.info(f"Generated refresh token for user: {username}, expires: {expires}")
    return token


def refresh_access_token(refresh_token: str) -> tuple[str, str] | None:
    """
    Exchange refresh token for new access token and refresh token.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        Tuple of (new_access_token, new_refresh_token) or None if invalid
    """
    try:
        import jwt
    except ImportError:
        raise RuntimeError("PyJWT not installed. Run: pip install pyjwt")
    
    # Verify refresh token
    if is_token_revoked(refresh_token):
        logger.warning("Refresh token has been revoked")
        return None
    
    if refresh_token not in _refresh_token_store:
        logger.warning("Refresh token not found in store")
        return None
    
    try:
        payload = jwt.decode(
            refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )
        
        if payload.get("type") != "refresh":
            logger.warning("Token is not a refresh token")
            return None
        
        username = payload["sub"]
        role = payload.get("role", "user")
        
        # Generate new access token and refresh token
        new_access_token = generate_jwt_token(username, role)
        new_refresh_token = generate_refresh_token(username, role)
        
        # Revoke old refresh token (rotation)
        revoke_token(refresh_token)
        
        logger.info(f"Refreshed access token for user: {username}")
        return (new_access_token, new_refresh_token)
        
    except jwt.ExpiredSignatureError:
        logger.warning("Refresh token expired")
        # Clean up from store
        if refresh_token in _refresh_token_store:
            del _refresh_token_store[refresh_token]
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid refresh token: {e}")
        return None


def revoke_token(token: str) -> bool:
    """
    Revoke a token (add to blacklist).
    
    Revoked tokens cannot be used even if not expired.
    
    Args:
        token: JWT token to revoke
        
    Returns:
        True if revoked, False if already revoked
    """
    if token in _token_blacklist:
        return False
    
    _token_blacklist.add(token)
    
    # Also remove from refresh token store if it's a refresh token
    if token in _refresh_token_store:
        del _refresh_token_store[token]
    
    logger.info("Token revoked")
    return True


def is_token_revoked(token: str) -> bool:
    """
    Check if token is revoked.
    
    Args:
        token: JWT token
        
    Returns:
        True if revoked, False otherwise
    """
    return token in _token_blacklist


def revoke_all_user_tokens(username: str) -> int:
    """
    Revoke all tokens for a specific user.
    
    Used for logout-all-sessions or security incidents.
    
    Args:
        username: Username whose tokens to revoke
        
    Returns:
        Number of tokens revoked
    """
    revoked_count = 0
    
    # Revoke all refresh tokens for user
    tokens_to_revoke = [
        token for token, metadata in _refresh_token_store.items()
        if metadata["username"] == username
    ]
    
    for token in tokens_to_revoke:
        revoke_token(token)
        revoked_count += 1
    
    logger.info(f"Revoked {revoked_count} tokens for user: {username}")
    return revoked_count


# ============================================================================
# MFA (TOTP - Time-based One-Time Password) Support
# ============================================================================

# MFA secret store (in-memory, use database in production)
_mfa_secrets: dict[str, dict] = {}  # {username: {secret, backup_codes, enabled}}


def generate_mfa_secret() -> str:
    """
    Generate a random MFA secret (base32 encoded).
    
    Returns:
        Base32-encoded secret string (16 bytes = 26 chars)
    """
    # Generate 16 random bytes (128 bits)
    random_bytes = secrets.token_bytes(16)
    # Encode as base32 for TOTP compatibility
    import base64
    secret = base64.b32encode(random_bytes).decode('utf-8')
    return secret


def generate_mfa_backup_codes(count: int = 10) -> list[str]:
    """
    Generate backup codes for MFA recovery.
    
    Args:
        count: Number of backup codes to generate
        
    Returns:
        List of backup codes (8-digit codes)
    """
    backup_codes = []
    for _ in range(count):
        # Generate 8-digit code
        code = f"{secrets.randbelow(100000000):08d}"
        backup_codes.append(code)
    return backup_codes


def setup_mfa(username: str) -> dict[str, Any]:
    """
    Set up MFA for a user.
    
    Args:
        username: User to enable MFA for
        
    Returns:
        Dictionary with secret, qr_url, and backup_codes
    """
    secret = generate_mfa_secret()
    backup_codes = generate_mfa_backup_codes()
    
    # Store MFA data
    _mfa_secrets[username] = {
        "secret": secret,
        "backup_codes": backup_codes,
        "enabled": False,  # User must verify first
        "created_at": datetime.now(timezone.utc)
    }
    
    # Generate QR code URL for authenticator apps
    # Format: otpauth://totp/Project-AI:username?secret=SECRET&issuer=Project-AI
    qr_url = f"otpauth://totp/Project-AI:{username}?secret={secret}&issuer=Project-AI"
    
    logger.info(f"MFA setup initiated for user: {username}")
    
    return {
        "secret": secret,
        "qr_url": qr_url,
        "backup_codes": backup_codes
    }


def verify_mfa_code(username: str, code: str) -> bool:
    """
    Verify TOTP code for user.
    
    Args:
        username: Username
        code: 6-digit TOTP code or 8-digit backup code
        
    Returns:
        True if code is valid, False otherwise
    """
    if username not in _mfa_secrets:
        logger.warning(f"MFA not set up for user: {username}")
        return False
    
    mfa_data = _mfa_secrets[username]
    
    # Check backup code first (8 digits)
    if len(code) == 8 and code in mfa_data["backup_codes"]:
        # Remove used backup code
        mfa_data["backup_codes"].remove(code)
        logger.info(f"Backup code used for user: {username}")
        return True
    
    # Verify TOTP code (6 digits)
    if len(code) == 6:
        try:
            import pyotp
            totp = pyotp.TOTP(mfa_data["secret"])
            
            # Verify with time window (allow 1 step before/after for clock drift)
            is_valid = totp.verify(code, valid_window=1)
            
            if is_valid:
                logger.info(f"TOTP code verified for user: {username}")
            else:
                logger.warning(f"Invalid TOTP code for user: {username}")
            
            return is_valid
            
        except ImportError:
            logger.error("pyotp not installed. Run: pip install pyotp")
            return False
    
    logger.warning(f"Invalid MFA code format for user: {username}")
    return False


def enable_mfa(username: str, verification_code: str) -> bool:
    """
    Enable MFA after verifying the setup code.
    
    Args:
        username: Username
        verification_code: 6-digit TOTP code to verify setup
        
    Returns:
        True if MFA enabled successfully, False otherwise
    """
    if username not in _mfa_secrets:
        logger.warning(f"MFA not set up for user: {username}")
        return False
    
    # Verify code before enabling
    if verify_mfa_code(username, verification_code):
        _mfa_secrets[username]["enabled"] = True
        logger.info(f"MFA enabled for user: {username}")
        return True
    else:
        logger.warning(f"Failed to enable MFA for user: {username} - invalid code")
        return False


def disable_mfa(username: str, verification_code: str) -> bool:
    """
    Disable MFA for a user (requires verification).
    
    Args:
        username: Username
        verification_code: 6-digit TOTP code or 8-digit backup code
        
    Returns:
        True if MFA disabled successfully, False otherwise
    """
    if username not in _mfa_secrets:
        return False
    
    # Verify code before disabling
    if verify_mfa_code(username, verification_code):
        del _mfa_secrets[username]
        logger.info(f"MFA disabled for user: {username}")
        return True
    else:
        logger.warning(f"Failed to disable MFA for user: {username} - invalid code")
        return False


def is_mfa_enabled(username: str) -> bool:
    """
    Check if MFA is enabled for a user.
    
    Args:
        username: Username
        
    Returns:
        True if MFA is enabled, False otherwise
    """
    return username in _mfa_secrets and _mfa_secrets[username].get("enabled", False)


def get_mfa_backup_codes(username: str, verification_code: str) -> list[str] | None:
    """
    Get remaining backup codes for a user.
    
    Args:
        username: Username
        verification_code: 6-digit TOTP code to verify request
        
    Returns:
        List of remaining backup codes or None if verification fails
    """
    if username not in _mfa_secrets:
        return None
    
    # Verify code before returning backup codes
    if verify_mfa_code(username, verification_code):
        return _mfa_secrets[username]["backup_codes"]
    else:
        logger.warning(f"Failed to retrieve backup codes for user: {username} - invalid code")
        return None


def regenerate_mfa_backup_codes(username: str, verification_code: str) -> list[str] | None:
    """
    Regenerate backup codes for a user.
    
    Args:
        username: Username
        verification_code: 6-digit TOTP code to verify request
        
    Returns:
        New list of backup codes or None if verification fails
    """
    if username not in _mfa_secrets:
        return None
    
    # Verify code before regenerating
    if verify_mfa_code(username, verification_code):
        new_codes = generate_mfa_backup_codes()
        _mfa_secrets[username]["backup_codes"] = new_codes
        logger.info(f"Backup codes regenerated for user: {username}")
        return new_codes
    else:
        logger.warning(f"Failed to regenerate backup codes for user: {username} - invalid code")
        return None
