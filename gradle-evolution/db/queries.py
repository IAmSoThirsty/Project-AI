"""
Build Query Engine.

Provides complex analytical queries for build analysis, failure correlation,
dependency tracking, and trend analysis.
"""

import csv
import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .sql_utils import sanitize_identifier

logger = logging.getLogger(__name__)


class BuildQueryEngine:
    """
    Advanced query engine for build analytics.

    Provides complex analytical queries with caching, optimization, and
    export capabilities.
    """

    def __init__(self, build_memory_db):
        """
        Initialize query engine.

        Args:
            build_memory_db: BuildMemoryDB instance
        """
        from gradle_evolution.db.schema import BuildMemoryDB

        if not isinstance(build_memory_db, BuildMemoryDB):
            raise TypeError("build_memory_db must be BuildMemoryDB instance")

        self.db = build_memory_db
        self._query_cache: dict[str, tuple[Any, datetime]] = {}
        self._cache_ttl = timedelta(minutes=5)
        logger.info("BuildQueryEngine initialized")

    def _get_cached_result(self, cache_key: str) -> Any | None:
        """Get cached query result if not expired."""
        if cache_key in self._query_cache:
            result, timestamp = self._query_cache[cache_key]
            if datetime.utcnow() - timestamp < self._cache_ttl:
                logger.debug("Cache hit for %s", cache_key)
                return result
            else:
                del self._query_cache[cache_key]
        return None

    def _cache_result(self, cache_key: str, result: Any) -> None:
        """Cache query result with timestamp."""
        self._query_cache[cache_key] = (result, datetime.utcnow())

    def clear_cache(self) -> None:
        """Clear all cached query results."""
        self._query_cache.clear()
        logger.info("Query cache cleared")

    # ==================== Failure Analysis ====================

    def analyze_failure_correlation(
        self,
        time_window_hours: int = 24,
        min_failures: int = 2,
    ) -> list[dict[str, Any]]:
        """
        Analyze correlated build failures.

        Args:
            time_window_hours: Time window for correlation analysis
            min_failures: Minimum number of failures to consider

        Returns:
            List of failure correlation reports
        """
        cache_key = f"failure_correlation_{time_window_hours}_{min_failures}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached

        with self.db.get_connection() as conn:
            # Get failed builds within time window
            cutoff_time = (
                datetime.utcnow() - timedelta(hours=time_window_hours)
            ).isoformat()

            cursor = conn.execute(
                """
                SELECT b.id, b.version, b.timestamp, b.error_message,
                       GROUP_CONCAT(DISTINCT v.principle) as violated_principles,
                       COUNT(DISTINCT d.id) as dependency_count,
                       SUM(d.vulnerability_count) as total_vulnerabilities
                FROM builds b
                LEFT JOIN constitutional_violations v ON b.id = v.build_id
                LEFT JOIN dependencies d ON b.id = d.build_id
                WHERE b.status = 'failure' AND b.timestamp >= ?
                GROUP BY b.id
                ORDER BY b.timestamp DESC
                """,
                (cutoff_time,),
            )

            failures = [dict(row) for row in cursor.fetchall()]

        if len(failures) < min_failures:
            logger.info(
                "Found %s failures, below minimum %s", len(failures), min_failures
            )
            return []

        # Group failures by common characteristics
        correlations = self._compute_failure_correlations(failures)

        self._cache_result(cache_key, correlations)
        logger.info(
            "Analyzed %s failures, found %s correlations",
            len(failures),
            len(correlations),
        )
        return correlations

    def _compute_failure_correlations(
        self,
        failures: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Compute correlations between failures."""
        correlations = []

        # Group by violated principles
        principle_groups = defaultdict(list)
        for failure in failures:
            principles = failure.get("violated_principles")
            if principles:
                for principle in principles.split(","):
                    principle_groups[principle.strip()].append(failure)

        for principle, group in principle_groups.items():
            if len(group) >= 2:
                correlations.append(
                    {
                        "type": "principle_violation",
                        "principle": principle,
                        "failure_count": len(group),
                        "builds": [f["id"] for f in group],
                        "versions": [f["version"] for f in group],
                    }
                )

        # Group by vulnerability presence
        vulnerable_failures = [
            f for f in failures if f.get("total_vulnerabilities", 0) > 0
        ]
        if len(vulnerable_failures) >= 2:
            correlations.append(
                {
                    "type": "vulnerability_related",
                    "failure_count": len(vulnerable_failures),
                    "builds": [f["id"] for f in vulnerable_failures],
                    "total_vulnerabilities": sum(
                        f.get("total_vulnerabilities", 0) for f in vulnerable_failures
                    ),
                }
            )

        # Group by time proximity (within 1 hour)
        time_clusters = self._cluster_by_time(failures, hours=1)
        for cluster in time_clusters:
            if len(cluster) >= 2:
                correlations.append(
                    {
                        "type": "temporal_cluster",
                        "failure_count": len(cluster),
                        "builds": [f["id"] for f in cluster],
                        "time_range": {
                            "start": min(f["timestamp"] for f in cluster),
                            "end": max(f["timestamp"] for f in cluster),
                        },
                    }
                )

        return correlations

    def _cluster_by_time(
        self,
        items: list[dict[str, Any]],
        hours: float,
    ) -> list[list[dict[str, Any]]]:
        """Cluster items by time proximity."""
        if not items:
            return []

        # Sort by timestamp
        sorted_items = sorted(items, key=lambda x: x["timestamp"])

        clusters = []
        current_cluster = [sorted_items[0]]
        cluster_start = datetime.fromisoformat(sorted_items[0]["timestamp"])

        for item in sorted_items[1:]:
            item_time = datetime.fromisoformat(item["timestamp"])
            if (item_time - cluster_start).total_seconds() <= hours * 3600:
                current_cluster.append(item)
            else:
                if len(current_cluster) >= 2:
                    clusters.append(current_cluster)
                current_cluster = [item]
                cluster_start = item_time

        if len(current_cluster) >= 2:
            clusters.append(current_cluster)

        return clusters

    def get_failure_hotspots(
        self,
        min_failures: int = 3,
        days: int = 30,
    ) -> list[dict[str, Any]]:
        """
        Identify build phases or components with frequent failures.

        Args:
            min_failures: Minimum failures to be considered a hotspot
            days: Time period to analyze

        Returns:
            List of failure hotspots
        """
        cutoff_time = (datetime.utcnow() - timedelta(days=days)).isoformat()

        with self.db.get_connection() as conn:
            # Phase-based hotspots
            cursor = conn.execute(
                """
                SELECT phase, COUNT(*) as failure_count,
                       AVG(duration) as avg_duration
                FROM build_phases
                WHERE status = 'failure' AND start_time >= ?
                GROUP BY phase
                HAVING COUNT(*) >= ?
                ORDER BY failure_count DESC
                """,
                (cutoff_time, min_failures),
            )
            phase_hotspots = [dict(row) for row in cursor.fetchall()]

            # Principle-based hotspots
            cursor = conn.execute(
                """
                SELECT principle, COUNT(*) as violation_count,
                       severity, COUNT(*) as count
                FROM constitutional_violations
                WHERE detected_at >= ?
                GROUP BY principle, severity
                HAVING COUNT(*) >= ?
                ORDER BY violation_count DESC
                """,
                (cutoff_time, min_failures),
            )
            principle_hotspots = [dict(row) for row in cursor.fetchall()]

        return {
            "phase_hotspots": phase_hotspots,
            "principle_hotspots": principle_hotspots,
            "time_period_days": days,
        }

    # ==================== Dependency Analysis ====================

    def track_dependency_vulnerabilities(
        self,
        group_by: str = "name",
    ) -> list[dict[str, Any]]:
        """
        Track dependency vulnerabilities across builds.

        Args:
            group_by: Grouping strategy ('name', 'version', 'build')

        Returns:
            Vulnerability tracking report
        """
        cache_key = f"dep_vulnerabilities_{group_by}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached

        with self.db.get_connection() as conn:
            if group_by == "name":
                query = """
                    SELECT name, COUNT(DISTINCT version) as version_count,
                           SUM(vulnerability_count) as total_vulnerabilities,
                           MAX(vulnerability_count) as max_vulnerabilities,
                           GROUP_CONCAT(DISTINCT version) as affected_versions
                    FROM dependencies
                    WHERE vulnerability_count > 0
                    GROUP BY name
                    ORDER BY total_vulnerabilities DESC
                """
            elif group_by == "version":
                query = """
                    SELECT name, version, SUM(vulnerability_count) as total_vulnerabilities,
                           COUNT(DISTINCT build_id) as affected_builds
                    FROM dependencies
                    WHERE vulnerability_count > 0
                    GROUP BY name, version
                    ORDER BY total_vulnerabilities DESC
                """
            else:  # build
                query = """
                    SELECT b.id as build_id, b.version as build_version,
                           b.timestamp, COUNT(d.id) as vulnerable_dep_count,
                           SUM(d.vulnerability_count) as total_vulnerabilities
                    FROM builds b
                    JOIN dependencies d ON b.id = d.build_id
                    WHERE d.vulnerability_count > 0
                    GROUP BY b.id
                    ORDER BY total_vulnerabilities DESC
                """

            cursor = conn.execute(query)
            results = [dict(row) for row in cursor.fetchall()]

        self._cache_result(cache_key, results)
        logger.info(
            "Tracked %s vulnerable dependencies (grouped by %s)", len(results), group_by
        )
        return results

    def analyze_dependency_trends(
        self,
        dependency_name: str,
        days: int = 90,
    ) -> dict[str, Any]:
        """
        Analyze trends for a specific dependency.

        Args:
            dependency_name: Dependency name
            days: Time period to analyze

        Returns:
            Trend analysis report
        """
        cutoff_time = (datetime.utcnow() - timedelta(days=days)).isoformat()

        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT d.version, b.timestamp, d.vulnerability_count,
                       d.license, d.scope
                FROM dependencies d
                JOIN builds b ON d.build_id = b.id
                WHERE d.name = ? AND b.timestamp >= ?
                ORDER BY b.timestamp ASC
                """,
                (dependency_name, cutoff_time),
            )
            usage_history = [dict(row) for row in cursor.fetchall()]

        if not usage_history:
            return {
                "dependency": dependency_name,
                "status": "not_found",
                "message": f"No usage found in last {days} days",
            }

        # Analyze trends
        versions_used = {r["version"] for r in usage_history}
        vulnerability_trend = [
            {
                "timestamp": r["timestamp"],
                "version": r["version"],
                "vulnerabilities": r["vulnerability_count"],
            }
            for r in usage_history
        ]

        return {
            "dependency": dependency_name,
            "time_period_days": days,
            "total_builds": len(usage_history),
            "versions_used": sorted(versions_used),
            "version_count": len(versions_used),
            "vulnerability_trend": vulnerability_trend,
            "current_version": usage_history[-1]["version"],
            "current_vulnerabilities": usage_history[-1]["vulnerability_count"],
            "licenses": list({r["license"] for r in usage_history if r["license"]}),
        }

    # ==================== Build Trends ====================

    def analyze_build_trends(
        self,
        days: int = 30,
        granularity: str = "daily",
    ) -> dict[str, Any]:
        """
        Analyze build trends over time.

        Args:
            days: Time period to analyze
            granularity: Time granularity ('hourly', 'daily', 'weekly')

        Returns:
            Build trend analysis
        """
        cache_key = f"build_trends_{days}_{granularity}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached

        cutoff_time = (datetime.utcnow() - timedelta(days=days)).isoformat()

        with self.db.get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT timestamp, status, duration, constitutional_status,
                       exit_code
                FROM builds
                WHERE timestamp >= ?
                ORDER BY timestamp ASC
                """,
                (cutoff_time,),
            )
            builds = [dict(row) for row in cursor.fetchall()]

        if not builds:
            return {"status": "no_data", "time_period_days": days}

        # Group by time period
        time_series = self._group_by_time_period(builds, granularity)

        # Calculate statistics
        total_builds = len(builds)
        successful_builds = sum(1 for b in builds if b["status"] == "success")
        failed_builds = sum(1 for b in builds if b["status"] == "failure")
        success_rate = successful_builds / total_builds if total_builds > 0 else 0

        # Duration statistics
        durations = [b["duration"] for b in builds if b["duration"]]
        avg_duration = sum(durations) / len(durations) if durations else 0

        # Constitutional compliance
        compliant = sum(
            1 for b in builds if b.get("constitutional_status") == "compliant"
        )
        compliance_rate = compliant / total_builds if total_builds > 0 else 0

        result = {
            "time_period_days": days,
            "granularity": granularity,
            "total_builds": total_builds,
            "success_rate": round(success_rate * 100, 2),
            "failed_builds": failed_builds,
            "avg_duration_seconds": round(avg_duration, 2),
            "compliance_rate": round(compliance_rate * 100, 2),
            "time_series": time_series,
        }

        self._cache_result(cache_key, result)
        logger.info("Analyzed %s builds over %s days", total_builds, days)
        return result

    def _group_by_time_period(
        self,
        builds: list[dict[str, Any]],
        granularity: str,
    ) -> list[dict[str, Any]]:
        """Group builds by time period."""
        groups = defaultdict(
            lambda: {
                "success": 0,
                "failure": 0,
                "cancelled": 0,
                "total": 0,
                "durations": [],
            }
        )

        for build in builds:
            try:
                timestamp = datetime.fromisoformat(build["timestamp"])

                if granularity == "hourly":
                    key = timestamp.strftime("%Y-%m-%d %H:00")
                elif granularity == "daily":
                    key = timestamp.strftime("%Y-%m-%d")
                else:  # weekly
                    week = timestamp.isocalendar()[1]
                    key = f"{timestamp.year}-W{week:02d}"

                groups[key]["total"] += 1
                status = build.get("status", "unknown")
                if status in groups[key]:
                    groups[key][status] += 1

                if build.get("duration"):
                    groups[key]["durations"].append(build["duration"])

            except (ValueError, KeyError):
                continue

        # Convert to list with averages
        result = []
        for period, data in sorted(groups.items()):
            avg_duration = (
                sum(data["durations"]) / len(data["durations"])
                if data["durations"]
                else 0
            )
            result.append(
                {
                    "period": period,
                    "total": data["total"],
                    "success": data["success"],
                    "failure": data["failure"],
                    "cancelled": data["cancelled"],
                    "success_rate": (
                        round(data["success"] / data["total"] * 100, 2)
                        if data["total"] > 0
                        else 0
                    ),
                    "avg_duration": round(avg_duration, 2),
                }
            )

        return result

    # ==================== Resource Usage ====================

    def analyze_resource_patterns(
        self,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Analyze resource usage patterns.

        Args:
            days: Time period to analyze

        Returns:
            Resource usage analysis
        """
        cutoff_time = (datetime.utcnow() - timedelta(days=days)).isoformat()

        with self.db.get_connection() as conn:
            # Build duration patterns
            cursor = conn.execute(
                """
                SELECT version, AVG(duration) as avg_duration,
                       MIN(duration) as min_duration,
                       MAX(duration) as max_duration,
                       COUNT(*) as build_count
                FROM builds
                WHERE timestamp >= ? AND duration IS NOT NULL
                GROUP BY version
                ORDER BY avg_duration DESC
                """,
                (cutoff_time,),
            )
            version_durations = [dict(row) for row in cursor.fetchall()]

            # Phase-level resource usage
            cursor = conn.execute(
                """
                SELECT phase, AVG(duration) as avg_duration,
                       COUNT(*) as execution_count
                FROM build_phases
                WHERE start_time >= ? AND duration IS NOT NULL
                GROUP BY phase
                ORDER BY avg_duration DESC
                """,
                (cutoff_time,),
            )
            phase_durations = [dict(row) for row in cursor.fetchall()]

            # Artifact size patterns
            cursor = conn.execute(
                """
                SELECT b.version, SUM(a.size) as total_size,
                       COUNT(a.id) as artifact_count,
                       AVG(a.size) as avg_artifact_size
                FROM artifacts a
                JOIN builds b ON a.build_id = b.id
                WHERE b.timestamp >= ?
                GROUP BY b.version
                ORDER BY total_size DESC
                """,
                (cutoff_time,),
            )
            artifact_sizes = [dict(row) for row in cursor.fetchall()]

        return {
            "time_period_days": days,
            "version_durations": version_durations,
            "phase_durations": phase_durations,
            "artifact_sizes": artifact_sizes,
        }

    # ==================== Constitutional Compliance ====================

    def analyze_constitutional_compliance(
        self,
        days: int = 30,
    ) -> dict[str, Any]:
        """
        Analyze constitutional compliance rates.

        Args:
            days: Time period to analyze

        Returns:
            Compliance analysis
        """
        cache_key = f"constitutional_compliance_{days}"
        cached = self._get_cached_result(cache_key)
        if cached:
            return cached

        cutoff_time = (datetime.utcnow() - timedelta(days=days)).isoformat()

        with self.db.get_connection() as conn:
            # Overall compliance
            cursor = conn.execute(
                """
                SELECT constitutional_status, COUNT(*) as count
                FROM builds
                WHERE timestamp >= ?
                GROUP BY constitutional_status
                """,
                (cutoff_time,),
            )
            status_counts = {
                row["constitutional_status"]: row["count"] for row in cursor.fetchall()
            }

            # Violations by principle
            cursor = conn.execute(
                """
                SELECT principle, severity, COUNT(*) as count,
                       SUM(CASE WHEN waived = 1 THEN 1 ELSE 0 END) as waived_count
                FROM constitutional_violations
                WHERE detected_at >= ?
                GROUP BY principle, severity
                ORDER BY count DESC
                """,
                (cutoff_time,),
            )
            violations = [dict(row) for row in cursor.fetchall()]

            # Waiver patterns
            cursor = conn.execute(
                """
                SELECT waived_by, COUNT(*) as waiver_count
                FROM constitutional_violations
                WHERE detected_at >= ? AND waived = 1
                GROUP BY waived_by
                ORDER BY waiver_count DESC
                """,
                (cutoff_time,),
            )
            waiver_patterns = [dict(row) for row in cursor.fetchall()]

        total_builds = sum(status_counts.values())
        compliant = status_counts.get("compliant", 0)
        compliance_rate = compliant / total_builds if total_builds > 0 else 0

        result = {
            "time_period_days": days,
            "total_builds": total_builds,
            "compliance_rate": round(compliance_rate * 100, 2),
            "status_breakdown": status_counts,
            "violations_by_principle": violations,
            "waiver_patterns": waiver_patterns,
            "total_violations": len(violations),
        }

        self._cache_result(cache_key, result)
        return result

    # ==================== Export Functions ====================

    def export_to_json(
        self,
        query_result: Any,
        output_path: str | Path,
    ) -> bool:
        """Export query result to JSON file."""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with output_path.open("w") as f:
                json.dump(query_result, f, indent=2, default=str)

            logger.info("Exported query result to %s", output_path)
            return True
        except Exception as e:
            logger.error("Failed to export to JSON: %s", e)
            return False

    def export_to_csv(
        self,
        query_result: list[dict[str, Any]],
        output_path: str | Path,
    ) -> bool:
        """Export query result to CSV file."""
        try:
            if not query_result:
                logger.warning("No data to export")
                return False

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with output_path.open("w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=query_result[0].keys())
                writer.writeheader()
                writer.writerows(query_result)

            logger.info("Exported %s rows to %s", len(query_result), output_path)
            return True
        except Exception as e:
            logger.error("Failed to export to CSV: %s", e)
            return False

    def export_to_sql(
        self,
        query_result: list[dict[str, Any]],
        table_name: str,
        output_path: str | Path,
    ) -> bool:
        """Export query result to SQL INSERT statements."""
        try:
            if not query_result:
                logger.warning("No data to export")
                return False

            # Sanitize table name to prevent SQL injection
            safe_table = sanitize_identifier(table_name)

            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with output_path.open("w") as f:
                for row in query_result:
                    columns = ", ".join(row.keys())
                    values = ", ".join(
                        f"'{v}'" if isinstance(v, str) else str(v) for v in row.values()
                    )
                    f.write(
                        f"INSERT INTO {safe_table} ({columns}) VALUES ({values});\n"
                    )

            logger.info(
                "Exported %s SQL statements to %s", len(query_result), output_path
            )
            return True
        except Exception as e:
            logger.error("Failed to export to SQL: %s", e)
            return False
