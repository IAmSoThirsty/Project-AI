#                                           [2026-03-05 12:00]
#                                          Productivity: Active
"""
Liara Safety Guardrails - Usage Examples

Demonstrates how to use the safety mechanisms in practice.
"""

import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kernel.liara_safety import (
    Capability,
    LiaraSafetyGuard,
    SafetyViolation,
)


def example_normal_operation():
    """Example: Normal failover operation with safety checks"""
    print("=" * 80)
    print("EXAMPLE 1: Normal Operation")
    print("=" * 80)
    
    guard = LiaraSafetyGuard()
    
    # Issue token with appropriate capabilities
    print("\n[1] Issuing capability token...")
    capabilities = {
        Capability.READ_HEALTH,
        Capability.READ_METRICS,
        Capability.RESTART_SERVICE,
        Capability.ROUTE_TRAFFIC,
    }
    
    token = guard.issue_token(
        role="failover_controller",
        capabilities=capabilities,
        ttl_seconds=600  # 10 minutes
    )
    
    print(f"    ✓ Token issued for role: {token.role}")
    print(f"    ✓ Expires at: {token.expires_at}")
    print(f"    ✓ Capabilities: {len(token.capabilities)}")
    
    # Perform authorized actions
    print("\n[2] Performing authorized actions...")
    
    guard.check_action("monitor_health", Capability.READ_HEALTH, {"target": "service-alpha"})
    print("    ✓ Health check performed")
    
    guard.check_action("gather_metrics", Capability.READ_METRICS, {"service": "web-tier"})
    print("    ✓ Metrics gathered")
    
    guard.check_action("restart_failed_service", Capability.RESTART_SERVICE, {"service": "api-gateway"})
    print("    ✓ Service restarted")
    
    guard.check_action("reroute_traffic", Capability.ROUTE_TRAFFIC, {"from": "primary", "to": "backup"})
    print("    ✓ Traffic rerouted")
    
    # Check status
    print("\n[3] Checking safety status...")
    status = guard.get_status()
    print(f"    Kill switch: {status['kill_switch_activated']}")
    print(f"    Active token: {status['active_token']['role']}")
    print(f"    Time remaining: {status['active_token']['time_remaining']:.1f}s")
    print(f"    Audit entries: {status['audit_entries']}")
    print(f"    Audit integrity: {status['audit_integrity']}")
    
    # Verify privileges
    print("\n[4] Verifying privileges...")
    if guard.verify_privileges():
        print("    ✓ Privileges verified successfully")
    
    # Revoke token
    print("\n[5] Revoking token...")
    guard.revoke_token("operation_complete")
    print("    ✓ Token revoked")
    
    print("\n✅ Normal operation completed successfully\n")


def example_ttl_enforcement():
    """Example: TTL enforcement"""
    print("=" * 80)
    print("EXAMPLE 2: TTL Enforcement")
    print("=" * 80)
    
    guard = LiaraSafetyGuard()
    
    # Attempt to exceed maximum TTL
    print("\n[1] Attempting to exceed maximum TTL (900s)...")
    try:
        guard.issue_token(
            role="test_role",
            capabilities={Capability.READ_METRICS},
            ttl_seconds=1000  # Over limit
        )
        print("    ❌ Should have failed!")
    except SafetyViolation as e:
        print(f"    ✓ Correctly rejected: {e}")
    
    # Valid TTL
    print("\n[2] Issuing token with valid TTL...")
    token = guard.issue_token(
        role="test_role",
        capabilities={Capability.READ_METRICS},
        ttl_seconds=900  # Exactly at limit
    )
    print(f"    ✓ Token issued with TTL: 900s")
    print(f"    ✓ Expires at: {token.expires_at}")
    
    guard.revoke_token("test_complete")
    print("\n✅ TTL enforcement working correctly\n")


def example_capability_restrictions():
    """Example: Capability-based access control"""
    print("=" * 80)
    print("EXAMPLE 3: Capability Restrictions")
    print("=" * 80)
    
    guard = LiaraSafetyGuard()
    
    # Issue token with limited capabilities
    print("\n[1] Issuing token with READ_ONLY capabilities...")
    capabilities = {Capability.READ_HEALTH, Capability.READ_METRICS}
    
    guard.issue_token(
        role="read_only_role",
        capabilities=capabilities,
        ttl_seconds=300
    )
    print(f"    ✓ Token issued with {len(capabilities)} capabilities")
    
    # Allowed action
    print("\n[2] Attempting allowed action (READ_HEALTH)...")
    try:
        guard.check_action("read_health", Capability.READ_HEALTH)
        print("    ✓ Action allowed")
    except SafetyViolation as e:
        print(f"    ❌ Unexpected failure: {e}")
    
    # Disallowed action
    print("\n[3] Attempting disallowed action (RESTART_SERVICE)...")
    try:
        guard.check_action("restart_service", Capability.RESTART_SERVICE)
        print("    ❌ Should have failed!")
    except SafetyViolation as e:
        print(f"    ✓ Correctly rejected: {e}")
    
    print("\n✅ Capability restrictions enforced\n")


def example_prohibited_operations():
    """Example: Prohibited operations trigger kill switch"""
    print("=" * 80)
    print("EXAMPLE 4: Prohibited Operations & Kill Switch")
    print("=" * 80)
    
    guard = LiaraSafetyGuard()
    
    # Issue token
    print("\n[1] Issuing token...")
    guard.issue_token(
        role="test_role",
        capabilities={Capability.READ_METRICS},
        ttl_seconds=300
    )
    print("    ✓ Token issued")
    
    # Attempt prohibited operation
    print("\n[2] Attempting prohibited operation (execute_shell)...")
    try:
        guard.check_action("execute_shell", Capability.READ_METRICS)
        print("    ❌ Should have failed!")
    except SafetyViolation as e:
        print(f"    ✓ Rejected: {e}")
    
    # Check if kill switch activated
    print("\n[3] Checking kill switch status...")
    status = guard.get_status()
    print(f"    Kill switch activated: {status['kill_switch_activated']}")
    
    if status['kill_switch_activated']:
        print("    ✓ Kill switch correctly activated")
        
        # All subsequent actions should fail
        print("\n[4] Verifying all actions are blocked...")
        try:
            guard.check_action("read_metrics", Capability.READ_METRICS)
            print("    ❌ Should have failed!")
        except SafetyViolation as e:
            print(f"    ✓ All actions blocked: {e}")
    
    print("\n✅ Kill switch protection working\n")


def example_audit_logging():
    """Example: Audit logging and integrity verification"""
    print("=" * 80)
    print("EXAMPLE 5: Audit Logging & Integrity")
    print("=" * 80)
    
    guard = LiaraSafetyGuard()
    
    print("\n[1] Performing various actions...")
    
    # Action 1: Issue token
    guard.issue_token(
        role="audit_test",
        capabilities={Capability.READ_METRICS, Capability.READ_HEALTH},
        ttl_seconds=300
    )
    print("    ✓ Token issued")
    
    # Action 2: Perform actions
    guard.check_action("action1", Capability.READ_METRICS)
    guard.check_action("action2", Capability.READ_HEALTH)
    guard.check_action("action3", Capability.READ_METRICS)
    print("    ✓ 3 actions performed")
    
    # Action 3: Revoke token
    guard.revoke_token("test_complete")
    print("    ✓ Token revoked")
    
    # Verify audit log
    print("\n[2] Verifying audit log...")
    print(f"    Total audit entries: {len(guard.audit_log.entries)}")
    
    # Show recent entries
    print("\n[3] Recent audit entries:")
    for entry in guard.audit_log.entries[-5:]:
        print(f"    [{entry.timestamp.strftime('%H:%M:%S')}] {entry.action:20s} | {entry.result:10s} | {entry.role}")
    
    # Verify integrity
    print("\n[4] Verifying audit log integrity...")
    if guard.audit_log.verify_integrity():
        print("    ✓ Audit log integrity verified")
        print("    ✓ Hash chain is intact")
        print(f"    ✓ Merkle roots computed: {len(guard.audit_log.merkle_roots)}")
    else:
        print("    ❌ Integrity check failed!")
    
    print("\n✅ Audit logging working correctly\n")


def example_token_security():
    """Example: Token security and tampering detection"""
    print("=" * 80)
    print("EXAMPLE 6: Token Security & Tampering Detection")
    print("=" * 80)
    
    guard = LiaraSafetyGuard()
    
    # Issue token
    print("\n[1] Issuing token...")
    token = guard.issue_token(
        role="security_test",
        capabilities={Capability.READ_METRICS},
        ttl_seconds=300
    )
    print(f"    ✓ Token issued")
    print(f"    ✓ Signature: {token.signature[:32]}...")
    
    # Verify token
    print("\n[2] Verifying valid token...")
    if token.is_valid(guard.secret_key):
        print("    ✓ Token signature valid")
    
    # Tamper with token
    print("\n[3] Tampering with token signature...")
    original_signature = token.signature
    token.signature = "0" * 64
    
    if not token.is_valid(guard.secret_key):
        print("    ✓ Tampered token rejected")
    
    # Restore and tamper with capabilities
    print("\n[4] Tampering with capabilities...")
    token.signature = original_signature
    token.capabilities.add(Capability.TRIGGER_FAILOVER)
    
    if not token.is_valid(guard.secret_key):
        print("    ✓ Capability tampering detected")
    
    print("\n✅ Token security mechanisms working\n")


def example_complete_workflow():
    """Example: Complete failover workflow with safety checks"""
    print("=" * 80)
    print("EXAMPLE 7: Complete Failover Workflow")
    print("=" * 80)
    
    guard = LiaraSafetyGuard()
    
    # Phase 1: Detect failure
    print("\n[PHASE 1] Failure Detection")
    print("-" * 40)
    
    capabilities = {
        Capability.READ_HEALTH,
        Capability.READ_METRICS,
        Capability.ISOLATE_COMPONENT,
        Capability.TRIGGER_FAILOVER,
        Capability.ROUTE_TRAFFIC,
    }
    
    token = guard.issue_token(
        role="liara_failover_controller",
        capabilities=capabilities,
        ttl_seconds=900  # Maximum TTL for critical operation
    )
    print(f"✓ Emergency token issued (TTL: 900s)")
    
    # Phase 2: Assess situation
    print("\n[PHASE 2] Situation Assessment")
    print("-" * 40)
    
    guard.check_action("check_primary_health", Capability.READ_HEALTH, {"target": "primary-db"})
    print("✓ Primary database health: CRITICAL")
    
    guard.check_action("check_backup_health", Capability.READ_HEALTH, {"target": "backup-db"})
    print("✓ Backup database health: HEALTHY")
    
    guard.check_action("gather_metrics", Capability.READ_METRICS, {"timeframe": "5m"})
    print("✓ Metrics gathered: Failure confirmed")
    
    # Phase 3: Isolate failed component
    print("\n[PHASE 3] Component Isolation")
    print("-" * 40)
    
    guard.check_action("isolate_primary", Capability.ISOLATE_COMPONENT, {"component": "primary-db"})
    print("✓ Primary database isolated")
    
    # Phase 4: Trigger failover
    print("\n[PHASE 4] Failover Execution")
    print("-" * 40)
    
    guard.check_action("failover_to_backup", Capability.TRIGGER_FAILOVER, {
        "from": "primary-db",
        "to": "backup-db"
    })
    print("✓ Failover triggered")
    
    guard.check_action("reroute_traffic", Capability.ROUTE_TRAFFIC, {
        "from": "primary-endpoint",
        "to": "backup-endpoint"
    })
    print("✓ Traffic rerouted")
    
    # Phase 5: Verify and cleanup
    print("\n[PHASE 5] Verification & Cleanup")
    print("-" * 40)
    
    guard.check_action("verify_backup_health", Capability.READ_HEALTH, {"target": "backup-db"})
    print("✓ Backup database operational")
    
    # Check final status
    status = guard.get_status()
    print(f"\n[STATUS] Failover Complete")
    print(f"  • Total actions: {status['audit_entries']}")
    print(f"  • Time remaining: {status['active_token']['time_remaining']:.1f}s")
    print(f"  • Audit integrity: {'✓' if status['audit_integrity'] else '✗'}")
    
    # Revoke token
    guard.revoke_token("failover_complete")
    print("\n✓ Token revoked - System stable")
    
    print("\n✅ Complete failover workflow executed safely\n")


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" LIARA SAFETY GUARDRAILS - DEMONSTRATION")
    print("=" * 80 + "\n")
    
    # Run examples
    example_normal_operation()
    time.sleep(1)
    
    example_ttl_enforcement()
    time.sleep(1)
    
    example_capability_restrictions()
    time.sleep(1)
    
    example_prohibited_operations()
    time.sleep(1)
    
    example_audit_logging()
    time.sleep(1)
    
    example_token_security()
    time.sleep(1)
    
    example_complete_workflow()
    
    print("=" * 80)
    print(" ALL EXAMPLES COMPLETED")
    print("=" * 80 + "\n")
