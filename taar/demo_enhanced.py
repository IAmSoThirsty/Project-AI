#!/usr/bin/env python3
"""
TAAR Enhanced Build System - Demo & Test Script

Demonstrates all features:
1. Distributed caching with local cache server
2. Dependency graph visualization
3. Incremental builds
4. Build analytics
5. Performance improvements
"""

import asyncio
import json
import os
import shutil
import tempfile
import time
from pathlib import Path

# Setup test environment
TEST_DIR = Path(tempfile.mkdtemp(prefix="taar_demo_"))
print(f"📁 Test directory: {TEST_DIR}")

# Create a simple Python project structure
(TEST_DIR / "src").mkdir()
(TEST_DIR / "tests").mkdir()
(TEST_DIR / ".taar-cache").mkdir()

# Create sample Python files
(TEST_DIR / "src" / "math_utils.py").write_text("""
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
""")

(TEST_DIR / "src" / "string_utils.py").write_text("""
def uppercase(s):
    return s.upper()

def lowercase(s):
    return s.lower()
""")

(TEST_DIR / "tests" / "test_math_utils.py").write_text("""
from src.math_utils import add, multiply

def test_add():
    assert add(2, 3) == 5

def test_multiply():
    assert multiply(2, 3) == 6
""")

(TEST_DIR / "tests" / "test_string_utils.py").write_text("""
from src.string_utils import uppercase, lowercase

def test_uppercase():
    assert uppercase("hello") == "HELLO"

def test_lowercase():
    assert lowercase("HELLO") == "hello"
""")

# Create taar.toml configuration
(TEST_DIR / "taar.toml").write_text("""
[taar]
version = "1.0.0"
parallelism = 4
cache_dir = ".taar-cache"
debounce_ms = 100
fail_fast = false
notifications = true

[taar.runners.python]
enabled = true
paths = ["src/**/*.py"]
test_paths = ["tests/**/*.py"]

[taar.runners.python.commands]
lint = "echo 'Linting {files}' && sleep 0.5 && echo 'Lint passed'"
typecheck = "echo 'Type checking {files}' && sleep 1 && echo 'Type check passed'"
test = "echo 'Testing {test_files}' && sleep 2 && echo 'Tests passed'"

[taar.runners.python.priority]
lint = 1
typecheck = 2
test = 3

[taar.graph.impact]
"src/math_utils.py" = ["tests/test_math_utils.py"]
"src/string_utils.py" = ["tests/test_string_utils.py"]
""")

print("✅ Test project created")
print(f"   - src/math_utils.py")
print(f"   - src/string_utils.py")
print(f"   - tests/test_math_utils.py")
print(f"   - tests/test_string_utils.py")
print(f"   - taar.toml")

# Initialize git repo (required for change detection)
os.chdir(TEST_DIR)
os.system("git init > nul 2>&1")
os.system("git config user.email 'test@example.com'")
os.system("git config user.name 'Test User'")
os.system("git add -A")
os.system("git commit -m 'Initial commit' > nul 2>&1")
print("✅ Git repository initialized")


# ═══════════════════════════════════════════════════════════════════════════
# DEMO FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════


async def demo_1_basic_build():
    """Demo 1: Basic incremental build"""
    print("\n" + "=" * 70)
    print("DEMO 1: Basic Incremental Build")
    print("=" * 70)
    
    # Import here to use test directory
    os.chdir(TEST_DIR)
    from taar.build_enhanced import IncrementalBuildOrchestrator
    from taar.config import load_config
    
    config = load_config(TEST_DIR)
    orchestrator = IncrementalBuildOrchestrator(config)
    
    # Modify one file
    print("\n📝 Modifying src/math_utils.py...")
    (TEST_DIR / "src" / "math_utils.py").write_text("""
def add(a, b):
    '''Add two numbers'''
    return a + b

def multiply(a, b):
    '''Multiply two numbers'''
    return a * b

def subtract(a, b):
    '''Subtract two numbers'''
    return a - b
""")
    
    # Run incremental build
    metrics = await orchestrator.run_incremental_build()
    
    print(f"\n✨ Results:")
    print(f"   Duration: {metrics.total_duration:.2f}s")
    print(f"   Tasks: {metrics.total_tasks} ({metrics.executed_tasks} executed, {metrics.cached_tasks} cached)")
    print(f"   Cache Hit Rate: {metrics.cache_hit_rate:.1f}%")
    print(f"   Success Rate: {metrics.success_rate:.1f}%")
    
    await orchestrator.close()
    return metrics


async def demo_2_full_build_then_incremental():
    """Demo 2: Full build, then incremental to show caching"""
    print("\n" + "=" * 70)
    print("DEMO 2: Full Build → Incremental Build (Caching Demo)")
    print("=" * 70)
    
    os.chdir(TEST_DIR)
    from taar.build_enhanced import IncrementalBuildOrchestrator
    from taar.config import load_config
    
    config = load_config(TEST_DIR)
    
    # Full build
    print("\n🔨 Running FULL build...")
    orchestrator1 = IncrementalBuildOrchestrator(config)
    metrics1 = await orchestrator1.run_incremental_build(full_build=True)
    await orchestrator1.close()
    
    print(f"\n✨ Full Build Results:")
    print(f"   Duration: {metrics1.total_duration:.2f}s")
    print(f"   Executed: {metrics1.executed_tasks} tasks")
    
    # Wait a bit
    await asyncio.sleep(1)
    
    # Incremental build (no changes - should be all cached)
    print("\n🔨 Running INCREMENTAL build (no changes)...")
    orchestrator2 = IncrementalBuildOrchestrator(config)
    metrics2 = await orchestrator2.run_incremental_build()
    await orchestrator2.close()
    
    print(f"\n✨ Incremental Build Results:")
    print(f"   Duration: {metrics2.total_duration:.2f}s")
    print(f"   Cached: {metrics2.cached_tasks} tasks")
    print(f"   Cache Hit Rate: {metrics2.cache_hit_rate:.1f}%")
    print(f"   Speedup: {metrics1.total_duration / max(0.1, metrics2.total_duration):.1f}x faster")


async def demo_3_distributed_cache():
    """Demo 3: Distributed cache with local server"""
    print("\n" + "=" * 70)
    print("DEMO 3: Distributed Cache")
    print("=" * 70)
    
    os.chdir(TEST_DIR)
    from taar.build_enhanced import (
        IncrementalBuildOrchestrator,
        RemoteCacheConfig,
        start_cache_server,
    )
    from taar.config import load_config
    
    # Start cache server in background
    print("\n🌐 Starting cache server on port 8765...")
    start_cache_server(port=8765)
    await asyncio.sleep(1)
    print("✅ Cache server running")
    
    # Clear local cache to force remote fetch
    local_cache_dir = TEST_DIR / ".taar-cache" / "results"
    if local_cache_dir.exists():
        shutil.rmtree(local_cache_dir)
        local_cache_dir.mkdir(parents=True)
    
    # Run build with remote cache
    print("\n🔨 Running build with remote cache...")
    config = load_config(TEST_DIR)
    remote_config = RemoteCacheConfig(
        enabled=True,
        backend="http",
        url="http://localhost:8765",
        compression=True,
    )
    
    orchestrator = IncrementalBuildOrchestrator(config, remote_config)
    
    # Modify a file
    (TEST_DIR / "src" / "string_utils.py").write_text("""
def uppercase(s):
    '''Convert to uppercase'''
    return s.upper()

def lowercase(s):
    '''Convert to lowercase'''
    return s.lower()

def titlecase(s):
    '''Convert to titlecase'''
    return s.title()
""")
    
    metrics = await orchestrator.run_incremental_build()
    
    print(f"\n✨ Results:")
    print(f"   Duration: {metrics.total_duration:.2f}s")
    print(f"   Cache Hit Rate: {metrics.cache_hit_rate:.1f}%")
    
    if metrics.remote_cache_metrics:
        rcm = metrics.remote_cache_metrics
        print(f"\n🌐 Remote Cache Metrics:")
        print(f"   Uploads: {rcm.uploads} ({rcm.upload_bytes / 1024:.1f} KB)")
        print(f"   Downloads: {rcm.downloads} ({rcm.download_bytes / 1024:.1f} KB)")
        if rcm.upload_time > 0:
            print(f"   Upload Speed: {rcm.upload_speed_mbps:.2f} MB/s")
        if rcm.download_time > 0:
            print(f"   Download Speed: {rcm.download_speed_mbps:.2f} MB/s")
    
    await orchestrator.close()


async def demo_4_graph_visualization():
    """Demo 4: Dependency graph visualization"""
    print("\n" + "=" * 70)
    print("DEMO 4: Dependency Graph Visualization")
    print("=" * 70)
    
    os.chdir(TEST_DIR)
    from taar.build_enhanced import GraphVisualizer, IncrementalBuildOrchestrator
    from taar.config import load_config
    from taar.graph import analyze_impact
    
    config = load_config(TEST_DIR)
    
    # Modify multiple files
    print("\n📝 Modifying multiple files...")
    (TEST_DIR / "src" / "math_utils.py").write_text("""
def add(a, b):
    return a + b

def divide(a, b):
    return a / b if b != 0 else None
""")
    
    (TEST_DIR / "src" / "string_utils.py").write_text("""
def uppercase(s):
    return s.upper()

def reverse(s):
    return s[::-1]
""")
    
    # Detect changes
    from taar.change_detector import detect_uncommitted_changes
    changes = detect_uncommitted_changes(TEST_DIR)
    changed_files = list(changes.all_changed)
    
    print(f"   Changed files: {len(changed_files)}")
    for f in changed_files:
        print(f"     - {f.relative_to(TEST_DIR)}")
    
    # Analyze impact
    impact = analyze_impact(changed_files, config)
    print(f"\n🎯 Impact Analysis:")
    print(f"   Affected runners: {', '.join(impact.runner_names)}")
    print(f"   Extra test files: {len(impact.extra_test_files)}")
    
    # Generate visualizations
    viz_dir = TEST_DIR / ".taar-cache" / "visualizations" / "demo"
    visualizer = GraphVisualizer(config)
    viz_paths = visualizer.visualize(changed_files, impact, viz_dir)
    
    print(f"\n📈 Generated Visualizations:")
    for viz_type, path in viz_paths.items():
        print(f"   {viz_type.upper()}: {path.relative_to(TEST_DIR)}")
    
    # Show graph data
    graph_json = viz_dir / "graph_data.json"
    with open(graph_json) as f:
        graph_data = json.load(f)
    
    print(f"\n📊 Graph Structure:")
    print(f"   Nodes: {len(graph_data['nodes'])}")
    print(f"   Edges: {len(graph_data['edges'])}")
    
    for node in graph_data['nodes']:
        print(f"     [{node['type']}] {node['label']}")


async def demo_5_analytics_dashboard():
    """Demo 5: Build analytics dashboard"""
    print("\n" + "=" * 70)
    print("DEMO 5: Build Analytics Dashboard")
    print("=" * 70)
    
    os.chdir(TEST_DIR)
    from taar.build_enhanced import IncrementalBuildOrchestrator
    from taar.config import load_config
    
    config = load_config(TEST_DIR)
    
    # Run multiple builds to generate history
    print("\n🔨 Running multiple builds to generate analytics...")
    
    for i in range(3):
        print(f"\n   Build {i + 1}/3...")
        orchestrator = IncrementalBuildOrchestrator(config)
        
        # Modify file
        (TEST_DIR / "src" / "math_utils.py").write_text(f"""
def add(a, b):
    '''Version {i + 1}'''
    return a + b

def multiply(a, b):
    return a * b
""")
        
        await orchestrator.run_incremental_build()
        await orchestrator.close()
        await asyncio.sleep(0.5)
    
    # Generate dashboard
    print("\n📊 Generating analytics dashboard...")
    orchestrator = IncrementalBuildOrchestrator(config)
    dashboard_path = orchestrator.analytics.save_dashboard()
    
    print(f"\n✨ Dashboard generated:")
    print(f"   Path: {dashboard_path.relative_to(TEST_DIR)}")
    print(f"   Size: {dashboard_path.stat().st_size / 1024:.1f} KB")
    
    # Show analytics summary
    history = orchestrator.analytics.get_build_history()
    print(f"\n📈 Analytics Summary:")
    print(f"   Total builds: {len(history)}")
    
    if history:
        latest = history[-1]
        print(f"\n   Latest Build:")
        print(f"     Duration: {latest.total_duration:.2f}s")
        print(f"     Cache Hit Rate: {latest.cache_hit_rate:.1f}%")
        print(f"     Success Rate: {latest.success_rate:.1f}%")
        print(f"     Incremental Savings: {latest.incremental_savings:.2f}s")
        
        print(f"\n   Runner Stats:")
        for runner, stats in latest.runner_stats.items():
            print(f"     {runner}:")
            print(f"       Tasks: {stats['tasks']}")
            print(f"       Avg Duration: {stats.get('avg_duration', 0):.2f}s")
            print(f"       Cache Hit: {stats.get('cache_hit_rate', 0):.1f}%")
    
    await orchestrator.close()


async def demo_6_performance_comparison():
    """Demo 6: Performance comparison (simulated)"""
    print("\n" + "=" * 70)
    print("DEMO 6: Performance Comparison")
    print("=" * 70)
    
    os.chdir(TEST_DIR)
    from taar.build_enhanced import IncrementalBuildOrchestrator
    from taar.config import load_config
    
    config = load_config(TEST_DIR)
    
    print("\n🏁 Simulating build scenarios...")
    
    # Scenario 1: Full build (first time)
    print("\n1️⃣ Full Build (cold cache)")
    orch1 = IncrementalBuildOrchestrator(config)
    metrics1 = await orch1.run_incremental_build(full_build=True)
    await orch1.close()
    
    # Scenario 2: Incremental build (one file changed)
    print("\n2️⃣ Incremental Build (1 file changed)")
    (TEST_DIR / "src" / "math_utils.py").write_text("""
def add(a, b):
    return a + b + 1  # Bug introduced
""")
    orch2 = IncrementalBuildOrchestrator(config)
    metrics2 = await orch2.run_incremental_build()
    await orch2.close()
    
    # Scenario 3: No changes (100% cached)
    print("\n3️⃣ Incremental Build (no changes)")
    orch3 = IncrementalBuildOrchestrator(config)
    metrics3 = await orch3.run_incremental_build()
    await orch3.close()
    
    # Comparison table
    print("\n" + "=" * 70)
    print("PERFORMANCE COMPARISON")
    print("=" * 70)
    print(f"{'Scenario':<30} {'Duration':<12} {'Cache Hit':<12} {'Speedup':<12}")
    print("-" * 70)
    print(f"{'Full Build (cold cache)':<30} {metrics1.total_duration:<12.2f} {metrics1.cache_hit_rate:<12.1f} {'1.0x':<12}")
    print(f"{'Incremental (1 file)':<30} {metrics2.total_duration:<12.2f} {metrics2.cache_hit_rate:<12.1f} {(metrics1.total_duration / max(0.1, metrics2.total_duration)):<12.1f}x")
    print(f"{'Incremental (no changes)':<30} {metrics3.total_duration:<12.2f} {metrics3.cache_hit_rate:<12.1f} {(metrics1.total_duration / max(0.1, metrics3.total_duration)):<12.1f}x")
    print("=" * 70)
    
    avg_speedup = (
        (metrics1.total_duration / max(0.1, metrics2.total_duration)) +
        (metrics1.total_duration / max(0.1, metrics3.total_duration))
    ) / 2
    
    print(f"\n🚀 Average Speedup: {avg_speedup:.1f}x faster")


# ═══════════════════════════════════════════════════════════════════════════
# MAIN DEMO RUNNER
# ═══════════════════════════════════════════════════════════════════════════


async def run_all_demos():
    """Run all demos in sequence"""
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  TAAR Enhanced Build System - Comprehensive Demo".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    demos = [
        ("Basic Incremental Build", demo_1_basic_build),
        ("Full → Incremental (Caching)", demo_2_full_build_then_incremental),
        ("Distributed Cache", demo_3_distributed_cache),
        ("Dependency Graph Visualization", demo_4_graph_visualization),
        ("Analytics Dashboard", demo_5_analytics_dashboard),
        ("Performance Comparison", demo_6_performance_comparison),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            print(f"\n\n{'=' * 70}")
            print(f"Running Demo {i}/{len(demos)}: {name}")
            print(f"{'=' * 70}")
            await demo_func()
            print(f"\n✅ Demo {i} completed successfully")
        except Exception as e:
            print(f"\n❌ Demo {i} failed: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  All Demos Completed!".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    print(f"\n📁 Test artifacts in: {TEST_DIR}")
    print(f"\n📊 View dashboard: {TEST_DIR / '.taar-cache' / 'analytics' / 'dashboard.html'}")
    print(f"📈 View graph: {TEST_DIR / '.taar-cache' / 'visualizations' / 'demo' / 'graph_interactive.html'}")
    
    print("\n🧹 Cleanup:")
    print(f"   rm -rf {TEST_DIR}")


if __name__ == "__main__":
    try:
        asyncio.run(run_all_demos())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    finally:
        print(f"\n📁 Test directory: {TEST_DIR}")
        print("   (Not automatically deleted - review artifacts before cleanup)")
