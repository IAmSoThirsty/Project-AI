// Package gossip — quorum.go
//
// Quorum evaluator for the OCTOREFLEX distributed gossip layer.
//
// Consistency model: eventual consistency, no leader, no coordinator.
//
// Quorum condition (from spec §6.3):
//   unique_nodes_reporting(process_hash) >= quorum_min
//
// Partition-aware fallback (§11):
//   When the fraction of reachable peers drops below PartitionThreshold
//   (default 0.5), the node enters PARTITION mode. In PARTITION mode:
//     - quorumMin is recalibrated to max(1, floor(reachablePeers * quorumFraction))
//     - Q_boost is computed against the recalibrated quorumMin
//     - A PartitionEvent is emitted to the PartitionSink for Tier 1 notification
//   When peer count recovers above PartitionThreshold, the node exits PARTITION
//   mode and restores the original quorumMin.
//
// This ensures that an isolated node can still enforce containment based on
// local observations alone (quorumMin=1), rather than silently dropping Q to 0
// because it cannot reach the swarm.
//
// Thread-safety: all methods are protected by a single RWMutex.
// The quorum map is bounded by the number of unique process hashes observed,
// which is bounded by the number of tracked PIDs (max 8192 per node).

package gossip

import (
	"math"
	"sync"
	"sync/atomic"
	"time"
)

// observation records a single node's report about a process.
type observation struct {
	nodeID       string
	anomalyScore float64
	recordedAt   time.Time
}

// PartitionMode describes the current gossip partition state of this node.
type PartitionMode int32

const (
	// PartitionModeNormal — quorum operates with the full configured quorumMin.
	PartitionModeNormal PartitionMode = 0
	// PartitionModeIsolated — quorum recalibrated to reachable peers only.
	PartitionModeIsolated PartitionMode = 1
)

// PartitionEvent is emitted when the node enters or exits partition mode.
// Tier 1 should consume this to update agent trust scores and alert operators.
type PartitionEvent struct {
	// Mode is the new partition mode.
	Mode PartitionMode
	// ReachablePeers is the number of peers currently reachable.
	ReachablePeers int
	// TotalPeers is the total configured peer count.
	TotalPeers int
	// RecalibratedQuorumMin is the quorumMin in effect during this mode.
	RecalibratedQuorumMin int
	// Timestamp is when the transition occurred.
	Timestamp time.Time
}

// PartitionSink receives PartitionEvents. Implementations must be non-blocking.
type PartitionSink interface {
	Emit(PartitionEvent)
}

// ChannelPartitionSink is a non-blocking PartitionSink backed by a channel.
// Events are dropped (and Dropped incremented) if the channel is full.
type ChannelPartitionSink struct {
	C       chan PartitionEvent
	Dropped uint64 // accessed atomically
}

// Emit implements PartitionSink. Non-blocking: drops if channel full.
func (s *ChannelPartitionSink) Emit(evt PartitionEvent) {
	select {
	case s.C <- evt:
	default:
		atomic.AddUint64(&s.Dropped, 1)
	}
}

// QuorumConfig holds configuration for the Quorum evaluator.
type QuorumConfig struct {
	// QuorumMin is the minimum number of unique nodes required for a quorum signal.
	// Must be >= 1.
	QuorumMin int

	// TTL is the observation expiry duration. Must be > 0.
	TTL time.Duration

	// TotalPeers is the total number of configured gossip peers (excluding self).
	// Used to compute the partition threshold. Must be >= 0.
	TotalPeers int

	// PartitionThreshold is the fraction of peers below which partition mode
	// is activated. Default: 0.5 (< 50% peers reachable → partition mode).
	// Range: (0, 1].
	PartitionThreshold float64

	// QuorumFraction is the fraction of reachable peers used to recalibrate
	// quorumMin in partition mode. Default: 0.5.
	// recalibratedMin = max(1, floor(reachablePeers * QuorumFraction))
	QuorumFraction float64

	// PartitionSink receives partition mode transition events.
	// May be nil (events are discarded).
	PartitionSink PartitionSink
}

// Quorum evaluates whether enough nodes have reported a process as anomalous.
// It is partition-aware: when peer reachability drops below PartitionThreshold,
// quorumMin is recalibrated to the reachable peer count.
type Quorum struct {
	mu           sync.RWMutex
	cfg          QuorumConfig
	observations map[string][]observation

	// partition state — protected by mu
	currentMode    PartitionMode
	reachablePeers int
	effectiveMin   int // quorumMin in effect (may be recalibrated)
}

// NewQuorum creates a Quorum evaluator with the given configuration.
// quorumMin must be >= 1. ttl must be > 0.
func NewQuorum(quorumMin int, ttl time.Duration) *Quorum {
	return NewQuorumWithConfig(QuorumConfig{
		QuorumMin:          quorumMin,
		TTL:                ttl,
		TotalPeers:         0,
		PartitionThreshold: 0.5,
		QuorumFraction:     0.5,
	})
}

// NewQuorumWithConfig creates a Quorum evaluator with full configuration.
func NewQuorumWithConfig(cfg QuorumConfig) *Quorum {
	if cfg.PartitionThreshold <= 0 || cfg.PartitionThreshold > 1 {
		cfg.PartitionThreshold = 0.5
	}
	if cfg.QuorumFraction <= 0 || cfg.QuorumFraction > 1 {
		cfg.QuorumFraction = 0.5
	}
	q := &Quorum{
		cfg:          cfg,
		observations: make(map[string][]observation),
		effectiveMin: cfg.QuorumMin,
	}
	go q.pruneLoop()
	return q
}

// Record implements QuorumAccumulator. Records an observation from a node.
// Idempotent: if the same node reports the same process within the TTL,
// the existing observation is updated (not duplicated).
func (q *Quorum) Record(processHash, nodeID string, anomalyScore float64) {
	q.mu.Lock()
	defer q.mu.Unlock()

	now := time.Now()
	obs := q.observations[processHash]

	// Update existing observation from this node if present.
	for i, o := range obs {
		if o.nodeID == nodeID {
			obs[i].anomalyScore = anomalyScore
			obs[i].recordedAt = now
			q.observations[processHash] = obs
			return
		}
	}

	// Append new observation.
	q.observations[processHash] = append(obs, observation{
		nodeID:       nodeID,
		anomalyScore: anomalyScore,
		recordedAt:   now,
	})
}

// UpdatePeerReachability updates the count of currently reachable peers.
// This is called by the gossip client on each health probe cycle.
// If reachablePeers / TotalPeers < PartitionThreshold, the node enters
// PARTITION mode and recalibrates quorumMin. If it recovers above the
// threshold, it exits PARTITION mode and restores the original quorumMin.
//
// Thread-safe. Non-blocking (PartitionSink.Emit is non-blocking by contract).
func (q *Quorum) UpdatePeerReachability(reachablePeers int) {
	q.mu.Lock()
	defer q.mu.Unlock()

	q.reachablePeers = reachablePeers
	totalPeers := q.cfg.TotalPeers

	// Determine whether we are in partition mode.
	var newMode PartitionMode
	var newEffectiveMin int

	if totalPeers == 0 {
		// Single-node deployment: always normal, quorumMin=1.
		newMode = PartitionModeNormal
		newEffectiveMin = 1
	} else {
		reachableFrac := float64(reachablePeers) / float64(totalPeers)
		if reachableFrac < q.cfg.PartitionThreshold {
			// Partition mode: recalibrate quorumMin to reachable peers.
			// recalibratedMin = max(1, floor(reachablePeers * QuorumFraction))
			recalibrated := int(math.Floor(float64(reachablePeers) * q.cfg.QuorumFraction))
			if recalibrated < 1 {
				recalibrated = 1
			}
			newMode = PartitionModeIsolated
			newEffectiveMin = recalibrated
		} else {
			newMode = PartitionModeNormal
			newEffectiveMin = q.cfg.QuorumMin
		}
	}

	// Emit a PartitionEvent only on mode transitions.
	if newMode != q.currentMode || newEffectiveMin != q.effectiveMin {
		q.currentMode = newMode
		q.effectiveMin = newEffectiveMin
		if q.cfg.PartitionSink != nil {
			q.cfg.PartitionSink.Emit(PartitionEvent{
				Mode:                  newMode,
				ReachablePeers:        reachablePeers,
				TotalPeers:            totalPeers,
				RecalibratedQuorumMin: newEffectiveMin,
				Timestamp:             time.Now(),
			})
		}
	}
}

// Signal returns the quorum signal Q for a process hash.
// Returns 1.0 if unique_nodes_reporting >= effectiveMin, 0.0 otherwise.
// In partition mode, effectiveMin is recalibrated to reachable peers.
func (q *Quorum) Signal(processHash string) float64 {
	q.mu.RLock()
	defer q.mu.RUnlock()

	obs := q.observations[processHash]
	unique := q.countUniqueActive(obs)
	if unique >= q.effectiveMin {
		return 1.0
	}
	return 0.0
}

// PartitionState returns the current partition mode and effective quorumMin.
// Safe for concurrent use.
func (q *Quorum) PartitionState() (mode PartitionMode, effectiveMin int, reachablePeers int) {
	q.mu.RLock()
	defer q.mu.RUnlock()
	return q.currentMode, q.effectiveMin, q.reachablePeers
}

// countUniqueActive counts observations that are within TTL.
// Must be called with at least a read lock held.
func (q *Quorum) countUniqueActive(obs []observation) int {
	cutoff := time.Now().Add(-q.cfg.TTL)
	seen := make(map[string]struct{}, len(obs))
	for _, o := range obs {
		if o.recordedAt.After(cutoff) {
			seen[o.nodeID] = struct{}{}
		}
	}
	return len(seen)
}

// pruneExpired removes observations older than TTL for all process hashes.
// Removes the process hash entry entirely if no active observations remain.
func (q *Quorum) pruneExpired() {
	q.mu.Lock()
	defer q.mu.Unlock()

	cutoff := time.Now().Add(-q.cfg.TTL)
	for hash, obs := range q.observations {
		var active []observation
		for _, o := range obs {
			if o.recordedAt.After(cutoff) {
				active = append(active, o)
			}
		}
		if len(active) == 0 {
			delete(q.observations, hash)
		} else {
			q.observations[hash] = active
		}
	}
}

// pruneLoop runs background pruning every 10 seconds.
func (q *Quorum) pruneLoop() {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()
	for range ticker.C {
		q.pruneExpired()
	}
}
