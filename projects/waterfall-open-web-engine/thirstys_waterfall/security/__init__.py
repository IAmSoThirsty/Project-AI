# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""Security module for Thirstys Waterfall - Advanced Security Features"""

from .hardware_root_of_trust import (
    HardwareRootOfTrust,
    TPMInterface,
    SecureEnclaveInterface,
    HSMInterface,
    HardwareType,
    AttestationStatus,
    HardwareInterface,
)
from .privacy_risk_engine import PrivacyRiskEngine, RiskLevel
from .microvm_isolation import MicroVMIsolationManager, MicroVMInstance
from .mfa_auth import (
    MFAAuthenticator,
    AuthContext,
    AuthMethod,
    AuthLevel,
    TOTPProvider,
    FIDO2Provider,
    PasskeyProvider,
    CertificateProvider,
    BiometricProvider,
    BiometricType,
)
from .dos_trap import (
    DOSTrapMode,
    CompromiseDetector,
    CompromiseEvent,
    CompromiseType,
    ThreatLevel,
    ResponseAction,
    SanitizationMode,
    SecretWiper,
    HardwareKeyDestroyer,
    InterfaceDisabler,
    MemorySanitizer,
    DiskSanitizer,
    create_dos_trap,
)

__all__ = [
    "HardwareRootOfTrust",
    "TPMInterface",
    "SecureEnclaveInterface",
    "HSMInterface",
    "HardwareType",
    "AttestationStatus",
    "HardwareInterface",
    "PrivacyRiskEngine",
    "RiskLevel",
    "MicroVMIsolationManager",
    "MicroVMInstance",
    "MFAAuthenticator",
    "AuthContext",
    "AuthMethod",
    "AuthLevel",
    "TOTPProvider",
    "FIDO2Provider",
    "PasskeyProvider",
    "CertificateProvider",
    "BiometricProvider",
    "BiometricType",
    "DOSTrapMode",
    "CompromiseDetector",
    "CompromiseEvent",
    "CompromiseType",
    "ThreatLevel",
    "ResponseAction",
    "SanitizationMode",
    "SecretWiper",
    "HardwareKeyDestroyer",
    "InterfaceDisabler",
    "MemorySanitizer",
    "DiskSanitizer",
    "create_dos_trap",
]
