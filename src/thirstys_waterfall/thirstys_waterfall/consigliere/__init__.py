"""
Thirsty Consigliere - Privacy-First In-Browser Assistant
Code of Omertà: Privacy as a first-class contract, not a vibe.
"""

from .consigliere_engine import ThirstyConsigliere
from .capability_manager import CapabilityManager
from .action_ledger import ActionLedger
from .privacy_checker import PrivacyChecker

__all__ = ["ThirstyConsigliere", "CapabilityManager", "ActionLedger", "PrivacyChecker"]
