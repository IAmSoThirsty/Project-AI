// Package escalation — pressure.go
//
// EWMA pressure accumulator for the OCTOREFLEX escalation engine.
//
// Formula (from system spec §5.1.6):
//
//	P_{t+1} = α * P_t + (1 - α) * A_t
//
// Where:
//   - P_t  = pressure at time t (EWMA)
//   - A_t  = anomaly score at time t (instantaneous)
//   - α    = smoothing factor (default 0.8, configurable)
//
// Properties:
//   - α close to 1.0: slow response, high smoothing (resistant to spikes).
//   - α close to 0.0: fast response, low smoothing (reacts to single events).
//   - Default α=0.8 gives a half-life of approximately 3 evaluation cycles.
//
// Invariants:
//   - P ≥ 0.0 always (A ≥ 0 and α ∈ [0,1] guarantee this).
//   - One Accumulator instance per PID.
//   - Thread-safe: Update() and Value() may be called from different goroutines.
//   - No global state.

package escalation

import "sync"

// Accumulator implements the EWMA pressure accumulator for a single PID.
type Accumulator struct {
	mu    sync.Mutex
	alpha float64 // Smoothing factor α ∈ [0.0, 1.0]
	value float64 // Current pressure P_t
}

// NewAccumulator creates an Accumulator with the given smoothing factor.
// alpha must be in [0.0, 1.0]. Panics if out of range.
func NewAccumulator(alpha float64) *Accumulator {
	if alpha < 0.0 || alpha > 1.0 {
		panic("alpha must be in [0.0, 1.0]")
	}
	return &Accumulator{alpha: alpha}
}

// Update applies one EWMA step: P_{t+1} = α * P_t + (1 - α) * anomalyScore.
// anomalyScore must be ≥ 0.0.
// Returns the new pressure value P_{t+1}.
func (a *Accumulator) Update(anomalyScore float64) float64 {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.value = a.alpha*a.value + (1.0-a.alpha)*anomalyScore
	return a.value
}

// Value returns the current pressure value without updating it.
func (a *Accumulator) Value() float64 {
	a.mu.Lock()
	defer a.mu.Unlock()
	return a.value
}

// Reset sets the pressure to zero. Used after a process decays to NORMAL
// and its baseline is reset.
func (a *Accumulator) Reset() {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.value = 0.0
}
