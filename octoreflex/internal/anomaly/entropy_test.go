// Package anomaly — entropy_test.go
//
// Unit tests for Shannon entropy computation.
// Target: 100% coverage.

package anomaly

import (
	"math"
	"testing"
)

func TestShannonEntropy_ZeroCounts(t *testing.T) {
	counts := EventCounts{0, 0, 0, 0}
	got := ShannonEntropy(counts)
	if got != 0.0 {
		t.Errorf("ShannonEntropy([0,0,0,0]) = %v, want 0.0", got)
	}
}

func TestShannonEntropy_SingleType(t *testing.T) {
	// All events of one type → minimum entropy (0.0)
	counts := EventCounts{0, 100, 0, 0}
	got := ShannonEntropy(counts)
	if got != 0.0 {
		t.Errorf("ShannonEntropy([0,100,0,0]) = %v, want 0.0", got)
	}
}

func TestShannonEntropy_UniformDistribution(t *testing.T) {
	// Uniform distribution over 3 types → max entropy = log₂(3)
	counts := EventCounts{0, 10, 10, 10}
	got := ShannonEntropy(counts)
	
	// For k=3 types with equal probability: H = log₂(3) ≈ 1.585
	expected := math.Log2(3)
	if math.Abs(got-expected) > 1e-9 {
		t.Errorf("ShannonEntropy([0,10,10,10]) = %v, want %v", got, expected)
	}
}

func TestShannonEntropy_NonUniform(t *testing.T) {
	// p1=0.5, p2=0.25, p3=0.25
	// H = -0.5*log2(0.5) - 0.25*log2(0.25) - 0.25*log2(0.25)
	//   = 0.5 + 0.5 + 0.5 = 1.5 bits
	counts := EventCounts{0, 100, 50, 50}
	got := ShannonEntropy(counts)
	
	expected := 1.5
	if math.Abs(got-expected) > 1e-9 {
		t.Errorf("ShannonEntropy([0,100,50,50]) = %v, want %v", got, expected)
	}
}

func TestShannonEntropy_TwoTypes(t *testing.T) {
	// p1=0.5, p2=0.5 → H = 1.0 bit (max for binary)
	counts := EventCounts{0, 50, 50, 0}
	got := ShannonEntropy(counts)
	
	expected := 1.0
	if math.Abs(got-expected) > 1e-9 {
		t.Errorf("ShannonEntropy([0,50,50,0]) = %v, want %v", got, expected)
	}
}

func TestMaxEntropy(t *testing.T) {
	tests := []struct {
		name string
		k    int
		want float64
	}{
		{"zero types", 0, 0.0},
		{"one type", 1, 0.0},
		{"two types", 2, 1.0},
		{"three types", 3, math.Log2(3)},
		{"four types", 4, 2.0},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := MaxEntropy(tt.k)
			if math.Abs(got-tt.want) > 1e-9 {
				t.Errorf("MaxEntropy(%d) = %v, want %v", tt.k, got, tt.want)
			}
		})
	}
}

func TestNormalisedEntropy_UniformDistribution(t *testing.T) {
	// Uniform over 3 types → normalised entropy = 1.0
	counts := EventCounts{0, 10, 10, 10}
	got := NormalisedEntropy(counts, 3)
	
	expected := 1.0
	if math.Abs(got-expected) > 1e-9 {
		t.Errorf("NormalisedEntropy([0,10,10,10], 3) = %v, want 1.0", got)
	}
}

func TestNormalisedEntropy_SingleType(t *testing.T) {
	// Single type → normalised entropy = 0.0
	counts := EventCounts{0, 100, 0, 0}
	got := NormalisedEntropy(counts, 3)
	
	if got != 0.0 {
		t.Errorf("NormalisedEntropy([0,100,0,0], 3) = %v, want 0.0", got)
	}
}

func TestNormalisedEntropy_ZeroMaxEntropy(t *testing.T) {
	// Only 1 event type possible → H_max = 0, normalised = 0
	counts := EventCounts{0, 100, 0, 0}
	got := NormalisedEntropy(counts, 1)
	
	if got != 0.0 {
		t.Errorf("NormalisedEntropy([0,100,0,0], 1) = %v, want 0.0", got)
	}
}

func TestNormalisedEntropy_Skewed(t *testing.T) {
	// Skewed distribution: p1=0.8, p2=0.1, p3=0.1
	// H ≈ 0.92, H_max ≈ 1.585, normalised ≈ 0.58
	counts := EventCounts{0, 80, 10, 10}
	got := NormalisedEntropy(counts, 3)
	
	// Compute expected
	h := ShannonEntropy(counts)
	hMax := MaxEntropy(3)
	expected := h / hMax
	
	if math.Abs(got-expected) > 1e-9 {
		t.Errorf("NormalisedEntropy([0,80,10,10], 3) = %v, want %v", got, expected)
	}
}

func BenchmarkShannonEntropy(b *testing.B) {
	counts := EventCounts{0, 123, 456, 789}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = ShannonEntropy(counts)
	}
}

func BenchmarkNormalisedEntropy(b *testing.B) {
	counts := EventCounts{0, 123, 456, 789}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = NormalisedEntropy(counts, 3)
	}
}
