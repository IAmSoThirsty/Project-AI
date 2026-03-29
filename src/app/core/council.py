# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / council.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / council.py

import logging
logger = logging.getLogger(__name__)


               #
# COMPLIANCE: Sovereign Substrate / Council Runtime Contract



"""
Council Runtime Contract
========================

This module defines the authoritative runtime contract for all agent modules
within the Project-AI sovereign substrate. All agents must conform to the 
CouncilMemberInterface to ensure consistent governance, auditability, 
and reflexive containment.

Defined by the Triumvirate.
"""
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any

class CouncilRole(Enum):
    """Roles within the sovereign council."""
    PLANNER = auto()
    EXECUTOR = auto()
    REVIEWER = auto()
    AUDITOR = auto()
    COMMUNICATOR = auto()
    GOVERNOR = auto()
    PERIMETER_GUARD = auto()

class CouncilMemberInterface(ABC):
    """
    Authoritative interface for all Council Members (Agents).
    """

    @abstractmethod
    def get_role(self) -> CouncilRole:
        """Return the assigned CouncilRole of the member."""
        pass

    @abstractmethod
    def execute_action(self, action_name: str, params: dict[str, Any]) -> Any:
        """
        Execute a specific action bound by the Council's governance.
        
        All implementations MUST route through the CognitionKernel for 
        audit and policy enforcement.
        """
        ...

    @abstractmethod
    def receive_message(self, from_id: str, message: str) -> None:
        """Handle incoming communication from other council members."""
        ...

    @abstractmethod
    def get_status(self) -> str:
        """Return current operational status (Active, Idle, Degraded, etc.)."""
        ...

class CouncilInterface(ABC):
    """
    Interface for the Council Orchestrator (CouncilHub).
    """

    @abstractmethod
    def register_member(self, member: CouncilMemberInterface) -> None:
        """Register a new member into the council."""
        ...

    @abstractmethod
    def route_transmission(self, from_id: str, to_id: str, transmission: str) -> bool:
        """Route a sovereign transmission between members."""
        ...

    @abstractmethod
    def enforce_quorum(self, proposal: Any) -> bool:
        """Verify Triumvirate quorum for a given proposal."""
        ...
