"""
Optimization Configuration - Policy-Driven Memory Management

Centralized configuration for all memory optimization policies:
- Compression strategies and levels
- Tier retention policies
- Hardware allocation policies
- Pruning schedules
- Deduplication settings
- Adaptive tuning parameters
- Audit policies

All parameters are tunable at runtime for performance optimization.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


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


@dataclass
class TieredStorageConfig:
    """Tiered storage configuration."""

    enabled: bool = True

    # Tier capacities (bytes)
    hot_capacity_mb: int = 100  # 100 MB
    warm_capacity_mb: int = 1024  # 1 GB
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
    eviction_threshold: float = 0.9  # 90% full triggers eviction

    # Background tasks
    migration_interval_seconds: int = 300  # 5 minutes
    pruning_interval_seconds: int = 3600  # 1 hour

    # Storage paths
    hot_storage_path: str = "data/memory_tiers/hot"
    warm_storage_path: str = "data/memory_tiers/warm"
    cold_storage_path: str = "data/memory_tiers/cold"


@dataclass
class DeduplicationConfig:
    """Deduplication engine configuration."""

    enabled: bool = True
    storage_path: str = "data/memory_dedup"
    enable_bloom_filter: bool = True
    bloom_filter_size: int = 1000000

    # Auto-save interval
    save_interval_seconds: int = 300  # 5 minutes

    # Compaction
    compaction_enabled: bool = True
    compaction_interval_hours: int = 24


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
    pruning_interval_hours: int = 6  # Every 6 hours


@dataclass
class FederationConfig:
    """Federation and external storage configuration."""

    enabled: bool = False  # Disabled by default

    # Backend types: local, s3, azure, gcp
    backend_type: str = "local"

    # Encryption
    encryption_enabled: bool = True
    encryption_key_path: str = "config/federation_key.enc"

    # Data sovereignty
    data_sovereignty_region: str = "us-east-1"
    sovereignty_tags: dict[str, str] = field(default_factory=dict)

    # S3 configuration (if backend_type == "s3")
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    s3_access_key_id: str = ""
    s3_secret_access_key: str = ""

    # Cold data hydration
    hydration_cache_size_mb: int = 100
    hydration_timeout_seconds: int = 30


@dataclass
class StreamingRecallConfig:
    """Streaming recall configuration."""

    enabled: bool = True

    # Recall strategies
    default_strategy: str = "adaptive"  # adaptive, eager, lazy, streaming

    # Prefetching
    prefetch_enabled: bool = True
    prefetch_lookahead: int = 3  # Prefetch next 3 items

    # Attention-based loading
    attention_threshold: float = 0.5
    attention_window_size: int = 10

    # Hot partition search
    hot_partition_enabled: bool = True
    hot_partition_hit_rate_threshold: float = 0.8
    dynamic_db_activation: bool = True


@dataclass
class AdaptivePolicyConfig:
    """Adaptive policy engine configuration."""

    enabled: bool = True

    # Telemetry
    telemetry_interval_seconds: int = 10  # Collect every 10 seconds

    # Policy tuning
    policy_tuning_interval_seconds: int = 300  # Tune every 5 minutes
    major_rebalancing_interval_hours: int = 1  # Rebalance every hour

    # Optimization targets
    memory_reduction_target: float = 0.75  # 75% reduction
    performance_impact_limit: float = 0.05  # <5% performance impact

    # Learning rate
    policy_learning_rate: float = 0.1  # How fast policies adapt

    # Metrics thresholds
    high_memory_threshold: float = 0.85  # 85% of capacity
    low_memory_threshold: float = 0.50  # 50% of capacity
    high_latency_threshold_ms: float = 100.0
    low_latency_threshold_ms: float = 10.0


@dataclass
class AuditConfig:
    """Audit policy configuration."""

    enabled: bool = True

    # Critical path audit (always logged)
    critical_audit_enabled: bool = True
    critical_audit_path: str = "data/audit/critical.log"

    # Aggregate audit (lossy, summarized)
    aggregate_audit_enabled: bool = True
    aggregate_audit_path: str = "data/audit/aggregate.log"
    aggregate_interval_seconds: int = 60  # Aggregate every minute

    # Metrics audit
    metrics_audit_enabled: bool = True
    metrics_audit_path: str = "data/audit/metrics.log"
    metrics_interval_seconds: int = 300  # Log metrics every 5 minutes

    # Retention
    audit_retention_days: int = 30
    compress_old_audits: bool = True


@dataclass
class OptimizationConfig:
    """Complete optimization configuration."""

    # Global settings
    enabled: bool = True
    optimization_level: str = "aggressive"  # conservative, moderate, aggressive

    # Component configurations
    compression: CompressionConfig = field(default_factory=CompressionConfig)
    tiered_storage: TieredStorageConfig = field(default_factory=TieredStorageConfig)
    deduplication: DeduplicationConfig = field(default_factory=DeduplicationConfig)
    pruning: PruningConfig = field(default_factory=PruningConfig)
    federation: FederationConfig = field(default_factory=FederationConfig)
    streaming_recall: StreamingRecallConfig = field(
        default_factory=StreamingRecallConfig
    )
    adaptive_policy: AdaptivePolicyConfig = field(default_factory=AdaptivePolicyConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)

    # Feature flags
    enable_compression: bool = True
    enable_tiered_storage: bool = True
    enable_deduplication: bool = True
    enable_pruning: bool = True
    enable_federation: bool = False  # Disabled by default
    enable_streaming_recall: bool = True
    enable_adaptive_policy: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "enabled": self.enabled,
            "optimization_level": self.optimization_level,
            "enable_compression": self.enable_compression,
            "enable_tiered_storage": self.enable_tiered_storage,
            "enable_deduplication": self.enable_deduplication,
            "enable_pruning": self.enable_pruning,
            "enable_federation": self.enable_federation,
            "enable_streaming_recall": self.enable_streaming_recall,
            "enable_adaptive_policy": self.enable_adaptive_policy,
            "compression": self.compression.__dict__,
            "tiered_storage": self.tiered_storage.__dict__,
            "deduplication": self.deduplication.__dict__,
            "pruning": self.pruning.__dict__,
            "federation": self.federation.__dict__,
            "streaming_recall": self.streaming_recall.__dict__,
            "adaptive_policy": self.adaptive_policy.__dict__,
            "audit": self.audit.__dict__,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OptimizationConfig":
        """Create from dictionary."""
        config = cls(
            enabled=data.get("enabled", True),
            optimization_level=data.get("optimization_level", "aggressive"),
            enable_compression=data.get("enable_compression", True),
            enable_tiered_storage=data.get("enable_tiered_storage", True),
            enable_deduplication=data.get("enable_deduplication", True),
            enable_pruning=data.get("enable_pruning", True),
            enable_federation=data.get("enable_federation", False),
            enable_streaming_recall=data.get("enable_streaming_recall", True),
            enable_adaptive_policy=data.get("enable_adaptive_policy", True),
        )

        # Load component configs
        if "compression" in data:
            config.compression = CompressionConfig(**data["compression"])
        if "tiered_storage" in data:
            config.tiered_storage = TieredStorageConfig(**data["tiered_storage"])
        if "deduplication" in data:
            config.deduplication = DeduplicationConfig(**data["deduplication"])
        if "pruning" in data:
            config.pruning = PruningConfig(**data["pruning"])
        if "federation" in data:
            config.federation = FederationConfig(**data["federation"])
        if "streaming_recall" in data:
            config.streaming_recall = StreamingRecallConfig(**data["streaming_recall"])
        if "adaptive_policy" in data:
            config.adaptive_policy = AdaptivePolicyConfig(**data["adaptive_policy"])
        if "audit" in data:
            config.audit = AuditConfig(**data["audit"])

        return config


def load_optimization_config(config_path: str | None = None) -> OptimizationConfig:
    """
    Load optimization configuration from file.

    Args:
        config_path: Path to YAML config file (default: config/memory_optimization.yaml)

    Returns:
        OptimizationConfig instance
    """
    if config_path is None:
        config_path = "config/memory_optimization.yaml"

    config_file = Path(config_path)

    if not config_file.exists():
        logger.warning(
            "Config file %s not found, using defaults. "
            "To customize, create config file with save_optimization_config()",
            config_path,
        )
        return OptimizationConfig()

    try:
        with open(config_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        config = OptimizationConfig.from_dict(data)
        logger.info("Loaded optimization config from %s", config_path)
        return config
    except Exception as e:
        logger.error("Failed to load config from %s: %s", config_path, e)
        logger.warning("Using default configuration")
        return OptimizationConfig()


def save_optimization_config(
    config: OptimizationConfig, config_path: str | None = None
):
    """
    Save optimization configuration to file.

    Args:
        config: OptimizationConfig to save
        config_path: Path to YAML config file (default: config/memory_optimization.yaml)
    """
    if config_path is None:
        config_path = "config/memory_optimization.yaml"

    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=False)

        logger.info("Saved optimization config to %s", config_path)
    except Exception as e:
        logger.error("Failed to save config to %s: %s", config_path, e)


def get_optimization_level_preset(level: str) -> OptimizationConfig:
    """
    Get preset configuration for optimization level.

    Args:
        level: Optimization level (conservative, moderate, aggressive)

    Returns:
        OptimizationConfig with preset values
    """
    config = OptimizationConfig(optimization_level=level)

    if level == "conservative":
        # Minimal optimization, prioritize safety
        config.compression.compression_level = 3
        config.tiered_storage.hot_capacity_mb = 500  # Larger hot tier
        config.tiered_storage.migration_interval_seconds = 600  # Less frequent
        config.pruning.inactive_threshold_days = 90  # Keep more data
        config.adaptive_policy.policy_learning_rate = 0.05  # Slow adaptation

    elif level == "moderate":
        # Balanced optimization
        config.compression.compression_level = 6
        config.tiered_storage.hot_capacity_mb = 200
        config.tiered_storage.migration_interval_seconds = 300
        config.pruning.inactive_threshold_days = 30
        config.adaptive_policy.policy_learning_rate = 0.1

    elif level == "aggressive":
        # Maximum optimization
        config.compression.compression_level = 9
        config.tiered_storage.hot_capacity_mb = 100  # Smaller hot tier
        config.tiered_storage.migration_interval_seconds = 60  # Frequent migration
        config.pruning.inactive_threshold_days = 7  # Aggressive pruning
        config.adaptive_policy.policy_learning_rate = 0.2  # Fast adaptation

    return config
