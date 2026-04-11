#                                           [2026-04-09 06:10]
#                                          Productivity: Ultimate
"""
Cerberus Enhanced Demo
======================

Demonstrates the ultimate adaptive security system capabilities.
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cognition.cerberus_enhanced import (
    AttackPhase,
    CerberusEnhanced,
    ThreatEvent,
    ThreatIndicator,
    ThreatSeverity,
    create_cerberus_enhanced,
)


async def demo_basic_threat_detection():
    """Demo: Basic threat detection and response."""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Threat Detection")
    print("=" * 70)
    
    # Create and initialize Cerberus
    cerberus = await create_cerberus_enhanced()
    
    # Create a threat event
    threat = ThreatEvent(
        event_id="demo_001",
        timestamp=datetime.now(),
        event_type="suspicious_login",
        severity=ThreatSeverity.MEDIUM,
        source_ip="192.168.1.100",
        user="admin",
        indicators=[
            ThreatIndicator(
                indicator_type="ip",
                value="192.168.1.100",
                severity=ThreatSeverity.MEDIUM,
                confidence=0.75,
                source="internal_detector",
                timestamp=datetime.now()
            )
        ]
    )
    
    # Process threat
    print("\nProcessing threat event...")
    results = await cerberus.process_event(threat)
    
    print(f"\nResults:")
    print(f"  Event ID: {results['event_id']}")
    print(f"  Original Severity: {results['original_severity']}")
    print(f"  Final Severity: {results['final_severity']}")
    print(f"  Threat Score: {results['threat_score']:.1f}/100")
    print(f"  Actions Taken: {len(results['actions_taken'])}")
    for action in results['actions_taken']:
        print(f"    - {action}")
    
    # Get status
    status = cerberus.get_security_status()
    print(f"\nSecurity Status:")
    print(f"  Threat Level: {status['threat_level']}")
    print(f"  Active Threats: {status['active_threats']}")


async def demo_zero_day_detection():
    """Demo: Zero-day threat detection."""
    print("\n" + "=" * 70)
    print("DEMO 2: Zero-Day Threat Detection")
    print("=" * 70)
    
    cerberus = await create_cerberus_enhanced()
    
    # Build baseline with normal events
    print("\nBuilding baseline with normal events...")
    for i in range(30):
        normal = ThreatEvent(
            event_id=f"baseline_{i}",
            timestamp=datetime.now(),
            event_type="routine_check",
            severity=ThreatSeverity.LOW,
            confidence=0.9
        )
        await cerberus.process_event(normal)
    
    print(f"Baseline established with {len(cerberus.threat_history)} events")
    
    # Introduce zero-day
    print("\nProcessing potential zero-day threat...")
    zero_day = ThreatEvent(
        event_id="zero_day_001",
        timestamp=datetime.now(),
        event_type="unknown_attack_pattern",
        severity=ThreatSeverity.CRITICAL,
        source_ip="203.0.113.42",
        indicators=[
            ThreatIndicator(
                indicator_type="pattern",
                value="never_before_seen",
                severity=ThreatSeverity.CRITICAL,
                confidence=0.85,
                source="anomaly_detector",
                timestamp=datetime.now()
            )
        ]
    )
    
    results = await cerberus.process_event(zero_day)
    
    print(f"\nZero-Day Detection Results:")
    if results.get('zero_day_detected'):
        print(f"  ⚠ ZERO-DAY DETECTED!")
        print(f"  Anomaly Score: {results['anomaly_score']:.2f}")
        print(f"  Reason: {results['anomaly_reason']}")
    
    print(f"\nMetrics:")
    print(f"  Zero-Days Detected: {cerberus.metrics['zero_days_detected']}")
    print(f"  Policies Generated: {cerberus.metrics['policies_generated']}")


async def demo_attack_prediction():
    """Demo: ML-based attack prediction."""
    print("\n" + "=" * 70)
    print("DEMO 3: Attack Pattern Prediction")
    print("=" * 70)
    
    cerberus = await create_cerberus_enhanced()
    
    # Simulate escalating attack
    print("\nSimulating escalating attack sequence...")
    attack_phases = [
        (AttackPhase.RECONNAISSANCE, ThreatSeverity.LOW),
        (AttackPhase.INITIAL_ACCESS, ThreatSeverity.MEDIUM),
        (AttackPhase.EXECUTION, ThreatSeverity.MEDIUM),
        (AttackPhase.PRIVILEGE_ESCALATION, ThreatSeverity.HIGH),
    ]
    
    for i, (phase, severity) in enumerate(attack_phases):
        event = ThreatEvent(
            event_id=f"attack_{i}",
            timestamp=datetime.now(),
            event_type=f"attack_phase_{phase.value}",
            severity=severity,
            attack_phase=phase,
            source_ip="198.51.100.10",
            mitre_techniques=cerberus.threat_predictor._get_phase_techniques(phase)
        )
        
        print(f"\n  Processing: {phase.value} ({severity.name})")
        results = await cerberus.process_event(event)
        
        if 'prediction' in results:
            pred = results['prediction']
            print(f"    Prediction: {pred['attack_type']}")
            print(f"    Confidence: {pred['confidence']:.2%}")
            print(f"    Probability: {pred['probability']:.2%}")
            print(f"    Time Window: {pred['time_window']}s")
            print(f"    Recommendations:")
            for rec in pred['recommendations'][:3]:
                print(f"      - {rec}")


async def demo_adaptive_policies():
    """Demo: Adaptive policy generation."""
    print("\n" + "=" * 70)
    print("DEMO 4: Adaptive Policy Generation")
    print("=" * 70)
    
    cerberus = await create_cerberus_enhanced()
    
    # Process threat that triggers policy generation
    print("\nProcessing high-severity threat...")
    threat = ThreatEvent(
        event_id="policy_demo_001",
        timestamp=datetime.now(),
        event_type="malware_execution",
        severity=ThreatSeverity.HIGH,
        source_ip="192.168.5.100",
        file_hash="deadbeef1234",
        indicators=[
            ThreatIndicator(
                indicator_type="hash",
                value="deadbeef1234",
                severity=ThreatSeverity.HIGH,
                confidence=0.92,
                source="malware_scanner",
                timestamp=datetime.now(),
                mitre_techniques=["T1059", "T1003"]
            )
        ],
        mitre_techniques=["T1059", "T1003"]
    )
    
    results = await cerberus.process_event(threat)
    
    if 'policy_generated' in results:
        policy_id = results['policy_generated']
        policy = cerberus.policy_generator.policies[policy_id]
        
        print(f"\nGenerated Policy: {policy.name}")
        print(f"  Policy ID: {policy.policy_id}")
        print(f"  Priority: {policy.priority}")
        print(f"  Enabled: {policy.enabled}")
        print(f"  Conditions: {len(policy.conditions)}")
        for cond in policy.conditions[:3]:
            print(f"    - {cond['type']}: {cond.get('value', 'N/A')}")
        print(f"  Actions: {len(policy.actions)}")
        for action in policy.actions:
            print(f"    - {action['type']}: {action.get('level', action.get('scope', 'N/A'))}")
        print(f"  MITRE Coverage: {', '.join(policy.mitre_coverage)}")


async def demo_octoreflex_coordination():
    """Demo: OctoReflex containment coordination."""
    print("\n" + "=" * 70)
    print("DEMO 5: OctoReflex Containment Coordination")
    print("=" * 70)
    
    cerberus = await create_cerberus_enhanced()
    
    # Process critical threat requiring containment
    print("\nProcessing critical threat requiring containment...")
    critical = ThreatEvent(
        event_id="containment_001",
        timestamp=datetime.now(),
        event_type="active_breach",
        severity=ThreatSeverity.CRITICAL,
        source_ip="203.0.113.99",
        user="compromised_account",
        attack_phase=AttackPhase.LATERAL_MOVEMENT,
        indicators=[
            ThreatIndicator(
                indicator_type="ip",
                value="203.0.113.99",
                severity=ThreatSeverity.CRITICAL,
                confidence=0.98,
                source="threat_feed",
                timestamp=datetime.now(),
                mitre_techniques=["T1021"]
            )
        ]
    )
    
    results = await cerberus.process_event(critical)
    
    if 'octoreflex_action' in results:
        action_id = results['octoreflex_action']
        action = await cerberus.octoreflex.check_action_status(action_id)
        
        print(f"\nOctoReflex Containment Action:")
        print(f"  Action ID: {action.action_id}")
        print(f"  Type: {action.action_type}")
        print(f"  Target: {action.target}")
        print(f"  Severity: {action.severity.name}")
        print(f"  Automated: {action.automated}")
        print(f"  Status: {action.status}")
        print(f"  Confidence: {action.confidence:.2%}")


async def demo_complete_scenario():
    """Demo: Complete attack scenario with full response."""
    print("\n" + "=" * 70)
    print("DEMO 6: Complete Attack Scenario")
    print("=" * 70)
    
    cerberus = await create_cerberus_enhanced()
    
    print("\nScenario: Multi-stage APT attack simulation")
    print("-" * 70)
    
    # Stage 1: Reconnaissance
    print("\n[STAGE 1] Reconnaissance detected...")
    recon = ThreatEvent(
        event_id="apt_001",
        timestamp=datetime.now(),
        event_type="port_scan",
        severity=ThreatSeverity.LOW,
        source_ip="198.51.100.200",
        attack_phase=AttackPhase.RECONNAISSANCE
    )
    await cerberus.process_event(recon)
    
    # Stage 2: Initial Access
    print("[STAGE 2] Initial access attempt...")
    access = ThreatEvent(
        event_id="apt_002",
        timestamp=datetime.now(),
        event_type="exploit_attempt",
        severity=ThreatSeverity.MEDIUM,
        source_ip="198.51.100.200",
        attack_phase=AttackPhase.INITIAL_ACCESS,
        mitre_techniques=["T1190"]
    )
    await cerberus.process_event(access)
    
    # Stage 3: Execution
    print("[STAGE 3] Malicious code execution...")
    execution = ThreatEvent(
        event_id="apt_003",
        timestamp=datetime.now(),
        event_type="script_execution",
        severity=ThreatSeverity.HIGH,
        source_ip="198.51.100.200",
        attack_phase=AttackPhase.EXECUTION,
        mitre_techniques=["T1059"]
    )
    results = await cerberus.process_event(execution)
    
    # Stage 4: Privilege Escalation
    print("[STAGE 4] Privilege escalation detected...")
    priv_esc = ThreatEvent(
        event_id="apt_004",
        timestamp=datetime.now(),
        event_type="privilege_escalation",
        severity=ThreatSeverity.CRITICAL,
        source_ip="198.51.100.200",
        attack_phase=AttackPhase.PRIVILEGE_ESCALATION,
        mitre_techniques=["T1068"]
    )
    results = await cerberus.process_event(priv_esc)
    
    # Final status
    print("\n" + "=" * 70)
    print("FINAL SECURITY STATUS")
    print("=" * 70)
    
    status = cerberus.get_security_status()
    print(f"\nThreat Level: {status['threat_level']}")
    print(f"Active Threats: {status['active_threats']}")
    print(f"\nMetrics:")
    print(f"  Events Processed: {cerberus.metrics['events_processed']}")
    print(f"  Threats Detected: {cerberus.metrics['threats_detected']}")
    print(f"  Zero-Days Detected: {cerberus.metrics['zero_days_detected']}")
    print(f"  Policies Generated: {cerberus.metrics['policies_generated']}")
    print(f"  Predictions Made: {cerberus.metrics['predictions_made']}")
    print(f"  OctoReflex Actions: {cerberus.metrics['octoreflex_actions']}")
    
    print(f"\nActive Policies: {status['active_policies']}")
    print(f"Recent Predictions: {status['recent_predictions']}")
    print(f"Threat Intel Indicators: {status['intel_indicators']}")


async def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("CERBERUS ENHANCED - ULTIMATE ADAPTIVE SECURITY SYSTEM")
    print("Demonstration Suite")
    print("=" * 70)
    
    demos = [
        ("Basic Threat Detection", demo_basic_threat_detection),
        ("Zero-Day Detection", demo_zero_day_detection),
        ("Attack Prediction", demo_attack_prediction),
        ("Adaptive Policies", demo_adaptive_policies),
        ("OctoReflex Coordination", demo_octoreflex_coordination),
        ("Complete Scenario", demo_complete_scenario),
    ]
    
    for name, demo_func in demos:
        try:
            await demo_func()
        except Exception as e:
            print(f"\n✗ Demo '{name}' failed: {e}")
        
        await asyncio.sleep(1)  # Brief pause between demos
    
    print("\n" + "=" * 70)
    print("All demonstrations completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
