"""
Memory Optimization Layer - GOD TIER Architecture

This module provides aggressive memory resource optimization while maintaining
full system capabilities. It acts as a transparent middleware layer that can be
enabled/disabled via configuration without impacting existing systems.

Key Features:
- Advanced compression (LZ4, Blosc, quantization, sparse vectors)
- Tiered retention & aging (hot/warm/cold storage)
- Hardware-aware allocation (RAM/NVMe/Disk/Cloud)
- Federation & externalized aging
- Model-aware pruning
- Streaming & partial recall
- Policy-aware configuration
- Content-addressed deduplication
- Adaptive policy tuning with continuous telemetry

Architecture:
- Non-invasive: Works as optional wrapper around existing memory systems
- Backward compatible: Disabled by default, opt-in via config
- Transparent: Existing code doesn't need to know about optimization
- Production-grade: Full error handling, logging, telemetry, auditing

Target: 75%+ memory reduction with <5% performance impact
"""

from .adaptive_policy_engine import AdaptivePolicyEngine, PolicyAction, PolicyRule
from .compression_engine import CompressionEngine, CompressionStrategy
from .deduplication_engine import ContentAddress, DeduplicationEngine
from .federation_backend import DataSovereignty, FederationBackend, StorageBackend
from .memory_pool_allocator import (
    HardwareProfile,
    MemoryPool,
    MemoryPoolAllocator,
    PoolConfiguration,
)
from .optimization_config import (
    OptimizationConfig,
    get_optimization_level_preset,
    load_optimization_config,
    save_optimization_config,
)
from .optimization_middleware import OptimizationMiddleware
from .pruning_scheduler import PruningPolicy, PruningScheduler
from .streaming_recall import RecallStrategy, StreamingRecallEngine
from .telemetry_collector import (
    CompressionMetrics,
    MemoryMetrics,
    TelemetryCollector,
    TierMetrics,
)
from .tiered_storage import (
    AccessPattern,
    StorageTier,
    TieredStorageManager,
    TierPolicy,
)

__all__ = [
    # Core engines
    "CompressionEngine",
    "CompressionStrategy",
    "TieredStorageManager",
    "StorageTier",
    "TierPolicy",
    "AccessPattern",
    "MemoryPoolAllocator",
    "MemoryPool",
    "PoolConfiguration",
    "HardwareProfile",
    "DeduplicationEngine",
    "ContentAddress",
    # Configuration
    "OptimizationConfig",
    "load_optimization_config",
    "save_optimization_config",
    "get_optimization_level_preset",
    # Integration
    "OptimizationMiddleware",
    # Telemetry
    "TelemetryCollector",
    "MemoryMetrics",
    "CompressionMetrics",
    "TierMetrics",
    # Adaptive policies
    "AdaptivePolicyEngine",
    "PolicyRule",
    "PolicyAction",
    # Advanced features
    "StreamingRecallEngine",
    "RecallStrategy",
    "PruningScheduler",
    "PruningPolicy",
    "FederationBackend",
    "StorageBackend",
    "DataSovereignty",
]

__version__ = "1.0.0"
