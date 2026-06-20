"""Experimental operator-side governance substrate."""

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
