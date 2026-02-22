"""
Tests for SubstrateManager.get_health_status() implementation.
"""

import pytest

from cerberus.sase.core.substrate import (
    DeploymentTopology,
    FailureMode,
    SubstrateManager,
)


class TestHealthStatus:
    def test_returns_expected_keys(self):
        sm = SubstrateManager()
        status = sm.get_health_status()
        assert "topology" in status
        assert "healthy" in status
        assert "metrics" in status
        assert "recent_failures" in status
        assert "monotonic_time" in status

    def test_topology_matches_init(self):
        sm = SubstrateManager(topology=DeploymentTopology.HA_CLUSTER)
        status = sm.get_health_status()
        assert status["topology"] == "ha-cluster"

    def test_healthy_is_bool(self):
        sm = SubstrateManager()
        status = sm.get_health_status()
        assert isinstance(status["healthy"], bool)

    def test_metrics_is_dict(self):
        sm = SubstrateManager()
        status = sm.get_health_status()
        assert isinstance(status["metrics"], dict)

    def test_recent_failures_starts_at_zero(self):
        sm = SubstrateManager()
        status = sm.get_health_status()
        assert status["recent_failures"] == 0

    def test_failure_increments_count(self):
        sm = SubstrateManager()
        sm.handle_failure(FailureMode.CLOCK_SKEW, {})
        status = sm.get_health_status()
        assert status["recent_failures"] == 1


class TestValidateDeployment:
    def test_returns_dict(self):
        sm = SubstrateManager()
        result = sm.validate_deployment()
        assert "valid" in result
        assert "topology" in result


class TestHandleFailure:
    def test_known_failure(self):
        sm = SubstrateManager()
        result = sm.handle_failure(FailureMode.REGIONAL_OUTAGE, {"backup_region": "eu-west-1"})
        assert result["success"] is True

    def test_clock_skew_recovery(self):
        sm = SubstrateManager()
        result = sm.handle_failure(FailureMode.CLOCK_SKEW, {})
        assert result["success"] is True
        assert result["action"] == "monotonic_enforcement"
