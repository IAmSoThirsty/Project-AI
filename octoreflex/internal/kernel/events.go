// Package kernel — events.go
//
// Ring buffer event processor for OCTOREFLEX.
//
// This package consumes kernel events from the BPF ring buffer and feeds
// them into the anomaly engine pipeline.
//
// Architecture:
//
//	[BPF Ring Buffer]
//	      ↓  (cilium/ebpf ringbuf.Reader)
//	[Event Processor goroutine]
//	      ↓  (buffered channel, cap=EventQueueSize)
//	[Worker goroutines (MaxGoroutines)]
//	      ↓
//	[Feature Aggregator → Anomaly Engine → Escalation Engine]
//
// Backpressure:
//   - If the in-memory channel is full, new events are dropped and
//     metrics.EventsDroppedTotal{reason="queue_full"} is incremented.
//   - Ring buffer overflow (kernel side) is tracked via the per-CPU
//     drop counter map and exposed as metrics.EventsDroppedTotal{reason="ringbuf_overflow"}.
//
// Shutdown:
//   - ctx cancellation stops the reader goroutine cleanly.
//   - The event channel is drained before the processor exits.

package kernel

import (
	"context"
	"fmt"
	"time"

	"github.com/cilium/ebpf/ringbuf"
	"go.uber.org/zap"

	bpfpkg "github.com/octoreflex/octoreflex/internal/bpf"
	"github.com/octoreflex/octoreflex/internal/observability"
)

// Processor reads kernel events from the BPF ring buffer and dispatches
// them to registered handlers.
type Processor struct {
	objs    *bpfpkg.Objects
	metrics *observability.Metrics
	log     *zap.Logger
	queue   chan bpfpkg.KernelEvent
	queueCap int
}

// NewProcessor creates a Processor with the given queue capacity.
// queueCap must be > 0 (typically config.Agent.EventQueueSize = 10000).
func NewProcessor(
	objs *bpfpkg.Objects,
	metrics *observability.Metrics,
	log *zap.Logger,
	queueCap int,
) *Processor {
	return &Processor{
		objs:     objs,
		metrics:  metrics,
		log:      log,
		queue:    make(chan bpfpkg.KernelEvent, queueCap),
		queueCap: queueCap,
	}
}

// Run starts the ring buffer reader and returns the event channel.
// The caller should spawn worker goroutines reading from the returned channel.
// Run blocks until ctx is cancelled, then closes the channel.
//
// Failure modes:
//   - If the ring buffer reader fails to open: returns error immediately.
//   - If an individual record is malformed: logged and skipped (not fatal).
//   - If the queue is full: event dropped, metric incremented.
func (p *Processor) Run(ctx context.Context) (<-chan bpfpkg.KernelEvent, error) {
	rd, err := ringbuf.NewReader(p.objs.Events)
	if err != nil {
		return nil, fmt.Errorf("ringbuf.NewReader: %w", err)
	}

	go func() {
		defer close(p.queue)
		defer rd.Close()

		// Periodically read the kernel-side drop counter and update metrics.
		dropTicker := time.NewTicker(5 * time.Second)
		defer dropTicker.Stop()

		var lastDropCount uint64

		for {
			select {
			case <-ctx.Done():
				return
			case <-dropTicker.C:
				// Read kernel-side ring buffer drop counter.
				total, err := p.objs.ReadDropCount()
				if err != nil {
					p.log.Warn("failed to read drop counter", zap.Error(err))
					continue
				}
				delta := total - lastDropCount
				if delta > 0 {
					p.metrics.EventsDroppedTotal.WithLabelValues("ringbuf_overflow").Add(float64(delta))
					lastDropCount = total
				}
			default:
				// Read next record from ring buffer.
				// SetDeadline allows us to check ctx cancellation periodically.
				_ = rd.SetDeadline(time.Now().Add(100 * time.Millisecond))
				record, err := rd.Read()
				if err != nil {
					if ringbuf.IsUnrecoverableError(err) {
						p.log.Error("unrecoverable ring buffer error", zap.Error(err))
						return
					}
					// Timeout or temporary error — loop and check ctx.
					continue
				}

				// Parse the raw bytes into a KernelEvent.
				event, err := bpfpkg.ParseEvent(record.RawSample)
				if err != nil {
					p.log.Warn("malformed kernel event", zap.Error(err),
						zap.Int("raw_len", len(record.RawSample)))
					continue
				}

				// Update metrics.
				p.metrics.EventsProcessedTotal.WithLabelValues(event.EventType.String()).Inc()
				p.metrics.EventQueueDepth.Set(float64(len(p.queue)))

				// Dispatch to queue with backpressure.
				select {
				case p.queue <- event:
					// Dispatched successfully.
				default:
					// Queue full — drop event.
					p.metrics.EventsDroppedTotal.WithLabelValues("queue_full").Inc()
					p.log.Debug("event queue full, dropping event",
						zap.Uint32("pid", event.PID),
						zap.String("type", event.EventType.String()))
				}
			}
		}
	}()

	return p.queue, nil
}
