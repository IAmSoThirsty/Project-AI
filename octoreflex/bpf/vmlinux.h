/* SPDX-License-Identifier: GPL-2.0 */
/*
 * vmlinux.h — Minimal kernel type definitions for OctoReflex eBPF programs.
 *
 * PRODUCTION NOTE:
 *   This is a STUB for documentation/testing purposes only.
 *   In production, generate vmlinux.h from your kernel's BTF data:
 *
 *     sudo bpftool btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h
 *
 * The real vmlinux.h is ~100,000 lines and contains all kernel struct
 * definitions with CO-RE relocations. This stub contains only the minimal
 * types needed for compilation on systems without BTF.
 *
 * Requirements:
 *   - Kernel >= 5.15 with CONFIG_DEBUG_INFO_BTF=y
 *   - /sys/kernel/btf/vmlinux must exist
 */

#ifndef __VMLINUX_H__
#define __VMLINUX_H__

/* Basic types from linux/types.h */
typedef signed char __s8;
typedef unsigned char __u8;
typedef signed short __s16;
typedef unsigned short __u16;
typedef signed int __s32;
typedef unsigned int __u32;
typedef signed long long __s64;
typedef unsigned long long __u64;

typedef __u8 u8;
typedef __u16 u16;
typedef __u32 u32;
typedef __u64 u64;
typedef __s8 s8;
typedef __s16 s16;
typedef __s32 s32;
typedef __s64 s64;

/* Kernel pointers are opaque in userspace */
struct task_struct;
struct file;
struct inode;
struct socket;
struct sockaddr;
struct linux_binprm;
struct cred;
struct bpf_prog;

/* BPF program type enumeration */
enum bpf_prog_type {
	BPF_PROG_TYPE_UNSPEC = 0,
	BPF_PROG_TYPE_SOCKET_FILTER,
	BPF_PROG_TYPE_KPROBE,
	BPF_PROG_TYPE_SCHED_CLS,
	BPF_PROG_TYPE_SCHED_ACT,
	BPF_PROG_TYPE_TRACEPOINT,
	BPF_PROG_TYPE_XDP,
	BPF_PROG_TYPE_PERF_EVENT,
	BPF_PROG_TYPE_CGROUP_SKB,
	BPF_PROG_TYPE_CGROUP_SOCK,
	BPF_PROG_TYPE_LWT_IN,
	BPF_PROG_TYPE_LWT_OUT,
	BPF_PROG_TYPE_LWT_XMIT,
	BPF_PROG_TYPE_SOCK_OPS,
	BPF_PROG_TYPE_SK_SKB,
	BPF_PROG_TYPE_CGROUP_DEVICE,
	BPF_PROG_TYPE_SK_MSG,
	BPF_PROG_TYPE_RAW_TRACEPOINT,
	BPF_PROG_TYPE_CGROUP_SOCK_ADDR,
	BPF_PROG_TYPE_LWT_SEG6LOCAL,
	BPF_PROG_TYPE_LIRC_MODE2,
	BPF_PROG_TYPE_SK_REUSEPORT,
	BPF_PROG_TYPE_FLOW_DISSECTOR,
	BPF_PROG_TYPE_CGROUP_SYSCTL,
	BPF_PROG_TYPE_RAW_TRACEPOINT_WRITABLE,
	BPF_PROG_TYPE_CGROUP_SOCKOPT,
	BPF_PROG_TYPE_TRACING,
	BPF_PROG_TYPE_STRUCT_OPS,
	BPF_PROG_TYPE_EXT,
	BPF_PROG_TYPE_LSM,
};

/* BPF attribute union (simplified) */
union bpf_attr {
	struct {
		__u32 prog_type;
		__u32 insn_cnt;
		__u64 insns;
		__u64 license;
		__u32 log_level;
		__u32 log_size;
		__u64 log_buf;
		__u32 kern_version;
		__u32 prog_flags;
		char prog_name[16];
	};
};

/*
 * PRODUCTION REMINDER:
 *   Replace this stub with real vmlinux.h before deploying to production.
 *   The stub does NOT contain CO-RE relocations and will break on kernel
 *   struct layout changes.
 *
 *   Generate real vmlinux.h:
 *     cd bpf
 *     make vmlinux
 */

#endif /* __VMLINUX_H__ */
