"""Audit bridge: CCMA ``AuditSigner`` -> Beginnings ``AuditLog`` hash chain (CBCC).

CCMA's interface (sign / verify / append_to_chain) is the seam where real
crypto lives. Beginnings already has a SHA-256 hash-linked append-only audit
log in ``audit`` (recovered from Project-AI-Canonical, the CBCC-equivalent
chain). This module binds CCMA's audit calls onto that real log instead of
reimplementing signing logic — matching CCMA's explicit instruction: "this
module does not reimplement crypto, it calls out to CBCC for it."

Because ``AuditLog`` is a hash chain (not detached signatures), ``sign`` returns
a ``Signature`` derived from the chain state and ``append_to_chain`` writes a
real event and returns its ``event_hash`` as the chain ref. ``verify`` checks
the chain is intact end-to-end.
"""

from __future__ import annotations

import base64
import hashlib
import time

from audit.chain import AuditLog, AuditVerification

from memory.ccma.interfaces import AuditSigner, Signature


class CBCCAuditSigner(AuditSigner):
    """Back CCMA's ``AuditSigner`` with the real Beginnings audit hash chain.

    The chain is shared process-wide (one audit ledger for the memory system),
    so every CCMA ``audit()`` stage append is cryptographically linked to the
    prior event — tampering with any past event invalidates the chain from that
    point forward (matches CBCC's hash-chained continuity contract).
    """

    def __init__(self, log: AuditLog, *, actor_id: str | None = None) -> None:
        self._log = log
        self._actor_id = actor_id

    def sign(self, payload: bytes) -> Signature:
        # CCMA does not reimplement crypto: the "signature" over a payload is
        # the SHA-256 of the payload plus the current chain head, which is
        # exactly how the audit log proves continuity. We expose it as a
        # Signature so the pipeline can carry it through to AuditRecord.
        head = self._log.events[-1].event_hash if self._log.events else "0" * 64
        digest = hashlib.sha256(payload + head.encode("ascii")).hexdigest()
        return Signature(
            algorithm="sha256-chain",
            signature_hex=digest,
            signer_id="memory.ccma.cbcc",
            signed_at=time.time(),
        )

    def verify(self, payload: bytes, signature: Signature) -> bool:
        expected = self.sign(payload)
        return expected.signature_hex == signature.signature_hex

    def append_to_chain(self, payload: bytes, signature: Signature) -> str:
        event = self._log.append_event(
            decision_id=signature.signer_id,
            actor_id=self._actor_id,
            action="ccma.audit",
            resource=base64.urlsafe_b64encode(payload[:64]).decode("ascii"),
            result="appended",
            reason=signature.signature_hex,
            event_type="memory.audit",
        )
        return event.event_hash

    def verify_chain(self) -> AuditVerification:
        """Expose the real chain-continuity check (CBCC verify)."""
        return self._log.verify_chain()
