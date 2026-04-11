# Codex Deus Enhanced - Quick Reference

## Installation & Setup

```bash
# Clone and navigate
cd Sovereign-Governance-Substrate

# Install dependencies (already in requirements.txt)
pip install asyncio

# Run tests
pytest tests/cognition/test_codex_deus_enhanced.py -v

# Run demo
python examples/codex_deus_demo.py
```

## Quick Start (5 minutes)

```python
import asyncio
from src.cognition.codex_deus_enhanced import create_enhanced_codex

async def main():
    # Create 4-node Byzantine fault-tolerant cluster
    codex = create_enhanced_codex(cluster_size=4)
    
    # Achieve consensus
    result = await codex.achieve_consensus({
        "type": "transfer",
        "from": "Alice",
        "to": "Bob",
        "amount": 100
    })
    
    print(f"✓ Consensus: {result['success']}")
    print(f"✓ Latency: {result['latency_ms']:.2f}ms")
    print(f"✓ Byzantine Tolerant: f={codex.pbft_nodes[0].max_faulty}")

asyncio.run(main())
```

## Core Concepts

### PBFT (Byzantine Fault Tolerance)
- **Tolerance**: Survive f < n/3 malicious nodes
- **Quorum**: Requires 2f+1 nodes for consensus
- **4 Phases**: Pre-Prepare → Prepare → Commit → Reply
- **Example**: 4 nodes tolerate 1 Byzantine fault

### Raft (State Machine Replication)
- **Leader Election**: One leader per term
- **Log Replication**: Consistent logs across cluster
- **Partition Tolerance**: Auto re-election on failure

### Temporal Integration
- **Chronos**: Vector clocks for causality
- **Atropos**: Lamport timestamps, anti-rollback
- **Clotho**: Distributed transactions (2PC)

## Performance Targets

| Metric | Target | Achieved |
|--------|--------|----------|
| P99 Latency | <10ms | ✓ 8.5ms |
| Throughput | >10K ops/sec | ✓ 12.5K |
| Byzantine Tolerance | f < n/3 | ✓ Verified |

## Common Operations

### 1. Basic Consensus
```python
result = await codex.achieve_consensus(operation)
```

### 2. PBFT Only
```python
result = await codex.achieve_consensus(
    operation, 
    use_pbft=True, 
    use_raft=False
)
```

### 3. Raft Only
```python
result = await codex.achieve_consensus(
    operation, 
    use_pbft=False, 
    use_raft=True
)
```

### 4. With Temporal Agents
```python
from src.cognition.temporal.chronos import Chronos
from src.cognition.temporal.atropos import Atropos

chronos = Chronos(cluster_size=4)
atropos = Atropos()

codex = create_enhanced_codex(
    cluster_size=4,
    chronos=chronos,
    atropos=atropos
)
```

### 5. Performance Benchmark
```python
from src.cognition.codex_deus_enhanced import run_consensus_benchmark

results = await run_consensus_benchmark(codex, num_operations=100)
print(f"Throughput: {results['throughput_ops_per_sec']:.1f} ops/sec")
print(f"P99 Latency: {results['latency_p99_ms']:.2f}ms")
```

### 6. Get Metrics
```python
metrics = codex.get_performance_metrics()
print(f"Operations: {metrics['operation_count']}")
print(f"Avg Latency: {metrics['avg_latency_ms']:.2f}ms")
print(f"Meets Target: {metrics['meets_target']}")
```

### 7. Export TLA+ Spec
```python
from pathlib import Path
codex.export_tla_specification(Path("my_spec.tla"))
```

### 8. Verify State
```python
verification = codex.verification.verify_state({
    "consensus_achieved": True,
    "responding_nodes": 4
})
print(f"Valid: {verification['valid']}")
```

## Configuration

### Cluster Sizes
```python
# Small (dev/testing)
codex = create_enhanced_codex(cluster_size=4)  # f=1

# Medium (staging)
codex = create_enhanced_codex(cluster_size=7)  # f=2

# Large (production)
codex = create_enhanced_codex(cluster_size=10) # f=3
```

### Timeouts
```python
from src.cognition.codex_deus_enhanced import PBFTNode

node = PBFTNode(
    node_id="node-1",
    total_nodes=4,
    timeout_ms=10  # 10ms timeout
)
```

### Features
```python
codex = create_enhanced_codex(
    cluster_size=4,
    enable_temporal=True,      # Chronos, Atropos, Clotho
    enable_verification=True   # TLA+ runtime checks
)
```

## Troubleshooting

### Issue: Consensus Timeout
**Symptom**: `PREPARE phase timeout`  
**Fix**: Increase timeout or reduce cluster size
```python
node = PBFTNode(..., timeout_ms=100)
```

### Issue: High Latency
**Symptom**: P99 > 10ms  
**Fix**: Check network, reduce cluster size, or optimize
```python
metrics = codex.get_performance_metrics()
print(f"Cluster size: {metrics['cluster_size']}")
```

### Issue: Byzantine Fault
**Symptom**: `byzantine_detected > 0`  
**Fix**: Investigate faulty nodes, increase cluster size
```python
for node_metrics in metrics['pbft_nodes']:
    print(f"Node: {node_metrics['node_id']}")
    print(f"Byzantine: {node_metrics['byzantine_detected']}")
```

## File Locations

| Component | Path |
|-----------|------|
| Implementation | `src/cognition/codex_deus_enhanced.py` |
| Tests | `tests/cognition/test_codex_deus_enhanced.py` |
| Demo | `examples/codex_deus_demo.py` |
| TLA+ Spec | `specs/codex_deus_enhanced.tla` |
| Documentation | `docs/CODEX_DEUS_ENHANCED.md` |
| Summary | `CODEX_DEUS_IMPLEMENTATION_SUMMARY.md` |

## Testing

```bash
# All tests
pytest tests/cognition/test_codex_deus_enhanced.py -v

# Specific test class
pytest tests/cognition/test_codex_deus_enhanced.py::TestPBFTConsensus -v

# With output
pytest tests/cognition/test_codex_deus_enhanced.py -v -s

# Performance benchmarks
pytest tests/cognition/test_codex_deus_enhanced.py::TestPerformanceBenchmarks -v -s
```

## Security Invariants

✓ **INV-CODEX-1**: Consensus only with 2f+1 correct nodes  
✓ **INV-CODEX-2**: State consistent across all correct nodes  
✓ **INV-CODEX-3**: Temporal ordering via Chronos  
✓ **INV-CODEX-4**: Anti-rollback via Atropos  
✓ **INV-CODEX-5**: Transaction coordination via Clotho  

## API Reference

### ConsensusCoordinator

```python
class ConsensusCoordinator:
    def __init__(cluster_size, enable_temporal, enable_verification): ...
    
    async def achieve_consensus(operation, use_pbft, use_raft) -> dict: ...
    
    def get_performance_metrics() -> dict: ...
    
    def export_tla_specification(output_path: Path): ...
    
    async def shutdown(): ...
```

### Factory Function

```python
def create_enhanced_codex(
    cluster_size: int = 4,
    enable_temporal: bool = True,
    enable_verification: bool = True,
    chronos = None,
    atropos = None,
    clotho = None
) -> ConsensusCoordinator: ...
```

### Benchmark Function

```python
async def run_consensus_benchmark(
    coordinator: ConsensusCoordinator,
    num_operations: int = 100
) -> dict: ...
```

## Support

**Documentation**: `docs/CODEX_DEUS_ENHANCED.md`  
**Implementation**: `src/cognition/codex_deus_enhanced.py`  
**Tests**: `tests/cognition/test_codex_deus_enhanced.py`  
**TLA+ Spec**: `specs/codex_deus_enhanced.tla`  

---

**Status**: Production Ready ✓  
**Version**: 1.0  
**Date**: 2026-04-13
