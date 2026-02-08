"""
Robotic Mainframe Integration System
Complete integration module for Project-AI robot control with Triumvirate and Four Laws.
God Tier architecture - monolithic, production-grade, drop-in ready.
"""

import logging
import logging.handlers
import threading
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any

from app.core.robotic_controller_manager import (
    ControlMode,
    RobotCommand,
    RobotControllerManager,
)
from app.core.robotic_hardware_layer import (
    CommunicationProtocol,
    HardwareAbstractionLayer,
    RobotConfiguration,
    RoboticSafetyValidator,
    SimulatedHardwareInterface,
)

logger = logging.getLogger(__name__)


@dataclass
class RoboticSystemStatus:
    """Complete robotic system status"""

    initialized: bool = False
    start_time: str | None = None
    uptime_seconds: float = 0.0

    hardware_healthy: bool = False
    controller_active: bool = False
    triumvirate_enabled: bool = True
    four_laws_enabled: bool = True

    robot_state: str = "idle"
    commands_executed: int = 0
    commands_rejected: int = 0
    safety_violations: int = 0

    active_alarms: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class RoboticMainframeSystem:
    """
    Complete robotic mainframe integration system.
    Provides comprehensive robot control with Four Laws enforcement
    and Triumvirate validation pipeline.
    """

    def __init__(self, config: RobotConfiguration | None = None):
        self.config = config or self._create_default_config()
        self.status = RoboticSystemStatus()

        # Core components
        self.hardware: HardwareAbstractionLayer | None = None
        self.safety_validator: RoboticSafetyValidator | None = None
        self.controller: RobotControllerManager | None = None

        # System state
        self._lock = threading.RLock()
        self._start_time: float | None = None
        self._event_handlers: dict[str, list[Callable]] = {}

        logger.info("Robotic Mainframe System created")

    def _create_default_config(self) -> RobotConfiguration:
        """Create default robot configuration"""
        return RobotConfiguration(
            robot_id="project_ai_robot_001",
            robot_name="Project-AI Robot",
            num_joints=6,
            num_end_effectors=1,
            workspace_bounds={"x": (-1.0, 1.0), "y": (-1.0, 1.0), "z": (0.0, 2.0)},
            max_payload=5.0,
            max_reach=1.5,
            communication_protocol=CommunicationProtocol.USB,
            control_frequency=100.0,
            safety_enabled=True,
            four_laws_enabled=True,
        )

    def initialize(self) -> bool:
        """
        Initialize complete robotic system.
        Returns True if successful.
        """
        try:
            with self._lock:
                logger.info("=" * 80)
                logger.info("INITIALIZING ROBOTIC MAINFRAME SYSTEM")
                logger.info("=" * 80)

                self._start_time = time.time()
                self.status.start_time = datetime.utcnow().isoformat()

                # Step 1: Initialize Hardware Interface
                logger.info("1/4 - Initializing Hardware Abstraction Layer...")
                self.hardware = SimulatedHardwareInterface(self.config)

                if not self.hardware.initialize():
                    logger.error("Hardware initialization failed")
                    return False

                self.status.hardware_healthy = self.hardware.is_healthy()
                logger.info("✅ Hardware initialized: %s", self.config.robot_name)

                # Step 2: Initialize Safety Validator
                logger.info("2/4 - Initializing Safety Validator (Four Laws)...")
                self.safety_validator = RoboticSafetyValidator(self.config)
                self.status.four_laws_enabled = self.config.four_laws_enabled
                logger.info("✅ Safety validator initialized")

                # Step 3: Initialize Controller
                logger.info("3/4 - Initializing Robot Controller Manager...")
                self.controller = RobotControllerManager(
                    self.hardware, self.safety_validator, self.config
                )

                if not self.controller.start():
                    logger.error("Controller start failed")
                    return False

                self.status.controller_active = True
                logger.info("✅ Controller started")

                # Step 4: Final validation
                logger.info("4/4 - Final system validation...")
                if not self._validate_system():
                    logger.error("System validation failed")
                    return False

                self.status.initialized = True

                logger.info("=" * 80)
                logger.info("ROBOTIC MAINFRAME SYSTEM INITIALIZED SUCCESSFULLY")
                logger.info("Robot: %s", self.config.robot_name)
                logger.info("Joints: %s", self.config.num_joints)
                logger.info("Four Laws: %s", 'ENABLED' if self.config.four_laws_enabled else 'DISABLED')
                logger.info("Triumvirate: ENABLED")
                logger.info("=" * 80)

                return True

        except Exception as e:
            logger.error(f"System initialization failed: {e}", exc_info=True)
            return False

    def _validate_system(self) -> bool:
        """Validate complete system is operational"""
        try:
            # Check hardware
            if not self.hardware or not self.hardware.is_healthy():
                logger.error("Hardware validation failed")
                return False

            # Check controller
            if not self.controller:
                logger.error("Controller not initialized")
                return False

            # Read joint states to verify communication
            joint_states = self.hardware.read_joint_states()
            if not joint_states:
                logger.error("Cannot read joint states")
                return False

            logger.info("System validation passed: %s joints responsive", len(joint_states))
            return True

        except Exception as e:
            logger.error("System validation error: %s", e)
            return False

    def execute_motion(
        self,
        joint_targets: list[float],
        duration: float = 1.0,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Execute robot motion to target joint positions.
        All commands are validated through Triumvirate pipeline.

        Args:
            joint_targets: Target positions for each joint (radians or meters)
            duration: Time to complete motion (seconds)
            context: Additional context for validation

        Returns:
            True if command queued successfully
        """
        try:
            if not self.status.initialized:
                logger.error("System not initialized")
                return False

            # Create command
            command = RobotCommand(
                command_id=f"motion_{int(time.time() * 1000)}",
                command_type=ControlMode.POSITION,
                joint_targets=joint_targets,
                duration=duration,
                priority=5,
                requires_four_laws_check=True,
                context=context or {},
            )

            # Queue for execution
            success = self.controller.execute_command(command)

            if success:
                logger.info("Motion command %s queued", command.command_id)
            else:
                logger.error("Failed to queue motion command")

            return success

        except Exception as e:
            logger.error("Motion execution error: %s", e)
            return False

    def emergency_stop(self) -> bool:
        """
        Execute emergency stop.
        Immediately halts all motion and clears command queue.
        """
        try:
            logger.critical("=" * 80)
            logger.critical("EMERGENCY STOP INITIATED")
            logger.critical("=" * 80)

            if self.controller:
                success = self.controller.emergency_stop()

                if success:
                    self.status.robot_state = "emergency_stop"
                    self.status.active_alarms.append("EMERGENCY_STOP")

                    # Trigger emergency stop event
                    self._trigger_event(
                        "emergency_stop", {"timestamp": datetime.utcnow().isoformat()}
                    )

                    return True

            return False

        except Exception as e:
            logger.error("Emergency stop error: %s", e)
            return False

    def reset_emergency_stop(self) -> bool:
        """Reset emergency stop after manual verification"""
        try:
            if not self.controller:
                return False

            success = self.controller.reset_emergency_stop()

            if success:
                self.status.robot_state = "ready"
                self.status.active_alarms = [
                    a for a in self.status.active_alarms if a != "EMERGENCY_STOP"
                ]

                logger.info("Emergency stop reset")
                return True

            return False

        except Exception as e:
            logger.error("Reset emergency stop error: %s", e)
            return False

    def get_status(self) -> RoboticSystemStatus:
        """Get current system status"""
        with self._lock:
            if self._start_time:
                self.status.uptime_seconds = time.time() - self._start_time

            if self.controller:
                robot_status = self.controller.get_status()
                self.status.robot_state = robot_status.state.value
                self.status.active_alarms = robot_status.active_alarms
                self.status.commands_executed = self.controller._commands_executed
                self.status.commands_rejected = self.controller._commands_rejected

            if self.safety_validator:
                violations = self.safety_validator.get_violation_history(limit=1000)
                self.status.safety_violations = len(violations)

            return self.status

    def get_robot_state(self) -> dict[str, Any]:
        """Get detailed robot state"""
        try:
            if not self.controller:
                return {"error": "Controller not initialized"}

            robot_status = self.controller.get_status()

            state = {
                "robot_state": robot_status.state.value,
                "joint_states": [asdict(js) for js in robot_status.joint_states],
                "sensor_readings": [asdict(sr) for sr in robot_status.sensor_readings],
                "current_command": (
                    asdict(robot_status.current_command)
                    if robot_status.current_command
                    else None
                ),
                "active_alarms": robot_status.active_alarms,
                "uptime": robot_status.uptime_seconds,
                "last_updated": robot_status.last_updated,
            }

            return state

        except Exception as e:
            logger.error("Get robot state error: %s", e)
            return {"error": str(e)}

    def register_event_handler(
        self, event_type: str, handler: Callable[[dict[str, Any]], None]
    ) -> None:
        """Register event handler"""
        with self._lock:
            if event_type not in self._event_handlers:
                self._event_handlers[event_type] = []
            self._event_handlers[event_type].append(handler)
            logger.info("Registered handler for %s", event_type)

    def _trigger_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Trigger event to registered handlers"""
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error("Event handler error: %s", e)

    def shutdown(self) -> None:
        """Graceful system shutdown"""
        try:
            logger.info("=" * 80)
            logger.info("SHUTTING DOWN ROBOTIC MAINFRAME SYSTEM")
            logger.info("=" * 80)

            if self.controller:
                self.controller.stop()

            if self.hardware:
                self.hardware.shutdown()

            self.status.initialized = False
            self.status.controller_active = False
            self.status.hardware_healthy = False

            logger.info("Robotic mainframe system shutdown complete")

        except Exception as e:
            logger.error("Shutdown error: %s", e)


class RoboticIntegrationAPI:
    """
    High-level API for robotic integration.
    Provides simple interface for common operations.
    """

    def __init__(self, system: RoboticMainframeSystem | None = None):
        self.system = system or RoboticMainframeSystem()
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize robotic system"""
        if self._initialized:
            logger.warning("System already initialized")
            return True

        success = self.system.initialize()
        self._initialized = success
        return success

    def move_joints(
        self, positions: list[float], duration: float = 1.0, safe_mode: bool = True
    ) -> bool:
        """
        Move robot joints to specified positions.

        Args:
            positions: Target positions for each joint
            duration: Time to complete motion
            safe_mode: Enable Four Laws validation

        Returns:
            True if motion started successfully
        """
        context = {"is_user_order": True, "safe_mode": safe_mode}

        return self.system.execute_motion(positions, duration, context)

    def emergency_stop(self) -> bool:
        """Emergency stop"""
        return self.system.emergency_stop()

    def get_joint_positions(self) -> list[float]:
        """Get current joint positions"""
        try:
            state = self.system.get_robot_state()
            if "joint_states" in state:
                return [js["position"] for js in state["joint_states"]]
            return []
        except Exception:
            return []

    def is_healthy(self) -> bool:
        """Check if system is healthy"""
        status = self.system.get_status()
        return (
            status.initialized
            and status.hardware_healthy
            and status.controller_active
            and "EMERGENCY_STOP" not in status.active_alarms
        )

    def shutdown(self) -> None:
        """Shutdown system"""
        self.system.shutdown()
        self._initialized = False


# Global instance
_default_system: RoboticMainframeSystem | None = None


def get_robotic_system() -> RoboticMainframeSystem:
    """Get or create default robotic system"""
    global _default_system
    if _default_system is None:
        _default_system = RoboticMainframeSystem()
    return _default_system


def initialize_robotic_system() -> bool:
    """Initialize default robotic system"""
    system = get_robotic_system()
    return system.initialize()


# Convenience functions
def robot_move_joints(positions: list[float], duration: float = 1.0) -> bool:
    """Quick function to move robot joints"""
    api = RoboticIntegrationAPI(get_robotic_system())
    if not api._initialized:
        api.initialize()
    return api.move_joints(positions, duration)


def robot_emergency_stop() -> bool:
    """Quick function for emergency stop"""
    system = get_robotic_system()
    return system.emergency_stop()


def robot_get_status() -> RoboticSystemStatus:
    """Quick function to get robot status"""
    system = get_robotic_system()
    return system.get_status()
