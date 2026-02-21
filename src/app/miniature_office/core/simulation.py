"""
Simulation Engine - Tick-based World Processor
Implements Simulation Design Document Section II
"""

import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from app.miniature_office.agents.agent import Agent, Manager, get_consensus_system
from app.miniature_office.core.audit import EventType, get_audit_log
from app.miniature_office.core.mission import Task, TaskState
from app.miniature_office.core.world import Floor, Office, World, get_world
from app.miniature_office.departments.department import get_department_registry


@dataclass
class SimulationConfig:
    """Configuration for simulation engine"""

    tick_duration_ms: int = 100  # Duration of each tick in milliseconds
    auto_assign_tasks: bool = True
    auto_resolve_meetings: bool = True
    max_ticks: Optional[int] = None  # None for infinite


class AgentExecutionEngine:
    """
    Agent execution engine.
    Agents execute tasks based on capability alignment.
    """

    @staticmethod
    def process_agent(agent: Agent) -> None:
        """
        Process a single agent's execution (Simulation Doc Section 6).

        Agents:
        - If assigned task and capabilities cover preconditions: execute
        - Else: request support
        - Errors trigger blocking transitions
        """
        if not agent.current_task_id:
            return

        # Get current task
        from app.miniature_office.core.entity import get_registry

        task_entity = get_registry().get(agent.current_task_id)
        if not task_entity or not isinstance(task_entity, Task):
            return

        task = task_entity

        # Check if agent is blocked
        if agent.status == "blocked":
            return

        # Check if capabilities cover preconditions
        if not task.check_preconditions():
            # Request support or block
            agent.status = "blocked"
            task.block("Preconditions not met")

            get_audit_log().log_event(
                EventType.AGENT_ACTION,
                actor_id=agent.entity_id,
                target_id=task.entity_id,
                data={"action": "task_blocked", "reason": "preconditions_not_met"},
            )
            return

        # Execute task
        agent.status = "working"

        # Check if task needs a meeting due to ambiguity
        if task.needs_meeting():
            agent.status = "in_meeting"

            get_audit_log().log_event(
                EventType.AGENT_ACTION,
                actor_id=agent.entity_id,
                target_id=task.entity_id,
                data={"action": "meeting_required", "ambiguity_score": task.ambiguity_score},
            )
            return

        # Transition task through states
        if task.state == TaskState.SCHEDULED:
            task.transition_to(TaskState.IN_REVIEW, "Agent started work")
        elif task.state == TaskState.IN_REVIEW:
            # Check postconditions
            if task.check_postconditions():
                task.transition_to(TaskState.APPROVAL, "Work completed")
        elif task.state == TaskState.APPROVAL:
            # This requires manager approval - handled by manager
            pass


class ManagerDecisionProtocol:
    """
    Manager decision protocol for consensus and approval.
    Simulation Doc Section 5.
    """

    @staticmethod
    def process_manager(manager: Manager) -> None:
        """
        Process manager decisions.

        Managers execute:
        - For each task with unresolved conflicts: run consensus
        - Approve tasks in approval state
        """
        # Get all tasks managed by this manager
        from app.miniature_office.core.entity import get_registry

        # Find tasks in manager's department
        if not manager.department_id:
            return

        department = get_registry().get(manager.department_id)
        if not department:
            return

        # Process tasks requiring approval
        for agent_id in manager.managed_agents:
            agent = get_registry().get(agent_id)
            if not agent or not isinstance(agent, Agent):
                continue

            if not agent.current_task_id:
                continue

            task = get_registry().get(agent.current_task_id)
            if not task or not isinstance(task, Task):
                continue

            # Handle tasks in approval state
            if task.state == TaskState.APPROVAL:
                # Check if ready for commit (all criteria pass)
                if task.is_ready_for_commit():
                    # Initiate consensus if needed
                    consensus_system = get_consensus_system()
                    decision = consensus_system.initiate_consensus(
                        subject=f"Approval for task {task.name}", target_id=task.entity_id
                    )

                    # Manager votes
                    decision.add_vote(
                        agent_id=manager.entity_id,
                        vote=True,
                        weight=2.0,  # Manager has higher weight
                        reasoning="Task meets all acceptance criteria",
                    )

                    # Finalize
                    if consensus_system.finalize_consensus(decision.decision_id):
                        task.transition_to(TaskState.MERGED, "Approved by manager")
                        agent.complete_task()


class OfficeProcessor:
    """
    Office-level task dispatch and processing.
    Simulation Doc Section 4.
    """

    @staticmethod
    def process_office(office: Office) -> None:
        """
        Process an office.

        Task Dispatch:
        - If manager has tasks: assign to agents
        - Agents pick based on capability alignment
        """
        if not office.manager:
            return

        # Get manager's tasks
        from app.miniature_office.core.entity import get_registry  # noqa: F401

        # Find idle agents (for future task assignment)
        # (currently idle agent list is not used, but will be for smarter assignment)
        _ = [a for a in office.get_agents() if a.status == "idle"]

        # Simple task assignment (would be more sophisticated in real implementation)
        # For now, we just process existing tasks
        for agent in office.get_agents():
            AgentExecutionEngine.process_agent(agent)

        # Process manager decisions
        ManagerDecisionProtocol.process_manager(office.manager)


class FloorSimulator:
    """
    Floor-level simulation processing.
    Simulation Doc Section 3.
    """

    @staticmethod
    def process_floor(floor: Floor) -> None:
        """
        Process a floor.

        For each floor:
        - Process all offices
        - Handle floor-level coordination
        """
        for office in floor.offices.values():
            OfficeProcessor.process_office(office)

        # Ensure department is fully staffed
        if floor.department:
            dept_registry = get_department_registry()
            dept_registry.ensure_all_staffed()


class SimulationEngine:
    """
    Main simulation engine with tick-based processing.
    Implements Simulation Design Document Section 2.

    Engine Loop:
    while (world.isActive):
        world.time += 1
        for floor in floors:
            processFloor(floor)
        persistState(world)
    """

    def __init__(self, world: World, config: Optional[SimulationConfig] = None):
        self.world = world
        self.config = config or SimulationConfig()
        self.is_running = False
        self.tick_count = 0
        self.event_handlers: Dict[str, List[Callable]] = {}

    def register_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def emit_event(self, event_type: str, data: Dict):
        """Emit an event to all registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                handler(data)

    def tick(self) -> None:
        """
        Execute a single simulation tick.
        Part of the main engine loop.
        """
        if not self.world.is_active:
            return

        # Increment world time
        self.world.tick()
        self.tick_count += 1

        # Emit tick start event
        self.emit_event("tick_start", {"time": self.world.time})

        # Process all floors
        for floor in self.world.floors.values():
            FloorSimulator.process_floor(floor)

        # Persist state (in real implementation, this would save to database)
        self.persist_state()

        # Emit tick end event
        self.emit_event("tick_end", {"time": self.world.time})

        # Check if max ticks reached
        if self.config.max_ticks and self.tick_count >= self.config.max_ticks:
            self.stop()

    def persist_state(self) -> None:
        """
        Persist world state.
        In real implementation, this would save to database or file.
        """
        # For now, just log the state persistence
        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            target_id=self.world.world_id,
            data={"action": "state_persisted", "time": self.world.time, "tick_count": self.tick_count},
        )

    def run(self) -> None:
        """
        Run the simulation loop.
        Blocks until stopped or max_ticks reached.
        """
        self.is_running = True

        while self.is_running and self.world.is_active:
            tick_start = time.time()

            self.tick()

            # Sleep to maintain tick rate
            tick_duration = (time.time() - tick_start) * 1000
            sleep_time = max(0, self.config.tick_duration_ms - tick_duration) / 1000
            time.sleep(sleep_time)

    def step(self) -> None:
        """
        Execute a single step (tick) of the simulation.
        Used for manual stepping through simulation.
        """
        self.tick()

    def stop(self) -> None:
        """Stop the simulation"""
        self.is_running = False
        self.world.is_active = False

        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            target_id=self.world.world_id,
            data={"action": "simulation_stopped", "final_time": self.world.time, "total_ticks": self.tick_count},
        )

    def get_state(self) -> Dict:
        """Get current simulation state"""
        return {
            "world": self.world.to_dict(),
            "is_running": self.is_running,
            "tick_count": self.tick_count,
            "time": self.world.time,
        }


def create_simulation(world: Optional[World] = None, config: Optional[SimulationConfig] = None) -> SimulationEngine:
    """Create a simulation engine"""
    if world is None:
        world = get_world()
        if world is None:
            raise ValueError("No world instance available")

    return SimulationEngine(world, config)
