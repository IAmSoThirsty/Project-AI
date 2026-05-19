"""Software Firewall implementation"""

from typing import Dict, Any
from .base import FirewallBase


class SoftwareFirewall(FirewallBase):
    """
    Software Firewall
    User-space firewall implementation
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.user_space = config.get("user_space", True)
        self._process_rules = {}

    def start(self):
        """Start software firewall"""
        self.logger.info("Starting Software Firewall")
        self._active = True
        self._load_process_rules()

    def stop(self):
        """Stop software firewall"""
        self.logger.info("Stopping Software Firewall")
        self._active = False

    def add_rule(self, rule: Dict[str, Any]):
        """Add software firewall rule"""
        self._rules.append(rule)

        # Process-specific rules
        if "process" in rule:
            self._process_rules[rule["process"]] = rule

    def remove_rule(self, rule_id: str):
        """Remove software firewall rule"""
        self._rules = [r for r in self._rules if r.get("id") != rule_id]

    def _load_process_rules(self):
        """Load default process rules"""
        # Allow system processes
        self.add_rule({"id": "allow_system", "process": "system", "action": "allow"})

    def process_packet(self, packet: Dict[str, Any]) -> bool:
        """Process packet through software firewall"""
        if not self._active:
            return True

        # Check process permissions
        process = packet.get("process", "unknown")
        if process in self._process_rules:
            rule = self._process_rules[process]
            allowed = rule.get("action") == "allow"
            self._update_statistics(allowed)
            return allowed

        # Application-level filtering
        if not self._check_application_rules(packet):
            self._update_statistics(False)
            return False

        self._update_statistics(True)
        return True

    def _check_application_rules(self, packet: Dict[str, Any]) -> bool:
        """Check application-level rules"""
        app = packet.get("application", "")

        # Block unauthorized applications
        if app and not self._is_authorized_app(app):
            self.logger.warning(f"Unauthorized application: {app}")
            return False

        return True

    def _is_authorized_app(self, app: str) -> bool:
        """Check if application is authorized"""
        # Simplified authorization check
        return True

    def add_process_rule(self, process: str, action: str):
        """Add rule for specific process"""
        self.add_rule(
            {"id": f"process_{process}", "process": process, "action": action}
        )
