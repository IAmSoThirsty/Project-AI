// Package contrib — scorer.go
//
// Plugin interface for custom anomaly scorers.
//
// OCTOREFLEX v0.2 introduces a contrib/ directory for community-contributed
// extensions. The primary extension point is the AnomalyScorer interface,
// which allows users to replace or augment the built-in Mahalanobis scorer
// with custom logic (e.g., ML models, rule-based systems, eBPF-assisted
// feature extractors).
//
// Plugin registration:
//   Plugins register themselves in an init() function using RegisterScorer().
//   The agent selects the active scorer via config:
//
//     agent:
//       anomaly_scorer: "mahalanobis"  # default
//       # anomaly_scorer: "my-custom-scorer"
//
//   Built-in scorers: "mahalanobis" (default).
//   Community scorers: registered via contrib.RegisterScorer().
//
// Plugin contract:
//   - Score() must be goroutine-safe (called from multiple workers).
//   - Score() must return in < 1ms to avoid blocking the event pipeline.
//   - Score() must not allocate on the hot path (use sync.Pool if needed).
//   - Score() must not call any blocking I/O (no disk, no network).
//   - Score() must not panic (use recover() internally if needed).
//   - Name() must return a stable, unique string (used as config key).
//
// Example plugin (contrib/scorers/zscore/zscore.go):
//
//   package zscore
//
//   import (
//     "math"
//     "github.com/octoreflex/octoreflex/contrib"
//   )
//
//   func init() {
//     contrib.RegisterScorer(&ZScoreScorer{})
//   }
//
//   type ZScoreScorer struct{}
//
//   func (z *ZScoreScorer) Name() string { return "zscore" }
//
//   func (z *ZScoreScorer) Score(req contrib.ScoreRequest) (float64, error) {
//     if req.Baseline == nil { return 0, nil }
//     var sum float64
//     for i, x := range req.Features {
//       if req.Baseline.StdDev[i] == 0 { continue }
//       z := (x - req.Baseline.Mean[i]) / req.Baseline.StdDev[i]
//       sum += z * z
//     }
//     return math.Sqrt(sum / float64(len(req.Features))), nil
//   }
//
//   func (z *ZScoreScorer) UpdateBaseline(req contrib.UpdateRequest) error { return nil }

package contrib

import (
	"fmt"
	"sync"
)

// ─── AnomalyScorer interface ──────────────────────────────────────────────────

// BaselineSnapshot is the read-only view of a process baseline passed to
// custom scorers. It contains pre-computed statistics from the local store.
type BaselineSnapshot struct {
	// ProcessHash is sha256(binary_path), hex-encoded.
	ProcessHash string

	// Mean is the per-feature mean vector μ.
	Mean []float64

	// StdDev is the per-feature standard deviation (sqrt(diag(Σ))).
	// Provided as a convenience for z-score based scorers.
	StdDev []float64

	// InvCovariance is Σ⁻¹. nil if the matrix is singular.
	// Provided for Mahalanobis-compatible scorers.
	InvCovariance [][]float64

	// BaselineEntropy is the Shannon entropy of the baseline event distribution.
	BaselineEntropy float64

	// SampleCount is the number of training samples used to compute this baseline.
	SampleCount uint32
}

// ScoreRequest is the input to AnomalyScorer.Score().
type ScoreRequest struct {
	// PID is the process ID being scored.
	PID uint32

	// Features is the current feature vector for the process.
	// Length matches Baseline.Mean if Baseline is non-nil.
	Features []float64

	// CurrentEntropy is the Shannon entropy of the current event distribution.
	CurrentEntropy float64

	// Baseline is the pre-computed baseline for this process binary.
	// nil if no baseline has been established yet.
	Baseline *BaselineSnapshot

	// TimestampNs is the event timestamp in nanoseconds.
	TimestampNs int64
}

// UpdateRequest is the input to AnomalyScorer.UpdateBaseline().
// Called after each training sample to allow the scorer to update its
// internal state (e.g., online mean/covariance updates).
type UpdateRequest struct {
	// PID is the process ID.
	PID uint32

	// ProcessHash is sha256(binary_path), hex-encoded.
	ProcessHash string

	// Features is the new feature vector sample.
	Features []float64

	// EventEntropy is the Shannon entropy of the event distribution for this sample.
	EventEntropy float64
}

// AnomalyScorer is the interface that custom anomaly scorers must implement.
//
// Contract:
//   - Score() must be goroutine-safe.
//   - Score() must return in < 1ms.
//   - Score() must not allocate on the hot path.
//   - Score() must not call blocking I/O.
//   - Score() must not panic.
//   - Name() must return a stable, unique string.
type AnomalyScorer interface {
	// Name returns the unique identifier for this scorer.
	// Used as the config key (agent.anomaly_scorer).
	Name() string

	// Score computes an anomaly score for the given request.
	// Returns a non-negative score (higher = more anomalous).
	// Returns 0.0 if no baseline is available (req.Baseline == nil).
	Score(req ScoreRequest) (float64, error)

	// UpdateBaseline is called after each training sample.
	// Implementations may update internal state (e.g., online statistics).
	// May be a no-op if the scorer uses only the BaselineSnapshot.
	UpdateBaseline(req UpdateRequest) error
}

// ─── Registry ─────────────────────────────────────────────────────────────────

var (
	registryMu sync.RWMutex
	registry   = make(map[string]AnomalyScorer)
)

// RegisterScorer registers a custom anomaly scorer.
// Panics if a scorer with the same name is already registered.
// Call from init() functions in plugin packages.
func RegisterScorer(s AnomalyScorer) {
	registryMu.Lock()
	defer registryMu.Unlock()
	if _, exists := registry[s.Name()]; exists {
		panic(fmt.Sprintf("contrib: scorer %q already registered", s.Name()))
	}
	registry[s.Name()] = s
}

// GetScorer returns the registered scorer with the given name.
// Returns an error if no scorer with that name is registered.
func GetScorer(name string) (AnomalyScorer, error) {
	registryMu.RLock()
	defer registryMu.RUnlock()
	s, ok := registry[name]
	if !ok {
		return nil, fmt.Errorf("contrib: scorer %q not registered (available: %v)", name, listNames())
	}
	return s, nil
}

// ListScorers returns the names of all registered scorers.
func ListScorers() []string {
	registryMu.RLock()
	defer registryMu.RUnlock()
	return listNames()
}

func listNames() []string {
	names := make([]string, 0, len(registry))
	for k := range registry {
		names = append(names, k)
	}
	return names
}

// ─── Example contrib scorer: Z-Score ─────────────────────────────────────────
// This is provided as a reference implementation in the contrib package itself.
// Community scorers should be in contrib/scorers/<name>/<name>.go.

// ZScoreScorer is a simple z-score based anomaly scorer.
// Score = RMS z-score across all features.
// Registered as "zscore".
type ZScoreScorer struct{}

func init() {
	RegisterScorer(&ZScoreScorer{})
}

func (z *ZScoreScorer) Name() string { return "zscore" }

func (z *ZScoreScorer) Score(req ScoreRequest) (float64, error) {
	if req.Baseline == nil {
		return 0.0, nil
	}
	if len(req.Features) != len(req.Baseline.Mean) {
		return 0.0, fmt.Errorf("zscore: dimension mismatch: features=%d baseline=%d",
			len(req.Features), len(req.Baseline.Mean))
	}
	var sumSq float64
	n := 0
	for i, x := range req.Features {
		if req.Baseline.StdDev[i] == 0 {
			continue // Skip zero-variance features.
		}
		z := (x - req.Baseline.Mean[i]) / req.Baseline.StdDev[i]
		sumSq += z * z
		n++
	}
	if n == 0 {
		return 0.0, nil
	}
	return sumSq / float64(n), nil // Mean squared z-score (not RMS, to match Mahalanobis scale).
}

func (z *ZScoreScorer) UpdateBaseline(_ UpdateRequest) error { return nil }
