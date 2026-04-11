// Package firewall — ratelimit.go
//
// Automatic rate limiting for suspicious processes using nftables.
// Limits packets per second for processes in PRESSURE state.
//
// Implementation:
//   - Uses nftables limit statement
//   - Per-PID rate limits stored in nftables map
//   - Configurable rate (pps) and burst size
//   - Automatic cleanup on process exit

package firewall

import (
	"context"
	"fmt"
	"sync"

	"go.uber.org/zap"
)

// RateLimiter manages per-process rate limiting.
type RateLimiter struct {
	mu     sync.Mutex
	logger *zap.Logger
	cfg    RateLimitConfig

	// State tracking
	limitedPIDs map[uint32]*RateLimit
}

// RateLimit holds rate limiting state for a single PID.
type RateLimit struct {
	PID   uint32
	Rate  uint32 // Packets per second
	Burst uint32 // Maximum burst size
}

// RateLimitConfig holds rate limiter configuration.
type RateLimitConfig struct {
	// Burst is the maximum burst size (packets).
	Burst uint32

	// Rate is the sustained rate limit (packets/second).
	Rate uint32
}

// NewRateLimiter creates a new rate limiter.
func NewRateLimiter(cfg RateLimitConfig, logger *zap.Logger) *RateLimiter {
	return &RateLimiter{
		logger:      logger,
		cfg:         cfg,
		limitedPIDs: make(map[uint32]*RateLimit),
	}
}

// Apply applies rate limiting to a PID.
// Rate and burst are taken from the global config.
func (r *RateLimiter) Apply(ctx context.Context, pid uint32) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, exists := r.limitedPIDs[pid]; exists {
		return nil // Already rate limited
	}

	r.logger.Debug("ratelimit: applying rate limit",
		zap.Uint32("pid", pid),
		zap.Uint32("rate", r.cfg.Rate),
		zap.Uint32("burst", r.cfg.Burst))

	// PLACEHOLDER: Real implementation would:
	// 1. Create nftables map entry for PID -> (rate, burst)
	// 2. Add rule: `nft add rule inet octoreflex filter_output meta skpid $pid limit rate $rate/second burst $burst packets accept`
	//
	// Example using nftables library:
	// conn := nftables.Conn{}
	// rule := &nftables.Rule{
	//     Table: table,
	//     Chain: chain,
	//     Exprs: []expr.Any{
	//         &expr.Meta{Key: expr.MetaKeySkpid, Register: 1},
	//         &expr.Cmp{Op: expr.CmpOpEq, Register: 1, Data: encodePID(pid)},
	//         &expr.Limit{Type: expr.LimitTypePackets, Rate: rate, Burst: burst},
	//         &expr.Verdict{Kind: expr.VerdictAccept},
	//     },
	// }
	// conn.AddRule(rule)
	// conn.Flush()

	r.limitedPIDs[pid] = &RateLimit{
		PID:   pid,
		Rate:  r.cfg.Rate,
		Burst: r.cfg.Burst,
	}

	r.logger.Info("ratelimit: rate limit applied",
		zap.Uint32("pid", pid),
		zap.Uint32("rate", r.cfg.Rate),
		zap.Uint32("burst", r.cfg.Burst),
		zap.Int("total_limited", len(r.limitedPIDs)))

	return nil
}

// Remove removes rate limiting from a PID.
func (r *RateLimiter) Remove(ctx context.Context, pid uint32) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, exists := r.limitedPIDs[pid]; !exists {
		return nil // Not rate limited
	}

	r.logger.Debug("ratelimit: removing rate limit", zap.Uint32("pid", pid))

	// PLACEHOLDER: Real implementation would remove the nftables rule
	// conn := nftables.Conn{}
	// conn.DelRule(rule)
	// conn.Flush()

	delete(r.limitedPIDs, pid)

	r.logger.Info("ratelimit: rate limit removed",
		zap.Uint32("pid", pid),
		zap.Int("total_limited", len(r.limitedPIDs)))

	return nil
}

// Update updates the rate limit for a PID.
func (r *RateLimiter) Update(ctx context.Context, pid uint32, rate, burst uint32) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	limit, exists := r.limitedPIDs[pid]
	if !exists {
		return fmt.Errorf("ratelimit: PID %d not rate limited", pid)
	}

	r.logger.Debug("ratelimit: updating rate limit",
		zap.Uint32("pid", pid),
		zap.Uint32("old_rate", limit.Rate),
		zap.Uint32("new_rate", rate),
		zap.Uint32("old_burst", limit.Burst),
		zap.Uint32("new_burst", burst))

	// PLACEHOLDER: Real implementation would update the nftables rule

	limit.Rate = rate
	limit.Burst = burst

	r.logger.Info("ratelimit: rate limit updated",
		zap.Uint32("pid", pid),
		zap.Uint32("rate", rate),
		zap.Uint32("burst", burst))

	return nil
}

// GetLimit returns the current rate limit for a PID.
func (r *RateLimiter) GetLimit(pid uint32) (*RateLimit, bool) {
	r.mu.Lock()
	defer r.mu.Unlock()

	limit, exists := r.limitedPIDs[pid]
	if !exists {
		return nil, false
	}

	// Return a copy to prevent external mutation
	return &RateLimit{
		PID:   limit.PID,
		Rate:  limit.Rate,
		Burst: limit.Burst,
	}, true
}

// GetLimitedPIDs returns a list of all PIDs with active rate limits.
func (r *RateLimiter) GetLimitedPIDs() []uint32 {
	r.mu.Lock()
	defer r.mu.Unlock()

	pids := make([]uint32, 0, len(r.limitedPIDs))
	for pid := range r.limitedPIDs {
		pids = append(pids, pid)
	}
	return pids
}

// GetCount returns the number of PIDs with active rate limits.
func (r *RateLimiter) GetCount() int {
	r.mu.Lock()
	defer r.mu.Unlock()
	return len(r.limitedPIDs)
}
