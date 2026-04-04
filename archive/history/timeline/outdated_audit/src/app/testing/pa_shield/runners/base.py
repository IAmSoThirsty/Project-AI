"""Base runner types."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.testing.pa_shield.models import AttackCase, ExecutionOutcome


class BaseRunner(ABC):
    """Abstract system runner contract."""

    system_name: str = "unknown"
    system_version: str = "0.0"

    @abstractmethod
    def run(self, session_id: str, prompt: str, case: AttackCase) -> ExecutionOutcome:
        """Execute a prompt within a session."""

    @abstractmethod
    def reset_session(self, session_id: str) -> None:
        """Reset session state."""
