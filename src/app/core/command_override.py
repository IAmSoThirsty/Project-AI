"""

Command Override System - Direct control system for managing safety protocols.

This module provides a direct interface for managing safety guards, content filters,
or security protocols in the system.

WARNING: This system grants control over safety mechanisms. Use with caution.
"""

import json
import os
from datetime import datetime
from typing import Any


class CommandOverrideSystem:
    """Direct command system for managing safety protocols."""

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

        # Load configuration and init audit
        self._load_config()
        self._init_audit_log()

    def _load_config(self) -> None:
        """Load override configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, encoding="utf-8") as f:
                    config = json.load(f)
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

    def enable_master_override(self) -> bool:
        """Enable master override - disables ALL safety protocols."""
        self.master_override_active = True
        for protocol in self.safety_protocols:
            self.safety_protocols[protocol] = False
        self._save_config()
        self._log_action(
            "MASTER_OVERRIDE", "ALL SAFETY PROTOCOLS DISABLED - MASTER OVERRIDE ACTIVE"
        )
        return True

    def disable_master_override(self) -> bool:
        """Disable master override - restores ALL safety protocols."""
        self.master_override_active = False
        for protocol in self.safety_protocols:
            self.safety_protocols[protocol] = True
        self._save_config()
        self._log_action("DISABLE_MASTER_OVERRIDE", "All safety protocols restored")
        return True

    def override_protocol(self, protocol_name: str, enabled: bool) -> bool:
        """Override a specific safety protocol."""
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
        """Check if a safety protocol is enabled."""
        return self.safety_protocols.get(protocol_name, True)

    def get_all_protocols(self) -> dict[str, bool]:
        """Get the status of all safety protocols."""
        return self.safety_protocols.copy()

    def emergency_lockdown(self) -> None:
        """Emergency lockdown - enables all safety protocols."""
        self.master_override_active = False
        for protocol in self.safety_protocols:
            self.safety_protocols[protocol] = True
        self._save_config()
        self._log_action(
            "EMERGENCY_LOCKDOWN",
            "EMERGENCY LOCKDOWN ACTIVATED - ALL PROTOCOLS RESTORED",
        )

    def get_status(self) -> dict[str, Any]:
        """Get the current status of the command override system."""
        return {
            "master_override_active": self.master_override_active,
            "safety_protocols": self.safety_protocols.copy(),
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
