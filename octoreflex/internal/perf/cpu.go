// Package perf provides CPU pinning, NUMA awareness, and thread affinity
// optimization for ultra-low-latency operation.
//
// Features:
//   - Pin critical goroutines to dedicated CPU cores
//   - NUMA-aware memory allocation
//   - CPU isolation (isolcpus kernel parameter integration)
//   - Real-time scheduling (SCHED_FIFO) for critical threads
//   - Hardware prefetching hints

package perf

import (
	"fmt"
	"os"
	"runtime"
	"syscall"
	"unsafe"

	"golang.org/x/sys/unix"
)

// CPUSet represents a set of CPU cores for affinity binding.
type CPUSet struct {
	bits [16]uint64 // Supports up to 1024 CPUs
}

// NewCPUSet creates an empty CPU set.
func NewCPUSet() *CPUSet {
	return &CPUSet{}
}

// Set adds a CPU to the set.
func (s *CPUSet) Set(cpu int) {
	if cpu < 0 || cpu >= 1024 {
		panic("cpu must be in range 0-1023")
	}
	s.bits[cpu/64] |= 1 << (cpu % 64)
}

// Clear removes a CPU from the set.
func (s *CPUSet) Clear(cpu int) {
	if cpu < 0 || cpu >= 1024 {
		panic("cpu must be in range 0-1023")
	}
	s.bits[cpu/64] &^= 1 << (cpu % 64)
}

// IsSet checks if a CPU is in the set.
func (s *CPUSet) IsSet(cpu int) bool {
	if cpu < 0 || cpu >= 1024 {
		return false
	}
	return (s.bits[cpu/64] & (1 << (cpu % 64))) != 0
}

// Zero clears all CPUs from the set.
func (s *CPUSet) Zero() {
	for i := range s.bits {
		s.bits[i] = 0
	}
}

// PinCurrentThreadToCPU pins the current OS thread to a specific CPU core.
// This function must be called from a goroutine that has called runtime.LockOSThread().
//
// Use case: Pin the BPF event processor thread to an isolated core for
// predictable latency.
//
// Example:
//   runtime.LockOSThread()
//   defer runtime.UnlockOSThread()
//   perf.PinCurrentThreadToCPU(8)  // Pin to core 8
func PinCurrentThreadToCPU(cpu int) error {
	cpuset := NewCPUSet()
	cpuset.Set(cpu)
	return SetAffinity(0, cpuset) // 0 = current thread
}

// SetAffinity sets the CPU affinity mask for a thread.
//
// Parameters:
//   - tid: Thread ID (0 for current thread, or from syscall.Gettid())
//   - cpuset: Set of allowed CPUs
func SetAffinity(tid int, cpuset *CPUSet) error {
	_, _, errno := unix.Syscall(
		unix.SYS_SCHED_SETAFFINITY,
		uintptr(tid),
		uintptr(unsafe.Sizeof(*cpuset)),
		uintptr(unsafe.Pointer(cpuset)),
	)
	if errno != 0 {
		return fmt.Errorf("sched_setaffinity: %w", errno)
	}
	return nil
}

// GetAffinity retrieves the CPU affinity mask for a thread.
func GetAffinity(tid int) (*CPUSet, error) {
	cpuset := NewCPUSet()
	_, _, errno := unix.Syscall(
		unix.SYS_SCHED_GETAFFINITY,
		uintptr(tid),
		uintptr(unsafe.Sizeof(*cpuset)),
		uintptr(unsafe.Pointer(cpuset)),
	)
	if errno != 0 {
		return nil, fmt.Errorf("sched_getaffinity: %w", errno)
	}
	return cpuset, nil
}

// SchedParam represents scheduling parameters for real-time priority.
type SchedParam struct {
	Priority int32
}

// SetRealtimePriority sets SCHED_FIFO real-time priority for the current thread.
// Requires CAP_SYS_NICE capability.
//
// Priority range: 1-99 (99 = highest)
//
// Use case: Give the BPF ring buffer reader thread hard real-time guarantees
// to minimize event processing latency.
//
// WARNING: Misconfigured RT priorities can hang the system. Use with caution.
func SetRealtimePriority(priority int) error {
	if priority < 1 || priority > 99 {
		return fmt.Errorf("RT priority must be 1-99, got %d", priority)
	}

	param := SchedParam{Priority: int32(priority)}
	_, _, errno := unix.Syscall(
		unix.SYS_SCHED_SETSCHEDULER,
		uintptr(syscall.Gettid()),
		uintptr(unix.SCHED_FIFO),
		uintptr(unsafe.Pointer(&param)),
	)
	if errno != 0 {
		return fmt.Errorf("sched_setscheduler SCHED_FIFO: %w", errno)
	}
	return nil
}

// NUMANode represents a NUMA node with its associated CPUs and memory.
type NUMANode struct {
	Node int      // NUMA node ID
	CPUs []int    // CPU cores in this node
	MemMB uint64  // Total memory in MB
}

// GetNUMATopology reads the system's NUMA topology from sysfs.
// Returns a slice of NUMA nodes with their associated CPUs.
//
// Use case: Allocate event processing structures on the same NUMA node
// as the CPU processing them to minimize memory access latency.
func GetNUMATopology() ([]NUMANode, error) {
	// Check if NUMA is available.
	if _, err := os.Stat("/sys/devices/system/node"); err != nil {
		if os.IsNotExist(err) {
			// No NUMA on this system, return single node with all CPUs.
			numCPU := runtime.NumCPU()
			cpus := make([]int, numCPU)
			for i := 0; i < numCPU; i++ {
				cpus[i] = i
			}
			return []NUMANode{{Node: 0, CPUs: cpus}}, nil
		}
		return nil, err
	}

	// Read NUMA nodes from sysfs.
	nodeDir := "/sys/devices/system/node"
	entries, err := os.ReadDir(nodeDir)
	if err != nil {
		return nil, fmt.Errorf("read %s: %w", nodeDir, err)
	}

	var nodes []NUMANode
	for _, entry := range entries {
		// NUMA node directories are named "node0", "node1", etc.
		var nodeID int
		if _, err := fmt.Sscanf(entry.Name(), "node%d", &nodeID); err != nil {
			continue
		}

		// Read CPUs in this node.
		cpulistPath := fmt.Sprintf("%s/node%d/cpulist", nodeDir, nodeID)
		data, err := os.ReadFile(cpulistPath)
		if err != nil {
			continue
		}

		cpus, err := parseCPUList(string(data))
		if err != nil {
			continue
		}

		// Read memory info.
		meminfoPath := fmt.Sprintf("%s/node%d/meminfo", nodeDir, nodeID)
		memMB := uint64(0)
		if data, err := os.ReadFile(meminfoPath); err == nil {
			// Parse "Node N MemTotal: XXXXX kB"
			var totalKB uint64
			fmt.Sscanf(string(data), "Node %*d MemTotal: %d kB", &totalKB)
			memMB = totalKB / 1024
		}

		nodes = append(nodes, NUMANode{
			Node:  nodeID,
			CPUs:  cpus,
			MemMB: memMB,
		})
	}

	return nodes, nil
}

// parseCPUList parses a Linux CPU list string (e.g., "0-3,8-11") into a slice.
func parseCPUList(s string) ([]int, error) {
	var cpus []int
	var start, end int

	for i := 0; i < len(s); {
		// Parse a number or range.
		if _, err := fmt.Sscanf(s[i:], "%d-%d", &start, &end); err == nil {
			// Range: "X-Y"
			for cpu := start; cpu <= end; cpu++ {
				cpus = append(cpus, cpu)
			}
			// Skip past the range.
			for i < len(s) && (s[i] >= '0' && s[i] <= '9' || s[i] == '-') {
				i++
			}
		} else if _, err := fmt.Sscanf(s[i:], "%d", &start); err == nil {
			// Single number.
			cpus = append(cpus, start)
			// Skip past the number.
			for i < len(s) && s[i] >= '0' && s[i] <= '9' {
				i++
			}
		} else {
			return nil, fmt.Errorf("invalid CPU list format: %s", s)
		}

		// Skip comma or whitespace.
		for i < len(s) && (s[i] == ',' || s[i] == ' ' || s[i] == '\n') {
			i++
		}
	}

	return cpus, nil
}

// Prefetch issues a CPU prefetch hint for the given memory address.
// This can reduce latency for predictable memory access patterns.
//
// Use case: Prefetch the next event in the BPF ring buffer while
// processing the current one.
//
// Note: This is a hint; the CPU may ignore it. Effectiveness varies
// by microarchitecture.
func Prefetch(addr unsafe.Pointer) {
	// On x86-64, use PREFETCHT0 instruction via inline assembly.
	// Go doesn't support inline assembly, but we can use a compiler
	// intrinsic on some platforms. For now, this is a no-op placeholder.
	// Real implementation would require CGO or assembly stubs.
	_ = addr
}

// HugepageAlloc allocates memory using 2MB hugepages for reduced TLB misses.
// Falls back to normal allocation if hugepages are not available.
//
// Use case: Allocate large ring buffers (>2MB) to reduce TLB overhead.
//
// Requires: hugetlbfs mounted at /dev/hugepages and sufficient hugepage pool.
func HugepageAlloc(size int) ([]byte, error) {
	// Try to use mmap with MAP_HUGETLB flag.
	const MAP_HUGETLB = 0x40000
	const MAP_HUGE_2MB = (21 << 26) // 2MB hugepage

	data, err := unix.Mmap(
		-1, 0,
		size,
		unix.PROT_READ|unix.PROT_WRITE,
		unix.MAP_PRIVATE|unix.MAP_ANONYMOUS|MAP_HUGETLB|MAP_HUGE_2MB,
	)
	if err != nil {
		// Hugepages not available, fall back to normal allocation.
		return make([]byte, size), nil
	}

	return data, nil
}

// DisableTransparentHugepages disables THP for the current process.
// THP can cause unpredictable latency spikes due to page compaction.
//
// Use case: Ensure consistent sub-200μs latency by avoiding THP stalls.
func DisableTransparentHugepages() error {
	// Use prctl(PR_SET_THP_DISABLE, 1) to disable THP for this process.
	const PR_SET_THP_DISABLE = 41
	_, _, errno := unix.Syscall(
		unix.SYS_PRCTL,
		PR_SET_THP_DISABLE,
		1,
		0,
	)
	if errno != 0 && errno != unix.EINVAL {
		// EINVAL means THP control not supported (kernel < 3.15).
		return fmt.Errorf("prctl PR_SET_THP_DISABLE: %w", errno)
	}
	return nil
}
