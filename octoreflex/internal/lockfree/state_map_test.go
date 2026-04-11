// Package lockfree — state_map_test.go
//
// Tests for lock-free state map.

package lockfree

import (
	"math"
	"sync"
	"testing"
	"time"
)

// TestStateMapBasic verifies basic get/set operations.
func TestStateMapBasic(t *testing.T) {
	sm := NewStateMap(16)

	// Create entry.
	entry := sm.GetOrCreate(1234, 0)
	if entry == nil {
		t.Fatal("GetOrCreate returned nil")
	}

	// Verify initial state.
	if state := entry.ReadState(); state != 0 {
		t.Errorf("Initial state = %d, want 0", state)
	}

	// Update state.
	entry.WriteState(2)
	if state := entry.ReadState(); state != 2 {
		t.Errorf("After WriteState(2), state = %d, want 2", state)
	}

	// Update pressure.
	entry.WritePressure(3.14)
	if pressure := entry.ReadPressure(); math.Abs(pressure-3.14) > 0.001 {
		t.Errorf("After WritePressure(3.14), pressure = %f, want 3.14", pressure)
	}

	// Verify GetOrCreate returns same entry.
	entry2 := sm.GetOrCreate(1234, 0)
	if entry2 != entry {
		t.Error("GetOrCreate returned different entry for same PID")
	}
}

// TestStateMapConcurrent verifies thread-safety.
func TestStateMapConcurrent(t *testing.T) {
	const (
		goroutines = 16
		iterations = 1000
	)

	sm := NewStateMap(64)
	var wg sync.WaitGroup
	wg.Add(goroutines)

	// Each goroutine updates different PIDs.
	for g := 0; g < goroutines; g++ {
		gID := uint32(g)
		go func() {
			defer wg.Done()
			for i := 0; i < iterations; i++ {
				pid := gID*1000 + uint32(i)
				entry := sm.GetOrCreate(pid, 0)
				
				// Update state and pressure.
				entry.WriteState(uint8(i % 6))
				entry.WritePressure(float64(i))
				entry.TouchEvent()
				
				// Read back to verify.
				state := entry.ReadState()
				pressure := entry.ReadPressure()
				
				if state != uint8(i%6) {
					t.Errorf("PID %d: state = %d, want %d", pid, state, i%6)
				}
				if math.Abs(pressure-float64(i)) > 0.001 {
					t.Errorf("PID %d: pressure = %f, want %f", pid, pressure, float64(i))
				}
			}
		}()
	}

	wg.Wait()

	// Verify all entries were created.
	expectedCount := goroutines * iterations
	if count := sm.Len(); count != expectedCount {
		t.Errorf("State map has %d entries, want %d", count, expectedCount)
	}
}

// TestStateMapDelete verifies deletion.
func TestStateMapDelete(t *testing.T) {
	sm := NewStateMap(16)

	// Create and delete entry.
	entry := sm.GetOrCreate(1234, 0)
	if entry == nil {
		t.Fatal("GetOrCreate failed")
	}

	sm.Delete(1234)

	// Get should return nil after delete.
	if got := sm.Get(1234); got != nil {
		t.Error("Get returned non-nil after Delete")
	}

	// GetOrCreate should create new entry.
	entry2 := sm.GetOrCreate(1234, 5)
	if entry2 == nil {
		t.Fatal("GetOrCreate failed after delete")
	}
	if state := entry2.ReadState(); state != 5 {
		t.Errorf("New entry state = %d, want 5", state)
	}
}

// TestStateMapForEach verifies iteration.
func TestStateMapForEach(t *testing.T) {
	sm := NewStateMap(16)

	// Create entries.
	pids := []uint32{100, 200, 300, 400, 500}
	for _, pid := range pids {
		entry := sm.GetOrCreate(pid, 0)
		entry.WriteState(uint8(pid / 100))
	}

	// Iterate and collect.
	seen := make(map[uint32]bool)
	sm.ForEach(func(pid uint32, entry *ProcessStateEntry) bool {
		seen[pid] = true
		expectedState := uint8(pid / 100)
		if state := entry.ReadState(); state != expectedState {
			t.Errorf("PID %d: state = %d, want %d", pid, state, expectedState)
		}
		return true
	})

	// Verify all PIDs were seen.
	for _, pid := range pids {
		if !seen[pid] {
			t.Errorf("PID %d not seen in ForEach", pid)
		}
	}
	if len(seen) != len(pids) {
		t.Errorf("ForEach saw %d entries, want %d", len(seen), len(pids))
	}
}

// TestStateMapTimeInState verifies time tracking.
func TestStateMapTimeInState(t *testing.T) {
	sm := NewStateMap(16)
	entry := sm.GetOrCreate(1234, 0)

	// Initial time should be near zero.
	if dur := entry.TimeInState(); dur > 10*time.Millisecond {
		t.Errorf("Initial TimeInState = %v, want < 10ms", dur)
	}

	// Wait and check again.
	time.Sleep(50 * time.Millisecond)
	dur := entry.TimeInState()
	if dur < 50*time.Millisecond || dur > 100*time.Millisecond {
		t.Errorf("TimeInState after 50ms = %v, want ~50ms", dur)
	}

	// Update state should reset timer.
	entry.WriteState(1)
	if dur := entry.TimeInState(); dur > 10*time.Millisecond {
		t.Errorf("TimeInState after WriteState = %v, want < 10ms", dur)
	}
}

// TestStateMapLastEventTime verifies event timestamp tracking.
func TestStateMapLastEventTime(t *testing.T) {
	sm := NewStateMap(16)
	entry := sm.GetOrCreate(1234, 0)

	// Touch event.
	before := time.Now()
	entry.TouchEvent()
	after := time.Now()

	// Verify timestamp is in expected range.
	lastEvent := entry.LastEventTime()
	if lastEvent.Before(before) || lastEvent.After(after) {
		t.Errorf("LastEventTime = %v, want between %v and %v", lastEvent, before, after)
	}
}

// BenchmarkStateMapReadState measures lock-free read performance.
func BenchmarkStateMapReadState(b *testing.B) {
	sm := NewStateMap(256)
	entry := sm.GetOrCreate(1234, 0)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = entry.ReadState()
	}
}

// BenchmarkStateMapWriteState measures atomic write performance.
func BenchmarkStateMapWriteState(b *testing.B) {
	sm := NewStateMap(256)
	entry := sm.GetOrCreate(1234, 0)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		entry.WriteState(uint8(i % 6))
	}
}

// BenchmarkStateMapGetOrCreate measures lookup/creation performance.
func BenchmarkStateMapGetOrCreate(b *testing.B) {
	sm := NewStateMap(256)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = sm.GetOrCreate(uint32(i%1000), 0)
	}
}

// BenchmarkStateMapConcurrentReads measures concurrent read throughput.
func BenchmarkStateMapConcurrentReads(b *testing.B) {
	sm := NewStateMap(256)
	
	// Pre-populate.
	for i := 0; i < 1000; i++ {
		sm.GetOrCreate(uint32(i), 0)
	}

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		i := 0
		for pb.Next() {
			entry := sm.Get(uint32(i % 1000))
			if entry != nil {
				_ = entry.ReadState()
			}
			i++
		}
	})
}
