// +build linux

package memory

import (
	"bytes"
	_ "embed"
	"encoding/binary"
	"fmt"
	"log"
	"sync"
	"unsafe"

	"github.com/cilium/ebpf"
	"github.com/cilium/ebpf/link"
	"github.com/cilium/ebpf/perf"
	"github.com/cilium/ebpf/ringbuf"
)

//go:embed bpf/memory_monitor.o
var memoryMonitorBPF []byte

// MemoryMonitor monitors memory operations using eBPF
type MemoryMonitor struct {
	mu       sync.RWMutex
	objs     *memoryMonitorObjects
	links    []link.Link
	reader   *ringbuf.Reader
	perfRead *perf.Reader
	handlers []EventHandler
	stats    *MonitorStats
	stopCh   chan struct{}
	wg       sync.WaitGroup
}

// EventType represents types of memory events
type EventType uint32

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

// MemoryEvent represents a memory-related event
type MemoryEvent struct {
	Type      EventType
	Timestamp uint64
	PID       uint32
	TID       uint32
	Addr      uint64
	Size      uint64
	Flags     uint32
	Comm      [16]byte
}

// MonitorStats tracks monitoring statistics
type MonitorStats struct {
	mu             sync.RWMutex
	EventsReceived uint64
	EventsDropped  uint64
	MallocCalls    uint64
	FreeCalls      uint64
	MmapCalls      uint64
	MunmapCalls    uint64
	MprotectCalls  uint64
	Violations     uint64
	PtraceBlocked  uint64
	CoreDumpBlocked uint64
}

// EventHandler handles memory events
type EventHandler interface {
	HandleEvent(event *MemoryEvent) error
}

// EventHandlerFunc is a function adapter for EventHandler
type EventHandlerFunc func(*MemoryEvent) error

func (f EventHandlerFunc) HandleEvent(event *MemoryEvent) error {
	return f(event)
}

// memoryMonitorObjects contains eBPF program objects
type memoryMonitorObjects struct {
	Programs map[string]*ebpf.Program
	Maps     map[string]*ebpf.Map
}

// NewMemoryMonitor creates a new memory monitor
func NewMemoryMonitor() (*MemoryMonitor, error) {
	mm := &MemoryMonitor{
		stats:  &MonitorStats{},
		stopCh: make(chan struct{}),
	}

	// Load eBPF programs
	if err := mm.loadBPF(); err != nil {
		return nil, fmt.Errorf("failed to load eBPF programs: %w", err)
	}

	// Attach to hooks
	if err := mm.attachHooks(); err != nil {
		mm.Close()
		return nil, fmt.Errorf("failed to attach hooks: %w", err)
	}

	// Start event reader
	if err := mm.startEventReader(); err != nil {
		mm.Close()
		return nil, fmt.Errorf("failed to start event reader: %w", err)
	}

	return mm, nil
}

// loadBPF loads eBPF programs
func (mm *MemoryMonitor) loadBPF() error {
	// In a real implementation, this would load the compiled eBPF object
	// For now, we'll create a placeholder structure
	mm.objs = &memoryMonitorObjects{
		Programs: make(map[string]*ebpf.Program),
		Maps:     make(map[string]*ebpf.Map),
	}

	// Note: In production, you would load from memoryMonitorBPF
	// spec, err := ebpf.LoadCollectionSpecFromReader(bytes.NewReader(memoryMonitorBPF))
	// if err != nil {
	//     return fmt.Errorf("failed to load spec: %w", err)
	// }

	return nil
}

// attachHooks attaches eBPF programs to kernel hooks
func (mm *MemoryMonitor) attachHooks() error {
	// Attach to memory allocation tracepoints
	hooks := []struct {
		name  string
		group string
		event string
	}{
		{"malloc", "syscalls", "sys_enter_brk"},
		{"mmap", "syscalls", "sys_enter_mmap"},
		{"munmap", "syscalls", "sys_exit_munmap"},
		{"mprotect", "syscalls", "sys_enter_mprotect"},
		{"ptrace", "syscalls", "sys_enter_ptrace"},
	}

	_ = hooks // Mark as used
	
	// In production, attach to tracepoints
	// for _, h := range hooks {
	//     prog := mm.objs.Programs[h.name]
	//     l, err := link.Tracepoint(h.group, h.event, prog, nil)
	//     if err != nil {
	//         return fmt.Errorf("failed to attach %s: %w", h.name, err)
	//     }
	//     mm.links = append(mm.links, l)
	// }

	return nil
}

// startEventReader starts reading events from eBPF
func (mm *MemoryMonitor) startEventReader() error {
	// In production, create ring buffer reader
	// rd, err := ringbuf.NewReader(mm.objs.Maps["events"])
	// if err != nil {
	//     return fmt.Errorf("failed to create ring buffer reader: %w", err)
	// }
	// mm.reader = rd

	// Start event processing goroutine
	mm.wg.Add(1)
	go mm.processEvents()

	return nil
}

// processEvents processes events from eBPF
func (mm *MemoryMonitor) processEvents() {
	defer mm.wg.Done()

	for {
		select {
		case <-mm.stopCh:
			return
		default:
			// In production, read from ring buffer
			// record, err := mm.reader.Read()
			// if err != nil {
			//     if errors.Is(err, ringbuf.ErrClosed) {
			//         return
			//     }
			//     continue
			// }

			// Parse and handle event
			// event := mm.parseEvent(record.RawSample)
			// mm.handleEvent(event)
		}
	}
}

// parseEvent parses raw eBPF event data
func (mm *MemoryMonitor) parseEvent(data []byte) *MemoryEvent {
	if len(data) < int(unsafe.Sizeof(MemoryEvent{})) {
		return nil
	}

	buf := bytes.NewReader(data)
	event := &MemoryEvent{}

	binary.Read(buf, binary.LittleEndian, &event.Type)
	binary.Read(buf, binary.LittleEndian, &event.Timestamp)
	binary.Read(buf, binary.LittleEndian, &event.PID)
	binary.Read(buf, binary.LittleEndian, &event.TID)
	binary.Read(buf, binary.LittleEndian, &event.Addr)
	binary.Read(buf, binary.LittleEndian, &event.Size)
	binary.Read(buf, binary.LittleEndian, &event.Flags)
	binary.Read(buf, binary.LittleEndian, &event.Comm)

	return event
}

// handleEvent processes a memory event
func (mm *MemoryMonitor) handleEvent(event *MemoryEvent) {
	if event == nil {
		return
	}

	// Update stats
	mm.stats.mu.Lock()
	mm.stats.EventsReceived++

	switch event.Type {
	case EventMalloc:
		mm.stats.MallocCalls++
	case EventFree:
		mm.stats.FreeCalls++
	case EventMmap:
		mm.stats.MmapCalls++
	case EventMunmap:
		mm.stats.MunmapCalls++
	case EventMprotect:
		mm.stats.MprotectCalls++
	case EventPtraceAttach:
		mm.stats.PtraceBlocked++
		mm.stats.Violations++
	case EventCoreDump:
		mm.stats.CoreDumpBlocked++
		mm.stats.Violations++
	case EventBufferOverflow, EventUseAfterFree, EventDoubleFree:
		mm.stats.Violations++
	}
	mm.stats.mu.Unlock()

	// Call registered handlers
	mm.mu.RLock()
	handlers := mm.handlers
	mm.mu.RUnlock()

	for _, handler := range handlers {
		if err := handler.HandleEvent(event); err != nil {
			log.Printf("event handler error: %v", err)
		}
	}
}

// RegisterHandler registers an event handler
func (mm *MemoryMonitor) RegisterHandler(handler EventHandler) {
	mm.mu.Lock()
	defer mm.mu.Unlock()
	mm.handlers = append(mm.handlers, handler)
}

// UnregisterHandler removes an event handler
func (mm *MemoryMonitor) UnregisterHandler(handler EventHandler) {
	mm.mu.Lock()
	defer mm.mu.Unlock()

	for i, h := range mm.handlers {
		if h == handler {
			mm.handlers = append(mm.handlers[:i], mm.handlers[i+1:]...)
			return
		}
	}
}

// GetStats returns current monitor statistics
func (mm *MemoryMonitor) GetStats() MonitorStats {
	mm.stats.mu.RLock()
	defer mm.stats.mu.RUnlock()
	return *mm.stats
}

// Close stops the monitor and cleans up resources
func (mm *MemoryMonitor) Close() error {
	// Signal stop
	close(mm.stopCh)

	// Wait for event processor
	mm.wg.Wait()

	// Close ring buffer reader
	if mm.reader != nil {
		mm.reader.Close()
	}

	if mm.perfRead != nil {
		mm.perfRead.Close()
	}

	// Detach all links
	for _, l := range mm.links {
		l.Close()
	}

	// Close all programs and maps
	if mm.objs != nil {
		for _, prog := range mm.objs.Programs {
			prog.Close()
		}
		for _, m := range mm.objs.Maps {
			m.Close()
		}
	}

	return nil
}

// InjectEvent manually injects an event (for testing)
func (mm *MemoryMonitor) InjectEvent(event *MemoryEvent) {
	mm.handleEvent(event)
}

// GetEventName returns a human-readable name for an event type
func GetEventName(eventType EventType) string {
	names := map[EventType]string{
		EventMalloc:         "malloc",
		EventFree:           "free",
		EventMmap:           "mmap",
		EventMunmap:         "munmap",
		EventMprotect:       "mprotect",
		EventBrk:            "brk",
		EventStackGrow:      "stack_grow",
		EventBufferOverflow: "buffer_overflow",
		EventUseAfterFree:   "use_after_free",
		EventDoubleFree:     "double_free",
		EventPtraceAttach:   "ptrace_attach",
		EventCoreDump:       "core_dump",
	}

	if name, ok := names[eventType]; ok {
		return name
	}
	return fmt.Sprintf("unknown_%d", eventType)
}

// String returns string representation of event
func (e *MemoryEvent) String() string {
	comm := string(bytes.TrimRight(e.Comm[:], "\x00"))
	return fmt.Sprintf("MemoryEvent{Type=%s, PID=%d, TID=%d, Addr=0x%x, Size=%d, Comm=%s}",
		GetEventName(e.Type), e.PID, e.TID, e.Addr, e.Size, comm)
}
