// SPDX-License-Identifier: GPL-2.0
// Memory monitoring eBPF program for OctoReflex

#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <linux/ptrace.h>
#include <linux/types.h>

#define TASK_COMM_LEN 16
#define MAX_STACK_DEPTH 20

// Event types
enum event_type {
    EVENT_MALLOC = 0,
    EVENT_FREE,
    EVENT_MMAP,
    EVENT_MUNMAP,
    EVENT_MPROTECT,
    EVENT_BRK,
    EVENT_STACK_GROW,
    EVENT_BUFFER_OVERFLOW,
    EVENT_USE_AFTER_FREE,
    EVENT_DOUBLE_FREE,
    EVENT_PTRACE_ATTACH,
    EVENT_CORE_DUMP,
};

// Memory event structure
struct memory_event {
    __u32 type;
    __u64 timestamp;
    __u32 pid;
    __u32 tid;
    __u64 addr;
    __u64 size;
    __u32 flags;
    char comm[TASK_COMM_LEN];
};

// Ring buffer for events
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} events SEC(".maps");

// Map to track allocations (for detecting use-after-free, double-free)
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __type(key, __u64);   // address
    __type(value, __u64); // size
    __uint(max_entries, 10000);
} allocations SEC(".maps");

// Map to track freed addresses (for detecting double-free)
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __type(key, __u64);   // address
    __type(value, __u64); // timestamp
    __uint(max_entries, 10000);
} freed_addrs SEC(".maps");

// Statistics map
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __type(key, __u32);
    __type(value, __u64);
    __uint(max_entries, 64);
} stats SEC(".maps");

// Helper to emit event
static __always_inline void emit_event(struct memory_event *event) {
    bpf_ringbuf_output(&events, event, sizeof(*event), 0);
}

// Helper to get current timestamp
static __always_inline __u64 get_timestamp() {
    return bpf_ktime_get_ns();
}

// Helper to increment stat counter
static __always_inline void inc_stat(__u32 idx) {
    __u64 *val = bpf_map_lookup_elem(&stats, &idx);
    if (val) {
        __sync_fetch_and_add(val, 1);
    }
}

// Tracepoint: sys_enter_brk
SEC("tracepoint/syscalls/sys_enter_brk")
int trace_brk(struct trace_event_raw_sys_enter *ctx) {
    struct memory_event *event;
    
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 0;
    
    event->type = EVENT_BRK;
    event->timestamp = get_timestamp();
    event->pid = bpf_get_current_pid_tgid() >> 32;
    event->tid = bpf_get_current_pid_tgid();
    event->addr = ctx->args[0];
    event->size = 0;
    event->flags = 0;
    bpf_get_current_comm(&event->comm, sizeof(event->comm));
    
    bpf_ringbuf_submit(event, 0);
    inc_stat(EVENT_BRK);
    
    return 0;
}

// Tracepoint: sys_enter_mmap
SEC("tracepoint/syscalls/sys_enter_mmap")
int trace_mmap(struct trace_event_raw_sys_enter *ctx) {
    struct memory_event *event;
    
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 0;
    
    event->type = EVENT_MMAP;
    event->timestamp = get_timestamp();
    event->pid = bpf_get_current_pid_tgid() >> 32;
    event->tid = bpf_get_current_pid_tgid();
    event->addr = ctx->args[0];
    event->size = ctx->args[1];
    event->flags = ctx->args[3];
    bpf_get_current_comm(&event->comm, sizeof(event->comm));
    
    bpf_ringbuf_submit(event, 0);
    inc_stat(EVENT_MMAP);
    
    return 0;
}

// Tracepoint: sys_exit_mmap (to track return address)
SEC("tracepoint/syscalls/sys_exit_mmap")
int trace_mmap_exit(struct trace_event_raw_sys_exit *ctx) {
    __u64 addr = ctx->ret;
    __u64 size = 0; // Size would need to be tracked from enter
    
    if (addr != -1ULL && addr != 0) {
        // Track allocation
        bpf_map_update_elem(&allocations, &addr, &size, BPF_ANY);
    }
    
    return 0;
}

// Tracepoint: sys_enter_munmap
SEC("tracepoint/syscalls/sys_enter_munmap")
int trace_munmap(struct trace_event_raw_sys_enter *ctx) {
    struct memory_event *event;
    __u64 addr = ctx->args[0];
    __u64 size = ctx->args[1];
    
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 0;
    
    event->type = EVENT_MUNMAP;
    event->timestamp = get_timestamp();
    event->pid = bpf_get_current_pid_tgid() >> 32;
    event->tid = bpf_get_current_pid_tgid();
    event->addr = addr;
    event->size = size;
    event->flags = 0;
    bpf_get_current_comm(&event->comm, sizeof(event->comm));
    
    // Check for double-free
    __u64 *freed_ts = bpf_map_lookup_elem(&freed_addrs, &addr);
    if (freed_ts) {
        event->type = EVENT_DOUBLE_FREE;
        inc_stat(EVENT_DOUBLE_FREE);
    } else {
        // Track freed address
        __u64 ts = get_timestamp();
        bpf_map_update_elem(&freed_addrs, &addr, &ts, BPF_ANY);
    }
    
    // Remove from allocations
    bpf_map_delete_elem(&allocations, &addr);
    
    bpf_ringbuf_submit(event, 0);
    inc_stat(EVENT_MUNMAP);
    
    return 0;
}

// Tracepoint: sys_enter_mprotect
SEC("tracepoint/syscalls/sys_enter_mprotect")
int trace_mprotect(struct trace_event_raw_sys_enter *ctx) {
    struct memory_event *event;
    
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 0;
    
    event->type = EVENT_MPROTECT;
    event->timestamp = get_timestamp();
    event->pid = bpf_get_current_pid_tgid() >> 32;
    event->tid = bpf_get_current_pid_tgid();
    event->addr = ctx->args[0];
    event->size = ctx->args[1];
    event->flags = ctx->args[2]; // protection flags
    bpf_get_current_comm(&event->comm, sizeof(event->comm));
    
    bpf_ringbuf_submit(event, 0);
    inc_stat(EVENT_MPROTECT);
    
    return 0;
}

// Tracepoint: sys_enter_ptrace (detect ptrace attacks)
SEC("tracepoint/syscalls/sys_enter_ptrace")
int trace_ptrace(struct trace_event_raw_sys_enter *ctx) {
    struct memory_event *event;
    __u32 request = ctx->args[0];
    
    // PTRACE_ATTACH = 16, PTRACE_SEIZE = 16902
    if (request == 16 || request == 16902) {
        event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
        if (!event)
            return 0;
        
        event->type = EVENT_PTRACE_ATTACH;
        event->timestamp = get_timestamp();
        event->pid = bpf_get_current_pid_tgid() >> 32;
        event->tid = bpf_get_current_pid_tgid();
        event->addr = ctx->args[1]; // target pid
        event->size = 0;
        event->flags = request;
        bpf_get_current_comm(&event->comm, sizeof(event->comm));
        
        bpf_ringbuf_submit(event, 0);
        inc_stat(EVENT_PTRACE_ATTACH);
    }
    
    return 0;
}

// Kprobe: do_coredump (detect core dump attempts)
SEC("kprobe/do_coredump")
int trace_coredump(struct pt_regs *ctx) {
    struct memory_event *event;
    
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 0;
    
    event->type = EVENT_CORE_DUMP;
    event->timestamp = get_timestamp();
    event->pid = bpf_get_current_pid_tgid() >> 32;
    event->tid = bpf_get_current_pid_tgid();
    event->addr = 0;
    event->size = 0;
    event->flags = 0;
    bpf_get_current_comm(&event->comm, sizeof(event->comm));
    
    bpf_ringbuf_submit(event, 0);
    inc_stat(EVENT_CORE_DUMP);
    
    return 0;
}

// Kprobe: expand_stack (detect stack growth)
SEC("kprobe/expand_stack")
int trace_stack_grow(struct pt_regs *ctx) {
    struct memory_event *event;
    
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 0;
    
    event->type = EVENT_STACK_GROW;
    event->timestamp = get_timestamp();
    event->pid = bpf_get_current_pid_tgid() >> 32;
    event->tid = bpf_get_current_pid_tgid();
    event->addr = PT_REGS_PARM1(ctx);
    event->size = 0;
    event->flags = 0;
    bpf_get_current_comm(&event->comm, sizeof(event->comm));
    
    bpf_ringbuf_submit(event, 0);
    inc_stat(EVENT_STACK_GROW);
    
    return 0;
}

// USDT probe: buffer_overflow (application-defined)
SEC("usdt/octoreflex:buffer_overflow")
int trace_buffer_overflow(struct pt_regs *ctx) {
    struct memory_event *event;
    
    event = bpf_ringbuf_reserve(&events, sizeof(*event), 0);
    if (!event)
        return 0;
    
    event->type = EVENT_BUFFER_OVERFLOW;
    event->timestamp = get_timestamp();
    event->pid = bpf_get_current_pid_tgid() >> 32;
    event->tid = bpf_get_current_pid_tgid();
    event->addr = PT_REGS_PARM1(ctx);
    event->size = PT_REGS_PARM2(ctx);
    event->flags = 0;
    bpf_get_current_comm(&event->comm, sizeof(event->comm));
    
    bpf_ringbuf_submit(event, 0);
    inc_stat(EVENT_BUFFER_OVERFLOW);
    
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
