# OctoReflex Deception Framework

## Overview

The OctoReflex Deception Framework is a comprehensive security deception layer designed to amplify attacker costs and gather threat intelligence. It implements multiple deception mechanisms that force attackers to waste CPU, bandwidth, and time resources while providing defenders with valuable intelligence.

## Architecture

### Core Components

1. **Honeypots** (`honeypot/`)
   - SSH honeypot with realistic shell environment
   - HTTP honeypot with fake admin panels and APIs
   - Database honeypots (MySQL, PostgreSQL, MongoDB)
   - All honeypots capture credentials, commands, and attack patterns

2. **Port Rotation** (`port_rotation.go`)
   - Advanced deterministic port rotation using cryptographic PRNG
   - Frequency hopping with configurable sequences
   - Chaos mode for unpredictable rotations
   - Adaptive rotation speed based on threat level

3. **TCP Decoys** (`tcp_decoy.go`)
   - Stateful TCP decoy services
   - Protocol-specific handlers (SSH, MySQL, PostgreSQL, Redis)
   - Bandwidth amplification to waste attacker resources
   - Connection fingerprinting and analysis

4. **Cost Amplification** (`cost_amplifier.go`)
   - Proof-of-work challenges (CPU intensive)
   - Bandwidth amplification (network intensive)
   - Artificial delays (time intensive)
   - Memory pressure operations

5. **Orchestrator** (`orchestrator.go`)
   - Unified coordination of all deception mechanisms
   - Event aggregation and correlation
   - Real-time analytics and metrics
   - Integration with OctoReflex state machine

## Features

### Honeypot Capabilities

**SSH Honeypot:**
- Realistic SSH banner and protocol negotiation
- Password and key-based authentication logging
- Interactive fake shell with common commands
- Credential harvesting for threat intelligence
- Configurable command responses

**HTTP Honeypot:**
- Fake admin panels and login pages
- API endpoints with fake credentials
- Attack pattern detection (SQLi, XSS, LFI, command injection)
- File upload handling with fake virus detection
- Scanner detection (Nikto, SQLMap, etc.)

**Database Honeypots:**
- MySQL, PostgreSQL, MongoDB protocol support
- Realistic handshakes and authentication flows
- Query logging and analysis
- Fake databases and tables advertised
- Authentication always fails after delay

### Port Rotation

**Frequency Hopping:**
```go
cfg := DefaultPortRotationConfig()
cfg.NodeID = "node-1"
cfg.HopSequenceLength = 256
cfg.EnableChaosMode = true

pr, _ := NewPortRotation(cfg, log)
port := pr.GetCurrentPort("my-service")
```

**Adaptive Rotation:**
- Rotation speed increases with threat level
- Deterministic prediction for legitimate clients
- Cryptographic sequence generation (AES-CTR)
- Chaos mode adds unpredictability

### TCP Decoys

**Protocol Handlers:**
- SSH: Complete handshake with fake key exchange
- MySQL: Handshake packet with authentication
- PostgreSQL: Startup message and MD5 auth
- Redis: Command handling with auth errors

**Resource Waste:**
- Configurable bandwidth amplification
- Artificial delays per response
- Connection timeout management
- CPU-intensive operations

### Cost Amplification

**Proof-of-Work:**
```go
ca := NewCostAmplifier(cfg, log)
challenge := ca.GeneratePOWChallenge()
// Attacker must solve: find nonce where hash has N leading zeros
nonce, _ := SolvePOW(challenge)
verified := ca.VerifyPOW(challenge, nonce)
```

**Cost Analysis:**
```go
cost := ca.CalculateCostUSD()
// Returns: CPU cost, bandwidth cost, time cost
// Example: $12.50 total ($2.00 CPU, $0.50 bandwidth, $10.00 time)
```

## Usage

### Basic Setup

```go
import "github.com/octoreflex/internal/deception"

// Create orchestrator
cfg := deception.DefaultOrchestratorConfig()
cfg.Enabled = true
cfg.EnableSSHHoneypot = true
cfg.EnableHTTPHoneypot = true

orchestrator, err := deception.NewOrchestrator(cfg, log)
if err != nil {
    log.Fatal("failed to create orchestrator", zap.Error(err))
}

// Start all deception mechanisms
err = orchestrator.Start()
if err != nil {
    log.Fatal("failed to start deception", zap.Error(err))
}
defer orchestrator.Stop()

// Adjust based on threat level
orchestrator.SetThreatLevel(0.8) // High threat = faster rotation
```

### Port Rotation Integration

```go
// Get current port for a service
port := orchestrator.GetCurrentPort("api-server")

// Generate hint for legitimate clients
hint := orchestrator.portRotation.GenerateHint("api-server")
// Hint includes: current port, epoch, validity window, sequence hash
```

### Cost Amplification

```go
// Generate POW challenge for suspicious connections
challenge := orchestrator.GeneratePOWChallenge()

// Client must solve and return nonce
if !orchestrator.VerifyPOW(challenge, clientNonce) {
    // Reject connection
    return
}
```

### Collecting Statistics

```go
stats := orchestrator.GetStats()

fmt.Printf("Deception Statistics:\n")
fmt.Printf("  Running: %v\n", stats.Running)
fmt.Printf("  Port Rotation Epoch: %d\n", stats.PortRotation.Epoch)
fmt.Printf("  TCP Decoy Connections: %d\n", stats.TCPDecoy.TotalConnections)
fmt.Printf("  Cost Imposed: $%.2f\n", stats.CostBreakdown.TotalCostUSD)
fmt.Printf("  SSH Honeypot Attempts: %d\n", stats.SSHHoneypot.TotalAttempts)
fmt.Printf("  HTTP Honeypot Attempts: %d\n", stats.HTTPHoneypot.TotalAttempts)
```

## Configuration

### Orchestrator Configuration

```go
type OrchestratorConfig struct {
    Enabled            bool
    PortRotation       PortRotationConfig
    TCPDecoy           TCPDecoyConfig
    CostAmplifier      CostAmplifierConfig
    EnableSSHHoneypot  bool
    EnableHTTPHoneypot bool
    SSHHoneypot        honeypot.SSHHoneypotConfig
    HTTPHoneypot       honeypot.HTTPHoneypotConfig
    EnableAnalytics    bool
    AnalyticsWindow    time.Duration
}
```

### Port Rotation Configuration

```go
type PortRotationConfig struct {
    NodeID                string
    PortBase              int           // Default: 32768
    PortRange             int           // Default: 16384
    MinRotationInterval   time.Duration // Default: 5 minutes
    MaxRotationInterval   time.Duration // Default: 1 hour
    HopSequenceLength     int           // Default: 256
    EnableChaosMode       bool          // Default: true
    ThreatLevelMultiplier float64       // Default: 2.0
}
```

### Cost Amplifier Configuration

```go
type CostAmplifierConfig struct {
    EnablePOW                    bool
    POWDifficulty                int           // Default: 20 (≈1s CPU)
    EnableBandwidthWaste         bool
    BandwidthAmplificationFactor int           // Default: 100x
    EnableSlowdown               bool
    BaseDelay                    time.Duration // Default: 500ms
    MaxDelay                     time.Duration // Default: 30s
    EnableMemoryPressure         bool
    MemoryPressureMB             int           // Default: 100MB
}
```

## Integration with OctoReflex State Machine

The deception framework integrates with the OctoReflex escalation state machine:

```go
// When process reaches ISOLATED (S2) or higher
if state >= StateIsolated {
    // Activate port rotation
    orchestrator.SetThreatLevel(severityNormalized)
    
    // Start collecting intelligence
    port := orchestrator.GetCurrentPort(serviceID)
    
    // Generate POW challenge for new connections
    challenge := orchestrator.GeneratePOWChallenge()
}

// When process reaches FROZEN (S3)
if state >= StateFrozen {
    // TCP decoys are active
    // Bandwidth amplification enabled
}

// When process reaches QUARANTINED (S4)
if state >= StateQuarantined {
    // Full deception active
    // Maximum cost amplification
    orchestrator.SetThreatLevel(1.0)
}
```

## Metrics and Analytics

### Cost Metrics

The framework tracks and calculates:

- **CPU Cost**: Based on POW difficulty and solve time
- **Bandwidth Cost**: Based on bytes amplified and sent
- **Time Cost**: Based on delays imposed and attacker time wasted
- **Total Cost**: Sum of all costs in USD

### Attack Metrics

- Total connection attempts
- Unique attacker IPs
- Authentication attempts
- Attack types detected (SQLi, XSS, LFI, etc.)
- Command patterns in honeypots
- Scanner signatures

### Analytics Window

```go
cfg.AnalyticsWindow = 24 * time.Hour // Keep 24 hours of data

stats := orchestrator.GetStats()
analytics := stats.Analytics
// analytics.TotalEvents
// analytics.UniqueAttackers
// analytics.EventTypeCount
```

## Security Considerations

1. **Honeypot Isolation**: Honeypots run in isolated network namespaces
2. **Resource Limits**: Connection limits prevent DoS
3. **No Real Credentials**: All credentials are fake
4. **Logging**: All attempts are logged for analysis
5. **Network Binding**: Configurable bind addresses (loopback vs public)

## Testing

Run the test suite:

```bash
cd octoreflex/internal/deception
go test -v ./...
```

Run benchmarks:

```bash
go test -bench=. -benchmem
```

## Performance

- Port rotation: ~100ns per lookup (cached sequence)
- POW verification: <1ms for difficulty 20
- TCP decoy: <10ms connection overhead
- Honeypot: ~100MB memory per 1000 concurrent sessions

## Future Enhancements

1. **Kernel-level IP Spoofing**: Full netfilter integration
2. **ML-based Attack Classification**: Pattern recognition
3. **Distributed Honeypots**: Multi-node coordination
4. **Advanced Protocol Emulation**: More realistic services
5. **Automated Response**: Dynamic policy adjustment

## License

Part of the OctoReflex project. See main LICENSE file.
