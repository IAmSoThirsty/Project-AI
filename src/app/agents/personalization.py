"""Personalization agent: manage user preferences and simple personalization."""

from typing import Any, Dict


class PersonalizationAgent:
    """Store and retrieve simple user preferences.

    This is an in-memory placeholder. Persisting to disk or a DB is left to
    higher-level systems.
    """

    def __init__(self) -> None:
        self.profile: Dict[str, Any] = {}

    def update_profile(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        self.profile.update(updates or {})
        return self.profile

    def get_profile(self) -> Dict[str, Any]:
        return dict(self.profile)
