// +build linux

package memory

import (
	"fmt"
	"sync"
	"unsafe"
)

// SecureAllocator provides a secure memory allocation interface
type SecureAllocator struct {
	pm          *ProtectionManager
	allocations sync.Map // map[uintptr]*Allocation
	stats       *AllocatorStats
}

// Allocation tracks a single allocation
type Allocation struct {
	ID       uint64
	Tag      string
	Size     uintptr
	Addr     uintptr
	Flags    uint32
	Data     []byte
	Locked   bool
	ReadOnly bool
}

// AllocatorStats tracks allocation statistics
type AllocatorStats struct {
	mu              sync.RWMutex
	TotalAllocated  uint64
	TotalFreed      uint64
	ActiveAllocs    uint64
	BytesAllocated  uint64
	BytesFreed      uint64
	ActiveBytes     uint64
	PeakBytes       uint64
	LockedBytes     uint64
}

var allocIDCounter uint64
var allocIDMutex sync.Mutex

// NewSecureAllocator creates a new secure allocator
func NewSecureAllocator(pm *ProtectionManager) *SecureAllocator {
	return &SecureAllocator{
		pm:    pm,
		stats: &AllocatorStats{},
	}
}

// Allocate allocates secure memory with the given parameters
func (sa *SecureAllocator) Allocate(size uintptr, tag string, options ...AllocOption) (*Allocation, error) {
	if size == 0 {
		return nil, fmt.Errorf("cannot allocate zero bytes")
	}

	// Apply options
	config := &allocConfig{
		flags: FlagSensitive, // Default to sensitive
		lock:  false,
	}
	for _, opt := range options {
		opt(config)
	}

	// Allocate using protection manager
	data, err := sa.pm.SecureAlloc(size, tag, config.flags)
	if err != nil {
		return nil, fmt.Errorf("secure allocation failed: %w", err)
	}

	// Generate allocation ID
	allocIDMutex.Lock()
	allocIDCounter++
	id := allocIDCounter
	allocIDMutex.Unlock()

	addr := uintptr(unsafe.Pointer(&data[0]))

	alloc := &Allocation{
		ID:    id,
		Tag:   tag,
		Size:  size,
		Addr:  addr,
		Flags: config.flags,
		Data:  data,
	}

	// Lock memory if requested
	if config.lock {
		if err := sa.pm.LockMemory(data); err != nil {
			sa.pm.SecureFree(data)
			return nil, fmt.Errorf("failed to lock memory: %w", err)
		}
		alloc.Locked = true
	}

	// Store allocation
	sa.allocations.Store(addr, alloc)

	// Update stats
	sa.stats.mu.Lock()
	sa.stats.TotalAllocated++
	sa.stats.ActiveAllocs++
	sa.stats.BytesAllocated += uint64(size)
	sa.stats.ActiveBytes += uint64(size)
	if sa.stats.ActiveBytes > sa.stats.PeakBytes {
		sa.stats.PeakBytes = sa.stats.ActiveBytes
	}
	if config.lock {
		sa.stats.LockedBytes += uint64(size)
	}
	sa.stats.mu.Unlock()

	return alloc, nil
}

// Free frees a secure allocation
func (sa *SecureAllocator) Free(alloc *Allocation) error {
	if alloc == nil {
		return nil
	}

	// Remove from tracking
	val, loaded := sa.allocations.LoadAndDelete(alloc.Addr)
	if !loaded {
		return fmt.Errorf("allocation not found: 0x%x", alloc.Addr)
	}

	tracked := val.(*Allocation)

	// Unlock if locked
	if tracked.Locked {
		if err := sa.pm.UnlockMemory(tracked.Data); err != nil {
			// Log but continue with free
		}
	}

	// Secure free
	if err := sa.pm.SecureFree(tracked.Data); err != nil {
		return fmt.Errorf("secure free failed: %w", err)
	}

	// Update stats
	sa.stats.mu.Lock()
	sa.stats.TotalFreed++
	sa.stats.ActiveAllocs--
	sa.stats.BytesFreed += uint64(tracked.Size)
	sa.stats.ActiveBytes -= uint64(tracked.Size)
	if tracked.Locked {
		sa.stats.LockedBytes -= uint64(tracked.Size)
	}
	sa.stats.mu.Unlock()

	return nil
}

// Resize resizes an allocation (allocates new, copies, frees old)
func (sa *SecureAllocator) Resize(alloc *Allocation, newSize uintptr) (*Allocation, error) {
	if alloc == nil {
		return nil, fmt.Errorf("cannot resize nil allocation")
	}
	if newSize == 0 {
		return nil, fmt.Errorf("cannot resize to zero bytes")
	}

	// Create new allocation with same parameters
	options := []AllocOption{
		WithFlags(alloc.Flags),
	}
	if alloc.Locked {
		options = append(options, WithLock())
	}

	newAlloc, err := sa.Allocate(newSize, alloc.Tag, options...)
	if err != nil {
		return nil, fmt.Errorf("failed to allocate new buffer: %w", err)
	}

	// Copy data (minimum of old and new size)
	copySize := alloc.Size
	if newSize < copySize {
		copySize = newSize
	}
	copy(newAlloc.Data[:copySize], alloc.Data[:copySize])

	// Free old allocation
	if err := sa.Free(alloc); err != nil {
		// Try to clean up new allocation
		sa.Free(newAlloc)
		return nil, fmt.Errorf("failed to free old buffer: %w", err)
	}

	return newAlloc, nil
}

// Lock locks an allocation in memory
func (sa *SecureAllocator) Lock(alloc *Allocation) error {
	if alloc == nil {
		return fmt.Errorf("cannot lock nil allocation")
	}
	if alloc.Locked {
		return nil // Already locked
	}

	if err := sa.pm.LockMemory(alloc.Data); err != nil {
		return fmt.Errorf("failed to lock memory: %w", err)
	}

	alloc.Locked = true

	sa.stats.mu.Lock()
	sa.stats.LockedBytes += uint64(alloc.Size)
	sa.stats.mu.Unlock()

	return nil
}

// Unlock unlocks an allocation
func (sa *SecureAllocator) Unlock(alloc *Allocation) error {
	if alloc == nil {
		return fmt.Errorf("cannot unlock nil allocation")
	}
	if !alloc.Locked {
		return nil // Not locked
	}

	if err := sa.pm.UnlockMemory(alloc.Data); err != nil {
		return fmt.Errorf("failed to unlock memory: %w", err)
	}

	alloc.Locked = false

	sa.stats.mu.Lock()
	sa.stats.LockedBytes -= uint64(alloc.Size)
	sa.stats.mu.Unlock()

	return nil
}

// SetReadOnly makes an allocation read-only
func (sa *SecureAllocator) SetReadOnly(alloc *Allocation) error {
	if alloc == nil {
		return fmt.Errorf("cannot set nil allocation read-only")
	}
	if alloc.ReadOnly {
		return nil // Already read-only
	}

	if err := sa.pm.SetReadOnly(alloc.Data); err != nil {
		return fmt.Errorf("failed to set read-only: %w", err)
	}

	alloc.ReadOnly = true
	return nil
}

// SetReadWrite makes an allocation read-write
func (sa *SecureAllocator) SetReadWrite(alloc *Allocation) error {
	if alloc == nil {
		return fmt.Errorf("cannot set nil allocation read-write")
	}
	if !alloc.ReadOnly {
		return nil // Already read-write
	}

	if err := sa.pm.SetReadWrite(alloc.Data); err != nil {
		return fmt.Errorf("failed to set read-write: %w", err)
	}

	alloc.ReadOnly = false
	return nil
}

// GetStats returns current allocator statistics
func (sa *SecureAllocator) GetStats() AllocatorStats {
	sa.stats.mu.RLock()
	defer sa.stats.mu.RUnlock()
	return *sa.stats
}

// GetAllocations returns all active allocations
func (sa *SecureAllocator) GetAllocations() []*Allocation {
	var allocs []*Allocation
	sa.allocations.Range(func(key, value interface{}) bool {
		allocs = append(allocs, value.(*Allocation))
		return true
	})
	return allocs
}

// GetAllocationsByTag returns allocations with a specific tag
func (sa *SecureAllocator) GetAllocationsByTag(tag string) []*Allocation {
	var allocs []*Allocation
	sa.allocations.Range(func(key, value interface{}) bool {
		alloc := value.(*Allocation)
		if alloc.Tag == tag {
			allocs = append(allocs, alloc)
		}
		return true
	})
	return allocs
}

// FreeAll frees all allocations
func (sa *SecureAllocator) FreeAll() error {
	var errs []error

	sa.allocations.Range(func(key, value interface{}) bool {
		alloc := value.(*Allocation)
		if err := sa.Free(alloc); err != nil {
			errs = append(errs, err)
		}
		return true
	})

	if len(errs) > 0 {
		return fmt.Errorf("failed to free %d allocations", len(errs))
	}

	return nil
}

// allocConfig holds allocation configuration
type allocConfig struct {
	flags uint32
	lock  bool
}

// AllocOption is a functional option for allocation
type AllocOption func(*allocConfig)

// WithFlags sets allocation flags
func WithFlags(flags uint32) AllocOption {
	return func(c *allocConfig) {
		c.flags = flags
	}
}

// WithLock locks the allocation in memory
func WithLock() AllocOption {
	return func(c *allocConfig) {
		c.lock = true
	}
}

// WithGuardPages adds guard pages around allocation
func WithGuardPages() AllocOption {
	return func(c *allocConfig) {
		c.flags |= FlagGuarded
	}
}

// WithCanary adds stack canary protection
func WithCanary() AllocOption {
	return func(c *allocConfig) {
		c.flags |= FlagCanary
	}
}

// WithExecutable makes memory executable (use with caution)
func WithExecutable() AllocOption {
	return func(c *allocConfig) {
		c.flags |= FlagExecutable
	}
}

// SecureBuffer is a wrapper for secure memory buffers
type SecureBuffer struct {
	alloc *Allocation
	sa    *SecureAllocator
}

// NewSecureBuffer creates a new secure buffer
func NewSecureBuffer(sa *SecureAllocator, size uintptr, tag string, options ...AllocOption) (*SecureBuffer, error) {
	alloc, err := sa.Allocate(size, tag, options...)
	if err != nil {
		return nil, err
	}

	return &SecureBuffer{
		alloc: alloc,
		sa:    sa,
	}, nil
}

// Write writes data to the buffer
func (sb *SecureBuffer) Write(data []byte) error {
	if sb.alloc.ReadOnly {
		return fmt.Errorf("buffer is read-only")
	}
	if uintptr(len(data)) > sb.alloc.Size {
		return fmt.Errorf("data too large for buffer")
	}
	copy(sb.alloc.Data, data)
	return nil
}

// Read reads data from the buffer
func (sb *SecureBuffer) Read() []byte {
	return sb.alloc.Data
}

// Size returns buffer size
func (sb *SecureBuffer) Size() uintptr {
	return sb.alloc.Size
}

// Wipe securely wipes the buffer contents
func (sb *SecureBuffer) Wipe() {
	SecureWipe(sb.alloc.Data)
}

// Close securely wipes and frees the buffer
func (sb *SecureBuffer) Close() error {
	return sb.sa.Free(sb.alloc)
}
