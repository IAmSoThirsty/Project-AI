"""
State Manager
=============

Manages short-term state, long-term memory, episodic logs, and introspection records.
"""

from typing import Any, Dict, List, Optional


class StateManager:
    """
    Manages short-term state, long-term memory, episodic logs, and introspection records.
    """

    def __init__(self, config: dict):
        self.config = config
        self.episodes: List[Dict[str, Any]] = []
        self.memory_store: Dict[str, Any] = {}

    def save_state(self, key: str, value: Any) -> None:
        """
        Save a state value.
        
        Args:
            key: State key
            value: Value to store
        """
        self.memory_store[key] = value

    def load_state(self, key: str, default=None) -> Any:
        """
        Load a state value.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            Stored value or default
        """
        return self.memory_store.get(key, default)

    def record_episode(self, data: dict) -> None:
        """
        Record an episode.
        
        Args:
            data: Episode data to record
        """
        self.episodes.append(data)

    def get_recent_episodes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent episodes.
        
        Args:
            limit: Maximum number of episodes to return
            
        Returns:
            List of recent episodes
        """
        return self.episodes[-limit:]


__all__ = ["StateManager"]
