// Package lockfree — mpsc_queue_test.go
//
// Tests for lock-free MPSC queue.

package lockfree

import (
	"runtime"
	"sync"
	"sync/atomic"
	"testing"
	"unsafe"
)

// TestMPSCQueueBasic verifies basic enqueue/dequeue operations.
func TestMPSCQueueBasic(t *testing.T) {
	q := NewMPSCQueue(16)

	// Enqueue some items.
	for i := 0; i < 10; i++ {
		val := i
		if !q.Enqueue(unsafe.Pointer(&val)) {
			t.Fatalf("Enqueue(%d) failed", i)
		}
	}

	// Dequeue and verify order.
	for i := 0; i < 10; i++ {
		ptr := q.Dequeue()
		if ptr == nil {
			t.Fatalf("Dequeue() returned nil at index %d", i)
		}
		val := *(*int)(ptr)
		if val != i {
			t.Errorf("Expected %d, got %d", i, val)
		}
	}

	// Queue should now be empty.
	if ptr := q.Dequeue(); ptr != nil {
		t.Errorf("Expected empty queue, got %v", ptr)
	}
}

// TestMPSCQueueFull verifies backpressure when queue is full.
func TestMPSCQueueFull(t *testing.T) {
	const capacity = 8
	q := NewMPSCQueue(capacity)

	// Fill the queue.
	for i := 0; i < int(capacity); i++ {
		val := i
		if !q.Enqueue(unsafe.Pointer(&val)) {
			t.Fatalf("Enqueue(%d) failed before capacity reached", i)
		}
	}

	// Next enqueue should fail.
	overflow := 999
	if q.Enqueue(unsafe.Pointer(&overflow)) {
		t.Error("Enqueue succeeded when queue was full")
	}

	// Dequeue one item to make space.
	q.Dequeue()

	// Now enqueue should succeed.
	if !q.Enqueue(unsafe.Pointer(&overflow)) {
		t.Error("Enqueue failed after dequeue")
	}
}

// TestMPSCQueueConcurrent verifies thread-safety with multiple producers.
func TestMPSCQueueConcurrent(t *testing.T) {
	const (
		producers  = 8
		itemsPerP  = 10000
		capacity   = 1024
	)

	q := NewMPSCQueue(capacity)
	
	// Launch producers.
	var wg sync.WaitGroup
	wg.Add(producers)
	
	for p := 0; p < producers; p++ {
		producerID := p
		go func() {
			defer wg.Done()
			for i := 0; i < itemsPerP; i++ {
				val := producerID*itemsPerP + i
				for !q.Enqueue(unsafe.Pointer(&val)) {
					runtime.Gosched() // Yield if queue full.
				}
			}
		}()
	}

	// Consumer goroutine.
	received := make([]bool, producers*itemsPerP)
	done := make(chan struct{})
	
	go func() {
		defer close(done)
		count := 0
		for count < producers*itemsPerP {
			ptr := q.Dequeue()
			if ptr != nil {
				val := *(*int)(ptr)
				if val < 0 || val >= len(received) {
					t.Errorf("Invalid value: %d", val)
					return
				}
				if received[val] {
					t.Errorf("Duplicate value: %d", val)
					return
				}
				received[val] = true
				count++
			} else {
				runtime.Gosched()
			}
		}
	}()

	wg.Wait()
	<-done

	// Verify all items received.
	for i, ok := range received {
		if !ok {
			t.Errorf("Item %d not received", i)
		}
	}
}

// TestMPSCQueueLen verifies the Len() method.
func TestMPSCQueueLen(t *testing.T) {
	q := NewMPSCQueue(32)

	if got := q.Len(); got != 0 {
		t.Errorf("Empty queue Len() = %d, want 0", got)
	}

	// Add some items.
	for i := 0; i < 10; i++ {
		val := i
		q.Enqueue(unsafe.Pointer(&val))
	}

	if got := q.Len(); got != 10 {
		t.Errorf("Queue Len() = %d, want 10", got)
	}

	// Remove some items.
	for i := 0; i < 5; i++ {
		q.Dequeue()
	}

	if got := q.Len(); got != 5 {
		t.Errorf("Queue Len() = %d, want 5", got)
	}
}

// BenchmarkMPSCQueueEnqueue measures enqueue performance.
func BenchmarkMPSCQueueEnqueue(b *testing.B) {
	q := NewMPSCQueue(1024)
	val := 42

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		q.Enqueue(unsafe.Pointer(&val))
	}
}

// BenchmarkMPSCQueueDequeue measures dequeue performance.
func BenchmarkMPSCQueueDequeue(b *testing.B) {
	q := NewMPSCQueue(1024)
	
	// Pre-fill queue.
	for i := 0; i < 1024; i++ {
		val := i
		q.Enqueue(unsafe.Pointer(&val))
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = q.Dequeue()
	}
}

// BenchmarkMPSCQueuePair measures enqueue + dequeue latency.
func BenchmarkMPSCQueuePair(b *testing.B) {
	q := NewMPSCQueue(1024)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		val := i
		q.Enqueue(unsafe.Pointer(&val))
		_ = q.Dequeue()
	}
}

// BenchmarkMPSCQueueConcurrentThroughput measures multi-producer throughput.
func BenchmarkMPSCQueueConcurrentThroughput(b *testing.B) {
	const producers = 4
	q := NewMPSCQueue(4096)

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		val := 42
		for pb.Next() {
			for !q.Enqueue(unsafe.Pointer(&val)) {
				runtime.Gosched()
			}
		}
	})
}
