"""Miniature Office — Cognitive IDE & Repair Crew for Project-AI.

Native integration of the Civilization-Tier Cognitive IDE.
Exposes four public facades:
  - CognitiveIDE: Full spatial code environment (VR, floors, simulation)
  - RepairCrew:   Self-healing agents for Project-AI diagnostics & repair
  - AgentLounge:  Off-duty social space for agent brainstorming & proposals
  - MetaSecurityDepartment: Tier-1 enforcement protecting the system
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Lazy imports to avoid import-time side-effects when disabled
_CognitiveIDE = None
_RepairCrew = None
_AgentLounge = None
_MetaSecurityDepartment = None


def get_cognitive_ide():
    """Return the CognitiveIDE singleton (lazy import)."""
    global _CognitiveIDE
    if _CognitiveIDE is None:
        from app.miniature_office.cognitive_ide import CognitiveIDE

        _CognitiveIDE = CognitiveIDE
    return _CognitiveIDE


def get_repair_crew():
    """Return the RepairCrew class (lazy import)."""
    global _RepairCrew
    if _RepairCrew is None:
        from app.miniature_office.repair_crew import RepairCrew

        _RepairCrew = RepairCrew
    return _RepairCrew


def get_agent_lounge():
    """Return the AgentLounge class (lazy import)."""
    global _AgentLounge
    if _AgentLounge is None:
        from app.miniature_office.agent_lounge import AgentLounge

        _AgentLounge = AgentLounge
    return _AgentLounge


def get_meta_security():
    """Return the MetaSecurityDepartment class (lazy import)."""
    global _MetaSecurityDepartment
    if _MetaSecurityDepartment is None:
        from app.miniature_office.meta_security_dept import MetaSecurityDepartment

        _MetaSecurityDepartment = MetaSecurityDepartment
    return _MetaSecurityDepartment


__all__ = [
    "get_cognitive_ide",
    "get_repair_crew",
    "get_agent_lounge",
    "get_meta_security",
]
