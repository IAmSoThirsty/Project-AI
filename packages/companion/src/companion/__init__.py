"""Project-AI companion public interface."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from companion.bonded import (
    BOND_IDENTITY_OPERATION,
    PRUNE_FATES_OPERATION,
    RECORD_FATE_OPERATION,
    BondedCompanion,
)
from companion.cognition import (
    ALLOWED_THOUGHT_TYPES,
    COGNITION_STATE_KEY,
    COGNITION_THOUGHTS_KEY,
    CognitionController,
    CognitionError,
    CognitionStrategy,
    Thought,
    default_cognition_strategy,
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
from companion.voice_bonding import (
    ALLOWED_EXPRESSIONS,
    BONDING_PHASES,
    DEFAULT_PHASE,
    VOICE_BONDING_HISTORY_KEY,
    VOICE_BONDING_STATE_KEY,
    VoiceBondingController,
    VoiceBondingError,
    VoiceBondingProfile,
    VoiceBondingScore,
    default_voice_profile,
)

try:
    __version__ = _pkg_version("project-ai-companion")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "ALLOWED_EXPRESSIONS",
    "ALLOWED_PHASES",
    "ALLOWED_STATES",
    "ALLOWED_THOUGHT_TYPES",
    "BONDING_PHASES",
    "BOND_IDENTITY_OPERATION",
    "COGNITION_STATE_KEY",
    "COGNITION_THOUGHTS_KEY",
    "DEFAULT_PHASE",
    "DEFAULT_STATE",
    "NIRL_STATE_KEY",
    "PHASE_BONDED",
    "PHASE_UNBONDED",
    "PRUNE_FATES_OPERATION",
    "RECORD_FATE_OPERATION",
    "RESTORE_OPERATION",
    "UPDATE_OPERATION",
    "VOICE_BONDING_HISTORY_KEY",
    "VOICE_BONDING_STATE_KEY",
    "BondedCompanion",
    "CognitionController",
    "CognitionError",
    "CognitionStrategy",
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
    "Thought",
    "VoiceBondingController",
    "VoiceBondingError",
    "VoiceBondingProfile",
    "VoiceBondingScore",
    "default_cognition_strategy",
    "default_nirl_transition",
    "default_voice_profile",
]
