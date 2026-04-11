# OctoReflex Memory Protection - Build & Test Guide

## Quick Start

### Building

```bash
# Build memory protection module
cd octoreflex/internal/memory
go build

# Build eBPF programs (Linux only)
cd bpf
make
cd ..
```

### Running Tests

```bash
# Run all tests (Linux only)
go test -v

# Run specific tests
go test -v -run TestSecureWipe
go test -v -run TestProtectionManager
go test -v -run TestSecureAllocator

# Run integration/exploit tests
cd ../../test/integration
go test -v -run TestExploit
```

### Running Demo

```bash
cd example
go run demo.go
```

## Building eBPF Programs

### Prerequisites

```bash
# Ubuntu/Debian
sudo apt-get install -y \
    clang \
    llvm \
    linux-headers-$(uname -r) \
    libbpf-dev

# Fedora/RHEL
sudo dnf install -y \
    clang \
    llvm \
    kernel-headers \
    libbpf-devel
```

### Compile

```bash
cd bpf
make
```

This creates `memory_monitor.o` which is embedded in the Go binary.

## Platform Support

| Platform | Protection | Allocator | Monitor | Tests |
|----------|-----------|-----------|---------|-------|
| Linux    | ✅ Full   | ✅ Full   | ✅ Full | ✅ Full |
| Windows  | ⚠️ Stub   | ⚠️ Stub   | ⚠️ Stub | ❌ Skip |
| macOS    | ⚠️ Stub   | ⚠️ Stub   | ⚠️ Stub | ❌ Skip |

On non-Linux platforms, stub implementations return errors indicating the feature is not supported.

## File Structure

```
memory/
├── README.md                    # Main documentation
├── BUILD.md                     # This file
├── protection.go                # Protection manager (Linux)
├── protection_stub.go           # Protection stubs (non-Linux)
├── allocator.go                 # Secure allocator (Linux)
├── allocator_stub.go            # Allocator stubs (non-Linux)
├── ebpf_monitor.go              # eBPF monitor (Linux)
├── ebpf_monitor_stub.go         # Monitor stubs (non-Linux)
├── memory_test.go               # Unit tests (Linux)
├── bpf/
│   ├── memory_monitor.c         # eBPF C source
│   ├── memory_monitor.o         # Compiled eBPF object
│   └── Makefile                 # eBPF build
└── example/
    └── demo.go                  # Demonstration program
```

## Testing on Linux

### Unit Tests

```bash
# All tests
go test -v

# With coverage
go test -v -cover

# With race detection
go test -v -race

# Benchmarks
go test -v -bench=. -benchmem
```

### Integration Tests

```bash
cd ../../test/integration

# All exploit tests
go test -v -run TestExploit

# Specific exploit
go test -v -run TestExploitBufferOverflow
go test -v -run TestExploitPtraceAttack
go test -v -run TestExploitMemoryDump
```

### Red Team Tests

The integration tests simulate real exploit attempts:

- **Buffer Overflow**: Canary corruption detection
- **Use-After-Free**: Freed memory access tracking
- **Double-Free**: Duplicate free detection
- **Ptrace Attack**: Debugger attachment blocking
- **Memory Dump**: Core dump prevention
- **ROP Attack**: DEP/NX verification
- **ASLR Bypass**: Randomization verification
- **Memory Disclosure**: Secure wipe verification

### Running as Root

Some tests require root privileges:

```bash
# Run with sudo
sudo go test -v -run TestExploitPtraceAttack

# Or add capabilities
sudo setcap cap_sys_ptrace,cap_sys_admin+eip $(which go)
go test -v -run TestExploitPtraceAttack
```

## Performance Testing

```bash
# Run benchmarks
go test -v -bench=BenchmarkSecureAlloc -benchmem
go test -v -bench=BenchmarkSecureWipe -benchmem
go test -v -bench=BenchmarkAllocator -benchmem

# CPU profiling
go test -bench=. -cpuprofile=cpu.prof
go tool pprof cpu.prof

# Memory profiling
go test -bench=. -memprofile=mem.prof
go tool pprof mem.prof
```

## Troubleshooting

### "Build failed" on Linux

Check Go version and dependencies:

```bash
go version  # Should be 1.21+
go mod tidy
go mod download
```

### "eBPF not loading"

Check kernel support:

```bash
# Kernel version (need 4.18+)
uname -r

# Check BPF support
cat /proc/kallsyms | grep bpf_prog_load

# Install headers
sudo apt-get install linux-headers-$(uname -r)
```

### "Memory locking fails"

Increase memlock limit:

```bash
# Check current limit
ulimit -l

# Increase temporarily
ulimit -l unlimited

# Permanent: add to /etc/security/limits.conf
echo "* soft memlock unlimited" | sudo tee -a /etc/security/limits.conf
echo "* hard memlock unlimited" | sudo tee -a /etc/security/limits.conf
```

### "ASLR verification failed"

Enable ASLR:

```bash
# Check status (should be 2)
cat /proc/sys/kernel/randomize_va_space

# Enable
echo 2 | sudo tee /proc/sys/kernel/randomize_va_space

# Permanent: add to /etc/sysctl.conf
echo "kernel.randomize_va_space = 2" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Memory Protection Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y clang llvm linux-headers-$(uname -r)
      - name: Build eBPF
        run: cd bpf && make
      - name: Run tests
        run: go test -v -race -cover
```

### Docker Testing

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    golang \
    clang \
    llvm \
    linux-headers-generic \
    libbpf-dev

WORKDIR /app
COPY . .

RUN cd bpf && make
RUN go test -v
```

Build and run:

```bash
docker build -t octoreflex-memory-test .
docker run --privileged octoreflex-memory-test
```

## Development

### Code Style

```bash
# Format code
go fmt ./...

# Lint
golangci-lint run

# Vet
go vet ./...
```

### Adding New Features

1. Update Linux implementation files (`*_linux.go` build tag)
2. Update stub files (`*_stub.go` with `!linux` tag)
3. Add tests in `*_test.go` (with Linux build tag)
4. Update documentation
5. Add integration tests if security-relevant

### eBPF Development

```bash
# Edit bpf/memory_monitor.c
# Rebuild
cd bpf && make

# Test loading
sudo bpftool prog load memory_monitor.o /sys/fs/bpf/memory_monitor

# View loaded programs
sudo bpftool prog list

# Cleanup
sudo rm /sys/fs/bpf/memory_monitor
```

## Release Checklist

- [ ] All tests pass on Linux
- [ ] Benchmarks show acceptable performance
- [ ] eBPF programs compile without warnings
- [ ] Documentation updated
- [ ] Integration tests pass
- [ ] No race conditions (`go test -race`)
- [ ] Code formatted and linted
- [ ] Platform stubs work correctly
- [ ] Demo runs successfully

## Support

For issues or questions:
1. Check this documentation
2. Review test files for examples
3. Check GitHub issues
4. Contact OctoReflex team
