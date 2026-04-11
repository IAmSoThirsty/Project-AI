package main

import (
	"fmt"
	"log"
	"time"

	"github.com/octoreflex/octoreflex/internal/memory"
)

func main() {
	fmt.Println("=== OctoReflex Memory Protection Demo ===\n")

	// 1. Initialize Protection Manager
	fmt.Println("1. Initializing Protection Manager...")
	pm, err := memory.NewProtectionManager()
	if err != nil {
		log.Fatalf("Failed to initialize protection manager: %v", err)
	}
	fmt.Println("   ✓ ASLR verified")
	fmt.Println("   ✓ DEP/NX verified")
	fmt.Println("   ✓ Anti-dump enabled")
	fmt.Println("   ✓ Ptrace blocked")
	fmt.Println()

	// 2. Initialize Secure Allocator
	fmt.Println("2. Creating Secure Allocator...")
	sa := memory.NewSecureAllocator(pm)
	fmt.Println("   ✓ Allocator ready")
	fmt.Println()

	// 3. Initialize Memory Monitor
	fmt.Println("3. Starting Memory Monitor (eBPF)...")
	mm, err := memory.NewMemoryMonitor()
	if err != nil {
		log.Printf("Warning: Memory monitor not available: %v", err)
	} else {
		defer mm.Close()
		fmt.Println("   ✓ eBPF hooks attached")

		// Register event handler
		mm.RegisterHandler(memory.EventHandlerFunc(func(e *memory.MemoryEvent) error {
			fmt.Printf("   [EVENT] %s\n", e.String())
			return nil
		}))
		fmt.Println("   ✓ Event handler registered")
	}
	fmt.Println()

	// 4. Demonstrate Basic Allocation
	fmt.Println("4. Basic Secure Allocation...")
	alloc1, err := sa.Allocate(4096, "api-key", memory.WithFlags(memory.FlagSensitive))
	if err != nil {
		log.Fatalf("Allocation failed: %v", err)
	}
	copy(alloc1.Data, []byte("SECRET_API_KEY_123456"))
	fmt.Printf("   ✓ Allocated %d bytes at 0x%x\n", alloc1.Size, alloc1.Addr)
	fmt.Println("   ✓ Sensitive data written")
	fmt.Println()

	// 5. Demonstrate Canary Protection
	fmt.Println("5. Allocation with Stack Canary...")
	alloc2, err := sa.Allocate(8192, "user-token",
		memory.WithFlags(memory.FlagSensitive),
		memory.WithCanary())
	if err != nil {
		log.Fatalf("Allocation failed: %v", err)
	}
	copy(alloc2.Data, []byte("USER_TOKEN_ABCDEF"))
	fmt.Printf("   ✓ Allocated %d bytes with canary\n", alloc2.Size)
	fmt.Println("   ✓ Buffer overflow protection active")
	fmt.Println()

	// 6. Demonstrate Guard Pages
	fmt.Println("6. Allocation with Guard Pages...")
	alloc3, err := sa.Allocate(4096, "crypto-key",
		memory.WithFlags(memory.FlagSensitive),
		memory.WithGuardPages())
	if err != nil {
		log.Fatalf("Allocation failed: %v", err)
	}
	copy(alloc3.Data, []byte("CRYPTO_KEY_XYZ789"))
	fmt.Printf("   ✓ Allocated %d bytes with guard pages\n", alloc3.Size)
	fmt.Println("   ✓ Out-of-bounds access protection active")
	fmt.Println()

	// 7. Demonstrate Memory Locking
	fmt.Println("7. Locked Memory (prevents swapping)...")
	alloc4, err := sa.Allocate(4096, "master-key",
		memory.WithFlags(memory.FlagSensitive),
		memory.WithLock(),
		memory.WithCanary(),
		memory.WithGuardPages())
	if err != nil {
		log.Fatalf("Allocation failed: %v", err)
	}
	copy(alloc4.Data, []byte("MASTER_KEY_999"))
	fmt.Printf("   ✓ Allocated %d bytes (locked in RAM)\n", alloc4.Size)
	fmt.Println("   ✓ Protected from swap")
	fmt.Println("   ✓ Canary + guard pages active")
	fmt.Println()

	// 8. Demonstrate Secure Buffer
	fmt.Println("8. Using Secure Buffer...")
	buf, err := memory.NewSecureBuffer(sa, 1024, "session-data",
		memory.WithFlags(memory.FlagSensitive),
		memory.WithCanary())
	if err != nil {
		log.Fatalf("Buffer creation failed: %v", err)
	}
	if err := buf.Write([]byte("SESSION_DATA_SENSITIVE")); err != nil {
		log.Fatalf("Write failed: %v", err)
	}
	fmt.Printf("   ✓ Secure buffer created (%d bytes)\n", buf.Size())
	fmt.Println("   ✓ Data written securely")
	fmt.Println()

	// 9. Demonstrate Memory Tagging
	fmt.Println("9. Tagged Memory Regions...")
	regions := pm.GetTaggedRegions()
	for tag, taggedRegions := range regions {
		fmt.Printf("   Tag: %s (%d regions)\n", tag, len(taggedRegions))
		for _, r := range taggedRegions {
			fmt.Printf("     - 0x%x (%d bytes)\n", r.Addr, r.Size)
		}
	}
	fmt.Println()

	// 10. Demonstrate Statistics
	fmt.Println("10. Allocator Statistics...")
	stats := sa.GetStats()
	fmt.Printf("   Total Allocated:  %d allocations (%d bytes)\n",
		stats.TotalAllocated, stats.BytesAllocated)
	fmt.Printf("   Active:           %d allocations (%d bytes)\n",
		stats.ActiveAllocs, stats.ActiveBytes)
	fmt.Printf("   Locked:           %d bytes\n", stats.LockedBytes)
	fmt.Printf("   Peak Usage:       %d bytes\n", stats.PeakBytes)
	fmt.Println()

	// 11. Demonstrate Protection Metrics
	fmt.Println("11. Protection Metrics...")
	protMetrics := pm.GetMetrics()
	fmt.Printf("   ASLR Verifications: %d\n", protMetrics.ASLRVerifications)
	fmt.Printf("   DEP Verifications:  %d\n", protMetrics.DEPVerifications)
	fmt.Printf("   Canary Violations:  %d\n", protMetrics.CanaryViolations)
	fmt.Printf("   Tagged Allocations: %d\n", protMetrics.TaggedAllocations)
	fmt.Println()

	// 12. Demonstrate Monitor Statistics
	if mm != nil {
		fmt.Println("12. Memory Monitor Statistics...")
		monStats := mm.GetStats()
		fmt.Printf("   Events Received:    %d\n", monStats.EventsReceived)
		fmt.Printf("   Malloc Calls:       %d\n", monStats.MallocCalls)
		fmt.Printf("   Mmap Calls:         %d\n", monStats.MmapCalls)
		fmt.Printf("   Violations:         %d\n", monStats.Violations)
		fmt.Printf("   Ptrace Blocked:     %d\n", monStats.PtraceBlocked)
		fmt.Printf("   Core Dump Blocked:  %d\n", monStats.CoreDumpBlocked)
		fmt.Println()
	}

	// 13. Demonstrate Secure Wiping
	fmt.Println("13. Secure Memory Wiping...")
	fmt.Println("   Wiping buffer...")
	buf.Wipe()
	fmt.Println("   ✓ Buffer securely wiped (multi-pass)")
	fmt.Println()

	// 14. Demonstrate Cleanup
	fmt.Println("14. Secure Cleanup...")
	if err := buf.Close(); err != nil {
		log.Printf("Buffer close error: %v", err)
	} else {
		fmt.Println("   ✓ Buffer closed and wiped")
	}

	if err := sa.Free(alloc1); err != nil {
		log.Printf("Free error: %v", err)
	} else {
		fmt.Println("   ✓ Allocation 1 freed and wiped")
	}

	if err := sa.Free(alloc2); err != nil {
		log.Printf("Free error: %v", err)
	} else {
		fmt.Println("   ✓ Allocation 2 freed (canary verified)")
	}

	if err := sa.Free(alloc3); err != nil {
		log.Printf("Free error: %v", err)
	} else {
		fmt.Println("   ✓ Allocation 3 freed (guard pages removed)")
	}

	if err := sa.Free(alloc4); err != nil {
		log.Printf("Free error: %v", err)
	} else {
		fmt.Println("   ✓ Allocation 4 freed (unlocked and wiped)")
	}
	fmt.Println()

	// 15. Final Statistics
	fmt.Println("15. Final Statistics...")
	finalStats := sa.GetStats()
	fmt.Printf("   Total Freed:        %d allocations (%d bytes)\n",
		finalStats.TotalFreed, finalStats.BytesFreed)
	fmt.Printf("   Active Remaining:   %d allocations (%d bytes)\n",
		finalStats.ActiveAllocs, finalStats.ActiveBytes)

	finalProtMetrics := pm.GetMetrics()
	fmt.Printf("   Memory Wipes:       %d\n", finalProtMetrics.MemoryWipes)
	fmt.Println()

	// 16. Simulate Attack Detection
	fmt.Println("16. Attack Detection Simulation...")
	simulateAttacks(mm)
	fmt.Println()

	fmt.Println("=== Demo Complete ===")
}

func simulateAttacks(mm *memory.MemoryMonitor) {
	if mm == nil {
		fmt.Println("   (Memory monitor not available)")
		return
	}

	// Simulate various attack attempts
	attacks := []*memory.MemoryEvent{
		{
			Type:      memory.EventPtraceAttach,
			Timestamp: uint64(time.Now().UnixNano()),
			PID:       12345,
			TID:       12345,
			Addr:      9999,
			Flags:     16, // PTRACE_ATTACH
		},
		{
			Type:      memory.EventBufferOverflow,
			Timestamp: uint64(time.Now().UnixNano()),
			PID:       12345,
			Addr:      0x7fff00000000,
			Size:      8192,
		},
		{
			Type:      memory.EventDoubleFree,
			Timestamp: uint64(time.Now().UnixNano()),
			PID:       12345,
			Addr:      0x7fff00010000,
			Size:      4096,
		},
		{
			Type:      memory.EventCoreDump,
			Timestamp: uint64(time.Now().UnixNano()),
			PID:       12345,
		},
	}

	for _, attack := range attacks {
		mm.InjectEvent(attack)
		fmt.Printf("   ✓ Detected: %s\n", memory.GetEventName(attack.Type))
		time.Sleep(10 * time.Millisecond)
	}

	monStats := mm.GetStats()
	fmt.Printf("\n   Total Violations Detected: %d\n", monStats.Violations)
}
