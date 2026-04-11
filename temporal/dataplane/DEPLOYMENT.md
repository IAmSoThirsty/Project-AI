# Data Plane Deployment Guide

## Quick Start (Local Development)

### 1. Start Infrastructure

```bash
# Start all services with Docker Compose
cd temporal/dataplane
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration if needed
# Default values work for local Docker setup
```

### 4. Run Example

```python
python examples/basic_usage.py
```

## Production Deployment (Kubernetes)

### Prerequisites

- Kubernetes cluster (v1.25+)
- kubectl configured
- At least 100GB storage per node
- Persistent volume provisioner

### Deploy

```bash
# Apply all manifests
cd temporal/dataplane/k8s
kubectl apply -f .

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod -l app=kafka -n dataplane --timeout=300s
kubectl wait --for=condition=ready pod -l app=minio -n dataplane --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n dataplane --timeout=300s

# Verify deployment
kubectl get pods -n dataplane
```

### Access Services

```bash
# MinIO Console
kubectl port-forward -n dataplane svc/minio-service 9001:9001
# Open http://localhost:9001 (minioadmin/minioadmin)

# Grafana
kubectl port-forward -n dataplane svc/grafana 3000:3000
# Open http://localhost:3000 (admin/admin)

# Kafka
kubectl run -n dataplane kafka-client --rm -it \
  --image=confluentinc/cp-kafka:7.5.0 -- bash
```

## Configuration

### Message Queue Selection

Choose between Kafka (durable, ordered) and NATS (fast, lightweight):

```bash
# Use Kafka (default)
export MESSAGE_QUEUE_TYPE=kafka
export KAFKA_BROKERS=localhost:9092

# Use NATS
export MESSAGE_QUEUE_TYPE=nats
export NATS_URL=nats://localhost:4222
```

### RDMA Support (Optional)

For ultra-low latency in RDMA-capable clusters:

```bash
export ENABLE_RDMA=true
export RDMA_DEVICE=mlx5_0  # Your Mellanox NIC device
```

**Requirements:**
- RDMA-capable NICs (Mellanox ConnectX-5 or newer)
- RoCE v2 enabled
- `pyverbs` Python package installed

### Performance Tuning

```bash
# Large message threshold (default: 1MB)
export LARGE_MESSAGE_THRESHOLD=1048576

# Cache TTL (seconds)
export REDIS_DEFAULT_TTL=3600

# Kafka batch settings
export KAFKA_LINGER_MS=10
export KAFKA_BATCH_SIZE=16384
```

## Monitoring

### Prometheus Metrics

Data plane exposes metrics at `:9090/metrics`:

- `dataplane_messages_sent_total`
- `dataplane_messages_received_total`
- `dataplane_bytes_transferred_total`
- `dataplane_latency_seconds`
- `dataplane_cache_hits_total`
- `dataplane_cache_misses_total`

### Grafana Dashboards

Pre-built dashboards available:

1. **Message Queue Dashboard**: Kafka/NATS throughput and lag
2. **Storage Dashboard**: MinIO bandwidth and usage
3. **Cache Dashboard**: Redis hit rates and memory
4. **RDMA Dashboard**: RDMA transfer statistics

## Benchmarks

### Run Full Benchmarks

```bash
python temporal/dataplane/benchmarks/run_all.py
```

### Quick Benchmarks (reduced iterations)

```bash
python temporal/dataplane/benchmarks/run_all.py --quick
```

### Expected Results

| Metric | Target | Typical |
|--------|--------|---------|
| Small Message Latency (p99) | < 10ms | 5-8ms |
| Large Message Throughput | > 1 GB/s | 2-5 GB/s |
| Cache Operations | > 100k ops/sec | 150k-300k ops/sec |
| Storage Upload | > 500 MB/s | 800 MB/s - 2 GB/s |
| Aggregate Throughput | 10 GB/s | 5-15 GB/s |

*Note: Results vary based on hardware, network, and cluster configuration*

## Troubleshooting

### Kafka Connection Issues

```bash
# Check Kafka logs
docker-compose logs kafka

# Verify broker is accessible
docker exec -it dataplane-kafka-1 kafka-broker-api-versions \
  --bootstrap-server localhost:9092
```

### MinIO Access Issues

```bash
# Check MinIO logs
docker-compose logs minio

# Test with MinIO client
docker run --rm -it --network dataplane_default minio/mc \
  alias set myminio http://minio:9000 minioadmin minioadmin
```

### Redis Connection Issues

```bash
# Test Redis connection
docker exec -it dataplane-redis-1 redis-cli ping

# Check memory usage
docker exec -it dataplane-redis-1 redis-cli info memory
```

### RDMA Not Working

1. Verify NIC supports RDMA:
   ```bash
   ibv_devices
   ibv_devinfo
   ```

2. Check RoCE is enabled:
   ```bash
   show_gids
   ```

3. Verify pyverbs installation:
   ```bash
   python -c "import pyverbs; print('OK')"
   ```

## Cleanup

### Local (Docker)

```bash
cd temporal/dataplane
docker-compose down -v  # Remove containers and volumes
```

### Kubernetes

```bash
kubectl delete namespace dataplane
```

## Security Considerations

1. **TLS/mTLS**: Enable encryption for production
2. **Authentication**: Configure SASL for Kafka, credentials for MinIO
3. **Network Policies**: Isolate data plane namespace
4. **Secrets Management**: Use Kubernetes secrets, not plaintext
5. **RBAC**: Limit access to data plane resources

## Scaling

### Horizontal Scaling

```bash
# Scale Kafka brokers
kubectl scale statefulset kafka -n dataplane --replicas=5

# Scale MinIO nodes
kubectl scale statefulset minio -n dataplane --replicas=8

# Scale Redis replicas
kubectl scale statefulset redis -n dataplane --replicas=5
```

### Vertical Scaling

Edit resource limits in Kubernetes manifests:

```yaml
resources:
  requests:
    memory: "8Gi"
    cpu: "4000m"
  limits:
    memory: "16Gi"
    cpu: "8000m"
```

## Migration

### From Development to Production

1. Export data from local MinIO
2. Import to production S3/MinIO
3. Update configuration
4. Verify connectivity
5. Run benchmarks to validate performance

## Support

For issues or questions:
- Check logs: `docker-compose logs` or `kubectl logs`
- Review metrics in Grafana
- Run diagnostics: `python temporal/dataplane/benchmarks/run_all.py --verbose`
