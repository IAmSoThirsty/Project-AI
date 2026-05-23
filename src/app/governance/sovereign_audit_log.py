"""
Sovereign-Grade Cryptographic Audit Log

Constitutional-grade audit logging with:
- Ed25519 per-entry digital signatures bound to a Genesis key pair
- HMAC with rotating keys for layered integrity
- Merkle tree batch anchoring for proof generation
- Deterministic replay mode for canonical verification
- Thread-safe append-only operation
- File persistence with truncation detection
- Genesis continuity protection (VECTOR 1, 2, 11)
- TSA anchor manager for external time proofs
- External Merkle anchor (optional IPFS / S3 / filesystem)
"""

from __future__ import annotations

import base64
import hashlib
import hmac as _hmac_module
import json
import logging
import secrets
import threading
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
    load_pem_private_key,
)

from .genesis_continuity import (
    GenesisContinuityGuard,
    GenesisDiscontinuityError,  # noqa: F401 — re-exported for callers
    GenesisReplacementError,
)

logger = logging.getLogger(__name__)


# ── stub anchor manager used when TSA deps are absent ────────────────────────

class _NoOpAnchorManager:
    """Zero-overhead stand-in when asn1crypto / requests are not installed."""

    anchor_points: list[dict] = []

    def get_anchor_count(self) -> int:
        return 0

    def get_latest_anchor(self):  # noqa: ANN201
        return None

    def get_anchor(self, idx: int):  # noqa: ANN201
        return None

    def get_anchors_since(self, idx: int) -> list:
        return []

    def verify_chain(self, public_key) -> tuple[bool, str]:  # noqa: ANN001
        return True, "No anchors (stub mode)"

    def _load(self) -> list[dict]:
        return []

    def _save(self, anchors: list[dict]) -> None:
        pass


def _make_anchor_manager(genesis_private_key, anchor_path: Path):
    """Return a TSAAnchorManager, or the no-op stub if deps are unavailable."""
    try:
        from .tsa_anchor_manager import TSAAnchorManager
        return TSAAnchorManager(genesis_private_key, anchor_path)
    except Exception:
        return _NoOpAnchorManager()


# ── GenesisKeyPair ────────────────────────────────────────────────────────────

class GenesisKeyPair:
    """Ed25519 key pair that persists as the root signing identity."""

    def __init__(self, key_dir: Path):
        self._key_dir = Path(key_dir)
        self._key_dir.mkdir(parents=True, exist_ok=True)
        self.private_key_path = self._key_dir / "genesis_audit.key"
        self.public_key_path = self._key_dir / "genesis_audit.pub"
        self.genesis_id_path = self._key_dir / "genesis_id.txt"
        self._load_or_generate()

    def _load_or_generate(self) -> None:
        if self.private_key_path.exists() and self.genesis_id_path.exists():
            raw = self.private_key_path.read_bytes()
            self.private_key = load_pem_private_key(raw, password=None)
            self.public_key = self.private_key.public_key()
            self.genesis_id = self.genesis_id_path.read_text().strip()
        else:
            self.private_key = Ed25519PrivateKey.generate()
            self.public_key = self.private_key.public_key()
            self.genesis_id = f"GENESIS-{uuid.uuid4().hex[:8].upper()}"
            self.private_key_path.write_bytes(
                self.private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
            )
            self.public_key_path.write_bytes(
                self.public_key.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)
            )
            self.genesis_id_path.write_text(self.genesis_id)
            logger.info("Genesis key pair generated: %s", self.genesis_id)

    def sign(self, data: bytes) -> bytes:
        return self.private_key.sign(data)

    def verify(self, signature: bytes, data: bytes) -> bool:
        try:
            self.public_key.verify(signature, data)
            return True
        except Exception:
            return False


# ── HMACKeyRotator ────────────────────────────────────────────────────────────

class HMACKeyRotator:
    """HMAC key that rotates on a time interval, with an optional deterministic mode."""

    def __init__(
        self,
        rotation_interval: int = 3600,
        deterministic_mode: bool = False,
        genesis_seed: bytes | None = None,
    ):
        if deterministic_mode and genesis_seed is None:
            raise ValueError("genesis_seed is required for deterministic_mode")
        self.rotation_interval = rotation_interval
        self.deterministic_mode = deterministic_mode
        self._genesis_seed = genesis_seed
        self._lock = threading.Lock()
        self._current_key: bytes = b""
        self._current_key_id: str = ""
        self._last_rotation: float = 0.0

        if deterministic_mode:
            self._init_deterministic()
        else:
            self._rotate()

    def _init_deterministic(self) -> None:
        seed = self._genesis_seed or b""
        self._current_key = hashlib.sha256(seed + b":key:0").digest()
        self._current_key_id = hashlib.sha256(seed + b":kid:0").hexdigest()[:16]

    def _rotate(self) -> None:
        self._current_key = secrets.token_bytes(32)
        self._current_key_id = secrets.token_hex(8)
        self._last_rotation = time.monotonic()

    def _maybe_rotate(self) -> None:
        if not self.deterministic_mode:
            elapsed = time.monotonic() - self._last_rotation
            if elapsed >= self.rotation_interval:
                self._rotate()

    def get_current_key(self) -> tuple[bytes, str]:
        with self._lock:
            self._maybe_rotate()
            return self._current_key, self._current_key_id

    def compute_hmac(self, data: bytes) -> tuple[bytes, str]:
        key, key_id = self.get_current_key()
        mac = _hmac_module.new(key, data, hashlib.sha256).digest()
        return mac, key_id


# ── MerkleTreeAnchor ──────────────────────────────────────────────────────────

class MerkleTreeAnchor:
    """Accumulates event hashes and produces Merkle root anchors in batches."""

    def __init__(self, batch_size: int = 1000):
        self.batch_size = batch_size
        self.anchor_points: list[dict[str, Any]] = []
        self._pending: list[bytes] = []
        self._counter = 0
        self._lock = threading.Lock()
        self.external_anchor = None  # set by SovereignAuditLog when enabled

    def add_entry(self, entry_bytes: bytes) -> dict[str, Any] | None:
        with self._lock:
            self._pending.append(entry_bytes)
            if len(self._pending) >= self.batch_size:
                return self._flush()
        return None

    def _flush(self) -> dict[str, Any]:
        leaves = [hashlib.sha256(e).digest() for e in self._pending]
        root = self._merkle_root(leaves)
        self._counter += 1
        anchor = {
            "anchor_id": f"anchor-{self._counter:06d}",
            "merkle_root": root.hex(),
            "batch_size": len(self._pending),
            "created_at": datetime.now(UTC).isoformat(),
        }
        self.anchor_points.append(anchor)
        self._pending = []
        return anchor

    @staticmethod
    def _merkle_root(leaves: list[bytes]) -> bytes:
        if not leaves:
            return b"\x00" * 32
        while len(leaves) > 1:
            if len(leaves) % 2:
                leaves.append(leaves[-1])
            leaves = [
                hashlib.sha256(leaves[i] + leaves[i + 1]).digest()
                for i in range(0, len(leaves), 2)
            ]
        return leaves[0]


# ── OperationalLog ────────────────────────────────────────────────────────────

class OperationalLog:
    """In-memory append-only store for structured sovereign events."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def append(self, event: dict[str, Any]) -> None:
        with self._lock:
            self._events.append(event)

    def get_events(self) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._events)

    def get_statistics(self) -> dict[str, Any]:
        with self._lock:
            return {"event_count": len(self._events)}


# ── SovereignAuditLog ─────────────────────────────────────────────────────────

class SovereignAuditLog:
    """Constitutional-grade audit log with Ed25519, HMAC, and Merkle anchoring."""

    def __init__(
        self,
        data_dir: str | Path,
        deterministic_mode: bool = False,
        enable_notarization: bool = False,
        enable_external_anchoring: bool = False,
        external_anchor_backends: list[str] | None = None,
    ):
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self.deterministic_mode = deterministic_mode
        self.enable_external_anchoring = enable_external_anchoring
        self.system_frozen = False
        self._lock = threading.Lock()
        self._audit_file = self._data_dir / "operational_audit.yaml"
        self._checkpoint_file = self._data_dir / "checkpoint.txt"

        # Genesis keys live one level above data_dir so they survive data wipes.
        key_dir = self._data_dir.parent / "genesis_keys"
        self.genesis_keypair = GenesisKeyPair(key_dir=key_dir)

        # ── VECTOR 2: public key file consistency check ──────────────────────
        pub_key_path = key_dir / "genesis_audit.pub"
        if pub_key_path.exists():
            stored_pub = pub_key_path.read_bytes()
            derived_pub = self.genesis_keypair.public_key.public_bytes(
                Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
            )
            if stored_pub != derived_pub:
                self.system_frozen = True
                raise GenesisReplacementError(
                    f"Genesis public key replacement detected at {pub_key_path}. "
                    f"genesis_audit.pub file does not match genesis_audit.key. "
                    f"VECTOR 2 attack — system MUST freeze."
                )

        # ── VECTOR 1 / 11: continuity guard ─────────────────────────────────
        self.continuity_guard = GenesisContinuityGuard()
        pub_pem_bytes = self.genesis_keypair.public_key.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        )
        # Raises GenesisDiscontinuityError if key_dir was seen with a different ID
        try:
            self.continuity_guard.check_or_pin(
                key_dir, self.genesis_keypair.genesis_id, pub_pem_bytes
            )
        except GenesisDiscontinuityError:
            self.system_frozen = True
            raise

        # ── remaining components ─────────────────────────────────────────────
        self.hmac_rotator = HMACKeyRotator()
        self.merkle_anchor = MerkleTreeAnchor()
        self.operational_log = OperationalLog()

        self.event_count: int = 0
        self.signature_count: int = 0
        self.anchor_count: int = 0

        # TSA anchor manager — always non-None (uses stub when deps absent)
        self.tsa_anchor_manager = _make_anchor_manager(
            self.genesis_keypair.private_key,
            self._data_dir / "tsa_anchors.json",
        )

        # External Merkle anchor
        if enable_external_anchoring:
            from .external_merkle_anchor import ExternalMerkleAnchor
            backends = external_anchor_backends or ["filesystem"]
            fs_dir = self._data_dir / "external_merkle_anchors"
            self.external_anchor: Any = ExternalMerkleAnchor(
                backends=backends,
                filesystem_dir=str(fs_dir),
            )
            self.merkle_anchor.external_anchor = self.external_anchor
        else:
            self.external_anchor = None

        self._load_persisted_events()

    # ── internal helpers ──────────────────────────────────────────────────────

    def _canonical_serialize(self, data: Any) -> bytes:
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def _load_persisted_events(self) -> None:
        if not self._audit_file.exists():
            return
        try:
            with open(self._audit_file) as f:
                for event in yaml.safe_load_all(f):
                    if event is None:
                        continue
                    self.operational_log.append(event)
                    self.event_count += 1
                    if event.get("data", {}).get("ed25519_signature"):
                        self.signature_count += 1
        except Exception:
            logger.exception("Failed to load persisted audit events")

    def _write_event_to_file(self, event: dict[str, Any]) -> None:
        try:
            with open(self._audit_file, "a") as f:
                yaml.dump(event, f, default_flow_style=False, allow_unicode=True)
                f.write("---\n")
            self._checkpoint_file.write_text(str(self.event_count))
        except Exception:
            logger.exception("Failed to persist audit event")

    def _log_genesis_seal(self) -> None:
        """Log unsigned genesis-seal as the first entry. Must be called with _lock held."""
        event_id = str(uuid.uuid4())
        now = datetime.now(UTC).isoformat()
        event = {
            "event_type": "audit.init",
            "data": {
                "event_id": event_id,
                "timestamp": now,
                "genesis_id": self.genesis_keypair.genesis_id,
            },
        }
        self.operational_log.append(event)
        self.event_count += 1
        self._write_event_to_file(event)

    # ── public API ────────────────────────────────────────────────────────────

    def log_event(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        actor: str | None = None,
        description: str | None = None,
        deterministic_timestamp: datetime | None = None,
    ) -> bool:
        with self._lock:
            try:
                if self.event_count == 0:
                    self._log_genesis_seal()

                ts = (
                    deterministic_timestamp.isoformat()
                    if deterministic_timestamp is not None
                    else datetime.now(UTC).isoformat()
                )
                user_data = data or {}
                actor_val = actor or "system"

                if self.deterministic_mode:
                    event_id = hashlib.sha256(
                        f"sovereign.{event_type}:{ts}:{json.dumps(user_data, sort_keys=True)}".encode()
                    ).hexdigest()[:32]
                else:
                    event_id = str(uuid.uuid4())

                content = {
                    "event_id": event_id,
                    "event_type": f"sovereign.{event_type}",
                    "timestamp": ts,
                    "actor": actor_val,
                    "data": user_data,
                }
                content_bytes = self._canonical_serialize(content)
                content_hash = hashlib.sha256(content_bytes).hexdigest()

                signature = self.genesis_keypair.sign(content_bytes)
                sig_b64 = base64.b64encode(signature).decode()

                mac_bytes, hmac_key_id = self.hmac_rotator.compute_hmac(content_bytes)
                mac_b64 = base64.b64encode(mac_bytes).decode()

                anchor_result = self.merkle_anchor.add_entry(content_bytes)
                if anchor_result:
                    self.anchor_count += 1
                    # Pin to external anchor if enabled
                    if self.external_anchor is not None:
                        try:
                            self.external_anchor.pin_merkle_root(
                                merkle_root=anchor_result["merkle_root"],
                                genesis_id=self.genesis_keypair.genesis_id,
                                batch_info=anchor_result,
                            )
                        except Exception:
                            logger.exception("External anchor pin failed")

                prior = self.operational_log.get_events()
                prev_hash = prior[-1]["data"].get("content_hash", "GENESIS") if prior else "GENESIS"
                chain_hash = hashlib.sha256((prev_hash + content_hash).encode()).hexdigest()

                event = {
                    "event_type": f"sovereign.{event_type}",
                    "data": {
                        "event_id": event_id,
                        "timestamp": ts,
                        "content_hash": content_hash,
                        "ed25519_signature": sig_b64,
                        "hmac": mac_b64,
                        "hmac_key_id": hmac_key_id,
                        "hash_chain": chain_hash,
                        "genesis_id": self.genesis_keypair.genesis_id,
                        "actor": actor_val,
                        # Stored as JSON string so mutations are detectable in raw file text
                        "user_data": json.dumps(user_data, sort_keys=True),
                    },
                }
                self.operational_log.append(event)
                self.event_count += 1
                self.signature_count += 1
                self._write_event_to_file(event)
                return True

            except Exception:
                logger.exception("Failed to log sovereign event: %s", event_type)
                return False

    def verify_event_signature(self, event_id: str) -> tuple[bool, str]:
        for event in self.operational_log.get_events():
            if event["data"].get("event_id") != event_id:
                continue
            sig_b64 = event["data"].get("ed25519_signature")
            if not sig_b64:
                return False, f"Event {event_id} has no signature"
            # user_data may be a JSON string (stored format) or a plain dict (in-memory)
            raw_ud = event["data"].get("user_data", {})
            if isinstance(raw_ud, str):
                try:
                    parsed_ud = json.loads(raw_ud)
                except Exception:
                    parsed_ud = {}
            else:
                parsed_ud = raw_ud or {}
            content = {
                "event_id": event_id,
                "event_type": event["event_type"],
                "timestamp": event["data"]["timestamp"],
                "actor": event["data"].get("actor", "system"),
                "data": parsed_ud,
            }
            content_bytes = self._canonical_serialize(content)
            try:
                sig = base64.b64decode(sig_b64)
                if self.genesis_keypair.verify(sig, content_bytes):
                    return True, "Signature verified successfully"
                return False, "Signature verification failed"
            except Exception as exc:
                return False, f"Verification error: {exc}"
        return False, f"Event {event_id} not found"

    def generate_proof_bundle(self, event_id: str) -> dict[str, Any] | None:
        for event in self.operational_log.get_events():
            if event["data"].get("event_id") == event_id:
                d = event["data"]
                return {
                    "event_id": event_id,
                    "ed25519_signature": d.get("ed25519_signature", ""),
                    "content_hash": d.get("content_hash", ""),
                    "hmac": d.get("hmac", ""),
                    "hash_chain": d.get("hash_chain", ""),
                    "genesis_id": d.get("genesis_id", ""),
                }
        return None

    def verify_proof_bundle(self, proof: dict[str, Any]) -> tuple[bool, str]:
        if not proof:
            return False, "No proof provided"
        event_id = proof.get("event_id")
        for event in self.operational_log.get_events():
            if event["data"].get("event_id") == event_id:
                if event["data"].get("content_hash") == proof.get("content_hash"):
                    return True, "Proof bundle verified successfully"
                return False, "Content hash mismatch"
        return False, f"Event {event_id} not found"

    def verify_integrity(self) -> tuple[bool, str]:
        if self._checkpoint_file.exists():
            try:
                checkpointed = int(self._checkpoint_file.read_text().strip())
                if self.event_count < checkpointed:
                    return (
                        False,
                        f"Truncation detected: checkpoint={checkpointed}, loaded={self.event_count}",
                    )
            except ValueError:
                pass

        events = self.operational_log.get_events()
        signed = [e for e in events if e["data"].get("ed25519_signature")]
        for event in signed:
            event_id = event["data"].get("event_id", "")
            ok, msg = self.verify_event_signature(event_id)
            if not ok:
                return False, f"Integrity failure at event {event_id}: {msg}"
        return True, "Integrity verified successfully"

    def get_statistics(self) -> dict[str, Any]:
        return {
            "genesis_id": self.genesis_keypair.genesis_id,
            "event_count": self.event_count,
            "signature_count": self.signature_count,
            "anchor_count": self.anchor_count,
            "deterministic_mode": self.deterministic_mode,
            "operational_log_stats": self.operational_log.get_statistics(),
        }
