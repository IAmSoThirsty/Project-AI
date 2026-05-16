"""Circuit-Level Gateway Firewall"""

from typing import Dict, Any
import time
from .base import FirewallBase


class CircuitLevelGateway(FirewallBase):
    """
    Circuit-Level Gateway
    Monitors TCP handshaking and session establishment
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.proxy_timeout = config.get("proxy_timeout", 30)
        self._sessions = {}

    def start(self):
        """Start circuit-level gateway"""
        self.logger.info("Starting Circuit-Level Gateway")
        self._active = True

    def stop(self):
        """Stop circuit-level gateway"""
        self.logger.info("Stopping Circuit-Level Gateway")
        self._active = False
        self._sessions.clear()

    def add_rule(self, rule: Dict[str, Any]):
        """Add circuit-level rule"""
        self._rules.append(rule)

    def remove_rule(self, rule_id: str):
        """Remove circuit-level rule"""
        self._rules = [r for r in self._rules if r.get("id") != rule_id]

    def process_packet(self, packet: Dict[str, Any]) -> bool:
        """Process packet through circuit-level inspection"""
        if not self._active:
            return True

        session_id = self._get_session_id(packet)

        # Check if session exists and is valid
        if session_id in self._sessions:
            session = self._sessions[session_id]
            if time.time() - session["established"] > self.proxy_timeout:
                # Session expired
                del self._sessions[session_id]
                self._update_statistics(False)
                return False

            self._update_statistics(True)
            return True

        # Check if this is a new connection attempt (SYN)
        if packet.get("flags") == "SYN":
            # Validate handshake
            if self._validate_handshake(packet):
                self._sessions[session_id] = {
                    "established": time.time(),
                    "src": packet.get("src_ip"),
                    "dst": packet.get("dst_ip"),
                }
                self._update_statistics(True)
                return True

        self._update_statistics(False)
        return False

    def _get_session_id(self, packet: Dict[str, Any]) -> str:
        """Generate unique session ID"""
        return f"{packet.get('src_ip')}:{packet.get('src_port')}->{packet.get('dst_ip')}:{packet.get('dst_port')}"

    def _validate_handshake(self, packet: Dict[str, Any]) -> bool:
        """Validate TCP handshake"""
        # Simplified validation
        return packet.get("protocol") == "tcp"

    def get_active_sessions(self) -> Dict[str, Any]:
        """Get all active sessions"""
        return self._sessions.copy()
