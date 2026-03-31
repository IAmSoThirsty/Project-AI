// Package observability — metrics.go
//
// Prometheus metrics for the OCTOREFLEX agent.
//
// Endpoint: GET /metrics on 127.0.0.1:9091 (configurable).
// Format: Prometheus text exposition format (OpenMetrics compatible).
// Bind: loopback only — no external exposure.
//
// Metric naming convention: octoreflex_<subsystem>_<name>_<unit>
//
// All metrics are registered on a dedicated prometheus.Registry (not the
// default global registry) to avoid collisions with other instrumented
// libraries in the same process.
//
// Cardinality control:
//   - State labels use the string state name (6 values max).
//   - PID is NOT used as a label (unbounded cardinality).
//   - Per-PID metrics are aggregated before recording.

package observability

import (
	"context"
	"fmt"
	"net/http"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// Metrics holds all Prometheus metric descriptors for OCTOREFLEX.
type Metrics struct {
	registry *prometheus.Registry

	// ─── Event processing ────────────────────────────────────────────────────

	// EventsProcessedTotal counts kernel events consumed from the ring buffer.
	// Labels: event_type (socket_connect, file_open, setuid)
	EventsProcessedTotal *prometheus.CounterVec

	// EventsDroppedTotal counts events dropped due to queue overflow.
	// Labels: reason (queue_full, ringbuf_overflow)
	EventsDroppedTotal *prometheus.CounterVec

	// EventQueueDepth is the current in-memory event queue depth.
	EventQueueDepth prometheus.Gauge

	// ─── Anomaly engine ───────────────────────────────────────────────────────

	// AnomalyScoreHistogram records the distribution of anomaly scores.
	AnomalyScoreHistogram prometheus.Histogram

	// AnomalyEvalsTotal counts anomaly evaluations performed.
	AnomalyEvalsTotal prometheus.Counter

	// ─── Escalation ───────────────────────────────────────────────────────────

	// StateTransitionsTotal counts state transitions.
	// Labels: from_state, to_state
	StateTransitionsTotal *prometheus.CounterVec

	// TrackedPIDs is the current number of PIDs under monitoring.
	TrackedPIDs prometheus.Gauge

	// ─── Budget ───────────────────────────────────────────────────────────────

	// BudgetTokensRemaining is the current token bucket level.
	BudgetTokensRemaining prometheus.Gauge

	// BudgetConsumedTotal counts total tokens consumed.
	BudgetConsumedTotal prometheus.Counter

	// BudgetRefillsTotal counts token bucket refill cycles.
	BudgetRefillsTotal prometheus.Counter

	// ─── Gossip ───────────────────────────────────────────────────────────────

	// GossipEnvelopesReceivedTotal counts received gossip envelopes.
	// Labels: accepted (true, false)
	GossipEnvelopesReceivedTotal *prometheus.CounterVec

	// GossipEnvelopesSentTotal counts sent gossip envelopes.
	GossipEnvelopesSentTotal prometheus.Counter

	// ─── Storage ──────────────────────────────────────────────────────────────

	// StorageWriteLatency records BoltDB write transaction latency.
	StorageWriteLatency prometheus.Histogram

	// StorageLedgerEntries is the current number of ledger entries.
	StorageLedgerEntries prometheus.Gauge

	// ─── Agent ────────────────────────────────────────────────────────────────

	// AgentUptimeSeconds is the number of seconds since agent start.
	AgentUptimeSeconds prometheus.Gauge

	// startTime records when the agent started (for uptime calculation).
	startTime time.Time
}

// NewMetrics creates and registers all OCTOREFLEX Prometheus metrics.
// Returns a *Metrics with all descriptors initialised.
func NewMetrics() *Metrics {
	reg := prometheus.NewRegistry()

	m := &Metrics{
		registry:  reg,
		startTime: time.Now(),

		EventsProcessedTotal: prometheus.NewCounterVec(prometheus.CounterOpts{
			Namespace: "octoreflex",
			Subsystem: "events",
			Name:      "processed_total",
			Help:      "Total kernel events consumed from the ring buffer, by event type.",
		}, []string{"event_type"}),

		EventsDroppedTotal: prometheus.NewCounterVec(prometheus.CounterOpts{
			Namespace: "octoreflex",
			Subsystem: "events",
			Name:      "dropped_total",
			Help:      "Total events dropped due to queue or ring buffer overflow.",
		}, []string{"reason"}),

		EventQueueDepth: prometheus.NewGauge(prometheus.GaugeOpts{
			Namespace: "octoreflex",
			Subsystem: "events",
			Name:      "queue_depth",
			Help:      "Current depth of the in-memory event processing queue.",
		}),

		AnomalyScoreHistogram: prometheus.NewHistogram(prometheus.HistogramOpts{
			Namespace: "octoreflex",
			Subsystem: "anomaly",
			Name:      "score",
			Help:      "Distribution of anomaly scores computed by the Mahalanobis engine.",
			Buckets:   []float64{0.1, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0},
		}),

		AnomalyEvalsTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Namespace: "octoreflex",
			Subsystem: "anomaly",
			Name:      "evals_total",
			Help:      "Total anomaly evaluations performed.",
		}),

		StateTransitionsTotal: prometheus.NewCounterVec(prometheus.CounterOpts{
			Namespace: "octoreflex",
			Subsystem: "escalation",
			Name:      "state_transitions_total",
			Help:      "Total state transitions, by from_state and to_state.",
		}, []string{"from_state", "to_state"}),

		TrackedPIDs: prometheus.NewGauge(prometheus.GaugeOpts{
			Namespace: "octoreflex",
			Subsystem: "escalation",
			Name:      "tracked_pids",
			Help:      "Current number of PIDs under active monitoring.",
		}),

		BudgetTokensRemaining: prometheus.NewGauge(prometheus.GaugeOpts{
			Namespace: "octoreflex",
			Subsystem: "budget",
			Name:      "tokens_remaining",
			Help:      "Current token bucket level.",
		}),

		BudgetConsumedTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Namespace: "octoreflex",
			Subsystem: "budget",
			Name:      "consumed_total",
			Help:      "Lifetime total tokens consumed from the budget bucket.",
		}),

		BudgetRefillsTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Namespace: "octoreflex",
			Subsystem: "budget",
			Name:      "refills_total",
			Help:      "Total number of token bucket refill cycles completed.",
		}),

		GossipEnvelopesReceivedTotal: prometheus.NewCounterVec(prometheus.CounterOpts{
			Namespace: "octoreflex",
			Subsystem: "gossip",
			Name:      "envelopes_received_total",
			Help:      "Total gossip envelopes received, by acceptance status.",
		}, []string{"accepted"}),

		GossipEnvelopesSentTotal: prometheus.NewCounter(prometheus.CounterOpts{
			Namespace: "octoreflex",
			Subsystem: "gossip",
			Name:      "envelopes_sent_total",
			Help:      "Total gossip envelopes sent to peers.",
		}),

		StorageWriteLatency: prometheus.NewHistogram(prometheus.HistogramOpts{
			Namespace: "octoreflex",
			Subsystem: "storage",
			Name:      "write_latency_seconds",
			Help:      "BoltDB write transaction latency in seconds.",
			Buckets:   prometheus.DefBuckets,
		}),

		StorageLedgerEntries: prometheus.NewGauge(prometheus.GaugeOpts{
			Namespace: "octoreflex",
			Subsystem: "storage",
			Name:      "ledger_entries",
			Help:      "Current number of audit ledger entries in BoltDB.",
		}),

		AgentUptimeSeconds: prometheus.NewGauge(prometheus.GaugeOpts{
			Namespace: "octoreflex",
			Subsystem: "agent",
			Name:      "uptime_seconds",
			Help:      "Number of seconds since the agent started.",
		}),
	}

	// Register all metrics with the dedicated registry.
	reg.MustRegister(
		m.EventsProcessedTotal,
		m.EventsDroppedTotal,
		m.EventQueueDepth,
		m.AnomalyScoreHistogram,
		m.AnomalyEvalsTotal,
		m.StateTransitionsTotal,
		m.TrackedPIDs,
		m.BudgetTokensRemaining,
		m.BudgetConsumedTotal,
		m.BudgetRefillsTotal,
		m.GossipEnvelopesReceivedTotal,
		m.GossipEnvelopesSentTotal,
		m.StorageWriteLatency,
		m.StorageLedgerEntries,
		m.AgentUptimeSeconds,
		// Standard Go runtime metrics.
		prometheus.NewGoCollector(),
		prometheus.NewProcessCollector(prometheus.ProcessCollectorOpts{}),
	)

	return m
}

// ServeMetrics starts the Prometheus HTTP metrics server on the given address.
// Blocks until ctx is cancelled or the server fails.
// The server binds to addr (e.g., "127.0.0.1:9091") and serves GET /metrics.
// Returns an error only if the server fails to start or encounters a fatal error.
func (m *Metrics) ServeMetrics(ctx context.Context, addr string) error {
	mux := http.NewServeMux()
	mux.Handle("/metrics", promhttp.HandlerFor(m.registry, promhttp.HandlerOpts{
		EnableOpenMetrics: true,
		ErrorHandling:     promhttp.ContinueOnError,
	}))
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		_, _ = w.Write([]byte("ok"))
	})

	srv := &http.Server{
		Addr:         addr,
		Handler:      mux,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Start uptime updater goroutine.
	go m.updateUptime(ctx)

	// Shutdown on context cancellation.
	go func() {
		<-ctx.Done()
		shutdownCtx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()
		_ = srv.Shutdown(shutdownCtx)
	}()

	if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		return fmt.Errorf("metrics server on %s: %w", addr, err)
	}
	return nil
}

// updateUptime periodically updates the AgentUptimeSeconds gauge.
func (m *Metrics) updateUptime(ctx context.Context) {
	ticker := time.NewTicker(10 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-ticker.C:
			m.AgentUptimeSeconds.Set(time.Since(m.startTime).Seconds())
		case <-ctx.Done():
			return
		}
	}
}
