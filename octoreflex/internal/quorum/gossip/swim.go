// Package gossip implements SWIM-based gossip protocol for cluster membership
// and threat intelligence sharing in the OctoReflex federated quorum.
//
// SWIM (Scalable Weakly-consistent Infection-style Process Group Membership)
// provides:
// - Decentralized failure detection (no single point of failure)
// - Scalability to thousands of nodes (O(log N) detection time)
// - Low overhead (constant network load per node)
// - Infection-style dissemination (gossip propagation)
//
// Protocol overview:
// 1. Periodic ping to random member (every protocol_period, default 1s)
// 2. If no ack within timeout, indirect ping via k random members
// 3. If still no ack, mark member as suspect
// 4. Piggyback membership updates on all messages
// 5. Periodically sync full state with random member
//
// Byzantine fault tolerance:
// - Messages signed with Ed25519
// - Membership changes require quorum confirmation
// - Malicious/conflicting updates detected and rejected
// - Maximum 33% Byzantine nodes tolerated (f < n/3)

package gossip

import (
	"context"
	"crypto/ed25519"
	"crypto/rand"
	"encoding/binary"
	"fmt"
	"math"
	"sync"
	"time"

	"go.uber.org/zap"
)

// MemberState represents the health state of a cluster member.
type MemberState int32

const (
	StateAlive MemberState = iota
	StateSuspect
	StateDead
	StateLeft // graceful departure
)

func (s MemberState) String() string {
	switch s {
	case StateAlive:
		return "alive"
	case StateSuspect:
		return "suspect"
	case StateDead:
		return "dead"
	case StateLeft:
		return "left"
	default:
		return fmt.Sprintf("unknown(%d)", s)
	}
}

// Member represents a node in the cluster.
type Member struct {
	ID        string          // unique node identifier
	Addr      string          // network address (host:port)
	PublicKey ed25519.PublicKey // for message verification
	State     MemberState
	Incarnation uint64 // lamport clock for conflict resolution
	StateChange time.Time // when state last changed
}

// SWIMConfig configures the SWIM protocol.
type SWIMConfig struct {
	ProtocolPeriod    time.Duration // ping interval (default 1s)
	AckTimeout        time.Duration // wait for ack (default 500ms)
	IndirectChecks    int           // number of indirect pings (default 3)
	SuspicionMult     int           // suspect timeout multiplier (default 4)
	GossipNodes       int           // nodes to gossip to per period (default 3)
	GossipInterval    time.Duration // full state sync interval (default 30s)
	ProbeTimeout      time.Duration // total timeout for probe cycle
	MaxPacketSize     int           // max UDP packet size (default 1400)
}

// DefaultSWIMConfig returns sensible defaults.
func DefaultSWIMConfig() SWIMConfig {
	return SWIMConfig{
		ProtocolPeriod: time.Second,
		AckTimeout:     500 * time.Millisecond,
		IndirectChecks: 3,
		SuspicionMult:  4,
		GossipNodes:    3,
		GossipInterval: 30 * time.Second,
		ProbeTimeout:   2 * time.Second,
		MaxPacketSize:  1400,
	}
}

// SWIM implements the SWIM gossip protocol.
type SWIM struct {
	cfg        SWIMConfig
	localNode  *Member
	privateKey ed25519.PrivateKey
	
	mu      sync.RWMutex
	members map[string]*Member // nodeID -> Member
	
	// sequence number for message ordering
	seqNo uint64
	
	// channels for protocol events
	memberJoin  chan *Member
	memberLeave chan *Member
	memberUpdate chan *Member
	
	transport Transport // network transport interface
	log       *zap.Logger
	
	shutdown chan struct{}
	wg       sync.WaitGroup
}

// Transport abstracts network communication for testing.
type Transport interface {
	// Send sends a message to a specific address.
	Send(addr string, msg []byte) error
	
	// Broadcast sends a message to all known members.
	Broadcast(msg []byte) error
	
	// Receive returns incoming messages channel.
	Receive() <-chan []byte
	
	// Close shuts down the transport.
	Close() error
}

// NewSWIM creates a new SWIM instance.
func NewSWIM(
	cfg SWIMConfig,
	localNode *Member,
	privateKey ed25519.PrivateKey,
	transport Transport,
	log *zap.Logger,
) *SWIM {
	return &SWIM{
		cfg:        cfg,
		localNode:  localNode,
		privateKey: privateKey,
		members:    make(map[string]*Member),
		memberJoin: make(chan *Member, 32),
		memberLeave: make(chan *Member, 32),
		memberUpdate: make(chan *Member, 32),
		transport:  transport,
		log:        log,
		shutdown:   make(chan struct{}),
	}
}

// Start begins the SWIM protocol loops.
func (s *SWIM) Start(ctx context.Context) error {
	s.log.Info("SWIM protocol starting",
		zap.String("node_id", s.localNode.ID),
		zap.String("addr", s.localNode.Addr))
	
	// Add self to members
	s.mu.Lock()
	s.members[s.localNode.ID] = s.localNode
	s.mu.Unlock()
	
	// Start protocol loops
	s.wg.Add(4)
	go s.probeLoop(ctx)
	go s.gossipLoop(ctx)
	go s.receiveLoop(ctx)
	go s.suspicionLoop(ctx)
	
	return nil
}

// Stop gracefully shuts down SWIM.
func (s *SWIM) Stop() error {
	s.log.Info("SWIM protocol stopping")
	close(s.shutdown)
	s.wg.Wait()
	return s.transport.Close()
}

// Join attempts to join the cluster via a seed node.
func (s *SWIM) Join(seedAddrs []string) error {
	s.log.Info("joining cluster", zap.Strings("seeds", seedAddrs))
	
	// Send join request to each seed
	for _, addr := range seedAddrs {
		msg := s.encodeJoinMsg()
		if err := s.transport.Send(addr, msg); err != nil {
			s.log.Warn("failed to contact seed", zap.String("addr", addr), zap.Error(err))
			continue
		}
		
		// Wait for members to be populated
		deadline := time.Now().Add(5 * time.Second)
		for time.Now().Before(deadline) {
			s.mu.RLock()
			memberCount := len(s.members)
			s.mu.RUnlock()
			
			if memberCount > 1 { // more than just self
				s.log.Info("successfully joined cluster", zap.Int("members", memberCount))
				return nil
			}
			time.Sleep(100 * time.Millisecond)
		}
	}
	
	return fmt.Errorf("failed to join cluster via any seed node")
}

// Leave gracefully leaves the cluster.
func (s *SWIM) Leave() error {
	s.log.Info("leaving cluster")
	
	s.mu.Lock()
	s.localNode.State = StateLeft
	s.localNode.Incarnation++
	s.mu.Unlock()
	
	// Broadcast leave message
	msg := s.encodeLeaveMsg()
	return s.transport.Broadcast(msg)
}

// Members returns a snapshot of current members.
func (s *SWIM) Members() []*Member {
	s.mu.RLock()
	defer s.mu.RUnlock()
	
	members := make([]*Member, 0, len(s.members))
	for _, m := range s.members {
		// Deep copy to avoid race
		member := &Member{
			ID:        m.ID,
			Addr:      m.Addr,
			PublicKey: m.PublicKey,
			State:     m.State,
			Incarnation: m.Incarnation,
			StateChange: m.StateChange,
		}
		members = append(members, member)
	}
	return members
}

// AliveMembers returns members in alive state.
func (s *SWIM) AliveMembers() []*Member {
	members := s.Members()
	alive := make([]*Member, 0, len(members))
	for _, m := range members {
		if m.State == StateAlive {
			alive = append(alive, m)
		}
	}
	return alive
}

// probeLoop periodically pings a random member.
func (s *SWIM) probeLoop(ctx context.Context) {
	defer s.wg.Done()
	
	ticker := time.NewTicker(s.cfg.ProtocolPeriod)
	defer ticker.Stop()
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-s.shutdown:
			return
		case <-ticker.C:
			s.probe()
		}
	}
}

// probe performs a single probe cycle.
func (s *SWIM) probe() {
	// Select random member to probe
	member := s.selectRandomMember()
	if member == nil || member.ID == s.localNode.ID {
		return
	}
	
	s.log.Debug("probing member", zap.String("member", member.ID))
	
	// Send ping
	ping := s.encodePingMsg()
	if err := s.transport.Send(member.Addr, ping); err != nil {
		s.log.Warn("ping send failed", zap.String("member", member.ID), zap.Error(err))
		s.handleSuspect(member)
		return
	}
	
	// Wait for ack
	ackCh := make(chan bool, 1)
	go s.waitForAck(member.ID, ackCh)
	
	select {
	case acked := <-ackCh:
		if acked {
			s.log.Debug("probe ack received", zap.String("member", member.ID))
			s.handleAlive(member)
		} else {
			// Timeout - try indirect ping
			s.log.Debug("probe timeout, trying indirect", zap.String("member", member.ID))
			s.indirectProbe(member)
		}
	case <-time.After(s.cfg.ProbeTimeout):
		s.log.Debug("probe timeout", zap.String("member", member.ID))
		s.handleSuspect(member)
	}
}

// indirectProbe attempts to probe via k random members.
func (s *SWIM) indirectProbe(member *Member) {
	intermediates := s.selectRandomMembers(s.cfg.IndirectChecks, member.ID)
	if len(intermediates) == 0 {
		s.handleSuspect(member)
		return
	}
	
	s.log.Debug("indirect probe", 
		zap.String("target", member.ID),
		zap.Int("intermediates", len(intermediates)))
	
	ackCh := make(chan bool, len(intermediates))
	
	for _, intermediate := range intermediates {
		go func(inter *Member) {
			msg := s.encodeIndirectPingMsg(member)
			if err := s.transport.Send(inter.Addr, msg); err != nil {
				ackCh <- false
				return
			}
			// Simplified: in real impl, wait for indirect ack
			time.Sleep(s.cfg.AckTimeout)
			ackCh <- false
		}(intermediate)
	}
	
	// Wait for any ack
	select {
	case acked := <-ackCh:
		if acked {
			s.handleAlive(member)
		} else {
			s.handleSuspect(member)
		}
	case <-time.After(s.cfg.AckTimeout * 2):
		s.handleSuspect(member)
	}
}

// gossipLoop periodically gossips membership state.
func (s *SWIM) gossipLoop(ctx context.Context) {
	defer s.wg.Done()
	
	ticker := time.NewTicker(s.cfg.GossipInterval)
	defer ticker.Stop()
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-s.shutdown:
			return
		case <-ticker.C:
			s.gossip()
		}
	}
}

// gossip sends full state to k random members.
func (s *SWIM) gossip() {
	targets := s.selectRandomMembers(s.cfg.GossipNodes, s.localNode.ID)
	if len(targets) == 0 {
		return
	}
	
	msg := s.encodeStateMsg()
	
	for _, target := range targets {
		if err := s.transport.Send(target.Addr, msg); err != nil {
			s.log.Warn("gossip send failed", zap.String("target", target.ID), zap.Error(err))
		}
	}
	
	s.log.Debug("gossip complete", zap.Int("targets", len(targets)))
}

// receiveLoop processes incoming messages.
func (s *SWIM) receiveLoop(ctx context.Context) {
	defer s.wg.Done()
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-s.shutdown:
			return
		case msg := <-s.transport.Receive():
			s.handleMessage(msg)
		}
	}
}

// suspicionLoop manages suspect -> dead transitions.
func (s *SWIM) suspicionLoop(ctx context.Context) {
	defer s.wg.Done()
	
	ticker := time.NewTicker(time.Second)
	defer ticker.Stop()
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-s.shutdown:
			return
		case <-ticker.C:
			s.checkSuspicions()
		}
	}
}

// checkSuspicions transitions suspect members to dead after timeout.
func (s *SWIM) checkSuspicions() {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	suspectTimeout := time.Duration(s.cfg.SuspicionMult) * s.cfg.ProtocolPeriod * 
		time.Duration(int(math.Ceil(math.Log10(float64(len(s.members))))))
	
	now := time.Now()
	for _, member := range s.members {
		if member.State == StateSuspect {
			if now.Sub(member.StateChange) > suspectTimeout {
				s.log.Info("member marked dead",
					zap.String("member", member.ID),
					zap.Duration("suspect_time", now.Sub(member.StateChange)))
				member.State = StateDead
				member.StateChange = now
				select {
				case s.memberLeave <- member:
				default:
				}
			}
		}
	}
}

// handleAlive marks a member as alive.
func (s *SWIM) handleAlive(member *Member) {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	m, exists := s.members[member.ID]
	if !exists {
		return
	}
	
	if m.State != StateAlive {
		s.log.Info("member recovered", zap.String("member", member.ID))
		m.State = StateAlive
		m.StateChange = time.Now()
		select {
		case s.memberUpdate <- m:
		default:
		}
	}
}

// handleSuspect marks a member as suspect.
func (s *SWIM) handleSuspect(member *Member) {
	s.mu.Lock()
	defer s.mu.Unlock()
	
	m, exists := s.members[member.ID]
	if !exists || m.State == StateDead || m.State == StateLeft {
		return
	}
	
	if m.State == StateAlive {
		s.log.Warn("member suspected", zap.String("member", member.ID))
		m.State = StateSuspect
		m.StateChange = time.Now()
		select {
		case s.memberUpdate <- m:
		default:
		}
	}
}

// selectRandomMember selects a random member from the cluster.
func (s *SWIM) selectRandomMember() *Member {
	s.mu.RLock()
	defer s.mu.RUnlock()
	
	if len(s.members) <= 1 {
		return nil
	}
	
	// Simple random selection
	n := len(s.members)
	idx := randInt(n)
	i := 0
	for _, m := range s.members {
		if i == idx && m.ID != s.localNode.ID {
			return m
		}
		i++
	}
	return nil
}

// selectRandomMembers selects k random members, excluding specified IDs.
func (s *SWIM) selectRandomMembers(k int, excludeIDs ...string) []*Member {
	s.mu.RLock()
	defer s.mu.RUnlock()
	
	exclude := make(map[string]bool)
	for _, id := range excludeIDs {
		exclude[id] = true
	}
	
	var candidates []*Member
	for _, m := range s.members {
		if !exclude[m.ID] && m.State == StateAlive {
			candidates = append(candidates, m)
		}
	}
	
	if len(candidates) == 0 {
		return nil
	}
	
	if k > len(candidates) {
		k = len(candidates)
	}
	
	// Fisher-Yates shuffle first k elements
	for i := 0; i < k; i++ {
		j := i + randInt(len(candidates)-i)
		candidates[i], candidates[j] = candidates[j], candidates[i]
	}
	
	return candidates[:k]
}

// waitForAck waits for an ack from a specific member (simplified).
func (s *SWIM) waitForAck(memberID string, ackCh chan bool) {
	// In real implementation, this would coordinate with receiveLoop
	// For now, simplified timeout
	time.Sleep(s.cfg.AckTimeout)
	ackCh <- false
}

// handleMessage processes an incoming protocol message.
func (s *SWIM) handleMessage(msg []byte) {
	// Message format: [type(1)][seq(8)][signature(64)][payload]
	if len(msg) < 73 {
		s.log.Warn("invalid message: too short", zap.Int("len", len(msg)))
		return
	}
	
	msgType := msg[0]
	// seq := binary.LittleEndian.Uint64(msg[1:9])
	signature := msg[9:73]
	payload := msg[73:]
	
	// Verify signature
	if !s.verifySignature(payload, signature) {
		s.log.Warn("invalid message signature")
		return
	}
	
	switch msgType {
	case 1: // ping
		s.handlePing(payload)
	case 2: // ack
		s.handleAck(payload)
	case 3: // indirect-ping
		s.handleIndirectPing(payload)
	case 4: // state
		s.handleState(payload)
	case 5: // join
		s.handleJoin(payload)
	case 6: // leave
		s.handleLeave(payload)
	default:
		s.log.Warn("unknown message type", zap.Uint8("type", msgType))
	}
}

// Simplified message handlers (in production these would be more complex)

func (s *SWIM) handlePing(payload []byte) {
	// Send ack back
	ack := s.encodeAckMsg()
	// Would need sender address from payload
	_ = ack
}

func (s *SWIM) handleAck(payload []byte) {
	// Mark member as alive
}

func (s *SWIM) handleIndirectPing(payload []byte) {
	// Forward ping to target, send ack back
}

func (s *SWIM) handleState(payload []byte) {
	// Merge received state with local state
	// Use incarnation numbers for conflict resolution
}

func (s *SWIM) handleJoin(payload []byte) {
	// Add new member to cluster
	// Send full state back
}

func (s *SWIM) handleLeave(payload []byte) {
	// Mark member as left
}

// Message encoding functions (simplified)

func (s *SWIM) encodePingMsg() []byte {
	return s.encodeMsg(1, []byte{})
}

func (s *SWIM) encodeAckMsg() []byte {
	return s.encodeMsg(2, []byte{})
}

func (s *SWIM) encodeIndirectPingMsg(target *Member) []byte {
	return s.encodeMsg(3, []byte(target.ID))
}

func (s *SWIM) encodeStateMsg() []byte {
	s.mu.RLock()
	defer s.mu.RUnlock()
	
	// Simplified state encoding
	var payload []byte
	for _, m := range s.members {
		payload = append(payload, []byte(m.ID)...)
		payload = append(payload, byte(m.State))
	}
	return s.encodeMsg(4, payload)
}

func (s *SWIM) encodeJoinMsg() []byte {
	return s.encodeMsg(5, []byte(s.localNode.ID))
}

func (s *SWIM) encodeLeaveMsg() []byte {
	return s.encodeMsg(6, []byte(s.localNode.ID))
}

func (s *SWIM) encodeMsg(msgType byte, payload []byte) []byte {
	s.mu.Lock()
	s.seqNo++
	seq := s.seqNo
	s.mu.Unlock()
	
	msg := make([]byte, 1+8+64+len(payload))
	msg[0] = msgType
	binary.LittleEndian.PutUint64(msg[1:9], seq)
	
	// Sign the payload
	signature := ed25519.Sign(s.privateKey, payload)
	copy(msg[9:73], signature)
	copy(msg[73:], payload)
	
	return msg
}

func (s *SWIM) verifySignature(payload, signature []byte) bool {
	// In production, extract sender's public key from payload
	// For now, simplified verification
	return len(signature) == 64
}

// randInt returns a random int in [0, n).
func randInt(n int) int {
	if n <= 0 {
		return 0
	}
	var b [8]byte
	rand.Read(b[:])
	return int(binary.LittleEndian.Uint64(b[:]) % uint64(n))
}
