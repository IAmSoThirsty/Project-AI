// Package consensus implements Raft consensus for critical distributed decisions.
//
// Raft guarantees:
// - Strong consistency (linearizable reads/writes)
// - Leader election (automatic failover)
// - Log replication (replicated state machine)
// - Safety: at most one leader per term
// - Liveness: cluster available with majority (f < n/2 failures)
//
// Use cases in OctoReflex:
// - Coordinated threat responses (network-wide isolation)
// - Configuration changes (updating cluster policies)
// - Critical metadata (threat signatures, IoC databases)
// - Membership changes (adding/removing nodes)
//
// Non-use cases (handled by SWIM gossip instead):
// - Individual threat detections (too frequent)
// - Per-process anomaly scores (high volume)
// - Heartbeats (use SWIM failure detection)

package consensus

import (
	"context"
	"crypto/ed25519"
	"crypto/rand"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"sync"
	"sync/atomic"
	"time"

	"go.uber.org/zap"
)

// NodeState represents the Raft state of a node.
type NodeState int32

const (
	StateFollower NodeState = iota
	StateCandidate
	StateLeader
)

func (s NodeState) String() string {
	switch s {
	case StateFollower:
		return "follower"
	case StateCandidate:
		return "candidate"
	case StateLeader:
		return "leader"
	default:
		return fmt.Sprintf("unknown(%d)", s)
	}
}

// RaftConfig configures the Raft consensus engine.
type RaftConfig struct {
	NodeID          string
	ElectionTimeout time.Duration // random [T, 2T], default 150-300ms
	HeartbeatPeriod time.Duration // default 50ms (< electionTimeout)
	MaxLogEntries   int           // max entries per AppendEntries RPC (default 100)
	SnapshotThreshold int         // snapshot after N log entries (default 10000)
}

// DefaultRaftConfig returns sensible defaults.
func DefaultRaftConfig(nodeID string) RaftConfig {
	return RaftConfig{
		NodeID:          nodeID,
		ElectionTimeout: 150 * time.Millisecond,
		HeartbeatPeriod: 50 * time.Millisecond,
		MaxLogEntries:   100,
		SnapshotThreshold: 10000,
	}
}

// LogEntry represents a single entry in the Raft log.
type LogEntry struct {
	Index   uint64      // log position (1-indexed)
	Term    uint64      // election term when entry was created
	Command Command     // state machine command
	Data    []byte      // serialized command data
}

// Command types for the threat consensus state machine.
type CommandType int

const (
	CommandAddNode CommandType = iota
	CommandRemoveNode
	CommandIsolateProcess
	CommandUpdateSignature
	CommandUpdatePolicy
	CommandNoop // for leader heartbeats
)

// Command represents a state machine operation.
type Command struct {
	Type      CommandType
	Payload   []byte
	Timestamp time.Time
	ClientID  string // for deduplication
	RequestID uint64 // for deduplication
}

// Raft implements the Raft consensus algorithm.
type Raft struct {
	cfg        RaftConfig
	privateKey ed25519.PrivateKey
	
	// Persistent state (must survive crashes)
	mu          sync.RWMutex
	currentTerm uint64
	votedFor    string   // candidateID that received vote in current term
	log         []LogEntry
	
	// Volatile state (all servers)
	commitIndex uint64 // highest log entry known to be committed
	lastApplied uint64 // highest log entry applied to state machine
	
	// Volatile state (leaders only)
	nextIndex  map[string]uint64 // next log entry to send to each server
	matchIndex map[string]uint64 // highest log entry known to be replicated
	
	// Node state
	state      atomic.Value // NodeState
	leaderID   atomic.Value // string
	peers      map[string]*Peer
	
	// Channels
	applyCh       chan ApplyMsg
	voteCh        chan *VoteRequest
	appendCh      chan *AppendRequest
	shutdownCh    chan struct{}
	
	// Election timer
	electionTimer  *time.Timer
	heartbeatTimer *time.Timer
	
	// State machine
	stateMachine StateMachine
	
	log_logger *zap.Logger
	wg         sync.WaitGroup
}

// Peer represents a cluster member.
type Peer struct {
	ID        string
	Addr      string
	PublicKey ed25519.PublicKey
	Transport Transport
}

// Transport abstracts network communication.
type Transport interface {
	SendVoteRequest(ctx context.Context, peer *Peer, req *VoteRequest) (*VoteResponse, error)
	SendAppendEntries(ctx context.Context, peer *Peer, req *AppendRequest) (*AppendResponse, error)
	SendSnapshot(ctx context.Context, peer *Peer, snapshot []byte) error
}

// VoteRequest is the RequestVote RPC message.
type VoteRequest struct {
	Term         uint64 // candidate's term
	CandidateID  string
	LastLogIndex uint64
	LastLogTerm  uint64
	Signature    []byte
}

// VoteResponse is the RequestVote RPC response.
type VoteResponse struct {
	Term        uint64 // current term, for candidate to update itself
	VoteGranted bool
	Signature   []byte
}

// AppendRequest is the AppendEntries RPC message.
type AppendRequest struct {
	Term         uint64
	LeaderID     string
	PrevLogIndex uint64
	PrevLogTerm  uint64
	Entries      []LogEntry
	LeaderCommit uint64
	Signature    []byte
}

// AppendResponse is the AppendEntries RPC response.
type AppendResponse struct {
	Term    uint64
	Success bool
	MatchIndex uint64 // for faster log backtracking
	Signature  []byte
}

// ApplyMsg is sent when a log entry is committed.
type ApplyMsg struct {
	CommandValid bool
	Command      Command
	CommandIndex uint64
}

// StateMachine represents the replicated state machine.
type StateMachine interface {
	Apply(cmd Command) (interface{}, error)
	Snapshot() ([]byte, error)
	Restore(snapshot []byte) error
}

// NewRaft creates a new Raft instance.
func NewRaft(
	cfg RaftConfig,
	privateKey ed25519.PrivateKey,
	peers map[string]*Peer,
	stateMachine StateMachine,
	log *zap.Logger,
) *Raft {
	r := &Raft{
		cfg:           cfg,
		privateKey:    privateKey,
		currentTerm:   0,
		votedFor:      "",
		log:           make([]LogEntry, 1), // 1-indexed, entry 0 is sentinel
		commitIndex:   0,
		lastApplied:   0,
		nextIndex:     make(map[string]uint64),
		matchIndex:    make(map[string]uint64),
		peers:         peers,
		applyCh:       make(chan ApplyMsg, 100),
		voteCh:        make(chan *VoteRequest, 10),
		appendCh:      make(chan *AppendRequest, 10),
		shutdownCh:    make(chan struct{}),
		stateMachine:  stateMachine,
		log_logger:    log,
	}
	
	r.state.Store(StateFollower)
	r.leaderID.Store("")
	
	// Initialize sentinel log entry
	r.log[0] = LogEntry{Index: 0, Term: 0}
	
	return r
}

// Start begins the Raft protocol.
func (r *Raft) Start(ctx context.Context) error {
	r.log_logger.Info("Raft consensus starting",
		zap.String("node_id", r.cfg.NodeID),
		zap.Int("peers", len(r.peers)))
	
	r.resetElectionTimer()
	
	r.wg.Add(3)
	go r.electionLoop(ctx)
	go r.heartbeatLoop(ctx)
	go r.applyLoop(ctx)
	
	return nil
}

// Stop gracefully shuts down Raft.
func (r *Raft) Stop() error {
	r.log_logger.Info("Raft consensus stopping")
	close(r.shutdownCh)
	r.wg.Wait()
	return nil
}

// Submit submits a command to the Raft cluster.
// Returns the log index and term if this node is the leader.
func (r *Raft) Submit(cmd Command) (uint64, uint64, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	if r.GetState() != StateLeader {
		leaderID := r.leaderID.Load().(string)
		if leaderID == "" {
			return 0, 0, fmt.Errorf("no leader elected")
		}
		return 0, 0, fmt.Errorf("not leader, current leader: %s", leaderID)
	}
	
	// Serialize command
	data, err := json.Marshal(cmd)
	if err != nil {
		return 0, 0, fmt.Errorf("marshal command: %w", err)
	}
	
	// Append to local log
	entry := LogEntry{
		Index:   uint64(len(r.log)),
		Term:    r.currentTerm,
		Command: cmd,
		Data:    data,
	}
	r.log = append(r.log, entry)
	
	r.log_logger.Info("command submitted",
		zap.Uint64("index", entry.Index),
		zap.Uint64("term", entry.Term),
		zap.String("type", fmt.Sprintf("%d", cmd.Type)))
	
	// Trigger immediate replication
	go r.replicateLogs()
	
	return entry.Index, entry.Term, nil
}

// GetState returns the current Raft state.
func (r *Raft) GetState() NodeState {
	return r.state.Load().(NodeState)
}

// GetLeader returns the current leader ID.
func (r *Raft) GetLeader() string {
	return r.leaderID.Load().(string)
}

// electionLoop manages election timeouts and initiates elections.
func (r *Raft) electionLoop(ctx context.Context) {
	defer r.wg.Done()
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-r.shutdownCh:
			return
		case <-r.electionTimer.C:
			// Election timeout - become candidate
			r.startElection()
			r.resetElectionTimer()
		}
	}
}

// heartbeatLoop sends periodic heartbeats when leader.
func (r *Raft) heartbeatLoop(ctx context.Context) {
	defer r.wg.Done()
	
	ticker := time.NewTicker(r.cfg.HeartbeatPeriod)
	defer ticker.Stop()
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-r.shutdownCh:
			return
		case <-ticker.C:
			if r.GetState() == StateLeader {
				r.sendHeartbeats()
			}
		}
	}
}

// applyLoop applies committed entries to the state machine.
func (r *Raft) applyLoop(ctx context.Context) {
	defer r.wg.Done()
	
	ticker := time.NewTicker(10 * time.Millisecond)
	defer ticker.Stop()
	
	for {
		select {
		case <-ctx.Done():
			return
		case <-r.shutdownCh:
			return
		case <-ticker.C:
			r.applyCommitted()
		}
	}
}

// applyCommitted applies entries between lastApplied and commitIndex.
func (r *Raft) applyCommitted() {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	for r.lastApplied < r.commitIndex {
		r.lastApplied++
		
		if r.lastApplied >= uint64(len(r.log)) {
			r.log_logger.Error("apply index out of bounds",
				zap.Uint64("lastApplied", r.lastApplied),
				zap.Int("logLen", len(r.log)))
			break
		}
		
		entry := r.log[r.lastApplied]
		
		r.log_logger.Debug("applying command",
			zap.Uint64("index", entry.Index),
			zap.Uint64("term", entry.Term))
		
		// Apply to state machine
		if entry.Command.Type != CommandNoop {
			if _, err := r.stateMachine.Apply(entry.Command); err != nil {
				r.log_logger.Error("state machine apply failed",
					zap.Uint64("index", entry.Index),
					zap.Error(err))
			}
		}
		
		// Notify application
		select {
		case r.applyCh <- ApplyMsg{
			CommandValid: true,
			Command:      entry.Command,
			CommandIndex: entry.Index,
		}:
		default:
			r.log_logger.Warn("apply channel full")
		}
	}
	
	// Check if snapshot needed
	if len(r.log) > r.cfg.SnapshotThreshold {
		r.takeSnapshot()
	}
}

// startElection initiates a leader election.
func (r *Raft) startElection() {
	r.mu.Lock()
	
	// Transition to candidate
	r.state.Store(StateCandidate)
	r.currentTerm++
	r.votedFor = r.cfg.NodeID
	term := r.currentTerm
	
	r.log_logger.Info("starting election",
		zap.Uint64("term", term))
	
	lastLogIndex := uint64(len(r.log) - 1)
	lastLogTerm := r.log[lastLogIndex].Term
	
	r.mu.Unlock()
	
	// Vote for self
	votesReceived := 1
	totalPeers := len(r.peers) + 1
	majority := totalPeers/2 + 1
	
	var voteMu sync.Mutex
	
	// Request votes from all peers
	for _, peer := range r.peers {
		go func(p *Peer) {
			req := &VoteRequest{
				Term:         term,
				CandidateID:  r.cfg.NodeID,
				LastLogIndex: lastLogIndex,
				LastLogTerm:  lastLogTerm,
			}
			
			// Sign request
			req.Signature = r.signVoteRequest(req)
			
			ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
			defer cancel()
			
			resp, err := p.Transport.SendVoteRequest(ctx, p, req)
			if err != nil {
				r.log_logger.Debug("vote request failed",
					zap.String("peer", p.ID),
					zap.Error(err))
				return
			}
			
			r.mu.Lock()
			defer r.mu.Unlock()
			
			// Check if term has changed
			if resp.Term > r.currentTerm {
				r.currentTerm = resp.Term
				r.state.Store(StateFollower)
				r.votedFor = ""
				r.resetElectionTimer()
				return
			}
			
			if resp.VoteGranted && r.GetState() == StateCandidate {
				voteMu.Lock()
				votesReceived++
				votes := votesReceived
				voteMu.Unlock()
				
				r.log_logger.Debug("vote granted",
					zap.String("peer", p.ID),
					zap.Int("votes", votes),
					zap.Int("needed", majority))
				
				if votes >= majority {
					r.becomeLeader()
				}
			}
		}(peer)
	}
}

// becomeLeader transitions to leader state.
func (r *Raft) becomeLeader() {
	if r.GetState() != StateCandidate {
		return
	}
	
	r.state.Store(StateLeader)
	r.leaderID.Store(r.cfg.NodeID)
	
	r.log_logger.Info("became leader",
		zap.Uint64("term", r.currentTerm))
	
	// Initialize leader state
	lastLogIndex := uint64(len(r.log))
	for peerID := range r.peers {
		r.nextIndex[peerID] = lastLogIndex
		r.matchIndex[peerID] = 0
	}
	
	// Send immediate heartbeat
	r.sendHeartbeats()
}

// sendHeartbeats sends AppendEntries RPCs to all peers.
func (r *Raft) sendHeartbeats() {
	for _, peer := range r.peers {
		go r.sendAppendEntries(peer)
	}
}

// replicateLogs replicates new log entries to followers.
func (r *Raft) replicateLogs() {
	for _, peer := range r.peers {
		go r.sendAppendEntries(peer)
	}
}

// sendAppendEntries sends AppendEntries RPC to a single peer.
func (r *Raft) sendAppendEntries(peer *Peer) {
	r.mu.RLock()
	
	if r.GetState() != StateLeader {
		r.mu.RUnlock()
		return
	}
	
	nextIdx := r.nextIndex[peer.ID]
	if nextIdx < 1 {
		nextIdx = 1
	}
	
	prevLogIndex := nextIdx - 1
	prevLogTerm := uint64(0)
	if prevLogIndex > 0 && prevLogIndex < uint64(len(r.log)) {
		prevLogTerm = r.log[prevLogIndex].Term
	}
	
	// Determine entries to send
	var entries []LogEntry
	if nextIdx < uint64(len(r.log)) {
		endIdx := nextIdx + uint64(r.cfg.MaxLogEntries)
		if endIdx > uint64(len(r.log)) {
			endIdx = uint64(len(r.log))
		}
		entries = r.log[nextIdx:endIdx]
	}
	
	req := &AppendRequest{
		Term:         r.currentTerm,
		LeaderID:     r.cfg.NodeID,
		PrevLogIndex: prevLogIndex,
		PrevLogTerm:  prevLogTerm,
		Entries:      entries,
		LeaderCommit: r.commitIndex,
	}
	
	r.mu.RUnlock()
	
	// Sign request
	req.Signature = r.signAppendRequest(req)
	
	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()
	
	resp, err := peer.Transport.SendAppendEntries(ctx, peer, req)
	if err != nil {
		r.log_logger.Debug("append entries failed",
			zap.String("peer", peer.ID),
			zap.Error(err))
		return
	}
	
	r.mu.Lock()
	defer r.mu.Unlock()
	
	// Check term
	if resp.Term > r.currentTerm {
		r.currentTerm = resp.Term
		r.state.Store(StateFollower)
		r.votedFor = ""
		r.resetElectionTimer()
		return
	}
	
	if resp.Success {
		// Update nextIndex and matchIndex
		newMatchIndex := prevLogIndex + uint64(len(entries))
		r.nextIndex[peer.ID] = newMatchIndex + 1
		r.matchIndex[peer.ID] = newMatchIndex
		
		// Update commitIndex
		r.updateCommitIndex()
	} else {
		// Log inconsistency - decrement nextIndex and retry
		if r.nextIndex[peer.ID] > 1 {
			r.nextIndex[peer.ID]--
		}
	}
}

// updateCommitIndex advances commitIndex if majority of peers have replicated.
func (r *Raft) updateCommitIndex() {
	// Find the highest index replicated on majority
	for n := r.commitIndex + 1; n < uint64(len(r.log)); n++ {
		if r.log[n].Term != r.currentTerm {
			continue
		}
		
		replicas := 1 // self
		for _, matchIdx := range r.matchIndex {
			if matchIdx >= n {
				replicas++
			}
		}
		
		majority := (len(r.peers)+1)/2 + 1
		if replicas >= majority {
			r.commitIndex = n
			r.log_logger.Debug("commit index advanced",
				zap.Uint64("commitIndex", n))
		}
	}
}

// resetElectionTimer resets the election timeout with randomization.
func (r *Raft) resetElectionTimer() {
	timeout := r.cfg.ElectionTimeout + randomDuration(r.cfg.ElectionTimeout)
	
	if r.electionTimer == nil {
		r.electionTimer = time.NewTimer(timeout)
	} else {
		r.electionTimer.Reset(timeout)
	}
}

// takeSnapshot creates a snapshot of the state machine.
func (r *Raft) takeSnapshot() {
	snapshot, err := r.stateMachine.Snapshot()
	if err != nil {
		r.log_logger.Error("snapshot failed", zap.Error(err))
		return
	}
	
	// Truncate log (keep only recent entries)
	lastIncluded := r.lastApplied
	if lastIncluded > 0 && lastIncluded < uint64(len(r.log)) {
		r.log = r.log[lastIncluded:]
	}
	
	r.log_logger.Info("snapshot created",
		zap.Int("size", len(snapshot)),
		zap.Uint64("lastIncluded", lastIncluded))
}

// signVoteRequest signs a vote request.
func (r *Raft) signVoteRequest(req *VoteRequest) []byte {
	buf := make([]byte, 32)
	binary.LittleEndian.PutUint64(buf[0:8], req.Term)
	binary.LittleEndian.PutUint64(buf[8:16], req.LastLogIndex)
	binary.LittleEndian.PutUint64(buf[16:24], req.LastLogTerm)
	copy(buf[24:], []byte(req.CandidateID)[:8])
	
	return ed25519.Sign(r.privateKey, buf)
}

// signAppendRequest signs an append request.
func (r *Raft) signAppendRequest(req *AppendRequest) []byte {
	buf := make([]byte, 32)
	binary.LittleEndian.PutUint64(buf[0:8], req.Term)
	binary.LittleEndian.PutUint64(buf[8:16], req.PrevLogIndex)
	binary.LittleEndian.PutUint64(buf[16:24], req.LeaderCommit)
	copy(buf[24:], []byte(req.LeaderID)[:8])
	
	return ed25519.Sign(r.privateKey, buf)
}

// randomDuration returns a random duration up to max.
func randomDuration(max time.Duration) time.Duration {
	var b [8]byte
	rand.Read(b[:])
	n := binary.LittleEndian.Uint64(b[:])
	return time.Duration(n % uint64(max))
}
