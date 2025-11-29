"""
Network utility functions for offline mode detection and connectivity status.
"""
import socket
import threading
from typing import Callable, Optional


class NetworkStatus:
    """Utility class to check and monitor network connectivity status."""

    # Common hosts to check connectivity (DNS servers are reliable)
    CHECK_HOSTS = [
        ("8.8.8.8", 53),  # Google DNS
        ("1.1.1.1", 53),  # Cloudflare DNS
    ]

    def __init__(self):
        self._is_online: Optional[bool] = None
        self._callbacks: list[Callable[[bool], None]] = []
        self._lock = threading.Lock()

    def check_connectivity(self, timeout: float = 3.0) -> bool:
        """Check if the system has internet connectivity.

        Args:
            timeout: Timeout in seconds for each connection attempt.

        Returns:
            True if online, False if offline.
        """
        for host, port in self.CHECK_HOSTS:
            try:
                socket.setdefaulttimeout(timeout)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((host, port))
                sock.close()
                with self._lock:
                    self._is_online = True
                return True
            except (OSError, socket.error):
                continue

        with self._lock:
            self._is_online = False
        return False

    @property
    def is_online(self) -> bool:
        """Get the current online status (cached result).

        If not checked yet, performs a connectivity check.
        """
        if self._is_online is None:
            return self.check_connectivity()
        return self._is_online

    def add_status_callback(self, callback: Callable[[bool], None]) -> None:
        """Add a callback to be notified when status changes."""
        with self._lock:
            self._callbacks.append(callback)

    def remove_status_callback(self, callback: Callable[[bool], None]) -> None:
        """Remove a status callback."""
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

    def _notify_callbacks(self, status: bool) -> None:
        """Notify all registered callbacks of status change."""
        with self._lock:
            callbacks = self._callbacks.copy()
        for callback in callbacks:
            try:
                callback(status)
            except Exception:
                pass


# Global singleton instance
_network_status = NetworkStatus()


def is_online(timeout: float = 3.0) -> bool:
    """Check if the system has internet connectivity.

    Args:
        timeout: Timeout in seconds for connection attempt.

    Returns:
        True if online, False if offline.
    """
    return _network_status.check_connectivity(timeout)


def get_network_status() -> NetworkStatus:
    """Get the global NetworkStatus instance."""
    return _network_status
