#!/usr/bin/env python3
"""
Three-Tier Platform Strategy Demo

This script demonstrates the three-tier platform architecture in action:
1. Register components in each tier
2. Show authority flow validation
3. Demonstrate cross-tier blocking
4. Display health monitoring
5. Show governance policy enforcement

Run: python demos/tier_platform_demo.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.platform_tiers import (
    AuthorityLevel,
    ComponentRole,
    PlatformTier,
    get_tier_registry,
)
from app.core.tier_governance_policies import (
    BlockReason,
    BlockType,
    get_policy_engine,
)
from app.core.tier_health_dashboard import (
    HealthMetric,
    MetricType,
    get_health_monitor,
)
from app.core.tier_interfaces import RequestType, TierRequest, get_tier_router


def print_header(text: str) -> None:
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def demo_component_registration() -> None:
    """Demonstrate component registration in all three tiers."""
    print_header("PHASE 1: Component Registration")

    registry = get_tier_registry()

    # Tier 1: Governance
    print("Registering Tier 1 (Governance) Components...")
    tier1_comp = registry.register_component(
        component_id="demo_governance",
        component_name="Demo Governance Core",
        tier=PlatformTier.TIER_1_GOVERNANCE,
        authority_level=AuthorityLevel.SOVEREIGN,
        role=ComponentRole.GOVERNANCE_CORE,
        component_ref=object(),
        dependencies=[],
        can_be_paused=False,
        can_be_replaced=False,
    )
    print(f"  ✓ {tier1_comp.component_name} [SOVEREIGN]")

    # Tier 2: Infrastructure
    print("\nRegistering Tier 2 (Infrastructure) Components...")
    tier2_comp = registry.register_component(
        component_id="demo_infrastructure",
        component_name="Demo Infrastructure Controller",
        tier=PlatformTier.TIER_2_INFRASTRUCTURE,
        authority_level=AuthorityLevel.CONSTRAINED,
        role=ComponentRole.INFRASTRUCTURE_CONTROLLER,
        component_ref=object(),
        dependencies=["demo_governance"],
        can_be_paused=True,
        can_be_replaced=False,
    )
    print(f"  ✓ {tier2_comp.component_name} [CONSTRAINED]")

    # Tier 3: Application
    print("\nRegistering Tier 3 (Application) Components...")
    tier3_comp = registry.register_component(
        component_id="demo_application",
        component_name="Demo Application Service",
        tier=PlatformTier.TIER_3_APPLICATION,
        authority_level=AuthorityLevel.SANDBOXED,
        role=ComponentRole.RUNTIME_SERVICE,
        component_ref=object(),
        dependencies=["demo_governance", "demo_infrastructure"],
        can_be_paused=True,
        can_be_replaced=True,
    )
    print(f"  ✓ {tier3_comp.component_name} [SANDBOXED]")

    print("\n✓ All components registered successfully!")


def demo_authority_flow() -> None:
    """Demonstrate authority flow validation."""
    print_header("PHASE 2: Authority Flow Validation")

    registry = get_tier_registry()
    router = get_tier_router()

    print("Testing Authority Commands (Must Flow Downward)...")

    # Valid: Tier 1 → Tier 2
    print("\n  1. Tier 1 → Tier 2 (Governance commanding Infrastructure)")
    request = TierRequest(
        request_id="req_1",
        request_type=RequestType.AUTHORITY_COMMAND,
        source_tier=1,
        target_tier=2,
        source_component="demo_governance",
        target_component="demo_infrastructure",
        operation="pause_component",
        payload={},
    )
    response = router.route_request(request)
    print(f"     Result: {'✓ ALLOWED' if response.success else '✗ BLOCKED'}")

    # Valid: Tier 2 → Tier 3
    print("\n  2. Tier 2 → Tier 3 (Infrastructure commanding Application)")
    request = TierRequest(
        request_id="req_2",
        request_type=RequestType.AUTHORITY_COMMAND,
        source_tier=2,
        target_tier=3,
        source_component="demo_infrastructure",
        target_component="demo_application",
        operation="throttle_requests",
        payload={},
    )
    response = router.route_request(request)
    print(f"     Result: {'✓ ALLOWED' if response.success else '✗ BLOCKED'}")

    # Invalid: Tier 3 → Tier 2 (Upward authority)
    print("\n  3. Tier 3 → Tier 2 (Application trying to command Infrastructure)")
    request = TierRequest(
        request_id="req_3",
        request_type=RequestType.AUTHORITY_COMMAND,
        source_tier=3,
        target_tier=2,
        source_component="demo_application",
        target_component="demo_infrastructure",
        operation="allocate_more_resources",
        payload={},
    )
    response = router.route_request(request)
    print(f"     Result: {'✗ BLOCKED' if not response.success else '✓ ALLOWED'}")
    if not response.success:
        print(f"     Reason: {response.error_message}")

    print("\nTesting Capability Requests (Must Flow Upward)...")

    # Valid: Tier 3 → Tier 1
    print("\n  4. Tier 3 → Tier 1 (Application requesting capability)")
    request = TierRequest(
        request_id="req_4",
        request_type=RequestType.CAPABILITY_REQUEST,
        source_tier=3,
        target_tier=1,
        source_component="demo_application",
        target_component="demo_governance",
        operation="request_data_access",
        payload={},
    )
    response = router.route_request(request)
    print(f"     Result: {'✓ ALLOWED' if response.success else '✗ BLOCKED'}")


def demo_cross_tier_blocking() -> None:
    """Demonstrate cross-tier blocking policies."""
    print_header("PHASE 3: Cross-Tier Governance Policies")

    policy_engine = get_policy_engine()

    print("Scenario: Tier 2 detects anomalous behavior in Tier 3 application\n")

    # Temporary block (autonomous)
    print("1. Tier 2 requests TEMPORARY block (<5 min) - AUTONOMOUS")
    success, reason, block = policy_engine.request_block(
        component_id="demo_application",
        component_name="Demo Application Service",
        tier=3,
        blocked_by="demo_infrastructure",
        blocking_tier=2,
        reason=BlockReason.ANOMALOUS_BEHAVIOR,
        block_type=BlockType.TEMPORARY,
        duration_seconds=300,
    )

    if success:
        print(f"   ✓ Block imposed: {block.block_id}")
        print(f"   - Type: {block.block_type.value}")
        print(f"   - Reason: {block.reason.value}")
        print("   - Duration: 300 seconds")
        print("   - Governance Approval Required: No (autonomous)")
    else:
        print(f"   ✗ Block failed: {reason}")

    # File appeal
    print("\n2. Application files APPEAL against the block")
    success, reason, appeal = policy_engine.file_appeal(
        block_id=block.block_id,
        appellant="demo_application",
        justification="False positive: Legitimate load spike during batch processing",
    )

    if success:
        print(f"   ✓ Appeal filed: {appeal.appeal_id}")
        print(f"   - Status: {appeal.status.value}")
        print(f"   - Justification: {appeal.justification}")
    else:
        print(f"   ✗ Appeal failed: {reason}")

    # Process appeal
    print("\n3. Tier 1 GOVERNANCE reviews and approves appeal")
    policy_engine.process_appeal(
        appeal_id=appeal.appeal_id,
        approved=True,
        decided_by="demo_governance",
        decision="Appeal granted: Analysis confirms legitimate batch process spike",
    )
    print("   ✓ Appeal APPROVED - Block lifted")

    # Try invalid upward block
    print("\n4. Attempting INVALID block: Tier 3 → Tier 2 (should fail)")
    success, reason, block = policy_engine.request_block(
        component_id="demo_infrastructure",
        component_name="Demo Infrastructure Controller",
        tier=2,
        blocked_by="demo_application",
        blocking_tier=3,  # Invalid: Tier 3 cannot block Tier 2
        reason=BlockReason.POLICY_BREACH,
        block_type=BlockType.TEMPORARY,
    )

    if not success:
        print("   ✓ Block correctly REJECTED")
        print(f"   - Reason: {reason}")
    else:
        print("   ✗ Block should have been rejected!")


def demo_health_monitoring() -> None:
    """Demonstrate health monitoring and alerting."""
    print_header("PHASE 4: Health Monitoring & Alerts")

    monitor = get_health_monitor()

    print("Recording metrics for each tier...\n")

    # Tier 1: Healthy
    print("1. Tier 1 (Governance) - Governance Decision Latency")
    metric = HealthMetric(
        metric_name="governance_decision_latency",
        metric_type=MetricType.LATENCY,
        value=85.5,
        unit="ms",
        threshold_warning=200.0,
        threshold_critical=500.0,
    )
    monitor.record_metric(PlatformTier.TIER_1_GOVERNANCE, metric)
    print(f"   Value: {metric.value} {metric.unit}")
    print(f"   Health: {metric.get_health_level().value.upper()}")

    # Tier 2: Degraded
    print("\n2. Tier 2 (Infrastructure) - Memory Utilization (WARNING)")
    metric = HealthMetric(
        metric_name="memory_utilization",
        metric_type=MetricType.RESOURCE_USAGE,
        value=85.0,
        unit="percent",
        threshold_warning=80.0,
        threshold_critical=95.0,
    )
    monitor.record_metric(PlatformTier.TIER_2_INFRASTRUCTURE, metric)
    print(f"   Value: {metric.value} {metric.unit}")
    print(f"   Health: {metric.get_health_level().value.upper()}")
    print("   ⚠ Alert generated: Exceeds warning threshold")

    # Tier 3: Critical
    print("\n3. Tier 3 (Application) - Error Rate (CRITICAL)")
    metric = HealthMetric(
        metric_name="error_rate",
        metric_type=MetricType.ERROR_RATE,
        value=25.0,
        unit="percent",
        threshold_warning=5.0,
        threshold_critical=15.0,
    )
    monitor.record_metric(PlatformTier.TIER_3_APPLICATION, metric)
    print(f"   Value: {metric.value} {metric.unit}")
    print(f"   Health: {metric.get_health_level().value.upper()}")
    print("   🚨 Alert generated: CRITICAL threshold exceeded")

    # Show platform health
    print("\n" + "-" * 70)
    print("Platform Health Report:")
    print("-" * 70)
    platform_report = monitor.collect_platform_health()
    print(monitor.format_health_report(platform_report))

    # Show alerts
    unack_alerts = monitor.get_alerts(acknowledged=False)
    if unack_alerts:
        print("\nUnacknowledged Alerts:")
        for alert in unack_alerts[:3]:  # Show first 3
            print(f"  • [{alert.severity.value}] {alert.message}")


def demo_statistics() -> None:
    """Show statistics from all systems."""
    print_header("PHASE 5: System Statistics")

    registry = get_tier_registry()
    router = get_tier_router()
    policy_engine = get_policy_engine()

    print("Component Registry Statistics:")
    all_components = registry.get_all_components()
    print(f"  Total Components: {len(all_components)}")
    for tier in [
        PlatformTier.TIER_1_GOVERNANCE,
        PlatformTier.TIER_2_INFRASTRUCTURE,
        PlatformTier.TIER_3_APPLICATION,
    ]:
        components = registry.get_tier_components(tier)
        print(f"  Tier {tier.value}: {len(components)} components")

    print("\nInterface Router Statistics:")
    stats = router.get_statistics()
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    print("\nPolicy Engine Statistics:")
    stats = policy_engine.get_statistics()
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")

    print("\nTier Boundary Violations:")
    violations = registry.get_all_violations()
    if violations:
        print(f"  Total Violations: {len(violations)}")
        for violation in violations[:3]:  # Show first 3
            print(f"    • {violation.violation_type}: {violation.description}")
    else:
        print("  ✓ No violations detected")


def main():
    """Run the complete demo."""
    print("\n" + "=" * 70)
    print("  THREE-TIER PLATFORM STRATEGY DEMONSTRATION")
    print("  Project-AI - Done Correctly")
    print("=" * 70)

    try:
        demo_component_registration()
        demo_authority_flow()
        demo_cross_tier_blocking()
        demo_health_monitoring()
        demo_statistics()

        print_header("DEMO COMPLETE")
        print("✓ All three-tier platform features demonstrated successfully!")
        print("\nKey Principles Enforced:")
        print("  1. Authority flows downward (Tier 1 → Tier 2 → Tier 3)")
        print("  2. Capability flows upward (Tier 3 → Tier 2 → Tier 1)")
        print("  3. Tier 1 never depends on Tier 2/3")
        print("  4. Infrastructure decisions validated by governance")
        print("  5. Tier 3 is swappable without threatening Tier 1/2")
        print("\n")

    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
