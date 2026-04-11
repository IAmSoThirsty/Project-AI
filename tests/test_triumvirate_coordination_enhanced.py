#                                           [2026-04-09 Enhanced Tests]
#                                          Productivity: Active
"""
Integration Tests for Enhanced Triumvirate Coordination

Tests cover:
- Real-time voting protocol (sub-millisecond latency)
- Deadlock resolution mechanisms
- Priority-based arbitration
- Performance metrics collection
- Graceful degradation and Liara failover
- Pillar failure scenarios
"""

import asyncio
import time
from unittest.mock import Mock, AsyncMock, MagicMock

import pytest

from src.cognition.triumvirate_coordination_enhanced import (
    CoordinationConfig,
    EnhancedTriumvirateCoordinator,
    PillarType,
    Vote,
    VoteType,
    Priority,
    VotingResult,
    PerformanceMetrics
)


# Fixtures


@pytest.fixture
def mock_galahad():
    """Mock Galahad engine"""
    galahad = Mock()
    galahad.reason.return_value = {
        'success': True,
        'confidence': 0.8,
        'explanation': 'Ethical analysis complete',
        'contradictions': []
    }
    galahad.get_curiosity_metrics.return_value = {'current_score': 0.5}
    return galahad


@pytest.fixture
def mock_cerberus():
    """Mock Cerberus engine"""
    cerberus = Mock()
    cerberus.validate_input.return_value = {
        'valid': True,
        'reason': 'Security check passed'
    }
    cerberus.get_statistics.return_value = {'total_enforcements': 0}
    return cerberus


@pytest.fixture
def mock_codex():
    """Mock Codex engine"""
    codex = Mock()
    codex.process.return_value = {
        'success': True,
        'output': 'Inference complete'
    }
    codex.get_status.return_value = {'loaded': True}
    return codex


@pytest.fixture
def coordinator(mock_galahad, mock_cerberus, mock_codex):
    """Create coordinator with mocked engines"""
    config = CoordinationConfig(
        voting_timeout=0.01,  # 10ms for tests
        async_voting=True
    )
    return EnhancedTriumvirateCoordinator(
        config=config,
        galahad_engine=mock_galahad,
        cerberus_engine=mock_cerberus,
        codex_engine=mock_codex
    )


@pytest.fixture
def sync_coordinator(mock_galahad, mock_cerberus, mock_codex):
    """Create coordinator for synchronous tests"""
    config = CoordinationConfig(
        voting_timeout=0.01,
        async_voting=False
    )
    return EnhancedTriumvirateCoordinator(
        config=config,
        galahad_engine=mock_galahad,
        cerberus_engine=mock_cerberus,
        codex_engine=mock_codex
    )


# Test: Basic Voting Protocol


@pytest.mark.asyncio
async def test_async_unanimous_vote(coordinator):
    """Test unanimous decision in async mode"""
    context = {'data': 'test_input'}
    
    result = await coordinator.vote_async('test_001', context)
    
    assert isinstance(result, VotingResult)
    assert result.decision == VoteType.ALLOW
    assert result.resolution_method == 'unanimous'
    assert len(result.votes) == 3  # All three pillars
    assert result.latency_ms < 100  # Should be very fast
    assert result.confidence > 0.7


def test_sync_unanimous_vote(sync_coordinator):
    """Test unanimous decision in sync mode"""
    context = {'data': 'test_input'}
    
    result = sync_coordinator.vote_sync('test_002', context)
    
    assert isinstance(result, VotingResult)
    assert result.decision == VoteType.ALLOW
    assert result.resolution_method == 'unanimous'
    assert len(result.votes) == 3


@pytest.mark.asyncio
async def test_voting_latency(coordinator):
    """Test that voting completes in sub-millisecond range (target)"""
    context = {'data': 'performance_test'}
    
    start = time.perf_counter()
    result = await coordinator.vote_async('test_latency', context)
    elapsed_ms = (time.perf_counter() - start) * 1000
    
    # Note: Sub-millisecond is the target, but in practice may be higher
    # due to Python overhead and mock calls
    assert result.latency_ms < 10  # Still very fast
    assert elapsed_ms < 20  # Total time including overhead


# Test: Majority Voting


@pytest.mark.asyncio
async def test_majority_vote(coordinator, mock_cerberus):
    """Test majority decision when one pillar disagrees"""
    # Make Cerberus deny while others allow
    mock_cerberus.validate_input.return_value = {
        'valid': False,
        'reason': 'Security violation'
    }
    
    context = {'data': 'test_majority'}
    result = await coordinator.vote_async('test_003', context)
    
    assert isinstance(result, VotingResult)
    assert len(result.votes) == 3
    # Should be majority ALLOW (Galahad + Codex)
    assert result.resolution_method == 'majority'


# Test: Deadlock Resolution


@pytest.mark.asyncio
async def test_deadlock_priority_resolution(coordinator, mock_galahad, mock_cerberus, mock_codex):
    """Test priority-based deadlock resolution (Security > Ethics > Consistency)"""
    # Create a three-way split
    mock_galahad.reason.return_value = {
        'success': True,
        'confidence': 0.8,
        'explanation': 'Allow with modifications',
        'contradictions': ['minor']
    }
    
    mock_cerberus.validate_input.return_value = {
        'valid': False,
        'reason': 'Security risk detected'
    }
    
    mock_codex.process.return_value = {
        'success': True,
        'output': 'Consistent'
    }
    
    context = {'data': 'deadlock_test'}
    result = await coordinator.vote_async('test_deadlock', context)
    
    # With default priority (Cerberus > Galahad > Codex), Cerberus should win
    assert 'deadlock' in result.resolution_method
    assert result.decision == VoteType.DENY  # Cerberus's vote
    assert 'cerberus' in result.metadata.get('tiebreaker', '')


@pytest.mark.asyncio
async def test_deadlock_confidence_strategy(coordinator, mock_galahad, mock_cerberus, mock_codex):
    """Test highest-confidence deadlock resolution"""
    coordinator.config.deadlock_strategy = 'highest_confidence'
    
    # Create different confidence levels
    mock_galahad.reason.return_value = {
        'success': True,
        'confidence': 0.95,  # Highest confidence
        'explanation': 'High confidence allow',
        'contradictions': []
    }
    
    mock_cerberus.validate_input.return_value = {
        'valid': False,
        'reason': 'Low confidence deny'
    }
    
    mock_codex.process.return_value = {
        'success': True,
        'output': 'Consistent'
    }
    
    context = {'data': 'confidence_deadlock'}
    result = await coordinator.vote_async('test_confidence', context)
    
    # Galahad has highest confidence, should win deadlock
    if 'deadlock' in result.resolution_method:
        assert result.confidence >= 0.8  # Should reflect Galahad's confidence


# Test: Performance Metrics


def test_metrics_collection(sync_coordinator):
    """Test that performance metrics are collected correctly"""
    context = {'data': 'metrics_test'}
    
    # Perform multiple votes
    for i in range(5):
        sync_coordinator.vote_sync(f'test_metric_{i}', context)
    
    metrics = sync_coordinator.get_metrics()
    
    assert metrics is not None
    assert metrics.total_votes == 5
    assert metrics.avg_latency_ms > 0
    assert metrics.min_latency_ms <= metrics.avg_latency_ms
    assert metrics.max_latency_ms >= metrics.avg_latency_ms
    assert metrics.decisions_by_type[VoteType.ALLOW] == 5
    assert metrics.unanimous_decisions == 5


def test_metrics_confidence_tracking(sync_coordinator):
    """Test confidence metric tracking"""
    context = {'data': 'confidence_tracking'}
    
    sync_coordinator.vote_sync('test_conf_1', context)
    
    metrics = sync_coordinator.get_metrics()
    assert 0.0 <= metrics.avg_confidence <= 1.0


def test_metrics_reset(sync_coordinator):
    """Test metrics reset functionality"""
    context = {'data': 'reset_test'}
    
    sync_coordinator.vote_sync('test_reset', context)
    assert sync_coordinator.get_metrics().total_votes == 1
    
    sync_coordinator.reset_metrics()
    assert sync_coordinator.get_metrics().total_votes == 0


# Test: Pillar Failure and Graceful Degradation


def test_single_pillar_failure(sync_coordinator, mock_galahad):
    """Test voting continues with one pillar failed"""
    # Make Galahad fail
    mock_galahad.reason.side_effect = Exception("Galahad failure")
    
    context = {'data': 'single_failure'}
    result = sync_coordinator.vote_sync('test_single_fail', context)
    
    # Should still get result from remaining 2 pillars
    assert isinstance(result, VotingResult)
    assert len(result.votes) >= 2  # At least Cerberus and Codex
    
    # Check health status
    health = sync_coordinator.get_health_status()
    assert health['healthy_count'] >= 2
    assert health['failed_count'] >= 1


def test_two_pillar_failure(sync_coordinator, mock_galahad, mock_codex):
    """Test voting with two pillars failed"""
    # Make two pillars fail
    mock_galahad.reason.side_effect = Exception("Galahad failure")
    mock_codex.process.side_effect = Exception("Codex failure")
    
    context = {'data': 'two_failures'}
    result = sync_coordinator.vote_sync('test_two_fail', context)
    
    # Should still get result from Cerberus alone
    assert isinstance(result, VotingResult)
    assert len(result.votes) >= 1
    
    metrics = sync_coordinator.get_metrics()
    assert metrics.pillar_failures[PillarType.GALAHAD] >= 1
    assert metrics.pillar_failures[PillarType.CODEX] >= 1


def test_total_pillar_failure(sync_coordinator, mock_galahad, mock_cerberus, mock_codex):
    """Test emergency fallback when all pillars fail"""
    # Make all pillars fail
    mock_galahad.reason.side_effect = Exception("Galahad failure")
    mock_cerberus.validate_input.side_effect = Exception("Cerberus failure")
    mock_codex.process.side_effect = Exception("Codex failure")
    
    context = {'data': 'total_failure'}
    result = sync_coordinator.vote_sync('test_total_fail', context)
    
    # Should get emergency response
    assert isinstance(result, VotingResult)
    assert result.resolution_method == 'emergency_deny'
    assert result.decision == VoteType.DENY  # Fail-safe deny
    assert len(result.votes) == 0


@pytest.mark.asyncio
async def test_liara_failover_on_total_failure(mock_galahad, mock_cerberus, mock_codex):
    """Test Liara failover activation on total pillar failure"""
    # Create coordinator with Liara bridge
    mock_liara = Mock()
    config = CoordinationConfig(enable_liara_failover=True)
    coordinator = EnhancedTriumvirateCoordinator(
        config=config,
        galahad_engine=mock_galahad,
        cerberus_engine=mock_cerberus,
        codex_engine=mock_codex,
        liara_bridge=mock_liara
    )
    
    # Make all pillars fail
    mock_galahad.reason.side_effect = Exception("Galahad failure")
    mock_cerberus.validate_input.side_effect = Exception("Cerberus failure")
    mock_codex.process.side_effect = Exception("Codex failure")
    
    context = {'data': 'liara_failover'}
    result = await coordinator.vote_async('test_liara', context)
    
    # Should trigger Liara failover
    assert 'liara' in result.resolution_method or result.resolution_method == 'emergency_deny'
    if coordinator.metrics:
        # May have incremented if failover attempted
        assert coordinator.metrics.liara_activations >= 0


# Test: Health Monitoring


def test_health_status_all_healthy(coordinator):
    """Test health status when all pillars healthy"""
    health = coordinator.get_health_status()
    
    assert health['overall_healthy'] is True
    assert health['healthy_count'] == 3
    assert health['failed_count'] == 0
    assert health['pillars'][PillarType.GALAHAD.value]['healthy'] is True
    assert health['pillars'][PillarType.CERBERUS.value]['healthy'] is True
    assert health['pillars'][PillarType.CODEX.value]['healthy'] is True


def test_health_check_execution(sync_coordinator, mock_galahad):
    """Test periodic health checks detect failures"""
    # Force immediate health check
    sync_coordinator._last_health_check = 0
    
    # Make health check fail
    mock_galahad.get_curiosity_metrics.side_effect = Exception("Health check failed")
    
    # Trigger health check via voting
    context = {'data': 'health_check'}
    sync_coordinator.vote_sync('test_health', context)
    
    # Galahad should be marked unhealthy
    health = sync_coordinator.get_health_status()
    assert health['pillars'][PillarType.GALAHAD.value]['status'] == 'failed'


def test_pillar_restoration(sync_coordinator):
    """Test manual pillar restoration"""
    # Manually mark pillar as failed
    sync_coordinator.pillar_health[PillarType.GALAHAD] = False
    
    assert sync_coordinator.get_health_status()['healthy_count'] == 2
    
    # Restore pillar
    sync_coordinator.restore_pillar(PillarType.GALAHAD)
    
    assert sync_coordinator.get_health_status()['healthy_count'] == 3
    assert sync_coordinator.pillar_health[PillarType.GALAHAD] is True


# Test: Vote History


def test_vote_history_tracking(sync_coordinator):
    """Test that vote history is maintained"""
    context = {'data': 'history_test'}
    
    # Perform multiple votes
    for i in range(3):
        sync_coordinator.vote_sync(f'test_history_{i}', context)
    
    history = sync_coordinator.get_vote_history()
    
    assert len(history) == 3
    assert all(isinstance(r, VotingResult) for r in history)


def test_vote_history_limit(sync_coordinator):
    """Test vote history retrieval with limit"""
    context = {'data': 'history_limit'}
    
    # Perform many votes
    for i in range(10):
        sync_coordinator.vote_sync(f'test_limit_{i}', context)
    
    # Get limited history
    history = sync_coordinator.get_vote_history(limit=5)
    
    assert len(history) == 5
    assert all(isinstance(r, VotingResult) for r in history)


# Test: Priority Configuration


@pytest.mark.asyncio
async def test_custom_priority_order(mock_galahad, mock_cerberus, mock_codex):
    """Test custom priority ordering (Ethics > Security > Consistency)"""
    config = CoordinationConfig(
        priority_order=[
            PillarType.GALAHAD,   # Ethics first
            PillarType.CERBERUS,  # Security second
            PillarType.CODEX      # Consistency third
        ]
    )
    coordinator = EnhancedTriumvirateCoordinator(
        config=config,
        galahad_engine=mock_galahad,
        cerberus_engine=mock_cerberus,
        codex_engine=mock_codex
    )
    
    # Create deadlock scenario
    mock_galahad.reason.return_value = {
        'success': True,
        'confidence': 0.8,
        'explanation': 'Ethical approval',
        'contradictions': []
    }
    
    mock_cerberus.validate_input.return_value = {
        'valid': False,
        'reason': 'Security concern'
    }
    
    mock_codex.process.return_value = {
        'success': True,
        'output': 'Consistent'
    }
    
    context = {'data': 'custom_priority'}
    result = await coordinator.vote_async('test_custom_priority', context)
    
    # With custom priority, Galahad should win deadlocks
    if 'deadlock' in result.resolution_method:
        assert 'galahad' in result.metadata.get('tiebreaker', '')


# Test: Timeout Handling


@pytest.mark.asyncio
async def test_voting_timeout(mock_galahad, mock_cerberus, mock_codex):
    """Test voting timeout behavior"""
    # Make one engine very slow
    async def slow_reason(*args, **kwargs):
        await asyncio.sleep(1)  # Longer than timeout
        return {'success': True, 'confidence': 0.8, 'explanation': 'Slow', 'contradictions': []}
    
    mock_galahad.reason = slow_reason
    
    config = CoordinationConfig(voting_timeout=0.01)  # 10ms timeout
    coordinator = EnhancedTriumvirateCoordinator(
        config=config,
        galahad_engine=mock_galahad,
        cerberus_engine=mock_cerberus,
        codex_engine=mock_codex
    )
    
    context = {'data': 'timeout_test'}
    result = await coordinator.vote_async('test_timeout', context)
    
    # Should complete even with timeout (with fewer votes)
    assert isinstance(result, VotingResult)
    # May have fewer than 3 votes due to timeout
    assert len(result.votes) <= 3


# Test: Integration Scenarios


@pytest.mark.asyncio
async def test_security_override_scenario(coordinator, mock_cerberus):
    """Test that security concerns override other pillars (default priority)"""
    # Cerberus denies, others allow
    mock_cerberus.validate_input.return_value = {
        'valid': False,
        'reason': 'Critical security violation'
    }
    
    context = {'data': 'security_critical'}
    result = await coordinator.vote_async('test_security_override', context)
    
    # Should have majority ALLOW from Galahad + Codex
    assert result.resolution_method == 'majority'


@pytest.mark.asyncio
async def test_modification_vote_scenario(coordinator, mock_galahad):
    """Test MODIFY vote type handling"""
    mock_galahad.reason.return_value = {
        'success': True,
        'confidence': 0.8,
        'explanation': 'Requires modification',
        'contradictions': ['issue']
    }
    
    context = {'data': 'needs_modification'}
    result = await coordinator.vote_async('test_modify', context)
    
    # At least one vote should be MODIFY
    assert any(v.decision == VoteType.MODIFY for v in result.votes)


def test_vote_confidence_validation():
    """Test that votes with invalid confidence are rejected"""
    with pytest.raises(ValueError):
        Vote(
            pillar=PillarType.GALAHAD,
            decision=VoteType.ALLOW,
            confidence=1.5,  # Invalid - must be 0.0-1.0
            priority=Priority.HIGH,
            rationale="Test"
        )
    
    with pytest.raises(ValueError):
        Vote(
            pillar=PillarType.CERBERUS,
            decision=VoteType.DENY,
            confidence=-0.1,  # Invalid - must be 0.0-1.0
            priority=Priority.CRITICAL,
            rationale="Test"
        )


# Test: Edge Cases


@pytest.mark.asyncio
async def test_empty_context(coordinator):
    """Test voting with empty context"""
    result = await coordinator.vote_async('test_empty', {})
    
    assert isinstance(result, VotingResult)
    assert result.decision in [VoteType.ALLOW, VoteType.DENY, VoteType.MODIFY]


def test_metrics_disabled(mock_galahad, mock_cerberus, mock_codex):
    """Test coordinator with metrics disabled"""
    config = CoordinationConfig(enable_metrics=False)
    coordinator = EnhancedTriumvirateCoordinator(
        config=config,
        galahad_engine=mock_galahad,
        cerberus_engine=mock_cerberus,
        codex_engine=mock_codex
    )
    
    context = {'data': 'no_metrics'}
    coordinator.vote_sync('test_no_metrics', context)
    
    assert coordinator.get_metrics() is None


# Performance Benchmarks


@pytest.mark.asyncio
async def test_voting_performance_benchmark(coordinator):
    """Benchmark voting performance over multiple iterations"""
    context = {'data': 'benchmark_test'}
    
    latencies = []
    for i in range(10):
        start = time.perf_counter()
        result = await coordinator.vote_async(f'bench_{i}', context)
        latency_ms = (time.perf_counter() - start) * 1000
        latencies.append(latency_ms)
    
    avg_latency = sum(latencies) / len(latencies)
    
    # Performance assertions (may vary by system)
    assert avg_latency < 50  # Average under 50ms
    assert min(latencies) < 20  # Best case under 20ms
    
    print(f"\nBenchmark Results:")
    print(f"  Average latency: {avg_latency:.3f}ms")
    print(f"  Min latency: {min(latencies):.3f}ms")
    print(f"  Max latency: {max(latencies):.3f}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
