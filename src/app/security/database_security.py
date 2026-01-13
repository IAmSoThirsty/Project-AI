"""Secure database management with parameterized queries.

This module implements:
- Migration from pickle to parameterized SQL
- Query security with prepared statements
- Rollback capability and transaction management
- SQL injection prevention
"""

import json
import logging
import sqlite3
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)


class SecureDatabaseManager:
    """Secure database operations with SQL injection prevention."""

    # Whitelist of allowed columns for user updates
    ALLOWED_USER_COLUMNS = {"username", "password_hash", "email"}

    def __init__(self, db_path: str = "data/secure.db"):
        """Initialize secure database manager.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self) -> None:
        """Initialize database with secure schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """
            )

            # Create audit log table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    resource TEXT,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """
            )

            # Create agent state table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_state (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT UNIQUE NOT NULL,
                    state_data TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create knowledge base table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(category, key)
                )
            """
            )

            conn.commit()
            logger.info("Database initialized: %s", self.db_path)

    @contextmanager
    def _get_connection(self):
        """Get database connection with automatic commit/rollback.

        Yields:
            sqlite3.Connection
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error("Database transaction rolled back: %s", e)
            raise
        finally:
            conn.close()

    def execute_query(
        self, query: str, params: tuple = (), fetch: bool = False
    ) -> list[sqlite3.Row] | None:
        """Execute parameterized query safely.

        Args:
            query: SQL query with ? placeholders
            params: Query parameters
            fetch: Whether to fetch results

        Returns:
            Query results if fetch=True, None otherwise

        Raises:
            sqlite3.Error: If query execution fails
        """
        # Validate query doesn't contain dangerous patterns
        if not self._validate_query(query):
            raise ValueError("Query contains dangerous patterns")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch:
                return cursor.fetchall()

            return None

    def _validate_query(self, query: str) -> bool:
        """Validate query for safety.

        Args:
            query: SQL query to validate

        Returns:
            True if query is safe
        """
        query_upper = query.upper()

        # Check for dynamic SQL (should use parameters instead)
        dangerous_patterns = [
            "EXEC(",
            "EXECUTE(",
            "sp_executesql",
            "xp_cmdshell",
            "--",  # SQL comments
            "/*",  # Multi-line comments
            "';",  # Statement terminator with quote
        ]

        for pattern in dangerous_patterns:
            if pattern.upper() in query_upper:
                logger.warning("Dangerous pattern in query: %s", pattern)
                return False

        return True

    def insert_user(
        self, username: str, password_hash: str, email: str | None = None
    ) -> int:
        """Insert new user with parameterized query.

        Args:
            username: Username
            password_hash: Hashed password
            email: Optional email

        Returns:
            User ID

        Raises:
            sqlite3.IntegrityError: If username already exists
        """
        query = """
            INSERT INTO users (username, password_hash, email)
            VALUES (?, ?, ?)
        """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (username, password_hash, email))
            user_id = cursor.lastrowid

        logger.info("User created: %s (id: %d)", username, user_id)
        return user_id

    def get_user(self, username: str) -> dict[str, Any] | None:
        """Get user by username with parameterized query.

        Args:
            username: Username to lookup

        Returns:
            User data dictionary or None
        """
        query = "SELECT * FROM users WHERE username = ?"

        rows = self.execute_query(query, (username,), fetch=True)

        if rows:
            return dict(rows[0])

        return None

    def update_user(self, user_id: int, **kwargs) -> None:
        """Update user fields with parameterized query.

        Args:
            user_id: User ID
            **kwargs: Fields to update

        Raises:
            ValueError: If invalid column name provided
        """
        if not kwargs:
            return

        # Validate all column names against whitelist
        invalid_columns = set(kwargs.keys()) - self.ALLOWED_USER_COLUMNS
        if invalid_columns:
            raise ValueError(f"Invalid column names: {invalid_columns}")

        # Build query dynamically with parameters - safe now since columns are validated
        set_clauses = [f"{key} = ?" for key in kwargs]
        values = list(kwargs.values()) + [user_id]

        query = f"""
            UPDATE users
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """  # nosec B608 - Column names are validated against whitelist above, parameters are properly escaped

        self.execute_query(query, tuple(values))
        logger.info("User %d updated", user_id)

    def log_action(
        self,
        user_id: int | None,
        action: str,
        resource: str | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> None:
        """Log user action to audit log.

        Args:
            user_id: User ID (None for system actions)
            action: Action performed
            resource: Resource affected
            details: Additional details
            ip_address: Client IP address
        """
        query = """
            INSERT INTO audit_log (user_id, action, resource, details, ip_address)
            VALUES (?, ?, ?, ?, ?)
        """

        details_json = json.dumps(details) if details else None

        self.execute_query(
            query, (user_id, action, resource, details_json, ip_address)
        )

    def get_audit_log(
        self, user_id: int | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """Get audit log entries.

        Args:
            user_id: Optional user ID filter
            limit: Maximum number of entries

        Returns:
            List of audit log entries
        """
        if user_id is not None:
            query = """
                SELECT * FROM audit_log
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """
            params = (user_id, limit)
        else:
            query = """
                SELECT * FROM audit_log
                ORDER BY timestamp DESC
                LIMIT ?
            """
            params = (limit,)

        rows = self.execute_query(query, params, fetch=True)
        return [dict(row) for row in rows]

    def save_agent_state(self, agent_id: str, state_data: dict[str, Any]) -> None:
        """Save agent state to database.

        Args:
            agent_id: Agent identifier
            state_data: State data to save
        """
        state_json = json.dumps(state_data)

        query = """
            INSERT INTO agent_state (agent_id, state_data)
            VALUES (?, ?)
            ON CONFLICT(agent_id) DO UPDATE SET
                state_data = excluded.state_data,
                updated_at = CURRENT_TIMESTAMP
        """

        self.execute_query(query, (agent_id, state_json))
        logger.debug("Agent state saved: %s", agent_id)

    def load_agent_state(self, agent_id: str) -> dict[str, Any] | None:
        """Load agent state from database.

        Args:
            agent_id: Agent identifier

        Returns:
            State data or None
        """
        query = "SELECT state_data FROM agent_state WHERE agent_id = ?"

        rows = self.execute_query(query, (agent_id,), fetch=True)

        if rows:
            return json.loads(rows[0]["state_data"])

        return None

    def store_knowledge(
        self, category: str, key: str, value: Any, metadata: dict | None = None
    ) -> None:
        """Store knowledge in database.

        Args:
            category: Knowledge category
            key: Knowledge key
            value: Knowledge value
            metadata: Optional metadata
        """
        value_json = json.dumps(value)
        metadata_json = json.dumps(metadata) if metadata else None

        query = """
            INSERT INTO knowledge_base (category, key, value, metadata)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(category, key) DO UPDATE SET
                value = excluded.value,
                metadata = excluded.metadata,
                updated_at = CURRENT_TIMESTAMP
        """

        self.execute_query(query, (category, key, value_json, metadata_json))
        logger.debug("Knowledge stored: %s/%s", category, key)

    def get_knowledge(
        self, category: str, key: str | None = None
    ) -> list[dict[str, Any]]:
        """Get knowledge from database.

        Args:
            category: Knowledge category
            key: Optional specific key

        Returns:
            List of knowledge entries
        """
        if key is not None:
            query = "SELECT * FROM knowledge_base WHERE category = ? AND key = ?"
            params = (category, key)
        else:
            query = "SELECT * FROM knowledge_base WHERE category = ?"
            params = (category,)

        rows = self.execute_query(query, params, fetch=True)
        return [dict(row) for row in rows]

    @contextmanager
    def transaction(self):
        """Context manager for explicit transaction control.

        Yields:
            sqlite3.Connection

        Example:
            with db.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT ...")
                cursor.execute("UPDATE ...")
        """
        with self._get_connection() as conn:
            yield conn
