# OctoReflex Federated Threat Consensus System

A gossip-based federated quorum for distributed threat intelligence sharing and consensus across OctoReflex nodes.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│           OctoReflex Federated Quorum               │
└─────────────────────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
  ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
  │  SWIM   │    │  Raft   │    │ ThreatDB│
  │ Gossip  │    │Consensus│    │  (IoCs) │
  └────┬────┘    └────┬────┘    └────┬────┘
       │               │               │
  ┌────▼────────────────▼───────────────▼────┐
  │      Network Protocol (gRPC/mTLS)        │
  └──────────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       │               │               │
  ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
  │  Node 1 │    │  Node 2 │    │  Node 3 │
  └─────────┘    └─────────┘    └─────────┘
```

## Components

### 1. SWIM Gossip Protocol (`gossip/swim.go`)

**Purpose**: Scalable, weakly-consistent cluster membership and failure detection.

**Features**:
- Decentralized failure detection (no SPOF)
- O(log N) detection time
- Constant network load per node
- Infection-style state dissemination
- Configurable suspicion timeout

**Protocol Flow**:
1. Periodic ping to random member (every 1s)
2. Indirect ping via k random nodes if no ack
3. Mark member as suspect if all fail
4. Transition suspect → dead after timeout
5. Gossip membership changes on all messages

**Configuration**:
```go
cfg := gossip.DefaultSWIMConfig()
cfg.ProtocolPeriod = 1 * time.Second
cfg.AckTimeout = 500 * time.Millisecond
cfg.IndirectChecks = 3
cfg.SuspicionMult = 4
```

### 2. Byzantine Fault Tolerance (`gossip/byzantine.go`)

**Purpose**: Detect and mitigate Byzantine (malicious/faulty) nodes.

**Guarantees**:
- System remains correct with f < n/3 Byzantine nodes
- Cryptographic message authentication (Ed25519)
- Replay attack prevention
- Double-vote detection
- Reputation tracking

**Attack Mitigations**:
- **Sybil attack**: PKI-based identity verification
- **Eclipse attack**: Diverse peer selection
- **Replay attack**: Sequence numbers + timestamps
- **Message tampering**: Cryptographic signatures
- **Split-brain**: Quorum requirements

**Evidence Types**:
- Invalid signature
- Double voting (conflicting votes)
- Replay attacks
- Timestamp skew
- Conflicting state reports
- Malformed messages

### 3. Raft Consensus (`consensus/raft.go`)

**Purpose**: Strong consistency for critical decisions.

**Guarantees**:
- Linearizable reads/writes
- Automatic leader election
- Log replication
- Safety: at most one leader per term
- Liveness: majority (f < n/2) failures tolerated

**Use Cases**:
- ✅ Coordinated threat responses (network-wide isolation)
- ✅ Configuration changes (cluster policies)
- ✅ Critical metadata (threat signatures)
- ✅ Membership changes (add/remove nodes)

**Non-Use Cases** (use SWIM instead):
- ❌ Individual threat detections (too frequent)
- ❌ Per-process anomaly scores (high volume)
- ❌ Heartbeats (use SWIM failure detection)

**Configuration**:
```go
cfg := consensus.DefaultRaftConfig("node-id")
cfg.ElectionTimeout = 150 * time.Millisecond
cfg.HeartbeatPeriod = 50 * time.Millisecond
```

### 4. Threat Intelligence Database (`threatdb/database.go`)

**Purpose**: Distributed threat intelligence storage and sharing.

**Storage Types**:
- **Signatures**: SHA256 hashes, YARA rules, binary patterns
- **IoCs**: IPs, domains, file hashes, certificates
- **Behavioral Patterns**: Syscall sequences, network flows

**Features**:
- BoltDB for local persistence
- In-memory cache for fast lookups
- Delta synchronization (incremental updates)
- Consensus-based confirmation
- Automatic aggregation of scores

**API**:
```go
// Add signature
sig := &threatdb.Signature{
    Hash:     sha256.Sum256([]byte("malware")),
    Type:     threatdb.SignatureYARA,
    Pattern:  []byte("rule malware {...}"),
    Severity: 0.9,
}
db.AddSignature(sig)

// Check threat
isThreat, severity := db.CheckIP("192.168.1.100")
```

### 5. Network Protocol (`network/protocol.go`)

**Purpose**: Efficient, secure communication between nodes.

**Features**:
- gRPC with mTLS (TLS 1.3)
- Message compression (gzip)
- Batch aggregation
- Connection pooling
- Rate limiting (token bucket)
- Multicast support

**Message Types**:
- Threat announcements
- Consensus votes (Raft RPCs)
- Membership updates (SWIM)
- Threat intelligence deltas
- Health checks

**Network Optimizations**:
- Compress messages > 1KB
- Batch small messages (10 msgs or 100ms)
- Connection reuse
- Backpressure handling

## Usage

### Starting a Quorum Node

```go
import (
    "context"
    "github.com/octoreflex/octoreflex/internal/quorum"
    "go.uber.org/zap"
)

// Create configuration
cfg := quorum.DefaultConfig("node-1", "127.0.0.1:7000")
cfg.SeedNodes = []string{"127.0.0.1:7000", "127.0.0.1:7001"}
cfg.Peers = map[string]string{
    "node-2": "127.0.0.1:7001",
    "node-3": "127.0.0.1:7002",
}
cfg.CertFile = "certs/node-1.pem"
cfg.KeyFile = "certs/node-1-key.pem"
cfg.CAFile = "certs/ca.pem"

// Create quorum
log := zap.NewProduction()
q, err := quorum.NewQuorum(cfg, log)
if err != nil {
    log.Fatal("failed to create quorum", zap.Error(err))
}

// Start quorum
ctx := context.Background()
if err := q.Start(ctx); err != nil {
    log.Fatal("failed to start quorum", zap.Error(err))
}
defer q.Stop()
```

### Submitting Threats

```go
// Submit threat for consensus
threat := &quorum.ThreatSubmission{
    ProcessHash:  "abc123...",
    AnomalyScore: 0.95,
    Severity:     0.9,
    Evidence:     []byte("suspicious syscalls"),
    SubmittedBy:  "node-1",
    SubmittedAt:  time.Now(),
}

if err := q.SubmitThreat(threat); err != nil {
    log.Error("failed to submit threat", zap.Error(err))
}
```

### Adding Threat Intelligence

```go
// Add signature
sig := &threatdb.Signature{
    Hash:        threatdb.ComputeHash([]byte("malware-pattern")),
    Type:        threatdb.SignatureYARA,
    Pattern:     []byte("rule malware { ... }"),
    Severity:    0.9,
    Description: "Ransomware variant",
    Source:      "node-1",
    Confidence:  0.95,
}
q.AddSignature(sig)

// Check if process is a threat
isThreat, severity, err := q.CheckThreat(processHash)
if isThreat {
    log.Warn("threat detected", zap.Float64("severity", severity))
}
```

### Monitoring Cluster Health

```go
// Get cluster members
members := q.GetMembers()
for _, m := range members {
    log.Info("member",
        zap.String("id", m.ID),
        zap.String("addr", m.Addr),
        zap.String("state", m.State.String()))
}

// Get current leader
leader := q.GetLeader()
log.Info("current leader", zap.String("id", leader))

// Get metrics
metrics := q.GetMetrics()
log.Info("quorum metrics",
    zap.Uint64("messages_rx", metrics.MessagesReceived),
    zap.Uint64("messages_tx", metrics.MessagesSent),
    zap.Uint64("consensus", metrics.ConsensusDecisions),
    zap.Uint64("threats_synced", metrics.ThreatsSynced),
    zap.Uint64("byzantine", metrics.ByzantineDetected))
```

## Security Considerations

### Cryptographic Guarantees

- **Ed25519 signatures**: All messages cryptographically signed
- **mTLS**: TLS 1.3 with mutual authentication
- **PKI**: Certificate-based node identity
- **Replay protection**: Timestamp + sequence numbers
- **Byzantine tolerance**: Up to 33% malicious nodes

### Certificate Setup

Generate certificates for each node:

```bash
# Generate CA
openssl req -x509 -newkey ed25519 -nodes \
    -keyout ca-key.pem -out ca.pem \
    -days 3650 -subj "/CN=OctoReflex-CA"

# Generate node certificate
openssl req -newkey ed25519 -nodes \
    -keyout node-1-key.pem -out node-1.csr \
    -subj "/CN=node-1"

openssl x509 -req -in node-1.csr \
    -CA ca.pem -CAkey ca-key.pem \
    -out node-1.pem -days 365 -CAcreateserial
```

## Performance Characteristics

### Scalability

- **Cluster size**: 3-1000 nodes
- **SWIM detection time**: O(log N)
- **Network load per node**: Constant (independent of N)
- **Raft write latency**: 1-2 RTTs
- **Threat sync interval**: 5 minutes (configurable)

### Resource Usage

Per-node baseline (1000 processes monitored):
- **Memory**: ~50MB (threat DB) + ~10MB (membership)
- **CPU**: <2% (gossip + consensus)
- **Network**: ~10KB/s (steady state)
- **Disk**: ~100MB (threat DB + logs)

### Tuning Parameters

```go
// SWIM tuning
cfg.SWIM.ProtocolPeriod = 1 * time.Second     // ping frequency
cfg.SWIM.IndirectChecks = 3                   // indirect ping fanout
cfg.SWIM.SuspicionMult = 4                    // suspect timeout multiplier

// Raft tuning
cfg.Raft.ElectionTimeout = 150 * time.Millisecond
cfg.Raft.HeartbeatPeriod = 50 * time.Millisecond
cfg.Raft.SnapshotThreshold = 10000            // log entries before snapshot

// Network tuning
cfg.BatchSize = 10                            // messages per batch
cfg.BatchDelay = 100 * time.Millisecond       // max batch delay
cfg.Compression = true                        // enable compression
```

## Testing

### Unit Tests

```bash
cd internal/quorum
go test -v ./...
```

### Integration Tests

```bash
# Multi-node tests (requires more time)
go test -v -timeout 60s ./... -run Integration

# Byzantine fault injection
go test -v ./gossip -run Byzantine

# Raft consensus tests
go test -v ./consensus -run Raft
```

### Benchmark Tests

```bash
go test -bench=. -benchmem ./...
```

## Troubleshooting

### Split-Brain Detection

If nodes disagree on cluster membership:

1. Check network connectivity (`ping`, `traceroute`)
2. Verify TLS certificates are valid
3. Check for clock skew (`ntpd`, `chrony`)
4. Review logs for Byzantine detection events
5. Verify quorum configuration matches on all nodes

### Performance Issues

If messages are slow or dropped:

1. Check network bandwidth (`iperf`)
2. Increase batch size/delay
3. Enable compression
4. Adjust SWIM protocol period
5. Monitor CPU/memory usage

### Byzantine Nodes

If suspicious behavior detected:

1. Review evidence in logs
2. Check node reputation scores
3. Verify certificates haven't been compromised
4. Isolate suspected node
5. Rotate certificates if needed

## Future Enhancements

- [ ] PBFT consensus option (stronger Byzantine tolerance)
- [ ] Multicast optimization for LAN deployments
- [ ] Adaptive quorum sizing
- [ ] Machine learning for threat scoring
- [ ] Geo-distributed optimizations
- [ ] WebAssembly signatures for portable rules
- [ ] Threat intelligence marketplace integration

## References

- [SWIM: Scalable Weakly-consistent Infection-style Process Group Membership Protocol](https://www.cs.cornell.edu/projects/Quicksilver/public_pdfs/SWIM.pdf)
- [In Search of an Understandable Consensus Algorithm (Raft)](https://raft.github.io/raft.pdf)
- [Practical Byzantine Fault Tolerance](http://pmg.csail.mit.edu/papers/osdi99.pdf)
- [The Byzantine Generals Problem](https://lamport.azurewebsites.net/pubs/byz.pdf)

## License

Copyright (c) 2024 OctoReflex Project. All rights reserved.
