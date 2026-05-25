"""PSIA Identity Head — DID validation, key expiry, device attestation, risk tier."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class VoteReason:
    code: str
    message: str = ""


@dataclass
class GateVote:
    head: str
    decision: str
    reasons: list[VoteReason] = field(default_factory=list)


_RISK_TIERS = {"low": 0, "med": 1, "medium": 1, "high": 2, "critical": 3}


class IdentityDocumentStore:
    def __init__(self) -> None:
        self._docs: dict[str, Any] = {}

    def register(self, doc: Any) -> None:
        if doc.id in self._docs:
            raise ValueError(f"INV-ROOT-8: DID '{doc.id}' already registered")
        self._docs[doc.id] = doc

    def get(self, did: str) -> Any | None:
        return self._docs.get(did)

    def __len__(self) -> int:
        return len(self._docs)


class DeviceAttestationRegistry:
    def __init__(self) -> None:
        self._devices: dict[str, set[str]] = {}

    def register_device(self, did: str, device_hash: str) -> None:
        if did not in self._devices:
            self._devices[did] = set()
        self._devices[did].add(device_hash)

    def is_trusted(self, did: str, device_hash: str) -> bool:
        return device_hash in self._devices.get(did, set())

    def has_registered_device(self, did: str) -> bool:
        return did in self._devices


def _is_valid_did(did: str) -> bool:
    parts = did.split(":")
    return len(parts) >= 3 and parts[0] == "did"


def _is_key_expired(key: Any) -> bool:
    if not key.expires:
        return False
    try:
        expiry = datetime.fromisoformat(key.expires)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) >= expiry
    except Exception:
        return False


class IdentityHead:
    def __init__(
        self,
        doc_store: IdentityDocumentStore | None = None,
        device_registry: DeviceAttestationRegistry | None = None,
        require_device_attestation: bool = False,
        max_risk_tier: str | None = None,
    ) -> None:
        self._store = doc_store
        self._device_registry = device_registry
        self._require_device_attestation = require_device_attestation
        self._max_risk_tier = max_risk_tier

    def evaluate(self, envelope: Any) -> GateVote:
        actor = envelope.actor

        if not _is_valid_did(actor):
            return GateVote(
                head="identity",
                decision="deny",
                reasons=[VoteReason(code="IDENTITY_INVALID_DID_FORMAT", message=f"Not a valid DID: {actor}")],
            )

        if self._store is None or len(self._store) == 0:
            return GateVote(head="identity", decision="allow")

        doc = self._store.get(actor)
        if doc is None:
            return GateVote(
                head="identity",
                decision="deny",
                reasons=[VoteReason(code="IDENTITY_NOT_FOUND", message=f"DID not found: {actor}")],
            )

        if doc.revocation and doc.revocation.is_revoked:
            return GateVote(
                head="identity",
                decision="deny",
                reasons=[VoteReason(code="IDENTITY_REVOKED", message=f"DID revoked: {actor}")],
            )

        valid_keys = [k for k in doc.public_keys if not _is_key_expired(k)]
        if not valid_keys:
            return GateVote(
                head="identity",
                decision="deny",
                reasons=[VoteReason(code="IDENTITY_NO_VALID_KEY", message="No non-expired public keys")],
            )

        if self._require_device_attestation and self._device_registry:
            if self._device_registry.has_registered_device(actor):
                device_hash = envelope.context.metadata.get("device_attestation", "")
                if not self._device_registry.is_trusted(actor, device_hash):
                    return GateVote(
                        head="identity",
                        decision="deny",
                        reasons=[VoteReason(code="IDENTITY_DEVICE_UNTRUSTED", message="Device not trusted")],
                    )

        if self._max_risk_tier and doc.attributes:
            identity_tier = _RISK_TIERS.get(doc.attributes.risk_tier, 0)
            max_tier = _RISK_TIERS.get(self._max_risk_tier, 0)
            if identity_tier > max_tier:
                return GateVote(
                    head="identity",
                    decision="deny",
                    reasons=[VoteReason(code="IDENTITY_RISK_TIER_EXCEEDED", message=f"Risk tier {doc.attributes.risk_tier} > max {self._max_risk_tier}")],
                )

        return GateVote(head="identity", decision="allow")
