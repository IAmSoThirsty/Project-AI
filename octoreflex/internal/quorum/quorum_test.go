// Package quorum_test provides integration tests for the federated quorum system.

package quorum_test

import (
	"context"
	"crypto/ed25519"
	"crypto/rand"
	"fmt"
	"testing"
	"time"

	"go.uber.org/zap"

	"github.com/octoreflex/octoreflex/internal/quorum"
	"github.com/octoreflex/octoreflex/internal/quorum/consensus"
	"github.com/octoreflex/octoreflex/internal/quorum/gossip"
	"github.com/octoreflex/octoreflex/internal/quorum/threatdb"
)

// TestMultiNodeGossip tests SWIM gossip with multiple nodes.
func TestMultiNodeGossip(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	log := zap.NewNop()
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Create 5 nodes
	nodes := make([]*gossip.SWIM, 5)
	transports := make([]gossip.Transport, 5)

	for i := 0; i < 5; i++ {
		_, privKey, _ := ed25519.GenerateKey(rand.Reader)
		
		member := &gossip.Member{
			ID:          fmt.Sprintf("node-%d", i),
			Addr:        fmt.Sprintf("127.0.0.1:%d", 9000+i),
			PublicKey:   privKey.Public().(ed25519.PublicKey),
			State:       gossip.StateAlive,
			Incarnation: 0,
			StateChange: time.Now(),
		}

		transport := newMockTransport()
		transports[i] = transport

		cfg := gossip.DefaultSWIMConfig()
		cfg.ProtocolPeriod = 100 * time.Millisecond
		cfg.AckTimeout = 50 * time.Millisecond

		nodes[i] = gossip.NewSWIM(cfg, member, privKey, transport, log)
		
		if err := nodes[i].Start(ctx); err != nil {
			t.Fatalf("failed to start node %d: %v", i, err)
		}
		defer nodes[i].Stop()
	}

	// Let gossip stabilize
	time.Sleep(2 * time.Second)

	// Verify all nodes know about each other
	for i, node := range nodes {
		members := node.Members()
		if len(members) < 3 {
			t.Errorf("node %d has too few members: %d", i, len(members))
		}
	}

	t.Logf("Multi-node gossip test passed: %d nodes", len(nodes))
}

// TestByzantineDetection tests Byzantine fault detection.
func TestByzantineDetection(t *testing.T) {
	log := zap.NewNop()
	cfg := gossip.DefaultByzantineConfig()
	detector := gossip.NewByzantineDetector(cfg, "test-node", log)

	_, privKey, _ := ed25519.GenerateKey(rand.Reader)
	pubKey := privKey.Public().(ed25519.PublicKey)

	// Test valid message
	timestamp := time.Now().UnixNano()
	payload := []byte("test message")
	signature := ed25519.Sign(privKey, payload)

	err := detector.ValidateMessage("peer-1", pubKey, timestamp, payload, signature)
	if err != nil {
		t.Errorf("valid message rejected: %v", err)
	}

	// Test invalid signature
	badSig := make([]byte, 64)
	err = detector.ValidateMessage("peer-2", pubKey, timestamp, payload, badSig)
	if err == nil {
		t.Error("invalid signature accepted")
	}

	// Test replay attack
	time.Sleep(100 * time.Millisecond)
	err = detector.ValidateMessage("peer-1", pubKey, timestamp, payload, signature)
	if err == nil {
		t.Error("replay attack not detected")
	}

	// Test timestamp skew
	futureTime := time.Now().Add(1 * time.Hour).UnixNano()
	err = detector.ValidateMessage("peer-3", pubKey, futureTime, payload, signature)
	if err == nil {
		t.Error("future timestamp accepted")
	}

	// Check suspected nodes
	suspected := detector.SuspectedNodes()
	if len(suspected) == 0 {
		t.Error("no Byzantine nodes detected despite violations")
	}

	t.Logf("Byzantine detection test passed: %d nodes suspected", len(suspected))
}

// TestRaftConsensus tests Raft consensus with multiple nodes.
func TestRaftConsensus(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	log := zap.NewNop()
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// Create 3 nodes (minimum for Raft)
	nodes := make([]*consensus.Raft, 3)
	stateMachines := make([]consensus.StateMachine, 3)

	for i := 0; i < 3; i++ {
		_, privKey, _ := ed25519.GenerateKey(rand.Reader)
		
		cfg := consensus.DefaultRaftConfig(fmt.Sprintf("node-%d", i))
		cfg.ElectionTimeout = 150 * time.Millisecond
		cfg.HeartbeatPeriod = 50 * time.Millisecond

		// Create peers map
		peers := make(map[string]*consensus.Peer)
		for j := 0; j < 3; j++ {
			if i != j {
				peers[fmt.Sprintf("node-%d", j)] = &consensus.Peer{
					ID:        fmt.Sprintf("node-%d", j),
					Addr:      fmt.Sprintf("127.0.0.1:%d", 8000+j),
					Transport: &mockRaftTransport{},
				}
			}
		}

		stateMachine := &mockStateMachine{commands: make([]consensus.Command, 0)}
		stateMachines[i] = stateMachine

		nodes[i] = consensus.NewRaft(cfg, privKey, peers, stateMachine, log)
		
		if err := nodes[i].Start(ctx); err != nil {
			t.Fatalf("failed to start Raft node %d: %v", i, err)
		}
		defer nodes[i].Stop()
	}

	// Wait for leader election
	time.Sleep(1 * time.Second)

	// Find the leader
	var leader *consensus.Raft
	for _, node := range nodes {
		if node.GetState() == consensus.StateLeader {
			leader = node
			break
		}
	}

	if leader == nil {
		t.Fatal("no leader elected")
	}

	// Submit a command to the leader
	cmd := consensus.Command{
		Type:      consensus.CommandUpdateSignature,
		Payload:   []byte("test signature"),
		Timestamp: time.Now(),
		ClientID:  "test-client",
	}

	index, term, err := leader.Submit(cmd)
	if err != nil {
		t.Fatalf("failed to submit command: %v", err)
	}

	t.Logf("Command submitted: index=%d term=%d", index, term)

	// Wait for command to be applied
	time.Sleep(500 * time.Millisecond)

	t.Log("Raft consensus test passed")
}

// TestThreatDBOperations tests threat database operations.
func TestThreatDBOperations(t *testing.T) {
	log := zap.NewNop()
	
	// Create temporary database
	dbPath := t.TempDir() + "/threat.db"
	db, err := threatdb.NewThreatDB(dbPath, log)
	if err != nil {
		t.Fatalf("failed to create threat db: %v", err)
	}
	defer db.Close()

	// Test signature operations
	sig := &threatdb.Signature{
		Hash:        threatdb.ComputeHash([]byte("malware-pattern")),
		Type:        threatdb.SignatureYARA,
		Pattern:     []byte("rule malware { condition: true }"),
		Severity:    0.9,
		Description: "Test malware signature",
		Source:      "test-node",
		Confidence:  0.95,
	}

	if err := db.AddSignature(sig); err != nil {
		t.Fatalf("failed to add signature: %v", err)
	}

	retrieved, err := db.GetSignature(sig.Hash)
	if err != nil {
		t.Fatalf("failed to retrieve signature: %v", err)
	}

	if retrieved.Severity != sig.Severity {
		t.Errorf("severity mismatch: got %f, want %f", retrieved.Severity, sig.Severity)
	}

	// Test IoC operations
	ioc := &threatdb.IoC{
		Value:    "192.168.1.100",
		Type:     threatdb.IoCIPv4,
		Severity: 0.8,
		Source:   "test-node",
		Metadata: map[string]string{
			"country": "unknown",
			"asn":     "12345",
		},
		Confirmed: true,
	}

	if err := db.AddIoC(ioc); err != nil {
		t.Fatalf("failed to add IoC: %v", err)
	}

	isThreat, severity := db.CheckIP(ioc.Value)
	if !isThreat {
		t.Error("IP not recognized as threat")
	}
	if severity != ioc.Severity {
		t.Errorf("severity mismatch: got %f, want %f", severity, ioc.Severity)
	}

	// Test behavior pattern operations
	pattern := &threatdb.BehaviorPattern{
		ID:       "ransomware-001",
		Name:     "Ransomware file encryption",
		Syscalls: []string{"open", "read", "write", "rename"},
		Severity: 0.95,
		Source:   "test-node",
	}

	if err := db.AddBehaviorPattern(pattern); err != nil {
		t.Fatalf("failed to add behavior pattern: %v", err)
	}

	retrievedPattern, err := db.GetBehaviorPattern(pattern.ID)
	if err != nil {
		t.Fatalf("failed to retrieve pattern: %v", err)
	}

	if retrievedPattern.Name != pattern.Name {
		t.Errorf("pattern name mismatch: got %s, want %s", retrievedPattern.Name, pattern.Name)
	}

	// Test delta export/import
	delta, err := db.ExportDelta(time.Now().Add(-1 * time.Hour))
	if err != nil {
		t.Fatalf("failed to export delta: %v", err)
	}

	if len(delta.Signatures) == 0 {
		t.Error("delta should contain signatures")
	}
	if len(delta.IoCs) == 0 {
		t.Error("delta should contain IoCs")
	}

	t.Logf("ThreatDB test passed: %d signatures, %d IoCs, %d behaviors",
		len(delta.Signatures), len(delta.IoCs), len(delta.Behaviors))
}

// TestQuorumIntegration tests end-to-end quorum functionality.
func TestQuorumIntegration(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping integration test")
	}

	log := zap.NewNop()
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	// Create 3-node quorum
	nodes := make([]*quorum.Quorum, 3)

	for i := 0; i < 3; i++ {
		cfg := quorum.DefaultConfig(
			fmt.Sprintf("node-%d", i),
			fmt.Sprintf("127.0.0.1:%d", 7000+i),
		)
		cfg.ThreatDBPath = t.TempDir() + fmt.Sprintf("/threat-%d.db", i)
		
		// Configure peers
		for j := 0; j < 3; j++ {
			if i != j {
				cfg.Peers[fmt.Sprintf("node-%d", j)] = fmt.Sprintf("127.0.0.1:%d", 7000+j)
			}
		}

		// First node has no seeds, others bootstrap from first
		if i > 0 {
			cfg.SeedNodes = []string{"127.0.0.1:7000"}
		}

		q, err := quorum.NewQuorum(cfg, log)
		if err != nil {
			t.Fatalf("failed to create quorum node %d: %v", i, err)
		}

		nodes[i] = q
		defer q.Stop()
	}

	// Start all nodes
	for i, node := range nodes {
		if err := node.Start(ctx); err != nil {
			t.Fatalf("failed to start quorum node %d: %v", i, err)
		}
	}

	// Wait for cluster stabilization
	time.Sleep(3 * time.Second)

	// Submit threat to leader
	threat := &quorum.ThreatSubmission{
		ProcessHash:  "abc123def456",
		AnomalyScore: 0.95,
		Severity:     0.9,
		Evidence:     []byte("suspicious syscall pattern"),
		SubmittedBy:  "node-0",
		SubmittedAt:  time.Now(),
	}

	// Find leader and submit
	for _, node := range nodes {
		leader := node.GetLeader()
		if leader != "" {
			if err := node.SubmitThreat(threat); err != nil {
				// Expected if not leader
				continue
			}
			break
		}
	}

	// Wait for threat to propagate
	time.Sleep(2 * time.Second)

	// Verify cluster membership
	for i, node := range nodes {
		members := node.GetMembers()
		if len(members) < 2 {
			t.Errorf("node %d has insufficient members: %d", i, len(members))
		}
		t.Logf("Node %d knows about %d members", i, len(members))
	}

	// Check metrics
	for i, node := range nodes {
		metrics := node.GetMetrics()
		t.Logf("Node %d metrics: messages_rx=%d, messages_tx=%d, consensus=%d",
			i, metrics.MessagesReceived, metrics.MessagesSent, metrics.ConsensusDecisions)
	}

	t.Log("Quorum integration test passed")
}

// Mock implementations for testing

type mockTransport struct {
	recvCh chan []byte
}

func newMockTransport() *mockTransport {
	return &mockTransport{
		recvCh: make(chan []byte, 10),
	}
}

func (mt *mockTransport) Send(addr string, msg []byte) error {
	return nil
}

func (mt *mockTransport) Broadcast(msg []byte) error {
	return nil
}

func (mt *mockTransport) Receive() <-chan []byte {
	return mt.recvCh
}

func (mt *mockTransport) Close() error {
	close(mt.recvCh)
	return nil
}

type mockRaftTransport struct{}

func (mrt *mockRaftTransport) SendVoteRequest(ctx context.Context, peer *consensus.Peer, req *consensus.VoteRequest) (*consensus.VoteResponse, error) {
	return &consensus.VoteResponse{
		Term:        req.Term,
		VoteGranted: true,
	}, nil
}

func (mrt *mockRaftTransport) SendAppendEntries(ctx context.Context, peer *consensus.Peer, req *consensus.AppendRequest) (*consensus.AppendResponse, error) {
	return &consensus.AppendResponse{
		Term:    req.Term,
		Success: true,
	}, nil
}

func (mrt *mockRaftTransport) SendSnapshot(ctx context.Context, peer *consensus.Peer, snapshot []byte) error {
	return nil
}

type mockStateMachine struct {
	mu       sync.Mutex
	commands []consensus.Command
}

func (msm *mockStateMachine) Apply(cmd consensus.Command) (interface{}, error) {
	msm.mu.Lock()
	defer msm.mu.Unlock()
	msm.commands = append(msm.commands, cmd)
	return nil, nil
}

func (msm *mockStateMachine) Snapshot() ([]byte, error) {
	return []byte{}, nil
}

func (msm *mockStateMachine) Restore(snapshot []byte) error {
	return nil
}
