"""
Enhanced Runtime Integration Example
[2026-04-11]

Demonstrates integration between Enhanced Sovereign Runtime and existing systems:
- Triumvirate (Galahad, Cerberus, CodexDeus)
- STATE_REGISTER
- Temporal Workflows
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from governance.sovereign_runtime_enhanced import (
    CapabilityScope,
    EnhancedSovereignRuntime,
    RateLimitConfig,
)


def example_triumvirate_integration():
    """
    Example: Integrate with Triumvirate for high-stakes decisions
    """
    print("\n" + "="*80)
    print("TRIUMVIRATE INTEGRATION EXAMPLE")
    print("="*80)
    
    with TemporaryDirectory() as tmpdir:
        runtime = EnhancedSovereignRuntime(Path(tmpdir))
        
        # Simulated Triumvirate consensus function
        def triumvirate_consensus(policy_id: str, context: dict, initial_decision: dict) -> dict:
            """
            Simulates Triumvirate (Galahad, Cerberus, CodexDeus) consensus.
            
            In production, this would:
            1. Send decision to Galahad for reasoning
            2. Consult Cerberus for security policy
            3. Get CodexDeus ML inference
            4. Compute consensus
            """
            high_stakes = context.get("high_stakes", False)
            risk_level = context.get("risk_level", "low")
            
            if high_stakes and risk_level in ["high", "critical"]:
                print(f"\n  [Triumvirate] High-stakes decision detected!")
                print(f"  [Galahad] Analyzing reasoning...")
                print(f"  [Cerberus] Checking security policy...")
                print(f"  [CodexDeus] Running ML inference...")
                
                # Simulate unanimous agreement required
                galahad_vote = context.get("galahad_approve", False)
                cerberus_vote = context.get("cerberus_approve", False)
                codex_vote = context.get("codex_approve", False)
                
                all_approve = galahad_vote and cerberus_vote and codex_vote
                
                if not all_approve:
                    print(f"  [Triumvirate] CONSENSUS: Requires unanimous approval")
                    return {
                        "override": True,
                        "allowed": False,
                        "reason": "Triumvirate consensus not reached - requires unanimous approval for high-stakes operations"
                    }
                else:
                    print(f"  [Triumvirate] CONSENSUS: Unanimous approval granted")
                    return {
                        "override": True,
                        "allowed": True,
                        "reason": "Triumvirate consensus reached - operation approved"
                    }
            
            return {"override": False}
        
        # Register callback
        runtime.register_triumvirate_callback(triumvirate_consensus)
        
        # Compile policy
        policy_def = {
            "rules": [
                {
                    "condition": "context.get('user_role') == 'admin'",
                    "allow": True,
                    "reason": "Admin access"
                }
            ],
            "default": {"allowed": False, "reason": "Unauthorized"}
        }
        runtime.compile_policy("critical_operation", policy_def)
        
        # Test 1: Normal operation (no override)
        print("\n[Test 1] Normal operation - no Triumvirate override")
        allowed, reason, metadata = runtime.enforce_policy(
            "critical_operation",
            {"user_role": "admin", "high_stakes": False}
        )
        print(f"  Result: {allowed}")
        print(f"  Reason: {reason}\n")
        
        # Test 2: High-stakes operation - no consensus
        print("\n[Test 2] High-stakes operation - Triumvirate blocks")
        allowed, reason, metadata = runtime.enforce_policy(
            "critical_operation",
            {
                "user_role": "admin",
                "high_stakes": True,
                "risk_level": "critical",
                "galahad_approve": True,
                "cerberus_approve": False,  # Cerberus blocks
                "codex_approve": True
            },
            triumvirate_override=True
        )
        print(f"  Result: {allowed}")
        print(f"  Reason: {reason}\n")
        
        # Test 3: High-stakes operation - unanimous approval
        print("\n[Test 3] High-stakes operation - Triumvirate approves")
        allowed, reason, metadata = runtime.enforce_policy(
            "critical_operation",
            {
                "user_role": "admin",
                "high_stakes": True,
                "risk_level": "critical",
                "galahad_approve": True,
                "cerberus_approve": True,
                "codex_approve": True
            },
            triumvirate_override=True
        )
        print(f"  Result: {allowed}")
        print(f"  Reason: {reason}\n")


def example_state_register_integration():
    """
    Example: Track policy decisions in STATE_REGISTER
    """
    print("\n" + "="*80)
    print("STATE_REGISTER INTEGRATION EXAMPLE")
    print("="*80)
    
    with TemporaryDirectory() as tmpdir:
        runtime = EnhancedSovereignRuntime(Path(tmpdir))
        
        # Compile policies
        access_policy = {
            "rules": [
                {
                    "condition": "context.get('clearance_level', 0) >= 5",
                    "allow": True,
                    "reason": "Sufficient clearance"
                }
            ],
            "default": {"allowed": False, "reason": "Insufficient clearance"}
        }
        runtime.compile_policy("data_access", access_policy)
        
        # Execute several decisions
        print("\n[Scenario] Multiple users accessing classified data")
        
        users = [
            {"name": "alice", "clearance_level": 8},
            {"name": "bob", "clearance_level": 3},
            {"name": "charlie", "clearance_level": 6},
        ]
        
        for user in users:
            allowed, reason, metadata = runtime.enforce_policy(
                "data_access",
                user
            )
            print(f"  User {user['name']}: {'ALLOWED' if allowed else 'DENIED'} ({reason})")
        
        # Check STATE_REGISTER
        print("\n[STATE_REGISTER] Current state:")
        state = runtime.state_register.get("data_access")
        if state:
            print(f"  Last decision: {state['last_decision']}")
            print(f"  Timestamp: {state['timestamp']}")
            print(f"  Context hash: {state['context_hash'][:16]}...")
        
        # Export state
        summary = runtime.get_state_summary()
        print(f"\n[Summary]")
        print(f"  Total capabilities issued: {summary['capabilities']['total']}")
        print(f"  Policies compiled: {summary['policies']['total_policies']}")
        print(f"  Proofs generated: {summary['proofs']['total']}")
        print(f"  STATE_REGISTER entries: {summary['state_register']['entries']}")


def example_capability_workflow():
    """
    Example: Complete capability-based workflow
    """
    print("\n" + "="*80)
    print("CAPABILITY WORKFLOW EXAMPLE")
    print("="*80)
    
    with TemporaryDirectory() as tmpdir:
        runtime = EnhancedSovereignRuntime(Path(tmpdir))
        
        print("\n[Scenario] API access control with capabilities")
        
        # Issue API access capability
        print("\n1. Admin issues API capability to client")
        api_token = runtime.create_rate_limited_capability(
            issuer="api_admin",
            subject="client_app_123",
            action="api:call",
            max_calls=1000,
            window_seconds=3600,  # 1 hour
            ttl_days=30
        )
        print(f"   Token ID: {api_token.token_id}")
        print(f"   Rate limit: 1000 calls/hour")
        print(f"   Valid until: {api_token.expires_at.strftime('%Y-%m-%d')}")
        
        # Client uses capability
        print("\n2. Client makes API calls")
        for i in range(5):
            valid, reason = runtime.check_capability(api_token.token_id)
            if valid:
                success, msg = runtime.use_capability(api_token.token_id)
                print(f"   Call #{i+1}: {msg}")
        
        # Create business-hours-only capability
        print("\n3. Admin issues business-hours capability to employee")
        bh_token = runtime.create_business_hours_capability(
            issuer="hr_system",
            subject="employee_dave",
            action="access:office_systems",
            ttl_days=90
        )
        print(f"   Token ID: {bh_token.token_id}")
        print(f"   Constraints: Business hours only (9-5, Mon-Fri)")
        
        # Check capability
        valid, reason = runtime.check_capability(
            bh_token.token_id,
            context={"in_business_hours": False}
        )
        print(f"   Current validity: {valid} ({reason})")
        
        # Delegation example
        print("\n4. Team lead delegates approval capability")
        approval_token = runtime.issue_capability(
            issuer="management",
            subject="team_lead",
            action="approve:expenses",
            scope=CapabilityScope.RESOURCE,
            scope_value="expense_system",
            ttl_seconds=86400 * 7,  # 1 week
            can_delegate=True,
            max_delegation_depth=1
        )
        
        delegated = approval_token.delegate("team_member")
        if delegated:
            runtime.capability_registry.register(delegated)
            print(f"   Delegated to: {delegated.subject}")
            print(f"   Delegation depth: {delegated.delegation_depth}")
            print(f"   Original issuer: {approval_token.subject}")


def example_policy_compilation_performance():
    """
    Example: Policy compilation performance comparison
    """
    print("\n" + "="*80)
    print("POLICY COMPILATION PERFORMANCE EXAMPLE")
    print("="*80)
    
    import time
    
    with TemporaryDirectory() as tmpdir:
        runtime = EnhancedSovereignRuntime(Path(tmpdir))
        
        # Create complex policy with many rules
        print("\n[Scenario] Complex authorization policy with 50 rules")
        
        policy_def = {
            "rules": [
                {
                    "condition": f"context.get('department') == 'dept_{i}' and context.get('role') == 'admin'",
                    "allow": True,
                    "reason": f"Department {i} admin access"
                }
                for i in range(50)
            ],
            "default": {"allowed": False, "reason": "No matching rule"}
        }
        
        # Compile policy
        print("\n1. Compiling policy...")
        start = time.time()
        runtime.compile_policy("complex_auth", policy_def)
        compile_time = time.time() - start
        print(f"   Compilation time: {compile_time*1000:.2f}ms")
        
        # Execute many times
        print("\n2. Executing policy 1000 times...")
        start = time.time()
        for i in range(1000):
            dept = i % 50
            runtime.evaluate_policy(
                "complex_auth",
                {"department": f"dept_{dept}", "role": "admin"},
                generate_proof=False
            )
        exec_time = time.time() - start
        avg_time = exec_time / 1000
        print(f"   Total time: {exec_time*1000:.2f}ms")
        print(f"   Average per execution: {avg_time*1000:.3f}ms")
        
        # Get statistics
        stats = runtime.policy_compiler.get_stats()
        for policy_stat in stats["policy_stats"]:
            if policy_stat["policy_id"] == "complex_auth":
                print(f"\n3. Policy statistics:")
                print(f"   Total executions: {policy_stat['execution_count']}")
                print(f"   Total execution time: {policy_stat['total_execution_time']*1000:.2f}ms")
                print(f"   Average execution time: {policy_stat['average_execution_time']*1000:.3f}ms")


def main():
    """Run all integration examples"""
    print("\n" + "="*80)
    print("ENHANCED SOVEREIGN RUNTIME - INTEGRATION EXAMPLES")
    print("="*80)
    
    try:
        example_triumvirate_integration()
        example_state_register_integration()
        example_capability_workflow()
        example_policy_compilation_performance()
        
        print("\n" + "="*80)
        print("ALL INTEGRATION EXAMPLES COMPLETE")
        print("="*80)
        print("\nKey Integrations Demonstrated:")
        print("  • Triumvirate consensus for high-stakes decisions")
        print("  • STATE_REGISTER for decision tracking")
        print("  • Capability-based access control workflows")
        print("  • High-performance policy compilation")
        print("\n")
        
    except Exception as e:
        print(f"\nError during integration examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
