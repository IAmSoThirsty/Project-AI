"""
Build Memory Manager.

Provides automatic cleanup, retention policies, archival, and optimization
for build memory database.
"""

import gzip
import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class RetentionPolicy:
    """Defines retention policy for build data."""

    def __init__(
        self,
        keep_last_n_builds: int | None = None,
        keep_days: int | None = None,
        keep_successful_days: int | None = None,
        keep_failed_builds: bool = True,
        keep_with_violations: bool = True,
        keep_with_vulnerabilities: bool = True,
    ):
        """
        Initialize retention policy.

        Args:
            keep_last_n_builds: Keep last N builds regardless of age
            keep_days: Keep builds newer than N days
            keep_successful_days: Keep successful builds for N days
            keep_failed_builds: Always keep failed builds
            keep_with_violations: Always keep builds with constitutional violations
            keep_with_vulnerabilities: Always keep builds with security vulnerabilities
        """
        self.keep_last_n_builds = keep_last_n_builds
        self.keep_days = keep_days
        self.keep_successful_days = keep_successful_days
        self.keep_failed_builds = keep_failed_builds
        self.keep_with_violations = keep_with_violations
        self.keep_with_vulnerabilities = keep_with_vulnerabilities


class MemoryManager:
    """
    Build memory database manager.

    Handles automatic cleanup, archival, optimization, and monitoring.
    """

    DEFAULT_POLICY = RetentionPolicy(
        keep_last_n_builds=100,
        keep_days=90,
        keep_successful_days=30,
        keep_failed_builds=True,
        keep_with_violations=True,
        keep_with_vulnerabilities=True,
    )

    def __init__(
        self,
        build_memory_db,
        archive_dir: Path | None = None,
        retention_policy: RetentionPolicy | None = None,
    ):
        """
        Initialize memory manager.

        Args:
            build_memory_db: BuildMemoryDB instance
            archive_dir: Directory for archived builds
            retention_policy: Retention policy (uses default if not provided)
        """
        from gradle_evolution.db.schema import BuildMemoryDB

        if not isinstance(build_memory_db, BuildMemoryDB):
            raise TypeError("build_memory_db must be BuildMemoryDB instance")

        self.db = build_memory_db

        if archive_dir is None:
            archive_dir = Path("data/build_archives")
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        self.policy = retention_policy or self.DEFAULT_POLICY
        logger.info("MemoryManager initialized with archive dir: %s", self.archive_dir)

    def cleanup(self, dry_run: bool = False) -> dict[str, Any]:
        """
        Clean up old build data according to retention policy.

        Args:
            dry_run: If True, simulate cleanup without deleting

        Returns:
            Cleanup report with statistics
        """
        logger.info("Starting cleanup (dry_run=%s)...", dry_run)

        # Get all builds
        all_builds = self.db.get_builds(limit=100000, offset=0)

        if not all_builds:
            logger.info("No builds to clean up")
            return {"status": "no_data", "deleted_count": 0}

        # Sort by timestamp (newest first)
        all_builds.sort(key=lambda b: b["timestamp"], reverse=True)

        # Determine which builds to keep
        builds_to_keep = set()
        builds_to_delete = []

        # Rule 1: Keep last N builds
        if self.policy.keep_last_n_builds:
            for build in all_builds[: self.policy.keep_last_n_builds]:
                builds_to_keep.add(build["id"])

        # Rule 2: Keep builds within age threshold
        if self.policy.keep_days:
            cutoff_time = (
                datetime.utcnow() - timedelta(days=self.policy.keep_days)
            ).isoformat()
            for build in all_builds:
                if build["timestamp"] >= cutoff_time:
                    builds_to_keep.add(build["id"])

        # Rule 3: Keep successful builds for shorter period
        if self.policy.keep_successful_days:
            cutoff_time = (
                datetime.utcnow() - timedelta(days=self.policy.keep_successful_days)
            ).isoformat()
            for build in all_builds:
                if build["status"] == "success" and build["timestamp"] >= cutoff_time:
                    builds_to_keep.add(build["id"])

        # Rule 4: Always keep failed builds
        if self.policy.keep_failed_builds:
            for build in all_builds:
                if build["status"] == "failure":
                    builds_to_keep.add(build["id"])

        # Rule 5: Keep builds with constitutional violations
        if self.policy.keep_with_violations:
            violations = self.db.get_violations()
            for violation in violations:
                builds_to_keep.add(violation["build_id"])

        # Rule 6: Keep builds with security vulnerabilities
        if self.policy.keep_with_vulnerabilities:
            vulnerable_deps = self.db.get_vulnerable_dependencies()
            for dep in vulnerable_deps:
                builds_to_keep.add(dep["build_id"])

        # Determine deletions
        for build in all_builds:
            if build["id"] not in builds_to_keep:
                builds_to_delete.append(build)

        logger.info(
            f"Cleanup plan: {len(builds_to_keep)} to keep, "
            f"{len(builds_to_delete)} to delete"
        )

        deleted_count = 0
        archived_count = 0

        if not dry_run and builds_to_delete:
            # Archive before deleting
            for build in builds_to_delete:
                if self._archive_build(build["id"]):
                    archived_count += 1

            # Delete builds
            for build in builds_to_delete:
                if self.db.delete_build(build["id"]):
                    deleted_count += 1

        return {
            "status": "completed",
            "dry_run": dry_run,
            "total_builds": len(all_builds),
            "kept_builds": len(builds_to_keep),
            "deleted_builds": deleted_count,
            "archived_builds": archived_count,
            "policy": {
                "keep_last_n": self.policy.keep_last_n_builds,
                "keep_days": self.policy.keep_days,
                "keep_successful_days": self.policy.keep_successful_days,
            },
        }

    def _archive_build(self, build_id: int) -> bool:
        """
        Archive build to compressed JSON file.

        Args:
            build_id: Build ID to archive

        Returns:
            bool: True if archived successfully
        """
        try:
            # Get all build data
            build = self.db.get_build(build_id)
            if not build:
                logger.warning("Build %s not found for archival", build_id)
                return False

            archive_data = {
                "build": build,
                "phases": self.db.get_build_phases(build_id),
                "violations": self.db.get_violations(build_id=build_id),
                "policy_decisions": self.db.get_policy_decisions(build_id),
                "security_events": self.db.get_security_events(build_id=build_id),
                "artifacts": self.db.get_artifacts(build_id),
                "dependencies": self.db.get_dependencies(build_id),
            }

            # Create archive file
            timestamp = datetime.utcnow().strftime("%Y%m%d")
            archive_file = self.archive_dir / f"build_{build_id}_{timestamp}.json.gz"

            with gzip.open(archive_file, "wt", encoding="utf-8") as f:
                json.dump(archive_data, f, indent=2, default=str)

            logger.debug("Archived build %s to %s", build_id, archive_file)
            return True

        except Exception as e:
            logger.error("Failed to archive build %s: %s", build_id, e)
            return False

    def restore_from_archive(self, archive_file: Path) -> int | None:
        """
        Restore build from archive file.

        Args:
            archive_file: Path to archive file

        Returns:
            Build ID if restored successfully, None otherwise
        """
        try:
            with gzip.open(archive_file, "rt", encoding="utf-8") as f:
                archive_data = json.load(f)

            build_data = archive_data["build"]

            # Create build
            build_id = self.db.create_build(
                version=build_data["version"],
                status=build_data["status"],
                capsule_id=build_data.get("capsule_id"),
                constitutional_status=build_data.get("constitutional_status"),
                gradle_version=build_data.get("gradle_version"),
                java_version=build_data.get("java_version"),
                os_info=build_data.get("os_info"),
                host_name=build_data.get("host_name"),
                user_name=build_data.get("user_name"),
            )

            # Update with additional fields
            self.db.update_build(
                build_id,
                duration=build_data.get("duration"),
                exit_code=build_data.get("exit_code"),
                error_message=build_data.get("error_message"),
            )

            # Restore phases
            for phase in archive_data.get("phases", []):
                self.db.create_build_phase(
                    build_id,
                    phase["phase"],
                    status=phase["status"],
                    logs_path=phase.get("logs_path"),
                )

            # Restore violations
            for violation in archive_data.get("violations", []):
                self.db.create_violation(
                    build_id,
                    violation["phase"],
                    violation["principle"],
                    violation["severity"],
                    violation["reason"],
                )

            # Restore policy decisions
            for decision in archive_data.get("policy_decisions", []):
                self.db.create_policy_decision(
                    build_id,
                    decision["policy_id"],
                    decision["decision"],
                    decision["reason"],
                    policy_name=decision.get("policy_name"),
                )

            # Restore security events
            for event in archive_data.get("security_events", []):
                self.db.create_security_event(
                    build_id,
                    event["event_type"],
                    event["severity"],
                    event["details"],
                )

            # Restore artifacts
            for artifact in archive_data.get("artifacts", []):
                self.db.create_artifact(
                    build_id,
                    artifact["path"],
                    artifact["hash"],
                    artifact["size"],
                    artifact["type"],
                    signed=bool(artifact.get("signed", False)),
                )

            # Restore dependencies
            for dep in archive_data.get("dependencies", []):
                self.db.create_dependency(
                    build_id,
                    dep["name"],
                    dep["version"],
                    hash=dep.get("hash"),
                    source=dep.get("source"),
                    license=dep.get("license"),
                    scope=dep.get("scope"),
                )

            logger.info("Restored build %s from %s", build_id, archive_file)
            return build_id

        except Exception as e:
            logger.error("Failed to restore from archive %s: %s", archive_file, e)
            return None

    def vacuum_database(self) -> dict[str, Any]:
        """
        Vacuum database to reclaim space and optimize.

        Returns:
            Optimization report
        """
        logger.info("Vacuuming database...")

        # Get size before
        size_before = self.db.get_database_size()

        # Vacuum
        success = self.db.vacuum()

        # Get size after
        size_after = self.db.get_database_size()
        reclaimed = size_before - size_after

        result = {
            "status": "success" if success else "failed",
            "size_before_bytes": size_before,
            "size_after_bytes": size_after,
            "reclaimed_bytes": reclaimed,
            "reclaimed_mb": round(reclaimed / 1024 / 1024, 2),
        }

        logger.info(
            f"Vacuum completed: reclaimed {result['reclaimed_mb']} MB "
            f"({result['size_after_bytes']} bytes remaining)"
        )
        return result

    def optimize_database(self) -> dict[str, Any]:
        """
        Perform comprehensive database optimization.

        Returns:
            Optimization report
        """
        logger.info("Optimizing database...")

        results = {}

        # Vacuum
        results["vacuum"] = self.vacuum_database()

        # Analyze tables
        with self.db.get_connection() as conn:
            try:
                conn.execute("ANALYZE")
                conn.commit()
                results["analyze"] = {"status": "success"}
                logger.info("Database analysis completed")
            except Exception as e:
                results["analyze"] = {"status": "failed", "error": str(e)}
                logger.error("Database analysis failed: %s", e)

        # Rebuild indexes
        results["reindex"] = self._rebuild_indexes()

        return {
            "status": "completed",
            "operations": results,
        }

    def _rebuild_indexes(self) -> dict[str, Any]:
        """Rebuild all database indexes."""
        with self.db.get_connection() as conn:
            try:
                cursor = conn.execute(
                    """
                    SELECT name FROM sqlite_master
                    WHERE type = 'index' AND sql IS NOT NULL
                """
                )
                indexes = [row[0] for row in cursor.fetchall()]

                for index in indexes:
                    conn.execute(f"REINDEX {index}")

                conn.commit()
                logger.info("Rebuilt %s indexes", len(indexes))
                return {"status": "success", "indexes_rebuilt": len(indexes)}
            except Exception as e:
                logger.error("Failed to rebuild indexes: %s", e)
                return {"status": "failed", "error": str(e)}

    def get_memory_usage(self) -> dict[str, Any]:
        """
        Get database memory usage statistics.

        Returns:
            Memory usage report
        """
        stats = self.db.get_statistics()
        db_size = self.db.get_database_size()

        # Calculate approximate size per table
        with self.db.get_connection() as conn:
            table_sizes = {}
            for table, _count in stats.items():
                try:
                    cursor = conn.execute(
                        "SELECT SUM(pgsize) FROM dbstat WHERE name = ?", (table,)
                    )
                    row = cursor.fetchone()
                    table_sizes[table] = row[0] if row and row[0] else 0
                except Exception:
                    table_sizes[table] = 0

        return {
            "total_size_bytes": db_size,
            "total_size_mb": round(db_size / 1024 / 1024, 2),
            "record_counts": stats,
            "table_sizes": table_sizes,
            "archive_count": len(list(self.archive_dir.glob("*.json.gz"))),
        }

    def get_health_status(self) -> dict[str, Any]:
        """
        Get database health status.

        Returns:
            Health status report
        """
        logger.info("Checking database health...")

        health = {
            "status": "healthy",
            "issues": [],
            "warnings": [],
        }

        # Check database size
        size_mb = self.db.get_database_size() / 1024 / 1024
        if size_mb > 1000:  # 1 GB
            health["warnings"].append(f"Large database size: {size_mb:.2f} MB")

        # Check record counts
        stats = self.db.get_statistics()

        if stats.get("builds", 0) > 10000:
            health["warnings"].append(f"Large number of builds: {stats['builds']}")

        if stats.get("dependencies", 0) > 100000:
            health["warnings"].append(
                f"Large number of dependencies: {stats['dependencies']}"
            )

        # Check for unresolved violations
        unresolved_violations = len(self.db.get_violations(waived=False))
        if unresolved_violations > 0:
            health["warnings"].append(
                f"Unresolved constitutional violations: {unresolved_violations}"
            )

        # Check for unremediated security events
        unremediated_events = len(self.db.get_security_events(remediated=False))
        if unremediated_events > 0:
            health["warnings"].append(
                f"Unremediated security events: {unremediated_events}"
            )

        # Check integrity
        with self.db.get_connection() as conn:
            try:
                cursor = conn.execute("PRAGMA integrity_check")
                result = cursor.fetchone()[0]
                if result != "ok":
                    health["status"] = "unhealthy"
                    health["issues"].append(f"Integrity check failed: {result}")
            except Exception as e:
                health["status"] = "unhealthy"
                health["issues"].append(f"Integrity check error: {e}")

        if health["issues"]:
            health["status"] = "unhealthy"
        elif health["warnings"]:
            health["status"] = "warning"

        logger.info("Health check completed: %s", health["status"])
        return health

    def create_backup(self, backup_path: Path | None = None) -> Path:
        """
        Create full database backup.

        Args:
            backup_path: Path for backup file

        Returns:
            Path to backup file
        """
        if backup_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = self.archive_dir / f"backup_{timestamp}.db"
        else:
            backup_path = Path(backup_path)

        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Use SQLite backup API
        with self.db.get_connection() as source_conn:
            backup_conn = self.db._get_connection()
            try:
                source_conn.backup(backup_conn)
                backup_conn.close()

                # Compress backup
                compressed_path = backup_path.with_suffix(".db.gz")
                with (
                    open(backup_path, "rb") as f_in,
                    gzip.open(compressed_path, "wb") as f_out,
                ):
                    shutil.copyfileobj(f_in, f_out)

                # Remove uncompressed backup
                backup_path.unlink()

                logger.info("Created database backup: %s", compressed_path)
                return compressed_path
            except Exception as e:
                if backup_conn:
                    backup_conn.close()
                logger.error("Backup failed: %s", e)
                raise

    def list_archives(self) -> list[dict[str, Any]]:
        """
        List all archived builds.

        Returns:
            List of archive metadata
        """
        archives = []
        for archive_file in sorted(self.archive_dir.glob("*.json.gz")):
            stat = archive_file.stat()
            archives.append(
                {
                    "filename": archive_file.name,
                    "path": str(archive_file),
                    "size_bytes": stat.st_size,
                    "size_mb": round(stat.st_size / 1024 / 1024, 2),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                }
            )
        return archives
