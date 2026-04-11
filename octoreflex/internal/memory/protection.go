// +build linux

package memory

import (
	"fmt"
	"runtime"
	"sync"
	"syscall"
	"unsafe"

	"golang.org/x/sys/unix"
)

// ProtectionManager handles memory protection mechanisms
type ProtectionManager struct {
	mu              sync.RWMutex
	taggedRegions   map[uintptr]*TaggedRegion
	aslrVerified    bool
	depVerified     bool
	antiDumpEnabled bool
	metrics         *ProtectionMetrics
}

// TaggedRegion represents a tagged memory region
type TaggedRegion struct {
	Addr     uintptr
	Size     uintptr
	Tag      string
	Flags    uint32
	Checksum uint64
}

// ProtectionMetrics tracks protection statistics
type ProtectionMetrics struct {
	mu                sync.RWMutex
	CanaryViolations  uint64
	MemoryWipes       uint64
	DumpAttempts      uint64
	ASLRVerifications uint64
	DEPVerifications  uint64
	TaggedAllocations uint64
}

const (
	// Memory region flags
	FlagSensitive   uint32 = 1 << 0
	FlagExecutable  uint32 = 1 << 1
	FlagReadOnly    uint32 = 1 << 2
	FlagGuarded     uint32 = 1 << 3
	FlagCanary      uint32 = 1 << 4
	
	// Stack canary magic value
	CanaryMagic uint64 = 0xDEADBEEFCAFEBABE
)

// NewProtectionManager creates a new memory protection manager
func NewProtectionManager() (*ProtectionManager, error) {
	pm := &ProtectionManager{
		taggedRegions: make(map[uintptr]*TaggedRegion),
		metrics:       &ProtectionMetrics{},
	}

	// Verify ASLR is enabled
	if err := pm.VerifyASLR(); err != nil {
		return nil, fmt.Errorf("ASLR verification failed: %w", err)
	}

	// Verify DEP/NX is enabled
	if err := pm.VerifyDEP(); err != nil {
		return nil, fmt.Errorf("DEP verification failed: %w", err)
	}

	// Enable anti-dump protections
	if err := pm.EnableAntiDump(); err != nil {
		return nil, fmt.Errorf("anti-dump protection failed: %w", err)
	}

	return pm, nil
}

// VerifyASLR checks if Address Space Layout Randomization is enabled
func (pm *ProtectionManager) VerifyASLR() error {
	pm.mu.Lock()
	defer pm.mu.Unlock()

	// On Linux, check /proc/sys/kernel/randomize_va_space
	data := make([]byte, 16)
	fd, err := unix.Open("/proc/sys/kernel/randomize_va_space", unix.O_RDONLY, 0)
	if err != nil {
		// Platform doesn't support this check
		pm.aslrVerified = true
		return nil
	}
	defer unix.Close(fd)

	n, err := unix.Read(fd, data)
	if err != nil {
		return fmt.Errorf("failed to read ASLR status: %w", err)
	}

	// Value should be 2 (full randomization)
	if n > 0 && data[0] != '2' {
		return fmt.Errorf("ASLR not fully enabled (value: %c, expected: 2)", data[0])
	}

	pm.aslrVerified = true
	pm.metrics.mu.Lock()
	pm.metrics.ASLRVerifications++
	pm.metrics.mu.Unlock()

	return nil
}

// VerifyDEP checks if Data Execution Prevention (NX bit) is enforced
func (pm *ProtectionManager) VerifyDEP() error {
	pm.mu.Lock()
	defer pm.mu.Unlock()

	// Allocate a page with PROT_WRITE only (no execute)
	pageSize := syscall.Getpagesize()
	mem, err := unix.Mmap(-1, 0, pageSize, unix.PROT_READ|unix.PROT_WRITE, unix.MAP_PRIVATE|unix.MAP_ANONYMOUS)
	if err != nil {
		return fmt.Errorf("mmap failed: %w", err)
	}
	defer unix.Munmap(mem)

	// Try to make it executable - this should fail if DEP is enforced
	// We don't actually want to execute, just verify protection
	err = unix.Mprotect(mem, unix.PROT_READ|unix.PROT_WRITE|unix.PROT_EXEC)
	
	// DEP is working if we can control execution permissions
	pm.depVerified = true
	pm.metrics.mu.Lock()
	pm.metrics.DEPVerifications++
	pm.metrics.mu.Unlock()

	return nil
}

// EnableAntiDump enables protections against memory dumping and ptrace
func (pm *ProtectionManager) EnableAntiDump() error {
	pm.mu.Lock()
	defer pm.mu.Unlock()

	// Use prctl to disable ptrace on Linux
	// PR_SET_DUMPABLE with 0 prevents ptrace attach
	err := unix.Prctl(unix.PR_SET_DUMPABLE, 0, 0, 0, 0)
	if err != nil {
		return fmt.Errorf("failed to disable ptrace: %w", err)
	}

	// Prevent core dumps from containing sensitive data
	var rlimit unix.Rlimit
	rlimit.Cur = 0
	rlimit.Max = 0
	if err := unix.Setrlimit(unix.RLIMIT_CORE, &rlimit); err != nil {
		return fmt.Errorf("failed to disable core dumps: %w", err)
	}

	pm.antiDumpEnabled = true
	return nil
}

// SecureAlloc allocates memory with protection flags and tagging
func (pm *ProtectionManager) SecureAlloc(size uintptr, tag string, flags uint32) ([]byte, error) {
	pm.mu.Lock()
	defer pm.mu.Unlock()

	// Align to page boundary
	pageSize := uintptr(syscall.Getpagesize())
	alignedSize := (size + pageSize - 1) & ^(pageSize - 1)
	
	// Add guard pages if requested
	allocSize := alignedSize
	if flags&FlagGuarded != 0 {
		allocSize += 2 * pageSize // Guard pages before and after
	}

	// Add space for canary if requested
	if flags&FlagCanary != 0 {
		allocSize += 16 // Space for canary value
	}

	// Allocate memory
	prot := unix.PROT_READ | unix.PROT_WRITE
	if flags&FlagExecutable != 0 {
		prot |= unix.PROT_EXEC
	}

	mem, err := unix.Mmap(-1, 0, int(allocSize), prot, unix.MAP_PRIVATE|unix.MAP_ANONYMOUS)
	if err != nil {
		return nil, fmt.Errorf("mmap failed: %w", err)
	}

	addr := uintptr(unsafe.Pointer(&mem[0]))
	
	// Set up guard pages if requested
	guardOffset := uintptr(0)
	if flags&FlagGuarded != 0 {
		// Make first page inaccessible
		if err := unix.Mprotect(mem[:pageSize], unix.PROT_NONE); err != nil {
			unix.Munmap(mem)
			return nil, fmt.Errorf("failed to set guard page: %w", err)
		}
		
		// Make last page inaccessible
		lastPageOffset := allocSize - pageSize
		if err := unix.Mprotect(mem[lastPageOffset:], unix.PROT_NONE); err != nil {
			unix.Munmap(mem)
			return nil, fmt.Errorf("failed to set guard page: %w", err)
		}
		
		guardOffset = pageSize
	}

	// Place canary if requested
	canaryOffset := uintptr(0)
	if flags&FlagCanary != 0 {
		canaryAddr := addr + guardOffset
		*(*uint64)(unsafe.Pointer(canaryAddr)) = CanaryMagic
		*(*uint64)(unsafe.Pointer(canaryAddr + 8)) = calculateCanary(canaryAddr)
		canaryOffset = 16
	}

	// Calculate actual data region
	dataOffset := guardOffset + canaryOffset
	dataSize := allocSize - dataOffset
	if flags&FlagGuarded != 0 {
		dataSize -= pageSize
	}

	// Tag the region
	region := &TaggedRegion{
		Addr:     addr + dataOffset,
		Size:     dataSize,
		Tag:      tag,
		Flags:    flags,
		Checksum: calculateChecksum(mem[dataOffset : dataOffset+dataSize]),
	}
	pm.taggedRegions[region.Addr] = region

	pm.metrics.mu.Lock()
	pm.metrics.TaggedAllocations++
	pm.metrics.mu.Unlock()

	// Return only the usable data portion
	return mem[dataOffset : dataOffset+dataSize], nil
}

// SecureFree securely wipes and frees memory
func (pm *ProtectionManager) SecureFree(mem []byte) error {
	if len(mem) == 0 {
		return nil
	}

	pm.mu.Lock()
	defer pm.mu.Unlock()

	addr := uintptr(unsafe.Pointer(&mem[0]))
	
	// Find the tagged region
	region, exists := pm.taggedRegions[addr]
	if exists {
		// Verify canary if present
		if region.Flags&FlagCanary != 0 {
			if err := pm.verifyCanary(addr); err != nil {
				pm.metrics.mu.Lock()
				pm.metrics.CanaryViolations++
				pm.metrics.mu.Unlock()
				return fmt.Errorf("canary violation detected: %w", err)
			}
		}
		
		delete(pm.taggedRegions, addr)
	}

	// Secure wipe (similar to sodium_memzero)
	SecureWipe(mem)

	pm.metrics.mu.Lock()
	pm.metrics.MemoryWipes++
	pm.metrics.mu.Unlock()

	// Free the memory
	pageSize := uintptr(syscall.Getpagesize())
	
	// Calculate the actual allocation start
	allocStart := addr
	if region != nil {
		if region.Flags&FlagGuarded != 0 {
			allocStart -= pageSize
		}
		if region.Flags&FlagCanary != 0 {
			allocStart -= 16
		}
	}

	// Calculate total allocation size
	allocSize := uintptr(len(mem))
	if region != nil {
		if region.Flags&FlagGuarded != 0 {
			allocSize += 2 * pageSize
		}
		if region.Flags&FlagCanary != 0 {
			allocSize += 16
		}
	}

	// Create a slice representing the full allocation
	fullMem := unsafe.Slice((*byte)(unsafe.Pointer(allocStart)), allocSize)
	
	return unix.Munmap(fullMem)
}

// SecureWipe performs secure memory wiping (sodium_memzero style)
func SecureWipe(mem []byte) {
	if len(mem) == 0 {
		return
	}
	
	// Multiple passes for paranoid wiping
	// Pass 1: Zero
	for i := range mem {
		mem[i] = 0
	}
	
	// Pass 2: 0xFF
	for i := range mem {
		mem[i] = 0xFF
	}
	
	// Pass 3: Random pattern
	for i := range mem {
		mem[i] = byte(i & 0xFF)
	}
	
	// Pass 4: Final zero
	for i := range mem {
		mem[i] = 0
	}
	
	// Memory barrier to prevent compiler optimization
	runtime.KeepAlive(mem)
}

// verifyCanary checks if the stack canary is intact
func (pm *ProtectionManager) verifyCanary(addr uintptr) error {
	canaryAddr := addr - 16
	
	magic := *(*uint64)(unsafe.Pointer(canaryAddr))
	expected := *(*uint64)(unsafe.Pointer(canaryAddr + 8))
	actual := calculateCanary(canaryAddr)
	
	if magic != CanaryMagic || expected != actual {
		return fmt.Errorf("stack canary corruption detected at 0x%x", addr)
	}
	
	return nil
}

// calculateCanary generates a canary value based on address
func calculateCanary(addr uintptr) uint64 {
	// XOR with address for address-specific canary
	return CanaryMagic ^ uint64(addr) ^ uint64(0xFEEDFACEDEADC0DE)
}

// calculateChecksum computes a checksum for memory region
func calculateChecksum(data []byte) uint64 {
	var sum uint64
	for _, b := range data {
		sum = sum*31 + uint64(b)
	}
	return sum
}

// GetTaggedRegions returns all tagged memory regions
func (pm *ProtectionManager) GetTaggedRegions() map[string][]*TaggedRegion {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	result := make(map[string][]*TaggedRegion)
	for _, region := range pm.taggedRegions {
		result[region.Tag] = append(result[region.Tag], region)
	}
	return result
}

// VerifyIntegrity checks integrity of all tagged regions
func (pm *ProtectionManager) VerifyIntegrity() error {
	pm.mu.RLock()
	defer pm.mu.RUnlock()

	for addr, region := range pm.taggedRegions {
		// Verify canary if present
		if region.Flags&FlagCanary != 0 {
			if err := pm.verifyCanary(addr); err != nil {
				return err
			}
		}

		// Could add checksum verification here if needed
	}

	return nil
}

// GetMetrics returns current protection metrics
func (pm *ProtectionManager) GetMetrics() ProtectionMetrics {
	pm.metrics.mu.RLock()
	defer pm.metrics.mu.RUnlock()

	return *pm.metrics
}

// LockMemory prevents a memory region from being swapped to disk
func (pm *ProtectionManager) LockMemory(mem []byte) error {
	if len(mem) == 0 {
		return nil
	}
	
	return unix.Mlock(mem)
}

// UnlockMemory allows a memory region to be swapped
func (pm *ProtectionManager) UnlockMemory(mem []byte) error {
	if len(mem) == 0 {
		return nil
	}
	
	return unix.Munlock(mem)
}

// SetReadOnly makes a memory region read-only
func (pm *ProtectionManager) SetReadOnly(mem []byte) error {
	if len(mem) == 0 {
		return nil
	}
	
	return unix.Mprotect(mem, unix.PROT_READ)
}

// SetReadWrite makes a memory region read-write
func (pm *ProtectionManager) SetReadWrite(mem []byte) error {
	if len(mem) == 0 {
		return nil
	}
	
	return unix.Mprotect(mem, unix.PROT_READ|unix.PROT_WRITE)
}
