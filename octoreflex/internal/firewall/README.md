# Firewall Integration for OCTOREFLEX

## Overview

The firewall module provides network-level enforcement for OCTOREFLEX process isolation. It bridges the userspace escalation engine with kernel-level packet filtering using nftables, cgroups v2, and DNS filtering.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Escalation Engine                         │
│              (Process State Machine)                        │
└────────────────────┬────────────────────────────────────────┘
                     │ State Change Event
                     ↓
┌─────────────────────────────────────────────────────────────┐
│               Firewall Controller                           │
│  • State mapping (NORMAL → ISOLATED)                        │
│  • Rule coordination                                        │
│  • Metrics tracking                                         │
└─┬─────────┬──────────┬──────────┬─────────────────────────┘
  │         │          │          │
  ↓         ↓          ↓          ↓
┌────┐  ┌─────┐  ┌──────┐  ┌──────────┐
│NFT │  │ DNS │  │ Rate │  │ Cgroup   │
│    │  │Filter│  │Limit │  │Isolator  │
└────┘  └─────┘  └──────┘  └──────────┘
  │         │          │          │
  ↓         ↓          ↓          ↓
┌─────────────────────────────────────┐
│         Linux Kernel                │
│  • nftables (packet filter)         │
│  • cgroups v2 (resource isolation)  │
│  • netlink (rule management)        │
└─────────────────────────────────────┘
```

## Components

### 1. Firewall Controller (`controller.go`)

Main coordinator that:
- Receives state change events from escalation engine
- Translates states to firewall rules
- Coordinates nftables, DNS filter, rate limiter, and cgroup isolator
- Tracks rule lifecycle
- Enforces <50μs rule update latency target

### 2. nftables Manager (`nftables.go`)

Manages nftables rules for packet filtering:
- Dynamic rule generation
- PID-based network blocking
- Set-based matching (O(log n) kernel lookup)
- Rule generator for common patterns

**Table Structure:**
```nft
table inet octoreflex {
    set blocked_pids {
        type pid
    }
    
    chain filter_output {
        type filter hook output priority 0
        policy accept
        meta skpid @blocked_pids drop
    }
}
```

### 3. DNS Filter (`dns.go`)

Kernel-level DNS filtering:
- Blocklist loading from file
- nftables DNS expression matching (kernel 5.18+)
- Per-PID DNS filtering
- Runtime domain add/remove
- Subdomain blocking (e.g., blocking `evil.com` blocks `sub.evil.com`)

**Blocklist Format:**
```
# DNS blocklist for OCTOREFLEX
# One domain per line, # for comments

malware.com
phishing.net
crypto-miner.io
```

### 4. Rate Limiter (`ratelimit.go`)

Automatic rate limiting for suspicious processes:
- Per-PID packet rate limits
- Configurable rate (pps) and burst
- nftables limit statement integration
- Applied in PRESSURE state

### 5. Cgroup Isolator (`cgroup.go`)

Per-process resource isolation using cgroups v2:
- Creates isolated cgroups: `/sys/fs/cgroup/octoreflex/isolated/pid-{pid}`
- Resource limits (CPU, memory, PIDs)
- nftables cgroup matching integration
- Automatic cleanup on process exit

## State Enforcement

| State | Network | DNS | Rate Limit | Cgroup | Description |
|-------|---------|-----|------------|--------|-------------|
| **NORMAL** (0) | ✓ | ✗ | ✗ | ✗ | No restrictions |
| **PRESSURE** (1) | ✓ | ✗ | ✓ | ✗ | Rate limiting enabled |
| **ISOLATED** (2) | ✗ | ✓ | ✓ | ✗ | Network + DNS blocked |
| **FROZEN** (3) | ✗ | ✓ | ✓ | ✓ | Cgroup freeze (escalation engine) |
| **QUARANTINED** (4) | ✗ | ✓ | ✓ | ✓ | Full isolation |
| **TERMINATED** (5) | — | — | — | — | Rules removed (process killed) |

## Configuration

### Example `/etc/octoreflex/config.yaml`

```yaml
schema_version: "1"
node_id: "node-01"

# Firewall integration (NEW)
firewall:
  enabled: true
  
  # nftables configuration
  nftables_table: "octoreflex"
  nftables_family: "inet"  # inet, ip, or ip6
  
  # DNS filtering
  dns_blocklist: "/etc/octoreflex/dns-blocklist.txt"
  
  # Rate limiting
  rate_limit_burst: 100    # packets
  rate_limit_rate: 1000    # pps
  
  # Cgroup isolation
  cgroup_root: "/sys/fs/cgroup"
  isolation_cgroup_path: "/sys/fs/cgroup/octoreflex/isolated"

# Existing configuration...
agent:
  max_goroutines: 4
  event_queue_size: 10000
```

## Integration with State Machine

The firewall controller hooks into the escalation engine via callbacks:

```go
// In main.go or escalation engine initialization:

import "github.com/octoreflex/octoreflex/internal/firewall"

// Create firewall integration
fwIntegration, err := firewall.NewIntegration(firewall.IntegrationConfig{
    Enabled: true,
    FirewallConfig: firewall.Defaults(),
}, logger)
if err != nil {
    log.Fatal(err)
}

// Start firewall
if err := fwIntegration.Start(ctx); err != nil {
    log.Fatal(err)
}
defer fwIntegration.Stop(ctx)

// Register state change hook
escalationEngine.OnStateChange(func(pid uint32, oldState, newState uint8) {
    if err := fwIntegration.OnStateChange(ctx, pid, oldState, newState); err != nil {
        logger.Error("firewall state change failed", zap.Error(err))
    }
})

// Register process exit hook
processMonitor.OnExit(func(pid uint32) {
    if err := fwIntegration.OnProcessExit(ctx, pid); err != nil {
        logger.Error("firewall cleanup failed", zap.Error(err))
    }
})
```

## Performance

### Targets

- **Rule update latency**: <50μs (p99)
- **DNS lookup overhead**: <10μs
- **Memory overhead**: <1KB per tracked PID
- **CPU overhead**: <0.1% (idle), <1% (1000 state changes/s)

### Benchmarks

Run benchmarks:
```bash
cd internal/firewall
go test -bench=. -benchmem
```

Expected results (placeholder implementation):
```
BenchmarkStateChange-4              500000    2.5 μs/op    0 B/op    0 allocs/op
BenchmarkStateChangeParallel-4     1000000    1.2 μs/op    0 B/op    0 allocs/op
BenchmarkDNSFilterIsBlocked-4      5000000    0.3 μs/op    0 B/op    0 allocs/op
```

## Requirements

### Kernel

- **Linux 5.15+** (recommended)
- **Linux 5.18+** for DNS expression support in nftables
- cgroup v2 enabled (`CONFIG_CGROUPS=y`)
- nftables support (`CONFIG_NF_TABLES=y`)
- BPF support (already required by OCTOREFLEX)

### Userspace

- `nft` command-line tool (for manual rule inspection)
- cgroup v2 mounted at `/sys/fs/cgroup`
- Root privileges (required for nftables and cgroup manipulation)

### Go Dependencies

Add to `go.mod`:
```go
require (
    github.com/google/nftables v0.1.0
    github.com/vishvananda/netlink v1.1.0
)
```

## Testing

### Unit Tests

```bash
cd internal/firewall
go test -v
```

### Integration Tests

```bash
# Requires root and nftables installed
sudo go test -v -tags=integration
```

### Manual Testing

```bash
# Start OCTOREFLEX with firewall enabled
sudo ./octoreflex --config=/etc/octoreflex/config.yaml

# In another terminal, trigger anomaly
./trigger-anomaly --pid=1234

# Verify nftables rules
sudo nft list table inet octoreflex

# Verify cgroups
cat /sys/fs/cgroup/octoreflex/isolated/pid-1234/cgroup.procs

# Check firewall stats
curl http://localhost:9091/metrics | grep octoreflex_firewall
```

## Metrics

Prometheus metrics exported:

```
# Rule updates
octoreflex_firewall_rule_updates_total{state="isolated"}

# Rule update errors
octoreflex_firewall_rule_update_errors_total

# Network isolations
octoreflex_firewall_isolations_total

# DNS blocks
octoreflex_firewall_dns_blocks_total

# Active rules
octoreflex_firewall_active_rules
```

## Troubleshooting

### Firewall not working

1. **Check nftables**:
   ```bash
   sudo nft list tables
   # Should show "table inet octoreflex"
   ```

2. **Check cgroup v2**:
   ```bash
   ls /sys/fs/cgroup/cgroup.controllers
   # Should show: cpu memory io pids
   ```

3. **Check logs**:
   ```bash
   journalctl -u octoreflex -f | grep firewall
   ```

### Permission errors

OCTOREFLEX must run as root for firewall integration:
```bash
sudo systemctl start octoreflex
```

### DNS filtering not working

Requires kernel 5.18+ for DNS expression support. On older kernels, DNS filtering is disabled automatically.

Check kernel version:
```bash
uname -r
# Should be >= 5.18
```

## Security Considerations

1. **Privilege Separation**: Firewall operations require `CAP_NET_ADMIN` and `CAP_SYS_ADMIN`. OCTOREFLEX drops privileges after initialization where possible.

2. **Race Conditions**: State machine updates and firewall rule updates are coordinated but not atomic. A malicious process might send packets in the window between state transition and rule application (~50μs).

3. **Bypass via Raw Sockets**: Processes with `CAP_NET_RAW` can bypass nftables filtering. OCTOREFLEX BPF hooks catch raw socket creation.

4. **Resource Exhaustion**: Each tracked PID consumes ~1KB memory. With 16K tracked PIDs (default limit), total overhead is ~16MB.

## Future Enhancements

1. **IPv6 Support**: Full IPv6 filtering (currently inet handles both)
2. **Port-based Isolation**: Allow only specific ports (e.g., HTTPS only)
3. **Traffic Shaping**: QoS for rate-limited processes
4. **Connection Tracking**: Track established connections across state changes
5. **Hardware Offload**: XDP integration for line-rate filtering

## References

- [nftables Wiki](https://wiki.nftables.org/)
- [cgroup v2 Documentation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)
- [OCTOREFLEX Architecture](../docs/ARCHITECTURE.md)
