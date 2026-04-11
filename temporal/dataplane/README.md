# High-Performance Data Plane Architecture

## Overview

The Sovereign Governance Data Plane provides low-latency, high-throughput communication infrastructure for agent-to-agent communication, artifact transfer, and state synchronization.

**Target Performance**: 10GB/s aggregate throughput with sub-millisecond latency.

## Architecture Components

### 1. Message Queue Layer (Kafka/NATS)
- **Kafka**: For guaranteed message ordering and durable event streaming
- **NATS**: For ultra-low latency pub/sub messaging
- Both support multi-tenancy and topic-based routing

### 2. Object Storage (S3/MinIO)
- Artifact storage for build outputs, datasets, models
- Versioned storage with lifecycle policies
- Multi-region replication support
- Direct client-to-storage transfers to avoid gateway bottlenecks

### 3. Cache Layer (Redis)
- Hot data caching for frequently accessed artifacts
- Session state management
- Message deduplication
- Distributed locks for coordination

### 4. RDMA Support (Optional)
- Hardware-accelerated networking using RDMA over Converged Ethernet (RoCE)
- Direct memory access between agents
- Feature-flagged for environments with RDMA-capable NICs
- Bypasses kernel for ultra-low latency (<1μs)

## Data Flow Patterns

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Agent A   │─────▶│ Message Queue│─────▶│   Agent B   │
│             │      │ (Kafka/NATS) │      │             │
└─────────────┘      └──────────────┘      └─────────────┘
       │                                           │
       │             ┌──────────────┐             │
       └────────────▶│    Redis     │◀────────────┘
                     │   (Cache)    │
                     └──────────────┘
                            │
                     ┌──────────────┐
                     │    MinIO     │
                     │  (Storage)   │
                     └──────────────┘
```

### Pattern 1: Small Messages (< 1MB)
- Direct message queue delivery
- Cached in Redis for hot access
- No object storage involved

### Pattern 2: Large Artifacts (> 1MB)
1. Upload artifact to MinIO
2. Send object reference via message queue
3. Receiver pulls from MinIO (with Redis caching)

### Pattern 3: RDMA Direct Transfer (Optional)
- For cluster-local, RDMA-capable nodes
- Direct memory-to-memory transfer
- Fallback to standard network stack if unavailable

## Deployment

All components deploy via Docker Compose for local development and Kubernetes for production:

```bash
# Local development
docker-compose -f temporal/dataplane/docker-compose.yml up -d

# Production (Kubernetes)
kubectl apply -f temporal/dataplane/k8s/
```

## Configuration

Environment variables control feature flags and endpoints:

```bash
# Message Queue Selection
MESSAGE_QUEUE_TYPE=kafka  # or 'nats'

# RDMA Feature Flag
ENABLE_RDMA=false

# Endpoints
KAFKA_BROKERS=localhost:9092
NATS_URL=nats://localhost:4222
MINIO_ENDPOINT=localhost:9000
REDIS_URL=redis://localhost:6379
```

## Performance Targets

| Metric | Target | Measured |
|--------|--------|----------|
| Message Latency (p99) | < 10ms | TBD |
| Throughput (aggregate) | 10GB/s | TBD |
| Object Storage Bandwidth | 5GB/s | TBD |
| Cache Hit Rate | > 80% | TBD |
| RDMA Latency (p99) | < 100μs | TBD |

## Benchmarks

Run benchmarks:
```bash
python temporal/dataplane/benchmarks/run_all.py
```

See detailed results in `temporal/dataplane/benchmarks/results/`.

## Security

- TLS encryption for all network traffic
- mTLS between agents
- Object storage encryption at rest (AES-256)
- Redis AUTH password protection
- RBAC policies for Kafka topics
- Network isolation via VLANs/VPCs

## Monitoring

Metrics exported via Prometheus:
- Message queue lag
- Object storage bandwidth
- Cache hit/miss rates
- RDMA transfer statistics
- End-to-end latency histograms

Dashboards available in Grafana.
