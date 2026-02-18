// Package escalation — state_machine.go
//
// Defines the process isolation state machine for OCTOREFLEX.
//
// State transition graph:
//
//	NORMAL (0) ──→ PRESSURE (1) ──→ ISOLATED (2) ──→ FROZEN (3) ──→ QUARANTINED (4) ──→ TERMINATED (5)
//	   ↑               ↑               ↑
//	   └───────────────┴───────────────┘  (decay, userspace only)
//
// Monotonicity invariant:
//   - Escalation (state increase) is performed by the escalation engine
//     when severity thresholds are crossed.
//   - Decay (state decrease) is performed by the cool-down scheduler
//     after a configurable quiescence period.
//   - The BPF kernel layer only reads state; it never writes it.
//   - State transitions are atomic under a per-PID mutex.
//
// State semantics:
//   NORMAL      — No anomaly. All syscalls permitted.
//   PRESSURE    — Anomaly accumulating. UID changes blocked (kernel).
//                 Monitoring frequency increased (userspace).
//   ISOLATED    — Network + file writes blocked (kernel).
//                 cgroup memory limit applied (userspace).
//   FROZEN      — cgroup freeze applied. Process suspended.
//                 Evidence collection begins.
//   QUARANTINED — Process moved to dedicated PID namespace.
//                 All external communication severed.
//   TERMINATED  — SIGKILL sent. Entry retained in audit ledger.
//                 State never decays from TERMINATED.

package escalation

import (
	"fmt"
	"sync"
	"time"
)

// State represents the isolation level of a monitored process.
// Values must match the octo_state_t enum in octoreflex.h exactly.
type State uint8

const (
	StateNormal      State = 0
	StatePressure    State = 1
	StateIsolated    State = 2
	StateFrozen      State = 3
	StateQuarantined State = 4
	StateTerminated  State = 5
)

// String returns the human-readable state name.
func (s State) String() string {
	switch s {
	case StateNormal:
		return "NORMAL"
	case StatePressure:
		return "PRESSURE"
	case StateIsolated:
		return "ISOLATED"
	case StateFrozen:
		return "FROZEN"
	case StateQuarantined:
		return "QUARANTINED"
	case StateTerminated:
		return "TERMINATED"
	default:
		return fmt.Sprintf("UNKNOWN(%d)", uint8(s))
	}
}

// IsTerminal returns true if the state cannot be decayed further.
// TERMINATED is the only terminal state.
func (s State) IsTerminal() bool {
	return s == StateTerminated
}

// ProcessState holds the mutable isolation state for a single PID.
// All fields are protected by mu. Do not access fields directly.
type ProcessState struct {
	mu             sync.Mutex
	pid            uint32
	current        State
	enteredAt      time.Time // When the current state was entered.
	lastEventAt    time.Time // Last kernel event timestamp for this PID.
	pressureScore  float64   // Cached EWMA pressure value (from accumulator).
}

// NewProcessState creates a ProcessState for a PID in NORMAL state.
func NewProcessState(pid uint32) *ProcessState {
	now := time.Now()
	return &ProcessState{
		pid:         pid,
		current:     StateNormal,
		enteredAt:   now,
		lastEventAt: now,
	}
}

// Current returns the current isolation state.
func (ps *ProcessState) Current() State {
	ps.mu.Lock()
	defer ps.mu.Unlock()
	return ps.current
}

// TimeInState returns how long the process has been in its current state.
func (ps *ProcessState) TimeInState() time.Duration {
	ps.mu.Lock()
	defer ps.mu.Unlock()
	return time.Since(ps.enteredAt)
}

// Escalate attempts to transition the process to a higher state.
// Returns (newState, true) if the transition occurred.
// Returns (currentState, false) if already at or above the target state,
// or if the target state is lower than current (escalate never decays).
//
// Thread-safe. The caller is responsible for propagating the new state
// to the BPF process_state_map via bpf.Objects.SetProcessState().
func (ps *ProcessState) Escalate(target State) (State, bool) {
	ps.mu.Lock()
	defer ps.mu.Unlock()

	if target <= ps.current {
		return ps.current, false // Already at or above target.
	}
	ps.current = target
	ps.enteredAt = time.Now()
	return ps.current, true
}

// Decay attempts to reduce the state by one level.
// TERMINATED never decays. Returns (newState, true) if decay occurred.
// Returns (currentState, false) if already NORMAL or TERMINATED.
//
// Decay is only called by the cool-down scheduler, never by the
// escalation engine or BPF programs.
func (ps *ProcessState) Decay() (State, bool) {
	ps.mu.Lock()
	defer ps.mu.Unlock()

	if ps.current == StateNormal || ps.current == StateTerminated {
		return ps.current, false
	}
	ps.current--
	ps.enteredAt = time.Now()
	return ps.current, true
}

// UpdatePressure stores the latest EWMA pressure score for this PID.
// Used by the escalation engine to make threshold decisions.
func (ps *ProcessState) UpdatePressure(p float64) {
	ps.mu.Lock()
	defer ps.mu.Unlock()
	ps.pressureScore = p
}

// PressureScore returns the last stored EWMA pressure value.
func (ps *ProcessState) PressureScore() float64 {
	ps.mu.Lock()
	defer ps.mu.Unlock()
	return ps.pressureScore
}

// TouchEvent records the timestamp of the most recent kernel event.
func (ps *ProcessState) TouchEvent(t time.Time) {
	ps.mu.Lock()
	defer ps.mu.Unlock()
	ps.lastEventAt = t
}

// LastEventAt returns the timestamp of the most recent kernel event.
func (ps *ProcessState) LastEventAt() time.Time {
	ps.mu.Lock()
	defer ps.mu.Unlock()
	return ps.lastEventAt
}

// PID returns the process ID this state belongs to.
func (ps *ProcessState) PID() uint32 {
	return ps.pid // Immutable after construction, no lock needed.
}
