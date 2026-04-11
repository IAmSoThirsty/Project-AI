// Package escalation — state_machine_bench_test.go
//
// Performance benchmarks for lock-free atomic state machine.
//
// TARGET: <10μs per state transition (including audit log write)
//
// BENCHMARKS:
//   - State read (Current): <100ns
//   - State transition (Escalate): <10μs
//   - Concurrent transitions (parallel): <20μs (with contention)
//   - WAL append: <5μs (async)
//   - Audit log write: <5μs (async)

package escalation_test

import (
	"crypto/ed25519"
	"path/filepath"
	"sync"
	"sync/atomic"
	"testing"
	"time"

	"github.com/octoreflex/octoreflex/internal/escalation"
)

// ─── Baseline Benchmarks ──────────────────────────────────────────────────

// BenchmarkStateRead measures the cost of reading the current state (fast path).
// TARGET: <100ns
func BenchmarkStateRead(b *testing.B) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = ps.Current()
	}
}

// BenchmarkStateReadWithTime measures reading state + timestamp atomically.
// TARGET: <150ns
func BenchmarkStateReadWithTime(b *testing.B) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, _ = ps.CurrentWithTime()
	}
}

// ─── State Transition Benchmarks ──────────────────────────────────────────

// BenchmarkEscalate_NoWAL measures escalation without WAL (raw CAS performance).
// TARGET: <1μs
func BenchmarkEscalate_NoWAL(b *testing.B) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	
	states := []escalation.State{
		escalation.StatePressure,
		escalation.StateIsolated,
		escalation.StateFrozen,
		escalation.StateQuarantined,
		escalation.StateTerminated,
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		target := states[i%len(states)]
		ps.Escalate(target)
	}
}

// BenchmarkEscalate_WithWAL measures escalation with WAL enabled.
// TARGET: <10μs (includes async WAL append)
func BenchmarkEscalate_WithWAL(b *testing.B) {
	tmpDir := b.TempDir()
	walPath := filepath.Join(tmpDir, "test.wal")
	
	wal, err := escalation.OpenWAL(walPath)
	if err != nil {
		b.Fatalf("failed to open WAL: %v", err)
	}
	defer wal.Close()
	
	ps := escalation.NewAtomicProcessState(1234, wal, nil, nil)
	
	states := []escalation.State{
		escalation.StatePressure,
		escalation.StateIsolated,
		escalation.StateFrozen,
		escalation.StateQuarantined,
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		target := states[i%len(states)]
		ps.Escalate(target)
	}
}

// BenchmarkEscalate_WithAudit measures escalation with cryptographic audit log.
// TARGET: <10μs (includes Ed25519 signature)
func BenchmarkEscalate_WithAudit(b *testing.B) {
	tmpDir := b.TempDir()
	auditPath := filepath.Join(tmpDir, "test.audit")
	
	pubKey, privKey, err := ed25519.GenerateKey(nil)
	if err != nil {
		b.Fatalf("failed to generate key: %v", err)
	}
	
	auditLog, err := escalation.OpenAuditLog(auditPath, pubKey)
	if err != nil {
		b.Fatalf("failed to open audit log: %v", err)
	}
	defer auditLog.Close()
	
	ps := escalation.NewAtomicProcessState(1234, nil, auditLog, privKey)
	
	states := []escalation.State{
		escalation.StatePressure,
		escalation.StateIsolated,
		escalation.StateFrozen,
		escalation.StateQuarantined,
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		target := states[i%len(states)]
		ps.Escalate(target)
	}
}

// BenchmarkEscalate_Full measures end-to-end escalation with WAL + audit.
// TARGET: <10μs
func BenchmarkEscalate_Full(b *testing.B) {
	tmpDir := b.TempDir()
	walPath := filepath.Join(tmpDir, "test.wal")
	auditPath := filepath.Join(tmpDir, "test.audit")
	
	wal, err := escalation.OpenWAL(walPath)
	if err != nil {
		b.Fatalf("failed to open WAL: %v", err)
	}
	defer wal.Close()
	
	pubKey, privKey, err := ed25519.GenerateKey(nil)
	if err != nil {
		b.Fatalf("failed to generate key: %v", err)
	}
	
	auditLog, err := escalation.OpenAuditLog(auditPath, pubKey)
	if err != nil {
		b.Fatalf("failed to open audit log: %v", err)
	}
	defer auditLog.Close()
	
	ps := escalation.NewAtomicProcessState(1234, wal, auditLog, privKey)
	
	states := []escalation.State{
		escalation.StatePressure,
		escalation.StateIsolated,
		escalation.StateFrozen,
		escalation.StateQuarantined,
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		target := states[i%len(states)]
		ps.Escalate(target)
	}
	
	b.StopTimer()
	
	// Report latency in microseconds
	elapsed := b.Elapsed()
	perOp := elapsed / time.Duration(b.N)
	us := perOp.Microseconds()
	b.ReportMetric(float64(us), "μs/op")
}

// ─── Concurrency Benchmarks ───────────────────────────────────────────────

// BenchmarkEscalate_Parallel measures concurrent escalations (contention).
// TARGET: <20μs (with CAS retry overhead)
func BenchmarkEscalate_Parallel(b *testing.B) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	
	b.RunParallel(func(pb *testing.PB) {
		i := 0
		states := []escalation.State{
			escalation.StatePressure,
			escalation.StateIsolated,
			escalation.StateFrozen,
			escalation.StateQuarantined,
		}
		for pb.Next() {
			target := states[i%len(states)]
			ps.Escalate(target)
			i++
		}
	})
}

// BenchmarkMultiProcessEscalate measures non-contending parallel transitions.
// Each goroutine operates on a different ProcessState (no contention).
// TARGET: <10μs per goroutine
func BenchmarkMultiProcessEscalate(b *testing.B) {
	const numProcesses = 8
	
	tmpDir := b.TempDir()
	walPath := filepath.Join(tmpDir, "test.wal")
	
	wal, err := escalation.OpenWAL(walPath)
	if err != nil {
		b.Fatalf("failed to open WAL: %v", err)
	}
	defer wal.Close()
	
	// Create multiple ProcessState instances
	processes := make([]*escalation.AtomicProcessState, numProcesses)
	for i := 0; i < numProcesses; i++ {
		processes[i] = escalation.NewAtomicProcessState(uint32(1000+i), wal, nil, nil)
	}
	
	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		i := 0
		procIdx := i % numProcesses
		states := []escalation.State{
			escalation.StatePressure,
			escalation.StateIsolated,
			escalation.StateFrozen,
		}
		for pb.Next() {
			target := states[i%len(states)]
			processes[procIdx].Escalate(target)
			i++
			procIdx = i % numProcesses
		}
	})
}

// ─── Decay Benchmarks ─────────────────────────────────────────────────────

// BenchmarkDecay measures decay performance.
// TARGET: <1μs (same as escalate)
func BenchmarkDecay(b *testing.B) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	ps.Escalate(escalation.StateQuarantined) // Start high
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ps.Decay()
		if ps.Current() == escalation.StateNormal {
			ps.Escalate(escalation.StateQuarantined) // Reset
		}
	}
}

// ─── WAL Benchmarks ───────────────────────────────────────────────────────

// BenchmarkWAL_Append measures WAL append throughput.
// TARGET: <5μs per entry
func BenchmarkWAL_Append(b *testing.B) {
	tmpDir := b.TempDir()
	walPath := filepath.Join(tmpDir, "test.wal")
	
	wal, err := escalation.OpenWAL(walPath)
	if err != nil {
		b.Fatalf("failed to open WAL: %v", err)
	}
	defer wal.Close()
	
	entry := escalation.WALEntry{
		PID:       1234,
		OldState:  escalation.StateNormal,
		NewState:  escalation.StatePressure,
		Timestamp: time.Now().UnixNano(),
		EventType: escalation.EventEscalate,
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		wal.Append(entry)
	}
}

// BenchmarkWAL_ParallelAppend measures WAL throughput under concurrency.
func BenchmarkWAL_ParallelAppend(b *testing.B) {
	tmpDir := b.TempDir()
	walPath := filepath.Join(tmpDir, "test.wal")
	
	wal, err := escalation.OpenWAL(walPath)
	if err != nil {
		b.Fatalf("failed to open WAL: %v", err)
	}
	defer wal.Close()
	
	b.RunParallel(func(pb *testing.PB) {
		entry := escalation.WALEntry{
			PID:       1234,
			OldState:  escalation.StateNormal,
			NewState:  escalation.StatePressure,
			Timestamp: time.Now().UnixNano(),
			EventType: escalation.EventEscalate,
		}
		for pb.Next() {
			wal.Append(entry)
		}
	})
}

// ─── Pressure Score Benchmarks ────────────────────────────────────────────

// BenchmarkPressureUpdate measures atomic pressure score updates.
// TARGET: <50ns
func BenchmarkPressureUpdate(b *testing.B) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ps.UpdatePressure(float64(i) * 0.01)
	}
}

// BenchmarkPressureRead measures pressure score reads.
// TARGET: <50ns
func BenchmarkPressureRead(b *testing.B) {
	ps := escalation.NewAtomicProcessState(1234, nil, nil, nil)
	ps.UpdatePressure(5.0)
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = ps.PressureScore()
	}
}

// ─── Throughput Test ──────────────────────────────────────────────────────

// TestTransitionThroughput measures sustained throughput over time.
func TestTransitionThroughput(t *testing.T) {
	tmpDir := t.TempDir()
	walPath := filepath.Join(tmpDir, "test.wal")
	
	wal, err := escalation.OpenWAL(walPath)
	if err != nil {
		t.Fatalf("failed to open WAL: %v", err)
	}
	defer wal.Close()
	
	const numGoroutines = 8
	const duration = 5 * time.Second
	
	var count atomic.Int64
	var wg sync.WaitGroup
	
	processes := make([]*escalation.AtomicProcessState, numGoroutines)
	for i := 0; i < numGoroutines; i++ {
		processes[i] = escalation.NewAtomicProcessState(uint32(2000+i), wal, nil, nil)
	}
	
	start := time.Now()
	stopChan := make(chan struct{})
	
	// Stop after duration
	go func() {
		time.Sleep(duration)
		close(stopChan)
	}()
	
	// Start workers
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			ps := processes[idx]
			states := []escalation.State{
				escalation.StatePressure,
				escalation.StateIsolated,
				escalation.StateFrozen,
			}
			j := 0
			for {
				select {
				case <-stopChan:
					return
				default:
					target := states[j%len(states)]
					ps.Escalate(target)
					count.Add(1)
					j++
				}
			}
		}(i)
	}
	
	wg.Wait()
	elapsed := time.Since(start)
	
	totalOps := count.Load()
	throughput := float64(totalOps) / elapsed.Seconds()
	avgLatency := elapsed / time.Duration(totalOps)
	
	t.Logf("Throughput: %.0f transitions/sec", throughput)
	t.Logf("Average latency: %v", avgLatency)
	t.Logf("Total transitions: %d", totalOps)
	
	// Verify target: average latency < 10μs
	if avgLatency > 10*time.Microsecond {
		t.Errorf("Average latency %v exceeds 10μs target", avgLatency)
	}
}
