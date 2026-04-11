#!/usr/bin/env python3
"""
Chronos Temporal Weight Engine - Demonstration

This script demonstrates the capabilities of Chronos, one of "The Fates" 
temporal agents. It shows causality tracking, weight assignment, consistency
verification, and anomaly detection.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timezone, timedelta
import json

from src.cognition.temporal import Chronos


def print_separator(title=""):
    """Print a section separator."""
    print("\n" + "=" * 70)
    if title:
        print(f"  {title}")
        print("=" * 70)
    print()


def demo_basic_usage():
    """Demonstrate basic event tracking."""
    print_separator("Basic Event Tracking")
    
    chronos = Chronos("demo-chronos", enable_audit=False)
    
    # Record a series of events
    print("Recording events...")
    e1 = chronos.record_event("e1", "data_ingestion", "sensor_agent", 
                               data={"source": "sensor_a", "value": 42})
    print(f"  ✓ Event e1 recorded (weight: {e1.temporal_weight:.2f})")
    
    e2 = chronos.record_event("e2", "data_validation", "validator_agent",
                               causes=["e1"],
                               data={"status": "valid"})
    print(f"  ✓ Event e2 recorded (weight: {e2.temporal_weight:.2f})")
    
    e3 = chronos.record_event("e3", "data_processing", "processor_agent",
                               causes=["e2"],
                               data={"algorithm": "filter", "result": 38})
    print(f"  ✓ Event e3 recorded (weight: {e3.temporal_weight:.2f})")
    
    e4 = chronos.record_event("e4", "data_storage", "storage_agent",
                               causes=["e3"],
                               data={"location": "db_primary"})
    print(f"  ✓ Event e4 recorded (weight: {e4.temporal_weight:.2f})")
    
    # Show causal chain
    print(f"\nCausal chain to e4: {' -> '.join(chronos.get_causal_chain('e4'))}")
    
    # Show vector clocks
    print("\nVector clocks:")
    for event_id in ["e1", "e2", "e3", "e4"]:
        event = chronos.events[event_id]
        print(f"  {event_id}: {event.vector_clock}")


def demo_distributed_tracking():
    """Demonstrate tracking across multiple agents."""
    print_separator("Distributed Multi-Agent Tracking")
    
    chronos = Chronos("demo-distributed", enable_audit=False)
    
    print("Simulating distributed workflow...\n")
    
    # Service A starts processing
    chronos.record_event("req_1", "request_received", "service_a",
                        data={"endpoint": "/api/users"})
    print("  📥 Service A receives request")
    
    # Service A queries database
    chronos.record_event("db_1", "database_query", "service_a",
                        causes=["req_1"],
                        data={"query": "SELECT * FROM users"})
    print("  🗄️  Service A queries database")
    
    # Service A calls Service B
    chronos.record_event("call_b", "service_call", "service_a",
                        causes=["db_1"],
                        data={"target": "service_b"})
    print("  📞 Service A calls Service B")
    
    # Service B processes
    chronos.record_event("proc_b", "processing", "service_b",
                        causes=["call_b"],
                        data={"action": "enrichment"})
    print("  ⚙️  Service B processes request")
    
    # Service B calls Service C
    chronos.record_event("call_c", "service_call", "service_b",
                        causes=["proc_b"],
                        data={"target": "service_c"})
    print("  📞 Service B calls Service C")
    
    # Service C processes
    chronos.record_event("proc_c", "processing", "service_c",
                        causes=["call_c"],
                        data={"action": "validation"})
    print("  ✅ Service C validates data")
    
    # Response flows back
    chronos.record_event("resp_1", "response_sent", "service_a",
                        causes=["proc_c"],
                        data={"status": 200})
    print("  📤 Service A sends response\n")
    
    # Show statistics
    stats = chronos.get_statistics()
    print(f"Statistics:")
    print(f"  Total events: {stats['total_events']}")
    print(f"  Active agents: {stats['active_agents']}")
    print(f"  Max depth: {stats['graph_stats']['max_depth']}")
    
    # Show causal chain
    chain = chronos.get_causal_chain("resp_1")
    print(f"\nComplete request trace:")
    for i, event_id in enumerate(chain, 1):
        event = chronos.events[event_id]
        print(f"  {i}. {event_id} ({event.event_type}) - agent: {event.agent_id}")


def demo_branching_causality():
    """Demonstrate branching and merging causal patterns."""
    print_separator("Branching and Merging Causality")
    
    chronos = Chronos("demo-branching", enable_audit=False)
    
    print("Creating branching workflow...\n")
    
    # Start event
    chronos.record_event("start", "job_start", "orchestrator",
                        data={"job_id": "job_123"})
    print("  🚀 Job started")
    
    # Branch into parallel tasks
    chronos.record_event("task_a", "parallel_task", "worker_1",
                        causes=["start"],
                        data={"task": "transform_data"})
    print("  📊 Task A: Data transformation (worker_1)")
    
    chronos.record_event("task_b", "parallel_task", "worker_2",
                        causes=["start"],
                        data={"task": "validate_schema"})
    print("  📋 Task B: Schema validation (worker_2)")
    
    chronos.record_event("task_c", "parallel_task", "worker_3",
                        causes=["start"],
                        data={"task": "check_permissions"})
    print("  🔐 Task C: Permission check (worker_3)")
    
    # Merge results
    chronos.record_event("merge", "merge_results", "orchestrator",
                        causes=["task_a", "task_b", "task_c"],
                        data={"status": "all_complete"})
    print("  ✨ Results merged")
    
    chronos.record_event("complete", "job_complete", "orchestrator",
                        causes=["merge"],
                        data={"result": "success"})
    print("  ✅ Job completed\n")
    
    # Show concurrent events
    concurrent_with_a = chronos.get_concurrent_events("task_a")
    print(f"Events concurrent with task_a: {concurrent_with_a}")
    
    # Show weights
    print("\nTemporal weights:")
    for event_id in ["start", "task_a", "task_b", "task_c", "merge", "complete"]:
        weight = chronos.temporal_weights[event_id]
        print(f"  {event_id:12s}: {weight:.2f}")
    
    print("\nNote: 'start' has highest weight (many descendants)")
    print("      'merge' has moderate weight (combines multiple branches)")


def demo_consistency_verification():
    """Demonstrate temporal consistency verification."""
    print_separator("Temporal Consistency Verification")
    
    chronos = Chronos("demo-consistency", enable_audit=False)
    
    print("Recording events with proper causality...\n")
    
    chronos.record_event("e1", "event_1", "agent1")
    chronos.record_event("e2", "event_2", "agent1", causes=["e1"])
    chronos.record_event("e3", "event_3", "agent2", causes=["e2"])
    
    print("Verifying consistency...")
    is_consistent, violations = chronos.verify_consistency()
    
    if is_consistent:
        print("  ✅ Temporal consistency verified")
        print("  - No cycles detected")
        print("  - Vector clocks align with causality")
        print("  - Wall-clock times are consistent")
    else:
        print("  ❌ Consistency violations detected:")
        for violation in violations:
            print(f"    - {violation}")


def demo_drift_detection():
    """Demonstrate clock drift detection."""
    print_separator("Clock Drift Detection")
    
    # Set a low threshold to demonstrate drift
    chronos = Chronos("demo-drift", enable_audit=False, drift_threshold_seconds=2.0)
    
    print("Recording events with time gaps...\n")
    
    now = datetime.now(timezone.utc)
    
    chronos.record_event("e1", "event_1", "agent1", timestamp=now)
    print(f"  Event e1 recorded at {now.strftime('%H:%M:%S.%f')[:-3]}")
    
    # Small gap - no drift
    later1 = now + timedelta(seconds=1.5)
    chronos.record_event("e2", "event_2", "agent1", causes=["e1"], timestamp=later1)
    print(f"  Event e2 recorded at {later1.strftime('%H:%M:%S.%f')[:-3]} (+1.5s)")
    
    # Large gap - drift detected
    later2 = later1 + timedelta(seconds=5.0)
    chronos.record_event("e3", "event_3", "agent1", causes=["e2"], timestamp=later2)
    print(f"  Event e3 recorded at {later2.strftime('%H:%M:%S.%f')[:-3]} (+5.0s)")
    
    print(f"\nDrift violations detected: {len(chronos.drift_violations)}")
    for violation in chronos.drift_violations:
        print(f"  ⚠️  {violation['cause_id']} -> {violation['event_id']}: "
              f"{violation['time_diff_seconds']:.1f}s (threshold: {violation['threshold']:.1f}s)")


def demo_anomaly_detection():
    """Demonstrate temporal anomaly detection."""
    print_separator("Anomaly Detection")
    
    chronos = Chronos("demo-anomalies", enable_audit=False)
    
    print("Creating event patterns...\n")
    
    # Create a highly branched event (high weight)
    chronos.record_event("critical", "critical_decision", "orchestrator")
    
    for i in range(5):
        chronos.record_event(f"branch_{i}", "downstream_task", f"worker_{i}",
                           causes=["critical"])
    
    # Create normal events
    chronos.record_event("normal_1", "regular_task", "worker_a")
    chronos.record_event("normal_2", "regular_task", "worker_b")
    
    # Create security event
    chronos.record_event("security", "security_violation", "security_agent",
                        causes=["branch_2"])
    
    print("Detecting anomalies...\n")
    anomalies = chronos.detect_anomalies()
    
    for anomaly in anomalies:
        if anomaly["type"] == "high_temporal_weight":
            print(f"  🔴 High temporal weight detected:")
            print(f"     Event: {anomaly['event_id']}")
            print(f"     Weight: {anomaly['weight']:.2f} (threshold: {anomaly['threshold']:.2f})")
    
    print(f"\nTotal anomalies detected: {len(anomalies)}")


def demo_state_persistence():
    """Demonstrate state save/load."""
    print_separator("State Persistence")
    
    state_file = Path("./chronos_demo_state.json")
    
    print("Creating Chronos instance and recording events...\n")
    chronos1 = Chronos("demo-persist", enable_audit=False, state_file=state_file)
    
    chronos1.record_event("e1", "event_1", "agent1")
    chronos1.record_event("e2", "event_2", "agent2", causes=["e1"])
    chronos1.record_event("e3", "event_3", "agent3", causes=["e2"])
    
    print(f"Recorded {chronos1.event_count} events")
    
    # Save state
    chronos1.save_state()
    print(f"  ✅ State saved to {state_file}")
    
    # Create new instance and load
    print("\nCreating new Chronos instance and loading state...\n")
    chronos2 = Chronos("demo-persist", enable_audit=False, state_file=state_file)
    
    print(f"Loaded {chronos2.event_count} events")
    print(f"  Events: {list(chronos2.events.keys())}")
    print(f"  Agents: {list(chronos2.agent_clocks.keys())}")
    
    # Cleanup
    if state_file.exists():
        state_file.unlink()
        print(f"\n  🗑️  Cleaned up demo state file")


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║        CHRONOS - Temporal Weight Engine Demonstration           ║")
    print("║               One of 'The Fates' Temporal Agents                ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    
    demo_basic_usage()
    demo_distributed_tracking()
    demo_branching_causality()
    demo_consistency_verification()
    demo_drift_detection()
    demo_anomaly_detection()
    demo_state_persistence()
    
    print_separator("Demonstration Complete")
    print("Chronos successfully demonstrated:")
    print("  ✅ Causality tracking with vector clocks")
    print("  ✅ Distributed multi-agent event tracking")
    print("  ✅ Branching and merging causal patterns")
    print("  ✅ Temporal weight assignment")
    print("  ✅ Consistency verification")
    print("  ✅ Clock drift detection")
    print("  ✅ Anomaly detection")
    print("  ✅ State persistence")
    print()


if __name__ == "__main__":
    main()
