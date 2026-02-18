// Package anomaly implements the Mahalanobis-distance anomaly scorer for
// OCTOREFLEX.
//
// Mathematical specification (from system spec §5.1.5):
//
//	A = (x - μ)ᵀ Σ⁻¹ (x - μ) + wₑ |ΔH|
//
// Where:
//   - x  = current feature vector (n-dimensional, n = feature count)
//   - μ  = baseline mean vector (from BoltDB baseline store)
//   - Σ  = baseline covariance matrix (n×n)
//   - Σ⁻¹ = precomputed inverse covariance matrix (updated on baseline change)
//   - wₑ = entropy weight coefficient (configurable, default 0.3)
//   - ΔH = entropy delta between current window and baseline entropy
//
// Complexity: O(n²) per evaluation where n = feature dimension.
// For OCTOREFLEX, n ≤ 16 (small), so O(256) operations per eval.
// Max evaluations per second: 10,000 (enforced by the event processor).
//
// Invariants:
//   - Score A ≥ 0 always (Mahalanobis distance is non-negative).
//   - If Σ is singular (not invertible), falls back to Euclidean distance.
//   - If baseline is absent (new process), returns score 0.0 (no data).
//   - Matrix inversion is precomputed and cached; recomputed only when
//     the baseline is updated (sample_count changes).

package anomaly

import (
	"fmt"
	"math"
	"sync"
)

// Baseline holds the statistical parameters for a single process binary.
// Loaded from BoltDB by the baseline store and passed to the engine.
type Baseline struct {
	// MeanVector is the per-feature mean computed from training samples.
	// Length must equal the feature dimension n.
	MeanVector []float64

	// CovarianceMatrix is the n×n sample covariance matrix.
	// Must be positive semi-definite.
	CovarianceMatrix [][]float64

	// InvCovariance is the precomputed inverse of CovarianceMatrix.
	// Nil if the matrix is singular (fallback to Euclidean distance).
	InvCovariance [][]float64

	// BaselineEntropy is the Shannon entropy of the baseline event distribution.
	BaselineEntropy float64

	// SampleCount is the number of samples used to compute this baseline.
	// Used to detect staleness.
	SampleCount int
}

// Engine computes anomaly scores for process feature vectors.
// Thread-safe: multiple goroutines may call Score() concurrently.
type Engine struct {
	mu            sync.RWMutex
	entropyWeight float64 // wₑ in the formula, default 0.3
}

// NewEngine creates an anomaly engine with the given entropy weight.
// entropyWeight must be in [0.0, 1.0]. Panics if out of range.
func NewEngine(entropyWeight float64) *Engine {
	if entropyWeight < 0.0 || entropyWeight > 1.0 {
		panic(fmt.Sprintf("entropyWeight %f out of range [0.0, 1.0]", entropyWeight))
	}
	return &Engine{entropyWeight: entropyWeight}
}

// Score computes the anomaly score A for a given feature vector x against
// a baseline. Returns 0.0 if baseline is nil (no data for this process).
//
// Formula: A = (x - μ)ᵀ Σ⁻¹ (x - μ) + wₑ |ΔH|
//
// Parameters:
//   - x        : current feature vector, len must equal len(baseline.MeanVector)
//   - baseline : statistical baseline for this process binary
//   - currentH : Shannon entropy of the current event window
//
// Returns: anomaly score A ≥ 0.0
func (e *Engine) Score(x []float64, baseline *Baseline, currentH float64) (float64, error) {
	if baseline == nil {
		return 0.0, nil
	}

	n := len(baseline.MeanVector)
	if len(x) != n {
		return 0.0, fmt.Errorf(
			"feature dimension mismatch: x has %d elements, baseline has %d",
			len(x), n,
		)
	}

	e.mu.RLock()
	wE := e.entropyWeight
	e.mu.RUnlock()

	// Compute (x - μ): the deviation vector.
	diff := make([]float64, n)
	for i := range diff {
		diff[i] = x[i] - baseline.MeanVector[i]
	}

	// Compute Mahalanobis distance squared: (x-μ)ᵀ Σ⁻¹ (x-μ)
	var mahal float64
	if baseline.InvCovariance != nil {
		mahal = mahalanobisSquared(diff, baseline.InvCovariance)
	} else {
		// Fallback: Euclidean distance squared (Σ⁻¹ = I).
		mahal = euclideanSquared(diff)
	}

	// Entropy delta: |ΔH| = |H_current - H_baseline|
	deltaH := math.Abs(currentH - baseline.BaselineEntropy)

	// Final score.
	score := mahal + wE*deltaH
	return score, nil
}

// mahalanobisSquared computes vᵀ M v where v is a vector and M is a matrix.
// Both must have compatible dimensions.
// Complexity: O(n²).
func mahalanobisSquared(v []float64, M [][]float64) float64 {
	n := len(v)
	// Mv = M * v  (matrix-vector product)
	Mv := make([]float64, n)
	for i := 0; i < n; i++ {
		for j := 0; j < n; j++ {
			Mv[i] += M[i][j] * v[j]
		}
	}
	// vᵀ Mv = dot(v, Mv)
	var result float64
	for i := 0; i < n; i++ {
		result += v[i] * Mv[i]
	}
	return result
}

// euclideanSquared computes the squared Euclidean norm of v.
func euclideanSquared(v []float64) float64 {
	var sum float64
	for _, vi := range v {
		sum += vi * vi
	}
	return sum
}

// InvertCovariance computes the inverse of a symmetric positive-definite
// matrix using Cholesky decomposition (LLᵀ = Σ).
//
// Returns nil if the matrix is singular or not positive-definite.
// The caller should store the result in Baseline.InvCovariance.
//
// Complexity: O(n³) — called only on baseline update, not per-event.
func InvertCovariance(cov [][]float64) [][]float64 {
	n := len(cov)
	if n == 0 {
		return nil
	}

	// Cholesky decomposition: L such that L * Lᵀ = cov.
	L := choleskyDecompose(cov)
	if L == nil {
		return nil // Singular or not positive-definite.
	}

	// Invert L (lower triangular forward substitution).
	Linv := invertLowerTriangular(L)
	if Linv == nil {
		return nil
	}

	// Σ⁻¹ = Lᵀ⁻¹ * L⁻¹  (since Σ = L Lᵀ → Σ⁻¹ = (Lᵀ)⁻¹ L⁻¹)
	inv := make([][]float64, n)
	for i := range inv {
		inv[i] = make([]float64, n)
		for j := 0; j < n; j++ {
			for k := 0; k < n; k++ {
				inv[i][j] += Linv[k][i] * Linv[k][j]
			}
		}
	}
	return inv
}

// choleskyDecompose computes the lower-triangular Cholesky factor L of A.
// Returns nil if A is not positive-definite (diagonal element ≤ 0).
func choleskyDecompose(A [][]float64) [][]float64 {
	n := len(A)
	L := make([][]float64, n)
	for i := range L {
		L[i] = make([]float64, n)
	}

	for i := 0; i < n; i++ {
		for j := 0; j <= i; j++ {
			sum := A[i][j]
			for k := 0; k < j; k++ {
				sum -= L[i][k] * L[j][k]
			}
			if i == j {
				if sum <= 0 {
					return nil // Not positive-definite.
				}
				L[i][j] = math.Sqrt(sum)
			} else {
				if L[j][j] == 0 {
					return nil // Singular.
				}
				L[i][j] = sum / L[j][j]
			}
		}
	}
	return L
}

// invertLowerTriangular computes the inverse of a lower-triangular matrix L
// using forward substitution. Returns nil on singular input.
func invertLowerTriangular(L [][]float64) [][]float64 {
	n := len(L)
	inv := make([][]float64, n)
	for i := range inv {
		inv[i] = make([]float64, n)
	}

	for j := 0; j < n; j++ {
		if L[j][j] == 0 {
			return nil // Singular.
		}
		inv[j][j] = 1.0 / L[j][j]
		for i := j + 1; i < n; i++ {
			var sum float64
			for k := j; k < i; k++ {
				sum -= L[i][k] * inv[k][j]
			}
			inv[i][j] = sum / L[i][i]
		}
	}
	return inv
}
