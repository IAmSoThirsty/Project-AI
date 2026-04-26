"""
Tests for Memory Optimization Layer

Comprehensive test suite covering:
- Compression engine (all strategies)
- Tiered storage (hot/warm/cold)
- Deduplication engine
- Optimization middleware
- Configuration loading
- Integration scenarios
"""

import tempfile

import numpy as np
import pytest

from app.core.memory_optimization import (
    CompressionEngine,
    CompressionStrategy,
    DeduplicationEngine,
    OptimizationConfig,
    OptimizationMiddleware,
    StorageTier,
    TieredStorageManager,
    TierPolicy,
    load_optimization_config,
    save_optimization_config,
)

# ============================================================================
# Compression Engine Tests
# ============================================================================


class TestCompressionEngine:
    """Test compression engine functionality."""

    @pytest.fixture
    def engine(self):
        """Create compression engine."""
        return CompressionEngine(
            default_strategy=CompressionStrategy.ADAPTIVE,
            compression_level=6,
        )

    def test_compress_general_data(self, engine):
        """Test compression of general data (dict, list)."""
        data = {
            "key1": "value1",
            "key2": [1, 2, 3, 4, 5],
            "key3": {"nested": "data"},
        }

        result = engine.compress(data, strategy=CompressionStrategy.ZLIB)

        assert result.compressed_size > 0
        assert result.compressed_size < result.original_size
        assert result.compression_ratio > 0
        assert result.strategy == CompressionStrategy.ZLIB
        assert result.checksum != ""

    def test_compress_decompress_roundtrip(self, engine):
        """Test compression and decompression roundtrip."""
        original_data = {"test": "data", "numbers": [1, 2, 3, 4, 5]}

        # Compress
        compressed = engine.compress(original_data)

        # Decompress
        decompressed = engine.decompress(compressed)

        assert decompressed.decompressed_data == original_data
        assert decompressed.checksum_valid is True

    def test_compress_numpy_array(self, engine):
        """Test compression of numpy arrays."""
        data = np.random.rand(100, 10).astype(np.float32)

        result = engine.compress(data, strategy=CompressionStrategy.QUANTIZE_INT8)

        assert result.compression_ratio > 0
        assert result.strategy == CompressionStrategy.QUANTIZE_INT8

        # Decompress and verify shape
        decompressed = engine.decompress(result)
        assert decompressed.decompressed_data.shape == data.shape

    def test_compress_sparse_array(self, engine):
        """Test sparse array compression."""
        # Create sparse array (90% zeros)
        data = np.zeros((100, 100))
        data[::10, ::10] = 1.0  # 10% non-zero

        result = engine.compress(data, strategy=CompressionStrategy.SPARSE_CSR)

        assert result.compression_ratio > 0.5  # Should compress well

        # Decompress and verify
        decompressed = engine.decompress(result)
        np.testing.assert_array_almost_equal(decompressed.decompressed_data, data)

    def test_compress_graph_data(self, engine):
        """Test graph data compression."""
        graph = {
            "nodes": ["A", "B", "C"],
            "edges": [
                {"from": "A", "to": "B", "confidence": 0.9},
                {"from": "B", "to": "C", "confidence": 0.2},  # Will be pruned
                {"from": "A", "to": "C", "confidence": 0.8},
            ],
        }

        result = engine.compress(graph, strategy=CompressionStrategy.GRAPH_PRUNE)

        # Should prune low-confidence edge
        assert "pruned_edges" in result.metadata
        assert result.metadata["pruned_edges"] == 1

    def test_adaptive_strategy_selection(self, engine):
        """Test adaptive strategy selection."""
        # NumPy array should select quantization
        array_data = np.random.rand(50).astype(np.float32)
        result = engine.compress(array_data)
        assert result.strategy in (
            CompressionStrategy.QUANTIZE_INT8,
            CompressionStrategy.BLOSC,
            CompressionStrategy.LZ4,
        )

        # Dict should select fast compression
        dict_data = {"key": "value"}
        result = engine.compress(dict_data)
        assert result.strategy in (
            CompressionStrategy.BLOSC,
            CompressionStrategy.LZ4,
            CompressionStrategy.ZLIB,
        )

    def test_compression_statistics(self, engine):
        """Test compression statistics tracking."""
        data = {"test": "data"}

        # Compress multiple times
        for _ in range(5):
            engine.compress(data)

        stats = engine.get_statistics()

        assert stats["total_compressions"] == 5
        assert stats["total_original_bytes"] > 0
        assert stats["total_compressed_bytes"] > 0
        assert stats["overall_compression_ratio"] >= 0


# ============================================================================
# Tiered Storage Tests
# ============================================================================


class TestTieredStorage:
    """Test tiered storage functionality."""

    @pytest.fixture
    def storage(self):
        """Create tiered storage manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            policy = TierPolicy(
                hot_capacity_bytes=1024 * 1024,  # 1 MB
                warm_capacity_bytes=10 * 1024 * 1024,  # 10 MB
                hot_storage_path=f"{tmpdir}/hot",
                warm_storage_path=f"{tmpdir}/warm",
                cold_storage_path=f"{tmpdir}/cold",
            )
            manager = TieredStorageManager(policy=policy, enable_background_tasks=False)
            yield manager
            manager.shutdown()

    def test_write_and_read(self, storage):
        """Test basic write and read operations."""
        data = {"test": "data", "number": 42}

        # Write to hot tier
        success = storage.write("test_key", data, tier=StorageTier.HOT)
        assert success is True

        # Read back
        retrieved, tier = storage.read("test_key")
        assert retrieved == data
        assert tier == StorageTier.HOT

    def test_tier_migration(self, storage):
        """Test manual tier migration."""
        data = {"test": "data"}

        # Write to hot tier
        storage.write("test_key", data, tier=StorageTier.HOT)

        # Migrate to warm tier
        success = storage.migrate_tier("test_key", StorageTier.WARM)
        assert success is True

        # Verify in warm tier
        retrieved, tier = storage.read("test_key")
        assert retrieved == data
        assert tier == StorageTier.WARM

    def test_delete(self, storage):
        """Test delete operation."""
        data = {"test": "data"}

        storage.write("test_key", data)
        success = storage.delete("test_key")
        assert success is True

        # Verify deleted
        retrieved, tier = storage.read("test_key")
        assert retrieved is None
        assert tier is None

    def test_capacity_enforcement(self, storage):
        """Test tier capacity enforcement."""
        # Fill hot tier beyond capacity
        large_data = {"data": "x" * 10000}  # ~10 KB

        # Write many entries
        for i in range(200):  # Should exceed 1 MB hot capacity
            storage.write(f"key_{i}", large_data, tier=StorageTier.HOT)

        stats = storage.get_statistics()

        # Some data should have been evicted to warm tier
        assert stats["hot_usage_bytes"] <= storage.policy.hot_capacity_bytes

    def test_access_pattern_tracking(self, storage):
        """Test access pattern tracking."""
        data = {"test": "data"}

        storage.write("test_key", data)

        # Access multiple times
        for _ in range(5):
            storage.read("test_key")

        # Check access pattern
        pattern = storage.access_patterns.get("test_key")
        assert pattern is not None
        assert pattern.access_count >= 5

    def test_statistics(self, storage):
        """Test statistics collection."""
        # Write some data
        for i in range(10):
            storage.write(f"key_{i}", {"data": i}, tier=StorageTier.HOT)

        # Read some data
        for i in range(5):
            storage.read(f"key_{i}")

        stats = storage.get_statistics()

        assert stats["total_keys"] == 10
        assert stats["total_reads"] >= 5
        assert stats["total_writes"] >= 10
        assert "hot_usage_bytes" in stats


# ============================================================================
# Deduplication Engine Tests
# ============================================================================


class TestDeduplicationEngine:
    """Test deduplication engine functionality."""

    @pytest.fixture
    def dedup_engine(self):
        """Create deduplication engine."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = DeduplicationEngine(
                storage_path=tmpdir,
                enable_bloom_filter=True,
            )
            yield engine
            engine.shutdown()

    def test_write_and_read(self, dedup_engine):
        """Test basic write and read."""
        data = {"test": "data"}

        # Write
        content_hash, was_duplicate = dedup_engine.write("key1", data)
        assert content_hash != ""
        assert was_duplicate is False

        # Read
        retrieved = dedup_engine.read("key1")
        assert retrieved == data

    def test_deduplication(self, dedup_engine):
        """Test deduplication of identical content."""
        data = {"test": "data", "number": 42}

        # Write same data with different keys
        hash1, dup1 = dedup_engine.write("key1", data)
        hash2, dup2 = dedup_engine.write("key2", data)

        # Second write should be deduplicated
        assert hash1 == hash2
        assert dup1 is False
        assert dup2 is True

        # Both keys should retrieve same data
        assert dedup_engine.read("key1") == data
        assert dedup_engine.read("key2") == data

    def test_reference_counting(self, dedup_engine):
        """Test reference counting."""
        data = {"test": "data"}

        # Write same data multiple times
        hash1, _ = dedup_engine.write("key1", data)
        dedup_engine.write("key2", data)
        dedup_engine.write("key3", data)

        # Reference count should be 3
        assert dedup_engine.get_reference_count(hash1) == 3

        # Delete one reference
        dedup_engine.delete("key1")
        assert dedup_engine.get_reference_count(hash1) == 2

        # Delete all references
        dedup_engine.delete("key2")
        dedup_engine.delete("key3")
        assert dedup_engine.get_reference_count(hash1) == 0

    def test_statistics(self, dedup_engine):
        """Test deduplication statistics."""
        data = {"test": "data"}

        # Write same data multiple times
        for i in range(10):
            dedup_engine.write(f"key_{i}", data)

        stats = dedup_engine.get_statistics()

        assert stats["total_writes"] == 10
        assert stats["unique_contents"] == 1  # All same data
        assert stats["dedup_hits"] == 9  # First is miss, rest are hits
        assert stats["dedup_ratio"] > 0.8  # High dedup ratio


# ============================================================================
# Optimization Middleware Tests
# ============================================================================


class TestOptimizationMiddleware:
    """Test optimization middleware functionality."""

    @pytest.fixture
    def middleware(self):
        """Create middleware with test configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = OptimizationConfig()
            config.enabled = True
            config.compression.enabled = True
            config.tiered_storage.enabled = True
            config.tiered_storage.hot_storage_path = f"{tmpdir}/hot"
            config.tiered_storage.warm_storage_path = f"{tmpdir}/warm"
            config.tiered_storage.cold_storage_path = f"{tmpdir}/cold"
            config.deduplication.enabled = True
            config.deduplication.storage_path = f"{tmpdir}/dedup"

            middleware = OptimizationMiddleware(config=config)
            yield middleware
            middleware.shutdown()

    def test_store_and_retrieve(self, middleware):
        """Test basic store and retrieve."""
        data = {"test": "data", "number": 42}

        # Store
        success = middleware.store("test_key", data)
        assert success is True

        # Retrieve
        retrieved = middleware.retrieve("test_key")
        assert retrieved == data

    def test_compression_integration(self, middleware):
        """Test compression in middleware."""
        # Large data that should compress well
        data = {"data": "x" * 10000, "numbers": list(range(1000))}

        middleware.store("large_key", data)
        retrieved = middleware.retrieve("large_key")

        assert retrieved == data

        # Check compression stats
        stats = middleware.get_statistics()
        assert "compression" in stats
        assert stats["compression"]["total_compressions"] > 0

    def test_deduplication_integration(self, middleware):
        """Test deduplication in middleware."""
        data = {"test": "data"}

        # Store same data multiple times
        middleware.store("key1", data)
        middleware.store("key2", data)
        middleware.store("key3", data)

        # Check dedup stats
        stats = middleware.get_statistics()
        assert "deduplication" in stats
        assert stats["deduplication"]["dedup_hits"] >= 2

    def test_delete(self, middleware):
        """Test delete operation."""
        data = {"test": "data"}

        middleware.store("test_key", data)
        success = middleware.delete("test_key")
        assert success is True

        # Verify deleted
        retrieved = middleware.retrieve("test_key")
        assert retrieved is None

    def test_statistics_comprehensive(self, middleware):
        """Test comprehensive statistics."""
        # Perform various operations
        for i in range(10):
            middleware.store(f"key_{i}", {"data": i})

        for i in range(5):
            middleware.retrieve(f"key_{i}")

        stats = middleware.get_statistics()

        assert "middleware" in stats
        assert "compression" in stats
        assert "tiered_storage" in stats
        assert "deduplication" in stats
        assert stats["middleware"]["total_writes"] >= 10
        assert stats["middleware"]["total_reads"] >= 5

    def test_disabled_optimization(self):
        """Test middleware with optimization disabled."""
        config = OptimizationConfig()
        config.enabled = False

        middleware = OptimizationMiddleware(config=config)

        # Should still work but bypass optimization
        data = {"test": "data"}
        success = middleware.store("test_key", data)

        # Since no wrapped engine, should fail gracefully
        assert success is False


# ============================================================================
# Configuration Tests
# ============================================================================


class TestOptimizationConfig:
    """Test configuration loading and saving."""

    def test_default_config(self):
        """Test default configuration."""
        config = OptimizationConfig()

        assert config.enabled is True
        assert config.optimization_level == "aggressive"
        assert config.compression.enabled is True
        assert config.tiered_storage.enabled is True
        assert config.deduplication.enabled is True

    def test_config_to_dict(self):
        """Test configuration serialization."""
        config = OptimizationConfig()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "enabled" in config_dict
        assert "compression" in config_dict
        assert "tiered_storage" in config_dict

    def test_config_from_dict(self):
        """Test configuration deserialization."""
        config_dict = {
            "enabled": False,
            "optimization_level": "moderate",
            "compression": {"compression_level": 3},
        }

        config = OptimizationConfig.from_dict(config_dict)

        assert config.enabled is False
        assert config.optimization_level == "moderate"
        assert config.compression.compression_level == 3

    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = f"{tmpdir}/test_config.yaml"

            # Create and save config
            config = OptimizationConfig()
            config.optimization_level = "moderate"
            save_optimization_config(config, config_path)

            # Load config
            loaded_config = load_optimization_config(config_path)

            assert loaded_config.optimization_level == "moderate"

    def test_load_nonexistent_config(self):
        """Test loading non-existent config file."""
        # Should return default config
        config = load_optimization_config("/nonexistent/path.yaml")

        assert isinstance(config, OptimizationConfig)
        assert config.enabled is True


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegrationScenarios:
    """Test complete integration scenarios."""

    def test_full_pipeline(self):
        """Test complete optimization pipeline."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config
            config = OptimizationConfig()
            config.enabled = True
            config.tiered_storage.hot_storage_path = f"{tmpdir}/hot"
            config.tiered_storage.warm_storage_path = f"{tmpdir}/warm"
            config.tiered_storage.cold_storage_path = f"{tmpdir}/cold"
            config.deduplication.storage_path = f"{tmpdir}/dedup"

            # Create middleware
            middleware = OptimizationMiddleware(config=config)

            # Store various types of data
            data_types = [
                {"type": "dict", "data": {"key": "value"}},
                {"type": "list", "data": [1, 2, 3, 4, 5]},
                {"type": "string", "data": "test string"},
                {"type": "large", "data": "x" * 10000},
            ]

            for i, item in enumerate(data_types):
                success = middleware.store(f"key_{i}", item["data"])
                assert success is True

            # Retrieve all data
            for i, item in enumerate(data_types):
                retrieved = middleware.retrieve(f"key_{i}")
                assert retrieved == item["data"]

            # Get statistics
            stats = middleware.get_statistics()

            assert stats["middleware"]["total_writes"] >= len(data_types)
            assert stats["middleware"]["total_reads"] >= len(data_types)

            # Cleanup
            middleware.shutdown()

    def test_memory_reduction_measurement(self):
        """Test memory reduction measurement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = OptimizationConfig()
            config.enabled = True
            config.tiered_storage.hot_storage_path = f"{tmpdir}/hot"
            config.tiered_storage.warm_storage_path = f"{tmpdir}/warm"
            config.tiered_storage.cold_storage_path = f"{tmpdir}/cold"
            config.deduplication.storage_path = f"{tmpdir}/dedup"

            middleware = OptimizationMiddleware(config=config)

            # Store duplicate data
            data = {"data": "x" * 1000, "numbers": list(range(100))}

            for i in range(20):
                middleware.store(f"key_{i}", data)

            # Get statistics
            stats = middleware.get_statistics()

            # Should achieve significant memory reduction
            if "overall" in stats:
                assert stats["overall"]["memory_reduction_percent"] > 50

            middleware.shutdown()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
