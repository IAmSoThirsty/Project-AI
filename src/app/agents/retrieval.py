"""Retrieval agent: abstracts access to the memory system."""

from typing import Any, Dict, List, Optional


class RetrievalAgent:
    """Wraps an optional memory system to provide a stable retrieval API."""

    def __init__(self, memory_system: Optional[Any] = None) -> None:
        self.memory_system = memory_system

    def retrieve(self, query: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """Return a list of knowledge items matching the query.

        If no memory_system is provided, returns an empty list.
        """
        if not self.memory_system:
            return []
        try:
            # memory_system expected to implement `.search(query, top_n=...)` or similar
            if hasattr(self.memory_system, "search"):
                return self.memory_system.search(query, top_n=top_n)
            # Generic fallback: try to call find / retrieve
            if hasattr(self.memory_system, "retrieve"):
                return self.memory_system.retrieve(query, top_n=top_n)
        except Exception:
            return []
        return []
