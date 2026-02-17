# SASE Deployment Guide

## Quick Start

### 1. Prerequisites

**Required**:

- Python 3.9+
- Docker & Docker Compose (for observability stack)

**Optional External Services**:

- GeoIP API (ipapi.co or maxmind)
- HSM (YubiHSM2 or AWS CloudHSM)  
- Blockchain RPC (for Merkle anchoring)

### 2. Installation

```bash
cd Project-AI/src/cerberus/sase

# Install Python dependencies
pip install numpy avro-python3

# (Optional) Install SASE as package
cd ../../..
pip install -e .
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
nano .env
```

**Minimal Configuration** (dev mode):

```env
SASE_DEPLOYMENT=single_node
SASE_PROMETHEUS_ENABLED=true
SASE_GRAFANA_ENABLED=true
```

**Production Configuration**:

```env
SASE_DEPLOYMENT=ha_cluster
SASE_NODE_ID=sase-node-1
SASE_CLUSTER_NODES=sase-node-1,sase-node-2,sase-node-3

# External Services
SASE_GEOIP_ENABLED=true
SASE_GEOIP_API_KEY=<your_key>

SASE_HSM_ENABLED=true
SASE_HSM_TYPE=yubihsm

# Observability
SASE_PROMETHEUS_ENABLED=true
SASE_GRAFANA_ENABLED=true
```

### 4. Start Observability Stack

```bash
# Start Prometheus + Grafana via Docker
docker-compose up -d

# Verify
docker ps
curl http://localhost:9090/-/healthy  # Prometheus
curl http://localhost:3000/api/health  # Grafana
```

Access Grafana: `http://localhost:3000`

- Username: `admin`
- Password: `sase_admin`

### 5. Run SASE

```bash
cd src
python -m cerberus.sase.example_usage
```

---

## Integration with Cerberus

### 1. Import SASE Orchestrator

```python
from cerberus.sase.sase_orchestrator import SASEOrchestrator
from cerberus.sase.core.substrate import DeploymentTopology

# Initialize
sase = SASEOrchestrator(
    deployment=DeploymentTopology.SINGLE_NODE,
    node_id="cerberus-sase-1"
)
```

### 2. Integrate with Triumvirate

```python
from cerberus.sase.integration.cerberus_bridge import SASECerberusBridge

# Initialize bridge
bridge = SASECerberusBridge()

# Process telemetry and request authorization
result = sase.process_telemetry(raw_event)

if result['success']:
    # Request Cerberus action via Triumvirate
    action_result = bridge.request_cerberus_action(result)
```

### 3. Triumvirate Authorization Flow

```
SASE Confidence → Threat Level Mapping:
- <30%:  LOW
- 30-49%:  MEDIUM  
- 50-69%: HIGH
- 70-84%: CRITICAL
- 85-100%: EXISTENTIAL

Triumvirate Auto-Approval:
- CRITICAL+ threats → Auto-approved
- HIGH and below → Multi-consensus required
```

---

## HSM Setup

### YubiHSM2

1. Install YubiHSM connector:

```bash
# Download from yubico.com
# Start connector
yubihsm-connector -d
```

1. Configure `.env`:

```env
SASE_HSM_ENABLED=true
SASE_HSM_TYPE=yubihsm
YUBIHSM_CONNECTOR_URL=http://localhost:12345
YUBIHSM_AUTH_KEY_ID=1
YUBIHSM_PASSWORD=<your_password>
```

### AWS CloudHSM

1. Provision cluster via AWS Console

2. Configure `.env`:

```env
SASE_HSM_ENABLED=true
SASE_HSM_TYPE=aws_cloudhsm
AWS_CLOUDHSM_CLUSTER_ID=cluster-xxx
AWS_CLOUDHSM_USER=admin
AWS_CLOUDHSM_PASSWORD=<your_password>
```

---

## GeoIP/ASN Enrichment

### Option 1: ipapi.co (Free tier)

```env
SASE_GEOIP_ENABLED=true
SASE_GEOIP_API_URL=https://ipapi.co/{ip}/json/
# No API key needed for free tier (1000 req/day)
```

### Option 2: MaxMind GeoIP2

1. Create account at maxmind.com
2. Download GeoLite2 database
3. Configure:

```env
SASE_GEOIP_ENABLED=true
GEOIP_DATABASE_PATH=/path/to/GeoLite2-City.mmdb
```

### ASN Lookup (BGPView)

```env
SASE_ASN_ENABLED=true
SASE_ASN_API_URL=https://api.bgpview.io/ip/{ip}
```

---

## Monitoring & Dashboards

### Prometheus Metrics

SASE exposes metrics at `/metrics` endpoint:

- `sase_events_ingested_total` - Total events processed
- `sase_false_positive_rate` - False positive rate (0-1)
- `sase_mean_time_to_detect_seconds` - Detection latency
- `sase_model_drift_delta` - Current model drift
- `sase_containment_actions_total` - Containment actions executed

### Grafana Dashboard

1. Access Grafana: `http://localhost:3000`
2. Navigate to Dashboards → SASE Overview
3. View real-time metrics

**Dashboard includes**:

- Events ingested (total & rate)
- False positive gauge
- Mean time to detect
- Model drift indicator
- Containment action timeline
- ASN entropy trends

---

## Multi-Region Deployment

### HA Cluster (3-node Raft)

**Node 1** (`.env`):

```env
SASE_DEPLOYMENT=ha_cluster
SASE_NODE_ID=sase-node-1
SASE_CLUSTER_NODES=sase-node-1,sase-node-2,sase-node-3
```

**Node 2** (`.env`):

```env
SASE_DEPLOYMENT=ha_cluster
SASE_NODE_ID=sase-node-2
SASE_CLUSTER_NODES=sase-node-1,sase-node-2,sase-node-3
```

**Node 3** (`.env`):

```env
SASE_DEPLOYMENT=ha_cluster
SASE_NODE_ID=sase-node-3
SASE_CLUSTER_NODES=sase-node-1,sase-node-2,sase-node-3
```

Raft consensus ensures:

- Leader election on failure
- Log replication across nodes
- Split-brain prevention

---

## Troubleshooting

### Module Import Errors

```
ModuleNotFoundError: No module named 'cerberus'
```

**Fix**: Run from `src/` directory:

```bash
cd Project-AI/src
python -m cerberus.sase.example_usage
```

### Prometheus Connection Refused

```
Error: connection refused to prometheus:9090
```

**Fix**: Ensure Docker containers running:

```bash
docker-compose up -d
docker logs sase-prometheus
```

### HSM Connection Failed

```
Warning: HSM not available - using software signing
```

**Fix**:

- Verify HSM connector running
- Check `YUBIHSM_CONNECTOR_URL` in `.env`
- Validate credentials

### Model Drift Warning

```
WARNING: DRIFT DETECTED: KL=0.62
```

**Action**: Review drift metrics in Grafana, consider manual model retraining

---

## Security Checklist

- [ ] HSM enabled for production (`SASE_HSM_ENABLED=true`)
- [ ] Unique keys per environment (dev/staging/prod)
- [ ] 90-day key rotation configured
- [ ] Multi-party approval enabled for irreversible actions
- [ ] GeoIP/ASN enrichment active
- [ ] Prometheus metrics restricted (firewall `/metrics`)
- [ ] Grafana admin password changed
- [ ] Blockchain anchoring configured (optional)
- [ ] Audit logs write-protected
- [ ] Triumvirate authorization integrated

---

## Production Deployment

### Recommended Architecture

```
┌─────────────────────────────────────────────────┐
│              Load Balancer (WAF)                │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐     ┌────────▼───────┐
│  SASE Node 1   │     │  SASE Node 2   │
│   (Leader)     │◄────┤  (Follower)    │
└───────┬────────┘     └────────┬───────┘
        │                       │
        └───────────┬───────────┘
                    │
           ┌────────▼──────────┐
           │   SASE Node 3     │
           │   (Follower)      │
           └───────────────────┘
                    │
        ┌───────────┴────────────┐
        │                        │
┌───────▼────────┐    ┌──────────▼──────┐
│  Prometheus    │    │   EvidenceVault  │
│  + Grafana     │    │   (HSM-backed)   │
└────────────────┘    └──────────────────┘
```

### Resource Requirements

**Per Node**:

- CPU: 4 cores
- RAM: 8GB
- Disk: 100GB SSD (for event storage)
- Network: 1GB/s

**Observability**:

- Prometheus: 2 cores, 4GB RAM
- Grafana: 1 core, 2GB RAM

### Scaling

- **Vertical**: Increase node resources for higher throughput
- **Horizontal**: Add nodes to cluster (maintain odd number for Raft)
- **Edge**: Deploy at network edge for geo-distributed telemetry

---

## Next Steps

1. ✅ Complete integration testing
2. ✅ Configure external services (GeoIP, HSM)
3. ✅ Deploy observability stack
4. **TODO**: Create unit tests for each layer
5. **TODO**: Perform failure mode testing
6. **TODO**: Conduct security audit
7. **TODO**: Production deployment to staging

---

## Support & Documentation

- **Full Implementation**: [sase_walkthrough.md](file:///C:/Users/Quencher/.gemini/antigravity/brain/5e337573-fd3c-4a9f-8c0c-32d2ba062217/sase_walkthrough.md)
- **SASEarch Specification**: [spec_omega.md](file:///C:/Users/Quencher/.gemini/antigravity/brain/5e337573-fd3c-4a9f-8c0c-32d2ba062217/spec_omega.md)
- **Cerberus Integration**: [CERBERUS_INTEGRATION.md](file:///c:/Users/Quencher/.gemini/antigravity/scratch/sovereign-repos/Project-AI/security/CERBERUS_INTEGRATION.md)
