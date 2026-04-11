// Package deception — cost_amplifier.go
//
// Cost amplification mechanisms to maximize attacker resource expenditure.
//
// Purpose:
//   Implements various techniques to force attackers to waste CPU, bandwidth,
//   and time resources while attempting to compromise the system.
//
// Features:
//   - Computational proof-of-work challenges
//   - Bandwidth amplification via large responses
//   - Timing attacks to slow down attackers
//   - Resource exhaustion through fake operations

package deception

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"math"
	"sync"
	"sync/atomic"
	"time"

	"go.uber.org/zap"
)

// CostAmplifierConfig configures cost amplification mechanisms.
type CostAmplifierConfig struct {
	// EnablePOW enables proof-of-work challenges.
	EnablePOW bool

	// POWDifficulty is the number of leading zero bits required.
	// Higher values require exponentially more CPU.
	POWDifficulty int

	// EnableBandwidthWaste enables bandwidth amplification.
	EnableBandwidthWaste bool

	// BandwidthAmplificationFactor multiplies response size.
	// E.g., factor of 100 means 1KB request gets 100KB response.
	BandwidthAmplificationFactor int

	// EnableSlowdown enables artificial delays.
	EnableSlowdown bool

	// BaseDelay is the minimum delay for responses.
	BaseDelay time.Duration

	// MaxDelay is the maximum delay for responses.
	MaxDelay time.Duration

	// EnableMemoryPressure enables memory-intensive operations.
	EnableMemoryPressure bool

	// MemoryPressureMB is the amount of memory to allocate.
	MemoryPressureMB int
}

// DefaultCostAmplifierConfig returns default configuration.
func DefaultCostAmplifierConfig() CostAmplifierConfig {
	return CostAmplifierConfig{
		EnablePOW:                    true,
		POWDifficulty:                20, // ~1 second on modern CPU
		EnableBandwidthWaste:         true,
		BandwidthAmplificationFactor: 100,
		EnableSlowdown:               true,
		BaseDelay:                    500 * time.Millisecond,
		MaxDelay:                     30 * time.Second,
		EnableMemoryPressure:         true,
		MemoryPressureMB:             100,
	}
}

// CostAmplifier implements cost amplification mechanisms.
type CostAmplifier struct {
	cfg              CostAmplifierConfig
	log              *zap.Logger
	mu               sync.RWMutex
	totalCPUCost     uint64 // Estimated CPU seconds wasted
	totalBandwidth   uint64 // Bytes sent
	totalDelay       uint64 // Milliseconds of delay imposed
	challengeCount   uint64
	successfulSolves uint64
}

// NewCostAmplifier creates a new cost amplifier.
func NewCostAmplifier(cfg CostAmplifierConfig, log *zap.Logger) *CostAmplifier {
	return &CostAmplifier{
		cfg: cfg,
		log: log,
	}
}

// GeneratePOWChallenge generates a proof-of-work challenge.
func (ca *CostAmplifier) GeneratePOWChallenge() POWChallenge {
	if !ca.cfg.EnablePOW {
		return POWChallenge{}
	}

	// Generate random challenge data
	challengeData := make([]byte, 32)
	rand.Read(challengeData)

	challenge := POWChallenge{
		Data:       hex.EncodeToString(challengeData),
		Difficulty: ca.cfg.POWDifficulty,
		Timestamp:  time.Now(),
	}

	atomic.AddUint64(&ca.challengeCount, 1)

	ca.log.Debug("POW challenge generated",
		zap.Int("difficulty", ca.cfg.POWDifficulty),
		zap.String("data", challenge.Data[:16]+"..."))

	return challenge
}

// VerifyPOW verifies a proof-of-work solution.
func (ca *CostAmplifier) VerifyPOW(challenge POWChallenge, nonce uint64) bool {
	if !ca.cfg.EnablePOW {
		return true
	}

	// Check if challenge is too old (5 minutes)
	if time.Since(challenge.Timestamp) > 5*time.Minute {
		ca.log.Warn("POW challenge expired")
		return false
	}

	// Compute hash(challenge + nonce)
	data := challenge.Data + fmt.Sprintf("%016x", nonce)
	hash := sha256.Sum256([]byte(data))

	// Count leading zero bits
	leadingZeros := countLeadingZeroBits(hash[:])

	verified := leadingZeros >= challenge.Difficulty

	if verified {
		atomic.AddUint64(&ca.successfulSolves, 1)
		
		// Estimate CPU time (exponential with difficulty)
		cpuSeconds := uint64(math.Pow(2, float64(challenge.Difficulty-10)))
		atomic.AddUint64(&ca.totalCPUCost, cpuSeconds)

		ca.log.Info("POW verified",
			zap.Uint64("nonce", nonce),
			zap.Int("leading_zeros", leadingZeros),
			zap.Uint64("estimated_cpu_seconds", cpuSeconds))
	} else {
		ca.log.Warn("POW verification failed",
			zap.Uint64("nonce", nonce),
			zap.Int("leading_zeros", leadingZeros),
			zap.Int("required", challenge.Difficulty))
	}

	return verified
}

// AmplifyBandwidth generates amplified response data.
func (ca *CostAmplifier) AmplifyBandwidth(requestSize int) []byte {
	if !ca.cfg.EnableBandwidthWaste {
		return nil
	}

	responseSize := requestSize * ca.cfg.BandwidthAmplificationFactor
	if responseSize > 10*1024*1024 { // Cap at 10MB
		responseSize = 10 * 1024 * 1024
	}

	// Generate random data
	data := make([]byte, responseSize)
	rand.Read(data)

	atomic.AddUint64(&ca.totalBandwidth, uint64(responseSize))

	ca.log.Debug("bandwidth amplified",
		zap.Int("request_size", requestSize),
		zap.Int("response_size", responseSize),
		zap.Int("amplification_factor", ca.cfg.BandwidthAmplificationFactor))

	return data
}

// ApplySlowdown returns a delay duration based on threat level.
func (ca *CostAmplifier) ApplySlowdown(threatLevel float64) time.Duration {
	if !ca.cfg.EnableSlowdown {
		return 0
	}

	// Scale delay based on threat level (0.0 - 1.0)
	delayRange := float64(ca.cfg.MaxDelay - ca.cfg.BaseDelay)
	delay := ca.cfg.BaseDelay + time.Duration(delayRange*threatLevel)

	if delay > ca.cfg.MaxDelay {
		delay = ca.cfg.MaxDelay
	}

	atomic.AddUint64(&ca.totalDelay, uint64(delay.Milliseconds()))

	ca.log.Debug("slowdown applied",
		zap.Float64("threat_level", threatLevel),
		zap.Duration("delay", delay))

	return delay
}

// ApplyMemoryPressure allocates memory to pressure attacker.
func (ca *CostAmplifier) ApplyMemoryPressure() []byte {
	if !ca.cfg.EnableMemoryPressure {
		return nil
	}

	// Allocate and fill memory
	size := ca.cfg.MemoryPressureMB * 1024 * 1024
	data := make([]byte, size)
	rand.Read(data)

	ca.log.Debug("memory pressure applied",
		zap.Int("mb", ca.cfg.MemoryPressureMB))

	return data
}

// GetStats returns cost amplification statistics.
func (ca *CostAmplifier) GetStats() CostAmplifierStats {
	return CostAmplifierStats{
		TotalChallenges:     atomic.LoadUint64(&ca.challengeCount),
		SuccessfulSolves:    atomic.LoadUint64(&ca.successfulSolves),
		EstimatedCPUSeconds: atomic.LoadUint64(&ca.totalCPUCost),
		TotalBytesAmplified: atomic.LoadUint64(&ca.totalBandwidth),
		TotalDelayMs:        atomic.LoadUint64(&ca.totalDelay),
	}
}

// CalculateCostUSD estimates the cost imposed in USD.
func (ca *CostAmplifier) CalculateCostUSD() CostBreakdown {
	stats := ca.GetStats()

	// CPU cost: $0.10 per CPU hour
	cpuHours := float64(stats.EstimatedCPUSeconds) / 3600.0
	cpuCost := cpuHours * 0.10

	// Bandwidth cost: $0.10 per GB
	bandwidthGB := float64(stats.TotalBytesAmplified) / (1024 * 1024 * 1024)
	bandwidthCost := bandwidthGB * 0.10

	// Time cost: $50 per hour (attacker's time value)
	timeHours := float64(stats.EstimatedCPUSeconds) / 3600.0
	timeCost := timeHours * 50.0

	totalCost := cpuCost + bandwidthCost + timeCost

	return CostBreakdown{
		TotalCostUSD:    totalCost,
		CPUCostUSD:      cpuCost,
		BandwidthCostUSD: bandwidthCost,
		TimeCostUSD:     timeCost,
		CPUHoursWasted:  cpuHours,
		BandwidthGBWasted: bandwidthGB,
	}
}

// POWChallenge represents a proof-of-work challenge.
type POWChallenge struct {
	Data       string    // Challenge data (hex encoded)
	Difficulty int       // Number of leading zero bits required
	Timestamp  time.Time // When challenge was created
}

// CostAmplifierStats contains statistics about cost amplification.
type CostAmplifierStats struct {
	TotalChallenges     uint64
	SuccessfulSolves    uint64
	EstimatedCPUSeconds uint64
	TotalBytesAmplified uint64
	TotalDelayMs        uint64
}

// CostBreakdown provides detailed cost analysis.
type CostBreakdown struct {
	TotalCostUSD      float64
	CPUCostUSD        float64
	BandwidthCostUSD  float64
	TimeCostUSD       float64
	CPUHoursWasted    float64
	BandwidthGBWasted float64
}

// countLeadingZeroBits counts the number of leading zero bits in data.
func countLeadingZeroBits(data []byte) int {
	count := 0
	for _, b := range data {
		if b == 0 {
			count += 8
			continue
		}
		// Count bits in this byte
		for i := 7; i >= 0; i-- {
			if (b & (1 << i)) == 0 {
				count++
			} else {
				return count
			}
		}
	}
	return count
}

// SolvePOW solves a proof-of-work challenge (for testing).
// In production, this would be used by legitimate clients only.
func SolvePOW(challenge POWChallenge) (uint64, error) {
	var nonce uint64 = 0
	maxAttempts := uint64(1 << 30) // Limit attempts

	for nonce < maxAttempts {
		data := challenge.Data + fmt.Sprintf("%016x", nonce)
		hash := sha256.Sum256([]byte(data))

		if countLeadingZeroBits(hash[:]) >= challenge.Difficulty {
			return nonce, nil
		}

		nonce++
	}

	return 0, fmt.Errorf("failed to solve POW after %d attempts", maxAttempts)
}
