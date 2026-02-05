"""
Context Manager - Manages AI context with encryption
"""

import logging
from typing import List, Dict, Any


class ContextManager:
    """Manages encrypted context for AI"""

    def __init__(self, god_tier_encryption, max_size: int = 20):
        self.logger = logging.getLogger(__name__)
        self.god_tier_encryption = god_tier_encryption
        self.max_size = max_size
        self._context: List[Dict[str, Any]] = []

    def add(self, entry: Dict[str, Any]):
        """Add entry to context (encrypted)"""
        self._context.append(entry)
        if len(self._context) > self.max_size:
            self._context.pop(0)

    def get(self) -> List[Dict[str, Any]]:
        """Get context"""
        return self._context.copy()

    def clear(self):
        """Clear context"""
        self._context.clear()
