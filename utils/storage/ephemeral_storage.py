"""Ephemeral Storage - Temporary, auto-wiping storage"""

import logging
from typing import Dict, Any, Optional
import time


class EphemeralStorage:
    """
    Ephemeral storage that automatically wipes data.
    Data is kept in memory only and never written to disk.
    """

    def __init__(self, config: Dict[str, Any]):
        self.enabled = config.get('ephemeral_mode', True)
        self.memory_only = config.get('memory_only', True)
        self.auto_wipe_interval = config.get('auto_wipe_interval', 300)  # 5 minutes
        self.logger = logging.getLogger(__name__)

        self._storage: Dict[str, Dict[str, Any]] = {}
        self._active = False

    def start(self):
        """Start ephemeral storage"""
        self.logger.info("Starting Ephemeral Storage (memory-only)")
        self._active = True

    def stop(self):
        """Stop ephemeral storage and wipe all data"""
        self.logger.info("Stopping Ephemeral Storage")
        self._wipe_all()
        self._active = False

    def store(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Store data temporarily.

        Args:
            key: Data key
            value: Data value
            ttl: Time to live in seconds (optional)
        """
        if not self._active:
            raise RuntimeError("Ephemeral storage not active")

        self._storage[key] = {
            'value': value,
            'created': time.time(),
            'ttl': ttl
        }

        self.logger.debug(f"Stored ephemeral data: {key}")

    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve ephemeral data.

        Returns:
            Value or None if not found or expired
        """
        if not self._active or key not in self._storage:
            return None

        item = self._storage[key]

        # Check if expired
        if item['ttl']:
            if time.time() - item['created'] > item['ttl']:
                self.delete(key)
                return None

        return item['value']

    def delete(self, key: str):
        """Delete ephemeral data"""
        if key in self._storage:
            del self._storage[key]
            self.logger.debug(f"Deleted ephemeral data: {key}")

    def _wipe_all(self):
        """Wipe all ephemeral data"""
        self.logger.info("Wiping all ephemeral data")
        self._storage.clear()

    def cleanup_expired(self):
        """Remove expired items"""
        current_time = time.time()
        expired_keys = []

        for key, item in self._storage.items():
            if item['ttl'] and current_time - item['created'] > item['ttl']:
                expired_keys.append(key)

        for key in expired_keys:
            self.delete(key)

        if expired_keys:
            self.logger.debug(f"Cleaned up {len(expired_keys)} expired items")

    def get_statistics(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return {
            'active': self._active,
            'items_stored': len(self._storage),
            'memory_only': self.memory_only
        }
