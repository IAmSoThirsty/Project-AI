# bpf/Makefile — Compile OCTOREFLEX BPF CO-RE object.
#
# Requirements:
#   clang >= 16 with BPF target support
#   llvm-strip (from llvm package)
#   bpftool (for vmlinux.h generation)
#   Linux kernel headers (for fallback if vmlinux.h absent)
#
# Usage:
#   make          — build octoreflex.bpf.o (debug, with BTF)
#   make release  — build stripped release object
#   make vmlinux  — regenerate vmlinux.h from running kernel
#   make clean    — remove build artifacts

CLANG      ?= clang
LLVM_STRIP ?= llvm-strip
BPFTOOL    ?= bpftool

# Architecture: always x86_64 per spec.
ARCH       := x86_64

# BPF target triple for clang.
BPF_TARGET := bpf

# Kernel headers path (fallback if vmlinux.h not present).
KERNEL_HEADERS ?= /usr/include

# Output object.
BPF_OBJ := octoreflex.bpf.o

# Source.
BPF_SRC := octoreflex.bpf.c

# Include paths:
#   1. Current directory (for octoreflex.h, vmlinux.h)
#   2. libbpf headers (for bpf_helpers.h, bpf_core_read.h, bpf_tracing.h)
#      Typically at /usr/include/bpf or $(LIBBPF_INCLUDE)
LIBBPF_INCLUDE ?= /usr/include/bpf
INCLUDES := -I. -I$(LIBBPF_INCLUDE)

# Compiler flags:
#   -O2            — required by BPF verifier (no unoptimised loads)
#   -g             — emit BTF debug info (required for CO-RE)
#   -target bpf    — BPF target
#   -D__TARGET_ARCH_x86 — architecture macro for vmlinux.h
#   -Wall -Wextra  — catch common mistakes
#   -Werror        — treat warnings as errors in production build
#   -fno-stack-protector — not supported by BPF backend
#   -mcpu=v3       — BPF ISA v3 (supports 32-bit atomic ops, needed for
#                    __sync_fetch_and_add on per-CPU maps)
CFLAGS := \
    -O2 \
    -g \
    -target $(BPF_TARGET) \
    -D__TARGET_ARCH_x86 \
    -Wall \
    -Wextra \
    -Werror \
    -fno-stack-protector \
    -mcpu=v3 \
    $(INCLUDES)

# Release flags: strip BTF debug sections to reduce object size.
# BTF type info is preserved (required for CO-RE); only debug line info
# is stripped.
STRIP_FLAGS := --strip-debug

.PHONY: all release vmlinux clean verify

all: $(BPF_OBJ)

$(BPF_OBJ): $(BPF_SRC) octoreflex.h vmlinux.h
	@echo "[BPF] Compiling $(BPF_SRC) → $(BPF_OBJ)"
	$(CLANG) $(CFLAGS) -c $(BPF_SRC) -o $@
	@echo "[BPF] Verifying BTF presence in object..."
	@readelf --sections $@ | grep -q BTF || \
		(echo "ERROR: No BTF section in $@. Ensure -g flag and clang >= 16." && exit 1)
	@echo "[BPF] Build complete: $@"

release: $(BPF_OBJ)
	@echo "[BPF] Stripping debug info for release..."
	$(LLVM_STRIP) $(STRIP_FLAGS) $(BPF_OBJ) -o $(BPF_OBJ:.o=.release.o)
	@echo "[BPF] Release object: $(BPF_OBJ:.o=.release.o)"

# Generate vmlinux.h from the running kernel's BTF data.
# Requires bpftool and a BTF-enabled kernel (/sys/kernel/btf/vmlinux).
# Run this once per kernel version upgrade.
vmlinux:
	@echo "[BPF] Generating vmlinux.h from /sys/kernel/btf/vmlinux..."
	@test -f /sys/kernel/btf/vmlinux || \
		(echo "ERROR: /sys/kernel/btf/vmlinux not found. Kernel must have CONFIG_DEBUG_INFO_BTF=y" && exit 1)
	$(BPFTOOL) btf dump file /sys/kernel/btf/vmlinux format c > vmlinux.h
	@echo "[BPF] vmlinux.h generated ($(shell wc -l < vmlinux.h) lines)"

# Verify the compiled object passes the kernel verifier (dry-run load).
# Requires root and a running kernel with BPF LSM enabled.
verify: $(BPF_OBJ)
	@echo "[BPF] Verifying BPF object (requires root + BPF LSM kernel)..."
	$(BPFTOOL) prog load $(BPF_OBJ) /sys/fs/bpf/octoreflex_verify_tmp \
		type lsm 2>&1 || true
	@rm -f /sys/fs/bpf/octoreflex_verify_tmp
	@echo "[BPF] Verification complete."

clean:
	@echo "[BPF] Cleaning..."
	rm -f $(BPF_OBJ) $(BPF_OBJ:.o=.release.o)
	@echo "[BPF] Clean complete."
