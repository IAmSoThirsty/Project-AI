"""
Supply Store and Tool Management System
Implements Codex Section 5 (Tools, Supply Store & Permissions)
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set

from app.miniature_office.core.audit import EventType, get_audit_log
from app.miniature_office.core.entity import Entity, EntityType, RelationType, get_registry


class ToolTag(Enum):
    """Tool categories"""

    COMPILER = "compiler"
    LINTER = "linter"
    TEST_FRAMEWORK = "test_framework"
    BUILD_SYSTEM = "build_system"
    MCP_SERVER = "mcp_server"
    SDK = "sdk"
    LIBRARY = "library"
    SECURITY_SCANNER = "security_scanner"


@dataclass
class ToolMetadata:
    """
    Tool metadata (Codex 5.2).
    Every tool has: Tag, Version, Trust score, Security rating
    """

    tag: ToolTag
    version: str
    trust_score: float = 0.5  # 0.0 - 1.0
    security_rating: int = 3  # 1-5, where 5 is most secure
    capabilities: Set[str] = field(default_factory=set)
    requires_justification: bool = False

    def to_dict(self) -> Dict:
        return {
            "tag": self.tag.value,
            "version": self.version,
            "trust_score": self.trust_score,
            "security_rating": self.security_rating,
            "capabilities": list(self.capabilities),
            "requires_justification": self.requires_justification,
        }


class Tool(Entity):
    """
    Tool entity for the supply store (Codex 1.1, 5.1)
    """

    def __init__(self, tool_id: str, name: str, metadata: ToolMetadata):
        super().__init__(tool_id, EntityType.TOOL, name)
        self.metadata_info = metadata
        self.checked_out_by: Optional[str] = None  # Agent ID
        self.checkout_history: List[Dict] = []
        self.is_available = True

        # Register tool
        get_registry().register(self)

        # Log creation
        get_audit_log().log_event(
            EventType.ENTITY_CREATED,
            target_id=self.entity_id,
            data={"entity_type": "tool", "tool_metadata": metadata.to_dict()},
        )

    def to_dict(self) -> Dict:
        base = super().to_dict()
        base.update(
            {
                "tool_metadata": self.metadata_info.to_dict(),
                "checked_out_by": self.checked_out_by,
                "is_available": self.is_available,
            }
        )
        return base


@dataclass
class CheckoutRecord:
    """Record of a tool checkout"""

    checkout_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tool_id: str = ""
    agent_id: str = ""
    justification: str = ""
    checked_out_at: datetime = field(default_factory=datetime.utcnow)
    checked_in_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        return {
            "checkout_id": self.checkout_id,
            "tool_id": self.tool_id,
            "agent_id": self.agent_id,
            "justification": self.justification,
            "checked_out_at": self.checked_out_at.isoformat(),
            "checked_in_at": self.checked_in_at.isoformat() if self.checked_in_at else None,
        }


class SupplyStore:
    """
    Supply Store for tool inventory management (Codex 5.2).
    Agents must explicitly check out tools from supply store.
    """

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.checkouts: Dict[str, CheckoutRecord] = {}

    def add_tool(self, tool: Tool):
        """Add a tool to the supply store inventory"""
        self.tools[tool.entity_id] = tool

        get_audit_log().log_event(
            EventType.ENTITY_CREATED,
            target_id=tool.entity_id,
            data={"action": "tool_added_to_supply_store", "tool_name": tool.name},
        )

    def check_out_tool(self, tool_id: str, agent_id: str, justification: str = "") -> Optional[CheckoutRecord]:
        """
        Check out a tool (Codex 5.2).
        Agents must explicitly check out tools from supply store.
        MCP Sessions require capability justification by agent (Codex 5.1)
        """
        tool = self.tools.get(tool_id)
        if not tool:
            return None

        if not tool.is_available:
            return None

        # Check if justification required
        if tool.metadata_info.requires_justification and not justification:
            return None

        # Check agent capabilities match tool requirements
        agent = get_registry().get(agent_id)
        if not agent:
            return None

        # Create checkout record
        checkout = CheckoutRecord(tool_id=tool_id, agent_id=agent_id, justification=justification)

        self.checkouts[checkout.checkout_id] = checkout
        tool.checked_out_by = agent_id
        tool.is_available = False
        tool.checkout_history.append(checkout.to_dict())

        # Declare relationship
        agent.declare_relationship(tool, RelationType.USES)

        # Log checkout
        get_audit_log().log_event(
            EventType.TOOL_CHECKED_OUT,
            actor_id=agent_id,
            target_id=tool_id,
            data={"checkout_id": checkout.checkout_id, "justification": justification},
        )

        return checkout

    def check_in_tool(self, checkout_id: str) -> bool:
        """Check in a tool, making it available again"""
        checkout = self.checkouts.get(checkout_id)
        if not checkout or checkout.checked_in_at:
            return False

        tool = self.tools.get(checkout.tool_id)
        if not tool:
            return False

        checkout.checked_in_at = datetime.utcnow()
        tool.checked_out_by = None
        tool.is_available = True

        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            actor_id=checkout.agent_id,
            target_id=tool.entity_id,
            data={"action": "tool_checked_in", "checkout_id": checkout_id},
        )

        return True

    def get_available_tools(self) -> List[Tool]:
        """Get all available tools"""
        return [t for t in self.tools.values() if t.is_available]

    def get_tools_by_tag(self, tag: ToolTag) -> List[Tool]:
        """Get all tools with a specific tag"""
        return [t for t in self.tools.values() if t.metadata_info.tag == tag]

    def get_tools_by_capability(self, capability: str) -> List[Tool]:
        """Get all tools that provide a specific capability"""
        return [t for t in self.tools.values() if capability in t.metadata_info.capabilities]

    def get_agent_checkouts(self, agent_id: str) -> List[CheckoutRecord]:
        """Get all active checkouts for an agent"""
        return [c for c in self.checkouts.values() if c.agent_id == agent_id and not c.checked_in_at]


# Global supply store
_supply_store = SupplyStore()


def get_supply_store() -> SupplyStore:
    """Get the global supply store"""
    return _supply_store
