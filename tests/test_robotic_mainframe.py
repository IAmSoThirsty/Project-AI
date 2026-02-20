"""
Comprehensive tests for Robotic Mainframe Integration System
Tests hardware layer, controller, Four Laws enforcement, and Triumvirate validation.
"""

import sys
import time

import pytest

sys.path.insert(0, "src")

from app.core.robotic_controller_manager import (
    ControlMode,
    RobotCommand,
    RobotControllerManager,
    TriumvirateRobotValidator,
)
from app.core.robotic_hardware_layer import (
    CommunicationProtocol,
    HardwareLimit,
    RobotConfiguration,
    RoboticSafetyValidator,
    RobotState,
    SimulatedHardwareInterface,
)
from app.core.robotic_mainframe_integration import (
    RoboticIntegrationAPI,
    RoboticMainframeSystem,
)


class TestHardwareAbstractionLayer:
    """Test hardware abstraction layer"""

    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return RobotConfiguration(
            robot_id="test_robot",
            robot_name="Test Robot",
            num_joints=6,
            num_end_effectors=1,
            workspace_bounds={"x": (-1, 1), "y": (-1, 1), "z": (0, 2)},
            max_payload=5.0,
            max_reach=1.5,
            communication_protocol=CommunicationProtocol.USB,
        )

    @pytest.fixture
    def hardware(self, config):
        """Create hardware interface"""
        return SimulatedHardwareInterface(config)

    def test_hardware_initialization(self, hardware, config):
        """Test hardware initialization"""
        success = hardware.initialize()
        assert success
        assert hardware._initialized
        assert len(hardware._joint_states) == config.num_joints

    def test_hardware_joint_read(self, hardware):
        """Test joint state reading"""
        hardware.initialize()
        joint_states = hardware.read_joint_states()

        assert len(joint_states) > 0
        assert all(hasattr(js, "position") for js in joint_states)
        assert all(hasattr(js, "velocity") for js in joint_states)

    def test_hardware_joint_write(self, hardware):
        """Test joint command writing"""
        hardware.initialize()

        commands = [{"position": 0.5} for _ in range(6)]
        success = hardware.write_joint_commands(commands)

        assert success

    def test_hardware_sensor_read(self, hardware):
        """Test sensor reading"""
        hardware.initialize()
        sensors = hardware.read_sensors()

        assert len(sensors) > 0
        assert all(hasattr(s, "sensor_type") for s in sensors)
        assert all(hasattr(s, "value") for s in sensors)

    def test_hardware_emergency_stop(self, hardware):
        """Test emergency stop"""
        hardware.initialize()
        success = hardware.emergency_stop()

        assert success
        assert hardware._emergency_stopped

    def test_hardware_health_check(self, hardware):
        """Test hardware health check"""
        hardware.initialize()
        is_healthy = hardware.is_healthy()

        assert is_healthy

    def test_hardware_shutdown(self, hardware):
        """Test hardware shutdown"""
        hardware.initialize()
        hardware.shutdown()

        assert not hardware._initialized


class TestSafetyValidator:
    """Test safety validator"""

    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return RobotConfiguration(
            robot_id="test_robot",
            robot_name="Test Robot",
            num_joints=6,
            num_end_effectors=1,
            workspace_bounds={"x": (-1, 1), "y": (-1, 1), "z": (0, 2)},
            max_payload=5.0,
            max_reach=1.5,
            communication_protocol=CommunicationProtocol.USB,
            four_laws_enabled=True,
        )

    @pytest.fixture
    def validator(self, config):
        """Create safety validator"""
        return RoboticSafetyValidator(config)

    @pytest.fixture
    def joint_states(self):
        """Create test joint states"""
        from app.core.robotic_hardware_layer import JointState, RobotJointType

        states = []
        for i in range(6):
            state = JointState(
                joint_id=f"joint_{i}",
                joint_type=RobotJointType.REVOLUTE,
                position=0.0,
                velocity=0.0,
                acceleration=0.0,
                torque=0.0,
                temperature=25.0,
                limits=HardwareLimit(
                    min_value=-3.14,
                    max_value=3.14,
                    max_velocity=2.0,
                    max_acceleration=5.0,
                ),
            )
            states.append(state)
        return states

    def test_four_laws_safe_action(self, validator, joint_states):
        """Test safe action validation"""
        commands = [{"position": 0.5} for _ in range(6)]
        context = {"is_user_order": True}

        is_valid, reason = validator.validate_action("Test motion", commands, joint_states, context)

        assert is_valid

    def test_four_laws_endangers_human(self, validator, joint_states):
        """Test action that endangers human"""
        commands = [{"position": 0.5} for _ in range(6)]
        context = {"is_user_order": True, "endangers_human": True}

        is_valid, reason = validator.validate_action("Dangerous motion", commands, joint_states, context)

        assert not is_valid
        assert "FOUR LAWS VIOLATION" in reason

    def test_four_laws_human_in_workspace(self, validator, joint_states):
        """Test human in workspace detection"""
        commands = [{"position": 0.5} for _ in range(6)]
        context = {
            "is_user_order": True,
            "human_in_workspace": True,
            "safe_distance": False,
        }

        is_valid, reason = validator.validate_action("Motion with human nearby", commands, joint_states, context)

        assert not is_valid

    def test_hardware_limits_validation(self, validator, joint_states):
        """Test hardware limits enforcement"""
        # Exceed position limits
        commands = [{"position": 5.0} for _ in range(6)]  # Outside limits
        context = {}

        is_valid, reason = validator.validate_action("Limit exceeding motion", commands, joint_states, context)

        assert not is_valid
        assert "exceeds limits" in reason

    def test_violation_history(self, validator, joint_states):
        """Test violation history tracking"""
        commands = [{"position": 5.0} for _ in range(6)]
        context = {}

        # Trigger violation
        validator.validate_action("Test", commands, joint_states, context)

        history = validator.get_violation_history()
        assert len(history) > 0


class TestRobotController:
    """Test robot controller"""

    @pytest.fixture
    def system_components(self):
        """Create complete system components"""
        config = RobotConfiguration(
            robot_id="test_robot",
            robot_name="Test Robot",
            num_joints=6,
            num_end_effectors=1,
            workspace_bounds={"x": (-1, 1), "y": (-1, 1), "z": (0, 2)},
            max_payload=5.0,
            max_reach=1.5,
            communication_protocol=CommunicationProtocol.USB,
        )

        hardware = SimulatedHardwareInterface(config)
        validator = RoboticSafetyValidator(config)

        return hardware, validator, config

    def test_controller_initialization(self, system_components):
        """Test controller initialization"""
        hardware, validator, config = system_components

        controller = RobotControllerManager(hardware, validator, config)
        success = controller.start()

        assert success
        assert controller._state == RobotState.READY

        controller.stop()

    def test_controller_command_execution(self, system_components):
        """Test command execution"""
        hardware, validator, config = system_components

        controller = RobotControllerManager(hardware, validator, config)
        controller.start()

        command = RobotCommand(
            command_id="test_cmd_1",
            command_type=ControlMode.POSITION,
            joint_targets=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            duration=1.0,
        )

        success = controller.execute_command(command)
        assert success

        time.sleep(0.5)
        controller.stop()

    def test_controller_emergency_stop(self, system_components):
        """Test emergency stop"""
        hardware, validator, config = system_components

        controller = RobotControllerManager(hardware, validator, config)
        controller.start()

        success = controller.emergency_stop()
        assert success
        assert controller._state == RobotState.EMERGENCY_STOP

        controller.stop()

    def test_controller_status(self, system_components):
        """Test status retrieval"""
        hardware, validator, config = system_components

        controller = RobotControllerManager(hardware, validator, config)
        controller.start()

        status = controller.get_status()
        assert status.state == RobotState.READY
        assert len(status.joint_states) > 0

        controller.stop()


class TestTriumvirateValidation:
    """Test Triumvirate validation"""

    @pytest.fixture
    def validator(self):
        """Create Triumvirate validator"""
        config = RobotConfiguration(
            robot_id="test_robot",
            robot_name="Test Robot",
            num_joints=6,
            num_end_effectors=1,
            workspace_bounds={"x": (-1, 1), "y": (-1, 1), "z": (0, 2)},
            max_payload=5.0,
            max_reach=1.5,
            communication_protocol=CommunicationProtocol.USB,
            four_laws_enabled=True,
        )

        safety_validator = RoboticSafetyValidator(config)
        return TriumvirateRobotValidator(safety_validator)

    @pytest.fixture
    def joint_states(self):
        """Create test joint states"""
        from app.core.robotic_hardware_layer import JointState, RobotJointType

        states = []
        for i in range(6):
            state = JointState(
                joint_id=f"joint_{i}",
                joint_type=RobotJointType.REVOLUTE,
                position=0.0,
                velocity=0.0,
                acceleration=0.0,
                torque=0.0,
                temperature=25.0,
                limits=HardwareLimit(
                    min_value=-3.14,
                    max_value=3.14,
                    max_velocity=2.0,
                    max_acceleration=5.0,
                ),
            )
            states.append(state)
        return states

    def test_triumvirate_validation_pass(self, validator, joint_states):
        """Test successful validation through all stages"""
        command = RobotCommand(
            command_id="test_cmd",
            command_type=ControlMode.POSITION,
            joint_targets=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            duration=1.0,
            context={"is_user_order": True},
        )

        is_valid, reason, metadata = validator.validate_command(command, joint_states)

        assert is_valid
        assert "cerberus" in metadata["validation_stages"]
        assert "codex" in metadata["validation_stages"]
        assert "galahad" in metadata["validation_stages"]

    def test_triumvirate_cerberus_rejection(self, validator, joint_states):
        """Test Cerberus stage rejection"""
        command = RobotCommand(
            command_id="test_cmd",
            command_type=ControlMode.POSITION,
            joint_targets=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
            duration=1.0,
            context={"endangers_human": True},
        )

        is_valid, reason, metadata = validator.validate_command(command, joint_states)

        assert not is_valid
        assert "Cerberus" in reason


class TestMainframeIntegration:
    """Test complete mainframe integration"""

    def test_system_initialization(self):
        """Test system initialization"""
        system = RoboticMainframeSystem()
        success = system.initialize()

        assert success
        assert system.status.initialized
        assert system.status.hardware_healthy
        assert system.status.controller_active

        system.shutdown()

    def test_system_motion_execution(self):
        """Test motion execution"""
        system = RoboticMainframeSystem()
        system.initialize()

        success = system.execute_motion([0.1, 0.1, 0.1, 0.1, 0.1, 0.1], 1.0)
        assert success

        time.sleep(1.5)
        system.shutdown()

    def test_system_emergency_stop(self):
        """Test system emergency stop"""
        system = RoboticMainframeSystem()
        system.initialize()

        # Start motion
        system.execute_motion([1.0, 1.0, 1.0, 1.0, 1.0, 1.0], 5.0)
        time.sleep(0.5)

        # Emergency stop
        success = system.emergency_stop()
        assert success

        status = system.get_status()
        assert "EMERGENCY_STOP" in status.active_alarms

        system.shutdown()

    def test_api_usage(self):
        """Test high-level API"""
        api = RoboticIntegrationAPI()
        success = api.initialize()

        assert success

        # Move joints
        success = api.move_joints([0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
        assert success

        # Check health
        is_healthy = api.is_healthy()
        assert is_healthy

        api.shutdown()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
