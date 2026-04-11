// +build linux

package memory

import (
	"bytes"
	"fmt"
	"testing"
	"time"
	"unsafe"
)

func TestProtectionManager(t *testing.T) {
	pm, err := NewProtectionManager()
	if err != nil {
		t.Skipf("Protection manager not available: %v", err)
		return
	}

	t.Run("ASLR verification", func(t *testing.T) {
		if !pm.aslrVerified {
			t.Error("ASLR not verified")
		}
	})

	t.Run("DEP verification", func(t *testing.T) {
		if !pm.depVerified {
			t.Error("DEP not verified")
		}
	})

	t.Run("Anti-dump enabled", func(t *testing.T) {
		if !pm.antiDumpEnabled {
			t.Error("Anti-dump not enabled")
		}
	})
}

func TestSecureAlloc(t *testing.T) {
	pm, err := NewProtectionManager()
	if err != nil {
		t.Skipf("Protection manager not available: %v", err)
		return
	}

	t.Run("basic allocation", func(t *testing.T) {
		size := uintptr(4096)
		mem, err := pm.SecureAlloc(size, "test", FlagSensitive)
		if err != nil {
			t.Fatalf("SecureAlloc failed: %v", err)
		}

		// Verify we can write to it
		for i := range mem {
			mem[i] = byte(i % 256)
		}

		// Verify data
		for i := range mem {
			if mem[i] != byte(i%256) {
				t.Errorf("Data mismatch at offset %d", i)
			}
		}

		// Free
		if err := pm.SecureFree(mem); err != nil {
			t.Errorf("SecureFree failed: %v", err)
		}
	})

	t.Run("allocation with guard pages", func(t *testing.T) {
		size := uintptr(4096)
		mem, err := pm.SecureAlloc(size, "test-guarded", FlagSensitive|FlagGuarded)
		if err != nil {
			t.Fatalf("SecureAlloc with guards failed: %v", err)
		}

		// Should be able to access memory
		mem[0] = 0xFF
		mem[len(mem)-1] = 0xFF

		// Free
		if err := pm.SecureFree(mem); err != nil {
			t.Errorf("SecureFree failed: %v", err)
		}
	})

	t.Run("allocation with canary", func(t *testing.T) {
		size := uintptr(4096)
		mem, err := pm.SecureAlloc(size, "test-canary", FlagSensitive|FlagCanary)
		if err != nil {
			t.Fatalf("SecureAlloc with canary failed: %v", err)
		}

		// Write data
		for i := range mem {
			mem[i] = 0xAA
		}

		// Free should succeed (canary intact)
		if err := pm.SecureFree(mem); err != nil {
			t.Errorf("SecureFree failed: %v", err)
		}
	})
}

func TestStackCanaryDetection(t *testing.T) {
	pm, err := NewProtectionManager()
	if err != nil {
		t.Skipf("Protection manager not available: %v", err)
		return
	}

	size := uintptr(4096)
	mem, err := pm.SecureAlloc(size, "test-overflow", FlagSensitive|FlagCanary)
	if err != nil {
		t.Fatalf("SecureAlloc failed: %v", err)
	}

	// Simulate canary corruption
	addr := uintptr(unsafe.Pointer(&mem[0]))
	canaryAddr := addr - 16

	// Corrupt the canary
	*(*uint64)(unsafe.Pointer(canaryAddr)) = 0xDEADDEADDEADDEAD

	// Free should detect corruption
	err = pm.SecureFree(mem)
	if err == nil {
		t.Error("Expected canary violation to be detected")
	}

	metrics := pm.GetMetrics()
	if metrics.CanaryViolations == 0 {
		t.Error("Canary violation not recorded in metrics")
	}
}

func TestSecureWipe(t *testing.T) {
	data := make([]byte, 1024)

	// Fill with pattern
	for i := range data {
		data[i] = 0xAA
	}

	// Wipe
	SecureWipe(data)

	// Verify all zeros
	for i, b := range data {
		if b != 0 {
			t.Errorf("Data not wiped at offset %d: got 0x%02x", i, b)
		}
	}
}

func TestSecureAllocator(t *testing.T) {
	pm, err := NewProtectionManager()
	if err != nil {
		t.Skipf("Protection manager not available: %v", err)
		return
	}

	sa := NewSecureAllocator(pm)

	t.Run("basic allocation", func(t *testing.T) {
		alloc, err := sa.Allocate(4096, "test", WithFlags(FlagSensitive))
		if err != nil {
			t.Fatalf("Allocate failed: %v", err)
		}

		// Write data
		copy(alloc.Data, []byte("Hello, World!"))

		// Verify
		if !bytes.Equal(alloc.Data[:13], []byte("Hello, World!")) {
			t.Error("Data mismatch")
		}

		// Free
		if err := sa.Free(alloc); err != nil {
			t.Errorf("Free failed: %v", err)
		}

		stats := sa.GetStats()
		if stats.TotalAllocated != 1 || stats.TotalFreed != 1 {
			t.Errorf("Stats mismatch: allocated=%d, freed=%d",
				stats.TotalAllocated, stats.TotalFreed)
		}
	})

	t.Run("allocation with lock", func(t *testing.T) {
		alloc, err := sa.Allocate(4096, "test-locked", WithFlags(FlagSensitive), WithLock())
		if err != nil {
			t.Fatalf("Allocate with lock failed: %v", err)
		}

		if !alloc.Locked {
			t.Error("Memory not locked")
		}

		stats := sa.GetStats()
		if stats.LockedBytes == 0 {
			t.Error("Locked bytes not tracked")
		}

		if err := sa.Free(alloc); err != nil {
			t.Errorf("Free failed: %v", err)
		}
	})

	t.Run("allocation with guard pages and canary", func(t *testing.T) {
		alloc, err := sa.Allocate(4096, "test-protected",
			WithFlags(FlagSensitive), WithGuardPages(), WithCanary())
		if err != nil {
			t.Fatalf("Allocate with protections failed: %v", err)
		}

		if alloc.Flags&FlagGuarded == 0 {
			t.Error("Guard pages not set")
		}
		if alloc.Flags&FlagCanary == 0 {
			t.Error("Canary not set")
		}

		if err := sa.Free(alloc); err != nil {
			t.Errorf("Free failed: %v", err)
		}
	})

	t.Run("resize allocation", func(t *testing.T) {
		alloc, err := sa.Allocate(4096, "test-resize", WithFlags(FlagSensitive))
		if err != nil {
			t.Fatalf("Allocate failed: %v", err)
		}

		// Write data
		copy(alloc.Data, []byte("Test data"))

		// Resize
		newAlloc, err := sa.Resize(alloc, 8192)
		if err != nil {
			t.Fatalf("Resize failed: %v", err)
		}

		// Verify data preserved
		if !bytes.Equal(newAlloc.Data[:9], []byte("Test data")) {
			t.Error("Data not preserved after resize")
		}

		if err := sa.Free(newAlloc); err != nil {
			t.Errorf("Free failed: %v", err)
		}
	})

	t.Run("get allocations by tag", func(t *testing.T) {
		alloc1, _ := sa.Allocate(1024, "tag1", WithFlags(FlagSensitive))
		alloc2, _ := sa.Allocate(2048, "tag1", WithFlags(FlagSensitive))
		alloc3, _ := sa.Allocate(4096, "tag2", WithFlags(FlagSensitive))

		tag1Allocs := sa.GetAllocationsByTag("tag1")
		if len(tag1Allocs) != 2 {
			t.Errorf("Expected 2 allocations with tag1, got %d", len(tag1Allocs))
		}

		tag2Allocs := sa.GetAllocationsByTag("tag2")
		if len(tag2Allocs) != 1 {
			t.Errorf("Expected 1 allocation with tag2, got %d", len(tag2Allocs))
		}

		sa.Free(alloc1)
		sa.Free(alloc2)
		sa.Free(alloc3)
	})
}

func TestSecureBuffer(t *testing.T) {
	pm, err := NewProtectionManager()
	if err != nil {
		t.Skipf("Protection manager not available: %v", err)
		return
	}

	sa := NewSecureAllocator(pm)

	t.Run("basic buffer operations", func(t *testing.T) {
		buf, err := NewSecureBuffer(sa, 1024, "test-buf", WithFlags(FlagSensitive))
		if err != nil {
			t.Fatalf("NewSecureBuffer failed: %v", err)
		}
		defer buf.Close()

		// Write
		data := []byte("Secret data")
		if err := buf.Write(data); err != nil {
			t.Errorf("Write failed: %v", err)
		}

		// Read
		read := buf.Read()
		if !bytes.Equal(read[:len(data)], data) {
			t.Error("Data mismatch")
		}

		// Wipe
		buf.Wipe()

		// Verify wiped
		read = buf.Read()
		allZero := true
		for _, b := range read {
			if b != 0 {
				allZero = false
				break
			}
		}
		if !allZero {
			t.Error("Buffer not properly wiped")
		}
	})
}

func TestMemoryMonitor(t *testing.T) {
	mm, err := NewMemoryMonitor()
	if err != nil {
		t.Skipf("Memory monitor not available: %v", err)
		return
	}
	defer mm.Close()

	t.Run("event injection", func(t *testing.T) {
		event := &MemoryEvent{
			Type:      EventMalloc,
			Timestamp: uint64(time.Now().UnixNano()),
			PID:       1234,
			TID:       1234,
			Addr:      0x7fff00000000,
			Size:      4096,
			Flags:     0,
		}
		copy(event.Comm[:], "test")

		mm.InjectEvent(event)

		stats := mm.GetStats()
		if stats.MallocCalls == 0 {
			t.Error("Event not processed")
		}
	})

	t.Run("event handler", func(t *testing.T) {
		var handled bool
		handler := EventHandlerFunc(func(e *MemoryEvent) error {
			if e.Type == EventPtraceAttach {
				handled = true
			}
			return nil
		})

		mm.RegisterHandler(handler)

		event := &MemoryEvent{
			Type:      EventPtraceAttach,
			Timestamp: uint64(time.Now().UnixNano()),
			PID:       5678,
		}

		mm.InjectEvent(event)

		// Give handler time to process
		time.Sleep(10 * time.Millisecond)

		if !handled {
			t.Error("Handler not called")
		}

		stats := mm.GetStats()
		if stats.PtraceBlocked == 0 {
			t.Error("Ptrace attempt not recorded")
		}
	})
}

func BenchmarkSecureAlloc(b *testing.B) {
	pm, err := NewProtectionManager()
	if err != nil {
		b.Skip("Protection manager not available")
		return
	}

	b.Run("4KB", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			mem, _ := pm.SecureAlloc(4096, "bench", FlagSensitive)
			pm.SecureFree(mem)
		}
	})

	b.Run("4KB with canary", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			mem, _ := pm.SecureAlloc(4096, "bench", FlagSensitive|FlagCanary)
			pm.SecureFree(mem)
		}
	})

	b.Run("4KB with guards", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			mem, _ := pm.SecureAlloc(4096, "bench", FlagSensitive|FlagGuarded)
			pm.SecureFree(mem)
		}
	})
}

func BenchmarkSecureWipe(b *testing.B) {
	sizes := []int{1024, 4096, 16384, 65536}

	for _, size := range sizes {
		b.Run(fmt.Sprintf("%dB", size), func(b *testing.B) {
			data := make([]byte, size)
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				SecureWipe(data)
			}
		})
	}
}

func BenchmarkAllocator(b *testing.B) {
	pm, err := NewProtectionManager()
	if err != nil {
		b.Skip("Protection manager not available")
		return
	}

	sa := NewSecureAllocator(pm)

	b.Run("alloc/free", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			alloc, _ := sa.Allocate(4096, "bench", WithFlags(FlagSensitive))
			sa.Free(alloc)
		}
	})

	b.Run("alloc/free with lock", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			alloc, _ := sa.Allocate(4096, "bench", WithFlags(FlagSensitive), WithLock())
			sa.Free(alloc)
		}
	})
}
