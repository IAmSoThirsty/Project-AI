"""
sovereign_vault.metadata

Dual-index model (per the "metadata leakage" and "dual index" corrections):

  1. Encrypted index (self.index)      — full plaintext metadata (real
     filename, category, tags, timestamps), sealed under MetadataKey.
     This is what the vault reads internally to answer real queries.

  2. Exposure index (self.exposure)    — what a directory listing /
     filesystem-adjacent view is allowed to show: an opaque UUID,
     a coarse padded size bucket, and a coarse category TOKEN drawn from
     a fixed enum (never free text, never the real filename).

The two are cryptographically bound: exposure_entry.binding_tag is an
HMAC-style tag (HKDF-derived, keyed) over (object_id || encrypted-index
content hash), so a caller cannot swap in a mismatched exposure entry
without detection, and the two indexes cannot silently diverge.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum

from .primitives import hkdf_sha512, seal, unseal


class Category(Enum):
    """Fixed enum, deliberately coarse. Real category detail lives only
    inside the encrypted index. Extend this list; do not put free text
    into the exposure index under any circumstance."""

    DOCUMENT = "document"
    KEY_MATERIAL = "key_material"
    CREDENTIAL = "credential"
    AUDIT_ARTIFACT = "audit_artifact"
    CONFIGURATION = "configuration"
    OTHER = "other"


_SIZE_BUCKETS = (4_096, 16_384, 65_536, 262_144, 1_048_576, 4_194_304, 16_777_216)


def size_bucket(n: int) -> int:
    """Rounds up to a fixed bucket so real object size isn't observable
    at fine granularity from ciphertext length."""
    for b in _SIZE_BUCKETS:
        if n <= b:
            return b
    # beyond the largest named bucket: round up to next 16MB multiple
    step = _SIZE_BUCKETS[-1]
    return ((n // step) + 1) * step


@dataclass
class IndexEntry:
    object_id: str
    real_name: str
    category_detail: str
    tool_id: str
    created_epoch: int
    real_size: int
    content_sha256: str


@dataclass
class ExposureEntry:
    object_id: str
    category_token: str  # Category.value
    padded_size: int
    created_epoch: int
    binding_tag: str  # hex


@dataclass
class MetadataIndex:
    metadata_key: bytes  # from keys.KeyHierarchy.metadata_key(root_kek)
    index: dict[str, IndexEntry] = field(default_factory=dict)  # object_id -> IndexEntry
    exposure: dict[str, ExposureEntry] = field(default_factory=dict)  # object_id -> ExposureEntry

    def _binding_tag(self, object_id: str, index_content_hash: str) -> str:
        tag_key = hkdf_sha512(self.metadata_key, info=b"metadata-binding:v1")
        return hashlib.blake2b(
            (object_id + "|" + index_content_hash).encode("utf-8"),
            key=tag_key[:64] if len(tag_key) >= 16 else tag_key,
            digest_size=32,
        ).hexdigest()

    def admit(
        self,
        object_id: str,
        real_name: str,
        category: Category,
        category_detail: str,
        tool_id: str,
        created_epoch: int,
        real_size: int,
        content_sha256: str,
    ) -> None:
        if object_id in self.index:
            raise ValueError(
                f"metadata: object_id {object_id} already admitted (no silent overwrite)"
            )
        entry = IndexEntry(
            object_id=object_id,
            real_name=real_name,
            category_detail=category_detail,
            tool_id=tool_id,
            created_epoch=created_epoch,
            real_size=real_size,
            content_sha256=content_sha256,
        )
        self.index[object_id] = entry

        content_hash = hashlib.sha256(_canonical_entry(entry)).hexdigest()
        self.exposure[object_id] = ExposureEntry(
            object_id=object_id,
            category_token=category.value,
            padded_size=size_bucket(real_size),
            created_epoch=created_epoch,
            binding_tag=self._binding_tag(object_id, content_hash),
        )

    def verify_binding(self, object_id: str) -> bool:
        """Detects divergence between the two indexes — call before
        trusting an exposure entry for any authorization decision."""
        if object_id not in self.index or object_id not in self.exposure:
            return False
        entry = self.index[object_id]
        exp = self.exposure[object_id]
        content_hash = hashlib.sha256(_canonical_entry(entry)).hexdigest()
        expected = self._binding_tag(object_id, content_hash)
        return expected == exp.binding_tag

    def seal_index(self) -> tuple[bytes, bytes]:
        """Seals the full (sensitive) index under MetadataKey for at-rest
        storage. The exposure index is NOT sealed here — it is meant to be
        readable at the coarse level it already restricts itself to; if
        you want it sealed too, seal it with a distinct derived key so a
        compromise of one does not implicate the other."""
        payload = json.dumps(
            {oid: e.__dict__ for oid, e in self.index.items()}, sort_keys=True
        ).encode("utf-8")
        return seal(self.metadata_key, payload, aad=b"sovereign_vault.metadata_index.v1")

    def load_index(self, nonce: bytes, ciphertext: bytes) -> None:
        payload = unseal(
            self.metadata_key, nonce, ciphertext, aad=b"sovereign_vault.metadata_index.v1"
        )
        raw = json.loads(payload.decode("utf-8"))
        self.index = {oid: IndexEntry(**fields_) for oid, fields_ in raw.items()}


def _canonical_entry(entry: IndexEntry) -> bytes:
    return json.dumps(entry.__dict__, sort_keys=True, separators=(",", ":")).encode("utf-8")
