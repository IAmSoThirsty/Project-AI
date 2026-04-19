"""
Sovereign Tool Vault - Constitutional Grade Security for Offensive Security Tools

Provides fortress-grade protection for penetration testing tools with:
- Genesis key binding (cryptographic root of trust)
- Multi-layer encryption (AES-256-GCM + Fernet)
- USB physical token authentication
- Zero-trust access control
- Constitutional audit logging
- Sandboxed execution isolation
- Emergency panic lockdown

Architecture:
    - Control Plane: Policy decisions, approvals, audit
    - Execution Plane: Tool decryption, execution, monitoring
    - Split-plane design prevents direct operator bypass

Security Posture: MAXIMUM - Constitutional Grade

Example:
    >>> from app.vault import SovereignToolVault
    >>> vault = SovereignToolVault(data_dir="security/sovereign_vault")
    >>> vault.mount_with_usb_token("/media/usb", passphrase="***")
    >>> vault.execute_tool("tools/001_rubeus.exe.enc", args=["asktgt", "/user:test"])
    >>> vault.unmount()
"""

from app.vault.core.vault import SovereignToolVault
from app.vault.auth.usb_token import USBPhysicalToken
from app.vault.core.exceptions import (
    VaultError,
    VaultLockdownError,
    VaultAuthenticationError,
    TokenError,
)

__all__ = [
    "SovereignToolVault",
    "USBPhysicalToken",
    "VaultError",
    "VaultLockdownError",
    "VaultAuthenticationError",
    "TokenError",
]

__version__ = "1.0.0"
