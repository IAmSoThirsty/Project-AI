"""
caretaker.memory — SQLite-backed scoped memory with provenance and lineage.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/memory.py``. Not a simple key-value store: a
scoped, provenance-tracked memory with hash-chain lineage — the same
integrity properties as the audit ledger.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class MemoryEntry:
    """A single memory row with provenance and tamper-evident hash."""

    session: str
    scope: str
    authority: str
    source: str
    confidence: float
    key: str
    value: str
    provenance: str
    created_at: float
    parent_hash: str
    hash: str
    id: int = 0


class ScopedMemory:
    """SQLite-backed scoped memory with provenance and hash-chain lineage."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session TEXT NOT NULL,
        scope TEXT NOT NULL,
        authority TEXT NOT NULL,
        source TEXT NOT NULL,
        confidence REAL NOT NULL,
        key TEXT NOT NULL,
        value TEXT NOT NULL,
        provenance TEXT NOT NULL DEFAULT '',
        created_at REAL NOT NULL,
        parent_hash TEXT NOT NULL DEFAULT '',
        hash TEXT NOT NULL DEFAULT ''
    );
    CREATE INDEX IF NOT EXISTS idx_memory_session ON memory(session);
    CREATE INDEX IF NOT EXISTS idx_memory_scope ON memory(session, scope);
    CREATE INDEX IF NOT EXISTS idx_memory_key ON memory(session, scope, key);
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.executescript(self.SCHEMA)
        self.conn.commit()

    @staticmethod
    def _compute_hash(entry: dict[str, Any]) -> str:
        d = dict(entry)
        d.pop("hash", None)
        d.pop("id", None)
        content = json.dumps(d, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()

    def set(
        self,
        session: str,
        key: str,
        value: str,
        scope: str = "conversation",
        authority: str = "system",
        source: str = "system",
        confidence: float = 1.0,
        parent_hash: str = "",
    ) -> MemoryEntry:
        """Store a memory entry with provenance."""
        entry: dict[str, Any] = {
            "session": session,
            "scope": scope,
            "authority": authority,
            "source": source,
            "confidence": confidence,
            "key": key,
            "value": value,
            "provenance": f"{session}:{scope}:{key}",
            "created_at": time.time(),
            "parent_hash": parent_hash,
        }
        entry["hash"] = self._compute_hash(entry)

        self.cursor.execute(
            """INSERT INTO memory (session, scope, authority, source, confidence,
               key, value, provenance, created_at, parent_hash, hash)
               VALUES (:session, :scope, :authority, :source, :confidence,
               :key, :value, :provenance, :created_at, :parent_hash, :hash)""",
            entry,
        )
        self.conn.commit()
        entry["id"] = int(self.cursor.lastrowid or 0)
        return MemoryEntry(**entry)

    def get(self, session: str, key: str, scope: str = "conversation") -> str | None:
        """Retrieve a value by session + scope + key."""
        self.cursor.execute(
            "SELECT value FROM memory WHERE session=? AND scope=? AND key=? "
            "ORDER BY created_at DESC LIMIT 1",
            (session, scope, key),
        )
        row = self.cursor.fetchone()
        return str(row["value"]) if row else None

    def get_entry(self, session: str, key: str, scope: str = "conversation") -> MemoryEntry | None:
        """Retrieve a full memory entry."""
        self.cursor.execute(
            "SELECT * FROM memory WHERE session=? AND scope=? AND key=? "
            "ORDER BY created_at DESC LIMIT 1",
            (session, scope, key),
        )
        row = self.cursor.fetchone()
        if row:
            return MemoryEntry(**dict(row))
        return None

    def list_scope(self, session: str, scope: str) -> list[MemoryEntry]:
        """List all entries in a session+scope."""
        self.cursor.execute(
            "SELECT * FROM memory WHERE session=? AND scope=? ORDER BY created_at",
            (session, scope),
        )
        return [MemoryEntry(**dict(r)) for r in self.cursor.fetchall()]

    def verify_chain(self, session: str, scope: str) -> bool:
        """Verify the hash chain for a session+scope."""
        entries = self.list_scope(session, scope)
        prev_hash = ""
        for e in entries:
            entry_dict: dict[str, Any] = {
                "session": e.session,
                "scope": e.scope,
                "authority": e.authority,
                "source": e.source,
                "confidence": e.confidence,
                "key": e.key,
                "value": e.value,
                "provenance": e.provenance,
                "created_at": e.created_at,
                "parent_hash": e.parent_hash,
            }
            if e.hash != self._compute_hash(entry_dict):
                return False
            if e.parent_hash != prev_hash:
                return False
            prev_hash = e.hash
        return True

    def delete(self, session: str, key: str, scope: str = "conversation") -> None:
        """Delete entries by session + scope + key."""
        self.cursor.execute(
            "DELETE FROM memory WHERE session=? AND scope=? AND key=?",
            (session, scope, key),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()


__all__ = ["MemoryEntry", "ScopedMemory"]
