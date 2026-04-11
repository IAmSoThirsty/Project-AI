# OctoReflex eBPF Core — Ultimate Implementation

## Overview

The OctoReflex eBPF Core is a Tier 0 containment system that uses Linux Security Module (LSM) hooks implemented in eBPF to detect and block anomalous process behavior in under 200 microseconds.

## Architecture

### LSM Hooks Implemented

| Hook | Attachment Point | Enforcement | Use Case |
|------|-----------------|-------------|----------|
| `lsm/socket_connect` | Outbound network connections | ISOLATED+ | Network quarantine |
| `lsm/file_open` | File open operations | ISOLATED+ | Filesystem containment |
| `lsm/task_fix_setuid` | UID/GID changes | PRESSURE+ | Privilege escalation prevention |
| `lsm/bprm_check_security` | Program execution | ISOLATED+ | Lateral movement blocking |
| `lsm/file_mmap` | Memory mapping | ISOLATED+ | JIT-spray and code injection prevention |
| `lsm/ptrace_access_check` | Process debugging | PRESSURE+ | Anti-debugging enforcement |
| `lsm/kernel_module_request` | Kernel module loading | PRESSURE+ | Rootkit prevention |
| `lsm/bpf_prog` | BPF program loading | PRESSURE+ | eBPF-based attacks prevention |

### Process Isolation States

```
NORMAL (0)       → No restrictions, all operations permitted
PRESSURE (1)     → Monitoring intensified, privilege operations blocked
ISOLATED (2)     → Network + filesystem quarantine active
FROZEN (3)       → Process suspended via cgroup freeze
QUARANTINED (4)  → Moved to dedicated namespace
TERMINATED (5)   → Process killed, entry retained for audit
```

**Escalation is monotonic:** Only userspace can decay states after cool-down.

## eBPF Maps

### process_state_map
- **Type:** `BPF_MAP_TYPE_HASH`
- **Key:** `u32` (PID)
- **Value:** `u8` (octo_state_t)
- **Max Entries:** 16,384
- **Purpose:** Track per-process isolation state

### events (Ring Buffer)
- **Type:** `BPF_MAP_TYPE_RINGBUF`
- **Size:** 16 MiB
- **Overflow Policy:** Safe-drop (increments `octo_drop_counter`)
- **Purpose:** Emit events to userspace anomaly engine

### cgroup_map
- **Type:** `BPF_MAP_TYPE_HASH`
- **Key:** `u32` (PID)
- **Value:** `u64` (cgroup ID)
- **Max Entries:** 4,096
- **Purpose:** Track containment cgroup associations

### memory_tracking_map
- **Type:** `BPF_MAP_TYPE_LRU_HASH`
- **Key:** `u64` (memory address)
- **Value:** `u32` (allocation size)
- **Max Entries:** 8,192
- **Purpose:** Buffer overflow detection

### octo_drop_counter
- **Type:** `BPF_MAP_TYPE_PERCPU_ARRAY`
- **Purpose:** Track ring buffer overflow events

## Event Format

```c
struct octo_event {
    u32 pid;              // Process ID (tgid)
    u32 uid;              // User ID
    u8  event_type;       // Event type (1-9)
    u8  flags;            // Event flags (see below)
    u8  _pad[2];          // Padding for alignment
    u32 metadata;         // Event-specific metadata
    s64 timestamp_ns;     // Timestamp (bpf_ktime_get_ns)
};
```

### Event Types

| Value | Name | Description |
|-------|------|-------------|
| 1 | SOCKET_CONNECT | Outbound network connection |
| 2 | FILE_OPEN | File open operation |
| 3 | SETUID | UID/GID change attempt |
| 4 | EXEC | Program execution (execve/execveat) |
| 5 | MMAP | Memory mapping operation |
| 6 | PTRACE | Process debugging attempt |
| 7 | MODULE_LOAD | Kernel module load request |
| 8 | BPF_LOAD | BPF program load attempt |
| 9 | MEM_VIOLATION | Memory access violation detected |

### Event Flags

```c
#define OCTO_FLAG_EXEC_SUID      (1 << 0)  // Setuid binary execution
#define OCTO_FLAG_MMAP_EXEC      (1 << 1)  // Executable memory mapping
#define OCTO_FLAG_MMAP_WRITE     (1 << 2)  // Writable memory mapping
#define OCTO_FLAG_PTRACE_ATTACH  (1 << 3)  // Ptrace attach (not read)
#define OCTO_FLAG_MEM_OVERFLOW   (1 << 4)  // Buffer overflow detected
```

## CO-RE (Compile Once - Run Everywhere)

OctoReflex uses **BTF (BPF Type Format)** for portable eBPF programs:

- Programs compiled once work across kernel versions
- Uses `BPF_CORE_READ()` for safe kernel struct access
- Requires kernel ≥ 5.15 with `CONFIG_DEBUG_INFO_BTF=y`
- vmlinux.h generated via `bpftool btf dump`

## Performance

### Latency Requirements

- **LSM hook overhead:** < 200μs (p99)
- **Event parsing:** < 1μs
- **Map operations:** < 10μs
- **Ring buffer write:** < 5μs

### Verification

Run benchmarks:
```bash
cd bench
go test -bench=. -benchmem -benchtime=10s
```

Expected output:
```
BenchmarkEventParsing-8           100000000    0.8 ns/op    0 B/op
BenchmarkLSMHookLatency-8         50000        180 μs/op
```

## Memory Safety

### BPF Verifier Invariants

1. **No dynamic allocation:** Stack-only memory
2. **Bounded loops:** All loops have compile-time upper bounds
3. **Safe pointer access:** All kernel reads use `BPF_CORE_READ()`
4. **No blocking:** Ring buffer overflow is safe-drop
5. **Instruction limit:** < 1 million instructions per program

### W^X Detection

The `lsm/file_mmap` hook detects Write-XOR-Execute violations:

```c
if ((prot & PROT_EXEC) && (prot & PROT_WRITE)) {
    emit_event(OCTO_EVT_MEM_VIOLATION, pid, uid, flags, prot);
}
```

## Cgroup v2 Integration

OctoReflex integrates with cgroup v2 for enhanced containment:

1. **Namespace isolation:** Processes moved to dedicated PID/net namespaces
2. **Resource limits:** CPU/memory constraints via cgroup controllers
3. **Freeze enforcement:** Instant process suspension via `cgroup.freeze`

### Go API

```go
// Track process in containment cgroup
objs.SetProcessCgroup(pid, cgroupID)

// Retrieve cgroup association
cgroupID, err := objs.GetProcessCgroup(pid)

// Remove from tracking
objs.DeleteProcessCgroup(pid)
```

## Build & Deployment

### Prerequisites

```bash
# Ubuntu/Debian
apt-get install -y clang-16 llvm-16 libbpf-dev linux-headers-$(uname -r) bpftool

# Verify kernel version
uname -r  # Must be >= 5.15

# Verify BPF LSM enabled
cat /sys/kernel/security/lsm | grep bpf
```

### Compilation

```bash
# Build BPF object
cd bpf
make

# Build Go agent (embeds BPF object)
cd ..
make agent

# Run tests
make test

# Build release (static binary)
make release
```

### Installation

```bash
# Install system-wide (requires root)
sudo make install

# Enable systemd service
sudo systemctl enable --now octoreflex
```

## Testing

### Unit Tests

```bash
go test -v ./internal/bpf/...
```

### Integration Tests (requires root)

```bash
sudo go test -v -tags=integration ./test/integration/
```

### Red Team Tests

```bash
cd test/redteam
sudo go test -v
```

## Security Considerations

### Agent Self-Protection

The agent whitelists its own PID immediately after loading:

```go
agentPID := uint32(os.Getpid())
objs.SetProcessState(agentPID, bpf.StateNormal)
```

Without this, the `lsm/file_open` hook would block the agent's own file operations.

### Map Pinning

All maps are pinned to `/sys/fs/bpf/octoreflex/` for persistence across agent restarts. Process state is preserved during crashes.

### Audit Trail

All enforcement actions are logged with:
- PID, UID, timestamp
- Event type and metadata
- Enforcement decision (permit/deny)

Logs are immutable and stored in BoltDB for forensic analysis.

## Troubleshooting

### BPF LSM not active

```bash
# Check kernel command line
cat /proc/cmdline | grep lsm

# Enable BPF LSM (requires reboot)
echo 'GRUB_CMDLINE_LINUX="lsm=...,bpf"' | sudo tee -a /etc/default/grub
sudo update-grub
sudo reboot
```

### Ring buffer drops

```bash
# Check drop counter
sudo cat /sys/fs/bpf/octoreflex/octo_drop_counter

# Increase ring buffer size (bpf/octoreflex.h)
#define OCTO_RINGBUF_SIZE (1U << 25)  // 32 MiB
```

### Verifier errors

```bash
# Check dmesg for BPF verifier logs
sudo dmesg | grep bpf

# Increase verifier log level
sudo sysctl -w kernel.bpf_log_level=1
```

## Performance Tuning

### CPU Pinning

Pin agent to dedicated cores:

```bash
sudo taskset -c 0,1 /usr/bin/octoreflex
```

### Ring Buffer Tuning

Adjust polling interval in `internal/kernel/events.go`:

```go
reader.SetDeadline(time.Now().Add(1 * time.Millisecond))
```

### Map Size Limits

Increase map sizes for large deployments:

```c
#define OCTO_PROCESS_STATE_MAP_MAX  65536U  // 64K processes
```

## Future Enhancements

- [ ] eBPF CO-RE tracepoints for deeper visibility
- [ ] XDP integration for network-level containment
- [ ] USDT (User Statically-Defined Tracing) probes
- [ ] eBPF LSM socket filtering
- [ ] Kernel-level anomaly scoring

## References

- [BPF LSM Documentation](https://docs.kernel.org/bpf/prog_lsm.html)
- [CO-RE (Compile Once - Run Everywhere)](https://nakryiko.com/posts/bpf-portability-and-co-re/)
- [Linux Security Modules](https://www.kernel.org/doc/html/latest/security/lsm.html)
- [cilium/ebpf Go Library](https://github.com/cilium/ebpf)

---

**Version:** 2.0.0-ultimate  
**Last Updated:** 2026-03-03  
**Maintainer:** OctoReflex Security Team
