#                                           [2026-04-11 02:45]
#                                          Productivity: Active
"""
Temporal Attack Engine Integration Demo

Demonstrates full integration with Chronos and Atropos temporal agents,
showcasing attack detection, anomaly identification, and causality validation.
"""

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.temporal_attack_enhanced import (
    AttackCategory,
    TemporalAttackEngine,
)

try:
    from src.cognition.temporal.chronos import Chronos, TemporalEvent as ChronosEvent
    from src.cognition.temporal.atropos import Atropos
    from src.cognition.temporal.vector_clock import VectorClock
    
    TEMPORAL_AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Warning: Temporal agents not available: {e}")
    print("  Running in standalone mode without Chronos/Atropos integration\n")
    TEMPORAL_AGENTS_AVAILABLE = False


def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_section(title):
    """Print formatted section."""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}\n")


def demo_attack_vectors():
    """Demonstrate attack vector generation."""
    print_header("DEMONSTRATION: Temporal Attack Vectors")
    
    engine = TemporalAttackEngine()
    attacks = engine.generate_all_attack_vectors()
    
    print(f"Generated {len(attacks)} temporal attack scenarios\n")
    
    # Show summary by category
    print("Attack Categories:")
    for category in AttackCategory:
        count = sum(1 for a in attacks if a.category == category)
        if count > 0:
            print(f"  • {category.value:30s} {count:2d} scenarios")
    
    # Show some example attacks
    print("\n📋 Example Attack Scenarios:\n")
    
    examples = [
        ("TEMP_RACE_002", "Double-Spend Race Condition"),
        ("TEMP_TOCTOU_004", "Authentication State TOCTOU"),
        ("TEMP_REPLAY_001", "Session Cookie Replay"),
        ("TEMP_CLOCK_002", "Distributed System Clock Skew"),
        ("TEMP_CAUSE_003", "Temporal Paradox Injection")
    ]
    
    for attack_id, _ in examples:
        attack = next((a for a in attacks if a.attack_id == attack_id), None)
        if attack:
            print(f"🎯 {attack.name}")
            print(f"   ID: {attack.attack_id}")
            print(f"   Category: {attack.category.value}")
            print(f"   Severity: {attack.severity.value.upper()}")
            print(f"   CVSS Score: {attack.cvss_score}")
            print(f"   Complexity: {attack.exploitation_complexity}")
            print(f"   Description: {attack.description}")
            print(f"   Temporal Window: {attack.temporal_window_ms}ms")
            print(f"   Mitigations: {', '.join(attack.mitigation_strategies[:2])}...\n")


def demo_anomaly_detection():
    """Demonstrate temporal anomaly detection."""
    print_header("DEMONSTRATION: Temporal Anomaly Detection")
    
    engine = TemporalAttackEngine()
    detector = engine.anomaly_detector
    
    print("Testing various temporal anomaly scenarios...\n")
    
    # Scenario 1: Future timestamp
    print_section("Scenario 1: Future Timestamp Detection")
    future_event = {
        "event_id": "evt_future_001",
        "event_type": "transaction",
        "timestamp": datetime.now(timezone.utc) + timedelta(seconds=3),
        "source_id": "malicious_agent",
        "sequence": 1,
        "payload": {"amount": 1000}
    }
    
    print("📨 Event with future timestamp (3 seconds ahead)")
    anomalies = detector.check_event(future_event)
    
    for anomaly in anomalies:
        print(f"\n🚨 ANOMALY DETECTED!")
        print(f"   Type: {anomaly.anomaly_type.value}")
        print(f"   Severity: {anomaly.severity.value}")
        print(f"   Confidence: {anomaly.confidence:.0%}")
        print(f"   Description: {anomaly.description}")
        print(f"   Recommended Action: {anomaly.recommended_action}")
    
    # Scenario 2: Replay attack (duplicate event)
    print_section("Scenario 2: Replay Attack Detection")
    original_event = {
        "event_id": "evt_original",
        "event_type": "transfer",
        "timestamp": datetime.now(timezone.utc),
        "source_id": "agent1",
        "sequence": 2,
        "payload": {"from": "user1", "to": "user2", "amount": 500}
    }
    
    print("📨 Original transaction event")
    detector.check_event(original_event)
    print("✓ Event processed normally\n")
    
    time.sleep(0.1)
    
    print("📨 Replaying same transaction (replay attack attempt)")
    anomalies = detector.check_event(original_event)
    
    for anomaly in anomalies:
        print(f"\n🚨 REPLAY ATTACK DETECTED!")
        print(f"   Type: {anomaly.anomaly_type.value}")
        print(f"   Confidence: {anomaly.confidence:.0%}")
        print(f"   Description: {anomaly.description}")
        print(f"   Evidence: {json.dumps(anomaly.evidence, indent=6)}")
    
    # Scenario 3: Sequence violation
    print_section("Scenario 3: Sequence Violation Detection")
    
    seq_events = [
        {"event_id": f"evt_seq_{i}", "sequence": i, "source_id": "agent2"}
        for i in [1, 2, 3, 5, 4]  # Out of order at the end
    ]
    
    for i, evt in enumerate(seq_events):
        evt.update({
            "event_type": "operation",
            "timestamp": datetime.now(timezone.utc)
        })
        
        print(f"📨 Event sequence {evt['sequence']}")
        anomalies = detector.check_event(evt)
        
        if anomalies:
            for anomaly in anomalies:
                if "sequence" in anomaly.anomaly_type.value.lower():
                    print(f"   🚨 {anomaly.description}")
        else:
            print("   ✓ Sequence valid")
    
    # Scenario 4: Clock drift
    print_section("Scenario 4: Clock Drift Detection")
    
    agent_timestamps = {
        "node1": datetime.now(timezone.utc),
        "node2": datetime.now(timezone.utc) - timedelta(seconds=3),
        "node3": datetime.now(timezone.utc) - timedelta(seconds=8),
    }
    
    print("🕐 Agent timestamps:")
    for agent, ts in agent_timestamps.items():
        print(f"   {agent}: {ts.strftime('%H:%M:%S.%f')[:-3]}")
    
    drift_anomalies = detector.detect_clock_drift(agent_timestamps)
    
    for anomaly in drift_anomalies:
        print(f"\n🚨 CLOCK DRIFT DETECTED!")
        print(f"   Severity: {anomaly.severity.value}")
        print(f"   Drift: {anomaly.evidence['drift_ms']:.0f}ms")
        print(f"   Threshold: {anomaly.evidence['max_allowed_drift_ms']}ms")
        print(f"   Recommended Action: {anomaly.recommended_action}")


def demo_causality_validation():
    """Demonstrate causality validation and violation detection."""
    print_header("DEMONSTRATION: Causality Validation")
    
    engine = TemporalAttackEngine()
    validator = engine.causality_validator
    
    # Valid causal chain
    print_section("Scenario 1: Valid Causal Chain")
    
    print("Building event chain: e1 → e2 → e3")
    
    validator.add_event("e1", {"agent1": 1, "agent2": 0}, None)
    print("✓ Event e1: Create account (VC: agent1=1, agent2=0)")
    
    validator.add_event("e2", {"agent1": 2, "agent2": 1}, ["e1"])
    print("✓ Event e2: Deposit funds (VC: agent1=2, agent2=1) [depends on e1]")
    
    validator.add_event("e3", {"agent1": 3, "agent2": 2}, ["e2"])
    print("✓ Event e3: Make transfer (VC: agent1=3, agent2=2) [depends on e2]")
    
    is_valid, reason = validator.verify_happens_before("e1", "e3")
    print(f"\n🔍 Verification: e1 happens-before e3")
    print(f"   Result: {'✓ VALID' if is_valid else '✗ INVALID'}")
    print(f"   Reason: {reason}")
    
    # Causality violation
    print_section("Scenario 2: Causality Violation")
    
    print("Attempting invalid event ordering...")
    
    validator.add_event("e4", {"agent1": 5, "agent2": 3}, None)
    print("✓ Event e4: Operation A (VC: agent1=5, agent2=3)")
    
    # This creates a violation - e5 depends on e4, but its vector clock
    # suggests it happened before e4
    validator.add_event("e5", {"agent1": 4, "agent2": 2}, ["e4"])
    print("✓ Event e5: Operation B (VC: agent1=4, agent2=2) [claims to depend on e4]")
    
    violations = validator.detect_violations()
    
    if violations:
        print(f"\n🚨 CAUSALITY VIOLATION DETECTED!")
        for v in violations:
            print(f"   Type: {v.violation_type}")
            print(f"   Severity: {v.severity.value}")
            print(f"   Description: {v.description}")
            print(f"   Expected: {v.expected_order}")
            print(f"   Actual: {v.actual_order}")
    
    # Temporal paradox (cycle)
    print_section("Scenario 3: Temporal Paradox (Cycle)")
    
    validator2 = engine.causality_validator.__class__()
    
    print("Creating circular dependency chain...")
    validator2.add_event("a", {"agent1": 1})
    print("✓ Event a (VC: agent1=1)")
    
    validator2.add_event("b", {"agent1": 2}, ["a"])
    print("✓ Event b depends on a")
    
    validator2.add_event("c", {"agent1": 3}, ["b"])
    print("✓ Event c depends on b")
    
    # Create cycle: a → b → c → a
    validator2.dependencies["a"] = ["c"]
    print("✓ Making event a depend on c (creating cycle)")
    
    cycle = validator2.check_cycle()
    
    if cycle:
        print(f"\n🚨 TEMPORAL PARADOX DETECTED!")
        print(f"   Cycle: {' → '.join(cycle)}")
        print(f"   Impact: This creates an impossible causal loop")
        print(f"   Action: Reject event creating cycle")


def demo_chronos_integration():
    """Demonstrate Chronos integration."""
    if not TEMPORAL_AGENTS_AVAILABLE:
        print_header("DEMONSTRATION: Chronos Integration (SKIPPED)")
        print("⚠ Chronos module not available - skipping this demo\n")
        return
    
    print_header("DEMONSTRATION: Chronos Integration")
    
    # Initialize Chronos and engine
    chronos = Chronos(instance_id="demo_chronos")
    engine = TemporalAttackEngine()
    engine.integrate_chronos(chronos)
    
    print("✓ Initialized Chronos temporal weight engine")
    print("✓ Integrated with temporal attack engine\n")
    
    print_section("Creating Causal Event Chain")
    
    # Create causal chain of events
    events_data = [
        ("create_user", "agent1", None),
        ("verify_email", "agent1", ["create_user"]),
        ("update_profile", "agent2", ["verify_email"]),
        ("grant_permissions", "agent2", ["update_profile"]),
    ]
    
    for event_type, agent_id, causes in events_data:
        event = chronos.record_event(
            event_id=f"evt_{event_type}",
            event_type=event_type,
            agent_id=agent_id,
            data={"action": event_type},
            causes=causes
        )
        
        print(f"📝 Event: {event_type}")
        print(f"   Agent: {agent_id}")
        print(f"   Vector Clock: {event.vector_clock.clock}")
        if causes:
            print(f"   Depends on: {', '.join(causes)}")
        print()
    
    print_section("Simulating Causality Violation Attack")
    
    attacks = engine.generate_all_attack_vectors()
    causality_attack = next(
        (a for a in attacks if a.category == AttackCategory.CAUSALITY_VIOLATION),
        None
    )
    
    if causality_attack:
        print(f"🎯 Attack: {causality_attack.name}")
        print(f"   Description: {causality_attack.description}\n")
        
        result = engine.simulate_attack(causality_attack.attack_id)
        
        print("📊 Simulation Result:")
        print(f"   Attack Success: {result.get('success')}")
        print(f"   Detection Results:")
        for system, detection in result.get('detection_results', {}).items():
            print(f"      • {system}: {detection}")


def demo_atropos_integration():
    """Demonstrate Atropos integration."""
    if not TEMPORAL_AGENTS_AVAILABLE:
        print_header("DEMONSTRATION: Atropos Integration (SKIPPED)")
        print("⚠ Atropos module not available - skipping this demo\n")
        return
    
    print_header("DEMONSTRATION: Atropos Integration")
    
    # Initialize Atropos and engine
    atropos = Atropos()
    engine = TemporalAttackEngine()
    engine.integrate_atropos(atropos)
    
    print("✓ Initialized Atropos anti-rollback protection")
    print("✓ Integrated with temporal attack engine\n")
    
    print_section("Creating Tamper-Proof Event Chain")
    
    # Create events with hash chaining
    transactions = [
        {"type": "deposit", "amount": 1000, "account": "user1"},
        {"type": "withdraw", "amount": 100, "account": "user1"},
        {"type": "transfer", "amount": 200, "from": "user1", "to": "user2"},
    ]
    
    for i, tx in enumerate(transactions):
        event = atropos.create_event(
            event_id=f"tx_{i+1:03d}",
            event_type=tx["type"],
            payload=tx
        )
        
        print(f"🔒 Transaction {i+1}: {tx['type']}")
        print(f"   Event Hash: {event.event_hash[:16]}...")
        print(f"   Previous Hash: {event.previous_hash[:16]}...")
        print(f"   Lamport TS: {event.lamport_timestamp}")
        print(f"   Monotonic Seq: {event.monotonic_sequence}")
        print(f"   Hash Valid: {event.verify_hash()}")
        print()
        
        time.sleep(0.01)
    
    print_section("Simulating Replay Attack")
    
    attacks = engine.generate_all_attack_vectors()
    replay_attack = next(
        (a for a in attacks if a.category == AttackCategory.SESSION_REPLAY),
        None
    )
    
    if replay_attack:
        print(f"🎯 Attack: {replay_attack.name}")
        print(f"   Description: {replay_attack.description}\n")
        
        result = engine.simulate_attack(replay_attack.attack_id)
        
        print("📊 Simulation Result:")
        print(f"   Attack Success: {result.get('success')}")
        print(f"   Detection Results:")
        for system, detection in result.get('detection_results', {}).items():
            print(f"      • {system}: {detection}")


def demo_comprehensive_report():
    """Generate comprehensive attack report."""
    print_header("DEMONSTRATION: Comprehensive Attack Report")
    
    engine = TemporalAttackEngine()
    
    # Generate attacks
    print("Generating attack scenarios...")
    engine.generate_all_attack_vectors()
    
    # Generate some anomalies
    print("Simulating anomaly detection...")
    test_events = [
        {
            "event_id": f"test_{i}",
            "event_type": "test",
            "timestamp": datetime.now(timezone.utc),
            "source_id": "agent1",
            "sequence": i
        }
        for i in range(5)
    ]
    
    for event in test_events:
        engine.anomaly_detector.check_event(event)
    
    # Generate report
    print("Generating comprehensive report...\n")
    report = engine.generate_report()
    
    print("📊 TEMPORAL ATTACK SIMULATION REPORT")
    print(f"   Generated: {report['report_generated']}")
    
    print("\n📍 Attack Vectors:")
    print(f"   Total Scenarios: {report['attack_vectors']['total']}")
    print(f"\n   By Category:")
    for category, count in report['attack_vectors']['by_category'].items():
        print(f"      • {category:30s} {count:2d}")
    
    print(f"\n   By Severity:")
    for severity, count in report['attack_vectors']['by_severity'].items():
        print(f"      • {severity.upper():10s} {count:2d}")
    
    print("\n🔍 Anomaly Detection:")
    print(f"   Total Anomalies: {report['anomalies']['total']}")
    print(f"   High Confidence: {report['anomalies']['high_confidence']}")
    
    print("\n⚠️  Causality Violations:")
    print(f"   Total: {report['causality_violations']['total']}")
    print(f"   Critical: {report['causality_violations']['critical']}")
    
    print("\n🔗 Integrations:")
    print(f"   Chronos: {'✓ Active' if report['integrations']['chronos'] else '✗ Not integrated'}")
    print(f"   Atropos: {'✓ Active' if report['integrations']['atropos'] else '✗ Not integrated'}")
    
    # Export results
    print_section("Exporting Results")
    
    attack_file = engine.export_attack_vectors()
    print(f"✓ Attack vectors exported to:\n  {attack_file}")
    
    anomaly_file = engine.export_anomalies()
    print(f"\n✓ Anomalies exported to:\n  {anomaly_file}")


def main():
    """Run all demonstrations."""
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "    ENHANCED TEMPORAL ATTACK SIMULATION ENGINE".center(78) + "║")
    print("║" + "    Integration Demonstration".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    
    demos = [
        ("Attack Vector Generation", demo_attack_vectors),
        ("Anomaly Detection", demo_anomaly_detection),
        ("Causality Validation", demo_causality_validation),
        ("Chronos Integration", demo_chronos_integration),
        ("Atropos Integration", demo_atropos_integration),
        ("Comprehensive Report", demo_comprehensive_report),
    ]
    
    for demo_name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n✗ Error in {demo_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print_header("DEMONSTRATION COMPLETE")
    print("All temporal attack scenarios, detections, and integrations demonstrated.\n")
    print("For testing, run: python engines/tests/test_temporal_attack_enhanced.py\n")


if __name__ == "__main__":
    main()
