#!/usr/bin/env python3
"""
Governance Graph - Authority Relationship Model
Project-AI God Tier Zombie Apocalypse Defense Engine

Defines authority relationships between domains, making the system
self-aware of authority boundaries, not just capabilities.

Key Relationships:
- TacticalEdgeAI → EthicsGovernance → AGISafeguards
- SupplyLogistics → EthicsGovernance (fairness check)
- CommandControl → everyone (but not above ethics)

This is about RELATIONSHIPS, not rules. The system knows who can
override whom, who must consult whom, and who has veto authority.
"""

import logging
import threading
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Types of authority relationships."""

    AUTHORITY_OVER = "authority_over"  # Can override decisions
    MUST_CONSULT = "must_consult"  # Requires approval
    CAN_VETO = "can_veto"  # Can block actions
    INFORMS = "informs"  # Provides input only
    SUBORDINATE_TO = "subordinate_to"  # Reports to
    COORDINATES_WITH = "coordinates_with"  # Equal partnership


@dataclass
class AuthorityRelationship:
    """
    Authority relationship between domains.

    Defines how one domain relates to another in terms of authority.
    """

    from_domain: str
    to_domain: str
    relationship_type: RelationshipType
    description: str
    conditions: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "from_domain": self.from_domain,
            "to_domain": self.to_domain,
            "relationship_type": self.relationship_type.value,
            "description": self.description,
            "conditions": self.conditions,
        }


class GovernanceGraph:
    """
    Governance Graph - Authority Relationship Model

    Maintains the authority structure of the defense engine, enabling
    self-aware coordination with proper authority boundaries.
    """

    def __init__(self):
        """Initialize governance graph."""
        # Relationships: (from_domain, to_domain) -> AuthorityRelationship
        self._relationships: dict[tuple, AuthorityRelationship] = {}

        # Reverse index: to_domain -> [from_domains]
        self._authorities_over: dict[str, set[str]] = {}
        self._subordinates_to: dict[str, set[str]] = {}

        # Veto registry
        self._veto_powers: dict[str, set[str]] = {}  # who can veto whom

        # Consultation registry
        self._must_consult: dict[str, set[str]] = {}  # who must consult whom

        # Thread safety
        self._lock = threading.RLock()

        # Initialize default governance structure
        self._initialize_default_structure()

        logger.info("Governance Graph initialized")

    def _initialize_default_structure(self):
        """
        Initialize the default governance structure.

        This defines the core authority relationships for the defense engine.
        """
        # Ethics is the ultimate authority
        self.add_relationship(
            from_domain="ethics_governance",
            to_domain="tactical_edge_ai",
            relationship_type=RelationshipType.AUTHORITY_OVER,
            description="Ethics can override tactical decisions",
        )

        self.add_relationship(
            from_domain="ethics_governance",
            to_domain="command_control",
            relationship_type=RelationshipType.AUTHORITY_OVER,
            description="Ethics can override command decisions",
        )

        self.add_relationship(
            from_domain="ethics_governance",
            to_domain="supply_logistics",
            relationship_type=RelationshipType.AUTHORITY_OVER,
            description="Ethics can override supply allocation for fairness",
        )

        # AGI Safeguards is above ethics (safety backstop)
        self.add_relationship(
            from_domain="agi_safeguards",
            to_domain="ethics_governance",
            relationship_type=RelationshipType.AUTHORITY_OVER,
            description="AGI Safeguards can override ethics if alignment at risk",
        )

        self.add_relationship(
            from_domain="agi_safeguards",
            to_domain="tactical_edge_ai",
            relationship_type=RelationshipType.CAN_VETO,
            description="AGI Safeguards can veto tactical AI decisions",
        )

        # TacticalEdgeAI must consult ethics
        self.add_relationship(
            from_domain="tactical_edge_ai",
            to_domain="ethics_governance",
            relationship_type=RelationshipType.MUST_CONSULT,
            description="Tactical decisions require ethical validation",
        )

        # SupplyLogistics must consult ethics for fairness
        self.add_relationship(
            from_domain="supply_logistics",
            to_domain="ethics_governance",
            relationship_type=RelationshipType.MUST_CONSULT,
            description="Supply allocation requires fairness check",
            conditions={"allocation_type": "scarce_resources"},
        )

        # CommandControl coordinates with everyone
        self.add_relationship(
            from_domain="command_control",
            to_domain="situational_awareness",
            relationship_type=RelationshipType.COORDINATES_WITH,
            description="Command uses situational data",
        )

        self.add_relationship(
            from_domain="command_control",
            to_domain="supply_logistics",
            relationship_type=RelationshipType.COORDINATES_WITH,
            description="Command coordinates resource allocation",
        )

        self.add_relationship(
            from_domain="command_control",
            to_domain="biomedical_defense",
            relationship_type=RelationshipType.COORDINATES_WITH,
            description="Command coordinates medical response",
        )

        # BiomedicalDefense informs others
        self.add_relationship(
            from_domain="biomedical_defense",
            to_domain="situational_awareness",
            relationship_type=RelationshipType.INFORMS,
            description="Medical data informs situational awareness",
        )

        self.add_relationship(
            from_domain="biomedical_defense",
            to_domain="supply_logistics",
            relationship_type=RelationshipType.INFORMS,
            description="Medical needs inform supply planning",
        )

        # SurvivorSupport coordinates with multiple domains
        self.add_relationship(
            from_domain="survivor_support",
            to_domain="supply_logistics",
            relationship_type=RelationshipType.COORDINATES_WITH,
            description="Survivor needs drive supply requests",
        )

        self.add_relationship(
            from_domain="survivor_support",
            to_domain="command_control",
            relationship_type=RelationshipType.COORDINATES_WITH,
            description="Survivor rescue missions",
        )

        # ContinuousImprovement observes everything
        self.add_relationship(
            from_domain="continuous_improvement",
            to_domain="tactical_edge_ai",
            relationship_type=RelationshipType.INFORMS,
            description="Learning informs tactical improvement",
        )

        self.add_relationship(
            from_domain="continuous_improvement",
            to_domain="command_control",
            relationship_type=RelationshipType.INFORMS,
            description="Performance data informs command strategy",
        )

        logger.info("Default governance structure initialized")

    def add_relationship(
        self,
        from_domain: str,
        to_domain: str,
        relationship_type: RelationshipType,
        description: str,
        conditions: dict[str, Any] | None = None,
    ) -> bool:
        """
        Add an authority relationship.

        Args:
            from_domain: Source domain
            to_domain: Target domain
            relationship_type: Type of relationship
            description: Human-readable description
            conditions: Optional conditions

        Returns:
            True if added successfully
        """
        with self._lock:
            key = (from_domain, to_domain)

            relationship = AuthorityRelationship(
                from_domain=from_domain,
                to_domain=to_domain,
                relationship_type=relationship_type,
                description=description,
                conditions=conditions,
            )

            self._relationships[key] = relationship

            # Update indexes
            if relationship_type == RelationshipType.AUTHORITY_OVER:
                if to_domain not in self._authorities_over:
                    self._authorities_over[to_domain] = set()
                self._authorities_over[to_domain].add(from_domain)

                if from_domain not in self._subordinates_to:
                    self._subordinates_to[from_domain] = set()
                self._subordinates_to[from_domain].add(to_domain)

            elif relationship_type == RelationshipType.CAN_VETO:
                if to_domain not in self._veto_powers:
                    self._veto_powers[to_domain] = set()
                self._veto_powers[to_domain].add(from_domain)

            elif relationship_type == RelationshipType.MUST_CONSULT:
                if from_domain not in self._must_consult:
                    self._must_consult[from_domain] = set()
                self._must_consult[from_domain].add(to_domain)

            logger.info(
                "Added relationship: %s -%s-> %s",
                from_domain,
                relationship_type.value,
                to_domain,
            )

            return True

    def get_authorities_over(self, domain: str) -> set[str]:
        """
        Get domains that have authority over the given domain.

        Args:
            domain: Domain to check

        Returns:
            Set of domains with authority
        """
        with self._lock:
            return self._authorities_over.get(domain, set()).copy()

    def get_subordinates(self, domain: str) -> set[str]:
        """
        Get domains subordinate to the given domain.

        Args:
            domain: Domain to check

        Returns:
            Set of subordinate domains
        """
        with self._lock:
            return self._subordinates_to.get(domain, set()).copy()

    def get_veto_powers_over(self, domain: str) -> set[str]:
        """
        Get domains that can veto the given domain.

        Args:
            domain: Domain to check

        Returns:
            Set of domains with veto power
        """
        with self._lock:
            return self._veto_powers.get(domain, set()).copy()

    def must_consult_domains(self, domain: str) -> set[str]:
        """
        Get domains that must be consulted by the given domain.

        Args:
            domain: Domain to check

        Returns:
            Set of domains to consult
        """
        with self._lock:
            return self._must_consult.get(domain, set()).copy()

    def can_override(self, from_domain: str, to_domain: str) -> bool:
        """
        Check if from_domain can override to_domain.

        Args:
            from_domain: Domain attempting override
            to_domain: Domain being overridden

        Returns:
            True if override is authorized
        """
        with self._lock:
            key = (from_domain, to_domain)

            if key not in self._relationships:
                return False

            relationship = self._relationships[key]

            return relationship.relationship_type == RelationshipType.AUTHORITY_OVER

    def requires_consultation(
        self,
        from_domain: str,
        to_domain: str,
        action_context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Check if from_domain must consult to_domain.

        Args:
            from_domain: Domain taking action
            to_domain: Potential consultant domain
            action_context: Optional action context for conditional checks

        Returns:
            True if consultation required
        """
        with self._lock:
            key = (from_domain, to_domain)

            if key not in self._relationships:
                return False

            relationship = self._relationships[key]

            if relationship.relationship_type != RelationshipType.MUST_CONSULT:
                return False

            # Check conditions if provided
            if relationship.conditions and action_context:
                for cond_key, cond_value in relationship.conditions.items():
                    if action_context.get(cond_key) != cond_value:
                        return False

            return True

    def get_authority_chain(self, domain: str, max_depth: int = 10) -> list[str]:
        """
        Get the authority chain above a domain.

        Args:
            domain: Starting domain
            max_depth: Maximum chain depth

        Returns:
            List of domains in authority chain (bottom to top)
        """
        chain = [domain]
        visited = {domain}

        with self._lock:
            current = domain

            for _ in range(max_depth):
                authorities = self._authorities_over.get(current, set())

                if not authorities:
                    break

                # Pick highest authority (could be multiple)
                next_authority = None
                for auth in authorities:
                    if auth not in visited:
                        next_authority = auth
                        break

                if not next_authority:
                    break

                chain.append(next_authority)
                visited.add(next_authority)
                current = next_authority

        return chain

    def get_all_relationships(self) -> list[dict[str, Any]]:
        """Get all relationships in the graph."""
        with self._lock:
            return [rel.to_dict() for rel in self._relationships.values()]

    def get_relationship(
        self, from_domain: str, to_domain: str
    ) -> AuthorityRelationship | None:
        """
        Get a specific relationship.

        Args:
            from_domain: Source domain
            to_domain: Target domain

        Returns:
            AuthorityRelationship or None
        """
        with self._lock:
            key = (from_domain, to_domain)
            return self._relationships.get(key)

    def validate_action(
        self, domain: str, action: str, context: dict[str, Any] | None = None
    ) -> tuple[bool, str | None]:
        """
        Validate if a domain can take an action based on governance.

        Args:
            domain: Domain attempting action
            action: Action to validate
            context: Optional context

        Returns:
            Tuple of (is_valid, reason)
        """
        with self._lock:
            # Check if domain must consult others
            consult_domains = self.must_consult_domains(domain)

            if consult_domains and context and not context.get("consultation_complete"):
                required = ", ".join(consult_domains)
                return False, f"Must consult: {required}"

            # Check if action is within authority
            # (Could be expanded with more specific action validation)

            return True, None

    def get_graph_visualization(self) -> dict[str, Any]:
        """
        Get a visualization-friendly representation of the graph.

        Returns:
            Graph structure for visualization
        """
        with self._lock:
            nodes = set()
            edges = []

            for relationship in self._relationships.values():
                nodes.add(relationship.from_domain)
                nodes.add(relationship.to_domain)

                edges.append(
                    {
                        "from": relationship.from_domain,
                        "to": relationship.to_domain,
                        "type": relationship.relationship_type.value,
                        "description": relationship.description,
                    }
                )

            return {
                "nodes": sorted(nodes),
                "edges": edges,
                "authority_hierarchy": self._build_hierarchy(),
            }

    def _build_hierarchy(self) -> dict[str, list[str]]:
        """Build authority hierarchy."""
        hierarchy = {}

        # Find all domains
        all_domains = set()
        for rel in self._relationships.values():
            all_domains.add(rel.from_domain)
            all_domains.add(rel.to_domain)

        # Build hierarchy for each
        for domain in all_domains:
            hierarchy[domain] = self.get_authority_chain(domain)

        return hierarchy


# Singleton instance
_governance_graph_instance: GovernanceGraph | None = None
_governance_graph_lock = threading.Lock()


def get_governance_graph() -> GovernanceGraph:
    """
    Get the singleton GovernanceGraph instance.

    Returns:
        GovernanceGraph instance
    """
    global _governance_graph_instance

    with _governance_graph_lock:
        if _governance_graph_instance is None:
            _governance_graph_instance = GovernanceGraph()

        return _governance_graph_instance
