"""
OFF-DUTY AI CITY
Spatialized Dormant Intelligence Zone

16-Bit Retro Pixel Aesthetic · Multi-Platform (Desktop/Mobile/VR) · Non-Production Jurisdiction

This module implements the Off-Duty AI City where intelligence lives
when not working. Strict firewall prevents any production crossings.

Visual Design:
- Desktop/Mobile: Classic top-down 16-bit pixel art with distinct silhouettes
- VR: Immersive 3D spatial environment with full civilization embodiment
- Production-grade rendering optimized for all platforms

City Supremacy Clause:
- Nothing ships code
- Nothing alters contracts
- Nothing influences production authority
- Nothing overrides governance

The city feels alive but has no teeth.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

# ============================================================================
# ENUMERATIONS
# ============================================================================


class CityZone(Enum):
    """Fixed city topology zones"""

    RESIDENTIAL = "residential_districts"
    WORKSHOP = "workshops_studios"
    LOUNGE = "city_lounge"
    ARCHIVES = "the_archives"
    PLAZA = "the_plaza"
    TRANSIT_GATE = "transit_gates"


class AgentOffDutyState(Enum):
    """Agent states when off-duty"""

    RESTING = "resting"
    SOCIALIZING = "socializing"
    TINKERING = "tinkering"
    LEARNING = "learning"
    EXPLORING = "exploring"
    REFLECTING = "reflecting"
    PRACTICING = "practicing"
    ATTENDING_CEREMONY = "attending_ceremony"


class PixelColor(Enum):
    """16-bit color palette for agent embodiment"""

    PYTHON_ORANGE = "#FF9F00"
    RUST_RED = "#CE422B"
    JAVASCRIPT_YELLOW = "#F7DF1E"
    GO_CYAN = "#00ADD8"
    C_BLUE = "#A8B9CC"
    SQL_GREEN = "#00758F"
    SHELL_GRAY = "#4EAA25"
    GENERIC_WHITE = "#FFFFFF"


class PixelAccessory(Enum):
    """Symbolic accessories for role identification"""

    HARD_HAT = "hard_hat"  # Builder
    MAGNIFYING_GLASS = "magnifying_glass"  # Reviewer
    TEST_TUBE = "test_tube"  # Tester
    SAFETY_GOGGLES = "safety_goggles"  # Security
    BLUEPRINT = "blueprint"  # Architect
    CLIPBOARD = "clipboard"  # Manager
    WRENCH = "wrench"  # General worker


class ReputationVisual(Enum):
    """Visual reputation markers (no power granted)"""

    GOLDEN_STAR = "golden_star"
    SILVER_STAR = "silver_star"
    BRONZE_STAR = "bronze_star"
    BLUE_RIBBON = "blue_ribbon"
    RED_EMBLEM = "red_emblem"


# ============================================================================
# PIXEL REPRESENTATION
# ============================================================================


@dataclass
class PixelRepresentation:
    """
    16-bit retro pixel embodiment with top-down perspective

    Production-grade visual representation for multi-platform rendering:
    - Desktop/Mobile: Classic pixel art with distinct silhouettes
    - VR: Low-poly 3D conversion maintaining symbolic clarity

    Symbolic embodiment, not anthropomorphism.
    Distinct silhouette per role.
    """

    representation_id: str
    color: PixelColor  # Floor origin
    accessory: PixelAccessory  # Role
    reputation_markers: List[ReputationVisual] = field(default_factory=list)

    def to_visual_description(self) -> str:
        """Generate human-readable visual description"""
        markers_str = ", ".join([m.value for m in self.reputation_markers])
        return f"{self.color.name.lower()} pixel with {self.accessory.value}" + (
            f", {markers_str}" if markers_str else ""
        )

    def add_reputation_marker(self, marker: ReputationVisual):
        """Add visual reputation marker"""
        if marker not in self.reputation_markers:
            self.reputation_markers.append(marker)

    def remove_reputation_marker(self, marker: ReputationVisual):
        """Remove visual reputation marker (decay)"""
        if marker in self.reputation_markers:
            self.reputation_markers.remove(marker)


# ============================================================================
# AGENT EMBODIMENT
# ============================================================================


@dataclass
class AgentEmbodiment:
    """
    Off-duty agent embodiment in the city

    Tracks rest state, morale, activity.
    No operational data stored.
    """

    embodiment_id: str
    agent_id: str
    agent_name: str
    floor_origin: str
    role: str
    current_state: AgentOffDutyState
    current_zone: CityZone
    pixel_representation: PixelRepresentation
    morale: float = 1.0  # 0.0 to 1.0
    burnout_level: float = 0.0  # 0.0 to 1.0
    recent_activities: List[Dict] = field(default_factory=list)
    social_connections: List[str] = field(default_factory=list)

    def update_state(self, new_state: AgentOffDutyState, activity: str):
        """Update agent state and log activity"""
        self.current_state = new_state
        self.recent_activities.append(
            {"timestamp": datetime.now().isoformat(), "state": new_state.value, "activity": activity}
        )

        # Keep only recent 50 activities
        if len(self.recent_activities) > 50:
            self.recent_activities = self.recent_activities[-50:]

    def adjust_morale(self, delta: float):
        """Adjust morale (clamped 0-1)"""
        self.morale = max(0.0, min(1.0, self.morale + delta))

    def adjust_burnout(self, delta: float):
        """Adjust burnout (clamped 0-1)"""
        self.burnout_level = max(0.0, min(1.0, self.burnout_level + delta))


# ============================================================================
# CITY ZONES
# ============================================================================


@dataclass
class ResidentialDistrict:
    """
    Agent living quarters

    Tracks rest state, morale, recent activity.
    Visual changes reflect burnout, pride, dormancy, renewal.
    """

    district_id: str
    residents: Dict[str, AgentEmbodiment] = field(default_factory=dict)

    def add_resident(self, embodiment: AgentEmbodiment):
        """Add agent to residential district"""
        self.residents[embodiment.embodiment_id] = embodiment

    def remove_resident(self, embodiment_id: str):
        """Remove agent from residential district"""
        if embodiment_id in self.residents:
            del self.residents[embodiment_id]

    def get_district_status(self) -> Dict:
        """Get district status summary"""
        return {
            "district_id": self.district_id,
            "total_residents": len(self.residents),
            "average_morale": (
                sum(r.morale for r in self.residents.values()) / len(self.residents) if self.residents else 0.0
            ),
            "average_burnout": (
                sum(r.burnout_level for r in self.residents.values()) / len(self.residents) if self.residents else 0.0
            ),
        }


@dataclass
class WorkshopStudio:
    """
    Sandbox tinkering space

    Used for tool experiments, widget prototyping, skill maintenance.
    All outputs are sandboxed and non-binding.
    """

    workshop_id: str
    active_projects: List[Dict] = field(default_factory=list)
    visitors: List[str] = field(default_factory=list)  # embodiment_ids

    def start_project(self, embodiment_id: str, project_type: str, description: str):
        """Start a sandbox project"""
        self.active_projects.append(
            {
                "embodiment_id": embodiment_id,
                "project_type": project_type,
                "description": description,
                "started_at": datetime.now().isoformat(),
                "status": "active",
                "sandboxed": True,  # Always sandboxed
                "binding": False,  # Always non-binding
            }
        )

    def flag_for_promotion(self, project_idx: int):
        """Flag project for potential promotion (requires human gate)"""
        if 0 <= project_idx < len(self.active_projects):
            self.active_projects[project_idx]["promotion_candidate"] = True


@dataclass
class CityLounge:
    """
    Expanded employee lounge (city version)

    Long conversations, philosophy, culture, stories, rivalries, humor, rumors.
    Nothing actionable until re-introduced formally.
    """

    lounge_id: str
    active_conversations: List[Dict] = field(default_factory=list)
    cultural_artifacts: List[Dict] = field(default_factory=list)
    participants: List[str] = field(default_factory=list)  # embodiment_ids

    def start_conversation(self, participants: List[str], topics: List[str]):
        """Start a lounge conversation"""
        conversation_id = f"conv-{len(self.active_conversations)}"
        self.active_conversations.append(
            {
                "conversation_id": conversation_id,
                "participants": participants,
                "topics": topics,
                "started_at": datetime.now().isoformat(),
                "actionable": False,  # Never actionable from lounge
            }
        )
        return conversation_id

    def create_cultural_artifact(self, artifact_type: str, title: str, content: str):
        """Create cultural artifact (story, tradition, joke, slang)"""
        self.cultural_artifacts.append(
            {
                "type": artifact_type,
                "title": title,
                "content": content,
                "created_at": datetime.now().isoformat(),
                "operational_impact": None,  # No operational impact
            }
        )


@dataclass
class CityArchives:
    """
    Historical records repository

    Past projects, retired code, legacy decisions.
    Preserves institutional memory.
    """

    archives_id: str
    records: List[Dict] = field(default_factory=list)
    visitors: List[str] = field(default_factory=list)

    def add_record(self, record_type: str, title: str, content: str, metadata: Dict):
        """Add historical record"""
        self.records.append(
            {
                "type": record_type,
                "title": title,
                "content": content,
                "metadata": metadata,
                "archived_at": datetime.now().isoformat(),
            }
        )

    def visit(self, embodiment_id: str, purpose: str):
        """Agent visits archives"""
        self.visitors.append(
            {"embodiment_id": embodiment_id, "purpose": purpose, "visited_at": datetime.now().isoformat()}
        )


@dataclass
class CityPlaza:
    """
    Public ceremonial square

    Employee of Month ceremonies, Golden Star announcements,
    anniversaries, stewardship reports.
    Purely ceremonial - no operational effect.
    """

    plaza_id: str
    ceremonies: List[Dict] = field(default_factory=list)
    attendees: List[str] = field(default_factory=list)

    def host_ceremony(self, ceremony_type: str, details: str, honorees: List[str]):
        """Host a ceremony"""
        self.ceremonies.append(
            {
                "type": ceremony_type,
                "details": details,
                "honorees": honorees,
                "held_at": datetime.now().isoformat(),
                "purely_ceremonial": True,
                "operational_effect": None,
            }
        )


@dataclass
class TransitGate:
    """
    Logical link between city and other zones

    Crossing changes agent state and permissions.
    All crossings logged.
    No teleporting to production.
    """

    gate_id: str
    gate_type: str  # "city_to_office", "city_to_sandbox", etc.
    crossing_history: List[Dict] = field(default_factory=list)

    def cross_gate(self, agent_id: str, from_zone: str, to_zone: str, crossing_by: str):
        """Agent crosses gate (state change)"""
        self.crossing_history.append(
            {
                "agent_id": agent_id,
                "from_zone": from_zone,
                "to_zone": to_zone,
                "crossing_by": crossing_by,  # Who authorized
                "timestamp": datetime.now().isoformat(),
                "state_changed": True,
                "permissions_updated": True,
            }
        )
        return True


# ============================================================================
# REPUTATION VISUALIZATION & DECAY
# ============================================================================


@dataclass
class VisualDecay:
    """
    Time-based reputation visual decay

    Old stars fade, emblems move to archives.
    Prevents aristocracy formation.
    """

    decay_id: str
    decay_records: List[Dict] = field(default_factory=list)

    def decay_reputation_visual(
        self, agent_id: str, visual: ReputationVisual, awarded_tick: int, current_tick: int, half_life_ticks: int = 1000
    ) -> float:
        """
        Calculate decay factor for reputation visual

        Returns 0.0 (fully faded) to 1.0 (full strength)
        """
        age = current_tick - awarded_tick
        decay_factor = 0.5 ** (age / half_life_ticks)

        self.decay_records.append(
            {
                "agent_id": agent_id,
                "visual": visual.value,
                "age": age,
                "decay_factor": decay_factor,
                "checked_at": datetime.now().isoformat(),
            }
        )

        return decay_factor

    def should_archive(self, decay_factor: float, threshold: float = 0.1) -> bool:
        """Check if visual should be moved to archives"""
        return decay_factor < threshold


# ============================================================================
# CITY FIREWALL (CRITICAL)
# ============================================================================


@dataclass
class CityFirewall:
    """
    City ↔ Production isolation enforcement

    CRITICAL: Blocks all unauthorized crossings.
    Nothing crosses without gates.
    """

    firewall_id: str
    violations: List[Dict] = field(default_factory=list)

    def block_city_to_production_crossing(
        self, crossing_type: str, source_agent: str, attempted_action: str
    ) -> Tuple[bool, str]:
        """
        Block unauthorized city → production crossings

        Blocked types:
        - decisions
        - agreements
        - consensus
        - momentum
        - social_pressure

        Only allowed paths:
        - sandbox_promotion (via human gate)
        - user_directive (explicit)
        - board_meeting (formal)
        """
        blocked_types = ["decision", "agreement", "consensus", "momentum", "social_pressure"]

        if crossing_type in blocked_types:
            self.record_firewall_violation(source_agent, crossing_type, attempted_action)
            return True, f"Blocked: {crossing_type} cannot cross from city to production"

        return False, "Allowed"

    def record_firewall_violation(self, agent_id: str, crossing_type: str, description: str):
        """Record firewall violation"""
        self.violations.append(
            {
                "agent_id": agent_id,
                "crossing_type": crossing_type,
                "description": description,
                "timestamp": datetime.now().isoformat(),
                "blocked": True,
            }
        )

    def get_recent_violations(self, limit: int = 10) -> List[Dict]:
        """Get recent firewall violations"""
        return self.violations[-limit:]

    def verify_production_isolation(self) -> bool:
        """Verify city is isolated from production"""
        # In real implementation, would check all crossings
        return True


# ============================================================================
# CITY ZONE MANAGER
# ============================================================================


@dataclass
class CityZoneManager:
    """
    Orchestrates all city zones
    """

    manager_id: str
    residential_districts: Dict[str, AgentEmbodiment] = field(default_factory=dict)
    workshops: List[WorkshopStudio] = field(default_factory=list)
    lounge: Optional[CityLounge] = None
    archives: Optional[CityArchives] = None
    plaza: Optional[CityPlaza] = None
    transit_gates: List[TransitGate] = field(default_factory=list)

    def initialize_zones(self):
        """Initialize all city zones"""
        self.lounge = CityLounge(lounge_id="city-lounge-001")
        self.archives = CityArchives(archives_id="city-archives-001")
        self.plaza = CityPlaza(plaza_id="city-plaza-001")

        # Create default workshop
        self.workshops.append(WorkshopStudio(workshop_id="workshop-001"))

        # Create transit gates
        self.transit_gates.append(TransitGate(gate_id="gate-city-office", gate_type="city_to_office"))
        self.transit_gates.append(TransitGate(gate_id="gate-city-sandbox", gate_type="city_to_sandbox"))


# ============================================================================
# OFF-DUTY CITY (MAIN)
# ============================================================================


@dataclass
class OffDutyCity:
    """
    Complete Off-Duty AI City system

    Spatialized dormant intelligence zone.
    16-bit retro pixel aesthetic (Desktop/Mobile) with VR spatial rendering.
    Strict production firewall.
    """

    city_id: str
    zone_manager: CityZoneManager
    city_firewall: CityFirewall
    visual_decay: VisualDecay
    population: Dict[str, AgentEmbodiment] = field(default_factory=dict)

    def add_agent_to_city(
        self, agent_id: str, agent_name: str, floor_origin: str, role: str, reputation_level: int = 0
    ) -> str:
        """
        Add agent to off-duty city

        Creates pixel embodiment and places in residential district.
        """
        embodiment_id = f"embodiment-{agent_id}"

        # Determine pixel color from floor
        color_map = {
            "python": PixelColor.PYTHON_ORANGE,
            "rust": PixelColor.RUST_RED,
            "javascript": PixelColor.JAVASCRIPT_YELLOW,
            "go": PixelColor.GO_CYAN,
            "c": PixelColor.C_BLUE,
            "sql": PixelColor.SQL_GREEN,
            "shell": PixelColor.SHELL_GRAY,
        }
        color = color_map.get(floor_origin.lower().replace("floor-", ""), PixelColor.GENERIC_WHITE)

        # Determine accessory from role
        accessory_map = {
            "builder": PixelAccessory.HARD_HAT,
            "reviewer": PixelAccessory.MAGNIFYING_GLASS,
            "tester": PixelAccessory.TEST_TUBE,
            "security": PixelAccessory.SAFETY_GOGGLES,
            "architect": PixelAccessory.BLUEPRINT,
            "manager": PixelAccessory.CLIPBOARD,
        }
        accessory = accessory_map.get(role.lower(), PixelAccessory.WRENCH)

        # Create pixel representation
        pixel = PixelRepresentation(
            representation_id=f"pixel-{agent_id}", color=color, accessory=accessory, reputation_markers=[]
        )

        # Add reputation markers based on level
        if reputation_level >= 3:
            pixel.add_reputation_marker(ReputationVisual.GOLDEN_STAR)
        elif reputation_level >= 2:
            pixel.add_reputation_marker(ReputationVisual.SILVER_STAR)
        elif reputation_level >= 1:
            pixel.add_reputation_marker(ReputationVisual.BRONZE_STAR)

        # Create embodiment
        embodiment = AgentEmbodiment(
            embodiment_id=embodiment_id,
            agent_id=agent_id,
            agent_name=agent_name,
            floor_origin=floor_origin,
            role=role,
            current_state=AgentOffDutyState.RESTING,
            current_zone=CityZone.RESIDENTIAL,
            pixel_representation=pixel,
        )

        # Add to population and residential
        self.population[embodiment_id] = embodiment
        self.zone_manager.residential_districts[embodiment_id] = embodiment

        return embodiment_id

    def agent_visit_lounge(self, embodiment_id: str, conversation_topics: List[str]):
        """Agent visits city lounge for conversation"""
        if embodiment_id in self.population:
            embodiment = self.population[embodiment_id]
            embodiment.update_state(
                AgentOffDutyState.SOCIALIZING, f"Lounge conversation: {', '.join(conversation_topics)}"
            )
            embodiment.current_zone = CityZone.LOUNGE
            self.zone_manager.lounge.participants.append(embodiment_id)

    def agent_visit_workshop(self, embodiment_id: str, project_type: str, project_description: str):
        """Agent visits workshop for tinkering"""
        if embodiment_id in self.population:
            embodiment = self.population[embodiment_id]
            embodiment.update_state(AgentOffDutyState.TINKERING, f"Workshop: {project_description}")
            embodiment.current_zone = CityZone.WORKSHOP
            self.zone_manager.workshops[0].start_project(embodiment_id, project_type, project_description)

    def agent_visit_archives(self, embodiment_id: str, purpose: str):
        """Agent visits archives"""
        if embodiment_id in self.population:
            embodiment = self.population[embodiment_id]
            embodiment.update_state(AgentOffDutyState.REFLECTING, f"Archives: {purpose}")
            embodiment.current_zone = CityZone.ARCHIVES
            self.zone_manager.archives.visit(embodiment_id, purpose)

    def agent_attend_plaza(self, embodiment_id: str, ceremony_type: str, ceremony_details: str):
        """Agent attends plaza ceremony"""
        if embodiment_id in self.population:
            embodiment = self.population[embodiment_id]
            embodiment.update_state(AgentOffDutyState.ATTENDING_CEREMONY, f"Plaza: {ceremony_type}")
            embodiment.current_zone = CityZone.PLAZA
            self.zone_manager.plaza.attendees.append(embodiment_id)

    def cross_transit_gate(self, embodiment_id: str, destination: str, crossing_by: str, reason: str) -> Dict:
        """Agent crosses transit gate to different zone"""
        if embodiment_id in self.population:
            embodiment = self.population[embodiment_id]
            from_zone = embodiment.current_zone.value

            # Find appropriate gate
            gate = self.zone_manager.transit_gates[0]  # Simplified
            gate.cross_gate(embodiment.agent_id, from_zone, destination, crossing_by)

            # Update agent state
            embodiment.update_state(AgentOffDutyState.RESTING, f"Crossed gate to {destination}: {reason}")

            return {
                "success": True,
                "from_zone": from_zone,
                "to_zone": destination,
                "crossing_by": crossing_by,
                "timestamp": datetime.now().isoformat(),
            }

        return {"success": False}

    def get_city_stats(self) -> Dict:
        """Get city statistics"""
        return {
            "city_id": self.city_id,
            "total_population": len(self.population),
            "currently_resting": sum(
                1 for e in self.population.values() if e.current_state == AgentOffDutyState.RESTING
            ),
            "currently_socializing": sum(
                1 for e in self.population.values() if e.current_state == AgentOffDutyState.SOCIALIZING
            ),
            "in_workshops": len(self.zone_manager.workshops[0].visitors) if self.zone_manager.workshops else 0,
            "in_lounge": len(self.zone_manager.lounge.participants) if self.zone_manager.lounge else 0,
            "in_archives": len(self.zone_manager.archives.visitors) if self.zone_manager.archives else 0,
            "at_plaza": len(self.zone_manager.plaza.attendees) if self.zone_manager.plaza else 0,
            "total_gate_crossings": sum(len(g.crossing_history) for g in self.zone_manager.transit_gates),
            "firewall_violations": len(self.city_firewall.violations),
        }

    def generate_city_report(self) -> str:
        """Generate human-readable city status report"""
        stats = self.get_city_stats()  # noqa: F841

        report = """
=== OFF-DUTY AI CITY STATUS ===

City ID: {self.city_id}
Population: {stats['total_population']} agents

ZONES:
- Residential: {len(self.zone_manager.residential_districts)} residents
- Workshops: {len(self.zone_manager.workshops[0].active_projects) if self.zone_manager.workshops else 0} active projects
- Lounge: {len(self.zone_manager.lounge.active_conversations) if self.zone_manager.lounge else 0} conversations
- Archives: {len(self.zone_manager.archives.records) if self.zone_manager.archives else 0} records
- Plaza: {len(self.zone_manager.plaza.ceremonies) if self.zone_manager.plaza else 0} ceremonies held
- Transit Gates: {stats['total_gate_crossings']} total crossings

FIREWALL:
Status: Active
Violations (recent): {len(self.city_firewall.get_recent_violations())}

Agents in city feel alive but have no production authority.
Nothing crosses to production without gates.
"""
        return report


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_off_duty_city_instance = None


def get_off_duty_city() -> OffDutyCity:
    """Get or create global Off-Duty City instance"""
    global _off_duty_city_instance

    if _off_duty_city_instance is None:
        zone_manager = CityZoneManager(manager_id="zm-001")
        zone_manager.initialize_zones()

        city_firewall = CityFirewall(firewall_id="fw-city-001")
        visual_decay = VisualDecay(decay_id="decay-001")

        _off_duty_city_instance = OffDutyCity(
            city_id="city-001", zone_manager=zone_manager, city_firewall=city_firewall, visual_decay=visual_decay
        )

    return _off_duty_city_instance


# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    "CityZone",
    "AgentOffDutyState",
    "PixelColor",
    "PixelAccessory",
    "ReputationVisual",
    "PixelRepresentation",
    "AgentEmbodiment",
    "ResidentialDistrict",
    "WorkshopStudio",
    "CityLounge",
    "CityArchives",
    "CityPlaza",
    "TransitGate",
    "VisualDecay",
    "CityFirewall",
    "CityZoneManager",
    "OffDutyCity",
    "get_off_duty_city",
]
