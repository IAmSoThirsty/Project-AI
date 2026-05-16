"""Global Kill Switch - Coordinates all subsystem kill switches"""

import logging
from typing import Callable, List
import threading


class GlobalKillSwitch:
    """
    Master kill switch that coordinates browser, VPN, and firewall kill switches.
    Ensures complete privacy protection by blocking all traffic if any component fails.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._active = False
        self._triggered = False
        self._callbacks: List[Callable] = []
        self._lock = threading.Lock()

        # Component kill switches
        self._vpn_kill_switch = None
        self._browser_kill_switch = None
        self._firewall_kill_switch = None

    def enable(self):
        """Enable global kill switch"""
        with self._lock:
            self._active = True
            self.logger.info("Global Kill Switch ENABLED")

    def disable(self):
        """Disable global kill switch"""
        with self._lock:
            self._active = False
            self.logger.info("Global Kill Switch DISABLED")

    def register_vpn_kill_switch(self, vpn_kill_switch):
        """Register VPN kill switch"""
        self._vpn_kill_switch = vpn_kill_switch
        if vpn_kill_switch:
            vpn_kill_switch.register_callback(self._on_vpn_failure)

    def register_browser_kill_switch(self, browser):
        """Register browser component"""
        self._browser_kill_switch = browser

    def register_firewall_kill_switch(self, firewall):
        """Register firewall component"""
        self._firewall_kill_switch = firewall

    def trigger(self, reason: str, component: str):
        """
        Trigger global kill switch.

        Args:
            reason: Reason for trigger
            component: Component that triggered (vpn/browser/firewall)
        """
        if not self._active:
            return

        with self._lock:
            if self._triggered:
                return

            self._triggered = True
            self.logger.critical(
                f"GLOBAL KILL SWITCH TRIGGERED by {component}: {reason}"
            )

            # Emergency shutdown of all components
            self._emergency_shutdown(component)

            # Notify callbacks
            self._notify_callbacks(reason, component)

    def _emergency_shutdown(self, source_component: str):
        """Emergency shutdown of all components"""
        self.logger.critical("Initiating emergency shutdown of all components")

        # Stop all network traffic
        self._block_all_traffic()

        # Close browser
        if self._browser_kill_switch and source_component != "browser":
            try:
                self._browser_kill_switch.stop()
                self.logger.info("Browser stopped")
            except Exception as e:
                self.logger.error(f"Failed to stop browser: {e}")

        # Trigger VPN kill switch
        if self._vpn_kill_switch and source_component != "vpn":
            try:
                self._vpn_kill_switch.trigger("Global kill switch")
                self.logger.info("VPN kill switch triggered")
            except Exception as e:
                self.logger.error(f"Failed to trigger VPN kill switch: {e}")

        # Block firewall
        if self._firewall_kill_switch and source_component != "firewall":
            try:
                self._firewall_kill_switch.stop()
                self.logger.info("Firewall stopped")
            except Exception as e:
                self.logger.error(f"Failed to stop firewall: {e}")

    def _block_all_traffic(self):
        """Block all network traffic immediately"""
        self.logger.critical("BLOCKING ALL NETWORK TRAFFIC")
        # In production, would set iptables to block all traffic
        # iptables -P INPUT DROP
        # iptables -P OUTPUT DROP
        # iptables -P FORWARD DROP

    def _on_vpn_failure(self, reason: str):
        """Callback for VPN failure"""
        self.trigger(reason, "vpn")

    def register_callback(self, callback: Callable):
        """Register callback for kill switch trigger"""
        self._callbacks.append(callback)

    def _notify_callbacks(self, reason: str, component: str):
        """Notify all registered callbacks"""
        for callback in self._callbacks:
            try:
                callback(reason, component)
            except Exception as e:
                self.logger.error(f"Callback error: {e}")

    def reset(self):
        """Reset kill switch after issue resolved"""
        with self._lock:
            if not self._triggered:
                return

            self.logger.warning("Resetting global kill switch")
            self._triggered = False

    def is_active(self) -> bool:
        """Check if kill switch is active"""
        return self._active

    def is_triggered(self) -> bool:
        """Check if kill switch is triggered"""
        return self._triggered
