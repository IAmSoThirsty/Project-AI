# Data Plane Performance Benchmarks - Results Template

## Test Environment
- **Date**: [Date of test]
- **Hardware**: [CPU, RAM, Network specs]
- **Cluster Size**: [Number of nodes]
- **Configuration**: [Kafka/NATS, Redis, MinIO settings]

## Benchmark Results

### 1. Small Messages (1KB)
- **Throughput**: X Mbps
- **Operations/sec**: X ops
- **Average Latency**: X ms
- **P99 Latency**: X ms
- **Target**: > 10,000 ops/sec, < 10ms p99

### 2. Large Messages (10MB)
- **Throughput**: X Mbps
- **Operations/sec**: X ops
- **Average Latency**: X ms
- **P99 Latency**: X ms
- **Target**: > 1 GB/s throughput

### 3. Cache Operations
- **Operations/sec**: X ops
- **Hit Rate**: X%
- **Average Latency**: X μs
- **P99 Latency**: X μs
- **Target**: > 100,000 ops/sec, > 80% hit rate

### 4. Storage Upload (5MB files)
- **Throughput**: X Mbps
- **Average Latency**: X ms
- **P99 Latency**: X ms
- **Target**: > 500 MB/s

### 5. Storage Download (5MB files)
- **Throughput**: X Mbps
- **Cache Hit Rate**: X%
- **Average Latency**: X ms
- **P99 Latency**: X ms
- **Target**: > 1 GB/s with caching

### 6. Mixed Workload
- **Aggregate Throughput**: X Mbps
- **Operations/sec**: X ops
- **Average Latency**: X ms
- **P99 Latency**: X ms

## RDMA Performance (if enabled)

### Direct Memory Transfer
- **Latency**: X μs
- **Throughput**: X Mbps
- **CPU Utilization**: X%
- **Target**: < 100μs latency

## Aggregate Performance

**Total Throughput**: X GB/s
**Target Achievement**: X% of 10 GB/s target

## Resource Utilization

### Kafka
- CPU: X%
- Memory: X GB
- Network I/O: X Mbps

### MinIO
- CPU: X%
- Memory: X GB
- Disk I/O: X MB/s
- Network I/O: X Mbps

### Redis
- CPU: X%
- Memory: X GB
- Network I/O: X Mbps
- Hit Rate: X%

## Bottlenecks Identified
1. [List any identified bottlenecks]
2. [Suggestions for optimization]

## Recommendations
- [Scaling recommendations]
- [Configuration tuning suggestions]
- [Hardware recommendations]

## Notes
[Any additional notes or observations]
