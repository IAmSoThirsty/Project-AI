"""Firewall Manager - Coordinates all 8 firewall types"""

from typing import Dict, Any
import logging
from .packet_filtering import PacketFilteringFirewall
from .circuit_level import CircuitLevelGateway
from .stateful_inspection import StatefulInspectionFirewall
from .proxy import ProxyFirewall
from .next_generation import NextGenerationFirewall
from .software import SoftwareFirewall
from .hardware import HardwareFirewall
from .cloud import CloudFirewall


class FirewallManager:
    """
    Manages all 8 firewall types in integrated pipeline.
    Processes packets through all enabled firewalls in sequence.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize all firewall types
        self.firewalls = {
            "packet_filtering": PacketFilteringFirewall(
                config.get("packet_filtering", {})
            ),
            "circuit_level": CircuitLevelGateway(config.get("circuit_level", {})),
            "stateful_inspection": StatefulInspectionFirewall(
                config.get("stateful_inspection", {})
            ),
            "proxy": ProxyFirewall(config.get("proxy", {})),
            "next_generation": NextGenerationFirewall(
                config.get("next_generation", {})
            ),
            "software": SoftwareFirewall(config.get("software", {})),
            "hardware": HardwareFirewall(config.get("hardware", {})),
            "cloud": CloudFirewall(config.get("cloud", {})),
        }

        self._active = False

    def start(self):
        """Start all enabled firewalls"""
        self.logger.info("Starting Firewall Manager")

        for name, firewall in self.firewalls.items():
            if firewall.enabled:
                try:
                    firewall.start()
                    self.logger.info(f"Started {name} firewall")
                except Exception as e:
                    self.logger.error(f"Failed to start {name}: {e}")

        self._active = True

    def stop(self):
        """Stop all firewalls"""
        self.logger.info("Stopping Firewall Manager")

        for name, firewall in self.firewalls.items():
            try:
                firewall.stop()
            except Exception as e:
                self.logger.error(f"Failed to stop {name}: {e}")

        self._active = False

    def process_packet(self, packet: Dict[str, Any]) -> bool:
        """
        Process packet through all enabled firewalls.
        Packet must pass all firewalls to be allowed.

        Returns:
            True if packet allowed, False if blocked
        """
        if not self._active:
            return False

        # Process through each enabled firewall
        for name, firewall in self.firewalls.items():
            if firewall.enabled and firewall.is_active():
                try:
                    if not firewall.process_packet(packet):
                        self.logger.debug(f"Packet blocked by {name}")
                        return False
                except Exception as e:
                    self.logger.error(f"Error in {name}: {e}")
                    return False

        return True

    def add_rule(self, firewall_type: str, rule: Dict[str, Any]):
        """Add rule to specific firewall"""
        if firewall_type in self.firewalls:
            self.firewalls[firewall_type].add_rule(rule)
        else:
            raise ValueError(f"Unknown firewall type: {firewall_type}")

    def remove_rule(self, firewall_type: str, rule_id: str):
        """Remove rule from specific firewall"""
        if firewall_type in self.firewalls:
            self.firewalls[firewall_type].remove_rule(rule_id)

    def get_statistics(self) -> Dict[str, Dict[str, int]]:
        """Get statistics from all firewalls"""
        stats = {}
        for name, firewall in self.firewalls.items():
            stats[name] = firewall.get_statistics()
        return stats

    def get_firewall(self, firewall_type: str):
        """Get specific firewall instance"""
        return self.firewalls.get(firewall_type)

    def is_active(self) -> bool:
        """Check if firewall manager is active"""
        return self._active
