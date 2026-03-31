// Package anomaly — engine_test.go
//
// Unit tests for the Mahalanobis anomaly engine.
//
// Test coverage:
//   - Score() with known baseline (expected Mahalanobis distance)
//   - Score() with nil baseline (returns 0.0)
//   - Score() with dimension mismatch (returns error)
//   - Score() with singular covariance (Euclidean fallback)
//   - InvertCovariance() with identity matrix (inverse = identity)
//   - InvertCovariance() with singular matrix (returns nil)
//   - ShannonEntropy() with uniform distribution (H = log₂(k))
//   - ShannonEntropy() with degenerate distribution (H = 0)
//   - ShannonEntropy() with empty counts (H = 0)
//   - EWMA Accumulator: Update(), Value(), Reset()
//   - Severity computation: ComputeSeverity(), TargetState()
//   - Budget: Consume(), ConsumeForState(), Remaining()
//   - Quorum: Record(), Signal(), TTL expiry

package anomaly_test

import (
	"math"
	"testing"
	"time"

	"github.com/octoreflex/octoreflex/internal/anomaly"
	"github.com/octoreflex/octoreflex/internal/budget"
	"github.com/octoreflex/octoreflex/internal/escalation"
	"github.com/octoreflex/octoreflex/internal/gossip"
)

// ─── Anomaly Engine Tests ─────────────────────────────────────────────────────

func TestScore_NilBaseline(t *testing.T) {
	eng := anomaly.NewEngine(0.3)
	score, err := eng.Score([]float64{1.0, 2.0}, nil, 0.5)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if score != 0.0 {
		t.Errorf("expected 0.0 for nil baseline, got %f", score)
	}
}

func TestScore_DimensionMismatch(t *testing.T) {
	eng := anomaly.NewEngine(0.3)
	baseline := &anomaly.Baseline{
		MeanVector: []float64{0.0, 0.0},
	}
	_, err := eng.Score([]float64{1.0}, baseline, 0.0)
	if err == nil {
		t.Fatal("expected error for dimension mismatch, got nil")
	}
}

func TestScore_IdentityCovariance(t *testing.T) {
	// With Σ = I (identity), Mahalanobis = Euclidean.
	// x = [1, 0], μ = [0, 0] → distance² = 1.0
	// entropy delta = 0.0, wₑ = 0.0 → A = 1.0
	eng := anomaly.NewEngine(0.0) // wₑ = 0 to isolate Mahalanobis

	identity := [][]float64{{1, 0}, {0, 1}}
	inv := anomaly.InvertCovariance(identity)
	if inv == nil {
		t.Fatal("InvertCovariance(identity) returned nil")
	}

	baseline := &anomaly.Baseline{
		MeanVector:       []float64{0.0, 0.0},
		CovarianceMatrix: identity,
		InvCovariance:    inv,
		BaselineEntropy:  0.0,
	}

	score, err := eng.Score([]float64{1.0, 0.0}, baseline, 0.0)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if math.Abs(score-1.0) > 1e-9 {
		t.Errorf("expected score=1.0, got %f", score)
	}
}

func TestScore_SingularCovariance_EuclideanFallback(t *testing.T) {
	// Singular matrix → InvertCovariance returns nil → Euclidean fallback.
	singular := [][]float64{{1, 1}, {1, 1}} // rank 1, not invertible
	inv := anomaly.InvertCovariance(singular)
	if inv != nil {
		t.Fatal("expected nil for singular matrix, got non-nil")
	}

	eng := anomaly.NewEngine(0.0)
	baseline := &anomaly.Baseline{
		MeanVector:      []float64{0.0, 0.0},
		InvCovariance:   nil, // Singular — Euclidean fallback.
		BaselineEntropy: 0.0,
	}

	// x = [3, 4], μ = [0, 0] → Euclidean² = 9 + 16 = 25
	score, err := eng.Score([]float64{3.0, 4.0}, baseline, 0.0)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if math.Abs(score-25.0) > 1e-9 {
		t.Errorf("expected score=25.0 (Euclidean fallback), got %f", score)
	}
}

func TestScore_EntropyDelta(t *testing.T) {
	// Test that entropy weight contributes correctly.
	// wₑ = 1.0, |ΔH| = 1.0 → entropy contribution = 1.0
	// Mahalanobis = 0 (x = μ) → total score = 1.0
	eng := anomaly.NewEngine(1.0)
	identity := [][]float64{{1, 0}, {0, 1}}
	inv := anomaly.InvertCovariance(identity)

	baseline := &anomaly.Baseline{
		MeanVector:      []float64{1.0, 1.0},
		InvCovariance:   inv,
		BaselineEntropy: 0.5,
	}

	// x = μ → Mahalanobis = 0. currentH = 1.5 → |ΔH| = 1.0
	score, err := eng.Score([]float64{1.0, 1.0}, baseline, 1.5)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if math.Abs(score-1.0) > 1e-9 {
		t.Errorf("expected score=1.0, got %f", score)
	}
}

// ─── Entropy Tests ────────────────────────────────────────────────────────────

func TestShannonEntropy_Empty(t *testing.T) {
	var counts anomaly.EventCounts
	H := anomaly.ShannonEntropy(counts)
	if H != 0.0 {
		t.Errorf("expected H=0.0 for empty counts, got %f", H)
	}
}

func TestShannonEntropy_Uniform(t *testing.T) {
	// 3 event types, equal counts → H = log₂(3) ≈ 1.585
	counts := anomaly.EventCounts{0, 10, 10, 10}
	H := anomaly.ShannonEntropy(counts)
	expected := math.Log2(3)
	if math.Abs(H-expected) > 1e-9 {
		t.Errorf("expected H=%.6f, got %.6f", expected, H)
	}
}

func TestShannonEntropy_Degenerate(t *testing.T) {
	// Only one event type → H = 0
	counts := anomaly.EventCounts{0, 100, 0, 0}
	H := anomaly.ShannonEntropy(counts)
	if H != 0.0 {
		t.Errorf("expected H=0.0 for degenerate distribution, got %f", H)
	}
}

// ─── EWMA Accumulator Tests ───────────────────────────────────────────────────

func TestAccumulator_Update(t *testing.T) {
	// α=0.8, start at 0.
	// After one update with A=10: P = 0.8*0 + 0.2*10 = 2.0
	acc := escalation.NewAccumulator(0.8)
	p := acc.Update(10.0)
	if math.Abs(p-2.0) > 1e-9 {
		t.Errorf("expected P=2.0, got %f", p)
	}
}

func TestAccumulator_Reset(t *testing.T) {
	acc := escalation.NewAccumulator(0.8)
	acc.Update(100.0)
	acc.Reset()
	if acc.Value() != 0.0 {
		t.Errorf("expected 0.0 after Reset, got %f", acc.Value())
	}
}

func TestAccumulator_InvalidAlpha(t *testing.T) {
	defer func() {
		if r := recover(); r == nil {
			t.Error("expected panic for alpha > 1.0")
		}
	}()
	escalation.NewAccumulator(1.5)
}

// ─── Severity Tests ───────────────────────────────────────────────────────────

func TestComputeSeverity(t *testing.T) {
	weights := escalation.DefaultWeights()
	inputs := escalation.Inputs{
		AnomalyScore:   5.0,
		QuorumSignal:   1.0,
		IntegrityScore: 0.5,
		PressureScore:  2.0,
	}
	// S = 0.4*5 + 0.2*1 + 0.2*0.5 + 0.2*2 = 2.0 + 0.2 + 0.1 + 0.4 = 2.7
	expected := 2.7
	got := escalation.ComputeSeverity(inputs, weights)
	if math.Abs(got-expected) > 1e-9 {
		t.Errorf("expected S=%.4f, got %.4f", expected, got)
	}
}

func TestTargetState(t *testing.T) {
	thresholds := escalation.DefaultThresholds()
	tests := []struct {
		severity float64
		expected escalation.State
	}{
		{0.5, escalation.StateNormal},
		{1.0, escalation.StatePressure},
		{3.0, escalation.StateIsolated},
		{6.0, escalation.StateFrozen},
		{9.0, escalation.StateQuarantined},
		{12.0, escalation.StateTerminated},
		{100.0, escalation.StateTerminated},
	}
	for _, tt := range tests {
		got := escalation.TargetState(tt.severity, thresholds)
		if got != tt.expected {
			t.Errorf("severity=%.1f: expected %s, got %s", tt.severity, tt.expected, got)
		}
	}
}

// ─── Budget Tests ─────────────────────────────────────────────────────────────

func TestBucket_Consume(t *testing.T) {
	b := budget.New(100, 60*time.Second)
	defer b.Close()

	if !b.Consume(10) {
		t.Error("expected Consume(10) to succeed with 100 tokens")
	}
	if b.Remaining() != 90 {
		t.Errorf("expected 90 remaining, got %d", b.Remaining())
	}
}

func TestBucket_Overdraft(t *testing.T) {
	b := budget.New(10, 60*time.Second)
	defer b.Close()

	if b.Consume(11) {
		t.Error("expected Consume(11) to fail with only 10 tokens")
	}
	if b.Remaining() != 10 {
		t.Errorf("expected 10 remaining after failed consume, got %d", b.Remaining())
	}
}

func TestBucket_ConsumeForState(t *testing.T) {
	b := budget.New(100, 60*time.Second)
	defer b.Close()

	// TERMINATED costs 50.
	if !b.ConsumeForState(escalation.StateTerminated) {
		t.Error("expected ConsumeForState(TERMINATED) to succeed")
	}
	if b.Remaining() != 50 {
		t.Errorf("expected 50 remaining after TERMINATED cost, got %d", b.Remaining())
	}
}

// ─── Quorum Tests ─────────────────────────────────────────────────────────────

func TestQuorum_Signal_BelowMin(t *testing.T) {
	q := gossip.NewQuorum(2, 30*time.Second)
	q.Record("hash1", "node1", 5.0)
	// Only 1 node — below quorum_min=2.
	if q.Signal("hash1") != 0.0 {
		t.Error("expected quorum signal 0.0 with only 1 node")
	}
}

func TestQuorum_Signal_AtMin(t *testing.T) {
	q := gossip.NewQuorum(2, 30*time.Second)
	q.Record("hash1", "node1", 5.0)
	q.Record("hash1", "node2", 4.0)
	// 2 nodes — meets quorum_min=2.
	if q.Signal("hash1") != 1.0 {
		t.Error("expected quorum signal 1.0 with 2 nodes")
	}
}

func TestQuorum_Signal_Deduplication(t *testing.T) {
	q := gossip.NewQuorum(2, 30*time.Second)
	// Same node reporting twice — should count as 1 unique node.
	q.Record("hash1", "node1", 5.0)
	q.Record("hash1", "node1", 6.0)
	if q.Signal("hash1") != 0.0 {
		t.Error("expected quorum signal 0.0 — same node counted twice")
	}
}

func TestQuorum_Signal_UnknownHash(t *testing.T) {
	q := gossip.NewQuorum(2, 30*time.Second)
	if q.Signal("nonexistent") != 0.0 {
		t.Error("expected quorum signal 0.0 for unknown process hash")
	}
}

// ─── State Machine Tests ──────────────────────────────────────────────────────

func TestProcessState_Escalate(t *testing.T) {
	ps := escalation.NewProcessState(1234)
	if ps.Current() != escalation.StateNormal {
		t.Error("expected initial state NORMAL")
	}

	newState, ok := ps.Escalate(escalation.StateIsolated)
	if !ok {
		t.Error("expected escalation to succeed")
	}
	if newState != escalation.StateIsolated {
		t.Errorf("expected ISOLATED, got %s", newState)
	}
}

func TestProcessState_EscalateNoDowngrade(t *testing.T) {
	ps := escalation.NewProcessState(1234)
	ps.Escalate(escalation.StateFrozen)

	// Attempt to escalate to a lower state — should be a no-op.
	_, ok := ps.Escalate(escalation.StatePressure)
	if ok {
		t.Error("expected escalation to lower state to fail")
	}
	if ps.Current() != escalation.StateFrozen {
		t.Errorf("expected state to remain FROZEN, got %s", ps.Current())
	}
}

func TestProcessState_Decay(t *testing.T) {
	ps := escalation.NewProcessState(1234)
	ps.Escalate(escalation.StateIsolated)

	newState, ok := ps.Decay()
	if !ok {
		t.Error("expected decay to succeed")
	}
	if newState != escalation.StatePressure {
		t.Errorf("expected PRESSURE after decay from ISOLATED, got %s", newState)
	}
}

func TestProcessState_TerminatedNoDecay(t *testing.T) {
	ps := escalation.NewProcessState(1234)
	ps.Escalate(escalation.StateTerminated)

	_, ok := ps.Decay()
	if ok {
		t.Error("expected decay from TERMINATED to fail (terminal state)")
	}
}
