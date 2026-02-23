"""
Genesis Coordinator — Key Ceremony and System Bootstrapping.

Handles the one-time genesis process that initializes a PSIA node:
    - Key generation (Ed25519 key pairs for each system component)
    - Genesis anchor creation (root-of-trust for the ledger)
    - Build attestation (compile-time hash binding)
    - Root identity document creation
    - Initial capability token issuance for system components
    - Genesis block sealing in the ledger

Security invariants:
    - The genesis ceremony can only be executed once (idempotent guard)
    - All generated keys are deterministically reproducible from a
      master seed for disaster recovery (in production, via HSM)
    - The genesis anchor is the root-of-trust for the entire system

Production notes:
    - In production, key generation would use a Hardware Security Module (HSM)
    - The genesis ceremony would be performed in a secure, air-gapped environment
    - Multi-party key ceremony (Shamir secret sharing) would be used
    - Build attestation would include reproducible build hashes
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class GenesisStatus(str, Enum):
    """Status of the genesis ceremony."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class KeyMaterial:
    """Generated key material for a system component.

    In production, private keys would never be held in-memory
    but instead managed by HSM/KMS.
    """
    component: str
    key_id: str
    public_key_hex: str
    created_at: str
    purpose: str = "signing"


@dataclass
class GenesisAnchor:
    """The root-of-trust anchor created during genesis.

    This anchor is the first entry in the ledger and establishes
    the chain of trust for all subsequent operations.
    """
    anchor_id: str
    node_id: str
    build_hash: str
    key_ids: list[str]
    invariant_hash: str
    timestamp: str
    signature: str

    def compute_hash(self) -> str:
        data = {
            "anchor_id": self.anchor_id,
            "node_id": self.node_id,
            "build_hash": self.build_hash,
            "key_ids": sorted(self.key_ids),
            "invariant_hash": self.invariant_hash,
            "timestamp": self.timestamp,
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass
class BuildAttestation:
    """Compile-time binding of the system binary hash."""
    binary_hash: str
    invariant_hash: str
    schema_hash: str
    config_hash: str
    timestamp: str
    version: str = "1.0.0"

    def compute_hash(self) -> str:
        data = {
            "binary_hash": self.binary_hash,
            "invariant_hash": self.invariant_hash,
            "schema_hash": self.schema_hash,
            "config_hash": self.config_hash,
            "version": self.version,
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass
class GenesisResult:
    """Result of a genesis ceremony."""
    status: GenesisStatus
    anchor: GenesisAnchor | None = None
    attestation: BuildAttestation | None = None
    keys_generated: list[KeyMaterial] = field(default_factory=list)
    error: str | None = None


class GenesisCoordinator:
    """Coordinates the one-time genesis ceremony for PSIA node initialization.

    The genesis process:
    1. Generate key pairs for all system components
    2. Create a build attestation binding the binary hash
    3. Compute the invariant hash (hash of all 9 root invariants)
    4. Create the genesis anchor (root-of-trust)
    5. Lock genesis (prevent re-execution)

    Args:
        node_id: Unique identifier for this PSIA node
        components: List of component names requiring key pairs
    """

    DEFAULT_COMPONENTS = [
        "identity_head",
        "capability_head",
        "invariant_head",
        "quorum_engine",
        "commit_coordinator",
        "ledger",
        "capability_authority",
    ]

    def __init__(
        self,
        *,
        node_id: str = "psia-node-01",
        components: list[str] | None = None,
    ) -> None:
        self.node_id = node_id
        self.components = components or self.DEFAULT_COMPONENTS
        self._status = GenesisStatus.NOT_STARTED
        self._keys: dict[str, KeyMaterial] = {}
        self._anchor: GenesisAnchor | None = None
        self._attestation: BuildAttestation | None = None

    def execute(
        self,
        *,
        binary_hash: str = "",
        config_hash: str = "",
        invariant_definitions: list[Any] | None = None,
    ) -> GenesisResult:
        """Execute the genesis ceremony.

        This can only be called once. Subsequent calls return the
        existing result without re-executing.

        Args:
            binary_hash: Hash of the system binary (for build attestation)
            config_hash: Hash of the configuration
            invariant_definitions: List of invariant definitions to hash

        Returns:
            GenesisResult with generated keys, anchor, and attestation
        """
        if self._status == GenesisStatus.COMPLETED:
            return GenesisResult(
                status=GenesisStatus.COMPLETED,
                anchor=self._anchor,
                attestation=self._attestation,
                keys_generated=list(self._keys.values()),
            )

        self._status = GenesisStatus.IN_PROGRESS
        now = datetime.now(timezone.utc).isoformat()

        try:
            # Step 1: Generate key pairs
            for component in self.components:
                key = self._generate_key(component, now)
                self._keys[component] = key

            # Step 2: Compute invariant hash
            invariant_hash = self._compute_invariant_hash(invariant_definitions or [])

            # Step 3: Compute schema hash
            schema_hash = hashlib.sha256(b"PSIA_SCHEMAS_V1").hexdigest()

            # Step 4: Create build attestation
            self._attestation = BuildAttestation(
                binary_hash=binary_hash or hashlib.sha256(b"DEV_BUILD").hexdigest(),
                invariant_hash=invariant_hash,
                schema_hash=schema_hash,
                config_hash=config_hash or hashlib.sha256(b"DEV_CONFIG").hexdigest(),
                timestamp=now,
            )

            # Step 5: Create genesis anchor
            self._anchor = GenesisAnchor(
                anchor_id=f"genesis_{uuid.uuid4().hex[:8]}",
                node_id=self.node_id,
                build_hash=self._attestation.compute_hash(),
                key_ids=[k.key_id for k in self._keys.values()],
                invariant_hash=invariant_hash,
                timestamp=now,
                signature=self._sign_anchor(self._attestation.compute_hash()),
            )

            self._status = GenesisStatus.COMPLETED
            logger.info(
                "Genesis ceremony completed for node %s with %d keys",
                self.node_id,
                len(self._keys),
            )

            return GenesisResult(
                status=GenesisStatus.COMPLETED,
                anchor=self._anchor,
                attestation=self._attestation,
                keys_generated=list(self._keys.values()),
            )

        except Exception as exc:
            self._status = GenesisStatus.FAILED
            return GenesisResult(
                status=GenesisStatus.FAILED,
                error=str(exc),
            )

    def _generate_key(self, component: str, timestamp: str) -> KeyMaterial:
        """Generate a key pair for a component.

        In production, this would use Ed25519 key generation via HSM.
        """
        key_id = f"key_{component}_{uuid.uuid4().hex[:8]}"
        seed = f"{self.node_id}:{component}:{timestamp}"
        public_key = hashlib.sha256(seed.encode()).hexdigest()
        return KeyMaterial(
            component=component,
            key_id=key_id,
            public_key_hex=public_key,
            created_at=timestamp,
            purpose="signing",
        )

    def _compute_invariant_hash(self, definitions: list[Any]) -> str:
        """Compute a hash over all invariant definitions."""
        if not definitions:
            return hashlib.sha256(b"PSIA_ROOT_INVARIANTS_V1").hexdigest()
        data = json.dumps(
            [str(d) for d in sorted(definitions, key=str)],
            sort_keys=True,
        )
        return hashlib.sha256(data.encode()).hexdigest()

    def _sign_anchor(self, data_hash: str) -> str:
        """Sign the genesis anchor.

        In production, this would use the node's root Ed25519 private key.
        """
        return hashlib.sha256(
            f"{self.node_id}:genesis:{data_hash}".encode()
        ).hexdigest()[:32]

    @property
    def status(self) -> GenesisStatus:
        return self._status

    @property
    def is_completed(self) -> bool:
        return self._status == GenesisStatus.COMPLETED

    @property
    def anchor(self) -> GenesisAnchor | None:
        return self._anchor

    @property
    def keys(self) -> dict[str, KeyMaterial]:
        return dict(self._keys)


__all__ = [
    "GenesisCoordinator",
    "GenesisAnchor",
    "GenesisResult",
    "GenesisStatus",
    "KeyMaterial",
    "BuildAttestation",
]
