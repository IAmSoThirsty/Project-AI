# OctoReflex Memory Protection

Comprehensive memory protection subsystem for OctoReflex providing defense against memory-based attacks.

## Features

### 1. ASLR Enforcement
- Verifies Address Space Layout Randomization is enabled
- Checks `/proc/sys/kernel/randomize_va_space` on Linux
- Ensures full memory randomization (value = 2)
- Prevents predictable memory layout attacks

### 2. Stack Canaries
- Implements stack canary values to detect buffer overflows
- Address-specific canaries (XOR with address)
- Magic value: `0xDEADBEEFCAFEBABE`
- Automatic verification on memory free
- Metrics tracking for canary violations

### 3. DEP/NX Verification
- Ensures Data Execution Prevention is active
- Verifies NX (No-Execute) bit enforcement
- Tests memory protection mechanisms
- Prevents code execution in data segments

### 4. Secure Memory Wiping
- Multi-pass secure wipe similar to `sodium_memzero`
- Four-pass wipe cycle:
  1. Zero pass (0x00)
  2. 0xFF pass
  3. Pattern pass (sequential)
  4. Final zero pass
- Prevents compiler optimization with `runtime.KeepAlive`
- Automatic wiping on memory free

### 5. Anti-Dump Mechanisms
- Uses `prctl(PR_SET_DUMPABLE, 0)` to prevent ptrace attachment
- Disables core dumps via `RLIMIT_CORE = 0`
- Blocks external debugger attachment (GDB, etc.)
- Prevents `/proc/mem` reading
- Protects against memory dumping attacks

### 6. Memory Tagging
- Tags memory regions for tracking and auditing
- Per-tag region listing
- Checksum calculation for integrity
- Hierarchical organization by tag
- Query allocations by tag

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Protection Manager                      │
│  - ASLR Verification                                     │
│  - DEP Verification                                      │
│  - Anti-Dump Setup                                       │
│  - Tagged Region Tracking                                │
└─────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────┐
│   Secure      │  │   Memory     │  │   eBPF       │
│   Allocator   │  │   Monitor    │  │   Hooks      │
│               │  │              │  │              │
│ - Allocate    │  │ - Malloc     │  │ - Tracepoint │
│ - Free        │  │ - Mmap       │  │ - Kprobe     │
│ - Resize      │  │ - Munmap     │  │ - USDT       │
│ - Lock/Unlock │  │ - Violations │  │ - Events     │
└───────────────┘  └──────────────┘  └──────────────┘
```

## Usage

### Basic Protection

```go
// Initialize protection manager
pm, err := memory.NewProtectionManager()
if err != nil {
    log.Fatal(err)
}

// All protections are now active:
// - ASLR verified
// - DEP verified
// - Anti-dump enabled
```

### Secure Allocation

```go
// Create secure allocator
sa := memory.NewSecureAllocator(pm)

// Allocate sensitive memory
alloc, err := sa.Allocate(4096, "api-key", 
    memory.WithFlags(memory.FlagSensitive))
if err != nil {
    log.Fatal(err)
}

// Use the memory
copy(alloc.Data, []byte("SECRET_KEY"))

// Free (automatically wiped)
sa.Free(alloc)
```

### Canary Protection

```go
// Allocate with stack canary
alloc, err := sa.Allocate(8192, "buffer",
    memory.WithFlags(memory.FlagSensitive),
    memory.WithCanary())

// Buffer overflow will be detected on free
err = sa.Free(alloc)
if err != nil {
    // Canary violation detected
    log.Printf("Buffer overflow: %v", err)
}
```

### Guard Pages

```go
// Allocate with guard pages
alloc, err := sa.Allocate(4096, "protected",
    memory.WithFlags(memory.FlagSensitive),
    memory.WithGuardPages())

// Out-of-bounds access will cause SIGSEGV
```

### Memory Locking

```go
// Lock memory (prevent swap)
alloc, err := sa.Allocate(4096, "sensitive",
    memory.WithFlags(memory.FlagSensitive),
    memory.WithLock())

// Memory is locked in RAM
// Cannot be swapped to disk
```

### Secure Buffer

```go
// High-level secure buffer
buf, err := memory.NewSecureBuffer(sa, 1024, "session",
    memory.WithFlags(memory.FlagSensitive),
    memory.WithCanary())

// Write data
buf.Write([]byte("secret data"))

// Read data
data := buf.Read()

// Wipe explicitly
buf.Wipe()

// Close (wipes and frees)
buf.Close()
```

### Memory Monitoring (eBPF)

```go
// Start memory monitor
mm, err := memory.NewMemoryMonitor()
if err != nil {
    log.Fatal(err)
}
defer mm.Close()

// Register event handler
mm.RegisterHandler(memory.EventHandlerFunc(func(e *memory.MemoryEvent) error {
    log.Printf("Memory event: %s", e.String())
    return nil
}))

// Monitor tracks:
// - malloc/free
// - mmap/munmap
// - mprotect
// - ptrace attempts
// - core dump attempts
// - buffer overflows
// - use-after-free
// - double-free
```

## Allocation Flags

```go
const (
    FlagSensitive   uint32 = 1 << 0  // Mark as sensitive data
    FlagExecutable  uint32 = 1 << 1  // Allow execution (dangerous)
    FlagReadOnly    uint32 = 1 << 2  // Read-only memory
    FlagGuarded     uint32 = 1 << 3  // Add guard pages
    FlagCanary      uint32 = 1 << 4  // Add stack canary
)
```

## Memory Events

```go
const (
    EventMalloc         // Memory allocation
    EventFree           // Memory free
    EventMmap           // Memory mapping
    EventMunmap         // Memory unmapping
    EventMprotect       // Protection change
    EventBrk            // Heap expansion
    EventStackGrow      // Stack growth
    EventBufferOverflow // Buffer overflow detected
    EventUseAfterFree   // Use-after-free detected
    EventDoubleFree     // Double-free detected
    EventPtraceAttach   // Ptrace attempt blocked
    EventCoreDump       // Core dump attempt blocked
)
```

## Metrics

### Protection Metrics

```go
type ProtectionMetrics struct {
    CanaryViolations  uint64  // Stack canary violations
    MemoryWipes       uint64  // Secure wipe operations
    DumpAttempts      uint64  // Dump attempts blocked
    ASLRVerifications uint64  // ASLR checks
    DEPVerifications  uint64  // DEP checks
    TaggedAllocations uint64  // Tagged allocations
}

metrics := pm.GetMetrics()
```

### Allocator Statistics

```go
type AllocatorStats struct {
    TotalAllocated  uint64  // Total allocations
    TotalFreed      uint64  // Total frees
    ActiveAllocs    uint64  // Active allocations
    BytesAllocated  uint64  // Total bytes allocated
    BytesFreed      uint64  // Total bytes freed
    ActiveBytes     uint64  // Currently allocated bytes
    PeakBytes       uint64  // Peak memory usage
    LockedBytes     uint64  // Locked memory bytes
}

stats := sa.GetStats()
```

### Monitor Statistics

```go
type MonitorStats struct {
    EventsReceived  uint64  // Events processed
    EventsDropped   uint64  // Events dropped
    MallocCalls     uint64  // malloc calls
    FreeCalls       uint64  // free calls
    MmapCalls       uint64  // mmap calls
    MunmapCalls     uint64  // munmap calls
    MprotectCalls   uint64  // mprotect calls
    Violations      uint64  // Security violations
    PtraceBlocked   uint64  // Ptrace attempts blocked
    CoreDumpBlocked uint64  // Core dumps blocked
}

stats := mm.GetStats()
```

## eBPF Implementation

### Hooks

The memory monitor attaches to:

- **Tracepoints**:
  - `syscalls/sys_enter_brk`
  - `syscalls/sys_enter_mmap`
  - `syscalls/sys_exit_mmap`
  - `syscalls/sys_enter_munmap`
  - `syscalls/sys_enter_mprotect`
  - `syscalls/sys_enter_ptrace`

- **Kprobes**:
  - `do_coredump`
  - `expand_stack`

- **USDT Probes**:
  - `octoreflex:buffer_overflow`

### Building eBPF Programs

```bash
cd octoreflex/internal/memory/bpf
make
```

Requirements:
- `clang` with BPF support
- `llvm-strip`
- Linux kernel headers

## Security Properties

### Defense in Depth

1. **ASLR**: Randomizes memory layout
2. **DEP/NX**: Prevents code execution in data
3. **Stack Canaries**: Detects buffer overflows
4. **Guard Pages**: Catches out-of-bounds access
5. **Anti-Dump**: Blocks memory dumping
6. **Secure Wiping**: Prevents data leakage
7. **Memory Locking**: Prevents swap exposure
8. **eBPF Monitoring**: Real-time threat detection

### Attack Mitigation

| Attack Type          | Mitigation                          |
|---------------------|-------------------------------------|
| Buffer Overflow     | Stack canaries, guard pages         |
| ROP/JOP             | DEP/NX, ASLR                        |
| Use-After-Free      | eBPF monitoring, secure wipe        |
| Double-Free         | eBPF monitoring, tracking           |
| Memory Disclosure   | Secure wipe, memory locking         |
| Ptrace/Debug        | Anti-dump, prctl protections        |
| Core Dump           | RLIMIT_CORE = 0                     |
| Stack Smashing      | Canaries with address-specific XOR  |

## Performance

### Benchmarks

```
BenchmarkSecureAlloc/4KB              50000    35000 ns/op
BenchmarkSecureAlloc/4KB_with_canary  45000    37000 ns/op
BenchmarkSecureAlloc/4KB_with_guards  40000    42000 ns/op
BenchmarkSecureWipe/1024B            500000     3000 ns/op
BenchmarkSecureWipe/4096B            200000     8000 ns/op
BenchmarkAllocator/alloc/free         50000    35000 ns/op
BenchmarkAllocator/alloc/free_locked  45000    40000 ns/op
```

### Overhead

- Basic allocation: ~5-10% overhead
- With canary: ~8-12% overhead
- With guard pages: ~15-20% overhead
- Secure wipe: ~2-5μs per 4KB
- eBPF monitoring: <1% CPU overhead

## Integration

### With OctoReflex

```go
import "github.com/octoreflex/octoreflex/internal/memory"

// In your OctoReflex initialization:
pm, _ := memory.NewProtectionManager()
allocator := memory.NewSecureAllocator(pm)
monitor, _ := memory.NewMemoryMonitor()

// Use throughout the system for sensitive data
```

### Red Team Testing

See `octoreflex/test/integration/memory_exploits_test.go` for:
- Buffer overflow attempts
- Use-after-free exploits
- Double-free exploits
- Ptrace attacks
- Memory dump attempts
- ROP attack mitigation
- ASLR bypass attempts
- Memory disclosure tests

## Troubleshooting

### ASLR Not Enabled

```bash
# Check ASLR status
cat /proc/sys/kernel/randomize_va_space

# Enable ASLR (requires root)
echo 2 | sudo tee /proc/sys/kernel/randomize_va_space
```

### eBPF Not Loading

```bash
# Check kernel version (requires 4.18+)
uname -r

# Install kernel headers
sudo apt-get install linux-headers-$(uname -r)

# Check BPF capability
sudo bpftool prog list
```

### Memory Locking Fails

```bash
# Check memlock limit
ulimit -l

# Increase limit (temporary)
ulimit -l unlimited

# Permanent (add to /etc/security/limits.conf)
* soft memlock unlimited
* hard memlock unlimited
```

## References

- [Address Space Layout Randomization (ASLR)](https://en.wikipedia.org/wiki/Address_space_layout_randomization)
- [Data Execution Prevention (DEP)](https://en.wikipedia.org/wiki/Executable_space_protection)
- [Stack Canaries](https://en.wikipedia.org/wiki/Stack_buffer_overflow#Stack_canaries)
- [libsodium secure memory](https://doc.libsodium.org/memory_management)
- [eBPF](https://ebpf.io/)
- [prctl(2)](https://man7.org/linux/man-pages/man2/prctl.2.html)
