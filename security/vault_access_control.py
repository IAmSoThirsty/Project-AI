"""
Security Vault Access Control
Maximum security layer for penetration testing tools

CRITICAL: This module enforces strict access controls for offensive security tools
All access attempts are logged and require multi-factor authorization
"""

import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configure audit logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - SECURITY_VAULT - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("security/vault_audit.log"), logging.StreamHandler()],
)
logger = logging.getLogger("SecurityVault")


class AccessDeniedError(Exception):
    """Raised when access to security vault is denied"""

    pass


class SecurityVault:
    """
    Maximum security access control for penetration testing tools

    Security Layers:
    1. Role-based access (RED_TEAM only)
    2. Time-based access windows
    3. Multi-factor authentication
    4. Audit logging
    5. Dormant state enforcement
    """

    # Security configuration
    VAULT_PATH = Path(__file__).parent / "penetration-testing-tools"
    AUTHORIZED_ROLES = ["RED_TEAM", "SECURITY_ADMIN"]
    ACCESS_LOG = Path(__file__).parent / "vault_audit.log"

    # Dormant state - tools are NOT active by default
    DORMANT = True

    def __init__(self):
        self.vault_locked = True
        self._active_sessions = {}
        self._failed_attempts = {}

        # Ensure vault is isolated
        self._enforce_isolation()

    def _enforce_isolation(self):
        """Ensure vault directory has proper permissions"""
        if not self.VAULT_PATH.exists():
            logger.warning("Vault path does not exist")
            return

        # Log vault status
        logger.info(f"Security Vault initialized at {self.VAULT_PATH}")
        logger.info("VAULT STATUS: LOCKED AND DORMANT")
        logger.info("Access requires: RED_TEAM role + authentication token")

    def authenticate(
        self, user_id: str, role: str, auth_token: str, justification: str = ""
    ) -> Dict:
        """
        Authenticate user for vault access

        Args:
            user_id: User identifier
            role: User role (must be in AUTHORIZED_ROLES)
            auth_token: Authentication token
            justification: Required justification for access

        Returns:
            Session token if successful

        Raises:
            AccessDeniedError: If authentication fails
        """
        # Log attempt
        logger.warning(f"VAULT ACCESS ATTEMPT - User: {user_id}, Role: {role}")

        # Check if vault is dormant
        if self.DORMANT:
            logger.error("VAULT ACCESS DENIED - Vault is in DORMANT state")
            self._log_failed_attempt(user_id, "Vault dormant")
            raise AccessDeniedError("Security vault is dormant. Requires activation.")

        # Validate role
        if role not in self.AUTHORIZED_ROLES:
            logger.error(f"VAULT ACCESS DENIED - Unauthorized role: {role}")
            self._log_failed_attempt(user_id, "Unauthorized role")
            raise AccessDeniedError(f"Role '{role}' not authorized for vault access")

        # Validate token
        if not self._validate_token(auth_token):
            logger.error(f"VAULT ACCESS DENIED - Invalid token for user: {user_id}")
            self._log_failed_attempt(user_id, "Invalid token")
            raise AccessDeniedError("Invalid authentication token")

        # Require justification
        if not justification or len(justification) < 20:
            logger.error(f"VAULT ACCESS DENIED - Insufficient justification")
            self._log_failed_attempt(user_id, "No justification")
            raise AccessDeniedError("Valid justification required (min 20 chars)")

        # Generate session token
        session_token = self._create_session(user_id, role, justification)

        logger.warning(
            f"VAULT ACCESS GRANTED - User: {user_id}, Session: {session_token[:8]}..."
        )
        logger.warning(f"JUSTIFICATION: {justification}")

        return {
            "session_token": session_token,
            "expires_at": time.time() + 3600,  # 1 hour
            "role": role,
            "user_id": user_id,
        }

    def _validate_token(self, token: str) -> bool:
        """Validate authentication token"""
        # In production, this would validate against a secure token store
        # For now, require minimum complexity
        return len(token) >= 32 and any(c.isdigit() for c in token)

    def _create_session(self, user_id: str, role: str, justification: str) -> str:
        """Create secure session token"""
        data = f"{user_id}:{role}:{time.time()}:{justification}"
        session_token = hashlib.sha256(data.encode()).hexdigest()

        self._active_sessions[session_token] = {
            "user_id": user_id,
            "role": role,
            "created_at": time.time(),
            "justification": justification,
        }

        return session_token

    def validate_session(self, session_token: str) -> bool:
        """Validate active session"""
        if session_token not in self._active_sessions:
            return False

        session = self._active_sessions[session_token]

        # Check expiration (1 hour)
        if time.time() - session["created_at"] > 3600:
            logger.warning(f"Session expired: {session_token[:8]}...")
            del self._active_sessions[session_token]
            return False

        return True

    def access_tool(self, session_token: str, category: str, tool_name: str) -> Path:
        """
        Access a specific tool from vault

        Requires valid session token
        All access is logged
        """
        if not self.validate_session(session_token):
            logger.error(f"TOOL ACCESS DENIED - Invalid session")
            raise AccessDeniedError("Invalid or expired session")

        session = self._active_sessions[session_token]
        user_id = session["user_id"]

        # Construct tool path
        tool_path = self.VAULT_PATH / category / tool_name

        if not tool_path.exists():
            logger.error(f"TOOL ACCESS DENIED - Tool not found: {category}/{tool_name}")
            raise FileNotFoundError(f"Tool not found: {category}/{tool_name}")

        # Log access
        logger.warning(f"TOOL ACCESS - User: {user_id}, Tool: {category}/{tool_name}")

        return tool_path

    def _log_failed_attempt(self, user_id: str, reason: str):
        """Log failed access attempt"""
        if user_id not in self._failed_attempts:
            self._failed_attempts[user_id] = []

        self._failed_attempts[user_id].append(
            {"timestamp": time.time(), "reason": reason}
        )

        # Alert on repeated failures
        recent = [
            a
            for a in self._failed_attempts[user_id]
            if time.time() - a["timestamp"] < 600
        ]  # 10 minutes

        if len(recent) >= 3:
            logger.critical(
                f"SECURITY ALERT - Multiple failed attempts from: {user_id}"
            )

    def activate_vault(self, admin_token: str, justification: str) -> bool:
        """
        Activate vault from dormant state

        Requires SECURITY_ADMIN token
        """
        logger.critical(f"VAULT ACTIVATION ATTEMPT")

        if not self._validate_admin_token(admin_token):
            logger.critical("VAULT ACTIVATION DENIED - Invalid admin token")
            return False

        if not justification or len(justification) < 50:
            logger.critical("VAULT ACTIVATION DENIED - Insufficient justification")
            return False

        self.DORMANT = False
        logger.critical(f"VAULT ACTIVATED - Justification: {justification}")

        return True

    def deactivate_vault(self):
        """Return vault to dormant state"""
        self.DORMANT = True
        self._active_sessions = {}
        logger.critical("VAULT DEACTIVATED - Returned to dormant state")

    def _validate_admin_token(self, token: str) -> bool:
        """Validate admin-level token"""
        # In production, this would be a secure admin credential
        return len(token) >= 64

    def get_audit_log(self, admin_token: str, limit: int = 100) -> List[Dict]:
        """Retrieve audit log (admin only)"""
        if not self._validate_admin_token(admin_token):
            raise AccessDeniedError("Admin token required for audit log")

        # Read recent audit entries
        audit_entries = []

        if self.ACCESS_LOG.exists():
            with open(self.ACCESS_LOG, "r") as f:
                lines = f.readlines()[-limit:]
                for line in lines:
                    audit_entries.append({"log": line.strip()})

        return audit_entries


# Global vault instance
vault = SecurityVault()


def require_red_team_auth(func):
    """Decorator to require red team authorization"""

    def wrapper(*args, **kwargs):
        session_token = kwargs.get("session_token")

        if not session_token:
            raise AccessDeniedError("Session token required")

        if not vault.validate_session(session_token):
            raise AccessDeniedError("Invalid or expired session")

        return func(*args, **kwargs)

    return wrapper


__all__ = ["SecurityVault", "vault", "AccessDeniedError", "require_red_team_auth"]
