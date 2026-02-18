// Package anomaly — entropy.go
//
// Shannon entropy computation for the OCTOREFLEX anomaly engine.
//
// Entropy is computed over the distribution of event types observed in a
// sliding window. A process with uniform event distribution has high entropy
// (normal behaviour). A process suddenly emitting only one event type
// (e.g., only socket_connect events) has low entropy — a strong anomaly
// signal for exfiltration or C2 beaconing.
//
// Formula:
//   H = -Σ p(eᵢ) * log₂(p(eᵢ))
//
// Where p(eᵢ) is the empirical probability of event type i in the window.
//
// Bounds:
//   H = 0.0  when all events are the same type (minimum entropy).
//   H = log₂(k) when all k event types are equally probable (maximum entropy).
//   For k=3 event types: H_max = log₂(3) ≈ 1.585 bits.
//
// The entropy delta |ΔH| = |H_current - H_baseline| is used in the
// anomaly score formula as an additional signal orthogonal to the
// Mahalanobis distance.

package anomaly

import "math"

// EventCounts holds the count of each event type in a window.
// Index 0 is unused (event types start at 1 per octoreflex.h).
// Index 1 = socket_connect, 2 = file_open, 3 = setuid.
type EventCounts [4]uint64

// ShannonEntropy computes H = -Σ p(eᵢ) * log₂(p(eᵢ)) over the event counts.
//
// Returns 0.0 if the total count is zero (empty window — no information).
// Returns 0.0 if only one event type is present (degenerate distribution).
//
// The result is in bits (base-2 logarithm).
func ShannonEntropy(counts EventCounts) float64 {
	// Compute total events across all types.
	var total uint64
	for _, c := range counts {
		total += c
	}
	if total == 0 {
		return 0.0
	}

	fTotal := float64(total)
	var H float64
	for _, c := range counts {
		if c == 0 {
			continue // 0 * log(0) = 0 by convention.
		}
		p := float64(c) / fTotal
		H -= p * math.Log2(p)
	}
	return H
}

// MaxEntropy returns the maximum possible entropy for k non-zero event types.
// H_max = log₂(k). Used for normalisation if needed.
func MaxEntropy(k int) float64 {
	if k <= 1 {
		return 0.0
	}
	return math.Log2(float64(k))
}

// NormalisedEntropy returns H / H_max, giving a value in [0.0, 1.0].
// Returns 0.0 if H_max is 0 (only one event type possible).
func NormalisedEntropy(counts EventCounts, numTypes int) float64 {
	hMax := MaxEntropy(numTypes)
	if hMax == 0.0 {
		return 0.0
	}
	return ShannonEntropy(counts) / hMax
}
