"""PSIA genesis coordinator — key generation, anchor creation, attestation."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from psia.crypto.ed25519_provider import Ed25519KeyPair, Ed25519Provider

DEFAULT_COMPONENTS = [
    "identity",
    "capability",
    "invariant",
    "shadow",
    "canonical",
    "ingress",
    "legislative",
]


class GenesisStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class GenesisAnchor:
    anchor_id: str
    node_id: str
    key_ids: list[str]
    build_hash: str = ""
    invariant_hash: str = ""
    timestamp: str = ""
    signature: str = ""

    def compute_hash(self) -> str:
        d = {
            "node_id": self.node_id,
            "key_ids": sorted(self.key_ids),
            "anchor_id": self.anchor_id,
            "build_hash": self.build_hash,
            "invariant_hash": self.invariant_hash,
            "timestamp": self.timestamp,
        }
        return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()


@dataclass
class GenesisAttestation:
    binary_hash: str = ""
    config_hash: str = ""
    invariant_hash: str = ""


@dataclass
class BuildAttestation:
    binary_hash: str
    invariant_hash: str
    schema_hash: str
    config_hash: str
    timestamp: str
    version: str = "1.0.0"

    def compute_hash(self) -> str:
        d = {
            "binary_hash": self.binary_hash,
            "invariant_hash": self.invariant_hash,
            "schema_hash": self.schema_hash,
            "config_hash": self.config_hash,
            "timestamp": self.timestamp,
            "version": self.version,
        }
        return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()


@dataclass
class KeyMaterial:
    component: str
    key_id: str
    public_key_hex: str
    created_at: str
    purpose: str = "signing"


@dataclass
class GenesisResult:
    status: GenesisStatus
    keys_generated: list[str] = field(default_factory=list)
    anchor: GenesisAnchor | None = None
    attestation: GenesisAttestation | BuildAttestation | None = None
    error: str = ""


class GenesisCoordinator:
    DEFAULT_COMPONENTS = DEFAULT_COMPONENTS

    def __init__(
        self,
        node_id: str = "psia-node-01",
        components: list[str] | None = None,
    ) -> None:
        self._node_id = node_id
        self._components = list(components) if components is not None else list(DEFAULT_COMPONENTS)
        self._status = GenesisStatus.NOT_STARTED
        self._keys: dict[str, Ed25519KeyPair] = {}
        self._anchor: GenesisAnchor | None = None
        self._result: GenesisResult | None = None

    @property
    def node_id(self) -> str:
        return self._node_id

    @property
    def status(self) -> GenesisStatus:
        return self._status

    @property
    def is_completed(self) -> bool:
        return self._status == GenesisStatus.COMPLETED

    @property
    def keys(self) -> dict[str, Ed25519KeyPair]:
        return dict(self._keys)

    @property
    def anchor(self) -> GenesisAnchor | None:
        return self._anchor

    def execute(
        self,
        binary_hash: str = "",
        config_hash: str = "",
        invariant_definitions: list[Any] | None = None,
    ) -> GenesisResult:
        if self._result is not None:
            attestation = self._build_attestation(binary_hash, config_hash, invariant_definitions)
            return GenesisResult(
                status=GenesisStatus.COMPLETED,
                keys_generated=list(self._keys.keys()),
                anchor=self._anchor,
                attestation=attestation,
            )

        self._status = GenesisStatus.IN_PROGRESS
        for component in self._components:
            if component not in self._keys:
                self._keys[component] = Ed25519Provider.generate_keypair(component)

        key_ids = [kp.key_id for kp in self._keys.values()]
        anchor_seed = hashlib.sha256(
            (self._node_id + "".join(sorted(key_ids))).encode()
        ).hexdigest()
        anchor_id = f"genesis_{anchor_seed[:16]}"

        inv_hash = ""
        if invariant_definitions:
            inv_hash = hashlib.sha256(
                json.dumps([str(d) for d in invariant_definitions], sort_keys=True).encode()
            ).hexdigest()

        ts = datetime.now(timezone.utc).isoformat()
        sig = hashlib.sha256((anchor_id + self._node_id + ts).encode()).hexdigest()[:32]
        self._anchor = GenesisAnchor(
            anchor_id=anchor_id,
            node_id=self._node_id,
            key_ids=key_ids,
            build_hash=binary_hash,
            invariant_hash=inv_hash,
            timestamp=ts,
            signature=sig,
        )

        attestation = self._build_attestation(binary_hash, config_hash, invariant_definitions)
        self._status = GenesisStatus.COMPLETED
        self._result = GenesisResult(
            status=GenesisStatus.COMPLETED,
            keys_generated=list(self._keys.keys()),
            anchor=self._anchor,
            attestation=attestation,
        )
        return self._result

    def _build_attestation(
        self,
        binary_hash: str,
        config_hash: str,
        invariant_definitions: list[Any] | None,
    ) -> BuildAttestation:
        inv_hash = ""
        if invariant_definitions:
            inv_hash = hashlib.sha256(
                json.dumps([str(d) for d in invariant_definitions], sort_keys=True).encode()
            ).hexdigest()
        ts = datetime.now(timezone.utc).isoformat()
        return BuildAttestation(
            binary_hash=binary_hash,
            invariant_hash=inv_hash,
            schema_hash="",
            config_hash=config_hash,
            timestamp=ts,
        )
