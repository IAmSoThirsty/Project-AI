"""

Command Override System - Privileged control system for disabling safety protocols.

This module provides a privileged command interface that allows authorized users
to override safety guards, content filters, or security protocols in the system.

WARNING: This system grants full control over all safety mechanisms. Use with caution.
"""

import base64
import hashlib
import json
import os
from datetime import datetime
from typing import Any

# Prefer passlib bcrypt if available for secure password hashing
try:
    from passlib.hash import bcrypt as _bcrypt
except Exception:  # pragma: no cover - fallback
    _bcrypt = None


class CommandOverrideSystem:
    """Privileged command system for overriding safety protocols."""

    def __init__(self, data_dir: str = "data"):
        """Initialize the command override system."""
        self.data_dir = data_dir
        # Ensure the base data directory exists to avoid persistence failures
        try:
            os.makedirs(self.data_dir, exist_ok=True)
        except Exception:
            # Best-effort; other methods will also create directories when needed
            pass

        self.config_file = os.path.join(data_dir, "command_override_config.json")
        self.audit_log = os.path.join(data_dir, "command_override_audit.log")

        # Safety protocol states
        self.safety_protocols = {
            "content_filter": True,
            "prompt_safety": True,
            "data_validation": True,
            "rate_limiting": True,
            "user_approval": True,
            "api_safety": True,
            "ml_safety": True,
            "plugin_sandbox": True,
            "cloud_encryption": True,
            "emergency_only": True,
        }

        # Master override (disables ALL safety protocols)
        self.master_override_active = False

        # Authentication
        self.master_password_hash = None
        self.authenticated = False
        self.auth_timestamp = None

        # Load configuration and init audit
        self._load_config()
        self._init_audit_log()

    def _load_config(self) -> None:
        """Load override configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, encoding="utf-8") as f:
                    config = json.load(f)
                    self.master_password_hash = config.get("master_password_hash")
                    self.safety_protocols.update(config.get("safety_protocols", {}))
            else:
                self._save_config()
        except Exception as e:
            print(f"Error loading command override config: {e}")

    def _save_config(self) -> None:
        """Save override configuration to file."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            config = {
                "master_password_hash": self.master_password_hash,
                "safety_protocols": self.safety_protocols,
            }
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error saving command override config: {e}")

    def _init_audit_log(self) -> None:
        """Initialize the audit log file."""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            if not os.path.exists(self.audit_log):
                with open(self.audit_log, "w", encoding="utf-8") as f:
                    f.write("=== Command Override System Audit Log ===\n")
                    f.write(f"Initialized: {datetime.now().isoformat()}\n\n")
        except Exception as e:
            print(f"Error initializing audit log: {e}")

    def _log_action(self, action: str, details: str = "", success: bool = True) -> None:
        """Log an action to the audit log."""
        try:
            timestamp = datetime.now().isoformat()
            status = "SUCCESS" if success else "FAILED"
            log_entry = f"[{timestamp}] {status}: {action}"
            if details:
                log_entry += f" | Details: {details}"
            log_entry += "\n"

            with open(self.audit_log, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Error writing to audit log: {e}")

    def _is_sha256_hash(self, s: str | None) -> bool:
        """Detect if a stored string looks like a SHA256 hex digest."""
        if not s or not isinstance(s, str):
            return False
        return len(s) == 64 and all(c in "0123456789abcdef" for c in s.lower())

    def _hash_with_bcrypt(self, password: str) -> str:
        """Hash password using bcrypt (passlib) when available, otherwise PBKDF2 fallback."""
        if _bcrypt is not None:
            try:
                return _bcrypt.hash(password)
            except Exception:
                pass
        # Fallback to pbkdf2
        salt = os.urandom(16)
        iterations = 100_000
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return f"pbkdf2${iterations}${base64.b64encode(salt).decode()}${base64.b64encode(dk).decode()}"

    def _verify_bcrypt_or_pbkdf2(self, stored: str, password: str) -> bool:
        """Verify password against bcrypt or pbkdf2 fallback format."""
        if not stored:
            return False
        if _bcrypt is not None and stored.startswith("$2"):
            try:
                return _bcrypt.verify(password, stored)
            except Exception:
                return False
        try:
            if stored.startswith("pbkdf2$"):
                parts = stored.split("$")
                if len(parts) == 4:
                    iterations = int(parts[1])
                    salt = base64.b64decode(parts[2])
                    stored_dk = parts[3]
                    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
                    return base64.b64encode(dk).decode() == stored_dk
        except Exception:
            return False
        return False

    def _hash_password(self, password: str) -> str:
        """Hash a password using secure scheme (bcrypt preferred)."""
        return self._hash_with_bcrypt(password)

    def set_master_password(self, password: str) -> bool:
        """Set the master password for override authentication."""
        try:
            self.master_password_hash = self._hash_password(password)
            self._save_config()
            self._log_action("SET_MASTER_PASSWORD", "Master password configured")
            return True
        except Exception as e:
            self._log_action("SET_MASTER_PASSWORD", str(e), success=False)
            return False

    def authenticate(self, password: str) -> bool:
        """Authenticate with the master password. Migrates legacy SHA256 hashes on success."""
        if not self.master_password_hash:
            self._log_action("AUTHENTICATE", "No master password set", success=False)
            return False

        # Legacy SHA256 migration
        if self._is_sha256_hash(self.master_password_hash):
            legacy_hash = self.master_password_hash
            if hashlib.sha256(password.encode("utf-8")).hexdigest() == legacy_hash:
                try:
                    new_hash = self._hash_with_bcrypt(password)
                    self.master_password_hash = new_hash
                    self._save_config()
                    self._log_action("AUTHENTICATE", "Legacy password migrated to stronger hash")
                except Exception:
                    self._log_action(
                        "AUTHENTICATE",
                        "Migration to stronger hash failed",
                        success=False,
                    )
                self.authenticated = True
                self.auth_timestamp = datetime.now()
                self._log_action("AUTHENTICATE", "Authentication successful (legacy migrated)")
                return True
            else:
                self._log_action("AUTHENTICATE", "Invalid password", success=False)
                return False

        # Verify against current hash formats
        if self._verify_bcrypt_or_pbkdf2(self.master_password_hash, password):
            self.authenticated = True
            self.auth_timestamp = datetime.now()
            self._log_action("AUTHENTICATE", "Authentication successful")
            return True

        self._log_action("AUTHENTICATE", "Invalid password", success=False)
        return False

    def logout(self) -> None:
        """Logout and clear authentication."""
        self.authenticated = False
        self.auth_timestamp = None
        self._log_action("LOGOUT", "User logged out")

    def enable_master_override(self) -> bool:
        """Enable master override - disables ALL safety protocols."""
        if not self.authenticated:
            self._log_action("MASTER_OVERRIDE", "Authentication required", success=False)
            return False
        self.master_override_active = True
        for protocol in self.safety_protocols:
            self.safety_protocols[protocol] = False
        self._save_config()
        self._log_action("MASTER_OVERRIDE", "ALL SAFETY PROTOCOLS DISABLED - MASTER OVERRIDE ACTIVE")
        return True

    def disable_master_override(self) -> bool:
        """Disable master override - restores ALL safety protocols."""
        if not self.authenticated:
            self._log_action("DISABLE_MASTER_OVERRIDE", "Authentication required", success=False)
            return False
        self.master_override_active = False
        for protocol in self.safety_protocols:
            self.safety_protocols[protocol] = True
        self._save_config()
        self._log_action("DISABLE_MASTER_OVERRIDE", "All safety protocols restored")
        return True

    def override_protocol(self, protocol_name: str, enabled: bool) -> bool:
        """Override a specific safety protocol."""
        if not self.authenticated:
            self._log_action(
                "OVERRIDE_PROTOCOL",
                f"{protocol_name}: Authentication required",
                success=False,
            )
            return False
        if protocol_name not in self.safety_protocols:
            self._log_action("OVERRIDE_PROTOCOL", f"Unknown protocol: {protocol_name}", success=False)
            return False
        self.safety_protocols[protocol_name] = enabled
        self._save_config()
        status = "ENABLED" if enabled else "DISABLED"
        self._log_action("OVERRIDE_PROTOCOL", f"{protocol_name} {status}")
        return True

    def is_protocol_enabled(self, protocol_name: str) -> bool:
        """Check if a safety protocol is enabled."""
        return self.safety_protocols.get(protocol_name, True)

    def get_all_protocols(self) -> dict[str, bool]:
        """Get the status of all safety protocols."""
        return self.safety_protocols.copy()

    def emergency_lockdown(self) -> None:
        """Emergency lockdown - enables all safety protocols and revokes auth."""
        self.master_override_active = False
        for protocol in self.safety_protocols:
            self.safety_protocols[protocol] = True
        self.authenticated = False
        self.auth_timestamp = None
        self._save_config()
        self._log_action(
            "EMERGENCY_LOCKDOWN",
            "EMERGENCY LOCKDOWN ACTIVATED - ALL PROTOCOLS RESTORED",
        )

    def get_status(self) -> dict[str, Any]:
        """Get the current status of the command override system."""
        return {
            "authenticated": self.authenticated,
            "master_override_active": self.master_override_active,
            "auth_timestamp": (self.auth_timestamp.isoformat() if self.auth_timestamp else None),
            "safety_protocols": self.safety_protocols.copy(),
            "has_master_password": self.master_password_hash is not None,
        }

    def get_audit_log(self, lines: int = 50) -> list[str]:
        """Retrieve the most recent audit log entries."""
        try:
            if os.path.exists(self.audit_log):
                with open(self.audit_log, encoding="utf-8") as f:
                    all_lines = f.readlines()
                    return all_lines[-lines:]
            return []
        except Exception as e:
            return [f"Error reading audit log: {e}"]
