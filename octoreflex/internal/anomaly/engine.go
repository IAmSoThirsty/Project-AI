// Package anomaly — engine.go
//
// Public interface for the OCTOREFLEX anomaly engine.
//
// This file defines the Engine type and Baseline struct that are used by
// the test suite and the main worker pipeline.
//
// The Engine wraps the Mahalanobis distance computation (mahalanobis.go)
// and entropy delta computation (entropy.go) into a single Score() call.
//
// Score formula (from spec §5.1.5):
//   A = mahal(x, μ, Σ) + wₑ * |H(current) - H(baseline)|
//
// Where:
//   - mahal(x, μ, Σ) = (x-μ)ᵀ Σ⁻¹ (x-μ)  (Mahalanobis distance squared)
//   - wₑ = entropy weight (config: anomaly.entropy_weight, default 0.3)
//   - H = Shannon entropy of the event type distribution
//
// Baseline:
//   - Computed from a training window of normal process behaviour.
//   - Stored in BoltDB (storage.BaselineRecord) and loaded on startup.
//   - Updated incrementally as new normal samples arrive.
//   - InvCovariance is pre-computed and cached to avoid repeated inversion.
//
// Nil baseline handling:
//   - If no baseline exists for a PID's binary, Score() returns 0.0.
//   - The process is not escalated until a baseline is established.
//   - Baseline establishment requires config.Agent.WindowDuration of samples.

package anomaly

import (
	"fmt"
	"math"
)

// EventCounts holds the per-type event count for entropy computation.
// Index 0 is unused (event types start at 1 per the BPF header).
// Index 1 = socket_connect, 2 = file_open, 3 = setuid.
// Length must be 4 (indices 0–3).
type EventCounts [4]uint64

// Baseline holds the pre-computed statistical baseline for a process binary.
// All fields must be consistent (same dimensionality).
type Baseline struct {
	// MeanVector μ is the per-feature mean from training samples.
	// Length = number of features (currently 3: event rates per type).
	MeanVector []float64

	// CovarianceMatrix Σ is the n×n sample covariance matrix.
	// Length = n×n where n = len(MeanVector).
	CovarianceMatrix [][]float64

	// InvCovariance Σ⁻¹ is the pre-computed inverse of CovarianceMatrix.
	// nil if the matrix is singular (Euclidean fallback used).
	InvCovariance [][]float64

	// BaselineEntropy H is the Shannon entropy of the baseline event distribution.
	BaselineEntropy float64
}

// Engine computes anomaly scores for process feature vectors.
type Engine struct {
	entropyWeight float64 // wₑ ∈ [0.0, 1.0]
}

// NewEngine creates an Engine with the given entropy weight.
// entropyWeight must be in [0.0, 1.0].
func NewEngine(entropyWeight float64) *Engine {
	return &Engine{entropyWeight: entropyWeight}
}

// Score computes the composite anomaly score A for a feature vector x.
//
// Parameters:
//   - x: current feature vector (event rates per type, length must match baseline)
//   - baseline: pre-computed baseline (nil → returns 0.0, no error)
//   - currentEntropy: Shannon entropy of the current event distribution
//
// Returns:
//   - score: A ≥ 0.0
//   - error: non-nil if x and baseline have incompatible dimensions
func (e *Engine) Score(x []float64, baseline *Baseline, currentEntropy float64) (float64, error) {
	if baseline == nil {
		return 0.0, nil
	}

	if len(x) != len(baseline.MeanVector) {
		return 0.0, fmt.Errorf(
			"anomaly.Score: dimension mismatch: x has %d features, baseline has %d",
			len(x), len(baseline.MeanVector))
	}

	// Compute Mahalanobis distance squared.
	var mahal float64
	if baseline.InvCovariance != nil {
		mahal = MahalanobisSquared(x, baseline.MeanVector, baseline.InvCovariance)
	} else {
		// Singular covariance — fall back to squared Euclidean distance.
		mahal = euclideanSquared(x, baseline.MeanVector)
	}

	// Entropy delta.
	entropyDelta := math.Abs(currentEntropy - baseline.BaselineEntropy)

	// Composite score.
	return mahal + e.entropyWeight*entropyDelta, nil
}

// euclideanSquared computes the squared Euclidean distance between x and μ.
// Complexity: O(n).
func euclideanSquared(x, mu []float64) float64 {
	var sum float64
	for i := range x {
		d := x[i] - mu[i]
		sum += d * d
	}
	return sum
}
