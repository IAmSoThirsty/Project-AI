// Package config provides configuration loading, validation, and hot-reload
// for the OCTOREFLEX agent.
//
// Configuration file: /etc/octoreflex/config.yaml (default)
// Schema version: 1
//
// Hot-reload:
//   - Agent listens for SIGHUP.
//   - On SIGHUP: re-read and re-validate config.yaml.
//   - Apply non-destructive changes only (thresholds, weights, log level).
//   - Destructive changes (DB path, BPF pin path, gossip port) require restart.
//   - If the new config is invalid, the old config remains active and an
//     error is logged. The agent does NOT crash on invalid hot-reload config.
//
// Validation:
//   - All required fields must be present.
//   - Numeric ranges enforced (e.g., alpha ∈ [0,1], weights ≥ 0).
//   - File paths must be absolute.
//   - Invalid config on startup: agent refuses to start (fatal error).
//   - Invalid config on hot-reload: logged, old config retained.

package config

import (
	"fmt"
	"os"
	"time"

	"gopkg.in/yaml.v3"
)

// Version, GitCommit, BuildTime are injected by the Makefile via -ldflags.
var (
	Version   = "dev"
	GitCommit = "unknown"
	BuildTime = "unknown"
)

// Config is the root configuration structure for OCTOREFLEX.
// All fields have defaults; see Defaults() for values.
type Config struct {
	// SchemaVersion must be "1". Future versions will trigger migration.
	SchemaVersion string `yaml:"schema_version"`

	// NodeID is a unique identifier for this OCTOREFLEX node.
	// Used in gossip envelopes and ledger entries.
	// Default: hostname.
	NodeID string `yaml:"node_id"`

	// Agent configures the userspace agent behaviour.
	Agent AgentConfig `yaml:"agent"`

	// Anomaly configures the anomaly detection engine.
	Anomaly AnomalyConfig `yaml:"anomaly"`

	// Escalation configures the state machine thresholds and weights.
	Escalation EscalationConfig `yaml:"escalation"`

	// Budget configures the token bucket.
	Budget BudgetConfig `yaml:"budget"`

	// Storage configures the BoltDB persistent store.
	Storage StorageConfig `yaml:"storage"`

	// Gossip configures the optional distributed quorum layer.
	Gossip GossipConfig `yaml:"gossip"`

	// Observability configures metrics and logging.
	Observability ObservabilityConfig `yaml:"observability"`

	// Operator configures the operator override Unix socket.
	Operator OperatorConfig `yaml:"operator"`
}

// AgentConfig holds agent-level operational parameters.
type AgentConfig struct {
	// MaxGoroutines is the maximum number of goroutines for event processing.
	// Default: 4.
	MaxGoroutines int `yaml:"max_goroutines"`

	// EventQueueSize is the in-memory event queue depth.
	// If full, new events are dropped and the drop counter is incremented.
	// Default: 10000.
	EventQueueSize int `yaml:"event_queue_size"`

	// MaxTrackedPIDs is the maximum number of PIDs tracked simultaneously.
	// Default: 8192.
	MaxTrackedPIDs int `yaml:"max_tracked_pids"`

	// WindowDuration is the sliding window duration for feature aggregation.
	// Default: 5s.
	WindowDuration time.Duration `yaml:"window_duration"`

	// WindowEvictionTimeout is the idle time after which a PID's window is
	// evicted from memory. Default: 60s.
	WindowEvictionTimeout time.Duration `yaml:"window_eviction_timeout"`

	// LightweightMode disables Prometheus metrics and gossip to reduce
	// resource consumption on edge/low-power nodes.
	// When true: metrics HTTP server is not started, gossip is forced off
	// regardless of gossip.enabled, and max_goroutines is capped at 2.
	// Default: false.
	LightweightMode bool `yaml:"lightweight_mode"`
}

// OperatorConfig holds operator override parameters.
// Overrides allow privileged operators to manually reset or pin process
// states without restarting the agent.
type OperatorConfig struct {
	// SocketPath is the Unix domain socket path for the operator CLI.
	// The CLI (octoreflex-cli) connects here to issue override commands.
	// Permissions: 0600, owned by root. Default: /run/octoreflex/operator.sock.
	SocketPath string `yaml:"socket_path"`

	// Enabled controls whether the operator socket is active.
	// Default: true.
	Enabled bool `yaml:"enabled"`
}

// AnomalyConfig holds anomaly engine parameters.
type AnomalyConfig struct {
	// EntropyWeight is wₑ in the anomaly formula A = mahal + wₑ|ΔH|.
	// Range: [0.0, 1.0]. Default: 0.3.
	EntropyWeight float64 `yaml:"entropy_weight"`

	// MaxEvalsPerSecond caps the anomaly evaluation rate.
	// Default: 10000.
	MaxEvalsPerSecond int `yaml:"max_evals_per_second"`
}

// EscalationConfig holds severity weights and state transition thresholds.
type EscalationConfig struct {
	// Weights for the composite severity formula S = w₁A + w₂Q + w₃I + w₄P.
	WeightAnomaly   float64 `yaml:"weight_anomaly"`
	WeightQuorum    float64 `yaml:"weight_quorum"`
	WeightIntegrity float64 `yaml:"weight_integrity"`
	WeightPressure  float64 `yaml:"weight_pressure"`

	// Thresholds for state transitions.
	ThresholdPressure    float64 `yaml:"threshold_pressure"`
	ThresholdIsolated    float64 `yaml:"threshold_isolated"`
	ThresholdFrozen      float64 `yaml:"threshold_frozen"`
	ThresholdQuarantined float64 `yaml:"threshold_quarantined"`
	ThresholdTerminated  float64 `yaml:"threshold_terminated"`

	// PressureAlpha is the EWMA smoothing factor α ∈ [0.0, 1.0].
	// Default: 0.8.
	PressureAlpha float64 `yaml:"pressure_alpha"`

	// CooldownDuration is the time a process must be quiescent before
	// its state decays by one level. Default: 30s.
	CooldownDuration time.Duration `yaml:"cooldown_duration"`
}

// BudgetConfig holds token bucket parameters.
type BudgetConfig struct {
	// Capacity is the maximum number of tokens. Default: 100.
	Capacity int `yaml:"capacity"`

	// RefillPeriod is the interval between full refills. Default: 60s.
	RefillPeriod time.Duration `yaml:"refill_period"`
}

// StorageConfig holds BoltDB parameters.
type StorageConfig struct {
	// DBPath is the absolute path to the BoltDB file.
	// Default: /var/lib/octoreflex/octoreflex.db.
	DBPath string `yaml:"db_path"`

	// RetentionDays is the ledger retention period. Default: 30.
	RetentionDays int `yaml:"retention_days"`
}

// GossipConfig holds the optional distributed quorum parameters.
type GossipConfig struct {
	// Enabled controls whether the gossip layer is active.
	// Default: false (standalone mode).
	Enabled bool `yaml:"enabled"`

	// ListenAddr is the gRPC listen address. Default: 0.0.0.0:9443.
	ListenAddr string `yaml:"listen_addr"`

	// Peers is the static list of peer addresses (host:port).
	Peers []string `yaml:"peers"`

	// QuorumMin is the minimum number of unique nodes that must report
	// a process as anomalous before the quorum signal is set to 1.0.
	// Default: 2.
	QuorumMin int `yaml:"quorum_min"`

	// EnvelopeTTL is the maximum age of a gossip envelope before rejection.
	// Default: 30s.
	EnvelopeTTL time.Duration `yaml:"envelope_ttl"`

	// TLSCertFile is the path to the node's TLS certificate (PEM).
	TLSCertFile string `yaml:"tls_cert_file"`

	// TLSKeyFile is the path to the node's TLS private key (PEM).
	TLSKeyFile string `yaml:"tls_key_file"`

	// TLSCAFile is the path to the CA certificate for peer verification (PEM).
	TLSCAFile string `yaml:"tls_ca_file"`

	// FederatedBaseline configures anonymized μ/Σ vector sharing between nodes.
	// When enabled, nodes periodically broadcast their baseline statistics
	// (mean vector + covariance diagonal only — no raw events) so that
	// fresh nodes can bootstrap faster than waiting for a full local window.
	// Gated by a separate toggle to keep v1 behaviour conservative.
	FederatedBaseline FederatedBaselineConfig `yaml:"federated_baseline"`
}

// FederatedBaselineConfig controls anonymized baseline sharing via gossip.
// Privacy model: only μ (mean vector) and diag(Σ) (covariance diagonal)
// are shared — never raw events or binary paths. The binary is identified
// only by its sha256 hash (same key as BoltDB baselines bucket).
type FederatedBaselineConfig struct {
	// Enabled gates federated baseline sharing. Requires gossip.enabled=true.
	// Default: false (conservative — local baselines only).
	Enabled bool `yaml:"enabled"`

	// ShareInterval is how often a node broadcasts its baselines to peers.
	// Default: 5m.
	ShareInterval time.Duration `yaml:"share_interval"`

	// MinSamples is the minimum number of local training samples required
	// before a baseline is eligible for sharing. Prevents sharing of
	// under-trained baselines that could corrupt peer learning.
	// Default: 100.
	MinSamples int `yaml:"min_samples"`

	// TrustWeight is the weight applied to federated baselines when merging
	// with local baselines. Range: [0.0, 1.0].
	// 0.0 = ignore federated data entirely.
	// 1.0 = treat federated baseline as equally trusted as local.
	// Default: 0.3 (conservative — local data dominates).
	TrustWeight float64 `yaml:"trust_weight"`
}

// ObservabilityConfig holds metrics and logging parameters.
type ObservabilityConfig struct {
	// MetricsAddr is the Prometheus metrics HTTP bind address.
	// Default: 127.0.0.1:9091.
	MetricsAddr string `yaml:"metrics_addr"`

	// LogLevel controls the minimum log level (debug, info, warn, error).
	// Default: info.
	LogLevel string `yaml:"log_level"`

	// LogFormat controls the log output format (json, console).
	// Default: json.
	LogFormat string `yaml:"log_format"`
}

// Defaults returns a Config populated with all default values.
func Defaults() Config {
	hostname, _ := os.Hostname()
	return Config{
		SchemaVersion: "1",
		NodeID:        hostname,
		Agent: AgentConfig{
			MaxGoroutines:         4,
			EventQueueSize:        10000,
			MaxTrackedPIDs:        8192,
			WindowDuration:        5 * time.Second,
			WindowEvictionTimeout: 60 * time.Second,
		},
		Anomaly: AnomalyConfig{
			EntropyWeight:     0.3,
			MaxEvalsPerSecond: 10000,
		},
		Escalation: EscalationConfig{
			WeightAnomaly:        0.4,
			WeightQuorum:         0.2,
			WeightIntegrity:      0.2,
			WeightPressure:       0.2,
			ThresholdPressure:    1.0,
			ThresholdIsolated:    3.0,
			ThresholdFrozen:      6.0,
			ThresholdQuarantined: 9.0,
			ThresholdTerminated:  12.0,
			PressureAlpha:        0.8,
			CooldownDuration:     30 * time.Second,
		},
		Budget: BudgetConfig{
			Capacity:     100,
			RefillPeriod: 60 * time.Second,
		},
		Storage: StorageConfig{
			DBPath:        DefaultDBPath,
			RetentionDays: 30,
		},
		Gossip: GossipConfig{
			Enabled:     false,
			ListenAddr:  "0.0.0.0:9443",
			QuorumMin:   2,
			EnvelopeTTL: 30 * time.Second,
			FederatedBaseline: FederatedBaselineConfig{
				Enabled:       false,
				ShareInterval: 5 * time.Minute,
				MinSamples:    100,
				TrustWeight:   0.3,
			},
		},
		Observability: ObservabilityConfig{
			MetricsAddr: "127.0.0.1:9091",
			LogLevel:    "info",
			LogFormat:   "json",
		},
		Operator: OperatorConfig{
			Enabled:    true,
			SocketPath: "/run/octoreflex/operator.sock",
		},
	}
}

// DefaultDBPath mirrors the storage package constant for use in config defaults.
const DefaultDBPath = "/var/lib/octoreflex/octoreflex.db"

// Load reads and validates a config file from the given path.
// Returns the merged config (defaults overridden by file values).
// Returns an error if the file cannot be read, parsed, or validated.
func Load(path string) (*Config, error) {
	cfg := Defaults()

	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("config.Load: read %q: %w", path, err)
	}

	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, fmt.Errorf("config.Load: parse %q: %w", path, err)
	}

	if err := Validate(&cfg); err != nil {
		return nil, fmt.Errorf("config.Load: validation failed: %w", err)
	}

	return &cfg, nil
}

// Validate checks all config fields for correctness.
// Returns a descriptive error listing all violations found.
func Validate(cfg *Config) error {
	var errs []string

	if cfg.SchemaVersion != "1" {
		errs = append(errs, fmt.Sprintf("schema_version must be \"1\", got %q", cfg.SchemaVersion))
	}
	if cfg.NodeID == "" {
		errs = append(errs, "node_id must not be empty")
	}
	if cfg.Agent.MaxGoroutines < 1 || cfg.Agent.MaxGoroutines > 64 {
		errs = append(errs, fmt.Sprintf("agent.max_goroutines must be in [1, 64], got %d", cfg.Agent.MaxGoroutines))
	}
	if cfg.Agent.EventQueueSize < 100 {
		errs = append(errs, fmt.Sprintf("agent.event_queue_size must be >= 100, got %d", cfg.Agent.EventQueueSize))
	}
	if cfg.Agent.MaxTrackedPIDs < 1 || cfg.Agent.MaxTrackedPIDs > 65536 {
		errs = append(errs, fmt.Sprintf("agent.max_tracked_pids must be in [1, 65536], got %d", cfg.Agent.MaxTrackedPIDs))
	}
	if cfg.Anomaly.EntropyWeight < 0.0 || cfg.Anomaly.EntropyWeight > 1.0 {
		errs = append(errs, fmt.Sprintf("anomaly.entropy_weight must be in [0.0, 1.0], got %f", cfg.Anomaly.EntropyWeight))
	}
	if cfg.Escalation.PressureAlpha < 0.0 || cfg.Escalation.PressureAlpha > 1.0 {
		errs = append(errs, fmt.Sprintf("escalation.pressure_alpha must be in [0.0, 1.0], got %f", cfg.Escalation.PressureAlpha))
	}
	if cfg.Escalation.WeightAnomaly < 0 || cfg.Escalation.WeightQuorum < 0 ||
		cfg.Escalation.WeightIntegrity < 0 || cfg.Escalation.WeightPressure < 0 {
		errs = append(errs, "all escalation weights must be >= 0")
	}
	if cfg.Budget.Capacity < 1 {
		errs = append(errs, fmt.Sprintf("budget.capacity must be >= 1, got %d", cfg.Budget.Capacity))
	}
	if cfg.Budget.RefillPeriod < time.Second {
		errs = append(errs, fmt.Sprintf("budget.refill_period must be >= 1s, got %s", cfg.Budget.RefillPeriod))
	}
	if cfg.Storage.DBPath == "" {
		errs = append(errs, "storage.db_path must not be empty")
	}
	if cfg.Storage.RetentionDays < 1 {
		errs = append(errs, fmt.Sprintf("storage.retention_days must be >= 1, got %d", cfg.Storage.RetentionDays))
	}
	if cfg.Gossip.Enabled {
		if cfg.Gossip.TLSCertFile == "" || cfg.Gossip.TLSKeyFile == "" || cfg.Gossip.TLSCAFile == "" {
			errs = append(errs, "gossip.tls_cert_file, tls_key_file, and tls_ca_file are required when gossip is enabled")
		}
		if cfg.Gossip.QuorumMin < 1 {
			errs = append(errs, fmt.Sprintf("gossip.quorum_min must be >= 1, got %d", cfg.Gossip.QuorumMin))
		}
		if cfg.Gossip.FederatedBaseline.Enabled {
			if cfg.Gossip.FederatedBaseline.TrustWeight < 0.0 || cfg.Gossip.FederatedBaseline.TrustWeight > 1.0 {
				errs = append(errs, fmt.Sprintf(
					"gossip.federated_baseline.trust_weight must be in [0.0, 1.0], got %f",
					cfg.Gossip.FederatedBaseline.TrustWeight))
			}
			if cfg.Gossip.FederatedBaseline.MinSamples < 1 {
				errs = append(errs, fmt.Sprintf(
					"gossip.federated_baseline.min_samples must be >= 1, got %d",
					cfg.Gossip.FederatedBaseline.MinSamples))
			}
		}
	}
	if cfg.Agent.LightweightMode && cfg.Gossip.Enabled {
		errs = append(errs, "agent.lightweight_mode=true is incompatible with gossip.enabled=true")
	}

	if len(errs) > 0 {
		return fmt.Errorf("config validation errors:\n  - %s",
			joinStrings(errs, "\n  - "))
	}
	return nil
}

// joinStrings joins a slice of strings with a separator.
func joinStrings(ss []string, sep string) string {
	if len(ss) == 0 {
		return ""
	}
	result := ss[0]
	for _, s := range ss[1:] {
		result += sep + s
	}
	return result
}
