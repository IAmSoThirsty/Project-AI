// Package governance provides Layer 0 constitutional kernel integration for OCTOREFLEX.
//
// This package bridges OCTOREFLEX's Tier 0 (kernel reflex) with Project-AI's
// Constitutional Kernel, ensuring all containment actions comply with
// Project-AI's foundational axioms.
//
// CONSTITUTIONAL AXIOMS (from Atlas Ω Layer 0):
// 1. Determinism > Interpretation — All escalations must be reproducible
// 2. Probability > Narrative — Decisions based on evidence, not assumptions
// 3. Evidence > Agency — Actions require audit trail
// 4. Isolation > Contamination — Containment must prevent lateral movement
// 5. Reproducibility > Authority — All decisions must be cryptographically verifiable
// 6. Bounded Inputs > Open Chaos — All parameters must be within bounds
// 7. Abort > Drift — Violations trigger immediate halt
//
// SCOPE: These axioms apply to OCTOREFLEX's autonomous containment decisions.
// They do NOT override Project-AI Triumvirate authority or baseline governance.

package governance

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"math"
	"sync"
	"time"

	"go.uber.org/zap"
)

// ViolationType represents constitutional constraint violations.
type ViolationType string

const (
	// ViolationNonDeterministic - Decision cannot be reproduced from inputs
	ViolationNonDeterministic ViolationType = "non_deterministic_decision"

	// ViolationUnboundedParameter - Parameter outside allowed bounds
	ViolationUnboundedParameter ViolationType = "unbounded_parameter"

	// ViolationNonMonotonicTime - Time moved backwards or skewed
	ViolationNonMonotonicTime ViolationType = "non_monotonic_time"

	// ViolationMissingAudit - Action executed without audit trail
	ViolationMissingAudit ViolationType = "missing_audit_trail"

	// ViolationNaNInf - NaN or Inf in numeric computation
	ViolationNaNInf ViolationType = "nan_inf_detected"

	// ViolationHashMismatch - Cryptographic verification failed
	ViolationHashMismatch ViolationType = "hash_mismatch"

	// ViolationStateContamination - Isolation boundary violated
	ViolationStateContamination ViolationType = "state_contamination"
)

// ConstitutionalViolation represents a violation of foundational constraints.
type ConstitutionalViolation struct {
	Type      ViolationType `json:"type"`
	Message   string        `json:"message"`
	Timestamp time.Time     `json:"timestamp"`
	Context   map[string]interface{} `json:"context"`
}

func (v *ConstitutionalViolation) Error() string {
	return fmt.Sprintf("CONSTITUTIONAL VIOLATION [%s]: %s", v.Type, v.Message)
}

// EscalationDecision represents a containment decision with constitutional proof.
type EscalationDecision struct {
	PID              uint32                 `json:"pid"`
	FromState        uint8                  `json:"from_state"`
	ToState          uint8                  `json:"to_state"`
	Severity         float64                `json:"severity"`
	Timestamp        time.Time              `json:"timestamp"`
	NodeID           string                 `json:"node_id"`
	Inputs           map[string]interface{} `json:"inputs"`
	DecisionHash     string                 `json:"decision_hash"`     // SHA256 of canonical inputs
	ParentHash       string                 `json:"parent_hash"`       // Hash of previous decision (Merkle chain)
	ConstitutionalOK bool                   `json:"constitutional_ok"` // Passed all checks
}

// ParameterBounds defines allowed ranges for OCTOREFLEX parameters.
type ParameterBounds struct {
	// Severity must be in [0, 10]
	SeverityMin float64
	SeverityMax float64

	// Anomaly score must be in [0, 1]
	AnomalyMin float64
	AnomalyMax float64

	// Quorum signal must be in [0, 1]
	QuorumMin float64
	QuorumMax float64

	// Pressure must be in [0, 1]
	PressureMin float64
	PressureMax float64

	// State values must be in [0, 5] (NORMAL to TERMINATED)
	StateMin uint8
	StateMax uint8

	// Timestamp skew tolerance (5 seconds)
	TimestampSkewTolerance time.Duration
}

// DefaultBounds returns production-grade parameter bounds.
func DefaultBounds() ParameterBounds {
	return ParameterBounds{
		SeverityMin:            0.0,
		SeverityMax:            10.0,
		AnomalyMin:             0.0,
		AnomalyMax:             1.0,
		QuorumMin:              0.0,
		QuorumMax:              1.0,
		PressureMin:            0.0,
		PressureMax:            1.0,
		StateMin:               0,
		StateMax:               5,
		TimestampSkewTolerance: 5 * time.Second,
	}
}

// ConstitutionalKernel enforces foundational constraints on all OCTOREFLEX actions.
type ConstitutionalKernel struct {
	mu                sync.RWMutex
	bounds            ParameterBounds
	lastTimestamp     time.Time
	lastDecisionHash  string
	violationCount    int64
	decisionsVerified int64
	logger            *zap.Logger
	strict            bool // If true, violations trigger panic (test mode only)
}

// NewConstitutionalKernel creates a new kernel with default bounds.
func NewConstitutionalKernel(logger *zap.Logger, strict bool) *ConstitutionalKernel {
	ck := &ConstitutionalKernel{
		bounds:         DefaultBounds(),
		lastTimestamp:  time.Now(),
		logger:         logger,
		strict:         strict,
	}

	logger.Info("ConstitutionalKernel initialized",
		zap.Bool("strict_mode", strict),
		zap.Float64("severity_max", ck.bounds.SeverityMax),
		zap.Duration("time_skew_tolerance", ck.bounds.TimestampSkewTolerance),
	)

	return ck
}

// ValidateDecision enforces constitutional constraints on an escalation decision.
// Returns the decision with cryptographic hash and parent hash set, or an error
// if any constraint is violated.
func (ck *ConstitutionalKernel) ValidateDecision(decision *EscalationDecision) error {
	ck.mu.Lock()
	defer ck.mu.Unlock()

	// Axiom 7: Abort > Drift — Check timestamp monotonicity
	if err := ck.checkTimeMonotonicity(decision.Timestamp); err != nil {
		return ck.handleViolation(err)
	}

	// Axiom 6: Bounded Inputs > Open Chaos — Validate all parameters
	if err := ck.checkParameterBounds(decision); err != nil {
		return ck.handleViolation(err)
	}

	// Axiom 6: Check for NaN/Inf in severity
	if math.IsNaN(decision.Severity) || math.IsInf(decision.Severity, 0) {
		err := &ConstitutionalViolation{
			Type:      ViolationNaNInf,
			Message:   fmt.Sprintf("Severity is NaN or Inf: %f", decision.Severity),
			Timestamp: time.Now(),
			Context:   map[string]interface{}{"pid": decision.PID},
		}
		return ck.handleViolation(err)
	}

	// Axiom 3: Evidence > Agency — Ensure audit trail exists
	if decision.Inputs == nil || len(decision.Inputs) == 0 {
		err := &ConstitutionalViolation{
			Type:      ViolationMissingAudit,
			Message:   "Decision inputs not recorded",
			Timestamp: time.Now(),
			Context:   map[string]interface{}{"pid": decision.PID},
		}
		return ck.handleViolation(err)
	}

	// Axiom 1: Determinism > Interpretation — Compute canonical hash
	decisionHash, err := ck.computeDecisionHash(decision)
	if err != nil {
		return fmt.Errorf("failed to compute decision hash: %w", err)
	}
	decision.DecisionHash = decisionHash

	// Axiom 5: Reproducibility > Authority — Link to parent (Merkle chain)
	decision.ParentHash = ck.lastDecisionHash
	ck.lastDecisionHash = decisionHash

	// Update state
	ck.lastTimestamp = decision.Timestamp
	ck.decisionsVerified++
	decision.ConstitutionalOK = true

	ck.logger.Debug("Decision validated",
		zap.Uint32("pid", decision.PID),
		zap.Uint8("to_state", decision.ToState),
		zap.String("hash", decisionHash[:16]),
		zap.Int64("verified_count", ck.decisionsVerified),
	)

	return nil
}

// checkTimeMonotonicity enforces Axiom 7: time must move forward.
func (ck *ConstitutionalKernel) checkTimeMonotonicity(ts time.Time) error {
	if ts.Before(ck.lastTimestamp) {
		return &ConstitutionalViolation{
			Type:      ViolationNonMonotonicTime,
			Message:   fmt.Sprintf("Time went backwards: %v < %v", ts, ck.lastTimestamp),
			Timestamp: time.Now(),
			Context: map[string]interface{}{
				"current":  ts.Format(time.RFC3339Nano),
				"previous": ck.lastTimestamp.Format(time.RFC3339Nano),
			},
		}
	}

	// Check for unreasonable forward skew
	skew := ts.Sub(ck.lastTimestamp)
	if skew > ck.bounds.TimestampSkewTolerance {
		ck.logger.Warn("Large timestamp skew detected",
			zap.Duration("skew", skew),
			zap.Duration("tolerance", ck.bounds.TimestampSkewTolerance),
		)
	}

	return nil
}

// checkParameterBounds enforces Axiom 6: all parameters must be within bounds.
func (ck *ConstitutionalKernel) checkParameterBounds(decision *EscalationDecision) error {
	// Check severity bounds
	if decision.Severity < ck.bounds.SeverityMin || decision.Severity > ck.bounds.SeverityMax {
		return &ConstitutionalViolation{
			Type:    ViolationUnboundedParameter,
			Message: fmt.Sprintf("Severity %.2f outside bounds [%.2f, %.2f]", decision.Severity, ck.bounds.SeverityMin, ck.bounds.SeverityMax),
			Timestamp: time.Now(),
			Context: map[string]interface{}{
				"parameter": "severity",
				"value":     decision.Severity,
				"min":       ck.bounds.SeverityMin,
				"max":       ck.bounds.SeverityMax,
			},
		}
	}

	// Check state bounds
	if decision.ToState < ck.bounds.StateMin || decision.ToState > ck.bounds.StateMax {
		return &ConstitutionalViolation{
			Type:    ViolationUnboundedParameter,
			Message: fmt.Sprintf("ToState %d outside bounds [%d, %d]", decision.ToState, ck.bounds.StateMin, ck.bounds.StateMax),
			Timestamp: time.Now(),
			Context: map[string]interface{}{
				"parameter": "to_state",
				"value":     decision.ToState,
				"min":       ck.bounds.StateMin,
				"max":       ck.bounds.StateMax,
			},
		}
	}

	// Check inputs for NaN/Inf and bounds
	if inputs := decision.Inputs; inputs != nil {
		if anomaly, ok := inputs["anomaly_score"].(float64); ok {
			if math.IsNaN(anomaly) || math.IsInf(anomaly, 0) {
				return &ConstitutionalViolation{
					Type:      ViolationNaNInf,
					Message:   fmt.Sprintf("Anomaly score is NaN or Inf: %f", anomaly),
					Timestamp: time.Now(),
					Context:   map[string]interface{}{"pid": decision.PID},
				}
			}
			if anomaly < ck.bounds.AnomalyMin || anomaly > ck.bounds.AnomalyMax {
				return &ConstitutionalViolation{
					Type:    ViolationUnboundedParameter,
					Message: fmt.Sprintf("Anomaly score %.2f outside bounds [%.2f, %.2f]", anomaly, ck.bounds.AnomalyMin, ck.bounds.AnomalyMax),
					Timestamp: time.Now(),
					Context: map[string]interface{}{
						"parameter": "anomaly_score",
						"value":     anomaly,
					},
				}
			}
		}

		if quorum, ok := inputs["quorum_signal"].(float64); ok {
			if math.IsNaN(quorum) || math.IsInf(quorum, 0) {
				return &ConstitutionalViolation{
					Type:      ViolationNaNInf,
					Message:   fmt.Sprintf("Quorum signal is NaN or Inf: %f", quorum),
					Timestamp: time.Now(),
					Context:   map[string]interface{}{"pid": decision.PID},
				}
			}
			if quorum < ck.bounds.QuorumMin || quorum > ck.bounds.QuorumMax {
				return &ConstitutionalViolation{
					Type:    ViolationUnboundedParameter,
					Message: fmt.Sprintf("Quorum signal %.2f outside bounds [%.2f, %.2f]", quorum, ck.bounds.QuorumMin, ck.bounds.QuorumMax),
					Timestamp: time.Now(),
					Context: map[string]interface{}{
						"parameter": "quorum_signal",
						"value":     quorum,
					},
				}
			}
		}

		if pressure, ok := inputs["pressure_score"].(float64); ok {
			if math.IsNaN(pressure) || math.IsInf(pressure, 0) {
				return &ConstitutionalViolation{
					Type:      ViolationNaNInf,
					Message:   fmt.Sprintf("Pressure score is NaN or Inf: %f", pressure),
					Timestamp: time.Now(),
					Context:   map[string]interface{}{"pid": decision.PID},
				}
			}
			if pressure < ck.bounds.PressureMin || pressure > ck.bounds.PressureMax {
				return &ConstitutionalViolation{
					Type:    ViolationUnboundedParameter,
					Message: fmt.Sprintf("Pressure score %.2f outside bounds [%.2f, %.2f]", pressure, ck.bounds.PressureMin, ck.bounds.PressureMax),
					Timestamp: time.Now(),
					Context: map[string]interface{}{
						"parameter": "pressure_score",
						"value":     pressure,
					},
				}
			}
		}
	}

	return nil
}

// computeDecisionHash creates a canonical SHA256 hash of the decision inputs.
// This enforces Axiom 1 (Determinism) and Axiom 5 (Reproducibility).
func (ck *ConstitutionalKernel) computeDecisionHash(decision *EscalationDecision) (string, error) {
	// Create canonical representation
	canonical := map[string]interface{}{
		"pid":        decision.PID,
		"from_state": decision.FromState,
		"to_state":   decision.ToState,
		"severity":   fmt.Sprintf("%.8f", decision.Severity), // 8 decimal places
		"timestamp":  decision.Timestamp.UnixNano(),
		"node_id":    decision.NodeID,
		"inputs":     decision.Inputs,
	}

	// Marshal to JSON (deterministic key ordering)
	jsonBytes, err := json.Marshal(canonical)
	if err != nil {
		return "", fmt.Errorf("failed to marshal decision: %w", err)
	}

	// Compute SHA256
	hash := sha256.Sum256(jsonBytes)
	return hex.EncodeToString(hash[:]), nil
}

// handleViolation processes a constitutional violation.
// In strict mode (testing), it panics. In production, it logs and increments counter.
func (ck *ConstitutionalKernel) handleViolation(err error) error {
	ck.violationCount++

	violation, ok := err.(*ConstitutionalViolation)
	if !ok {
		violation = &ConstitutionalViolation{
			Type:      ViolationType("unknown"),
			Message:   err.Error(),
			Timestamp: time.Now(),
		}
	}

	ck.logger.Error("CONSTITUTIONAL VIOLATION",
		zap.String("type", string(violation.Type)),
		zap.String("message", violation.Message),
		zap.Any("context", violation.Context),
		zap.Int64("total_violations", ck.violationCount),
	)

	if ck.strict {
		panic(fmt.Sprintf("CONSTITUTIONAL VIOLATION IN STRICT MODE: %v", violation))
	}

	return violation
}

// Stats returns kernel statistics.
type Stats struct {
	DecisionsVerified int64 `json:"decisions_verified"`
	ViolationCount    int64 `json:"violation_count"`
	LastDecisionHash  string `json:"last_decision_hash"`
}

// GetStats returns current kernel statistics.
func (ck *ConstitutionalKernel) GetStats() Stats {
	ck.mu.RLock()
	defer ck.mu.RUnlock()

	return Stats{
		DecisionsVerified: ck.decisionsVerified,
		ViolationCount:    ck.violationCount,
		LastDecisionHash:  ck.lastDecisionHash,
	}
}
