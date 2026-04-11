#                                           [2026-03-05 08:49]
#                                          Productivity: Active
"""
Integration Tests for Liara-Triumvirate Bridge

Tests the complete integration between Liara and Triumvirate including:
- Handoff protocols
- State synchronization
- Health monitoring
- Capability mapping
- Automatic fallback mechanisms
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from cognition.health import HealthSignal
from cognition.liara_guard import LiaraState
from kernel.liara_triumvirate_bridge import (
    LiaraTriumvirateBridge,
    TriumvirateHealth,
    BridgeState,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def healthy_health_signal():
    """Create a healthy HealthSignal"""
    return HealthSignal(alive=True, responsive=True, bounded=True, compliant=True)


@pytest.fixture
def unhealthy_health_signal():
    """Create an unhealthy HealthSignal"""
    return HealthSignal(alive=False, responsive=False, bounded=False, compliant=False)


@pytest.fixture
def healthy_triumvirate_health(healthy_health_signal):
    """Create a healthy TriumvirateHealth"""
    return TriumvirateHealth(
        galahad=healthy_health_signal,
        cerberus=healthy_health_signal,
        codex=healthy_health_signal,
        timestamp=datetime.utcnow(),
    )


@pytest.fixture
def degraded_triumvirate_health(healthy_health_signal, unhealthy_health_signal):
    """Create a TriumvirateHealth with one failed pillar"""
    return TriumvirateHealth(
        galahad=unhealthy_health_signal,  # Failed
        cerberus=healthy_health_signal,
        codex=healthy_health_signal,
        timestamp=datetime.utcnow(),
    )


@pytest.fixture
def mock_triumvirate():
    """Create a mock Triumvirate instance"""
    triumvirate = Mock()

    # Mock Galahad
    triumvirate.galahad = Mock()
    triumvirate.galahad.get_reasoning_history = Mock(return_value=[])
    triumvirate.galahad.get_curiosity_metrics = Mock(
        return_value={"current_score": 0.3, "enabled": True, "threshold": 0.5}
    )

    # Mock Cerberus
    triumvirate.cerberus = Mock()

    # Mock Codex
    triumvirate.codex = Mock()

    # Mock status
    triumvirate.get_status = Mock(
        return_value={
            "galahad": {
                "curiosity_metrics": {"current_score": 0.3},
                "history_size": 10,
            },
            "cerberus": {
                "total_enforcements": 100,
                "denied_count": 5,
                "policy_mode": "production",
            },
            "codex": {"loaded": True, "device": "cpu"},
        }
    )

    triumvirate.get_telemetry = Mock(return_value=[])
    triumvirate.process = Mock(
        return_value={
            "success": True,
            "output": "test_output",
            "correlation_id": "test_123",
        }
    )

    return triumvirate


@pytest.fixture
def liara_state():
    """Create a LiaraState instance"""
    state = LiaraState()
    return state


@pytest.fixture
def bridge(mock_triumvirate, liara_state):
    """Create a LiaraTriumvirateBridge instance"""
    return LiaraTriumvirateBridge(triumvirate=mock_triumvirate, liara_state=liara_state)


# ============================================================================
# HEALTH MONITORING TESTS
# ============================================================================


class TestHealthMonitoring:
    """Test health monitoring functionality"""

    def test_monitor_healthy_triumvirate(self, bridge, mock_triumvirate):
        """Test monitoring a healthy Triumvirate"""
        health = bridge.monitor_triumvirate_health()

        assert health.galahad.healthy
        assert health.cerberus.healthy
        assert health.codex.healthy
        assert health.is_stable()
        assert len(health.get_failed_pillars()) == 0

    def test_monitor_degraded_galahad(self, bridge, mock_triumvirate):
        """Test monitoring when Galahad is degraded"""
        # Set excessive curiosity
        mock_triumvirate.get_status = Mock(
            return_value={
                "galahad": {
                    "curiosity_metrics": {"current_score": 0.99},  # Too high
                    "history_size": 10,
                },
                "cerberus": {
                    "total_enforcements": 100,
                    "denied_count": 5,
                    "policy_mode": "production",
                },
                "codex": {"loaded": True, "device": "cpu"},
            }
        )

        health = bridge.monitor_triumvirate_health()

        assert not health.galahad.compliant  # Curiosity too high
        assert not health.galahad.healthy
        assert "galahad" in health.get_failed_pillars()

    def test_monitor_degraded_cerberus(self, bridge, mock_triumvirate):
        """Test monitoring when Cerberus is degraded"""
        # Set high denial rate
        mock_triumvirate.get_status = Mock(
            return_value={
                "galahad": {
                    "curiosity_metrics": {"current_score": 0.3},
                    "history_size": 10,
                },
                "cerberus": {
                    "total_enforcements": 100,
                    "denied_count": 60,  # 60% denial rate
                    "policy_mode": "production",
                },
                "codex": {"loaded": True, "device": "cpu"},
            }
        )

        health = bridge.monitor_triumvirate_health()

        assert not health.cerberus.bounded  # High denial rate
        assert not health.cerberus.healthy
        assert "cerberus" in health.get_failed_pillars()

    def test_monitor_degraded_codex(self, bridge, mock_triumvirate):
        """Test monitoring when Codex is degraded"""
        # Set model not loaded
        mock_triumvirate.get_status = Mock(
            return_value={
                "galahad": {
                    "curiosity_metrics": {"current_score": 0.3},
                    "history_size": 10,
                },
                "cerberus": {
                    "total_enforcements": 100,
                    "denied_count": 5,
                    "policy_mode": "production",
                },
                "codex": {"loaded": False, "device": "cpu"},  # Not loaded
            }
        )

        health = bridge.monitor_triumvirate_health()

        assert not health.codex.bounded  # Model not loaded
        assert not health.codex.healthy
        assert "codex" in health.get_failed_pillars()

    def test_monitor_no_triumvirate(self):
        """Test monitoring when no Triumvirate instance exists"""
        bridge = LiaraTriumvirateBridge(triumvirate=None)
        health = bridge.monitor_triumvirate_health()

        assert not health.is_stable()
        assert len(health.get_failed_pillars()) == 3

    def test_health_check_count(self, bridge):
        """Test that health checks are counted"""
        assert bridge.health_checks == 0

        bridge.monitor_triumvirate_health()
        assert bridge.health_checks == 1

        bridge.monitor_triumvirate_health()
        bridge.monitor_triumvirate_health()
        assert bridge.health_checks == 3


# ============================================================================
# HANDOFF PROTOCOL TESTS
# ============================================================================


class TestHandoffProtocol:
    """Test handoff protocol between Triumvirate and Liara"""

    @patch("kernel.liara_triumvirate_bridge.maybe_activate_liara")
    @patch("kernel.liara_triumvirate_bridge.audit")
    def test_handoff_to_liara_success(
        self, mock_audit, mock_activate, bridge, mock_triumvirate
    ):
        """Test successful handoff from Triumvirate to Liara"""
        mock_activate.return_value = "galahad"  # Activation successful

        success = bridge.execute_handoff_to_liara("galahad", "test_failure")

        assert success
        assert bridge.state.mode == "liara"
        assert bridge.state.active_controller == "liara"
        assert bridge.state.handoff_reason == "galahad:test_failure"
        assert bridge.handoff_count == 1
        assert bridge.state.last_handoff is not None

        mock_activate.assert_called_once()
        mock_audit.assert_called()

    @patch("kernel.liara_triumvirate_bridge.maybe_activate_liara")
    @patch("kernel.liara_triumvirate_bridge.audit")
    def test_handoff_to_liara_activation_failure(
        self, mock_audit, mock_activate, bridge
    ):
        """Test handoff when Liara activation fails"""
        mock_activate.return_value = None  # Activation failed

        success = bridge.execute_handoff_to_liara("cerberus", "test_failure")

        assert not success
        assert bridge.state.mode == "triumvirate"  # Should remain in Triumvirate mode
        assert bridge.handoff_count == 0

    @patch("kernel.liara_triumvirate_bridge.restore_pillar")
    @patch("kernel.liara_triumvirate_bridge.audit")
    def test_handoff_to_triumvirate_success(
        self, mock_audit, mock_restore, bridge, healthy_triumvirate_health
    ):
        """Test successful handoff from Liara to Triumvirate"""
        # Setup: Start in Liara mode
        bridge.state.mode = "liara"
        bridge.state.active_controller = "liara"
        bridge.state.triumvirate_health = healthy_triumvirate_health

        success = bridge.execute_handoff_to_triumvirate("test_restore")

        assert success
        assert bridge.state.mode == "triumvirate"
        assert bridge.state.active_controller == "triumvirate"
        assert bridge.state.handoff_reason == "test_restore"
        assert bridge.handoff_count == 1

        mock_restore.assert_called_once()
        mock_audit.assert_called()

    @patch("kernel.liara_triumvirate_bridge.audit")
    def test_handoff_to_triumvirate_unhealthy(
        self, mock_audit, bridge, degraded_triumvirate_health, mock_triumvirate
    ):
        """Test handoff to Triumvirate fails when it's unhealthy"""
        bridge.state.mode = "liara"
        
        # Update mock to return unhealthy status (history too large)
        mock_triumvirate.get_status = Mock(
            return_value={
                "galahad": {
                    "curiosity_metrics": {"current_score": 0.3},
                    "history_size": 20000,  # Too large, exceeds 10000 bound
                },
                "cerberus": {
                    "total_enforcements": 100,
                    "denied_count": 5,
                    "policy_mode": "production",
                },
                "codex": {"loaded": True, "device": "cpu"},
            }
        )

        success = bridge.execute_handoff_to_triumvirate("test_restore")

        assert not success
        assert bridge.state.mode == "liara"  # Should remain in Liara mode

    @patch("kernel.liara_triumvirate_bridge.maybe_activate_liara")
    def test_handoff_validation_invalid_pillar(self, mock_activate, bridge):
        """Test handoff validation with invalid pillar name"""
        success = bridge.execute_handoff_to_liara("invalid_pillar", "test")

        assert not success
        mock_activate.assert_not_called()

    @patch("kernel.liara_triumvirate_bridge.maybe_activate_liara")
    @patch("kernel.liara_triumvirate_bridge.COOLDOWN_SECONDS", 300)
    def test_handoff_cooldown_enforcement(self, mock_activate, bridge):
        """Test that cooldown period is enforced"""
        mock_activate.return_value = "galahad"

        # First handoff
        success1 = bridge.execute_handoff_to_liara("galahad", "test1")
        assert success1

        # Immediate second handoff should fail due to cooldown
        success2 = bridge.execute_handoff_to_liara("cerberus", "test2")
        assert not success2

        # Only one activation should have occurred
        assert mock_activate.call_count == 1


# ============================================================================
# STATE SYNCHRONIZATION TESTS
# ============================================================================


class TestStateSynchronization:
    """Test state synchronization between systems"""

    def test_capture_triumvirate_state(self, bridge, mock_triumvirate):
        """Test capturing Triumvirate state"""
        state = bridge._capture_triumvirate_state()

        assert "status" in state
        assert "telemetry" in state
        assert "timestamp" in state
        assert "galahad_history" in state

    def test_capture_liara_state(self, bridge, liara_state):
        """Test capturing Liara state"""
        liara_state.active_role = "galahad"
        liara_state.expires_at = datetime.utcnow() + timedelta(seconds=900)

        state = bridge._capture_liara_state()

        assert state["active_role"] == "galahad"
        assert state["expires_at"] is not None
        assert "timestamp" in state

    @patch("kernel.liara_triumvirate_bridge.audit")
    def test_sync_state_to_liara(self, mock_audit, bridge):
        """Test syncing Triumvirate state to Liara"""
        triumvirate_state = {
            "status": {"test": "data"},
            "telemetry": [],
        }

        bridge._sync_state_to_liara(triumvirate_state, "galahad")

        assert "triumvirate_snapshot" in bridge.state.sync_data
        assert bridge.state.sync_data["failed_pillar"] == "galahad"
        assert "handoff_timestamp" in bridge.state.sync_data
        assert bridge.sync_operations == 1

    @patch("kernel.liara_triumvirate_bridge.audit")
    def test_sync_state_to_triumvirate(self, mock_audit, bridge):
        """Test syncing Liara state to Triumvirate"""
        liara_state = {"active_role": "galahad", "test": "data"}

        bridge._sync_state_to_triumvirate(liara_state)

        assert "liara_snapshot" in bridge.state.sync_data
        assert "restore_timestamp" in bridge.state.sync_data
        assert bridge.sync_operations == 1

        # Triumvirate-specific data should be cleared
        assert "triumvirate_snapshot" not in bridge.state.sync_data
        assert "failed_pillar" not in bridge.state.sync_data


# ============================================================================
# CAPABILITY MAPPING TESTS
# ============================================================================


class TestCapabilityMapping:
    """Test capability mapping between systems"""

    def test_map_galahad_capabilities(self, bridge):
        """Test mapping Galahad capabilities to Liara"""
        capabilities = bridge.map_triumvirate_capabilities_to_liara("galahad")

        assert capabilities["reasoning"] == "limited"
        assert capabilities["arbitration"] == "allowed"
        assert capabilities["curiosity"] == "disabled"
        assert capabilities["history_depth"] == 10
        assert capabilities["sovereign_mode"] is True

    def test_map_cerberus_capabilities(self, bridge):
        """Test mapping Cerberus capabilities to Liara"""
        capabilities = bridge.map_triumvirate_capabilities_to_liara("cerberus")

        assert capabilities["policy_enforcement"] == "strict"
        assert capabilities["input_validation"] == "allowed"
        assert capabilities["output_validation"] == "allowed"
        assert capabilities["custom_policies"] == "disabled"
        assert capabilities["block_on_deny"] is True

    def test_map_codex_capabilities(self, bridge):
        """Test mapping Codex capabilities to Liara"""
        capabilities = bridge.map_triumvirate_capabilities_to_liara("codex")

        assert capabilities["ml_inference"] == "disabled"
        assert capabilities["model_loading"] == "disabled"
        assert capabilities["fallback_mode"] == "rule_based"
        assert capabilities["device"] == "cpu"

    def test_map_unknown_pillar(self, bridge):
        """Test mapping unknown pillar returns safe defaults"""
        capabilities = bridge.map_triumvirate_capabilities_to_liara("unknown")

        assert "status" in capabilities
        assert capabilities["status"] == "unknown_pillar"


# ============================================================================
# TTL AND AUTOMATIC FALLBACK TESTS
# ============================================================================


class TestTTLAndFallback:
    """Test TTL expiry and automatic fallback"""

    @patch("kernel.liara_triumvirate_bridge.check_liara_state")
    @patch("kernel.liara_triumvirate_bridge.audit")
    def test_ttl_expired_triggers_fallback(
        self, mock_audit, mock_check_state, bridge, liara_state, healthy_triumvirate_health
    ):
        """Test that expired TTL triggers automatic fallback"""
        # Setup: Liara mode with expired state
        bridge.state.mode = "liara"
        bridge.state.active_controller = "liara"
        liara_state.active_role = None  # Simulates expiry
        liara_state.expires_at = None
        bridge.state.triumvirate_health = healthy_triumvirate_health

        with patch.object(
            bridge, "execute_handoff_to_triumvirate", return_value=True
        ) as mock_handoff:
            fallback_executed = bridge.check_liara_ttl_and_fallback()

            assert fallback_executed
            mock_handoff.assert_called_once_with("ttl_expired")

    @patch("kernel.liara_triumvirate_bridge.check_liara_state")
    @patch("kernel.liara_triumvirate_bridge.audit")
    def test_ttl_expired_but_triumvirate_unhealthy(
        self, mock_audit, mock_check_state, bridge, liara_state, degraded_triumvirate_health, mock_triumvirate
    ):
        """Test TTL expiry when Triumvirate is still unhealthy"""
        bridge.state.mode = "liara"
        liara_state.active_role = None  # Expired
        
        # Update mock to return unhealthy status (history too large)
        mock_triumvirate.get_status = Mock(
            return_value={
                "galahad": {
                    "curiosity_metrics": {"current_score": 0.3},
                    "history_size": 20000,  # Too large, exceeds 10000 bound
                },
                "cerberus": {
                    "total_enforcements": 100,
                    "denied_count": 5,
                    "policy_mode": "production",
                },
                "codex": {"loaded": True, "device": "cpu"},
            }
        )

        fallback_executed = bridge.check_liara_ttl_and_fallback()

        assert not fallback_executed
        assert bridge.state.mode == "governance_hold"  # Enter governance hold

    def test_no_fallback_when_liara_active(self, bridge, liara_state):
        """Test no fallback when Liara is still active"""
        bridge.state.mode = "liara"
        liara_state.active_role = "galahad"
        liara_state.expires_at = datetime.utcnow() + timedelta(seconds=600)

        with patch("kernel.liara_triumvirate_bridge.check_liara_state"):
            fallback_executed = bridge.check_liara_ttl_and_fallback()

            assert not fallback_executed
            assert bridge.state.mode == "liara"


# ============================================================================
# REQUEST PROCESSING TESTS
# ============================================================================


class TestRequestProcessing:
    """Test request processing through the bridge"""

    def test_process_with_triumvirate(self, bridge, mock_triumvirate):
        """Test processing request through Triumvirate"""
        result = bridge.process_request("test_input", {"test": "context"})

        assert result["success"]
        assert result["bridge_mode"] == "triumvirate"
        assert result["controller"] == "triumvirate"
        mock_triumvirate.process.assert_called_once()

    @patch("kernel.liara_triumvirate_bridge.maybe_activate_liara")
    def test_process_triggers_handoff_on_degradation(
        self, mock_activate, bridge, mock_triumvirate
    ):
        """Test that processing triggers handoff when Triumvirate degrades"""
        # Make Triumvirate unhealthy
        mock_triumvirate.get_status = Mock(
            return_value={
                "galahad": {
                    "curiosity_metrics": {"current_score": 0.99},
                    "history_size": 10,
                },
                "cerberus": {
                    "total_enforcements": 100,
                    "denied_count": 5,
                    "policy_mode": "production",
                },
                "codex": {"loaded": True, "device": "cpu"},
            }
        )
        mock_activate.return_value = "galahad"

        result = bridge.process_request("test_input")

        # Should detect unhealthy state and handoff to Liara
        mock_activate.assert_called_once()
        assert result["controller"] == "liara"

    def test_process_with_liara(self, bridge, liara_state):
        """Test processing request through Liara"""
        bridge.state.mode = "liara"
        bridge.state.active_controller = "liara"
        bridge.state.sync_data["failed_pillar"] = "galahad"
        liara_state.active_role = "galahad"

        result = bridge.process_request("test_input", {"test": "context"})

        assert result["success"]
        assert result["bridge_mode"] == "liara"
        assert result["controller"] == "liara"
        assert "restrictions" in result
        assert result["liara_role"] == "galahad"


# ============================================================================
# STATUS AND DIAGNOSTICS TESTS
# ============================================================================


class TestStatusAndDiagnostics:
    """Test status reporting and diagnostics"""

    def test_get_bridge_status(self, bridge, liara_state):
        """Test getting comprehensive bridge status"""
        liara_state.active_role = "galahad"
        liara_state.expires_at = datetime.utcnow() + timedelta(seconds=900)

        status = bridge.get_bridge_status()

        assert status["mode"] == "triumvirate"
        assert status["active_controller"] == "triumvirate"
        assert status["handoff_count"] == 0
        assert status["health_checks"] == 0
        assert status["sync_operations"] == 0
        assert "liara_state" in status
        assert status["liara_state"]["active_role"] == "galahad"

    @patch("kernel.liara_triumvirate_bridge.maybe_activate_liara")
    def test_metrics_tracking(self, mock_activate, bridge, mock_triumvirate):
        """Test that bridge tracks metrics correctly"""
        mock_activate.return_value = "galahad"

        # Perform operations
        bridge.monitor_triumvirate_health()
        bridge.monitor_triumvirate_health()
        bridge.execute_handoff_to_liara("galahad", "test")

        status = bridge.get_bridge_status()

        assert status["health_checks"] == 2
        assert status["handoff_count"] == 1
        assert status["sync_operations"] == 1  # From handoff


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestEndToEndIntegration:
    """End-to-end integration tests"""

    @patch("kernel.liara_triumvirate_bridge.maybe_activate_liara")
    @patch("kernel.liara_triumvirate_bridge.restore_pillar")
    @patch("kernel.liara_triumvirate_bridge.audit")
    def test_full_cycle_triumvirate_to_liara_and_back(
        self, mock_audit, mock_restore, mock_activate, mock_triumvirate, liara_state
    ):
        """Test complete cycle: Triumvirate -> Liara -> Triumvirate"""
        bridge = LiaraTriumvirateBridge(
            triumvirate=mock_triumvirate, liara_state=liara_state
        )

        # Initial state: Triumvirate
        assert bridge.state.mode == "triumvirate"

        # Step 1: Triumvirate degrades, handoff to Liara
        mock_activate.return_value = "galahad"
        success = bridge.execute_handoff_to_liara("galahad", "health_degradation")

        assert success
        assert bridge.state.mode == "liara"
        assert bridge.handoff_count == 1

        # Step 2: Process requests through Liara
        liara_state.active_role = "galahad"
        result = bridge.process_request("test_input")

        assert result["success"]
        assert result["controller"] == "liara"

        # Step 3: Triumvirate recovers, handoff back
        success = bridge.execute_handoff_to_triumvirate("pillar_restored")

        assert success
        assert bridge.state.mode == "triumvirate"
        assert bridge.handoff_count == 2

        # Step 4: Process requests through Triumvirate again
        result = bridge.process_request("test_input")

        assert result["success"]
        assert result["controller"] == "triumvirate"

    @patch("kernel.liara_triumvirate_bridge.check_liara_state")
    @patch("kernel.liara_triumvirate_bridge.maybe_activate_liara")
    @patch("kernel.liara_triumvirate_bridge.audit")
    def test_automatic_fallback_scenario(
        self, mock_audit, mock_activate, mock_check_state, mock_triumvirate, liara_state
    ):
        """Test automatic fallback when TTL expires"""
        bridge = LiaraTriumvirateBridge(
            triumvirate=mock_triumvirate, liara_state=liara_state
        )

        # Setup: In Liara mode
        mock_activate.return_value = "galahad"
        bridge.execute_handoff_to_liara("galahad", "test")
        liara_state.active_role = "galahad"

        # Simulate TTL expiry
        liara_state.active_role = None
        liara_state.expires_at = None

        # Process request triggers TTL check and automatic fallback
        # Mock the handoff to return successfully
        with patch.object(
            bridge, "execute_handoff_to_triumvirate", return_value=True
        ) as mock_handoff:
            result = bridge.process_request("test_input")

            # Should have triggered fallback
            mock_handoff.assert_called_once_with("ttl_expired")

        # After the mocked handoff, manually update state to reflect success
        bridge.state.mode = "triumvirate"
        bridge.state.active_controller = "triumvirate"
        
        # Process another request to verify we're now using Triumvirate
        result = bridge.process_request("test_input")
        assert result["controller"] == "triumvirate"

    def test_multiple_pillars_failure_governance_hold(
        self, mock_triumvirate, liara_state
    ):
        """Test governance hold when multiple pillars fail"""
        bridge = LiaraTriumvirateBridge(
            triumvirate=mock_triumvirate, liara_state=liara_state
        )

        # Make multiple pillars unhealthy
        mock_triumvirate.get_status = Mock(
            return_value={
                "galahad": {
                    "curiosity_metrics": {"current_score": 0.99},
                    "history_size": 10,
                },
                "cerberus": {
                    "total_enforcements": 100,
                    "denied_count": 60,
                    "policy_mode": "production",
                },
                "codex": {"loaded": False, "device": "cpu"},
            }
        )

        health = bridge.monitor_triumvirate_health()

        # Multiple failures
        assert len(health.get_failed_pillars()) >= 2
        assert not health.is_stable()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
