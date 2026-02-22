"""
Deadman Switch - Heartbeat Monitoring and Failsafe

This module implements a deadman switch system that monitors system heartbeats
and triggers failsafe actions if the system becomes unresponsive or compromised.

Key Features:
- Background daemon thread for heartbeat monitoring
- Configurable timeout thresholds
- Registered failsafe action execution with exception isolation
- Thread-safe heartbeat and state management
- Status reporting

STATUS: PRODUCTION
"""

import logging
import threading
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class DeadmanSwitch:
    """Implements heartbeat monitoring with failsafe triggers.

    The deadman switch monitors system health through regular heartbeats.
    If heartbeats stop or anomalies are detected, failsafe actions are
    triggered to prevent harm or secure the system.

    Thread Safety:
        All mutable state is guarded by ``_lock``. The background
        monitoring thread is a daemon so it will not block process exit.
    """

    def __init__(self, timeout_seconds: int = 300):
        """Initialize the deadman switch.

        Args:
            timeout_seconds: Seconds without heartbeat before trigger
        """
        self.timeout_seconds = timeout_seconds
        self.last_heartbeat: datetime | None = None
        self.enabled: bool = False
        self.monitoring_thread: threading.Thread | None = None
        self.failsafe_actions: list[Callable[[], None]] = []
        self.triggered: bool = False
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self.trigger_history: list[dict[str, Any]] = []

    def start_monitoring(self) -> bool:
        """Start heartbeat monitoring.

        Launches a daemon background thread that checks for heartbeat
        timeouts once per second. Sets the initial heartbeat timestamp.

        Returns:
            True if started successfully, False if already monitoring
        """
        with self._lock:
            if self.enabled:
                logger.warning("Deadman switch already monitoring")
                return False

            self.enabled = True
            self.last_heartbeat = datetime.now()
            self.triggered = False
            self._stop_event.clear()

        logger.info(
            "Deadman switch monitoring started (timeout: %ss)",
            self.timeout_seconds,
        )

        self.monitoring_thread = threading.Thread(
            target=self._monitor_loop, name="deadman-switch-monitor", daemon=True
        )
        self.monitoring_thread.start()

        return True

    def stop_monitoring(self) -> bool:
        """Stop heartbeat monitoring.

        Signals the monitoring thread to exit and waits for it to join.

        Returns:
            True if stopped successfully, False if not monitoring
        """
        with self._lock:
            if not self.enabled:
                logger.warning("Deadman switch not monitoring")
                return False
            self.enabled = False

        self._stop_event.set()

        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)

        logger.info("Deadman switch monitoring stopped")
        return True

    def send_heartbeat(self) -> bool:
        """Send a heartbeat signal to reset the timeout.

        Thread-safe. Resets the heartbeat timestamp so the timeout
        window starts anew.

        Returns:
            True if heartbeat accepted, False if monitoring is disabled
        """
        with self._lock:
            if not self.enabled:
                logger.debug("Heartbeat ignored - monitoring not enabled")
                return False

            self.last_heartbeat = datetime.now()

        logger.debug("Heartbeat received")
        return True

    def check_timeout(self) -> bool:
        """Check if heartbeat timeout has occurred.

        Thread-safe comparison of current time against last heartbeat.

        Returns:
            True if timeout occurred, False otherwise
        """
        with self._lock:
            if not self.enabled or self.last_heartbeat is None:
                return False

            elapsed = datetime.now() - self.last_heartbeat
            timeout_delta = timedelta(seconds=self.timeout_seconds)

        return elapsed > timeout_delta

    def trigger_failsafe(self, reason: str = "timeout") -> bool:
        """Trigger failsafe actions.

        Executes all registered failsafe actions in order. Each action
        is isolated — if one raises, the remaining actions still run.

        Args:
            reason: Reason for triggering failsafe

        Returns:
            True if triggered (even if some actions fail), False if
            already triggered
        """
        with self._lock:
            if self.triggered:
                logger.warning("Failsafe already triggered")
                return False
            self.triggered = True

        trigger_time = datetime.now().isoformat()
        logger.critical("DEADMAN SWITCH TRIGGERED: %s at %s", reason, trigger_time)

        action_results: list[dict[str, Any]] = []
        for i, action in enumerate(self.failsafe_actions):
            try:
                logger.info("Executing failsafe action %s", i + 1)
                action()
                action_results.append({"index": i, "status": "success"})
            except Exception as e:
                logger.error("Failsafe action %s failed: %s", i + 1, e)
                action_results.append({"index": i, "status": "error", "error": str(e)})

        record = {
            "reason": reason,
            "trigger_time": trigger_time,
            "action_results": action_results,
        }
        self.trigger_history.append(record)

        return True

    def register_failsafe_action(self, action: Callable[[], None]) -> bool:
        """Register a failsafe action to execute on trigger.

        Args:
            action: Callable to execute on failsafe trigger

        Returns:
            True if registered successfully
        """
        if not callable(action):
            logger.error("Attempted to register non-callable failsafe action")
            return False

        self.failsafe_actions.append(action)
        logger.info(
            "Registered failsafe action (total: %s)", len(self.failsafe_actions)
        )
        return True

    def _monitor_loop(self):
        """Internal monitoring loop.

        Runs in a background daemon thread. Checks heartbeat timeout
        every second and triggers failsafe if a timeout is detected.
        """
        while not self._stop_event.is_set():
            if self.check_timeout():
                logger.warning("Heartbeat timeout detected")
                self.trigger_failsafe("heartbeat_timeout")
                break

            self._stop_event.wait(timeout=1.0)

    def get_status(self) -> dict[str, Any]:
        """Get deadman switch status.

        Returns:
            Status dictionary
        """
        with self._lock:
            return {
                "enabled": self.enabled,
                "triggered": self.triggered,
                "timeout_seconds": self.timeout_seconds,
                "last_heartbeat": (
                    self.last_heartbeat.isoformat()
                    if self.last_heartbeat
                    else None
                ),
                "failsafe_actions_registered": len(self.failsafe_actions),
                "trigger_count": len(self.trigger_history),
            }


__all__ = ["DeadmanSwitch"]
