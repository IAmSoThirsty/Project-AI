"""Cognitive IDE — Full-capability user-facing facade for the Miniature Office.

Provides the complete spatial code environment including:
  - Directive trees and floor/department browsing
  - Simulation engine control
  - Agent Lounge access (VR floor)
  - Meta Security overlay (VR enforcement)
  - Immutable audit trails
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class Directive:
    """A user intent expressed as a directive tree node."""

    directive_id: str
    intent: str
    sub_directives: list[Directive] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    assigned_agents: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class FloorInfo:
    """Information about a language floor in the office."""

    floor_number: int
    language: str
    department_count: int
    agent_count: int
    status: str = "active"


@dataclass
class SimulationSnapshot:
    """Snapshot of the simulation state."""

    tick: int
    total_agents: int
    active_tasks: int
    completed_tasks: int
    world_status: str = "running"
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


# ---------------------------------------------------------------------------
# CognitiveIDE Facade
# ---------------------------------------------------------------------------


class CognitiveIDE:
    """Full Cognitive IDE with VR, floors, simulation, lounge, and security.

    This is the primary user-facing facade. It aggregates all Miniature
    Office capabilities into a single interface that can be browsed via
    VR or accessed through the API.
    """

    def __init__(
        self,
        agent_lounge: Any | None = None,
        meta_security: Any | None = None,
    ) -> None:
        self._agent_lounge = agent_lounge
        self._meta_security = meta_security
        self._directives: list[Directive] = []
        self._simulation_tick: int = 0
        self._world = None
        self._simulation_engine = None
        self._audit_entries: list[dict[str, Any]] = []

        # Attempt to connect to vendored MO systems
        self._connect_mo_systems()

        logger.info("CognitiveIDE initialized — full capabilities active")

    # ------------------------------------------------------------------
    # Directive System
    # ------------------------------------------------------------------

    def create_directive(self, user_intent: str) -> Directive:
        """Create a directive tree from a user intent.

        Args:
            user_intent: Natural language description of what the user wants.

        Returns:
            Root Directive node.
        """
        directive = Directive(
            directive_id=f"dir_{uuid.uuid4().hex[:8]}",
            intent=user_intent,
        )
        self._directives.append(directive)
        self._log_audit("create_directive", {"id": directive.directive_id, "intent": user_intent})
        logger.info("Directive created: %s", user_intent)
        return directive

    def get_directives(self) -> list[Directive]:
        """Return all directives."""
        return list(self._directives)

    # ------------------------------------------------------------------
    # Floor / Department Browsing
    # ------------------------------------------------------------------

    def list_floors(self) -> list[FloorInfo]:
        """Return all language floors and their departments.

        Attempts to use the vendored world system; falls back to
        a static representation if not available.
        """
        if self._world and hasattr(self._world, "floors"):
            try:
                floors = []
                for i, floor in enumerate(self._world.floors):
                    floors.append(
                        FloorInfo(
                            floor_number=i,
                            language=getattr(floor, "language", f"Floor {i}"),
                            department_count=len(getattr(floor, "departments", [])),
                            agent_count=len(getattr(floor, "agents", [])),
                        )
                    )
                return floors
            except Exception as exc:
                logger.warning("Error reading world floors: %s", exc)

        # Fallback: static floor list from MO's default configuration
        return [
            FloorInfo(0, "Lobby / Agent Lounge", 1, 0),
            FloorInfo(1, "Python", 4, 8),
            FloorInfo(2, "JavaScript / TypeScript", 4, 6),
            FloorInfo(3, "Rust", 3, 4),
            FloorInfo(4, "Go", 3, 4),
            FloorInfo(5, "C / C++", 3, 4),
            FloorInfo(6, "Meta Security", 1, 4, "enforcing"),
        ]

    # ------------------------------------------------------------------
    # Simulation
    # ------------------------------------------------------------------

    def get_simulation_state(self) -> SimulationSnapshot:
        """Return the current simulation snapshot."""
        if self._simulation_engine and hasattr(self._simulation_engine, "get_state"):
            try:
                state = self._simulation_engine.get_state()
                return SimulationSnapshot(
                    tick=state.get("tick", self._simulation_tick),
                    total_agents=state.get("total_agents", 0),
                    active_tasks=state.get("active_tasks", 0),
                    completed_tasks=state.get("completed_tasks", 0),
                    world_status=state.get("status", "running"),
                )
            except Exception as exc:
                logger.warning("Simulation state error: %s", exc)

        return SimulationSnapshot(
            tick=self._simulation_tick,
            total_agents=0,
            active_tasks=0,
            completed_tasks=0,
            world_status="idle",
        )

    def step_simulation(self) -> SimulationSnapshot:
        """Advance the simulation by one tick."""
        if self._simulation_engine and hasattr(self._simulation_engine, "step"):
            try:
                self._simulation_engine.step()
            except Exception as exc:
                logger.warning("Simulation step error: %s", exc)

        self._simulation_tick += 1
        self._log_audit("simulation_step", {"tick": self._simulation_tick})
        return self.get_simulation_state()

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def get_audit_trail(self, entity_id: str | None = None) -> list[dict[str, Any]]:
        """Return the immutable audit log, optionally filtered by entity.

        Args:
            entity_id: If provided, filter to entries mentioning this entity.
        """
        if entity_id:
            return [
                e for e in self._audit_entries if entity_id in str(e.get("details", {}))
            ]
        return list(self._audit_entries)

    # ------------------------------------------------------------------
    # Lounge Integration
    # ------------------------------------------------------------------

    def get_lounge(self) -> Any:
        """Return the Agent Lounge for VR rendering."""
        return self._agent_lounge

    def get_lounge_state(self) -> dict[str, Any] | None:
        """Return the Lounge VR state snapshot."""
        if self._agent_lounge and hasattr(self._agent_lounge, "get_lounge_state"):
            state = self._agent_lounge.get_lounge_state()
            return {
                "floor_name": state.floor_name,
                "floor_number": state.floor_number,
                "agents_present": state.agents_present,
                "active_discussions": state.active_discussions,
                "pending_proposals": state.pending_proposals,
                "ambient_mood": state.ambient_mood,
            }
        return None

    # ------------------------------------------------------------------
    # Meta Security Integration
    # ------------------------------------------------------------------

    def get_meta_security_status(self) -> dict[str, Any] | None:
        """Return Meta Security state for VR overlay."""
        if self._meta_security and hasattr(self._meta_security, "get_security_state"):
            state = self._meta_security.get_security_state()
            return {
                "alert_level": state.alert_level.name,
                "active_violations": state.active_violations,
                "contained_components": state.contained_components,
                "restricted_users": state.restricted_users,
                "agents_deployed": state.agents_deployed,
                "system_integrity": state.system_integrity,
            }
        return None

    # ------------------------------------------------------------------
    # CouncilHub interface
    # ------------------------------------------------------------------

    def receive_message(self, from_id: str, message: str) -> None:
        """CouncilHub message handler."""
        logger.info("CognitiveIDE received message from %s: %s", from_id, message)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _connect_mo_systems(self) -> None:
        """Attempt to connect to vendored Miniature Office world + simulation."""
        try:
            from app.miniature_office.core.world import get_world

            self._world = get_world()
        except Exception:
            self._world = None

        try:
            from app.miniature_office.core.simulation import SimulationEngine

            self._simulation_engine = SimulationEngine
        except Exception:
            self._simulation_engine = None

    def _log_audit(self, action: str, details: dict[str, Any]) -> None:
        self._audit_entries.append(
            {
                "action": action,
                "timestamp": datetime.now(UTC).isoformat(),
                "details": details,
            }
        )
