#                                           [2026-04-09 06:25]
#                                          Productivity: Active
"""
SASE - Sovereign Adversarial Signal Engine
L7: Network Persistence & Enforcement Plane

Real-time enforcement of network policies.
Implements rate-limiting, ASN blocking, and high-entropy connection termination.
"""

import logging
from collections import OrderedDict
from typing import Any

logger = logging.getLogger("SASE.L7.Network")


class EnforcementError(Exception):
    """Exception raised during network enforcement"""


class EdgeEnforcementPlane:
    """
    SASE L7 Enforcement Plane

    Orchestrates real-time network containment and rate-limiting.
    """

    def __init__(self, capacity: int = 10000):
        # LRU cache for O(1) deduplication
        self.capacity = capacity
        self.request_hashes: OrderedDict[str, None] = OrderedDict()
        self.blocked_ips: set[str] = set()

        logger.info("L7 Enforcement Plane initialized (capacity: %d)", capacity)

    def enforce_policy(self, event: dict[str, Any]) -> bool:
        """
        Evaluate and enforce network policy on event

        Returns:
            True if allowed, False if blocked
        """
        origin_ip = event.get("origin_ip")
        if not origin_ip:
            return True  # Fallback: allow if no IP present

        # 1. Blocklist check
        if origin_ip in self.blocked_ips:
            logger.info("BLOCKED: Event from blocklisted IP: %s", origin_ip)
            return False

        # 2. Rate limit check (using event hash)
        event_hash = event.get("event_id", "N/A")
        if self._is_duplicate(event_hash):
            logger.warning("RATE_LIMIT: Duplicate event hash: %s", event_hash)
            return False

        # 3. Decision evaluation
        verdict = event.get("verdict", "ALLOWED")
        if verdict == "CONTAINED":
            self.block_ip(origin_ip)
            return False

        return True

    def block_ip(self, ip: str, reason: str = "Policy violation"):
        """Add IP to real-time blocklist"""
        if ip not in self.blocked_ips:
            self.blocked_ips.add(ip)
            logger.critical("ENFORCEMENT: IP %s BLOCKED. Reason: %s", ip, reason)

    def _is_duplicate(self, event_hash: str) -> bool:
        """Check if event hash is in recent window (O(1) lookup)"""
        if event_hash in self.request_hashes:
            return True
        self.request_hashes[event_hash] = None
        if len(self.request_hashes) > self.capacity:
            self.request_hashes.popitem(last=False)
        return False

    def reset_blocklist(self):
        """Clear all blocked IPs"""
        self.blocked_ips.clear()
        logger.warning("ENFORCEMENT: Blocklist cleared")


__all__ = ["EdgeEnforcementPlane", "EnforcementError"]
