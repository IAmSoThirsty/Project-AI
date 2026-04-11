# OCTOREFLEX Test Suite

Comprehensive test coverage for the OCTOREFLEX reflexive containment system.

## Test Categories

### 1. Unit Tests (90%+ coverage target)

Located in `internal/*/` alongside source files.

**Modules covered:**
- `internal/anomaly/` - Anomaly detection engine, entropy, Mahalanobis distance
- `internal/budget/` - Token bucket rate limiter
- `internal/escalation/` - State machine and severity calculation
- `internal/gossip/` - Federated gossip protocol
- `internal/governance/` - Constitutional kernel integration
- `internal/bpf/` - eBPF loader and event handling
- `internal/config/` - Configuration parsing
- `internal/storage/` - BoltDB persistence

**Run unit tests:**
```bash
go test -v -cover ./internal/...
```

**Generate coverage report:**
```bash
go test -coverprofile=coverage.out ./internal/...
go tool cover -html=coverage.out -o coverage.html
```

**Target metrics:**
- Line coverage: ≥ 90%
- Branch coverage: ≥ 85%
- Function coverage: ≥ 95%

### 2. Integration Tests

Located in `test/integration/`.

**Tests:**
- `pipeline_test.go` - Full containment pipeline (eBPF → anomaly → escalation)
- `ebpf_test.go` - eBPF program loading and LSM hook attachment
- `multinode_test.go` - Multi-node gossip quorum

**Requirements:**
- Linux kernel 5.15+ with `CONFIG_BPF_LSM=y`
- Root privileges (`sudo`)
- Compiled eBPF bytecode (`make bpf`)

**Run:**
```bash
sudo go test -v ./test/integration
```

### 3. Adversarial Tests

Located in `test/adversarial/`.

Simulates real-world attacks to verify detection and containment:

**Attack scenarios:**
- `ransomware_test.go` - Mass file encryption, high-entropy writes, file renaming
- `privilege_escalation_test.go` - setuid/setgid attempts, SUID exploits
- `network_exfiltration_test.go` - C2 beaconing, port scanning, data exfiltration
- `cryptominer_test.go` - CPU-intensive workloads, unusual system calls
- `lateral_movement_test.go` - Network scanning, SSH brute force

**Run:**
```bash
go test -v ./test/adversarial
```

**Expected behavior:**
- Containment latency < 3 seconds (spec requirement)
- No false negatives (all attacks detected)
- Minimal false positives (< 0.5%)

### 4. Fuzzing

Located in `test/fuzz/`.

Uses Go's native fuzzing framework (Go 1.18+).

**Fuzz targets:**
- `event_parser_fuzz_test.go` - eBPF event parser
- `config_parser_fuzz_test.go` - YAML configuration parser
- `proto_fuzz_test.go` - Protobuf envelope parsing

**Run fuzzing:**
```bash
go test -fuzz=FuzzEventParser -fuzztime=60s ./test/fuzz
go test -fuzz=FuzzConfigParser -fuzztime=60s ./test/fuzz
```

**AFL++ integration (for eBPF programs):**
```bash
cd bpf
afl-clang-fast -g -O2 -c octoreflex.bpf.c -o octoreflex.bpf.o
afl-fuzz -i fuzz_input -o fuzz_output -- ./harness @@
```

### 5. Formal Verification

Located in `verification/`.

Uses TLA+ for model checking critical safety properties.

**Specifications:**
- `containment.tla` - State transition monotonicity, budget enforcement, terminal states

**Verified properties:**
1. State transitions are monotonic (no rollback in kernel)
2. TERMINATED state is permanent
3. Budget exhaustion prevents escalation
4. No state value exceeds TERMINATED (5)

**Run verification:**
```bash
cd verification
java -jar tla2tools.jar -workers auto containment.tla
```

**See:** `verification/README.md` for detailed instructions.

### 6. Performance Tests

Located in `test/performance/`.

Validates latency and throughput requirements.

**Benchmarks:**
- Containment latency (p50 < 200μs, p99 < 800μs)
- Event processing throughput (> 10,000 events/sec)
- Anomaly scoring overhead
- Concurrent event processing

**Run:**
```bash
go test -bench=. -benchtime=10s ./test/performance
```

**Sample output:**
```
BenchmarkContainmentLatency-8     500000    187 μs/op  (p50: 165μs, p99: 723μs)
BenchmarkEventProcessingThroughput-8  85432 events/sec
```

### 7. Chaos Engineering

Located in `test/chaos/`.

Tests resilience under adverse conditions:

**Scenarios:**
- Event flood (backpressure handling)
- Memory exhaustion
- Goroutine exhaustion
- Random component failures
- Clock skew and time jumps
- Network partitions
- CPU starvation

**Run:**
```bash
go test -v ./test/chaos
```

## CI/CD Integration

### GitHub Actions Workflow

See `.github/workflows/test.yml`:

```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.22'
      - run: make test
      - run: make coverage
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage.out

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: make bpf
      - run: sudo go test -v ./test/integration

  adversarial-tests:
    runs-on: ubuntu-latest
    steps:
      - run: go test -v ./test/adversarial

  fuzzing:
    runs-on: ubuntu-latest
    steps:
      - run: go test -fuzz=. -fuzztime=5m ./test/fuzz
```

### Makefile Targets

```makefile
.PHONY: test test-unit test-integration test-adversarial test-all coverage

test: test-unit

test-unit:
	go test -v -race -cover ./internal/...

test-integration:
	sudo go test -v ./test/integration

test-adversarial:
	go test -v ./test/adversarial

test-fuzz:
	go test -fuzz=FuzzEventParser -fuzztime=10s ./test/fuzz

test-performance:
	go test -bench=. -benchtime=10s ./test/performance

test-chaos:
	go test -v ./test/chaos

test-all: test-unit test-integration test-adversarial test-performance

coverage:
	go test -coverprofile=coverage.out ./internal/...
	go tool cover -html=coverage.out -o coverage.html
	go tool cover -func=coverage.out | grep total
```

## Test Execution Strategy

### Pre-commit
```bash
make test-unit          # < 5 seconds
make test-adversarial   # < 30 seconds
```

### CI Pipeline
```bash
make test-unit          # All commits
make test-integration   # Pull requests only
make test-fuzz          # Nightly
```

### Pre-release
```bash
make test-all           # Full suite
make test-performance   # Verify SLAs
cd verification && make verify  # Formal verification
```

## Coverage Requirements

| Module | Line Coverage | Branch Coverage |
|--------|---------------|-----------------|
| `internal/anomaly` | ≥ 95% | ≥ 90% |
| `internal/escalation` | ≥ 95% | ≥ 90% |
| `internal/budget` | ≥ 95% | ≥ 90% |
| `internal/bpf` | ≥ 85% | ≥ 80% |
| `internal/gossip` | ≥ 90% | ≥ 85% |
| `internal/governance` | ≥ 90% | ≥ 85% |
| **Overall** | **≥ 90%** | **≥ 85%** |

## Test Data

Test fixtures and datasets located in `test/fixtures/`:
- `baseline_samples.json` - Baseline training data
- `attack_patterns.json` - Known attack signatures
- `config_examples/` - Valid and invalid configs

## Debugging Failed Tests

**Verbose output:**
```bash
go test -v -race ./internal/anomaly
```

**Run specific test:**
```bash
go test -v -run TestEngine_Score ./internal/anomaly
```

**Enable debug logging:**
```bash
OCTOREFLEX_LOG_LEVEL=debug go test -v ./test/integration
```

**Preserve test artifacts:**
```bash
go test -v ./test/integration -test.keep-tmp-dir
```

## Contributing Tests

When adding new features:

1. **Unit tests are mandatory** (aim for 95%+ coverage)
2. **Integration tests for new subsystems**
3. **Adversarial tests for security-critical paths**
4. **Performance benchmarks for hot paths**

Test naming convention:
- `TestFunctionName_Scenario` for unit tests
- `TestIntegration_Feature` for integration tests
- `TestAdversarial_AttackType` for adversarial tests
- `BenchmarkOperation` for performance tests

## Known Limitations

- eBPF tests require Linux kernel (skip on macOS/Windows)
- Integration tests require root (use CI containers)
- Fuzzing is time-intensive (run in CI only)
- Formal verification requires TLA+ toolbox

## References

- [Go Testing Documentation](https://pkg.go.dev/testing)
- [TLA+ Hyperbook](https://lamport.azurewebsites.net/tla/hyperbook.html)
- [AFL++ Fuzzing Guide](https://aflplus.plus/)
