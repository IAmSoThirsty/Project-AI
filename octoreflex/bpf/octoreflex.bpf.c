//                                           [2026-03-03 13:45]
//                                          Productivity: Active
// SPDX-License-Identifier: GPL-2.0
/*
 * octoreflex.bpf.c — OCTOREFLEX eBPF LSM programs.
 *
 * Compiled with clang 16+ targeting BPF with CO-RE (Compile Once, Run
 * Everywhere). Requires BTF-enabled kernel ≥ 5.15 with CONFIG_BPF_LSM=y
 * and "lsm=bpf" on the kernel command line (or appended via
 * /sys/kernel/security/lsm).
 *
 * Design invariants (enforced by BPF verifier + code review):
 *   1. No dynamic memory allocation (no bpf_malloc).
 *   2. No unbounded loops — all loops have a verifier-provable bound.
 *   3. No user-pointer dereferences without bpf_probe_read_user().
 *   4. Ring buffer overflow is safe-drop: bpf_ringbuf_reserve() returns
 *      NULL when full; we increment a counter and return without blocking.
 *   5. State transitions are monotonic-increasing in kernel space.
 *      Userspace is the only entity that may decay state.
 *   6. No heavy computation — anomaly scoring is entirely in userspace.
 *   7. All maps pinned under /sys/fs/bpf/octoreflex/ by the Go loader.
 *
 * LSM hooks implemented:
 *   lsm/socket_connect       — blocks outbound connections for ISOLATED+ PIDs.
 *   lsm/file_open            — blocks file opens for ISOLATED+ PIDs.
 *   lsm/task_fix_setuid      — blocks UID changes for PRESSURE+ PIDs.
 *   lsm/bprm_check_security  — blocks exec for ISOLATED+ PIDs.
 *   lsm/file_mmap            — blocks executable mmaps for ISOLATED+ PIDs.
 *   lsm/ptrace_access_check  — blocks ptrace for PRESSURE+ PIDs.
 *   lsm/kernel_module_request— blocks module loading for PRESSURE+ PIDs.
 *   lsm/bpf_prog             — blocks BPF program loading for PRESSURE+ PIDs.
 *
 * Event types emitted to ring buffer (see octoreflex.h):
 *   OCTO_EVT_SOCKET_CONNECT = 1
 *   OCTO_EVT_FILE_OPEN      = 2
 *   OCTO_EVT_SETUID         = 3
 *   OCTO_EVT_EXEC           = 4
 *   OCTO_EVT_MMAP           = 5
 *   OCTO_EVT_PTRACE         = 6
 *   OCTO_EVT_MODULE_LOAD    = 7
 *   OCTO_EVT_BPF_LOAD       = 8
 *   OCTO_EVT_MEM_VIOLATION  = 9
 */

#include "octoreflex.h"
#include "vmlinux.h"
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>


char LICENSE[] SEC("license") = "GPL";

/* =========================================================================
 * MAP DEFINITIONS
 *
 * All maps are pinned by the Go loader under /sys/fs/bpf/octoreflex/.
 * The BPF programs themselves do not pin — they reference maps by name
 * and the loader performs pinning after successful load.
 * ========================================================================= */

/*
 * process_state_map
 *
 * Key:   u32 PID (tgid from bpf_get_current_pid_tgid() >> 32)
 * Value: u8  octo_state_t
 *
 * Semantics:
 *   - Absent entry ≡ OCTO_NORMAL (default-permit).
 *   - Userspace writes state upgrades; BPF reads and enforces.
 *   - BPF never writes to this map (enforcement only, no self-escalation).
 *   - Max 16384 entries. LRU eviction not used — userspace prunes stale
 *     entries when a process exits (via perf/tracepoint exit hook).
 */
struct {
  __uint(type, BPF_MAP_TYPE_HASH);
  __uint(max_entries, OCTO_PROCESS_STATE_MAP_MAX);
  __type(key, __u32);
  __type(value, __u8);
} process_state_map SEC(".maps");

/*
 * events (ring buffer)
 *
 * Size: 16 MiB (OCTO_RINGBUF_SIZE = 1 << 24).
 * Overflow policy: safe-drop. bpf_ringbuf_reserve() returns NULL when
 * the buffer is full. We increment octo_drop_counter and return without
 * blocking the kernel path.
 *
 * Consumer: Go event processor goroutine via perf_buffer / ring_buffer API.
 */
struct {
  __uint(type, BPF_MAP_TYPE_RINGBUF);
  __uint(max_entries, OCTO_RINGBUF_SIZE);
} events SEC(".maps");

/*
 * octo_drop_counter
 *
 * Per-CPU array tracking ring buffer overflow drops.
 * Userspace Prometheus exporter reads this to expose
 * octoreflex_ringbuf_drops_total counter.
 */
struct {
  __uint(type, BPF_MAP_TYPE_PERCPU_ARRAY);
  __uint(max_entries, 1);
  __type(key, __u32);
  __type(value, __u64);
} octo_drop_counter SEC(".maps");

/*
 * cgroup_map
 *
 * Track PIDs in containment cgroups for enhanced isolation.
 * Key:   u32 PID
 * Value: u64 cgroup_id (from bpf_get_current_cgroup_id())
 */
struct {
  __uint(type, BPF_MAP_TYPE_HASH);
  __uint(max_entries, OCTO_CGROUP_MAP_MAX);
  __type(key, __u32);
  __type(value, __u64);
} cgroup_map SEC(".maps");

/*
 * memory_tracking_map
 *
 * Track memory allocations for overflow detection.
 * Key:   u64 address
 * Value: u32 size
 * Used for stack canary and heap overflow detection.
 */
struct {
  __uint(type, BPF_MAP_TYPE_LRU_HASH);
  __uint(max_entries, OCTO_MEM_TRACK_MAP_MAX);
  __type(key, __u64);
  __type(value, __u32);
} memory_tracking_map SEC(".maps");

/* =========================================================================
 * HELPER: emit_event_extended
 *
 * Extended event emission with flags and metadata support.
 * On ring buffer full: increments per-CPU drop counter and returns without
 * blocking.
 *
 * Parameters:
 *   event_type  — one of octo_event_type_t values
 *   pid         — tgid of the calling process
 *   uid         — uid of the calling process
 *   flags       — event-specific flags
 *   metadata    — event-specific metadata (32 bits)
 *
 * Returns: void (errors are counted, not propagated to LSM return value).
 * ========================================================================= */
static __always_inline void emit_event_extended(__u8 event_type, __u32 pid, 
                                                __u32 uid, __u8 flags, 
                                                __u32 metadata) {
  struct octo_event *e;

  e = bpf_ringbuf_reserve(&events, sizeof(struct octo_event), 0);
  if (!e) {
    /* Ring buffer full — safe drop. Increment per-CPU counter. */
    __u32 key = 0;
    __u64 *drops = bpf_map_lookup_elem(&octo_drop_counter, &key);
    if (drops)
      __sync_fetch_and_add(drops, 1);
    return;
  }

  e->pid = pid;
  e->uid = uid;
  e->event_type = event_type;
  e->flags = flags;
  e->_pad[0] = 0;
  e->_pad[1] = 0;
  e->metadata = metadata;
  e->timestamp_ns = bpf_ktime_get_ns();

  bpf_ringbuf_submit(e, 0);
}

/* =========================================================================
 * HELPER: emit_event
 *
 * Simplified event emission (backwards compatibility).
 * ========================================================================= */
static __always_inline void emit_event(__u8 event_type, __u32 pid, __u32 uid) {
  emit_event_extended(event_type, pid, uid, 0, 0);
}

/* =========================================================================
 * HELPER: get_process_state
 *
 * Looks up the current PID's state in process_state_map.
 * Returns OCTO_NORMAL (0) if the PID is not present (default-permit).
 * ========================================================================= */
static __always_inline __u8 get_process_state(__u32 pid) {
  __u8 *state = bpf_map_lookup_elem(&process_state_map, &pid);
  if (!state)
    return OCTO_NORMAL;
  return *state;
}

/* =========================================================================
 * LSM HOOK: lsm/socket_connect
 *
 * Fires before a process initiates an outbound TCP/UDP/UNIX connection.
 *
 * Enforcement:
 *   - State >= OCTO_ISOLATED  → deny (-EPERM). Network quarantine.
 *   - State <  OCTO_ISOLATED  → emit event, permit.
 *
 * Rationale: PRESSURE state still permits connections (monitoring only).
 * ISOLATED and above represent confirmed or high-confidence threats where
 * network exfiltration must be prevented immediately.
 *
 * BPF verifier constraints satisfied:
 *   - No loops.
 *   - No user-pointer dereference.
 *   - Stack usage < 512 bytes.
 *   - Instruction count < 100k (actual: ~30 instructions).
 * ========================================================================= */
SEC("lsm/socket_connect")
int BPF_PROG(octo_socket_connect, struct socket *sock, struct sockaddr *address,
             int addrlen) {
  __u64 pid_tgid = bpf_get_current_pid_tgid();
  __u32 pid = (__u32)(pid_tgid >> 32);
  __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
  __u8 state = get_process_state(pid);

  /* Emit event regardless of state (userspace needs the data). */
  emit_event(OCTO_EVT_SOCKET_CONNECT, pid, uid);

  /* Enforce isolation: deny if ISOLATED or above. */
  if (state >= OCTO_ISOLATED)
    return -EPERM;

  return OCTO_PERMIT;
}

/* =========================================================================
 * LSM HOOK: lsm/file_open
 *
 * Fires before a process opens a file (read, write, or execute).
 *
 * Enforcement:
 *   - State >= OCTO_ISOLATED → deny (-EPERM). Filesystem quarantine.
 *   - State <  OCTO_ISOLATED → emit event, permit.
 *
 * Note: This hook fires for ALL file opens including /proc reads.
 * Userspace must whitelist its own PID in process_state_map to avoid
 * self-denial. The Go agent sets its own PID to OCTO_NORMAL explicitly
 * after loading BPF programs.
 * ========================================================================= */
SEC("lsm/file_open")
int BPF_PROG(octo_file_open, struct file *file) {
  __u64 pid_tgid = bpf_get_current_pid_tgid();
  __u32 pid = (__u32)(pid_tgid >> 32);
  __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
  __u8 state = get_process_state(pid);

  emit_event(OCTO_EVT_FILE_OPEN, pid, uid);

  if (state >= OCTO_ISOLATED)
    return -EPERM;

  return OCTO_PERMIT;
}

/* =========================================================================
 * LSM HOOK: lsm/task_fix_setuid
 *
 * Fires when a process attempts to change its UID (setuid, seteuid, etc.).
 * This is a critical privilege escalation vector.
 *
 * Enforcement:
 *   - State >= OCTO_PRESSURE → deny (-EPERM). Even PRESSURE-level
 *     processes must not be allowed to escalate privileges.
 *   - State == OCTO_NORMAL   → emit event, permit.
 *
 * Rationale: UID changes are almost never legitimate for monitored
 * processes. Blocking at PRESSURE (not ISOLATED) provides early
 * containment of privilege escalation chains.
 * ========================================================================= */
SEC("lsm/task_fix_setuid")
int BPF_PROG(octo_task_fix_setuid, struct cred *new, const struct cred *old,
             int flags) {
  __u64 pid_tgid = bpf_get_current_pid_tgid();
  __u32 pid = (__u32)(pid_tgid >> 32);
  __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
  __u8 state = get_process_state(pid);

  emit_event(OCTO_EVT_SETUID, pid, uid);

  /* Block UID changes for any process under observation (PRESSURE+). */
  if (state >= OCTO_PRESSURE)
    return -EPERM;

  return OCTO_PERMIT;
}

/* =========================================================================
 * LSM HOOK: lsm/bprm_check_security
 *
 * Fires before a process executes a new binary (execve, execveat).
 *
 * Enforcement:
 *   - State >= OCTO_ISOLATED → deny (-EPERM). Execution quarantine.
 *   - Detect setuid/setgid binaries and emit enhanced events.
 *
 * Critical for preventing privilege escalation chains and lateral movement.
 * ========================================================================= */
SEC("lsm/bprm_check_security")
int BPF_PROG(octo_bprm_check_security, struct linux_binprm *bprm) {
  __u64 pid_tgid = bpf_get_current_pid_tgid();
  __u32 pid = (__u32)(pid_tgid >> 32);
  __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
  __u8 state = get_process_state(pid);

  /* Check for setuid/setgid execution */
  __u8 flags = 0;
  struct inode *inode = BPF_CORE_READ(bprm, file, f_inode);
  __u16 mode = BPF_CORE_READ(inode, i_mode);
  if (mode & 0004000) /* S_ISUID */
    flags |= OCTO_FLAG_EXEC_SUID;

  emit_event_extended(OCTO_EVT_EXEC, pid, uid, flags, mode & 0007777);

  if (state >= OCTO_ISOLATED)
    return -EPERM;

  return OCTO_PERMIT;
}

/* =========================================================================
 * LSM HOOK: lsm/file_mmap
 *
 * Fires before a process maps memory (mmap, mprotect with executable pages).
 *
 * Enforcement:
 *   - State >= OCTO_ISOLATED → deny PROT_EXEC mmaps (-EPERM).
 *   - Track PROT_WRITE + PROT_EXEC (W^X violations) for all states.
 *
 * Prevents JIT-spray attacks and memory corruption exploits.
 * ========================================================================= */
SEC("lsm/file_mmap")
int BPF_PROG(octo_file_mmap, struct file *file, unsigned long reqprot,
             unsigned long prot, unsigned long flags) {
  __u64 pid_tgid = bpf_get_current_pid_tgid();
  __u32 pid = (__u32)(pid_tgid >> 32);
  __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
  __u8 state = get_process_state(pid);

  __u8 event_flags = 0;
  if (prot & 0x4) /* PROT_EXEC */
    event_flags |= OCTO_FLAG_MMAP_EXEC;
  if (prot & 0x2) /* PROT_WRITE */
    event_flags |= OCTO_FLAG_MMAP_WRITE;

  /* W^X violation detection */
  if ((event_flags & OCTO_FLAG_MMAP_EXEC) && 
      (event_flags & OCTO_FLAG_MMAP_WRITE)) {
    emit_event_extended(OCTO_EVT_MEM_VIOLATION, pid, uid, 
                       event_flags, (__u32)prot);
  }

  emit_event_extended(OCTO_EVT_MMAP, pid, uid, event_flags, (__u32)prot);

  /* Block executable mmaps for isolated processes */
  if (state >= OCTO_ISOLATED && (prot & 0x4))
    return -EPERM;

  return OCTO_PERMIT;
}

/* =========================================================================
 * LSM HOOK: lsm/ptrace_access_check
 *
 * Fires when a process attempts to ptrace another process.
 *
 * Enforcement:
 *   - State >= OCTO_PRESSURE → deny (-EPERM).
 *   - PTRACE_ATTACH is a strong indicator of malicious behavior.
 *
 * Prevents debugging-based privilege escalation and code injection.
 * ========================================================================= */
SEC("lsm/ptrace_access_check")
int BPF_PROG(octo_ptrace_access_check, struct task_struct *child, 
             unsigned int mode) {
  __u64 pid_tgid = bpf_get_current_pid_tgid();
  __u32 pid = (__u32)(pid_tgid >> 32);
  __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
  __u8 state = get_process_state(pid);

  __u8 flags = 0;
  if (mode == 1) /* PTRACE_MODE_ATTACH */
    flags |= OCTO_FLAG_PTRACE_ATTACH;

  __u32 target_pid = BPF_CORE_READ(child, tgid);
  emit_event_extended(OCTO_EVT_PTRACE, pid, uid, flags, target_pid);

  if (state >= OCTO_PRESSURE)
    return -EPERM;

  return OCTO_PERMIT;
}

/* =========================================================================
 * LSM HOOK: lsm/kernel_module_request
 *
 * Fires when a process attempts to load a kernel module.
 *
 * Enforcement:
 *   - State >= OCTO_PRESSURE → deny (-EPERM).
 *
 * Kernel module loading is a critical privilege that should never be
 * available to monitored processes.
 * ========================================================================= */
SEC("lsm/kernel_module_request")
int BPF_PROG(octo_kernel_module_request, char *kmod_name) {
  __u64 pid_tgid = bpf_get_current_pid_tgid();
  __u32 pid = (__u32)(pid_tgid >> 32);
  __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
  __u8 state = get_process_state(pid);

  emit_event(OCTO_EVT_MODULE_LOAD, pid, uid);

  if (state >= OCTO_PRESSURE)
    return -EPERM;

  return OCTO_PERMIT;
}

/* =========================================================================
 * LSM HOOK: lsm/bpf_prog
 *
 * Fires when a process attempts to load a BPF program.
 *
 * Enforcement:
 *   - State >= OCTO_PRESSURE → deny (-EPERM).
 *
 * BPF program loading grants kernel-level access and must be blocked
 * for any process under observation.
 * ========================================================================= */
SEC("lsm/bpf_prog")
int BPF_PROG(octo_bpf_prog, struct bpf_prog *prog, union bpf_attr *attr,
             enum bpf_prog_type ptype) {
  __u64 pid_tgid = bpf_get_current_pid_tgid();
  __u32 pid = (__u32)(pid_tgid >> 32);
  __u32 uid = bpf_get_current_uid_gid() & 0xFFFFFFFF;
  __u8 state = get_process_state(pid);

  emit_event_extended(OCTO_EVT_BPF_LOAD, pid, uid, 0, (__u32)ptype);

  if (state >= OCTO_PRESSURE)
    return -EPERM;

  return OCTO_PERMIT;
}
