// Package main — cmd/octoreflex-sim/main.go
//
// OCTOREFLEX Dominance Simulator.
//
// Purpose: Validate the mathematical dominance condition before release.
// The dominance condition states that OCTOREFLEX's containment response
// must dominate the attacker's mutation rate across all simulated scenarios.
//
// Mathematical model (from spec §15):
//
// Attacker mutation model:
//   m_{t+1} = clamp(m_t + λ₁ * A_t - λ₂ * (1 - U_t), 0, 1)
//
// Where:
//   m_t  = attacker mutation rate at time t ∈ [0, 1]
//   A_t  = OCTOREFLEX anomaly score at time t (sampled from scenario)
//   U_t  = OCTOREFLEX utility (containment effectiveness) ∈ [0, 1]
//   λ₁   = attacker adaptation rate (how fast attacker responds to detection)
//   λ₂   = defender suppression rate (how fast OCTOREFLEX suppresses mutation)
//
// Dominance condition:
//   P(m_T < m_0) > 0.95  over T=10000 simulation steps
//
// Where m_0 = initial mutation rate and m_T = final mutation rate.
// If this condition holds, OCTOREFLEX is said to dominate the attacker.
//
// Success probability:
//   P_success = logistic(1.0 - m_t)  (probability of successful containment)
//
// Output: per-step CSV to stdout (step, mutation_rate, success_prob)
// Summary: dominance condition result to stderr.
//
// Usage:
//   octoreflex-sim [flags]
//   octoreflex-sim -steps 10000 -lambda1 0.4 -lambda2 0.6 -m0 0.2 -U 1.0

package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"math"
	"math/rand"
	"os"
	"strconv"
	"time"
)

func main() {
	// ── Flags ─────────────────────────────────────────────────────────────────
	steps   := flag.Int("steps", 10000, "Number of simulation steps")
	lambda1 := flag.Float64("lambda1", 0.4, "Attacker adaptation rate λ₁")
	lambda2 := flag.Float64("lambda2", 0.6, "Defender suppression rate λ₂")
	m0      := flag.Float64("m0", 0.2, "Initial mutation rate m₀ ∈ [0,1]")
	U       := flag.Float64("U", 1.0, "OCTOREFLEX utility U ∈ [0,1]")
	seed    := flag.Int64("seed", time.Now().UnixNano(), "Random seed")
	flag.Parse()

	// Validate inputs.
	if *m0 < 0 || *m0 > 1 {
		fmt.Fprintln(os.Stderr, "ERROR: m0 must be in [0, 1]")
		os.Exit(1)
	}
	if *U < 0 || *U > 1 {
		fmt.Fprintln(os.Stderr, "ERROR: U must be in [0, 1]")
		os.Exit(1)
	}
	if *lambda1 < 0 || *lambda2 < 0 {
		fmt.Fprintln(os.Stderr, "ERROR: lambda1 and lambda2 must be >= 0")
		os.Exit(1)
	}

	rng := rand.New(rand.NewSource(*seed))

	// ── Simulation ────────────────────────────────────────────────────────────
	sim := NewSimulator(*steps, *lambda1, *lambda2, *m0, *U, rng)
	results := sim.Run()

	// ── Output: CSV to stdout ─────────────────────────────────────────────────
	w := csv.NewWriter(os.Stdout)
	_ = w.Write([]string{"step", "mutation_rate", "anomaly_score", "success_prob"})
	for _, r := range results {
		_ = w.Write([]string{
			strconv.Itoa(r.Step),
			strconv.FormatFloat(r.MutationRate, 'f', 6, 64),
			strconv.FormatFloat(r.AnomalyScore, 'f', 6, 64),
			strconv.FormatFloat(r.SuccessProb, 'f', 6, 64),
		})
	}
	w.Flush()

	// ── Dominance condition evaluation ────────────────────────────────────────
	finalM := results[len(results)-1].MutationRate
	dominated := finalM < *m0

	// Count steps where mutation rate decreased.
	decreasedCount := 0
	for _, r := range results {
		if r.MutationRate < *m0 {
			decreasedCount++
		}
	}
	dominanceProbability := float64(decreasedCount) / float64(*steps)

	fmt.Fprintf(os.Stderr, "\n=== DOMINANCE CONDITION RESULT ===\n")
	fmt.Fprintf(os.Stderr, "Initial mutation rate m₀:  %.4f\n", *m0)
	fmt.Fprintf(os.Stderr, "Final mutation rate m_T:   %.4f\n", finalM)
	fmt.Fprintf(os.Stderr, "Steps with m < m₀:         %d / %d (%.1f%%)\n",
		decreasedCount, *steps, dominanceProbability*100)
	fmt.Fprintf(os.Stderr, "Dominance condition (P > 0.95): %v\n",
		dominanceProbability > 0.95)

	if dominated && dominanceProbability > 0.95 {
		fmt.Fprintf(os.Stderr, "RESULT: PASS — OCTOREFLEX dominates attacker\n")
		os.Exit(0)
	} else {
		fmt.Fprintf(os.Stderr, "RESULT: FAIL — dominance condition not satisfied\n")
		fmt.Fprintf(os.Stderr, "  Adjust λ₂ (defender suppression rate) or U (utility).\n")
		os.Exit(2)
	}
}

// StepResult holds the output of a single simulation step.
type StepResult struct {
	Step         int
	MutationRate float64
	AnomalyScore float64
	SuccessProb  float64
}

// Simulator runs the dominance simulation.
type Simulator struct {
	steps   int
	lambda1 float64
	lambda2 float64
	m0      float64
	U       float64
	rng     *rand.Rand
}

// NewSimulator creates a configured Simulator.
func NewSimulator(steps int, lambda1, lambda2, m0, U float64, rng *rand.Rand) *Simulator {
	return &Simulator{
		steps:   steps,
		lambda1: lambda1,
		lambda2: lambda2,
		m0:      m0,
		U:       U,
		rng:     rng,
	}
}

// Run executes the simulation and returns per-step results.
// Complexity: O(steps). Memory: O(steps) for result slice.
func (s *Simulator) Run() []StepResult {
	results := make([]StepResult, s.steps)
	m := s.m0

	for t := 0; t < s.steps; t++ {
		// Sample anomaly score from a half-normal distribution.
		// Mean ≈ 2.5, representing a realistic anomaly signal.
		A := math.Abs(s.rng.NormFloat64()) * 2.5

		// Attacker mutation update:
		// m_{t+1} = clamp(m_t + λ₁ * A_t - λ₂ * (1 - U_t), 0, 1)
		delta := s.lambda1*A - s.lambda2*(1.0-s.U)
		m = clamp(m+delta, 0.0, 1.0)

		// Success probability: logistic(1.0 - m)
		pSucc := logistic(1.0 - m)

		results[t] = StepResult{
			Step:         t,
			MutationRate: m,
			AnomalyScore: A,
			SuccessProb:  pSucc,
		}
	}

	return results
}

// logistic computes the logistic (sigmoid) function: 1 / (1 + e^(-x)).
func logistic(x float64) float64 {
	return 1.0 / (1.0 + math.Exp(-x))
}

// clamp restricts v to the range [lo, hi].
func clamp(v, lo, hi float64) float64 {
	if v < lo {
		return lo
	}
	if v > hi {
		return hi
	}
	return v
}
