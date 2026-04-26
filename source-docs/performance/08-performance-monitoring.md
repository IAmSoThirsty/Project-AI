# Performance Monitoring and Metrics

**Module:** `src/app/core/hydra_50_performance.py`  
**Category:** Performance Optimization  
**Last Updated:** 2025-01-27

## Overview

Project-AI provides comprehensive performance monitoring capabilities to track system health, identify bottlenecks, and optimize resource usage. The monitoring system collects metrics on caching, memory, queries, and background tasks.

## Architecture

### Monitoring Stack

```
Performance Monitoring
├── Cache Statistics (LRU, TTL)
├── Memory Monitoring (MemoryOptimizer)
├── Query Profiling (QueryOptimizer)
├── Compression Metrics (CompressionEngine)
├── Deduplication Stats (DeduplicationEngine)
├── Tier Statistics (TieredStorageManager)
└── Background Task Metrics (BackgroundTaskProcessor)
```

---

## Cache Metrics

### LRU Cache Statistics

**File:** `src/app/core/hydra_50_performance.py:99-111`

```python
def get_stats(self) -> dict[str, Any]:
    """Get cache statistics"""
    with self.lock:
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
        }
```

### Metrics Available

| Metric | Type | Description |
|--------|------|-------------|
| `size` | int | Current number of cached items |
| `max_size` | int | Maximum cache capacity |
| `hits` | int | Total cache hits |
| `misses` | int | Total cache misses |
| `hit_rate` | float | Hit ratio (0.0-1.0) |

### Usage Example

```python
from app.core.hydra_50_performance import LRUCache

cache = LRUCache(max_size=1000)

# Populate cache
for i in range(500):
    cache.put(f"key_{i}", {"data": i})

# Access some keys (hits)
for i in range(250):
    cache.get(f"key_{i}")

# Access non-existent keys (misses)
for i in range(500, 600):
    cache.get(f"key_{i}")

# Get statistics
stats = cache.get_stats()

print(f"Cache Statistics:")
print(f"  Size: {stats['size']}/{stats['max_size']}")
print(f"  Hits: {stats['hits']}")
print(f"  Misses: {stats['misses']}")
print(f"  Hit Rate: {stats['hit_rate']:.2%}")
```

**Output:**
```
Cache Statistics:
  Size: 500/1000
  Hits: 250
  Misses: 100
  Hit Rate: 71.43%
```

### Monitoring Cache Performance

```python
import time
import threading

def monitor_cache_performance(cache: LRUCache, interval_seconds: int = 60):
    """Monitor cache performance periodically"""
    last_stats = cache.get_stats()
    
    while True:
        time.sleep(interval_seconds)
        
        current_stats = cache.get_stats()
        
        # Calculate deltas
        delta_hits = current_stats['hits'] - last_stats['hits']
        delta_misses = current_stats['misses'] - last_stats['misses']
        
        if delta_hits + delta_misses > 0:
            interval_hit_rate = delta_hits / (delta_hits + delta_misses)
            
            logging.info(
                "Cache Performance (last %ds): hits=%d, misses=%d, hit_rate=%.2f%%",
                interval_seconds,
                delta_hits,
                delta_misses,
                interval_hit_rate * 100
            )
            
            # Alert on low hit rate
            if interval_hit_rate < 0.70:
                logging.warning("Low cache hit rate: %.2f%%", interval_hit_rate * 100)
        
        last_stats = current_stats

# Start monitoring thread
threading.Thread(
    target=monitor_cache_performance,
    args=(cache, 60),
    daemon=True
).start()
```

---

## Memory Metrics

### MemoryOptimizer Monitoring

**File:** `src/app/core/hydra_50_performance.py:249-258`

```python
@staticmethod
def get_memory_usage() -> dict[str, float]:
    """Get current memory usage"""
    process = psutil.Process()
    mem_info = process.memory_info()
    
    return {
        "rss_mb": mem_info.rss / 1024 / 1024,
        "vms_mb": mem_info.vms / 1024 / 1024,
        "percent": process.memory_percent(),
    }
```

### Metrics Available

| Metric | Type | Description |
|--------|------|-------------|
| `rss_mb` | float | Resident Set Size (physical RAM) in MB |
| `vms_mb` | float | Virtual Memory Size in MB |
| `percent` | float | Percentage of system memory used |

### Usage Example

```python
from app.core.hydra_50_performance import MemoryOptimizer

# Get current memory usage
mem = MemoryOptimizer.get_memory_usage()

print(f"Memory Usage:")
print(f"  RSS: {mem['rss_mb']:.1f} MB")
print(f"  VMS: {mem['vms_mb']:.1f} MB")
print(f"  System %: {mem['percent']:.2f}%")

# Check if under pressure
if MemoryOptimizer.check_memory_pressure():
    print("WARNING: System under memory pressure!")
    
    # Trigger GC
    if MemoryOptimizer.suggest_gc():
        print("Garbage collection triggered")
```

### Memory Tracking Over Time

```python
import time
from collections import deque

class MemoryTracker:
    def __init__(self, window_size: int = 60):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)
    
    def record(self):
        """Record current memory usage"""
        mem = MemoryOptimizer.get_memory_usage()
        self.history.append({
            "timestamp": time.time(),
            "rss_mb": mem["rss_mb"],
            "percent": mem["percent"]
        })
    
    def get_stats(self) -> dict:
        """Get memory statistics"""
        if not self.history:
            return {}
        
        rss_values = [entry["rss_mb"] for entry in self.history]
        percent_values = [entry["percent"] for entry in self.history]
        
        return {
            "current_rss_mb": rss_values[-1],
            "min_rss_mb": min(rss_values),
            "max_rss_mb": max(rss_values),
            "avg_rss_mb": sum(rss_values) / len(rss_values),
            "current_percent": percent_values[-1],
            "max_percent": max(percent_values),
            "samples": len(self.history)
        }

# Track memory every 10 seconds
tracker = MemoryTracker(window_size=360)  # 1 hour of data

def memory_tracking_loop():
    while True:
        tracker.record()
        time.sleep(10)

threading.Thread(target=memory_tracking_loop, daemon=True).start()

# Get stats
stats = tracker.get_stats()
print(f"Memory Stats (last {stats['samples']} samples):")
print(f"  Current: {stats['current_rss_mb']:.1f} MB")
print(f"  Average: {stats['avg_rss_mb']:.1f} MB")
print(f"  Peak: {stats['max_rss_mb']:.1f} MB")
```

---

## Query Performance Metrics

### QueryOptimizer Statistics

**File:** `src/app/core/hydra_50_performance.py:283-306`

```python
def get_slow_queries(self, threshold_ms: float = 100.0) -> dict[str, float]:
    """Get queries exceeding threshold"""
    with self.lock:
        slow_queries = {}
        for query_id, durations in self.query_stats.items():
            avg_duration = sum(durations) / len(durations)
            if avg_duration > threshold_ms:
                slow_queries[query_id] = avg_duration
        return slow_queries
```

### Usage Example

```python
from app.core.hydra_50_performance import QueryOptimizer
import time

optimizer = QueryOptimizer()

# Record query executions
def execute_tracked_query(query_id: str, query: str):
    start = time.time()
    
    # Execute query (simulated)
    result = database.execute(query)
    
    duration_ms = (time.time() - start) * 1000
    optimizer.record_query(query_id, duration_ms)
    
    return result

# Execute queries
for i in range(100):
    execute_tracked_query(f"user_query_{i % 10}", "SELECT * FROM users")
    execute_tracked_query("complex_query", "SELECT * FROM users JOIN sessions")

# Find slow queries
slow_queries = optimizer.get_slow_queries(threshold_ms=50.0)

print("Slow Queries (>50ms):")
for query_id, avg_ms in sorted(slow_queries.items(), key=lambda x: x[1], reverse=True):
    print(f"  {query_id}: {avg_ms:.2f} ms")
```

### Query Performance Report

```python
class QueryPerformanceReport:
    def __init__(self, optimizer: QueryOptimizer):
        self.optimizer = optimizer
    
    def generate_report(self) -> dict:
        """Generate comprehensive query performance report"""
        with self.optimizer.lock:
            report = {
                "total_queries": sum(len(durations) for durations in self.optimizer.query_stats.values()),
                "unique_queries": len(self.optimizer.query_stats),
                "query_details": []
            }
            
            for query_id, durations in self.optimizer.query_stats.items():
                query_report = {
                    "query_id": query_id,
                    "executions": len(durations),
                    "min_ms": min(durations),
                    "max_ms": max(durations),
                    "avg_ms": sum(durations) / len(durations),
                    "p95_ms": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 20 else max(durations),
                    "p99_ms": sorted(durations)[int(len(durations) * 0.99)] if len(durations) > 100 else max(durations),
                }
                report["query_details"].append(query_report)
            
            # Sort by average duration
            report["query_details"].sort(key=lambda x: x["avg_ms"], reverse=True)
            
            return report

# Generate report
report_generator = QueryPerformanceReport(optimizer)
report = report_generator.generate_report()

print(f"Query Performance Report:")
print(f"  Total Queries: {report['total_queries']}")
print(f"  Unique Queries: {report['unique_queries']}")
print(f"\nSlowest Queries:")

for query in report["query_details"][:5]:
    print(f"  {query['query_id']}:")
    print(f"    Executions: {query['executions']}")
    print(f"    Avg: {query['avg_ms']:.2f} ms")
    print(f"    P95: {query['p95_ms']:.2f} ms")
    print(f"    P99: {query['p99_ms']:.2f} ms")
```

---

## Compression Metrics

### CompressionEngine Statistics

**File:** `src/app/core/memory_optimization/compression_engine.py`

```python
# Statistics tracking
self.compression_stats = {
    "total_compressions": 0,
    "total_original_bytes": 0,
    "total_compressed_bytes": 0,
    "total_decompressions": 0,
    "checksum_failures": 0,
    "strategy_usage": {},
}
```

### Usage Example

```python
from app.core.memory_optimization.compression_engine import (
    CompressionEngine,
    CompressionStrategy
)

engine = CompressionEngine()

# Compress various data
for i in range(100):
    data = {"id": i, "content": "data" * 100}
    engine.compress(data)

# Get statistics
stats = engine.compression_stats

print(f"Compression Statistics:")
print(f"  Total Compressions: {stats['total_compressions']}")
print(f"  Original Size: {stats['total_original_bytes']:,} bytes")
print(f"  Compressed Size: {stats['total_compressed_bytes']:,} bytes")

overall_ratio = 1 - (stats['total_compressed_bytes'] / stats['total_original_bytes'])
print(f"  Overall Ratio: {overall_ratio:.1%}")

print(f"\nStrategy Usage:")
for strategy, count in stats['strategy_usage'].items():
    print(f"  {strategy}: {count} uses")
```

---

## Deduplication Metrics

### DeduplicationEngine Statistics

**File:** `src/app/core/memory_optimization/deduplication_engine.py`

```python
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
```

### Usage Example

```python
from app.core.memory_optimization.deduplication_engine import DeduplicationEngine

dedup = DeduplicationEngine()

# Write data with duplicates
for i in range(1000):
    data = {"shared": "content", "id": i % 100}  # 90% duplication
    dedup.write(f"key_{i}", data)

# Get statistics
stats = dedup.get_statistics()

print(f"Deduplication Statistics:")
print(f"  Total Writes: {stats['total_writes']}")
print(f"  Dedup Hits: {stats['dedup_hits']}")
print(f"  Dedup Misses: {stats['dedup_misses']}")
print(f"  Unique Contents: {stats['unique_contents']}")
print(f"  Total References: {stats['total_references']}")
print(f"  Space Saved: {stats['space_saved_bytes']:,} bytes")
print(f"  Dedup Ratio: {stats['dedup_ratio']:.1%}")
```

---

## Tiered Storage Metrics

### TieredStorageManager Statistics

**File:** `src/app/core/memory_optimization/tiered_storage.py`

```python
# Statistics tracking
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
```

### Usage Example

```python
from app.core.memory_optimization.tiered_storage import TieredStorageManager

manager = TieredStorageManager()

# Simulate access patterns
for i in range(100):
    manager.write(f"key_{i}", {"data": i})

for i in range(50):
    manager.read(f"key_{i}")  # Hot tier

# Get statistics
stats = manager.get_statistics()

print(f"Tiered Storage Statistics:")
print(f"  Total Reads: {stats['total_reads']}")
print(f"  Hot Tier Reads: {stats['hot_reads']}")
print(f"  Warm Tier Reads: {stats['warm_reads']}")
print(f"  Cold Tier Reads: {stats['cold_reads']}")
print(f"  Promotions: {stats['promotions']}")
print(f"  Demotions: {stats['demotions']}")
print(f"  Evictions: {stats['evictions']}")

hot_ratio = stats['hot_reads'] / stats['total_reads']
print(f"  Hot Tier Hit Rate: {hot_ratio:.1%}")
```

---

## Comprehensive Monitoring Dashboard

### Implementation

```python
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime

@dataclass
class PerformanceSnapshot:
    """Single performance snapshot"""
    timestamp: str
    memory: dict
    cache: dict
    queries: dict
    compression: dict
    deduplication: dict
    tiers: dict

class PerformanceMonitor:
    """Comprehensive performance monitoring"""
    
    def __init__(
        self,
        cache: LRUCache,
        optimizer: QueryOptimizer,
        compression: CompressionEngine,
        dedup: DeduplicationEngine,
        tiers: TieredStorageManager
    ):
        self.cache = cache
        self.optimizer = optimizer
        self.compression = compression
        self.dedup = dedup
        self.tiers = tiers
        
        self.snapshots = []
    
    def capture_snapshot(self) -> PerformanceSnapshot:
        """Capture current performance metrics"""
        snapshot = PerformanceSnapshot(
            timestamp=datetime.now().isoformat(),
            memory=MemoryOptimizer.get_memory_usage(),
            cache=self.cache.get_stats(),
            queries=self._get_query_summary(),
            compression=self.compression.compression_stats,
            deduplication=self.dedup.get_statistics(),
            tiers=self.tiers.get_statistics()
        )
        
        self.snapshots.append(snapshot)
        
        # Keep last 100 snapshots
        if len(self.snapshots) > 100:
            self.snapshots.pop(0)
        
        return snapshot
    
    def _get_query_summary(self) -> dict:
        """Get query performance summary"""
        with self.optimizer.lock:
            if not self.optimizer.query_stats:
                return {"total_queries": 0}
            
            all_durations = []
            for durations in self.optimizer.query_stats.values():
                all_durations.extend(durations)
            
            if not all_durations:
                return {"total_queries": 0}
            
            return {
                "total_queries": len(all_durations),
                "unique_queries": len(self.optimizer.query_stats),
                "avg_duration_ms": sum(all_durations) / len(all_durations),
                "max_duration_ms": max(all_durations),
                "min_duration_ms": min(all_durations),
            }
    
    def get_report(self) -> dict:
        """Generate comprehensive performance report"""
        if not self.snapshots:
            return {}
        
        latest = self.snapshots[-1]
        
        return {
            "timestamp": latest.timestamp,
            "memory": {
                "current_mb": latest.memory["rss_mb"],
                "percent": latest.memory["percent"],
                "pressure": MemoryOptimizer.check_memory_pressure()
            },
            "cache": {
                "hit_rate": latest.cache["hit_rate"],
                "size": latest.cache["size"],
                "utilization": latest.cache["size"] / latest.cache["max_size"]
            },
            "queries": latest.queries,
            "compression": {
                "total_compressions": latest.compression["total_compressions"],
                "overall_ratio": (
                    1 - (latest.compression["total_compressed_bytes"] / 
                         latest.compression["total_original_bytes"])
                    if latest.compression["total_original_bytes"] > 0
                    else 0
                )
            },
            "deduplication": {
                "dedup_ratio": latest.deduplication["dedup_ratio"],
                "space_saved_mb": latest.deduplication["space_saved_bytes"] / 1024 / 1024,
                "unique_contents": latest.deduplication["unique_contents"]
            },
            "tiers": {
                "hot_hit_rate": (
                    latest.tiers["hot_reads"] / latest.tiers["total_reads"]
                    if latest.tiers["total_reads"] > 0
                    else 0
                ),
                "promotions": latest.tiers["promotions"],
                "demotions": latest.tiers["demotions"]
            }
        }
    
    def print_report(self):
        """Print human-readable report"""
        report = self.get_report()
        
        if not report:
            print("No data collected yet")
            return
        
        print("=" * 60)
        print(f"PERFORMANCE REPORT - {report['timestamp']}")
        print("=" * 60)
        
        print(f"\nMEMORY:")
        print(f"  Current: {report['memory']['current_mb']:.1f} MB")
        print(f"  System %: {report['memory']['percent']:.1f}%")
        print(f"  Pressure: {'YES' if report['memory']['pressure'] else 'NO'}")
        
        print(f"\nCACHE:")
        print(f"  Hit Rate: {report['cache']['hit_rate']:.1%}")
        print(f"  Size: {report['cache']['size']}")
        print(f"  Utilization: {report['cache']['utilization']:.1%}")
        
        print(f"\nQUERIES:")
        print(f"  Total: {report['queries'].get('total_queries', 0)}")
        print(f"  Avg Duration: {report['queries'].get('avg_duration_ms', 0):.2f} ms")
        
        print(f"\nCOMPRESSION:")
        print(f"  Compressions: {report['compression']['total_compressions']}")
        print(f"  Overall Ratio: {report['compression']['overall_ratio']:.1%}")
        
        print(f"\nDEDUPLICATION:")
        print(f"  Dedup Ratio: {report['deduplication']['dedup_ratio']:.1%}")
        print(f"  Space Saved: {report['deduplication']['space_saved_mb']:.1f} MB")
        
        print(f"\nTIERED STORAGE:")
        print(f"  Hot Hit Rate: {report['tiers']['hot_hit_rate']:.1%}")
        print(f"  Promotions: {report['tiers']['promotions']}")
        print(f"  Demotions: {report['tiers']['demotions']}")
        
        print("=" * 60)

# Usage
monitor = PerformanceMonitor(
    cache=cache,
    optimizer=optimizer,
    compression=compression_engine,
    dedup=dedup_engine,
    tiers=tier_manager
)

# Capture snapshots periodically
def monitoring_loop():
    while True:
        monitor.capture_snapshot()
        time.sleep(60)  # Every minute

threading.Thread(target=monitoring_loop, daemon=True).start()

# Print report on demand
monitor.print_report()
```

**Example Output:**
```
============================================================
PERFORMANCE REPORT - 2025-01-27T15:30:00.123456
============================================================

MEMORY:
  Current: 245.3 MB
  System %: 2.8%
  Pressure: NO

CACHE:
  Hit Rate: 94.5%
  Size: 850
  Utilization: 85.0%

QUERIES:
  Total: 12450
  Avg Duration: 23.45 ms

COMPRESSION:
  Compressions: 5000
  Overall Ratio: 68.2%

DEDUPLICATION:
  Dedup Ratio: 42.3%
  Space Saved: 125.7 MB

TIERED STORAGE:
  Hot Hit Rate: 87.3%
  Promotions: 234
  Demotions: 567
============================================================
```

---

## Performance Alerts

### Alert System

```python
class PerformanceAlertSystem:
    """Alert on performance issues"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
        self.thresholds = {
            "memory_percent": 80.0,
            "cache_hit_rate": 0.70,
            "query_avg_duration_ms": 100.0,
            "hot_hit_rate": 0.75,
        }
    
    def check_alerts(self) -> list[str]:
        """Check for performance issues"""
        alerts = []
        report = self.monitor.get_report()
        
        if not report:
            return alerts
        
        # Memory alert
        if report["memory"]["percent"] > self.thresholds["memory_percent"]:
            alerts.append(
                f"HIGH MEMORY: {report['memory']['percent']:.1f}% "
                f"(threshold: {self.thresholds['memory_percent']:.1f}%)"
            )
        
        # Cache alert
        if report["cache"]["hit_rate"] < self.thresholds["cache_hit_rate"]:
            alerts.append(
                f"LOW CACHE HIT RATE: {report['cache']['hit_rate']:.1%} "
                f"(threshold: {self.thresholds['cache_hit_rate']:.1%})"
            )
        
        # Query alert
        if report["queries"].get("avg_duration_ms", 0) > self.thresholds["query_avg_duration_ms"]:
            alerts.append(
                f"SLOW QUERIES: {report['queries']['avg_duration_ms']:.1f} ms "
                f"(threshold: {self.thresholds['query_avg_duration_ms']:.1f} ms)"
            )
        
        # Tier alert
        if report["tiers"]["hot_hit_rate"] < self.thresholds["hot_hit_rate"]:
            alerts.append(
                f"LOW HOT TIER HIT RATE: {report['tiers']['hot_hit_rate']:.1%} "
                f"(threshold: {self.thresholds['hot_hit_rate']:.1%})"
            )
        
        return alerts

# Usage
alert_system = PerformanceAlertSystem(monitor)

def alert_check_loop():
    while True:
        alerts = alert_system.check_alerts()
        
        for alert in alerts:
            logging.warning("PERFORMANCE ALERT: %s", alert)
        
        time.sleep(300)  # Check every 5 minutes

threading.Thread(target=alert_check_loop, daemon=True).start()
```

---

## Best Practices

### 1. Monitor Continuously

```python
# Start monitoring on application startup
monitor = PerformanceMonitor(...)
threading.Thread(target=monitoring_loop, daemon=True).start()
```

### 2. Set Appropriate Thresholds

```python
# Based on your system and requirements
thresholds = {
    "memory_percent": 80.0,  # 80% memory usage
    "cache_hit_rate": 0.80,  # 80% hit rate
    "query_avg_duration_ms": 50.0,  # 50ms avg query time
}
```

### 3. Log Performance Metrics

```python
# Log snapshots for historical analysis
snapshot = monitor.capture_snapshot()
logging.info("Performance: %s", json.dumps(asdict(snapshot), indent=2))
```

### 4. Export Metrics

```python
# Export to Prometheus, Grafana, etc.
def export_to_prometheus():
    report = monitor.get_report()
    # Format for Prometheus
    metrics = f"""
# HELP memory_usage_mb Current memory usage in MB
# TYPE memory_usage_mb gauge
memory_usage_mb {report['memory']['current_mb']}

# HELP cache_hit_rate Cache hit rate
# TYPE cache_hit_rate gauge
cache_hit_rate {report['cache']['hit_rate']}
    """
    return metrics
```

---

## Related Documentation

- **[01-caching-strategies.md](01-caching-strategies.md)** - Cache implementation
- **[03-memory-optimization.md](03-memory-optimization.md)** - Memory management
- **[06-lazy-loading.md](06-lazy-loading.md)** - Query optimization

---

## References

- **Cache Stats:** `src/app/core/hydra_50_performance.py:99-111`
- **Memory Stats:** `src/app/core/hydra_50_performance.py:249-258`
- **Query Stats:** `src/app/core/hydra_50_performance.py:297-305`
- **Compression:** `src/app/core/memory_optimization/compression_engine.py`
- **Deduplication:** `src/app/core/memory_optimization/deduplication_engine.py`
- **Tiered Storage:** `src/app/core/memory_optimization/tiered_storage.py`
