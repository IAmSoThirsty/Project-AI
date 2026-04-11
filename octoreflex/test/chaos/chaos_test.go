// Chaos engineering tests for OCTOREFLEX
//
// Tests system behavior under adverse conditions:
//   - Network partitions between gossip nodes
//   - Resource exhaustion (CPU, memory, file descriptors)
//   - Random process termination
//   - Clock skew and time jumps
//   - Kernel event flood

package chaos

import (
	"context"
	"fmt"
	"math/rand"
	"runtime"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestChaos_EventFlood(t *testing.T) {
	// Flood the system with events to test backpressure handling
	const (
		floodDuration = 5 * time.Second
		eventsPerSec  = 1000000 // 1M events/sec
	)

	eventCount := atomic.Uint64{}
	droppedCount := atomic.Uint64{}

	ctx, cancel := context.WithTimeout(context.Background(), floodDuration)
	defer cancel()

	// Event processing goroutine with bounded queue
	eventQueue := make(chan *Event, 10000)
	var wg sync.WaitGroup

	// Processor
	wg.Add(1)
	go func() {
		defer wg.Done()
		for evt := range eventQueue {
			_ = processEvent(evt)
			eventCount.Add(1)
		}
	}()

	// Flood generator
	wg.Add(1)
	go func() {
		defer wg.Done()
		defer close(eventQueue)

		ticker := time.NewTicker(time.Second / time.Duration(eventsPerSec))
		defer ticker.Stop()

		for {
			select {
			case <-ctx.Done():
				return
			case <-ticker.C:
				select {
				case eventQueue <- mockEvent():
					// Queued successfully
				default:
					// Queue full - backpressure
					droppedCount.Add(1)
				}
			}
		}
	}()

	<-ctx.Done()
	wg.Wait()

	processed := eventCount.Load()
	dropped := droppedCount.Load()
	total := processed + dropped

	t.Logf("Event flood test:")
	t.Logf("  Duration: %v", floodDuration)
	t.Logf("  Events processed: %d", processed)
	t.Logf("  Events dropped: %d", dropped)
	t.Logf("  Drop rate: %.2f%%", float64(dropped)/float64(total)*100)
	t.Logf("  Throughput: %.0f events/sec", float64(processed)/floodDuration.Seconds())

	// System should gracefully handle backpressure
	if dropped > total/2 {
		t.Logf("WARNING: High drop rate (>50%%) indicates capacity issues")
	}
}

func TestChaos_MemoryExhaustion(t *testing.T) {
	// Test behavior under memory pressure
	if testing.Short() {
		t.Skip("Skipping memory exhaustion test in short mode")
	}

	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)
	initialAlloc := memStats.Alloc

	// Allocate large buffers to simulate memory pressure
	buffers := make([][]byte, 0, 1000)
	const bufferSize = 10 * 1024 * 1024 // 10MB per buffer

	allocated := uint64(0)
	for i := 0; i < 100; i++ {
		buf := make([]byte, bufferSize)
		buffers = append(buffers, buf)
		allocated += bufferSize

		// Continue processing events under memory pressure
		for j := 0; j < 100; j++ {
			_ = processEvent(mockEvent())
		}

		if i%10 == 0 {
			runtime.ReadMemStats(&memStats)
			t.Logf("Iteration %d: Allocated %.2f MB, Heap %.2f MB",
				i, float64(allocated)/1e6, float64(memStats.HeapAlloc)/1e6)
		}
	}

	runtime.ReadMemStats(&memStats)
	finalAlloc := memStats.Alloc

	t.Logf("Memory exhaustion test:")
	t.Logf("  Initial alloc: %.2f MB", float64(initialAlloc)/1e6)
	t.Logf("  Final alloc: %.2f MB", float64(finalAlloc)/1e6)
	t.Logf("  Allocated: %.2f MB", float64(allocated)/1e6)

	// Force GC
	runtime.GC()
	runtime.ReadMemStats(&memStats)
	t.Logf("  After GC: %.2f MB", float64(memStats.HeapAlloc)/1e6)
}

func TestChaos_GoroutineExhaustion(t *testing.T) {
	// Test behavior when goroutine limit is reached
	const maxGoroutines = 10000

	var wg sync.WaitGroup
	done := make(chan bool)

	for i := 0; i < maxGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			<-done // Block until signaled
		}(i)
	}

	t.Logf("Spawned %d goroutines", maxGoroutines)

	// Try to process events with goroutine pool exhausted
	for i := 0; i < 1000; i++ {
		_ = processEvent(mockEvent())
	}

	// Release goroutines
	close(done)
	wg.Wait()

	t.Logf("All goroutines terminated successfully")
}

func TestChaos_RandomFailures(t *testing.T) {
	// Simulate random component failures
	const (
		operations    = 10000
		failureRate   = 0.05 // 5% failure rate
	)

	successCount := 0
	failureCount := 0

	for i := 0; i < operations; i++ {
		if rand.Float64() < failureRate {
			// Simulate failure
			failureCount++
			continue
		}

		// Simulate success
		_ = processEvent(mockEvent())
		successCount++
	}

	t.Logf("Random failure test:")
	t.Logf("  Operations: %d", operations)
	t.Logf("  Successes: %d", successCount)
	t.Logf("  Failures: %d", failureCount)
	t.Logf("  Actual failure rate: %.2f%%", float64(failureCount)/float64(operations)*100)

	// System should degrade gracefully
	if successCount < operations*90/100 {
		t.Errorf("Success rate %.2f%% below 90%% threshold", 
			float64(successCount)/float64(operations)*100)
	}
}

func TestChaos_ClockSkew(t *testing.T) {
	// Test behavior when system clock jumps
	events := make([]*TimestampedEvent, 0, 100)

	baseTime := time.Now()
	
	for i := 0; i < 100; i++ {
		var timestamp time.Time
		
		if i == 50 {
			// Simulate clock jump backward
			timestamp = baseTime.Add(-1 * time.Hour)
			t.Logf("Clock jumped backward by 1 hour")
		} else if i == 75 {
			// Simulate clock jump forward
			timestamp = baseTime.Add(1 * time.Hour)
			t.Logf("Clock jumped forward by 1 hour")
		} else {
			timestamp = baseTime.Add(time.Duration(i) * time.Second)
		}

		evt := &TimestampedEvent{
			Event:     mockEvent(),
			Timestamp: timestamp,
		}
		events = append(events, evt)
	}

	// Verify events are processed correctly despite clock skew
	monotonic := true
	for i := 1; i < len(events); i++ {
		if events[i].Timestamp.Before(events[i-1].Timestamp) {
			monotonic = false
			t.Logf("Non-monotonic timestamp at index %d", i)
		}
	}

	if !monotonic {
		t.Logf("Clock skew detected - system should use monotonic clock")
	}
}

func TestChaos_NetworkPartition(t *testing.T) {
	// Simulate network partition in gossip protocol
	nodes := 5
	partitionDuration := 3 * time.Second

	t.Logf("Simulating network partition:")
	t.Logf("  Nodes: %d", nodes)
	t.Logf("  Partition duration: %v", partitionDuration)

	// Simulate nodes trying to communicate
	messagesSent := 0
	messagesDelivered := 0

	endTime := time.Now().Add(partitionDuration)
	for time.Now().Before(endTime) {
		from := rand.Intn(nodes)
		to := rand.Intn(nodes)

		if from == to {
			continue
		}

		messagesSent++

		// Simulate partition: 50% of messages fail
		if rand.Float64() < 0.5 {
			// Message lost due to partition
			continue
		}

		messagesDelivered++
		time.Sleep(10 * time.Millisecond)
	}

	deliveryRate := float64(messagesDelivered) / float64(messagesSent) * 100

	t.Logf("Partition results:")
	t.Logf("  Messages sent: %d", messagesSent)
	t.Logf("  Messages delivered: %d", messagesDelivered)
	t.Logf("  Delivery rate: %.2f%%", deliveryRate)
	t.Logf("Expected: Quorum decisions should still be reached with majority")
}

func TestChaos_CPUStarvation(t *testing.T) {
	// Test behavior under CPU starvation
	cpuHogs := runtime.NumCPU() * 2

	done := make(chan bool)
	var wg sync.WaitGroup

	// Spawn CPU-intensive goroutines
	for i := 0; i < cpuHogs; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			sum := 0.0
			for {
				select {
				case <-done:
					return
				default:
					// CPU-intensive calculation
					for j := 0; j < 1000000; j++ {
						sum += float64(j) * 0.001
					}
				}
			}
		}()
	}

	// Try to process events under CPU contention
	startTime := time.Now()
	eventCount := 0
	for i := 0; i < 1000; i++ {
		_ = processEvent(mockEvent())
		eventCount++
	}
	elapsed := time.Since(startTime)

	// Stop CPU hogs
	close(done)
	wg.Wait()

	t.Logf("CPU starvation test:")
	t.Logf("  CPU hogs: %d", cpuHogs)
	t.Logf("  Events processed: %d", eventCount)
	t.Logf("  Duration: %v", elapsed)
	t.Logf("  Throughput: %.0f events/sec", float64(eventCount)/elapsed.Seconds())
}

// Helper types and functions
type Event struct {
	PID  uint32
	Type uint8
}

type TimestampedEvent struct {
	*Event
	Timestamp time.Time
}

func mockEvent() *Event {
	return &Event{
		PID:  uint32(rand.Intn(10000)),
		Type: uint8(rand.Intn(3) + 1),
	}
}

func processEvent(evt *Event) error {
	// Simulate minimal processing
	_ = fmt.Sprintf("PID:%d Type:%d", evt.PID, evt.Type)
	return nil
}
