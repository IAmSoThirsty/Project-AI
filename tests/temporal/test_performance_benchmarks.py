#                                           [2026-04-09 04:26]
#                                          Productivity: Active
"""
Performance Benchmarks

Tests verifying sub-second state restoration, low-latency consensus,
and performance characteristics of the Temporal/Liara agent system.
"""

import pytest
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor
import statistics


@dataclass
class PerformanceMetrics:
    """Performance metrics for benchmarking."""
    operation: str
    latency_ms: float
    throughput_ops_sec: float
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    min_ms: float = 0.0
    max_ms: float = 0.0
    mean_ms: float = 0.0
    stddev_ms: float = 0.0


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark."""
    name: str
    success: bool
    duration_ms: float
    metrics: PerformanceMetrics
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""


class StateRestoration:
    """Simulates state restoration for benchmarking."""
    
    def __init__(self):
        self.states: Dict[int, Dict[str, Any]] = {}
        self._lock = Lock()
    
    def save_state(self, version: int, state: Dict[str, Any]) -> None:
        """Save state snapshot."""
        with self._lock:
            self.states[version] = state.copy()
    
    def restore_state(self, version: int) -> Optional[Dict[str, Any]]:
        """Restore state from snapshot."""
        with self._lock:
            return self.states.get(version, {}).copy()
    
    def get_state_size(self, version: int) -> int:
        """Get size of state in bytes (approximate)."""
        state = self.states.get(version, {})
        return len(str(state).encode())


class ConsensusEngine:
    """Simulates consensus engine for benchmarking."""
    
    def __init__(self, num_agents: int):
        self.num_agents = num_agents
        self.quorum = (num_agents + 1) // 2 + 1
        self.votes: Dict[str, List[bool]] = {}
        self._lock = Lock()
    
    def propose(self, proposal_id: str, value: Any) -> None:
        """Submit proposal for consensus."""
        with self._lock:
            self.votes[proposal_id] = []
    
    def vote(self, proposal_id: str, vote: bool) -> None:
        """Cast vote on proposal."""
        with self._lock:
            if proposal_id in self.votes:
                self.votes[proposal_id].append(vote)
    
    def has_consensus(self, proposal_id: str) -> bool:
        """Check if consensus reached."""
        with self._lock:
            votes = self.votes.get(proposal_id, [])
            yes_votes = sum(1 for v in votes if v)
            return yes_votes >= self.quorum


class FailoverSimulator:
    """Simulates failover for performance testing."""
    
    def __init__(self):
        self.active_agent: Optional[str] = None
        self.backup_agents: List[str] = []
        self.failover_count = 0
    
    def execute_failover(self) -> float:
        """Execute failover and return latency in ms."""
        start = time.perf_counter()
        
        if self.backup_agents:
            self.active_agent = self.backup_agents.pop(0)
            self.failover_count += 1
        
        end = time.perf_counter()
        return (end - start) * 1000


def calculate_percentiles(latencies: List[float]) -> tuple:
    """Calculate percentile values."""
    if not latencies:
        return 0, 0, 0
    
    sorted_latencies = sorted(latencies)
    n = len(sorted_latencies)
    
    p50 = sorted_latencies[int(n * 0.50)]
    p95 = sorted_latencies[int(n * 0.95)]
    p99 = sorted_latencies[int(n * 0.99)]
    
    return p50, p95, p99


class TestStateRestorationPerformance:
    """Test state restoration performance."""
    
    def test_state_save_latency(self):
        """Test state save operation latency."""
        restoration = StateRestoration()
        
        state = {f"key-{i}": f"value-{i}" for i in range(1000)}
        
        latencies = []
        for i in range(100):
            start = time.perf_counter()
            restoration.save_state(i, state)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)
        
        mean_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        # Target: < 10ms for state save
        assert mean_latency < 10
        assert p95_latency < 20
    
    def test_state_restore_latency(self):
        """Test state restore operation latency."""
        restoration = StateRestoration()
        
        state = {f"key-{i}": f"value-{i}" for i in range(1000)}
        restoration.save_state(0, state)
        
        latencies = []
        for _ in range(100):
            start = time.perf_counter()
            restored = restoration.restore_state(0)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)
        
        mean_latency = statistics.mean(latencies)
        p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
        
        # Target: < 5ms for state restore
        assert mean_latency < 5
        assert p99_latency < 10
    
    def test_sub_second_state_restoration(self):
        """Test state restoration completes in sub-second time."""
        restoration = StateRestoration()
        
        # Save large state
        large_state = {f"key-{i}": f"value-{i}" * 100 for i in range(10000)}
        restoration.save_state(0, large_state)
        
        # Restore and measure
        start = time.perf_counter()
        restored = restoration.restore_state(0)
        end = time.perf_counter()
        
        latency_ms = (end - start) * 1000
        
        # Must be < 1000ms (sub-second)
        assert latency_ms < 1000
        assert len(restored) == len(large_state)
    
    def test_concurrent_state_operations(self):
        """Test concurrent state save/restore performance."""
        restoration = StateRestoration()
        
        state = {f"key-{i}": f"value-{i}" for i in range(100)}
        
        def save_states(thread_id: int, count: int):
            for i in range(count):
                restoration.save_state(thread_id * 100 + i, state)
        
        start = time.perf_counter()
        
        threads = [
            Thread(target=save_states, args=(i, 10))
            for i in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        end = time.perf_counter()
        
        total_ops = 100
        duration_s = end - start
        throughput = total_ops / duration_s
        
        # Target: > 100 ops/sec
        assert throughput > 100
    
    def test_state_size_scalability(self):
        """Test performance with different state sizes."""
        restoration = StateRestoration()
        
        sizes = [100, 1000, 10000, 100000]
        latencies = {}
        
        for size in sizes:
            state = {f"key-{i}": f"value-{i}" for i in range(size)}
            
            start = time.perf_counter()
            restoration.save_state(size, state)
            end = time.perf_counter()
            
            latencies[size] = (end - start) * 1000
        
        # Latency should scale reasonably
        assert latencies[100] < latencies[100000]
        
        # Even largest state should be quick
        assert latencies[100000] < 100  # < 100ms


class TestConsensusPerformance:
    """Test consensus operation performance."""
    
    def test_consensus_latency_small_cluster(self):
        """Test consensus latency with 5 agents."""
        engine = ConsensusEngine(num_agents=5)
        
        latencies = []
        
        for i in range(100):
            proposal_id = f"prop-{i}"
            
            start = time.perf_counter()
            
            engine.propose(proposal_id, f"value-{i}")
            
            # All agents vote yes
            for _ in range(5):
                engine.vote(proposal_id, True)
            
            has_consensus = engine.has_consensus(proposal_id)
            
            end = time.perf_counter()
            
            latencies.append((end - start) * 1000)
            assert has_consensus
        
        mean_latency = statistics.mean(latencies)
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]
        
        # Target: < 50ms for consensus
        assert mean_latency < 50
        assert p95_latency < 100
    
    def test_consensus_latency_large_cluster(self):
        """Test consensus latency with 100 agents."""
        engine = ConsensusEngine(num_agents=100)
        
        start = time.perf_counter()
        
        engine.propose("prop-1", "value")
        
        # 51 agents vote (quorum)
        for _ in range(51):
            engine.vote("prop-1", True)
        
        has_consensus = engine.has_consensus("prop-1")
        
        end = time.perf_counter()
        
        latency_ms = (end - start) * 1000
        
        assert has_consensus
        # Even with 100 agents, should be fast
        assert latency_ms < 100
    
    def test_consensus_throughput(self):
        """Test consensus throughput (proposals/sec)."""
        engine = ConsensusEngine(num_agents=5)
        
        num_proposals = 1000
        
        start = time.perf_counter()
        
        for i in range(num_proposals):
            proposal_id = f"prop-{i}"
            engine.propose(proposal_id, f"value-{i}")
            
            for _ in range(3):  # Quorum = 3
                engine.vote(proposal_id, True)
        
        end = time.perf_counter()
        
        duration_s = end - start
        throughput = num_proposals / duration_s
        
        # Target: > 100 proposals/sec
        assert throughput > 100
    
    def test_low_latency_consensus(self):
        """Test consensus achieves low latency target."""
        engine = ConsensusEngine(num_agents=7)
        
        latencies = []
        
        for i in range(50):
            proposal_id = f"prop-{i}"
            
            start = time.perf_counter()
            engine.propose(proposal_id, f"value-{i}")
            
            # Quorum votes
            for _ in range(4):
                engine.vote(proposal_id, True)
            
            engine.has_consensus(proposal_id)
            end = time.perf_counter()
            
            latencies.append((end - start) * 1000)
        
        p50, p95, p99 = calculate_percentiles(latencies)
        
        # Low latency targets
        assert p50 < 10  # < 10ms for p50
        assert p95 < 50  # < 50ms for p95
        assert p99 < 100  # < 100ms for p99
    
    @pytest.mark.asyncio
    async def test_async_consensus_performance(self):
        """Test async consensus performance."""
        class AsyncConsensus:
            def __init__(self, num_agents: int):
                self.num_agents = num_agents
                self.quorum = (num_agents + 1) // 2 + 1
                self.votes: Dict[str, List[bool]] = {}
                self._lock = asyncio.Lock()
            
            async def propose_and_vote(self, proposal_id: str) -> bool:
                async with self._lock:
                    self.votes[proposal_id] = []
                    
                    # Simulate voting
                    for _ in range(self.quorum):
                        await asyncio.sleep(0.001)
                        self.votes[proposal_id].append(True)
                    
                    return len(self.votes[proposal_id]) >= self.quorum
        
        engine = AsyncConsensus(num_agents=5)
        
        start = time.perf_counter()
        
        results = await asyncio.gather(
            *[engine.propose_and_vote(f"prop-{i}") for i in range(10)]
        )
        
        end = time.perf_counter()
        
        latency_ms = (end - start) * 1000
        
        assert all(results)
        # Async should be efficient
        assert latency_ms < 200


class TestFailoverPerformance:
    """Test failover performance."""
    
    def test_failover_latency(self):
        """Test failover completes quickly."""
        simulator = FailoverSimulator()
        
        simulator.active_agent = "agent-1"
        simulator.backup_agents = ["agent-2", "agent-3"]
        
        latencies = []
        
        for _ in range(2):
            latency = simulator.execute_failover()
            latencies.append(latency)
        
        mean_latency = statistics.mean(latencies)
        max_latency = max(latencies)
        
        # Target: < 100ms for failover
        assert mean_latency < 100
        assert max_latency < 200
    
    def test_sub_second_failover(self):
        """Test failover completes in sub-second time."""
        simulator = FailoverSimulator()
        
        simulator.active_agent = "agent-1"
        simulator.backup_agents = [f"agent-{i}" for i in range(2, 10)]
        
        start = time.perf_counter()
        
        # Execute multiple failovers
        for _ in range(5):
            simulator.execute_failover()
        
        end = time.perf_counter()
        
        total_latency_ms = (end - start) * 1000
        
        # All failovers should complete < 1 second
        assert total_latency_ms < 1000
    
    def test_failover_with_state_restoration(self):
        """Test combined failover and state restoration performance."""
        simulator = FailoverSimulator()
        restoration = StateRestoration()
        
        simulator.active_agent = "agent-1"
        simulator.backup_agents = ["agent-2"]
        
        # Save state
        state = {f"key-{i}": f"value-{i}" for i in range(1000)}
        restoration.save_state(0, state)
        
        start = time.perf_counter()
        
        # Execute failover
        simulator.execute_failover()
        
        # Restore state
        restored = restoration.restore_state(0)
        
        end = time.perf_counter()
        
        total_latency_ms = (end - start) * 1000
        
        # Combined operation should be < 500ms
        assert total_latency_ms < 500
        assert len(restored) == len(state)


class TestThroughputBenchmarks:
    """Test system throughput."""
    
    def test_operation_throughput(self):
        """Test overall system operation throughput."""
        operations_completed = [0]
        lock = Lock()
        
        def perform_operations(count: int):
            for _ in range(count):
                # Simulate operation
                time.sleep(0.001)
                with lock:
                    operations_completed[0] += 1
        
        start = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(perform_operations, 10)
                for _ in range(10)
            ]
            
            for future in futures:
                future.result()
        
        end = time.perf_counter()
        
        duration_s = end - start
        throughput = operations_completed[0] / duration_s
        
        # Target: > 50 ops/sec
        assert throughput > 50
    
    def test_message_throughput(self):
        """Test message processing throughput."""
        messages_processed = []
        
        def process_message(msg_id: int):
            # Simulate processing
            start = time.perf_counter()
            time.sleep(0.001)
            end = time.perf_counter()
            messages_processed.append((end - start) * 1000)
        
        start = time.perf_counter()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(process_message, i)
                for i in range(100)
            ]
            
            for future in futures:
                future.result()
        
        end = time.perf_counter()
        
        duration_s = end - start
        throughput = len(messages_processed) / duration_s
        
        # Target: > 20 messages/sec
        assert throughput > 20


class TestLatencyDistribution:
    """Test latency distribution characteristics."""
    
    def test_latency_consistency(self):
        """Test latency is consistent (low variance)."""
        latencies = []
        
        restoration = StateRestoration()
        state = {f"key-{i}": f"value-{i}" for i in range(100)}
        
        for i in range(100):
            start = time.perf_counter()
            restoration.save_state(i, state)
            end = time.perf_counter()
            latencies.append((end - start) * 1000)
        
        mean = statistics.mean(latencies)
        stddev = statistics.stdev(latencies)
        
        # Low variance indicates consistent performance
        coefficient_of_variation = stddev / mean
        
        # Target: CV < 0.5 (reasonable consistency)
        assert coefficient_of_variation < 0.5
    
    def test_tail_latency(self):
        """Test tail latency characteristics."""
        engine = ConsensusEngine(num_agents=5)
        
        latencies = []
        
        for i in range(200):
            proposal_id = f"prop-{i}"
            
            start = time.perf_counter()
            engine.propose(proposal_id, f"value-{i}")
            
            for _ in range(3):
                engine.vote(proposal_id, True)
            
            engine.has_consensus(proposal_id)
            end = time.perf_counter()
            
            latencies.append((end - start) * 1000)
        
        p50, p95, p99 = calculate_percentiles(latencies)
        
        # Tail latency should not be too much worse than median
        tail_inflation = p99 / p50
        
        # Target: p99 < 5x p50
        assert tail_inflation < 5


class TestScalabilityBenchmarks:
    """Test scalability characteristics."""
    
    def test_agent_count_scalability(self):
        """Test performance scales with agent count."""
        results = {}
        
        for num_agents in [5, 10, 20, 50]:
            engine = ConsensusEngine(num_agents=num_agents)
            
            start = time.perf_counter()
            
            engine.propose("prop-1", "value")
            
            # Quorum votes
            quorum = (num_agents + 1) // 2 + 1
            for _ in range(quorum):
                engine.vote("prop-1", True)
            
            engine.has_consensus("prop-1")
            
            end = time.perf_counter()
            
            results[num_agents] = (end - start) * 1000
        
        # Latency should increase roughly linearly or better
        # Not exponentially
        assert results[50] < results[5] * 20
    
    def test_state_size_scalability(self):
        """Test performance scales with state size."""
        restoration = StateRestoration()
        
        results = {}
        
        for size in [100, 1000, 10000]:
            state = {f"key-{i}": f"value-{i}" for i in range(size)}
            
            start = time.perf_counter()
            restoration.save_state(size, state)
            end = time.perf_counter()
            
            results[size] = (end - start) * 1000
        
        # Should scale sub-linearly due to efficiency
        growth_factor = results[10000] / results[100]
        
        # 100x data should not take 100x time
        assert growth_factor < 50


class TestBenchmarkReporting:
    """Test benchmark result reporting."""
    
    def test_metrics_calculation(self):
        """Test performance metrics calculation."""
        latencies = [10, 20, 15, 25, 30, 18, 22, 28, 16, 24]
        
        p50, p95, p99 = calculate_percentiles(latencies)
        mean = statistics.mean(latencies)
        stddev = statistics.stdev(latencies)
        
        metrics = PerformanceMetrics(
            operation="test",
            latency_ms=mean,
            throughput_ops_sec=1000 / mean,
            p50_ms=p50,
            p95_ms=p95,
            p99_ms=p99,
            min_ms=min(latencies),
            max_ms=max(latencies),
            mean_ms=mean,
            stddev_ms=stddev
        )
        
        assert metrics.p50_ms > 0
        assert metrics.p95_ms > metrics.p50_ms
        assert metrics.p99_ms >= metrics.p95_ms
        assert metrics.max_ms >= metrics.p99_ms
    
    def test_benchmark_result_creation(self):
        """Test benchmark result creation."""
        metrics = PerformanceMetrics(
            operation="state_restore",
            latency_ms=5.2,
            throughput_ops_sec=192.3,
            p50_ms=4.8,
            p95_ms=6.1,
            p99_ms=7.5
        )
        
        result = BenchmarkResult(
            name="State Restoration Benchmark",
            success=True,
            duration_ms=5.2,
            metrics=metrics,
            notes="All targets met"
        )
        
        assert result.success
        assert result.metrics.latency_ms < 10
        assert result.timestamp is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--benchmark-only"])
