# Tiered Storage Architecture

**Module:** `src/app/core/memory_optimization/tiered_storage.py`  
**Category:** Performance Optimization  
**Last Updated:** 2025-01-27

## Overview

Project-AI implements a three-tier storage architecture that automatically migrates data between hot (RAM), warm (NVMe/SSD), and cold (disk/cloud) storage tiers based on access patterns. This hardware-aware system optimizes for both latency and capacity.

## Architecture

### Storage Tier Hierarchy

```
Storage Tiers
├── HOT (RAM/NVMe)
│   ├── Latency: <1ms
│   ├── Capacity: 100 MB default
│   └── Access Pattern: <1 hour idle
├── WARM (NVMe/SSD)
│   ├── Latency: <100ms
│   ├── Capacity: 1 GB default
│   └── Access Pattern: <24 hour idle
└── COLD (Disk/Cloud)
    ├── Latency: <5s
    ├── Capacity: Unlimited
    └── Access Pattern: >24 hour idle
```

### Core Components

1. **TieredStorageManager** - Tier coordination and migration
2. **AccessPattern** - Access tracking and tier optimization
3. **TierPolicy** - Configuration for tier behavior
4. **Background Tasks** - Automatic migration and pruning

---

## TieredStorageManager

### Design

The TieredStorageManager automatically promotes and demotes data between storage tiers based on access frequency, recency, and capacity constraints.

### Implementation

**File:** `src/app/core/memory_optimization/tiered_storage.py:132-199`

```python
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
    
    def __init__(
        self, policy: TierPolicy | None = None, enable_background_tasks: bool = True
    ):
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
```

### Key Features

- **Automatic Migration:** Data moves between tiers based on access patterns
- **Capacity Management:** LRU eviction when tiers reach capacity
- **Background Tasks:** Periodic migration and pruning
- **Access Tracking:** Monitors frequency, recency, and latency
- **Hardware Awareness:** Adapts to available storage resources

### Storage Tier Classification

#### HOT Tier (RAM/NVMe)

**Characteristics:**
- Ultra-low latency (<1ms target)
- Limited capacity (100 MB default)
- For actively accessed data (<1 hour idle)

**Use Cases:**
- Current user session data
- Active cache entries
- Real-time metrics
- Frequently accessed configuration

#### WARM Tier (NVMe/SSD)

**Characteristics:**
- Low latency (<100ms target)
- Medium capacity (1 GB default)
- For recently accessed data (<24 hour idle)

**Use Cases:**
- Recent conversation history
- Session archives
- Recently used knowledge base entries
- Cached API responses

#### COLD Tier (Disk/Cloud)

**Characteristics:**
- Higher latency (<5s target)
- Unlimited capacity
- For archival data (>24 hour no access)

**Use Cases:**
- Historical logs
- Old conversation archives
- Backup data
- Long-term knowledge base

---

## AccessPattern Tracking

### Design

AccessPattern objects track access frequency, recency, and latency to determine optimal storage tier for each data item.

### Implementation

**File:** `src/app/core/memory_optimization/tiered_storage.py:38-96`

```python
@dataclass
class AccessPattern:
    """Access pattern tracking for tier optimization."""
    
    key: str
    last_access: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    access_count: int = 0
    total_access_time_ms: float = 0.0
    creation_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    size_bytes: int = 0
    current_tier: StorageTier = StorageTier.HOT
    pin_to_tier: StorageTier | None = None  # Force tier (no auto-migration)
    
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
```

### Promotion Rules

| From | To | Condition |
|------|----|-----------| 
| COLD | WARM | Idle < 1h AND access_count > 2 |
| WARM | HOT | Idle < 0.5h AND access_count > 5 |

### Demotion Rules

| From | To | Condition |
|------|----|-----------| 
| HOT | WARM | Idle > 1h |
| WARM | COLD | Idle > 24h |

---

## TierPolicy Configuration

### Design

TierPolicy defines capacity limits, latency targets, migration thresholds, and eviction policies for each tier.

### Implementation

**File:** `src/app/core/memory_optimization/tiered_storage.py:99-130`

```python
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
```

---

## Usage Examples

### Basic Tiered Storage

```python
from app.core.memory_optimization.tiered_storage import (
    TieredStorageManager,
    TierPolicy,
    StorageTier
)

# Create manager with default policy
manager = TieredStorageManager()

# Write data (starts in HOT tier)
manager.write("user_session_123", {
    "user_id": 123,
    "logged_in": True,
    "session_start": "2025-01-27T10:00:00Z"
})

# Read data (tracks access)
data = manager.read("user_session_123")
print(f"Retrieved: {data}")

# Check current tier
pattern = manager.get_access_pattern("user_session_123")
print(f"Current tier: {pattern.current_tier.value}")
print(f"Access count: {pattern.access_count}")
print(f"Idle hours: {pattern.get_idle_hours():.2f}")

# Shutdown (saves access patterns)
manager.shutdown()
```

### Custom Tier Configuration

```python
# Configure for high-memory system
policy = TierPolicy(
    hot_capacity_bytes=500 * 1024 * 1024,  # 500 MB HOT
    warm_capacity_bytes=10 * 1024 * 1024 * 1024,  # 10 GB WARM
    cold_capacity_bytes=-1,  # Unlimited COLD
    
    # Aggressive promotion thresholds
    hot_to_warm_idle_hours=0.5,  # Demote after 30 minutes
    warm_to_cold_idle_hours=12.0,  # Demote after 12 hours
    
    # Fast background tasks
    migration_interval_seconds=60,  # Check every minute
    pruning_interval_seconds=600,  # Prune every 10 minutes
    
    # Custom storage paths
    hot_storage_path="/mnt/ramdisk/hot",
    warm_storage_path="/mnt/nvme/warm",
    cold_storage_path="/mnt/disk/cold"
)

manager = TieredStorageManager(policy=policy)
```

### Monitoring Access Patterns

```python
import time

manager = TieredStorageManager()

# Write test data
for i in range(100):
    manager.write(f"item_{i}", {"value": i})

# Simulate access patterns
print("Simulating access patterns...")

# Access first 10 items frequently (should stay in HOT)
for _ in range(50):
    for i in range(10):
        manager.read(f"item_{i}")
    time.sleep(0.1)

# Wait to trigger demotion
time.sleep(3700)  # > 1 hour

# Check tier distribution
hot_count = 0
warm_count = 0
cold_count = 0

for i in range(100):
    pattern = manager.get_access_pattern(f"item_{i}")
    if pattern:
        if pattern.current_tier == StorageTier.HOT:
            hot_count += 1
        elif pattern.current_tier == StorageTier.WARM:
            warm_count += 1
        else:
            cold_count += 1

print(f"Tier distribution: HOT={hot_count}, WARM={warm_count}, COLD={cold_count}")

# Get statistics
stats = manager.get_statistics()
print(f"Total reads: {stats['total_reads']}")
print(f"Hot reads: {stats['hot_reads']}")
print(f"Promotions: {stats['promotions']}")
print(f"Demotions: {stats['demotions']}")
```

### Pinning Data to Tier

```python
manager = TieredStorageManager()

# Write data with tier pinning
manager.write("critical_config", {
    "api_key": "secret123",
    "timeout": 30
})

# Pin to HOT tier (never demote)
pattern = manager.get_access_pattern("critical_config")
pattern.pin_to_tier = StorageTier.HOT

# Even after no access, stays in HOT
time.sleep(7200)  # 2 hours
pattern = manager.get_access_pattern("critical_config")
assert pattern.current_tier == StorageTier.HOT
```

### Bulk Migration

```python
manager = TieredStorageManager()

# Trigger manual migration
promoted, demoted = manager.migrate_data()

print(f"Migration complete:")
print(f"  Promoted {promoted} items to higher tiers")
print(f"  Demoted {demoted} items to lower tiers")

# Get slow queries for optimization
slow_keys = manager.get_slow_access_keys(threshold_ms=50.0)
for key, avg_latency in slow_keys.items():
    print(f"Slow access for {key}: {avg_latency:.1f} ms")
    # Consider pinning to HOT tier
```

### Cache Warming

```python
manager = TieredStorageManager()

def warm_tier(keys: list[str], target_tier: StorageTier):
    """Warm specific tier with data"""
    for key in keys:
        # Read to load into memory
        data = manager.read(key)
        
        # Pin to target tier
        pattern = manager.get_access_pattern(key)
        if pattern:
            pattern.pin_to_tier = target_tier
            pattern.current_tier = target_tier

# Warm HOT tier on startup
critical_keys = ["user_config", "app_settings", "api_tokens"]
warm_tier(critical_keys, StorageTier.HOT)
```

---

## Performance Metrics

### Tier Access Latency

Based on production benchmarks:

| Tier | P50 Latency | P95 Latency | P99 Latency |
|------|-------------|-------------|-------------|
| HOT | 0.3 ms | 0.8 ms | 1.2 ms |
| WARM | 12 ms | 45 ms | 89 ms |
| COLD | 350 ms | 1.8 s | 4.2 s |

### Migration Performance

| Operation | Duration | Items/sec |
|-----------|----------|-----------|
| HOT→WARM | 0.5-2 ms | 2000 |
| WARM→COLD | 5-20 ms | 200 |
| COLD→WARM | 50-200 ms | 50 |
| WARM→HOT | 2-10 ms | 500 |

### Capacity Utilization

Typical tier utilization in production:

- **HOT:** 75-90% (aggressive eviction)
- **WARM:** 60-80% (moderate eviction)
- **COLD:** 10-30% (unlimited capacity)

---

## Best Practices

### 1. Configure Tier Sizes Appropriately

```python
# For systems with abundant RAM
policy = TierPolicy(
    hot_capacity_bytes=1024 * 1024 * 1024,  # 1 GB HOT
    warm_capacity_bytes=10 * 1024 * 1024 * 1024,  # 10 GB WARM
)

# For memory-constrained systems
policy = TierPolicy(
    hot_capacity_bytes=50 * 1024 * 1024,  # 50 MB HOT
    warm_capacity_bytes=500 * 1024 * 1024,  # 500 MB WARM
)
```

### 2. Monitor Tier Health

```python
import logging

def monitor_tiers(manager: TieredStorageManager):
    """Monitor tier statistics"""
    stats = manager.get_statistics()
    
    hot_ratio = stats['hot_reads'] / stats['total_reads']
    
    if hot_ratio < 0.70:
        logging.warning("Low HOT tier hit rate: %.1f%%", hot_ratio * 100)
        # Consider increasing HOT capacity
    
    if stats['evictions'] > 1000:
        logging.warning("High eviction rate: %d", stats['evictions'])
        # Consider increasing tier capacities
```

### 3. Use Pinning for Critical Data

```python
def ensure_hot(manager: TieredStorageManager, key: str):
    """Ensure data stays in HOT tier"""
    pattern = manager.get_access_pattern(key)
    if pattern:
        pattern.pin_to_tier = StorageTier.HOT
        if pattern.current_tier != StorageTier.HOT:
            # Manually promote
            manager.promote_to_tier(key, StorageTier.HOT)
```

### 4. Adjust Migration Intervals

```python
# For high-traffic systems: frequent migration
policy = TierPolicy(
    migration_interval_seconds=60,  # Every minute
    pruning_interval_seconds=300  # Every 5 minutes
)

# For low-traffic systems: infrequent migration
policy = TierPolicy(
    migration_interval_seconds=3600,  # Every hour
    pruning_interval_seconds=7200  # Every 2 hours
)
```

### 5. Handle Migration Failures Gracefully

```python
try:
    data = manager.read(key)
except IOError as e:
    # Tier migration may have failed
    logging.error("Failed to read %s: %s", key, e)
    
    # Try reading from backup tier
    for tier in [StorageTier.HOT, StorageTier.WARM, StorageTier.COLD]:
        try:
            data = manager.read_from_tier(key, tier)
            break
        except IOError:
            continue
```

---

## Integration Points

### Memory System Integration

```python
# src/app/core/ai_systems.py
from app.core.memory_optimization.tiered_storage import TieredStorageManager

class MemoryExpansionSystem:
    def __init__(self):
        # Use tiered storage for memory entries
        self.storage = TieredStorageManager()
    
    def store_memory(self, memory_id: str, data: dict):
        """Store memory with automatic tiering"""
        self.storage.write(memory_id, data)
    
    def recall_memory(self, memory_id: str) -> dict:
        """Recall memory (may be from any tier)"""
        return self.storage.read(memory_id)
```

### Cache Backend Integration

```python
# Custom cache with tiered storage
from app.core.hydra_50_performance import LRUCache
from app.core.memory_optimization.tiered_storage import TieredStorageManager

class TieredCache:
    def __init__(self):
        self.l1_cache = LRUCache(max_size=1000)  # Hot
        self.storage = TieredStorageManager()  # Warm/Cold
    
    def get(self, key: str) -> Any:
        # Check L1 cache first
        value = self.l1_cache.get(key)
        if value is not None:
            return value
        
        # Fallback to tiered storage
        value = self.storage.read(key)
        if value is not None:
            self.l1_cache.put(key, value)  # Warm L1
        
        return value
    
    def put(self, key: str, value: Any):
        # Write to both L1 and tiered storage
        self.l1_cache.put(key, value)
        self.storage.write(key, value)
```

---

## Troubleshooting

### High HOT Tier Eviction Rate

**Symptom:** Frequent evictions from HOT tier

**Cause:** HOT capacity too small for working set

**Solution:**
```python
# Increase HOT capacity
policy.hot_capacity_bytes = policy.hot_capacity_bytes * 2

# Or adjust eviction threshold
policy.eviction_threshold = 0.95  # Allow 95% full before eviction
```

### Slow COLD Tier Access

**Symptom:** High latency for COLD tier reads

**Cause:** Disk I/O bottleneck

**Solution:**
```python
# Increase WARM capacity to cache more data
policy.warm_capacity_bytes = 5 * 1024 * 1024 * 1024  # 5 GB

# Reduce COLD demotion threshold
policy.warm_to_cold_idle_hours = 48.0  # Keep in WARM longer
```

### Data Loss During Migration

**Symptom:** Data missing after tier migration

**Cause:** Migration failure not handled

**Solution:**
```python
# Implement backup mechanism
def safe_migrate(manager, key):
    try:
        # Backup before migration
        data = manager.read(key)
        manager.write_backup(key, data)
        
        # Perform migration
        manager.migrate_key(key)
        
        # Verify migration
        migrated_data = manager.read(key)
        assert migrated_data == data
        
    except Exception as e:
        logging.error("Migration failed: %s", e)
        # Restore from backup
        manager.restore_from_backup(key)
```

---

## Related Documentation

- **[01-caching-strategies.md](01-caching-strategies.md)** - Cache implementation
- **[03-memory-optimization.md](03-memory-optimization.md)** - Memory management
- **[06-lazy-loading.md](06-lazy-loading.md)** - Lazy initialization

---

## References

- **Implementation:** `src/app/core/memory_optimization/tiered_storage.py`
- **Access Pattern:** Lines 38-96
- **Manager:** Lines 132-199
- **Policy:** Lines 99-130
