"""Project-AI companion public interface."""

from companion.bonded import (
    BOND_IDENTITY_OPERATION,
    PRUNE_FATES_OPERATION,
    RECORD_FATE_OPERATION,
    BondedCompanion,
)
from companion.fates import FateLedger, FateLedgerError, FateRecord
from companion.identity import (
    ALLOWED_PHASES,
    PHASE_BONDED,
    PHASE_UNBONDED,
    IdentityDerivation,
    IdentityError,
    IdentityManager,
)
from companion.service import RESTORE_OPERATION, UPDATE_OPERATION, Companion

__version__ = "0.0.0.dev0"

__all__ = [
    "ALLOWED_PHASES",
    "BOND_IDENTITY_OPERATION",
    "PHASE_BONDED",
    "PHASE_UNBONDED",
    "PRUNE_FATES_OPERATION",
    "RECORD_FATE_OPERATION",
    "RESTORE_OPERATION",
    "UPDATE_OPERATION",
    "BondedCompanion",
    "Companion",
    "FateLedger",
    "FateLedgerError",
    "FateRecord",
    "IdentityDerivation",
    "IdentityError",
    "IdentityManager",
]
