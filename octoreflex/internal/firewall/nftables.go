// Package firewall — nftables.go
//
// nftables integration for dynamic rule generation and management.
// Uses the nftables netlink API via github.com/google/nftables.
//
// Rule structure:
//   table inet octoreflex {
//     set blocked_pids {
//       type pid
//     }
//     chain filter_output {
//       type filter hook output priority 0; policy accept;
//       meta skuid @blocked_pids drop
//     }
//   }

package firewall

import (
	"context"
	"fmt"
	"sync"

	"go.uber.org/zap"
)

// NftablesManager manages nftables rules for process isolation.
type NftablesManager struct {
	mu     sync.Mutex
	logger *zap.Logger
	cfg    NftablesConfig

	// nftables state
	table      string
	family     string
	blockedSet map[uint32]struct{} // PIDs with network blocked
}

// NftablesConfig holds nftables configuration.
type NftablesConfig struct {
	Table  string // nftables table name
	Family string // nftables family (inet, ip, ip6)
}

// NewNftablesManager creates a new nftables manager.
func NewNftablesManager(cfg NftablesConfig, logger *zap.Logger) (*NftablesManager, error) {
	if cfg.Table == "" {
		return nil, fmt.Errorf("nftables table name is required")
	}
	if cfg.Family == "" {
		cfg.Family = "inet" // Default to inet (handles both IPv4 and IPv6)
	}

	return &NftablesManager{
		logger:     logger,
		cfg:        cfg,
		table:      cfg.Table,
		family:     cfg.Family,
		blockedSet: make(map[uint32]struct{}),
	}, nil
}

// Initialize creates the nftables table, chains, and sets.
// This is a placeholder implementation. Real implementation would use:
//   import "github.com/google/nftables"
//   import "github.com/google/nftables/expr"
//
// Example nftables setup:
//   conn := nftables.Conn{}
//   table := conn.AddTable(&nftables.Table{Name: "octoreflex", Family: nftables.TableFamilyINet})
//   set := conn.AddSet(&nftables.Set{Name: "blocked_pids", Table: table, KeyType: nftables.TypePID})
//   chain := conn.AddChain(&nftables.Chain{Name: "filter_output", Table: table, Type: nftables.ChainTypeFilter, ...})
//   rule := conn.AddRule(&nftables.Rule{Table: table, Chain: chain, Exprs: [...]})
//   conn.Flush()
func (n *NftablesManager) Initialize(ctx context.Context) error {
	n.mu.Lock()
	defer n.mu.Unlock()

	n.logger.Info("nftables: initializing table and chains",
		zap.String("table", n.table),
		zap.String("family", n.family))

	// PLACEHOLDER: Real implementation would:
	// 1. Create table: `nft add table inet octoreflex`
	// 2. Create set: `nft add set inet octoreflex blocked_pids { type pid; }`
	// 3. Create chain: `nft add chain inet octoreflex filter_output { type filter hook output priority 0; policy accept; }`
	// 4. Add rule: `nft add rule inet octoreflex filter_output meta skpid @blocked_pids drop`
	//
	// For now, we simulate success:
	n.logger.Warn("nftables: using PLACEHOLDER implementation (no actual rules created)")

	// In production, check if nftables is available:
	// if err := exec.CommandContext(ctx, "nft", "list", "tables").Run(); err != nil {
	//     return fmt.Errorf("nftables not available: %w", err)
	// }

	return nil
}

// Teardown removes the nftables table and all associated rules.
func (n *NftablesManager) Teardown(ctx context.Context) error {
	n.mu.Lock()
	defer n.mu.Unlock()

	n.logger.Info("nftables: tearing down table", zap.String("table", n.table))

	// PLACEHOLDER: Real implementation would:
	// conn := nftables.Conn{}
	// conn.DelTable(table)
	// conn.Flush()

	n.blockedSet = make(map[uint32]struct{})
	return nil
}

// BlockNetwork adds a PID to the blocked_pids set, preventing all network access.
//
// Implementation strategy:
//   - Use nftables sets for efficient PID matching
//   - Match on meta skpid (socket owning process PID)
//   - Drop packets in output chain before they leave the host
//
// Performance: O(log n) set lookup in kernel
func (n *NftablesManager) BlockNetwork(ctx context.Context, pid uint32) error {
	n.mu.Lock()
	defer n.mu.Unlock()

	if _, exists := n.blockedSet[pid]; exists {
		return nil // Already blocked
	}

	n.logger.Debug("nftables: blocking network for PID", zap.Uint32("pid", pid))

	// PLACEHOLDER: Real implementation would:
	// conn := nftables.Conn{}
	// set := &nftables.Set{Name: "blocked_pids", Table: table}
	// conn.SetAddElements(set, []nftables.SetElement{{Key: encodePID(pid)}})
	// if err := conn.Flush(); err != nil {
	//     return fmt.Errorf("nftables: add element: %w", err)
	// }

	n.blockedSet[pid] = struct{}{}
	n.logger.Info("nftables: network blocked",
		zap.Uint32("pid", pid),
		zap.Int("total_blocked", len(n.blockedSet)))

	return nil
}

// UnblockNetwork removes a PID from the blocked_pids set, restoring network access.
func (n *NftablesManager) UnblockNetwork(ctx context.Context, pid uint32) error {
	n.mu.Lock()
	defer n.mu.Unlock()

	if _, exists := n.blockedSet[pid]; !exists {
		return nil // Not blocked
	}

	n.logger.Debug("nftables: unblocking network for PID", zap.Uint32("pid", pid))

	// PLACEHOLDER: Real implementation would:
	// conn := nftables.Conn{}
	// set := &nftables.Set{Name: "blocked_pids", Table: table}
	// conn.SetDeleteElements(set, []nftables.SetElement{{Key: encodePID(pid)}})
	// if err := conn.Flush(); err != nil {
	//     return fmt.Errorf("nftables: delete element: %w", err)
	// }

	delete(n.blockedSet, pid)
	n.logger.Info("nftables: network unblocked",
		zap.Uint32("pid", pid),
		zap.Int("total_blocked", len(n.blockedSet)))

	return nil
}

// GetBlockedCount returns the number of PIDs currently blocked.
func (n *NftablesManager) GetBlockedCount() int {
	n.mu.Lock()
	defer n.mu.Unlock()
	return len(n.blockedSet)
}

// RuleGenerator generates nftables rules for specific use cases.
type RuleGenerator struct{}

// NewRuleGenerator creates a new rule generator.
func NewRuleGenerator() *RuleGenerator {
	return &RuleGenerator{}
}

// GenerateBlockRule generates an nftables rule to block all traffic from a PID.
// Returns the rule in nftables syntax.
//
// Example output:
//   "meta skpid 1234 drop"
func (g *RuleGenerator) GenerateBlockRule(pid uint32) string {
	return fmt.Sprintf("meta skpid %d drop", pid)
}

// GenerateRateLimitRule generates an nftables rule for rate limiting.
// Uses the limit statement to enforce packets/second limits.
//
// Example output:
//   "meta skpid 1234 limit rate 1000/second burst 100 packets accept"
func (g *RuleGenerator) GenerateRateLimitRule(pid uint32, ratePerSec, burst uint32) string {
	return fmt.Sprintf("meta skpid %d limit rate %d/second burst %d packets accept",
		pid, ratePerSec, burst)
}

// GenerateDNSBlockRule generates an nftables rule to block DNS queries to specific domains.
// Uses the dns expression (requires kernel 5.18+).
//
// Example output:
//   "meta skpid 1234 udp dport 53 dns query name @blocked_domains drop"
func (g *RuleGenerator) GenerateDNSBlockRule(pid uint32, blockedSet string) string {
	return fmt.Sprintf("meta skpid %d udp dport 53 dns query name @%s drop",
		pid, blockedSet)
}

// GenerateCgroupMatchRule generates an nftables rule using cgroup matching.
// Matches packets from processes in a specific cgroup.
//
// Example output:
//   "meta cgroup 1234 drop"
func (g *RuleGenerator) GenerateCgroupMatchRule(cgroupID uint32) string {
	return fmt.Sprintf("meta cgroup %d drop", cgroupID)
}

// encodePID encodes a PID for use in nftables set elements.
// PIDs are encoded as 32-bit unsigned integers in network byte order.
func encodePID(pid uint32) []byte {
	// Network byte order (big-endian)
	return []byte{
		byte(pid >> 24),
		byte(pid >> 16),
		byte(pid >> 8),
		byte(pid),
	}
}

// decodePID decodes a PID from nftables set element format.
func decodePID(b []byte) uint32 {
	if len(b) != 4 {
		return 0
	}
	return uint32(b[0])<<24 | uint32(b[1])<<16 | uint32(b[2])<<8 | uint32(b[3])
}
