// Package firewall provides network-level enforcement for OCTOREFLEX process isolation.
//
// Architecture:
//   - nftables integration for kernel-level packet filtering
//   - Per-process network isolation using cgroups v2 + nftables sets
//   - DNS filtering at kernel level via nftables DNS maps
//   - Automatic rate limiting for suspicious processes
//   - State machine integration (rules updated on state changes)
//
// Performance target: <50μs rule update latency
//
// Thread safety: All public methods are goroutine-safe.

package firewall

import (
	"context"
	"fmt"
	"sync"
	"time"

	"go.uber.org/zap"
)

// Controller manages firewall rules for process isolation.
type Controller struct {
	mu       sync.RWMutex
	logger   *zap.Logger
	nft      *NftablesManager
	dns      *DNSFilter
	ratelim  *RateLimiter
	cgroup   *CgroupIsolator
	
	// State tracking
	rules    map[uint32]*ProcessRules // pid -> rules
	enabled  bool
	
	// Metrics
	ruleUpdates      uint64
	ruleUpdateErrors uint64
	isolations       uint64
	dnsBlocks        uint64
}

// ProcessRules holds the firewall configuration for a single process.
type ProcessRules struct {
	PID            uint32
	State          uint8 // Matches escalation.State
	NetworkBlocked bool
	DNSFiltered    bool
	RateLimited    bool
	CgroupPath     string
	CreatedAt      time.Time
	UpdatedAt      time.Time
}

// Config holds firewall controller configuration.
type Config struct {
	// Enabled controls whether firewall integration is active.
	Enabled bool

	// NftablesTable is the nftables table name for OCTOREFLEX rules.
	// Default: "octoreflex"
	NftablesTable string

	// NftablesFamily is the nftables family (inet, ip, ip6).
	// Default: "inet" (handles both IPv4 and IPv6)
	NftablesFamily string

	// DNSBlocklist is the path to a file containing blocked domains.
	// Format: one domain per line, # for comments.
	DNSBlocklist string

	// RateLimitBurst is the maximum burst size for rate limiting.
	// Default: 100 packets
	RateLimitBurst uint32

	// RateLimitRate is the sustained rate limit in packets/second.
	// Default: 1000 pps
	RateLimitRate uint32

	// CgroupRoot is the cgroup v2 mount point.
	// Default: /sys/fs/cgroup
	CgroupRoot string

	// IsolationCgroupPath is the cgroup path for isolated processes.
	// Default: /sys/fs/cgroup/octoreflex/isolated
	IsolationCgroupPath string
}

// Defaults returns a Config with default values.
func Defaults() Config {
	return Config{
		Enabled:             false, // Must be explicitly enabled
		NftablesTable:       "octoreflex",
		NftablesFamily:      "inet",
		DNSBlocklist:        "/etc/octoreflex/dns-blocklist.txt",
		RateLimitBurst:      100,
		RateLimitRate:       1000,
		CgroupRoot:          "/sys/fs/cgroup",
		IsolationCgroupPath: "/sys/fs/cgroup/octoreflex/isolated",
	}
}

// New creates a new firewall controller.
// Returns error if nftables or cgroup initialization fails.
func New(cfg Config, logger *zap.Logger) (*Controller, error) {
	if logger == nil {
		return nil, fmt.Errorf("firewall.New: logger is nil")
	}

	if !cfg.Enabled {
		logger.Info("firewall: disabled (cfg.Enabled=false)")
		return &Controller{
			logger:  logger,
			enabled: false,
			rules:   make(map[uint32]*ProcessRules),
		}, nil
	}

	// Initialize nftables manager
	nft, err := NewNftablesManager(NftablesConfig{
		Table:  cfg.NftablesTable,
		Family: cfg.NftablesFamily,
	}, logger)
	if err != nil {
		return nil, fmt.Errorf("firewall.New: nftables init: %w", err)
	}

	// Initialize DNS filter
	dns, err := NewDNSFilter(DNSConfig{
		BlocklistPath: cfg.DNSBlocklist,
		NftablesTable: cfg.NftablesTable,
	}, logger)
	if err != nil {
		logger.Warn("firewall: DNS filter init failed, continuing without DNS filtering",
			zap.Error(err))
		dns = nil // Non-fatal, DNS filtering is optional
	}

	// Initialize rate limiter
	ratelim := NewRateLimiter(RateLimitConfig{
		Burst: cfg.RateLimitBurst,
		Rate:  cfg.RateLimitRate,
	}, logger)

	// Initialize cgroup isolator
	cgroup, err := NewCgroupIsolator(CgroupConfig{
		Root:         cfg.CgroupRoot,
		IsolatedPath: cfg.IsolationCgroupPath,
	}, logger)
	if err != nil {
		return nil, fmt.Errorf("firewall.New: cgroup init: %w", err)
	}

	c := &Controller{
		logger:  logger,
		nft:     nft,
		dns:     dns,
		ratelim: ratelim,
		cgroup:  cgroup,
		enabled: true,
		rules:   make(map[uint32]*ProcessRules),
	}

	logger.Info("firewall: initialized",
		zap.String("table", cfg.NftablesTable),
		zap.String("family", cfg.NftablesFamily),
		zap.String("cgroup_root", cfg.CgroupRoot))

	return c, nil
}

// Start initializes firewall infrastructure (tables, chains, sets).
// Must be called once before any rule updates.
func (c *Controller) Start(ctx context.Context) error {
	if !c.enabled {
		return nil
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	c.logger.Info("firewall: starting infrastructure setup")

	// Create nftables table and base chains
	if err := c.nft.Initialize(ctx); err != nil {
		return fmt.Errorf("firewall.Start: nftables init: %w", err)
	}

	// Initialize DNS filter tables
	if c.dns != nil {
		if err := c.dns.Initialize(ctx); err != nil {
			c.logger.Warn("firewall: DNS filter initialization failed",
				zap.Error(err))
			// Non-fatal, continue without DNS filtering
			c.dns = nil
		}
	}

	// Create cgroup hierarchy
	if err := c.cgroup.Initialize(ctx); err != nil {
		return fmt.Errorf("firewall.Start: cgroup init: %w", err)
	}

	c.logger.Info("firewall: started successfully")
	return nil
}

// Stop tears down firewall infrastructure and removes all rules.
func (c *Controller) Stop(ctx context.Context) error {
	if !c.enabled {
		return nil
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	c.logger.Info("firewall: stopping")

	// Remove all process rules
	for pid := range c.rules {
		if err := c.removeRulesLocked(ctx, pid); err != nil {
			c.logger.Error("firewall: failed to remove rules during shutdown",
				zap.Uint32("pid", pid),
				zap.Error(err))
		}
	}

	// Teardown nftables
	if err := c.nft.Teardown(ctx); err != nil {
		c.logger.Error("firewall: nftables teardown failed", zap.Error(err))
	}

	// Teardown DNS filter
	if c.dns != nil {
		if err := c.dns.Teardown(ctx); err != nil {
			c.logger.Error("firewall: DNS filter teardown failed", zap.Error(err))
		}
	}

	// Teardown cgroup hierarchy
	if err := c.cgroup.Teardown(ctx); err != nil {
		c.logger.Error("firewall: cgroup teardown failed", zap.Error(err))
	}

	c.logger.Info("firewall: stopped")
	return nil
}

// OnStateChange is called by the escalation engine when a process state changes.
// It updates firewall rules to match the new isolation level.
//
// Performance target: <50μs
func (c *Controller) OnStateChange(ctx context.Context, pid uint32, newState uint8) error {
	if !c.enabled {
		return nil
	}

	start := time.Now()
	defer func() {
		latency := time.Since(start)
		if latency > 50*time.Microsecond {
			c.logger.Warn("firewall: rule update latency exceeded target",
				zap.Uint32("pid", pid),
				zap.Uint8("state", newState),
				zap.Duration("latency", latency))
		}
	}()

	c.mu.Lock()
	defer c.mu.Unlock()

	// Get or create rule set
	rules, exists := c.rules[pid]
	if !exists {
		rules = &ProcessRules{
			PID:       pid,
			CreatedAt: time.Now(),
		}
		c.rules[pid] = rules
	}

	oldState := rules.State
	rules.State = newState
	rules.UpdatedAt = time.Now()

	c.logger.Debug("firewall: state change",
		zap.Uint32("pid", pid),
		zap.Uint8("old_state", oldState),
		zap.Uint8("new_state", newState))

	// Apply rules based on new state
	if err := c.applyStateLocked(ctx, pid, newState); err != nil {
		c.ruleUpdateErrors++
		return fmt.Errorf("firewall.OnStateChange: pid=%d state=%d: %w", pid, newState, err)
	}

	c.ruleUpdates++
	return nil
}

// applyStateLocked applies firewall rules for a specific state.
// Caller must hold c.mu.
//
// State enforcement:
//   NORMAL (0)      - No restrictions
//   PRESSURE (1)    - Rate limiting enabled
//   ISOLATED (2)    - Network blocked, DNS filtered
//   FROZEN (3)      - cgroup freeze (no additional firewall rules)
//   QUARANTINED (4) - Full isolation (network, DNS, cgroup)
//   TERMINATED (5)  - Rules removed (process will be killed)
func (c *Controller) applyStateLocked(ctx context.Context, pid uint32, state uint8) error {
	rules := c.rules[pid]

	switch state {
	case 0: // NORMAL
		// Remove all restrictions
		return c.removeAllRestrictionsLocked(ctx, pid)

	case 1: // PRESSURE
		// Enable rate limiting
		if !rules.RateLimited {
			if err := c.ratelim.Apply(ctx, pid); err != nil {
				return fmt.Errorf("rate limit apply: %w", err)
			}
			rules.RateLimited = true
		}
		return nil

	case 2: // ISOLATED
		// Block network, enable DNS filtering
		if !rules.NetworkBlocked {
			if err := c.nft.BlockNetwork(ctx, pid); err != nil {
				return fmt.Errorf("block network: %w", err)
			}
			rules.NetworkBlocked = true
			c.isolations++
		}
		if c.dns != nil && !rules.DNSFiltered {
			if err := c.dns.EnableForPID(ctx, pid); err != nil {
				c.logger.Warn("firewall: DNS filter enable failed",
					zap.Uint32("pid", pid),
					zap.Error(err))
				// Non-fatal
			} else {
				rules.DNSFiltered = true
			}
		}
		return nil

	case 3: // FROZEN
		// Cgroup freeze is handled by escalation engine
		// No additional firewall rules needed
		return nil

	case 4: // QUARANTINED
		// Full isolation: network + cgroup
		if !rules.NetworkBlocked {
			if err := c.nft.BlockNetwork(ctx, pid); err != nil {
				return fmt.Errorf("block network: %w", err)
			}
			rules.NetworkBlocked = true
			c.isolations++
		}
		// Move to isolated cgroup
		cgroupPath, err := c.cgroup.Isolate(ctx, pid)
		if err != nil {
			return fmt.Errorf("cgroup isolate: %w", err)
		}
		rules.CgroupPath = cgroupPath
		return nil

	case 5: // TERMINATED
		// Remove all rules (process will be killed)
		return c.removeRulesLocked(ctx, pid)

	default:
		return fmt.Errorf("unknown state: %d", state)
	}
}

// removeAllRestrictionsLocked removes all firewall restrictions for a PID.
// Caller must hold c.mu.
func (c *Controller) removeAllRestrictionsLocked(ctx context.Context, pid uint32) error {
	rules, exists := c.rules[pid]
	if !exists {
		return nil
	}

	if rules.RateLimited {
		if err := c.ratelim.Remove(ctx, pid); err != nil {
			c.logger.Error("firewall: rate limit remove failed",
				zap.Uint32("pid", pid),
				zap.Error(err))
		}
		rules.RateLimited = false
	}

	if rules.NetworkBlocked {
		if err := c.nft.UnblockNetwork(ctx, pid); err != nil {
			c.logger.Error("firewall: network unblock failed",
				zap.Uint32("pid", pid),
				zap.Error(err))
		}
		rules.NetworkBlocked = false
	}

	if rules.DNSFiltered && c.dns != nil {
		if err := c.dns.DisableForPID(ctx, pid); err != nil {
			c.logger.Error("firewall: DNS filter disable failed",
				zap.Uint32("pid", pid),
				zap.Error(err))
		}
		rules.DNSFiltered = false
	}

	if rules.CgroupPath != "" {
		if err := c.cgroup.Release(ctx, pid); err != nil {
			c.logger.Error("firewall: cgroup release failed",
				zap.Uint32("pid", pid),
				zap.Error(err))
		}
		rules.CgroupPath = ""
	}

	return nil
}

// removeRulesLocked removes all firewall rules for a PID and deletes the rule set.
// Caller must hold c.mu.
func (c *Controller) removeRulesLocked(ctx context.Context, pid uint32) error {
	if err := c.removeAllRestrictionsLocked(ctx, pid); err != nil {
		return err
	}
	delete(c.rules, pid)
	return nil
}

// OnProcessExit is called when a process terminates.
// Removes all firewall rules for the PID.
func (c *Controller) OnProcessExit(ctx context.Context, pid uint32) error {
	if !c.enabled {
		return nil
	}

	c.mu.Lock()
	defer c.mu.Unlock()

	if _, exists := c.rules[pid]; !exists {
		return nil // No rules to remove
	}

	c.logger.Debug("firewall: process exit, removing rules",
		zap.Uint32("pid", pid))

	return c.removeRulesLocked(ctx, pid)
}

// Stats returns firewall statistics.
type Stats struct {
	RuleUpdates      uint64
	RuleUpdateErrors uint64
	Isolations       uint64
	DNSBlocks        uint64
	ActiveRules      int
}

// GetStats returns current firewall statistics.
func (c *Controller) GetStats() Stats {
	c.mu.RLock()
	defer c.mu.RUnlock()

	dnsBlocks := uint64(0)
	if c.dns != nil {
		dnsBlocks = c.dns.GetBlockCount()
	}

	return Stats{
		RuleUpdates:      c.ruleUpdates,
		RuleUpdateErrors: c.ruleUpdateErrors,
		Isolations:       c.isolations,
		DNSBlocks:        dnsBlocks,
		ActiveRules:      len(c.rules),
	}
}

// IsEnabled returns true if firewall integration is enabled.
func (c *Controller) IsEnabled() bool {
	return c.enabled
}
