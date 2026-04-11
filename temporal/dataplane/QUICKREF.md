# Data Plane Quick Reference

## 🚀 Quick Commands

### Local Development
```bash
# Start all services
cd temporal/dataplane && docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f [service]

# Stop all
docker-compose down

# Clean everything
docker-compose down -v
```

### Production (Kubernetes)
```bash
# Deploy
kubectl apply -f temporal/dataplane/k8s/

# Check pods
kubectl get pods -n dataplane

# Check services
kubectl get svc -n dataplane

# View logs
kubectl logs -f <pod-name> -n dataplane

# Scale
kubectl scale statefulset kafka --replicas=5 -n dataplane

# Delete
kubectl delete namespace dataplane
```

## 📝 Environment Variables

```bash
# Required
MESSAGE_QUEUE_TYPE=kafka          # or 'nats'
KAFKA_BROKERS=localhost:9092
MINIO_ENDPOINT=localhost:9000
REDIS_URL=redis://localhost:6379

# Optional
ENABLE_RDMA=false
LARGE_MESSAGE_THRESHOLD=1048576
ENABLE_COMPRESSION=true
```

## 💻 Python Usage

```python
from temporal.dataplane import DataPlaneClient

# Initialize
client = DataPlaneClient()
await client.connect()

# Send message
await client.send_message("topic", b"data", "agent-id")

# Upload artifact
key = await client.upload_artifact("file.bin", data)

# Cache
await client.cache_set("key", b"value", ttl=3600)
value = await client.cache_get("key")

# Cleanup
await client.disconnect()
```

## 🔍 Monitoring URLs

```bash
# MinIO Console (local)
http://localhost:9001  # minioadmin / minioadmin

# Prometheus (local)
http://localhost:9090

# Grafana (local)
http://localhost:3000  # admin / admin

# NATS Monitoring (local)
http://localhost:8222

# Redis Commander (local)
http://localhost:8081
```

## 📊 Benchmarking

```bash
# Full benchmarks
python temporal/dataplane/benchmarks/run_all.py

# Quick test
python temporal/dataplane/benchmarks/run_all.py --quick

# Custom output
python temporal/dataplane/benchmarks/run_all.py --output my_results.json
```

## 🐛 Troubleshooting

```bash
# Kafka not starting?
docker-compose logs zookeeper kafka

# MinIO access denied?
docker exec -it dataplane-minio-1 mc admin info local

# Redis connection refused?
docker exec -it dataplane-redis-1 redis-cli ping

# Out of disk space?
docker system prune -a --volumes
```

## 📦 Dependencies

```bash
# Install
pip install -r temporal/dataplane/requirements.txt

# Upgrade
pip install --upgrade -r temporal/dataplane/requirements.txt
```

## 🧪 Testing

```bash
# Run tests
cd temporal/dataplane
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test
pytest tests/test_dataplane.py::TestDataPlaneClient::test_send_small_message
```

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `.env.example` | Configuration template |
| `docker-compose.yml` | Local deployment |
| `k8s/*.yaml` | Kubernetes manifests |
| `prometheus.yml` | Metrics config |
| `requirements.txt` | Python deps |

## 📈 Performance Targets

| Metric | Target |
|--------|--------|
| Small msg latency (p99) | < 10ms |
| Large msg throughput | > 1 GB/s |
| Cache ops/sec | > 100k |
| Storage bandwidth | > 500 MB/s |
| Aggregate throughput | 10 GB/s |

## 🛡️ Security Checklist

- [ ] Enable TLS for all services
- [ ] Configure SASL for Kafka
- [ ] Set strong MinIO credentials
- [ ] Enable Redis AUTH
- [ ] Use Kubernetes secrets
- [ ] Apply network policies
- [ ] Enable audit logging
- [ ] Rotate credentials regularly

## 📚 Documentation

- `README.md` - Overview
- `DEPLOYMENT.md` - Deployment guide
- `ARCHITECTURE.md` - Architecture details
- `COMPLETION_SUMMARY.md` - Implementation summary

## 🆘 Support

1. Check logs
2. Review metrics in Grafana
3. Run benchmarks with `--verbose`
4. Check GitHub issues
5. Review deployment guide

---
**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅
