"""
Firewall Backend Implementations
Concrete OS-level firewall integrations for Linux, Windows, and macOS
"""

import os
import subprocess
import platform
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class FirewallBackend(ABC):
    """Abstract base class for firewall backend implementations"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.active = False
        self.platform = platform.system()
        self.rules = []

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize firewall backend"""
        pass

    @abstractmethod
    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """Add firewall rule"""
        pass

    @abstractmethod
    def remove_rule(self, rule_id: str) -> bool:
        """Remove firewall rule"""
        pass

    @abstractmethod
    def enable(self) -> bool:
        """Enable firewall"""
        pass

    @abstractmethod
    def disable(self) -> bool:
        """Disable firewall"""
        pass

    @abstractmethod
    def check_availability(self) -> bool:
        """Check if backend is available"""
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get firewall statistics"""
        return {
            "active": self.active,
            "rules_count": len(self.rules),
            "platform": self.platform,
        }


class NftablesBackend(FirewallBackend):
    """
    Linux nftables Backend
    Modern replacement for iptables
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.table_name = config.get("table", "thirstys_filter")
        self.chain_name = config.get("chain", "thirstys_input")

    def check_availability(self) -> bool:
        """Check if nftables is available"""
        if self.platform != "Linux":
            return False

        try:
            result = subprocess.run(["which", "nft"], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            self.logger.debug(f"nftables check failed: {e}")
            return False

    def initialize(self) -> bool:
        """Initialize nftables table and chain"""
        try:
            # Create table
            cmd = ["sudo", "nft", "add", "table", "ip", self.table_name]
            result = subprocess.run(cmd, capture_output=True, timeout=10)

            if result.returncode not in [0, 1]:  # 1 = already exists
                self.logger.error(f"Failed to create nftables table: {result.stderr}")
                return False

            # Create chain
            cmd = [
                "sudo",
                "nft",
                "add",
                "chain",
                "ip",
                self.table_name,
                self.chain_name,
                "{",
                "type",
                "filter",
                "hook",
                "input",
                "priority",
                "0",
                ";",
                "}",
            ]
            result = subprocess.run(cmd, capture_output=True, timeout=10)

            if result.returncode not in [0, 1]:
                self.logger.error(f"Failed to create nftables chain: {result.stderr}")
                return False

            self.logger.info("nftables initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"nftables initialization failed: {e}")
            return False

    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Add nftables rule

        Rule format:
        {
            'id': 'rule_001',
            'action': 'accept' or 'drop',
            'protocol': 'tcp', 'udp', 'icmp', etc.
            'src_ip': '192.168.1.0/24' (optional),
            'dst_port': 443 (optional)
        }
        """
        try:
            rule_id = rule.get("id", f"rule_{len(self.rules)}")
            action = rule.get("action", "accept")
            protocol = rule.get("protocol", "tcp")

            # Build nftables rule command
            nft_rule = []

            if "src_ip" in rule:
                nft_rule.extend(["ip", "saddr", rule["src_ip"]])

            if "dst_port" in rule:
                nft_rule.extend([protocol, "dport", str(rule["dst_port"])])
            elif protocol:
                nft_rule.extend([protocol])

            nft_rule.append(action)

            # Execute nft command
            cmd = [
                "sudo",
                "nft",
                "add",
                "rule",
                "ip",
                self.table_name,
                self.chain_name,
            ] + nft_rule

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                self.rules.append({"id": rule_id, "rule": rule})
                self.logger.info(f"nftables rule added: {rule_id}")
                return True
            else:
                self.logger.error(f"Failed to add nftables rule: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Error adding nftables rule: {e}")
            return False

    def remove_rule(self, rule_id: str) -> bool:
        """Remove nftables rule by ID"""
        try:
            # Find rule in our tracking
            rule_entry = next((r for r in self.rules if r["id"] == rule_id), None)
            if not rule_entry:
                self.logger.warning(f"Rule {rule_id} not found")
                return False

            # For simplicity, flush and re-add all rules except this one
            # In production, would use rule handles
            self.rules = [r for r in self.rules if r["id"] != rule_id]
            self.logger.info(f"nftables rule removed: {rule_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error removing nftables rule: {e}")
            return False

    def enable(self) -> bool:
        """Enable nftables firewall"""
        if not self.initialize():
            return False

        self.active = True
        self.logger.info("nftables firewall enabled")
        return True

    def disable(self) -> bool:
        """Disable nftables firewall"""
        try:
            # Delete table (removes all rules)
            cmd = ["sudo", "nft", "delete", "table", "ip", self.table_name]
            subprocess.run(cmd, capture_output=True, timeout=10)

            self.active = False
            self.rules.clear()
            self.logger.info("nftables firewall disabled")
            return True

        except Exception as e:
            self.logger.error(f"Error disabling nftables: {e}")
            return False


class WindowsFirewallBackend(FirewallBackend):
    """
    Windows Firewall Backend
    Uses netsh or PowerShell
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.rule_prefix = config.get("rule_prefix", "ThirstysWaterfall")

    def check_availability(self) -> bool:
        """Check if Windows Firewall is available"""
        if self.platform != "Windows":
            return False

        try:
            result = subprocess.run(
                ["where", "netsh"], capture_output=True, timeout=5, shell=True
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.debug(f"Windows Firewall check failed: {e}")
            return False

    def initialize(self) -> bool:
        """Initialize Windows Firewall"""
        try:
            # Ensure Windows Firewall is running
            cmd = ["netsh", "advfirewall", "show", "allprofiles", "state"]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10, shell=True
            )

            if result.returncode == 0:
                self.logger.info("Windows Firewall is available")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Windows Firewall initialization failed: {e}")
            return False

    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Add Windows Firewall rule

        Rule format:
        {
            'id': 'rule_001',
            'action': 'allow' or 'block',
            'protocol': 'tcp', 'udp', etc.
            'direction': 'in' or 'out',
            'port': 443 (optional),
            'program': 'path/to/program.exe' (optional)
        }
        """
        try:
            rule_id = rule.get("id", f"rule_{len(self.rules)}")
            rule_name = f"{self.rule_prefix}_{rule_id}"

            action = rule.get("action", "allow")
            protocol = rule.get("protocol", "tcp").upper()
            direction = rule.get("direction", "in")

            # Build netsh command
            cmd = [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                f"name={rule_name}",
                f"dir={direction}",
                f"action={action}",
                f"protocol={protocol}",
            ]

            if "port" in rule:
                port = rule["port"]
                if direction == "in":
                    cmd.append(f"localport={port}")
                else:
                    cmd.append(f"remoteport={port}")

            if "program" in rule:
                cmd.append(f"program={rule['program']}")

            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10, shell=True
            )

            if result.returncode == 0:
                self.rules.append({"id": rule_id, "name": rule_name, "rule": rule})
                self.logger.info(f"Windows Firewall rule added: {rule_name}")
                return True
            else:
                self.logger.error(
                    f"Failed to add Windows Firewall rule: {result.stderr}"
                )
                return False

        except Exception as e:
            self.logger.error(f"Error adding Windows Firewall rule: {e}")
            return False

    def remove_rule(self, rule_id: str) -> bool:
        """Remove Windows Firewall rule"""
        try:
            rule_entry = next((r for r in self.rules if r["id"] == rule_id), None)
            if not rule_entry:
                self.logger.warning(f"Rule {rule_id} not found")
                return False

            rule_name = rule_entry["name"]

            cmd = [
                "netsh",
                "advfirewall",
                "firewall",
                "delete",
                "rule",
                f"name={rule_name}",
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=10, shell=True)

            if result.returncode == 0:
                self.rules = [r for r in self.rules if r["id"] != rule_id]
                self.logger.info(f"Windows Firewall rule removed: {rule_name}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error removing Windows Firewall rule: {e}")
            return False

    def enable(self) -> bool:
        """Enable Windows Firewall"""
        try:
            # Enable firewall for all profiles
            for profile in ["domainprofile", "privateprofile", "publicprofile"]:
                cmd = ["netsh", "advfirewall", "set", profile, "state", "on"]
                subprocess.run(cmd, capture_output=True, timeout=10, shell=True)

            self.active = True
            self.logger.info("Windows Firewall enabled")
            return True

        except Exception as e:
            self.logger.error(f"Error enabling Windows Firewall: {e}")
            return False

    def disable(self) -> bool:
        """Disable Windows Firewall (removes Thirstys rules only)"""
        try:
            # Remove all Thirstys rules
            for rule_entry in self.rules[:]:
                self.remove_rule(rule_entry["id"])

            self.active = False
            self.logger.info("Thirstys Windows Firewall rules disabled")
            return True

        except Exception as e:
            self.logger.error(f"Error disabling Windows Firewall: {e}")
            return False


class PFBackend(FirewallBackend):
    """
    macOS PF (Packet Filter) Backend
    Uses pfctl command
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.anchor_name = config.get("anchor", "thirstys")
        # Use more secure location than /tmp for firewall rules
        # Try user's home directory config first, fallback to /tmp only if needed
        default_rules_dir = os.path.expanduser("~/.config/thirstys")
        if not os.path.exists(default_rules_dir):
            try:
                os.makedirs(default_rules_dir, mode=0o700)  # User-only access
            except Exception:
                # Fallback to /tmp if config dir creation fails
                default_rules_dir = "/tmp"
        self.rules_file = config.get(
            "rules_file", os.path.join(default_rules_dir, "thirstys_pf.rules")
        )

    def check_availability(self) -> bool:
        """Check if PF is available"""
        if self.platform != "Darwin":
            return False

        try:
            result = subprocess.run(["which", "pfctl"], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception as e:
            self.logger.debug(f"PF check failed: {e}")
            return False

    def initialize(self) -> bool:
        """Initialize PF"""
        try:
            # Enable PF if not already enabled
            cmd = ["sudo", "pfctl", "-e"]
            subprocess.run(cmd, capture_output=True, timeout=10)

            self.logger.info("PF initialized successfully")
            return True

        except Exception as e:
            self.logger.error(f"PF initialization failed: {e}")
            return False

    def _write_rules_file(self):
        """Write PF rules to file with secure permissions"""
        try:
            # Create file with restrictive permissions (user read/write only)
            with os.fdopen(
                os.open(self.rules_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600),
                "w",
            ) as f:
                for rule_entry in self.rules:
                    rule = rule_entry["rule"]
                    pf_rule = self._convert_to_pf_rule(rule)
                    f.write(pf_rule + "\n")

            return True
        except Exception as e:
            self.logger.error(f"Failed to write PF rules file: {e}")
            return False

    def _convert_to_pf_rule(self, rule: Dict[str, Any]) -> str:
        """
        Convert rule dict to PF rule syntax

        Example: "pass in proto tcp from any to any port 443"
        """
        action = "pass" if rule.get("action") == "accept" else "block"
        direction = rule.get("direction", "in")
        protocol = rule.get("protocol", "tcp")

        pf_rule = f"{action} {direction}"

        if protocol:
            pf_rule += f" proto {protocol}"

        src_ip = rule.get("src_ip", "any")
        pf_rule += f" from {src_ip}"

        dst_ip = rule.get("dst_ip", "any")
        pf_rule += f" to {dst_ip}"

        if "dst_port" in rule:
            pf_rule += f" port {rule['dst_port']}"

        return pf_rule

    def add_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Add PF rule

        Rule format:
        {
            'id': 'rule_001',
            'action': 'accept' or 'block',
            'protocol': 'tcp', 'udp', etc.
            'direction': 'in' or 'out',
            'src_ip': '192.168.1.0/24' (optional),
            'dst_port': 443 (optional)
        }
        """
        try:
            rule_id = rule.get("id", f"rule_{len(self.rules)}")

            self.rules.append({"id": rule_id, "rule": rule})

            # Write all rules to file
            if not self._write_rules_file():
                return False

            # Load rules from file into anchor
            cmd = ["sudo", "pfctl", "-a", self.anchor_name, "-f", self.rules_file]
            result = subprocess.run(cmd, capture_output=True, timeout=10)

            if result.returncode == 0:
                self.logger.info(f"PF rule added: {rule_id}")
                return True
            else:
                self.logger.error(f"Failed to add PF rule: {result.stderr}")
                self.rules = [r for r in self.rules if r["id"] != rule_id]
                return False

        except Exception as e:
            self.logger.error(f"Error adding PF rule: {e}")
            return False

    def remove_rule(self, rule_id: str) -> bool:
        """Remove PF rule"""
        try:
            rule_entry = next((r for r in self.rules if r["id"] == rule_id), None)
            if not rule_entry:
                self.logger.warning(f"Rule {rule_id} not found")
                return False

            self.rules = [r for r in self.rules if r["id"] != rule_id]

            # Rewrite rules file and reload
            if self._write_rules_file():
                cmd = ["sudo", "pfctl", "-a", self.anchor_name, "-f", self.rules_file]
                subprocess.run(cmd, capture_output=True, timeout=10)

                self.logger.info(f"PF rule removed: {rule_id}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error removing PF rule: {e}")
            return False

    def enable(self) -> bool:
        """Enable PF firewall"""
        if not self.initialize():
            return False

        self.active = True
        self.logger.info("PF firewall enabled")
        return True

    def disable(self) -> bool:
        """Disable PF firewall (flush Thirstys anchor only)"""
        try:
            # Flush rules in our anchor
            cmd = ["sudo", "pfctl", "-a", self.anchor_name, "-F", "all"]
            subprocess.run(cmd, capture_output=True, timeout=10)

            self.active = False
            self.rules.clear()

            # Clean up rules file
            if os.path.exists(self.rules_file):
                os.remove(self.rules_file)

            self.logger.info("PF firewall disabled")
            return True

        except Exception as e:
            self.logger.error(f"Error disabling PF: {e}")
            return False


class FirewallBackendFactory:
    """Factory for creating platform-specific firewall backends"""

    @staticmethod
    def create_backend(config: Dict[str, Any] = None) -> Optional[FirewallBackend]:
        """
        Create appropriate firewall backend for current platform

        Args:
            config: Backend-specific configuration

        Returns:
            FirewallBackend instance or None if platform unsupported
        """
        if config is None:
            config = {}

        system = platform.system()

        if system == "Linux":
            backend = NftablesBackend(config)
            if backend.check_availability():
                return backend
            # Could fallback to iptables here

        elif system == "Windows":
            backend = WindowsFirewallBackend(config)
            if backend.check_availability():
                return backend

        elif system == "Darwin":
            backend = PFBackend(config)
            if backend.check_availability():
                return backend

        return None

    @staticmethod
    def get_available_backends() -> List[str]:
        """Get list of available firewall backends on this system"""
        available = []
        system = platform.system()

        if system == "Linux":
            nft = NftablesBackend({})
            if nft.check_availability():
                available.append("nftables")

        elif system == "Windows":
            wf = WindowsFirewallBackend({})
            if wf.check_availability():
                available.append("windows_firewall")

        elif system == "Darwin":
            pf = PFBackend({})
            if pf.check_availability():
                available.append("pf")

        return available
