"""
Vault Exception Hierarchy

All vault-related exceptions for proper error handling.
"""


class VaultError(Exception):
    """Base exception for all vault operations."""

    pass


class VaultLockdownError(VaultError):
    """Vault is in lockdown state - emergency seal active."""

    pass


class VaultAuthenticationError(VaultError):
    """Authentication failed - invalid credentials or token."""

    pass


class VaultMountError(VaultError):
    """Failed to mount vault - initialization or validation error."""

    pass


class VaultNotMountedError(VaultError):
    """Operation requires mounted vault but vault is not mounted."""

    pass


class TokenError(VaultError):
    """Base exception for USB token operations."""

    pass


class TokenNotFoundError(TokenError):
    """USB token not detected or invalid."""

    pass


class TokenSignatureError(TokenError):
    """Token signature verification failed - possible counterfeit."""

    pass


class TokenHardwareBindingError(TokenError):
    """Token hardware UUID mismatch - token copied or tampered."""

    pass


class TokenRevokedError(TokenError):
    """Token has been revoked - cannot use."""

    pass


class TokenTimeConstraintError(TokenError):
    """Token time constraints not satisfied - outside allowed window."""

    pass


class ToolNotFoundError(VaultError):
    """Requested tool not found in vault inventory."""

    pass


class ToolDecryptionError(VaultError):
    """Failed to decrypt tool - key mismatch or corruption."""

    pass


class ToolExecutionError(VaultError):
    """Tool execution failed in sandboxed environment."""

    pass


class QuorumError(VaultError):
    """Quorum threshold not met - insufficient operators."""

    pass


class CapabilityTokenError(VaultError):
    """Capability token validation failed."""

    pass


class ShadowSimulationError(VaultError):
    """Shadow simulation detected behavior deviation."""

    pass
