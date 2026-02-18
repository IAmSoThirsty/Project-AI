// Package bpf — events.go
//
// KernelEvent mirrors the struct octo_event defined in octoreflex.h.
// The Go struct must have identical memory layout to the C struct so that
// the ring buffer consumer can cast raw bytes directly without copying.
//
// C layout (24 bytes, 8-byte aligned):
//   [0..3]   pid          u32
//   [4..7]   uid          u32
//   [8]      event_type   u8
//   [9..11]  _pad         u8[3]
//   [12..15] _pad2        u32
//   [16..23] timestamp_ns s64
//
// Go struct uses explicit padding fields to match this layout exactly.
// unsafe.Sizeof(KernelEvent{}) must equal 24.

package bpf

import (
	"encoding/binary"
	"fmt"
	"unsafe"
)

// EventType mirrors octo_event_type_t from octoreflex.h.
type EventType uint8

const (
	EventSocketConnect EventType = 1
	EventFileOpen      EventType = 2
	EventSetUID        EventType = 3
)

// String returns a human-readable event type name.
func (e EventType) String() string {
	switch e {
	case EventSocketConnect:
		return "socket_connect"
	case EventFileOpen:
		return "file_open"
	case EventSetUID:
		return "setuid"
	default:
		return fmt.Sprintf("unknown(%d)", uint8(e))
	}
}

// KernelEvent is the Go representation of struct octo_event.
// Layout must match the C struct exactly (verified by init() below).
type KernelEvent struct {
	PID         uint32    // [0..3]
	UID         uint32    // [4..7]
	EventType   EventType // [8]
	_pad        [3]uint8  // [9..11]
	_pad2       uint32    // [12..15]
	TimestampNS int64     // [16..23]
}

// expectedEventSize is the expected size of KernelEvent in bytes.
// Must match sizeof(struct octo_event) in C.
const expectedEventSize = 24

func init() {
	if sz := unsafe.Sizeof(KernelEvent{}); sz != expectedEventSize {
		panic(fmt.Sprintf(
			"KernelEvent size mismatch: Go=%d bytes, expected=%d bytes. "+
				"Check struct padding against octoreflex.h.",
			sz, expectedEventSize,
		))
	}
}

// ParseEvent deserialises a raw ring buffer record into a KernelEvent.
// The record must be exactly expectedEventSize bytes.
// Returns an error if the record is malformed.
//
// Byte order: little-endian (x86_64 kernel, x86_64 userspace).
func ParseEvent(raw []byte) (KernelEvent, error) {
	if len(raw) < expectedEventSize {
		return KernelEvent{}, fmt.Errorf(
			"event record too short: got %d bytes, expected %d",
			len(raw), expectedEventSize,
		)
	}

	var e KernelEvent
	e.PID = binary.LittleEndian.Uint32(raw[0:4])
	e.UID = binary.LittleEndian.Uint32(raw[4:8])
	e.EventType = EventType(raw[8])
	// raw[9..15] are padding — skip.
	e.TimestampNS = int64(binary.LittleEndian.Uint64(raw[16:24]))
	return e, nil
}
