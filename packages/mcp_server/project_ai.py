"""
Project-AI MCP Server Implementation

OPTIONAL integration point for MCP-compatible clients (Claude Desktop, Cursor, etc).

Project-AI is LOCAL-FIRST and runs 100% offline. This MCP server is an OPTIONAL
interface layer that allows external clients to query the local API - nothing more.

Core operations:
- Governed execution via the Constitutional Triumvirate (always works locally)
- Immutable audit chain queries (always works locally)
- CCMA memory system integration (always works locally)
- Capability-based access control (always works locally)

MCP is just a convenience wrapper for Claude Desktop / Cursor users.
The system is fully functional without it.
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, cast

import httpx

logger = logging.getLogger(__name__)


@dataclass
class MCPCapability:
    """An MCP capability granted by Project-AI governance."""
    name: str
    resource: str
    scope: str  # "read", "write", "execute"
    granted_by: str  # "galahad", "cerberus", "codex"
    expires_at: str | None = None


class ProjectAIMCPServer:
    """
    MCP Server bridging Claude/Cursor to Project-AI governance and memory.

    Routes MCP requests through the Constitutional Triumvirate:
    - Galahad: verifies legitimacy and agency
    - Cerberus: verifies security and boundary
    - Codex Deus Maximus: applies constitutional policy
    """

    def __init__(self) -> None:
        self.api_url = os.getenv("PROJECT_AI_MCP_API_URL", "http://localhost:8000")
        self.api_token = os.getenv("PROJECT_AI_MCP_TOKEN", "")
        self.governance_mode = os.getenv("PROJECT_AI_MCP_GOVERNANCE_MODE", "strict")
        self.audit_enabled = os.getenv("PROJECT_AI_MCP_AUDIT_ENABLED", "true").lower() == "true"

        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "User-Agent": "Project-AI-MCP/0.1.0",
            },
            timeout=30.0,
        )

    async def handle_verdict(self, verdict: dict[str, Any]) -> dict[str, Any]:
        """
        Submit a governance verdict through the Triumvirate.

        Args:
            verdict: {"matter": str, "proposed_action": str, "evidence": dict, ...}

        Returns:
            {"status": "ALLOW"|"DENY"|"ESCALATE", "reason": str, "audit_id": str}
        """
        logger.info(f"MCP Verdict Request: {verdict.get('matter')}")

        # Route through Constitutional Triumvirate
        response = await self.client.post(
            "/governance/verdict",
            json={
                "source": "mcp_server",
                "verdict": verdict,
                "mode": self.governance_mode,
            },
        )
        response.raise_for_status()
        return cast("dict[str, Any]", response.json())

    async def handle_audit_query(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Query the immutable audit chain with cryptographic verification.

        Args:
            query: {"filter": str, "limit": int, "verify_chain": bool}

        Returns:
            List of audit records with verified cryptographic hashes
        """
        logger.info(f"MCP Audit Query: {query.get('filter')}")

        response = await self.client.post(
            "/audit",
            json=query,
        )
        response.raise_for_status()
        return cast("list[dict[str, Any]]", response.json())

    async def handle_memory(self, operation: dict[str, Any]) -> Any:
        """
        Memory system operations: store, retrieve, query.

        Args:
            operation: {
                "op": "store"|"retrieve"|"query",
                "category": str,
                "content": str|dict,
                "tags": list[str]
            }
        """
        logger.info(f"MCP Memory Operation: {operation.get('op')}")

        op_type = operation.get("op", "query")

        if op_type == "store":
            response = await self.client.post(
                "/memory/store",
                json=operation,
            )
        elif op_type == "retrieve":
            response = await self.client.get(
                f"/memory/{operation.get('id')}"
            )
        else:  # query
            response = await self.client.post(
                "/memory/query",
                json=operation,
            )

        response.raise_for_status()
        return response.json()

    async def handle_capabilities(self) -> list[MCPCapability]:
        """
        List capabilities currently granted to the MCP client.
        """
        logger.info("MCP Capabilities Query")

        response = await self.client.get("/capabilities")
        response.raise_for_status()

        caps = response.json()
        return [MCPCapability(**cap) for cap in caps]

    async def handle_constitution(self) -> dict[str, Any]:
        """
        Return the constitutional framework and policies.
        """
        logger.info("MCP Constitution Query")

        response = await self.client.get("/governance/constitution")
        response.raise_for_status()
        return cast("dict[str, Any]", response.json())

    async def handle_governance_state(self) -> dict[str, Any]:
        """
        Return current governance state and policy.
        """
        logger.info("MCP Governance State Query")

        response = await self.client.get("/governance/state")
        response.raise_for_status()
        return cast("dict[str, Any]", response.json())


# MCP Tool Definitions (for integration with Claude Desktop)
MCP_TOOLS = {
    "project-ai/verdict": {
        "description": "Submit an action for constitutional governance review",
        "inputSchema": {
            "type": "object",
            "properties": {
                "matter": {"type": "string", "description": "What is being decided"},
                "proposed_action": {"type": "string", "description": "The action proposed"},
                "evidence": {"type": "object", "description": "Supporting evidence"},
                "authority_required": {"type": "string", "enum": ["human", "ai", "dual"]}
            },
            "required": ["matter", "proposed_action"]
        }
    },
    "project-ai/audit": {
        "description": "Query the cryptographically-verified audit log",
        "inputSchema": {
            "type": "object",
            "properties": {
                "filter": {"type": "string", "description": "Search filter (e.g., 'verdict_id=12345')"},
                "limit": {"type": "integer", "description": "Max results", "default": 100},
                "verify_chain": {"type": "boolean", "description": "Cryptographically verify hashes"}
            }
        }
    },
    "project-ai/memory": {
        "description": "Access the CCMA memory system",
        "inputSchema": {
            "type": "object",
            "properties": {
                "op": {"type": "string", "enum": ["store", "retrieve", "query"]},
                "category": {"type": "string", "description": "Memory category"},
                "content": {"description": "Content to store or query"}
            },
            "required": ["op"]
        }
    },
    "project-ai/capabilities": {
        "description": "List capabilities granted by governance",
        "inputSchema": {"type": "object"}
    }
}
