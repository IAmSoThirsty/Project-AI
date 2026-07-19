"""Experimental operator-side governance substrate."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from .arbiter_gov import (
    AdversarialReview,
    AdversarialReviewError,
    AppendOnlyLedger,
    ArbiterGovernance,
    ArbiterStatus,
    CapacityBudget,
    DegradationScan,
    DualSignatureExecutor,
    EntryType,
    FileLedgerBackend,
    Finding,
    GateState,
    GateViolation,
    LedgerIntegrityError,
    Severity,
    SignatureError,
    Signer,
    SuccessionRegistry,
    SustainabilityGate,
    SustainabilityViolation,
    TimeDelayGate,
    rule_power_consolidation,
)

try:
    __version__ = _pkg_version("project-ai-arbiter")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"
__status__ = "experimental"

__all__ = [
    "AdversarialReview",
    "AdversarialReviewError",
    "AppendOnlyLedger",
    "ArbiterGovernance",
    "ArbiterStatus",
    "CapacityBudget",
    "DegradationScan",
    "DualSignatureExecutor",
    "EntryType",
    "FileLedgerBackend",
    "Finding",
    "GateState",
    "GateViolation",
    "LedgerIntegrityError",
    "Severity",
    "SignatureError",
    "Signer",
    "SuccessionRegistry",
    "SustainabilityGate",
    "SustainabilityViolation",
    "TimeDelayGate",
    "rule_power_consolidation",
]
