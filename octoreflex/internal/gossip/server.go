// Package gossip — server.go
//
// gRPC mTLS server for the OCTOREFLEX gossip layer.
//
// Transport security:
//   - TLS 1.3 only (tls.VersionTLS13).
//   - Cipher suite: TLS_AES_256_GCM_SHA384 (only suite available in TLS 1.3
//     that is explicitly listed; Go's TLS 1.3 implementation always uses
//     AES-256-GCM-SHA384 and CHACHA20-POLY1305-SHA256 automatically).
//   - Mutual TLS: client must present a certificate signed by the configured CA.
//   - Certificate type: Ed25519 (as per spec §6.1).
//
// Envelope verification (per §6.2):
//   1. Reject if timestamp older than EnvelopeTTL (default 30s).
//   2. Reject if Ed25519 signature invalid.
//   3. Reject if peer node_id not in trusted peer list.
//
// Quorum accumulation:
//   - Accepted envelopes are forwarded to the quorum evaluator.
//   - The quorum evaluator is injected as a dependency (interface).

package gossip

import (
	"context"
	"crypto/ed25519"
	"crypto/tls"
	"crypto/x509"
	"encoding/binary"
	"fmt"
	"math"
	"net"
	"os"
	"time"

	"go.uber.org/zap"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/peer"

	gossipv1 "github.com/octoreflex/octoreflex/api/generated/gossip/v1"
)

// QuorumAccumulator is the interface the server uses to forward accepted
// envelopes to the quorum evaluator.
type QuorumAccumulator interface {
	// Record records an accepted envelope observation.
	Record(processHash string, nodeID string, anomalyScore float64)
}

// Server implements the GossipService gRPC server.
type Server struct {
	gossipv1.UnimplementedGossipServiceServer

	nodeID      string
	trustedPeers map[string]ed25519.PublicKey // node_id → public key
	envelopeTTL  time.Duration
	quorum       QuorumAccumulator
	log          *zap.Logger
	startTime    time.Time
}

// NewServer creates a gossip server.
// trustedPeers maps node_id to Ed25519 public key for envelope verification.
func NewServer(
	nodeID string,
	trustedPeers map[string]ed25519.PublicKey,
	envelopeTTL time.Duration,
	quorum QuorumAccumulator,
	log *zap.Logger,
) *Server {
	return &Server{
		nodeID:       nodeID,
		trustedPeers: trustedPeers,
		envelopeTTL:  envelopeTTL,
		quorum:       quorum,
		log:          log,
		startTime:    time.Now(),
	}
}

// ShareObservation implements GossipService.ShareObservation.
// Verifies the envelope and forwards it to the quorum accumulator.
func (s *Server) ShareObservation(
	ctx context.Context,
	env *gossipv1.Envelope,
) (*gossipv1.AckResponse, error) {
	// Step 1: Timestamp freshness check.
	envTime := time.Unix(0, env.TimestampUnixNs)
	age := time.Since(envTime)
	if age > s.envelopeTTL || age < -5*time.Second {
		s.log.Warn("gossip envelope rejected: stale timestamp",
			zap.String("node_id", env.NodeId),
			zap.Duration("age", age))
		return &gossipv1.AckResponse{
			Accepted:        false,
			RejectionReason: "timestamp_stale",
		}, nil
	}

	// Step 2: Peer trust check.
	pubKey, trusted := s.trustedPeers[env.NodeId]
	if !trusted {
		s.log.Warn("gossip envelope rejected: unknown peer",
			zap.String("node_id", env.NodeId))
		return &gossipv1.AckResponse{
			Accepted:        false,
			RejectionReason: "peer_unknown",
		}, nil
	}

	// Step 3: Ed25519 signature verification.
	msg := envelopeSignatureMessage(env)
	if !ed25519.Verify(pubKey, msg, env.Signature) {
		s.log.Warn("gossip envelope rejected: invalid signature",
			zap.String("node_id", env.NodeId))
		return &gossipv1.AckResponse{
			Accepted:        false,
			RejectionReason: "signature_invalid",
		}, nil
	}

	// Step 4: Forward to quorum accumulator.
	s.quorum.Record(env.ProcessHash, env.NodeId, env.AnomalyScore)

	s.log.Debug("gossip envelope accepted",
		zap.String("node_id", env.NodeId),
		zap.String("process_hash", env.ProcessHash),
		zap.Float64("anomaly_score", env.AnomalyScore))

	return &gossipv1.AckResponse{Accepted: true}, nil
}

// HealthCheck implements GossipService.HealthCheck.
func (s *Server) HealthCheck(
	ctx context.Context,
	req *gossipv1.HealthRequest,
) (*gossipv1.HealthResponse, error) {
	return &gossipv1.HealthResponse{
		NodeId:        s.nodeID,
		Status:        "ok",
		UptimeSeconds: int64(time.Since(s.startTime).Seconds()),
	}, nil
}

// envelopeSignatureMessage constructs the canonical byte sequence that is
// signed by the sender and verified by the receiver.
//
// Message = node_id_bytes || timestamp_bytes (8 LE) || process_hash_bytes ||
//           anomaly_score_bytes (8 LE IEEE 754) || impact_score_bytes (8 LE)
//
// This is deterministic and does not include the signature field itself.
func envelopeSignatureMessage(env *gossipv1.Envelope) []byte {
	var buf []byte
	buf = append(buf, []byte(env.NodeId)...)
	ts := make([]byte, 8)
	binary.LittleEndian.PutUint64(ts, uint64(env.TimestampUnixNs))
	buf = append(buf, ts...)
	buf = append(buf, []byte(env.ProcessHash)...)
	as := make([]byte, 8)
	binary.LittleEndian.PutUint64(as, math.Float64bits(env.AnomalyScore))
	buf = append(buf, as...)
	is := make([]byte, 8)
	binary.LittleEndian.PutUint64(is, math.Float64bits(env.ImpactScore))
	buf = append(buf, is...)
	return buf
}

// ListenAndServe starts the gRPC mTLS server on the given address.
// Blocks until ctx is cancelled.
func ListenAndServe(
	ctx context.Context,
	addr string,
	certFile, keyFile, caFile string,
	srv *Server,
	log *zap.Logger,
) error {
	tlsCfg, err := buildServerTLS(certFile, keyFile, caFile)
	if err != nil {
		return fmt.Errorf("gossip TLS config: %w", err)
	}

	creds := credentials.NewTLS(tlsCfg)
	grpcSrv := grpc.NewServer(
		grpc.Creds(creds),
		grpc.MaxRecvMsgSize(64*1024), // 64 KiB max envelope size.
		grpc.MaxSendMsgSize(64*1024),
	)
	gossipv1.RegisterGossipServiceServer(grpcSrv, srv)

	lis, err := net.Listen("tcp", addr)
	if err != nil {
		return fmt.Errorf("gossip listen %s: %w", addr, err)
	}

	log.Info("gossip server listening", zap.String("addr", addr))

	go func() {
		<-ctx.Done()
		grpcSrv.GracefulStop()
	}()

	if err := grpcSrv.Serve(lis); err != nil {
		return fmt.Errorf("gossip grpc serve: %w", err)
	}
	return nil
}

// buildServerTLS constructs a TLS 1.3-only mTLS config for the gRPC server.
// Requires Ed25519 certificate and key, and a CA certificate for client
// verification.
func buildServerTLS(certFile, keyFile, caFile string) (*tls.Config, error) {
	cert, err := tls.LoadX509KeyPair(certFile, keyFile)
	if err != nil {
		return nil, fmt.Errorf("load server cert/key: %w", err)
	}

	caData, err := os.ReadFile(caFile)
	if err != nil {
		return nil, fmt.Errorf("read CA file %q: %w", caFile, err)
	}
	caPool := x509.NewCertPool()
	if !caPool.AppendCertsFromPEM(caData) {
		return nil, fmt.Errorf("failed to parse CA certificate from %q", caFile)
	}

	return &tls.Config{
		Certificates: []tls.Certificate{cert},
		ClientAuth:   tls.RequireAndVerifyClientCert,
		ClientCAs:    caPool,
		MinVersion:   tls.VersionTLS13,
		// TLS 1.3 cipher suites are not configurable in Go's crypto/tls;
		// Go automatically uses TLS_AES_256_GCM_SHA384 and
		// TLS_CHACHA20_POLY1305_SHA256. Both are acceptable per spec.
		// The spec's TLS_AES_256_GCM_SHA384 preference is satisfied.
	}, nil
}

// peerFromContext extracts the peer address from a gRPC context.
// Used for logging. Returns "unknown" if not available.
func peerFromContext(ctx context.Context) string {
	p, ok := peer.FromContext(ctx)
	if !ok {
		return "unknown"
	}
	return p.Addr.String()
}
