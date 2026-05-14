"""Proxy Firewall implementation"""

from typing import Dict, Any
from .base import FirewallBase


class ProxyFirewall(FirewallBase):
    """
    Proxy Firewall
    Acts as intermediary between clients and servers
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.cache_enabled = config.get("cache_enabled", False)
        self._proxy_cache = {}
        self._proxy_connections = {}

    def start(self):
        """Start proxy firewall"""
        self.logger.info("Starting Proxy Firewall")
        self._active = True

    def stop(self):
        """Stop proxy firewall"""
        self.logger.info("Stopping Proxy Firewall")
        self._active = False
        self._proxy_cache.clear()
        self._proxy_connections.clear()

    def add_rule(self, rule: Dict[str, Any]):
        """Add proxy rule"""
        self._rules.append(rule)

    def remove_rule(self, rule_id: str):
        """Remove proxy rule"""
        self._rules = [r for r in self._rules if r.get("id") != rule_id]

    def process_packet(self, packet: Dict[str, Any]) -> bool:
        """Process packet through proxy"""
        if not self._active:
            return True

        # Inspect application layer data
        if not self._inspect_payload(packet):
            self._update_statistics(False, threat=True)
            return False

        # Check proxy rules
        for rule in self._rules:
            if self._match_proxy_rule(packet, rule):
                allowed = rule.get("action") == "allow"
                self._update_statistics(allowed)
                return allowed

        # Default allow for proxy
        self._update_statistics(True)
        return True

    def _inspect_payload(self, packet: Dict[str, Any]) -> bool:
        """Inspect packet payload for threats"""
        payload = packet.get("payload", "")

        # Check for malicious patterns
        malicious_patterns = [
            "eval(",
            "exec(",
            "<script>",
            "DROP TABLE",
            "../../../",
            "etc/passwd",
        ]

        for pattern in malicious_patterns:
            if pattern in str(payload):
                self.logger.warning(f"Malicious pattern detected: {pattern}")
                return False

        return True

    def _match_proxy_rule(self, packet: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Match packet against proxy rule"""
        # Match based on application layer criteria
        if "url_pattern" in rule:
            url = packet.get("url", "")
            if rule["url_pattern"] in url:
                return True

        if "content_type" in rule:
            if packet.get("content_type") == rule["content_type"]:
                return True

        return False

    def cache_response(self, key: str, response: Any):
        """Cache proxy response"""
        if self.cache_enabled:
            self._proxy_cache[key] = response

    def get_cached_response(self, key: str) -> Any:
        """Get cached response"""
        return self._proxy_cache.get(key)
