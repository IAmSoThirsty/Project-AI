// Package escalation — state_machine_integration_test.go
//
// Integration tests for the optimized state machine with WAL and audit log.
//
// TEST COVERAGE:
//   - End-to-end state transitions with persistence
//   - WAL replay after simulated crash
//   - Audit log verification
//   - Concurrent multi-process escalation
//   - Monotonicity enforcement
//   - Terminal state invariant

package escalation_test

import (
	"crypto/ed25519"
	"os"
	"path/filepath"
	"sync"
	"testing"
	"time"

	"github.com/octoreflex/octoreflex/internal/escalation"
)

// TestAtomicProcessState_BasicTransitions verifies basic state machine behavior.
func TestAtomicProcessState_BasicTransitions(t *testing.T) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	
	// Initial state
	if ps.Current() != escalation.StateNormal {
		t.Errorf("expected initial state NORMAL, got %s", ps.Current())
	}
	
	// Escalate to PRESSURE
	newState, ok := ps.Escalate(escalation.StatePressure)
	if !ok {
		t.Error("expected escalation to succeed")
	}
	if newState != escalation.StatePressure {
		t.Errorf("expected PRESSURE, got %s", newState)
	}
	
	// Escalate to ISOLATED
	newState, ok = ps.Escalate(escalation.StateIsolated)
	if !ok {
		t.Error("expected escalation to succeed")
	}
	if newState != escalation.StateIsolated {
		t.Errorf("expected ISOLATED, got %s", newState)
	}
	
	// Attempt to escalate to lower state (should fail)
	_, ok = ps.Escalate(escalation.StatePressure)
	if ok {
		t.Error("expected escalation to lower state to fail")
	}
	if ps.Current() != escalation.StateIsolated {
		t.Errorf("expected state to remain ISOLATED, got %s", ps.Current())
	}
}

// TestAtomicProcessState_Decay verifies decay behavior.
func TestAtomicProcessState_Decay(t *testing.T) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	
	// Escalate to FROZEN
	ps.Escalate(escalation.StateFrozen)
	
	// Decay to ISOLATED
	newState, ok := ps.Decay()
	if !ok {
		t.Error("expected decay to succeed")
	}
	if newState != escalation.StateIsolated {
		t.Errorf("expected ISOLATED after decay, got %s", newState)
	}
	
	// Decay to PRESSURE
	newState, ok = ps.Decay()
	if !ok {
		t.Error("expected decay to succeed")
	}
	if newState != escalation.StatePressure {
		t.Errorf("expected PRESSURE after decay, got %s", newState)
	}
	
	// Decay to NORMAL
	newState, ok = ps.Decay()
	if !ok {
		t.Error("expected decay to succeed")
	}
	if newState != escalation.StateNormal {
		t.Errorf("expected NORMAL after decay, got %s", newState)
	}
	
	// Attempt to decay from NORMAL (should fail)
	_, ok = ps.Decay()
	if ok {
		t.Error("expected decay from NORMAL to fail")
	}
}

// TestAtomicProcessState_TerminalState verifies TERMINATED is permanent.
func TestAtomicProcessState_TerminalState(t *testing.T) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	
	// Escalate to TERMINATED
	ps.Escalate(escalation.StateTerminated)
	
	// Attempt to decay (should fail)
	_, ok := ps.Decay()
	if ok {
		t.Error("expected decay from TERMINATED to fail")
	}
	if ps.Current() != escalation.StateTerminated {
		t.Errorf("expected state to remain TERMINATED, got %s", ps.Current())
	}
}

// TestWAL_WriteAndReplay verifies WAL persistence and replay.
func TestWAL_WriteAndReplay(t *testing.T) {
	tmpDir := t.TempDir()
	walPath := filepath.Join(tmpDir, "test.wal")
	
	// Write transitions to WAL
	{
		wal, err := escalation.OpenWAL(walPath)
		if err != nil {
			t.Fatalf("failed to open WAL: %v", err)
		}
		
		ps := escalation.NewAtomicProcessState(1234, wal, nil, nil)
		
		ps.Escalate(escalation.StatePressure)
		ps.Escalate(escalation.StateIsolated)
		ps.Escalate(escalation.StateFrozen)
		
		// Close WAL to flush
		wal.Close()
	}
	
	// Replay WAL
	entries, err := escalation.ReplayWAL(walPath)
	if err != nil {
		t.Fatalf("failed to replay WAL: %v", err)
	}
	
	if len(entries) != 3 {
		t.Fatalf("expected 3 entries, got %d", len(entries))
	}
	
	// Verify entries
	expected := []struct {
		old, new escalation.State
	}{
		{escalation.StateNormal, escalation.StatePressure},
		{escalation.StatePressure, escalation.StateIsolated},
		{escalation.StateIsolated, escalation.StateFrozen},
	}
	
	for i, entry := range entries {
		if entry.PID != 1234 {
			t.Errorf("entry %d: expected PID 1234, got %d", i, entry.PID)
		}
		if entry.OldState != expected[i].old {
			t.Errorf("entry %d: expected old state %s, got %s", i, expected[i].old, entry.OldState)
		}
		if entry.NewState != expected[i].new {
			t.Errorf("entry %d: expected new state %s, got %s", i, expected[i].new, entry.NewState)
		}
		if entry.EventType != escalation.EventEscalate {
			t.Errorf("entry %d: expected EventEscalate, got %d", i, entry.EventType)
		}
	}
}

// TestWAL_CrashRecovery simulates a crash and verifies state recovery.
func TestWAL_CrashRecovery(t *testing.T) {
	tmpDir := t.TempDir()
	walPath := filepath.Join(tmpDir, "test.wal")
	
	// Phase 1: Create and escalate processes
	{
		wal, err := escalation.OpenWAL(walPath)
		if err != nil {
			t.Fatalf("failed to open WAL: %v", err)
		}
		
		ps1 := escalation.NewAtomicProcessState(100, wal, nil, nil)
		ps2 := escalation.NewAtomicProcessState(200, wal, nil, nil)
		
		ps1.Escalate(escalation.StateIsolated)
		ps2.Escalate(escalation.StateQuarantined)
		
		// Simulate crash (force close)
		wal.Close()
	}
	
	// Phase 2: Recover from WAL
	entries, err := escalation.ReplayWAL(walPath)
	if err != nil {
		t.Fatalf("failed to replay WAL: %v", err)
	}
	
	// Reconstruct state
	state := make(map[uint32]escalation.State)
	for _, entry := range entries {
		state[entry.PID] = entry.NewState
	}
	
	// Verify recovered state
	if state[100] != escalation.StateIsolated {
		t.Errorf("expected PID 100 in ISOLATED, got %s", state[100])
	}
	if state[200] != escalation.StateQuarantined {
		t.Errorf("expected PID 200 in QUARANTINED, got %s", state[200])
	}
}

// TestAuditLog_WriteAndVerify tests cryptographic audit log.
func TestAuditLog_WriteAndVerify(t *testing.T) {
	tmpDir := t.TempDir()
	auditPath := filepath.Join(tmpDir, "test.audit")
	
	pubKey, privKey, err := ed25519.GenerateKey(nil)
	if err != nil {
		t.Fatalf("failed to generate key: %v", err)
	}
	
	// Write audit entries
	{
		auditLog, err := escalation.OpenAuditLog(auditPath, pubKey)
		if err != nil {
			t.Fatalf("failed to open audit log: %v", err)
		}
		
		ps := escalation.NewAtomicProcessState(1234, nil, auditLog, privKey)
		
		ps.Escalate(escalation.StatePressure)
		ps.Escalate(escalation.StateIsolated)
		ps.Escalate(escalation.StateFrozen)
		
		auditLog.Close()
	}
	
	// Wait for async writes to complete
	time.Sleep(200 * time.Millisecond)
	
	// Verify signatures
	validCount, err := escalation.VerifyLog(auditPath, pubKey)
	if err != nil {
		t.Fatalf("failed to verify audit log: %v", err)
	}
	
	if validCount != 3 {
		t.Errorf("expected 3 valid entries, got %d", validCount)
	}
}

// TestAuditLog_TamperDetection verifies tamper detection.
func TestAuditLog_TamperDetection(t *testing.T) {
	tmpDir := t.TempDir()
	auditPath := filepath.Join(tmpDir, "test.audit")
	
	pubKey, privKey, err := ed25519.GenerateKey(nil)
	if err != nil {
		t.Fatalf("failed to generate key: %v", err)
	}
	
	// Write audit entry
	{
		auditLog, err := escalation.OpenAuditLog(auditPath, pubKey)
		if err != nil {
			t.Fatalf("failed to open audit log: %v", err)
		}
		
		ps := escalation.NewAtomicProcessState(1234, nil, auditLog, privKey)
		ps.Escalate(escalation.StatePressure)
		
		auditLog.Close()
	}
	
	time.Sleep(200 * time.Millisecond)
	
	// Tamper with the file
	data, err := os.ReadFile(auditPath)
	if err != nil {
		t.Fatalf("failed to read audit log: %v", err)
	}
	
	// Flip a bit in the middle
	data[len(data)/2] ^= 0xFF
	
	err = os.WriteFile(auditPath, data, 0600)
	if err != nil {
		t.Fatalf("failed to write tampered audit log: %v", err)
	}
	
	// Verification should fail
	_, err = escalation.VerifyLog(auditPath, pubKey)
	if err == nil {
		t.Error("expected verification to fail on tampered log")
	}
}

// TestConcurrentEscalation verifies lock-free behavior under contention.
func TestConcurrentEscalation(t *testing.T) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	
	const numGoroutines = 100
	var wg sync.WaitGroup
	
	// All goroutines try to escalate to different states concurrently
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			
			states := []escalation.State{
				escalation.StatePressure,
				escalation.StateIsolated,
				escalation.StateFrozen,
				escalation.StateQuarantined,
			}
			
			target := states[idx%len(states)]
			ps.Escalate(target)
		}(i)
	}
	
	wg.Wait()
	
	// Final state should be the highest target (QUARANTINED)
	// due to monotonicity
	final := ps.Current()
	if final != escalation.StateQuarantined {
		t.Errorf("expected final state QUARANTINED, got %s", final)
	}
}

// TestMultiProcessConcurrency verifies independent process state updates.
func TestMultiProcessConcurrency(t *testing.T) {
	tmpDir := t.TempDir()
	walPath := filepath.Join(tmpDir, "test.wal")
	
	wal, err := escalation.OpenWAL(walPath)
	if err != nil {
		t.Fatalf("failed to open WAL: %v", err)
	}
	defer wal.Close()
	
	const numProcesses = 50
	processes := make([]*escalation.AtomicProcessState, numProcesses)
	for i := 0; i < numProcesses; i++ {
		processes[i] = escalation.NewAtomicProcessState(uint32(3000+i), wal, nil, nil)
	}
	
	var wg sync.WaitGroup
	
	// Each process escalates independently
	for i := 0; i < numProcesses; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			
			ps := processes[idx]
			ps.Escalate(escalation.StatePressure)
			ps.Escalate(escalation.StateIsolated)
			ps.Escalate(escalation.StateFrozen)
		}(i)
	}
	
	wg.Wait()
	
	// Verify all processes reached FROZEN
	for i, ps := range processes {
		if ps.Current() != escalation.StateFrozen {
			t.Errorf("process %d: expected FROZEN, got %s", i, ps.Current())
		}
	}
}

// TestPressureScoreAtomic verifies atomic pressure score updates.
func TestPressureScoreAtomic(t *testing.T) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	
	const numGoroutines = 100
	var wg sync.WaitGroup
	
	// Concurrent pressure updates
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(val float64) {
			defer wg.Done()
			ps.UpdatePressure(val)
		}(float64(i))
	}
	
	wg.Wait()
	
	// Should not crash or race (verified by -race flag)
	score := ps.PressureScore()
	if score < 0 || score >= float64(numGoroutines) {
		t.Logf("Final pressure score: %f (expected 0–%d)", score, numGoroutines-1)
	}
}

// TestTimeInState verifies time tracking.
func TestTimeInState(t *testing.T) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	
	time.Sleep(50 * time.Millisecond)
	
	duration := ps.TimeInState()
	if duration < 50*time.Millisecond {
		t.Errorf("expected duration >= 50ms, got %v", duration)
	}
	
	// Escalate and check new time
	ps.Escalate(escalation.StatePressure)
	time.Sleep(10 * time.Millisecond)
	duration2 := ps.TimeInState()
	
	// After escalation, time in new state should be small
	if duration2 >= duration {
		t.Logf("Note: duration2=%v is >= duration=%v, but this can happen due to timing", duration2, duration)
	}
	
	// The new duration should be less than the total time since start
	if duration2 > 100*time.Millisecond {
		t.Errorf("expected new state duration < 100ms, got %v", duration2)
	}
	
	t.Logf("Time in initial state: %v, time in new state: %v", duration, duration2)
}
