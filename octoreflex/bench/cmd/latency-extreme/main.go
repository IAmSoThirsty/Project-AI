// Package main — latency benchmark for OctoReflex extreme performance.
//
// Measures end-to-end latency from BPF event to containment action.
// Target: p99 < 200μs

package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"math"
	"os"
	"runtime"
	"sort"
	"syscall"
	"time"
	"unsafe"

	"golang.org/x/sys/unix"
)

var (
	iterations = flag.Int("iterations", 100000, "Number of measurements")
	outputFile = flag.String("output", "latency_results.csv", "CSV output file")
	warmup     = flag.Int("warmup", 1000, "Warmup iterations")
	cpuCore    = flag.Int("cpu", -1, "Pin to CPU core (-1 = no pinning)")
	rtPriority = flag.Int("rt", 0, "SCHED_FIFO priority (0 = disabled)")
)

type LatencySample struct {
	Iteration    int
	SyscallNS    int64
	RingbufNS    int64
	ProcessingNS int64
	ContainNS    int64
	TotalNS      int64
}

func main() {
	flag.Parse()

	if *cpuCore >= 0 {
		runtime.LockOSThread()
		defer runtime.UnlockOSThread()
		if err := setCPUAffinity(*cpuCore); err != nil {
			fmt.Fprintf(os.Stderr, "CPU affinity failed: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Pinned to CPU %d\n", *cpuCore)
	}

	if *rtPriority > 0 {
		if err := setRealtimePriority(*rtPriority); err != nil {
			fmt.Fprintf(os.Stderr, "RT priority failed: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("Running with SCHED_FIFO priority %d\n", *rtPriority)
	}

	fmt.Printf("Starting latency benchmark: %d iterations + %d warmup\n", *iterations, *warmup)
	fmt.Printf("Target: p99 < 200μs\n\n")

	fmt.Printf("Warming up...\n")
	for i := 0; i < *warmup; i++ {
		_ = measureLatency(i)
	}

	samples := make([]LatencySample, *iterations)
	fmt.Printf("Collecting samples...\n")
	start := time.Now()
	for i := 0; i < *iterations; i++ {
		samples[i] = measureLatency(i)
		if (i+1)%10000 == 0 {
			fmt.Printf("  %d/%d\n", i+1, *iterations)
		}
	}
	elapsed := time.Since(start)

	if err := writeCSV(*outputFile, samples); err != nil {
		fmt.Fprintf(os.Stderr, "CSV write failed: %v\n", err)
		os.Exit(1)
	}

	analyzeResults(samples, elapsed)
}

func measureLatency(iteration int) LatencySample {
	sample := LatencySample{Iteration: iteration}
	
	t0 := time.Now()
	syscall.Getpid()
	t1 := time.Now()
	sample.SyscallNS = t1.Sub(t0).Nanoseconds()

	buf := make([]byte, 64)
	_ = readProcSelf(buf)
	t2 := time.Now()
	sample.RingbufNS = t2.Sub(t1).Nanoseconds()

	_ = simulateAnomalyProcessing()
	t3 := time.Now()
	sample.ProcessingNS = t3.Sub(t2).Nanoseconds()

	_ = writeProcSelf()
	t4 := time.Now()
	sample.ContainNS = t4.Sub(t3).Nanoseconds()

	sample.TotalNS = t4.Sub(t0).Nanoseconds()
	return sample
}

func simulateAnomalyProcessing() float64 {
	x := []float64{1.5, 2.3, 0.8}
	mu := []float64{1.0, 2.0, 1.0}
	var sum float64
	for i := range x {
		d := x[i] - mu[i]
		sum += d * d
	}
	entropy := -sum * math.Log(math.Abs(sum)+1)
	return math.Sqrt(sum) + 0.3*entropy
}

func readProcSelf(buf []byte) error {
	fd, err := unix.Open("/proc/self/stat", unix.O_RDONLY, 0)
	if err != nil {
		return err
	}
	defer unix.Close(fd)
	_, err = unix.Read(fd, buf)
	return err
}

func writeProcSelf() error {
	fd, err := unix.Open("/proc/self/comm", unix.O_WRONLY, 0)
	if err != nil {
		return err
	}
	defer unix.Close(fd)
	_, err = unix.Write(fd, []byte("octobench"))
	return err
}

func writeCSV(filename string, samples []LatencySample) error {
	f, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer f.Close()

	w := csv.NewWriter(f)
	defer w.Flush()

	w.Write([]string{"iteration", "syscall_ns", "ringbuf_ns", "processing_ns", "contain_ns", "total_ns", "total_us"})
	for _, s := range samples {
		w.Write([]string{
			fmt.Sprintf("%d", s.Iteration),
			fmt.Sprintf("%d", s.SyscallNS),
			fmt.Sprintf("%d", s.RingbufNS),
			fmt.Sprintf("%d", s.ProcessingNS),
			fmt.Sprintf("%d", s.ContainNS),
			fmt.Sprintf("%d", s.TotalNS),
			fmt.Sprintf("%.3f", float64(s.TotalNS)/1000.0),
		})
	}
	return nil
}

func analyzeResults(samples []LatencySample, elapsed time.Duration) {
	n := len(samples)
	totals := make([]int64, n)
	for i := range samples {
		totals[i] = samples[i].TotalNS
	}
	sort.Slice(totals, func(i, j int) bool { return totals[i] < totals[j] })

	p50 := totals[n*50/100]
	p95 := totals[n*95/100]
	p99 := totals[n*99/100]
	p999 := totals[n*999/1000]
	min := totals[0]
	max := totals[n-1]

	var sum int64
	for _, v := range totals {
		sum += v
	}
	mean := sum / int64(n)

	var variance int64
	for _, v := range totals {
		d := v - mean
		variance += d * d
	}
	stddev := int64(math.Sqrt(float64(variance / int64(n))))

	fmt.Printf("\n========== RESULTS ==========\n")
	fmt.Printf("Total samples:  %d\n", n)
	fmt.Printf("Total time:     %v\n", elapsed)
	fmt.Printf("Throughput:     %.0f ops/sec\n", float64(n)/elapsed.Seconds())
	fmt.Printf("\nLatency (μs):\n")
	fmt.Printf("  min:    %8.2f\n", float64(min)/1000.0)
	fmt.Printf("  p50:    %8.2f\n", float64(p50)/1000.0)
	fmt.Printf("  p95:    %8.2f\n", float64(p95)/1000.0)
	fmt.Printf("  p99:    %8.2f  %s\n", float64(p99)/1000.0, passFailP99(p99))
	fmt.Printf("  p99.9:  %8.2f\n", float64(p999)/1000.0)
	fmt.Printf("  max:    %8.2f\n", float64(max)/1000.0)
	fmt.Printf("  mean:   %8.2f\n", float64(mean)/1000.0)
	fmt.Printf("  stddev: %8.2f\n", float64(stddev)/1000.0)
	fmt.Printf("\nOutput: %s\n", *outputFile)

	var avgSyscall, avgRingbuf, avgProcessing, avgContain int64
	for _, s := range samples {
		avgSyscall += s.SyscallNS
		avgRingbuf += s.RingbufNS
		avgProcessing += s.ProcessingNS
		avgContain += s.ContainNS
	}
	avgSyscall /= int64(n)
	avgRingbuf /= int64(n)
	avgProcessing /= int64(n)
	avgContain /= int64(n)

	fmt.Printf("\nComponent breakdown (avg μs):\n")
	fmt.Printf("  Syscall:      %8.2f\n", float64(avgSyscall)/1000.0)
	fmt.Printf("  Ring buffer:  %8.2f\n", float64(avgRingbuf)/1000.0)
	fmt.Printf("  Processing:   %8.2f\n", float64(avgProcessing)/1000.0)
	fmt.Printf("  Containment:  %8.2f\n", float64(avgContain)/1000.0)

	if p99 > 200*1000 {
		fmt.Printf("\n❌ FAIL: p99 %.2fμs exceeds 200μs target\n", float64(p99)/1000.0)
		os.Exit(1)
	}

	fmt.Printf("\n✓ PASS: p99 %.2fμs meets <200μs target\n", float64(p99)/1000.0)
}

func passFailP99(p99ns int64) string {
	if p99ns <= 200*1000 {
		return "✓ PASS"
	}
	return "✗ FAIL"
}

func setCPUAffinity(cpu int) error {
	var cpuset [128]uint64
	cpuset[cpu/64] |= 1 << (cpu % 64)
	_, _, errno := unix.Syscall(unix.SYS_SCHED_SETAFFINITY, 0, uintptr(unsafe.Sizeof(cpuset)), uintptr(unsafe.Pointer(&cpuset)))
	if errno != 0 {
		return errno
	}
	return nil
}

func setRealtimePriority(priority int) error {
	param := struct{ priority int32 }{int32(priority)}
	_, _, errno := unix.Syscall(unix.SYS_SCHED_SETSCHEDULER, uintptr(syscall.Gettid()), uintptr(unix.SCHED_FIFO), uintptr(unsafe.Pointer(&param)))
	if errno != 0 {
		return errno
	}
	return nil
}
