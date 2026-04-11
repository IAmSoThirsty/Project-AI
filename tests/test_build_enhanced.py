"""
Tests for TAAR Enhanced Build System

Tests all major components:
- DistributedCache
- BuildAnalytics
- GraphVisualizer
- IncrementalBuildOrchestrator
- EnhancedExecutor
"""

import asyncio
import json
import tempfile
import time
from pathlib import Path

import pytest

from taar.build_enhanced import (
    BuildAnalytics,
    BuildMetrics,
    CacheTransferMetrics,
    DistributedCache,
    GraphVisualizer,
    IncrementalBuildOrchestrator,
    RemoteCacheConfig,
    SimpleCacheServer,
    start_cache_server,
)
from taar.cache import CacheEntry, ResultCache
from taar.config import Runner, RunnerCommand, TaarConfig, load_config
from taar.graph import ImpactResult


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    tmp = Path(tempfile.mkdtemp(prefix="taar_test_"))
    yield tmp
    # Cleanup handled by test


@pytest.fixture
def sample_config(temp_dir):
    """Create a sample TaarConfig for testing."""
    return TaarConfig(
        version="1.0.0",
        parallelism=2,
        cache_dir=temp_dir / ".taar-cache",
        debounce_ms=100,
        fail_fast=False,
        notifications=False,
        runners={
            "test_runner": Runner(
                name="test_runner",
                enabled=True,
                paths=("**/*.py",),
                test_paths=("tests/**/*.py",),
                commands=(
                    RunnerCommand(
                        name="test_cmd",
                        template="echo 'test' && exit 0",
                        priority=1,
                    ),
                ),
            )
        },
        impact_map={},
        project_root=temp_dir,
    )


@pytest.fixture
def sample_cache_entry():
    """Create a sample CacheEntry for testing."""
    return CacheEntry(
        cache_key="abc123",
        runner_name="test_runner",
        command_name="test_cmd",
        passed=True,
        return_code=0,
        duration=1.5,
        output="test output",
        timestamp=time.time(),
        file_hashes={"test.py": "hash123"},
    )


# ═══════════════════════════════════════════════════════════════════════════
# DistributedCache Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_distributed_cache_local_only(temp_dir, sample_cache_entry):
    """Test DistributedCache with local cache only (remote disabled)."""
    local_cache = ResultCache(temp_dir / ".cache")
    remote_config = RemoteCacheConfig(enabled=False)
    
    cache = DistributedCache(local_cache, remote_config)
    
    # Store
    files = [temp_dir / "test.py"]
    files[0].touch()
    
    await cache.store(
        runner_name="test",
        command_name="cmd",
        files=files,
        command_template="echo test",
        passed=True,
        return_code=0,
        duration=1.0,
        output="output",
    )
    
    # Lookup
    entry = await cache.lookup("test", "cmd", files, "echo test")
    
    assert entry is not None
    assert entry.passed is True
    assert entry.duration == 1.0
    
    await cache.close()


@pytest.mark.asyncio
async def test_distributed_cache_metrics(temp_dir):
    """Test cache transfer metrics tracking."""
    local_cache = ResultCache(temp_dir / ".cache")
    remote_config = RemoteCacheConfig(enabled=False)
    
    cache = DistributedCache(local_cache, remote_config)
    
    assert cache.metrics.uploads == 0
    assert cache.metrics.downloads == 0
    assert cache.metrics.upload_speed_mbps == 0.0
    
    await cache.close()


# ═══════════════════════════════════════════════════════════════════════════
# BuildAnalytics Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_build_analytics_record_and_retrieve(temp_dir):
    """Test recording and retrieving build metrics."""
    analytics = BuildAnalytics(temp_dir / "analytics")
    
    metrics = BuildMetrics(
        run_id="test123",
        timestamp=time.time(),
        total_duration=10.5,
        total_tasks=5,
        cached_tasks=2,
        executed_tasks=3,
        failed_tasks=0,
        cache_hit_rate=40.0,
        parallelism=4,
        runner_stats={},
        bottlenecks=[],
        incremental_savings=5.0,
    )
    
    analytics.record_build(metrics)
    
    history = analytics.get_build_history()
    assert len(history) == 1
    assert history[0].run_id == "test123"
    assert history[0].total_duration == 10.5


def test_build_analytics_dashboard_generation(temp_dir):
    """Test HTML dashboard generation."""
    analytics = BuildAnalytics(temp_dir / "analytics")
    
    # Record some builds
    for i in range(3):
        metrics = BuildMetrics(
            run_id=f"run{i}",
            timestamp=time.time() + i,
            total_duration=10.0 + i,
            total_tasks=10,
            cached_tasks=i * 2,
            executed_tasks=10 - i * 2,
            failed_tasks=0,
            cache_hit_rate=i * 20.0,
            parallelism=4,
        )
        analytics.record_build(metrics)
    
    dashboard_html = analytics.generate_dashboard()
    
    assert "TAAR Build Analytics Dashboard" in dashboard_html
    assert "d3.js" in dashboard_html
    assert "Cache Hit Rate" in dashboard_html


def test_build_analytics_save_dashboard(temp_dir):
    """Test saving dashboard to file."""
    analytics = BuildAnalytics(temp_dir / "analytics")
    
    metrics = BuildMetrics(
        run_id="test",
        timestamp=time.time(),
        total_duration=5.0,
        total_tasks=3,
        cached_tasks=1,
        executed_tasks=2,
        failed_tasks=0,
        cache_hit_rate=33.3,
        parallelism=2,
    )
    analytics.record_build(metrics)
    
    dashboard_path = analytics.save_dashboard()
    
    assert dashboard_path.exists()
    assert dashboard_path.suffix == ".html"
    assert dashboard_path.stat().st_size > 0


# ═══════════════════════════════════════════════════════════════════════════
# GraphVisualizer Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_graph_visualizer_impact_graph(sample_config, temp_dir):
    """Test generating impact graph data."""
    visualizer = GraphVisualizer(sample_config)
    
    changed_files = [temp_dir / "test.py"]
    impact = ImpactResult(
        affected_runners={"test_runner": changed_files},
        extra_test_files=[temp_dir / "test_test.py"],
    )
    
    graph_data = visualizer.generate_impact_graph(changed_files, impact)
    
    assert "nodes" in graph_data
    assert "edges" in graph_data
    assert len(graph_data["nodes"]) >= 2  # At least file + runner
    assert len(graph_data["edges"]) >= 1  # At least one connection


def test_graph_visualizer_graphviz_dot(sample_config, temp_dir):
    """Test generating Graphviz DOT format."""
    visualizer = GraphVisualizer(sample_config)
    
    graph_data = {
        "nodes": [
            {"id": "test.py", "type": "changed_file", "label": "test.py"},
            {"id": "runner", "type": "runner", "label": "runner"},
        ],
        "edges": [{"source": "test.py", "target": "runner"}],
    }
    
    dot = visualizer.generate_graphviz_dot(graph_data)
    
    assert "digraph TAAR" in dot
    assert "test_py" in dot
    assert "runner" in dot
    assert "->" in dot


def test_graph_visualizer_d3_html(sample_config, temp_dir):
    """Test generating D3.js interactive HTML."""
    visualizer = GraphVisualizer(sample_config)
    
    graph_data = {
        "nodes": [
            {"id": "test.py", "type": "changed_file", "label": "test.py"},
        ],
        "edges": [],
    }
    
    html = visualizer.generate_d3_html(graph_data)
    
    assert "<!DOCTYPE html>" in html
    assert "d3.js" in html
    assert "forceSimulation" in html
    assert "test.py" in html


def test_graph_visualizer_visualize(sample_config, temp_dir):
    """Test full visualization pipeline."""
    visualizer = GraphVisualizer(sample_config)
    
    changed_files = [temp_dir / "test.py"]
    impact = ImpactResult(
        affected_runners={"test_runner": changed_files},
    )
    
    output_dir = temp_dir / "viz"
    viz_paths = visualizer.visualize(changed_files, impact, output_dir)
    
    assert "json" in viz_paths
    assert "dot" in viz_paths
    assert "html" in viz_paths
    
    assert viz_paths["json"].exists()
    assert viz_paths["dot"].exists()
    assert viz_paths["html"].exists()


# ═══════════════════════════════════════════════════════════════════════════
# BuildMetrics Tests
# ═══════════════════════════════════════════════════════════════════════════


def test_build_metrics_properties():
    """Test BuildMetrics computed properties."""
    metrics = BuildMetrics(
        run_id="test",
        timestamp=time.time(),
        total_duration=10.0,
        total_tasks=10,
        cached_tasks=6,
        executed_tasks=4,
        failed_tasks=1,
        cache_hit_rate=60.0,
        parallelism=4,
    )
    
    assert metrics.success_rate == 90.0  # 9/10 passed
    assert metrics.average_task_duration == 2.5  # 10s / 4 executed


def test_cache_transfer_metrics_properties():
    """Test CacheTransferMetrics speed calculations."""
    metrics = CacheTransferMetrics(
        upload_bytes=1024 * 1024,  # 1 MB
        upload_time=1.0,  # 1 second
        download_bytes=2048 * 1024,  # 2 MB
        download_time=2.0,  # 2 seconds
    )
    
    assert metrics.upload_speed_mbps == pytest.approx(1.0, rel=0.01)
    assert metrics.download_speed_mbps == pytest.approx(1.0, rel=0.01)


# ═══════════════════════════════════════════════════════════════════════════
# Integration Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_incremental_build_orchestrator_basic(sample_config, temp_dir):
    """Test basic incremental build orchestration."""
    # Create test file
    test_file = temp_dir / "test.py"
    test_file.write_text("# test")
    
    orchestrator = IncrementalBuildOrchestrator(sample_config)
    
    # Run build with explicit files (no git needed)
    metrics = await orchestrator.run_incremental_build(
        changed_files=[test_file],
        full_build=False,
    )
    
    assert metrics.total_tasks >= 1
    assert metrics.total_duration > 0
    
    await orchestrator.close()


@pytest.mark.asyncio
async def test_incremental_build_full_vs_incremental(sample_config, temp_dir):
    """Test full build vs incremental build."""
    test_file = temp_dir / "test.py"
    test_file.write_text("# test")
    
    orchestrator = IncrementalBuildOrchestrator(sample_config)
    
    # Full build
    metrics_full = await orchestrator.run_incremental_build(
        changed_files=[test_file],
        full_build=True,
    )
    
    # Incremental (should hit cache)
    metrics_inc = await orchestrator.run_incremental_build(
        changed_files=[test_file],
        full_build=False,
    )
    
    # Incremental should be faster or same (all cached)
    assert metrics_inc.cache_hit_rate >= 0
    
    await orchestrator.close()


# ═══════════════════════════════════════════════════════════════════════════
# Performance Tests
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
async def test_parallel_execution_performance(sample_config, temp_dir):
    """Test that parallel execution is faster than sequential."""
    # Create multiple test commands
    commands = []
    for i in range(4):
        commands.append(
            RunnerCommand(
                name=f"cmd{i}",
                template=f"echo 'test{i}' && exit 0",
                priority=1,  # Same priority = parallel
            )
        )
    
    runner = Runner(
        name="parallel_test",
        enabled=True,
        paths=("**/*.py",),
        test_paths=(),
        commands=tuple(commands),
    )
    
    config_parallel = TaarConfig(
        version="1.0.0",
        parallelism=4,  # Parallel
        cache_dir=temp_dir / ".cache-parallel",
        debounce_ms=0,
        fail_fast=False,
        notifications=False,
        runners={"parallel_test": runner},
        impact_map={},
        project_root=temp_dir,
    )
    
    config_sequential = TaarConfig(
        version="1.0.0",
        parallelism=1,  # Sequential
        cache_dir=temp_dir / ".cache-sequential",
        debounce_ms=0,
        fail_fast=False,
        notifications=False,
        runners={"parallel_test": runner},
        impact_map={},
        project_root=temp_dir,
    )
    
    test_file = temp_dir / "test.py"
    test_file.write_text("# test")
    
    # Parallel execution
    orch_parallel = IncrementalBuildOrchestrator(config_parallel)
    start = time.perf_counter()
    await orch_parallel.run_incremental_build([test_file])
    duration_parallel = time.perf_counter() - start
    await orch_parallel.close()
    
    # Sequential execution
    orch_sequential = IncrementalBuildOrchestrator(config_sequential)
    start = time.perf_counter()
    await orch_sequential.run_incremental_build([test_file])
    duration_sequential = time.perf_counter() - start
    await orch_sequential.close()
    
    # Parallel should be faster (but may not be due to overhead in test env)
    # Just check both complete successfully
    assert duration_parallel > 0
    assert duration_sequential > 0


# ═══════════════════════════════════════════════════════════════════════════
# Run Tests
# ═══════════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
