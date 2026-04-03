<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `benchmarks/` — Performance Benchmarks

> **Automated performance measurement for critical subsystems.**

## Benchmarks

| File | What It Measures |
|---|---|
| **`performance_suite.py`** | Full performance suite — latency, throughput, memory usage across all engine subsystems |
| **`psia_benchmark.py`** | PSIA framework performance — reasoning latency, policy evaluation speed, invariant check overhead |
| **`run_benchmarks.py`** | Runner script — executes all benchmarks, generates `benchmark_report.json` |
| **`benchmark_report.json`** | Latest benchmark results (auto-generated) |

## Running

```bash
# Run all benchmarks
python benchmarks/run_benchmarks.py

# Run PSIA-specific benchmarks
python benchmarks/psia_benchmark.py

# Full performance suite
python benchmarks/performance_suite.py
```

## Output

Results are written to `benchmark_report.json` with:

- Execution time (P50, P95, P99)
- Memory usage (peak, average)
- Throughput (ops/sec)
- Regression detection (comparison against baseline)
