#!/usr/bin/env python3
#                                           [2026-03-05 10:03]
#                                          Productivity: Active
"""
Enhanced Network Defense Engine - Usage Examples.

Comprehensive examples demonstrating all features of the network defense simulation.
"""

import logging
import time
from engines.network_defense_enhanced import (
    NetworkDefenseEnhancedEngine,
    DDoSIntensity,
    APTStage,
    TrustLevel,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def example_basic_simulation():
    """Basic simulation example."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Network Defense Simulation")
    print("=" * 70)
    
    engine = NetworkDefenseEnhancedEngine()
    
    # Initialize
    print("\n1. Initializing engine...")
    engine.init()
    
    # Run simulation
    print("\n2. Running 5 simulation ticks...")
    for i in range(5):
        engine.tick()
        state = engine.observe()
        print(f"   Tick {i+1}: DDoS={state['ddos_attacks_active']}, "
              f"APT={state['apt_scenarios_active']}, "
              f"Bandwidth={state['total_bandwidth_used_gbps']:.2f} Gbps")
    
    # Generate report
    print("\n3. Generating summary report...")
    print(engine.report("summary"))


def example_ddos_response():
    """DDoS attack detection and response."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: DDoS Attack Detection and Mitigation")
    print("=" * 70)
    
    # High probability of DDoS attacks
    engine = NetworkDefenseEnhancedEngine({"ddos_probability": 1.0})
    engine.init()
    
    print("\n1. Simulating DDoS attacks...")
    for _ in range(3):
        engine._simulate_ddos_attack()
    
    print(f"   Generated {len(engine.state.ddos_attacks)} attacks")
    
    # Display attacks
    print("\n2. Attack details:")
    for attack in engine.state.ddos_attacks:
        print(f"   [{attack.attack_id}]")
        print(f"      Layer: {attack.layer.value}")
        print(f"      Intensity: {attack.intensity.value}")
        print(f"      Bandwidth: {attack.bandwidth_gbps:.2f} Gbps")
        print(f"      Protocol: {attack.protocol}")
        print(f"      Mitigated: {attack.mitigation_triggered}")
    
    # Mitigate unmitigated attacks
    print("\n3. Mitigating remaining attacks...")
    for attack in engine.state.ddos_attacks:
        if not attack.mitigation_triggered:
            result = engine.action("mitigate_ddos", {"attack_id": attack.attack_id})
            print(f"   Mitigated {attack.attack_id}: {result}")
    
    # Final state
    state = engine.observe()
    print(f"\n4. Final state:")
    print(f"   Blocked attacks: {state['blocked_attacks']}")
    print(f"   Current bandwidth: {state['total_bandwidth_used_gbps']:.2f} Gbps")


def example_apt_campaign():
    """Advanced Persistent Threat campaign simulation."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Advanced Persistent Threat Campaign")
    print("=" * 70)
    
    engine = NetworkDefenseEnhancedEngine()
    engine.init()
    
    print("\n1. Initial APT scenarios:")
    for apt in engine.state.apt_scenarios:
        print(f"   {apt.threat_actor}: {apt.current_stage.value}")
    
    # Progress APT scenarios
    print("\n2. Progressing APT campaigns (50 ticks)...")
    for i in range(50):
        engine.tick()
        if (i + 1) % 10 == 0:
            print(f"   Tick {i+1}: Active={len([a for a in engine.state.apt_scenarios if not a.detected])}, "
                  f"Detected={engine.state.detected_apts}")
    
    # Display APT details
    print("\n3. APT campaign details:")
    for apt in engine.state.apt_scenarios:
        print(f"\n   {apt.threat_actor} ({apt.scenario_id}):")
        print(f"      Status: {'Detected' if apt.detected else 'Active'}")
        print(f"      Current Stage: {apt.current_stage.value}")
        print(f"      Stages Completed: {len(apt.stages_completed)}")
        print(f"      Dwell Time: {apt.dwell_time_days} days")
        print(f"      Credentials Stolen: {apt.credentials_stolen}")
        print(f"      Hosts Compromised: {len(apt.compromised_hosts)}")
        print(f"      Data Exfiltrated: {apt.data_exfiltrated_mb:.2f} MB")
        print(f"      Persistence Mechanisms: {', '.join(apt.persistence_mechanisms) if apt.persistence_mechanisms else 'None'}")
    
    # Block C2 for active APTs
    print("\n4. Blocking C2 communications for active threats...")
    for apt in engine.state.apt_scenarios:
        if not apt.detected:
            result = engine.action("block_c2", {"scenario_id": apt.scenario_id})
            print(f"   Blocked C2 for {apt.threat_actor}: {result}")


def example_lateral_movement():
    """Lateral movement detection example."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Lateral Movement Detection")
    print("=" * 70)
    
    engine = NetworkDefenseEnhancedEngine({"lateral_movement_probability": 1.0})
    engine.init()
    
    print("\n1. Generating lateral movement events...")
    for _ in range(20):
        engine._detect_lateral_movement()
    
    print(f"   Total events: {len(engine.state.lateral_movements)}")
    
    # Filter suspicious events
    suspicious = [lm for lm in engine.state.lateral_movements if lm.is_suspicious]
    print(f"   Suspicious events: {len(suspicious)}")
    
    # Display suspicious movements
    print("\n2. Suspicious lateral movements:")
    for event in suspicious[:5]:  # Show first 5
        print(f"\n   {event.source_zone} → {event.destination_zone}")
        print(f"      Protocol: {event.protocol} (Port {event.port})")
        print(f"      Anomaly Score: {event.anomaly_score:.2f}")
        print(f"      Indicators: {', '.join(event.indicators)}")
        print(f"      Detection Method: {event.detection_method}")
    
    # Isolate suspicious hosts
    print("\n3. Isolating suspicious hosts...")
    for event in suspicious[:3]:  # Isolate first 3
        result = engine.action("isolate_host", {"host": event.source_host})
        print(f"   Isolated {event.source_host}: {result}")


def example_network_segmentation():
    """Network segmentation validation example."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Network Segmentation Validation")
    print("=" * 70)
    
    engine = NetworkDefenseEnhancedEngine()
    engine.init()
    
    # Display segments
    print("\n1. Network segments:")
    for seg in engine.state.network_segments:
        print(f"\n   {seg.name} ({seg.segment_id})")
        print(f"      VLAN: {seg.vlan_id}")
        print(f"      Subnet: {seg.subnet}")
        print(f"      Isolation: {seg.isolation_level}")
        print(f"      Micro-segmentation: {seg.micro_segmentation}")
        print(f"      Firewall Rules: {seg.firewall_rules}")
        print(f"      ACL Rules: {seg.acl_rules}")
        print(f"      Allowed Outbound: {', '.join(seg.allowed_outbound) if seg.allowed_outbound else 'None'}")
        print(f"      Allowed Inbound: {', '.join(seg.allowed_inbound) if seg.allowed_inbound else 'None'}")
    
    # Run validation
    print("\n2. Running segmentation validation (100 checks)...")
    initial_violations = engine.state.segmentation_violations
    for _ in range(100):
        engine._validate_network_segmentation()
    
    violations = engine.state.segmentation_violations - initial_violations
    print(f"   Violations detected: {violations}")
    
    # Enforce strict segmentation
    print("\n3. Enforcing strict segmentation on critical segments...")
    for seg in engine.state.network_segments:
        if seg.name in ["Database Tier", "Management"]:
            result = engine.action("enforce_segmentation", {"segment_id": seg.segment_id})
            print(f"   Enforced {seg.name}: {result}")
            print(f"      New isolation level: {seg.isolation_level}")


def example_zero_trust():
    """Zero Trust enforcement example."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Zero Trust Architecture Enforcement")
    print("=" * 70)
    
    engine = NetworkDefenseEnhancedEngine()
    engine.init()
    
    # Display policies
    print("\n1. Zero Trust policies:")
    for policy in engine.state.zero_trust_policies:
        print(f"\n   {policy.policy_id}")
        print(f"      Resource: {policy.resource}")
        print(f"      User Identity: {policy.user_identity}")
        print(f"      Device Identity: {policy.device_identity}")
        print(f"      Trust Level: {policy.trust_level.value}")
        print(f"      MFA Required: {policy.mfa_required}")
        print(f"      Device Posture Check: {policy.device_posture_check}")
        print(f"      Location Check: {policy.location_check}")
        print(f"      Time-based Access: {policy.time_based_access}")
        print(f"      Context-aware: {policy.context_aware}")
        print(f"      Continuous Validation: {policy.continuous_validation}")
    
    # Run enforcement
    print("\n2. Running policy enforcement (100 validations)...")
    initial_violations = engine.state.zero_trust_violations
    for _ in range(100):
        engine._enforce_zero_trust()
    
    violations = engine.state.zero_trust_violations - initial_violations
    print(f"   Violations detected: {violations}")
    
    # Display violations per policy
    print("\n3. Violations by policy:")
    for policy in engine.state.zero_trust_policies:
        if policy.violations > 0:
            print(f"   {policy.policy_id}: {policy.violations} violations")
    
    # Revoke access for violated policies
    print("\n4. Revoking access for policies with violations...")
    for policy in engine.state.zero_trust_policies:
        if policy.violations > 2:  # Threshold
            result = engine.action("revoke_access", {"policy_id": policy.policy_id})
            print(f"   Revoked {policy.policy_id}: {result}")
            print(f"      New trust level: {policy.trust_level.value}")


def example_integrated_scenario():
    """Integrated multi-threat scenario."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Integrated Multi-Threat Scenario")
    print("=" * 70)
    
    # High probability configuration
    config = {
        "ddos_probability": 0.7,
        "apt_probability": 0.5,
        "lateral_movement_probability": 0.6,
    }
    
    engine = NetworkDefenseEnhancedEngine(config)
    engine.init()
    
    print("\n1. Running integrated simulation (30 ticks)...")
    for i in range(30):
        engine.tick()
        
        if (i + 1) % 5 == 0:
            state = engine.observe()
            print(f"\n   Tick {i+1} Status:")
            print(f"      DDoS: {state['ddos_attacks_active']} active, {state['ddos_attacks_mitigated']} mitigated")
            print(f"      APT: {state['apt_scenarios_active']} active, {state['apt_scenarios_detected']} detected")
            print(f"      Lateral Movements: {state['lateral_movements_detected']} ({state['suspicious_lateral_movements']} suspicious)")
            print(f"      Bandwidth: {state['total_bandwidth_used_gbps']:.2f} Gbps")
            print(f"      Segmentation Violations: {state['segmentation_violations']}")
            print(f"      Zero Trust Violations: {state['zero_trust_violations']}")
    
    # Take defensive actions
    print("\n2. Executing coordinated defense...")
    
    # Mitigate active DDoS
    active_ddos = [a for a in engine.state.ddos_attacks if not a.mitigation_triggered]
    print(f"   Mitigating {len(active_ddos)} DDoS attacks...")
    for attack in active_ddos[:3]:  # Limit to 3
        engine.action("mitigate_ddos", {"attack_id": attack.attack_id})
    
    # Block active APTs
    active_apts = [a for a in engine.state.apt_scenarios if not a.detected]
    print(f"   Blocking {len(active_apts)} APT scenarios...")
    for apt in active_apts:
        engine.action("block_c2", {"scenario_id": apt.scenario_id})
    
    # Isolate suspicious movements
    suspicious = [lm for lm in engine.state.lateral_movements if lm.is_suspicious]
    print(f"   Isolating {len(suspicious[:5])} suspicious hosts...")
    for event in suspicious[:5]:
        engine.action("isolate_host", {"host": event.source_host})
    
    # Final report
    print("\n3. Final Detailed Report:")
    print(engine.report("detailed"))


def example_custom_scenario():
    """Custom scenario with manual control."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Custom Controlled Scenario")
    print("=" * 70)
    
    engine = NetworkDefenseEnhancedEngine({"ddos_probability": 0.0})
    engine.init()
    
    # Manually create specific attacks
    print("\n1. Creating specific attack scenarios...")
    
    # Create Layer 7 DDoS
    print("   Creating Layer 7 DDoS attack...")
    engine._simulate_ddos_attack()
    
    # Create Layer 4 DDoS
    print("   Creating Layer 4 DDoS attack...")
    engine._simulate_ddos_attack()
    
    # Create lateral movement
    print("   Creating lateral movement event...")
    engine._detect_lateral_movement()
    
    # Display created attacks
    print("\n2. Created attacks:")
    for attack in engine.state.ddos_attacks:
        print(f"   DDoS: {attack.layer.value} - {attack.intensity.value} - {attack.bandwidth_gbps:.2f} Gbps")
    
    for event in engine.state.lateral_movements:
        print(f"   Lateral: {event.source_zone} → {event.destination_zone} (score: {event.anomaly_score:.2f})")
    
    # Respond systematically
    print("\n3. Systematic response:")
    
    # Mitigate all attacks
    for attack in engine.state.ddos_attacks:
        if not attack.mitigation_triggered:
            engine.action("mitigate_ddos", {"attack_id": attack.attack_id})
            print(f"   ✓ Mitigated {attack.attack_id}")
    
    # Isolate all suspicious hosts
    for event in engine.state.lateral_movements:
        if event.is_suspicious:
            engine.action("isolate_host", {"host": event.source_host})
            print(f"   ✓ Isolated {event.source_host}")
    
    # Enforce segmentation
    for seg in engine.state.network_segments:
        engine.action("enforce_segmentation", {"segment_id": seg.segment_id})
        print(f"   ✓ Enforced segmentation on {seg.name}")
    
    print("\n4. Response complete!")


def main():
    """Run all examples."""
    examples = [
        example_basic_simulation,
        example_ddos_response,
        example_apt_campaign,
        example_lateral_movement,
        example_network_segmentation,
        example_zero_trust,
        example_integrated_scenario,
        example_custom_scenario,
    ]
    
    print("\n" + "=" * 70)
    print("ENHANCED NETWORK DEFENSE ENGINE - COMPREHENSIVE EXAMPLES")
    print("=" * 70)
    print(f"\nRunning {len(examples)} examples...\n")
    
    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
            print(f"\n✅ Example {i} completed successfully")
        except Exception as e:
            print(f"\n❌ Example {i} failed: {e}")
        
        # Brief pause between examples
        time.sleep(0.5)
    
    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
