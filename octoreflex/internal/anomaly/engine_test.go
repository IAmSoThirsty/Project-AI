// Package anomaly — engine_test.go
//
// Unit tests for the anomaly detection engine.
// Target: 90%+ coverage.

package anomaly

import (
	"math"
	"testing"
)

func TestNewEngine(t *testing.T) {
	tests := []struct {
		name          string
		entropyWeight float64
		want          float64
	}{
		{"zero weight", 0.0, 0.0},
		{"half weight", 0.5, 0.5},
		{"full weight", 1.0, 1.0},
		{"default weight", 0.3, 0.3},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			eng := NewEngine(tt.entropyWeight)
			if eng.entropyWeight != tt.want {
				t.Errorf("NewEngine(%v) = %v, want %v", tt.entropyWeight, eng.entropyWeight, tt.want)
			}
		})
	}
}

func TestEngine_Score_NilBaseline(t *testing.T) {
	eng := NewEngine(0.3)
	x := []float64{1.0, 2.0, 3.0}
	
	score, err := eng.Score(x, nil, 0.5)
	if err != nil {
		t.Fatalf("Score with nil baseline returned error: %v", err)
	}
	if score != 0.0 {
		t.Errorf("Score with nil baseline = %v, want 0.0", score)
	}
}

func TestEngine_Score_DimensionMismatch(t *testing.T) {
	eng := NewEngine(0.3)
	baseline := &Baseline{
		MeanVector: []float64{1.0, 2.0, 3.0},
		CovarianceMatrix: [][]float64{
			{1.0, 0.0, 0.0},
			{0.0, 1.0, 0.0},
			{0.0, 0.0, 1.0},
		},
		BaselineEntropy: 0.5,
	}
	
	// Feature vector with wrong dimension
	x := []float64{1.0, 2.0}
	
	_, err := eng.Score(x, baseline, 0.5)
	if err == nil {
		t.Fatal("Expected dimension mismatch error, got nil")
	}
}

func TestEngine_Score_WithInvCovariance(t *testing.T) {
	eng := NewEngine(0.3)
	
	// Identity covariance → Mahalanobis = Euclidean
	baseline := &Baseline{
		MeanVector: []float64{0.0, 0.0, 0.0},
		CovarianceMatrix: [][]float64{
			{1.0, 0.0, 0.0},
			{0.0, 1.0, 0.0},
			{0.0, 0.0, 1.0},
		},
		InvCovariance: [][]float64{
			{1.0, 0.0, 0.0},
			{0.0, 1.0, 0.0},
			{0.0, 0.0, 1.0},
		},
		BaselineEntropy: 1.0,
	}
	
	x := []float64{1.0, 0.0, 0.0}
	currentEntropy := 1.5
	
	score, err := eng.Score(x, baseline, currentEntropy)
	if err != nil {
		t.Fatalf("Score returned error: %v", err)
	}
	
	// Expected: mahal = 1.0^2 = 1.0, entropy delta = |1.5 - 1.0| = 0.5
	// Score = 1.0 + 0.3*0.5 = 1.15
	expected := 1.15
	if math.Abs(score-expected) > 1e-9 {
		t.Errorf("Score = %v, want %v", score, expected)
	}
}

func TestEngine_Score_SingularCovariance(t *testing.T) {
	eng := NewEngine(0.3)
	
	// Singular covariance (InvCovariance = nil) → fallback to Euclidean
	baseline := &Baseline{
		MeanVector:       []float64{0.0, 0.0, 0.0},
		CovarianceMatrix: [][]float64{{0, 0, 0}, {0, 0, 0}, {0, 0, 0}},
		InvCovariance:    nil,
		BaselineEntropy:  1.0,
	}
	
	x := []float64{3.0, 4.0, 0.0}
	currentEntropy := 1.2
	
	score, err := eng.Score(x, baseline, currentEntropy)
	if err != nil {
		t.Fatalf("Score returned error: %v", err)
	}
	
	// Euclidean^2 = 3^2 + 4^2 + 0^2 = 25
	// Entropy delta = |1.2 - 1.0| = 0.2
	// Score = 25 + 0.3*0.2 = 25.06
	expected := 25.06
	if math.Abs(score-expected) > 1e-9 {
		t.Errorf("Score = %v, want %v", score, expected)
	}
}

func TestEngine_Score_ZeroEntropy(t *testing.T) {
	eng := NewEngine(0.0) // zero entropy weight
	
	baseline := &Baseline{
		MeanVector: []float64{1.0, 1.0, 1.0},
		InvCovariance: [][]float64{
			{1.0, 0.0, 0.0},
			{0.0, 1.0, 0.0},
			{0.0, 0.0, 1.0},
		},
		BaselineEntropy: 1.5,
	}
	
	x := []float64{2.0, 2.0, 2.0}
	
	score, err := eng.Score(x, baseline, 5.0)
	if err != nil {
		t.Fatalf("Score returned error: %v", err)
	}
	
	// Mahalanobis^2 = (1^2 + 1^2 + 1^2) = 3.0
	// Entropy contribution = 0 (weight is 0)
	expected := 3.0
	if math.Abs(score-expected) > 1e-9 {
		t.Errorf("Score = %v, want %v", score, expected)
	}
}

func TestEuclideanSquared(t *testing.T) {
	tests := []struct {
		name string
		x    []float64
		mu   []float64
		want float64
	}{
		{
			name: "zero distance",
			x:    []float64{1.0, 2.0, 3.0},
			mu:   []float64{1.0, 2.0, 3.0},
			want: 0.0,
		},
		{
			name: "unit distance",
			x:    []float64{1.0, 0.0, 0.0},
			mu:   []float64{0.0, 0.0, 0.0},
			want: 1.0,
		},
		{
			name: "pythagorean triple",
			x:    []float64{3.0, 4.0},
			mu:   []float64{0.0, 0.0},
			want: 25.0,
		},
		{
			name: "negative values",
			x:    []float64{-1.0, -2.0},
			mu:   []float64{1.0, 2.0},
			want: 20.0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := euclideanSquared(tt.x, tt.mu)
			if math.Abs(got-tt.want) > 1e-9 {
				t.Errorf("euclideanSquared(%v, %v) = %v, want %v", tt.x, tt.mu, got, tt.want)
			}
		})
	}
}

func BenchmarkEngine_Score(b *testing.B) {
	eng := NewEngine(0.3)
	baseline := &Baseline{
		MeanVector: []float64{1.0, 2.0, 3.0},
		InvCovariance: [][]float64{
			{1.0, 0.0, 0.0},
			{0.0, 1.0, 0.0},
			{0.0, 0.0, 1.0},
		},
		BaselineEntropy: 1.0,
	}
	x := []float64{1.5, 2.5, 3.5}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = eng.Score(x, baseline, 1.2)
	}
}

func BenchmarkEngine_Score_SingularFallback(b *testing.B) {
	eng := NewEngine(0.3)
	baseline := &Baseline{
		MeanVector:      []float64{1.0, 2.0, 3.0},
		InvCovariance:   nil,
		BaselineEntropy: 1.0,
	}
	x := []float64{1.5, 2.5, 3.5}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = eng.Score(x, baseline, 1.2)
	}
}
