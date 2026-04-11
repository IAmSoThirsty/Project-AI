# Temporal/Liara Test Suite

This directory contains comprehensive tests for the Temporal and Liara agent systems.

## Test Modules

### 1. Temporal Consistency Tests (`test_temporal_consistency.py`)
- **Causal Ordering**: Vector clock implementation and happens-before relationships
- **Anti-Rollback**: State version management with commit/rollback guarantees
- **Clock Synchronization**: NTP-like sync, Hybrid Logical Clocks (HLC)
- **Temporal Invariants**: Causality preservation, deterministic replay

**Key Tests:**
- `TestCausalOrdering`: Vector clocks, causal chains, multi-agent ordering
- `TestAntiRollback`: State commits, rollback prevention, concurrent appends
- `TestClockSynchronization`: Logical clocks, NTP sync, HLC implementation
- `TestTemporalInvariants`: No time travel, deterministic replay

### 2. Failover Scenarios (`test_failover_scenarios.py`)
- **Liara Takeover**: Automated failover on agent failure
- **Health Monitoring**: Heartbeat detection, timeout handling
- **Network Partitions**: Split-brain prevention, partition recovery
- **Cascading Failures**: Sequential failure handling
- **Failure Modes**: Crash, hang, slow response, resource exhaustion

**Key Tests:**
- `TestBasicFailover`: Controller initialization, failover triggers, cooldown
- `TestHeartbeatMonitoring`: Timeout detection, degradation, healthy agent tracking
- `TestNetworkPartition`: Split-brain prevention, quorum-based decisions
- `TestCascadingFailures`: Multiple sequential failures, all-agents-failed
- `TestFailoverPerformance`: Sub-100ms failover, concurrent attempts

### 3. Race Condition Tests (`test_race_conditions.py`)
- **Concurrent Access**: Thread-safe state management
- **Distributed Locks**: Mutual exclusion, deadlock prevention
- **Distributed Transactions**: 2-Phase Commit (2PC)
- **Optimistic Concurrency Control**: Version-based and timestamp-based OCC
- **Eventual Consistency**: Replica convergence

**Key Tests:**
- `TestBasicRaceConditions`: Concurrent writes, atomic increments, CAS operations
- `TestDistributedLocks`: Lock acquisition, exclusion, timeout, contention
- `TestTransactionIsolation`: Transaction lifecycle, 2PC protocol
- `TestOptimisticConcurrencyControl`: Version and timestamp-based OCC
- `TestAsyncRaceConditions`: Async concurrent updates, semaphore limiting

**ThreadSanitizer Compatible:** All tests use proper locking and synchronization primitives.

### 4. Byzantine Fault Tolerance (`test_byzantine_faults.py`)
- **Malicious Agent Detection**: Message signature verification
- **PBFT Consensus**: Practical Byzantine Fault Tolerance
- **Merkle Trees**: Data integrity verification
- **Quorum Systems**: Byzantine quorum requirements
- **State Replication**: Majority-based consensus

**Key Tests:**
- `TestByzantineAgentDetection`: Honest/Byzantine behaviors, signature verification
- `TestPBFTConsensus`: Minimum agents, consensus with Byzantine nodes
- `TestMerkleTreeVerification`: Tree construction, proof generation/verification
- `TestQuorumSystems`: Quorum intersection, Byzantine quorum
- `TestByzantineResilience`: State replication, checkpoint recovery

### 5. Performance Benchmarks (`test_performance_benchmarks.py`)
- **State Restoration**: Sub-second restoration targets
- **Consensus Latency**: Low-latency consensus (p50 < 10ms)
- **Failover Performance**: Sub-100ms failover
- **Throughput**: Operations/second metrics
- **Scalability**: Agent count and state size scaling

**Key Benchmarks:**
- `TestStateRestorationPerformance`: Sub-second restoration, concurrent operations
- `TestConsensusPerformance`: p50 < 10ms, p95 < 50ms, p99 < 100ms
- `TestFailoverPerformance`: < 100ms failover, < 500ms with state restoration
- `TestThroughputBenchmarks`: > 50 ops/sec, > 20 messages/sec
- `TestScalabilityBenchmarks`: Linear or better scaling

**Performance Targets:**
- State save: < 10ms mean
- State restore: < 5ms mean
- Large state restore: < 1000ms (sub-second)
- Consensus p50: < 10ms
- Consensus p95: < 50ms
- Consensus p99: < 100ms
- Failover: < 100ms
- Throughput: > 100 proposals/sec

## Running Tests

### Run All Temporal Tests
```bash
pytest tests/temporal/ -v
```

### Run Specific Test Module
```bash
pytest tests/temporal/test_temporal_consistency.py -v
pytest tests/temporal/test_failover_scenarios.py -v
pytest tests/temporal/test_race_conditions.py -v
pytest tests/temporal/test_byzantine_faults.py -v
pytest tests/temporal/test_performance_benchmarks.py -v
```

### Run Performance Benchmarks Only
```bash
pytest tests/temporal/test_performance_benchmarks.py -v --benchmark-only
```

### Run with Coverage
```bash
pytest tests/temporal/ --cov=cognition --cov-report=html
```

### Run with ThreadSanitizer (Linux/Mac)
```bash
# Requires tsan-enabled Python build
TSAN_OPTIONS="halt_on_error=1" pytest tests/temporal/test_race_conditions.py -v
```

### Run with Helgrind (Valgrind)
```bash
valgrind --tool=helgrind python -m pytest tests/temporal/test_race_conditions.py -v
```

## Test Categories

### Unit Tests
- Individual component testing
- Mock dependencies
- Fast execution

### Integration Tests
- Multi-component interaction
- Real dependencies (marked with `@pytest.mark.integration`)
- May require Temporal server

### Performance Tests
- Benchmark execution time
- Measure throughput/latency
- Marked with `@pytest.mark.benchmark`

### Async Tests
- Asyncio-based testing
- Marked with `@pytest.mark.asyncio`

## CI/CD Integration

### GitHub Actions Workflow
See `.github/workflows/temporal-tests.yml` for CI configuration.

### Test Stages
1. **Unit Tests**: Fast, isolated tests
2. **Integration Tests**: With Temporal server
3. **Performance Tests**: Benchmark validation
4. **Race Condition Tests**: With sanitizers (optional)

### Required Environment
- Python 3.11+
- pytest >= 7.0.0
- pytest-asyncio >= 0.21.0
- pytest-cov >= 4.0.0

### Optional Tools
- ThreadSanitizer (for race detection)
- Helgrind (Valgrind, for race detection)
- Temporal server (for integration tests)

## Architecture

### Temporal Consistency
```
Event → Vector Clock → Causal Order → State Version → Committed State
         ↓                ↓              ↓                ↓
    Happens-Before    Multi-Agent    Anti-Rollback    Immutable
```

### Failover Flow
```
Health Monitor → Heartbeat Timeout → Trigger Failover → Liara Takeover
                      ↓                    ↓                  ↓
                  Degraded            Backup Agent      State Restore
```

### Byzantine Consensus
```
Proposal → Pre-Prepare → Prepare → Commit → Execute
    ↓           ↓           ↓         ↓         ↓
 n agents   2f+1 votes  2f+1 votes  Consensus  Result
```

## Metrics and Targets

### Performance SLAs
- **State Restoration**: < 1s for any state size
- **Consensus Latency**: < 10ms (p50), < 100ms (p99)
- **Failover Time**: < 100ms
- **Throughput**: > 100 consensus rounds/sec

### Reliability
- **Fault Tolerance**: f Byzantine faults with n ≥ 3f + 1 agents
- **Availability**: 99.9% uptime with proper failover
- **Consistency**: Strong consistency (linearizability)

### Scalability
- **Agents**: Linear scaling up to 100 agents
- **State Size**: Sub-linear scaling up to 10MB states
- **Message Throughput**: > 1000 messages/sec

## Contributing

When adding new tests:
1. Follow existing naming conventions
2. Add docstrings explaining test purpose
3. Include performance targets where applicable
4. Mark integration tests appropriately
5. Update this README with new test descriptions

## References

- [Lamport Timestamps](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
- [Vector Clocks](https://en.wikipedia.org/wiki/Vector_clock)
- [PBFT Paper](http://pmg.csail.mit.edu/papers/osdi99.pdf)
- [Hybrid Logical Clocks](https://cse.buffalo.edu/tech-reports/2014-04.pdf)
- [Merkle Trees](https://en.wikipedia.org/wiki/Merkle_tree)
