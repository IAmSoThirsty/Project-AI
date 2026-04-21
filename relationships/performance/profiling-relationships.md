# Profiling System Relationships

**System ID:** PERF-003  
**Category:** Performance Measurement & Analysis  
**Layer:** Observability  
**Status:** Production

## Overview

Profiling is the systematic measurement and analysis of application performance characteristics, providing the data foundation for all optimization decisions. It identifies bottlenecks, resource usage patterns, and performance regressions.

---

## Upstream Dependencies

### Application Instrumentation
- **Code Instrumentation** → Profiling Data
  - Function call timing
  - Method entry/exit hooks
  - Custom performance markers
  - Distributed tracing points

### System Metrics
- **OS-Level Metrics** → System Profiling
  - CPU utilization per process
  - Memory allocation/deallocation
  - Disk I/O operations
  - Network traffic patterns

### Performance Events
- **Runtime Events** → Event Profiling
  - Garbage collection pauses
  - Thread context switches
  - Lock contention events
  - Page faults

---

## Downstream Consumers

### Optimization Systems
- **All Performance Systems** ← Profiling Data
  - Caching (hit/miss rates, latency)
  - Query Optimization (slow query log)
  - Load Balancing (server utilization)
  - Resource Management (memory/CPU usage)
  - Connection Pooling (pool saturation)
  - Lazy Loading (load timing)

### Monitoring & Alerting
- **Alerts** ← Threshold Violations
  - Performance degradation
  - Resource exhaustion
  - SLA breaches

### Development Workflow
- **Developers** ← Performance Reports
  - Bottleneck identification
  - Optimization opportunities
  - Regression detection

---

## Profiling Types & Techniques

### 1. CPU Profiling
**Purpose:** Identify where CPU time is spent

#### Sampling Profiler (Low Overhead)
```python
import cProfile
import pstats

# Profile execution
profiler = cProfile.Profile()
profiler.enable()

# Code to profile
result = expensive_function()

profiler.disable()

# Analyze results
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

**Output Analysis:**
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
  1000    2.450    0.002    5.120    0.005 query.py:45(execute_query)
  5000    1.200    0.000    1.200    0.000 validation.py:12(validate_input)
```

**Relationships:**
- → Optimization (identifies CPU bottlenecks)
- → Resource Management (CPU allocation)

#### Deterministic Profiler
```python
from line_profiler import LineProfiler

profiler = LineProfiler()
profiler.add_function(critical_function)
profiler.run('critical_function()')
profiler.print_stats()
```

**Line-by-Line Output:**
```
Line #      Hits         Time  Per Hit   % Time  Line Contents
    10         1       1000.0   1000.0     10.0      result = []
    11      1000     500000.0    500.0     50.0      for item in items:
    12      1000     400000.0    400.0     40.0          result.append(process(item))
```

**Relationships:** → Optimization (pinpoint exact bottleneck lines)

### 2. Memory Profiling
**Purpose:** Identify memory leaks, excessive allocation

#### Memory Usage Tracking
```python
import tracemalloc

tracemalloc.start()

# Code to profile
result = memory_intensive_function()

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f} MB")
print(f"Peak: {peak / 1024 / 1024:.1f} MB")

# Show top memory allocations
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)

tracemalloc.stop()
```

**Relationships:**
- → Resource Management (memory limits)
- → Caching (cache size tuning)
- → Lazy Loading (defer allocations)

#### Memory Growth Detection
```python
import psutil
import os

process = psutil.Process(os.getpid())

for i in range(100):
    perform_operation()
    mem_mb = process.memory_info().rss / 1024 / 1024
    print(f"Iteration {i}: {mem_mb:.1f} MB")
    
# Detect leaks: should plateau, not grow linearly
```

**Relationships:** → Resource Management (leak detection)

### 3. I/O Profiling
**Purpose:** Identify disk/network bottlenecks

#### Database Query Profiling
```python
import time
import logging

class QueryProfiler:
    def __init__(self):
        self.slow_query_threshold = 0.1  # 100ms
        
    def profile_query(self, query, params):
        start = time.perf_counter()
        result = self.db.execute(query, params)
        elapsed = time.perf_counter() - start
        
        if elapsed > self.slow_query_threshold:
            logging.warning(
                f"Slow query ({elapsed*1000:.1f}ms): {query[:100]}"
            )
            # Log to slow query log for analysis
            self.slow_query_log.append({
                'query': query,
                'duration': elapsed,
                'timestamp': time.time()
            })
        
        return result, elapsed
```

**Relationships:**
- → Query Optimization (slow query identification)
- → Caching (cache slow queries)
- → Connection Pooling (pool exhaustion detection)

#### Network I/O Profiling
```python
import time
from contextlib import contextmanager

@contextmanager
def network_profile(operation_name):
    start = time.perf_counter()
    bytes_sent_before = psutil.net_io_counters().bytes_sent
    bytes_recv_before = psutil.net_io_counters().bytes_recv
    
    yield
    
    elapsed = time.perf_counter() - start
    bytes_sent = psutil.net_io_counters().bytes_sent - bytes_sent_before
    bytes_recv = psutil.net_io_counters().bytes_recv - bytes_recv_before
    
    print(f"{operation_name}: {elapsed*1000:.1f}ms")
    print(f"  Sent: {bytes_sent/1024:.1f} KB")
    print(f"  Received: {bytes_recv/1024:.1f} KB")

# Usage
with network_profile("API Call"):
    response = requests.get("https://api.example.com/data")
```

**Relationships:**
- → Load Balancing (network saturation)
- → Caching (reduce network calls)
- → Lazy Loading (defer network operations)

### 4. Concurrency Profiling
**Purpose:** Identify thread contention, lock bottlenecks

#### Lock Contention Detection
```python
import threading
import time
from contextlib import contextmanager

class ProfiledLock:
    def __init__(self, name):
        self.lock = threading.Lock()
        self.name = name
        self.wait_times = []
        
    @contextmanager
    def acquire_profiled(self):
        start = time.perf_counter()
        acquired = self.lock.acquire(timeout=5)
        wait_time = time.perf_counter() - start
        
        if wait_time > 0.01:  # 10ms threshold
            self.wait_times.append(wait_time)
            logging.warning(f"Lock '{self.name}' wait: {wait_time*1000:.1f}ms")
        
        try:
            yield acquired
        finally:
            if acquired:
                self.lock.release()
    
    def report(self):
        if self.wait_times:
            avg = sum(self.wait_times) / len(self.wait_times)
            max_wait = max(self.wait_times)
            print(f"Lock '{self.name}':")
            print(f"  Contention events: {len(self.wait_times)}")
            print(f"  Avg wait: {avg*1000:.1f}ms")
            print(f"  Max wait: {max_wait*1000:.1f}ms")
```

**Relationships:**
- → Resource Management (lock-free alternatives)
- → Connection Pooling (pool lock contention)
- → Load Balancing (distribute to avoid contention)

### 5. Application Performance Monitoring (APM)
**Purpose:** End-to-end request tracing

#### Distributed Tracing
```python
import opentelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# Setup tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Add span processor
trace.get_tracer_provider().add_span_processor(
    SimpleSpanProcessor(ConsoleSpanExporter())
)

# Instrument code
@tracer.start_as_current_span("process_request")
def process_request(request):
    with tracer.start_as_current_span("validate_input"):
        validate(request)
    
    with tracer.start_as_current_span("fetch_data"):
        data = fetch_from_db(request.id)
    
    with tracer.start_as_current_span("transform"):
        result = transform(data)
    
    return result
```

**Trace Output:**
```
Span: process_request (500ms)
  └─ Span: validate_input (10ms)
  └─ Span: fetch_data (450ms)  ← BOTTLENECK
  └─ Span: transform (40ms)
```

**Relationships:**
- → All performance systems (comprehensive visibility)
- → Optimization (end-to-end bottleneck identification)

---

## Profiling Metrics & KPIs

### Performance Metrics
```python
class PerformanceMetrics:
    def __init__(self):
        self.metrics = {
            # Response time percentiles
            'response_time_p50': [],
            'response_time_p95': [],
            'response_time_p99': [],
            
            # Throughput
            'requests_per_second': 0,
            'transactions_per_second': 0,
            
            # Resource utilization
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_io_mb_per_sec': 0,
            
            # Error rates
            'error_rate': 0,
            'timeout_rate': 0,
            
            # Cache performance
            'cache_hit_rate': 0,
            'cache_miss_rate': 0,
            
            # Database performance
            'db_query_time_avg': 0,
            'db_connection_pool_usage': 0,
        }
    
    def calculate_percentiles(self, values):
        import numpy as np
        return {
            'p50': np.percentile(values, 50),
            'p95': np.percentile(values, 95),
            'p99': np.percentile(values, 99),
            'max': np.max(values),
        }
```

### SLA Monitoring
```python
class SLAMonitor:
    def __init__(self, sla_threshold_ms=500):
        self.sla_threshold = sla_threshold_ms / 1000
        self.requests = []
    
    def record_request(self, duration):
        self.requests.append(duration)
    
    def sla_compliance(self):
        """Calculate percentage of requests meeting SLA"""
        if not self.requests:
            return 100.0
        
        compliant = sum(1 for r in self.requests if r <= self.sla_threshold)
        return (compliant / len(self.requests)) * 100
    
    def report(self):
        compliance = self.sla_compliance()
        print(f"SLA Compliance: {compliance:.2f}%")
        
        if compliance < 95:
            print("⚠️ SLA VIOLATION: Below 95% target")
            # Trigger optimization workflow
```

**Relationships:**
- → Optimization (SLA violations trigger optimization)
- → All performance systems (contribute to SLA)

---

## Profiling-Driven Workflows

### 1. Baseline Establishment
```python
def establish_baseline(workload_function, iterations=100):
    """Run workload to establish performance baseline"""
    metrics = {
        'execution_times': [],
        'memory_usage': [],
        'cpu_usage': [],
    }
    
    for i in range(iterations):
        start = time.perf_counter()
        mem_before = tracemalloc.get_traced_memory()[0]
        
        workload_function()
        
        elapsed = time.perf_counter() - start
        mem_after = tracemalloc.get_traced_memory()[0]
        
        metrics['execution_times'].append(elapsed)
        metrics['memory_usage'].append(mem_after - mem_before)
    
    return {
        'avg_time': np.mean(metrics['execution_times']),
        'p95_time': np.percentile(metrics['execution_times'], 95),
        'avg_memory': np.mean(metrics['memory_usage']),
    }
```

### 2. Regression Detection
```python
class PerformanceRegression:
    def __init__(self, baseline_metrics):
        self.baseline = baseline_metrics
        self.threshold_percent = 10  # 10% regression threshold
    
    def detect_regression(self, current_metrics):
        regressions = []
        
        for metric, baseline_value in self.baseline.items():
            current_value = current_metrics.get(metric)
            if current_value is None:
                continue
            
            # Calculate percent change
            percent_change = ((current_value - baseline_value) / baseline_value) * 100
            
            if percent_change > self.threshold_percent:
                regressions.append({
                    'metric': metric,
                    'baseline': baseline_value,
                    'current': current_value,
                    'regression_percent': percent_change
                })
        
        return regressions
    
    def report_regressions(self, regressions):
        if not regressions:
            print("✅ No performance regressions detected")
            return
        
        print("❌ PERFORMANCE REGRESSIONS DETECTED:")
        for reg in regressions:
            print(f"  {reg['metric']}: {reg['regression_percent']:.1f}% slower")
            print(f"    Baseline: {reg['baseline']:.3f}")
            print(f"    Current:  {reg['current']:.3f}")
```

**Relationships:**
- → CI/CD Pipeline (automated regression tests)
- → Optimization (regression triggers optimization)

### 3. Continuous Profiling
```python
class ContinuousProfiler:
    def __init__(self, sample_rate=0.01):
        """Sample 1% of requests for profiling"""
        self.sample_rate = sample_rate
        self.profiles = []
    
    def should_profile(self):
        import random
        return random.random() < self.sample_rate
    
    @contextmanager
    def profile_request(self, request_id):
        if not self.should_profile():
            yield None
            return
        
        profiler = cProfile.Profile()
        profiler.enable()
        
        start = time.perf_counter()
        yield profiler
        elapsed = time.perf_counter() - start
        
        profiler.disable()
        
        # Store profile for analysis
        self.profiles.append({
            'request_id': request_id,
            'duration': elapsed,
            'profile': profiler,
            'timestamp': time.time()
        })

# Usage
profiler = ContinuousProfiler(sample_rate=0.01)

def handle_request(request):
    with profiler.profile_request(request.id) as profile:
        return process_request(request)
```

**Relationships:**
- → Production monitoring (low overhead)
- → Optimization (real-world performance data)

---

## Cross-System Profiling Integration

### Cache Performance Profiling
```python
class CacheProfiler:
    def __init__(self, cache):
        self.cache = cache
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'hit_latencies': [],
            'miss_latencies': [],
        }
    
    def get(self, key):
        start = time.perf_counter()
        value = self.cache.get(key)
        elapsed = time.perf_counter() - start
        
        if value is not None:
            self.metrics['hits'] += 1
            self.metrics['hit_latencies'].append(elapsed)
        else:
            self.metrics['misses'] += 1
            self.metrics['miss_latencies'].append(elapsed)
        
        return value
    
    def report(self):
        total = self.metrics['hits'] + self.metrics['misses']
        hit_rate = (self.metrics['hits'] / total * 100) if total > 0 else 0
        
        print(f"Cache Hit Rate: {hit_rate:.2f}%")
        print(f"Avg Hit Latency: {np.mean(self.metrics['hit_latencies'])*1000:.2f}ms")
        print(f"Avg Miss Latency: {np.mean(self.metrics['miss_latencies'])*1000:.2f}ms")
```

**Relationships:** → Caching (performance tuning)

### Database Query Profiling
```python
class DatabaseProfiler:
    def __init__(self):
        self.slow_queries = []
        self.query_counts = {}
        
    def profile_query(self, query, params):
        start = time.perf_counter()
        result = db.execute(query, params)
        elapsed = time.perf_counter() - start
        
        # Track query frequency
        query_hash = hash(query)
        self.query_counts[query_hash] = self.query_counts.get(query_hash, 0) + 1
        
        # Track slow queries
        if elapsed > 0.1:  # 100ms
            self.slow_queries.append({
                'query': query,
                'duration': elapsed,
                'count': self.query_counts[query_hash]
            })
        
        return result
    
    def optimization_candidates(self):
        """Identify queries needing optimization"""
        # Sort by total impact (duration * frequency)
        candidates = sorted(
            self.slow_queries,
            key=lambda q: q['duration'] * q['count'],
            reverse=True
        )
        return candidates[:10]  # Top 10
```

**Relationships:** → Query Optimization (identifies optimization targets)

---

## Profiling Tools & Technologies

### Python Profiling Stack
| Tool | Purpose | Overhead |
|------|---------|----------|
| cProfile | CPU profiling | Low (2-5%) |
| line_profiler | Line-by-line CPU | Medium (10-50%) |
| memory_profiler | Memory usage | High (50-100%) |
| tracemalloc | Memory allocation tracking | Low (5-10%) |
| py-spy | Sampling profiler (production) | Very Low (<1%) |
| Pyinstrument | Statistical profiler | Low (2-5%) |

### APM Tools
| Tool | Features | Use Case |
|------|----------|----------|
| New Relic | Full-stack APM | Production monitoring |
| Datadog | Infrastructure + APM | Multi-service apps |
| Prometheus | Metrics collection | Time-series data |
| Jaeger | Distributed tracing | Microservices |
| Grafana | Visualization | Dashboards |

### Database Profiling
| Tool | Purpose |
|------|---------|
| EXPLAIN/EXPLAIN ANALYZE | Query execution plans |
| pg_stat_statements | PostgreSQL query stats |
| MySQL slow query log | Slow query tracking |
| Database-specific profilers | Vendor tools |

---

## Profiling Patterns

### 1. Performance Testing Pattern
```python
def performance_test(function, workload, iterations=1000):
    """Comprehensive performance test"""
    results = {
        'execution_times': [],
        'memory_deltas': [],
        'cpu_times': [],
    }
    
    for i in range(iterations):
        # CPU time
        cpu_start = time.process_time()
        
        # Memory
        tracemalloc.start()
        mem_start = tracemalloc.get_traced_memory()[0]
        
        # Wall time
        wall_start = time.perf_counter()
        
        # Execute
        function(workload)
        
        # Collect metrics
        wall_elapsed = time.perf_counter() - wall_start
        cpu_elapsed = time.process_time() - cpu_start
        mem_end = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        
        results['execution_times'].append(wall_elapsed)
        results['cpu_times'].append(cpu_elapsed)
        results['memory_deltas'].append(mem_end - mem_start)
    
    return {
        'wall_time_avg': np.mean(results['execution_times']),
        'wall_time_p95': np.percentile(results['execution_times'], 95),
        'cpu_time_avg': np.mean(results['cpu_times']),
        'memory_avg': np.mean(results['memory_deltas']),
    }
```

### 2. Load Testing Pattern
```python
import concurrent.futures
import time

def load_test(endpoint, concurrent_users=10, duration_seconds=60):
    """Simulate concurrent load"""
    results = []
    start_time = time.time()
    
    def user_session():
        session_results = []
        while time.time() - start_time < duration_seconds:
            req_start = time.perf_counter()
            try:
                response = endpoint()
                elapsed = time.perf_counter() - req_start
                session_results.append({
                    'success': True,
                    'duration': elapsed
                })
            except Exception as e:
                session_results.append({
                    'success': False,
                    'error': str(e)
                })
        return session_results
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(user_session) for _ in range(concurrent_users)]
        for future in concurrent.futures.as_completed(futures):
            results.extend(future.result())
    
    # Analyze results
    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]
    
    return {
        'total_requests': len(results),
        'successful': len(successful),
        'failed': len(failed),
        'success_rate': len(successful) / len(results) * 100,
        'avg_response_time': np.mean([r['duration'] for r in successful]),
        'p95_response_time': np.percentile([r['duration'] for r in successful], 95),
        'requests_per_second': len(results) / duration_seconds,
    }
```

**Relationships:**
- → Load Balancing (capacity planning)
- → Resource Management (resource requirements)
- → All performance systems (stress testing)

---

## Profiling Checklist

- [ ] Establish performance baseline before optimization
- [ ] Profile in production-like environment
- [ ] Use statistical sampling for production profiling
- [ ] Monitor all critical performance metrics (CPU, memory, I/O, network)
- [ ] Set up automated performance regression detection
- [ ] Create profiling dashboards for visibility
- [ ] Profile database queries separately
- [ ] Track cache hit/miss rates
- [ ] Monitor connection pool utilization
- [ ] Set up distributed tracing for microservices
- [ ] Define SLAs and monitor compliance
- [ ] Integrate profiling into CI/CD pipeline
- [ ] Review profiling data weekly
- [ ] Archive profiling data for trend analysis

---

## Related Documentation
- Optimization: `optimization-relationships.md`
- Caching: `caching-relationships.md`
- Query Optimization: `query-optimization-relationships.md`
- Resource Management: `resource-management-relationships.md`
