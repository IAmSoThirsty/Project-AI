"""Project-AI capability public interface."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from capability.authority import (
    CapabilityAuthority,
    CapabilityClaims,
    CapabilityError,
    ExpiredCapabilityError,
    InvalidCapabilityError,
    ReplayedCapabilityError,
    RevokedCapabilityError,
    ScopeMismatchError,
)

try:
    __version__ = _pkg_version("project-ai-capability")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "CapabilityAuthority",
    "CapabilityClaims",
    "CapabilityError",
    "ExpiredCapabilityError",
    "InvalidCapabilityError",
    "ReplayedCapabilityError",
    "RevokedCapabilityError",
    "ScopeMismatchError",
]
