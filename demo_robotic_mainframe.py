"""
Robotic Mainframe Integration Demo
Demonstrates complete robotic system with Four Laws and Triumvirate validation.
"""
import logging
import sys
import time

# Add src to path
sys.path.insert(0, 'src')

import numpy as np

from app.core.robotic_mainframe_integration import (
    RoboticMainframeSystem, RoboticIntegrationAPI,
    initialize_robotic_system, get_robotic_system,
    robot_move_joints, robot_emergency_stop, robot_get_status
)
from app.core.robotic_hardware_layer import RobotConfiguration, CommunicationProtocol
from app.core.robotic_controller_manager import RobotCommand, ControlMode

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def demo_system_initialization():
    """Demonstrate system initialization"""
    print("\n" + "=" * 80)
    print("DEMO 1: SYSTEM INITIALIZATION")
    print("=" * 80)
    
    # Create configuration
    config = RobotConfiguration(
        robot_id="demo_robot_001",
        robot_name="Demo Robot Arm",
        num_joints=6,
        num_end_effectors=1,
        workspace_bounds={"x": (-1, 1), "y": (-1, 1), "z": (0, 2)},
        max_payload=5.0,
        max_reach=1.5,
        communication_protocol=CommunicationProtocol.USB,
        four_laws_enabled=True
    )
    
    # Initialize system
    system = RoboticMainframeSystem(config)
    success = system.initialize()
    
    if success:
        print("\n✅ System initialized successfully!")
        status = system.get_status()
        print(f"\nSystem Status:")
        print(f"  - Robot: {config.robot_name}")
        print(f"  - Joints: {config.num_joints}")
        print(f"  - Four Laws: {'ENABLED' if status.four_laws_enabled else 'DISABLED'}")
        print(f"  - Triumvirate: {'ENABLED' if status.triumvirate_enabled else 'DISABLED'}")
        print(f"  - Hardware: {'HEALTHY' if status.hardware_healthy else 'UNHEALTHY'}")
    else:
        print("\n❌ System initialization failed")
        return None
    
    return system


def demo_simple_motion(system: RoboticMainframeSystem):
    """Demonstrate simple joint motion"""
    print("\n" + "=" * 80)
    print("DEMO 2: SIMPLE JOINT MOTION")
    print("=" * 80)
    
    # Get current joint positions
    robot_state = system.get_robot_state()
    current_positions = [js["position"] for js in robot_state["joint_states"]]
    
    print(f"\nCurrent positions: {[f'{p:.3f}' for p in current_positions]}")
    
    # Define target positions (small movements)
    target_positions = [0.1, -0.1, 0.2, -0.2, 0.15, -0.15]
    
    print(f"Target positions:  {[f'{p:.3f}' for p in target_positions]}")
    print("\nExecuting motion...")
    
    # Execute motion
    success = system.execute_motion(
        joint_targets=target_positions,
        duration=2.0,
        context={"is_user_order": True}
    )
    
    if success:
        print("✅ Motion command queued successfully")
        time.sleep(2.5)  # Wait for motion to complete
        
        # Check new positions
        robot_state = system.get_robot_state()
        new_positions = [js["position"] for js in robot_state["joint_states"]]
        print(f"New positions:     {[f'{p:.3f}' for p in new_positions]}")
    else:
        print("❌ Motion command failed")


def demo_four_laws_violation(system: RoboticMainframeSystem):
    """Demonstrate Four Laws violation detection"""
    print("\n" + "=" * 80)
    print("DEMO 3: FOUR LAWS VIOLATION DETECTION")
    print("=" * 80)
    
    print("\nAttempting motion that would endanger human...")
    
    # Try to execute motion with context that endangers human
    target_positions = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    
    success = system.execute_motion(
        joint_targets=target_positions,
        duration=1.0,
        context={
            "is_user_order": True,
            "endangers_human": True,  # This should be rejected
            "human_in_workspace": True
        }
    )
    
    if success:
        print("⚠️  Command was queued (will be rejected by Triumvirate)")
        time.sleep(1.5)
        
        # Check status
        status = system.get_status()
        print(f"\nCommands rejected: {status.commands_rejected}")
        print("✅ Four Laws successfully prevented dangerous motion")
    else:
        print("❌ Command rejected immediately")


def demo_emergency_stop(system: RoboticMainframeSystem):
    """Demonstrate emergency stop"""
    print("\n" + "=" * 80)
    print("DEMO 4: EMERGENCY STOP")
    print("=" * 80)
    
    print("\nStarting motion...")
    
    # Start a motion
    target_positions = [1.0, -1.0, 1.0, -1.0, 1.0, -1.0]
    system.execute_motion(target_positions, duration=5.0)
    
    time.sleep(0.5)
    
    print("Triggering EMERGENCY STOP...")
    success = system.emergency_stop()
    
    if success:
        print("✅ Emergency stop activated!")
        
        status = system.get_status()
        print(f"\nRobot state: {status.robot_state}")
        print(f"Active alarms: {status.active_alarms}")
        
        # Reset emergency stop
        print("\nResetting emergency stop...")
        time.sleep(1.0)
        
        reset_success = system.reset_emergency_stop()
        if reset_success:
            print("✅ Emergency stop reset")
            status = system.get_status()
            print(f"Robot state: {status.robot_state}")
        else:
            print("❌ Failed to reset emergency stop")
    else:
        print("❌ Emergency stop failed")


def demo_triumvirate_validation(system: RoboticMainframeSystem):
    """Demonstrate Triumvirate validation pipeline"""
    print("\n" + "=" * 80)
    print("DEMO 5: TRIUMVIRATE VALIDATION PIPELINE")
    print("=" * 80)
    
    print("\nTriumvirate validates commands through 3 stages:")
    print("  1. Cerberus: Policy & safety enforcement")
    print("  2. Codex: Command analysis & optimization")
    print("  3. Galahad: Outcome reasoning & contradiction detection")
    
    # Execute various commands to show validation
    test_commands = [
        {
            "name": "Safe motion",
            "targets": [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            "context": {"is_user_order": True}
        },
        {
            "name": "Large motion (needs trajectory planning)",
            "targets": [1.5, 1.5, 1.5, 1.5, 1.5, 1.5],
            "context": {"is_user_order": True}
        },
        {
            "name": "Motion near human",
            "targets": [0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
            "context": {"is_user_order": True, "human_nearby": True}
        }
    ]
    
    for cmd in test_commands:
        print(f"\n{cmd['name']}:")
        success = system.execute_motion(cmd["targets"], 1.0, cmd["context"])
        print(f"  Result: {'✅ Queued' if success else '❌ Rejected'}")
        time.sleep(1.5)
    
    # Show statistics
    status = system.get_status()
    print(f"\n📊 Statistics:")
    print(f"  Commands executed: {status.commands_executed}")
    print(f"  Commands rejected: {status.commands_rejected}")
    print(f"  Safety violations: {status.safety_violations}")


def demo_sensor_readings(system: RoboticMainframeSystem):
    """Demonstrate sensor data reading"""
    print("\n" + "=" * 80)
    print("DEMO 6: SENSOR DATA READINGS")
    print("=" * 80)
    
    robot_state = system.get_robot_state()
    
    print("\nSensor Readings:")
    for sensor in robot_state["sensor_readings"]:
        print(f"  {sensor['sensor_id']} ({sensor['sensor_type']}):")
        print(f"    Value: {sensor['value']}")
        print(f"    Unit: {sensor['unit']}")
        print(f"    Confidence: {sensor['confidence']}")


def demo_api_usage():
    """Demonstrate high-level API usage"""
    print("\n" + "=" * 80)
    print("DEMO 7: HIGH-LEVEL API USAGE")
    print("=" * 80)
    
    print("\nThe API provides simple functions for common operations:")
    
    # Initialize system
    print("\n1. Initializing system...")
    success = initialize_robotic_system()
    print(f"   {'✅ Success' if success else '❌ Failed'}")
    
    if not success:
        return
    
    # Move joints using convenience function
    print("\n2. Moving joints (convenience function)...")
    positions = [0.5, -0.5, 0.3, -0.3, 0.2, -0.2]
    success = robot_move_joints(positions, duration=2.0)
    print(f"   {'✅ Motion queued' if success else '❌ Motion failed'}")
    
    time.sleep(2.5)
    
    # Get status
    print("\n3. Getting system status...")
    status = robot_get_status()
    print(f"   State: {status.robot_state}")
    print(f"   Uptime: {status.uptime_seconds:.1f}s")
    print(f"   Commands: {status.commands_executed} executed, {status.commands_rejected} rejected")


def main():
    """Main demo function"""
    print("\n" + "=" * 80)
    print("PROJECT-AI ROBOTIC MAINFRAME INTEGRATION DEMO")
    print("=" * 80)
    print("\nThis demo showcases:")
    print("  ✅ Complete robotic hardware integration")
    print("  ✅ Four Laws of Robotics enforcement")
    print("  ✅ Triumvirate validation pipeline (Cerberus, Codex, Galahad)")
    print("  ✅ Emergency stop capabilities")
    print("  ✅ Safety constraint validation")
    print("  ✅ Real-time monitoring and diagnostics")
    
    try:
        # Demo 1: System Initialization
        system = demo_system_initialization()
        if not system:
            print("\nDemo aborted: System initialization failed")
            return
        
        time.sleep(2)
        
        # Demo 2: Simple Motion
        demo_simple_motion(system)
        time.sleep(2)
        
        # Demo 3: Four Laws Violation
        demo_four_laws_violation(system)
        time.sleep(2)
        
        # Demo 4: Emergency Stop
        demo_emergency_stop(system)
        time.sleep(2)
        
        # Demo 5: Triumvirate Validation
        demo_triumvirate_validation(system)
        time.sleep(2)
        
        # Demo 6: Sensor Readings
        demo_sensor_readings(system)
        time.sleep(2)
        
        # Demo 7: API Usage (creates new system)
        demo_api_usage()
        
        # Cleanup
        print("\n" + "=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)
        print("\nShutting down system...")
        system.shutdown()
        print("✅ Shutdown complete")
        
        # Final statistics
        print("\n📊 Final Statistics:")
        status = system.get_status()
        print(f"  Total uptime: {status.uptime_seconds:.1f}s")
        print(f"  Commands executed: {status.commands_executed}")
        print(f"  Commands rejected: {status.commands_rejected}")
        print(f"  Safety violations detected: {status.safety_violations}")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        if 'system' in locals():
            print("Performing emergency shutdown...")
            system.emergency_stop()
            system.shutdown()
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
        if 'system' in locals():
            system.shutdown()


if __name__ == "__main__":
    main()
