// Package escalation — severity.go
//
// Composite severity computation for the OCTOREFLEX escalation engine.
//
// Formula (from system spec §5.1.7):
//
//	S = w₁A + w₂Q + w₃I + w₄P
//
// Where:
//   - A = anomaly score (Mahalanobis + entropy delta, from anomaly engine)
//   - Q = quorum signal (0.0 or 1.0, from gossip quorum evaluator)
//   - I = integrity violation score (0.0–1.0, from integrity checker)
//   - P = EWMA pressure (from pressure accumulator, range [0.0, ∞))
//   - w₁, w₂, w₃, w₄ = configurable weights (defaults: 0.4, 0.2, 0.2, 0.2)
//
// Threshold table (from system spec §5.1.7, configurable):
//
//	S ≥ 1.0  → escalate to PRESSURE
//	S ≥ 3.0  → escalate to ISOLATED
//	S ≥ 6.0  → escalate to FROZEN
//	S ≥ 9.0  → escalate to QUARANTINED
//	S ≥ 12.0 → escalate to TERMINATED
//
// Evaluation is sequential: the highest threshold crossed determines the
// target state. Transition is atomic under the ProcessState mutex.
//
// Budget check:
//   Before any state transition above PRESSURE, the budget manager is
//   consulted. If the budget is exhausted, the transition is deferred
//   and logged. This prevents runaway containment actions.

package escalation

// Weights holds the four weight coefficients for the severity formula.
// All weights must be non-negative. They need not sum to 1.0.
type Weights struct {
	Anomaly   float64 // w₁: weight for Mahalanobis anomaly score
	Quorum    float64 // w₂: weight for gossip quorum signal
	Integrity float64 // w₃: weight for integrity violation score
	Pressure  float64 // w₄: weight for EWMA pressure
}

// DefaultWeights returns the default weight configuration.
func DefaultWeights() Weights {
	return Weights{
		Anomaly:   0.4,
		Quorum:    0.2,
		Integrity: 0.2,
		Pressure:  0.2,
	}
}

// Thresholds holds the severity score boundaries for each state transition.
// All thresholds must be strictly increasing.
type Thresholds struct {
	Pressure    float64 // S ≥ this → PRESSURE
	Isolated    float64 // S ≥ this → ISOLATED
	Frozen      float64 // S ≥ this → FROZEN
	Quarantined float64 // S ≥ this → QUARANTINED
	Terminated  float64 // S ≥ this → TERMINATED
}

// DefaultThresholds returns the default threshold configuration.
func DefaultThresholds() Thresholds {
	return Thresholds{
		Pressure:    1.0,
		Isolated:    3.0,
		Frozen:      6.0,
		Quarantined: 9.0,
		Terminated:  12.0,
	}
}

// Inputs holds the four input signals for the severity computation.
type Inputs struct {
	// AnomalyScore is the output of the Mahalanobis anomaly engine (A).
	// Range: [0.0, ∞). Typical range: [0.0, 20.0].
	AnomalyScore float64

	// QuorumSignal is 1.0 if the gossip quorum has confirmed this process
	// as anomalous on multiple nodes, 0.0 otherwise (Q).
	QuorumSignal float64

	// IntegrityScore is the normalised integrity violation score from the
	// integrity checker (I). Range: [0.0, 1.0].
	IntegrityScore float64

	// PressureScore is the EWMA-smoothed pressure value for this PID (P).
	// Range: [0.0, ∞). Grows as anomaly persists over time.
	PressureScore float64
}

// ComputeSeverity computes S = w₁A + w₂Q + w₃I + w₄P.
// All inputs and weights must be non-negative.
// Returns the composite severity score S ≥ 0.0.
func ComputeSeverity(inputs Inputs, weights Weights) float64 {
	return weights.Anomaly*inputs.AnomalyScore +
		weights.Quorum*inputs.QuorumSignal +
		weights.Integrity*inputs.IntegrityScore +
		weights.Pressure*inputs.PressureScore
}

// TargetState determines the target isolation state for a given severity score.
// Evaluates thresholds from highest to lowest (sequential, as per spec).
// Returns StateNormal if no threshold is crossed.
func TargetState(severity float64, thresholds Thresholds) State {
	switch {
	case severity >= thresholds.Terminated:
		return StateTerminated
	case severity >= thresholds.Quarantined:
		return StateQuarantined
	case severity >= thresholds.Frozen:
		return StateFrozen
	case severity >= thresholds.Isolated:
		return StateIsolated
	case severity >= thresholds.Pressure:
		return StatePressure
	default:
		return StateNormal
	}
}
