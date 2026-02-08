#!/usr/bin/env python3
"""
Domain 2: Command & Control Subsystem
Project-AI God Tier Zombie Apocalypse Defense Engine

Provides centralized command and control for mission planning, resource allocation,
communication coordination, and tactical decision support.

Capabilities:
- Mission planning and execution tracking
- Resource allocation and dynamic tasking
- Multi-channel communication coordination
- Decision support and tactical planning
- Command hierarchy management
- Air-gapped operation with local command structures
- Byzantine fault tolerance for command integrity
"""

import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

from ..core.interface_abstractions import (
    BaseSubsystem,
    ICommandable,
    ICommunication,
    IMonitorable,
    IObservable,
    SubsystemCommand,
    SubsystemResponse,
)

logger = logging.getLogger(__name__)


class MissionStatus(Enum):
    """Mission execution status"""

    PLANNED = "planned"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MissionPriority(Enum):
    """Mission priority levels"""

    CRITICAL = 0
    HIGH = 2
    MEDIUM = 5
    LOW = 7
    DEFERRED = 10


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class CommunicationChannel(Enum):
    """Communication channel types"""

    RADIO = "radio"
    MESH = "mesh"
    SATELLITE = "satellite"
    HARDLINE = "hardline"
    RUNNER = "runner"
    SIGNAL = "signal"


@dataclass
class Mission:
    """Mission definition and tracking"""

    mission_id: str
    name: str
    objective: str
    priority: MissionPriority
    status: MissionStatus
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    assigned_resources: dict[str, list[str]] = field(default_factory=dict)
    tasks: list[str] = field(default_factory=list)
    success_criteria: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Individual task within a mission"""

    task_id: str
    mission_id: str
    description: str
    status: TaskStatus
    assigned_to: str | None = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    dependencies: list[str] = field(default_factory=list)
    resources_required: dict[str, float] = field(default_factory=dict)
    progress: float = 0.0


@dataclass
class CommandMessage:
    """Command message for communication"""

    message_id: str
    sender: str
    destination: str
    channel: CommunicationChannel
    content: Any
    priority: int
    timestamp: datetime = field(default_factory=datetime.now)
    requires_ack: bool = False
    acknowledged: bool = False
    encrypted: bool = False


class CommandControlSubsystem(
    BaseSubsystem, ICommandable, IMonitorable, IObservable, ICommunication
):
    """
    Command & Control Subsystem

    Provides centralized command and control for all defense operations,
    including mission planning, resource allocation, and communication coordination.
    """

    SUBSYSTEM_METADATA = {
        "id": "command_control",
        "name": "Command & Control",
        "version": "1.0.0",
        "priority": "CRITICAL",
        "dependencies": ["situational_awareness"],
        "provides_capabilities": [
            "mission_planning",
            "resource_allocation",
            "communication_coordination",
            "decision_support",
            "command_hierarchy",
        ],
        "config": {
            "data_dir": "data",
            "max_concurrent_missions": 10,
            "task_timeout_seconds": 3600,
            "message_retention_seconds": 86400,
            "enable_message_encryption": True,
        },
    }

    def __init__(self, data_dir: str = "data", **config):
        """Initialize Command & Control subsystem."""
        super().__init__(data_dir=data_dir, config=config)

        self.data_path = Path(data_dir) / "command_control"
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.max_concurrent_missions = config.get("max_concurrent_missions", 10)
        self.task_timeout = timedelta(seconds=config.get("task_timeout_seconds", 3600))
        self.message_retention = timedelta(
            seconds=config.get("message_retention_seconds", 86400)
        )
        self.enable_encryption = config.get("enable_message_encryption", True)

        # Mission management
        self._missions: dict[str, Mission] = {}
        self._mission_lock = threading.Lock()

        # Task management
        self._tasks: dict[str, Task] = {}
        self._task_lock = threading.Lock()

        # Communication
        self._message_queue: list[CommandMessage] = []
        self._message_history: list[CommandMessage] = []
        self._message_lock = threading.Lock()

        # Resource allocation tracking
        self._resource_allocations: dict[str, dict[str, Any]] = {}
        self._allocation_lock = threading.Lock()

        # Command hierarchy
        self._command_chain: dict[str, list[str]] = {}
        self._commander_roles: dict[str, str] = {}

        # Event system
        self._subscriptions: dict[str, list[tuple[str, callable]]] = {}
        self._subscription_counter = 0
        self._subscription_lock = threading.Lock()

        # Background processing
        self._processing_thread: threading.Thread | None = None
        self._processing_active = False

        # Metrics
        self._metrics = {
            "missions_created": 0,
            "missions_completed": 0,
            "missions_failed": 0,
            "tasks_completed": 0,
            "messages_sent": 0,
            "resource_allocations": 0,
            "command_decisions": 0,
        }
        self._metrics_lock = threading.Lock()

        # Air-gapped command cache
        self._air_gapped_cache = {
            "emergency_protocols": [],
            "fallback_commanders": [],
            "offline_resources": {},
        }

        # Byzantine fault tolerance
        self._command_quorum = {}
        self._command_validators = []

        self.logger.info("Command & Control subsystem created")

    def initialize(self) -> bool:
        """Initialize the subsystem."""
        self.logger.info("Initializing Command & Control subsystem...")

        try:
            # Load persistent state
            self._load_state()

            # Initialize command hierarchy
            self._initialize_command_hierarchy()

            # Start background processing
            self._processing_active = True
            self._processing_thread = threading.Thread(
                target=self._processing_loop, daemon=True, name="CommandProcessing"
            )
            self._processing_thread.start()

            self._initialized = True
            self.logger.info("Command & Control subsystem initialized successfully")
            return True

        except Exception as e:
            self.logger.error("Failed to initialize Command & Control subsystem: %s", e)
            return False

    def shutdown(self) -> bool:
        """Shutdown the subsystem."""
        self.logger.info("Shutting down Command & Control subsystem...")

        try:
            # Stop processing thread
            self._processing_active = False
            if self._processing_thread:
                self._processing_thread.join(timeout=5.0)

            # Save state
            self._save_state()

            self._initialized = False
            self.logger.info("Command & Control subsystem shutdown complete")
            return True

        except Exception as e:
            self.logger.error("Error during shutdown: %s", e)
            return False

    def health_check(self) -> bool:
        """Perform health check."""
        if not self._initialized:
            return False

        # Check that processing thread is running
        if (
            not self._processing_active
            or not self._processing_thread
            or not self._processing_thread.is_alive()
        ):
            self.logger.warning("Command processing thread not running")
            return False

        # Check for mission overload
        active_missions = sum(
            1 for m in self._missions.values() if m.status == MissionStatus.ACTIVE
        )
        if active_missions > self.max_concurrent_missions:
            self.logger.warning("Too many active missions: %s", active_missions)
            return False

        return True

    def get_status(self) -> dict[str, Any]:
        """Get subsystem status."""
        status = super().get_status()

        with self._mission_lock:
            status["total_missions"] = len(self._missions)
            status["active_missions"] = sum(
                1 for m in self._missions.values() if m.status == MissionStatus.ACTIVE
            )

        with self._task_lock:
            status["total_tasks"] = len(self._tasks)
            status["pending_tasks"] = sum(
                1 for t in self._tasks.values() if t.status == TaskStatus.PENDING
            )

        with self._message_lock:
            status["queued_messages"] = len(self._message_queue)

        with self._metrics_lock:
            status["metrics"] = self._metrics.copy()

        return status

    # ICommunication implementation

    def send_message(self, destination: str, message: Any, priority: int = 5) -> bool:
        """Send a message."""
        try:
            msg = CommandMessage(
                message_id=str(uuid.uuid4()),
                sender="command_control",
                destination=destination,
                channel=self._select_best_channel(),
                content=message,
                priority=priority,
                encrypted=self.enable_encryption,
            )

            with self._message_lock:
                self._message_queue.append(msg)
                self._message_queue.sort(key=lambda m: m.priority)

            with self._metrics_lock:
                self._metrics["messages_sent"] += 1

            self.emit_event(
                "message_sent",
                {"message_id": msg.message_id, "destination": destination},
            )

            return True

        except Exception as e:
            self.logger.error("Failed to send message: %s", e)
            return False

    def receive_messages(self) -> list[Any]:
        """Receive pending messages."""
        with self._message_lock:
            messages = [m.content for m in self._message_queue[:10]]
            self._message_queue = self._message_queue[10:]
            return messages

    def broadcast(self, message: Any, group: str | None = None) -> int:
        """Broadcast a message."""
        recipients = self._get_broadcast_recipients(group)
        count = 0

        for recipient in recipients:
            if self.send_message(recipient, message, priority=3):
                count += 1

        return count

    # ICommandable implementation

    def execute_command(self, command: SubsystemCommand) -> SubsystemResponse:
        """Execute a command."""
        start_time = time.time()

        try:
            if command.command_type == "create_mission":
                mission = self._create_mission(command.parameters)
                success = mission is not None
                result = {"mission_id": mission.mission_id} if mission else None

            elif command.command_type == "update_mission_status":
                success = self._update_mission_status(command.parameters)
                result = {"updated": success}

            elif command.command_type == "create_task":
                task = self._create_task(command.parameters)
                success = task is not None
                result = {"task_id": task.task_id} if task else None

            elif command.command_type == "allocate_resources":
                allocation_id = self._allocate_resources(command.parameters)
                success = allocation_id is not None
                result = {"allocation_id": allocation_id}

            elif command.command_type == "get_mission_status":
                mission_status = self._get_mission_status(command.parameters)
                success = mission_status is not None
                result = mission_status

            elif command.command_type == "plan_tactical_response":
                plan = self._plan_tactical_response(command.parameters)
                success = plan is not None
                result = {"plan": plan}

            else:
                success = False
                result = None
                error = f"Unknown command type: {command.command_type}"

                return SubsystemResponse(
                    command_id=command.command_id,
                    success=False,
                    error=error,
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

            return SubsystemResponse(
                command_id=command.command_id,
                success=success,
                result=result,
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        except Exception as e:
            self.logger.error("Command execution failed: %s", e)
            return SubsystemResponse(
                command_id=command.command_id,
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    def get_supported_commands(self) -> list[str]:
        """Get list of supported command types."""
        return [
            "create_mission",
            "update_mission_status",
            "create_task",
            "allocate_resources",
            "get_mission_status",
            "plan_tactical_response",
        ]

    # IMonitorable implementation

    def get_metrics(self) -> dict[str, Any]:
        """Get current metrics."""
        with self._metrics_lock:
            return self._metrics.copy()

    def get_metric(self, metric_name: str) -> Any:
        """Get a specific metric value."""
        with self._metrics_lock:
            return self._metrics.get(metric_name)

    def reset_metrics(self) -> bool:
        """Reset all metrics."""
        with self._metrics_lock:
            for key in self._metrics:
                if isinstance(self._metrics[key], (int, float)):
                    self._metrics[key] = 0
        return True

    # IObservable implementation

    def subscribe(self, event_type: str, callback: callable) -> str:
        """Subscribe to events."""
        with self._subscription_lock:
            subscription_id = f"sub_{self._subscription_counter}"
            self._subscription_counter += 1

            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []

            self._subscriptions[event_type].append((subscription_id, callback))

            return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        with self._subscription_lock:
            for event_type in self._subscriptions:
                self._subscriptions[event_type] = [
                    (sid, cb)
                    for sid, cb in self._subscriptions[event_type]
                    if sid != subscription_id
                ]
            return True

    def emit_event(self, event_type: str, data: Any) -> int:
        """Emit an event to all subscribers."""
        with self._subscription_lock:
            subscribers = self._subscriptions.get(event_type, [])

            for subscription_id, callback in subscribers:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(
                        "Error in event callback %s: %s", subscription_id, e
                    )

            return len(subscribers)

    # Internal methods

    def _processing_loop(self):
        """Background processing loop."""
        while self._processing_active:
            try:
                self._process_tasks()
                self._process_messages()
                self._cleanup_old_data()
                time.sleep(1.0)
            except Exception as e:
                self.logger.error("Error in processing loop: %s", e)
                time.sleep(1.0)

    def _process_tasks(self):
        """Process pending tasks."""
        with self._task_lock:
            for task in self._tasks.values():
                if task.status == TaskStatus.PENDING:
                    # Check dependencies
                    deps_completed = all(
                        self._tasks.get(
                            dep_id, Task("", "", "", TaskStatus.FAILED)
                        ).status
                        == TaskStatus.COMPLETED
                        for dep_id in task.dependencies
                    )

                    if deps_completed and self._can_allocate_task_resources(task):
                        task.status = TaskStatus.IN_PROGRESS
                        task.started_at = datetime.now()

                        self.emit_event("task_started", {"task_id": task.task_id})

    def _process_messages(self):
        """Process outgoing messages."""
        with self._message_lock:
            # Archive old messages
            now = datetime.now()
            for msg in self._message_queue[:]:
                age = now - msg.timestamp
                if age > self.message_retention:
                    self._message_queue.remove(msg)
                    self._message_history.append(msg)

    def _cleanup_old_data(self):
        """Clean up old data."""
        with self._message_lock:
            # Keep only recent history
            cutoff = datetime.now() - self.message_retention * 2
            self._message_history = [
                m for m in self._message_history if m.timestamp > cutoff
            ]

    def _create_mission(self, params: dict[str, Any]) -> Mission | None:
        """Create a new mission."""
        try:
            mission = Mission(
                mission_id=str(uuid.uuid4()),
                name=params["name"],
                objective=params["objective"],
                priority=MissionPriority[params.get("priority", "MEDIUM")],
                status=MissionStatus.PLANNED,
                success_criteria=params.get("success_criteria", {}),
                metadata=params.get("metadata", {}),
            )

            with self._mission_lock:
                self._missions[mission.mission_id] = mission

            with self._metrics_lock:
                self._metrics["missions_created"] += 1

            self.emit_event("mission_created", {"mission_id": mission.mission_id})

            return mission

        except Exception as e:
            self.logger.error("Failed to create mission: %s", e)
            return None

    def _update_mission_status(self, params: dict[str, Any]) -> bool:
        """Update mission status."""
        mission_id = params.get("mission_id")
        new_status = params.get("status")

        if not mission_id or not new_status:
            return False

        with self._mission_lock:
            if mission_id not in self._missions:
                return False

            mission = self._missions[mission_id]
            old_status = mission.status
            mission.status = MissionStatus[new_status]

            if (
                mission.status == MissionStatus.ACTIVE
                and old_status == MissionStatus.PLANNED
            ):
                mission.started_at = datetime.now()
            elif mission.status in [MissionStatus.COMPLETED, MissionStatus.FAILED]:
                mission.completed_at = datetime.now()

                if mission.status == MissionStatus.COMPLETED:
                    with self._metrics_lock:
                        self._metrics["missions_completed"] += 1
                else:
                    with self._metrics_lock:
                        self._metrics["missions_failed"] += 1

            self.emit_event(
                "mission_status_changed",
                {
                    "mission_id": mission_id,
                    "old_status": old_status.value,
                    "new_status": mission.status.value,
                },
            )

            return True

    def _create_task(self, params: dict[str, Any]) -> Task | None:
        """Create a new task."""
        try:
            task = Task(
                task_id=str(uuid.uuid4()),
                mission_id=params["mission_id"],
                description=params["description"],
                status=TaskStatus.PENDING,
                assigned_to=params.get("assigned_to"),
                dependencies=params.get("dependencies", []),
                resources_required=params.get("resources_required", {}),
            )

            with self._task_lock:
                self._tasks[task.task_id] = task

            # Add task to mission
            with self._mission_lock:
                if task.mission_id in self._missions:
                    self._missions[task.mission_id].tasks.append(task.task_id)

            self.emit_event("task_created", {"task_id": task.task_id})

            return task

        except Exception as e:
            self.logger.error("Failed to create task: %s", e)
            return None

    def _allocate_resources(self, params: dict[str, Any]) -> str | None:
        """Allocate resources to a mission or task."""
        try:
            allocation_id = str(uuid.uuid4())

            allocation = {
                "allocation_id": allocation_id,
                "target_id": params["target_id"],
                "target_type": params["target_type"],  # "mission" or "task"
                "resources": params["resources"],
                "allocated_at": datetime.now(),
                "status": "active",
            }

            with self._allocation_lock:
                self._resource_allocations[allocation_id] = allocation

            with self._metrics_lock:
                self._metrics["resource_allocations"] += 1

            self.emit_event(
                "resources_allocated",
                {"allocation_id": allocation_id, "target_id": params["target_id"]},
            )

            return allocation_id

        except Exception as e:
            self.logger.error("Failed to allocate resources: %s", e)
            return None

    def _get_mission_status(self, params: dict[str, Any]) -> dict[str, Any] | None:
        """Get detailed mission status."""
        mission_id = params.get("mission_id")

        with self._mission_lock:
            if mission_id not in self._missions:
                return None

            mission = self._missions[mission_id]

            # Get task statuses
            with self._task_lock:
                task_statuses = {
                    task_id: self._tasks[task_id].status.value
                    for task_id in mission.tasks
                    if task_id in self._tasks
                }

            return {
                "mission_id": mission.mission_id,
                "name": mission.name,
                "status": mission.status.value,
                "priority": mission.priority.value,
                "created_at": mission.created_at.isoformat(),
                "started_at": (
                    mission.started_at.isoformat() if mission.started_at else None
                ),
                "completed_at": (
                    mission.completed_at.isoformat() if mission.completed_at else None
                ),
                "tasks": task_statuses,
                "assigned_resources": mission.assigned_resources,
            }

    def _plan_tactical_response(self, params: dict[str, Any]) -> dict[str, Any] | None:
        """Plan a tactical response to a situation."""
        try:
            situation = params["situation"]
            available_resources = params.get("resources", {})

            with self._metrics_lock:
                self._metrics["command_decisions"] += 1

            # Simple tactical planning (would use AI/optimization in production)
            plan = {
                "plan_id": str(uuid.uuid4()),
                "situation": situation,
                "recommended_actions": self._generate_recommended_actions(situation),
                "resource_requirements": self._estimate_resource_requirements(
                    situation
                ),
                "estimated_duration": self._estimate_duration(situation),
                "risk_level": self._assess_risk(situation),
                "success_probability": self._estimate_success_probability(
                    situation, available_resources
                ),
            }

            self.emit_event("tactical_plan_created", {"plan_id": plan["plan_id"]})

            return plan

        except Exception as e:
            self.logger.error("Failed to plan tactical response: %s", e)
            return None

    def _initialize_command_hierarchy(self):
        """Initialize command hierarchy."""
        # Default command structure
        self._command_chain = {
            "supreme_commander": ["tactical_commander", "logistics_commander"],
            "tactical_commander": ["field_commander_alpha", "field_commander_beta"],
            "logistics_commander": ["supply_coordinator", "medical_coordinator"],
        }

        self._commander_roles = {
            "supreme_commander": "Overall strategic command",
            "tactical_commander": "Tactical operations",
            "logistics_commander": "Supply and logistics",
        }

    def _select_best_channel(self) -> CommunicationChannel:
        """Select best available communication channel."""
        # Priority: hardline > mesh > radio > satellite > runner
        if self.context.air_gapped:
            return CommunicationChannel.MESH
        return CommunicationChannel.RADIO

    def _get_broadcast_recipients(self, group: str | None) -> list[str]:
        """Get recipients for broadcast."""
        if group:
            return self._command_chain.get(group, [])
        # Broadcast to all
        all_recipients = set()
        for recipients in self._command_chain.values():
            all_recipients.update(recipients)
        return list(all_recipients)

    def _can_allocate_task_resources(self, task: Task) -> bool:
        """Check if resources can be allocated for task."""
        # Simplified check - would integrate with resource management in production
        return (
            len(task.resources_required) == 0 or len(self._resource_allocations) < 100
        )

    def _generate_recommended_actions(self, situation: dict[str, Any]) -> list[str]:
        """Generate recommended actions for a situation."""
        actions = []

        threat_level = situation.get("threat_level", 0)
        if threat_level > 7:
            actions.append("Evacuate civilians from threat zone")
            actions.append("Deploy tactical response teams")
            actions.append("Establish secure perimeter")
        elif threat_level > 4:
            actions.append("Monitor situation closely")
            actions.append("Pre-position response teams")
        else:
            actions.append("Continue standard operations")

        return actions

    def _estimate_resource_requirements(
        self, situation: dict[str, Any]
    ) -> dict[str, float]:
        """Estimate resource requirements."""
        threat_level = situation.get("threat_level", 0)

        return {
            "personnel": max(5, threat_level * 2),
            "ammunition": max(100, threat_level * 50),
            "medical_supplies": max(10, threat_level * 5),
            "fuel": max(50, threat_level * 10),
        }

    def _estimate_duration(self, situation: dict[str, Any]) -> int:
        """Estimate operation duration in seconds."""
        threat_level = situation.get("threat_level", 0)
        return max(1800, threat_level * 600)  # 30 min to 10+ hours

    def _assess_risk(self, situation: dict[str, Any]) -> str:
        """Assess risk level."""
        threat_level = situation.get("threat_level", 0)

        if threat_level >= 8:
            return "CRITICAL"
        elif threat_level >= 6:
            return "HIGH"
        elif threat_level >= 4:
            return "MODERATE"
        else:
            return "LOW"

    def _estimate_success_probability(
        self, situation: dict[str, Any], resources: dict[str, float]
    ) -> float:
        """Estimate probability of mission success."""
        threat_level = situation.get("threat_level", 0)
        required = self._estimate_resource_requirements(situation)

        # Calculate resource adequacy
        adequacy = 0.0
        for resource, amount in required.items():
            available = resources.get(resource, 0)
            adequacy += min(1.0, available / amount) if amount > 0 else 1.0

        adequacy /= len(required) if required else 1.0

        # Success probability based on resources and threat
        base_probability = 0.9 - (threat_level * 0.05)
        adjusted = base_probability * adequacy

        return max(0.1, min(0.95, adjusted))

    def _save_state(self):
        """Save persistent state."""
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "missions": {
                    mid: {
                        "mission_id": m.mission_id,
                        "name": m.name,
                        "objective": m.objective,
                        "status": m.status.value,
                        "priority": m.priority.value,
                        "created_at": m.created_at.isoformat(),
                    }
                    for mid, m in self._missions.items()
                },
                "metrics": self._metrics,
                "command_chain": self._command_chain,
            }

            state_file = self.data_path / "state.json"
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2, default=str)

            self.logger.info("State saved to %s", state_file)

        except Exception as e:
            self.logger.error("Failed to save state: %s", e)

    def _load_state(self):
        """Load persistent state."""
        try:
            state_file = self.data_path / "state.json"
            if state_file.exists():
                with open(state_file) as f:
                    state = json.load(f)

                self._metrics = state.get("metrics", self._metrics)
                self._command_chain = state.get("command_chain", self._command_chain)

                # Load missions
                for mission_data in state.get("missions", {}).values():
                    mission = Mission(
                        mission_id=mission_data["mission_id"],
                        name=mission_data["name"],
                        objective=mission_data["objective"],
                        priority=MissionPriority[mission_data["priority"]],
                        status=MissionStatus[mission_data["status"]],
                        created_at=datetime.fromisoformat(mission_data["created_at"]),
                    )
                    self._missions[mission.mission_id] = mission

                self.logger.info("State loaded from %s", state_file)

        except Exception as e:
            self.logger.error("Failed to load state: %s", e)
