"""
Project-AI MCP Server

Exposes Project-AI governance, memory, audit, and capabilities to Claude Desktop,
Cursor, and other MCP-compatible clients.

Standards: OpenAI MCP v1.0, Constitutional Governance v2.0
"""

__version__ = "0.1.0"
__author__ = "Project-AI Core Team"

from .project_ai import ProjectAIMCPServer

__all__ = ["ProjectAIMCPServer"]
