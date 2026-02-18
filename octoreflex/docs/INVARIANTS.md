# OCTOREFLEX Invariants

This document specifies the invariants that OCTOREFLEX guarantees at each layer.
An invariant is a property that must hold at all times, regardless of input.
Violations are bugs, not configuration errors.

---

## I. BPF Layer Invariants

### I-1: Monotonic State Escalation

**Invariant:** The kernel-side `process_state_map` value for a PID can only increase (toward `TERMINATED`). The BPF LSM hooks never write a lower state value.

**Enforcement:** The BPF hook reads the current state, computes the new state, and only writes if `new_state > current_state`. This is a single atomic map update (no compare-and-swap needed — single-writer per PID from the userspace agent).

**Consequence:** A process cannot escape a higher isolation state by triggering a BPF hook that would normally apply a lower state.

### I-2: Safe Ring Buffer Drop

**Invariant:** Ring buffer overflow never causes a kernel panic, memory corruption, or BPF verifier violation. Events are silently dropped and the per-CPU drop counter is incremented.

**Enforcement:** `bpf_ringbuf_reserve()` returns NULL on overflow. The BPF program checks for NULL before writing. The drop counter is a per-CPU array map (no contention).

### I-3: BPF Verifier Compliance

**Invariant:** All BPF programs pass the kernel verifier at load time. The agent refuses to start if any program fails verification.

**Enforcement:** `bpf_object__load()` returns an error on verifier failure. The agent calls `os.Exit(1)` in this case.

### I-4: No Userspace Pointer Dereference

**Invariant:** BPF programs never dereference userspace pointers. All data is read from kernel context structures or BPF maps.

**Enforcement:** Enforced by the BPF verifier. No `bpf_probe_read_user()` calls in the LSM hooks.

### I-5: Bounded Loops

**Invariant:** All loops in BPF programs have a statically-bounded iteration count, verifiable by the kernel verifier.

**Enforcement:** No loops in the current BPF implementation. All operations are O(1).

---

## II. Userspace Agent Invariants

### II-1: Config Validation Before Application

**Invariant:** The agent never applies a configuration that fails `Validate()`. On startup, an invalid config causes `os.Exit(1)`. On hot-reload (SIGHUP), an invalid config is logged and the previous config is retained.

### II-2: Budget Gate

**Invariant:** No escalation action is applied without first consuming the required tokens from the budget bucket. If the bucket is empty, the action is skipped and logged.

**Consequence:** Budget exhaustion causes a temporary suspension of escalation, not a crash or panic.

### II-3: Operator Pin Precedence

**Invariant:** A pinned PID is never escalated or decayed by the automatic escalation engine. The pin can only be removed by an explicit `unpin` operator command.

**Consequence:** Operator overrides are authoritative. The engine cannot override an operator decision.

### II-4: Ledger Completeness

**Invariant:** Every state transition (escalation or decay) is written to the BoltDB ledger before the BPF map is updated. If the ledger write fails, the BPF map is not updated and the transition is aborted.

**Consequence:** The ledger is always at least as current as the BPF enforcement state.

### II-5: Graceful Shutdown

**Invariant:** On SIGTERM, the agent drains the event queue (up to 5 seconds), flushes the ledger, and exits cleanly. BPF programs remain loaded (kernel-owned) until the agent is restarted or the system reboots.

**Consequence:** BPF enforcement continues during agent restart. There is no enforcement gap.

### II-6: No Panic in Production Code

**Invariant:** No `panic()` call exists in production code paths (non-test, non-init). All errors are returned as `error` values and handled by the caller.

**Exceptions:** `init()` functions in the `contrib` package may panic on duplicate scorer registration (programmer error, not runtime error).

---

## III. Gossip Layer Invariants

### III-1: Signature Verification Before Processing

**Invariant:** No gossip envelope is processed (quorum updated, baseline merged) without first verifying the Ed25519 signature. Invalid signatures are rejected and logged.

### III-2: Timestamp TTL Enforcement

**Invariant:** Gossip envelopes older than `envelope_ttl` (default 30s) are rejected, regardless of signature validity. This prevents replay attacks.

### III-3: Quorum Independence

**Invariant:** Each node evaluates the quorum signal independently from its own observation set. No node can force another node's quorum signal to 1.0 without meeting the `quorum_min` threshold.

### III-4: Federated Baseline Conservative Merge

**Invariant:** Federated baselines are merged with a trust weight ≤ `trust_weight` (default 0.3). Local data always contributes at least `(1 - trust_weight) = 70%` of the merged baseline weight.

---

## IV. Storage Invariants

### IV-1: Schema Version Check

**Invariant:** The agent refuses to open a BoltDB file with a schema version other than the current version. This prevents silent data corruption from version skew.

### IV-2: Ledger Key Monotonicity

**Invariant:** Ledger keys are `RFC3339Nano_PID`, which are lexicographically monotonic. BoltDB's B-tree cursor can therefore scan the ledger in chronological order without sorting.

### IV-3: Retention Pruning Safety

**Invariant:** Retention pruning only deletes ledger entries older than `retention_days`. It never deletes baseline records or metadata.

---

## V. Anomaly Engine Invariants

### V-1: Score Non-Negativity

**Invariant:** `Score()` always returns a non-negative value. Mahalanobis distance squared is always ≥ 0. Entropy delta is always ≥ 0. The entropy weight `wₑ ≥ 0`.

### V-2: Nil Baseline Returns Zero

**Invariant:** `Score()` returns `(0.0, nil)` when `baseline == nil`. A process with no established baseline is never escalated due to anomaly score alone.

### V-3: Euclidean Fallback for Singular Covariance

**Invariant:** When the covariance matrix is singular (non-invertible), `Score()` falls back to squared Euclidean distance. It never returns an error for this case.

---

## VI. Camouflage Module Invariants

### VI-1: Idempotent Activation

**Invariant:** Calling `Activate()` twice for the same PID and state is a no-op. The module tracks active actions per PID and skips re-activation.

### VI-2: Deterministic Port Selection

**Invariant:** For the same `(nodeID, pid, epoch)` triple, `deterministicPort()` always returns the same port. This allows legitimate clients to predict the next port.

### VI-3: Atomic Hint File Writes

**Invariant:** Hint files (`port_hints.json`, `ip_hints.json`) are written atomically via write-to-temp + rename. Readers never observe a partial write.
