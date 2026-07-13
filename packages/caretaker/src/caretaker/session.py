"""
caretaker.session — Per-session continuity, memory, and audit ledger.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/session.py``. Each session is isolated:
continuity, memory, and the audit ledger are per-session.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any

from caretaker.continuity import GENESIS_HASH, ContinuityManager
from caretaker.governance.ledger import AuditLedger
from caretaker.memory import ScopedMemory


@dataclass
class SessionState:
    """Serializable session state (for crash recovery)."""

    session_id: str
    created_at: float
    message_count: int = 0
    last_decision: str = "none"
    last_theta: float = 0.0


class Session:
    """A single user session with its own continuity, memory, and ledger."""

    def __init__(self, session_id: str, db_path: str = ":memory:") -> None:
        self.session_id = session_id
        self.state = SessionState(session_id=session_id, created_at=time.time())
        self.continuity = ContinuityManager()
        self.memory = ScopedMemory(db_path)
        self.ledger = AuditLedger()

    def _memory_digest(self) -> str:
        """Digest of the most recent conversation-scope memory entry."""
        entries = self.memory.list_scope(self.session_id, "conversation")
        payload: dict[str, Any] = entries[0].__dict__ if entries else {}
        return hashlib.sha256(json.dumps(payload, default=str, sort_keys=True).encode()).hexdigest()

    def record_message(self, user_message: str, decision: str, theta: float) -> None:
        """Record that a message was processed."""
        _ = user_message
        self.state.message_count += 1
        self.state.last_decision = decision
        self.state.last_theta = theta

        self.continuity.checkpoint(
            transition=f"message:{self.state.message_count}",
            memory_digest=self._memory_digest() if self.memory else GENESIS_HASH,
            execution_digest=self.ledger.head_hash,
        )

    def verify_integrity(self) -> bool:
        """Verify both the continuity chain and the audit ledger."""
        return self.continuity.verify_chain() and self.ledger.verify_chain()

    def state_dict(self) -> dict[str, Any]:
        """Export session state as a dictionary."""
        return {
            "session_id": self.state.session_id,
            "created_at": self.state.created_at,
            "message_count": self.state.message_count,
            "last_decision": self.state.last_decision,
            "last_theta": self.state.last_theta,
            "continuity_length": self.continuity.length,
            "ledger_length": self.ledger.length,
            "integrity_valid": self.verify_integrity(),
        }


class SessionManager:
    """Manages multiple sessions."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def get_or_create(self, session_id: str) -> Session:
        if session_id not in self._sessions:
            self._sessions[session_id] = Session(session_id)
        return self._sessions[session_id]

    def get(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[str]:
        return list(self._sessions.keys())


__all__ = ["Session", "SessionManager", "SessionState"]
