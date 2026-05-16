"""Packet-Filtering Firewall implementation"""

from typing import Dict, Any
from .base import FirewallBase


class PacketFilteringFirewall(FirewallBase):
    """
    Packet-Filtering Firewall
    Filters packets based on IP addresses, ports, and protocols
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.default_policy = config.get("default_policy", "deny")
        self._packet_rules = []

    def start(self):
        """Start packet filtering"""
        self.logger.info("Starting Packet-Filtering Firewall")
        self._active = True
        self._load_default_rules()

    def stop(self):
        """Stop packet filtering"""
        self.logger.info("Stopping Packet-Filtering Firewall")
        self._active = False

    def _load_default_rules(self):
        """Load default packet filtering rules"""
        # Allow established connections
        self.add_rule(
            {"id": "default_established", "action": "allow", "state": "established"}
        )

        # Block known malicious IPs (example)
        self.add_rule(
            {
                "id": "block_malicious",
                "action": "deny",
                "src_ip": ["0.0.0.0/8", "127.0.0.0/8"],
            }
        )

    def add_rule(self, rule: Dict[str, Any]):
        """Add packet filtering rule"""
        if "id" not in rule:
            rule["id"] = f"rule_{len(self._packet_rules)}"

        self._rules.append(rule)
        self._packet_rules.append(rule)
        self.logger.debug(f"Added rule: {rule['id']}")

    def remove_rule(self, rule_id: str):
        """Remove packet filtering rule"""
        self._rules = [r for r in self._rules if r.get("id") != rule_id]
        self._packet_rules = [r for r in self._packet_rules if r.get("id") != rule_id]

    def process_packet(self, packet: Dict[str, Any]) -> bool:
        """
        Process packet through filtering rules.

        Packet format:
        {
            'src_ip': '192.168.1.1',
            'dst_ip': '8.8.8.8',
            'src_port': 54321,
            'dst_port': 80,
            'protocol': 'tcp',
            'state': 'new|established|related'
        }
        """
        if not self._active:
            return True

        # Check each rule
        for rule in self._packet_rules:
            if self._match_rule(packet, rule):
                allowed = rule.get("action", "deny") == "allow"
                self._update_statistics(allowed)
                return allowed

        # Apply default policy
        allowed = self.default_policy == "allow"
        self._update_statistics(allowed)
        return allowed

    def _match_rule(self, packet: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Check if packet matches rule criteria"""
        # Match protocol
        if "protocol" in rule and packet.get("protocol") != rule["protocol"]:
            return False

        # Match source IP
        if "src_ip" in rule:
            if not self._match_ip(packet.get("src_ip"), rule["src_ip"]):
                return False

        # Match destination IP
        if "dst_ip" in rule:
            if not self._match_ip(packet.get("dst_ip"), rule["dst_ip"]):
                return False

        # Match source port
        if "src_port" in rule and packet.get("src_port") != rule["src_port"]:
            return False

        # Match destination port
        if "dst_port" in rule and packet.get("dst_port") != rule["dst_port"]:
            return False

        # Match state
        if "state" in rule and packet.get("state") != rule["state"]:
            return False

        return True

    def _match_ip(self, ip: str, rule_ips) -> bool:
        """Match IP address against rule"""
        if isinstance(rule_ips, str):
            rule_ips = [rule_ips]

        # Simplified IP matching (production would use ipaddress module)
        for rule_ip in rule_ips:
            if (
                ip == rule_ip
                or rule_ip.endswith("/8")
                and ip.startswith(rule_ip.split("/")[0].rsplit(".", 3)[0])
            ):
                return True

        return False
