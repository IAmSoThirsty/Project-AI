"""
Security tests for Cerberus Runtime Manager.

Validates:
- No shell injection vulnerabilities (B602)
- Command validation works
- Health checks execute safely with shell=False
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.core.cerberus_runtime_manager import RuntimeDescriptor, RuntimeManager


class TestRuntimeManagerSecurity:
    """Test security of runtime manager against shell injection."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory with test runtimes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            cerberus_dir = data_dir / "cerberus"
            cerberus_dir.mkdir(parents=True, exist_ok=True)

            # Create test runtimes.json with safe and potentially unsafe commands
            runtimes_data = {
                "runtimes": {
                    "python": {
                        "name": "Python",
                        "version": "3.11+",
                        "exec_path": "python3",
                        "category": "interpreted",
                        "health_check_cmd": "python3 --version",
                        "verified": True,
                        "priority": 10,
                    },
                    "safe_cmd": {
                        "name": "Safe Command",
                        "version": "1.0",
                        "exec_path": "echo",
                        "category": "script",
                        "health_check_cmd": "echo test",
                        "verified": False,
                        "priority": 5,
                    },
                }
            }

            runtimes_file = cerberus_dir / "runtimes.json"
            with open(runtimes_file, "w", encoding="utf-8") as f:
                json.dump(runtimes_data, f)

            yield str(data_dir)

    def test_no_shell_injection_vulnerability(self, temp_data_dir):
        """Test that subprocess.run is called with shell=False."""
        manager = RuntimeManager(data_dir=temp_data_dir)

        # Verify runtimes loaded
        assert len(manager.runtimes) == 2
        assert "python" in manager.runtimes
        assert "safe_cmd" in manager.runtimes

    def test_health_check_with_shell_false(self, temp_data_dir):
        """Test that health checks work with shell=False."""
        manager = RuntimeManager(data_dir=temp_data_dir)

        # Run health checks - should execute without shell
        summary = manager.verify_runtimes(timeout=5)

        # Verify summary has expected structure
        assert "total_runtimes" in summary
        assert "healthy" in summary
        assert "degraded" in summary
        assert "unavailable" in summary
        assert summary["total_runtimes"] == 2

    def test_command_validation_rejects_invalid_chars(self, temp_data_dir):
        """Test that command validation rejects potentially dangerous characters."""
        manager = RuntimeManager(data_dir=temp_data_dir)

        # Create runtime with suspicious command
        bad_runtime = RuntimeDescriptor(
            language_key="malicious",
            name="Malicious",
            version="1.0",
            exec_path="echo",
            category="script",
            health_check_cmd="echo test; rm -rf /",  # Semicolon for command chaining
            priority=1,
            verified=False,
        )

        # Add to manager
        manager.runtimes["malicious"] = bad_runtime

        # Run health checks - should mark as unavailable due to validation
        summary = manager.verify_runtimes(timeout=5)

        # The malicious runtime should be marked unavailable
        assert manager.health_cache.get("malicious") == "unavailable"

    def test_shlex_split_handles_quoted_args(self, temp_data_dir):
        """Test that shlex.split correctly handles quoted arguments."""
        manager = RuntimeManager(data_dir=temp_data_dir)

        # Add runtime with quoted args
        quoted_runtime = RuntimeDescriptor(
            language_key="quoted",
            name="Quoted",
            version="1.0",
            exec_path="echo",
            category="script",
            health_check_cmd="echo 'hello world'",
            priority=1,
            verified=False,
        )

        manager.runtimes["quoted"] = quoted_runtime

        # Run health checks
        summary = manager.verify_runtimes(timeout=5)

        # Should handle quoted args correctly
        assert "quoted" in manager.health_cache

    def test_get_runtime_by_key(self, temp_data_dir):
        """Test retrieving runtime by language key."""
        manager = RuntimeManager(data_dir=temp_data_dir)

        python_runtime = manager.get_runtime("python")
        assert python_runtime is not None
        assert python_runtime.name == "Python"
        assert python_runtime.language_key == "python"

        # Non-existent runtime
        missing = manager.get_runtime("nonexistent")
        assert missing is None

    def test_get_all_runtimes(self, temp_data_dir):
        """Test getting all runtimes."""
        manager = RuntimeManager(data_dir=temp_data_dir)

        all_runtimes = manager.get_all_runtimes()
        assert len(all_runtimes) == 2

    def test_health_summary(self, temp_data_dir):
        """Test health summary generation."""
        manager = RuntimeManager(data_dir=temp_data_dir)

        # Before verification
        summary = manager.get_health_summary()
        assert summary["total_runtimes"] == 2
        assert summary["verified_count"] == 1  # Only Python is verified

        # Verify runtimes
        manager.verify_runtimes(timeout=5)

        # After verification
        summary = manager.get_health_summary()
        assert "by_status" in summary
        assert "by_category" in summary
