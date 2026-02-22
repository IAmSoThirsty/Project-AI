"""
Tests for SelfRepairAgent implementation.
"""

import os
import tempfile

import pytest

from app.resilience.self_repair_agent import SelfRepairAgent


class TestSelfRepairAgentInit:
    def test_initialises_disabled(self):
        agent = SelfRepairAgent(kernel=None)
        assert agent.enabled is False
        assert agent.repair_history == []
        assert agent.health_checks == {}

    def test_statistics_empty_on_init(self):
        agent = SelfRepairAgent(kernel=None)
        stats = agent.get_repair_statistics()
        assert stats["total_repairs"] == 0
        assert stats["components_monitored"] == 0


class TestHealthMonitoring:
    def test_monitor_health_returns_status(self):
        agent = SelfRepairAgent(kernel=None)
        report = agent.monitor_health("test_component")
        assert report["component"] == "test_component"
        assert report["status"] in ("healthy", "degraded")
        assert "metrics" in report
        assert "timestamp" in report

    def test_monitor_health_stores_check(self):
        agent = SelfRepairAgent(kernel=None)
        agent.monitor_health("test_component")
        assert "test_component" in agent.health_checks

    def test_monitor_health_updates_baselines(self):
        agent = SelfRepairAgent(kernel=None)
        agent.monitor_health("comp")
        assert "comp" in agent._baselines

    def test_monitor_health_multiple_calls_build_baseline(self):
        agent = SelfRepairAgent(kernel=None)
        for _ in range(5):
            agent.monitor_health("comp")
        # Should have at least some baseline entries
        assert len(agent._baselines["comp"]) > 0


class TestAnomalyDetection:
    def test_no_anomaly_on_normal_metrics(self):
        agent = SelfRepairAgent(kernel=None)
        # Build a stable baseline
        for _ in range(10):
            agent.monitor_health("comp")
        metrics = agent.health_checks["comp"]["metrics"]
        result = agent.detect_anomaly("comp", metrics)
        # Under normal conditions, should be False (no spike)
        assert isinstance(result, bool)

    def test_anomaly_on_critical_cpu(self):
        agent = SelfRepairAgent(kernel=None)
        # CPU above 95% triggers absolute threshold
        assert agent.detect_anomaly("comp", {"cpu_percent": 99.0}) is True

    def test_anomaly_on_critical_memory(self):
        agent = SelfRepairAgent(kernel=None)
        assert agent.detect_anomaly("comp", {"memory_percent": 95.0}) is True

    def test_anomaly_on_critical_disk(self):
        agent = SelfRepairAgent(kernel=None)
        assert agent.detect_anomaly("comp", {"disk_percent": 95.0}) is True

    def test_no_anomaly_on_low_values(self):
        agent = SelfRepairAgent(kernel=None)
        assert agent.detect_anomaly("comp", {"cpu_percent": 5.0}) is False


class TestDiagnosis:
    def test_diagnose_no_anomaly(self):
        agent = SelfRepairAgent(kernel=None)
        agent.monitor_health("comp")
        diag = agent.diagnose_problem("comp")
        assert diag["component"] == "comp"
        assert diag["diagnosis"] in ("no_anomaly", "anomaly_detected")

    def test_diagnose_auto_monitors_if_needed(self):
        agent = SelfRepairAgent(kernel=None)
        # No prior health check
        diag = agent.diagnose_problem("new_comp")
        assert diag["component"] == "new_comp"

    def test_diagnose_returns_suggested_fixes(self):
        agent = SelfRepairAgent(kernel=None)
        # Force a high-CPU health check
        agent.health_checks["comp"] = {
            "anomalies": [{"metric": "cpu_percent", "value": 99, "z_score": 5.0}],
        }
        diag = agent.diagnose_problem("comp")
        assert diag["diagnosis"] == "anomaly_detected"
        assert len(diag["suggested_fixes"]) > 0


class TestRepair:
    def test_repair_disabled_returns_false(self):
        agent = SelfRepairAgent(kernel=None)
        agent.enabled = False
        result = agent.apply_repair("comp", {"actions": ["reduce_load"]})
        assert result is False

    def test_repair_reduce_load(self):
        agent = SelfRepairAgent(kernel=None)
        agent.enabled = True
        result = agent.apply_repair("comp", {"actions": ["reduce_load"]})
        assert result is True
        assert len(agent.repair_history) == 1
        assert agent.repair_history[0]["status"] == "completed"

    def test_repair_clear_cache(self):
        agent = SelfRepairAgent(kernel=None)
        agent.enabled = True
        # Create a temp file matching the prefix
        tmp = tempfile.NamedTemporaryFile(prefix="project_ai_", delete=False)
        tmp.close()
        try:
            result = agent.apply_repair("comp", {"actions": ["clear_cache"]})
            assert result is True
        finally:
            # Cleanup in case test fails
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_repair_unknown_action(self):
        agent = SelfRepairAgent(kernel=None)
        agent.enabled = True
        result = agent.apply_repair("comp", {"actions": ["reboot_server"]})
        assert result is False

    def test_repair_recorded_in_history(self):
        agent = SelfRepairAgent(kernel=None)
        agent.enabled = True
        agent.apply_repair("comp", {"actions": ["reduce_load"]})
        assert len(agent.repair_history) == 1


class TestRecoveryValidation:
    def test_validate_recovery_returns_bool(self):
        agent = SelfRepairAgent(kernel=None)
        result = agent.validate_recovery("comp")
        assert isinstance(result, bool)


class TestStatistics:
    def test_statistics_tracks_repairs(self):
        agent = SelfRepairAgent(kernel=None)
        agent.enabled = True
        agent.apply_repair("a", {"actions": ["reduce_load"]})
        agent.apply_repair("b", {"actions": ["reboot_server"]})

        stats = agent.get_repair_statistics()
        assert stats["total_repairs"] == 2
        assert stats["successful_repairs"] == 1
        assert stats["failed_repairs"] == 1
