"""
Command Override System - Privileged control system for disabling safety protocols.

This module provides a privileged command interface that allows authorized users
to override any safety guards, content filters, or security protocols in the system.

Security: Master password hashing uses passlib CryptContext (shared with UserManager),
ensuring secure, salted hashes and verification via passlib schemes.

WARNING: This system grants full control over all safety mechanisms. Use with caution.
"""



import json
import os
from datetime import datetime
from typing import Any


class CommandOverrideSystem:

    """

    Privileged command system for overriding safety protocols.



    Features:

    - Master password authentication

    - Override individual or all safety guards

    - Audit logging of all override commands

    - Per-module safety control

    - Emergency lockdown capability

    """



    def __init__(self, data_dir: str = "data"):

        """Initialize the command override system."""

        self.data_dir = data_dir

        self.config_file = os.path.join(data_dir, "command_override_config.json")

        self.audit_log = os.path.join(data_dir, "command_override_audit.log")



        # Safety protocol states

        self.safety_protocols = {

            "content_filter": True,  # Content filtering for image generation

            "prompt_safety": True,  # Prompt safety checks

            "data_validation": True,  # Input data validation

            "rate_limiting": True,  # Rate limiting for API calls

            "user_approval": True,  # User approval for sensitive operations

            "api_safety": True,  # API safety checks

            "ml_safety": True,  # ML model safety constraints

            "plugin_sandbox": True,  # Plugin sandboxing

            "cloud_encryption": True,  # Cloud sync encryption

            "emergency_only": True,  # Emergency alert restrictions

        }



        # Master override (disables ALL safety protocols)

        self.master_override_active = False



        # Authentication

        self.master_password_hash = None

        self.authenticated = False

        self.auth_timestamp = None



        # Load configuration

        self._load_config()



        # Initialize audit log

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

                # Create default config

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



    def _hash_password(self, password: str) -> str:

        """Hash a password using passlib CryptContext.

        Reuses the shared context from UserManager for consistency.
        """

        # Import here to avoid circular import issues on module load
        from app.core.user_manager import pwd_context
        return pwd_context.hash(password)



    def set_master_password(self, password: str) -> bool:

        """

        Set the master password for override authentication.



        Args:

            password: The master password



        Returns:

            True if password was set successfully

        """

        try:

            self.master_password_hash = self._hash_password(password)

            self._save_config()

            self._log_action("SET_MASTER_PASSWORD", "Master password configured")

            return True

        except Exception as e:

            self._log_action("SET_MASTER_PASSWORD", str(e), success=False)

            return False



    def authenticate(self, password: str) -> bool:

        """

        Authenticate with the master password.



        Args:

            password: The master password



        Returns:

            True if authentication succeeded

        """

        if not self.master_password_hash:

            self._log_action("AUTHENTICATE", "No master password set", success=False)

            return False



        # Verify using passlib CryptContext (shared with UserManager)
        try:
            from app.core.user_manager import pwd_context
            verified = pwd_context.verify(password, self.master_password_hash)
        except Exception:
            verified = False

        if verified:

            self.authenticated = True

            self.auth_timestamp = datetime.now()

            self._log_action("AUTHENTICATE", "Authentication successful")

            return True

        else:

            self._log_action("AUTHENTICATE", "Invalid password", success=False)

            return False



    def logout(self) -> None:

        """Logout and clear authentication."""

        self.authenticated = False

        self.auth_timestamp = None

        self._log_action("LOGOUT", "User logged out")



    def enable_master_override(self) -> bool:

        """

        Enable master override - disables ALL safety protocols.



        Returns:

            True if master override was enabled

        """

        if not self.authenticated:

            self._log_action(

                "MASTER_OVERRIDE", "Authentication required", success=False

            )

            return False



        self.master_override_active = True

        # Disable all safety protocols

        for protocol in self.safety_protocols:

            self.safety_protocols[protocol] = False



        self._save_config()

        self._log_action(

            "MASTER_OVERRIDE", "ALL SAFETY PROTOCOLS DISABLED - MASTER OVERRIDE ACTIVE"

        )

        return True



    def disable_master_override(self) -> bool:

        """

        Disable master override - restores ALL safety protocols.



        Returns:

            True if master override was disabled

        """

        if not self.authenticated:

            self._log_action(

                "DISABLE_MASTER_OVERRIDE", "Authentication required", success=False

            )

            return False



        self.master_override_active = False

        # Re-enable all safety protocols

        for protocol in self.safety_protocols:

            self.safety_protocols[protocol] = True



        self._save_config()

        self._log_action("DISABLE_MASTER_OVERRIDE", "All safety protocols restored")

        return True



    def override_protocol(self, protocol_name: str, enabled: bool) -> bool:

        """

        Override a specific safety protocol.



        Args:

            protocol_name: Name of the protocol to override

            enabled: True to enable protocol, False to disable



        Returns:

            True if override was successful

        """

        if not self.authenticated:

            self._log_action(

                "OVERRIDE_PROTOCOL",

                f"{protocol_name}: Authentication required",

                success=False,

            )

            return False



        if protocol_name not in self.safety_protocols:

            self._log_action(

                "OVERRIDE_PROTOCOL", f"Unknown protocol: {protocol_name}", success=False

            )

            return False



        self.safety_protocols[protocol_name] = enabled

        self._save_config()



        status = "ENABLED" if enabled else "DISABLED"

        self._log_action("OVERRIDE_PROTOCOL", f"{protocol_name} {status}")

        return True



    def is_protocol_enabled(self, protocol_name: str) -> bool:

        """

        Check if a safety protocol is enabled.



        Args:

            protocol_name: Name of the protocol to check



        Returns:

            True if protocol is enabled

        """

        return self.safety_protocols.get(protocol_name, True)



    def get_all_protocols(self) -> dict[str, bool]:

        """Get the status of all safety protocols."""

        return self.safety_protocols.copy()



    def emergency_lockdown(self) -> None:

        """

        Emergency lockdown - immediately enables all safety protocols

        and revokes authentication.

        """

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

        """

        Get the current status of the command override system.



        Returns:

            Dictionary with system status

        """

        return {

            "authenticated": self.authenticated,

            "master_override_active": self.master_override_active,

            "auth_timestamp": (

                self.auth_timestamp.isoformat() if self.auth_timestamp else None

            ),

            "safety_protocols": self.safety_protocols.copy(),

            "has_master_password": self.master_password_hash is not None,

        }



    def get_audit_log(self, lines: int = 50) -> list[str]:

        """

        Retrieve the most recent audit log entries.



        Args:

            lines: Number of lines to retrieve



        Returns:

            List of log entries

        """

        try:

            if os.path.exists(self.audit_log):

                with open(self.audit_log, encoding="utf-8") as f:

                    all_lines = f.readlines()

                    return all_lines[-lines:]

            return []

        except Exception as e:

            return [f"Error reading audit log: {e}"]

