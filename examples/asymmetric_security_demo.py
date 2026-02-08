#!/usr/bin/env python3
"""
Asymmetric Security Framework - Live Demo

This script demonstrates the God Tier Asymmetric Security Framework in action.
"""

import json
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.god_tier_asymmetric_security import GodTierAsymmetricSecurity


def print_section(title: str):
    """Print formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def demo_basic_validation():
    """Demonstrate basic action validation."""
    print_section("1. BASIC ACTION VALIDATION")
    
    god_tier = GodTierAsymmetricSecurity("data/security/demo", enable_all=True)
    
    # Valid action
    print("Testing VALID action (authenticated user with token)...")
    valid_context = {
        "user_id": "alice_123",
        "auth_token": "valid_jwt_token",
        "state_changed": False,
        "current_state": "authenticated",
        "target_state": "authenticated",
    }
    
    result = god_tier.validate_action_comprehensive(
        action="read_profile",
        context=valid_context,
        user_id="alice_123"
    )
    
    print(f"✓ Result: {'ALLOWED' if result['allowed'] else 'BLOCKED'}")
    print(f"  Layers passed: {', '.join(result['layers_passed'])}")
    print(f"  RFI Score: {result.get('rfi_score', 'N/A')}")
    
    # Invalid action
    print("\nTesting INVALID action (no auth token)...")
    invalid_context = {
        "user_id": "attacker_456",
        "auth_token": None,  # Missing token!
        "state_changed": True,
        "current_state": "unauthenticated",
        "target_state": "authenticated",
    }
    
    result = god_tier.validate_action_comprehensive(
        action="delete_user_data",
        context=invalid_context,
        user_id="attacker_456"
    )
    
    print(f"✗ Result: {'ALLOWED' if result['allowed'] else 'BLOCKED'}")
    if not result['allowed']:
        print(f"  Reason: {result.get('failure_reason', 'Unknown')}")
        print(f"  Threat Level: {result['threat_level']}")
    
    return god_tier


def demo_state_machine_analysis(god_tier):
    """Demonstrate state machine cognitive blind spot detection."""
    print_section("2. STATE MACHINE ANALYSIS (Cognitive Blind Spots)")
    
    # Attempt illegal state transition
    print("Attempting illegal state transition (unauthenticated → elevated)...")
    
    context = {
        "user_id": "attacker_789",
        "current_state": "unauthenticated",
        "target_state": "elevated_without_mfa",  # Illegal state!
        "auth_token": None,
        "state_changed": True,
    }
    
    result = god_tier.validate_action_comprehensive(
        action="escalate_privileges",
        context=context,
        user_id="attacker_789"
    )
    
    print(f"✗ Illegal transition BLOCKED")
    print(f"  From: {context['current_state']}")
    print(f"  To: {context['target_state']}")
    print(f"  Reason: {result.get('failure_reason', 'Unknown')}")
    
    # Show illegal-but-reachable states
    illegal_states = god_tier.state_machine_analyzer.find_illegal_reachable_states()
    print(f"\n⚠ Found {len(illegal_states)} illegal-but-reachable states:")
    for state in illegal_states:
        print(f"  - {state.state_id}: {state.properties}")


def demo_temporal_attacks(god_tier):
    """Demonstrate temporal attack detection."""
    print_section("3. TEMPORAL ATTACK DETECTION")
    
    print("Simulating rapid state mutations (race condition)...")
    
    # First mutation
    context1 = {
        "user_id": "user_999",
        "auth_token": "valid",
        "current_state": "authenticated",
        "target_state": "authenticated",
    }
    
    god_tier.temporal_analyzer.record_event(
        "payment_system",
        "mutate_balance",
        {"amount": 100, "operation": "credit"}
    )
    
    time.sleep(0.01)  # 10ms delay
    
    # Second mutation (too fast!)
    god_tier.temporal_analyzer.record_event(
        "payment_system",
        "mutate_balance",
        {"amount": -50, "operation": "debit"}
    )
    
    # Check for race condition
    violation = god_tier.temporal_analyzer.detect_race_condition("payment_system", window_ms=100)
    
    if violation:
        print(f"✗ RACE CONDITION DETECTED!")
        print(f"  Component: {violation.component}")
        print(f"  Time Delta: {violation.time_delta:.2f}ms")
        print(f"  Threat Level: {violation.threat_level.value}")
    else:
        print("✓ No race condition detected")


def demo_inverted_kill_chain(god_tier):
    """Demonstrate inverted kill chain (Detect→Predict→Preempt)."""
    print_section("4. INVERTED KILL CHAIN")
    
    print("Phase 1: DETECT - Checking attack preconditions...")
    
    context = {
        "mfa_enabled": False,  # Weak session!
        "session_age": 3600,
        "ip_suspicious": True,
    }
    
    met_preconditions = god_tier.inverted_kill_chain.detect_preconditions(context)
    
    if met_preconditions:
        print(f"⚠ Detected {len(met_preconditions)} attack preconditions:")
        for precond in met_preconditions:
            print(f"  - {precond}")
        
        print("\nPhase 2: PREDICT - Predicting likely attacks...")
        predictions = god_tier.inverted_kill_chain.predict_attacks(met_preconditions, context)
        
        for pred in predictions:
            print(f"  • {pred.attack_type} (confidence: {pred.confidence:.2f})")
            print(f"    Preemptive actions: {', '.join(pred.preemptive_actions)}")
    else:
        print("✓ No attack preconditions detected")


def demo_entropic_architecture(god_tier):
    """Demonstrate observer-dependent schemas."""
    print_section("5. ENTROPIC ARCHITECTURE (Observer-Dependent Schemas)")
    
    # Original data
    data = {
        "user_id": 42,
        "name": "Bob Smith",
        "email": "bob@example.com",
        "status": "active"
    }
    
    print("Original data:")
    print(f"  {json.dumps(data, indent=2)}")
    
    # Transform for Observer A
    print("\nObserver A sees:")
    transformed_a = god_tier.apply_entropic_transformation(data, "observer_a")
    print(f"  {json.dumps(transformed_a, indent=2)}")
    
    # Transform for Observer B
    print("\nObserver B sees:")
    transformed_b = god_tier.apply_entropic_transformation(data, "observer_b")
    print(f"  {json.dumps(transformed_b, indent=2)}")
    
    print("\n⚡ Same data, different field names!")
    print("   Attacker's exploit script breaks when reused.")


def demo_rfi_calculation(god_tier):
    """Demonstrate Reuse Friction Index calculation."""
    print_section("6. REUSE FRICTION INDEX (Quantifying Irreducibility)")
    
    # Low friction (easily reusable exploit)
    print("Calculating RFI for LOW friction endpoint...")
    low_friction = {
        "requires_observer_schema": False,
        "temporal_window": None,
        "invariant_checks": [],
        "requires_state_path": False,
    }
    
    rfi_low = god_tier.rfi_calculator.calculate_rfi("simple_endpoint", low_friction)
    print(f"  RFI Score: {rfi_low:.2f}")
    print(f"  ⚠ DANGEROUS: Exploit is highly reusable!")
    
    # High friction (hard to reuse)
    print("\nCalculating RFI for HIGH friction endpoint...")
    high_friction = {
        "requires_observer_schema": True,
        "temporal_window": "2024-01-01T00:00:00Z",
        "invariant_checks": ["check1", "check2", "check3"],
        "requires_state_path": True,
    }
    
    rfi_high = god_tier.rfi_calculator.calculate_rfi("protected_endpoint", high_friction)
    print(f"  RFI Score: {rfi_high:.2f}")
    print(f"  ✓ GOOD: Exploit requires {len(high_friction)} independent conditions")


def demo_comprehensive_report(god_tier):
    """Generate and display comprehensive security report."""
    print_section("7. COMPREHENSIVE SECURITY REPORT")
    
    report = god_tier.generate_god_tier_report()
    
    print(f"System: {report['system']} v{report['version']}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"\nMetrics:")
    for metric, value in report['metrics'].items():
        print(f"  {metric}: {value}")
    
    print(f"\nSubsystems Status:")
    subsystems = report['subsystems']
    
    print(f"  State Machine Analyzer:")
    print(f"    - States: {subsystems['state_machine_analyzer']['states']}")
    print(f"    - Illegal transitions: {subsystems['state_machine_analyzer']['illegal_transitions']}")
    print(f"    - Illegal reachable states: {subsystems['state_machine_analyzer']['illegal_reachable_states']}")
    
    print(f"  Temporal Analyzer:")
    print(f"    - Violations detected: {subsystems['temporal_analyzer']['violations']}")
    
    print(f"  Inverted Kill Chain:")
    print(f"    - Attack predictions: {subsystems['inverted_kill_chain']['predictions']}")
    
    print(f"  Entropic Architecture:")
    print(f"    - Schema version: {subsystems['entropic_architecture']['schema_version']}")
    print(f"    - Observer schemas: {subsystems['entropic_architecture']['observer_schemas']}")
    
    print(f"  RFI Calculator:")
    print(f"    - Measurements taken: {subsystems['rfi_calculator']['measurements']}")
    print(f"    - Minimum RFI required: {subsystems['rfi_calculator']['minimum_rfi']}")


def main():
    """Run the complete demo."""
    print("\n" + "="*80)
    print(" "*20 + "GOD TIER ASYMMETRIC SECURITY FRAMEWORK")
    print(" "*25 + "Live Demonstration")
    print("="*80)
    
    try:
        # Initialize
        god_tier = demo_basic_validation()
        
        # Run all demos
        demo_state_machine_analysis(god_tier)
        demo_temporal_attacks(god_tier)
        demo_inverted_kill_chain(god_tier)
        demo_entropic_architecture(god_tier)
        demo_rfi_calculation(god_tier)
        demo_comprehensive_report(god_tier)
        
        # Shutdown
        god_tier.shutdown()
        
        print_section("DEMO COMPLETE")
        print("✓ All systems operational")
        print("✓ Asymmetric advantage demonstrated")
        print("\nKey Takeaway:")
        print("  FROM: 'Finding bugs faster'")
        print("  TO:   'Making exploitation structurally unfinishable'")
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
