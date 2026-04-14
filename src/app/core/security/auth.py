"""
Production-grade authentication: JWT tokens + argon2 password hashing.

Replaces:
    - Plaintext passwords → argon2-cffi
    - Predictable tokens → PyJWT with expiration
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

# Constants
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# CRITICAL: JWT secret MUST be set in environment for production
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable not set. "
        "Generate a secure key with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )


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
        TokenPayload if valid, None if invalid/expired
    """
    try:
        import jwt
    except ImportError:
        raise RuntimeError(
            "PyJWT not installed. Run: pip install pyjwt"
        )

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
