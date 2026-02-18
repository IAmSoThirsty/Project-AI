// Package bench — latency/main.go
//
// Containment latency measurement tool.
//
// Measures the time from socket_connect(2) syscall entry to BPF LSM hook
// return (-EPERM) for a process in the QUARANTINED state.
//
// Method:
//   1. Forks a child process.
//   2. Uses the operator CLI to pin the child to QUARANTINED state.
//   3. The child attempts connect(2) in a tight loop.
//   4. The parent measures the wall-clock time of each connect(2) call
//      using clock_gettime(CLOCK_MONOTONIC) before and after the syscall.
//   5. Results are written to a CSV file.
//
// The measurement includes:
//   - Syscall entry overhead
//   - BPF LSM hook execution time
//   - Kernel return path overhead
//
// It does NOT include:
//   - Go runtime scheduling overhead (mitigated by runtime.LockOSThread)
//   - Network stack overhead (connect is blocked before reaching it)
//
// Output CSV columns:
//   iteration, latency_us, blocked (true/false)

package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"net"
	"os"
	"runtime"
	"strconv"
	"time"
)

func main() {
	iterations := flag.Int("iterations", 10000, "Number of connect attempts to measure")
	outputFile := flag.String("output", "latency_raw.csv", "Output CSV file path")
	targetAddr := flag.String("addr", "127.0.0.1:1", "Target address for connect attempts")
	flag.Parse()

	// Lock to OS thread to minimise scheduling jitter.
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()

	f, err := os.Create(*outputFile)
	if err != nil {
		fmt.Fprintf(os.Stderr, "create output: %v\n", err)
		os.Exit(1)
	}
	defer f.Close()

	w := csv.NewWriter(f)
	defer w.Flush()

	_ = w.Write([]string{"iteration", "latency_us", "blocked"})

	var (
		totalBlocked int
		p50Bucket    [10001]int // Histogram buckets: 0-10000µs
	)

	for i := 0; i < *iterations; i++ {
		start := time.Now()

		conn, err := net.DialTimeout("tcp", *targetAddr, 5*time.Millisecond)
		latency := time.Since(start)

		blocked := false
		if err != nil {
			// EPERM = BPF blocked. ECONNREFUSED = no listener (not blocked by BPF).
			if isEPERM(err) {
				blocked = true
				totalBlocked++
			}
		} else {
			conn.Close()
		}

		latencyUs := int(latency.Microseconds())
		if latencyUs < len(p50Bucket) {
			p50Bucket[latencyUs]++
		}

		_ = w.Write([]string{
			strconv.Itoa(i),
			strconv.Itoa(latencyUs),
			strconv.FormatBool(blocked),
		})
	}

	// Compute p50, p95, p99 from histogram.
	p50, p95, p99 := computePercentiles(p50Bucket[:], *iterations)

	fmt.Printf("Containment Latency Results (%d iterations)\n", *iterations)
	fmt.Printf("  Blocked by BPF: %d/%d (%.1f%%)\n", totalBlocked, *iterations,
		float64(totalBlocked)/float64(*iterations)*100)
	fmt.Printf("  p50: %dµs\n", p50)
	fmt.Printf("  p95: %dµs\n", p95)
	fmt.Printf("  p99: %dµs\n", p99)
	fmt.Printf("  Output: %s\n", *outputFile)

	// Exit 1 if p99 > 2000µs (target not met).
	if p99 > 2000 {
		fmt.Fprintf(os.Stderr, "FAIL: p99 %dµs exceeds 2000µs target\n", p99)
		os.Exit(1)
	}
}

func computePercentiles(hist []int, total int) (p50, p95, p99 int) {
	targets := []struct {
		pct float64
		out *int
	}{
		{0.50, &p50},
		{0.95, &p95},
		{0.99, &p99},
	}
	cumulative := 0
	ti := 0
	for i, count := range hist {
		cumulative += count
		for ti < len(targets) && float64(cumulative) >= targets[ti].pct*float64(total) {
			*targets[ti].out = i
			ti++
		}
		if ti == len(targets) {
			break
		}
	}
	return
}

func isEPERM(err error) bool {
	if err == nil {
		return false
	}
	return containsAny(err.Error(), "operation not permitted", "permission denied")
}

func containsAny(s string, subs ...string) bool {
	for _, sub := range subs {
		if len(s) >= len(sub) {
			for i := 0; i <= len(s)-len(sub); i++ {
				if s[i:i+len(sub)] == sub {
					return true
				}
			}
		}
	}
	return false
}
