/* SPDX-License-Identifier: GPL-2.0 */
/*
 * octoreflex.h — Shared kernel/userspace type definitions for OCTOREFLEX.
 *
 * This header is included by both the BPF C program and the Go userspace
 * agent (via cgo or bpf2go generated bindings). All types must be
 * layout-compatible between the two environments.
 *
 * Constraints:
 *   - No pointers in map values (BPF verifier restriction).
 *   - All integers explicitly sized.
 *   - Padding explicit to avoid ABI surprises.
 *   - Enums represented as u8 to minimise map value size.
 */

#ifndef __OCTOREFLEX_H__
#define __OCTOREFLEX_H__

#include <linux/types.h>

/* =========================================================================
 * PROCESS ISOLATION STATE
 *
 * Monotonic escalation path:
 *   NORMAL → PRESSURE → ISOLATED → FROZEN → QUARANTINED → TERMINATED
 *
 * Decay (FROZEN → ISOLATED → PRESSURE → NORMAL) is performed exclusively
 * by userspace after a configurable cool-down period. The kernel enforces
 * the current state but never decrements it autonomously.
 * ========================================================================= */

typedef enum __attribute__((packed)) octo_state {
    OCTO_NORMAL      = 0,  /* No anomaly detected. All syscalls permitted. */
    OCTO_PRESSURE    = 1,  /* Anomaly accumulating. Monitoring intensified. */
    OCTO_ISOLATED    = 2,  /* Network blocked. File writes restricted.      */
    OCTO_FROZEN      = 3,  /* cgroup freeze applied. Process suspended.     */
    OCTO_QUARANTINED = 4,  /* Moved to dedicated PID namespace.             */
    OCTO_TERMINATED  = 5,  /* SIGKILL sent. Entry retained for audit.       */
} octo_state_t;

/* =========================================================================
 * KERNEL EVENT TYPES
 *
 * Emitted to the ring buffer on each LSM hook invocation.
 * Userspace consumes these to drive the anomaly engine.
 * ========================================================================= */

typedef enum __attribute__((packed)) octo_event_type {
    OCTO_EVT_SOCKET_CONNECT = 1,  /* lsm/socket_connect hook fired         */
    OCTO_EVT_FILE_OPEN      = 2,  /* lsm/file_open hook fired              */
    OCTO_EVT_SETUID         = 3,  /* lsm/task_fix_setuid hook fired        */
    OCTO_EVT_EXEC           = 4,  /* lsm/bprm_check_security hook fired    */
    OCTO_EVT_MMAP           = 5,  /* lsm/file_mmap hook fired              */
    OCTO_EVT_PTRACE         = 6,  /* lsm/ptrace_access_check hook fired    */
    OCTO_EVT_MODULE_LOAD    = 7,  /* lsm/kernel_module_request hook fired  */
    OCTO_EVT_BPF_LOAD       = 8,  /* lsm/bpf_prog hook fired               */
    OCTO_EVT_MEM_VIOLATION  = 9,  /* memory access violation detected      */
} octo_event_type_t;

/* =========================================================================
 * KERNEL EVENT RECORD
 *
 * Written to the ring buffer by BPF programs. Fixed size: 24 bytes.
 * Alignment: 8 bytes (natural for int64 timestamp).
 *
 * Layout:
 *   [0..3]   pid        u32
 *   [4..7]   uid        u32
 *   [8]      event_type u8
 *   [9..11]  _pad       u8[3]
 *   [12..15] _pad2      u32
 *   [16..23] timestamp  s64  (nanoseconds since boot, bpf_ktime_get_ns())
 *
 * Total: 24 bytes. No trailing padding needed (aligned to 8).
 * ========================================================================= */

struct octo_event {
    __u32              pid;
    __u32              uid;
    __u8               event_type;   /* octo_event_type_t */
    __u8               flags;        /* event flags (exec_suid, mmap_exec, etc) */
    __u8               _pad[2];
    __u32              metadata;     /* event-specific metadata */
    __s64              timestamp_ns; /* bpf_ktime_get_ns() */
};

/* =========================================================================
 * REFLEX BUDGET RECORD
 *
 * Stored in reflex_budget_map at key=0.
 * Atomic decrements by BPF programs when emitting events.
 * Userspace refills every 60 seconds.
 * ========================================================================= */

struct octo_budget {
    __u32 remaining_tokens;
    __u32 _pad;
};

/* =========================================================================
 * MAP SIZE CONSTANTS
 *
 * Defined here so both BPF C and Go loader use identical values.
 * ========================================================================= */

#define OCTO_PROCESS_STATE_MAP_MAX  16384U
#define OCTO_RINGBUF_SIZE           (1U << 24)  /* 16 MiB */
#define OCTO_BUDGET_MAP_MAX         1U
#define OCTO_CGROUP_MAP_MAX         4096U
#define OCTO_MEM_TRACK_MAP_MAX      8192U

/* Event flag bits */
#define OCTO_FLAG_EXEC_SUID         (1 << 0)  /* exec with setuid bit */
#define OCTO_FLAG_MMAP_EXEC         (1 << 1)  /* mmap with PROT_EXEC */
#define OCTO_FLAG_MMAP_WRITE        (1 << 2)  /* mmap with PROT_WRITE */
#define OCTO_FLAG_PTRACE_ATTACH     (1 << 3)  /* ptrace attach (not read) */
#define OCTO_FLAG_MEM_OVERFLOW      (1 << 4)  /* buffer overflow detected */

/* =========================================================================
 * ENFORCEMENT RETURN CODES
 *
 * LSM hooks return 0 to permit or -EPERM to deny.
 * ========================================================================= */

#define OCTO_PERMIT  0
#define OCTO_DENY   -1  /* Resolved to -EPERM by LSM framework */

#endif /* __OCTOREFLEX_H__ */
