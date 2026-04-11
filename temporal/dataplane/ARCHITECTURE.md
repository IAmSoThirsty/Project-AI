# Data Plane Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SOVEREIGN AGENT LAYER                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Agent 1  │  │ Agent 2  │  │ Agent 3  │  │ Agent N  │  │ Workflow │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼────────────┘
        │             │             │             │             │
        └─────────────┴─────────────┴─────────────┴─────────────┘
                               │
        ┌──────────────────────┴───────────────────────┐
        │                                              │
┌───────▼────────────────────────────────────────────┐ │
│         DATA PLANE CLIENT (Unified API)            │ │
│  ┌──────────────────────────────────────────────┐  │ │
│  │  • Automatic routing (small vs large msgs)   │  │ │
│  │  • Cache-aware operations                    │  │ │
│  │  • RDMA fallback support                     │  │ │
│  │  • Compression & encryption                  │  │ │
│  └──────────────────────────────────────────────┘  │ │
└────────────────────────────────────────────────────┘ │
        │                                              │
        │ Smart Routing                                │
        ├──────────────┬──────────────┬────────────────┤
        │              │              │                │
        ▼              ▼              ▼                ▼
┌───────────────┐ ┌──────────┐ ┌──────────┐  ┌─────────────┐
│  MESSAGE      │ │ OBJECT   │ │  CACHE   │  │   RDMA      │
│  QUEUE        │ │ STORAGE  │ │ (Redis)  │  │ (Optional)  │
└───────────────┘ └──────────┘ └──────────┘  └─────────────┘
        │              │              │                │
        ▼              ▼              ▼                ▼
┌───────────────────────────────────────────────────────────┐
│              INFRASTRUCTURE LAYER                          │
├───────────────┬──────────────┬──────────────┬─────────────┤
│  KAFKA        │   MinIO      │   Redis      │    RoCE     │
│  (or NATS)    │   (S3)       │  Cluster     │  Network    │
│               │              │              │             │
│ • Brokers: 3+ │ • Nodes: 4+  │ • Replicas:3 │ • NIC:      │
│ • Topics      │ • Buckets    │ • Sentinel   │   Mellanox  │
│ • Partitions  │ • Versioning │ • Sharding   │ • Protocol: │
│ • Replication │ • Lifecycle  │ • Eviction   │   RoCEv2    │
└───────────────┴──────────────┴──────────────┴─────────────┘
        │              │              │                │
        └──────────────┴──────────────┴────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              MONITORING & OBSERVABILITY                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐        │
│  │ Prometheus │  │  Grafana   │  │   Alerts   │        │
│  │  Metrics   │  │ Dashboards │  │  Manager   │        │
│  └────────────┘  └────────────┘  └────────────┘        │
└─────────────────────────────────────────────────────────┘
```

## Data Flow Patterns

### Pattern 1: Small Message (< 1MB)
```
Agent A → DataPlane Client → Message Queue → Agent B
                    ↓
                  Cache (optional)
```

### Pattern 2: Large Message (>= 1MB)
```
Agent A → DataPlane Client → Object Storage (upload)
                    ↓
              Message Queue (reference)
                    ↓
              Agent B → Fetch from Storage
                    ↓
                  Cache (hot data)
```

### Pattern 3: RDMA Direct Transfer (optional)
```
Agent A → DataPlane Client → RDMA Write → Agent B Memory
         (cluster-local, sub-microsecond latency)
```

## Component Responsibilities

### Message Queue (Kafka/NATS)
- **Purpose**: Reliable, ordered message delivery
- **Best for**: Small messages, events, commands
- **Guarantees**: At-least-once delivery, ordering per partition
- **Performance**: 10k-100k msgs/sec, 5-10ms latency

### Object Storage (MinIO/S3)
- **Purpose**: Scalable artifact storage
- **Best for**: Large files, build outputs, datasets
- **Features**: Versioning, lifecycle, multi-region
- **Performance**: 1-5 GB/s throughput per node

### Cache (Redis)
- **Purpose**: Hot data acceleration
- **Best for**: Frequently accessed artifacts, session state
- **Features**: LRU eviction, TTL, distributed locks
- **Performance**: 100k-500k ops/sec, sub-millisecond latency

### RDMA (Optional)
- **Purpose**: Ultra-low latency transfers
- **Best for**: Time-critical agent communication
- **Requirements**: RDMA-capable NICs, RoCE network
- **Performance**: < 1μs latency, kernel bypass

## Deployment Topologies

### Development (Single Node)
```
Docker Compose → All services on localhost
- Kafka: 1 broker
- MinIO: 1 node
- Redis: 1 instance
- RDMA: Disabled
```

### Production (Kubernetes Cluster)
```
Multi-node K8s cluster:
- Kafka: 3-5 brokers (fault tolerance)
- MinIO: 4-16 nodes (distributed mode)
- Redis: 3-6 replicas (Sentinel HA)
- RDMA: Optional (with capable nodes)
```

## Performance Targets

| Metric                    | Target        | Scaling Strategy           |
|---------------------------|---------------|----------------------------|
| Small Message Latency     | < 10ms p99    | Add Kafka partitions       |
| Large Message Throughput  | > 1 GB/s      | Add MinIO nodes            |
| Cache Operations          | > 100k ops/s  | Add Redis replicas         |
| Storage Upload            | > 500 MB/s    | Network + disk bandwidth   |
| Aggregate Throughput      | 10 GB/s       | Horizontal scaling         |
| RDMA Latency (optional)   | < 100μs       | RoCE tuning, QoS           |

## Scaling Guidelines

### Horizontal Scaling
- **Kafka**: Add brokers, increase partitions
- **MinIO**: Add nodes (distributed erasure coding)
- **Redis**: Add replicas, enable cluster mode
- **Network**: Add bandwidth, multiple NICs

### Vertical Scaling
- **CPU**: More cores for compression, encryption
- **Memory**: Larger caches, message buffers
- **Network**: 25/40/100 GbE, RDMA-capable NICs
- **Storage**: NVMe SSDs for MinIO

## Security

### Encryption
- **In-flight**: TLS 1.3 for all network traffic
- **At-rest**: AES-256 for object storage
- **RDMA**: Encrypted payloads (RDMA doesn't encrypt)

### Authentication
- **Kafka**: SASL/SCRAM or mTLS
- **MinIO**: Access/Secret keys, IAM policies
- **Redis**: AUTH password, ACLs

### Network Isolation
- **Kubernetes**: Network policies, namespaces
- **Firewall**: Allow only required ports
- **VLANs**: Separate data plane traffic
