// Package quorum provides the main federated quorum coordinator for OctoReflex.
//
// The quorum system integrates:
// - SWIM gossip for membership and failure detection
// - Byzantine fault tolerance for security
// - Raft consensus for critical decisions
// - Threat intelligence database for shared IOCs
// - Network protocol for efficient communication
//
// Architecture:
//
//   ┌─────────────────────────────────────────────────────┐
//   │           OctoReflex Federated Quorum               │
//   └─────────────────────────────────────────────────────┘
//                          │
//          ┌───────────────┼───────────────┐
//          │               │               │
//     ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
//     │  SWIM   │    │  Raft   │    │ ThreatDB│
//     │ Gossip  │    │Consensus│    │  (IoCs) │
//     └────┬────┘    └────┬────┘    └────┬────┘
//          │               │               │
//     ┌────▼────────────────▼───────────────▼────┐
//     │      Network Protocol (gRPC/mTLS)        │
//     └──────────────────────────────────────────┘
//                          │
//          ┌───────────────┼───────────────┐
//          │               │               │
//     ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
//     │  Node 1 │    │  Node 2 │    │  Node 3 │
//     └─────────┘    └─────────┘    └─────────┘

package quorum

import (
	"context"
	"crypto/ed25519"
	"crypto/rand"
	"fmt"
	"sync"
	"time"

	"go.uber.org/zap"

	"github.com/octoreflex/octoreflex/internal/quorum/consensus"
	"github.com/octoreflex/octoreflex/internal/quorum/gossip"
	"github.com/octoreflex/octoreflex/internal/quorum/network"
	"github.com/octoreflex/octoreflex/internal/quorum/threatdb"
)

// Config configures the federated quorum.
type Config struct {
	NodeID     string
	ListenAddr string
	
	// Peer configuration
	SeedNodes []string          // bootstrap nodes
	Peers     map[string]string // nodeID -> address
	
	// Security
	CertFile   string
	KeyFile    string
	CAFile     string
	PrivateKey ed25519.PrivateKey
	
	// Gossip configuration
	SWIM gossip.SWIMConfig
	
	// Consensus configuration
	Raft consensus.RaftConfig
	
	// Threat database
	ThreatDBPath string
	
	// Network tuning
	MaxMessageSize int
	Compression    bool
	BatchSize      int
	BatchDelay     time.Duration
}

// DefaultConfig returns sensible defaults.
func DefaultConfig(nodeID, listenAddr string) Config {
	// Generate Ed25519 keypair
	publicKey, privateKey, _ := ed25519.GenerateKey(rand.Reader)
	_ = publicKey
	
	return Config{
		NodeID:         nodeID,
		ListenAddr:     listenAddr,
		SeedNodes:      []string{},
		Peers:          make(map[string]string),
		PrivateKey:     privateKey,
		SWIM:           gossip.DefaultSWIMConfig(),
		Raft:           consensus.DefaultRaftConfig(nodeID),
		ThreatDBPath:   "threat.db",
		MaxMessageSize: 4 * 1024 * 1024, // 4MB
		Compression:    true,
		BatchSize:      10,
		BatchDelay:     100 * time.Millisecond,
	}
}

// Quorum coordinates the federated threat consensus system.
type Quorum struct {
	cfg Config
	log *zap.Logger
	
	// Core components
	swim          *gossip.SWIM
	byzantine     *gossip.ByzantineDetector
	raft          *consensus.Raft
	threatDB      *threatdb.ThreatDB
	protocol      network.Protocol
	
	// State
	mu       sync.RWMutex
	started  bool
	shutdown chan struct{}
	wg       sync.WaitGroup
	
	// Metrics
	metrics *Metrics
}

// Metrics tracks quorum performance.
type Metrics struct {
	mu sync.RWMutex
	
	MessagesReceived   uint64
	MessagesSent       uint64
	ConsensusDecisions uint64
	ThreatsSynced      uint64
	ByzantineDetected  uint64
	MembershipChanges  uint64
}

// NewQuorum creates a new federated quorum instance.
func NewQuorum(cfg Config, log *zap.Logger) (*Quorum, error) {
	// Initialize threat database
	threatDB, err := threatdb.NewThreatDB(cfg.ThreatDBPath, log)
	if err != nil {
		return nil, fmt.Errorf("init threat db: %w", err)
	}
	
	// Initialize Byzantine detector
	byzantineCfg := gossip.DefaultByzantineConfig()
	byzantine := gossip.NewByzantineDetector(byzantineCfg, cfg.NodeID, log)
	
	// Initialize network protocol
	protocol, err := network.NewGRPCProtocol(
		cfg.NodeID,
		cfg.ListenAddr,
		cfg.Peers,
		cfg.CertFile,
		cfg.KeyFile,
		cfg.CAFile,
		log,
	)
	if err != nil {
		return nil, fmt.Errorf("init protocol: %w", err)
	}
	
	// Initialize SWIM gossip (transport will be set later)
	localMember := &gossip.Member{
		ID:          cfg.NodeID,
		Addr:        cfg.ListenAddr,
		PublicKey:   cfg.PrivateKey.Public().(ed25519.PublicKey),
		State:       gossip.StateAlive,
		Incarnation: 0,
		StateChange: time.Now(),
	}
	
	// Create SWIM transport adapter
	swimTransport := &SWIMTransportAdapter{protocol: protocol}
	
	swim := gossip.NewSWIM(
		cfg.SWIM,
		localMember,
		cfg.PrivateKey,
		swimTransport,
		log,
	)
	
	// Initialize Raft consensus
	// Create peer map
	raftPeers := make(map[string]*consensus.Peer)
	for peerID, addr := range cfg.Peers {
		raftPeers[peerID] = &consensus.Peer{
			ID:   peerID,
			Addr: addr,
			// PublicKey would be loaded from config
			Transport: &RaftTransportAdapter{protocol: protocol},
		}
	}
	
	// Create state machine for threat consensus
	stateMachine := NewThreatStateMachine(threatDB, log)
	
	raft := consensus.NewRaft(
		cfg.Raft,
		cfg.PrivateKey,
		raftPeers,
		stateMachine,
		log,
	)
	
	return &Quorum{
		cfg:       cfg,
		log:       log,
		swim:      swim,
		byzantine: byzantine,
		raft:      raft,
		threatDB:  threatDB,
		protocol:  protocol,
		shutdown:  make(chan struct{}),
		metrics:   &Metrics{},
	}, nil
}

// Start starts the quorum system.
func (q *Quorum) Start(ctx context.Context) error {
	q.mu.Lock()
	if q.started {
		q.mu.Unlock()
		return fmt.Errorf("quorum already started")
	}
	q.started = true
	q.mu.Unlock()
	
	q.log.Info("starting federated quorum",
		zap.String("node_id", q.cfg.NodeID),
		zap.String("addr", q.cfg.ListenAddr),
		zap.Int("peers", len(q.cfg.Peers)))
	
	// Start network protocol
	if err := q.protocol.Start(ctx); err != nil {
		return fmt.Errorf("start protocol: %w", err)
	}
	
	// Start SWIM gossip
	if err := q.swim.Start(ctx); err != nil {
		return fmt.Errorf("start SWIM: %w", err)
	}
	
	// Join cluster if seed nodes provided
	if len(q.cfg.SeedNodes) > 0 {
		if err := q.swim.Join(q.cfg.SeedNodes); err != nil {
			q.log.Warn("failed to join cluster", zap.Error(err))
			// Continue anyway - might be first node
		}
	}
	
	// Start Raft consensus
	if err := q.raft.Start(ctx); err != nil {
		return fmt.Errorf("start Raft: %w", err)
	}
	
	// Start background tasks
	q.wg.Add(3)
	go q.syncThreatIntel(ctx)
	go q.monitorByzantine(ctx)
	go q.handleMessages(ctx)
	
	q.log.Info("federated quorum started successfully")
	return nil
}

// Stop gracefully stops the quorum.
func (q *Quorum) Stop() error {
	q.mu.Lock()
	if !q.started {
		q.mu.Unlock()
		return nil
	}
	q.mu.Unlock()
	
	q.log.Info("stopping federated quorum")
	
	close(q.shutdown)
	
	// Stop components
	q.swim.Stop()
	q.raft.Stop()
	q.protocol.Close()
	q.threatDB.Close()
	
	q.wg.Wait()
	
	q.log.Info("federated quorum stopped")
	return nil
}

// SubmitThreat submits a threat detection for consensus.
func (q *Quorum) SubmitThreat(threat *ThreatSubmission) error {
	// Create Raft command
	cmd := consensus.Command{
		Type:      consensus.CommandIsolateProcess,
		Payload:   threat.Serialize(),
		Timestamp: time.Now(),
		ClientID:  q.cfg.NodeID,
	}
	
	// Submit to Raft
	index, term, err := q.raft.Submit(cmd)
	if err != nil {
		return fmt.Errorf("submit to raft: %w", err)
	}
	
	q.log.Info("threat submitted to consensus",
		zap.String("process_hash", threat.ProcessHash),
		zap.Uint64("index", index),
		zap.Uint64("term", term))
	
	q.metrics.mu.Lock()
	q.metrics.ConsensusDecisions++
	q.metrics.mu.Unlock()
	
	return nil
}

// AddSignature adds a threat signature to the database.
func (q *Quorum) AddSignature(sig *threatdb.Signature) error {
	return q.threatDB.AddSignature(sig)
}

// CheckThreat checks if a hash is a known threat.
func (q *Quorum) CheckThreat(hash [32]byte) (bool, float64, error) {
	sig, err := q.threatDB.GetSignature(hash)
	if err != nil {
		return false, 0, nil // not found, not an error
	}
	
	return true, sig.Severity, nil
}

// GetMembers returns current cluster members.
func (q *Quorum) GetMembers() []*gossip.Member {
	return q.swim.Members()
}

// GetLeader returns the current Raft leader.
func (q *Quorum) GetLeader() string {
	return q.raft.GetLeader()
}

// GetMetrics returns quorum metrics.
func (q *Quorum) GetMetrics() Metrics {
	q.metrics.mu.RLock()
	defer q.metrics.mu.RUnlock()
	
	return Metrics{
		MessagesReceived:   q.metrics.MessagesReceived,
		MessagesSent:       q.metrics.MessagesSent,
		ConsensusDecisions: q.metrics.ConsensusDecisions,
		ThreatsSynced:      q.metrics.ThreatsSynced,
		ByzantineDetected:  q.metrics.ByzantineDetected,
		MembershipChanges:  q.metrics.MembershipChanges,
	}
}

// syncThreatIntel periodically syncs threat intelligence with peers.
func (q *Quorum) syncThreatIntel(ctx context.Context) {
	defer q.wg.Done()
	
	ticker := time.NewTicker(5 * time.Minute)
	defer ticker.Stop()
	
	lastSync := time.Now().Add(-24 * time.Hour) // sync last 24h on startup
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-q.shutdown:
			return
		case <-ticker.C:
			q.doThreatSync(lastSync)
			lastSync = time.Now()
		}
	}
}

// doThreatSync performs threat intelligence sync.
func (q *Quorum) doThreatSync(since time.Time) {
	delta, err := q.threatDB.ExportDelta(since)
	if err != nil {
		q.log.Error("export threat delta", zap.Error(err))
		return
	}
	
	if len(delta.Signatures) == 0 && len(delta.IoCs) == 0 && len(delta.Behaviors) == 0 {
		return
	}
	
	q.log.Info("syncing threat intelligence",
		zap.Int("signatures", len(delta.Signatures)),
		zap.Int("iocs", len(delta.IoCs)),
		zap.Int("behaviors", len(delta.Behaviors)))
	
	// Serialize and broadcast
	payload, err := delta.Serialize()
	if err != nil {
		q.log.Error("serialize delta", zap.Error(err))
		return
	}
	
	msg := &network.Message{
		Type:      network.MsgThreatDelta,
		Sender:    q.cfg.NodeID,
		Payload:   payload,
		Timestamp: time.Now(),
	}
	
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	
	if err := q.protocol.Broadcast(ctx, msg); err != nil {
		q.log.Error("broadcast threat delta", zap.Error(err))
	}
	
	q.metrics.mu.Lock()
	q.metrics.ThreatsSynced++
	q.metrics.mu.Unlock()
}

// monitorByzantine monitors for Byzantine behavior.
func (q *Quorum) monitorByzantine(ctx context.Context) {
	defer q.wg.Done()
	
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-q.shutdown:
			return
		case <-ticker.C:
			q.checkByzantineNodes()
		}
	}
}

// checkByzantineNodes checks for suspected Byzantine nodes.
func (q *Quorum) checkByzantineNodes() {
	suspected := q.byzantine.SuspectedNodes()
	if len(suspected) == 0 {
		return
	}
	
	q.log.Warn("Byzantine nodes detected",
		zap.Strings("nodes", suspected),
		zap.Int("count", len(suspected)))
	
	q.metrics.mu.Lock()
	q.metrics.ByzantineDetected += uint64(len(suspected))
	q.metrics.mu.Unlock()
	
	// In production: trigger alerts, isolation, etc.
}

// handleMessages processes incoming network messages.
func (q *Quorum) handleMessages(ctx context.Context) {
	defer q.wg.Done()
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-q.shutdown:
			return
		case msg := <-q.protocol.Receive():
			q.handleMessage(msg)
		}
	}
}

// handleMessage handles a single incoming message.
func (q *Quorum) handleMessage(msg *network.Message) {
	q.metrics.mu.Lock()
	q.metrics.MessagesReceived++
	q.metrics.mu.Unlock()
	
	switch msg.Type {
	case network.MsgThreatDelta:
		q.handleThreatDelta(msg)
	case network.MsgMembershipUpdate:
		q.handleMembershipUpdate(msg)
	default:
		q.log.Debug("unhandled message type",
			zap.String("type", msg.Type.String()),
			zap.String("sender", msg.Sender))
	}
}

// handleThreatDelta handles incoming threat intelligence delta.
func (q *Quorum) handleThreatDelta(msg *network.Message) {
	delta, err := threatdb.DeserializeDelta(msg.Payload)
	if err != nil {
		q.log.Error("deserialize threat delta", zap.Error(err))
		return
	}
	
	q.log.Info("received threat delta",
		zap.String("sender", msg.Sender),
		zap.Int("signatures", len(delta.Signatures)),
		zap.Int("iocs", len(delta.IoCs)))
	
	if err := q.threatDB.ImportDelta(delta); err != nil {
		q.log.Error("import threat delta", zap.Error(err))
	}
}

// handleMembershipUpdate handles membership changes.
func (q *Quorum) handleMembershipUpdate(msg *network.Message) {
	q.metrics.mu.Lock()
	q.metrics.MembershipChanges++
	q.metrics.mu.Unlock()
}

// ThreatSubmission represents a threat for consensus.
type ThreatSubmission struct {
	ProcessHash   string
	AnomalyScore  float64
	Severity      float64
	Evidence      []byte
	SubmittedBy   string
	SubmittedAt   time.Time
}

// Serialize encodes the threat submission.
func (ts *ThreatSubmission) Serialize() []byte {
	// Simplified serialization
	return []byte(ts.ProcessHash)
}

// SWIMTransportAdapter adapts network.Protocol to gossip.Transport.
type SWIMTransportAdapter struct {
	protocol network.Protocol
}

func (sta *SWIMTransportAdapter) Send(addr string, msg []byte) error {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	
	netMsg := &network.Message{
		Type:      network.MsgMembershipUpdate,
		Payload:   msg,
		Timestamp: time.Now(),
	}
	
	return sta.protocol.Send(ctx, addr, netMsg)
}

func (sta *SWIMTransportAdapter) Broadcast(msg []byte) error {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	netMsg := &network.Message{
		Type:      network.MsgMembershipUpdate,
		Payload:   msg,
		Timestamp: time.Now(),
	}
	
	return sta.protocol.Broadcast(ctx, netMsg)
}

func (sta *SWIMTransportAdapter) Receive() <-chan []byte {
	// In production, would filter messages from protocol.Receive()
	ch := make(chan []byte, 10)
	return ch
}

func (sta *SWIMTransportAdapter) Close() error {
	return nil
}

// RaftTransportAdapter adapts network.Protocol to consensus.Transport.
type RaftTransportAdapter struct {
	protocol network.Protocol
}

func (rta *RaftTransportAdapter) SendVoteRequest(ctx context.Context, peer *consensus.Peer, req *consensus.VoteRequest) (*consensus.VoteResponse, error) {
	// Simplified - in production would marshal req and send via protocol
	return &consensus.VoteResponse{
		Term:        req.Term,
		VoteGranted: false,
	}, nil
}

func (rta *RaftTransportAdapter) SendAppendEntries(ctx context.Context, peer *consensus.Peer, req *consensus.AppendRequest) (*consensus.AppendResponse, error) {
	// Simplified
	return &consensus.AppendResponse{
		Term:    req.Term,
		Success: false,
	}, nil
}

func (rta *RaftTransportAdapter) SendSnapshot(ctx context.Context, peer *consensus.Peer, snapshot []byte) error {
	return nil
}

// ThreatStateMachine implements consensus.StateMachine for threat consensus.
type ThreatStateMachine struct {
	threatDB *threatdb.ThreatDB
	log      *zap.Logger
}

func NewThreatStateMachine(threatDB *threatdb.ThreatDB, log *zap.Logger) *ThreatStateMachine {
	return &ThreatStateMachine{
		threatDB: threatDB,
		log:      log,
	}
}

func (tsm *ThreatStateMachine) Apply(cmd consensus.Command) (interface{}, error) {
	tsm.log.Debug("applying threat command", zap.Int("type", int(cmd.Type)))
	
	switch cmd.Type {
	case consensus.CommandIsolateProcess:
		// Handle process isolation command
		return nil, nil
	case consensus.CommandUpdateSignature:
		// Handle signature update
		return nil, nil
	default:
		return nil, fmt.Errorf("unknown command type: %d", cmd.Type)
	}
}

func (tsm *ThreatStateMachine) Snapshot() ([]byte, error) {
	// Export threat DB snapshot
	return []byte{}, nil
}

func (tsm *ThreatStateMachine) Restore(snapshot []byte) error {
	// Restore threat DB from snapshot
	return nil
}
