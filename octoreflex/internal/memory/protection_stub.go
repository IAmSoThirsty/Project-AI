// +build !linux

package memory

import (
	"fmt"
	"runtime"
)

// Stub implementations for non-Linux platforms

type ProtectionManager struct {
	unsupported bool
}

type ProtectionMetrics struct{}

type TaggedRegion struct{}

func NewProtectionManager() (*ProtectionManager, error) {
	return nil, fmt.Errorf("memory protection not supported on %s", runtime.GOOS)
}

func (pm *ProtectionManager) VerifyASLR() error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (pm *ProtectionManager) VerifyDEP() error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (pm *ProtectionManager) EnableAntiDump() error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (pm *ProtectionManager) SecureAlloc(size uintptr, tag string, flags uint32) ([]byte, error) {
	return nil, fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (pm *ProtectionManager) SecureFree(mem []byte) error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (pm *ProtectionManager) GetTaggedRegions() map[string][]*TaggedRegion {
	return nil
}

func (pm *ProtectionManager) VerifyIntegrity() error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (pm *ProtectionManager) GetMetrics() ProtectionMetrics {
	return ProtectionMetrics{}
}

func (pm *ProtectionManager) LockMemory(mem []byte) error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (pm *ProtectionManager) UnlockMemory(mem []byte) error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (pm *ProtectionManager) SetReadOnly(mem []byte) error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func (pm *ProtectionManager) SetReadWrite(mem []byte) error {
	return fmt.Errorf("not supported on %s", runtime.GOOS)
}

func SecureWipe(mem []byte) {
	// Basic wipe for non-Linux platforms
	for i := range mem {
		mem[i] = 0
	}
}

const (
	FlagSensitive  uint32 = 1 << 0
	FlagExecutable uint32 = 1 << 1
	FlagReadOnly   uint32 = 1 << 2
	FlagGuarded    uint32 = 1 << 3
	FlagCanary     uint32 = 1 << 4
	CanaryMagic    uint64 = 0xDEADBEEFCAFEBABE
)
