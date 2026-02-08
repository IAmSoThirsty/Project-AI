"""
Database Schema Versioning and Migration System.

Provides automatic schema migrations with version tracking, rollback support,
and data migration helpers.
"""

import logging
import sqlite3
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from .sql_utils import sanitize_identifier, sanitize_identifier_list

logger = logging.getLogger(__name__)


class Migration:
    """Represents a single database migration."""

    def __init__(
        self,
        version: int,
        description: str,
        up: Callable[[sqlite3.Connection], None],
        down: Callable[[sqlite3.Connection], None] | None = None,
    ):
        """
        Initialize migration.

        Args:
            version: Migration version number (sequential)
            description: Human-readable description
            up: Function to apply migration
            down: Function to rollback migration (optional)
        """
        self.version = version
        self.description = description
        self.up = up
        self.down = down

    def apply(self, conn: sqlite3.Connection) -> None:
        """Apply migration."""
        logger.info("Applying migration %s: %s", self.version, self.description)
        try:
            self.up(conn)
            conn.commit()
            logger.info("Migration %s applied successfully", self.version)
        except Exception as e:
            conn.rollback()
            logger.error("Failed to apply migration %s: %s", self.version, e)
            raise

    def rollback(self, conn: sqlite3.Connection) -> None:
        """Rollback migration."""
        if not self.down:
            raise ValueError(f"Migration {self.version} has no rollback function")

        logger.info("Rolling back migration %s: %s", self.version, self.description)
        try:
            self.down(conn)
            conn.commit()
            logger.info("Migration %s rolled back successfully", self.version)
        except Exception as e:
            conn.rollback()
            logger.error("Failed to rollback migration %s: %s", self.version, e)
            raise


class MigrationManager:
    """
    Database migration manager.

    Handles schema versioning, automatic migrations, and rollbacks.
    """

    def __init__(self, db_path: Path):
        """
        Initialize migration manager.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.migrations: list[Migration] = []
        self._register_migrations()
        logger.info("MigrationManager initialized with %s migrations", len(self.migrations))

    def _register_migrations(self) -> None:
        """Register all migrations."""
        self.migrations = [
            Migration(
                version=1,
                description="Initial schema",
                up=self._migration_1_up,
                down=self._migration_1_down,
            ),
            Migration(
                version=2,
                description="Add build metadata fields",
                up=self._migration_2_up,
                down=self._migration_2_down,
            ),
            Migration(
                version=3,
                description="Add security event tracking",
                up=self._migration_3_up,
                down=self._migration_3_down,
            ),
            Migration(
                version=4,
                description="Add dependency vulnerability tracking",
                up=self._migration_4_up,
                down=self._migration_4_down,
            ),
            Migration(
                version=5,
                description="Add artifact signing metadata",
                up=self._migration_5_up,
                down=self._migration_5_down,
            ),
        ]

    def get_current_version(self) -> int:
        """Get current schema version from database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "SELECT value FROM schema_metadata WHERE key = 'schema_version'"
                )
                row = cursor.fetchone()
                if row:
                    return int(row[0])
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            pass
        return 0

    def get_latest_version(self) -> int:
        """Get latest available migration version."""
        return max((m.version for m in self.migrations), default=0)

    def get_pending_migrations(self) -> list[Migration]:
        """Get list of pending migrations."""
        current = self.get_current_version()
        return [m for m in self.migrations if m.version > current]

    def migrate(self, target_version: int | None = None) -> bool:
        """
        Apply pending migrations.

        Args:
            target_version: Target version to migrate to (default: latest)

        Returns:
            bool: True if successful

        Raises:
            Exception: If migration fails
        """
        current_version = self.get_current_version()
        target = target_version or self.get_latest_version()

        if current_version == target:
            logger.info("Database already at version %s", target)
            return True

        if current_version > target:
            logger.error("Cannot migrate backwards (current: %s, target: %s)", current_version, target)
            return False

        pending = [m for m in self.migrations if current_version < m.version <= target]
        pending.sort(key=lambda m: m.version)

        if not pending:
            logger.info("No pending migrations")
            return True

        logger.info("Applying %s migrations (%s -> %s)", len(pending), current_version, target)

        with self._get_connection() as conn:
            for migration in pending:
                try:
                    migration.apply(conn)
                    self._update_version(conn, migration.version)
                except Exception as e:
                    logger.error("Migration failed at version %s: %s", migration.version, e)
                    raise

        logger.info("Successfully migrated to version %s", target)
        return True

    def rollback(self, target_version: int | None = None) -> bool:
        """
        Rollback migrations.

        Args:
            target_version: Target version to rollback to (default: previous version)

        Returns:
            bool: True if successful

        Raises:
            Exception: If rollback fails
        """
        current_version = self.get_current_version()
        target = target_version if target_version is not None else current_version - 1

        if current_version <= target:
            logger.error("Cannot rollback forwards (current: %s, target: %s)", current_version, target)
            return False

        to_rollback = [m for m in self.migrations if target < m.version <= current_version]
        to_rollback.sort(key=lambda m: m.version, reverse=True)

        if not to_rollback:
            logger.info("No migrations to rollback")
            return True

        logger.info("Rolling back %s migrations (%s -> %s)", len(to_rollback), current_version, target)

        with self._get_connection() as conn:
            for migration in to_rollback:
                try:
                    migration.rollback(conn)
                    self._update_version(conn, migration.version - 1)
                except Exception as e:
                    logger.error("Rollback failed at version %s: %s", migration.version, e)
                    raise

        logger.info("Successfully rolled back to version %s", target)
        return True

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self.db_path, timeout=30.0)

    def _update_version(self, conn: sqlite3.Connection, version: int) -> None:
        """Update schema version in database."""
        # Ensure schema_metadata table exists
        conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute(
            "INSERT OR REPLACE INTO schema_metadata (key, value, updated_at) VALUES (?, ?, ?)",
            ("schema_version", str(version), datetime.utcnow().isoformat()),
        )

        # Record migration in history
        conn.execute("""
            CREATE TABLE IF NOT EXISTS migration_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version INTEGER NOT NULL,
                description TEXT,
                applied_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        migration = next((m for m in self.migrations if m.version == version), None)
        description = migration.description if migration else f"Version {version}"

        conn.execute(
            "INSERT INTO migration_history (version, description) VALUES (?, ?)",
            (version, description),
        )

    def get_migration_history(self) -> list[dict[str, Any]]:
        """Get migration history."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT version, description, applied_at
                    FROM migration_history
                    ORDER BY version DESC
                """)
                return [
                    {
                        "version": row[0],
                        "description": row[1],
                        "applied_at": row[2],
                    }
                    for row in cursor.fetchall()
                ]
        except sqlite3.OperationalError:
            return []

    # ==================== Migration Definitions ====================

    def _migration_1_up(self, conn: sqlite3.Connection) -> None:
        """Initial schema creation."""
        # This is handled by BuildMemoryDB._create_schema
        # Just mark as complete
        pass

    def _migration_1_down(self, conn: sqlite3.Connection) -> None:
        """Drop initial schema."""
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
            conn.execute(f"DROP TABLE IF EXISTS {table}")

    def _migration_2_up(self, conn: sqlite3.Connection) -> None:
        """Add build metadata fields."""
        # Add columns if they don't exist
        columns_to_add = [
            ("builds", "gradle_version", "TEXT"),
            ("builds", "java_version", "TEXT"),
            ("builds", "os_info", "TEXT"),
            ("builds", "host_name", "TEXT"),
            ("builds", "user_name", "TEXT"),
        ]

        for table, column, col_type in columns_to_add:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                logger.debug("Added column %s to %s", column, table)
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise

    def _migration_2_down(self, conn: sqlite3.Connection) -> None:
        """Remove build metadata fields."""
        # SQLite doesn't support DROP COLUMN easily, would need table recreation
        logger.warning("Migration 2 rollback not fully implemented (SQLite limitation)")

    def _migration_3_up(self, conn: sqlite3.Connection) -> None:
        """Add security event tracking fields."""
        columns_to_add = [
            ("security_events", "cve_ids", "TEXT"),
            ("security_events", "cvss_score", "REAL"),
            ("security_events", "affected_components", "TEXT"),
        ]

        for table, column, col_type in columns_to_add:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                logger.debug("Added column %s to %s", column, table)
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise

    def _migration_3_down(self, conn: sqlite3.Connection) -> None:
        """Remove security event tracking fields."""
        logger.warning("Migration 3 rollback not fully implemented (SQLite limitation)")

    def _migration_4_up(self, conn: sqlite3.Connection) -> None:
        """Add dependency vulnerability tracking."""
        columns_to_add = [
            ("dependencies", "vulnerability_count", "INTEGER DEFAULT 0"),
            ("dependencies", "license", "TEXT"),
            ("dependencies", "scope", "TEXT"),
        ]

        for table, column, col_type in columns_to_add:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                logger.debug("Added column %s to %s", column, table)
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise

        # Create index on vulnerability_count
        try:
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_deps_vulnerabilities "
                "ON dependencies(vulnerability_count)"
            )
        except sqlite3.OperationalError:
            pass

    def _migration_4_down(self, conn: sqlite3.Connection) -> None:
        """Remove dependency vulnerability tracking."""
        try:
            conn.execute("DROP INDEX IF EXISTS idx_deps_vulnerabilities")
        except sqlite3.OperationalError:
            pass
        logger.warning("Migration 4 rollback not fully implemented (SQLite limitation)")

    def _migration_5_up(self, conn: sqlite3.Connection) -> None:
        """Add artifact signing metadata."""
        columns_to_add = [
            ("artifacts", "signature_hash", "TEXT"),
            ("artifacts", "signature_algorithm", "TEXT"),
            ("artifacts", "checksum_algorithm", "TEXT DEFAULT 'SHA-256'"),
        ]

        for table, column, col_type in columns_to_add:
            try:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
                logger.debug("Added column %s to %s", column, table)
            except sqlite3.OperationalError as e:
                if "duplicate column" not in str(e).lower():
                    raise

    def _migration_5_down(self, conn: sqlite3.Connection) -> None:
        """Remove artifact signing metadata."""
        logger.warning("Migration 5 rollback not fully implemented (SQLite limitation)")

    # ==================== Data Migration Helpers ====================

    def migrate_data(
        self,
        table: str,
        transform: Callable[[dict[str, Any]], dict[str, Any]],
        batch_size: int = 1000,
    ) -> int:
        """
        Migrate data with transformation function.

        Args:
            table: Table name
            transform: Function to transform each row
            batch_size: Number of rows to process per batch

        Returns:
            Number of rows migrated
        """
        with self._get_connection() as conn:
            # Sanitize table name to prevent SQL injection
            # Note: Table names cannot be parameterized in SQL, so we validate them
            safe_table = sanitize_identifier(table)
            
            # Get all rows
            cursor = conn.execute(f"SELECT * FROM {safe_table}")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            migrated = 0
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]

                for row in batch:
                    row_dict = dict(zip(columns, row, strict=False))
                    transformed = transform(row_dict)

                    # Build UPDATE statement with validated column names
                    # Column names cannot be parameterized, so we sanitize them
                    safe_columns = sanitize_identifier_list(list(transformed.keys()))
                    set_clause = ", ".join(f"{col} = ?" for col in safe_columns)
                    values = list(transformed.values())
                    row_id = row_dict.get("id")

                    if row_id:
                        values.append(row_id)
                        conn.execute(
                            f"UPDATE {safe_table} SET {set_clause} WHERE id = ?",
                            values,
                        )
                        migrated += 1

                conn.commit()
                logger.debug("Migrated batch %s (%s rows)", i // batch_size + 1, migrated)

        logger.info("Data migration complete: %s rows migrated in %s", migrated, table)
        return migrated

    def copy_table(
        self,
        source_table: str,
        dest_table: str,
        column_mapping: dict[str, str] | None = None,
    ) -> int:
        """
        Copy data from one table to another.

        Args:
            source_table: Source table name
            dest_table: Destination table name
            column_mapping: Optional mapping of source -> dest columns

        Returns:
            Number of rows copied
        """
        with self._get_connection() as conn:
            # Sanitize table names to prevent SQL injection
            safe_source = sanitize_identifier(source_table)
            safe_dest = sanitize_identifier(dest_table)
            
            if column_mapping:
                # Sanitize column names
                safe_src_cols = sanitize_identifier_list(list(column_mapping.keys()))
                safe_dest_cols = sanitize_identifier_list(list(column_mapping.values()))
                source_cols = ", ".join(safe_src_cols)
                dest_cols = ", ".join(safe_dest_cols)
            else:
                # Copy all columns with same names
                cursor = conn.execute(f"SELECT * FROM {safe_source} LIMIT 0")
                columns = [desc[0] for desc in cursor.description]
                # Sanitize column names from schema
                safe_columns = sanitize_identifier_list(columns)
                source_cols = dest_cols = ", ".join(safe_columns)

            conn.execute(f"""
                INSERT INTO {safe_dest} ({dest_cols})
                SELECT {source_cols} FROM {safe_source}
            """)

            cursor = conn.execute("SELECT changes()")
            copied = cursor.fetchone()[0]
            conn.commit()

        logger.info("Copied %s rows from %s to %s", copied, source_table, dest_table)
        return copied

    def backup_table(self, table: str) -> str:
        """
        Create backup of table.

        Args:
            table: Table name

        Returns:
            Backup table name
        """
        # Sanitize table name to prevent SQL injection
        safe_table = sanitize_identifier(table)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_table = f"{table}_backup_{timestamp}"
        safe_backup = sanitize_identifier(backup_table)

        with self._get_connection() as conn:
            conn.execute(f"CREATE TABLE {safe_backup} AS SELECT * FROM {safe_table}")
            cursor = conn.execute(f"SELECT COUNT(*) FROM {safe_backup}")
            count = cursor.fetchone()[0]
            conn.commit()

        logger.info("Created backup %s with %s rows", backup_table, count)
        return backup_table

    def restore_table(self, backup_table: str, target_table: str) -> int:
        """
        Restore table from backup.

        Args:
            backup_table: Backup table name
            target_table: Target table name

        Returns:
            Number of rows restored
        """
        # Sanitize table names to prevent SQL injection
        safe_backup = sanitize_identifier(backup_table)
        safe_target = sanitize_identifier(target_table)
        
        with self._get_connection() as conn:
            # Clear target table
            conn.execute(f"DELETE FROM {safe_target}")

            # Copy from backup
            conn.execute(f"INSERT INTO {safe_target} SELECT * FROM {safe_backup}")

            cursor = conn.execute("SELECT changes()")
            restored = cursor.fetchone()[0]
            conn.commit()

        logger.info("Restored %s rows from %s to %s", restored, backup_table, target_table)
        return restored

    def validate_schema(self) -> tuple[bool, list[str]]:
        """
        Validate database schema integrity.

        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []

        with self._get_connection() as conn:
            # Check foreign key constraints
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.execute("PRAGMA foreign_key_check")
            fk_violations = cursor.fetchall()
            if fk_violations:
                issues.append(f"Foreign key violations: {len(fk_violations)}")

            # Check integrity
            cursor = conn.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            if result != "ok":
                issues.append(f"Integrity check failed: {result}")

            # Verify required tables exist
            required_tables = [
                "builds",
                "build_phases",
                "constitutional_violations",
                "policy_decisions",
                "security_events",
                "artifacts",
                "dependencies",
            ]

            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            existing_tables = {row[0] for row in cursor.fetchall()}

            missing = set(required_tables) - existing_tables
            if missing:
                issues.append(f"Missing tables: {', '.join(missing)}")

        is_valid = len(issues) == 0
        if is_valid:
            logger.info("Schema validation passed")
        else:
            logger.warning("Schema validation failed: %s", '; '.join(issues))

        return is_valid, issues
