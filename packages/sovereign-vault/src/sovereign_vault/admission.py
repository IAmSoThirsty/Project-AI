"""
sovereign_vault.admission

Admission is a verification pipeline, not a write operation. Nothing
reaches metadata.MetadataIndex.admit() or release.py's storage path
without first passing through AdmissionRecord.verify() and being logged
to the audit chain as an ADMISSION_APPROVED event.

SBOM verification (in-toto / Cosign attestation format) and hash-registry
lookups are named as seams here (`ProvenanceVerifier`), not reimplemented —
this package does not ship a supply-chain attestation verifier; it defines
the contract admission must satisfy before storage is permitted.
"""

from __future__ import annotations

import hashlib
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .errors import AdmissionRejectedError
from .interfaces import AuditChainProvider, AuthorityProvider, AuthorityToken


@dataclass(frozen=True)
class AdmissionRecord:
    object_id: str
    source: str  # where it came from: system/user/pipeline identifier
    sha256: str  # content hash of the plaintext being admitted
    signature: bytes | None  # signature over the content, if the source provides one
    signer_public_key: bytes | None
    version: str
    sbom_reference: str | None  # in-toto/Cosign attestation reference, if applicable
    approved_by: AuthorityToken  # explicit human/admin approval — never inferred
    approved_at_ns: int


class ProvenanceVerifier(ABC):
    """Seam for actual SBOM/signature/hash-registry verification (e.g.
    in-toto layout verification, Cosign signature/attestation checks,
    known-good hash registry lookup). Default fails closed."""

    @abstractmethod
    def verify(self, record: AdmissionRecord, plaintext: bytes) -> bool: ...


class FailClosedProvenanceVerifier(ProvenanceVerifier):
    def verify(self, record: AdmissionRecord, plaintext: bytes) -> bool:
        raise AdmissionRejectedError(
            "No ProvenanceVerifier wired — cannot verify SBOM/signature/hash "
            "registry. Refusing admission rather than trusting unverified input."
        )


def admit_object(
    record: AdmissionRecord,
    plaintext: bytes,
    provenance: ProvenanceVerifier,
    authority: AuthorityProvider,
    audit: AuditChainProvider,
) -> str:
    """
    Full admission pipeline. Returns the audit entry id on success.
    Raises AdmissionRejectedError on any failure — partial admission does
    not exist; either the object is fully verified and logged, or nothing
    happens.
    """
    computed_hash = hashlib.sha256(plaintext).hexdigest()
    if computed_hash != record.sha256:
        raise AdmissionRejectedError(
            f"admission {record.object_id}: declared sha256 {record.sha256} "
            f"does not match computed {computed_hash}"
        )

    if not authority.verify(record.approved_by, required_scope="vault.admit"):
        raise AdmissionRejectedError(
            f"admission {record.object_id}: approval token does not carry "
            f"'vault.admit' scope, or failed verification"
        )

    if not audit.has_capacity():
        raise AdmissionRejectedError(
            f"admission {record.object_id}: audit chain has no reserved "
            f"capacity — refusing an unauditable admission"
        )

    if not provenance.verify(record, plaintext):
        raise AdmissionRejectedError(
            f"admission {record.object_id}: provenance verification failed "
            f"(SBOM/signature/hash-registry check did not pass)"
        )

    if record.approved_at_ns > time.time_ns() + 5_000_000_000:
        # approval timestamp more than 5s in the future: reject rather than
        # silently accept a clock-skewed or forged approval
        raise AdmissionRejectedError(
            f"admission {record.object_id}: approval timestamp is in the future"
        )

    return audit.append(
        "ADMISSION_APPROVED",
        {
            "object_id": record.object_id,
            "source": record.source,
            "sha256": record.sha256,
            "version": record.version,
            "sbom_reference": record.sbom_reference,
            "approved_by": record.approved_by.subject,
            "approved_at_ns": record.approved_at_ns,
        },
    )
