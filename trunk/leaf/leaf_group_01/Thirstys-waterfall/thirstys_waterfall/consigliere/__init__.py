# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Thirsty Consigliere - Privacy-First In-Browser Assistant
Code of Omertà: Privacy as a first-class contract, not a vibe.
"""

from .consigliere_engine import ThirstyConsigliere
from .capability_manager import CapabilityManager
from .action_ledger import ActionLedger
from .privacy_checker import PrivacyChecker

__all__ = ["ThirstyConsigliere", "CapabilityManager", "ActionLedger", "PrivacyChecker"]
