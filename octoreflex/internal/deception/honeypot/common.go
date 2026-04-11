// Package honeypot — common.go
//
// Common interfaces and types for honeypot implementations.
//
// Purpose:
//   Defines the common interface for all honeypot types and shared
//   event handling infrastructure.

package honeypot

import (
	"context"
	"time"
)

// EventType represents the type of honeypot event.
type EventType string

const (
	EventTypeSSHAttempt  EventType = "ssh_attempt"
	EventTypeHTTPAttempt EventType = "http_attempt"
	EventTypeDBAttempt   EventType = "db_attempt"
	EventTypeSMBAttempt  EventType = "smb_attempt"
)

// HoneypotEvent represents a generic honeypot event.
type HoneypotEvent struct {
	Type       EventType
	RemoteAddr string
	Timestamp  time.Time
	Metadata   map[string]interface{}
}

// EventSink receives honeypot events for processing.
type EventSink interface {
	Emit(evt HoneypotEvent)
}

// ChannelEventSink is a channel-based event sink.
type ChannelEventSink struct {
	C chan HoneypotEvent
}

// NewChannelEventSink creates a new channel-based event sink.
func NewChannelEventSink(bufSize int) *ChannelEventSink {
	return &ChannelEventSink{
		C: make(chan HoneypotEvent, bufSize),
	}
}

// Emit sends an event to the channel.
func (s *ChannelEventSink) Emit(evt HoneypotEvent) {
	select {
	case s.C <- evt:
	default:
		// Drop event if channel is full
	}
}

// HoneypotStats represents statistics for a honeypot.
type HoneypotStats struct {
	Type             string
	TotalConnections int
	ActiveSessions   int
	TotalAttempts    int
	UniqueIPs        int
	Metadata         map[string]interface{}
}

// Honeypot is the common interface for all honeypot implementations.
type Honeypot interface {
	// Start starts the honeypot listener.
	Start(ctx context.Context) error

	// Stop stops the honeypot.
	Stop() error

	// GetStats returns honeypot statistics.
	GetStats() HoneypotStats
}
