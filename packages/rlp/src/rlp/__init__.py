"""Experimental Reciprocal Legitimacy Protocol policy engine."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from .rlp import (
    RLP,
    ActionRequest,
    AuditLog,
    AuditTamper,
    CapabilityToken,
    GateResult,
    HarmVerdict,
    HumanDiscretion,
    RLPDenied,
    StateRegister,
    SystemStatus,
)

try:
    __version__ = _pkg_version("project-ai-rlp")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"
__status__ = "experimental"

__all__ = [
    "RLP",
    "ActionRequest",
    "AuditLog",
    "AuditTamper",
    "CapabilityToken",
    "GateResult",
    "HarmVerdict",
    "HumanDiscretion",
    "RLPDenied",
    "StateRegister",
    "SystemStatus",
]
