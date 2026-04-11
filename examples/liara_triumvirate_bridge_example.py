#                                           [2026-03-05 08:49]
#                                          Productivity: Active
"""
Example: Using the Liara-Triumvirate Bridge

Demonstrates:
- Setting up the integration bridge
- Processing requests through the bridge
- Monitoring health and triggering handoffs
- Handling automatic fallback
"""

import time
from datetime import datetime

from cognition.liara_guard import LiaraState
from kernel.liara_triumvirate_bridge import LiaraTriumvirateBridge
from src.cognition.triumvirate import Triumvirate, TriumvirateConfig


def print_separator(title: str = ""):
    """Print a visual separator"""
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)
    print()


def print_status(bridge: LiaraTriumvirateBridge):
    """Print current bridge status"""
    status = bridge.get_bridge_status()
    print(f"Mode: {status['mode']}")
    print(f"Active Controller: {status['active_controller']}")
    print(f"Handoff Count: {status['handoff_count']}")
    print(f"Health Checks: {status['health_checks']}")

    if status.get("triumvirate_health"):
        health = status["triumvirate_health"]
        print("\nTriumvirate Health:")
        print(f"  Galahad: {'✓' if health['galahad']['healthy'] else '✗'}")
        print(f"  Cerberus: {'✓' if health['cerberus']['healthy'] else '✗'}")
        print(f"  Codex: {'✓' if health['codex']['healthy'] else '✗'}")

    if status["liara_state"]["active_role"]:
        print(f"\nLiara Active Role: {status['liara_state']['active_role']}")
        print(f"Expires At: {status['liara_state']['expires_at']}")


def example_basic_usage():
    """Example 1: Basic bridge usage with healthy Triumvirate"""
    print_separator("Example 1: Basic Bridge Usage")

    # Initialize Triumvirate
    print("Initializing Triumvirate...")
    config = TriumvirateConfig()
    triumvirate = Triumvirate(config=config)

    # Initialize Liara state
    liara_state = LiaraState()

    # Create bridge
    print("Creating Liara-Triumvirate Bridge...")
    bridge = LiaraTriumvirateBridge(triumvirate=triumvirate, liara_state=liara_state)

    print("\nInitial Status:")
    print_status(bridge)

    # Process a request
    print_separator("Processing Request")
    result = bridge.process_request(
        input_data={"query": "What is the meaning of life?"},
        context={"user": "example_user"},
    )

    print(f"Success: {result['success']}")
    print(f"Controller: {result.get('controller', 'unknown')}")
    print(f"Bridge Mode: {result.get('bridge_mode', 'unknown')}")

    if result["success"]:
        print(f"Output: {result.get('output', 'N/A')}")

    print("\nFinal Status:")
    print_status(bridge)


def example_health_monitoring():
    """Example 2: Health monitoring and detection"""
    print_separator("Example 2: Health Monitoring")

    config = TriumvirateConfig()
    triumvirate = Triumvirate(config=config)
    bridge = LiaraTriumvirateBridge(triumvirate=triumvirate)

    # Monitor health
    print("Monitoring Triumvirate health...")
    health = bridge.monitor_triumvirate_health()

    print(f"Triumvirate Stable: {health.is_stable()}")
    print(f"Failed Pillars: {health.get_failed_pillars()}")

    print("\nDetailed Health:")
    print(f"  Galahad:")
    print(f"    Alive: {health.galahad.alive}")
    print(f"    Responsive: {health.galahad.responsive}")
    print(f"    Bounded: {health.galahad.bounded}")
    print(f"    Compliant: {health.galahad.compliant}")

    print(f"  Cerberus:")
    print(f"    Alive: {health.cerberus.alive}")
    print(f"    Responsive: {health.cerberus.responsive}")
    print(f"    Bounded: {health.cerberus.bounded}")
    print(f"    Compliant: {health.cerberus.compliant}")

    print(f"  Codex:")
    print(f"    Alive: {health.codex.alive}")
    print(f"    Responsive: {health.codex.responsive}")
    print(f"    Bounded: {health.codex.bounded}")
    print(f"    Compliant: {health.codex.compliant}")


def example_manual_handoff():
    """Example 3: Manual handoff to Liara"""
    print_separator("Example 3: Manual Handoff to Liara")

    config = TriumvirateConfig()
    triumvirate = Triumvirate(config=config)
    liara_state = LiaraState()
    bridge = LiaraTriumvirateBridge(triumvirate=triumvirate, liara_state=liara_state)

    print("Initial state: Triumvirate")
    print_status(bridge)

    # Simulate manual handoff (e.g., for testing or emergency)
    print_separator("Executing Manual Handoff")
    print("Triggering handoff to Liara (simulated Galahad failure)...")

    # Note: In real usage, this would be triggered by actual health degradation
    # For demo purposes, we'll show the capability mapping
    capabilities = bridge.map_triumvirate_capabilities_to_liara("galahad")

    print("\nLiara will substitute Galahad with restrictions:")
    for key, value in capabilities.items():
        print(f"  {key}: {value}")

    print("\nIn production, handoff would be triggered automatically by health monitoring")


def example_capability_mapping():
    """Example 4: Capability mapping for each pillar"""
    print_separator("Example 4: Capability Mapping")

    bridge = LiaraTriumvirateBridge()

    pillars = ["galahad", "cerberus", "codex"]

    for pillar in pillars:
        print(f"\n{pillar.upper()} -> Liara Restrictions:")
        capabilities = bridge.map_triumvirate_capabilities_to_liara(pillar)

        for key, value in capabilities.items():
            print(f"  {key}: {value}")


def example_state_synchronization():
    """Example 5: State synchronization"""
    print_separator("Example 5: State Synchronization")

    config = TriumvirateConfig()
    triumvirate = Triumvirate(config=config)
    liara_state = LiaraState()
    bridge = LiaraTriumvirateBridge(triumvirate=triumvirate, liara_state=liara_state)

    # Capture states
    print("Capturing Triumvirate state...")
    triumvirate_state = bridge._capture_triumvirate_state()

    print("\nTriumvirate State Keys:")
    for key in triumvirate_state.keys():
        print(f"  - {key}")

    print("\nCapturing Liara state...")
    liara_state_snapshot = bridge._capture_liara_state()

    print("\nLiara State Keys:")
    for key in liara_state_snapshot.keys():
        print(f"  - {key}")

    print("\nSync Data (shared between systems):")
    for key, value in bridge.state.sync_data.items():
        print(f"  {key}: {str(value)[:50]}...")


def example_processing_workflow():
    """Example 6: Complete processing workflow"""
    print_separator("Example 6: Complete Processing Workflow")

    config = TriumvirateConfig()
    triumvirate = Triumvirate(config=config)
    liara_state = LiaraState()
    bridge = LiaraTriumvirateBridge(triumvirate=triumvirate, liara_state=liara_state)

    # Process multiple requests
    requests = [
        {"query": "Analyze security policy", "priority": "high"},
        {"query": "Generate report", "priority": "medium"},
        {"query": "Validate input data", "priority": "low"},
    ]

    print("Processing multiple requests through the bridge...\n")

    for i, req in enumerate(requests, 1):
        print(f"Request {i}: {req['query']}")

        # Check health before processing
        health = bridge.monitor_triumvirate_health()
        print(f"  System Health: {'Healthy' if health.is_stable() else 'Degraded'}")

        # Process request
        result = bridge.process_request(req, context={"request_id": i})

        print(f"  Controller: {result.get('controller', 'unknown')}")
        print(f"  Success: {result['success']}")

        if not result["success"]:
            print(f"  Error: {result.get('error', 'Unknown error')}")

        print()

    # Final status
    print_separator("Final Bridge Status")
    print_status(bridge)


def main():
    """Run all examples"""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                 Liara-Triumvirate Bridge Examples                          ║
║                                                                            ║
║  Demonstrating seamless integration between Liara and Triumvirate         ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)

    try:
        # Run examples
        example_basic_usage()
        example_health_monitoring()
        example_manual_handoff()
        example_capability_mapping()
        example_state_synchronization()
        example_processing_workflow()

        print_separator("Examples Complete")
        print("All examples completed successfully!")
        print("\nKey Takeaways:")
        print("  ✓ Bridge provides transparent integration between systems")
        print("  ✓ Health monitoring enables automatic handoffs")
        print("  ✓ State synchronization maintains consistency")
        print("  ✓ Capability mapping enforces Liara restrictions")
        print("  ✓ Processing is seamless regardless of active controller")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
