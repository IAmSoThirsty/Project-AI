"""
Security utilities (authentication, authorization, input validation)
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import jwt

from .config import settings
from .logging_config import logger
from .metrics import AUTH_ATTEMPTS


def verify_api_key(api_key: str) -> bool:
    """Verify API key"""
    # Constant-time comparison to prevent timing attacks
    valid = any(
        secrets.compare_digest(api_key, valid_key) for valid_key in settings.API_KEYS
    )

    AUTH_ATTEMPTS.labels(status="success" if valid else "failure").inc()

    if not valid:
        logger.warning(f"Invalid API key attempt: {api_key[:8]}...")

    return valid


def create_jwt_token(subject: str, claims: Optional[Dict[str, Any]] = None) -> str:
    """Create JWT token"""
    now = datetime.utcnow()
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(hours=settings.JWT_EXPIRY_HOURS),
        "iss": settings.SERVICE_NAME,
    }

    if claims:
        payload.update(claims)

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "require": ["sub", "exp", "iat"],
            },
            leeway=10,  # 10 second clock skew tolerance
        )

        # Validate issuer
        if payload.get("iss") != settings.SERVICE_NAME:
            logger.warning(f"Invalid token issuer: {payload.get('iss')}")
            AUTH_ATTEMPTS.labels(status="failure").inc()
            return None

        AUTH_ATTEMPTS.labels(status="success").inc()
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Expired JWT token")
        AUTH_ATTEMPTS.labels(status="failure").inc()
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {e}")
        AUTH_ATTEMPTS.labels(status="failure").inc()
        return None


# RBAC - Role-Based Access Control
class Permission:
    """Permission definitions"""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class Role:
    """Role definitions with permissions"""

    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"


# Role -> Permissions mapping
ROLE_PERMISSIONS: Dict[str, List[str]] = {
    Role.VIEWER: [Permission.READ],
    Role.EDITOR: [Permission.READ, Permission.WRITE],
    Role.ADMIN: [
        Permission.READ,
        Permission.WRITE,
        Permission.DELETE,
        Permission.ADMIN,
    ],
}


def has_permission(user_role: str, required_permission: str) -> bool:
    """Check if user role has required permission"""
    permissions = ROLE_PERMISSIONS.get(user_role, [])
    return required_permission in permissions


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks"""
    # Truncate to max length
    text = text[:max_length]

    # Remove null bytes
    text = text.replace("\x00", "")

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for logging/storage"""
    return hashlib.sha256(data.encode()).hexdigest()[:16]
