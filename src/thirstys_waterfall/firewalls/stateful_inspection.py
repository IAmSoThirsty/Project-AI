"""Stateful Inspection Firewall"""

from typing import Dict, Any
import time
from .base import FirewallBase


class StatefulInspectionFirewall(FirewallBase):
    """
    Stateful Inspection Firewall
    Tracks connection state and context
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection_timeout = config.get("connection_timeout", 3600)
        self._connection_table = {}

    def start(self):
        """Start stateful inspection"""
        self.logger.info("Starting Stateful Inspection Firewall")
        self._active = True

    def stop(self):
        """Stop stateful inspection"""
        self.logger.info("Stopping Stateful Inspection Firewall")
        self._active = False
        self._connection_table.clear()

    def add_rule(self, rule: Dict[str, Any]):
        """Add stateful rule"""
        self._rules.append(rule)

    def remove_rule(self, rule_id: str):
        """Remove stateful rule"""
        self._rules = [r for r in self._rules if r.get("id") != rule_id]

    def process_packet(self, packet: Dict[str, Any]) -> bool:
        """Process packet with stateful inspection"""
        if not self._active:
            return True

        conn_id = self._get_connection_id(packet)
        current_time = time.time()

        # Clean expired connections
        self._cleanup_expired_connections(current_time)

        # Check existing connections
        if conn_id in self._connection_table:
            conn = self._connection_table[conn_id]

            # Validate packet belongs to this connection
            if self._validate_connection_state(packet, conn):
                conn["last_seen"] = current_time
                conn["packet_count"] += 1
                self._update_statistics(True)
                return True
            else:
                self._update_statistics(False, threat=True)
                return False

        # New connection
        if packet.get("flags") in ["SYN", None]:
            self._connection_table[conn_id] = {
                "state": "new",
                "established": current_time,
                "last_seen": current_time,
                "packet_count": 1,
                "src_ip": packet.get("src_ip"),
                "dst_ip": packet.get("dst_ip"),
                "protocol": packet.get("protocol"),
            }
            self._update_statistics(True)
            return True

        # Packet doesn't belong to known connection
        self._update_statistics(False)
        return False

    def _get_connection_id(self, packet: Dict[str, Any]) -> str:
        """Generate connection identifier"""
        return f"{packet.get('src_ip')}:{packet.get('src_port')}-{packet.get('dst_ip')}:{packet.get('dst_port')}"

    def _validate_connection_state(
        self, packet: Dict[str, Any], connection: Dict[str, Any]
    ) -> bool:
        """Validate packet matches connection state"""
        # Verify IPs match
        if packet.get("src_ip") != connection["src_ip"]:
            return False
        if packet.get("dst_ip") != connection["dst_ip"]:
            return False

        # Verify protocol matches
        if packet.get("protocol") != connection["protocol"]:
            return False

        return True

    def _cleanup_expired_connections(self, current_time: float):
        """Remove expired connections"""
        expired = [
            conn_id
            for conn_id, conn in self._connection_table.items()
            if current_time - conn["last_seen"] > self.connection_timeout
        ]

        for conn_id in expired:
            del self._connection_table[conn_id]

    def get_connection_table(self) -> Dict[str, Any]:
        """Get active connection table"""
        return self._connection_table.copy()
