"""Project-AI Atlas public interface."""

from atlas.analysis import (
    SUBORDINATION_NOTICE,
    Claim,
    ClaimType,
    Evidence,
    EvidenceTier,
    Projection,
    analyze,
)
from atlas.service import RECORD_OPERATION, Atlas

__version__ = "0.0.0.dev0"

__all__ = [
    "RECORD_OPERATION",
    "SUBORDINATION_NOTICE",
    "Atlas",
    "Claim",
    "ClaimType",
    "Evidence",
    "EvidenceTier",
    "Projection",
    "analyze",
]
