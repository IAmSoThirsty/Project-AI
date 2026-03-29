// Package gossip — federated_baseline.go
//
// Federated baseline sharing: anonymized μ/diag(Σ) gossip between nodes.
//
// Protocol:
//   1. Every share_interval (default 5m), the local node iterates its BoltDB
//      baselines bucket and selects baselines with sample_count >= min_samples.
//   2. For each eligible baseline, it constructs a BaselineEnvelope:
//        - process_hash = sha256(binary_path) — already the BoltDB key.
//        - mean_vector = μ (full, not anonymized — only shared with mTLS peers).
//        - covariance_diagonal = diag(Σ) — not the full matrix.
//        - sample_count = number of training samples.
//        - baseline_entropy = Shannon entropy of the baseline event distribution.
//        - signature = Ed25519(node_key, canonical_bytes).
//   3. The envelope is sent to all configured peers via the ShareBaseline RPC.
//   4. Receiving nodes merge the federated baseline with their local baseline
//      using a weighted average controlled by trust_weight:
//
//        μ_merged = (1 - w) * μ_local + w * μ_federated
//        diag(Σ)_merged = (1 - w) * diag(Σ)_local + w * diag(Σ)_federated
//
//      where w = trust_weight * (sample_count_federated / (sample_count_local + sample_count_federated))
//
//      This gives higher trust to peers with more samples, and respects the
//      configured trust_weight ceiling.
//
// Privacy guarantees:
//   - Only μ and diag(Σ) are shared — not raw events or binary paths.
//   - process_hash = sha256(binary_path) — binary path is never transmitted.
//   - All communication is over mTLS (TLS 1.3) — no plaintext.
//   - Envelopes are Ed25519-signed — receivers verify authenticity.
//
// Convergence:
//   - With N nodes sharing baselines every 5m, a fresh node reaches a
//     reasonable baseline (within 10% of the cluster mean) in approximately
//     max(min_samples / event_rate, share_interval) time.
//   - This is significantly faster than waiting for a full local window
//     (which requires min_samples events from the monitored binary).

package gossip

import (
	"context"
	"crypto/ed25519"
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"math"
	"time"

	"go.uber.org/zap"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"

	gossipv1 "github.com/octoreflex/octoreflex/api/generated/gossip/v1"
)

// BaselineRecord is the local representation of a process baseline.
// Mirrors the BoltDB storage record.
type BaselineRecord struct {
	ProcessHash     string    // sha256(binary_path), hex-encoded.
	MeanVector      []float64 // Per-feature mean.
	CovDiagonal     []float64 // diag(Σ) — covariance diagonal.
	SampleCount     uint32    // Number of training samples.
	BaselineEntropy float64   // Shannon entropy of event distribution.
	UpdatedAt       time.Time
}

// BaselineStore is the interface for reading local baselines.
// Implemented by internal/storage.Store.
type BaselineStore interface {
	// ListBaselines returns all stored baselines.
	ListBaselines() ([]BaselineRecord, error)

	// MergeBaseline merges a federated baseline into the local store.
	// The merge uses the weighted average formula described above.
	MergeBaseline(rec BaselineRecord, trustWeight float64) error
}

// FederatedBaselineConfig mirrors the config struct for use in this package.
type FederatedBaselineConfig struct {
	Enabled       bool
	ShareInterval time.Duration
	MinSamples    uint32
	TrustWeight   float64
}

// FederatedBaselineManager manages periodic baseline sharing and receiving.
type FederatedBaselineManager struct {
	cfg        FederatedBaselineConfig
	nodeID     string
	privateKey ed25519.PrivateKey
	store      BaselineStore
	peers      []string // host:port
	tlsCreds   credentials.TransportCredentials
	log        *zap.Logger
}

// NewFederatedBaselineManager creates a manager for federated baseline sharing.
func NewFederatedBaselineManager(
	cfg FederatedBaselineConfig,
	nodeID string,
	privateKey ed25519.PrivateKey,
	store BaselineStore,
	peers []string,
	tlsCreds credentials.TransportCredentials,
	log *zap.Logger,
) *FederatedBaselineManager {
	return &FederatedBaselineManager{
		cfg:        cfg,
		nodeID:     nodeID,
		privateKey: privateKey,
		store:      store,
		peers:      peers,
		tlsCreds:   tlsCreds,
		log:        log,
	}
}

// Run starts the periodic baseline sharing loop.
// Blocks until ctx is cancelled.
func (m *FederatedBaselineManager) Run(ctx context.Context) {
	if !m.cfg.Enabled {
		m.log.Info("federated baseline sharing disabled")
		return
	}

	ticker := time.NewTicker(m.cfg.ShareInterval)
	defer ticker.Stop()

	m.log.Info("federated baseline manager started",
		zap.Duration("share_interval", m.cfg.ShareInterval),
		zap.Float64("trust_weight", m.cfg.TrustWeight),
		zap.Uint32("min_samples", m.cfg.MinSamples))

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			m.shareRound(ctx)
		}
	}
}

// shareRound performs one round of baseline sharing with all peers.
func (m *FederatedBaselineManager) shareRound(ctx context.Context) {
	baselines, err := m.store.ListBaselines()
	if err != nil {
		m.log.Error("federated baseline: list baselines", zap.Error(err))
		return
	}

	// Filter to eligible baselines (min_samples threshold).
	var eligible []BaselineRecord
	for _, b := range baselines {
		if b.SampleCount >= m.cfg.MinSamples {
			eligible = append(eligible, b)
		}
	}

	if len(eligible) == 0 {
		m.log.Debug("federated baseline: no eligible baselines to share",
			zap.Int("total", len(baselines)),
			zap.Uint32("min_samples", m.cfg.MinSamples))
		return
	}

	m.log.Info("federated baseline: sharing baselines",
		zap.Int("count", len(eligible)),
		zap.Int("peers", len(m.peers)))

	for _, peer := range m.peers {
		m.shareToPeer(ctx, peer, eligible)
	}
}

// shareToPeer sends all eligible baselines to a single peer.
func (m *FederatedBaselineManager) shareToPeer(ctx context.Context, peer string, baselines []BaselineRecord) {
	conn, err := grpc.DialContext(ctx, peer,
		grpc.WithTransportCredentials(m.tlsCreds),
		grpc.WithBlock(),
		grpc.WithTimeout(10*time.Second))
	if err != nil {
		m.log.Warn("federated baseline: dial peer", zap.String("peer", peer), zap.Error(err))
		return
	}
	defer conn.Close()

	client := gossipv1.NewGossipServiceClient(conn)

	sent, rejected := 0, 0
	for _, b := range baselines {
		env, err := m.buildEnvelope(b)
		if err != nil {
			m.log.Error("federated baseline: build envelope", zap.Error(err))
			continue
		}

		resp, err := client.ShareBaseline(ctx, env)
		if err != nil {
			m.log.Warn("federated baseline: ShareBaseline RPC",
				zap.String("peer", peer), zap.Error(err))
			rejected++
			continue
		}
		if !resp.Accepted {
			m.log.Debug("federated baseline: peer rejected envelope",
				zap.String("peer", peer),
				zap.String("reason", resp.RejectionReason))
			rejected++
		} else {
			sent++
		}
	}

	m.log.Info("federated baseline: share round complete",
		zap.String("peer", peer),
		zap.Int("sent", sent),
		zap.Int("rejected", rejected))
}

// buildEnvelope constructs and signs a BaselineEnvelope for a baseline record.
func (m *FederatedBaselineManager) buildEnvelope(b BaselineRecord) (*gossipv1.BaselineEnvelope, error) {
	now := time.Now().UnixNano()

	env := &gossipv1.BaselineEnvelope{
		NodeId:              m.nodeID,
		TimestampUnixNs:     now,
		ProcessHash:         b.ProcessHash,
		MeanVector:          b.MeanVector,
		CovarianceDiagonal:  b.CovDiagonal,
		SampleCount:         b.SampleCount,
		BaselineEntropy:     b.BaselineEntropy,
	}

	// Sign the canonical byte representation.
	msg := canonicalBaselineBytes(m.nodeID, now, b.ProcessHash, b.MeanVector, b.CovDiagonal)
	sig := ed25519.Sign(m.privateKey, msg)
	env.Signature = sig

	return env, nil
}

// canonicalBaselineBytes produces the deterministic byte sequence that is
// signed and verified for a BaselineEnvelope.
//
// Format (all little-endian):
//   sha256(
//     len(nodeID) [4 bytes] || nodeID ||
//     timestamp_unix_ns [8 bytes] ||
//     len(processHash) [4 bytes] || processHash ||
//     len(meanVector) [4 bytes] || meanVector[0..n] [8 bytes each] ||
//     len(covDiag) [4 bytes] || covDiag[0..n] [8 bytes each]
//   )
func canonicalBaselineBytes(nodeID string, tsNs int64, processHash string, mean, covDiag []float64) []byte {
	h := sha256.New()
	writeStr := func(s string) {
		b := make([]byte, 4)
		binary.LittleEndian.PutUint32(b, uint32(len(s)))
		h.Write(b)
		h.Write([]byte(s))
	}
	writeFloat64Slice := func(fs []float64) {
		b := make([]byte, 4)
		binary.LittleEndian.PutUint32(b, uint32(len(fs)))
		h.Write(b)
		fb := make([]byte, 8)
		for _, f := range fs {
			binary.LittleEndian.PutUint64(fb, math.Float64bits(f))
			h.Write(fb)
		}
	}
	writeStr(nodeID)
	tsBytes := make([]byte, 8)
	binary.LittleEndian.PutUint64(tsBytes, uint64(tsNs))
	h.Write(tsBytes)
	writeStr(processHash)
	writeFloat64Slice(mean)
	writeFloat64Slice(covDiag)
	return h.Sum(nil)
}

// ReceiveBaseline handles an incoming BaselineEnvelope from a peer.
// Called by the gRPC server's ShareBaseline handler.
//
// Merge formula:
//   w_eff = trust_weight * (n_fed / (n_local + n_fed))
//   μ_merged[i] = (1 - w_eff) * μ_local[i] + w_eff * μ_fed[i]
//   diag(Σ)_merged[i] = (1 - w_eff) * diag(Σ)_local[i] + w_eff * diag(Σ)_fed[i]
func (m *FederatedBaselineManager) ReceiveBaseline(
	env *gossipv1.BaselineEnvelope,
	peerPublicKey ed25519.PublicKey,
	envelopeTTL time.Duration,
) error {
	// 1. Timestamp freshness check.
	age := time.Since(time.Unix(0, env.TimestampUnixNs))
	if age > envelopeTTL || age < -30*time.Second {
		return fmt.Errorf("baseline envelope stale: age=%v ttl=%v", age, envelopeTTL)
	}

	// 2. Signature verification.
	msg := canonicalBaselineBytes(
		env.NodeId, env.TimestampUnixNs, env.ProcessHash,
		env.MeanVector, env.CovarianceDiagonal)
	if !ed25519.Verify(peerPublicKey, msg, env.Signature) {
		return fmt.Errorf("baseline envelope: invalid Ed25519 signature from node %q", env.NodeId)
	}

	// 3. Minimum samples check.
	if env.SampleCount < m.cfg.MinSamples {
		return fmt.Errorf("baseline envelope: insufficient samples (%d < %d)",
			env.SampleCount, m.cfg.MinSamples)
	}

	// 4. Validate process hash format (must be 64-char hex sha256).
	if len(env.ProcessHash) != 64 {
		return fmt.Errorf("baseline envelope: invalid process_hash length %d", len(env.ProcessHash))
	}
	if _, err := hex.DecodeString(env.ProcessHash); err != nil {
		return fmt.Errorf("baseline envelope: invalid process_hash hex: %w", err)
	}

	// 5. Merge into local store.
	rec := BaselineRecord{
		ProcessHash:     env.ProcessHash,
		MeanVector:      env.MeanVector,
		CovDiagonal:     env.CovarianceDiagonal,
		SampleCount:     env.SampleCount,
		BaselineEntropy: env.BaselineEntropy,
		UpdatedAt:       time.Now(),
	}

	if err := m.store.MergeBaseline(rec, m.cfg.TrustWeight); err != nil {
		return fmt.Errorf("baseline merge: %w", err)
	}

	m.log.Info("federated baseline: merged",
		zap.String("node", env.NodeId),
		zap.String("process_hash", env.ProcessHash[:8]+"…"),
		zap.Uint32("samples", env.SampleCount),
		zap.Float64("trust_weight", m.cfg.TrustWeight))

	return nil
}
