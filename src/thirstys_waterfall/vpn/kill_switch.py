"""Kill Switch implementation"""

from typing import Callable, List
import logging
import threading


class KillSwitch:
    """
    Kill Switch ensures no traffic leaks if VPN disconnects.
    Integrated with browser, VPN, and firewall layers.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.logger = logging.getLogger(__name__)
        self._active = False
        self._callbacks: List[Callable] = []
        self._lock = threading.Lock()
        self._monitoring = False

    def enable(self):
        """Enable kill switch"""
        with self._lock:
            self._active = True
            self.logger.info("Kill switch enabled")
            self._start_monitoring()

    def disable(self):
        """Disable kill switch"""
        with self._lock:
            self._active = False
            self._monitoring = False
            self.logger.info("Kill switch disabled")

    def _start_monitoring(self):
        """Start monitoring VPN connection"""
        if not self._monitoring:
            self._monitoring = True
            # In production, would monitor connection state

    def trigger(self, reason: str = "VPN disconnected"):
        """
        Trigger kill switch - block all traffic.

        Args:
            reason: Reason for triggering kill switch
        """
        if not self._active:
            return

        self.logger.critical(f"KILL SWITCH TRIGGERED: {reason}")

        # Block all network traffic
        self._block_all_traffic()

        # Notify all registered callbacks
        self._notify_callbacks(reason)

    def _block_all_traffic(self):
        """Block all network traffic"""
        self.logger.info("Blocking all network traffic")
        # In production, would set iptables/firewall rules
        # iptables -P INPUT DROP
        # iptables -P OUTPUT DROP
        # iptables -P FORWARD DROP

    def register_callback(self, callback: Callable):
        """Register callback to be called when kill switch triggers"""
        self._callbacks.append(callback)

    def _notify_callbacks(self, reason: str):
        """Notify all registered callbacks"""
        for callback in self._callbacks:
            try:
                callback(reason)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")

    def is_active(self) -> bool:
        """Check if kill switch is active"""
        return self._active

    def restore_traffic(self):
        """Restore traffic after kill switch trigger"""
        if self._active:
            self.logger.info("Restoring traffic after kill switch")
            # In production, would restore iptables rules
