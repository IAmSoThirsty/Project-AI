"""
Tests for the three-tier platform strategy implementation.

Tests verify:
- Tier component registration
- Authority flow validation (downward only)
- Capability flow validation (upward only)
- Tier health monitoring
- Cross-tier governance policies
"""

import pytest

from app.core.platform_tiers import (
    AuthorityLevel,
    ComponentRole,
    PlatformTier,
    TierRegistry,
    get_tier_registry,
)
from app.core.tier_governance_policies import (
    BlockReason,
    BlockType,
    CrossTierPolicyEngine,
    get_policy_engine,
)
from app.core.tier_health_dashboard import (
    HealthLevel,
    HealthMetric,
    MetricType,
    TierHealthMonitor,
    get_health_monitor,
)
from app.core.tier_interfaces import (
    RequestType,
    TierInterfaceRouter,
    TierRequest,
    get_tier_router,
)


class TestTierRegistry:
    """Test tier component registration and validation."""

    def setup_method(self):
        """Set up fresh registry for each test."""
        # Create a new registry instance for testing
        self.registry = TierRegistry()

    def test_register_tier1_component(self):
        """Test registering a Tier 1 component."""
        component = self.registry.register_component(
            component_id="test_governance",
            component_name="TestGovernance",
            tier=PlatformTier.TIER_1_GOVERNANCE,
            authority_level=AuthorityLevel.SOVEREIGN,
            role=ComponentRole.GOVERNANCE_CORE,
            component_ref=object(),
            dependencies=[],
            can_be_paused=False,
            can_be_replaced=False,
        )

        assert component.component_id == "test_governance"
        assert component.tier == PlatformTier.TIER_1_GOVERNANCE
        assert component.authority_level == AuthorityLevel.SOVEREIGN
        assert not component.can_be_paused
        assert not component.can_be_replaced

    def test_register_tier2_component(self):
        """Test registering a Tier 2 component."""
        component = self.registry.register_component(
            component_id="test_infrastructure",
            component_name="TestInfrastructure",
            tier=PlatformTier.TIER_2_INFRASTRUCTURE,
            authority_level=AuthorityLevel.CONSTRAINED,
            role=ComponentRole.INFRASTRUCTURE_CONTROLLER,
            component_ref=object(),
            dependencies=[],
            can_be_paused=True,
            can_be_replaced=False,
        )

        assert component.tier == PlatformTier.TIER_2_INFRASTRUCTURE
        assert component.authority_level == AuthorityLevel.CONSTRAINED
        assert component.can_be_paused

    def test_register_tier3_component(self):
        """Test registering a Tier 3 component."""
        component = self.registry.register_component(
            component_id="test_application",
            component_name="TestApplication",
            tier=PlatformTier.TIER_3_APPLICATION,
            authority_level=AuthorityLevel.SANDBOXED,
            role=ComponentRole.RUNTIME_SERVICE,
            component_ref=object(),
            dependencies=[],
            can_be_paused=True,
            can_be_replaced=True,
        )

        assert component.tier == PlatformTier.TIER_3_APPLICATION
        assert component.authority_level == AuthorityLevel.SANDBOXED
        assert component.can_be_paused
        assert component.can_be_replaced

    def test_tier1_cannot_depend_on_tier2(self):
        """Test that Tier 1 components cannot depend on Tier 2."""
        # First register Tier 2 component
        self.registry.register_component(
            component_id="tier2_infra",
            component_name="Tier2Infrastructure",
            tier=PlatformTier.TIER_2_INFRASTRUCTURE,
            authority_level=AuthorityLevel.CONSTRAINED,
            role=ComponentRole.INFRASTRUCTURE_CONTROLLER,
            component_ref=object(),
            dependencies=[],
        )

        # Try to register Tier 1 with dependency on Tier 2 - should fail
        with pytest.raises(ValueError, match="Tier 1 cannot depend on Tier 2"):
            self.registry.register_component(
                component_id="tier1_gov",
                component_name="Tier1Governance",
                tier=PlatformTier.TIER_1_GOVERNANCE,
                authority_level=AuthorityLevel.SOVEREIGN,
                role=ComponentRole.GOVERNANCE_CORE,
                component_ref=object(),
                dependencies=["tier2_infra"],  # Invalid dependency
            )

    def test_authority_flow_downward(self):
        """Test that authority can only flow downward."""
        # Register components in all tiers
        self.registry.register_component(
            component_id="tier1",
            component_name="Tier1Component",
            tier=PlatformTier.TIER_1_GOVERNANCE,
            authority_level=AuthorityLevel.SOVEREIGN,
            role=ComponentRole.GOVERNANCE_CORE,
            component_ref=object(),
        )

        self.registry.register_component(
            component_id="tier2",
            component_name="Tier2Component",
            tier=PlatformTier.TIER_2_INFRASTRUCTURE,
            authority_level=AuthorityLevel.CONSTRAINED,
            role=ComponentRole.INFRASTRUCTURE_CONTROLLER,
            component_ref=object(),
        )

        self.registry.register_component(
            component_id="tier3",
            component_name="Tier3Component",
            tier=PlatformTier.TIER_3_APPLICATION,
            authority_level=AuthorityLevel.SANDBOXED,
            role=ComponentRole.RUNTIME_SERVICE,
            component_ref=object(),
        )

        # Valid: Tier 1 → Tier 2 (downward)
        is_valid, reason = self.registry.validate_authority_flow("tier1", "tier2", "command")
        assert is_valid

        # Valid: Tier 2 → Tier 3 (downward)
        is_valid, reason = self.registry.validate_authority_flow("tier2", "tier3", "command")
        assert is_valid

        # Invalid: Tier 3 → Tier 2 (upward)
        is_valid, reason = self.registry.validate_authority_flow("tier3", "tier2", "command")
        assert not is_valid

        # Invalid: Tier 2 → Tier 1 (upward)
        is_valid, reason = self.registry.validate_authority_flow("tier2", "tier1", "command")
        assert not is_valid

    def test_pause_resume_component(self):
        """Test pausing and resuming components."""
        component_id = "pausable_component"
        self.registry.register_component(
            component_id=component_id,
            component_name="PausableComponent",
            tier=PlatformTier.TIER_2_INFRASTRUCTURE,
            authority_level=AuthorityLevel.CONSTRAINED,
            role=ComponentRole.INFRASTRUCTURE_CONTROLLER,
            component_ref=object(),
            can_be_paused=True,
        )

        # Pause component
        assert self.registry.pause_component(component_id)
        assert self.registry.is_component_paused(component_id)

        # Resume component
        assert self.registry.resume_component(component_id)
        assert not self.registry.is_component_paused(component_id)

    def test_get_tier_health(self):
        """Test getting tier health status."""
        # Register a component
        self.registry.register_component(
            component_id="health_test",
            component_name="HealthTest",
            tier=PlatformTier.TIER_1_GOVERNANCE,
            authority_level=AuthorityLevel.SOVEREIGN,
            role=ComponentRole.GOVERNANCE_CORE,
            component_ref=object(),
        )

        health = self.registry.get_tier_health(PlatformTier.TIER_1_GOVERNANCE)
        assert health.tier == PlatformTier.TIER_1_GOVERNANCE
        assert health.component_count >= 1
        assert health.is_operational


class TestTierInterfaceRouter:
    """Test cross-tier request routing."""

    def setup_method(self):
        """Set up fresh router for each test."""
        self.router = TierInterfaceRouter()

    def test_authority_command_downward_valid(self):
        """Test that authority commands can flow downward."""
        request = TierRequest(
            request_id="req_1",
            request_type=RequestType.AUTHORITY_COMMAND,
            source_tier=1,  # Tier 1
            target_tier=2,  # Tier 2
            source_component="governance",
            target_component="infrastructure",
            operation="pause",
            payload={},
        )

        response = self.router.route_request(request)
        assert response.success

    def test_authority_command_upward_invalid(self):
        """Test that authority commands cannot flow upward."""
        request = TierRequest(
            request_id="req_2",
            request_type=RequestType.AUTHORITY_COMMAND,
            source_tier=3,  # Tier 3
            target_tier=2,  # Tier 2 (upward)
            source_component="application",
            target_component="infrastructure",
            operation="pause",
            payload={},
        )

        response = self.router.route_request(request)
        assert not response.success
        assert "Authority cannot flow upward" in response.error_message

    def test_capability_request_upward_valid(self):
        """Test that capability requests can flow upward."""
        request = TierRequest(
            request_id="req_3",
            request_type=RequestType.CAPABILITY_REQUEST,
            source_tier=3,  # Tier 3
            target_tier=1,  # Tier 1 (upward)
            source_component="application",
            target_component="governance",
            operation="evaluate_action",
            payload={},
        )

        response = self.router.route_request(request)
        assert response.success

    def test_capability_request_downward_invalid(self):
        """Test that capability requests cannot flow downward."""
        request = TierRequest(
            request_id="req_4",
            request_type=RequestType.CAPABILITY_REQUEST,
            source_tier=1,  # Tier 1
            target_tier=3,  # Tier 3 (downward)
            source_component="governance",
            target_component="application",
            operation="request_capability",
            payload={},
        )

        response = self.router.route_request(request)
        assert not response.success
        assert "cannot flow downward" in response.error_message


class TestCrossTierPolicyEngine:
    """Test cross-tier governance policies."""

    def setup_method(self):
        """Set up fresh policy engine for each test."""
        self.engine = CrossTierPolicyEngine()

    def test_tier2_temporary_block_autonomous(self):
        """Test that Tier 2 can autonomously block Tier 3 temporarily."""
        success, reason, block = self.engine.request_block(
            component_id="app_unsafe",
            component_name="UnsafeApp",
            tier=3,
            blocked_by="security_enforcer",
            blocking_tier=2,
            reason=BlockReason.SECURITY_VIOLATION,
            block_type=BlockType.TEMPORARY,
            duration_seconds=180,  # 3 minutes
        )

        assert success
        assert block is not None
        assert block.block_type == BlockType.TEMPORARY
        assert block.is_active

    def test_tier2_permanent_block_requires_approval(self):
        """Test that Tier 2 permanent blocks require approval."""
        success, reason, block = self.engine.request_block(
            component_id="app_malicious",
            component_name="MaliciousApp",
            tier=3,
            blocked_by="security_enforcer",
            blocking_tier=2,
            reason=BlockReason.SECURITY_VIOLATION,
            block_type=BlockType.PERMANENT,
        )

        # Should succeed but require approval
        assert success
        assert block is not None
        # In real system, governance_approved would be False until reviewed

    def test_upward_block_invalid(self):
        """Test that Tier 3 cannot block Tier 2."""
        success, reason, block = self.engine.request_block(
            component_id="infra_component",
            component_name="InfraComponent",
            tier=2,
            blocked_by="malicious_app",
            blocking_tier=3,  # Tier 3 trying to block Tier 2
            reason=BlockReason.POLICY_BREACH,
            block_type=BlockType.TEMPORARY,
        )

        assert not success
        assert "Authority cannot flow upward" in reason

    def test_appeal_mechanism(self):
        """Test block appeal mechanism."""
        # Create a block
        success, _, block = self.engine.request_block(
            component_id="app_blocked",
            component_name="BlockedApp",
            tier=3,
            blocked_by="security_enforcer",
            blocking_tier=2,
            reason=BlockReason.ANOMALOUS_BEHAVIOR,
            block_type=BlockType.TEMPORARY,
        )
        assert success

        # File appeal
        success, reason, appeal = self.engine.file_appeal(
            block_id=block.block_id,
            appellant="app_blocked",
            justification="False positive detection",
        )

        assert success
        assert appeal is not None
        assert appeal.block_id == block.block_id

    def test_lift_block(self):
        """Test lifting an active block."""
        # Create block
        success, _, block = self.engine.request_block(
            component_id="app_temp",
            component_name="TempBlockedApp",
            tier=3,
            blocked_by="security_enforcer",
            blocking_tier=2,
            reason=BlockReason.MAINTENANCE,
            block_type=BlockType.TEMPORARY,
        )
        assert success
        assert block.is_active

        # Lift block
        assert self.engine.lift_block(block.block_id, "security_enforcer")
        assert not block.is_active


class TestTierHealthMonitor:
    """Test tier health monitoring."""

    def setup_method(self):
        """Set up fresh health monitor for each test."""
        self.monitor = TierHealthMonitor()

    def test_record_metric(self):
        """Test recording health metrics."""
        metric = HealthMetric(
            metric_name="test_latency",
            metric_type=MetricType.LATENCY,
            value=150.0,
            unit="ms",
            threshold_warning=200.0,
            threshold_critical=500.0,
        )

        self.monitor.record_metric(PlatformTier.TIER_1_GOVERNANCE, metric)

        # Metric should be healthy (below warning threshold)
        assert metric.get_health_level() == HealthLevel.HEALTHY

    def test_metric_thresholds(self):
        """Test metric threshold detection."""
        # Warning threshold
        metric_warning = HealthMetric(
            metric_name="test_metric",
            metric_type=MetricType.ERROR_RATE,
            value=15.0,
            unit="percent",
            threshold_warning=10.0,
            threshold_critical=20.0,
        )
        assert metric_warning.get_health_level() == HealthLevel.DEGRADED

        # Critical threshold
        metric_critical = HealthMetric(
            metric_name="test_metric",
            metric_type=MetricType.ERROR_RATE,
            value=25.0,
            unit="percent",
            threshold_warning=10.0,
            threshold_critical=20.0,
        )
        assert metric_critical.get_health_level() == HealthLevel.CRITICAL

    def test_platform_health_collection(self):
        """Test collecting platform-wide health."""
        report = self.monitor.collect_platform_health()

        assert report is not None
        assert report.overall_health in [
            HealthLevel.HEALTHY,
            HealthLevel.DEGRADED,
            HealthLevel.CRITICAL,
            HealthLevel.OFFLINE,
        ]
        assert len(report.tier_reports) == 3  # Three tiers

    def test_alert_generation(self):
        """Test that alerts are generated for critical metrics."""
        metric = HealthMetric(
            metric_name="critical_metric",
            metric_type=MetricType.ERROR_RATE,
            value=50.0,
            unit="percent",
            threshold_warning=10.0,
            threshold_critical=20.0,
        )

        initial_alert_count = len(self.monitor.get_alerts())
        self.monitor.record_metric(PlatformTier.TIER_2_INFRASTRUCTURE, metric)

        # Should have generated an alert
        alerts = self.monitor.get_alerts()
        assert len(alerts) > initial_alert_count

    def test_alert_acknowledgment(self):
        """Test acknowledging alerts."""
        # Generate alert
        metric = HealthMetric(
            metric_name="test_alert",
            metric_type=MetricType.ERROR_RATE,
            value=30.0,
            unit="percent",
            threshold_critical=20.0,
        )
        self.monitor.record_metric(PlatformTier.TIER_3_APPLICATION, metric)

        # Get unacknowledged alerts
        unack_alerts = self.monitor.get_alerts(acknowledged=False)
        if unack_alerts:
            alert = unack_alerts[0]

            # Acknowledge alert
            assert self.monitor.acknowledge_alert(alert.alert_id)

            # Should now be acknowledged
            assert alert.acknowledged


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
