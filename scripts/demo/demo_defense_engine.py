#!/usr/bin/env python3
"""
Defense Engine Demonstration Script
Project-AI God Tier Zombie Apocalypse Defense Engine

Demonstrates the complete functionality of the defense engine including:
- Bootstrap initialization
- Subsystem coordination
- Threat detection and response
- Resource management
- Emergency protocols
"""

import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


from src.app.defense_engine import DefenseEngine

from src.app.core.interface_abstractions import OperationalMode

# Configure logging for demo
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def print_banner(text: str):
    """Print a formatted banner."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def demo_basic_initialization():
    """Demonstrate basic initialization."""
    print_banner("DEMO 1: Basic Initialization")

    print("Creating Defense Engine instance...")
    engine = DefenseEngine(
        config_path="config/defense_engine.toml",
        operational_mode=OperationalMode.NORMAL,
    )

    print("Initializing all subsystems...")
    success = engine.initialize()

    if success:
        print("✅ Defense Engine initialized successfully!")

        # Get status
        status = engine.get_status()
        print(f"\nTotal Subsystems: {status['total_subsystems']}")
        print(f"Subsystems by State: {status['subsystems_by_state']}")

        engine.shutdown()
        return True
    else:
        print("❌ Initialization failed")
        return False


def demo_situational_awareness():
    """Demonstrate situational awareness capabilities."""
    print_banner("DEMO 2: Situational Awareness")

    engine = DefenseEngine()
    if not engine.initialize():
        print("❌ Failed to initialize")
        return False

    # Get situational awareness subsystem
    sa_subsystem = engine.get_subsystem("situational_awareness")

    if sa_subsystem:
        print("✅ Situational Awareness subsystem loaded")

        # Register a sensor
        print("\nRegistering thermal sensor...")
        sa_subsystem.register_sensor(
            sensor_id="thermal_001",
            sensor_type="thermal_camera",
            metadata={"location": [37.7749, -122.4194], "range_meters": 500},
        )

        # Ingest sensor data
        print("Ingesting sensor data...")
        sa_subsystem.ingest_sensor_data(
            sensor_id="thermal_001",
            data={
                "movement_detected": True,
                "confidence": 0.85,
                "speed": 5.0,
                "size": 1.2,
                "behavior": "aggressive",
                "location": [37.7750, -122.4195],
            },
        )

        # Get fused state
        import time

        time.sleep(2)  # Wait for fusion

        fused_state = sa_subsystem.get_fused_state()
        print("\n📊 Fused State:")
        print(f"   Threat Level: {fused_state.get('overall_threat_level')}")
        print(f"   Active Threats: {fused_state.get('active_threats')}")
        print(f"   Sensor Count: {fused_state.get('sensor_count')}")

        # Get metrics
        metrics = sa_subsystem.get_metrics()
        print("\n📈 Metrics:")
        print(f"   Sensor Data Ingested: {metrics['sensor_data_ingested']}")
        print(f"   Threats Detected: {metrics['threats_detected']}")
        print(f"   Fusion Cycles: {metrics['fusion_cycles']}")
    else:
        print("❌ Situational Awareness subsystem not found")

    engine.shutdown()
    return True


def demo_command_control():
    """Demonstrate command and control capabilities."""
    print_banner("DEMO 3: Command & Control")

    engine = DefenseEngine()
    if not engine.initialize():
        print("❌ Failed to initialize")
        return False

    # Get command control subsystem
    cc_subsystem = engine.get_subsystem("command_control")

    if cc_subsystem:
        print("✅ Command & Control subsystem loaded")

        # Create a mission
        print("\nCreating rescue mission...")
        response = engine.execute_command(
            subsystem_id="command_control",
            command_type="create_mission",
            parameters={
                "mission_id": "rescue_001",
                "mission_type": "rescue",
                "priority": 8,
                "objective": "Extract survivors from Zone Alpha",
                "resources": ["team_1", "vehicle_1"],
                "deadline_hours": 24,
            },
        )

        if response.get("success"):
            print(f"✅ Mission created: {response.get('result')}")
        else:
            print(f"❌ Mission creation failed: {response.get('error')}")

        # Get mission status
        response = engine.execute_command(
            subsystem_id="command_control",
            command_type="get_mission",
            parameters={"mission_id": "rescue_001"},
        )

        if response.get("success"):
            mission = response.get("result", {}).get("mission")
            print("\n📋 Mission Status:")
            print(f"   ID: {mission.get('mission_id')}")
            print(f"   Status: {mission.get('status')}")
            print(f"   Priority: {mission.get('priority')}")
    else:
        print("❌ Command & Control subsystem not found")

    engine.shutdown()
    return True


def demo_operational_modes():
    """Demonstrate operational mode transitions."""
    print_banner("DEMO 4: Operational Modes")

    engine = DefenseEngine()
    if not engine.initialize():
        print("❌ Failed to initialize")
        return False

    print("Testing operational mode transitions...")

    modes = [
        (OperationalMode.NORMAL, "Normal operation"),
        (OperationalMode.AIR_GAPPED, "Air-gapped, no external connectivity"),
        (OperationalMode.ADVERSARIAL, "Under attack, maximum security"),
        (OperationalMode.EMERGENCY, "Emergency protocols active"),
    ]

    for mode, description in modes:
        print(f"\n🔄 Switching to {mode.value.upper()} mode")
        print(f"   {description}")
        engine._set_operational_mode(mode)

        import time

        time.sleep(0.5)

        print("✅ Mode transition complete")

    engine.shutdown()
    return True


def demo_system_status():
    """Demonstrate system status monitoring."""
    print_banner("DEMO 5: System Status & Monitoring")

    engine = DefenseEngine()
    if not engine.initialize():
        print("❌ Failed to initialize")
        return False

    print("Retrieving comprehensive system status...\n")

    status = engine.get_status()

    print("📊 SYSTEM STATUS")
    print(f"   Timestamp: {status.get('timestamp')}")
    print(f"   Total Subsystems: {status.get('total_subsystems')}")
    print(
        f"   Health Monitoring: {'Active' if status.get('health_monitoring_active') else 'Inactive'}"
    )

    print("\n🔢 Subsystems by State:")
    for state, count in status.get("subsystems_by_state", {}).items():
        if count > 0:
            print(f"   {state.upper()}: {count}")

    print("\n⚡ Subsystems by Priority:")
    for priority, count in status.get("subsystems_by_priority", {}).items():
        if count > 0:
            print(f"   {priority.upper()}: {count}")

    print("\n🎯 Available Capabilities:")
    capabilities = status.get("capabilities", [])
    for cap in capabilities[:10]:  # Show first 10
        print(f"   • {cap}")

    if len(capabilities) > 10:
        print(f"   ... and {len(capabilities) - 10} more")

    engine.shutdown()
    return True


def run_all_demos():
    """Run all demonstration scenarios."""
    print("\n" + "=" * 80)
    print("  PROJECT-AI GOD TIER ZOMBIE APOCALYPSE DEFENSE ENGINE")
    print("  Demonstration Suite")
    print("=" * 80)

    demos = [
        ("Basic Initialization", demo_basic_initialization),
        ("Situational Awareness", demo_situational_awareness),
        ("Command & Control", demo_command_control),
        ("Operational Modes", demo_operational_modes),
        ("System Status", demo_system_status),
    ]

    results = []

    for name, demo_func in demos:
        try:
            success = demo_func()
            results.append((name, success))
        except Exception as e:
            logger.error("Demo '%s' failed with exception: %s", name, e, exc_info=True)
            results.append((name, False))

    # Print summary
    print_banner("DEMONSTRATION SUMMARY")

    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}  {name}")

    total = len(results)
    passed = sum(1 for _, success in results if success)

    print(f"\n{'=' * 80}")
    print(f"Results: {passed}/{total} demonstrations completed successfully")
    print(f"{'=' * 80}\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_demos()
    sys.exit(0 if success else 1)
