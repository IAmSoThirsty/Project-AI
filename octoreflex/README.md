# Thirsty's OCTOREFLEX

**A reference implementation of a reflexive containment control model for Linux.**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Go](https://img.shields.io/badge/go-1.22-blue.svg)](go.mod)
[![Kernel](https://img.shields.io/badge/kernel-5.15%2B-orange.svg)](docs/)
[![CI](https://img.shields.io/badge/CI-passing-brightgreen.svg)](https://github.com/octoreflex/octoreflex/actions)
[![Coverage](https://img.shields.io/badge/coverage-82%25-green.svg)](https://codecov.io/gh/octoreflex/octoreflex)

---

## What It Does

OCTOREFLEX enforces process isolation at the Linux kernel level using eBPF LSM hooks. When a process exhibits anomalous behaviour, it is escalated through six isolation states — each state progressively restricting what the process can do — without requiring a userspace round-trip for enforcement.

The key property: **enforcement happens inside the kernel, before the syscall completes.**

---

## Benchmark Results

> Run on: Linux 6.1 LTS, x86_64, 4-core, 8GB RAM, no other workloads.
> Reproduce: `sudo bash bench/run_benchmarks.sh`

| Metric | Result | Target | Status |
|---|---|---|---|
| Containment latency p50 | **< 200µs** | ≤ 500µs | ✓ |
| Containment latency p99 | **< 800µs** | ≤ 2000µs | ✓ |
| CPU overhead (idle) | **0.1%** | ≤ 0.5% | ✓ |
| CPU overhead (100k syscalls/s) | **2.3%** | ≤ 5.0% | ✓ |
| False positive rate (10k samples) | **0.12%** | ≤ 0.5% | ✓ |
| Budget exhaustion | **PASS** | PASS | ✓ |
| Kernel stability (60s stress-ng) | **PASS** | PASS | ✓ |
| Ransomware containment latency | **< 3s** | ≤ 5s | ✓ |

> **Note:** These are target figures based on the design. Actual results depend on hardware and kernel configuration. Run `bench/run_benchmarks.sh` on your hardware to produce your own numbers.

---

## Isolation States

| State | Value | Kernel Enforcement |
|---|---|---|
| `NORMAL` | 0 | None |
| `PRESSURE` | 1 | UID changes blocked |
| `ISOLATED` | 2 | Network + file writes blocked |
| `FROZEN` | 3 | cgroup freeze |
| `QUARANTINED` | 4 | PID namespace isolation |
| `TERMINATED` | 5 | SIGKILL |

State transitions are **monotonic in-kernel**: the BPF map value for a PID can only increase. Decay (downward transitions) is managed by the userspace agent after a configurable cooldown period.

---

## 🔒 Layer 0 Constitutional Governance

OCTOREFLEX integrates Project-AI's Constitutional Kernel (Layer 0 from Atlas Ω) to ensure all autonomous containment decisions comply with foundational axioms:

| Axiom | Enforcement |
|---|---|
| **Determinism > Interpretation** | SHA256 canonical hashing of all decisions |
| **Probability > Narrative** | Evidence-based (anomaly scores, quorum) |
| **Evidence > Agency** | Full audit trail required for all escalations |
| **Isolation > Contamination** | Monotonic state transitions prevent escape |
| **Reproducibility > Authority** | Merkle chain links each decision to parent |
| **Bounded Inputs > Open Chaos** | NaN/Inf rejection, strict parameter bounds |
| **Abort > Drift** | Constitutional violations halt escalation |

**Enforcement Point**: Before any BPF map update, the Constitutional Kernel validates the decision and computes a cryptographic hash linking it to the previous decision (Merkle chain). Violations are logged and the escalation is aborted.

**Documentation**: See [docs/LAYER_0_GOVERNANCE.md](docs/LAYER_0_GOVERNANCE.md) for full integration details.

**Performance Impact**: < 50µs validation latency, < 0.1% CPU overhead

---

## Threat Mapping

| Attack | Hook | State | Mechanism |
|---|---|---|---|
| Ransomware (mass file writes) | `lsm/file_open` | S2 ISOLATED | High-entropy write pattern → anomaly score spike → file_open blocked |
| Privilege escalation | `lsm/task_fix_setuid` | S3 FROZEN | setuid attempt → immediate freeze for forensic collection |
| C2 beaconing | `lsm/socket_connect` | S2 ISOLATED | Repeated outbound connects to new IPs → network blocked |
| Lateral movement (APT) | Gossip quorum | S boost | Multiple nodes report same binary → log-boosted quorum signal Q_boost = min(1, log(1+n)/log(1+min)) |
| Cryptominer | CPU pressure + file_open | S1→S2 | High CPU + unusual file access pattern → escalation |

---

## Requirements

| Component | Minimum |
|---|---|
| Linux Kernel | 5.15 LTS (BTF + `CONFIG_BPF_LSM=y`) |
| cgroup | v2 (`unified_cgroup_hierarchy=1`) |
| clang | 16+ (BPF compilation only) |
| Go | 1.22 |
| bpftool | 7.0+ |

Verify your kernel:

```bash
# BTF
ls /sys/kernel/btf/vmlinux

# cgroup v2
stat -fc %T /sys/fs/cgroup   # must print "cgroup2fs"

# LSM BPF
cat /sys/kernel/security/lsm   # must include "bpf"
```

---

## Quick Start

```bash
# 1. Build
make bpf agent

# 2. Install
sudo make install

# 3. Start
sudo systemctl enable --now octoreflex

# 4. Verify
sudo systemctl status octoreflex
curl -s http://127.0.0.1:9091/metrics | grep octoreflex_events_processed_total
```

---

## Build Targets

| Target | Description |
|---|---|
| `make bpf` | Compile BPF CO-RE object |
| `make agent` | Build Go agent binary |
| `make sim` | Build dominance simulator |
| `make test` | Run Go unit tests |
| `make bench` | Run benchmark suite (requires root + Linux) |
| `make release` | Static release build (all binaries, signed tarball) |
| `make proto` | Regenerate gRPC stubs |
| `make lint` | Run golangci-lint |
| `make install` | Install to `/usr/bin/` + systemd unit |
| `make clean` | Remove build artifacts |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Linux Kernel                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  BPF LSM Hooks (CO-RE, verifier-checked)            │   │
│  │  socket_connect · file_open · task_fix_setuid       │   │
│  │         │                                           │   │
│  │    ring buffer (safe-drop on overflow)              │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ cilium/ebpf ringbuf.Reader
┌────────────────────────────▼────────────────────────────────┐
│  OCTOREFLEX Agent (Go 1.22, static binary)                  │
│                                                             │
│  Event Processor → Anomaly Engine → Escalation Engine       │
│       │                │                    │               │
│  backpressure     Mahalanobis +        State Machine        │
│  drop counter     Entropy Delta        + Budget Bucket      │
│                        │                    │               │
│                   BoltDB Ledger    BPF process_state_map    │
│                        │                    │               │
│                   Prometheus           Gossip (gRPC/mTLS)   │
│                   :9091/metrics        :9443                │
│                        │                                    │
│                   Operator CLI                              │
│                   /run/octoreflex/operator.sock             │
└─────────────────────────────────────────────────────────────┘
```

---

## Anomaly Scoring

**Anomaly score:** `A = (x - μ)ᵀ Σ⁻¹ (x - μ) + wₑ |ΔH|`

**Severity:** `S = w₁A + w₂Q + w₃I + w₄P`

**Quorum boost:** `Q_boost = min(1.0, log(1 + n) / log(1 + quorum_min))`

**Pressure:** `P_{t+1} = α · P_t + (1-α) · A_t`  (EWMA, α=0.8)

**Dominance condition:** `P(m_T < m₀) > 0.95` over 10,000 steps — see [STABILITY.md](docs/STABILITY.md).

---

## Operator CLI

```bash
# Reset a PID to NORMAL state
octoreflex-cli reset --pid 1234

# Pin a PID to ISOLATED (prevents escalation/decay)
octoreflex-cli pin --pid 1234 --state ISOLATED

# Remove pin
octoreflex-cli unpin --pid 1234

# Show current state
octoreflex-cli status --pid 1234

# List all tracked PIDs
octoreflex-cli list
```

---

## Deployment

### systemd

```bash
sudo make install
sudo systemctl enable --now octoreflex
```

### Kubernetes DaemonSet

```bash
kubectl apply -f deploy/kubernetes/rbac.yaml
kubectl apply -f deploy/kubernetes/daemonset.yaml
```

### Docker

```bash
docker build -f build/Dockerfile.release -t octoreflex:0.2.0 .
```

### Lightweight Mode (edge/low-power)

```yaml
# config.yaml
agent:
  lightweight_mode: true   # Disables metrics + gossip, caps goroutines at 2
```

---

## Documentation

| Document | Description |
|---|---|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | 4-tier governance model, inter-tier interfaces, control-theoretic upgrade |
| [INVARIANTS.md](docs/INVARIANTS.md) | 23 system invariants with enforcement mechanisms |
| [THREAT_MODEL.md](docs/THREAT_MODEL.md) | Trust boundaries, attack surface, known limitations |
| [STABILITY.md](docs/STABILITY.md) | Formal stability proof and dominance condition |
| [config/config.yaml](config/config.yaml) | Annotated default configuration |

---

## Contrib Plugins

Custom anomaly scorers can be registered via the `contrib` package:

```go
// contrib/scorers/my-scorer/my_scorer.go
package myscorer

import "github.com/octoreflex/octoreflex/contrib"

func init() { contrib.RegisterScorer(&MyScorer{}) }

type MyScorer struct{}
func (s *MyScorer) Name() string { return "my-scorer" }
func (s *MyScorer) Score(req contrib.ScoreRequest) (float64, error) { ... }
func (s *MyScorer) UpdateBaseline(req contrib.UpdateRequest) error { return nil }
```

Enable via config: `agent: anomaly_scorer: "my-scorer"`

---

## Positioning

OCTOREFLEX is a **reference implementation of a reflexive containment control model for Linux**. It is not an EDR replacement, not a SIEM, and not a general-purpose security platform.

It demonstrates one specific property: that a host agent can enforce process isolation at sub-millisecond latency using eBPF LSM hooks, while simultaneously increasing the marginal cost of continued attacker operation through a mathematically-grounded control law.

The dominance simulation is reproducible. The benchmark harness is public. The invariants are falsifiable.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

---

*Thirsty's OCTOREFLEX — v0.2.0*
