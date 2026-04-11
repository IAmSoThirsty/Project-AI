# Kubernetes Deployment for Data Plane

Deploy all data plane components to Kubernetes cluster.

## Prerequisites
- Kubernetes cluster (v1.25+)
- kubectl configured
- Persistent volume provisioner

## Quick Deploy
```bash
kubectl apply -f .
```

## Components
- Kafka cluster (3 replicas)
- NATS cluster (3 replicas)
- MinIO distributed storage (4 nodes)
- Redis with Sentinel (HA)
- Prometheus monitoring
- Grafana dashboards

## Access Services
```bash
# Port forward MinIO console
kubectl port-forward -n dataplane svc/minio-service 9001:9001

# Port forward Grafana
kubectl port-forward -n dataplane svc/grafana 3000:3000

# Access Kafka
kubectl run -n dataplane kafka-client --rm -it --image=confluentinc/cp-kafka:7.5.0 -- bash
```
