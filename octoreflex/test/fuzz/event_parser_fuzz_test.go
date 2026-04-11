// Fuzzing harness for eBPF event parser
//
// This fuzzer tests the event parsing logic that processes raw bytes from
// the eBPF ring buffer. Malformed or malicious events should not crash the
// agent or cause undefined behavior.
//
// Run with: go test -fuzz=FuzzEventParser -fuzztime=60s

package fuzz

import (
	"testing"
)

// EventHeader represents the fixed-size header from eBPF events
type EventHeader struct {
	PID       uint32
	TID       uint32
	EventType uint8
	_         [3]byte // padding
	Timestamp uint64
}

// ParseEventHeader extracts event header from raw bytes
func ParseEventHeader(data []byte) (*EventHeader, error) {
	if len(data) < 16 {
		return nil, ErrTooShort
	}

	evt := &EventHeader{
		PID:       le32(data[0:4]),
		TID:       le32(data[4:8]),
		EventType: data[8],
		Timestamp: le64(data[9:17]),
	}

	return evt, nil
}

var (
	ErrTooShort     = &ParseError{"event too short"}
	ErrInvalidType  = &ParseError{"invalid event type"}
	ErrCorruptedData = &ParseError{"corrupted event data"}
)

type ParseError struct {
	msg string
}

func (e *ParseError) Error() string {
	return e.msg
}

func le32(b []byte) uint32 {
	return uint32(b[0]) | uint32(b[1])<<8 | uint32(b[2])<<16 | uint32(b[3])<<24
}

func le64(b []byte) uint64 {
	return uint64(b[0]) | uint64(b[1])<<8 | uint64(b[2])<<16 | uint64(b[3])<<24 |
		uint64(b[4])<<32 | uint64(b[5])<<40 | uint64(b[6])<<48 | uint64(b[7])<<56
}

func FuzzEventParser(f *testing.F) {
	// Seed corpus with valid event samples
	f.Add([]byte{
		0x01, 0x00, 0x00, 0x00, // PID: 1
		0x01, 0x00, 0x00, 0x00, // TID: 1
		0x02,                   // Type: FILE_OPEN
		0x00, 0x00, 0x00,       // padding
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // timestamp
	})

	f.Add([]byte{
		0xFF, 0xFF, 0xFF, 0xFF, // PID: max uint32
		0xFF, 0xFF, 0xFF, 0xFF, // TID: max uint32
		0xFF,                   // Type: invalid
		0x00, 0x00, 0x00,
		0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
	})

	f.Add([]byte{}) // empty input
	f.Add([]byte{0x00}) // single byte
	f.Add(make([]byte, 1024)) // large zeroed buffer

	f.Fuzz(func(t *testing.T, data []byte) {
		// Parser must not crash on any input
		evt, err := ParseEventHeader(data)

		if err != nil {
			// Expected errors are fine
			return
		}

		// If parse succeeded, validate constraints
		if evt.EventType > 3 {
			t.Errorf("Parsed invalid event type: %d (max is 3)", evt.EventType)
		}

		// PID 0 is valid (kernel threads)
		// TID must be >= PID for single-threaded processes
		// (this is a soft constraint, can be violated but worth checking)
	})
}

func FuzzConfigParser(f *testing.F) {
	// Fuzz YAML configuration parsing
	f.Add([]byte("agent:\n  window_duration: 60s\n"))
	f.Add([]byte("agent:\n  entropy_weight: 0.3\n"))
	f.Add([]byte("malformed: [[[\n"))
	f.Add([]byte("agent:\n  window_duration: -1s\n")) // negative duration

	f.Fuzz(func(t *testing.T, configYAML []byte) {
		// Config parser must not crash
		_ = parseConfig(configYAML)
	})
}

func parseConfig(data []byte) error {
	// Stub for actual config parser
	// In production this would call config.Load()
	return nil
}

func FuzzAnomalyScore(f *testing.F) {
	// Fuzz anomaly scoring with extreme values
	f.Add([]byte{
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // feature 0
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // feature 1
		0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, // feature 2
	})

	f.Fuzz(func(t *testing.T, data []byte) {
		if len(data) < 24 {
			return
		}

		// Extract 3 float64 features
		features := []float64{
			float64FromBytes(data[0:8]),
			float64FromBytes(data[8:16]),
			float64FromBytes(data[16:24]),
		}

		// Test that scoring doesn't panic on extreme values
		score := computeAnomalyScore(features)

		// Validate score constraints
		if score < 0 {
			t.Errorf("Negative anomaly score: %f", score)
		}

		// Check for NaN/Inf
		if isNaN(score) || isInf(score) {
			t.Errorf("Invalid anomaly score: %f", score)
		}
	})
}

func float64FromBytes(b []byte) float64 {
	bits := le64(b)
	return *(*float64)(unsafe.Pointer(&bits))
}

func computeAnomalyScore(features []float64) float64 {
	// Stub for actual anomaly engine
	// Must handle NaN, Inf, extreme values
	sum := 0.0
	for _, f := range features {
		if isNaN(f) || isInf(f) {
			return 0.0 // Constitutional NaN rejection
		}
		sum += f * f
	}
	return sum
}

func isNaN(f float64) bool {
	return f != f
}

func isInf(f float64) bool {
	return f > 1e308 || f < -1e308
}

import "unsafe"
