// Package escalation — camouflage.go
//
// Camouflage module: defensive deception driven by the m_t control law.
//
// Purpose:
//   When a process reaches ISOLATED (S2) or higher, OCTOREFLEX activates
//   camouflage actions to increase the attacker's marginal cost of continued
//   operation. These are *defensive* deception actions — no external network
//   calls, no offensive capability.
//
// Control law (from simulator spec §15, STABILITY.md):
//
//   m_{t+1} = clamp(m_t + λ₁ * A_t - λ₂ * (1 - U_t), 0, 1)
//
// MutationRateFromControlLaw() is the SINGLE authoritative implementation of
// this formula. The simulator uses the same function. There is no divergence.
//
// Epoch rotation:
//   Port shuffle epoch length is derived from m_t, not a fixed interval.
//   Higher m_t (more active attacker) → shorter epoch → faster rotation.
//   Formula: epoch_seconds = max(MinEpochSeconds, BaseEpochSeconds * (1 - m_t))
//   At m_t=0.0: epoch = BaseEpochSeconds (default 3600s = 1h)
//   At m_t=0.5: epoch = BaseEpochSeconds * 0.5 (default 1800s = 30m)
//   At m_t=1.0: epoch = MinEpochSeconds (default 300s = 5m)
//
// Decoy listener:
//   Connections to the decoy port are NOT passive telemetry. Each connection
//   emits a synthetic event via the DecoyEventSink interface, which feeds
//   directly into the escalation engine's event pipeline. This makes the
//   decoy an active component of the control loop.
//
// Hint file ownership:
//   Hint files are written with mode 0600 and chowned to root:octoreflex (GID
//   from config). The .tmp file is chowned before rename to avoid a window
//   where the file is readable by other users.
//
// Invariants:
//   - All camouflage actions are gated by config.Camouflage.Enabled.
//   - Activate() is idempotent: no-op if already active at this or higher state.
//   - Deactivate() reverses all active actions for a PID.
//   - deterministicPort() is pure: same inputs → same output, always.
//   - No external network calls. All actions are local.
//   - Decoy listener never sends data to connecting clients.
//   - MutationRateFromControlLaw() is the single source of truth for m_t.

package escalation

import (
	"crypto/sha256"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"math"
	"net"
	"os"
	"sync"
	"time"

	"go.uber.org/zap"
)

// ─── Control law (single authoritative implementation) ────────────────────────

// ControlLawParams holds the λ₁/λ₂ parameters shared between the simulator
// and the camouflage module. These MUST match the values in cmd/octoreflex-sim.
//
// Default values match the simulator defaults documented in STABILITY.md.
type ControlLawParams struct {
	Lambda1 float64 // Attacker adaptation rate (default 0.4)
	Lambda2 float64 // Defender suppression rate (default 0.6)
}

// DefaultControlLawParams returns the canonical default parameters.
// These match the simulator defaults in STABILITY.md §6.
func DefaultControlLawParams() ControlLawParams {
	return ControlLawParams{Lambda1: 0.4, Lambda2: 0.6}
}

// MutationRateFromControlLaw computes the next mutation rate m_{t+1} using
// the canonical control law from STABILITY.md §1:
//
//	m_{t+1} = clamp(m_t + λ₁ * A_t - λ₂ * (1 - U_t), 0, 1)
//
// Parameters:
//   - mt:     current mutation rate ∈ [0, 1]
//   - anomaly: current anomaly signal A_t ∈ [0, 1] (normalised severity)
//   - utility: current defender utility U_t ∈ [0, 1] (from state table)
//   - p:      control law parameters (λ₁, λ₂)
//
// This is the SINGLE authoritative implementation. The simulator calls this
// function directly. The camouflage module calls this function directly.
// There is no separate approximation.
func MutationRateFromControlLaw(mt, anomaly, utility float64, p ControlLawParams) float64 {
	next := mt + p.Lambda1*anomaly - p.Lambda2*(1-utility)
	return math.Max(0, math.Min(1, next))
}

// DefenderUtilityFromState returns U_t for a given isolation state.
// Matches the table in STABILITY.md §5.
func DefenderUtilityFromState(s State) float64 {
	switch s {
	case StateNormal:
		return 0.0
	case StatePressure:
		return 0.2
	case StateIsolated:
		return 0.5
	case StateFrozen:
		return 0.7
	case StateQuarantined:
		return 0.9
	case StateTerminated:
		return 1.0
	default:
		return 0.0
	}
}

// AnomalySignalFromSeverity maps a composite severity score S to the anomaly
// signal A_t ∈ (0, 1) using the sigmoid from STABILITY.md §4.
//
//	A_t = sigmoid(S / S_max)  where sigmoid(x) = 1 / (1 + exp(-4(x - 0.5)))
func AnomalySignalFromSeverity(severity, severityMax float64) float64 {
	if severityMax <= 0 {
		return 0.5
	}
	x := severity / severityMax
	return 1.0 / (1.0 + math.Exp(-4.0*(x-0.5)))
}

// ─── Epoch rotation ───────────────────────────────────────────────────────────

// EpochParams controls how port shuffle epoch length varies with m_t.
type EpochParams struct {
	// BaseEpochSeconds is the epoch length at m_t = 0 (no attacker pressure).
	// Default: 3600 (1 hour).
	BaseEpochSeconds int64

	// MinEpochSeconds is the minimum epoch length at m_t = 1 (maximum pressure).
	// Default: 300 (5 minutes).
	MinEpochSeconds int64
}

// DefaultEpochParams returns the default epoch parameters.
func DefaultEpochParams() EpochParams {
	return EpochParams{BaseEpochSeconds: 3600, MinEpochSeconds: 300}
}

// epochLengthSeconds computes the epoch length in seconds for a given m_t.
//
// Formula: epoch_s = max(MinEpochSeconds, floor(BaseEpochSeconds * (1 - m_t)))
//
// At m_t=0.0: epoch = BaseEpochSeconds (1h default)
// At m_t=0.5: epoch = BaseEpochSeconds/2 (30m default)
// At m_t=1.0: epoch = MinEpochSeconds (5m default)
func epochLengthSeconds(mt float64, p EpochParams) int64 {
	length := int64(float64(p.BaseEpochSeconds) * (1.0 - mt))
	if length < p.MinEpochSeconds {
		return p.MinEpochSeconds
	}
	return length
}

// currentEpoch returns the current epoch index for a given m_t and epoch params.
// epoch = unix_time / epoch_length_seconds
func currentEpoch(mt float64, p EpochParams) int64 {
	epochLen := epochLengthSeconds(mt, p)
	return time.Now().Unix() / epochLen
}

// ─── Decoy event sink ─────────────────────────────────────────────────────────

// DecoyEvent is emitted by the decoy listener when a connection is received.
// It is fed into the escalation engine's event pipeline as a synthetic event.
type DecoyEvent struct {
	// PID is the PID of the process that owns the decoy (the quarantined process).
	PID uint32

	// RemoteAddr is the address of the connecting client.
	RemoteAddr string

	// DecoyPort is the port the decoy was listening on.
	DecoyPort int

	// Timestamp is when the connection was received.
	Timestamp time.Time
}

// DecoyEventSink is the interface for receiving decoy connection events.
// Implemented by the escalation engine's event pipeline.
// The decoy listener calls Emit() for every connection attempt.
//
// Contract:
//   - Emit() must be goroutine-safe.
//   - Emit() must not block (use a buffered channel internally).
//   - Emit() must not panic.
type DecoyEventSink interface {
	Emit(evt DecoyEvent)
}

// ChannelDecoyEventSink is the reference implementation of DecoyEventSink.
// It enforces the non-blocking contract via select/default: if the channel
// is full, the event is dropped and the drop counter is incremented.
//
// A slow or stuck escalation engine cannot deadlock the decoy goroutine.
// The drop counter is exposed for Prometheus scraping.
//
// Usage:
//
//	sink := NewChannelDecoyEventSink(256)
//	go func() {
//	    for evt := range sink.C {
//	        // feed into escalation engine
//	    }
//	}()
type ChannelDecoyEventSink struct {
	// C is the channel of decoy events. The consumer reads from this channel.
	C chan DecoyEvent

	// Dropped is the number of events dropped due to a full channel.
	// Read with atomic.LoadUint64.
	Dropped uint64

	mu sync.Mutex // protects Dropped (uint64 alignment not guaranteed on 32-bit)
}

// NewChannelDecoyEventSink creates a ChannelDecoyEventSink with the given
// channel buffer size. bufSize=256 is a reasonable default for most workloads.
func NewChannelDecoyEventSink(bufSize int) *ChannelDecoyEventSink {
	return &ChannelDecoyEventSink{C: make(chan DecoyEvent, bufSize)}
}

// Emit sends evt to the channel. If the channel is full, the event is dropped
// and the drop counter is incremented. Never blocks. Goroutine-safe.
func (s *ChannelDecoyEventSink) Emit(evt DecoyEvent) {
	select {
	case s.C <- evt:
	default:
		s.mu.Lock()
		s.Dropped++
		s.mu.Unlock()
	}
}

// DroppedCount returns the number of dropped events since creation.
func (s *ChannelDecoyEventSink) DroppedCount() uint64 {
	s.mu.Lock()
	defer s.mu.Unlock()
	return s.Dropped
}

// DecoyEventSinkNop is a no-op implementation of DecoyEventSink for testing.
type DecoyEventSinkNop struct{}

func (DecoyEventSinkNop) Emit(DecoyEvent) {}


// ─── Config ───────────────────────────────────────────────────────────────────

// CamouflageConfig holds the configuration for the camouflage module.
type CamouflageConfig struct {
	// Enabled gates all camouflage actions. Default: false.
	Enabled bool

	// NodeID is used as the PRNG seed for deterministic port selection.
	NodeID string

	// PortBase is the base port for the shuffle range.
	// Shuffled ports are selected from [PortBase, PortBase+PortRange).
	// Default: 32768.
	PortBase int

	// PortRange is the number of ports available for shuffling.
	// Default: 16384 (ephemeral range).
	PortRange int

	// DecoyEnabled controls whether a decoy listener is opened.
	// Default: true (when Enabled=true).
	DecoyEnabled bool

	// DecoyBindAddr is the address the decoy listener binds to.
	// Default: "127.0.0.1" (loopback only).
	//
	// Rationale: OCTOREFLEX's threat model is local attacker processes on the
	// same host. Binding to loopback means the decoy is only reachable by
	// processes on this host, not by external scanners. This avoids exposing
	// an additional TCP port on external interfaces.
	//
	// Set to "0.0.0.0" only if the threat model includes remote attackers
	// who have already reached the host's network interface (e.g., after
	// lateral movement from another host). In that case, the decoy provides
	// an additional signal for remote reconnaissance detection.
	DecoyBindAddr string

	// HintDir is the directory where port/IP hint files are written.
	// Default: /run/octoreflex.
	HintDir string

	// HintGID is the GID of the octoreflex group for hint file ownership.
	// Hint files are chowned to root:HintGID with mode 0600.
	// Default: 0 (root).
	HintGID int

	// ControlLaw holds λ₁/λ₂ parameters. Must match simulator config.
	ControlLaw ControlLawParams

	// Epoch controls port shuffle rotation frequency vs m_t.
	Epoch EpochParams

	// SeverityMax is the maximum severity score (denominator for anomaly signal).
	// Must match escalation.ThresholdTerminated.
	SeverityMax float64
}

// DefaultCamouflageConfig returns the default camouflage configuration.
func DefaultCamouflageConfig() CamouflageConfig {
	return CamouflageConfig{
		Enabled:       false,
		PortBase:      32768,
		PortRange:     16384,
		DecoyEnabled:  true,
		DecoyBindAddr: "127.0.0.1",
		HintDir:       "/run/octoreflex",
		HintGID:       0,
		ControlLaw:    DefaultControlLawParams(),
		Epoch:         DefaultEpochParams(),
		SeverityMax:   10.0,
	}
}

// ─── Hint file types ──────────────────────────────────────────────────────────

type portHint struct {
	PID           uint32    `json:"pid"`
	OldPort       int       `json:"old_port"`
	NewPort       int       `json:"new_port"`
	ValidFrom     time.Time `json:"valid_from"`
	Epoch         int64     `json:"epoch"`
	EpochLengthS  int64     `json:"epoch_length_s"`
	MutationRate  float64   `json:"mutation_rate_mt"`
}

type ipHint struct {
	PID          uint32    `json:"pid"`
	Reason       string    `json:"reason"`
	Severity     float64   `json:"severity"`
	MutationRate float64   `json:"mutation_rate_mt"`
	CreatedAt    time.Time `json:"created_at"`
}

// ─── Engine ───────────────────────────────────────────────────────────────────

type camouflageEntry struct {
	pid         uint32
	activeState State
	decoyLis    net.Listener
	decoyPort   int
}

// CamouflageEngine manages defensive deception actions.
type CamouflageEngine struct {
	cfg    CamouflageConfig
	sink   DecoyEventSink // nil if no sink configured
	log    *zap.Logger
	mu     sync.Mutex
	active map[uint32]*camouflageEntry
}

// NewCamouflageEngine creates a CamouflageEngine.
// sink may be nil (decoy events will be logged but not fed to the pipeline).
func NewCamouflageEngine(cfg CamouflageConfig, sink DecoyEventSink, log *zap.Logger) *CamouflageEngine {
	return &CamouflageEngine{
		cfg:    cfg,
		sink:   sink,
		log:    log,
		active: make(map[uint32]*camouflageEntry),
	}
}

// Activate applies camouflage actions appropriate for the given state.
// Idempotent: no-op if already active at this or higher state.
//
// Parameters:
//   - pid:      process ID
//   - state:    current isolation state
//   - severity: composite severity score S (used to compute A_t and m_t)
//   - mt:       current mutation rate from the control law (caller maintains state)
func (e *CamouflageEngine) Activate(pid uint32, state State, severity, mt float64) {
	if !e.cfg.Enabled || state < StateIsolated {
		return
	}

	e.mu.Lock()
	defer e.mu.Unlock()

	entry, exists := e.active[pid]
	if exists && entry.activeState >= state {
		return
	}
	if !exists {
		entry = &camouflageEntry{pid: pid}
		e.active[pid] = entry
	}
	entry.activeState = state

	// Compute epoch index using m_t-dependent epoch length.
	// Higher m_t → shorter epoch → faster port rotation.
	epoch := currentEpoch(mt, e.cfg.Epoch)
	epochLen := epochLengthSeconds(mt, e.cfg.Epoch)

	// Action 1: Port shuffle (S2+).
	newPort := e.deterministicPort(pid, epoch)
	hint := portHint{
		PID:          pid,
		NewPort:      newPort,
		ValidFrom:    time.Now(),
		Epoch:        epoch,
		EpochLengthS: epochLen,
		MutationRate: mt,
	}
	e.writeHint("port_hints.json", hint)
	e.log.Info("camouflage: port shuffle",
		zap.Uint32("pid", pid),
		zap.Int("new_port", newPort),
		zap.Int64("epoch_len_s", epochLen),
		zap.Float64("mt", mt))

	// Action 2: Decoy listener (S3+).
	if state >= StateFrozen && e.cfg.DecoyEnabled && entry.decoyLis == nil {
		decoyPort := e.deterministicPort(pid, epoch+1)
		bindAddr := e.cfg.DecoyBindAddr
		if bindAddr == "" {
			bindAddr = "127.0.0.1" // Safe default: loopback only.
		}
		lis, err := net.Listen("tcp", fmt.Sprintf("%s:%d", bindAddr, decoyPort))
		if err == nil {
			entry.decoyLis = lis
			entry.decoyPort = decoyPort
			go e.runDecoy(lis, pid, decoyPort)
			e.log.Info("camouflage: decoy listener started",
				zap.Uint32("pid", pid),
				zap.Int("decoy_port", decoyPort))
		} else {
			e.log.Warn("camouflage: decoy listener failed",
				zap.Uint32("pid", pid), zap.Error(err))
		}
	}

	// Action 3: IP rotation hint (S4+).
	if state >= StateQuarantined {
		ipH := ipHint{
			PID:          pid,
			Reason:       fmt.Sprintf("state=%s severity=%.2f mt=%.3f", state.String(), severity, mt),
			Severity:     severity,
			MutationRate: mt,
			CreatedAt:    time.Now(),
		}
		e.writeHint("ip_hints.json", ipH)
		e.log.Info("camouflage: IP rotation hint written",
			zap.Uint32("pid", pid),
			zap.Float64("severity", severity),
			zap.Float64("mt", mt))
	}
}

// Deactivate reverses all active camouflage actions for a PID.
func (e *CamouflageEngine) Deactivate(pid uint32) {
	e.mu.Lock()
	defer e.mu.Unlock()

	entry, ok := e.active[pid]
	if !ok {
		return
	}
	if entry.decoyLis != nil {
		_ = entry.decoyLis.Close()
		e.log.Info("camouflage: decoy listener stopped", zap.Uint32("pid", pid))
	}
	delete(e.active, pid)
}

// deterministicPort computes a port in [PortBase, PortBase+PortRange) using
// sha256(nodeID || uint32LE(pid) || int64LE(epoch)).
//
// Pure function: same inputs always produce the same output.
// This allows legitimate clients to predict the next port given the epoch.
func (e *CamouflageEngine) deterministicPort(pid uint32, epoch int64) int {
	h := sha256.New()
	_, _ = h.Write([]byte(e.cfg.NodeID))
	pidB := make([]byte, 4)
	binary.LittleEndian.PutUint32(pidB, pid)
	_, _ = h.Write(pidB)
	epochB := make([]byte, 8)
	binary.LittleEndian.PutUint64(epochB, uint64(epoch))
	_, _ = h.Write(epochB)
	sum := h.Sum(nil)
	// Use uint32 to avoid negative modulo from int overflow.
	offset := int(binary.LittleEndian.Uint32(sum[:4]) % uint32(e.cfg.PortRange))
	return e.cfg.PortBase + offset
}

// runDecoy runs the decoy TCP listener.
//
// Every connection attempt emits a DecoyEvent to the escalation engine's
// event pipeline via the DecoyEventSink. This makes the decoy an ACTIVE
// component of the control loop — connections to the decoy directly increase
// the anomaly score for the connecting PID, not just log a warning.
//
// The decoy never sends data. It accepts the connection, emits the event,
// and immediately closes.
func (e *CamouflageEngine) runDecoy(lis net.Listener, pid uint32, port int) {
	defer lis.Close()
	for {
		conn, err := lis.Accept()
		if err != nil {
			return // Listener closed (Deactivate called).
		}
		remoteAddr := conn.RemoteAddr().String()
		_ = conn.Close() // Never send data.

		evt := DecoyEvent{
			PID:        pid,
			RemoteAddr: remoteAddr,
			DecoyPort:  port,
			Timestamp:  time.Now(),
		}

		e.log.Warn("camouflage: decoy connection received",
			zap.Uint32("pid", pid),
			zap.String("remote_addr", remoteAddr),
			zap.Int("decoy_port", port))

		// Feed directly into the escalation engine's event pipeline.
		// This is the active feedback loop: decoy connections increase
		// the anomaly score for the connecting IP's associated PID.
		if e.sink != nil {
			e.sink.Emit(evt)
		}
	}
}

// writeHint writes a JSON hint file atomically:
//   1. Marshal to JSON.
//   2. Write to <path>.tmp with mode 0600.
//   3. Chown <path>.tmp to root:HintGID.
//   4. Rename <path>.tmp → <path> (atomic on Linux).
//
// This ensures readers never observe a partial write, and the file is
// always owned by root with restricted permissions.
func (e *CamouflageEngine) writeHint(filename string, v any) {
	data, err := json.MarshalIndent(v, "", "  ")
	if err != nil {
		e.log.Error("camouflage: marshal hint", zap.Error(err))
		return
	}
	path := e.cfg.HintDir + "/" + filename
	tmp := path + ".tmp"

	if err := os.WriteFile(tmp, data, 0o600); err != nil {
		e.log.Error("camouflage: write hint tmp", zap.String("path", tmp), zap.Error(err))
		return
	}

	// Chown to root:HintGID before rename to avoid a window where the file
	// is readable by the wrong owner.
	if err := os.Chown(tmp, 0, e.cfg.HintGID); err != nil {
		// Non-fatal: log and continue. The file is still 0600 (root-only).
		e.log.Warn("camouflage: chown hint tmp", zap.String("path", tmp), zap.Error(err))
	}

	if err := os.Rename(tmp, path); err != nil {
		e.log.Error("camouflage: rename hint", zap.String("tmp", tmp), zap.String("path", path), zap.Error(err))
		_ = os.Remove(tmp)
	}
}
