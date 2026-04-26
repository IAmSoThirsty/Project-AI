# Memory Optimization Configuration

**Module**: `src/app/core/memory_optimization/optimization_config.py` [[src/app/core/memory_optimization/optimization_config.py]]  
**Purpose**: Policy-driven configuration for comprehensive memory optimization system  
**Classification**: Performance Configuration  
**Priority**: P1 - Performance & Scalability

---

## Overview

The Memory Optimization Configuration module provides centralized, policy-driven configuration for all memory optimization components including compression, tiered storage, deduplication, pruning, federation, streaming recall, adaptive policies, and audit logging. All parameters are tunable at runtime for performance optimization.

### Key Characteristics

- **Format**: YAML configuration with Python dataclasses
- **Components**: 8 major optimization subsystems
- **Presets**: Conservative, moderate, aggressive optimization levels
- **Validation**: Configuration validation before use
- **Runtime Tuning**: Dynamic parameter adjustment

---

## Architecture

### Configuration Hierarchy

```
OptimizationConfig (Master)
├── CompressionConfig
├── TieredStorageConfig
├── DeduplicationConfig
├── PruningConfig
├── FederationConfig
├── StreamingRecallConfig
├── AdaptivePolicyConfig
└── AuditConfig
```

### Class Structure

```python
@dataclass
class OptimizationConfig:
    """Complete optimization configuration."""
    
    # Global settings
    enabled: bool = True
    optimization_level: str = "aggressive"
    
    # Component configurations
    compression: CompressionConfig
    tiered_storage: TieredStorageConfig
    deduplication: DeduplicationConfig
    pruning: PruningConfig
    federation: FederationConfig
    streaming_recall: StreamingRecallConfig
    adaptive_policy: AdaptivePolicyConfig
    audit: AuditConfig
    
    # Feature flags
    enable_compression: bool = True
    enable_tiered_storage: bool = True
    enable_deduplication: bool = True
    enable_pruning: bool = True
    enable_federation: bool = False
    enable_streaming_recall: bool = True
    enable_adaptive_policy: bool = True
```

---

## Configuration Components

### 1. Compression Configuration

```python
@dataclass
class CompressionConfig:
    """Compression engine configuration."""
    
    enabled: bool = True
    default_strategy: str = "adaptive"  # adaptive, lz4, blosc, zlib
    compression_level: int = 6  # 1-9
    quantization_bits: int = 8  # 4, 8, 16
    sparse_threshold: float = 0.1
    graph_prune_threshold: float = 0.3
    
    # Compression targets per memory type
    episodic_compression_target: float = 0.70  # 70% reduction
    semantic_compression_target: float = 0.80  # 80% reduction
    session_compression_target: float = 0.60  # 60% reduction
    vector_compression_target: float = 0.85  # 85% reduction
```

**Purpose**: Configure memory compression strategies and targets

**Key Settings**:
- `default_strategy`: Compression algorithm selection
  - `adaptive`: Choose best algorithm per data type
  - `lz4`: Fast compression (low latency)
  - `blosc`: Optimized for numerical data
  - `zlib`: Maximum compression ratio
- `compression_level`: 1 (fast) to 9 (max compression)
- `quantization_bits`: Precision for floating-point quantization
- `*_compression_target`: Target reduction ratio (0.0-1.0)

### 2. Tiered Storage Configuration

```python
@dataclass
class TieredStorageConfig:
    """Tiered storage configuration."""
    
    enabled: bool = True
    
    # Tier capacities (bytes)
    hot_capacity_mb: int = 100
    warm_capacity_mb: int = 1024
    cold_capacity_unlimited: bool = True
    
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
    eviction_threshold: float = 0.9
    
    # Background tasks
    migration_interval_seconds: int = 300
    pruning_interval_seconds: int = 3600
    
    # Storage paths
    hot_storage_path: str = "data/memory_tiers/hot"
    warm_storage_path: str = "data/memory_tiers/warm"
    cold_storage_path: str = "data/memory_tiers/cold"
```

**Purpose**: Configure multi-tier memory storage system

**Storage Tiers**:
- **Hot**: In-memory, <1ms latency, 100MB default
- **Warm**: SSD/Fast disk, <100ms latency, 1GB default
- **Cold**: HDD/Object storage, <5s latency, unlimited

**Migration Strategy**:
- Hot→Warm: After 1 hour of inactivity
- Warm→Cold: After 24 hours of inactivity
- Cold→Warm: After 2+ accesses
- Warm→Hot: After 5+ accesses

### 3. Deduplication Configuration

```python
@dataclass
class DeduplicationConfig:
    """Deduplication engine configuration."""
    
    enabled: bool = True
    storage_path: str = "data/memory_dedup"
    enable_bloom_filter: bool = True
    bloom_filter_size: int = 1000000
    
    # Auto-save interval
    save_interval_seconds: int = 300
    
    # Compaction
    compaction_enabled: bool = True
    compaction_interval_hours: int = 24
```

**Purpose**: Configure memory deduplication to eliminate redundant data

**Key Settings**:
- `enable_bloom_filter`: Fast duplicate detection (probabilistic)
- `bloom_filter_size`: Bloom filter capacity (affects false positive rate)
- `compaction_enabled`: Periodic compaction of dedup index
- `compaction_interval_hours`: Compaction frequency

### 4. Pruning Configuration

```python
@dataclass
class PruningConfig:
    """Pruning scheduler configuration."""
    
    enabled: bool = True
    
    # Model-aware pruning
    inactive_threshold_days: int = 30
    query_history_retention_days: int = 90
    
    # Cluster pruning
    min_cluster_access_count: int = 5
    cluster_idle_threshold_days: int = 7
    
    # Entity pruning
    min_entity_confidence: float = 0.3
    entity_idle_threshold_days: int = 14
    
    # Schedule
    pruning_interval_hours: int = 6
```

**Purpose**: Configure automatic pruning of stale memory

**Pruning Strategies**:
- **Model Pruning**: Remove inactive models after N days
- **Cluster Pruning**: Remove low-access clusters
- **Entity Pruning**: Remove low-confidence entities
- **Query History**: Retain recent queries only

### 5. Federation Configuration

```python
@dataclass
class FederationConfig:
    """Federation and external storage configuration."""
    
    enabled: bool = False
    backend_type: str = "local"  # local, s3, azure, gcp
    
    # Encryption
    encryption_enabled: bool = True
    encryption_key_path: str = "config/federation_key.enc"
    
    # Data sovereignty
    data_sovereignty_region: str = "us-east-1"
    sovereignty_tags: dict[str, str] = field(default_factory=dict)
    
    # S3 configuration
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""
    
    # Cold data hydration
    hydration_cache_size_mb: int = 100
    hydration_timeout_seconds: int = 30
```

**Purpose**: Configure external storage federation for cold data

**Backend Types**:
- `local`: Local filesystem
- `s3`: Amazon S3
- `azure`: Azure Blob Storage
- `gcp`: Google Cloud Storage

**Security**:
- Encryption required by default
- Data sovereignty tags for compliance
- Per-backend access credentials

### 6. Streaming Recall Configuration

```python
@dataclass
class StreamingRecallConfig:
    """Streaming recall configuration."""
    
    enabled: bool = True
    default_strategy: str = "adaptive"  # adaptive, eager, lazy, streaming
    
    # Prefetching
    prefetch_enabled: bool = True
    prefetch_lookahead: int = 3
    
    # Attention-based loading
    attention_threshold: float = 0.5
    attention_window_size: int = 10
    
    # Hot partition search
    hot_partition_enabled: bool = True
    hot_partition_hit_rate_threshold: float = 0.8
    dynamic_db_activation: bool = True
```

**Purpose**: Configure intelligent memory recall strategies

**Recall Strategies**:
- `adaptive`: Choose best strategy per query
- `eager`: Load all data upfront
- `lazy`: Load data on-demand
- `streaming`: Stream data incrementally

**Optimizations**:
- **Prefetching**: Load next N items predictively
- **Attention-Based**: Load based on attention scores
- **Hot Partitions**: Keep frequently accessed data in memory

### 7. Adaptive Policy Configuration

```python
@dataclass
class AdaptivePolicyConfig:
    """Adaptive policy engine configuration."""
    
    enabled: bool = True
    
    # Telemetry
    telemetry_interval_seconds: int = 10
    
    # Policy tuning
    policy_tuning_interval_seconds: int = 300
    major_rebalancing_interval_hours: int = 1
    
    # Optimization targets
    memory_reduction_target: float = 0.75
    performance_impact_limit: float = 0.05
    
    # Learning rate
    policy_learning_rate: float = 0.1
    
    # Metrics thresholds
    high_memory_threshold: float = 0.85
    low_memory_threshold: float = 0.50
    high_latency_threshold_ms: float = 100.0
    low_latency_threshold_ms: float = 10.0
```

**Purpose**: Configure self-tuning adaptive optimization

**Adaptive Behavior**:
- Collects telemetry every 10 seconds
- Tunes policies every 5 minutes
- Major rebalancing every hour
- Targets 75% memory reduction with <5% performance impact

**Learning**:
- `policy_learning_rate`: How quickly policies adapt (0.0-1.0)
- Higher = faster adaptation, more volatile
- Lower = slower adaptation, more stable

### 8. Audit Configuration

```python
@dataclass
class AuditConfig:
    """Audit policy configuration."""
    
    enabled: bool = True
    
    # Critical path audit
    critical_audit_enabled: bool = True
    critical_audit_path: str = "data/audit/critical.log"
    
    # Aggregate audit
    aggregate_audit_enabled: bool = True
    aggregate_audit_path: str = "data/audit/aggregate.log"
    aggregate_interval_seconds: int = 60
    
    # Metrics audit
    metrics_audit_enabled: bool = True
    metrics_audit_path: str = "data/audit/metrics.log"
    metrics_interval_seconds: int = 300
    
    # Retention
    audit_retention_days: int = 30
    compress_old_audits: bool = True
```

**Purpose**: Configure audit logging for optimization operations

**Audit Types**:
- **Critical**: All critical operations (always logged)
- **Aggregate**: Summarized metrics (every minute)
- **Metrics**: Detailed performance metrics (every 5 minutes)

---

## Optimization Levels

### Conservative

```python
config = get_optimization_level_preset("conservative")

# Settings:
compression.compression_level = 3
tiered_storage.hot_capacity_mb = 500  # Larger hot tier
tiered_storage.migration_interval_seconds = 600  # Less frequent
pruning.inactive_threshold_days = 90  # Keep more data
adaptive_policy.policy_learning_rate = 0.05  # Slow adaptation
```

**Use Case**: Prioritize safety over optimization

### Moderate (Default)

```python
config = get_optimization_level_preset("moderate")

# Settings:
compression.compression_level = 6
tiered_storage.hot_capacity_mb = 200
tiered_storage.migration_interval_seconds = 300
pruning.inactive_threshold_days = 30
adaptive_policy.policy_learning_rate = 0.1
```

**Use Case**: Balanced optimization

### Aggressive

```python
config = get_optimization_level_preset("aggressive")

# Settings:
compression.compression_level = 9
tiered_storage.hot_capacity_mb = 100  # Smaller hot tier
tiered_storage.migration_interval_seconds = 60  # Frequent migration
pruning.inactive_threshold_days = 7  # Aggressive pruning
adaptive_policy.policy_learning_rate = 0.2  # Fast adaptation
```

**Use Case**: Maximum memory savings

---

## Core API

### Loading Configuration

```python
def load_optimization_config(config_path: str | None = None) -> OptimizationConfig:
    """Load optimization configuration from file.
    
    Args:
        config_path: Path to YAML config (default: config/memory_optimization.yaml)
    
    Returns:
        OptimizationConfig instance
    
    Behavior:
        - Returns defaults if file not found
        - Logs warnings for missing files
        - Returns defaults on parse errors
    """
```

### Saving Configuration

```python
def save_optimization_config(
    config: OptimizationConfig,
    config_path: str | None = None
):
    """Save optimization configuration to file.
    
    Args:
        config: OptimizationConfig to save
        config_path: Path to save (default: config/memory_optimization.yaml)
    """
```

### Preset Levels

```python
def get_optimization_level_preset(level: str) -> OptimizationConfig:
    """Get preset configuration for optimization level.
    
    Args:
        level: "conservative", "moderate", or "aggressive"
    
    Returns:
        OptimizationConfig with preset values
    """
```

---

## Usage Patterns

### Pattern 1: Basic Usage

```python
from src.app.core.memory_optimization.optimization_config import (
    load_optimization_config
)

# Load configuration
config = load_optimization_config()

# Access component configs
compression_config = config.compression
tiered_storage_config = config.tiered_storage

# Use in components
optimizer = MemoryOptimizer(config)
```

### Pattern 2: Preset Selection

```python
from src.app.core.memory_optimization.optimization_config import (
    get_optimization_level_preset,
    save_optimization_config
)

# Start with aggressive preset
config = get_optimization_level_preset("aggressive")

# Customize
config.compression.compression_level = 7  # Slightly less aggressive

# Save
save_optimization_config(config)
```

### Pattern 3: Runtime Tuning

```python
# Load current config
config = load_optimization_config()

# Adjust based on runtime metrics
if memory_usage > 0.9:
    # More aggressive
    config.compression.compression_level = 9
    config.pruning.inactive_threshold_days = 7
else:
    # Less aggressive
    config.compression.compression_level = 6
    config.pruning.inactive_threshold_days = 30

# Apply changes
optimizer.update_config(config)
```

---

## Configuration File Example

### Complete YAML Configuration

```yaml
enabled: true
optimization_level: aggressive

enable_compression: true
enable_tiered_storage: true
enable_deduplication: true
enable_pruning: true
enable_federation: false
enable_streaming_recall: true
enable_adaptive_policy: true

compression:
  enabled: true
  default_strategy: adaptive
  compression_level: 6
  quantization_bits: 8
  sparse_threshold: 0.1
  graph_prune_threshold: 0.3
  episodic_compression_target: 0.70
  semantic_compression_target: 0.80
  session_compression_target: 0.60
  vector_compression_target: 0.85

tiered_storage:
  enabled: true
  hot_capacity_mb: 100
  warm_capacity_mb: 1024
  cold_capacity_unlimited: true
  hot_latency_target_ms: 1.0
  warm_latency_target_ms: 100.0
  cold_latency_target_ms: 5000.0
  hot_to_warm_idle_hours: 1.0
  warm_to_cold_idle_hours: 24.0
  cold_to_warm_access_count: 2
  warm_to_hot_access_count: 5
  eviction_policy: lru
  eviction_threshold: 0.9
  migration_interval_seconds: 300
  pruning_interval_seconds: 3600
  hot_storage_path: data/memory_tiers/hot
  warm_storage_path: data/memory_tiers/warm
  cold_storage_path: data/memory_tiers/cold

# ... (remaining sections)
```

---

## Best Practices

1. **Start with Preset**: Use `get_optimization_level_preset()` as starting point
2. **Monitor Metrics**: Collect telemetry before aggressive tuning
3. **Gradual Changes**: Adjust one parameter at a time
4. **Backup Config**: Save config before major changes
5. **Test Presets**: Test all presets with representative workload
6. **Document Changes**: Comment YAML with reasons for customization
7. **Version Config**: Track config changes in version control
8. **Environment-Specific**: Different configs for dev/staging/prod
9. **Validate Targets**: Ensure compression targets are achievable
10. **Review Retention**: Adjust retention policies based on data growth

---

## Related Modules

- **Memory Pool Allocator**: Uses compression config
- **Optimization Middleware**: Uses all configs
- **Core Config**: `src/app/core/config.py` [[src/app/core/config.py]] - Application configuration
- **God-Tier Config**: `src/app/core/god_tier_config.py` [[src/app/core/god_tier_config.py]] - Multi-modal config

---

## Future Enhancements

1. **Auto-Tuning**: ML-based parameter optimization
2. **Workload Profiles**: Pre-configured profiles for common workloads
3. **A/B Testing**: Compare optimization strategies
4. **Real-Time Metrics**: Live dashboard for config impact
5. **Config Validation**: Schema validation before applying
6. **Cost Optimization**: Balance memory vs compute costs
7. **Multi-Region**: Region-specific optimization configs
8. **GPU Memory**: Support for GPU memory optimization
9. **Config History**: Track config changes over time
10. **Performance Prediction**: Predict impact before applying changes


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/memory_optimization/optimization_config.py]]
