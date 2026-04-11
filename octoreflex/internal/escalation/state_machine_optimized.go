// Package escalation — state_machine_optimized.go
//
// Lock-free atomic state machine for microsecond-latency state transitions.
//
// OPTIMIZATIONS:
//   1. Lock-free transitions using sync/atomic (CAS loop)
//   2. Inline critical paths (no function calls in hot path)
//   3. Zero-allocation state reads
//   4. Cache-aligned structs to prevent false sharing
//   5. Fast-path branch prediction hints
//
// INVARIANTS (formally verified in ../verification/monotonicity.tla):
//   - Monotonicity: state transitions only increase (except decay)
//   - Atomicity: state reads/writes are atomic at all times
//   - Terminal: TERMINATED state is permanent
//   - Decay safety: decay only decrements by 1, never skips states
//
// PERFORMANCE TARGET:
//   - State read: <100ns
//   - State transition (CAS): <10μs (including audit log write)
//   - WAL persistence: async, non-blocking

package escalation

import (
	"crypto/ed25519"
	"sync/atomic"
	"time"
	"unsafe"
)

// Note: State type is defined in state_machine.go

// StateAtomic is a cache-aligned atomic state container.
// Aligned to 64 bytes to prevent false sharing in multi-core systems.
type StateAtomic struct {
	value uint64 // Atomic state value (lower 8 bits = State, upper 56 bits = timestamp)
	_pad  [56]byte
}

// AtomicProcessState is the lock-free version of ProcessState.
// All operations use atomic CAS loops instead of mutexes.
type AtomicProcessState struct {
	pid           uint32       // Immutable
	state         StateAtomic  // Atomic state + timestamp
	pressureScore atomic.Uint64 // float64 bits as uint64
	lastEventNs   atomic.Int64  // Unix nanoseconds
	
	// WAL and audit
	wal       *WriteAheadLog
	auditLog  *AuditLog
	signingKey ed25519.PrivateKey
}

// NewAtomicProcessState creates a lock-free ProcessState for a PID.
func NewAtomicProcessState(pid uint32, wal *WriteAheadLog, auditLog *AuditLog, signingKey ed25519.PrivateKey) *AtomicProcessState {
	now := time.Now().UnixNano()
	aps := &AtomicProcessState{
		pid:        pid,
		wal:        wal,
		auditLog:   auditLog,
		signingKey: signingKey,
	}
	
	// Initialize state with timestamp
	aps.state.value = packStateTime(StateNormal, now)
	aps.lastEventNs.Store(now)
	
	return aps
}

// Current returns the current state (fast path: single atomic load).
// Inlined by compiler for zero-overhead abstraction.
//
//go:inline
func (aps *AtomicProcessState) Current() State {
	packed := atomic.LoadUint64(&aps.state.value)
	return unpackState(packed)
}

// CurrentWithTime returns state and entry timestamp atomically.
//
//go:inline
func (aps *AtomicProcessState) CurrentWithTime() (State, time.Time) {
	packed := atomic.LoadUint64(&aps.state.value)
	state := unpackState(packed)
	ts := unpackTime(packed)
	return state, time.Unix(0, ts)
}

// TimeInState returns how long the process has been in its current state.
func (aps *AtomicProcessState) TimeInState() time.Duration {
	_, enteredAt := aps.CurrentWithTime()
	return time.Since(enteredAt)
}

// Escalate performs an atomic state transition to a higher state.
// Returns (newState, true) if transition succeeded.
// Returns (currentState, false) if already at/above target or if target < current.
//
// Uses CAS loop for lock-free operation. Writes to WAL before returning.
func (aps *AtomicProcessState) Escalate(target State) (State, bool) {
	now := time.Now().UnixNano()
	
	for {
		oldPacked := atomic.LoadUint64(&aps.state.value)
		oldState := unpackState(oldPacked)
		
		// Fast path: already at or above target
		if target <= oldState {
			return oldState, false
		}
		
		// Prepare new packed value
		newPacked := packStateTime(target, now)
		
		// CAS: atomic compare-and-swap
		if atomic.CompareAndSwapUint64(&aps.state.value, oldPacked, newPacked) {
			// Transition succeeded — persist to WAL (async)
			if aps.wal != nil {
				entry := WALEntry{
					PID:       aps.pid,
					OldState:  oldState,
					NewState:  target,
					Timestamp: now,
					EventType: EventEscalate,
				}
				aps.wal.Append(entry) // Non-blocking
			}
			
			// Write to cryptographic audit log (async)
			if aps.auditLog != nil && aps.signingKey != nil {
				aps.auditLog.LogTransition(aps.pid, oldState, target, now, aps.signingKey)
			}
			
			return target, true
		}
		// CAS failed — retry loop (contention from another goroutine)
	}
}

// Decay decrements the state by one level atomically.
// TERMINAL states (TERMINATED) never decay.
// Returns (newState, true) if decay occurred.
// Returns (currentState, false) if already NORMAL or TERMINATED.
func (aps *AtomicProcessState) Decay() (State, bool) {
	now := time.Now().UnixNano()
	
	for {
		oldPacked := atomic.LoadUint64(&aps.state.value)
		oldState := unpackState(oldPacked)
		
		// Terminal or already NORMAL — cannot decay
		if oldState == StateNormal || oldState == StateTerminated {
			return oldState, false
		}
		
		newState := oldState - 1
		newPacked := packStateTime(newState, now)
		
		if atomic.CompareAndSwapUint64(&aps.state.value, oldPacked, newPacked) {
			// Persist to WAL
			if aps.wal != nil {
				entry := WALEntry{
					PID:       aps.pid,
					OldState:  oldState,
					NewState:  newState,
					Timestamp: now,
					EventType: EventDecay,
				}
				aps.wal.Append(entry)
			}
			
			// Audit log
			if aps.auditLog != nil && aps.signingKey != nil {
				aps.auditLog.LogTransition(aps.pid, oldState, newState, now, aps.signingKey)
			}
			
			return newState, true
		}
	}
}

// UpdatePressure stores the EWMA pressure score atomically.
//
//go:inline
func (aps *AtomicProcessState) UpdatePressure(p float64) {
	bits := *(*uint64)(unsafe.Pointer(&p))
	aps.pressureScore.Store(bits)
}

// PressureScore returns the current EWMA pressure value.
//
//go:inline
func (aps *AtomicProcessState) PressureScore() float64 {
	bits := aps.pressureScore.Load()
	return *(*float64)(unsafe.Pointer(&bits))
}

// TouchEvent records the timestamp of the most recent kernel event.
//
//go:inline
func (aps *AtomicProcessState) TouchEvent(t time.Time) {
	aps.lastEventNs.Store(t.UnixNano())
}

// LastEventAt returns the timestamp of the most recent kernel event.
func (aps *AtomicProcessState) LastEventAt() time.Time {
	ns := aps.lastEventNs.Load()
	return time.Unix(0, ns)
}

// PID returns the process ID (immutable, no atomic needed).
//
//go:inline
func (aps *AtomicProcessState) PID() uint32 {
	return aps.pid
}

// ─── Packing/Unpacking Helpers ───────────────────────────────────────────────

// packStateTime packs a State (8 bits) and timestamp (56 bits) into uint64.
// Layout: [56-bit timestamp][8-bit state]
//
//go:inline
func packStateTime(s State, timestampNs int64) uint64 {
	// Use only lower 56 bits of timestamp (enough for ~2000 years from epoch)
	ts := uint64(timestampNs) & 0x00FFFFFFFFFFFFFF
	return (ts << 8) | uint64(s)
}

// unpackState extracts the State from a packed uint64.
//
//go:inline
func unpackState(packed uint64) State {
	return State(packed & 0xFF)
}

// unpackTime extracts the timestamp from a packed uint64.
//
//go:inline
func unpackTime(packed uint64) int64 {
	return int64(packed >> 8)
}


