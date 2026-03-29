# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / governance.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / governance.py

"""
Governance Module - Unified System Access Point
Project-AI Sovereign Core

This module provides the canonical access point for the Project-AI governance
subsystem. It bridges the Tier-1 GovernanceService with external components
requesting Triumvirate-based authority evaluation.
"""

# Internal Imports
from src.app.core.services.governance_service import GovernanceService

# ────────────────────────────────────────────────────────────────────────────


# Alias for compatibility with components expecting "Triumvirate"
Triumvirate = GovernanceService


# Placeholder for GovernanceContext if needed in future deep integrations
class GovernanceContext(dict):
    """
    Governance Context - Data container for action evaluation.
    Extends dict for flexibility with formal typing in future iterations.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


__all__ = ["GovernanceService", "Triumvirate", "GovernanceContext"]
