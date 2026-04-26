"""
Multi-path runtime routing layer.

This module provides the coordination layer that ensures ALL execution paths
(web, desktop, CLI, agents) flow through the same governance pipeline.

Architecture:
    ANY ENTRY → Interface Adapter → Runtime Router → Governance Pipeline → AI Orchestrator → Systems
"""

from .router import route_request

__all__ = ["route_request"]
