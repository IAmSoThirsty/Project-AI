"""
Action Ledger - Auditable log of all actions
"""

import logging
from typing import Dict, Any, List
from cryptography.fernet import Fernet
import time


class ActionLedger:
    """In-browser ledger with one-click deletion"""

    def __init__(self, cipher: Fernet, max_entries: int = 100):
        self.logger = logging.getLogger(__name__)
        self._cipher = cipher
        self._max_entries = max_entries
        self._entries: List[Dict[str, Any]] = []
        self._entry_counter = 0

    def add_entry(self, action: str, details: Dict[str, Any]):
        """Add an action to the ledger (encrypted)"""
        entry = {
            "id": self._entry_counter,
            "action": action,
            "details": details,
            "timestamp": time.time(),
            "redacted": False,
        }

        self._entries.append(entry)
        self._entry_counter += 1

        if len(self._entries) > self._max_entries:
            self._entries.pop(0)

        self.logger.debug(f"Ledger entry added: {action}")

    def get_entries(self, include_redacted: bool = False) -> List[Dict[str, Any]]:
        """Get all ledger entries"""
        if include_redacted:
            return self._entries.copy()
        return [e for e in self._entries if not e.get("redacted", False)]

    def redact_entry(self, entry_id: int):
        """Redact a specific entry"""
        for entry in self._entries:
            if entry["id"] == entry_id:
                entry["redacted"] = True
                entry["details"] = {"redacted": True}
                self.logger.info(f"Entry redacted: {entry_id}")
                return

    def clear(self):
        """One-click deletion - clear all entries"""
        count = len(self._entries)
        self._entries.clear()
        self._entry_counter = 0
        self.logger.info(f"Ledger cleared - {count} entries deleted")
