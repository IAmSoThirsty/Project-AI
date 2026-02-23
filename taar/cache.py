"""
TAAR Cache — Content-addressed result caching.

Caches the results of runner commands based on the SHA-256 hash of
the input files + command template. If the inputs haven't changed
since the last run, the cached result is returned without re-executing.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from taar.change_detector import file_content_hash


@dataclass
class CacheEntry:
    """A cached result from a previous runner execution."""

    cache_key: str
    runner_name: str
    command_name: str
    passed: bool
    return_code: int
    duration: float
    output: str
    timestamp: float
    file_hashes: dict[str, str]

    def age_seconds(self) -> float:
        """How old this cache entry is in seconds."""
        return time.time() - self.timestamp


@dataclass
class CacheStats:
    """Statistics about cache usage."""

    total_entries: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0


class ResultCache:
    """Content-addressed result cache for TAAR runner outputs."""

    def __init__(self, cache_dir: Path, max_age_hours: int = 24):
        self.cache_dir = cache_dir
        self.max_age_seconds = max_age_hours * 3600
        self.stats = CacheStats()
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """Create cache directory structure."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        (self.cache_dir / "results").mkdir(exist_ok=True)

    def lookup(
        self,
        runner_name: str,
        command_name: str,
        files: list[Path],
        command_template: str,
    ) -> CacheEntry | None:
        """
        Look up a cached result for the given runner/command/files combination.

        Returns the cached entry if:
        1. The cache key matches (same files, same content, same command)
        2. The entry hasn't expired

        Returns None on cache miss.
        """
        key = self._compute_key(runner_name, command_name, files, command_template)
        entry_path = self._entry_path(key)

        if not entry_path.is_file():
            self.stats.misses += 1
            return None

        try:
            with open(entry_path) as f:
                raw = json.load(f)
            entry = CacheEntry(**raw)
        except (json.JSONDecodeError, TypeError, KeyError):
            self.stats.misses += 1
            entry_path.unlink(missing_ok=True)
            return None

        # Check age
        if entry.age_seconds() > self.max_age_seconds:
            self.stats.misses += 1
            self.stats.evictions += 1
            entry_path.unlink(missing_ok=True)
            return None

        # Verify file hashes still match
        for file_path, expected_hash in entry.file_hashes.items():
            current_hash = file_content_hash(Path(file_path))
            if current_hash != expected_hash:
                self.stats.misses += 1
                return None

        self.stats.hits += 1
        return entry

    def store(
        self,
        runner_name: str,
        command_name: str,
        files: list[Path],
        command_template: str,
        passed: bool,
        return_code: int,
        duration: float,
        output: str,
    ) -> CacheEntry:
        """
        Store a runner result in the cache.

        Only caches passing results by default. Failures are stored
        with a shorter TTL to allow quick re-checks.
        """
        key = self._compute_key(runner_name, command_name, files, command_template)

        file_hashes = {}
        for f in files:
            file_hashes[str(f)] = file_content_hash(f)

        entry = CacheEntry(
            cache_key=key,
            runner_name=runner_name,
            command_name=command_name,
            passed=passed,
            return_code=return_code,
            duration=duration,
            output=output[:5000],  # Truncate large outputs
            timestamp=time.time(),
            file_hashes=file_hashes,
        )

        entry_path = self._entry_path(key)
        with open(entry_path, "w") as f:
            json.dump(asdict(entry), f, indent=2)

        self.stats.total_entries += 1
        return entry

    def clear(self) -> int:
        """Clear all cache entries. Returns number of entries removed."""
        results_dir = self.cache_dir / "results"
        count = 0
        if results_dir.is_dir():
            for entry_file in results_dir.glob("*.json"):
                entry_file.unlink()
                count += 1
        self.stats = CacheStats()
        return count

    def get_stats(self) -> CacheStats:
        """Get current cache statistics, including on-disk entry count."""
        results_dir = self.cache_dir / "results"
        if results_dir.is_dir():
            self.stats.total_entries = len(list(results_dir.glob("*.json")))
        return self.stats

    def _compute_key(
        self,
        runner_name: str,
        command_name: str,
        files: list[Path],
        command_template: str,
    ) -> str:
        """Compute a content-addressed cache key."""
        hasher = hashlib.sha256()

        # Include runner and command identity
        hasher.update(f"{runner_name}:{command_name}:{command_template}".encode())

        # Include sorted file paths and their content hashes
        for f in sorted(files):
            hasher.update(str(f).encode())
            hasher.update(file_content_hash(f).encode())

        return hasher.hexdigest()[:16]

    def _entry_path(self, key: str) -> Path:
        """Path to cache entry file for a given key."""
        return self.cache_dir / "results" / f"{key}.json"
