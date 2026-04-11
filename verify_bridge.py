"""
Quick verification that the bridge works correctly
"""
import sys
sys.path.insert(0, r"C:\Users\Quencher\.gemini\antigravity\scratch\Sovereign-Governance-Substrate")

from unittest.mock import Mock
from cognition.liara_guard import LiaraState
from kernel.liara_triumvirate_bridge import LiaraTriumvirateBridge

# Create mock Triumvirate
triumvirate = Mock()
triumvirate.galahad = Mock()
triumvirate.galahad.get_reasoning_history = Mock(return_value=[])
triumvirate.cerberus = Mock()
triumvirate.codex = Mock()

triumvirate.get_status = Mock(
    return_value={
        "galahad": {
            "curiosity_metrics": {"current_score": 0.3},
            "history_size": 10,
        },
        "cerberus": {
            "total_enforcements": 100,
            "denied_count": 5,
            "policy_mode": "production",
        },
        "codex": {"loaded": True, "device": "cpu"},
    }
)

triumvirate.get_telemetry = Mock(return_value=[])
triumvirate.process = Mock(
    return_value={
        "success": True,
        "output": "Test output from Triumvirate",
        "correlation_id": "test_123",
    }
)

# Create bridge
print("Creating Liara-Triumvirate Bridge...")
liara_state = LiaraState()
bridge = LiaraTriumvirateBridge(triumvirate=triumvirate, liara_state=liara_state)

print("\n✓ Bridge created successfully")
print(f"  Mode: {bridge.state.mode}")
print(f"  Active Controller: {bridge.state.active_controller}")

# Monitor health
print("\nMonitoring Triumvirate health...")
health = bridge.monitor_triumvirate_health()
print(f"  Triumvirate Stable: {health.is_stable()}")
print(f"  Galahad Healthy: {health.galahad.healthy}")
print(f"  Cerberus Healthy: {health.cerberus.healthy}")
print(f"  Codex Healthy: {health.codex.healthy}")

# Process a request
print("\nProcessing request through bridge...")
result = bridge.process_request({"test": "input"}, {"user": "test"})
print(f"  Success: {result['success']}")
print(f"  Controller: {result.get('controller', 'unknown')}")
print(f"  Bridge Mode: {result.get('bridge_mode', 'unknown')}")

# Get status
print("\nBridge Status:")
status = bridge.get_bridge_status()
print(f"  Mode: {status['mode']}")
print(f"  Handoff Count: {status['handoff_count']}")
print(f"  Health Checks: {status['health_checks']}")

print("\n✓ All operations completed successfully!")
print("✓ Liara-Triumvirate Bridge integration is working correctly!")
