// Package budget — token_bucket_test.go
//
// Unit tests for the token bucket rate limiter.
// Target: 95%+ coverage.

package budget

import (
	"sync"
	"testing"
	"time"

	"github.com/octoreflex/octoreflex/internal/escalation"
)

func TestNew_ValidParameters(t *testing.T) {
	b := New(100, time.Second)
	defer b.Close()
	
	if b.Capacity() != 100 {
		t.Errorf("Capacity() = %d, want 100", b.Capacity())
	}
	if b.Remaining() != 100 {
		t.Errorf("Remaining() = %d, want 100 (should start full)", b.Remaining())
	}
}

func TestNew_PanicOnZeroCapacity(t *testing.T) {
	defer func() {
		if r := recover(); r == nil {
			t.Fatal("New(0, time.Second) did not panic")
		}
	}()
	_ = New(0, time.Second)
}

func TestNew_PanicOnNegativeCapacity(t *testing.T) {
	defer func() {
		if r := recover(); r == nil {
			t.Fatal("New(-1, time.Second) did not panic")
		}
	}()
	_ = New(-1, time.Second)
}

func TestNew_PanicOnZeroRefillPeriod(t *testing.T) {
	defer func() {
		if r := recover(); r == nil {
			t.Fatal("New(100, 0) did not panic")
		}
	}()
	_ = New(100, 0)
}

func TestConsume_Success(t *testing.T) {
	b := New(100, time.Hour) // Long refill to avoid race
	defer b.Close()
	
	ok := b.Consume(10)
	if !ok {
		t.Fatal("Consume(10) failed, expected success")
	}
	
	if b.Remaining() != 90 {
		t.Errorf("Remaining() = %d, want 90", b.Remaining())
	}
	if b.ConsumedTotal() != 10 {
		t.Errorf("ConsumedTotal() = %d, want 10", b.ConsumedTotal())
	}
}

func TestConsume_Failure_InsufficientTokens(t *testing.T) {
	b := New(50, time.Hour)
	defer b.Close()
	
	ok := b.Consume(60)
	if ok {
		t.Fatal("Consume(60) succeeded with only 50 tokens")
	}
	
	if b.Remaining() != 50 {
		t.Errorf("Remaining() = %d, want 50 (should be unchanged)", b.Remaining())
	}
	if b.ConsumedTotal() != 0 {
		t.Errorf("ConsumedTotal() = %d, want 0", b.ConsumedTotal())
	}
}

func TestConsume_ExactCapacity(t *testing.T) {
	b := New(100, time.Hour)
	defer b.Close()
	
	ok := b.Consume(100)
	if !ok {
		t.Fatal("Consume(100) failed with capacity 100")
	}
	
	if b.Remaining() != 0 {
		t.Errorf("Remaining() = %d, want 0", b.Remaining())
	}
}

func TestConsume_MultipleSmallConsumptions(t *testing.T) {
	b := New(100, time.Hour)
	defer b.Close()
	
	for i := 0; i < 10; i++ {
		if !b.Consume(10) {
			t.Fatalf("Consume(10) failed at iteration %d", i)
		}
	}
	
	if b.Remaining() != 0 {
		t.Errorf("Remaining() = %d, want 0", b.Remaining())
	}
	if b.ConsumedTotal() != 100 {
		t.Errorf("ConsumedTotal() = %d, want 100", b.ConsumedTotal())
	}
	
	// Next consume should fail
	if b.Consume(1) {
		t.Fatal("Consume(1) succeeded when bucket empty")
	}
}

func TestConsumeForState_ValidStates(t *testing.T) {
	tests := []struct {
		state    escalation.State
		expected int
	}{
		{escalation.StatePressure, 1},
		{escalation.StateIsolated, 5},
		{escalation.StateFrozen, 10},
		{escalation.StateQuarantined, 20},
		{escalation.StateTerminated, 50},
	}
	
	for _, tt := range tests {
		t.Run(tt.state.String(), func(t *testing.T) {
			b := New(100, time.Hour)
			defer b.Close()
			
			ok := b.ConsumeForState(tt.state)
			if !ok {
				t.Fatalf("ConsumeForState(%s) failed", tt.state)
			}
			
			remaining := b.Remaining()
			expectedRemaining := 100 - tt.expected
			if remaining != expectedRemaining {
				t.Errorf("Remaining() = %d, want %d", remaining, expectedRemaining)
			}
		})
	}
}

func TestConsumeForState_Normal_FreeCost(t *testing.T) {
	b := New(100, time.Hour)
	defer b.Close()
	
	// NORMAL state has no cost (decay is free)
	ok := b.ConsumeForState(escalation.StateNormal)
	if !ok {
		t.Fatal("ConsumeForState(NORMAL) failed")
	}
	
	if b.Remaining() != 100 {
		t.Errorf("Remaining() = %d, want 100 (NORMAL should be free)", b.Remaining())
	}
}

func TestRefillLoop_RefillsToCapacity(t *testing.T) {
	b := New(100, 50*time.Millisecond)
	defer b.Close()
	
	// Consume some tokens
	b.Consume(60)
	if b.Remaining() != 40 {
		t.Fatalf("Remaining() = %d, want 40 before refill", b.Remaining())
	}
	
	// Wait for refill
	time.Sleep(100 * time.Millisecond)
	
	if b.Remaining() != 100 {
		t.Errorf("Remaining() = %d, want 100 after refill", b.Remaining())
	}
	
	if b.RefillCount() == 0 {
		t.Error("RefillCount() = 0, expected at least 1 refill")
	}
}

func TestRefillLoop_MultipleRefills(t *testing.T) {
	b := New(100, 30*time.Millisecond)
	defer b.Close()
	
	// Wait for multiple refills
	time.Sleep(150 * time.Millisecond)
	
	count := b.RefillCount()
	if count < 3 {
		t.Errorf("RefillCount() = %d, want >= 3", count)
	}
}

func TestClose_StopsRefillLoop(t *testing.T) {
	b := New(100, 20*time.Millisecond)
	
	// Wait for initial refill
	time.Sleep(50 * time.Millisecond)
	countBefore := b.RefillCount()
	
	// Close the bucket
	b.Close()
	
	// Wait to confirm no more refills
	time.Sleep(100 * time.Millisecond)
	countAfter := b.RefillCount()
	
	if countAfter != countBefore {
		t.Errorf("RefillCount increased after Close(): before=%d, after=%d", countBefore, countAfter)
	}
}

func TestConcurrentConsumption(t *testing.T) {
	b := New(1000, time.Hour)
	defer b.Close()
	
	var wg sync.WaitGroup
	goroutines := 100
	consumePerGoroutine := 10
	
	successCount := make(chan int, goroutines)
	
	for i := 0; i < goroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			count := 0
			for j := 0; j < consumePerGoroutine; j++ {
				if b.Consume(1) {
					count++
				}
			}
			successCount <- count
		}()
	}
	
	wg.Wait()
	close(successCount)
	
	total := 0
	for c := range successCount {
		total += c
	}
	
	// Total successful consumptions should equal 1000 (capacity)
	if total != 1000 {
		t.Errorf("Total successful consumptions = %d, want 1000", total)
	}
	
	if b.Remaining() != 0 {
		t.Errorf("Remaining() = %d, want 0", b.Remaining())
	}
}

func TestCostModel(t *testing.T) {
	// Verify cost model matches spec
	tests := []struct {
		state State
		cost  int
	}{
		{escalation.StatePressure, 1},
		{escalation.StateIsolated, 5},
		{escalation.StateFrozen, 10},
		{escalation.StateQuarantined, 20},
		{escalation.StateTerminated, 50},
	}
	
	for _, tt := range tests {
		t.Run(tt.state.String(), func(t *testing.T) {
			cost, ok := CostModel[tt.state]
			if !ok {
				t.Fatalf("CostModel missing entry for %s", tt.state)
			}
			if cost != tt.cost {
				t.Errorf("CostModel[%s] = %d, want %d", tt.state, cost, tt.cost)
			}
		})
	}
}

func BenchmarkConsume(b *testing.B) {
	bucket := New(1000000, time.Hour)
	defer bucket.Close()
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		bucket.Consume(1)
	}
}

func BenchmarkConsume_Concurrent(b *testing.B) {
	bucket := New(1000000, time.Hour)
	defer bucket.Close()
	
	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			bucket.Consume(1)
		}
	})
}
