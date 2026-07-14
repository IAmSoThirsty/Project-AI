"""
sovereign_vault.state

Anti-rollback. Every state-mutating operation (metadata change, policy
update, revocation, key epoch bump) produces a new Checkpoint with a
strictly increasing sequence number, hash-linked to its predecessor and
Ed25519-signed. Restoring an older-but-valid checkpoint is exactly what
this is built to catch: `verify_advance` rejects any checkpoint whose
sequence is <= the last one this vault instance has observed, even if
the signature is perfectly valid.

VERIFIED here: local monotonic sequence + hash chain + signature.
SEAM (not implemented here): external anchoring (e.g. publishing the
checkpoint hash to a witness log / transparency service) so that even an
attacker with full control of local storage cannot roll back undetected.
`ExternalWitness` below is the seam for that; the default raises.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field

from .errors import RollbackDetectedError
from .primitives import SigningIdentity, verify_signature


def _canonical(obj: dict[str, object]) -> bytes:
    """Deterministic JSON: sorted keys, no whitespace ambiguity. Matches
    the canonicalization discipline CBCC already applies before hashing —
    do not hash a non-canonical representation of the same logical state."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


@dataclass(frozen=True)
class Checkpoint:
    sequence: int
    prev_hash: str  # hex sha256 of the previous checkpoint's canonical body, or "0"*64 for genesis
    state_summary: dict[
        str, object
    ]  # e.g. {"revocation_list_hash": ..., "policy_hash": ..., "metadata_hash": ...}
    timestamp_ns: int
    signature: bytes
    signer_public_key: bytes

    def body(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "prev_hash": self.prev_hash,
            "state_summary": self.state_summary,
            "timestamp_ns": self.timestamp_ns,
        }

    def content_hash(self) -> str:
        return hashlib.sha256(_canonical(self.body())).hexdigest()

    def verify_signature(self) -> bool:
        return verify_signature(self.signer_public_key, _canonical(self.body()), self.signature)


class ExternalWitness:
    """Seam for anchoring checkpoint hashes outside local storage
    (transparency log, second host, notarization service). Default
    fails closed rather than pretending local-only anti-rollback is
    sufficient against an attacker with disk access."""

    def anchor(self, checkpoint_hash: str) -> None:
        raise NotImplementedError(
            "No ExternalWitness wired. Local hash-chain + signature checks "
            "for rollback are active, but an attacker with full control of "
            "local storage can still replay an old *self-consistent* chain "
            "unless checkpoints are anchored externally. Wire a witness "
            "before relying on this for that threat model."
        )

    def verify_anchor(self, checkpoint_hash: str) -> bool:
        raise NotImplementedError("No ExternalWitness wired.")


@dataclass
class AntiRollbackState:
    signer: SigningIdentity
    witness: ExternalWitness | None = None
    _last: Checkpoint | None = field(default=None, repr=False)

    def genesis(self, state_summary: dict[str, object]) -> Checkpoint:
        if self._last is not None:
            raise RollbackDetectedError("genesis() called on a non-empty chain")
        cp = self._make(sequence=0, prev_hash="0" * 64, state_summary=state_summary)
        self._last = cp
        return cp

    def advance(self, state_summary: dict[str, object]) -> Checkpoint:
        if self._last is None:
            raise RollbackDetectedError("advance() called before genesis()")
        cp = self._make(
            sequence=self._last.sequence + 1,
            prev_hash=self._last.content_hash(),
            state_summary=state_summary,
        )
        self._last = cp
        return cp

    def _make(self, sequence: int, prev_hash: str, state_summary: dict[str, object]) -> Checkpoint:
        timestamp_ns: int = time.time_ns()
        body: dict[str, object] = {
            "sequence": sequence,
            "prev_hash": prev_hash,
            "state_summary": state_summary,
            "timestamp_ns": timestamp_ns,
        }
        sig = self.signer.sign(_canonical(body))
        return Checkpoint(
            sequence=sequence,
            prev_hash=prev_hash,
            state_summary=state_summary,
            timestamp_ns=timestamp_ns,
            signature=sig,
            signer_public_key=self.signer.public_bytes(),
        )

    def verify_advance(self, candidate: Checkpoint) -> None:
        """
        Call this on any checkpoint loaded from disk/backup/peer before
        trusting it. Raises RollbackDetectedError on:
          - bad signature
          - broken hash link
          - sequence <= last observed sequence (THE rollback check)
        """
        if not candidate.verify_signature():
            raise RollbackDetectedError(f"checkpoint {candidate.sequence}: invalid signature")
        if self._last is not None:
            if candidate.sequence <= self._last.sequence:
                raise RollbackDetectedError(
                    f"checkpoint sequence {candidate.sequence} <= last observed "
                    f"{self._last.sequence} — stale state rejected"
                )
            if candidate.prev_hash != self._last.content_hash():
                raise RollbackDetectedError(
                    f"checkpoint {candidate.sequence} prev_hash does not chain "
                    f"from last observed checkpoint {self._last.sequence}"
                )
        if self.witness is not None and not self.witness.verify_anchor(candidate.content_hash()):
            raise RollbackDetectedError(
                f"checkpoint {candidate.sequence} not found in external witness log"
            )
        self._last = candidate

    @property
    def last_sequence(self) -> int:
        if self._last is None:
            raise RollbackDetectedError("no checkpoint observed yet")
        return self._last.sequence
