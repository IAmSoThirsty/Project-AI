"""Next-Generation Firewall with AI-based threat detection"""

from typing import Dict, Any
import hashlib
from .base import FirewallBase


class NextGenerationFirewall(FirewallBase):
    """
    Next-Generation Firewall
    Includes deep packet inspection, intrusion prevention, AI-based detection
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.ai_detection = config.get("ai_detection", True)
        self._threat_signatures = set()
        self._anomaly_baseline = {}
        self._load_threat_signatures()

    def start(self):
        """Start next-generation firewall"""
        self.logger.info("Starting Next-Generation Firewall")
        self._active = True

    def stop(self):
        """Stop next-generation firewall"""
        self.logger.info("Stopping Next-Generation Firewall")
        self._active = False

    def add_rule(self, rule: Dict[str, Any]):
        """Add NGFW rule"""
        self._rules.append(rule)

    def remove_rule(self, rule_id: str):
        """Remove NGFW rule"""
        self._rules = [r for r in self._rules if r.get("id") != rule_id]

    def _load_threat_signatures(self):
        """Load known threat signatures"""
        # Known malware/threat signatures (hashes)
        self._threat_signatures.add("deadbeef")
        self._threat_signatures.add("baadf00d")

    def process_packet(self, packet: Dict[str, Any]) -> bool:
        """Process packet with advanced inspection"""
        if not self._active:
            return True

        # Deep packet inspection
        if not self._deep_packet_inspection(packet):
            self._update_statistics(False, threat=True)
            return False

        # AI-based anomaly detection
        if self.ai_detection and self._detect_anomaly(packet):
            self._update_statistics(False, threat=True)
            return False

        # Intrusion prevention
        if self._is_intrusion_attempt(packet):
            self._update_statistics(False, threat=True)
            return False

        self._update_statistics(True)
        return True

    def _deep_packet_inspection(self, packet: Dict[str, Any]) -> bool:
        """Perform deep packet inspection"""
        payload = packet.get("payload", "")

        # Calculate payload hash
        if payload:
            payload_hash = hashlib.md5(str(payload).encode()).hexdigest()
            if payload_hash in self._threat_signatures:
                self.logger.warning(f"Threat signature detected: {payload_hash}")
                return False

        # Check for protocol violations
        protocol = packet.get("protocol", "")
        if protocol == "http" and "Host" not in str(payload):
            return False

        return True

    def _detect_anomaly(self, packet: Dict[str, Any]) -> bool:
        """AI-based anomaly detection"""
        # Simplified anomaly detection
        src_ip = packet.get("src_ip")

        if src_ip not in self._anomaly_baseline:
            self._anomaly_baseline[src_ip] = {
                "packet_count": 0,
                "avg_size": 0,
                "protocols": set(),
            }

        baseline = self._anomaly_baseline[src_ip]
        baseline["packet_count"] += 1
        baseline["protocols"].add(packet.get("protocol"))

        # Detect port scanning (many different ports from same source)
        if baseline["packet_count"] > 100 and len(baseline["protocols"]) > 10:
            self.logger.warning(f"Possible port scan from {src_ip}")
            return True

        return False

    def _is_intrusion_attempt(self, packet: Dict[str, Any]) -> bool:
        """Detect intrusion attempts"""
        payload = str(packet.get("payload", ""))

        # SQL injection patterns
        sql_patterns = ["UNION SELECT", "OR 1=1", "'; DROP", "--"]
        for pattern in sql_patterns:
            if pattern.upper() in payload.upper():
                self.logger.warning("SQL injection attempt detected")
                return True

        # XSS patterns
        xss_patterns = ["<script>", "javascript:", "onerror="]
        for pattern in xss_patterns:
            if pattern.lower() in payload.lower():
                self.logger.warning("XSS attempt detected")
                return True

        return False

    def add_threat_signature(self, signature: str):
        """Add new threat signature"""
        self._threat_signatures.add(signature)

    def get_threat_intelligence(self) -> Dict[str, Any]:
        """Get threat intelligence data"""
        return {
            "signatures": len(self._threat_signatures),
            "monitored_ips": len(self._anomaly_baseline),
            "threats_detected": self._statistics["threats_detected"],
        }
