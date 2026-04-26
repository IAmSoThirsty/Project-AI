"""
Security module for Project-AI Sovereign Substrate.

This module provides cryptographic primitives, key management,
and security hardening utilities.
"""

from src.security.asymmetric_security import (
    SecurityContext,
    SecurityViolationError,
    OperationalState,
    RFICalculator,
    AdversarialProber,
    DimensionEntropyGuard,
    SecurityEnforcementGateway,
)

__all__ = [
    "SecurityContext",
    "SecurityViolationError",
    "OperationalState",
    "RFICalculator",
    "AdversarialProber",
    "DimensionEntropyGuard",
    "SecurityEnforcementGateway",
    "asymmetric_security",
]

# Create module-level instance for backward compatibility
asymmetric_security = SecurityEnforcementGateway()
