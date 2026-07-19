"""
sovereign_vault.release

There is no "open vault" state and no "mounted vault" state in this
module. The only operation is:

    verify -> authorize -> release (into locked memory) -> zeroize

`ObjectReleaseManager.release()` is a context manager. On entry it runs
every check in deny.RuntimeConditions (fully proven, not best-effort),
verifies the caller's AuthorityToken for exactly this object_id, verifies
the anti-rollback state is current, verifies audit has reserved capacity,
decrypts exactly one object into a SecureBuffer, and yields it. On exit —
success or exception — it zeroizes the buffer and writes a RELEASE_CLOSED
audit event. There is no path that leaves plaintext live after the `with`
block ends.

IPC hand-off (Unix domain socket with SCM_CREDENTIALS, or memfd_create
with F_SEAL_SEAL to a specific consumer PID) is a deploy-layer concern —
this module hands the consumer a SecureBuffer view in-process. The
`transfer_via_memfd` helper below is a real, working Linux
memfd_create-based option for when the consumer is a *separate* process
on the same host, sealed against further writes so the receiving process
cannot be tricked into treating it as a mutable, growable region.
"""

from __future__ import annotations

import contextlib
import os
import sys
from collections.abc import Iterator
from dataclasses import dataclass

from .buffer import SecureBuffer
from .deny import RuntimeConditions
from .errors import AuditUnavailableError, AuthorityNotProvenError, SafeHaltError
from .interfaces import AuditChainProvider, AuthorityProvider, AuthorityToken
from .metadata import MetadataIndex
from .primitives import unseal
from .state import AntiRollbackState


@dataclass
class SealedObjectRef:
    object_id: str
    tool_id: str
    nonce: bytes
    ciphertext: bytes
    aad: bytes


@dataclass
class ObjectReleaseManager:
    authority: AuthorityProvider
    audit: AuditChainProvider
    rollback_state: AntiRollbackState
    metadata: MetadataIndex

    def _preflight(
        self,
        object_id: str,
        token: AuthorityToken,
        conditions: RuntimeConditions,
        expected_state_sequence: int,
    ) -> None:
        # Deny-by-default gate: every condition must be explicitly proven.
        conditions.require_all()

        if not self.authority.verify(token, required_scope=f"vault.release:{object_id}"):
            raise AuthorityNotProvenError(
                f"release {object_id}: authority not proven for scope 'vault.release:{object_id}'"
            )

        if not self.metadata.verify_binding(object_id):
            raise SafeHaltError(
                f"release {object_id}: metadata dual-index binding failed — "
                f"encrypted index and exposure index have diverged"
            )

        if self.rollback_state.last_sequence != expected_state_sequence:
            raise SafeHaltError(
                f"release {object_id}: vault state sequence "
                f"{self.rollback_state.last_sequence} != caller's expected "
                f"{expected_state_sequence} — refusing release against stale state"
            )

        if not self.audit.has_capacity():
            raise AuditUnavailableError(
                f"release {object_id}: audit chain has no reserved capacity — "
                f"refusing an unauditable release"
            )

    @contextlib.contextmanager
    def release(
        self,
        sealed: SealedObjectRef,
        record_key: bytes,
        token: AuthorityToken,
        conditions: RuntimeConditions,
        expected_state_sequence: int,
    ) -> Iterator[SecureBuffer]:
        self._preflight(sealed.object_id, token, conditions, expected_state_sequence)

        entry_id = self.audit.append(
            "RELEASE_AUTHORIZED",
            {"object_id": sealed.object_id, "subject": token.subject, "scope": token.scope},
        )

        plaintext = unseal(record_key, sealed.nonce, sealed.ciphertext, aad=sealed.aad)
        buf = SecureBuffer(plaintext)
        try:
            yield buf
        finally:
            buf.zeroize()
            self.audit.append(
                "RELEASE_CLOSED",
                {"object_id": sealed.object_id, "authorized_entry": entry_id},
            )


def transfer_via_memfd(data: bytes, name: str = "vault-object") -> int | None:
    """
    Optional real Linux mechanism for handing released plaintext to a
    *separate* process without ever writing it to a normal file: creates
    an anonymous, in-memory file descriptor, writes the plaintext, seals
    it against further writes/growth/shrink, and returns the fd for
    passing over a Unix domain socket via SCM_RIGHTS.

    Returns None on non-Linux platforms — callers must have an in-process
    fallback (SecureBuffer hand-off) rather than assuming this succeeds.

    The caller is still responsible for closing/zeroizing on both ends
    after the consumer is done; sealing prevents the *receiver* from
    resizing/rewriting it, it does not itself zeroize on close.
    """
    if sys.platform == "win32":
        # memfd/fcntl sealing is POSIX-only. The static guard mirrors the
        # runtime hasattr check below so mypy's per-platform analysis never
        # sees fcntl members that its platform view does not define.
        return None
    if not hasattr(os, "memfd_create"):
        return None
    try:
        fd: int = os.memfd_create(name, flags=getattr(os, "MFD_ALLOW_SEALING", 0))
        os.write(fd, data)
        os.lseek(fd, 0, os.SEEK_SET)
        F_ADD_SEALS = 1033
        F_SEAL_SEAL = 0x0001
        F_SEAL_SHRINK = 0x0002
        F_SEAL_GROW = 0x0004
        F_SEAL_WRITE = 0x0008
        import fcntl

        fcntl.fcntl(fd, F_ADD_SEALS, F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_WRITE | F_SEAL_SEAL)
        return fd
    except Exception:
        return None
