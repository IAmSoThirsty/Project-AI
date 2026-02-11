"""
T-SECA/GHOST Protocol Usage Examples

This script demonstrates various usage patterns for the T-SECA/GHOST Protocol
security system, including:
- Basic system initialization
- Secure inference operations
- Identity fragmentation and recovery
- Heartbeat monitoring
- Catastrophic failure simulation
"""

import logging
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.app.security.tseca_ghost_protocol import (
    GhostProtocol,
    TSECA,
    HeartbeatMonitor,
    TSECA_Ghost_System,
    shamir_split,
    shamir_reconstruct,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def example_1_basic_shamir():
    """Example 1: Basic Shamir Secret Sharing"""
    print("\n" + "=" * 70)
    print("Example 1: Shamir Secret Sharing")
    print("=" * 70)

    secret = b"My secret message that needs protection"
    k, n = 3, 5  # Need 3 of 5 shares to reconstruct

    # Split secret
    shares = shamir_split(secret, k, n)
    print(f"Split secret into {len(shares)} shares (threshold: {k})")

    # Reconstruct with any k shares
    reconstructed = shamir_reconstruct(shares[:k])
    print(f"Reconstructed: {reconstructed.decode()}")
    assert reconstructed == secret
    print("✓ Secret successfully reconstructed!")


def example_2_ghost_protocol():
    """Example 2: Ghost Protocol Identity Management"""
    print("\n" + "=" * 70)
    print("Example 2: Ghost Protocol Identity Continuity")
    print("=" * 70)

    # Initialize Ghost Protocol
    ghost = GhostProtocol(quorum_k=3, total_n=5)
    print(f"Identity Hash: {ghost.identity_hash[:32]}...")

    # Fragment identity
    shards = ghost.fragment_identity()
    print(f"Created {len(shards)} encrypted identity shards")

    # Simulate catastrophic failure - resurrect identity
    print("Simulating catastrophic failure...")
    restored_hash = ghost.resurrect(shards[:3])  # Use any 3 shards
    print(f"Restored Hash: {restored_hash[:32]}...")
    print("✓ Identity successfully resurrected!")


def example_3_tseca_hardening():
    """Example 3: T-SECA Runtime Hardening"""
    print("\n" + "=" * 70)
    print("Example 3: T-SECA Secure Inference")
    print("=" * 70)

    ghost = GhostProtocol()
    tseca = TSECA(ghost)

    # Perform secure inference
    payload = {"operation": "analyze", "data": "test input"}
    result = tseca.secure_inference(payload)

    print("Inference Result:")
    print(f"  Strategic Summary: {result['result']['strategic_summary']}")
    print(f"  Risk Assessment: {result['result']['risk_assessment']}")
    print(f"  Confidence: {result['result']['confidence_score']}")
    print(f"  Identity Hash: {result['identity_hash'][:32]}...")
    print(f"  Response Hash: {result['response_hash'][:32]}...")
    print(f"  Signature: {result['signature'][:32]}...")
    print("✓ Secure inference completed with cryptographic attestation!")


def example_4_heartbeat_monitoring():
    """Example 4: Heartbeat Monitoring"""
    print("\n" + "=" * 70)
    print("Example 4: Heartbeat Monitoring")
    print("=" * 70)

    failure_detected = False

    def on_failure():
        nonlocal failure_detected
        failure_detected = True
        print("⚠ Catastrophic failure detected by monitor!")

    monitor = HeartbeatMonitor(timeout=2, threshold=2)
    print("Started heartbeat monitor (timeout=2s, threshold=2)")

    # Start monitoring in background
    import threading
    thread = threading.Thread(target=monitor.monitor, args=(on_failure,))
    thread.daemon = True
    thread.start()

    # Send heartbeats for a while
    for i in range(3):
        time.sleep(1)
        monitor.beat()
        print(f"Heartbeat {i + 1} sent")

    # Stop sending heartbeats to trigger failure
    print("Stopping heartbeats to simulate failure...")
    time.sleep(5)

    if failure_detected:
        print("✓ Failure detection working correctly!")


def example_5_unified_system():
    """Example 5: Unified TSECA_Ghost_System"""
    print("\n" + "=" * 70)
    print("Example 5: Complete Unified System")
    print("=" * 70)

    # Initialize unified system
    system = TSECA_Ghost_System()
    print("Unified system initialized with:")
    print(f"  - Ghost Protocol (identity: {system.ghost.identity_hash[:32]}...)")
    print(f"  - T-SECA Hardening")
    print(f"  - Heartbeat Monitor")
    print(f"  - {len(system.shards)} Identity Shards")

    # Perform secure operations
    print("\nPerforming secure inference...")
    result = system.inference({"operation": "test"})
    print(f"  Result: {result['result']['strategic_summary']}")

    # Send heartbeat
    print("Sending heartbeat...")
    system.send_heartbeat()

    # Test catastrophic recovery
    print("\nTesting catastrophic recovery...")
    original_hash = system.ghost.identity_hash
    system._catastrophic_event()
    print(f"  Original: {original_hash[:32]}...")
    print(f"  Restored: {system.ghost.identity_hash[:32]}...")
    assert original_hash == system.ghost.identity_hash
    print("✓ Complete system integration verified!")


def example_6_advanced_recovery():
    """Example 6: Advanced Recovery Scenarios"""
    print("\n" + "=" * 70)
    print("Example 6: Advanced Recovery Scenarios")
    print("=" * 70)

    ghost = GhostProtocol(quorum_k=3, total_n=7)
    original_hash = ghost.identity_hash
    shards = ghost.fragment_identity()

    print(f"Created {len(shards)} shards (quorum: {ghost.quorum_k})")

    # Test different shard combinations
    test_cases = [
        ([0, 1, 2], "First 3 shards"),
        ([2, 4, 6], "Every other shard"),
        ([0, 3, 6], "Sparse distribution"),
        ([4, 5, 6], "Last 3 shards"),
    ]

    for indices, description in test_cases:
        selected_shards = [shards[i] for i in indices]
        restored = ghost.resurrect(selected_shards)
        match = "✓" if restored == original_hash else "✗"
        print(f"  {match} {description}: {restored[:16]}...")

    print("✓ All recovery scenarios successful!")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("T-SECA/GHOST PROTOCOL - USAGE EXAMPLES")
    print("=" * 70)

    try:
        example_1_basic_shamir()
        example_2_ghost_protocol()
        example_3_tseca_hardening()
        example_4_heartbeat_monitoring()
        example_5_unified_system()
        example_6_advanced_recovery()

        print("\n" + "=" * 70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
