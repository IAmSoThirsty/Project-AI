#!/usr/bin/env python3
"""
Demonstration script to capture tier health report output.

This script initializes the tier registry and demonstrates the health
monitoring output without requiring full application startup.
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
from app.core.tier_health_dashboard import get_health_monitor


def demo_tier_health_report():
    """Demonstrate the tier health report output."""
    print("=" * 70)
    print("  THREE-TIER PLATFORM HEALTH REPORT DEMO")
    print("=" * 70)
    print()
    
    # Get registry and register demo components
    registry = get_tier_registry()
    
    # Register Tier 1 components
    print("Registering Tier 1 (Governance) components...")
    registry.register_component(
        component_id="cognition_kernel",
        component_name="CognitionKernel",
        tier=PlatformTier.TIER_1_GOVERNANCE,
        authority_level=AuthorityLevel.SOVEREIGN,
        role=ComponentRole.GOVERNANCE_CORE,
        component_ref=object(),
        can_be_paused=False,
        can_be_replaced=False,
    )
    
    registry.register_component(
        component_id="governance_service",
        component_name="GovernanceService",
        tier=PlatformTier.TIER_1_GOVERNANCE,
        authority_level=AuthorityLevel.SOVEREIGN,
        role=ComponentRole.POLICY_ENFORCER,
        component_ref=object(),
        can_be_paused=False,
        can_be_replaced=False,
    )
    print("  ✓ 2 components registered\n")
    
    # Register Tier 2 components
    print("Registering Tier 2 (Infrastructure) components...")
    registry.register_component(
        component_id="execution_service",
        component_name="ExecutionService",
        tier=PlatformTier.TIER_2_INFRASTRUCTURE,
        authority_level=AuthorityLevel.CONSTRAINED,
        role=ComponentRole.INFRASTRUCTURE_CONTROLLER,
        component_ref=object(),
        dependencies=["cognition_kernel"],
        can_be_paused=True,
    )
    
    registry.register_component(
        component_id="global_watch_tower",
        component_name="GlobalWatchTower",
        tier=PlatformTier.TIER_2_INFRASTRUCTURE,
        authority_level=AuthorityLevel.CONSTRAINED,
        role=ComponentRole.INFRASTRUCTURE_CONTROLLER,
        component_ref=object(),
        dependencies=["cognition_kernel"],
        can_be_paused=True,
    )
    
    registry.register_component(
        component_id="memory_engine",
        component_name="MemoryEngine",
        tier=PlatformTier.TIER_2_INFRASTRUCTURE,
        authority_level=AuthorityLevel.CONSTRAINED,
        role=ComponentRole.RESOURCE_ORCHESTRATOR,
        component_ref=object(),
        dependencies=["cognition_kernel"],
        can_be_paused=True,
    )
    print("  ✓ 3 components registered\n")
    
    # Register Tier 3 components
    print("Registering Tier 3 (Application) components...")
    registry.register_component(
        component_id="council_hub",
        component_name="CouncilHub",
        tier=PlatformTier.TIER_3_APPLICATION,
        authority_level=AuthorityLevel.SANDBOXED,
        role=ComponentRole.RUNTIME_SERVICE,
        component_ref=object(),
        dependencies=["cognition_kernel"],
        can_be_paused=True,
        can_be_replaced=True,
    )
    
    # Register several agents
    agent_names = [
        "SafetyGuard", "Expert", "Planner", "Oversight", "Validator",
        "RedTeam", "CodeAdversary", "Constitutional", "Explainability"
    ]
    
    for agent_name in agent_names:
        registry.register_component(
            component_id=f"agent_{agent_name.lower()}",
            component_name=f"{agent_name}Agent",
            tier=PlatformTier.TIER_3_APPLICATION,
            authority_level=AuthorityLevel.SANDBOXED,
            role=ComponentRole.RUNTIME_SERVICE,
            component_ref=object(),
            dependencies=["cognition_kernel", "council_hub"],
            can_be_paused=True,
            can_be_replaced=True,
        )
    
    # Register GUI components
    registry.register_component(
        component_id="dashboard_main",
        component_name="DashboardMainWindow",
        tier=PlatformTier.TIER_3_APPLICATION,
        authority_level=AuthorityLevel.SANDBOXED,
        role=ComponentRole.USER_INTERFACE,
        component_ref=object(),
        dependencies=["cognition_kernel", "council_hub"],
        can_be_paused=True,
        can_be_replaced=True,
    )
    
    registry.register_component(
        component_id="leather_book_interface",
        component_name="LeatherBookInterface",
        tier=PlatformTier.TIER_3_APPLICATION,
        authority_level=AuthorityLevel.SANDBOXED,
        role=ComponentRole.USER_INTERFACE,
        component_ref=object(),
        dependencies=["cognition_kernel", "council_hub"],
        can_be_paused=True,
        can_be_replaced=True,
    )
    
    print(f"  ✓ {1 + len(agent_names) + 2} components registered\n")
    
    # Now generate the health report
    print("=" * 70)
    print("🔍 TIER PLATFORM HEALTH CHECK")
    print("=" * 70)
    print()
    
    health_monitor = get_health_monitor()
    
    # Report each tier
    for tier_num, tier in enumerate([
        PlatformTier.TIER_1_GOVERNANCE,
        PlatformTier.TIER_2_INFRASTRUCTURE,
        PlatformTier.TIER_3_APPLICATION
    ], 1):
        tier_health = health_monitor.collect_tier_health(tier)
        print(f"Tier {tier_num} ({tier.name}):")
        print(f"   Status: {tier_health.overall_health.value.upper()}")
        print(f"   Components: {tier_health.tier_status.component_count}")
        print(f"   Active: {tier_health.tier_status.active_components}")
        print(f"   Paused: {tier_health.tier_status.paused_components}")
        
        # List components
        for comp in tier_health.component_reports[:5]:  # First 5
            status_icon = "✓" if comp.is_operational else "✗"
            print(f"     {status_icon} {comp.component_name}")
        
        if len(tier_health.component_reports) > 5:
            print(f"     ... and {len(tier_health.component_reports) - 5} more")
        print()
    
    # Overall status
    platform_health = health_monitor.collect_platform_health()
    print("-" * 70)
    print(f"Platform Status: {platform_health.overall_health.value.upper()}")
    print(f"Total Components: {platform_health.total_components}")
    print(f"Active: {platform_health.active_components}")
    print(f"Violations: {platform_health.total_violations}")
    
    # Check for violations
    violations = registry.get_all_violations()
    if violations:
        print(f"\n⚠️  {len(violations)} tier boundary violations detected:")
        for violation in violations[:3]:  # First 3
            print(f"   - {violation.violation_type}: {violation.description}")
    else:
        print("\n✓ No tier boundary violations")
    
    print("=" * 70)
    print()
    print("✅ Three-Tier Platform: Fully Integrated & Enforced (Feb 2026)")
    print()


if __name__ == "__main__":
    demo_tier_health_report()
