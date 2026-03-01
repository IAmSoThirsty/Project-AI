"""
Department Management System
Implements Codex Section 3 (Departmental Architecture)
"""

from typing import Dict, List, Optional, Set

from app.miniature_office.core.audit import EventType, get_audit_log
from app.miniature_office.core.entity import (
    Entity,
    EntityType,
    RelationType,
    get_registry,
)


class Department(Entity):
    """
    Department represents a language/runtime domain (Codex 1.1).
    Each department must have all required roles (Codex 3.1)
    """

    def __init__(
        self,
        department_id: str,
        name: str,
        domain: str,  # e.g., "Python", "Rust", "JavaScript"
        toolchain: Optional[List[str]] = None,
    ):
        super().__init__(department_id, EntityType.DEPARTMENT, name)
        self.domain = domain
        self.toolchain = toolchain or []
        self.agents: Dict = {}  # Role -> List of agent IDs
        self.contracts: List[str] = []  # Contract IDs this department implements

        # Register department
        get_registry().register(self)

        # Log creation
        get_audit_log().log_event(
            EventType.ENTITY_CREATED,
            target_id=self.entity_id,
            data={
                "entity_type": "department",
                "domain": domain,
                "toolchain": toolchain,
            },
        )

    def add_agent(self, agent):
        """
        Add an agent to this department.
        Agent must declare relationship before working here (Codex 1.2)
        """
        from app.miniature_office.agents.agent import Agent  # noqa: F401

        if agent.role not in self.agents:
            self.agents[agent.role] = []

        self.agents[agent.role].append(agent.entity_id)
        agent.department_id = self.entity_id

        # Declare relationship
        agent.declare_relationship(self, RelationType.WORKS_IN)

        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            actor_id=agent.entity_id,
            target_id=self.entity_id,
            data={"action": "joined_department"},
        )

    def get_missing_roles(self) -> Set:
        """
        Check for missing required roles.
        No department may neglect a role (Codex 3.1)
        """
        from app.miniature_office.agents.agent import AgentRole

        REQUIRED_ROLES = {
            AgentRole.ARCHITECT,
            AgentRole.BUILDER,
            AgentRole.VERIFIER,
            AgentRole.SECURITY,
            AgentRole.DOC_AGENT,
        }
        present_roles = {role for role, agents in self.agents.items() if agents}
        return REQUIRED_ROLES - present_roles

    def auto_spawn_assistants(self) -> List:
        """
        Auto-spawn assistant agents for missing roles (Codex 3.1).
        Missing roles auto-spawn assistant agents until fulfilled.
        """
        from app.miniature_office.agents.agent import Agent, AgentRole  # noqa: F401

        missing_roles = self.get_missing_roles()
        spawned_agents = []

        for role in missing_roles:
            agent_id = f"assistant_{role.value}_{self.entity_id[:8]}"
            agent = Agent(
                agent_id=agent_id,
                name=f"Assistant {role.value.title()}",
                role=role,
                department_id=self.entity_id,
                capabilities=self._default_capabilities_for_role(role),
            )
            self.add_agent(agent)
            spawned_agents.append(agent)

            get_audit_log().log_event(
                EventType.ENTITY_CREATED,
                target_id=agent.entity_id,
                data={
                    "entity_type": "assistant_agent",
                    "role": role.value,
                    "reason": "auto_spawned_for_missing_role",
                    "department_id": self.entity_id,
                },
            )

        return spawned_agents

    def _default_capabilities_for_role(self, role):
        """Generate default capabilities based on role and department domain"""
        from app.miniature_office.agents.agent import AgentRole, CapabilityProfile

        capabilities = CapabilityProfile()
        capabilities.languages.add(self.domain.lower())

        if role == AgentRole.ARCHITECT:
            capabilities.skills.update(["design", "architecture", "planning"])
            capabilities.security_clearance = 3
        elif role == AgentRole.BUILDER:
            capabilities.skills.update(["coding", "implementation"])
            capabilities.tools.update(["compiler", "interpreter"])
            capabilities.security_clearance = 2
        elif role == AgentRole.VERIFIER:
            capabilities.skills.update(["testing", "validation", "debugging"])
            capabilities.tools.update(["test_framework", "linter"])
            capabilities.security_clearance = 2
        elif role == AgentRole.SECURITY:
            capabilities.skills.update(["security", "threat_modeling", "auditing"])
            capabilities.security_clearance = 4
        elif role == AgentRole.DOC_AGENT:
            capabilities.skills.update(["documentation", "communication", "writing"])
            capabilities.security_clearance = 2

        return capabilities

    def add_tool_to_toolchain(self, tool_id: str):
        """
        Add a tool to department's toolchain.
        Must declare Department ↔ Toolchain relationship (Codex 1.2)
        """
        if tool_id not in self.toolchain:
            self.toolchain.append(tool_id)

            # Get tool entity and declare relationship
            tool = get_registry().get(tool_id)
            if tool:
                self.declare_relationship(tool, RelationType.USES)

    def has_role_filled(self, role) -> bool:
        """Check if a specific role is filled"""
        return len(self.agents.get(role, [])) > 0

    def is_fully_staffed(self) -> bool:
        """Check if all required roles are filled"""
        return len(self.get_missing_roles()) == 0

    def get_agents_by_role(self, role) -> List:
        """Get all agents with a specific role in this department"""
        from app.miniature_office.agents.agent import Agent

        agent_ids = self.agents.get(role, [])
        agents = []
        for agent_id in agent_ids:
            agent = get_registry().get(agent_id)
            if agent and isinstance(agent, Agent):
                agents.append(agent)
        return agents

    def implement_contract(self, contract_id: str):
        """
        Declare that this department implements a contract (Codex 6.1)
        """
        if contract_id not in self.contracts:
            self.contracts.append(contract_id)

            contract = get_registry().get(contract_id)
            if contract:
                self.declare_relationship(contract, RelationType.IMPLEMENTS)


class DepartmentRegistry:
    """Registry for managing all departments"""

    def __init__(self):
        self.departments: Dict[str, Department] = {}

    def register_department(self, department: Department):
        """Register a department"""
        self.departments[department.entity_id] = department

        # Auto-spawn assistants for missing roles
        department.auto_spawn_assistants()

    def get_department(self, department_id: str) -> Optional[Department]:
        """Get a department by ID"""
        return self.departments.get(department_id)

    def get_departments_by_domain(self, domain: str) -> List[Department]:
        """Get all departments for a specific domain"""
        return [
            d for d in self.departments.values() if d.domain.lower() == domain.lower()
        ]

    def ensure_all_staffed(self):
        """Ensure all departments have all required roles filled"""
        for department in self.departments.values():
            if not department.is_fully_staffed():
                department.auto_spawn_assistants()


# Global department registry
_department_registry = DepartmentRegistry()


def get_department_registry() -> DepartmentRegistry:
    """Get the global department registry"""
    return _department_registry
