"""
Build Memory Database Schema and Interface.

Provides comprehensive SQLite-based storage for build history, constitutional
violations, policy decisions, security events, artifacts, and dependencies.
"""

import logging
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from .sql_utils import sanitize_identifier_list

logger = logging.getLogger(__name__)


class BuildMemoryDB:
    """
    Main database interface for build memory storage.

    Manages SQLite database with ACID transactions, WAL mode for concurrency,
    and comprehensive indexing for fast queries.
    """

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str | Path | None = None):
        """
        Initialize build memory database.

        Args:
            db_path: Path to SQLite database file. Defaults to data/build_memory.db
        """
        if db_path is None:
            data_dir = Path("data")
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = data_dir / "build_memory.db"
        else:
            db_path = Path(db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None
        self._initialize_database()
        logger.info("BuildMemoryDB initialized at %s", self.db_path)

    def _initialize_database(self) -> None:
        """Initialize database with schema and enable WAL mode."""
        with self.get_connection() as conn:
            # Enable WAL mode for concurrent access
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.execute("PRAGMA cache_size=-64000")  # 64MB cache

            self._create_schema(conn)
            self._create_indexes(conn)
            self._store_schema_version(conn)
            conn.commit()

    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.

        Yields:
            sqlite3.Connection: Database connection with row factory
        """
        conn = sqlite3.connect(
            self.db_path,
            timeout=30.0,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _create_schema(self, conn: sqlite3.Connection) -> None:
        """Create database schema with all tables."""
        # Builds table - main build records
        conn.execute("""
            CREATE TABLE IF NOT EXISTS builds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                version TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('success', 'failure', 'cancelled', 'running')),
                duration REAL,
                capsule_id TEXT,
                constitutional_status TEXT CHECK(constitutional_status IN ('compliant', 'violated', 'waived', 'pending')),
                gradle_version TEXT,
                java_version TEXT,
                os_info TEXT,
                host_name TEXT,
                user_name TEXT,
                exit_code INTEGER,
                error_message TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Build phases - tracks individual build phases
        conn.execute("""
            CREATE TABLE IF NOT EXISTS build_phases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                build_id INTEGER NOT NULL,
                phase TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('success', 'failure', 'skipped', 'running')),
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration REAL,
                artifacts TEXT,
                logs_path TEXT,
                resource_usage TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE
            )
        """)

        # Constitutional violations - tracks principle violations
        conn.execute("""
            CREATE TABLE IF NOT EXISTS constitutional_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                build_id INTEGER NOT NULL,
                phase TEXT NOT NULL,
                principle TEXT NOT NULL,
                severity TEXT NOT NULL CHECK(severity IN ('critical', 'high', 'medium', 'low', 'info')),
                reason TEXT NOT NULL,
                waived BOOLEAN DEFAULT 0,
                waiver_reason TEXT,
                waived_by TEXT,
                waived_at TEXT,
                detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE
            )
        """)

        # Policy decisions - tracks policy evaluation results
        conn.execute("""
            CREATE TABLE IF NOT EXISTS policy_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                build_id INTEGER NOT NULL,
                policy_id TEXT NOT NULL,
                policy_name TEXT,
                decision TEXT NOT NULL CHECK(decision IN ('allow', 'deny', 'warn')),
                reason TEXT NOT NULL,
                human_override BOOLEAN DEFAULT 0,
                override_reason TEXT,
                overridden_by TEXT,
                overridden_at TEXT,
                context TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE
            )
        """)

        # Security events - tracks security-related events
        conn.execute("""
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                build_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL CHECK(severity IN ('critical', 'high', 'medium', 'low', 'info')),
                details TEXT NOT NULL,
                remediated BOOLEAN DEFAULT 0,
                remediation_details TEXT,
                remediated_by TEXT,
                remediated_at TEXT,
                cve_ids TEXT,
                cvss_score REAL,
                affected_components TEXT,
                detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE
            )
        """)

        # Artifacts - tracks build artifacts
        conn.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                build_id INTEGER NOT NULL,
                path TEXT NOT NULL,
                hash TEXT NOT NULL,
                size INTEGER NOT NULL,
                type TEXT NOT NULL,
                signed BOOLEAN DEFAULT 0,
                signature_hash TEXT,
                signature_algorithm TEXT,
                checksum_algorithm TEXT DEFAULT 'SHA-256',
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE
            )
        """)

        # Dependencies - tracks build dependencies
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dependencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                build_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                hash TEXT,
                source TEXT,
                vulnerabilities TEXT,
                vulnerability_count INTEGER DEFAULT 0,
                license TEXT,
                scope TEXT,
                transitive BOOLEAN DEFAULT 0,
                parent_dependency_id INTEGER,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (build_id) REFERENCES builds(id) ON DELETE CASCADE,
                FOREIGN KEY (parent_dependency_id) REFERENCES dependencies(id) ON DELETE CASCADE
            )
        """)

        # Schema metadata
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def _create_indexes(self, conn: sqlite3.Connection) -> None:
        """Create database indexes for query optimization."""
        indexes = [
            # Builds indexes
            "CREATE INDEX IF NOT EXISTS idx_builds_timestamp ON builds(timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_builds_status ON builds(status)",
            "CREATE INDEX IF NOT EXISTS idx_builds_version ON builds(version)",
            "CREATE INDEX IF NOT EXISTS idx_builds_capsule ON builds(capsule_id)",
            "CREATE INDEX IF NOT EXISTS idx_builds_constitutional ON builds(constitutional_status)",

            # Build phases indexes
            "CREATE INDEX IF NOT EXISTS idx_phases_build_id ON build_phases(build_id)",
            "CREATE INDEX IF NOT EXISTS idx_phases_phase ON build_phases(phase)",
            "CREATE INDEX IF NOT EXISTS idx_phases_status ON build_phases(status)",

            # Constitutional violations indexes
            "CREATE INDEX IF NOT EXISTS idx_violations_build_id ON constitutional_violations(build_id)",
            "CREATE INDEX IF NOT EXISTS idx_violations_principle ON constitutional_violations(principle)",
            "CREATE INDEX IF NOT EXISTS idx_violations_severity ON constitutional_violations(severity)",
            "CREATE INDEX IF NOT EXISTS idx_violations_waived ON constitutional_violations(waived)",

            # Policy decisions indexes
            "CREATE INDEX IF NOT EXISTS idx_policies_build_id ON policy_decisions(build_id)",
            "CREATE INDEX IF NOT EXISTS idx_policies_policy_id ON policy_decisions(policy_id)",
            "CREATE INDEX IF NOT EXISTS idx_policies_decision ON policy_decisions(decision)",

            # Security events indexes
            "CREATE INDEX IF NOT EXISTS idx_security_build_id ON security_events(build_id)",
            "CREATE INDEX IF NOT EXISTS idx_security_type ON security_events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_security_severity ON security_events(severity)",
            "CREATE INDEX IF NOT EXISTS idx_security_remediated ON security_events(remediated)",

            # Artifacts indexes
            "CREATE INDEX IF NOT EXISTS idx_artifacts_build_id ON artifacts(build_id)",
            "CREATE INDEX IF NOT EXISTS idx_artifacts_hash ON artifacts(hash)",
            "CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(type)",
            "CREATE INDEX IF NOT EXISTS idx_artifacts_path ON artifacts(path)",

            # Dependencies indexes
            "CREATE INDEX IF NOT EXISTS idx_deps_build_id ON dependencies(build_id)",
            "CREATE INDEX IF NOT EXISTS idx_deps_name_version ON dependencies(name, version)",
            "CREATE INDEX IF NOT EXISTS idx_deps_vulnerabilities ON dependencies(vulnerability_count)",
            "CREATE INDEX IF NOT EXISTS idx_deps_parent ON dependencies(parent_dependency_id)",
        ]

        for index_sql in indexes:
            conn.execute(index_sql)

    def _store_schema_version(self, conn: sqlite3.Connection) -> None:
        """Store schema version in metadata table."""
        conn.execute(
            "INSERT OR REPLACE INTO schema_metadata (key, value) VALUES (?, ?)",
            ("schema_version", str(self.SCHEMA_VERSION)),
        )

    def get_schema_version(self) -> int:
        """Get current schema version from database."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM schema_metadata WHERE key = ?",
                ("schema_version",),
            )
            row = cursor.fetchone()
            return int(row["value"]) if row else 0

    # ==================== CRUD Operations: Builds ====================

    def create_build(
        self,
        version: str,
        status: str = "running",
        capsule_id: str | None = None,
        constitutional_status: str | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs,
    ) -> int:
        """
        Create a new build record.

        Args:
            version: Build version
            status: Build status (success, failure, cancelled, running)
            capsule_id: Associated capsule ID
            constitutional_status: Constitutional compliance status
            metadata: Additional metadata as JSON
            **kwargs: Additional build fields

        Returns:
            int: Build ID

        Raises:
            sqlite3.Error: If database operation fails
        """
        import json

        timestamp = datetime.utcnow().isoformat()

        with self.get_connection() as conn:
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO builds (
                        timestamp, version, status, capsule_id, constitutional_status,
                        gradle_version, java_version, os_info, host_name, user_name,
                        metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        timestamp,
                        version,
                        status,
                        capsule_id,
                        constitutional_status,
                        kwargs.get("gradle_version"),
                        kwargs.get("java_version"),
                        kwargs.get("os_info"),
                        kwargs.get("host_name"),
                        kwargs.get("user_name"),
                        json.dumps(metadata) if metadata else None,
                    ),
                )
                conn.commit()
                build_id = cursor.lastrowid
                logger.info("Created build %s for version %s", build_id, version)
                return build_id
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to create build: %s", e)
                raise

    def update_build(
        self,
        build_id: int,
        status: str | None = None,
        duration: float | None = None,
        constitutional_status: str | None = None,
        exit_code: int | None = None,
        error_message: str | None = None,
        **kwargs,
    ) -> bool:
        """
        Update an existing build record.

        Args:
            build_id: Build ID
            status: New status
            duration: Build duration in seconds
            constitutional_status: New constitutional status
            exit_code: Process exit code
            error_message: Error message if failed
            **kwargs: Additional fields to update

        Returns:
            bool: True if updated successfully
        """
        updates = []
        params = []

        if status:
            updates.append("status = ?")
            params.append(status)
        if duration is not None:
            updates.append("duration = ?")
            params.append(duration)
        if constitutional_status:
            updates.append("constitutional_status = ?")
            params.append(constitutional_status)
        if exit_code is not None:
            updates.append("exit_code = ?")
            params.append(exit_code)
        if error_message:
            updates.append("error_message = ?")
            params.append(error_message)

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(build_id)

        if not updates:
            return True

        with self.get_connection() as conn:
            try:
                # Sanitize column names to prevent SQL injection
                # Extract column names from "column = ?" format and validate
                column_names = [u.split(" = ?")[0].strip() for u in updates if " = ?" in u]
                safe_columns = sanitize_identifier_list(column_names)
                # Rebuild updates list with sanitized column names
                safe_updates = [f"{col} = ?" for col in safe_columns]
                # Add the timestamp update that doesn't have a placeholder
                if "updated_at = CURRENT_TIMESTAMP" in updates:
                    safe_updates.append("updated_at = CURRENT_TIMESTAMP")
                
                conn.execute(
                    f"UPDATE builds SET {', '.join(safe_updates)} WHERE id = ?",
                    params,
                )
                conn.commit()
                logger.debug("Updated build %s", build_id)
                return True
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to update build %s: %s", build_id, e)
                return False

    def get_build(self, build_id: int) -> dict[str, Any] | None:
        """
        Get build record by ID.

        Args:
            build_id: Build ID

        Returns:
            Dict with build data or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM builds WHERE id = ?", (build_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_builds(
        self,
        limit: int = 100,
        offset: int = 0,
        status: str | None = None,
        version: str | None = None,
        constitutional_status: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Query builds with filters.

        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            status: Filter by status
            version: Filter by version
            constitutional_status: Filter by constitutional status

        Returns:
            List of build records
        """
        query = "SELECT * FROM builds WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if version:
            query += " AND version = ?"
            params.append(version)
        if constitutional_status:
            query += " AND constitutional_status = ?"
            params.append(constitutional_status)

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def delete_build(self, build_id: int) -> bool:
        """
        Delete build and all related records (cascading).

        Args:
            build_id: Build ID

        Returns:
            bool: True if deleted successfully
        """
        with self.get_connection() as conn:
            try:
                conn.execute("DELETE FROM builds WHERE id = ?", (build_id,))
                conn.commit()
                logger.info("Deleted build %s", build_id)
                return True
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to delete build %s: %s", build_id, e)
                return False

    # ==================== CRUD Operations: Build Phases ====================

    def create_build_phase(
        self,
        build_id: int,
        phase: str,
        status: str = "running",
        artifacts: list[str] | None = None,
        logs_path: str | None = None,
        **kwargs,
    ) -> int:
        """Create build phase record."""
        import json

        start_time = datetime.utcnow().isoformat()

        with self.get_connection() as conn:
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO build_phases (
                        build_id, phase, status, start_time, artifacts, logs_path, resource_usage
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        build_id,
                        phase,
                        status,
                        start_time,
                        json.dumps(artifacts) if artifacts else None,
                        logs_path,
                        json.dumps(kwargs.get("resource_usage")) if kwargs.get("resource_usage") else None,
                    ),
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to create build phase: %s", e)
                raise

    def update_build_phase(
        self,
        phase_id: int,
        status: str | None = None,
        end_time: str | None = None,
        duration: float | None = None,
    ) -> bool:
        """Update build phase record."""
        updates = []
        params = []

        if status:
            updates.append("status = ?")
            params.append(status)
        if end_time:
            updates.append("end_time = ?")
            params.append(end_time)
        if duration is not None:
            updates.append("duration = ?")
            params.append(duration)

        if not updates:
            return True

        params.append(phase_id)

        with self.get_connection() as conn:
            try:
                # Sanitize column names to prevent SQL injection
                column_names = [u.split(" = ?")[0].strip() for u in updates]
                safe_columns = sanitize_identifier_list(column_names)
                safe_updates = [f"{col} = ?" for col in safe_columns]
                
                conn.execute(
                    f"UPDATE build_phases SET {', '.join(safe_updates)} WHERE id = ?",
                    params,
                )
                conn.commit()
                return True
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to update build phase %s: %s", phase_id, e)
                return False

    def get_build_phases(self, build_id: int) -> list[dict[str, Any]]:
        """Get all phases for a build."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM build_phases WHERE build_id = ? ORDER BY start_time",
                (build_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    # ==================== CRUD Operations: Constitutional Violations ====================

    def create_violation(
        self,
        build_id: int,
        phase: str,
        principle: str,
        severity: str,
        reason: str,
    ) -> int:
        """Create constitutional violation record."""
        with self.get_connection() as conn:
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO constitutional_violations (
                        build_id, phase, principle, severity, reason
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (build_id, phase, principle, severity, reason),
                )
                conn.commit()
                logger.warning("Recorded %s violation for build %s: %s", severity, build_id, principle)
                return cursor.lastrowid
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to create violation: %s", e)
                raise

    def waive_violation(
        self,
        violation_id: int,
        waiver_reason: str,
        waived_by: str,
    ) -> bool:
        """Waive a constitutional violation."""
        with self.get_connection() as conn:
            try:
                conn.execute(
                    """
                    UPDATE constitutional_violations
                    SET waived = 1, waiver_reason = ?, waived_by = ?, waived_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (waiver_reason, waived_by, violation_id),
                )
                conn.commit()
                logger.info("Waived violation %s by %s", violation_id, waived_by)
                return True
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to waive violation %s: %s", violation_id, e)
                return False

    def get_violations(
        self,
        build_id: int | None = None,
        severity: str | None = None,
        waived: bool | None = None,
    ) -> list[dict[str, Any]]:
        """Query constitutional violations."""
        query = "SELECT * FROM constitutional_violations WHERE 1=1"
        params = []

        if build_id is not None:
            query += " AND build_id = ?"
            params.append(build_id)
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        if waived is not None:
            query += " AND waived = ?"
            params.append(1 if waived else 0)

        query += " ORDER BY detected_at DESC"

        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    # ==================== CRUD Operations: Policy Decisions ====================

    def create_policy_decision(
        self,
        build_id: int,
        policy_id: str,
        decision: str,
        reason: str,
        policy_name: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> int:
        """Create policy decision record."""
        import json

        with self.get_connection() as conn:
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO policy_decisions (
                        build_id, policy_id, policy_name, decision, reason, context
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        build_id,
                        policy_id,
                        policy_name,
                        decision,
                        reason,
                        json.dumps(context) if context else None,
                    ),
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to create policy decision: %s", e)
                raise

    def override_policy_decision(
        self,
        decision_id: int,
        override_reason: str,
        overridden_by: str,
    ) -> bool:
        """Override a policy decision."""
        with self.get_connection() as conn:
            try:
                conn.execute(
                    """
                    UPDATE policy_decisions
                    SET human_override = 1, override_reason = ?, overridden_by = ?,
                        overridden_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (override_reason, overridden_by, decision_id),
                )
                conn.commit()
                logger.info("Overridden policy decision %s by %s", decision_id, overridden_by)
                return True
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to override policy decision %s: %s", decision_id, e)
                return False

    def get_policy_decisions(self, build_id: int) -> list[dict[str, Any]]:
        """Get policy decisions for a build."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM policy_decisions WHERE build_id = ? ORDER BY created_at",
                (build_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    # ==================== CRUD Operations: Security Events ====================

    def create_security_event(
        self,
        build_id: int,
        event_type: str,
        severity: str,
        details: str,
        cve_ids: list[str] | None = None,
        cvss_score: float | None = None,
        affected_components: list[str] | None = None,
    ) -> int:
        """Create security event record."""
        import json

        with self.get_connection() as conn:
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO security_events (
                        build_id, event_type, severity, details, cve_ids, cvss_score, affected_components
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        build_id,
                        event_type,
                        severity,
                        details,
                        json.dumps(cve_ids) if cve_ids else None,
                        cvss_score,
                        json.dumps(affected_components) if affected_components else None,
                    ),
                )
                conn.commit()
                logger.warning("Recorded %s security event for build %s: %s", severity, build_id, event_type)
                return cursor.lastrowid
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to create security event: %s", e)
                raise

    def remediate_security_event(
        self,
        event_id: int,
        remediation_details: str,
        remediated_by: str,
    ) -> bool:
        """Mark security event as remediated."""
        with self.get_connection() as conn:
            try:
                conn.execute(
                    """
                    UPDATE security_events
                    SET remediated = 1, remediation_details = ?, remediated_by = ?,
                        remediated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (remediation_details, remediated_by, event_id),
                )
                conn.commit()
                logger.info("Remediated security event %s by %s", event_id, remediated_by)
                return True
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to remediate security event %s: %s", event_id, e)
                return False

    def get_security_events(
        self,
        build_id: int | None = None,
        severity: str | None = None,
        remediated: bool | None = None,
    ) -> list[dict[str, Any]]:
        """Query security events."""
        query = "SELECT * FROM security_events WHERE 1=1"
        params = []

        if build_id is not None:
            query += " AND build_id = ?"
            params.append(build_id)
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        if remediated is not None:
            query += " AND remediated = ?"
            params.append(1 if remediated else 0)

        query += " ORDER BY detected_at DESC"

        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    # ==================== CRUD Operations: Artifacts ====================

    def create_artifact(
        self,
        build_id: int,
        path: str,
        hash: str,
        size: int,
        artifact_type: str,
        signed: bool = False,
        signature_hash: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        """Create artifact record."""
        import json

        with self.get_connection() as conn:
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO artifacts (
                        build_id, path, hash, size, type, signed, signature_hash, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        build_id,
                        path,
                        hash,
                        size,
                        artifact_type,
                        1 if signed else 0,
                        signature_hash,
                        json.dumps(metadata) if metadata else None,
                    ),
                )
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to create artifact: %s", e)
                raise

    def get_artifacts(self, build_id: int) -> list[dict[str, Any]]:
        """Get all artifacts for a build."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM artifacts WHERE build_id = ? ORDER BY created_at",
                (build_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def find_artifact_by_hash(self, hash: str) -> dict[str, Any] | None:
        """Find artifact by hash across all builds."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM artifacts WHERE hash = ? ORDER BY created_at DESC LIMIT 1",
                (hash,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    # ==================== CRUD Operations: Dependencies ====================

    def create_dependency(
        self,
        build_id: int,
        name: str,
        version: str,
        hash: str | None = None,
        source: str | None = None,
        vulnerabilities: list[dict[str, Any]] | None = None,
        license: str | None = None,
        scope: str | None = None,
        transitive: bool = False,
        parent_dependency_id: int | None = None,
    ) -> int:
        """Create dependency record."""
        import json

        vuln_count = len(vulnerabilities) if vulnerabilities else 0

        with self.get_connection() as conn:
            try:
                cursor = conn.execute(
                    """
                    INSERT INTO dependencies (
                        build_id, name, version, hash, source, vulnerabilities,
                        vulnerability_count, license, scope, transitive, parent_dependency_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        build_id,
                        name,
                        version,
                        hash,
                        source,
                        json.dumps(vulnerabilities) if vulnerabilities else None,
                        vuln_count,
                        license,
                        scope,
                        1 if transitive else 0,
                        parent_dependency_id,
                    ),
                )
                conn.commit()
                if vuln_count > 0:
                    logger.warning("Dependency %s:%s has %s vulnerabilities", name, version, vuln_count)
                return cursor.lastrowid
            except sqlite3.Error as e:
                conn.rollback()
                logger.error("Failed to create dependency: %s", e)
                raise

    def get_dependencies(
        self,
        build_id: int,
        vulnerable_only: bool = False,
    ) -> list[dict[str, Any]]:
        """Get dependencies for a build."""
        query = "SELECT * FROM dependencies WHERE build_id = ?"
        params = [build_id]

        if vulnerable_only:
            query += " AND vulnerability_count > 0"

        query += " ORDER BY name, version"

        with self.get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_vulnerable_dependencies(
        self,
        severity_threshold: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get all vulnerable dependencies across builds."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT d.*, b.version as build_version, b.timestamp as build_timestamp
                FROM dependencies d
                JOIN builds b ON d.build_id = b.id
                WHERE d.vulnerability_count > 0
                ORDER BY d.vulnerability_count DESC, b.timestamp DESC
                """,
            )
            return [dict(row) for row in cursor.fetchall()]

    # ==================== Utility Methods ====================

    def vacuum(self) -> bool:
        """Vacuum database to reclaim space and optimize."""
        with self.get_connection() as conn:
            try:
                conn.execute("VACUUM")
                conn.commit()
                logger.info("Database vacuumed successfully")
                return True
            except sqlite3.Error as e:
                logger.error("Failed to vacuum database: %s", e)
                return False

    def get_database_size(self) -> int:
        """Get database file size in bytes."""
        return os.path.getsize(self.db_path)

    def get_statistics(self) -> dict[str, int]:
        """Get database statistics."""
        with self.get_connection() as conn:
            stats = {}
            tables = [
                "builds",
                "build_phases",
                "constitutional_violations",
                "policy_decisions",
                "security_events",
                "artifacts",
                "dependencies",
            ]
            for table in tables:
                cursor = conn.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[table] = cursor.fetchone()["count"]
            return stats

    def close(self) -> None:
        """Close database connection if open."""
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.debug("Database connection closed")
