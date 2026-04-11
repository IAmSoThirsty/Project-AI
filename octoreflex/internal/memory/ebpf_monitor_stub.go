// +build !linux

package memory

import (
	"fmt"
	"runtime"
)

type MemoryMonitor struct {
	unsupported bool
}

type EventType uint32
type MemoryEvent struct{}
type MonitorStats struct{}
type EventHandler interface{}
type EventHandlerFunc func(*MemoryEvent) error

func (f EventHandlerFunc) HandleEvent(event *MemoryEvent) error {
	return f(event)
}

const (
	EventMalloc EventType = iota
	EventFree
	EventMmap
	EventMunmap
	EventMprotect
	EventBrk
	EventStackGrow
	EventBufferOverflow
	EventUseAfterFree
	EventDoubleFree
	EventPtraceAttach
	EventCoreDump
)

func NewMemoryMonitor() (*MemoryMonitor, error) {
	return nil, fmt.Errorf("memory monitor not supported on %s", runtime.GOOS)
}

func (mm *MemoryMonitor) RegisterHandler(handler EventHandler) {}

func (mm *MemoryMonitor) UnregisterHandler(handler EventHandler) {}

func (mm *MemoryMonitor) GetStats() MonitorStats {
	return MonitorStats{}
}

func (mm *MemoryMonitor) Close() error {
	return nil
}

func (mm *MemoryMonitor) InjectEvent(event *MemoryEvent) {}

func GetEventName(eventType EventType) string {
	return "unknown"
}

func (e *MemoryEvent) String() string {
	return "MemoryEvent{}"
}
