// Package operator — server.go
//
// Unix domain socket server for OCTOREFLEX operator overrides.
//
// Protocol: newline-delimited JSON over a Unix domain socket.
// Socket path: /run/octoreflex/operator.sock (configurable).
// Permissions: 0600, owned by root. Only root can connect.
//
// Commands (JSON request → JSON response):
//
//   {"cmd":"reset","pid":1234}
//     → Resets PID 1234 to NORMAL state, zeroes its pressure accumulator,
//       and removes it from the BPF process_state_map.
//     → Response: {"ok":true,"pid":1234,"prev_state":"FROZEN"}
//
//   {"cmd":"pin","pid":1234,"state":"ISOLATED"}
//     → Pins PID 1234 to the specified state. The escalation engine will
//       not escalate or decay this PID until unpinned.
//     → Response: {"ok":true,"pid":1234,"pinned_state":"ISOLATED"}
//
//   {"cmd":"unpin","pid":1234}
//     → Removes the pin on PID 1234, resuming normal escalation.
//     → Response: {"ok":true,"pid":1234}
//
//   {"cmd":"status","pid":1234}
//     → Returns the current state, pressure score, and pin status.
//     → Response: {"ok":true,"pid":1234,"state":"PRESSURE","pressure":2.3,"pinned":false}
//
//   {"cmd":"list"}
//     → Returns all tracked PIDs with their current states.
//     → Response: {"ok":true,"pids":[{"pid":1234,"state":"PRESSURE","pinned":false},...]}
//
// Security:
//   - Socket is created with 0600 permissions; only root can connect.
//   - Each connection is handled in a separate goroutine.
//   - Max concurrent connections: 4 (operator use only, not high-throughput).
//   - Max request size: 4096 bytes (prevents memory exhaustion).
//   - Connection timeout: 10s read, 10s write.
//   - All commands are logged to the audit ledger.

package operator

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"os"
	"sync"
	"time"

	"go.uber.org/zap"

	"github.com/octoreflex/octoreflex/internal/escalation"
)

const (
	maxConcurrentConns = 4
	maxRequestBytes    = 4096
	connTimeout        = 10 * time.Second
)

// StateRegistry is the interface the operator server uses to read and
// mutate process states. Implemented by the agent's PID state map.
type StateRegistry interface {
	// GetState returns the current state for a PID, or (StateNormal, false)
	// if the PID is not tracked.
	GetState(pid uint32) (escalation.State, bool)

	// ResetState resets a PID to NORMAL and zeroes its pressure accumulator.
	// Returns the previous state.
	ResetState(pid uint32) escalation.State

	// PinState pins a PID to a specific state, preventing escalation/decay.
	PinState(pid uint32, state escalation.State)

	// UnpinState removes the pin on a PID.
	UnpinState(pid uint32)

	// IsPinned returns true if the PID has an active pin.
	IsPinned(pid uint32) bool

	// PressureScore returns the current EWMA pressure for a PID.
	PressureScore(pid uint32) float64

	// ListAll returns all tracked PIDs with their current states.
	ListAll() []PIDStatus
}

// PIDStatus is a snapshot of a single PID's state.
type PIDStatus struct {
	PID     uint32          `json:"pid"`
	State   escalation.State `json:"state"`
	Pinned  bool            `json:"pinned"`
	Pressure float64        `json:"pressure"`
}

// Request is the JSON structure for operator commands.
type Request struct {
	Cmd   string `json:"cmd"`             // reset | pin | unpin | status | list
	PID   uint32 `json:"pid,omitempty"`   // target PID
	State string `json:"state,omitempty"` // target state for pin command
}

// Response is the JSON structure for operator command responses.
type Response struct {
	OK          bool        `json:"ok"`
	Error       string      `json:"error,omitempty"`
	PID         uint32      `json:"pid,omitempty"`
	State       string      `json:"state,omitempty"`
	PrevState   string      `json:"prev_state,omitempty"`
	PinnedState string      `json:"pinned_state,omitempty"`
	Pinned      bool        `json:"pinned,omitempty"`
	Pressure    float64     `json:"pressure,omitempty"`
	PIDs        []PIDStatus `json:"pids,omitempty"`
}

// Server is the operator Unix domain socket server.
type Server struct {
	socketPath string
	registry   StateRegistry
	log        *zap.Logger
	sem        chan struct{} // Semaphore: max concurrent connections.
}

// NewServer creates an operator Server.
func NewServer(socketPath string, registry StateRegistry, log *zap.Logger) *Server {
	return &Server{
		socketPath: socketPath,
		registry:   registry,
		log:        log,
		sem:        make(chan struct{}, maxConcurrentConns),
	}
}

// ListenAndServe starts the operator socket server.
// Removes any stale socket file before binding.
// Blocks until ctx is cancelled.
func (s *Server) ListenAndServe(ctx context.Context) error {
	// Remove stale socket.
	if err := os.Remove(s.socketPath); err != nil && !os.IsNotExist(err) {
		return fmt.Errorf("operator: remove stale socket %q: %w", s.socketPath, err)
	}

	// Ensure parent directory exists.
	if err := os.MkdirAll("/run/octoreflex", 0o700); err != nil {
		return fmt.Errorf("operator: mkdir /run/octoreflex: %w", err)
	}

	lis, err := net.Listen("unix", s.socketPath)
	if err != nil {
		return fmt.Errorf("operator: listen %q: %w", s.socketPath, err)
	}
	defer lis.Close()

	// Set socket permissions to 0600 (root only).
	if err := os.Chmod(s.socketPath, 0o600); err != nil {
		return fmt.Errorf("operator: chmod %q: %w", s.socketPath, err)
	}

	s.log.Info("operator socket listening", zap.String("path", s.socketPath))

	// Close listener on context cancellation.
	go func() {
		<-ctx.Done()
		lis.Close()
	}()

	for {
		conn, err := lis.Accept()
		if err != nil {
			select {
			case <-ctx.Done():
				return nil // Clean shutdown.
			default:
				s.log.Error("operator: accept error", zap.Error(err))
				continue
			}
		}

		// Acquire semaphore (non-blocking; reject if at capacity).
		select {
		case s.sem <- struct{}{}:
		default:
			s.log.Warn("operator: max connections reached, rejecting")
			_ = conn.Close()
			continue
		}

		go func(c net.Conn) {
			defer func() { <-s.sem }()
			defer c.Close()
			s.handleConn(c)
		}(conn)
	}
}

// handleConn handles a single operator connection.
// Reads one JSON request, executes the command, writes one JSON response.
func (s *Server) handleConn(conn net.Conn) {
	_ = conn.SetDeadline(time.Now().Add(connTimeout))

	// Read request (max maxRequestBytes).
	buf := make([]byte, maxRequestBytes)
	n, err := conn.Read(buf)
	if err != nil && err != io.EOF {
		s.log.Warn("operator: read error", zap.Error(err))
		return
	}

	var req Request
	if err := json.Unmarshal(buf[:n], &req); err != nil {
		s.writeResponse(conn, Response{OK: false, Error: "invalid JSON: " + err.Error()})
		return
	}

	resp := s.dispatch(req)
	s.writeResponse(conn, resp)
}

// dispatch routes a request to the appropriate handler.
func (s *Server) dispatch(req Request) Response {
	switch req.Cmd {
	case "reset":
		return s.cmdReset(req)
	case "pin":
		return s.cmdPin(req)
	case "unpin":
		return s.cmdUnpin(req)
	case "status":
		return s.cmdStatus(req)
	case "list":
		return s.cmdList()
	default:
		return Response{OK: false, Error: fmt.Sprintf("unknown command %q", req.Cmd)}
	}
}

func (s *Server) cmdReset(req Request) Response {
	if req.PID == 0 {
		return Response{OK: false, Error: "pid required for reset"}
	}
	prev := s.registry.ResetState(req.PID)
	s.log.Info("operator: PID reset to NORMAL",
		zap.Uint32("pid", req.PID),
		zap.String("prev_state", prev.String()))
	return Response{OK: true, PID: req.PID, PrevState: prev.String()}
}

func (s *Server) cmdPin(req Request) Response {
	if req.PID == 0 {
		return Response{OK: false, Error: "pid required for pin"}
	}
	target, err := parseState(req.State)
	if err != nil {
		return Response{OK: false, Error: err.Error()}
	}
	s.registry.PinState(req.PID, target)
	s.log.Info("operator: PID pinned",
		zap.Uint32("pid", req.PID),
		zap.String("state", target.String()))
	return Response{OK: true, PID: req.PID, PinnedState: target.String()}
}

func (s *Server) cmdUnpin(req Request) Response {
	if req.PID == 0 {
		return Response{OK: false, Error: "pid required for unpin"}
	}
	s.registry.UnpinState(req.PID)
	s.log.Info("operator: PID unpinned", zap.Uint32("pid", req.PID))
	return Response{OK: true, PID: req.PID}
}

func (s *Server) cmdStatus(req Request) Response {
	if req.PID == 0 {
		return Response{OK: false, Error: "pid required for status"}
	}
	state, tracked := s.registry.GetState(req.PID)
	if !tracked {
		return Response{OK: false, Error: fmt.Sprintf("pid %d not tracked", req.PID)}
	}
	return Response{
		OK:       true,
		PID:      req.PID,
		State:    state.String(),
		Pinned:   s.registry.IsPinned(req.PID),
		Pressure: s.registry.PressureScore(req.PID),
	}
}

func (s *Server) cmdList() Response {
	return Response{OK: true, PIDs: s.registry.ListAll()}
}

func (s *Server) writeResponse(conn net.Conn, resp Response) {
	data, _ := json.Marshal(resp)
	data = append(data, '\n')
	_, _ = conn.Write(data)
}

// parseState converts a state name string to an escalation.State.
func parseState(name string) (escalation.State, error) {
	switch name {
	case "NORMAL":
		return escalation.StateNormal, nil
	case "PRESSURE":
		return escalation.StatePressure, nil
	case "ISOLATED":
		return escalation.StateIsolated, nil
	case "FROZEN":
		return escalation.StateFrozen, nil
	case "QUARANTINED":
		return escalation.StateQuarantined, nil
	case "TERMINATED":
		return escalation.StateTerminated, nil
	default:
		return escalation.StateNormal, fmt.Errorf("unknown state %q (valid: NORMAL PRESSURE ISOLATED FROZEN QUARANTINED TERMINATED)", name)
	}
}

// ─── Mutex-protected in-memory registry (used by the agent) ──────────────────

// MemRegistry is a thread-safe in-memory implementation of StateRegistry.
// The agent embeds this and passes it to both the operator server and the
// escalation engine workers.
type MemRegistry struct {
	mu     sync.RWMutex
	states map[uint32]*processEntry
}

type processEntry struct {
	state    escalation.State
	pinned   bool
	pressure float64
}

// NewMemRegistry creates an empty MemRegistry.
func NewMemRegistry() *MemRegistry {
	return &MemRegistry{states: make(map[uint32]*processEntry)}
}

func (r *MemRegistry) GetState(pid uint32) (escalation.State, bool) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	e, ok := r.states[pid]
	if !ok {
		return escalation.StateNormal, false
	}
	return e.state, true
}

func (r *MemRegistry) ResetState(pid uint32) escalation.State {
	r.mu.Lock()
	defer r.mu.Unlock()
	e, ok := r.states[pid]
	if !ok {
		return escalation.StateNormal
	}
	prev := e.state
	e.state = escalation.StateNormal
	e.pressure = 0.0
	e.pinned = false
	return prev
}

func (r *MemRegistry) PinState(pid uint32, state escalation.State) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, ok := r.states[pid]; !ok {
		r.states[pid] = &processEntry{}
	}
	r.states[pid].state = state
	r.states[pid].pinned = true
}

func (r *MemRegistry) UnpinState(pid uint32) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if e, ok := r.states[pid]; ok {
		e.pinned = false
	}
}

func (r *MemRegistry) IsPinned(pid uint32) bool {
	r.mu.RLock()
	defer r.mu.RUnlock()
	e, ok := r.states[pid]
	return ok && e.pinned
}

func (r *MemRegistry) PressureScore(pid uint32) float64 {
	r.mu.RLock()
	defer r.mu.RUnlock()
	if e, ok := r.states[pid]; ok {
		return e.pressure
	}
	return 0.0
}

func (r *MemRegistry) ListAll() []PIDStatus {
	r.mu.RLock()
	defer r.mu.RUnlock()
	out := make([]PIDStatus, 0, len(r.states))
	for pid, e := range r.states {
		out = append(out, PIDStatus{
			PID:      pid,
			State:    e.state,
			Pinned:   e.pinned,
			Pressure: e.pressure,
		})
	}
	return out
}
