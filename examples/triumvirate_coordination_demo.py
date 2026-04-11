#                                           [2026-04-09 Enhanced Demo]
#                                          Productivity: Active
"""
Enhanced Triumvirate Coordination Demo

Demonstrates the key features of the enhanced coordination system:
- Real-time voting protocol
- Deadlock resolution
- Priority-based arbitration
- Performance monitoring
- Graceful degradation
"""

import asyncio
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cognition.triumvirate_coordination_enhanced import (
    CoordinationConfig,
    EnhancedTriumvirateCoordinator,
    PillarType,
    VoteType,
    Priority
)
from src.cognition.galahad.engine import GalahadEngine, GalahadConfig
from src.cognition.cerberus.engine import CerberusEngine, CerberusConfig
from src.cognition.codex.engine import CodexEngine, CodexConfig


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_vote_result(result):
    """Print voting result in readable format"""
    print(f"\n  Decision: {result.decision.value}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Latency: {result.latency_ms:.3f}ms")
    print(f"  Resolution: {result.resolution_method}")
    print(f"  Participating Pillars: {[p.value for p in result.participating_pillars]}")
    
    if result.votes:
        print(f"\n  Individual Votes:")
        for vote in result.votes:
            print(f"    - {vote.pillar.value}: {vote.decision.value} "
                  f"(confidence={vote.confidence:.2f}, priority={vote.priority.name})")
            print(f"      Rationale: {vote.rationale}")


def demo_basic_voting():
    """Demonstrate basic voting protocol"""
    print_section("Demo 1: Basic Unanimous Voting")
    
    # Create engines
    galahad = GalahadEngine(GalahadConfig())
    cerberus = CerberusEngine(CerberusConfig())
    codex = CodexEngine(CodexConfig())
    
    # Create coordinator
    config = CoordinationConfig()
    coordinator = EnhancedTriumvirateCoordinator(
        config=config,
        galahad_engine=galahad,
        cerberus_engine=cerberus,
        codex_engine=codex
    )
    
    # Perform vote
    print("\nPerforming vote on normal request...")
    context = {
        'data': 'Process this request',
        'user_id': 'user_123',
        'action': 'read'
    }
    
    result = coordinator.vote_sync('demo_001', context)
    print_vote_result(result)
    
    # Show health status
    print("\n  Pillar Health Status:")
    health = coordinator.get_health_status()
    for pillar, status in health['pillars'].items():
        print(f"    - {pillar}: {status['status']}")


def demo_performance_monitoring():
    """Demonstrate performance metrics collection"""
    print_section("Demo 2: Performance Monitoring")
    
    galahad = GalahadEngine(GalahadConfig())
    cerberus = CerberusEngine(CerberusConfig())
    codex = CodexEngine(CodexConfig())
    
    coordinator = EnhancedTriumvirateCoordinator(
        config=CoordinationConfig(enable_metrics=True),
        galahad_engine=galahad,
        cerberus_engine=cerberus,
        codex_engine=codex
    )
    
    print("\nPerforming 10 votes to collect metrics...")
    
    for i in range(10):
        context = {'data': f'Request {i}', 'batch': 'performance_test'}
        coordinator.vote_sync(f'perf_{i}', context)
    
    # Display metrics
    metrics = coordinator.get_metrics()
    print(f"\n  Performance Metrics:")
    print(f"    Total Votes: {metrics.total_votes}")
    print(f"    Average Latency: {metrics.avg_latency_ms:.3f}ms")
    print(f"    Min Latency: {metrics.min_latency_ms:.3f}ms")
    print(f"    Max Latency: {metrics.max_latency_ms:.3f}ms")
    print(f"    Average Confidence: {metrics.avg_confidence:.2f}")
    
    print(f"\n  Decisions by Type:")
    for decision_type, count in metrics.decisions_by_type.items():
        if count > 0:
            print(f"    - {decision_type.value}: {count}")
    
    print(f"\n  Quality Metrics:")
    print(f"    Unanimous Decisions: {metrics.unanimous_decisions}")
    print(f"    Deadlocks Resolved: {metrics.deadlocks_resolved}")
    print(f"    Priority Overrides: {metrics.priority_overrides}")


async def demo_async_voting():
    """Demonstrate asynchronous voting for low latency"""
    print_section("Demo 3: Asynchronous Voting (Sub-millisecond target)")
    
    galahad = GalahadEngine(GalahadConfig())
    cerberus = CerberusEngine(CerberusConfig())
    codex = CodexEngine(CodexConfig())
    
    config = CoordinationConfig(
        async_voting=True,
        voting_timeout=0.001  # 1ms timeout
    )
    
    coordinator = EnhancedTriumvirateCoordinator(
        config=config,
        galahad_engine=galahad,
        cerberus_engine=cerberus,
        codex_engine=codex
    )
    
    print("\nPerforming async vote with sub-millisecond target...")
    
    context = {
        'data': 'High-priority request',
        'priority': 'critical',
        'async': True
    }
    
    start = time.perf_counter()
    result = await coordinator.vote_async('async_001', context)
    total_time = (time.perf_counter() - start) * 1000
    
    print_vote_result(result)
    print(f"\n  Total Time (including overhead): {total_time:.3f}ms")


def demo_custom_priorities():
    """Demonstrate custom priority configuration"""
    print_section("Demo 4: Custom Priority Configuration")
    
    galahad = GalahadEngine(GalahadConfig())
    cerberus = CerberusEngine(CerberusConfig())
    codex = CodexEngine(CodexConfig())
    
    # Configure Ethics > Security > Consistency
    config = CoordinationConfig(
        priority_order=[
            PillarType.GALAHAD,   # Ethics first
            PillarType.CERBERUS,  # Security second
            PillarType.CODEX      # Consistency third
        ]
    )
    
    coordinator = EnhancedTriumvirateCoordinator(
        config=config,
        galahad_engine=galahad,
        cerberus_engine=cerberus,
        codex_engine=codex
    )
    
    print("\nPriority Order: Ethics > Security > Consistency")
    print("Performing vote...")
    
    context = {
        'data': 'Request with ethical implications',
        'scenario': 'custom_priority'
    }
    
    result = coordinator.vote_sync('priority_001', context)
    print_vote_result(result)
    
    print("\n  Note: In case of deadlock, Galahad (Ethics) will take precedence")


def demo_graceful_degradation():
    """Demonstrate graceful degradation with pillar failures"""
    print_section("Demo 5: Graceful Degradation")
    
    galahad = GalahadEngine(GalahadConfig())
    cerberus = CerberusEngine(CerberusConfig())
    codex = CodexEngine(CodexConfig())
    
    coordinator = EnhancedTriumvirateCoordinator(
        config=CoordinationConfig(),
        galahad_engine=galahad,
        cerberus_engine=cerberus,
        codex_engine=codex
    )
    
    print("\nInitial Health Status:")
    health = coordinator.get_health_status()
    print(f"  Healthy Pillars: {health['healthy_count']}/3")
    
    # Simulate pillar failure
    print("\nSimulating Codex pillar failure...")
    coordinator._mark_pillar_failed(PillarType.CODEX)
    
    health = coordinator.get_health_status()
    print(f"  Healthy Pillars: {health['healthy_count']}/3")
    
    # Vote still works with degraded system
    print("\nPerforming vote with degraded system...")
    context = {'data': 'Request during degradation'}
    result = coordinator.vote_sync('degraded_001', context)
    print_vote_result(result)
    
    print("\n  System continues operating with remaining healthy pillars")
    
    # Restore pillar
    print("\nRestoring Codex pillar...")
    coordinator.restore_pillar(PillarType.CODEX)
    
    health = coordinator.get_health_status()
    print(f"  Healthy Pillars: {health['healthy_count']}/3")


def demo_vote_history():
    """Demonstrate vote history tracking"""
    print_section("Demo 6: Vote History Analysis")
    
    galahad = GalahadEngine(GalahadConfig())
    cerberus = CerberusEngine(CerberusConfig())
    codex = CodexEngine(CodexConfig())
    
    coordinator = EnhancedTriumvirateCoordinator(
        config=CoordinationConfig(),
        galahad_engine=galahad,
        cerberus_engine=cerberus,
        codex_engine=codex
    )
    
    print("\nPerforming 5 votes with different contexts...")
    
    contexts = [
        {'data': 'Normal request', 'type': 'read'},
        {'data': 'Write operation', 'type': 'write'},
        {'data': 'Delete operation', 'type': 'delete'},
        {'data': 'Admin action', 'type': 'admin'},
        {'data': 'Query data', 'type': 'query'}
    ]
    
    for i, context in enumerate(contexts):
        coordinator.vote_sync(f'history_{i}', context)
    
    # Analyze history
    history = coordinator.get_vote_history(limit=5)
    
    print(f"\n  Vote History (last {len(history)} votes):")
    for i, result in enumerate(history):
        print(f"\n    Vote #{i+1}:")
        print(f"      Decision: {result.decision.value}")
        print(f"      Latency: {result.latency_ms:.3f}ms")
        print(f"      Confidence: {result.confidence:.2f}")
        print(f"      Resolution: {result.resolution_method}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  Enhanced Triumvirate Coordination - Feature Demonstration")
    print("=" * 70)
    
    # Synchronous demos
    demo_basic_voting()
    demo_performance_monitoring()
    demo_custom_priorities()
    demo_graceful_degradation()
    demo_vote_history()
    
    # Async demo
    print_section("Demo 3: Asynchronous Voting")
    print("\nRunning async demo...")
    asyncio.run(demo_async_voting())
    
    print("\n" + "=" * 70)
    print("  All Demos Complete!")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✓ Real-time voting protocol")
    print("  ✓ Sub-millisecond latency target (async mode)")
    print("  ✓ Priority-based arbitration (configurable)")
    print("  ✓ Performance metrics collection")
    print("  ✓ Graceful degradation")
    print("  ✓ Vote history tracking")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
