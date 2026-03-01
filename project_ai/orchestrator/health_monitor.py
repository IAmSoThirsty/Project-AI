"""
Health Monitor for Sovereign Stack
Continuously monitors subsystem health
"""

import logging
import time
from threading import Event, Thread
from typing import Any, Dict


class HealthMonitor:
    """Monitors health of all subsystems"""

    def __init__(self, boot_sequence):
        self.logger = logging.getLogger(__name__)
        self.boot_sequence = boot_sequence
        self.monitoring = False
        self.monitor_thread = None
        self.stop_event = Event()
        self.check_interval = 30  # seconds

    def start_monitoring(self) -> None:
        """Start health monitoring"""
        if self.monitoring:
            self.logger.warning("Health monitor already running")
            return

        self.monitoring = True
        self.stop_event.clear()
        self.monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Health monitor started")

    def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        if not self.monitoring:
            return

        self.stop_event.set()
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Health monitor stopped")

    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while not self.stop_event.is_set():
            try:
                self._check_health()
            except Exception as e:
                self.logger.error(f"Health check error: {e}")

            # Wait for next check
            self.stop_event.wait(self.check_interval)

    def _check_health(self) -> None:
        """Check health of all subsystems"""
        status = self.boot_sequence.get_status()

        unhealthy = []
        for name, subsystem_status in status.items():
            if not subsystem_status.get("active", False):
                unhealthy.append(name)

        if unhealthy:
            self.logger.warning(f"Unhealthy subsystems: {unhealthy}")
        else:
            self.logger.debug("All subsystems healthy")
