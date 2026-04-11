// Package bpf — events_test.go
//
// Unit tests for KernelEvent parsing and event type definitions.

package bpf

import (
	"encoding/binary"
	"testing"
	"unsafe"
)

func TestEventTypeString(t *testing.T) {
	tests := []struct {
		eventType EventType
		expected  string
	}{
		{EventSocketConnect, "socket_connect"},
		{EventFileOpen, "file_open"},
		{EventSetUID, "setuid"},
		{EventExec, "exec"},
		{EventMmap, "mmap"},
		{EventPtrace, "ptrace"},
		{EventModuleLoad, "module_load"},
		{EventBPFLoad, "bpf_load"},
		{EventMemViolation, "mem_violation"},
		{EventType(99), "unknown(99)"},
	}

	for _, tt := range tests {
		t.Run(tt.expected, func(t *testing.T) {
			if got := tt.eventType.String(); got != tt.expected {
				t.Errorf("EventType.String() = %q, want %q", got, tt.expected)
			}
		})
	}
}

func TestParseEvent(t *testing.T) {
	tests := []struct {
		name      string
		raw       []byte
		wantEvent KernelEvent
		wantErr   bool
	}{
		{
			name: "valid socket_connect event",
			raw: func() []byte {
				buf := make([]byte, 24)
				binary.LittleEndian.PutUint32(buf[0:4], 1234)       // PID
				binary.LittleEndian.PutUint32(buf[4:8], 1000)       // UID
				buf[8] = uint8(EventSocketConnect)                  // EventType
				buf[9] = 0                                          // Flags
				binary.LittleEndian.PutUint32(buf[12:16], 0)        // Metadata
				binary.LittleEndian.PutUint64(buf[16:24], 123456789) // TimestampNS
				return buf
			}(),
			wantEvent: KernelEvent{
				PID:         1234,
				UID:         1000,
				EventType:   EventSocketConnect,
				Flags:       0,
				Metadata:    0,
				TimestampNS: 123456789,
			},
			wantErr: false,
		},
		{
			name: "valid exec event with flags",
			raw: func() []byte {
				buf := make([]byte, 24)
				binary.LittleEndian.PutUint32(buf[0:4], 5678)       // PID
				binary.LittleEndian.PutUint32(buf[4:8], 0)          // UID
				buf[8] = uint8(EventExec)                           // EventType
				buf[9] = 0x01                                       // Flags: OCTO_FLAG_EXEC_SUID
				binary.LittleEndian.PutUint32(buf[12:16], 0755)     // Metadata: file mode
				binary.LittleEndian.PutUint64(buf[16:24], 987654321) // TimestampNS
				return buf
			}(),
			wantEvent: KernelEvent{
				PID:         5678,
				UID:         0,
				EventType:   EventExec,
				Flags:       0x01,
				Metadata:    0755,
				TimestampNS: 987654321,
			},
			wantErr: false,
		},
		{
			name: "valid mmap event with W^X violation",
			raw: func() []byte {
				buf := make([]byte, 24)
				binary.LittleEndian.PutUint32(buf[0:4], 9999)       // PID
				binary.LittleEndian.PutUint32(buf[4:8], 1001)       // UID
				buf[8] = uint8(EventMmap)                           // EventType
				buf[9] = 0x06                                       // Flags: EXEC | WRITE
				binary.LittleEndian.PutUint32(buf[12:16], 0x7)      // Metadata: prot flags
				binary.LittleEndian.PutUint64(buf[16:24], 111111111) // TimestampNS
				return buf
			}(),
			wantEvent: KernelEvent{
				PID:         9999,
				UID:         1001,
				EventType:   EventMmap,
				Flags:       0x06,
				Metadata:    0x7,
				TimestampNS: 111111111,
			},
			wantErr: false,
		},
		{
			name:    "too short record",
			raw:     make([]byte, 16),
			wantErr: true,
		},
		{
			name:    "empty record",
			raw:     []byte{},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := ParseEvent(tt.raw)
			if (err != nil) != tt.wantErr {
				t.Errorf("ParseEvent() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if err == nil {
				if got.PID != tt.wantEvent.PID {
					t.Errorf("ParseEvent().PID = %d, want %d", got.PID, tt.wantEvent.PID)
				}
				if got.UID != tt.wantEvent.UID {
					t.Errorf("ParseEvent().UID = %d, want %d", got.UID, tt.wantEvent.UID)
				}
				if got.EventType != tt.wantEvent.EventType {
					t.Errorf("ParseEvent().EventType = %v, want %v", got.EventType, tt.wantEvent.EventType)
				}
				if got.Flags != tt.wantEvent.Flags {
					t.Errorf("ParseEvent().Flags = 0x%x, want 0x%x", got.Flags, tt.wantEvent.Flags)
				}
				if got.Metadata != tt.wantEvent.Metadata {
					t.Errorf("ParseEvent().Metadata = %d, want %d", got.Metadata, tt.wantEvent.Metadata)
				}
				if got.TimestampNS != tt.wantEvent.TimestampNS {
					t.Errorf("ParseEvent().TimestampNS = %d, want %d", got.TimestampNS, tt.wantEvent.TimestampNS)
				}
			}
		})
	}
}

func TestKernelEventSize(t *testing.T) {
	// Verify KernelEvent struct size matches expected 24 bytes
	var event KernelEvent
	size := int(unsafe.Sizeof(event))
	if size != expectedEventSize {
		t.Errorf("KernelEvent size = %d bytes, want %d bytes", size, expectedEventSize)
	}
}

func BenchmarkParseEvent(b *testing.B) {
	buf := make([]byte, 24)
	binary.LittleEndian.PutUint32(buf[0:4], 1234)
	binary.LittleEndian.PutUint32(buf[4:8], 1000)
	buf[8] = uint8(EventSocketConnect)
	buf[9] = 0
	binary.LittleEndian.PutUint32(buf[12:16], 0)
	binary.LittleEndian.PutUint64(buf[16:24], 123456789)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := ParseEvent(buf)
		if err != nil {
			b.Fatal(err)
		}
	}
}
