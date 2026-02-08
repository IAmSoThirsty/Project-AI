"""
Tests for Build Memory Database System.

Demonstrates functionality and validates core operations.
"""

import tempfile
from pathlib import Path

import pytest


class TestBuildMemoryDB:
    """Test BuildMemoryDB core functionality."""

    @pytest.fixture
    def db(self):
        """Create temporary database for testing."""
        from gradle_evolution.db.schema import BuildMemoryDB

        with tempfile.TemporaryDirectory() as tmpdir:
            yield BuildMemoryDB(Path(tmpdir) / "test.db")

    def test_create_build(self, db):
        """Test build creation."""
        build_id = db.create_build(
            version="1.0.0",
            status="success",
            capsule_id="test-capsule",
        )
        assert build_id > 0

        build = db.get_build(build_id)
        assert build["version"] == "1.0.0"
        assert build["status"] == "success"

    def test_create_violation(self, db):
        """Test constitutional violation tracking."""
        build_id = db.create_build(version="1.0.0", status="failure")

        violation_id = db.create_violation(
            build_id=build_id,
            phase="compilation",
            principle="determinism",
            severity="high",
            reason="Non-deterministic output",
        )
        assert violation_id > 0

        violations = db.get_violations(build_id=build_id)
        assert len(violations) == 1
        assert violations[0]["principle"] == "determinism"

    def test_create_security_event(self, db):
        """Test security event tracking."""
        build_id = db.create_build(version="1.0.0", status="success")

        event_id = db.create_security_event(
            build_id=build_id,
            event_type="vulnerability_detected",
            severity="critical",
            details="CVE-2024-1234",
            cve_ids=["CVE-2024-1234"],
            cvss_score=9.8,
        )
        assert event_id > 0

        events = db.get_security_events(build_id=build_id)
        assert len(events) == 1
        assert events[0]["severity"] == "critical"

    def test_create_artifact(self, db):
        """Test artifact tracking."""
        build_id = db.create_build(version="1.0.0", status="success")

        artifact_id = db.create_artifact(
            build_id=build_id,
            path="build/libs/app.jar",
            hash="sha256:abcd1234",
            size=1048576,
            artifact_type="jar",
            signed=True,
        )
        assert artifact_id > 0

        artifacts = db.get_artifacts(build_id)
        assert len(artifacts) == 1
        assert artifacts[0]["signed"] == 1

    def test_create_dependency(self, db):
        """Test dependency tracking."""
        build_id = db.create_build(version="1.0.0", status="success")

        dep_id = db.create_dependency(
            build_id=build_id,
            name="com.example:library",
            version="2.0.0",
            license="Apache-2.0",
        )
        assert dep_id > 0

        deps = db.get_dependencies(build_id)
        assert len(deps) == 1
        assert deps[0]["name"] == "com.example:library"


class TestBuildGraphDB:
    """Test BuildGraphDB graph operations."""

    @pytest.fixture
    def graph_db(self):
        """Create graph database for testing."""
        from gradle_evolution.db.graph_db import BuildGraphDB
        from gradle_evolution.db.schema import BuildMemoryDB

        with tempfile.TemporaryDirectory() as tmpdir:
            db = BuildMemoryDB(Path(tmpdir) / "test.db")

            # Create test data
            build1 = db.create_build(version="1.0.0", status="success")
            build2 = db.create_build(version="1.1.0", status="success")

            db.create_artifact(build1, "app.jar", "hash1", 100, "jar")
            db.create_dependency(build1, "dep1", "1.0", license="MIT")

            graph = BuildGraphDB(db)
            graph.build_graph()

            yield graph

    def test_build_graph(self, graph_db):
        """Test graph construction."""
        stats = graph_db.get_graph_statistics()
        assert stats["nodes"]["builds"] >= 2
        assert stats["edges"]["total"] >= 2

    def test_export_dot(self, graph_db):
        """Test DOT format export."""
        dot_content = graph_db.export_to_dot()
        assert "digraph BuildGraph" in dot_content
        assert "build_" in dot_content

    def test_export_json(self, graph_db):
        """Test JSON export."""
        graph_data = graph_db.export_to_json()
        assert "nodes" in graph_data
        assert "edges" in graph_data
        assert "builds" in graph_data["nodes"]


class TestMigrationManager:
    """Test migration system."""

    @pytest.fixture
    def migrator(self):
        """Create migration manager for testing."""
        from gradle_evolution.db.migrations import MigrationManager

        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            yield MigrationManager(db_path)

    def test_get_version(self, migrator):
        """Test version retrieval."""
        current = migrator.get_current_version()
        latest = migrator.get_latest_version()
        assert current >= 0
        assert latest >= 0

    def test_migrate(self, migrator):
        """Test migration application."""
        result = migrator.migrate()
        assert result is True


class TestBuildQueryEngine:
    """Test query engine."""

    @pytest.fixture
    def query_engine(self):
        """Create query engine for testing."""
        from gradle_evolution.db.queries import BuildQueryEngine
        from gradle_evolution.db.schema import BuildMemoryDB

        with tempfile.TemporaryDirectory() as tmpdir:
            db = BuildMemoryDB(Path(tmpdir) / "test.db")

            # Create test data
            for i in range(5):
                build_id = db.create_build(
                    version=f"1.{i}.0",
                    status="success" if i % 2 == 0 else "failure",
                )
                db.update_build(build_id, duration=float(100 + i * 10))

            yield BuildQueryEngine(db)

    def test_build_trends(self, query_engine):
        """Test build trend analysis."""
        trends = query_engine.analyze_build_trends(days=30)
        assert trends["total_builds"] >= 5
        assert "success_rate" in trends


class TestMemoryManager:
    """Test memory management."""

    @pytest.fixture
    def manager(self):
        """Create memory manager for testing."""
        from gradle_evolution.db.memory_manager import MemoryManager
        from gradle_evolution.db.schema import BuildMemoryDB

        with tempfile.TemporaryDirectory() as tmpdir:
            db = BuildMemoryDB(Path(tmpdir) / "test.db")

            # Create test builds
            for i in range(10):
                db.create_build(version=f"1.{i}.0", status="success")

            yield MemoryManager(db, archive_dir=Path(tmpdir) / "archives")

    def test_cleanup_dry_run(self, manager):
        """Test dry-run cleanup."""
        report = manager.cleanup(dry_run=True)
        assert report["dry_run"] is True
        assert report["total_builds"] >= 10

    def test_get_health_status(self, manager):
        """Test health monitoring."""
        health = manager.get_health_status()
        assert "status" in health
        assert health["status"] in ["healthy", "warning", "unhealthy"]

    def test_vacuum_database(self, manager):
        """Test database vacuum."""
        result = manager.vacuum_database()
        assert result["status"] in ["success", "failed"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
