# Makefile for eBPF memory monitor

CLANG ?= clang
LLVM_STRIP ?= llvm-strip
BPFTOOL ?= bpftool

ARCH := $(shell uname -m | sed 's/x86_64/x86/' | sed 's/aarch64/arm64/')
INCLUDES := -I/usr/include/bpf -I/usr/include -I.

CLANG_FLAGS := -g -O2 -target bpf -D__TARGET_ARCH_$(ARCH)

all: memory_monitor.o

memory_monitor.o: memory_monitor.c
	$(CLANG) $(CLANG_FLAGS) $(INCLUDES) -c $< -o $@
	$(LLVM_STRIP) -g $@

clean:
	rm -f *.o

.PHONY: all clean
