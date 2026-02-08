"""
Optimization Middleware - Transparent Integration Layer

This middleware acts as a transparent wrapper around existing memory systems,
providing aggressive optimization without modifying existing code.

Key Features:
- Drop-in replacement for existing memory operations
- Automatic compression/decompression
- Tiered storage management
- Deduplication
- Streaming recall
- Adaptive policy tuning
- Full backward compatibility

Usage:
    # Option 1: Wrap existing memory engine
    memory_engine = MemoryEngine()
    optimized_memory = OptimizationMiddleware(memory_engine, config)

    # Option 2: Use standalone
    optimized_memory = OptimizationMiddleware(config=config)
    optimized_memory.store("key", data)
    data = optimized_memory.retrieve("key")

The middleware is completely transparent - existing code doesn't need to change.
"""

import logging
import time
from typing import Any

from .adaptive_policy_engine import AdaptivePolicyEngine
from .compression_engine import CompressionEngine, CompressionStrategy
from .deduplication_engine import DeduplicationEngine
from .federation_backend import FederationBackend, StorageBackend
from .optimization_config import OptimizationConfig, load_optimization_config
from .pruning_scheduler import PruningScheduler
from .streaming_recall import RecallStrategy, StreamingRecallEngine
from .telemetry_collector import TelemetryCollector
from .tiered_storage import StorageTier, TieredStorageManager, TierPolicy

logger = logging.getLogger(__name__)


class OptimizationMiddleware:
    """
    Transparent optimization layer for memory systems.

    Acts as a drop-in wrapper that adds aggressive optimization to any
    memory system without requiring code changes.

    Target: 75%+ memory reduction with <5% performance impact
    """

    def __init__(
        self,
        wrapped_engine: Any | None = None,
        config: OptimizationConfig | None = None,
        config_path: str | None = None,
    ):
        """
        Initialize optimization middleware.

        Args:
            wrapped_engine: Existing memory engine to wrap (optional)
            config: Optimization configuration (optional, loads from file if None)
            config_path: Path to config file (default: config/memory_optimization.yaml)
        """
        self.wrapped_engine = wrapped_engine
        self.config = config or load_optimization_config(config_path)

        # Initialize components based on configuration
        self.compression_engine = None
        self.tiered_storage = None
        self.dedup_engine = None
        self.pruning_scheduler = None
        self.federation_backend = None
        self.streaming_recall = None
        self.adaptive_policy = None
        self.telemetry_collector = None

        self._initialize_components()

        # Statistics
        self.stats = {
            "total_reads": 0,
            "total_writes": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "optimization_enabled": self.config.enabled,
        }

        logger.info(
            "OptimizationMiddleware initialized (enabled=%s, level=%s)",
            self.config.enabled,
            self.config.optimization_level,
        )

    def _initialize_components(self):
        """Initialize optimization components based on configuration."""
        if not self.config.enabled:
            logger.info("Optimization disabled by configuration")
            return

        # Compression engine
        if self.config.enable_compression and self.config.compression.enabled:
            self.compression_engine = CompressionEngine(
                default_strategy=CompressionStrategy[
                    self.config.compression.default_strategy.upper()
                ],
                compression_level=self.config.compression.compression_level,
                quantization_bits=self.config.compression.quantization_bits,
                sparse_threshold=self.config.compression.sparse_threshold,
                graph_prune_threshold=self.config.compression.graph_prune_threshold,
            )
            logger.info("Compression engine enabled")

        # Tiered storage
        if self.config.enable_tiered_storage and self.config.tiered_storage.enabled:
            tier_policy = TierPolicy(
                hot_capacity_bytes=self.config.tiered_storage.hot_capacity_mb
                * 1024
                * 1024,
                warm_capacity_bytes=self.config.tiered_storage.warm_capacity_mb
                * 1024
                * 1024,
                cold_capacity_bytes=(
                    -1 if self.config.tiered_storage.cold_capacity_unlimited else 0
                ),
                hot_to_warm_idle_hours=self.config.tiered_storage.hot_to_warm_idle_hours,
                warm_to_cold_idle_hours=self.config.tiered_storage.warm_to_cold_idle_hours,
                eviction_policy=self.config.tiered_storage.eviction_policy,
                eviction_threshold=self.config.tiered_storage.eviction_threshold,
                migration_interval_seconds=self.config.tiered_storage.migration_interval_seconds,
                pruning_interval_seconds=self.config.tiered_storage.pruning_interval_seconds,
                hot_storage_path=self.config.tiered_storage.hot_storage_path,
                warm_storage_path=self.config.tiered_storage.warm_storage_path,
                cold_storage_path=self.config.tiered_storage.cold_storage_path,
            )
            self.tiered_storage = TieredStorageManager(policy=tier_policy)
            logger.info("Tiered storage enabled")

        # Deduplication engine
        if self.config.enable_deduplication and self.config.deduplication.enabled:
            self.dedup_engine = DeduplicationEngine(
                storage_path=self.config.deduplication.storage_path,
                enable_bloom_filter=self.config.deduplication.enable_bloom_filter,
                bloom_filter_size=self.config.deduplication.bloom_filter_size,
            )
            logger.info("Deduplication engine enabled")

        # Pruning scheduler
        if self.config.enable_pruning and self.config.pruning.enabled:
            from .pruning_scheduler import PruningPolicy

            pruning_policy = PruningPolicy(
                inactive_threshold_days=self.config.pruning.inactive_threshold_days,
                min_confidence=self.config.pruning.min_entity_confidence,
                min_access_count=self.config.pruning.min_cluster_access_count,
            )
            self.pruning_scheduler = PruningScheduler(policy=pruning_policy)
            logger.info("Pruning scheduler enabled")

        # Federation backend
        if self.config.enable_federation and self.config.federation.enabled:
            self.federation_backend = FederationBackend(
                backend_type=StorageBackend[self.config.federation.backend_type.upper()]
            )
            logger.info("Federation backend enabled")

        # Streaming recall
        if self.config.enable_streaming_recall and self.config.streaming_recall.enabled:
            self.streaming_recall = StreamingRecallEngine(
                default_strategy=RecallStrategy[
                    self.config.streaming_recall.default_strategy.upper()
                ]
            )
            logger.info("Streaming recall enabled")

        # Adaptive policy engine
        if self.config.enable_adaptive_policy and self.config.adaptive_policy.enabled:
            self.adaptive_policy = AdaptivePolicyEngine(
                learning_rate=self.config.adaptive_policy.policy_learning_rate
            )
            logger.info("Adaptive policy engine enabled")

        # Telemetry collector
        self.telemetry_collector = TelemetryCollector(
            collection_interval_seconds=self.config.adaptive_policy.telemetry_interval_seconds
        )
        logger.info("Telemetry collector enabled")

    # ========================================================================
    # Public API - Memory Operations
    # ========================================================================

    def store(self, key: str, data: Any, tier: StorageTier = StorageTier.HOT) -> bool:
        """
        Store data with full optimization pipeline.

        Args:
            key: Unique key for data
            data: Data to store
            tier: Target storage tier

        Returns:
            True if successful
        """
        if not self.config.enabled:
            # Pass through to wrapped engine if available
            if self.wrapped_engine and hasattr(self.wrapped_engine, "store"):
                return self.wrapped_engine.store(key, data)
            return False

        try:
            start_time = time.time()

            # Step 1: Compress if enabled
            if self.compression_engine:
                compressed_result = self.compression_engine.compress(data)
                data_to_store = {
                    "compressed": True,
                    "data": compressed_result.compressed_data.hex(),
                    "metadata": {
                        "original_size": compressed_result.original_size,
                        "compressed_size": compressed_result.compressed_size,
                        "compression_ratio": compressed_result.compression_ratio,
                        "strategy": compressed_result.strategy.value,
                        "checksum": compressed_result.checksum,
                    },
                }
                logger.debug(
                    "Compressed %s: %.2f%% reduction",
                    key,
                    compressed_result.compression_ratio * 100,
                )
            else:
                data_to_store = {"compressed": False, "data": data}

            # Step 2: Deduplicate if enabled
            if self.dedup_engine:
                content_hash, was_duplicate = self.dedup_engine.write(
                    key, data_to_store
                )
                if was_duplicate:
                    logger.debug("Dedup hit for %s", key)
                    self.stats["cache_hits"] += 1

            # Step 3: Store in tiered storage if enabled
            if self.tiered_storage:
                success = self.tiered_storage.write(key, data_to_store, tier=tier)
            elif self.wrapped_engine and hasattr(self.wrapped_engine, "store"):
                # Fallback to wrapped engine
                success = self.wrapped_engine.store(key, data_to_store)
            else:
                # No storage available
                success = False

            # Update statistics
            self.stats["total_writes"] += 1
            elapsed_ms = (time.time() - start_time) * 1000

            logger.debug("Store %s completed in %.2f ms", key, elapsed_ms)
            return success
        except Exception as e:
            logger.error("Store failed for key %s: %s", key, e)
            return False

    def retrieve(self, key: str) -> Any | None:
        """
        Retrieve data with full optimization pipeline.

        Args:
            key: Unique key for data

        Returns:
            Original data or None if not found
        """
        if not self.config.enabled:
            # Pass through to wrapped engine if available
            if self.wrapped_engine and hasattr(self.wrapped_engine, "retrieve"):
                return self.wrapped_engine.retrieve(key)
            return None

        try:
            start_time = time.time()

            # Step 1: Retrieve from tiered storage or dedup
            if self.dedup_engine:
                data_retrieved = self.dedup_engine.read(key)
            elif self.tiered_storage:
                data_retrieved, tier = self.tiered_storage.read(key)
            elif self.wrapped_engine and hasattr(self.wrapped_engine, "retrieve"):
                data_retrieved = self.wrapped_engine.retrieve(key)
            else:
                data_retrieved = None

            if data_retrieved is None:
                logger.debug("Key %s not found", key)
                self.stats["cache_misses"] += 1
                return None

            # Step 2: Decompress if needed
            if isinstance(data_retrieved, dict) and data_retrieved.get("compressed"):
                if self.compression_engine:
                    from .compression_engine import CompressionResult

                    metadata = data_retrieved["metadata"]
                    compressed_data = bytes.fromhex(data_retrieved["data"])

                    result = CompressionResult(
                        compressed_data=compressed_data,
                        original_size=metadata["original_size"],
                        compressed_size=metadata["compressed_size"],
                        compression_ratio=metadata["compression_ratio"],
                        strategy=CompressionStrategy[metadata["strategy"].upper()],
                        metadata={},
                        checksum=metadata["checksum"],
                    )

                    decompressed = self.compression_engine.decompress(result)
                    data = decompressed.decompressed_data

                    logger.debug("Decompressed %s", key)
                else:
                    logger.warning(
                        "Data is compressed but compression engine not available"
                    )
                    data = data_retrieved
            else:
                data = (
                    data_retrieved.get("data")
                    if isinstance(data_retrieved, dict)
                    else data_retrieved
                )

            # Update statistics
            self.stats["total_reads"] += 1
            self.stats["cache_hits"] += 1
            elapsed_ms = (time.time() - start_time) * 1000

            logger.debug("Retrieve %s completed in %.2f ms", key, elapsed_ms)
            return data
        except Exception as e:
            logger.error("Retrieve failed for key %s: %s", key, e)
            return None

    def delete(self, key: str) -> bool:
        """
        Delete data.

        Args:
            key: Unique key for data

        Returns:
            True if successful
        """
        if not self.config.enabled:
            if self.wrapped_engine and hasattr(self.wrapped_engine, "delete"):
                return self.wrapped_engine.delete(key)
            return False

        try:
            # Delete from all layers
            success = True

            if self.dedup_engine:
                success = self.dedup_engine.delete(key) and success

            if self.tiered_storage:
                success = self.tiered_storage.delete(key) and success

            if self.wrapped_engine and hasattr(self.wrapped_engine, "delete"):
                success = self.wrapped_engine.delete(key) and success

            logger.debug("Delete %s: success=%s", key, success)
            return success
        except Exception as e:
            logger.error("Delete failed for key %s: %s", key, e)
            return False

    # ========================================================================
    # Metrics and Management
    # ========================================================================

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive optimization statistics."""
        stats = {
            "middleware": self.stats,
            "config": {
                "enabled": self.config.enabled,
                "optimization_level": self.config.optimization_level,
            },
        }

        if self.compression_engine:
            stats["compression"] = self.compression_engine.get_statistics()

        if self.tiered_storage:
            stats["tiered_storage"] = self.tiered_storage.get_statistics()

        if self.dedup_engine:
            stats["deduplication"] = self.dedup_engine.get_statistics()

        if self.pruning_scheduler:
            stats["pruning"] = self.pruning_scheduler.get_statistics()

        if self.telemetry_collector:
            stats["telemetry"] = self.telemetry_collector.get_statistics()

        # Calculate overall memory reduction
        if self.compression_engine and self.dedup_engine:
            comp_stats = self.compression_engine.get_statistics()
            dedup_stats = self.dedup_engine.get_statistics()

            # Combined reduction from compression and dedup
            comp_ratio = comp_stats.get("overall_compression_ratio", 0.0)
            dedup_ratio = dedup_stats.get("dedup_ratio", 0.0)

            # Combined reduction (not simply additive)
            combined_reduction = 1.0 - ((1.0 - comp_ratio) * (1.0 - dedup_ratio))

            stats["overall"] = {
                "memory_reduction_percent": combined_reduction * 100,
                "memory_reduction_target_percent": 75.0,
                "target_achieved": combined_reduction >= 0.75,
            }

        return stats

    def shutdown(self):
        """Shutdown middleware and all components."""
        logger.info("Shutting down OptimizationMiddleware...")

        if self.tiered_storage:
            self.tiered_storage.shutdown()

        if self.dedup_engine:
            self.dedup_engine.shutdown()

        logger.info("OptimizationMiddleware shutdown complete")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()
