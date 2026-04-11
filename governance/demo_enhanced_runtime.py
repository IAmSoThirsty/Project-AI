#!/usr/bin/env python3
"""
Enhanced Sovereign Runtime Demo
[2026-03-05]

Demonstrates the enhanced sovereign runtime capabilities:
1. Capability-based security with fine-grained controls
2. Time-based constraints and rate limiting
3. JIT policy compilation for performance
4. Cryptographic proofs for all decisions
5. Integration with STATE_REGISTER and Triumvirate
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

from governance.sovereign_runtime_enhanced import (
    CapabilityConstraint,
    CapabilityScope,
    EnhancedSovereignRuntime,
    RateLimitConfig,
    TimeWindow,
)

# Fix Unicode output on Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def print_section(title: str):
    """Print section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print('=' * 80)


def demo_capability_system():
    """Demonstrate capability-based security"""
    print_section("1. Capability-Based Security")
    
    with TemporaryDirectory() as tmpdir:
        runtime = EnhancedSovereignRuntime(Path(tmpdir))
        
        # Issue a basic capability
        print("\n[1.1] Issuing basic capability token...")
        token = runtime.issue_capability(
            issuer="admin",
            subject="employee_alice",
            action="read:customer_data",
            scope=CapabilityScope.SERVICE,
            scope_value="customer_service_api",
            ttl_seconds=3600,  # 1 hour
            max_uses=100
        )
        
        print(f"  ✓ Issued token: {token.token_id}")
        print(f"  ✓ Subject: {token.subject}")
        print(f"  ✓ Action: {token.action}")
        print(f"  ✓ Scope: {token.scope.value} ({token.scope_value})")
        print(f"  ✓ Expires: {token.expires_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Check capability
        print("\n[1.2] Checking capability validity...")
        valid, reason = runtime.check_capability(token.token_id)
        print(f"  ✓ Valid: {valid}")
        print(f"  ✓ Reason: {reason}")
        
        # Use capability
        print("\n[1.3] Using capability...")
        for i in range(3):
            success, reason = runtime.use_capability(token.token_id)
            print(f"  ✓ Use #{i+1}: {success} - {reason}")
        
        # Capability with constraints
        print("\n[1.4] Issuing capability with time constraint...")
        now = datetime.now(timezone.utc)
        time_constraint = CapabilityConstraint(
            constraint_type="time_window",
            parameters={
                "start": now.isoformat(),
                "end": (now + timedelta(hours=2)).isoformat()
            }
        )
        
        constrained_token = runtime.issue_capability(
            issuer="admin",
            subject="contractor_bob",
            action="deploy:code",
            scope=CapabilityScope.OPERATION,
            scope_value="production_deploy",
            ttl_seconds=7200,
            constraints=[time_constraint]
        )
        
        print(f"  ✓ Issued constrained token: {constrained_token.token_id}")
        print(f"  ✓ Constraints: {len(constrained_token.constraints)}")
        
        # Delegation
        print("\n[1.5] Testing capability delegation...")
        delegatable_token = runtime.issue_capability(
            issuer="admin",
            subject="team_lead",
            action="approve:expenses",
            scope=CapabilityScope.RESOURCE,
            scope_value="finance_system",
            ttl_seconds=86400,
            can_delegate=True,
            max_delegation_depth=2
        )
        
        delegated = delegatable_token.delegate("team_member")
        if delegated:
            print(f"  ✓ Delegated to: {delegated.subject}")
            print(f"  ✓ Delegation depth: {delegated.delegation_depth}")
            runtime.capability_registry.register(delegated)


def demo_time_constraints():
    """Demonstrate time-based constraints"""
    print_section("2. Time-Based Constraints")
    
    with TemporaryDirectory() as tmpdir:
        runtime = EnhancedSovereignRuntime(Path(tmpdir))
        
        # Business hours configuration
        print("\n[2.1] Configuring business hours...")
        business_hours = TimeWindow(
            start_hour=9,
            end_hour=17,
            days_of_week=[0, 1, 2, 3, 4],  # Monday-Friday
            timezone_name="UTC"
        )
        runtime.time_engine.set_business_hours(business_hours)
        print(f"  ✓ Business hours: 9:00-17:00 (Monday-Friday)")
        
        # Check current time
        is_business = runtime.time_engine.is_business_hours()
        print(f"  ✓ Currently business hours: {is_business}")
        
        # Rate limiting
        print("\n[2.2] Configuring rate limits...")
        rate_config = RateLimitConfig(
            max_calls=10,
            window_seconds=60
        )
        runtime.time_engine.register_rate_limit("api_calls", rate_config)
        print(f"  ✓ Rate limit: {rate_config.max_calls} calls per {rate_config.window_seconds}s")
        
        # Test rate limiting
        print("\n[2.3] Testing rate limiting...")
        for i in range(12):
            allowed, info = runtime.time_engine.check_rate_limit("api_calls", "user1")
            status = "✓" if allowed else "✗"
            print(f"  {status} Call #{i+1}: {info.get('allowed', False)}")
            if not allowed:
                print(f"      Retry after: {info.get('retry_after', 0):.2f}s")
        
        # Temporal policy
        print("\n[2.4] Registering temporal policy...")
        now = datetime.now(timezone.utc)
        temporal_policy = {
            "allowed_windows": [
                {
                    "start_hour": 9,
                    "end_hour": 17,
                    "days_of_week": [0, 1, 2, 3, 4],
                    "timezone_name": "UTC"
                }
            ],
            "blackout_periods": [
                {
                    "start": (now + timedelta(days=7)).isoformat(),
                    "end": (now + timedelta(days=8)).isoformat(),
                    "reason": "Scheduled maintenance"
                }
            ]
        }
        runtime.time_engine.register_temporal_policy("maintenance_policy", temporal_policy)
        print("  ✓ Temporal policy registered")
        
        valid, reason = runtime.time_engine.evaluate_temporal_policy("maintenance_policy", {})
        print(f"  ✓ Policy evaluation: {valid} - {reason}")


def demo_policy_compilation():
    """Demonstrate JIT policy compilation"""
    print_section("3. Dynamic Policy Compilation (JIT)")
    
    with TemporaryDirectory() as tmpdir:
        runtime = EnhancedSovereignRuntime(Path(tmpdir))
        
        # Define a complex policy
        print("\n[3.1] Defining and compiling policy...")
        policy_def = {
            "rules": [
                {
                    "condition": "context.get('emergency', False)",
                    "allow": True,
                    "reason": "Emergency override activated",
                    "metadata": {"priority": "high"}
                },
                {
                    "condition": "context.get('user_role') == 'admin'",
                    "allow": True,
                    "reason": "Admin access granted",
                    "metadata": {"auth_level": "admin"}
                },
                {
                    "condition": "context.get('user_role') == 'manager' and context.get('department') == 'finance'",
                    "allow": True,
                    "reason": "Finance manager access",
                    "metadata": {"auth_level": "manager"}
                },
                {
                    "condition": "context.get('user_role') == 'user' and context.get('has_permission', False)",
                    "allow": True,
                    "reason": "User with explicit permission",
                    "metadata": {"auth_level": "user"}
                }
            ],
            "default": {
                "allowed": False,
                "reason": "Access denied - no matching rule"
            }
        }
        
        success = runtime.compile_policy("access_control_policy", policy_def)
        print(f"  ✓ Policy compiled: {success}")
        print(f"  ✓ Rules: {len(policy_def['rules'])}")
        
        # Test policy with different contexts
        print("\n[3.2] Evaluating policy with different contexts...")
        
        test_contexts = [
            {"emergency": True, "user_role": "guest"},
            {"user_role": "admin"},
            {"user_role": "manager", "department": "finance"},
            {"user_role": "manager", "department": "engineering"},
            {"user_role": "user", "has_permission": True},
            {"user_role": "user", "has_permission": False},
        ]
        
        for ctx in test_contexts:
            allowed, reason, metadata = runtime.evaluate_policy(
                "access_control_policy",
                ctx,
                generate_proof=False
            )
            status = "✓ ALLOW" if allowed else "✗ DENY"
            print(f"  {status}: {ctx}")
            print(f"         Reason: {reason}")
        
        # Performance stats
        print("\n[3.3] Policy execution statistics...")
        stats = runtime.policy_compiler.get_stats()
        for policy_stat in stats["policy_stats"]:
            if policy_stat["policy_id"] == "access_control_policy":
                print(f"  ✓ Executions: {policy_stat['execution_count']}")
                print(f"  ✓ Avg time: {policy_stat['average_execution_time']*1000:.3f}ms")


def demo_cryptographic_proofs():
    """Demonstrate cryptographic proof generation"""
    print_section("4. Cryptographic Proofs")
    
    with TemporaryDirectory() as tmpdir:
        runtime = EnhancedSovereignRuntime(Path(tmpdir))
        
        # Compile a policy
        print("\n[4.1] Compiling policy with proof generation...")
        policy_def = {
            "rules": [
                {
                    "condition": "context.get('security_level', 0) >= 5",
                    "allow": True,
                    "reason": "Security level sufficient"
                }
            ],
            "default": {"allowed": False, "reason": "Insufficient security level"}
        }
        runtime.compile_policy("security_policy", policy_def)
        
        # Evaluate with proof generation
        print("\n[4.2] Evaluating policy with proof generation...")
        contexts = [
            {"security_level": 10, "user": "alice", "action": "read_classified"},
            {"security_level": 3, "user": "bob", "action": "read_classified"},
        ]
        
        proofs = []
        for ctx in contexts:
            allowed, reason, metadata = runtime.evaluate_policy(
                "security_policy",
                ctx,
                generate_proof=True
            )
            
            proof_id = metadata.get("proof_id")
            status = "✓ ALLOW" if allowed else "✗ DENY"
            print(f"  {status}: {ctx}")
            print(f"         Proof ID: {proof_id}")
            proofs.append(proof_id)
        
        # Verify proofs
        print("\n[4.3] Verifying cryptographic proofs...")
        for proof_id in proofs:
            proof = runtime.proof_generator.proofs.get(proof_id)
            if proof:
                is_valid = runtime.proof_generator.verify_proof(proof)
                status = "✓" if is_valid else "✗"
                print(f"  {status} Proof {proof_id}: Valid={is_valid}")
                print(f"      Decision: {proof.decision_type}")
                print(f"      Signature: {proof.signature[:32]}...")
        
        # Export proofs
        print("\n[4.4] Exporting proofs...")
        proof_path = Path(tmpdir) / "proofs.json"
        runtime.proof_generator.export_proofs(proof_path)
        print(f"  ✓ Exported {len(proofs)} proofs to {proof_path}")


def demo_integration():
    """Demonstrate STATE_REGISTER and Triumvirate integration"""
    print_section("5. Integration (STATE_REGISTER & Triumvirate)")
    
    with TemporaryDirectory() as tmpdir:
        runtime = EnhancedSovereignRuntime(Path(tmpdir))
        
        # Register Triumvirate callback
        print("\n[5.1] Registering Triumvirate callback...")
        
        def triumvirate_callback(policy_id, context, decision):
            """Mock Triumvirate callback for high-stakes decisions"""
            print(f"      [Triumvirate] Reviewing policy: {policy_id}")
            print(f"      [Triumvirate] Context: {context}")
            print(f"      [Triumvirate] Initial decision: {decision['allowed']}")
            
            # Simulate consensus check
            if context.get("high_stakes", False):
                print("      [Triumvirate] HIGH STAKES - Requiring override")
                return {
                    "override": True,
                    "allowed": False,
                    "reason": "Triumvirate requires additional approval for high-stakes operations"
                }
            
            return {"override": False}
        
        runtime.register_triumvirate_callback(triumvirate_callback)
        print("  ✓ Triumvirate callback registered")
        
        # Compile policy
        print("\n[5.2] Compiling policy for integration test...")
        policy_def = {
            "rules": [
                {
                    "condition": "context.get('authorized', False)",
                    "allow": True,
                    "reason": "Authorized operation"
                }
            ],
            "default": {"allowed": False, "reason": "Not authorized"}
        }
        runtime.compile_policy("integrated_policy", policy_def)
        
        # Test without Triumvirate override
        print("\n[5.3] Normal enforcement (no override)...")
        allowed, reason, metadata = runtime.enforce_policy(
            "integrated_policy",
            {"authorized": True, "high_stakes": False}
        )
        print(f"  ✓ Decision: {allowed}")
        print(f"  ✓ Reason: {reason}")
        
        # Test with Triumvirate override
        print("\n[5.4] Enforcement with Triumvirate override...")
        allowed, reason, metadata = runtime.enforce_policy(
            "integrated_policy",
            {"authorized": True, "high_stakes": True},
            triumvirate_override=True
        )
        print(f"  ✓ Decision: {allowed}")
        print(f"  ✓ Reason: {reason}")
        print(f"  ✓ Override: {metadata.get('triumvirate_override', False)}")
        
        # Check STATE_REGISTER
        print("\n[5.5] Checking STATE_REGISTER...")
        for policy_id, state in runtime.state_register.items():
            print(f"  ✓ Policy: {policy_id}")
            print(f"      Last decision: {state['last_decision']}")
            print(f"      Timestamp: {state['timestamp']}")
            print(f"      Context hash: {state['context_hash'][:16]}...")


def demo_convenience_features():
    """Demonstrate convenience features"""
    print_section("6. Convenience Features")
    
    with TemporaryDirectory() as tmpdir:
        runtime = EnhancedSovereignRuntime(Path(tmpdir))
        
        # Business hours capability
        print("\n[6.1] Creating business hours capability...")
        bh_token = runtime.create_business_hours_capability(
            issuer="hr_system",
            subject="employee_charlie",
            action="access:office_systems",
            ttl_days=90
        )
        print(f"  ✓ Token ID: {bh_token.token_id}")
        print(f"  ✓ Constraints: {len(bh_token.constraints)}")
        print(f"  ✓ Expires: {bh_token.expires_at.strftime('%Y-%m-%d')}")
        
        # Rate-limited capability
        print("\n[6.2] Creating rate-limited capability...")
        rl_token = runtime.create_rate_limited_capability(
            issuer="api_gateway",
            subject="api_client_123",
            action="api:call",
            max_calls=1000,
            window_seconds=3600,
            ttl_days=30
        )
        print(f"  ✓ Token ID: {rl_token.token_id}")
        print(f"  ✓ Rate limit: 1000 calls/hour")
        print(f"  ✓ Constraints: {len(rl_token.constraints)}")
        
        # State summary
        print("\n[6.3] Getting runtime state summary...")
        summary = runtime.get_state_summary()
        print(f"  ✓ Capabilities: {summary['capabilities']['total']}")
        print(f"  ✓ Policies: {summary['policies']['total_policies']}")
        print(f"  ✓ Proofs: {summary['proofs']['total']}")
        print(f"  ✓ STATE_REGISTER entries: {summary['state_register']['entries']}")
        print(f"  ✓ Audit trail valid: {summary['audit_trail']['valid']}")
        
        # Export compliance bundle
        print("\n[6.4] Exporting compliance bundle...")
        bundle_dir = Path(tmpdir) / "compliance"
        success = runtime.export_full_compliance_bundle(bundle_dir)
        print(f"  ✓ Export success: {success}")
        if success:
            for file in bundle_dir.iterdir():
                print(f"      {file.name}")


def demo_audit_trail():
    """Demonstrate audit trail integrity"""
    print_section("7. Audit Trail & Compliance")
    
    with TemporaryDirectory() as tmpdir:
        runtime = EnhancedSovereignRuntime(Path(tmpdir))
        
        # Generate activity
        print("\n[7.1] Generating audit trail...")
        
        # Issue capabilities
        for i in range(3):
            runtime.issue_capability(
                issuer="admin",
                subject=f"user_{i}",
                action="test_action",
                scope=CapabilityScope.GLOBAL
            )
        
        # Compile and evaluate policies
        policy_def = {
            "rules": [],
            "default": {"allowed": True, "reason": "Test"}
        }
        runtime.compile_policy("audit_test", policy_def)
        
        for i in range(5):
            runtime.evaluate_policy("audit_test", {"iteration": i})
        
        print(f"  ✓ Generated audit events")
        
        # Verify audit trail integrity
        print("\n[7.2] Verifying audit trail integrity...")
        is_valid, issues = runtime.base_runtime.verify_audit_trail_integrity()
        print(f"  ✓ Audit trail valid: {is_valid}")
        if issues:
            print(f"  ✗ Issues found: {issues}")
        else:
            print("  ✓ No integrity issues found")
        
        # Export compliance bundle
        print("\n[7.3] Exporting compliance bundle...")
        bundle_path = Path(tmpdir) / "compliance_bundle.json"
        success = runtime.base_runtime.export_compliance_bundle(bundle_path)
        print(f"  ✓ Export success: {success}")
        
        if success:
            with open(bundle_path) as f:
                bundle = json.load(f)
            print(f"  ✓ Total audit blocks: {bundle['audit_trail']['total_blocks']}")
            print(f"  ✓ Integrity valid: {bundle['integrity_verification']['is_valid']}")


def main():
    """Run all demonstrations"""
    print("\n" + "=" * 80)
    print("  ENHANCED SOVEREIGN RUNTIME DEMONSTRATION")
    print("  Advanced Policy Enforcement with Cryptographic Proofs")
    print("=" * 80)
    
    try:
        demo_capability_system()
        demo_time_constraints()
        demo_policy_compilation()
        demo_cryptographic_proofs()
        demo_integration()
        demo_convenience_features()
        demo_audit_trail()
        
        print_section("DEMONSTRATION COMPLETE")
        print("\n✓ All features demonstrated successfully!")
        print("\nKey Features:")
        print("  • Capability-based security with fine-grained controls")
        print("  • Time-based constraints (business hours, rate limits)")
        print("  • JIT policy compilation for performance")
        print("  • Cryptographic proofs for all decisions")
        print("  • STATE_REGISTER and Triumvirate integration")
        print("  • Immutable audit trail with integrity verification")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
