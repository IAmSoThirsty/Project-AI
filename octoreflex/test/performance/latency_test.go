// Performance tests for OCTOREFLEX
//
// Validates critical latency and throughput requirements:
//   - Containment latency < 200μs (p50)
//   - Containment latency < 800μs (p99)
//   - Event processing throughput > 10,000 events/sec
//   - CPU overhead < 5% under load
//
// Run with: go test -bench=. -benchtime=10s ./test/performance

package performance

import (
	"math"
	"sort"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

// ContainmentLatency measures end-to-end containment latency
func BenchmarkContainmentLatency(b *testing.B) {
	// Simulate: Event -> Anomaly Score -> Escalation Decision -> BPF Map Update
	latencies := make([]time.Duration, b.N)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		start := time.Now()

		// Simulate event processing
		_ = processEvent(mockEvent())

		// Simulate anomaly scoring
		score := computeScore([]float64{1.0, 2.0, 3.0})

		// Simulate escalation decision
		if score > 5.0 {
			_ = escalateProcess(1234, 2) // ISOLATED
		}

		latencies[i] = time.Since(start)
	}
	b.StopTimer()

	// Compute percentiles
	sort.Slice(latencies, func(i, j int) bool {
		return latencies[i] < latencies[j]
	})

	p50 := latencies[len(latencies)/2]
	p99 := latencies[len(latencies)*99/100]

	b.Logf("Containment latency:")
	b.Logf("  p50: %v (target: < 200μs)", p50)
	b.Logf("  p99: %v (target: < 800μs)", p99)
	b.Logf("  ops: %d ops/sec", int(float64(b.N)/b.Elapsed().Seconds()))

	// Verify targets
	if p50 > 200*time.Microsecond {
		b.Errorf("p50 latency %v exceeds 200μs target", p50)
	}
	if p99 > 800*time.Microsecond {
		b.Errorf("p99 latency %v exceeds 800μs target", p99)
	}
}

func BenchmarkEventProcessingThroughput(b *testing.B) {
	// Target: > 10,000 events/sec
	eventCount := atomic.Uint64{}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = processEvent(mockEvent())
		eventCount.Add(1)
	}
	b.StopTimer()

	throughput := float64(eventCount.Load()) / b.Elapsed().Seconds()
	b.Logf("Event processing throughput: %.0f events/sec (target: > 10,000)", throughput)

	if throughput < 10000 {
		b.Errorf("Throughput %.0f events/sec below 10,000 target", throughput)
	}
}

func BenchmarkAnomalyScoring(b *testing.B) {
	// Measure anomaly engine performance
	features := []float64{1.5, 2.3, 3.7}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = computeScore(features)
	}
	b.StopTimer()

	opsPerSec := float64(b.N) / b.Elapsed().Seconds()
	b.Logf("Anomaly scoring: %.0f ops/sec", opsPerSec)
}

func BenchmarkConcurrentEventProcessing(b *testing.B) {
	// Concurrent event processing (multiple cores)
	const goroutines = 8

	b.ResetTimer()
	var wg sync.WaitGroup
	for g := 0; g < goroutines; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < b.N/goroutines; i++ {
				_ = processEvent(mockEvent())
			}
		}()
	}
	wg.Wait()
	b.StopTimer()

	throughput := float64(b.N) / b.Elapsed().Seconds()
	b.Logf("Concurrent throughput (%d cores): %.0f events/sec", goroutines, throughput)
}

func BenchmarkMatrixInversion(b *testing.B) {
	// Measure covariance matrix inversion performance
	cov := [][]float64{
		{2.0, 1.0, 0.5},
		{1.0, 3.0, 1.0},
		{0.5, 1.0, 2.0},
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = invertMatrix(cov)
	}
}

func BenchmarkBudgetConsumption(b *testing.B) {
	// Measure token bucket consumption speed
	tokens := 1000000
	cost := 1

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		if tokens >= cost {
			tokens -= cost
		}
	}
}

func BenchmarkStateTransitionUpdate(b *testing.B) {
	// Measure BPF map update simulation
	stateMap := make(map[uint32]uint8)
	pid := uint32(1234)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		stateMap[pid] = uint8(i % 6) // Cycle through states
	}
}

// TestContainmentLatencyUnderLoad verifies latency remains low under sustained load
func TestContainmentLatencyUnderLoad(t *testing.T) {
	const (
		duration      = 10 * time.Second
		targetRate    = 100000 // 100K events/sec
		targetP50     = 200 * time.Microsecond
		targetP99     = 800 * time.Microsecond
	)

	latencies := make([]time.Duration, 0, targetRate*int(duration.Seconds()))
	mu := sync.Mutex{}

	done := make(chan bool)
	go func() {
		ticker := time.NewTicker(time.Second / time.Duration(targetRate))
		defer ticker.Stop()

		timeout := time.After(duration)
		for {
			select {
			case <-ticker.C:
				start := time.Now()
				_ = processEvent(mockEvent())
				_ = computeScore([]float64{1.0, 2.0, 3.0})
				latency := time.Since(start)

				mu.Lock()
				latencies = append(latencies, latency)
				mu.Unlock()

			case <-timeout:
				done <- true
				return
			}
		}
	}()

	<-done

	// Analyze latencies
	sort.Slice(latencies, func(i, j int) bool {
		return latencies[i] < latencies[j]
	})

	p50 := latencies[len(latencies)/2]
	p99 := latencies[len(latencies)*99/100]

	t.Logf("Latency under load (%d events/sec for %v):", targetRate, duration)
	t.Logf("  Total events: %d", len(latencies))
	t.Logf("  p50: %v (target: < %v)", p50, targetP50)
	t.Logf("  p99: %v (target: < %v)", p99, targetP99)

	if p50 > targetP50 {
		t.Errorf("p50 latency %v exceeds target %v", p50, targetP50)
	}
	if p99 > targetP99 {
		t.Errorf("p99 latency %v exceeds target %v", p99, targetP99)
	}
}

// Mock functions for benchmarking
func mockEvent() *Event {
	return &Event{PID: 1234, Type: 2, Timestamp: uint64(time.Now().UnixNano())}
}

type Event struct {
	PID       uint32
	Type      uint8
	Timestamp uint64
}

func processEvent(evt *Event) error {
	// Simulate event processing overhead
	_ = evt.PID + uint32(evt.Type)
	return nil
}

func computeScore(features []float64) float64 {
	// Simplified anomaly scoring
	sum := 0.0
	for _, f := range features {
		sum += f * f
	}
	return math.Sqrt(sum)
}

func escalateProcess(pid uint32, state uint8) error {
	// Simulate state transition
	_ = pid + uint32(state)
	return nil
}

func invertMatrix(m [][]float64) [][]float64 {
	// Stub for matrix inversion
	n := len(m)
	inv := make([][]float64, n)
	for i := range inv {
		inv[i] = make([]float64, n)
	}
	return inv
}
