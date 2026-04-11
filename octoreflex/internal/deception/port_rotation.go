// Package deception — port_rotation.go
//
// Advanced port rotation with frequency hopping.
//
// Purpose:
//   Implements sophisticated port rotation using frequency hopping spread
//   spectrum (FHSS) techniques to make port prediction computationally expensive.
//
// Features:
//   - Multiple concurrent rotation sequences
//   - Cryptographic pseudo-random hopping patterns
//   - Adaptive rotation frequency based on threat level
//   - Prediction resistance through chaotic sequences

package deception

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"encoding/binary"
	"fmt"
	"sync"
	"time"

	"go.uber.org/zap"
)

// PortRotationConfig configures the advanced port rotation system.
type PortRotationConfig struct {
	// NodeID is used as seed for deterministic rotation.
	NodeID string

	// PortBase is the base port for rotation range.
	PortBase int

	// PortRange is the number of ports available.
	PortRange int

	// MinRotationInterval is minimum time between rotations.
	MinRotationInterval time.Duration

	// MaxRotationInterval is maximum time between rotations.
	MaxRotationInterval time.Duration

	// HopSequenceLength is the length of the hopping sequence.
	HopSequenceLength int

	// EnableChaosMode adds unpredictability to rotation.
	EnableChaosMode bool

	// ThreatLevelMultiplier adjusts rotation speed based on threat level.
	// Higher threat = faster rotation.
	ThreatLevelMultiplier float64
}

// DefaultPortRotationConfig returns default configuration.
func DefaultPortRotationConfig() PortRotationConfig {
	return PortRotationConfig{
		PortBase:              32768,
		PortRange:             16384,
		MinRotationInterval:   5 * time.Minute,
		MaxRotationInterval:   1 * time.Hour,
		HopSequenceLength:     256,
		EnableChaosMode:       true,
		ThreatLevelMultiplier: 2.0,
	}
}

// PortRotation manages advanced port rotation.
type PortRotation struct {
	cfg        PortRotationConfig
	log        *zap.Logger
	mu         sync.RWMutex
	currentSeq []int
	seqIndex   int
	epoch      int64
	cipher     cipher.Block
	lastRotate time.Time
	threatLevel float64
}

// NewPortRotation creates a new port rotation manager.
func NewPortRotation(cfg PortRotationConfig, log *zap.Logger) (*PortRotation, error) {
	// Generate AES cipher for PRNG
	key := sha256.Sum256([]byte(cfg.NodeID))
	block, err := aes.NewCipher(key[:])
	if err != nil {
		return nil, fmt.Errorf("create cipher: %w", err)
	}

	pr := &PortRotation{
		cfg:        cfg,
		log:        log,
		cipher:     block,
		lastRotate: time.Now(),
	}

	// Generate initial hopping sequence
	pr.generateHoppingSequence()

	return pr, nil
}

// GetCurrentPort returns the current port for a given service ID.
func (pr *PortRotation) GetCurrentPort(serviceID string) int {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	// Hash service ID to get index into sequence
	hash := sha256.Sum256([]byte(serviceID))
	idx := int(binary.BigEndian.Uint32(hash[:4])) % len(pr.currentSeq)

	return pr.currentSeq[idx]
}

// GetNextPort returns the next port in the rotation sequence.
func (pr *PortRotation) GetNextPort(serviceID string) int {
	pr.mu.Lock()
	defer pr.mu.Unlock()

	// Advance sequence index
	pr.seqIndex = (pr.seqIndex + 1) % len(pr.currentSeq)

	// Check if rotation needed
	if pr.shouldRotate() {
		pr.generateHoppingSequence()
		pr.lastRotate = time.Now()
		pr.epoch++
		pr.log.Info("port sequence rotated",
			zap.Int64("epoch", pr.epoch),
			zap.Float64("threat_level", pr.threatLevel))
	}

	hash := sha256.Sum256([]byte(serviceID))
	idx := int(binary.BigEndian.Uint32(hash[:4])) % len(pr.currentSeq)

	return pr.currentSeq[idx]
}

// SetThreatLevel adjusts rotation speed based on threat level (0.0 - 1.0).
func (pr *PortRotation) SetThreatLevel(level float64) {
	pr.mu.Lock()
	defer pr.mu.Unlock()
	pr.threatLevel = level
	pr.log.Debug("threat level updated", zap.Float64("level", level))
}

// shouldRotate determines if rotation is needed.
func (pr *PortRotation) shouldRotate() bool {
	elapsed := time.Since(pr.lastRotate)

	// Calculate interval based on threat level
	baseInterval := pr.cfg.MaxRotationInterval
	if pr.threatLevel > 0 {
		multiplier := 1.0 - (pr.threatLevel * pr.cfg.ThreatLevelMultiplier)
		if multiplier < 0 {
			multiplier = 0
		}
		baseInterval = time.Duration(float64(pr.cfg.MaxRotationInterval) * multiplier)
	}

	if baseInterval < pr.cfg.MinRotationInterval {
		baseInterval = pr.cfg.MinRotationInterval
	}

	return elapsed >= baseInterval
}

// generateHoppingSequence generates a new frequency hopping sequence.
func (pr *PortRotation) generateHoppingSequence() {
	pr.currentSeq = make([]int, pr.cfg.HopSequenceLength)

	// Use AES-CTR as cryptographic PRNG
	nonce := make([]byte, pr.cipher.BlockSize())
	binary.BigEndian.PutUint64(nonce, uint64(pr.epoch))

	stream := cipher.NewCTR(pr.cipher, nonce)
	buf := make([]byte, pr.cfg.HopSequenceLength*4)
	stream.XORKeyStream(buf, buf)

	// Generate ports ensuring no duplicates in sequence
	used := make(map[int]bool)
	for i := 0; i < pr.cfg.HopSequenceLength; i++ {
		port := pr.generateUniquePort(buf[i*4:(i+1)*4], used)
		pr.currentSeq[i] = port
		used[port] = true
	}

	// Apply chaos if enabled
	if pr.cfg.EnableChaosMode {
		pr.applyChaos()
	}

	pr.seqIndex = 0
}

// generateUniquePort generates a unique port not in the used set.
func (pr *PortRotation) generateUniquePort(seed []byte, used map[int]bool) int {
	for attempt := 0; attempt < 100; attempt++ {
		val := binary.BigEndian.Uint32(seed)
		port := pr.cfg.PortBase + int(val%uint32(pr.cfg.PortRange))

		if !used[port] {
			return port
		}

		// Rehash for next attempt
		hash := sha256.Sum256(seed)
		seed = hash[:4]
	}

	// Fallback: linear search
	for port := pr.cfg.PortBase; port < pr.cfg.PortBase+pr.cfg.PortRange; port++ {
		if !used[port] {
			return port
		}
	}

	return pr.cfg.PortBase
}

// applyChaos adds unpredictable perturbations to the sequence.
func (pr *PortRotation) applyChaos() {
	// Use logistic map for chaotic shuffling
	// x_{n+1} = r * x_n * (1 - x_n), r = 3.9 (chaotic regime)
	r := 3.9
	x := 0.5

	// Perform chaotic swaps
	for i := 0; i < len(pr.currentSeq)/2; i++ {
		x = r * x * (1 - x)
		idx1 := int(x * float64(len(pr.currentSeq)-1))

		x = r * x * (1 - x)
		idx2 := int(x * float64(len(pr.currentSeq)-1))

		pr.currentSeq[idx1], pr.currentSeq[idx2] = pr.currentSeq[idx2], pr.currentSeq[idx1]
	}
}

// GetSequenceInfo returns information about the current sequence.
func (pr *PortRotation) GetSequenceInfo() SequenceInfo {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	return SequenceInfo{
		Epoch:         pr.epoch,
		SequenceIndex: pr.seqIndex,
		SequenceLen:   len(pr.currentSeq),
		LastRotation:  pr.lastRotate,
		NextRotation:  pr.estimateNextRotation(),
		ThreatLevel:   pr.threatLevel,
	}
}

// estimateNextRotation estimates when next rotation will occur.
func (pr *PortRotation) estimateNextRotation() time.Time {
	elapsed := time.Since(pr.lastRotate)
	baseInterval := pr.cfg.MaxRotationInterval

	if pr.threatLevel > 0 {
		multiplier := 1.0 - (pr.threatLevel * pr.cfg.ThreatLevelMultiplier)
		if multiplier < 0 {
			multiplier = 0
		}
		baseInterval = time.Duration(float64(pr.cfg.MaxRotationInterval) * multiplier)
	}

	if baseInterval < pr.cfg.MinRotationInterval {
		baseInterval = pr.cfg.MinRotationInterval
	}

	return pr.lastRotate.Add(baseInterval)
}

// SequenceInfo provides information about the rotation sequence.
type SequenceInfo struct {
	Epoch         int64
	SequenceIndex int
	SequenceLen   int
	LastRotation  time.Time
	NextRotation  time.Time
	ThreatLevel   float64
}

// PredictPortAtTime predicts the port at a future time (for legitimate clients).
// This requires knowledge of the NodeID and sequence generation algorithm.
func (pr *PortRotation) PredictPortAtTime(serviceID string, t time.Time) int {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	// Calculate which epoch t falls into
	// This is simplified - real implementation would need precise epoch tracking
	futureEpoch := pr.epoch
	if t.After(pr.estimateNextRotation()) {
		futureEpoch++
	}

	// Generate sequence for that epoch
	tempPR := &PortRotation{
		cfg:    pr.cfg,
		cipher: pr.cipher,
		epoch:  futureEpoch,
	}
	tempPR.generateHoppingSequence()

	hash := sha256.Sum256([]byte(serviceID))
	idx := int(binary.BigEndian.Uint32(hash[:4])) % len(tempPR.currentSeq)

	return tempPR.currentSeq[idx]
}

// PortHint contains information for legitimate clients to track ports.
type PortHint struct {
	ServiceID    string    `json:"service_id"`
	CurrentPort  int       `json:"current_port"`
	Epoch        int64     `json:"epoch"`
	ValidUntil   time.Time `json:"valid_until"`
	NodeID       string    `json:"node_id"`
	SequenceHash string    `json:"sequence_hash"`
}

// GenerateHint generates a hint for legitimate clients.
func (pr *PortRotation) GenerateHint(serviceID string) PortHint {
	pr.mu.RLock()
	defer pr.mu.RUnlock()

	// Hash the sequence for verification
	seqBytes := make([]byte, len(pr.currentSeq)*4)
	for i, port := range pr.currentSeq {
		binary.BigEndian.PutUint32(seqBytes[i*4:], uint32(port))
	}
	hash := sha256.Sum256(seqBytes)

	return PortHint{
		ServiceID:    serviceID,
		CurrentPort:  pr.GetCurrentPort(serviceID),
		Epoch:        pr.epoch,
		ValidUntil:   pr.estimateNextRotation(),
		NodeID:       pr.cfg.NodeID,
		SequenceHash: fmt.Sprintf("%x", hash[:8]),
	}
}
