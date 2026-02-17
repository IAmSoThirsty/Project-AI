"""
SASE Example Usage

Demonstrates end-to-end adversarial telemetry processing
"""

import logging
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)


def main():
    """Run SASE example"""
    from cerberus.sase.core.substrate import DeploymentTopology
    from cerberus.sase.sase_orchestrator import SASEOrchestrator

    print("=" * 70)
    print(" SASE - Sovereign Adversarial Signal Engine - EXAMPLE")
    print("=" * 70)
    print()

    # Initialize SASE
    print("Initializing SASE orchestrator...")
    sase = SASEOrchestrator(
        deployment=DeploymentTopology.SINGLE_NODE, node_id="example-node-1"
    )
    print("✓ SASE initialized\n")

    # Example telemetry events
    test_events = [
        {
            "name": "Benign Traffic",
            "telemetry": {
                "source_ip": "192.168.1.100",
                "asn": "AS15169",  # Google
                "artifact_type": "HTTP_CALLBACK",
                "artifact_id": "token_benign_001",
                "payload_hash": "sha256:abc123",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "geo": {"country": "US", "city": "Mountain View"},
            },
            "expected": "LOW confidence",
        },
        {
            "name": "Suspicious Tor Traffic",
            "telemetry": {
                "source_ip": "185.220.101.1",  # Tor exit node
                "asn": "AS12345",
                "artifact_type": "CREDENTIAL_MISUSE",
                "artifact_id": "token_sensitive_999",
                "payload_hash": "sha256:def456",
                "user_agent": "curl/7.68.0",
                "geo": {"country": "NL", "city": "Amsterdam"},
            },
            "expected": "HIGH confidence",
        },
        {
            "name": "Cloud VPS Enumeration",
            "telemetry": {
                "source_ip": "54.201.123.45",
                "asn": "AS16509",  # AWS
                "artifact_type": "API_MISUSE",
                "artifact_id": "api_key_789",
                "payload_hash": "sha256:ghi789",
                "user_agent": "python-requests/2.25.1",
                "geo": {"country": "US", "city": "Ashburn"},
            },
            "expected": "MEDIUM-HIGH confidence",
        },
    ]

    # Process each event
    for i, test in enumerate(test_events, 1):
        print(f"\n{'=' * 70}")
        print(f"Test Event {i}: {test['name']}")
        print(f"Expected: {test['expected']}")
        print(f"{'=' * 70}\n")

        result = sase.process_telemetry(test["telemetry"])

        if result.get("success"):
            print(f"\n✓ Processing successful")
            print(f"  Event ID: {result['event_id']}")
            print(f"  Confidence: {result['confidence']['confidence_percentage']}%")
            print(f"  Threat Class: {result['confidence']['threat_classification']}")
            print(f"  Actor Type: {result['threat_class']['actor_class']}")
            print(f"  Risk Level: {result['threat_class']['risk_level']}/10")
            print(f"  Detection Time: {result['detection_time_ms']}ms")

            if result.get("behavior_state"):
                print(f"  Behavioral State: {result['behavior_state']}")
        else:
            print(f"\n✗ Processing failed: {result.get('error')}")

        print()

    # System status
    print("\n" + "=" * 70)
    print("SASE System Status")
    print("=" * 70)

    status = sase.get_system_status()
    print(f"\nSubstrate Health: {status['substrate']['status']}")
    print(f"Events Processed: {status['events_processed']}")
    print(f"Raft State: {status['raft_state']}")

    print("\n" + "=" * 70)
    print("SASE Example Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
