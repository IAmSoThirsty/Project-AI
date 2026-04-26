"""Graph Analysis Plugin for Project-AI Knowledge Navigation.

This plugin provides comprehensive graph visualization and analysis of the Project-AI
codebase, documentation, and knowledge domains with optimized filters and presets.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.core.ai_systems import FourLaws, Plugin

logger = logging.getLogger(__name__)

try:
    from app.core.observability import emit_event
except ImportError:

    def emit_event(event_name: str, metadata: dict[str, Any] | None = None) -> None:
        logger.debug("Observability stub for %s: %s", event_name, metadata)


class NodeType(Enum):
    """Types of nodes in the knowledge graph."""

    CONSTITUTIONAL = "constitutional"  # Four Laws, validators, constitutional model
    SECURITY = "security"  # Cerberus, security engines, honeypots
    AGENT = "agent"  # AI agents (oversight, planner, validator, explainability)
    AI_SYSTEM = "ai_system"  # Core AI systems (persona, memory, learning)
    KNOWLEDGE = "knowledge"  # Knowledge bases, documentation
    MODULE = "module"  # Code modules and components
    DATA = "data"  # Data persistence, storage


class LinkType(Enum):
    """Types of relationships between nodes."""

    VALIDATES = "validates"  # Constitutional validation
    ENFORCES = "enforces"  # Security enforcement
    USES = "uses"  # Component usage
    DEPENDS_ON = "depends_on"  # Dependency
    EXTENDS = "extends"  # Inheritance/extension
    REFERENCES = "references"  # Documentation/code reference
    STORES = "stores"  # Data storage
    TRIGGERS = "triggers"  # Event triggering


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph."""

    id: str
    name: str
    node_type: NodeType
    description: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    folder_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type.value,
            "description": self.description,
            "tags": self.tags,
            "metadata": self.metadata,
            "folder": self.folder_path,
        }


@dataclass
class GraphLink:
    """Represents a link between nodes."""

    source: str
    target: str
    link_type: LinkType
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.link_type.value,
            "weight": self.weight,
            "metadata": self.metadata,
        }


class GraphFilter:
    """Filter nodes and links based on criteria."""

    def __init__(
        self,
        node_types: list[NodeType] | None = None,
        tags: list[str] | None = None,
        folders: list[str] | None = None,
        link_types: list[LinkType] | None = None,
    ):
        """Initialize filter."""
        self.node_types = node_types or []
        self.tags = tags or []
        self.folders = folders or []
        self.link_types = link_types or []

    def filter_nodes(self, nodes: list[GraphNode]) -> list[GraphNode]:
        """Filter nodes based on criteria."""
        filtered = nodes

        if self.node_types:
            filtered = [n for n in filtered if n.node_type in self.node_types]

        if self.tags:
            filtered = [n for n in filtered if any(tag in n.tags for tag in self.tags)]

        if self.folders:
            filtered = [
                n
                for n in filtered
                if any(n.folder_path.startswith(folder) for folder in self.folders)
            ]

        return filtered

    def filter_links(
        self, links: list[GraphLink], valid_node_ids: set[str]
    ) -> list[GraphLink]:
        """Filter links based on criteria and valid nodes."""
        filtered = links

        if self.link_types:
            filtered = [lnk for lnk in filtered if lnk.link_type in self.link_types]

        # Only keep links where both source and target are in valid nodes
        filtered = [
            lnk
            for lnk in filtered
            if lnk.source in valid_node_ids and lnk.target in valid_node_ids
        ]

        return filtered


class GraphPreset:
    """Predefined graph view configurations."""

    CONSTITUTIONAL_AI = GraphFilter(
        node_types=[NodeType.CONSTITUTIONAL, NodeType.AGENT, NodeType.AI_SYSTEM],
        tags=["four_laws", "validation", "ethics", "constitutional"],
    )

    SECURITY_VIEW = GraphFilter(
        node_types=[NodeType.SECURITY, NodeType.CONSTITUTIONAL],
        tags=["security", "cerberus", "honeypot", "encryption", "auth"],
        folders=["src/app/security", "src/app/core/security"],
    )

    AGENT_SYSTEMS = GraphFilter(
        node_types=[NodeType.AGENT, NodeType.AI_SYSTEM],
        tags=["agent", "oversight", "planner", "validator", "explainability"],
        folders=["src/app/agents", "src/app/core"],
    )

    AI_CORE = GraphFilter(
        node_types=[NodeType.AI_SYSTEM, NodeType.KNOWLEDGE],
        tags=["persona", "memory", "learning", "intelligence"],
    )

    DATA_FLOW = GraphFilter(
        link_types=[LinkType.STORES, LinkType.USES],
        node_types=[NodeType.DATA, NodeType.AI_SYSTEM, NodeType.MODULE],
    )

    FULL_SYSTEM = GraphFilter()  # No filters - show everything


class GraphAnalysisEngine:
    """Core engine for graph analysis and visualization."""

    def __init__(self, data_dir: str = "data"):
        """Initialize graph analysis engine."""
        self.data_dir = data_dir
        self.graph_dir = os.path.join(data_dir, "graph_analysis")
        os.makedirs(self.graph_dir, exist_ok=True)

        self.nodes: dict[str, GraphNode] = {}
        self.links: list[GraphLink] = []
        self.presets: dict[str, GraphFilter] = {
            "constitutional": GraphPreset.CONSTITUTIONAL_AI,
            "security": GraphPreset.SECURITY_VIEW,
            "agents": GraphPreset.AGENT_SYSTEMS,
            "ai_core": GraphPreset.AI_CORE,
            "data_flow": GraphPreset.DATA_FLOW,
            "full": GraphPreset.FULL_SYSTEM,
        }

        self._initialize_graph()

    def _initialize_graph(self) -> None:
        """Initialize the knowledge graph with Project-AI structure."""
        # Constitutional AI nodes
        self.add_node(
            GraphNode(
                id="four_laws",
                name="Four Laws Framework",
                node_type=NodeType.CONSTITUTIONAL,
                description="Immutable ethics framework (Asimov's Laws)",
                tags=["four_laws", "ethics", "constitutional", "validation"],
                folder_path="src/app/core",
                metadata={"class": "FourLaws", "file": "ai_systems.py"},
            )
        )

        self.add_node(
            GraphNode(
                id="oversight_agent",
                name="Oversight Agent",
                node_type=NodeType.AGENT,
                description="Action safety validation agent",
                tags=["agent", "oversight", "validation", "safety"],
                folder_path="src/app/agents",
                metadata={"file": "oversight.py"},
            )
        )

        self.add_node(
            GraphNode(
                id="planner_agent",
                name="Planner Agent",
                node_type=NodeType.AGENT,
                description="Task decomposition and planning",
                tags=["agent", "planner", "task", "planning"],
                folder_path="src/app/agents",
                metadata={"file": "planner.py"},
            )
        )

        self.add_node(
            GraphNode(
                id="validator_agent",
                name="Validator Agent",
                node_type=NodeType.AGENT,
                description="Input/output validation",
                tags=["agent", "validator", "validation", "io"],
                folder_path="src/app/agents",
                metadata={"file": "validator.py"},
            )
        )

        self.add_node(
            GraphNode(
                id="explainability_agent",
                name="Explainability Agent",
                node_type=NodeType.AGENT,
                description="Decision explanation generation",
                tags=["agent", "explainability", "transparency", "explanation"],
                folder_path="src/app/agents",
                metadata={"file": "explainability.py"},
            )
        )

        # AI System nodes
        self.add_node(
            GraphNode(
                id="ai_persona",
                name="AI Persona System",
                node_type=NodeType.AI_SYSTEM,
                description="Self-aware AI with personality and mood tracking",
                tags=["persona", "personality", "mood", "ai_system"],
                folder_path="src/app/core",
                metadata={"class": "AIPersona", "file": "ai_systems.py"},
            )
        )

        self.add_node(
            GraphNode(
                id="memory_expansion",
                name="Memory Expansion System",
                node_type=NodeType.AI_SYSTEM,
                description="Conversation logging and knowledge base",
                tags=["memory", "knowledge", "conversation", "ai_system"],
                folder_path="src/app/core",
                metadata={"class": "MemoryExpansionSystem", "file": "ai_systems.py"},
            )
        )

        self.add_node(
            GraphNode(
                id="learning_system",
                name="Learning Request Manager",
                node_type=NodeType.AI_SYSTEM,
                description="Human-in-the-loop learning with Black Vault",
                tags=["learning", "approval", "black_vault", "ai_system"],
                folder_path="src/app/core",
                metadata={"class": "LearningRequestManager", "file": "ai_systems.py"},
            )
        )

        self.add_node(
            GraphNode(
                id="command_override",
                name="Command Override System",
                node_type=NodeType.AI_SYSTEM,
                description="Master password override with audit logging",
                tags=["override", "security", "audit", "ai_system"],
                folder_path="src/app/core",
                metadata={"class": "CommandOverrideSystem", "file": "ai_systems.py"},
            )
        )

        # Security nodes
        self.add_node(
            GraphNode(
                id="cerberus",
                name="Cerberus Security Engine",
                node_type=NodeType.SECURITY,
                description="Multi-headed security orchestration engine",
                tags=["security", "cerberus", "orchestration", "monitoring"],
                folder_path="src/app/security",
                metadata={"integration": "cerberus"},
            )
        )

        self.add_node(
            GraphNode(
                id="user_manager",
                name="User Manager",
                node_type=NodeType.SECURITY,
                description="User authentication with bcrypt hashing",
                tags=["security", "auth", "bcrypt", "user"],
                folder_path="src/app/core",
                metadata={"class": "UserManager", "file": "user_manager.py"},
            )
        )

        self.add_node(
            GraphNode(
                id="honeypot_detector",
                name="Honeypot Detector",
                node_type=NodeType.SECURITY,
                description="Detects and responds to honeypot triggers",
                tags=["security", "honeypot", "detection", "defense"],
                folder_path="src/app/core",
                metadata={"file": "honeypot_detector.py"},
            )
        )

        # Module nodes
        self.add_node(
            GraphNode(
                id="intelligence_engine",
                name="Intelligence Engine",
                node_type=NodeType.MODULE,
                description="OpenAI chat integration",
                tags=["openai", "chat", "intelligence", "llm"],
                folder_path="src/app/core",
                metadata={"file": "intelligence_engine.py"},
            )
        )

        self.add_node(
            GraphNode(
                id="image_generator",
                name="Image Generator",
                node_type=NodeType.MODULE,
                description="Image generation (HF Stable Diffusion, OpenAI DALL-E)",
                tags=["image", "generation", "dalle", "stable_diffusion"],
                folder_path="src/app/core",
                metadata={"file": "image_generator.py"},
            )
        )

        # Data nodes
        self.add_node(
            GraphNode(
                id="persona_data",
                name="Persona State Storage",
                node_type=NodeType.DATA,
                description="AI personality and mood persistence",
                tags=["data", "persistence", "persona", "json"],
                folder_path="data/ai_persona",
                metadata={"file": "state.json"},
            )
        )

        self.add_node(
            GraphNode(
                id="memory_data",
                name="Memory Knowledge Base",
                node_type=NodeType.DATA,
                description="Categorized knowledge storage",
                tags=["data", "persistence", "memory", "knowledge", "json"],
                folder_path="data/memory",
                metadata={"file": "knowledge.json"},
            )
        )

        self.add_node(
            GraphNode(
                id="learning_data",
                name="Learning Requests Storage",
                node_type=NodeType.DATA,
                description="Learning request tracking and Black Vault",
                tags=["data", "persistence", "learning", "black_vault", "json"],
                folder_path="data/learning_requests",
                metadata={"file": "requests.json"},
            )
        )

        self.add_node(
            GraphNode(
                id="user_data",
                name="User Database",
                node_type=NodeType.DATA,
                description="User profiles with bcrypt password hashes",
                tags=["data", "persistence", "users", "auth", "json"],
                folder_path="data",
                metadata={"file": "users.json"},
            )
        )

        # Add links
        self._add_relationships()

    def _add_relationships(self) -> None:
        """Define relationships between nodes."""
        # Constitutional validation relationships
        self.add_link(
            GraphLink(
                "four_laws",
                "oversight_agent",
                LinkType.VALIDATES,
                weight=2.0,
                metadata={"description": "Four Laws validate agent actions"},
            )
        )

        self.add_link(
            GraphLink(
                "oversight_agent",
                "planner_agent",
                LinkType.VALIDATES,
                weight=1.5,
                metadata={"description": "Oversight validates planned tasks"},
            )
        )

        self.add_link(
            GraphLink(
                "validator_agent",
                "intelligence_engine",
                LinkType.VALIDATES,
                weight=1.5,
                metadata={"description": "Validator checks intelligence engine I/O"},
            )
        )

        # AI System dependencies
        self.add_link(
            GraphLink(
                "ai_persona",
                "memory_expansion",
                LinkType.USES,
                weight=1.8,
                metadata={"description": "Persona uses memory for context"},
            )
        )

        self.add_link(
            GraphLink(
                "ai_persona",
                "learning_system",
                LinkType.USES,
                weight=1.5,
                metadata={"description": "Persona requests learning approvals"},
            )
        )

        self.add_link(
            GraphLink(
                "learning_system",
                "four_laws",
                LinkType.DEPENDS_ON,
                weight=2.0,
                metadata={"description": "Learning validates against Four Laws"},
            )
        )

        # Security enforcement
        self.add_link(
            GraphLink(
                "cerberus",
                "user_manager",
                LinkType.ENFORCES,
                weight=2.0,
                metadata={"description": "Cerberus enforces auth policies"},
            )
        )

        self.add_link(
            GraphLink(
                "command_override",
                "four_laws",
                LinkType.DEPENDS_ON,
                weight=2.5,
                metadata={"description": "Overrides can bypass Four Laws"},
            )
        )

        self.add_link(
            GraphLink(
                "honeypot_detector",
                "cerberus",
                LinkType.TRIGGERS,
                weight=1.8,
                metadata={"description": "Honeypot triggers Cerberus alerts"},
            )
        )

        # Data storage relationships
        self.add_link(
            GraphLink(
                "ai_persona",
                "persona_data",
                LinkType.STORES,
                weight=2.0,
                metadata={"description": "Persona persists to JSON"},
            )
        )

        self.add_link(
            GraphLink(
                "memory_expansion",
                "memory_data",
                LinkType.STORES,
                weight=2.0,
                metadata={"description": "Memory stores knowledge base"},
            )
        )

        self.add_link(
            GraphLink(
                "learning_system",
                "learning_data",
                LinkType.STORES,
                weight=2.0,
                metadata={"description": "Learning stores requests and Black Vault"},
            )
        )

        self.add_link(
            GraphLink(
                "user_manager",
                "user_data",
                LinkType.STORES,
                weight=2.0,
                metadata={"description": "User manager persists user profiles"},
            )
        )

        # Module usage
        self.add_link(
            GraphLink(
                "ai_persona",
                "intelligence_engine",
                LinkType.USES,
                weight=1.5,
                metadata={"description": "Persona uses intelligence for responses"},
            )
        )

        self.add_link(
            GraphLink(
                "explainability_agent",
                "intelligence_engine",
                LinkType.USES,
                weight=1.3,
                metadata={"description": "Explainability uses LLM for explanations"},
            )
        )

    def add_node(self, node: GraphNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node
        logger.debug("Added node: %s (%s)", node.name, node.node_type.value)

    def add_link(self, link: GraphLink) -> None:
        """Add a link to the graph."""
        self.links.append(link)
        logger.debug(
            "Added link: %s -> %s (%s)", link.source, link.target, link.link_type.value
        )

    def apply_filter(self, filter_obj: GraphFilter) -> dict[str, Any]:
        """Apply filter and return filtered graph."""
        filtered_nodes = filter_obj.filter_nodes(list(self.nodes.values()))
        valid_node_ids = {n.id for n in filtered_nodes}
        filtered_links = filter_obj.filter_links(self.links, valid_node_ids)

        return {
            "nodes": [n.to_dict() for n in filtered_nodes],
            "links": [lnk.to_dict() for lnk in filtered_links],
            "stats": {
                "node_count": len(filtered_nodes),
                "link_count": len(filtered_links),
                "node_types": list({n.node_type.value for n in filtered_nodes}),
            },
        }

    def get_preset(self, preset_name: str) -> dict[str, Any]:
        """Get a predefined graph view."""
        if preset_name not in self.presets:
            raise ValueError(f"Unknown preset: {preset_name}")

        return self.apply_filter(self.presets[preset_name])

    def export_graph(self, filepath: str, filter_obj: GraphFilter | None = None) -> None:
        """Export graph to JSON file."""
        if filter_obj is None:
            filter_obj = GraphPreset.FULL_SYSTEM

        graph_data = self.apply_filter(filter_obj)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2)

        logger.info("Exported graph to %s", filepath)

    def get_statistics(self) -> dict[str, Any]:
        """Get graph statistics."""
        node_type_counts = {}
        for node in self.nodes.values():
            node_type_counts[node.node_type.value] = (
                node_type_counts.get(node.node_type.value, 0) + 1
            )

        link_type_counts = {}
        for link in self.links:
            link_type_counts[link.link_type.value] = (
                link_type_counts.get(link.link_type.value, 0) + 1
            )

        return {
            "total_nodes": len(self.nodes),
            "total_links": len(self.links),
            "node_types": node_type_counts,
            "link_types": link_type_counts,
            "presets": list(self.presets.keys()),
        }


class GraphAnalysisPlugin(Plugin):
    """Graph Analysis Plugin for Project-AI knowledge navigation."""

    def __init__(self, data_dir: str = "data"):
        """Initialize plugin."""
        super().__init__(name="graph_analysis_plugin", version="1.0.0")
        self.data_dir = data_dir
        self.engine: GraphAnalysisEngine | None = None

    def initialize(self, context: dict[str, Any] | None = None) -> bool:
        """Initialize plugin with Four Laws validation."""
        context = context or {}

        # Validate against Four Laws
        allowed, reason = FourLaws.validate_action(
            "Initialize Graph Analysis Plugin", context
        )

        if not allowed:
            logger.warning("Graph Analysis Plugin blocked: %s", reason)
            emit_event("plugin.graph_analysis.blocked", {"reason": reason})
            return False

        # Initialize graph engine
        try:
            self.engine = GraphAnalysisEngine(data_dir=self.data_dir)
            self.enabled = True

            emit_event(
                "plugin.graph_analysis.initialized",
                {
                    "name": self.name,
                    "version": self.version,
                    "stats": self.engine.get_statistics(),
                },
            )

            logger.info("Graph Analysis Plugin initialized successfully")
            return True

        except Exception as e:
            logger.exception("Failed to initialize Graph Analysis Plugin: %s", e)
            emit_event("plugin.graph_analysis.init_failed", {"error": str(e)})
            return False

    def get_graph(
        self, preset: str | None = None, custom_filter: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Get graph data with optional preset or custom filter."""
        if not self.enabled or self.engine is None:
            raise RuntimeError("Plugin not initialized")

        if preset:
            return self.engine.get_preset(preset)

        if custom_filter:
            filter_obj = GraphFilter(
                node_types=[
                    NodeType(nt) for nt in custom_filter.get("node_types", [])
                ],
                tags=custom_filter.get("tags", []),
                folders=custom_filter.get("folders", []),
                link_types=[
                    LinkType(lt) for lt in custom_filter.get("link_types", [])
                ],
            )
            return self.engine.apply_filter(filter_obj)

        return self.engine.apply_filter(GraphPreset.FULL_SYSTEM)

    def get_statistics(self) -> dict[str, Any]:
        """Get graph statistics."""
        if not self.enabled or self.engine is None:
            raise RuntimeError("Plugin not initialized")

        return self.engine.get_statistics()

    def export(
        self, filepath: str, preset: str | None = None
    ) -> None:
        """Export graph to file."""
        if not self.enabled or self.engine is None:
            raise RuntimeError("Plugin not initialized")

        filter_obj = self.engine.presets.get(preset) if preset else None
        self.engine.export_graph(filepath, filter_obj)


def initialize(context: dict[str, Any] | None = None) -> bool:
    """Entry point for plugin loaders."""
    return GraphAnalysisPlugin().initialize(context)


__all__ = ["GraphAnalysisPlugin", "GraphAnalysisEngine", "initialize"]
