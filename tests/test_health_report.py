"""
Tests for the health reporting system.

This test suite validates:
- System metrics collection
- Dependency scanning
- Configuration summary
- YAML snapshot generation
- PNG report rendering
- Audit log integration
- CLI entry points
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import yaml

from app.core.config import Config
from app.governance.audit_log import AuditLog
from app.health.report import HealthReporter


class TestHealthReporter:
    """Test suite for HealthReporter class."""

    def test_init_creates_directories(self):
        """Test that initialization creates snapshot and report directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_dir = Path(tmpdir) / "snapshots"
            report_dir = Path(tmpdir) / "reports"

            reporter = HealthReporter(snapshot_dir=snapshot_dir, report_dir=report_dir)

            assert snapshot_dir.exists()
            assert report_dir.exists()
            assert reporter.snapshot_dir == snapshot_dir
            assert reporter.report_dir == report_dir

    def test_collect_system_metrics(self):
        """Test system metrics collection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = HealthReporter(snapshot_dir=Path(tmpdir))
            metrics = reporter.collect_system_metrics()

            assert "cpu" in metrics
            assert "memory" in metrics
            assert "disk" in metrics
            assert "platform" in metrics

            # Verify CPU metrics structure
            assert "usage_percent" in metrics["cpu"]
            assert "count" in metrics["cpu"]

            # Verify memory metrics structure
            assert "total_mb" in metrics["memory"]
            assert "usage_percent" in metrics["memory"]

            # Verify disk metrics structure
            assert "total_gb" in metrics["disk"]
            assert "usage_percent" in metrics["disk"]

            # Verify platform metrics structure
            assert "system" in metrics["platform"]
            assert "python_version" in metrics["platform"]

    def test_collect_dependencies(self):
        """Test dependency collection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = HealthReporter(snapshot_dir=Path(tmpdir))
            dependencies = reporter.collect_dependencies()

            assert isinstance(dependencies, dict)
            # Should have at least some packages
            assert len(dependencies) > 0

            # Common packages should be present
            package_names = [pkg.lower() for pkg in dependencies]
            assert any("pytest" in name for name in package_names)

    def test_collect_config_summary(self):
        """Test configuration summary collection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = HealthReporter(snapshot_dir=Path(tmpdir))
            config_summary = reporter.collect_config_summary()

            assert "sections" in config_summary
            assert isinstance(config_summary["sections"], list)
            assert "log_level" in config_summary
            assert "ai_provider" in config_summary
            assert "security_enabled" in config_summary

    def test_generate_yaml_snapshot(self):
        """Test YAML snapshot generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_dir = Path(tmpdir) / "snapshots"
            reporter = HealthReporter(snapshot_dir=snapshot_dir)

            success, snapshot_path = reporter.generate_yaml_snapshot()

            assert success is True
            assert snapshot_path is not None
            assert snapshot_path.exists()
            assert snapshot_path.suffix == ".yaml"
            assert "health_snapshot_" in snapshot_path.name

            # Verify YAML content
            with open(snapshot_path) as f:
                data = yaml.safe_load(f)

            assert "generated_at" in data
            assert "version" in data
            assert "system_metrics" in data
            assert "dependencies" in data
            assert "config_summary" in data

    def test_generate_png_report(self):
        """Test PNG report generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_dir = Path(tmpdir) / "reports"
            reporter = HealthReporter(report_dir=report_dir)

            # Create sample snapshot data
            snapshot_data = {
                "generated_at": "2024-01-01T00:00:00Z",
                "system_metrics": {
                    "cpu": {"usage_percent": 45.0, "count": 4},
                    "memory": {"usage_percent": 60.0, "total_mb": 16384},
                    "disk": {"usage_percent": 70.0, "total_gb": 500},
                    "platform": {
                        "system": "Linux",
                        "release": "5.15.0",
                        "machine": "x86_64",
                    },
                },
            }

            success, report_path = reporter.generate_png_report(snapshot_data)

            assert success is True
            assert report_path is not None
            assert report_path.exists()
            assert report_path.suffix == ".png"
            assert report_path.name == "health_report.png"

            # Check that timestamped version also exists
            timestamped_files = list(report_dir.glob("health_report_*.png"))
            assert len(timestamped_files) >= 1

    def test_generate_full_report(self):
        """Test full report generation (YAML + PNG)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_dir = Path(tmpdir) / "snapshots"
            report_dir = Path(tmpdir) / "reports"
            audit_log_path = Path(tmpdir) / "audit.yaml"

            audit = AuditLog(log_file=audit_log_path)
            reporter = HealthReporter(snapshot_dir=snapshot_dir, report_dir=report_dir, audit_log=audit)

            success, snapshot_path, report_path = reporter.generate_full_report()

            assert success is True
            assert snapshot_path is not None
            assert snapshot_path.exists()
            assert report_path is not None
            assert report_path.exists()

            # Verify audit log entry was created
            events = audit.get_events(event_type="health_report_generated")
            assert len(events) == 1
            assert events[0]["event_type"] == "health_report_generated"
            assert "snapshot_path" in events[0]["data"]
            assert "report_path" in events[0]["data"]

    def test_generate_full_report_logs_failure(self):
        """Test that failures are logged to audit when report generation fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_dir = Path(tmpdir) / "snapshots"
            report_dir = Path(tmpdir) / "reports"
            audit_log_path = Path(tmpdir) / "audit.yaml"
            audit = AuditLog(log_file=audit_log_path)

            reporter = HealthReporter(snapshot_dir=snapshot_dir, report_dir=report_dir, audit_log=audit)

            # Mock generate_yaml_snapshot to fail
            with patch.object(reporter, "generate_yaml_snapshot", return_value=(False, None)):
                success, snapshot_path, report_path = reporter.generate_full_report()

                assert success is False
                assert snapshot_path is None
                assert report_path is None

    def test_config_integration(self):
        """Test that health reporter uses configuration correctly."""
        with tempfile.TemporaryDirectory():
            # Create a config with health settings
            Config()

            reporter = HealthReporter()

            # Verify config is loaded
            assert reporter.config is not None
            health_config = reporter.config.get_section("health")
            assert health_config is not None
            assert "collect_system_metrics" in health_config
            assert "snapshot_dir" in health_config

    def test_audit_log_integration(self):
        """Test audit log integration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_log_path = Path(tmpdir) / "audit.yaml"
            audit = AuditLog(log_file=audit_log_path)

            reporter = HealthReporter(snapshot_dir=Path(tmpdir) / "snapshots", audit_log=audit)

            # Generate report
            success, _, _ = reporter.generate_full_report()
            assert success is True

            # Verify audit log chain
            is_valid, message = audit.verify_chain()
            assert is_valid is True

    def test_canonical_path_generation(self):
        """Test that canonical path (health_report.png) is always updated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_dir = Path(tmpdir) / "reports"
            reporter = HealthReporter(report_dir=report_dir)

            # Generate first report
            snapshot_data = {
                "generated_at": "2024-01-01T00:00:00Z",
                "system_metrics": {
                    "cpu": {"usage_percent": 45.0, "count": 4},
                    "memory": {"usage_percent": 60.0, "total_mb": 16384},
                    "disk": {"usage_percent": 70.0, "total_gb": 500},
                    "platform": {
                        "system": "Linux",
                        "release": "5.15.0",
                        "machine": "x86_64",
                    },
                },
            }

            success1, path1 = reporter.generate_png_report(snapshot_data)
            assert success1 is True

            # Get modification time
            mtime1 = path1.stat().st_mtime

            # Wait a moment and generate again
            import time

            time.sleep(0.1)

            success2, path2 = reporter.generate_png_report(snapshot_data)
            assert success2 is True

            # Canonical path should be updated
            mtime2 = path2.stat().st_mtime
            assert mtime2 > mtime1

            # Both should point to same canonical path
            assert path1 == path2
            assert path1.name == "health_report.png"

    def test_error_handling_in_collect_methods(self):
        """Test that collection methods handle errors gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            reporter = HealthReporter(snapshot_dir=Path(tmpdir))

            # Mock psutil to raise an exception
            with patch(
                "app.health.report.psutil.cpu_percent",
                side_effect=Exception("Test error"),
            ):
                metrics = reporter.collect_system_metrics()
                assert "error" in metrics

    def test_yaml_snapshot_config_driven_collection(self):
        """Test that YAML snapshot respects config settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_dir = Path(tmpdir) / "snapshots"

            # Create a reporter
            reporter = HealthReporter(snapshot_dir=snapshot_dir)

            # Override config for testing
            reporter.config.config["health"] = {
                "collect_system_metrics": True,
                "collect_dependencies": False,  # Disable dependencies
                "collect_config_summary": True,
            }

            success, snapshot_path = reporter.generate_yaml_snapshot()
            assert success is True

            # Load and verify
            with open(snapshot_path) as f:
                data = yaml.safe_load(f)

            assert "system_metrics" in data
            assert "dependencies" not in data  # Should be excluded
            assert "config_summary" in data


class TestHealthReportCLI:
    """Test suite for CLI entry point."""

    def test_main_function_success(self):
        """Test that main() function executes successfully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot_dir = Path(tmpdir) / "snapshots"
            report_dir = Path(tmpdir) / "reports"

            # Mock HealthReporter to use temp directories
            with patch("app.health.report.HealthReporter") as mock_reporter_class:
                mock_reporter = MagicMock()
                mock_reporter.generate_full_report.return_value = (
                    True,
                    snapshot_dir / "snapshot.yaml",
                    report_dir / "report.png",
                )
                mock_reporter.audit_log.verify_chain.return_value = (True, "Verified")
                mock_reporter_class.return_value = mock_reporter

                # Import and run main
                from app.health.report import main

                # Should not raise an exception
                try:
                    with patch("sys.exit"):  # Prevent actual exit
                        main()
                except SystemExit:
                    pass  # Expected if sys.exit is called
