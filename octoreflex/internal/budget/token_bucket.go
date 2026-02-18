// Package budget implements the token bucket rate limiter for OCTOREFLEX
// containment actions.
//
// Specification (from system spec §5.1.8):
//   - Capacity: configurable (default 100 tokens)
//   - Refill interval: 60 seconds
//   - Refill amount: full capacity (not incremental)
//   - Consumption: atomic, per-action cost
//
// Cost model:
//   - PRESSURE transition:    cost 1
//   - ISOLATED transition:    cost 5
//   - FROZEN transition:      cost 10
//   - QUARANTINED transition: cost 20
//   - TERMINATED transition:  cost 50
//
// Rationale: Higher-impact actions consume more budget, preventing a
// cascade of SIGKILL actions from a single burst of anomalous events.
// The 60-second full refill ensures the system recovers quickly after
// a legitimate threat response.
//
// Invariants:
//   - tokens ∈ [0, capacity] at all times.
//   - Consume() is atomic under mutex.
//   - Refill goroutine runs for the lifetime of the Bucket.
//   - No external dependencies.

package budget

import (
	"sync"
	"sync/atomic"
	"time"

	"github.com/octoreflex/octoreflex/internal/escalation"
)

// CostModel defines the token cost for each state transition.
// Costs must be positive integers.
var CostModel = map[escalation.State]int{
	escalation.StatePressure:    1,
	escalation.StateIsolated:    5,
	escalation.StateFrozen:      10,
	escalation.StateQuarantined: 20,
	escalation.StateTerminated:  50,
}

// Bucket is a thread-safe token bucket for rate-limiting containment actions.
type Bucket struct {
	mu           sync.Mutex
	capacity     int
	tokens       int
	refillPeriod time.Duration

	// consumedTotal tracks lifetime tokens consumed (for metrics).
	consumedTotal atomic.Uint64

	// refillCount tracks number of refill cycles (for metrics).
	refillCount atomic.Uint64

	// stop channel for graceful shutdown of the refill goroutine.
	stop chan struct{}
}

// New creates a Bucket with the given capacity and starts the refill goroutine.
// capacity must be > 0. refillPeriod must be > 0.
// Call Close() to stop the refill goroutine.
func New(capacity int, refillPeriod time.Duration) *Bucket {
	if capacity <= 0 {
		panic("budget.Bucket: capacity must be > 0")
	}
	if refillPeriod <= 0 {
		panic("budget.Bucket: refillPeriod must be > 0")
	}
	b := &Bucket{
		capacity:     capacity,
		tokens:       capacity,
		refillPeriod: refillPeriod,
		stop:         make(chan struct{}),
	}
	go b.refillLoop()
	return b
}

// refillLoop runs in a dedicated goroutine and refills the bucket to full
// capacity every refillPeriod. Exits when Close() is called.
func (b *Bucket) refillLoop() {
	ticker := time.NewTicker(b.refillPeriod)
	defer ticker.Stop()
	for {
		select {
		case <-ticker.C:
			b.mu.Lock()
			b.tokens = b.capacity
			b.mu.Unlock()
			b.refillCount.Add(1)
		case <-b.stop:
			return
		}
	}
}

// Consume attempts to consume `cost` tokens from the bucket.
// Returns true if the tokens were available and consumed.
// Returns false if insufficient tokens remain (action must be deferred).
// Thread-safe.
func (b *Bucket) Consume(cost int) bool {
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.tokens >= cost {
		b.tokens -= cost
		b.consumedTotal.Add(uint64(cost))
		return true
	}
	return false
}

// ConsumeForState consumes the standard cost for a given target state.
// Returns false if the state has no defined cost (e.g., StateNormal).
func (b *Bucket) ConsumeForState(target escalation.State) bool {
	cost, ok := CostModel[target]
	if !ok {
		return true // No cost for this state (e.g., NORMAL — decay is free).
	}
	return b.Consume(cost)
}

// Remaining returns the current token count.
func (b *Bucket) Remaining() int {
	b.mu.Lock()
	defer b.mu.Unlock()
	return b.tokens
}

// Capacity returns the maximum token capacity.
func (b *Bucket) Capacity() int {
	return b.capacity // Immutable after construction.
}

// ConsumedTotal returns the lifetime total of tokens consumed.
func (b *Bucket) ConsumedTotal() uint64 {
	return b.consumedTotal.Load()
}

// RefillCount returns the number of refill cycles completed.
func (b *Bucket) RefillCount() uint64 {
	return b.refillCount.Load()
}

// Close stops the refill goroutine. Safe to call once.
func (b *Bucket) Close() {
	close(b.stop)
}
