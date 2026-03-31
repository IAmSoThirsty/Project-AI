package governance

import (
	"math"
	"testing"
	"time"

	"go.uber.org/zap"
)

func TestConstitutionalKernel_ValidateDecision_Success(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	decision := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   2,
		Severity:  5.5,
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs: map[string]interface{}{
			"anomaly_score":  0.7,
			"quorum_signal":  0.5,
			"pressure_score": 0.6,
		},
	}

	err := ck.ValidateDecision(decision)
	if err != nil {
		t.Fatalf("Expected no error, got: %v", err)
	}

	if decision.DecisionHash == "" {
		t.Error("Expected decision hash to be set")
	}

	if !decision.ConstitutionalOK {
		t.Error("Expected constitutional_ok to be true")
	}

	stats := ck.GetStats()
	if stats.DecisionsVerified != 1 {
		t.Errorf("Expected 1 decision verified, got %d", stats.DecisionsVerified)
	}
}

func TestConstitutionalKernel_ValidateDecision_SeverityOutOfBounds(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	decision := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   2,
		Severity:  15.0, // Out of bounds (max is 10.0)
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs:    map[string]interface{}{"anomaly_score": 0.5},
	}

	err := ck.ValidateDecision(decision)
	if err == nil {
		t.Fatal("Expected error for out-of-bounds severity")
	}

	violation, ok := err.(*ConstitutionalViolation)
	if !ok {
		t.Fatalf("Expected ConstitutionalViolation, got %T", err)
	}

	if violation.Type != ViolationUnboundedParameter {
		t.Errorf("Expected ViolationUnboundedParameter, got %s", violation.Type)
	}

	stats := ck.GetStats()
	if stats.ViolationCount != 1 {
		t.Errorf("Expected 1 violation, got %d", stats.ViolationCount)
	}
}

func TestConstitutionalKernel_ValidateDecision_StateOutOfBounds(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	decision := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   10, // Out of bounds (max is 5)
		Severity:  5.0,
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs:    map[string]interface{}{"anomaly_score": 0.5},
	}

	err := ck.ValidateDecision(decision)
	if err == nil {
		t.Fatal("Expected error for out-of-bounds state")
	}

	violation, ok := err.(*ConstitutionalViolation)
	if !ok {
		t.Fatalf("Expected ConstitutionalViolation, got %T", err)
	}

	if violation.Type != ViolationUnboundedParameter {
		t.Errorf("Expected ViolationUnboundedParameter, got %s", violation.Type)
	}
}

func TestConstitutionalKernel_ValidateDecision_NaNSeverity(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	decision := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   2,
		Severity:  math.NaN(),
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs:    map[string]interface{}{"anomaly_score": 0.5},
	}

	err := ck.ValidateDecision(decision)
	if err == nil {
		t.Fatal("Expected error for NaN severity")
	}

	violation, ok := err.(*ConstitutionalViolation)
	if !ok {
		t.Fatalf("Expected ConstitutionalViolation, got %T", err)
	}

	if violation.Type != ViolationNaNInf {
		t.Errorf("Expected ViolationNaNInf, got %s", violation.Type)
	}
}

func TestConstitutionalKernel_ValidateDecision_InfSeverity(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	decision := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   2,
		Severity:  math.Inf(1),
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs:    map[string]interface{}{"anomaly_score": 0.5},
	}

	err := ck.ValidateDecision(decision)
	if err == nil {
		t.Fatal("Expected error for Inf severity")
	}

	violation, ok := err.(*ConstitutionalViolation)
	if !ok {
		t.Fatalf("Expected ConstitutionalViolation, got %T", err)
	}

	if violation.Type != ViolationNaNInf {
		t.Errorf("Expected ViolationNaNInf, got %s", violation.Type)
	}
}

func TestConstitutionalKernel_ValidateDecision_MissingInputs(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	decision := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   2,
		Severity:  5.0,
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs:    nil, // Missing inputs
	}

	err := ck.ValidateDecision(decision)
	if err == nil {
		t.Fatal("Expected error for missing inputs")
	}

	violation, ok := err.(*ConstitutionalViolation)
	if !ok {
		t.Fatalf("Expected ConstitutionalViolation, got %T", err)
	}

	if violation.Type != ViolationMissingAudit {
		t.Errorf("Expected ViolationMissingAudit, got %s", violation.Type)
	}
}

func TestConstitutionalKernel_ValidateDecision_NonMonotonicTime(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	// First decision
	decision1 := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   1,
		Severity:  3.0,
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs:    map[string]interface{}{"anomaly_score": 0.5},
	}

	err := ck.ValidateDecision(decision1)
	if err != nil {
		t.Fatalf("First decision failed: %v", err)
	}

	// Second decision with earlier timestamp
	decision2 := &EscalationDecision{
		PID:       12346,
		FromState: 0,
		ToState:   1,
		Severity:  3.0,
		Timestamp: time.Now().Add(-1 * time.Hour), // Time went backwards
		NodeID:    "test-node",
		Inputs:    map[string]interface{}{"anomaly_score": 0.5},
	}

	err = ck.ValidateDecision(decision2)
	if err == nil {
		t.Fatal("Expected error for non-monotonic time")
	}

	violation, ok := err.(*ConstitutionalViolation)
	if !ok {
		t.Fatalf("Expected ConstitutionalViolation, got %T", err)
	}

	if violation.Type != ViolationNonMonotonicTime {
		t.Errorf("Expected ViolationNonMonotonicTime, got %s", violation.Type)
	}
}

func TestConstitutionalKernel_ValidateDecision_AnomalyScoreOutOfBounds(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	decision := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   2,
		Severity:  5.0,
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs: map[string]interface{}{
			"anomaly_score": 1.5, // Out of bounds (max is 1.0)
		},
	}

	err := ck.ValidateDecision(decision)
	if err == nil {
		t.Fatal("Expected error for out-of-bounds anomaly score")
	}

	violation, ok := err.(*ConstitutionalViolation)
	if !ok {
		t.Fatalf("Expected ConstitutionalViolation, got %T", err)
	}

	if violation.Type != ViolationUnboundedParameter {
		t.Errorf("Expected ViolationUnboundedParameter, got %s", violation.Type)
	}
}

func TestConstitutionalKernel_ValidateDecision_QuorumSignalNaN(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	decision := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   2,
		Severity:  5.0,
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs: map[string]interface{}{
			"anomaly_score": 0.5,
			"quorum_signal": math.NaN(),
		},
	}

	err := ck.ValidateDecision(decision)
	if err == nil {
		t.Fatal("Expected error for NaN quorum signal")
	}

	violation, ok := err.(*ConstitutionalViolation)
	if !ok {
		t.Fatalf("Expected ConstitutionalViolation, got %T", err)
	}

	if violation.Type != ViolationNaNInf {
		t.Errorf("Expected ViolationNaNInf, got %s", violation.Type)
	}
}

func TestConstitutionalKernel_ValidateDecision_PressureScoreInf(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	decision := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   2,
		Severity:  5.0,
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs: map[string]interface{}{
			"anomaly_score":  0.5,
			"pressure_score": math.Inf(-1),
		},
	}

	err := ck.ValidateDecision(decision)
	if err == nil {
		t.Fatal("Expected error for Inf pressure score")
	}

	violation, ok := err.(*ConstitutionalViolation)
	if !ok {
		t.Fatalf("Expected ConstitutionalViolation, got %T", err)
	}

	if violation.Type != ViolationNaNInf {
		t.Errorf("Expected ViolationNaNInf, got %s", violation.Type)
	}
}

func TestConstitutionalKernel_ValidateDecision_MerkleChain(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	// First decision
	decision1 := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   1,
		Severity:  3.0,
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs:    map[string]interface{}{"anomaly_score": 0.5},
	}

	err := ck.ValidateDecision(decision1)
	if err != nil {
		t.Fatalf("First decision failed: %v", err)
	}

	if decision1.DecisionHash == "" {
		t.Error("First decision hash should be set")
	}

	if decision1.ParentHash != "" {
		t.Error("First decision should have empty parent hash")
	}

	hash1 := decision1.DecisionHash

	// Second decision
	decision2 := &EscalationDecision{
		PID:       12346,
		FromState: 0,
		ToState:   2,
		Severity:  4.5,
		Timestamp: time.Now().Add(1 * time.Second),
		NodeID:    "test-node",
		Inputs:    map[string]interface{}{"anomaly_score": 0.7},
	}

	err = ck.ValidateDecision(decision2)
	if err != nil {
		t.Fatalf("Second decision failed: %v", err)
	}

	if decision2.ParentHash != hash1 {
		t.Errorf("Second decision parent hash should be %s, got %s", hash1, decision2.ParentHash)
	}

	if decision2.DecisionHash == "" {
		t.Error("Second decision hash should be set")
	}

	if decision2.DecisionHash == hash1 {
		t.Error("Second decision hash should differ from first")
	}
}

func TestConstitutionalKernel_GetStats(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, false)

	stats := ck.GetStats()
	if stats.DecisionsVerified != 0 {
		t.Errorf("Expected 0 decisions verified, got %d", stats.DecisionsVerified)
	}

	if stats.ViolationCount != 0 {
		t.Errorf("Expected 0 violations, got %d", stats.ViolationCount)
	}

	// Add a valid decision
	decision := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   1,
		Severity:  3.0,
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs:    map[string]interface{}{"anomaly_score": 0.5},
	}

	ck.ValidateDecision(decision)

	stats = ck.GetStats()
	if stats.DecisionsVerified != 1 {
		t.Errorf("Expected 1 decision verified, got %d", stats.DecisionsVerified)
	}

	if stats.LastDecisionHash == "" {
		t.Error("Expected last decision hash to be set")
	}

	// Add an invalid decision
	badDecision := &EscalationDecision{
		PID:       12346,
		FromState: 0,
		ToState:   1,
		Severity:  math.NaN(),
		Timestamp: time.Now().Add(1 * time.Second),
		NodeID:    "test-node",
		Inputs:    map[string]interface{}{"anomaly_score": 0.5},
	}

	ck.ValidateDecision(badDecision)

	stats = ck.GetStats()
	if stats.ViolationCount != 1 {
		t.Errorf("Expected 1 violation, got %d", stats.ViolationCount)
	}

	// Verified count should not increase for invalid decision
	if stats.DecisionsVerified != 1 {
		t.Errorf("Expected still 1 decision verified, got %d", stats.DecisionsVerified)
	}
}

func TestConstitutionalKernel_StrictMode(t *testing.T) {
	logger := zap.NewNop()
	ck := NewConstitutionalKernel(logger, true) // strict = true

	decision := &EscalationDecision{
		PID:       12345,
		FromState: 0,
		ToState:   2,
		Severity:  15.0, // Out of bounds
		Timestamp: time.Now(),
		NodeID:    "test-node",
		Inputs:    map[string]interface{}{"anomaly_score": 0.5},
	}

	defer func() {
		if r := recover(); r == nil {
			t.Error("Expected panic in strict mode, but no panic occurred")
		}
	}()

	ck.ValidateDecision(decision)
}
