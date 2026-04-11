// +build !linux

package memory

import (
	"fmt"
	"runtime"
)

type SecureAllocator struct {
	unsupported bool
}

type Allocation struct{}
type AllocatorStats struct{}
type AllocOption func(*allocConfig)
type allocConfig struct{}

func NewSecureAllocator(pm *ProtectionManager) *SecureAllocator {
	return &SecureAllocator{unsupported: true}
}

func (sa *SecureAllocator) Allocate(size uintptr, tag string, options ...AllocOption) (*Allocation, error) {
	return nil, fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (sa *SecureAllocator) Free(alloc *Allocation) error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (sa *SecureAllocator) Resize(alloc *Allocation, newSize uintptr) (*Allocation, error) {
	return nil, fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (sa *SecureAllocator) Lock(alloc *Allocation) error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (sa *SecureAllocator) Unlock(alloc *Allocation) error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (sa *SecureAllocator) SetReadOnly(alloc *Allocation) error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (sa *SecureAllocator) SetReadWrite(alloc *Allocation) error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (sa *SecureAllocator) GetStats() AllocatorStats {
	return AllocatorStats{}
}

func (sa *SecureAllocator) GetAllocations() []*Allocation {
	return nil
}

func (sa *SecureAllocator) GetAllocationsByTag(tag string) []*Allocation {
	return nil
}

func (sa *SecureAllocator) FreeAll() error {
	return nil
}

func WithFlags(flags uint32) AllocOption {
	return func(c *allocConfig) {}
}

func WithLock() AllocOption {
	return func(c *allocConfig) {}
}

func WithGuardPages() AllocOption {
	return func(c *allocConfig) {}
}

func WithCanary() AllocOption {
	return func(c *allocConfig) {}
}

func WithExecutable() AllocOption {
	return func(c *allocConfig) {}
}

type SecureBuffer struct{}

func NewSecureBuffer(sa *SecureAllocator, size uintptr, tag string, options ...AllocOption) (*SecureBuffer, error) {
	return nil, fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (sb *SecureBuffer) Write(data []byte) error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (sb *SecureBuffer) Read() []byte {
	return nil
}

func (sb *SecureBuffer) Size() uintptr {
	return 0
}

func (sb *SecureBuffer) Wipe() {}

func (sb *SecureBuffer) Close() error {
	return nil
}
