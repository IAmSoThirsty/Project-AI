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
from companion.nirl import (
    ALLOWED_STATES,
    DEFAULT_STATE,
    NIRL_STATE_KEY,
    NIRLController,
    NIRLTransition,
    NIRLTransitionError,
    default_nirl_transition,
)
from companion.service import RESTORE_OPERATION, UPDATE_OPERATION, Companion

__version__ = "0.0.0.dev0"

__all__ = [
    "ALLOWED_PHASES",
    "ALLOWED_STATES",
    "BOND_IDENTITY_OPERATION",
    "DEFAULT_STATE",
    "NIRL_STATE_KEY",
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
    "NIRLController",
    "NIRLTransition",
    "NIRLTransitionError",
    "default_nirl_transition",
]
