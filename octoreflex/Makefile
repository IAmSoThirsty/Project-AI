# Makefile — OCTOREFLEX root build system.
#
# Targets:
#   make bpf      — compile BPF CO-RE object (requires clang 16+, root for vmlinux.h)
#   make agent    — build Go userspace agent binary (static, Linux/amd64)
#   make sim      — build Go simulator binary
#   make cli      — build octoreflex-cli binary
#   make test     — run all Go tests + Python simulator tests
#   make release  — static stripped release build of all binaries
#   make proto    — regenerate protobuf Go bindings
#   make clean    — remove all build artifacts
#   make lint     — run golangci-lint + staticcheck
#   make vet      — run go vet
#
# Environment variables:
#   CLANG         — clang binary (default: clang)
#   BPFTOOL       — bpftool binary (default: bpftool)
#   GOFLAGS       — extra go build flags
#   CGO_ENABLED   — set to 0 for static builds (default for release)
#   VERSION       — override version string (default: read from VERSION file)

SHELL := /bin/bash
.DEFAULT_GOAL := agent

# ── Version ──────────────────────────────────────────────────────────────────
VERSION     := $(shell cat VERSION 2>/dev/null || echo "0.0.0-dev")
GIT_COMMIT  := $(shell git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_TIME  := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

# ── Go configuration ──────────────────────────────────────────────────────────
GO          := go
GOOS        := linux
GOARCH      := amd64
MODULE      := github.com/octoreflex/octoreflex

# Linker flags injected into all Go binaries.
# -s -w: strip symbol table and DWARF debug info (release only).
# -X: embed version, commit, and build time into the binary.
LD_VERSION_FLAGS := \
    -X $(MODULE)/internal/config.Version=$(VERSION) \
    -X $(MODULE)/internal/config.GitCommit=$(GIT_COMMIT) \
    -X $(MODULE)/internal/config.BuildTime=$(BUILD_TIME)

LDFLAGS_DEBUG   := -ldflags "$(LD_VERSION_FLAGS)"
LDFLAGS_RELEASE := -ldflags "-s -w $(LD_VERSION_FLAGS)"

# ── Output directories ────────────────────────────────────────────────────────
BIN_DIR := bin

# ── BPF configuration ─────────────────────────────────────────────────────────
CLANG      ?= clang
BPFTOOL    ?= bpftool
BPF_DIR    := bpf
BPF_OBJ    := $(BPF_DIR)/octoreflex.bpf.o

# ── Protobuf configuration ────────────────────────────────────────────────────
PROTOC         ?= protoc
PROTO_DIR      := api/proto
PROTO_GEN_DIR  := api/generated
PROTO_FILES    := $(wildcard $(PROTO_DIR)/*.proto)

# ── Tools ─────────────────────────────────────────────────────────────────────
GOLANGCI_LINT  ?= golangci-lint
STATICCHECK    ?= staticcheck
PYTEST         ?= pytest

.PHONY: all bpf agent sim cli test test-unit test-integration test-adversarial \
        test-fuzz test-performance test-chaos test-all coverage release proto \
        clean lint vet vmlinux check-tools install uninstall bench-latency bench-lockfree

# ── bpf ───────────────────────────────────────────────────────────────────────
# Compile the BPF CO-RE object. Delegates to bpf/Makefile.
# The compiled object is embedded into the Go binary via go:embed in
# internal/bpf/loader.go so the agent ships as a single self-contained binary.
bpf:
	@echo "==> Building BPF CO-RE object..."
	$(MAKE) -C $(BPF_DIR) all CLANG=$(CLANG) BPFTOOL=$(BPFTOOL)
	@echo "==> BPF object: $(BPF_OBJ)"

# ── agent ─────────────────────────────────────────────────────────────────────
# Build the main octoreflex agent binary.
# Requires the BPF object to exist (embedded via go:embed).
# CGO_ENABLED=1 required for cilium/ebpf's cgo-based libbpf bindings.
agent: bpf
	@echo "==> Building octoreflex agent ($(GOOS)/$(GOARCH))..."
	@mkdir -p $(BIN_DIR)
	GOOS=$(GOOS) GOARCH=$(GOARCH) CGO_ENABLED=1 \
	    $(GO) build $(LDFLAGS_DEBUG) \
	    -o $(BIN_DIR)/octoreflex \
	    ./cmd/octoreflex/
	@echo "==> Binary: $(BIN_DIR)/octoreflex"

# ── sim ───────────────────────────────────────────────────────────────────────
# Build the dominance simulator binary (no BPF dependency, pure Go).
sim:
	@echo "==> Building octoreflex-sim..."
	@mkdir -p $(BIN_DIR)
	GOOS=$(GOOS) GOARCH=$(GOARCH) CGO_ENABLED=0 \
	    $(GO) build $(LDFLAGS_DEBUG) \
	    -o $(BIN_DIR)/octoreflex-sim \
	    ./cmd/octoreflex-sim/
	@echo "==> Binary: $(BIN_DIR)/octoreflex-sim"

# ── cli ───────────────────────────────────────────────────────────────────────
# Build the operator CLI (log inspection, policy replay).
cli:
	@echo "==> Building octoreflex-cli..."
	@mkdir -p $(BIN_DIR)
	GOOS=$(GOOS) GOARCH=$(GOARCH) CGO_ENABLED=0 \
	    $(GO) build $(LDFLAGS_DEBUG) \
	    -o $(BIN_DIR)/octoreflex-cli \
	    ./cmd/octoreflex-cli/
	@echo "==> Binary: $(BIN_DIR)/octoreflex-cli"

# ── test ──────────────────────────────────────────────────────────────────────
# Default test target: run unit tests only (fast, no root required)
test: test-unit

# Run unit tests with race detector and coverage
test-unit:
	@echo "==> Running unit tests..."
	$(GO) test -v -race -count=1 -coverprofile=coverage.out ./internal/...
	@echo "==> Unit tests complete."

# Run integration tests (requires root + BPF kernel)
test-integration: bpf
	@echo "==> Running integration tests..."
	@if [ -f /sys/kernel/btf/vmlinux ]; then \
	    sudo $(GO) test -v -count=1 ./test/integration/...; \
	else \
	    echo "    SKIP: /sys/kernel/btf/vmlinux not found (BPF kernel required)."; \
	fi

# Run adversarial attack simulations
test-adversarial:
	@echo "==> Running adversarial tests..."
	$(GO) test -v -count=1 ./test/adversarial/...
	@echo "==> Adversarial tests complete."

# Run fuzzing tests
test-fuzz:
	@echo "==> Running fuzz tests (10s per target)..."
	$(GO) test -fuzz=FuzzEventParser -fuzztime=10s ./test/fuzz || true
	$(GO) test -fuzz=FuzzConfigParser -fuzztime=10s ./test/fuzz || true
	$(GO) test -fuzz=FuzzAnomalyScore -fuzztime=10s ./test/fuzz || true
	@echo "==> Fuzzing complete."

# Run performance benchmarks
test-performance:
	@echo "==> Running performance benchmarks..."
	$(GO) test -bench=. -benchtime=10s -benchmem ./internal/lockfree/... | tee bench_lockfree.txt
	$(GO) test -bench=. -benchtime=10s -benchmem ./test/performance/... | tee bench.txt
	@echo "==> Performance tests complete."

# Run extreme latency benchmark (requires root for full optimization)
bench-latency:
	@echo "==> Building latency benchmark..."
	@mkdir -p $(BIN_DIR)
	$(GO) build -ldflags "-s -w" -o $(BIN_DIR)/latency-bench ./bench/cmd/latency-extreme/
	@echo "==> Benchmark binary: $(BIN_DIR)/latency-bench"
	@echo ""
	@echo "Run with: ./$(BIN_DIR)/latency-bench -iterations 100000"
	@echo "With optimizations (requires root): sudo ./$(BIN_DIR)/latency-bench -cpu 8 -rt 80 -iterations 100000"

# Run lock-free structure benchmarks
bench-lockfree:
	@echo "==> Benchmarking lock-free data structures..."
	$(GO) test -bench=. -benchtime=10s -benchmem ./internal/lockfree/
	@echo "==> Lock-free benchmarks complete."

# Run chaos engineering tests
test-chaos:
	@echo "==> Running chaos engineering tests..."
	$(GO) test -v -timeout=30m ./test/chaos
	@echo "==> Chaos tests complete."

# Run full test suite (unit + integration + adversarial + performance)
test-all: test-unit test-integration test-adversarial test-performance
	@echo "==> Full test suite complete."

# Generate coverage report
coverage:
	@echo "==> Generating coverage report..."
	$(GO) test -coverprofile=coverage.out ./internal/...
	$(GO) tool cover -html=coverage.out -o coverage.html
	@echo "==> Coverage summary:"
	@$(GO) tool cover -func=coverage.out | grep total
	@echo "==> Full report: coverage.html"

# ── release ───────────────────────────────────────────────────────────────────
# Fully static, stripped release build of all binaries.
# CGO_ENABLED=0 for sim and cli (pure Go).
# CGO_ENABLED=1 with static libbpf for agent (requires static libbpf.a).
# Sets -extldflags '-static' to force static linking.
release: bpf
	@echo "==> Building RELEASE binaries (static + stripped)..."
	@mkdir -p $(BIN_DIR)/release

	@echo "  → octoreflex agent (static, CGO)..."
	GOOS=$(GOOS) GOARCH=$(GOARCH) CGO_ENABLED=1 \
	    $(GO) build \
	    -ldflags "-s -w -extldflags '-static' $(LD_VERSION_FLAGS)" \
	    -o $(BIN_DIR)/release/octoreflex \
	    ./cmd/octoreflex/

	@echo "  → octoreflex-sim (static, no CGO)..."
	GOOS=$(GOOS) GOARCH=$(GOARCH) CGO_ENABLED=0 \
	    $(GO) build $(LDFLAGS_RELEASE) \
	    -o $(BIN_DIR)/release/octoreflex-sim \
	    ./cmd/octoreflex-sim/

	@echo "  → octoreflex-cli (static, no CGO)..."
	GOOS=$(GOOS) GOARCH=$(GOARCH) CGO_ENABLED=0 \
	    $(GO) build $(LDFLAGS_RELEASE) \
	    -o $(BIN_DIR)/release/octoreflex-cli \
	    ./cmd/octoreflex-cli/

	@echo "==> Release binaries in $(BIN_DIR)/release/:"
	@ls -lh $(BIN_DIR)/release/

# ── proto ─────────────────────────────────────────────────────────────────────
# Regenerate Go protobuf bindings from .proto files.
# Requires: protoc, protoc-gen-go, protoc-gen-go-grpc
proto:
	@echo "==> Generating protobuf bindings..."
	@mkdir -p $(PROTO_GEN_DIR)
	$(PROTOC) \
	    --proto_path=$(PROTO_DIR) \
	    --go_out=$(PROTO_GEN_DIR) \
	    --go_opt=paths=source_relative \
	    --go-grpc_out=$(PROTO_GEN_DIR) \
	    --go-grpc_opt=paths=source_relative \
	    $(PROTO_FILES)
	@echo "==> Protobuf generation complete."

# ── vmlinux ───────────────────────────────────────────────────────────────────
# Regenerate vmlinux.h from the running kernel. Run after kernel upgrades.
vmlinux:
	$(MAKE) -C $(BPF_DIR) vmlinux BPFTOOL=$(BPFTOOL)

# ── lint ──────────────────────────────────────────────────────────────────────
lint:
	@echo "==> Running golangci-lint..."
	$(GOLANGCI_LINT) run ./...
	@echo "==> Running staticcheck..."
	$(STATICCHECK) ./...

# ── vet ───────────────────────────────────────────────────────────────────────
vet:
	@echo "==> Running go vet..."
	$(GO) vet ./...

# ── check-tools ───────────────────────────────────────────────────────────────
# Verify all required tools are present before building.
check-tools:
	@echo "==> Checking required tools..."
	@command -v $(CLANG) >/dev/null 2>&1 || \
	    (echo "ERROR: clang not found. Install clang >= 16." && exit 1)
	@$(CLANG) --version | grep -qE "clang version (1[6-9]|[2-9][0-9])" || \
	    (echo "ERROR: clang >= 16 required." && exit 1)
	@command -v $(BPFTOOL) >/dev/null 2>&1 || \
	    (echo "ERROR: bpftool not found. Install linux-tools-$(uname -r)." && exit 1)
	@command -v $(GO) >/dev/null 2>&1 || \
	    (echo "ERROR: go not found. Install Go >= 1.22." && exit 1)
	@$(GO) version | grep -qE "go1\.(2[2-9]|[3-9][0-9])" || \
	    (echo "ERROR: Go >= 1.22 required." && exit 1)
	@command -v $(PYTEST) >/dev/null 2>&1 || \
	    (echo "ERROR: pytest not found. pip install pytest numpy." && exit 1)
	@echo "==> All required tools present."

# ── install ───────────────────────────────────────────────────────────────────
# Install agent binary and systemd unit to the local system.
# Requires root.
install: release
	@echo "==> Installing OCTOREFLEX..."
	install -m 0755 $(BIN_DIR)/release/octoreflex /usr/bin/octoreflex
	install -m 0755 $(BIN_DIR)/release/octoreflex-cli /usr/bin/octoreflex-cli
	install -m 0644 deploy/systemd/octoreflex.service \
	    /etc/systemd/system/octoreflex.service
	install -d /etc/octoreflex
	install -m 0600 config/config.yaml /etc/octoreflex/config.yaml
	install -d /var/lib/octoreflex
	systemctl daemon-reload
	@echo "==> Installation complete. Run: systemctl enable --now octoreflex"

# ── uninstall ─────────────────────────────────────────────────────────────────
uninstall:
	@echo "==> Uninstalling OCTOREFLEX..."
	-systemctl stop octoreflex
	-systemctl disable octoreflex
	rm -f /usr/bin/octoreflex /usr/bin/octoreflex-cli
	rm -f /etc/systemd/system/octoreflex.service
	systemctl daemon-reload
	@echo "==> Uninstall complete. /etc/octoreflex and /var/lib/octoreflex retained."

# ── clean ─────────────────────────────────────────────────────────────────────
clean:
	@echo "==> Cleaning build artifacts..."
	$(MAKE) -C $(BPF_DIR) clean
	rm -rf $(BIN_DIR)
	$(GO) clean -cache
	@echo "==> Clean complete."
