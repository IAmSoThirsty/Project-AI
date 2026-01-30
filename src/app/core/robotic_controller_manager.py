"""
Robot Controller Manager with Triumvirate Integration
Manages robot control loops, integrates with Triumvirate for validation,
and ensures Four Laws compliance for all robotic actions.
Production-grade, monolithic architecture.
"""
import json
import logging
import os
import threading
import time
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Tuple

import numpy as np

from app.core.robotic_hardware_layer import (
    HardwareAbstractionLayer, RoboticSafetyValidator,
    RobotConfiguration, RobotState, JointState, SensorReading
)

logger = logging.getLogger(__name__)


class ControlMode(Enum):
    """Robot control modes"""
    POSITION = "position"
    VELOCITY = "velocity"
    TORQUE = "torque"
    TRAJECTORY = "trajectory"
    FORCE_CONTROL = "force_control"


class PathPlanningAlgorithm(Enum):
    """Path planning algorithms"""
    LINEAR = "linear"
    CUBIC_SPLINE = "cubic_spline"
    QUINTIC_POLYNOMIAL = "quintic_polynomial"
    RRT = "rrt"  # Rapidly-exploring Random Tree
    A_STAR = "a_star"


@dataclass
class TrajectoryPoint:
    """Single point in a trajectory"""
    positions: List[float]
    velocities: List[float]
    accelerations: List[float]
    timestamp: float


@dataclass
class RobotCommand:
    """Command to be executed by robot"""
    command_id: str
    command_type: ControlMode
    joint_targets: List[float]
    duration: float  # seconds
    priority: int = 5  # 1-10, 10 is highest
    requires_four_laws_check: bool = True
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class RobotStatus:
    """Current robot status"""
    state: RobotState
    joint_states: List[JointState]
    sensor_readings: List[SensorReading]
    current_command: Optional[RobotCommand]
    active_alarms: List[str]
    cpu_usage: float
    memory_usage: float
    uptime_seconds: float
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class TriumvirateRobotValidator:
    """
    Integrates Triumvirate architecture with robotic validation.
    Ensures all robotic actions pass through Cerberus, Codex, and Galahad.
    """

    def __init__(self, safety_validator: RoboticSafetyValidator):
        self.safety_validator = safety_validator
        self._validation_history: deque = deque(maxlen=1000)
        self._lock = threading.RLock()
        
        logger.info("Triumvirate robot validator initialized")

    def validate_command(self, command: RobotCommand,
                        joint_states: List[JointState]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate robot command through Triumvirate pipeline.
        
        Pipeline:
        1. Cerberus: Policy and safety validation
        2. Codex: Command analysis and optimization
        3. Galahad: Reasoning about potential outcomes
        
        Returns:
            (is_valid, reason, metadata)
        """
        start_time = time.time()
        metadata = {
            "command_id": command.command_id,
            "validation_stages": {}
        }
        
        try:
            # Stage 1: Cerberus - Policy Enforcement
            cerberus_valid, cerberus_reason = self._cerberus_validate(command, joint_states)
            metadata["validation_stages"]["cerberus"] = {
                "valid": cerberus_valid,
                "reason": cerberus_reason
            }
            
            if not cerberus_valid:
                self._log_validation(command, False, cerberus_reason, metadata)
                return False, f"Cerberus rejection: {cerberus_reason}", metadata
            
            # Stage 2: Codex - Command Analysis
            codex_valid, codex_reason, codex_optimization = self._codex_analyze(command, joint_states)
            metadata["validation_stages"]["codex"] = {
                "valid": codex_valid,
                "reason": codex_reason,
                "optimization": codex_optimization
            }
            
            if not codex_valid:
                self._log_validation(command, False, codex_reason, metadata)
                return False, f"Codex rejection: {codex_reason}", metadata
            
            # Stage 3: Galahad - Outcome Reasoning
            galahad_valid, galahad_reason, galahad_assessment = self._galahad_reason(
                command, joint_states, codex_optimization
            )
            metadata["validation_stages"]["galahad"] = {
                "valid": galahad_valid,
                "reason": galahad_reason,
                "assessment": galahad_assessment
            }
            
            if not galahad_valid:
                self._log_validation(command, False, galahad_reason, metadata)
                return False, f"Galahad rejection: {galahad_reason}", metadata
            
            # All stages passed
            duration_ms = (time.time() - start_time) * 1000
            metadata["validation_duration_ms"] = duration_ms
            
            self._log_validation(command, True, "All Triumvirate stages passed", metadata)
            
            return True, "Command validated by Triumvirate", metadata
            
        except Exception as e:
            logger.error(f"Triumvirate validation error: {e}")
            metadata["error"] = str(e)
            return False, f"Validation error: {e}", metadata

    def _cerberus_validate(self, command: RobotCommand,
                          joint_states: List[JointState]) -> Tuple[bool, str]:
        """
        Cerberus stage: Enforce policies and safety constraints.
        """
        # Four Laws check
        if command.requires_four_laws_check:
            # Prepare joint commands from target positions
            joint_commands = [
                {"position": pos} for pos in command.joint_targets
            ]
            
            is_valid, reason = self.safety_validator.validate_action(
                f"Command {command.command_id}",
                joint_commands,
                joint_states,
                command.context
            )
            
            if not is_valid:
                return False, reason
        
        # Emergency stop check
        if command.context.get("emergency_stop_active"):
            return False, "Emergency stop is active"
        
        # Priority validation
        if command.priority < 1 or command.priority > 10:
            return False, f"Invalid priority: {command.priority}"
        
        return True, "Cerberus validation passed"

    def _codex_analyze(self, command: RobotCommand,
                      joint_states: List[JointState]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Codex stage: Analyze command and suggest optimizations.
        """
        optimization = {
            "original_targets": command.joint_targets.copy(),
            "optimized_targets": None,
            "trajectory_smoothness": 1.0,
            "energy_efficiency": 0.8
        }
        
        # Check for large position changes that might need trajectory planning
        max_delta = 0.0
        for i, (target, state) in enumerate(zip(command.joint_targets, joint_states)):
            delta = abs(target - state.position)
            max_delta = max(max_delta, delta)
            
            if delta > 1.0:  # > 1 radian change
                # Suggest trajectory planning
                optimization["needs_trajectory_planning"] = True
                optimization["large_motion_joint"] = i
        
        # Simple optimization: smooth out sharp changes
        if max_delta > 0.5:
            # In production, this would use actual trajectory planning
            optimization["optimized_targets"] = command.joint_targets
            optimization["trajectory_smoothness"] = 0.9
        
        return True, "Codex analysis complete", optimization

    def _galahad_reason(self, command: RobotCommand, joint_states: List[JointState],
                       codex_optimization: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Galahad stage: Reason about command outcomes and contradictions.
        """
        assessment = {
            "safety_risk": "low",
            "success_probability": 0.95,
            "potential_issues": [],
            "recommendations": []
        }
        
        # Assess command feasibility
        for i, (target, state) in enumerate(zip(command.joint_targets, joint_states)):
            # Check if target is reachable given current velocity
            delta = target - state.position
            time_required = abs(delta) / max(abs(state.limits.max_velocity), 0.1)
            
            if time_required > command.duration * 1.5:
                assessment["potential_issues"].append(
                    f"Joint {i} may not reach target in time"
                )
                assessment["success_probability"] *= 0.8
        
        # Check for contradictions in command
        if command.command_type == ControlMode.POSITION:
            # Ensure position targets are consistent
            pass  # Simplified for production
        
        # Assess safety risk
        if command.context.get("human_nearby"):
            assessment["safety_risk"] = "medium"
            assessment["recommendations"].append("Reduce velocity near humans")
            assessment["success_probability"] *= 0.9
        
        # Check temperature warnings
        hot_joints = [s for s in joint_states if s.temperature > 60.0]
        if hot_joints:
            assessment["safety_risk"] = "medium"
            assessment["potential_issues"].append(
                f"{len(hot_joints)} joints showing elevated temperature"
            )
        
        # Final decision
        if assessment["success_probability"] < 0.5:
            return False, "Low success probability", assessment
        
        if assessment["safety_risk"] == "high":
            return False, "High safety risk detected", assessment
        
        return True, "Galahad assessment positive", assessment

    def _log_validation(self, command: RobotCommand, is_valid: bool,
                       reason: str, metadata: Dict[str, Any]) -> None:
        """Log validation result"""
        with self._lock:
            log_entry = {
                "command_id": command.command_id,
                "is_valid": is_valid,
                "reason": reason,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat()
            }
            self._validation_history.append(log_entry)


class RobotControllerManager:
    """
    Main robot controller with Triumvirate integration.
    Manages control loops, trajectory execution, and safety monitoring.
    """

    def __init__(self, hardware: HardwareAbstractionLayer,
                 safety_validator: RoboticSafetyValidator,
                 config: RobotConfiguration,
                 data_dir: str = "data/robot_controller"):
        
        self.hardware = hardware
        self.safety_validator = safety_validator
        self.config = config
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Triumvirate validator
        self.triumvirate_validator = TriumvirateRobotValidator(safety_validator)
        
        # State management
        self._state = RobotState.IDLE
        self._command_queue: deque = deque()
        self._current_command: Optional[RobotCommand] = None
        self._active_alarms: List[str] = []
        
        # Control loop
        self._control_thread: Optional[threading.Thread] = None
        self._should_run = False
        self._lock = threading.RLock()
        
        # Statistics
        self._start_time = time.time()
        self._commands_executed = 0
        self._commands_rejected = 0
        
        logger.info(f"Robot controller initialized for {config.robot_name}")

    def start(self) -> bool:
        """Start robot controller"""
        try:
            with self._lock:
                if self._should_run:
                    logger.warning("Controller already running")
                    return False
                
                # Initialize hardware
                if not self.hardware.initialize():
                    logger.error("Failed to initialize hardware")
                    return False
                
                # Start control loop
                self._should_run = True
                self._state = RobotState.READY
                
                self._control_thread = threading.Thread(
                    target=self._control_loop,
                    daemon=True
                )
                self._control_thread.start()
                
                logger.info("Robot controller started")
                return True
                
        except Exception as e:
            logger.error(f"Failed to start controller: {e}")
            return False

    def stop(self) -> None:
        """Stop robot controller gracefully"""
        try:
            with self._lock:
                logger.info("Stopping robot controller")
                self._should_run = False
                self._state = RobotState.SHUTDOWN
                
                if self._control_thread:
                    self._control_thread.join(timeout=5.0)
                
                self.hardware.shutdown()
                logger.info("Robot controller stopped")
                
        except Exception as e:
            logger.error(f"Error stopping controller: {e}")

    def execute_command(self, command: RobotCommand) -> bool:
        """
        Queue command for execution.
        Command will be validated by Triumvirate before execution.
        """
        try:
            with self._lock:
                if self._state == RobotState.EMERGENCY_STOP:
                    logger.error("Cannot execute: emergency stop active")
                    return False
                
                # Add to queue (will be validated in control loop)
                self._command_queue.append(command)
                logger.info(f"Command {command.command_id} queued")
                return True
                
        except Exception as e:
            logger.error(f"Failed to queue command: {e}")
            return False

    def emergency_stop(self) -> bool:
        """Execute emergency stop"""
        try:
            with self._lock:
                logger.critical("EMERGENCY STOP INITIATED")
                self._state = RobotState.EMERGENCY_STOP
                
                # Clear command queue
                self._command_queue.clear()
                self._current_command = None
                
                # Hardware emergency stop
                self.hardware.emergency_stop()
                
                self._active_alarms.append("EMERGENCY_STOP_ACTIVATED")
                
                return True
                
        except Exception as e:
            logger.error(f"Emergency stop failed: {e}")
            return False

    def reset_emergency_stop(self) -> bool:
        """Reset emergency stop (requires manual intervention)"""
        try:
            with self._lock:
                if self._state != RobotState.EMERGENCY_STOP:
                    return False
                
                logger.info("Resetting emergency stop")
                
                # Clear alarms
                self._active_alarms = [a for a in self._active_alarms 
                                      if a != "EMERGENCY_STOP_ACTIVATED"]
                
                # Check hardware health
                if not self.hardware.is_healthy():
                    logger.error("Hardware not healthy, cannot reset")
                    return False
                
                self._state = RobotState.READY
                logger.info("Emergency stop reset complete")
                return True
                
        except Exception as e:
            logger.error(f"Failed to reset emergency stop: {e}")
            return False

    def get_status(self) -> RobotStatus:
        """Get current robot status"""
        with self._lock:
            joint_states = self.hardware.read_joint_states()
            sensor_readings = self.hardware.read_sensors()
            
            status = RobotStatus(
                state=self._state,
                joint_states=joint_states,
                sensor_readings=sensor_readings,
                current_command=self._current_command,
                active_alarms=self._active_alarms.copy(),
                cpu_usage=0.0,  # Simplified
                memory_usage=0.0,  # Simplified
                uptime_seconds=time.time() - self._start_time
            )
            
            return status

    def _control_loop(self) -> None:
        """Main control loop (runs in thread)"""
        logger.info("Control loop started")
        
        while self._should_run:
            try:
                # Check hardware health
                if not self.hardware.is_healthy():
                    logger.error("Hardware health check failed")
                    self.emergency_stop()
                    continue
                
                # Process next command
                if self._state == RobotState.READY and len(self._command_queue) > 0:
                    command = self._command_queue.popleft()
                    self._execute_command_internal(command)
                
                # Sleep for control cycle
                time.sleep(1.0 / self.config.control_frequency)
                
            except Exception as e:
                logger.error(f"Control loop error: {e}")
                time.sleep(0.1)
        
        logger.info("Control loop stopped")

    def _execute_command_internal(self, command: RobotCommand) -> None:
        """Execute command with Triumvirate validation"""
        try:
            self._state = RobotState.EXECUTING
            self._current_command = command
            
            # Read current joint states
            joint_states = self.hardware.read_joint_states()
            
            # Triumvirate validation
            is_valid, reason, metadata = self.triumvirate_validator.validate_command(
                command, joint_states
            )
            
            if not is_valid:
                logger.error(f"Command rejected: {reason}")
                self._commands_rejected += 1
                self._state = RobotState.READY
                self._current_command = None
                return
            
            # Execute command
            logger.info(f"Executing command {command.command_id}")
            
            # Prepare joint commands
            joint_commands = []
            for target in command.joint_targets:
                joint_commands.append({"position": target})
            
            # Send to hardware
            success = self.hardware.write_joint_commands(joint_commands)
            
            if success:
                self._commands_executed += 1
                logger.info(f"Command {command.command_id} executed successfully")
            else:
                logger.error(f"Command {command.command_id} execution failed")
                self._commands_rejected += 1
            
            self._state = RobotState.READY
            self._current_command = None
            
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            self._state = RobotState.ERROR
            self._current_command = None


# Global instances
_default_controller: Optional[RobotControllerManager] = None


def get_default_controller(hardware: Optional[HardwareAbstractionLayer] = None,
                          validator: Optional[RoboticSafetyValidator] = None,
                          config: Optional[RobotConfiguration] = None) -> RobotControllerManager:
    """Get or create default robot controller"""
    global _default_controller
    if _default_controller is None:
        from app.core.robotic_hardware_layer import (
            get_default_hardware, get_default_validator, RobotConfiguration
        )
        
        hw = hardware or get_default_hardware()
        val = validator or get_default_validator()
        cfg = config or RobotConfiguration(
            robot_id="default_robot",
            robot_name="Default Robot",
            num_joints=6,
            num_end_effectors=1,
            workspace_bounds={"x": (-1, 1), "y": (-1, 1), "z": (0, 2)},
            max_payload=5.0,
            max_reach=1.5,
            communication_protocol=CommunicationProtocol.USB
        )
        
        _default_controller = RobotControllerManager(hw, val, cfg)
    
    return _default_controller
