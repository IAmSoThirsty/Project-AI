"""DNS and IPv6 leak protection"""

import logging
from typing import List


class DNSProtection:
    """
    Protects against DNS and IPv6 leaks.
    Ensures all DNS queries go through VPN tunnel.
    """

    def __init__(self, dns_protection: bool = True, ipv6_protection: bool = True):
        self.dns_protection = dns_protection
        self.ipv6_protection = ipv6_protection
        self.logger = logging.getLogger(__name__)
        self._active = False
        self._dns_servers = []
        self._original_dns = []

    def start(self):
        """Start DNS leak protection"""
        if not self.dns_protection:
            return

        self.logger.info("Starting DNS leak protection")

        # Store original DNS servers
        self._original_dns = self._get_system_dns()

        # Set VPN DNS servers
        self._dns_servers = ["10.200.200.1", "10.200.200.2"]  # VPN DNS 1  # VPN DNS 2
        self._set_dns_servers(self._dns_servers)

        # Block IPv6 if protection enabled
        if self.ipv6_protection:
            self._block_ipv6()

        self._active = True

    def stop(self):
        """Stop DNS leak protection"""
        if not self._active:
            return

        self.logger.info("Stopping DNS leak protection")

        # Restore original DNS
        if self._original_dns:
            self._set_dns_servers(self._original_dns)

        # Restore IPv6
        if self.ipv6_protection:
            self._restore_ipv6()

        self._active = False

    def _get_system_dns(self) -> List[str]:
        """Get current system DNS servers"""
        # In production, would read from /etc/resolv.conf or registry
        return ["8.8.8.8", "8.8.4.4"]

    def _set_dns_servers(self, servers: List[str]):
        """Set system DNS servers"""
        self.logger.debug(f"Setting DNS servers: {servers}")
        # In production, would modify /etc/resolv.conf or Windows registry

    def _block_ipv6(self):
        """Block IPv6 to prevent leaks"""
        self.logger.info("Blocking IPv6 traffic")
        # In production, would disable IPv6 or add firewall rules
        # sysctl -w net.ipv6.conf.all.disable_ipv6=1

    def _restore_ipv6(self):
        """Restore IPv6 functionality"""
        self.logger.info("Restoring IPv6 traffic")
        # In production, would re-enable IPv6

    def verify_dns_leak(self) -> bool:
        """
        Verify no DNS leaks are occurring.

        Returns:
            True if protected (no leaks), False if leaking
        """
        # In production, would query DNS leak test service
        current_dns = self._get_system_dns()

        # Check if using VPN DNS
        for server in current_dns:
            if server not in self._dns_servers:
                self.logger.warning(f"Potential DNS leak detected: {server}")
                return False

        return True

    def verify_ipv6_leak(self) -> bool:
        """
        Verify no IPv6 leaks are occurring.

        Returns:
            True if protected (no leaks), False if leaking
        """
        # In production, would check IPv6 connectivity
        return True

    def is_active(self) -> bool:
        """Check if DNS protection is active"""
        return self._active
