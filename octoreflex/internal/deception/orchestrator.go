// Package deception — orchestrator.go
//
// Deception orchestrator for coordinating all deception mechanisms.
//
// Purpose:
//   Central coordinator that integrates honeypots, port rotation,
//   TCP decoys, cost amplification, and analytics into a unified
//   deception layer.
//
// Features:
//   - Unified configuration and lifecycle management
//   - Event aggregation and correlation
//   - Integration with OctoReflex state machine
//   - Real-time metrics and analytics

package deception

import (
	"context"
	"fmt"
	"sync"
	"time"

	"github.com/octoreflex/internal/deception/honeypot"
	"go.uber.org/zap"
)

// OrchestratorConfig configures the deception orchestrator.
type OrchestratorConfig struct {
	// Enabled controls whether deception is active.
	Enabled bool

	// PortRotation configuration.
	PortRotation PortRotationConfig

	// TCPDecoy configuration.
	TCPDecoy TCPDecoyConfig

	// CostAmplifier configuration.
	CostAmplifier CostAmplifierConfig

	// Honeypots configuration.
	EnableSSHHoneypot  bool
	EnableHTTPHoneypot bool

	SSHHoneypot  honeypot.SSHHoneypotConfig
	HTTPHoneypot honeypot.HTTPHoneypotConfig

	// Analytics configuration.
	EnableAnalytics bool
	AnalyticsWindow time.Duration
}

// DefaultOrchestratorConfig returns default configuration.
func DefaultOrchestratorConfig() OrchestratorConfig {
	return OrchestratorConfig{
		Enabled:            true,
		PortRotation:       DefaultPortRotationConfig(),
		TCPDecoy:           DefaultTCPDecoyConfig(),
		CostAmplifier:      DefaultCostAmplifierConfig(),
		EnableSSHHoneypot:  true,
		EnableHTTPHoneypot: true,
		SSHHoneypot:        honeypot.DefaultSSHHoneypotConfig(),
		HTTPHoneypot:       honeypot.DefaultHTTPHoneypotConfig(),
		EnableAnalytics:    true,
		AnalyticsWindow:    24 * time.Hour,
	}
}

// Orchestrator coordinates all deception mechanisms.
type Orchestrator struct {
	cfg           OrchestratorConfig
	log           *zap.Logger
	ctx           context.Context
	cancel        context.CancelFunc
	mu            sync.RWMutex
	portRotation  *PortRotation
	tcpDecoy      *TCPDecoy
	costAmplifier *CostAmplifier
	sshHoneypot   *honeypot.SSHHoneypot
	httpHoneypot  *honeypot.HTTPHoneypot
	eventChan     chan DeceptionEvent
	analytics     *Analytics
	running       bool
}

// NewOrchestrator creates a new deception orchestrator.
func NewOrchestrator(cfg OrchestratorConfig, log *zap.Logger) (*Orchestrator, error) {
	if !cfg.Enabled {
		log.Info("deception orchestrator disabled")
		return nil, nil
	}

	ctx, cancel := context.WithCancel(context.Background())

	// Create event channel
	eventChan := make(chan DeceptionEvent, 1000)

	// Create components
	portRotation, err := NewPortRotation(cfg.PortRotation, log)
	if err != nil {
		cancel()
		return nil, fmt.Errorf("create port rotation: %w", err)
	}

	tcpDecoy := NewTCPDecoy(cfg.TCPDecoy, log)
	costAmplifier := NewCostAmplifier(cfg.CostAmplifier, log)

	var analytics *Analytics
	if cfg.EnableAnalytics {
		analytics = NewAnalytics(cfg.AnalyticsWindow, log)
	}

	o := &Orchestrator{
		cfg:           cfg,
		log:           log,
		ctx:           ctx,
		cancel:        cancel,
		portRotation:  portRotation,
		tcpDecoy:      tcpDecoy,
		costAmplifier: costAmplifier,
		eventChan:     eventChan,
		analytics:     analytics,
	}

	// Create honeypots
	if cfg.EnableSSHHoneypot {
		cfg.SSHHoneypot.EventSink = honeypot.NewChannelEventSink(100)
		sshHP, err := honeypot.NewSSHHoneypot(cfg.SSHHoneypot, log)
		if err != nil {
			cancel()
			return nil, fmt.Errorf("create SSH honeypot: %w", err)
		}
		o.sshHoneypot = sshHP
	}

	if cfg.EnableHTTPHoneypot {
		cfg.HTTPHoneypot.EventSink = honeypot.NewChannelEventSink(100)
		o.httpHoneypot = honeypot.NewHTTPHoneypot(cfg.HTTPHoneypot, log)
	}

	return o, nil
}

// Start starts all deception mechanisms.
func (o *Orchestrator) Start() error {
	if !o.cfg.Enabled {
		return nil
	}

	o.mu.Lock()
	defer o.mu.Unlock()

	if o.running {
		return fmt.Errorf("already running")
	}

	o.log.Info("starting deception orchestrator")

	// Start TCP decoy
	if err := o.tcpDecoy.Start(); err != nil {
		return fmt.Errorf("start TCP decoy: %w", err)
	}

	// Start honeypots
	if o.sshHoneypot != nil {
		if err := o.sshHoneypot.Start(o.ctx); err != nil {
			return fmt.Errorf("start SSH honeypot: %w", err)
		}
	}

	if o.httpHoneypot != nil {
		if err := o.httpHoneypot.Start(o.ctx); err != nil {
			return fmt.Errorf("start HTTP honeypot: %w", err)
		}
	}

	// Start event processing
	go o.processEvents()

	o.running = true
	o.log.Info("deception orchestrator started")

	return nil
}

// Stop stops all deception mechanisms.
func (o *Orchestrator) Stop() error {
	if !o.cfg.Enabled {
		return nil
	}

	o.mu.Lock()
	defer o.mu.Unlock()

	if !o.running {
		return nil
	}

	o.log.Info("stopping deception orchestrator")

	o.cancel()

	// Stop components
	if o.tcpDecoy != nil {
		o.tcpDecoy.Stop()
	}

	if o.sshHoneypot != nil {
		o.sshHoneypot.Stop()
	}

	if o.httpHoneypot != nil {
		o.httpHoneypot.Stop()
	}

	close(o.eventChan)

	o.running = false
	o.log.Info("deception orchestrator stopped")

	return nil
}

// processEvents processes deception events.
func (o *Orchestrator) processEvents() {
	// Collect events from honeypots
	if o.sshHoneypot != nil && o.cfg.SSHHoneypot.EventSink != nil {
		sink := o.cfg.SSHHoneypot.EventSink.(*honeypot.ChannelEventSink)
		go func() {
			for evt := range sink.C {
				o.eventChan <- DeceptionEvent{
					Type:      "ssh_honeypot",
					Timestamp: evt.Timestamp,
					Source:    evt.RemoteAddr,
					Metadata:  evt.Metadata,
				}
			}
		}()
	}

	if o.httpHoneypot != nil && o.cfg.HTTPHoneypot.EventSink != nil {
		sink := o.cfg.HTTPHoneypot.EventSink.(*honeypot.ChannelEventSink)
		go func() {
			for evt := range sink.C {
				o.eventChan <- DeceptionEvent{
					Type:      "http_honeypot",
					Timestamp: evt.Timestamp,
					Source:    evt.RemoteAddr,
					Metadata:  evt.Metadata,
				}
			}
		}()
	}

	// Process events
	for evt := range o.eventChan {
		o.handleEvent(evt)
	}
}

// handleEvent handles a single deception event.
func (o *Orchestrator) handleEvent(evt DeceptionEvent) {
	o.log.Debug("deception event",
		zap.String("type", evt.Type),
		zap.String("source", evt.Source))

	// Record in analytics
	if o.analytics != nil {
		o.analytics.RecordEvent(evt)
	}

	// TODO: Feed into OctoReflex state machine
	// This would emit events to the escalation engine
}

// SetThreatLevel adjusts deception mechanisms based on threat level.
func (o *Orchestrator) SetThreatLevel(level float64) {
	o.mu.Lock()
	defer o.mu.Unlock()

	o.portRotation.SetThreatLevel(level)

	o.log.Info("threat level updated",
		zap.Float64("level", level))
}

// GetCurrentPort returns the current port for a service.
func (o *Orchestrator) GetCurrentPort(serviceID string) int {
	return o.portRotation.GetCurrentPort(serviceID)
}

// GeneratePOWChallenge generates a proof-of-work challenge.
func (o *Orchestrator) GeneratePOWChallenge() POWChallenge {
	return o.costAmplifier.GeneratePOWChallenge()
}

// VerifyPOW verifies a proof-of-work solution.
func (o *Orchestrator) VerifyPOW(challenge POWChallenge, nonce uint64) bool {
	return o.costAmplifier.VerifyPOW(challenge, nonce)
}

// GetStats returns comprehensive deception statistics.
func (o *Orchestrator) GetStats() DeceptionStats {
	o.mu.RLock()
	defer o.mu.RUnlock()

	stats := DeceptionStats{
		Enabled:       o.cfg.Enabled,
		Running:       o.running,
		PortRotation:  o.portRotation.GetSequenceInfo(),
		CostAmplifier: o.costAmplifier.GetStats(),
		CostBreakdown: o.costAmplifier.CalculateCostUSD(),
	}

	if o.tcpDecoy != nil {
		stats.TCPDecoy = o.tcpDecoy.GetStats()
	}

	if o.sshHoneypot != nil {
		stats.SSHHoneypot = o.sshHoneypot.GetStats()
	}

	if o.httpHoneypot != nil {
		stats.HTTPHoneypot = o.httpHoneypot.GetStats()
	}

	if o.analytics != nil {
		stats.Analytics = o.analytics.GetStats()
	}

	return stats
}

// DeceptionEvent represents a deception event.
type DeceptionEvent struct {
	Type      string
	Timestamp time.Time
	Source    string
	Metadata  map[string]interface{}
}

// DeceptionStats contains comprehensive deception statistics.
type DeceptionStats struct {
	Enabled       bool
	Running       bool
	PortRotation  SequenceInfo
	TCPDecoy      TCPDecoyStats
	CostAmplifier CostAmplifierStats
	CostBreakdown CostBreakdown
	SSHHoneypot   honeypot.HoneypotStats
	HTTPHoneypot  honeypot.HoneypotStats
	Analytics     AnalyticsStats
}

// Analytics tracks and analyzes deception events.
type Analytics struct {
	log           *zap.Logger
	mu            sync.RWMutex
	window        time.Duration
	events        []DeceptionEvent
	attackerProfiles map[string]*AttackerProfile
}

// AttackerProfile tracks information about an attacker.
type AttackerProfile struct {
	IP              string
	FirstSeen       time.Time
	LastSeen        time.Time
	EventCount      int
	EventTypes      map[string]int
	EstimatedCostUSD float64
}

// NewAnalytics creates a new analytics tracker.
func NewAnalytics(window time.Duration, log *zap.Logger) *Analytics {
	return &Analytics{
		log:              log,
		window:           window,
		events:           make([]DeceptionEvent, 0, 10000),
		attackerProfiles: make(map[string]*AttackerProfile),
	}
}

// RecordEvent records a deception event.
func (a *Analytics) RecordEvent(evt DeceptionEvent) {
	a.mu.Lock()
	defer a.mu.Unlock()

	// Cleanup old events
	cutoff := time.Now().Add(-a.window)
	newEvents := make([]DeceptionEvent, 0, len(a.events))
	for _, e := range a.events {
		if e.Timestamp.After(cutoff) {
			newEvents = append(newEvents, e)
		}
	}
	a.events = newEvents

	// Add new event
	a.events = append(a.events, evt)

	// Update attacker profile
	if profile, exists := a.attackerProfiles[evt.Source]; exists {
		profile.LastSeen = evt.Timestamp
		profile.EventCount++
		profile.EventTypes[evt.Type]++
	} else {
		a.attackerProfiles[evt.Source] = &AttackerProfile{
			IP:         evt.Source,
			FirstSeen:  evt.Timestamp,
			LastSeen:   evt.Timestamp,
			EventCount: 1,
			EventTypes: map[string]int{evt.Type: 1},
		}
	}
}

// GetStats returns analytics statistics.
func (a *Analytics) GetStats() AnalyticsStats {
	a.mu.RLock()
	defer a.mu.RUnlock()

	eventTypeCount := make(map[string]int)
	for _, evt := range a.events {
		eventTypeCount[evt.Type]++
	}

	return AnalyticsStats{
		TotalEvents:       len(a.events),
		UniqueAttackers:   len(a.attackerProfiles),
		EventTypeCount:    eventTypeCount,
		WindowDuration:    a.window,
	}
}

// AnalyticsStats contains analytics statistics.
type AnalyticsStats struct {
	TotalEvents     int
	UniqueAttackers int
	EventTypeCount  map[string]int
	WindowDuration  time.Duration
}
