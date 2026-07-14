"""
sovereign_vault.keys

Compartmentalized key hierarchy. There is no vault-wide key used directly
for sealing anything. RootKEK exists only long enough, in-process, to
derive the branch key actually needed, and is zeroized immediately after.

Tree:

    RootKEK (never stored; re-derived each session from combine_factors)
      -> VaultKey            info=b"vault:v1:<vault_id>"
           -> ToolKey         info=b"tool:v1:<tool_id>"
                -> RecordKey  info=b"record:v1:<record_id>"
      -> AuditSigningKey      info=b"audit-signing:v1:<vault_id>"
      -> MetadataKey          info=b"metadata:v1:<vault_id>"
      -> RecoveryWrapKey      info=b"recovery-wrap:v1:<vault_id>"
      -> TokenBindingKey      info=b"token-binding:v1:<vault_id>"

Compromise of RecordKey for record X reveals nothing about record Y
(different info label), nothing about AuditSigningKey (different branch),
and nothing about RootKEK (HKDF is one-way). This is what "compartmentalized"
has to mean operationally, not just as a diagram label.
"""

from __future__ import annotations

from dataclasses import dataclass

from .buffer import SecureBuffer
from .primitives import hkdf_sha512


def _info(*parts: str) -> bytes:
    return ("|".join(parts)).encode("utf-8")


@dataclass(frozen=True)
class KeyHierarchy:
    vault_id: str
    epoch: int = 0
    """
    epoch increments on every recovery.execute_recovery() call. Because
    epoch is folded into every derivation below, bumping it invalidates
    every subkey, token-binding key, and recovery-wrap key derived under
    the old epoch — by construction, not by a revocation list that has to
    be checked and can be bypassed if missed.
    """

    def vault_key(self, root_kek: bytes) -> bytes:
        return hkdf_sha512(root_kek, info=_info("vault", "v1", self.vault_id, f"epoch{self.epoch}"))

    def tool_key(self, root_kek: bytes, tool_id: str) -> bytes:
        vk = self.vault_key(root_kek)
        try:
            return hkdf_sha512(vk, info=_info("tool", "v1", tool_id))
        finally:
            _zero(vk)

    def record_key(self, root_kek: bytes, tool_id: str, record_id: str) -> bytes:
        tk = self.tool_key(root_kek, tool_id)
        try:
            return hkdf_sha512(tk, info=_info("record", "v1", record_id))
        finally:
            _zero(tk)

    def audit_signing_seed(self, root_kek: bytes) -> bytes:
        return hkdf_sha512(
            root_kek, info=_info("audit-signing", "v1", self.vault_id, f"epoch{self.epoch}")
        )

    def metadata_key(self, root_kek: bytes) -> bytes:
        return hkdf_sha512(
            root_kek, info=_info("metadata", "v1", self.vault_id, f"epoch{self.epoch}")
        )

    def recovery_wrap_key(self, root_kek: bytes) -> bytes:
        return hkdf_sha512(
            root_kek, info=_info("recovery-wrap", "v1", self.vault_id, f"epoch{self.epoch}")
        )

    def token_binding_key(self, root_kek: bytes) -> bytes:
        return hkdf_sha512(
            root_kek, info=_info("token-binding", "v1", self.vault_id, f"epoch{self.epoch}")
        )


def _zero(key_bytes: bytes) -> None:
    """Best-effort scrub of a derived key that was only needed transiently
    to reach a deeper branch. See buffer.py docstring for the honest
    limitation on what 'zeroize' can guarantee for immutable bytes."""
    # bytes are immutable in CPython; this cannot truly overwrite in place.
    # Recording the limitation rather than papering over it: real
    # transient-key hygiene for RootKEK itself is enforced by holding it
    # only inside a SecureBuffer at the call site (see vault.py), not here.
    del key_bytes


class RootKekSession:
    """
    Scopes RootKEK's lifetime to a `with` block. RootKEK is derived from
    combine_factors() by the caller, wrapped here, and zeroized on exit
    regardless of how the block ends.
    """

    def __init__(self, root_kek: bytes):
        self._buf = SecureBuffer(root_kek)

    def bytes(self) -> bytes:
        return bytes(self._buf.view())

    def __enter__(self) -> RootKekSession:
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        self._buf.zeroize()
