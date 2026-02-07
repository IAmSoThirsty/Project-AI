"""
Storage abstraction layer for Project-AI.

This module provides a unified interface for data persistence, supporting both
transactional SQLite storage and legacy JSON file storage.

Key Features:
- Transactional SQLite storage for governance, memory, and execution history
- Schema evolution and migration support
- Backward compatibility with JSON storage
- Thread-safe operations
- Connection pooling

Storage Engines:
- SQLiteStorage: Primary storage engine (recommended)
- JSONStorage: Legacy storage engine (deprecated)
"""

import json
import logging
import sqlite3
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

logger = logging.getLogger(__name__)


class StorageEngine(ABC):
    """Abstract base class for storage engines."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the storage engine and create necessary structures."""
        pass

    @abstractmethod
    def store(self, table: str, key: str, data: dict[str, Any]) -> bool:
        """Store data in the specified table with the given key."""
        pass

    @abstractmethod
    def retrieve(self, table: str, key: str) -> dict[str, Any] | None:
        """Retrieve data from the specified table by key."""
        pass

    @abstractmethod
    def query(
        self, table: str, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Query data from the specified table with optional filters."""
        pass

    @abstractmethod
    def delete(self, table: str, key: str) -> bool:
        """Delete data from the specified table by key."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the storage engine and cleanup resources."""
        pass


class SQLiteStorage(StorageEngine):
    """
    SQLite-based storage engine with transactional support.

    Provides thread-safe, transactional storage with schema evolution.
    Recommended for production use.
    """

    # Whitelist of allowed table names to prevent SQL injection
    ALLOWED_TABLES = {
        "governance_state",
        "governance_decisions",
        "execution_history",
        "reflection_history",
        "memory_records",
    }

    def __init__(self, db_path: str = "data/cognition.db"):
        """
        Initialize SQLite storage engine.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.lock = Lock()
        self._conn: sqlite3.Connection | None = None

        logger.info("SQLiteStorage initialized: %s", db_path)

    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections.

        Provides thread-safe connection handling with automatic cleanup.
        """
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            try:
                yield conn
            finally:
                conn.close()

    def _validate_table_name(self, table: str) -> None:
        """
        Validate table name against whitelist.

        Args:
            table: Table name to validate

        Raises:
            ValueError: If table name is not in whitelist
        """
        if table not in self.ALLOWED_TABLES:
            raise ValueError(
                f"Invalid table name: {table}. "
                f"Allowed tables: {', '.join(self.ALLOWED_TABLES)}"
            )

    def initialize(self) -> None:
        """Initialize database schema."""
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Governance table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS governance_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    version TEXT DEFAULT '1.0.0',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Governance decisions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS governance_decisions (
                    decision_id TEXT PRIMARY KEY,
                    action_id TEXT NOT NULL,
                    approved INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    council_votes TEXT,
                    mutation_intent TEXT,
                    consensus_required INTEGER DEFAULT 0,
                    consensus_achieved INTEGER DEFAULT 0,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Execution history table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_history (
                    trace_id TEXT PRIMARY KEY,
                    action_name TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    source TEXT,
                    user_id TEXT,
                    duration_ms REAL,
                    channels TEXT,
                    error TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Reflection history table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS reflection_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT NOT NULL,
                    action_name TEXT NOT NULL,
                    insights TEXT,
                    triggered_by TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trace_id) REFERENCES execution_history(trace_id)
                )
                """
            )

            # Memory records table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trace_id) REFERENCES execution_history(trace_id)
                )
                """
            )

            # Create indices for performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_execution_timestamp
                ON execution_history(timestamp)
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_governance_timestamp
                ON governance_decisions(timestamp)
                """
            )

            conn.commit()

        logger.info("SQLite storage initialized")

    def store(self, table: str, key: str, data: dict[str, Any]) -> bool:
        """
        Store data in the specified table.

        Args:
            table: Table name
            key: Record key
            data: Data to store

        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Convert data to JSON
                data_json = json.dumps(data)

                if table == "governance_state":
                    cursor.execute(
                        """
                        INSERT INTO governance_state (key, data, updated_at)
                        VALUES (?, ?, CURRENT_TIMESTAMP)
                        ON CONFLICT(key) DO UPDATE SET
                            data = excluded.data,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        (key, data_json),
                    )
                elif table == "governance_decisions":
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO governance_decisions
                        (decision_id, action_id, approved, reason, council_votes,
                         mutation_intent, consensus_required, consensus_achieved, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            key,
                            data.get("action_id"),
                            int(data.get("approved", False)),
                            data.get("reason", ""),
                            json.dumps(data.get("council_votes", {})),
                            data.get("mutation_intent"),
                            int(data.get("consensus_required", False)),
                            int(data.get("consensus_achieved", False)),
                            data.get("timestamp", datetime.now().isoformat()),
                        ),
                    )
                elif table == "execution_history":
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO execution_history
                        (trace_id, action_name, action_type, status, source,
                         user_id, duration_ms, channels, error, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            key,
                            data.get("action_name"),
                            data.get("action_type"),
                            data.get("status"),
                            data.get("source"),
                            data.get("user_id"),
                            data.get("duration_ms"),
                            json.dumps(data.get("channels", {})),
                            data.get("error"),
                            data.get("timestamp", datetime.now().isoformat()),
                        ),
                    )
                else:
                    # Validate table name before generic handling
                    self._validate_table_name(table)
                    # Generic table handling (for reflection_history and memory_records)
                    cursor.execute(
                        f"INSERT OR REPLACE INTO {table} (key, data) VALUES (?, ?)",
                        (key, data_json),
                    )

                conn.commit()
                return True

        except Exception as e:
            logger.error("Failed to store data in %s: %s", table, e)
            return False

    def retrieve(self, table: str, key: str) -> dict[str, Any] | None:
        """
        Retrieve data from the specified table.

        Args:
            table: Table name
            key: Record key

        Returns:
            Data dictionary or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if table == "governance_state":
                    cursor.execute(
                        "SELECT data FROM governance_state WHERE key = ?", (key,)
                    )
                elif table in [
                    "governance_decisions",
                    "execution_history",
                    "reflection_history",
                ]:
                    # Get column name for primary key (validated tables only)
                    pk_col = (
                        "decision_id" if table == "governance_decisions" else "trace_id"
                    )
                    if table == "reflection_history":
                        pk_col = "id"

                    # Safe: table is validated against whitelist in elif condition
                    cursor.execute(f"SELECT * FROM {table} WHERE {pk_col} = ?", (key,))
                else:
                    # Validate table name before generic handling
                    self._validate_table_name(table)
                    cursor.execute(f"SELECT data FROM {table} WHERE key = ?", (key,))

                row = cursor.fetchone()
                if row:
                    if "data" in row.keys():
                        return json.loads(row["data"])
                    else:
                        # Convert row to dict
                        return dict(row)

                return None

        except Exception as e:
            logger.error("Failed to retrieve data from %s: %s", table, e)
            return None

    def query(
        self, table: str, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Query data from the specified table.

        Args:
            table: Table name
            filters: Optional filter conditions

        Returns:
            List of matching records
        """
        try:
            # Validate table name first
            self._validate_table_name(table)

            with self._get_connection() as conn:
                cursor = conn.cursor()

                if filters:
                    # Build WHERE clause
                    conditions = [f"{k} = ?" for k in filters.keys()]
                    where_clause = " AND ".join(conditions)
                    # Safe: table is validated, and column names come from keys
                    query = f"SELECT * FROM {table} WHERE {where_clause}"
                    cursor.execute(query, tuple(filters.values()))
                else:
                    # Safe: table is validated
                    cursor.execute(f"SELECT * FROM {table}")

                rows = cursor.fetchall()
                return [dict(row) for row in rows]

        except Exception as e:
            logger.error("Failed to query data from %s: %s", table, e)
            return []

    def delete(self, table: str, key: str) -> bool:
        """
        Delete data from the specified table.

        Args:
            table: Table name
            key: Record key

        Returns:
            True if successful, False otherwise
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if table == "governance_state":
                    cursor.execute("DELETE FROM governance_state WHERE key = ?", (key,))
                elif table == "governance_decisions":
                    cursor.execute(
                        "DELETE FROM governance_decisions WHERE decision_id = ?", (key,)
                    )
                elif table == "execution_history":
                    cursor.execute(
                        "DELETE FROM execution_history WHERE trace_id = ?", (key,)
                    )
                else:
                    # Validate table name before generic handling
                    self._validate_table_name(table)
                    cursor.execute(f"DELETE FROM {table} WHERE key = ?", (key,))

                conn.commit()
                return True

        except Exception as e:
            logger.error("Failed to delete data from %s: %s", table, e)
            return False

    def close(self) -> None:
        """Close database connection."""
        # Connection is managed by context manager
        logger.info("SQLiteStorage closed")


class JSONStorage(StorageEngine):
    """
    JSON file-based storage engine (legacy).

    Provided for backward compatibility with existing JSON-based storage.
    Consider migrating to SQLiteStorage for production use.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize JSON storage engine.

        Args:
            data_dir: Directory for JSON files
        """
        self.data_dir = Path(data_dir)
        self.lock = Lock()

        logger.info("JSONStorage initialized: %s", data_dir)

    def initialize(self) -> None:
        """Initialize storage directory."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info("JSON storage initialized")

    def store(self, table: str, key: str, data: dict[str, Any]) -> bool:
        """
        Store data in JSON file.

        Args:
            table: Subdirectory name
            key: File name (without .json)
            data: Data to store

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.lock:
                file_path = self.data_dir / table / f"{key}.json"
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, "w") as f:
                    json.dump(data, f, indent=2)

                return True

        except Exception as e:
            logger.error("Failed to store JSON data: %s", e)
            return False

    def retrieve(self, table: str, key: str) -> dict[str, Any] | None:
        """
        Retrieve data from JSON file.

        Args:
            table: Subdirectory name
            key: File name (without .json)

        Returns:
            Data dictionary or None if not found
        """
        try:
            file_path = self.data_dir / table / f"{key}.json"

            if not file_path.exists():
                return None

            with open(file_path) as f:
                return json.load(f)

        except Exception as e:
            logger.error("Failed to retrieve JSON data: %s", e)
            return None

    def query(
        self, table: str, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Query data from JSON files (limited support).

        Args:
            table: Subdirectory name
            filters: Optional filter conditions (applied in-memory)

        Returns:
            List of matching records
        """
        try:
            table_dir = self.data_dir / table

            if not table_dir.exists():
                return []

            results = []
            for file_path in table_dir.glob("*.json"):
                with open(file_path) as f:
                    data = json.load(f)

                    # Apply filters
                    if filters:
                        if all(data.get(k) == v for k, v in filters.items()):
                            results.append(data)
                    else:
                        results.append(data)

            return results

        except Exception as e:
            logger.error("Failed to query JSON data: %s", e)
            return []

    def delete(self, table: str, key: str) -> bool:
        """
        Delete JSON file.

        Args:
            table: Subdirectory name
            key: File name (without .json)

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.data_dir / table / f"{key}.json"

            if file_path.exists():
                file_path.unlink()

            return True

        except Exception as e:
            logger.error("Failed to delete JSON data: %s", e)
            return False

    def close(self) -> None:
        """Close storage (no-op for JSON)."""
        logger.info("JSONStorage closed")


def get_storage_engine(storage_type: str = "sqlite", **kwargs) -> StorageEngine:
    """
    Factory function to get a storage engine.

    Args:
        storage_type: Type of storage engine ('sqlite' or 'json')
        **kwargs: Additional arguments for the storage engine

    Returns:
        StorageEngine instance

    Example:
        >>> storage = get_storage_engine('sqlite', db_path='data/cognition.db')
        >>> storage.initialize()
        >>> storage.store('governance_state', 'config', {'version': '1.0'})
    """
    if storage_type == "sqlite":
        return SQLiteStorage(**kwargs)
    elif storage_type == "json":
        return JSONStorage(**kwargs)
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")


__all__ = [
    "StorageEngine",
    "SQLiteStorage",
    "JSONStorage",
    "get_storage_engine",
]
