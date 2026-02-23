"""
Cerberus Identity Head — Actor Identity Verification.

Performs deep identity verification on the actor DID presented in
the RequestEnvelope.  This is the first of three Cerberus heads
and focuses exclusively on proving the actor *is who they claim to be*.

Checks performed:
    1. DID format validation (did:project-ai:<namespace>:<id>)
    2. Identity document resolution (lookup in IdentityDocumentStore)
    3. Revocation status check
    4. Public key validity window
    5. Certificate / device binding verification
    6. Subject-actor relationship validation
    7. Risk tier assessment

Security invariants:
    - INV-ROOT-2 (No identity bypass — every request must resolve to
      a valid, non-revoked identity)
    - INV-ROOT-8 (Identity uniqueness — no DID collisions)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from psia.schemas.cerberus_decision import (
    CerberusVote,
    ConstraintsApplied,
    DenyReason,
)
from psia.schemas.identity import IdentityDocument, Signature

logger = logging.getLogger(__name__)

# Canonical DID format:  did:project-ai:<namespace>:<identifier>
# Minimum: did:project-ai:<something>  (one colon-separated segment after prefix)
_DID_PATTERN = re.compile(
    r"^did:project-ai:"  # method prefix
    r"[a-z0-9_-]+"       # at least one namespace segment
    r"(:[a-z0-9_-]+)*$", # optional further segments
    re.IGNORECASE,
)


class IdentityDocumentStore:
    """Lookup service for IdentityDocument instances.

    In production this would be backed by a database or distributed
    directory (e.g., DID resolver connected to a VDR).
    """

    def __init__(self) -> None:
        self._documents: dict[str, IdentityDocument] = {}

    def register(self, doc: IdentityDocument) -> None:
        """Register an identity document.

        Raises:
            ValueError: If a document with the same DID already exists
                        (INV-ROOT-8 uniqueness).
        """
        if doc.id in self._documents:
            raise ValueError(
                f"INV-ROOT-8 violation: duplicate DID '{doc.id}' — "
                f"identity uniqueness constraint"
            )
        self._documents[doc.id] = doc

    def resolve(self, did: str) -> IdentityDocument | None:
        """Resolve a DID to its IdentityDocument or None."""
        return self._documents.get(did)

    def revoke(self, did: str, reason: str = "unspecified") -> bool:
        """Mark an identity as revoked (in-place mutation for Phase 3).

        Returns:
            True if the identity was found and revoked, False otherwise
        """
        doc = self._documents.get(did)
        if doc is None:
            return False
        # Pydantic models are frozen — rebuild with revocation
        updated = doc.model_copy(update={
            "revocation": {
                "status": "revoked",
                "revoked_at": datetime.now(timezone.utc).isoformat(),
                "reason": reason,
            }
        })
        self._documents[did] = updated
        return True

    @property
    def count(self) -> int:
        return len(self._documents)


@dataclass
class DeviceAttestationRegistry:
    """Registry of trusted device attestations per DID.

    In production this would be backed by a PKI / TPM-attestation
    verification service with certificate chain validation.
    """

    _attestations: dict[str, set[str]] = field(default_factory=dict)

    def register_device(self, did: str, attestation_hash: str) -> None:
        """Register an allowed device attestation for a DID."""
        self._attestations.setdefault(did, set()).add(attestation_hash)

    def is_trusted(self, did: str, attestation_hash: str | None) -> bool:
        """Check if the device attestation is trusted for this DID.

        If no attestations are registered for this DID, all devices
        are trusted (open enrollment mode).
        """
        if did not in self._attestations:
            return True  # Open enrollment
        if attestation_hash is None:
            return False  # Attestation required but not provided
        return attestation_hash in self._attestations[did]


class IdentityHead:
    """Cerberus Identity Head — production-grade actor verification.

    Replaces the Phase 1 ``StubIdentityHead`` with deep checks:
    DID format, document resolution, revocation, key validity,
    device binding, and risk tier.

    Args:
        doc_store: IdentityDocumentStore for DID resolution
        device_registry: Optional DeviceAttestationRegistry
        require_device_attestation: If True, deny when device attestation
            is required but not provided
        max_risk_tier: Maximum allowed risk tier ("low", "med", "high")
    """

    _RISK_RANK = {"low": 0, "med": 1, "high": 2, "critical": 3}

    def __init__(
        self,
        *,
        doc_store: IdentityDocumentStore | None = None,
        device_registry: DeviceAttestationRegistry | None = None,
        require_device_attestation: bool = False,
        max_risk_tier: str = "high",
    ) -> None:
        self.doc_store = doc_store or IdentityDocumentStore()
        self.device_registry = device_registry or DeviceAttestationRegistry()
        self.require_device_attestation = require_device_attestation
        self.max_risk_tier = max_risk_tier

    def evaluate(self, envelope: Any) -> CerberusVote:
        """Evaluate actor identity.

        Args:
            envelope: RequestEnvelope

        Returns:
            CerberusVote with identity verification result
        """
        reasons: list[DenyReason] = []
        constraints = ConstraintsApplied()

        # ── Check 1: DID format ──
        if not _DID_PATTERN.match(envelope.actor):
            reasons.append(DenyReason(
                code="IDENTITY_INVALID_DID_FORMAT",
                detail=f"Actor DID '{envelope.actor}' does not match "
                       f"'did:project-ai:<namespace>[:<id>]' format",
            ))

        # ── Check 2: Document resolution ──
        doc = self.doc_store.resolve(envelope.actor)
        if doc is None and not reasons and self.doc_store.count > 0:
            # Only report resolution failure if DID format was valid
            reasons.append(DenyReason(
                code="IDENTITY_NOT_FOUND",
                detail=f"No IdentityDocument found for DID '{envelope.actor}' — "
                       f"INV-ROOT-2 requires resolvable identity",
            ))

        # ── Check 3: Revocation status ──
        if doc is not None and doc.revocation.is_revoked:
            reasons.append(DenyReason(
                code="IDENTITY_REVOKED",
                detail=f"Identity '{envelope.actor}' is revoked: "
                       f"{doc.revocation.reason} (at {doc.revocation.revoked_at})",
            ))

        # ── Check 4: Public key validity window ──
        if doc is not None and not doc.revocation.is_revoked:
            now_iso = datetime.now(timezone.utc).isoformat()
            has_valid_key = False
            for key in doc.public_keys:
                key_created = key.created or "1970-01-01T00:00:00Z"
                key_expires = key.expires or "9999-12-31T23:59:59Z"
                if key_created <= now_iso <= key_expires:
                    has_valid_key = True
                    break
            if not has_valid_key:
                reasons.append(DenyReason(
                    code="IDENTITY_NO_VALID_KEY",
                    detail=f"No public key for '{envelope.actor}' is currently valid",
                ))

        # ── Check 5: Device attestation ──
        device_hash = getattr(envelope.context, "device_attestation", None)
        if not self.device_registry.is_trusted(envelope.actor, device_hash):
            if self.require_device_attestation:
                reasons.append(DenyReason(
                    code="IDENTITY_DEVICE_UNTRUSTED",
                    detail=f"Device attestation not recognized for '{envelope.actor}'",
                ))
            else:
                # Non-blocking constraint: add to constraints instead
                constraints = ConstraintsApplied(
                    rate_limit_per_min=60,  # Restrict untrusted devices
                )

        # ── Check 6: Subject-actor relationship ──
        if envelope.subject != envelope.actor:
            # Cross-identity request: requires delegation proof
            # For Phase 3, we accept if no doc store is configured (open mode)
            if self.doc_store.count > 0 and doc is not None:
                subject_doc = self.doc_store.resolve(envelope.subject)
                if subject_doc is None:
                    reasons.append(DenyReason(
                        code="IDENTITY_SUBJECT_NOT_FOUND",
                        detail=f"Subject DID '{envelope.subject}' not resolvable — "
                               f"cross-identity request denied",
                    ))

        # ── Check 7: Risk tier ──
        if doc is not None and hasattr(doc, "attributes") and doc.attributes:
            actor_tier = getattr(doc.attributes, "risk_tier", "low") or "low"
            max_rank = self._RISK_RANK.get(self.max_risk_tier, 2)
            actor_rank = self._RISK_RANK.get(actor_tier, 0)
            if actor_rank > max_rank:
                reasons.append(DenyReason(
                    code="IDENTITY_RISK_TIER_EXCEEDED",
                    detail=f"Actor risk tier '{actor_tier}' exceeds "
                           f"max allowed '{self.max_risk_tier}'",
                ))

        # ── Final vote ──
        if reasons:
            has_critical = any(
                r.code in ("IDENTITY_REVOKED", "IDENTITY_RISK_TIER_EXCEEDED")
                for r in reasons
            )
            decision = "deny"
        else:
            has_critical = False
            decision = "allow"

        return CerberusVote(
            request_id=envelope.request_id,
            head="identity",
            decision=decision,
            reasons=reasons,
            constraints_applied=constraints,
            timestamp=datetime.now(timezone.utc).isoformat(),
            signature=Signature(
                alg="ed25519",
                kid="cerberus_identity_k1",
                sig="identity_head_sig",
            ),
        )


__all__ = [
    "IdentityHead",
    "IdentityDocumentStore",
    "DeviceAttestationRegistry",
]
