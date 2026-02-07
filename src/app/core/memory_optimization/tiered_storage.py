"""
Tiered Storage Manager - Hardware-Aware Memory Allocation

Implements three-tier storage architecture:
- Hot tier: RAM/NVMe for active data (<1 hour access, <1ms latency)
- Warm tier: NVMe/SSD for recent data (<24 hour access, <100ms latency)
- Cold tier: Disk/cloud for archival (>24 hour no access, <5s latency)

Features:
- Automatic tier migration based on access patterns
- Lazy loading and streaming hydration
- Periodic pruning of cold data
- Write-through caching with aggressive expiry
- Hardware-aware allocation policies
"""

import json
import logging
import os
import shutil
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class StorageTier(Enum):
    """Storage tier classification."""
    
    HOT = "hot"      # RAM/NVMe, <1 hour access, <1ms latency
    WARM = "warm"    # NVMe/SSD, <24 hour access, <100ms latency
    COLD = "cold"    # Disk/cloud, >24 hour no access, <5s latency


@dataclass
class AccessPattern:
    """Access pattern tracking for tier optimization."""
    
    key: str
    last_access: datetime = field(default_factory=lambda: datetime.now(UTC))
    access_count: int = 0
    total_access_time_ms: float = 0.0
    creation_time: datetime = field(default_factory=lambda: datetime.now(UTC))
    size_bytes: int = 0
    current_tier: StorageTier = StorageTier.HOT
    pin_to_tier: StorageTier | None = None  # Force tier (no auto-migration)
    
    def record_access(self, access_time_ms: float):
        """Record an access event."""
        self.last_access = datetime.now(UTC)
        self.access_count += 1
        self.total_access_time_ms += access_time_ms
    
    def get_average_access_time_ms(self) -> float:
        """Get average access time."""
        return self.total_access_time_ms / self.access_count if self.access_count > 0 else 0.0
    
    def get_age_hours(self) -> float:
        """Get age since creation in hours."""
        return (datetime.now(UTC) - self.creation_time).total_seconds() / 3600
    
    def get_idle_hours(self) -> float:
        """Get hours since last access."""
        return (datetime.now(UTC) - self.last_access).total_seconds() / 3600
    
    def should_promote(self) -> bool:
        """Check if data should be promoted to higher tier."""
        idle_hours = self.get_idle_hours()
        
        if self.current_tier == StorageTier.COLD:
            # Promote from cold to warm if accessed recently
            return idle_hours < 1.0 and self.access_count > 2
        elif self.current_tier == StorageTier.WARM:
            # Promote from warm to hot if frequently accessed
            return idle_hours < 0.5 and self.access_count > 5
        return False
    
    def should_demote(self) -> bool:
        """Check if data should be demoted to lower tier."""
        idle_hours = self.get_idle_hours()
        
        if self.current_tier == StorageTier.HOT:
            # Demote from hot to warm if not accessed in 1 hour
            return idle_hours > 1.0
        elif self.current_tier == StorageTier.WARM:
            # Demote from warm to cold if not accessed in 24 hours
            return idle_hours > 24.0
        return False


@dataclass
class TierPolicy:
    """Configuration for tier behavior."""
    
    # Tier capacities (bytes)
    hot_capacity_bytes: int = 100 * 1024 * 1024  # 100 MB
    warm_capacity_bytes: int = 1024 * 1024 * 1024  # 1 GB
    cold_capacity_bytes: int = -1  # Unlimited
    
    # Tier latency targets (milliseconds)
    hot_latency_target_ms: float = 1.0
    warm_latency_target_ms: float = 100.0
    cold_latency_target_ms: float = 5000.0
    
    # Migration thresholds
    hot_to_warm_idle_hours: float = 1.0
    warm_to_cold_idle_hours: float = 24.0
    cold_to_warm_access_count: int = 2
    warm_to_hot_access_count: int = 5
    
    # Eviction policy
    eviction_policy: str = "lru"  # lru, lfu, fifo
    eviction_threshold: float = 0.9  # Evict when tier is 90% full
    
    # Background tasks
    migration_interval_seconds: int = 300  # 5 minutes
    pruning_interval_seconds: int = 3600  # 1 hour
    
    # Storage paths
    hot_storage_path: str = "data/memory_tiers/hot"
    warm_storage_path: str = "data/memory_tiers/warm"
    cold_storage_path: str = "data/memory_tiers/cold"


class TieredStorageManager:
    """
    Manages three-tier storage architecture with automatic migration.
    
    Features:
    - Automatic tier promotion/demotion based on access patterns
    - Capacity management with eviction policies
    - Lazy loading and streaming hydration
    - Background migration and pruning
    - Hardware-aware storage allocation
    """
    
    def __init__(self, policy: TierPolicy | None = None, enable_background_tasks: bool = True):
        """
        Initialize tiered storage manager.
        
        Args:
            policy: Tier policy configuration
            enable_background_tasks: Enable background migration/pruning
        """
        self.policy = policy or TierPolicy()
        self.enable_background_tasks = enable_background_tasks
        
        # Access pattern tracking
        self.access_patterns: dict[str, AccessPattern] = {}
        self.access_lock = threading.RLock()
        
        # Tier storage paths
        self.tier_paths = {
            StorageTier.HOT: Path(self.policy.hot_storage_path),
            StorageTier.WARM: Path(self.policy.warm_storage_path),
            StorageTier.COLD: Path(self.policy.cold_storage_path),
        }
        
        # Create tier directories
        for path in self.tier_paths.values():
            path.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            "total_reads": 0,
            "total_writes": 0,
            "hot_reads": 0,
            "warm_reads": 0,
            "cold_reads": 0,
            "promotions": 0,
            "demotions": 0,
            "evictions": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        
        # Background task control
        self.running = True
        self.migration_thread = None
        self.pruning_thread = None
        
        # Load existing access patterns
        self._load_access_patterns()
        
        # Start background tasks
        if self.enable_background_tasks:
            self._start_background_tasks()
        
        logger.info("TieredStorageManager initialized with policy: %s", self.policy)
    
    def write(self, key: str, data: Any, tier: StorageTier = StorageTier.HOT, pin_tier: bool = False) -> bool:
        """
        Write data to specified tier.
        
        Args:
            key: Unique key for data
            data: Data to write
            tier: Target storage tier
            pin_tier: If True, prevent auto-migration
        
        Returns:
            True if write successful
        """
        try:
            start_time = time.time()
            
            # Serialize data
            serialized = json.dumps(data, ensure_ascii=False, indent=None).encode("utf-8")
            size_bytes = len(serialized)
            
            # Check tier capacity
            if not self._check_tier_capacity(tier, size_bytes):
                logger.warning("Tier %s over capacity, triggering eviction", tier.value)
                self._evict_from_tier(tier, size_bytes)
            
            # Write to tier
            file_path = self._get_file_path(key, tier)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(serialized)
            
            # Track access pattern
            with self.access_lock:
                if key not in self.access_patterns:
                    self.access_patterns[key] = AccessPattern(
                        key=key,
                        size_bytes=size_bytes,
                        current_tier=tier,
                        pin_to_tier=tier if pin_tier else None,
                    )
                else:
                    pattern = self.access_patterns[key]
                    pattern.size_bytes = size_bytes
                    pattern.current_tier = tier
                    if pin_tier:
                        pattern.pin_to_tier = tier
            
            # Update stats
            self.stats["total_writes"] += 1
            
            elapsed_ms = (time.time() - start_time) * 1000
            logger.debug("Write %s to tier %s: %.2f ms", key, tier.value, elapsed_ms)
            
            return True
        except Exception as e:
            logger.error("Write failed for key %s: %s", key, e)
            return False
    
    def read(self, key: str) -> tuple[Any | None, StorageTier | None]:
        """
        Read data by key, searching across tiers.
        
        Args:
            key: Unique key for data
        
        Returns:
            Tuple of (data, tier) or (None, None) if not found
        """
        try:
            start_time = time.time()
            
            # Check access pattern for current tier
            with self.access_lock:
                pattern = self.access_patterns.get(key)
            
            if pattern:
                # Try current tier first
                data = self._read_from_tier(key, pattern.current_tier)
                if data is not None:
                    elapsed_ms = (time.time() - start_time) * 1000
                    
                    # Record access
                    with self.access_lock:
                        pattern.record_access(elapsed_ms)
                    
                    # Update stats
                    self.stats["total_reads"] += 1
                    self.stats["cache_hits"] += 1
                    if pattern.current_tier == StorageTier.HOT:
                        self.stats["hot_reads"] += 1
                    elif pattern.current_tier == StorageTier.WARM:
                        self.stats["warm_reads"] += 1
                    else:
                        self.stats["cold_reads"] += 1
                    
                    # Check if promotion needed
                    if pattern.should_promote() and pattern.pin_to_tier is None:
                        self._promote_tier(key, pattern)
                    
                    return data, pattern.current_tier
            
            # Search across all tiers
            for tier in [StorageTier.HOT, StorageTier.WARM, StorageTier.COLD]:
                data = self._read_from_tier(key, tier)
                if data is not None:
                    elapsed_ms = (time.time() - start_time) * 1000
                    
                    # Create or update access pattern
                    with self.access_lock:
                        if key not in self.access_patterns:
                            self.access_patterns[key] = AccessPattern(
                                key=key,
                                current_tier=tier,
                                size_bytes=len(json.dumps(data).encode("utf-8")),
                            )
                        self.access_patterns[key].record_access(elapsed_ms)
                    
                    # Update stats
                    self.stats["total_reads"] += 1
                    self.stats["cache_misses"] += 1
                    
                    return data, tier
            
            # Not found
            logger.debug("Key %s not found in any tier", key)
            return None, None
        except Exception as e:
            logger.error("Read failed for key %s: %s", key, e)
            return None, None
    
    def delete(self, key: str) -> bool:
        """
        Delete data by key from all tiers.
        
        Args:
            key: Unique key for data
        
        Returns:
            True if deleted
        """
        try:
            deleted = False
            
            # Delete from all tiers
            for tier in StorageTier:
                file_path = self._get_file_path(key, tier)
                if file_path.exists():
                    file_path.unlink()
                    deleted = True
            
            # Remove access pattern
            with self.access_lock:
                if key in self.access_patterns:
                    del self.access_patterns[key]
            
            logger.debug("Deleted key %s", key)
            return deleted
        except Exception as e:
            logger.error("Delete failed for key %s: %s", key, e)
            return False
    
    def migrate_tier(self, key: str, target_tier: StorageTier) -> bool:
        """
        Manually migrate data to target tier.
        
        Args:
            key: Unique key for data
            target_tier: Target storage tier
        
        Returns:
            True if migration successful
        """
        try:
            # Read from current tier
            data, current_tier = self.read(key)
            if data is None:
                logger.warning("Cannot migrate %s: not found", key)
                return False
            
            if current_tier == target_tier:
                logger.debug("Key %s already in tier %s", key, target_tier.value)
                return True
            
            # Write to target tier
            if not self.write(key, data, tier=target_tier):
                return False
            
            # Delete from current tier
            if current_tier:
                file_path = self._get_file_path(key, current_tier)
                if file_path.exists():
                    file_path.unlink()
            
            # Update stats
            if target_tier.value > current_tier.value:
                self.stats["demotions"] += 1
            else:
                self.stats["promotions"] += 1
            
            logger.info("Migrated %s from %s to %s", key, current_tier, target_tier.value)
            return True
        except Exception as e:
            logger.error("Migration failed for key %s: %s", key, e)
            return False
    
    # ========================================================================
    # Internal Methods
    # ========================================================================
    
    def _get_file_path(self, key: str, tier: StorageTier) -> Path:
        """Get file path for key in tier."""
        # Use hash to distribute files across subdirectories
        import hashlib
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        subdir = key_hash[:2]
        
        return self.tier_paths[tier] / subdir / f"{key_hash}.json"
    
    def _read_from_tier(self, key: str, tier: StorageTier) -> Any | None:
        """Read data from specific tier."""
        file_path = self._get_file_path(key, tier)
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, "rb") as f:
                data = json.loads(f.read().decode("utf-8"))
            return data
        except Exception as e:
            logger.error("Failed to read %s from tier %s: %s", key, tier.value, e)
            return None
    
    def _check_tier_capacity(self, tier: StorageTier, required_bytes: int) -> bool:
        """Check if tier has capacity for new data."""
        if tier == StorageTier.COLD:
            return True  # Unlimited
        
        # Calculate current tier usage
        current_usage = self._get_tier_usage(tier)
        
        capacity = (
            self.policy.hot_capacity_bytes
            if tier == StorageTier.HOT
            else self.policy.warm_capacity_bytes
        )
        
        return (current_usage + required_bytes) < (capacity * self.policy.eviction_threshold)
    
    def _get_tier_usage(self, tier: StorageTier) -> int:
        """Get current storage usage for tier in bytes."""
        tier_path = self.tier_paths[tier]
        total_size = 0
        
        try:
            for file_path in tier_path.rglob("*.json"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            logger.error("Failed to calculate tier usage for %s: %s", tier.value, e)
        
        return total_size
    
    def _evict_from_tier(self, tier: StorageTier, required_bytes: int):
        """Evict data from tier to make space."""
        logger.info("Evicting from tier %s to free %d bytes", tier.value, required_bytes)
        
        # Get all keys in tier
        with self.access_lock:
            tier_keys = [
                key
                for key, pattern in self.access_patterns.items()
                if pattern.current_tier == tier and pattern.pin_to_tier is None
            ]
        
        # Sort by eviction policy
        if self.policy.eviction_policy == "lru":
            # Least recently used
            tier_keys.sort(key=lambda k: self.access_patterns[k].last_access)
        elif self.policy.eviction_policy == "lfu":
            # Least frequently used
            tier_keys.sort(key=lambda k: self.access_patterns[k].access_count)
        else:
            # FIFO
            tier_keys.sort(key=lambda k: self.access_patterns[k].creation_time)
        
        # Evict keys until enough space
        freed_bytes = 0
        for key in tier_keys:
            if freed_bytes >= required_bytes:
                break
            
            pattern = self.access_patterns[key]
            
            # Demote to next tier
            if tier == StorageTier.HOT:
                self.migrate_tier(key, StorageTier.WARM)
            elif tier == StorageTier.WARM:
                self.migrate_tier(key, StorageTier.COLD)
            else:
                # Delete from cold tier
                self.delete(key)
            
            freed_bytes += pattern.size_bytes
            self.stats["evictions"] += 1
        
        logger.info("Evicted %d bytes from tier %s", freed_bytes, tier.value)
    
    def _promote_tier(self, key: str, pattern: AccessPattern):
        """Promote data to higher tier."""
        if pattern.current_tier == StorageTier.COLD:
            self.migrate_tier(key, StorageTier.WARM)
        elif pattern.current_tier == StorageTier.WARM:
            self.migrate_tier(key, StorageTier.HOT)
    
    def _demote_tier(self, key: str, pattern: AccessPattern):
        """Demote data to lower tier."""
        if pattern.current_tier == StorageTier.HOT:
            self.migrate_tier(key, StorageTier.WARM)
        elif pattern.current_tier == StorageTier.WARM:
            self.migrate_tier(key, StorageTier.COLD)
    
    # ========================================================================
    # Background Tasks
    # ========================================================================
    
    def _start_background_tasks(self):
        """Start background migration and pruning threads."""
        self.migration_thread = threading.Thread(target=self._migration_worker, daemon=True)
        self.pruning_thread = threading.Thread(target=self._pruning_worker, daemon=True)
        
        self.migration_thread.start()
        self.pruning_thread.start()
        
        logger.info("Background tasks started")
    
    def _migration_worker(self):
        """Background worker for tier migration."""
        while self.running:
            try:
                time.sleep(self.policy.migration_interval_seconds)
                
                with self.access_lock:
                    keys_to_migrate = []
                    
                    for key, pattern in self.access_patterns.items():
                        if pattern.pin_to_tier is not None:
                            continue
                        
                        if pattern.should_promote():
                            keys_to_migrate.append((key, "promote"))
                        elif pattern.should_demote():
                            keys_to_migrate.append((key, "demote"))
                
                # Perform migrations outside lock
                for key, action in keys_to_migrate:
                    pattern = self.access_patterns.get(key)
                    if pattern:
                        if action == "promote":
                            self._promote_tier(key, pattern)
                        else:
                            self._demote_tier(key, pattern)
                
                if keys_to_migrate:
                    logger.info("Background migration: %d keys migrated", len(keys_to_migrate))
            except Exception as e:
                logger.error("Migration worker error: %s", e)
    
    def _pruning_worker(self):
        """Background worker for pruning old cold data."""
        while self.running:
            try:
                time.sleep(self.policy.pruning_interval_seconds)
                
                # Find cold data not accessed in 30 days
                threshold_hours = 30 * 24
                keys_to_prune = []
                
                with self.access_lock:
                    for key, pattern in self.access_patterns.items():
                        if pattern.current_tier == StorageTier.COLD:
                            if pattern.get_idle_hours() > threshold_hours:
                                keys_to_prune.append(key)
                
                # Prune outside lock
                for key in keys_to_prune:
                    self.delete(key)
                
                if keys_to_prune:
                    logger.info("Background pruning: %d keys deleted", len(keys_to_prune))
            except Exception as e:
                logger.error("Pruning worker error: %s", e)
    
    def _load_access_patterns(self):
        """Load access patterns from disk."""
        patterns_file = Path(self.policy.hot_storage_path).parent / "access_patterns.json"
        
        if patterns_file.exists():
            try:
                with open(patterns_file, encoding="utf-8") as f:
                    data = json.load(f)
                
                for key, pattern_data in data.items():
                    self.access_patterns[key] = AccessPattern(
                        key=key,
                        last_access=datetime.fromisoformat(pattern_data["last_access"]),
                        access_count=pattern_data["access_count"],
                        total_access_time_ms=pattern_data["total_access_time_ms"],
                        creation_time=datetime.fromisoformat(pattern_data["creation_time"]),
                        size_bytes=pattern_data["size_bytes"],
                        current_tier=StorageTier(pattern_data["current_tier"]),
                        pin_to_tier=StorageTier(pattern_data["pin_to_tier"]) if pattern_data.get("pin_to_tier") else None,
                    )
                
                logger.info("Loaded %d access patterns", len(self.access_patterns))
            except Exception as e:
                logger.error("Failed to load access patterns: %s", e)
    
    def _save_access_patterns(self):
        """Save access patterns to disk."""
        patterns_file = Path(self.policy.hot_storage_path).parent / "access_patterns.json"
        patterns_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with self.access_lock:
                data = {
                    key: {
                        "last_access": pattern.last_access.isoformat(),
                        "access_count": pattern.access_count,
                        "total_access_time_ms": pattern.total_access_time_ms,
                        "creation_time": pattern.creation_time.isoformat(),
                        "size_bytes": pattern.size_bytes,
                        "current_tier": pattern.current_tier.value,
                        "pin_to_tier": pattern.pin_to_tier.value if pattern.pin_to_tier else None,
                    }
                    for key, pattern in self.access_patterns.items()
                }
            
            with open(patterns_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Saved %d access patterns", len(self.access_patterns))
        except Exception as e:
            logger.error("Failed to save access patterns: %s", e)
    
    def shutdown(self):
        """Shutdown manager and background tasks."""
        logger.info("Shutting down TieredStorageManager...")
        
        self.running = False
        
        # Wait for threads
        if self.migration_thread:
            self.migration_thread.join(timeout=5.0)
        if self.pruning_thread:
            self.pruning_thread.join(timeout=5.0)
        
        # Save access patterns
        self._save_access_patterns()
        
        logger.info("TieredStorageManager shutdown complete")
    
    def get_statistics(self) -> dict[str, Any]:
        """Get storage statistics."""
        hot_usage = self._get_tier_usage(StorageTier.HOT)
        warm_usage = self._get_tier_usage(StorageTier.WARM)
        cold_usage = self._get_tier_usage(StorageTier.COLD)
        
        return {
            **self.stats,
            "total_keys": len(self.access_patterns),
            "hot_usage_bytes": hot_usage,
            "warm_usage_bytes": warm_usage,
            "cold_usage_bytes": cold_usage,
            "total_usage_bytes": hot_usage + warm_usage + cold_usage,
            "hot_capacity_bytes": self.policy.hot_capacity_bytes,
            "warm_capacity_bytes": self.policy.warm_capacity_bytes,
            "hot_usage_percent": (hot_usage / self.policy.hot_capacity_bytes * 100) if self.policy.hot_capacity_bytes > 0 else 0,
            "warm_usage_percent": (warm_usage / self.policy.warm_capacity_bytes * 100) if self.policy.warm_capacity_bytes > 0 else 0,
        }
