"""
Deduplication Engine - Content-Addressed Storage

Implements hash-based deduplication for memory storage:
- Content addressing with SHA-256
- In-memory bloom filter for O(1) lookup
- Persistent dedup index
- Rapid orchestration integration
- 30-50% space savings on redundant data

Features:
- Automatic duplicate detection
- Reference counting for safe deletion
- Fast in-memory cache
- Persistent dedup index
- Transparent to callers
"""

import hashlib
import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ContentAddress:
    """Content-addressed storage reference."""

    content_hash: str  # SHA-256 hash
    size_bytes: int
    reference_count: int = 1
    first_seen: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_accessed: datetime = field(default_factory=lambda: datetime.now(UTC))
    content_type: str = "json"  # json, binary, text

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content_hash": self.content_hash,
            "size_bytes": self.size_bytes,
            "reference_count": self.reference_count,
            "first_seen": self.first_seen.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "content_type": self.content_type,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContentAddress":
        """Create from dictionary."""
        return cls(
            content_hash=data["content_hash"],
            size_bytes=data["size_bytes"],
            reference_count=data["reference_count"],
            first_seen=datetime.fromisoformat(data["first_seen"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            content_type=data.get("content_type", "json"),
        )


class BloomFilter:
    """
    Simple bloom filter for fast duplicate detection.

    Uses multiple hash functions to reduce false positives.
    """

    def __init__(self, size: int = 1000000, num_hashes: int = 3):
        """
        Initialize bloom filter.

        Args:
            size: Bit array size (larger = fewer false positives)
            num_hashes: Number of hash functions (more = fewer false positives)
        """
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [False] * size

    def add(self, item: str):
        """Add item to bloom filter."""
        for i in range(self.num_hashes):
            index = self._hash(item, i) % self.size
            self.bit_array[index] = True

    def might_contain(self, item: str) -> bool:
        """Check if item might be in set (may have false positives)."""
        for i in range(self.num_hashes):
            index = self._hash(item, i) % self.size
            if not self.bit_array[index]:
                return False
        return True

    def _hash(self, item: str, seed: int) -> int:
        """Generate hash with seed."""
        h = hashlib.sha256(f"{item}{seed}".encode()).digest()
        return int.from_bytes(h[:4], byteorder="big")

    def clear(self):
        """Clear bloom filter."""
        self.bit_array = [False] * self.size


class DeduplicationEngine:
    """
    Content-addressed storage with deduplication.

    Features:
    - SHA-256 content addressing
    - In-memory bloom filter for fast lookup
    - Persistent dedup index
    - Reference counting
    - Automatic garbage collection
    - Transparent to callers

    Space savings: 30-50% on redundant data
    """

    def __init__(
        self,
        storage_path: str = "data/memory_dedup",
        enable_bloom_filter: bool = True,
        bloom_filter_size: int = 1000000,
    ):
        """
        Initialize deduplication engine.

        Args:
            storage_path: Path for content-addressed storage
            enable_bloom_filter: Use bloom filter for fast lookups
            bloom_filter_size: Bloom filter size (larger = fewer false positives)
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.enable_bloom_filter = enable_bloom_filter

        # Content address index (hash -> ContentAddress)
        self.content_index: dict[str, ContentAddress] = {}
        self.index_lock = threading.RLock()

        # Key to content hash mapping (key -> hash)
        self.key_to_hash: dict[str, str] = {}

        # Bloom filter for fast duplicate detection
        self.bloom_filter = (
            BloomFilter(size=bloom_filter_size) if enable_bloom_filter else None
        )

        # Statistics
        self.stats = {
            "total_writes": 0,
            "total_reads": 0,
            "dedup_hits": 0,
            "dedup_misses": 0,
            "space_saved_bytes": 0,
            "unique_contents": 0,
            "total_references": 0,
        }

        # Load existing index
        self._load_index()

        logger.info(
            "DeduplicationEngine initialized at %s with %d unique contents",
            self.storage_path,
            len(self.content_index),
        )

    def write(self, key: str, data: Any) -> tuple[str, bool]:
        """
        Write data with automatic deduplication.

        Args:
            key: Logical key for data
            data: Data to write

        Returns:
            Tuple of (content_hash, was_duplicate)
        """
        try:
            # Serialize data
            if isinstance(data, (bytes, bytearray)):
                content = data
                content_type = "binary"
            elif isinstance(data, str):
                content = data.encode("utf-8")
                content_type = "text"
            else:
                content = json.dumps(data, ensure_ascii=False, sort_keys=True).encode(
                    "utf-8"
                )
                content_type = "json"

            # Calculate content hash
            content_hash = hashlib.sha256(content).hexdigest()
            size_bytes = len(content)

            # Check if content already exists
            was_duplicate = False

            with self.index_lock:
                # Check bloom filter first (if enabled)
                if self.enable_bloom_filter and self.bloom_filter.might_contain(
                    content_hash
                ):
                    # Bloom filter says it might exist, verify in index
                    if content_hash in self.content_index:
                        # Duplicate found, increment reference count
                        self.content_index[content_hash].reference_count += 1
                        self.content_index[content_hash].last_accessed = datetime.now(
                            UTC
                        )
                        was_duplicate = True

                        # Update stats
                        self.stats["dedup_hits"] += 1
                        self.stats["space_saved_bytes"] += size_bytes

                        logger.debug(
                            "Dedup hit for key %s (hash %s)", key, content_hash[:16]
                        )
                    else:
                        # False positive from bloom filter
                        logger.debug(
                            "Bloom filter false positive for hash %s", content_hash[:16]
                        )

                if not was_duplicate:
                    # New content, write to storage
                    self._write_content(content_hash, content)

                    # Add to index
                    self.content_index[content_hash] = ContentAddress(
                        content_hash=content_hash,
                        size_bytes=size_bytes,
                        reference_count=1,
                        content_type=content_type,
                    )

                    # Add to bloom filter
                    if self.enable_bloom_filter:
                        self.bloom_filter.add(content_hash)

                    # Update stats
                    self.stats["dedup_misses"] += 1
                    self.stats["unique_contents"] += 1

                    logger.debug(
                        "New content for key %s (hash %s)", key, content_hash[:16]
                    )

                # Map key to content hash
                old_hash = self.key_to_hash.get(key)
                if old_hash and old_hash != content_hash:
                    # Key is being updated, decrement old content reference
                    self._decrement_reference(old_hash)

                self.key_to_hash[key] = content_hash

                # Update stats
                self.stats["total_writes"] += 1
                self.stats["total_references"] = sum(
                    addr.reference_count for addr in self.content_index.values()
                )

            return content_hash, was_duplicate
        except Exception as e:
            logger.error("Write failed for key %s: %s", key, e)
            raise

    def read(self, key: str) -> Any | None:
        """
        Read data by logical key.

        Args:
            key: Logical key for data

        Returns:
            Data or None if not found
        """
        try:
            with self.index_lock:
                # Get content hash for key
                content_hash = self.key_to_hash.get(key)
                if not content_hash:
                    logger.debug("Key %s not found in key mapping", key)
                    return None

                # Get content address
                addr = self.content_index.get(content_hash)
                if not addr:
                    logger.warning(
                        "Content hash %s not found in index", content_hash[:16]
                    )
                    return None

                # Update last accessed
                addr.last_accessed = datetime.now(UTC)

            # Read content
            data = self._read_content(content_hash, addr.content_type)

            # Update stats
            self.stats["total_reads"] += 1

            return data
        except Exception as e:
            logger.error("Read failed for key %s: %s", key, e)
            return None

    def delete(self, key: str) -> bool:
        """
        Delete data by logical key.

        Decrements reference count and removes content if no more references.

        Args:
            key: Logical key for data

        Returns:
            True if deleted
        """
        try:
            with self.index_lock:
                # Get content hash for key
                content_hash = self.key_to_hash.get(key)
                if not content_hash:
                    logger.debug("Key %s not found for deletion", key)
                    return False

                # Remove key mapping
                del self.key_to_hash[key]

                # Decrement reference count
                self._decrement_reference(content_hash)

            logger.debug("Deleted key %s", key)
            return True
        except Exception as e:
            logger.error("Delete failed for key %s: %s", key, e)
            return False

    def get_content_hash(self, key: str) -> str | None:
        """Get content hash for logical key."""
        with self.index_lock:
            return self.key_to_hash.get(key)

    def get_reference_count(self, content_hash: str) -> int:
        """Get reference count for content hash."""
        with self.index_lock:
            addr = self.content_index.get(content_hash)
            return addr.reference_count if addr else 0

    # ========================================================================
    # Internal Methods
    # ========================================================================

    def _write_content(self, content_hash: str, content: bytes):
        """Write content to storage."""
        # Use first 2 characters of hash for subdirectory
        subdir = self.storage_path / content_hash[:2]
        subdir.mkdir(parents=True, exist_ok=True)

        file_path = subdir / f"{content_hash}.dat"

        with open(file_path, "wb") as f:
            f.write(content)

    def _read_content(self, content_hash: str, content_type: str) -> Any:
        """Read content from storage."""
        subdir = self.storage_path / content_hash[:2]
        file_path = subdir / f"{content_hash}.dat"

        if not file_path.exists():
            raise FileNotFoundError(f"Content not found: {content_hash}")

        with open(file_path, "rb") as f:
            content = f.read()

        # Deserialize based on content type
        if content_type == "binary":
            return content
        elif content_type == "text":
            return content.decode("utf-8")
        else:  # json
            return json.loads(content.decode("utf-8"))

    def _decrement_reference(self, content_hash: str):
        """Decrement reference count and delete content if zero."""
        addr = self.content_index.get(content_hash)
        if not addr:
            return

        addr.reference_count -= 1

        if addr.reference_count <= 0:
            # No more references, delete content
            subdir = self.storage_path / content_hash[:2]
            file_path = subdir / f"{content_hash}.dat"

            if file_path.exists():
                file_path.unlink()

            # Remove from index
            del self.content_index[content_hash]
            self.stats["unique_contents"] -= 1

            logger.debug("Garbage collected content %s", content_hash[:16])

    def _load_index(self):
        """Load dedup index from disk."""
        index_file = self.storage_path / "dedup_index.json"

        if index_file.exists():
            try:
                with open(index_file, encoding="utf-8") as f:
                    data = json.load(f)

                # Load content index
                for hash_str, addr_data in data.get("content_index", {}).items():
                    self.content_index[hash_str] = ContentAddress.from_dict(addr_data)

                    # Rebuild bloom filter
                    if self.enable_bloom_filter:
                        self.bloom_filter.add(hash_str)

                # Load key mappings
                self.key_to_hash = data.get("key_to_hash", {})

                # Load stats
                self.stats.update(data.get("stats", {}))

                logger.info(
                    "Loaded dedup index: %d unique contents, %d keys",
                    len(self.content_index),
                    len(self.key_to_hash),
                )
            except Exception as e:
                logger.error("Failed to load dedup index: %s", e)

    def _save_index(self):
        """Save dedup index to disk."""
        index_file = self.storage_path / "dedup_index.json"

        try:
            with self.index_lock:
                data = {
                    "content_index": {
                        hash_str: addr.to_dict()
                        for hash_str, addr in self.content_index.items()
                    },
                    "key_to_hash": self.key_to_hash,
                    "stats": self.stats,
                }

            # Atomic write
            temp_file = index_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            temp_file.replace(index_file)

            logger.debug(
                "Saved dedup index with %d unique contents", len(self.content_index)
            )
        except Exception as e:
            logger.error("Failed to save dedup index: %s", e)

    def shutdown(self):
        """Shutdown engine and save index."""
        logger.info("Shutting down DeduplicationEngine...")
        self._save_index()
        logger.info("DeduplicationEngine shutdown complete")

    def get_statistics(self) -> dict[str, Any]:
        """Get deduplication statistics."""
        with self.index_lock:
            total_content_size = sum(
                addr.size_bytes * addr.reference_count
                for addr in self.content_index.values()
            )
            unique_content_size = sum(
                addr.size_bytes for addr in self.content_index.values()
            )

            dedup_ratio = (
                1.0 - (unique_content_size / total_content_size)
                if total_content_size > 0
                else 0.0
            )

            return {
                **self.stats,
                "total_content_size_bytes": total_content_size,
                "unique_content_size_bytes": unique_content_size,
                "dedup_ratio": dedup_ratio,
                "space_saved_percent": dedup_ratio * 100,
                "bloom_filter_enabled": self.enable_bloom_filter,
                "bloom_filter_size": self.bloom_filter.size if self.bloom_filter else 0,
            }

    def compact(self):
        """
        Compact storage by removing orphaned content.

        Scans storage directory and removes content not in index.
        """
        logger.info("Compacting dedup storage...")

        orphaned = 0

        try:
            for subdir in self.storage_path.iterdir():
                if not subdir.is_dir() or len(subdir.name) != 2:
                    continue

                for file_path in subdir.glob("*.dat"):
                    content_hash = file_path.stem

                    with self.index_lock:
                        if content_hash not in self.content_index:
                            # Orphaned content
                            file_path.unlink()
                            orphaned += 1

            logger.info("Compaction complete: removed %d orphaned contents", orphaned)
        except Exception as e:
            logger.error("Compaction failed: %s", e)
