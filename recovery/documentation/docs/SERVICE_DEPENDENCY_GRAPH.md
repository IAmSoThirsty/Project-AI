# Service Dependency Graph

**Integration Architecture Visualization**  
**Date**: 2026-03-04  
**System**: Sovereign Governance Substrate

---

## Network Topology

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         External Clients                                │
│                    (Browsers, CLI, API Consumers)                       │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             │ HTTP/HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (Future)                               │
│                         (Not Implemented)                               │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
             ┌───────────────┴──────────────┐
             │                              │
             ▼                              ▼
┌──────────────────────┐         ┌──────────────────────┐
│   Main API Gateway   │         │   Sovereign API      │
│   localhost:8001     │         │  (docs/api/)         │
│  ─────────────────   │         └──────────────────────┘
│  /health             │
│  /tarl               │
│  /audit              │
│  /intent             │
│  /execute            │
└──────────────────────┘
             │
             │ Future Integration
             │
┌────────────┴──────────────────────────────────────────────────────────┐
│                                                                        │
│                     MICROSERVICE MESH                                  │
│                  (Docker Network: project-ai-network)                  │
│                                                                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Mutation        │  │  Incident        │  │  Trust Graph     │   │
│  │  Firewall        │  │  Reflex          │  │  Engine          │   │
│  │  :8011           │  │  :8012           │  │  :8013           │   │
│  │                  │  │                  │  │                  │   │
│  │ Governs AI       │  │ Auto-responds    │  │ Reputation       │   │
│  │ mutations        │  │ to incidents     │  │ tracking         │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │  Data Vault      │  │  Negotiation     │  │  Compliance      │   │
│  │  :8014           │  │  Agent           │  │  Engine          │   │
│  │                  │  │  :8015           │  │  :8016           │   │
│  │ Encrypted        │  │                  │  │                  │   │
│  │ sovereign        │  │ Multi-party      │  │ Regulatory       │   │
│  │ storage          │  │ negotiations     │  │ compliance       │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘   │
│                                                                        │
│  ┌──────────────────┐  ┌──────────────────┐                          │
│  │  Verifiable      │  │  I Believe       │                          │
│  │  Reality         │  │  In You          │                          │
│  │  :8017           │  │  :8018           │                          │
│  │                  │  │                  │                          │
│  │ Proof layer      │  │ Motivational     │                          │
│  │ attestation      │  │ service          │                          │
│  └──────────────────┘  └──────────────────┘                          │
│                                                                        │
│         │         │         │         │         │         │           │
│         └─────────┴─────────┴─────────┴─────────┴─────────┘           │
│                            │                                           │
│                            │ Metrics Export                            │
│                            ▼                                           │
│                   ┌──────────────────┐                                │
│                   │   Prometheus     │                                │
│                   │   :9090          │                                │
│                   └────────┬─────────┘                                │
│                            │                                           │
│                            │ Scrapes                                   │
│                            ▼                                           │
│                   ┌──────────────────┐                                │
│                   │   Grafana        │                                │
│                   │   :3000          │                                │
│                   └──────────────────┘                                │
└────────────────────────────────────────────────────────────────────────┘
                             │
                             │ Alerts
                             ▼
                    ┌──────────────────┐
                    │  Alertmanager    │
                    │  :9093           │
                    └──────────────────┘
```

---

## Microservice Dependency Matrix

### Current State (No Inter-Service Calls)

| Service | Depends On | Called By | Integration Status |
|---------|-----------|-----------|-------------------|
| **Mutation Firewall** | None | None | ❌ Isolated |
| **Incident Reflex** | None | None | ❌ Isolated |
| **Trust Graph** | None | None | ❌ Isolated |
| **Data Vault** | None | None | ❌ Isolated |
| **Negotiation Agent** | None | None | ❌ Isolated |
| **Compliance Engine** | None | None | ❌ Isolated |
| **Verifiable Reality** | None | None | ❌ Isolated |
| **I Believe In You** | None | None | ❌ Isolated |

### Expected Dependencies (Design Intent)

| Service | Should Depend On | Purpose |
|---------|-----------------|---------|
| **Mutation Firewall** | Trust Graph, Verifiable Reality | Verify proposer reputation, validate proofs |
| **Incident Reflex** | Negotiation Agent, Compliance | Auto-negotiate remediation, check compliance |
| **Data Vault** | Compliance Engine | Verify data sovereignty rules |
| **Compliance Engine** | Verifiable Reality | Cryptographic compliance proofs |
| **Negotiation Agent** | Trust Graph | Verify negotiation party reputation |

---

## Infrastructure Dependencies

### All Microservices Depend On

```
┌──────────────────┐
│  Microservice    │
│  (any)           │
└────────┬─────────┘
         │
         ├─────▶ Prometheus (metrics export)
         │
         ├─────▶ Docker Network (service discovery)
         │
         └─────▶ Environment Variables (.env)
```

### Temporal Workflow System

```
┌──────────────────┐
│  Temporal        │
│  :7233 (gRPC)    │
│  :8233 (UI)      │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐        ┌──────────────────┐
│  PostgreSQL      │◀───────│ Temporal Worker  │
│  (temporal db)   │        │                  │
└──────────────────┘        └──────────────────┘
```

---

## Service Communication Patterns

### Pattern 1: Synchronous HTTP (Current Architecture)

```
┌─────────────┐                    ┌─────────────┐
│  Service A  │─────── HTTP ──────▶│  Service B  │
│             │◀────── JSON ───────│             │
└─────────────┘                    └─────────────┘

Library: httpx (async HTTP client)
Protocol: REST/JSON
Authentication: JWT or API Key
```

**Status**: ❌ Not implemented (httpx installed but unused)

### Pattern 2: Asynchronous Messaging (Not Implemented)

```
┌─────────────┐                    ┌─────────────┐
│  Service A  │                    │  Service B  │
│             │                    │             │
└──────┬──────┘                    └──────▲──────┘
       │                                  │
       │ Publish                          │ Subscribe
       ▼                                  │
┌───────────────────────────────────────────────┐
│           Message Queue (RabbitMQ/Kafka)      │
└───────────────────────────────────────────────┘
```

**Status**: ❌ Not implemented

### Pattern 3: Event-Driven (Not Implemented)

```
┌─────────────┐     Event     ┌──────────────┐
│  Service A  │────────▶──────│  Event Bus   │
└─────────────┘               └──────┬───────┘
                                     │
                         ┌───────────┴───────────┐
                         ▼                       ▼
                  ┌─────────────┐        ┌─────────────┐
                  │  Service B  │        │  Service C  │
                  └─────────────┘        └─────────────┘
```

**Status**: ❌ Not implemented

---

## Data Flow Diagrams

### Proposed: Mutation Proposal Flow

```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │ POST /api/v1/proposals
       ▼
┌────────────────────────────┐
│  Mutation Firewall (8011)  │
│  ───────────────────────   │
│  1. Validate proposal      │
│  2. Check proposer trust   │────────┐
│  3. Simulate mutation      │        │ GET /api/v1/reputation/{id}
│  4. Verify proof           │        ▼
│  5. Store decision         │  ┌─────────────────┐
└────────────────────────────┘  │  Trust Graph    │
       │                        │  (8013)         │
       │ Async call             └─────────────────┘
       ▼
┌────────────────────────────┐
│  Verifiable Reality (8017) │
│  ───────────────────────   │
│  1. Validate ZK proof      │
│  2. Attest reality         │
│  3. Return attestation     │
└────────────────────────────┘
```

**Status**: ⚠️ Designed but not implemented

### Proposed: Incident Response Flow

```
┌──────────────┐
│   Incident   │ (Security event detected)
└──────┬───────┘
       │ POST /api/v1/incidents
       ▼
┌────────────────────────────┐
│  Incident Reflex (8012)    │
│  ───────────────────────   │
│  1. Classify incident      │
│  2. Assess severity        │
│  3. Auto-remediate         │────────┐
│  4. Negotiate if needed    │        │ POST /api/v1/negotiations
└────────────────────────────┘        ▼
       │                        ┌─────────────────┐
       │ Record                 │  Negotiation    │
       ▼                        │  Agent (8015)   │
┌────────────────────────────┐ └─────────────────┘
│  Compliance Engine (8016)  │
│  ───────────────────────   │
│  1. Log compliance event   │
│  2. Check regulatory reqs  │
│  3. Generate audit report  │
└────────────────────────────┘
```

**Status**: ⚠️ Designed but not implemented

---

## Port Allocation Map

### Application Ports

| Port  | Service | Protocol | Accessibility |
|-------|---------|----------|---------------|
| 5000  | Main App (Flask) | HTTP | External |
| 8000  | Metrics (Main) | HTTP | External |
| 8001  | API Gateway | HTTP | External |
| 8002  | Reserved | - | - |
| 8003  | Reserved | - | - |
| 8011  | Mutation Firewall | HTTP | Internal/External |
| 8012  | Incident Reflex | HTTP | Internal/External |
| 8013  | Trust Graph | HTTP | Internal/External |
| 8014  | Data Vault | HTTP | Internal/External |
| 8015  | Negotiation Agent | HTTP | Internal/External |
| 8016  | Compliance Engine | HTTP | Internal/External |
| 8017  | Verifiable Reality | HTTP | Internal/External |
| 8018  | I Believe In You | HTTP | Internal/External |

### Infrastructure Ports

| Port  | Service | Protocol | Purpose |
|-------|---------|----------|---------|
| 3000  | Grafana | HTTP | Metrics visualization |
| 7233  | Temporal | gRPC | Workflow orchestration |
| 8233  | Temporal UI | HTTP | Workflow monitoring |
| 9090  | Prometheus | HTTP | Metrics collection |
| 9093  | Alertmanager | HTTP | Alert management |
| 5432  | PostgreSQL | TCP | Database (internal only) |

**Network**: All services on `project-ai-network` (Docker bridge)

---

## Service Discovery

### DNS Resolution (Docker)

Each service is accessible by container name:

```bash

# Within Docker network

curl http://mutation-firewall:8000/api/v1/health/liveness
curl http://trust-graph-engine:8000/api/v1/health/readiness
curl http://sovereign-data-vault:8000/api/v1/health/startup
```

### Service Registry (Not Implemented)

**Options for Future**:

- **Consul**: Service registry + health checking
- **Eureka**: Netflix service discovery
- **etcd**: Distributed key-value store
- **Kubernetes Service**: Native K8s discovery

---

## Load Balancing Strategy

### Current: None (Single Instances)

Each service runs as a single container.

### Proposed: Kubernetes HPA

```yaml

# kubernetes/hpa.yaml (exists for all services)

apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mutation-firewall
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mutation-firewall
  minReplicas: 2
  maxReplicas: 10
  metrics:

  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

```

**Status**: ✅ HPA manifests exist, not deployed

---

## Failure Modes & Recovery

### Service Failure Scenarios

| Failure | Impact | Current Mitigation | Recommendation |
|---------|--------|-------------------|----------------|
| **Mutation Firewall Down** | Can't process proposals | None | Circuit breaker + fallback |
| **Trust Graph Down** | Can't verify reputation | None | Cached reputation scores |
| **Data Vault Down** | Can't access encrypted data | None | Replicated storage |
| **Prometheus Down** | No metrics | None | Prometheus federation |
| **Temporal Down** | Workflows fail | PostgreSQL persistence | Multi-node Temporal |

### Health Check Matrix

| Service | Liveness | Readiness | Startup | Docker Health |
|---------|----------|-----------|---------|---------------|
| Main API | ✅ | ✅ | ✅ | ✅ Configured |
| Mutation Firewall | ✅ | ✅ | ✅ | ❌ Missing |
| Incident Reflex | ✅ | ✅ | ✅ | ❌ Missing |
| Trust Graph | ✅ | ✅ | ✅ | ❌ Missing |
| Data Vault | ✅ | ✅ | ✅ | ❌ Missing |
| Negotiation Agent | ✅ | ✅ | ✅ | ❌ Missing |
| Compliance Engine | ✅ | ✅ | ✅ | ❌ Missing |
| Verifiable Reality | ✅ | ✅ | ✅ | ❌ Missing |

---

## Security Boundaries

### Trust Zones

```
┌─────────────────────────────────────────────┐
│         EXTERNAL ZONE (Untrusted)           │
│                                             │
│  Internet Clients, Third-Party APIs         │
└──────────────────┬──────────────────────────┘
                   │
                   │ Firewall / API Gateway
                   │
┌──────────────────▼──────────────────────────┐
│         DMZ (Semi-Trusted)                  │
│                                             │
│  Main API (8001), Public Endpoints          │
└──────────────────┬──────────────────────────┘
                   │
                   │ Internal Auth (JWT/mTLS)
                   │
┌──────────────────▼──────────────────────────┐
│    INTERNAL ZONE (Trusted)                  │
│                                             │
│  Microservices (8011-8018)                  │
│  Prometheus, Grafana, Temporal              │
└──────────────────┬──────────────────────────┘
                   │
                   │ Database Auth
                   │
┌──────────────────▼──────────────────────────┐
│    DATA ZONE (Highly Restricted)            │
│                                             │
│  PostgreSQL, Data Vault Storage             │
└─────────────────────────────────────────────┘
```

### Network Policies (Kubernetes)

All services have `network-policy.yaml` defining:

- Ingress rules (allowed incoming traffic)
- Egress rules (allowed outgoing traffic)
- Pod selectors

**Status**: ✅ Defined, not deployed

---

## Deployment Dependencies

### Service Startup Order

```

1. PostgreSQL (temporal-postgresql)
   │
   ▼
2. Temporal
   │
   ▼
3. Prometheus
   │
   ├──▶ 4. All Microservices (parallel)
   │    │   - mutation-firewall
   │    │   - incident-reflex
   │    │   - trust-graph
   │    │   - data-vault
   │    │   - negotiation-agent
   │    │   - compliance-engine
   │    │   - verifiable-reality
   │    │   - i-believe-in-you
   │    │
   │    ▼
   ├──▶ 5. Temporal Worker
   │
   ▼
6. Grafana, Alertmanager (parallel)

```

**Managed By**: Docker Compose `depends_on` directives

---

## Performance Considerations

### Request Latency Budget

| Operation | Target | Max |
|-----------|--------|-----|
| Health check | < 10ms | 50ms |
| Simple GET | < 50ms | 200ms |
| Complex query | < 200ms | 1s |
| Inter-service call | < 100ms | 500ms |

### Throughput Targets

| Service | Target RPS | Max RPS |
|---------|-----------|---------|
| Mutation Firewall | 100 | 250 (rate limit) |
| Trust Graph | 500 | 1000 |
| Data Vault | 200 | 500 |

**Current Bottlenecks**: None (services not under load)

---

## Monitoring Dependencies

### Prometheus Scrape Targets

```yaml

# config/prometheus/prometheus.yml (expected)

scrape_configs:

  - job_name: 'main-api'
    static_configs:
      - targets: ['project-ai:8000']
  
  - job_name: 'mutation-firewall'
    static_configs:
      - targets: ['mutation-firewall:8000']
  
  - job_name: 'incident-reflex'
    static_configs:
      - targets: ['incident-reflex:8000']
  
  # ... all other services

```

### Grafana Dashboards

**Expected Dashboards**:

1. **Service Overview**: All service health, request rates
2. **Performance**: Latency percentiles, throughput
3. **Errors**: Error rates, failed requests
4. **Infrastructure**: CPU, memory, disk usage
5. **Business Metrics**: Mutation proposals, incidents, negotiations

**Status**: ⚠️ Configuration exists, dashboards need creation

---

## Conclusion

**Current State**: **ISOLATED MICROSERVICES**

- ✅ Network topology configured
- ✅ Service discovery available (DNS)
- ✅ Observability infrastructure ready
- ❌ No inter-service communication
- ❌ No integration testing

**Target State**: **INTEGRATED MICROSERVICES**

- Synchronous HTTP calls for request/response
- Asynchronous messaging for events (optional)
- Service mesh for security and observability
- Comprehensive integration testing

**Next Steps**:

1. Implement service client libraries
2. Define inter-service API contracts
3. Add integration tests
4. Deploy service mesh (optional)

---

**Generated**: 2026-03-04  
**Author**: Integration Architect Agent  
**Status**: ✅ COMPLETE
