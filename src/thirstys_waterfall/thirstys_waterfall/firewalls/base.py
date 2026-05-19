"""Base firewall interface for all firewall types"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging


class FirewallBase(ABC):
    """Base class for all firewall implementations"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get("enabled", True)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._active = False
        self._rules = []
        self._statistics = {
            "packets_inspected": 0,
            "packets_allowed": 0,
            "packets_blocked": 0,
            "threats_detected": 0,
        }

    @abstractmethod
    def start(self):
        """Start the firewall"""
        pass

    @abstractmethod
    def stop(self):
        """Stop the firewall"""
        pass

    @abstractmethod
    def add_rule(self, rule: Dict[str, Any]):
        """Add a firewall rule"""
        pass

    @abstractmethod
    def remove_rule(self, rule_id: str):
        """Remove a firewall rule"""
        pass

    @abstractmethod
    def process_packet(self, packet: Dict[str, Any]) -> bool:
        """
        Process a packet through the firewall.

        Returns:
            True if packet should be allowed, False if blocked
        """
        pass

    def is_active(self) -> bool:
        """Check if firewall is active"""
        return self._active

    def get_statistics(self) -> Dict[str, int]:
        """Get firewall statistics"""
        return self._statistics.copy()

    def reset_statistics(self):
        """Reset statistics counters"""
        self._statistics = {
            "packets_inspected": 0,
            "packets_allowed": 0,
            "packets_blocked": 0,
            "threats_detected": 0,
        }

    def _update_statistics(self, allowed: bool, threat: bool = False):
        """Update internal statistics"""
        self._statistics["packets_inspected"] += 1
        if allowed:
            self._statistics["packets_allowed"] += 1
        else:
            self._statistics["packets_blocked"] += 1
        if threat:
            self._statistics["threats_detected"] += 1
