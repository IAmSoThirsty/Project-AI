# OCTOREFLEX Threat Model

**Version:** 0.2  
**Date:** 2026-02-18  
**Scope:** Linux host-level containment agent

---

## 1. System Description

OCTOREFLEX is a Linux host agent that enforces process isolation via eBPF LSM hooks. It monitors process behaviour, computes anomaly scores, and escalates processes through six isolation states (NORMAL → TERMINATED). Enforcement is in-kernel; the userspace agent manages state transitions and audit.

---

## 2. Assets

| Asset | Sensitivity | Location |
|---|---|---|
| BPF programs | Critical | Kernel memory (pinned to `/sys/fs/bpf/octoreflex/`) |
| `process_state_map` | Critical | BPF map (kernel memory) |
| BoltDB database | High | `/var/lib/octoreflex/octoreflex.db` |
| Config file | High | `/etc/octoreflex/config.yaml` |
| TLS private key | Critical | `/etc/octoreflex/tls/node.key` |
| Operator socket | High | `/run/octoreflex/operator.sock` |
| Audit ledger | Medium | BoltDB `ledger` bucket |
| Prometheus metrics | Low | `127.0.0.1:9091/metrics` |

---

## 3. Trust Boundaries

```
┌─────────────────────────────────────────────────────────┐
│  TRUSTED                                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Kernel + BPF verifier                           │  │
│  │  OCTOREFLEX agent binary (root, verified)        │  │
│  │  BPF programs (verifier-checked at load time)    │  │
│  │  Operator CLI (root, Unix socket 0600)           │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  UNTRUSTED                                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Monitored user processes                        │  │
│  │  Network traffic (including gossip peers)        │  │
│  │  Gossip peers (verified via mTLS + Ed25519)      │  │
│  │  Config file contents (validated before use)     │  │
│  │  BoltDB file contents (CRC-checked on open)      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Threat Actors

| Actor | Capability | Goal |
|---|---|---|
| **Unprivileged process** | Standard Linux syscalls, no CAP_* | Evade detection, escalate privileges, exfiltrate data |
| **Privileged process (non-root)** | Some capabilities (CAP_NET_ADMIN, etc.) | Bypass BPF enforcement, modify cgroup membership |
| **Root process (compromised)** | Full root, but OCTOREFLEX already loaded | Unload BPF programs, modify `process_state_map` directly |
| **Network adversary** | Can send crafted gossip envelopes | Poison quorum signal, force false positives, replay attacks |
| **Supply chain adversary** | Can modify OCTOREFLEX binary before install | Backdoor the agent, weaken BPF enforcement |

---

## 5. Attack Surface

### 5.1 BPF Map (`process_state_map`)

**Threat:** A root process writes directly to the pinned BPF map to reset its own state.

**Mitigation:** The map is pinned at `/sys/fs/bpf/octoreflex/process_state_map`. Root can write to it. This is a known limitation of the current design.

**Residual risk:** A compromised root process can reset its own BPF state. This is mitigated by the audit ledger (the reset is logged) and by the fact that the agent will re-escalate on the next anomaly detection cycle.

**Future mitigation:** Use `BPF_F_RDONLY_PROG` map flag to prevent userspace writes after agent startup (requires kernel 5.15+, currently not implemented).

### 5.2 Operator Socket (`/run/octoreflex/operator.sock`)

**Threat:** A process with access to the socket issues `pin` or `reset` commands to disable containment.

**Mitigation:** Socket permissions are `0600`, owned by root. Only root can connect.

**Residual risk:** A compromised root process can issue operator commands. Mitigated by audit logging of all operator commands.

### 5.3 Gossip Network

**Threat 1:** Replay attack — an adversary replays a valid gossip envelope to inflate the quorum signal.

**Mitigation:** Timestamp TTL enforcement (default 30s). Envelopes older than TTL are rejected.

**Threat 2:** Signature forgery — an adversary sends a crafted envelope with a fake node ID.

**Mitigation:** Ed25519 signature verification. The adversary cannot forge a signature without the node's private key.

**Threat 3:** Quorum manipulation — a compromised peer sends anomalous observations to force false positives.

**Mitigation:** `quorum_min` threshold (default 2). A single compromised peer cannot reach quorum alone. The weight of the quorum signal in the severity formula is configurable (default `w₂=0.2`).

**Threat 4:** Federated baseline poisoning — a compromised peer sends a crafted baseline to corrupt the anomaly engine.

**Mitigation:** `trust_weight` (default 0.3) limits the influence of federated baselines. `min_samples` (default 100) prevents sharing of under-trained baselines. Local data always contributes ≥ 70% of the merged baseline.

### 5.4 Config File

**Threat:** An adversary modifies `/etc/octoreflex/config.yaml` to disable containment (e.g., set all thresholds to infinity).

**Mitigation:** Config is validated on load and on hot-reload. Invalid configs are rejected. The config file should be owned by root with mode `0600`.

**Residual risk:** A root adversary can modify the config and send SIGHUP. Mitigated by immutable file attributes (`chattr +i /etc/octoreflex/config.yaml`) — not enforced by OCTOREFLEX itself.

### 5.5 BoltDB Database

**Threat:** An adversary modifies the BoltDB file to corrupt baselines or delete ledger entries.

**Mitigation:** BoltDB is opened with CRC checking. Corrupted pages cause the agent to refuse to start. The database file should be owned by root with mode `0600`.

### 5.6 Supply Chain

**Threat:** The OCTOREFLEX binary is replaced with a backdoored version.

**Mitigation (recommended):** Verify the binary checksum against the release signature before installation. Use `sha256sum` and GPG signature verification. The Makefile `release` target produces a signed tarball.

---

## 6. Out of Scope

The following are explicitly out of scope for OCTOREFLEX v0.2:

- **Kernel exploits:** A process that exploits a kernel vulnerability to gain ring-0 execution can bypass all BPF enforcement. OCTOREFLEX is not a kernel exploit mitigation tool.
- **Hardware attacks:** DMA attacks, cold boot attacks, and hardware side-channels are out of scope.
- **Hypervisor escapes:** OCTOREFLEX operates at the host level. VM escape attacks are out of scope.
- **Physical access:** An attacker with physical access can reboot the host and disable BPF programs.

---

## 7. Security Properties

| Property | Guarantee | Condition |
|---|---|---|
| **Enforcement integrity** | BPF LSM hooks cannot be bypassed by unprivileged processes | Kernel 5.15+, LSM BPF enabled |
| **Monotonic escalation** | Process state can only increase in-kernel | BPF map write path is agent-only |
| **Audit completeness** | All state transitions are logged before enforcement | BoltDB write succeeds |
| **Gossip authenticity** | All gossip envelopes are Ed25519-signed | Private key not compromised |
| **Config integrity** | Invalid configs are rejected before application | Validate() covers all fields |
| **Operator auditability** | All operator commands are logged | Audit log not tampered |

---

## 8. Known Limitations

1. **Root bypass:** A compromised root process can write directly to the BPF map. Mitigation: `BPF_F_RDONLY_PROG` (planned for v0.3).
2. **Single-host baseline:** Without federated baselines, fresh nodes have no anomaly baseline for the first `window_duration` of operation.
3. **Static peer list:** Gossip peers are statically configured. Dynamic peer discovery is not implemented.
4. **No binary signing:** OCTOREFLEX does not verify the integrity of monitored binaries (integrity scoring is a placeholder). Full IMA integration is planned for v0.3.
