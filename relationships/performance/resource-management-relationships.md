# Resource Management System Relationships

**System ID:** PERF-005  
**Category:** Infrastructure Management  
**Layer:** System/Infrastructure  
**Status:** Production

## Overview

Resource Management encompasses the strategic allocation, monitoring, and optimization of system resources (CPU, memory, disk, network) to ensure application stability, performance, and cost-effectiveness.

---

## Upstream Dependencies

### System Resources
- **Operating System** → Resource Allocation
  - CPU cores and scheduling
  - RAM allocation and virtual memory
  - Disk I/O bandwidth
  - Network interfaces and bandwidth

### Application Demands
- **Workload Patterns** → Resource Requirements
  - Request rate and concurrency
  - Data processing volume
  - Computation complexity
  - Storage needs

### Infrastructure Limits
- **Hardware Constraints** → Maximum Capacity
  - Physical server specifications
  - Cloud instance types
  - Network bandwidth limits
  - Storage IOPS caps

---

## Downstream Impacts

### All Performance Systems
- **Caching** ← Memory Allocation
  - Cache size limits
  - Eviction policies under pressure
  
- **Connection Pooling** ← Connection Limits
  - Max pool size
  - Connection timeout settings
  
- **Load Balancing** ← Capacity-Based Routing
  - Server weight assignment
  - Auto-scaling triggers
  
- **Query Optimization** ← Resource Budgets
  - Query timeout limits
  - Result set size caps
  
- **Lazy Loading** ← Memory Pressure
  - Deferred loading triggers
  - Unload unused resources

---

## Resource Types

### 1. CPU Management

#### CPU Allocation Strategies
```python
import os
import multiprocessing
import psutil

class CPUManager:
    def __init__(self):
        self.total_cores = multiprocessing.cpu_count()
        self.physical_cores = psutil.cpu_count(logical=False)
        
    def recommend_worker_count(self, workload_type='cpu_bound'):
        """Recommend optimal worker count based on workload"""
        if workload_type == 'cpu_bound':
            # CPU-bound: use physical cores to avoid context switching
            return self.physical_cores
        elif workload_type == 'io_bound':
            # I/O-bound: can use more workers than cores
            return self.total_cores * 2
        elif workload_type == 'mixed':
            return self.total_cores
        
    def set_cpu_affinity(self, process, cores):
        """Pin process to specific CPU cores"""
        p = psutil.Process(process.pid)
        p.cpu_affinity(cores)
        
    def get_cpu_usage(self):
        """Monitor CPU utilization"""
        return {
            'percent': psutil.cpu_percent(interval=1, percpu=True),
            'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None,
            'context_switches': psutil.cpu_stats().ctx_switches,
        }

# Usage
cpu_mgr = CPUManager()

# Optimize worker pool size
worker_count = cpu_mgr.recommend_worker_count('io_bound')
executor = ThreadPoolExecutor(max_workers=worker_count)

# Monitor CPU usage
usage = cpu_mgr.get_cpu_usage()
if max(usage['percent']) > 90:
    print("⚠️ High CPU usage detected")
```

**Relationships:**
- → Optimization (worker pool sizing)
- → Load Balancing (CPU-based routing)
- ← Profiling (CPU usage monitoring)

#### CPU Throttling & Rate Limiting
```python
import time
from threading import Semaphore

class CPUThrottler:
    def __init__(self, max_cpu_percent=80):
        self.max_cpu_percent = max_cpu_percent
        self.check_interval = 1.0
        
    def throttle_if_needed(self):
        """Slow down execution if CPU is too high"""
        current_cpu = psutil.cpu_percent(interval=0.1)
        
        if current_cpu > self.max_cpu_percent:
            # Calculate sleep time to reduce CPU
            overage = current_cpu - self.max_cpu_percent
            sleep_time = (overage / 100) * self.check_interval
            time.sleep(sleep_time)
            return True
        return False

# Usage in processing loop
throttler = CPUThrottler(max_cpu_percent=80)

for item in large_dataset:
    process(item)
    throttler.throttle_if_needed()
```

**Relationships:**
- → Optimization (prevents CPU exhaustion)
- → Load Balancing (backpressure signaling)

### 2. Memory Management

#### Memory Allocation Tracking
```python
import tracemalloc
import gc

class MemoryManager:
    def __init__(self, max_memory_mb=4096):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        tracemalloc.start()
        
    def get_current_usage(self):
        """Get current memory usage"""
        process = psutil.Process()
        return {
            'rss': process.memory_info().rss,  # Resident set size
            'vms': process.memory_info().vms,  # Virtual memory size
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available,
        }
    
    def is_memory_pressure(self, threshold_percent=85):
        """Check if memory usage is too high"""
        usage = self.get_current_usage()
        return usage['percent'] > threshold_percent
    
    def emergency_cleanup(self):
        """Free memory in emergency situations"""
        print("⚠️ Memory pressure detected, performing cleanup...")
        
        # Force garbage collection
        collected = gc.collect()
        print(f"  Collected {collected} objects")
        
        # Clear caches (application-specific)
        if hasattr(self, 'cache'):
            cleared = self.cache.clear()
            print(f"  Cleared {cleared} cache entries")
        
        return self.get_current_usage()
    
    def get_top_memory_allocations(self, limit=10):
        """Identify memory hotspots"""
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        print(f"Top {limit} memory allocations:")
        for stat in top_stats[:limit]:
            print(f"  {stat}")
        
        return top_stats[:limit]

# Usage
mem_mgr = MemoryManager(max_memory_mb=4096)

# Monitor in processing loop
while processing:
    if mem_mgr.is_memory_pressure():
        mem_mgr.emergency_cleanup()
    
    process_batch()
```

**Relationships:**
- → Caching (cache size limits, eviction under pressure)
- → Lazy Loading (defer loading when memory tight)
- ← Profiling (memory usage monitoring)

#### Memory Pooling (Object Reuse)
```python
from queue import Queue
import threading

class ObjectPool:
    """Reuse expensive objects to reduce allocation overhead"""
    def __init__(self, factory, max_size=100):
        self.factory = factory  # Function to create new objects
        self.pool = Queue(maxsize=max_size)
        self.max_size = max_size
        self.created_count = 0
        self.reuse_count = 0
        self.lock = threading.Lock()
        
    def acquire(self):
        """Get object from pool or create new one"""
        try:
            obj = self.pool.get_nowait()
            self.reuse_count += 1
            return obj
        except:
            with self.lock:
                if self.created_count < self.max_size:
                    obj = self.factory()
                    self.created_count += 1
                    return obj
                else:
                    # Pool exhausted, wait for object
                    return self.pool.get()
    
    def release(self, obj):
        """Return object to pool"""
        # Reset object state before returning
        if hasattr(obj, 'reset'):
            obj.reset()
        
        try:
            self.pool.put_nowait(obj)
        except:
            # Pool full, discard object
            pass
    
    def stats(self):
        return {
            'pool_size': self.pool.qsize(),
            'max_size': self.max_size,
            'created': self.created_count,
            'reuse_rate': self.reuse_count / max(self.created_count, 1),
        }

# Usage
def create_database_connection():
    return DatabaseConnection(config)

conn_pool = ObjectPool(create_database_connection, max_size=50)

# Use connection
conn = conn_pool.acquire()
try:
    result = conn.execute(query)
finally:
    conn_pool.release(conn)

print(conn_pool.stats())  # Monitor pool efficiency
```

**Relationships:**
- → Connection Pooling (connection reuse pattern)
- → Optimization (reduce allocation overhead)

### 3. Disk I/O Management

#### I/O Throttling
```python
import time

class IOThrottler:
    def __init__(self, max_iops=1000, max_bandwidth_mbps=100):
        self.max_iops = max_iops
        self.max_bytes_per_second = max_bandwidth_mbps * 1024 * 1024
        
        self.operation_count = 0
        self.bytes_transferred = 0
        self.window_start = time.time()
        self.window_duration = 1.0  # 1 second window
        
    def throttle_operation(self, bytes_size):
        """Throttle if exceeding limits"""
        current_time = time.time()
        elapsed = current_time - self.window_start
        
        # Reset window if elapsed
        if elapsed >= self.window_duration:
            self.operation_count = 0
            self.bytes_transferred = 0
            self.window_start = current_time
            return
        
        # Check IOPS limit
        if self.operation_count >= self.max_iops:
            sleep_time = self.window_duration - elapsed
            time.sleep(sleep_time)
            self.operation_count = 0
            self.bytes_transferred = 0
            self.window_start = time.time()
        
        # Check bandwidth limit
        if self.bytes_transferred + bytes_size > self.max_bytes_per_second:
            sleep_time = self.window_duration - elapsed
            time.sleep(sleep_time)
            self.operation_count = 0
            self.bytes_transferred = 0
            self.window_start = time.time()
        
        self.operation_count += 1
        self.bytes_transferred += bytes_size

# Usage
throttler = IOThrottler(max_iops=1000, max_bandwidth_mbps=100)

for file in files_to_process:
    file_size = os.path.getsize(file)
    throttler.throttle_operation(file_size)
    process_file(file)
```

**Relationships:**
- → Optimization (prevent I/O saturation)
- → Load Balancing (distribute I/O across devices)

#### Buffered I/O
```python
class BufferedWriter:
    def __init__(self, filename, buffer_size_kb=64):
        self.filename = filename
        self.buffer_size = buffer_size_kb * 1024
        self.buffer = []
        self.buffer_bytes = 0
        
    def write(self, data):
        """Buffer writes to reduce I/O operations"""
        self.buffer.append(data)
        self.buffer_bytes += len(data)
        
        if self.buffer_bytes >= self.buffer_size:
            self.flush()
    
    def flush(self):
        """Write buffer to disk"""
        if self.buffer:
            with open(self.filename, 'ab') as f:
                for data in self.buffer:
                    f.write(data.encode())
            
            self.buffer = []
            self.buffer_bytes = 0
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.flush()

# Usage: Reduces 10,000 I/O ops to ~157 ops (64KB buffer)
with BufferedWriter('output.txt', buffer_size_kb=64) as writer:
    for i in range(10000):
        writer.write(f"Line {i}\n")
```

**Relationships:**
- → Optimization (batch I/O operations)
- → Profiling (I/O operation reduction)

### 4. Network Resource Management

#### Bandwidth Monitoring
```python
import psutil

class NetworkMonitor:
    def __init__(self):
        self.baseline = psutil.net_io_counters()
        
    def get_current_usage(self):
        """Get network usage since baseline"""
        current = psutil.net_io_counters()
        
        return {
            'bytes_sent': current.bytes_sent - self.baseline.bytes_sent,
            'bytes_recv': current.bytes_recv - self.baseline.bytes_recv,
            'packets_sent': current.packets_sent - self.baseline.packets_sent,
            'packets_recv': current.packets_recv - self.baseline.packets_recv,
            'errors_in': current.errin,
            'errors_out': current.errout,
            'drops_in': current.dropin,
            'drops_out': current.dropout,
        }
    
    def get_bandwidth_mbps(self, interval=1.0):
        """Calculate current bandwidth in Mbps"""
        before = psutil.net_io_counters()
        time.sleep(interval)
        after = psutil.net_io_counters()
        
        bytes_sent = (after.bytes_sent - before.bytes_sent) / interval
        bytes_recv = (after.bytes_recv - before.bytes_recv) / interval
        
        return {
            'upload_mbps': (bytes_sent * 8) / (1024 * 1024),
            'download_mbps': (bytes_recv * 8) / (1024 * 1024),
        }

# Usage
net_mon = NetworkMonitor()
bandwidth = net_mon.get_bandwidth_mbps(interval=1.0)
print(f"Upload: {bandwidth['upload_mbps']:.2f} Mbps")
print(f"Download: {bandwidth['download_mbps']:.2f} Mbps")
```

**Relationships:**
- ← Profiling (network usage tracking)
- → Load Balancing (network-aware routing)

#### Connection Limits
```python
class ConnectionLimiter:
    def __init__(self, max_connections=100):
        self.semaphore = Semaphore(max_connections)
        self.active_connections = 0
        self.total_connections = 0
        self.rejected_connections = 0
        
    def acquire_connection(self, timeout=5.0):
        """Acquire connection slot"""
        acquired = self.semaphore.acquire(timeout=timeout)
        
        if acquired:
            self.active_connections += 1
            self.total_connections += 1
            return True
        else:
            self.rejected_connections += 1
            return False
    
    def release_connection(self):
        """Release connection slot"""
        self.semaphore.release()
        self.active_connections -= 1
    
    def stats(self):
        return {
            'active': self.active_connections,
            'total': self.total_connections,
            'rejected': self.rejected_connections,
            'rejection_rate': self.rejected_connections / max(self.total_connections, 1),
        }

# Usage
limiter = ConnectionLimiter(max_connections=100)

def handle_connection(conn):
    if limiter.acquire_connection(timeout=5.0):
        try:
            process_connection(conn)
        finally:
            limiter.release_connection()
    else:
        reject_connection(conn, "Too many connections")
```

**Relationships:**
- → Connection Pooling (global connection limits)
- → Load Balancing (capacity management)

---

## Resource Allocation Patterns

### 1. Static Allocation
**Pattern:** Fixed resource allocation at startup

```python
class StaticResourceAllocator:
    def __init__(self, cpu_percent=50, memory_mb=2048, max_connections=100):
        self.cpu_limit = cpu_percent
        self.memory_limit = memory_mb * 1024 * 1024
        self.connection_limit = max_connections
        
        # Set hard limits
        self.enforce_limits()
    
    def enforce_limits(self):
        """Enforce resource limits"""
        # Memory limit (Linux)
        try:
            import resource
            resource.setrlimit(
                resource.RLIMIT_AS,
                (self.memory_limit, self.memory_limit)
            )
        except:
            pass
```

**Use Cases:** Predictable workloads, multi-tenant systems
**Relationships:** → Resource isolation, quota enforcement

### 2. Dynamic Allocation (Auto-Scaling)
**Pattern:** Adjust resources based on demand

```python
class DynamicResourceAllocator:
    def __init__(self):
        self.worker_pool_size = 10
        self.min_workers = 5
        self.max_workers = 50
        
    def auto_scale(self, queue_depth):
        """Adjust worker pool based on queue depth"""
        if queue_depth > self.worker_pool_size * 2:
            # Scale up
            new_size = min(self.worker_pool_size + 5, self.max_workers)
            self.scale_to(new_size)
        elif queue_depth < self.worker_pool_size * 0.5:
            # Scale down
            new_size = max(self.worker_pool_size - 5, self.min_workers)
            self.scale_to(new_size)
    
    def scale_to(self, new_size):
        print(f"Scaling worker pool: {self.worker_pool_size} → {new_size}")
        self.worker_pool_size = new_size
        # Adjust actual worker pool...
```

**Use Cases:** Variable workloads, cloud environments
**Relationships:** → Load Balancing (scaling triggers), ← Profiling (metrics-driven)

### 3. Priority-Based Allocation
**Pattern:** Allocate resources based on task priority

```python
import heapq
from dataclasses import dataclass, field
from typing import Any

@dataclass(order=True)
class PrioritizedTask:
    priority: int
    task: Any = field(compare=False)

class PriorityResourceAllocator:
    def __init__(self, max_concurrent=10):
        self.max_concurrent = max_concurrent
        self.active_tasks = 0
        self.task_queue = []
        
    def submit_task(self, task, priority=5):
        """Submit task with priority (lower number = higher priority)"""
        heapq.heappush(self.task_queue, PrioritizedTask(priority, task))
        self.process_queue()
    
    def process_queue(self):
        """Process tasks in priority order"""
        while self.task_queue and self.active_tasks < self.max_concurrent:
            prioritized = heapq.heappop(self.task_queue)
            self.execute_task(prioritized.task)
            self.active_tasks += 1
    
    def execute_task(self, task):
        # Execute task...
        pass
    
    def task_completed(self):
        self.active_tasks -= 1
        self.process_queue()

# Usage
allocator = PriorityResourceAllocator(max_concurrent=10)
allocator.submit_task(admin_task, priority=1)  # High priority
allocator.submit_task(batch_job, priority=10)  # Low priority
```

**Use Cases:** Mixed workloads, SLA differentiation
**Relationships:** → Optimization (priority optimization), → Load Balancing (priority routing)

---

## Resource Monitoring & Alerts

### Comprehensive Resource Monitor
```python
class ResourceMonitor:
    def __init__(self):
        self.thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90,
            'network_mbps': 900,  # For 1Gbps link
        }
        
    def check_all_resources(self):
        """Check all resource types"""
        alerts = []
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > self.thresholds['cpu_percent']:
            alerts.append(f"High CPU: {cpu_percent:.1f}%")
        
        # Memory
        mem = psutil.virtual_memory()
        if mem.percent > self.thresholds['memory_percent']:
            alerts.append(f"High Memory: {mem.percent:.1f}%")
        
        # Disk
        disk = psutil.disk_usage('/')
        if disk.percent > self.thresholds['disk_percent']:
            alerts.append(f"High Disk Usage: {disk.percent:.1f}%")
        
        # Network
        net_before = psutil.net_io_counters()
        time.sleep(1)
        net_after = psutil.net_io_counters()
        mbps = ((net_after.bytes_sent - net_before.bytes_sent) * 8) / (1024*1024)
        if mbps > self.thresholds['network_mbps']:
            alerts.append(f"High Network: {mbps:.1f} Mbps")
        
        return alerts
    
    def get_resource_report(self):
        """Generate comprehensive resource report"""
        return {
            'cpu': {
                'percent': psutil.cpu_percent(interval=1, percpu=True),
                'count': psutil.cpu_count(),
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None,
            },
            'memory': {
                'total_gb': psutil.virtual_memory().total / (1024**3),
                'available_gb': psutil.virtual_memory().available / (1024**3),
                'percent': psutil.virtual_memory().percent,
            },
            'disk': {
                'total_gb': psutil.disk_usage('/').total / (1024**3),
                'free_gb': psutil.disk_usage('/').free / (1024**3),
                'percent': psutil.disk_usage('/').percent,
            },
            'network': {
                'interfaces': psutil.net_if_stats(),
                'io_counters': psutil.net_io_counters(),
            }
        }

# Usage
monitor = ResourceMonitor()
alerts = monitor.check_all_resources()
if alerts:
    print("⚠️ Resource Alerts:")
    for alert in alerts:
        print(f"  - {alert}")
```

**Relationships:**
- ← Profiling (provides monitoring data)
- → All performance systems (resource availability affects all)

---

## Resource Quotas & Limits

### Multi-Tenant Resource Isolation
```python
class TenantResourceManager:
    def __init__(self):
        self.tenant_quotas = {}
        self.tenant_usage = {}
    
    def set_quota(self, tenant_id, cpu_percent=10, memory_mb=512, requests_per_min=1000):
        """Set resource quota for tenant"""
        self.tenant_quotas[tenant_id] = {
            'cpu_percent': cpu_percent,
            'memory_bytes': memory_mb * 1024 * 1024,
            'requests_per_min': requests_per_min,
        }
        self.tenant_usage[tenant_id] = {
            'cpu_percent': 0,
            'memory_bytes': 0,
            'requests_this_min': 0,
            'last_reset': time.time(),
        }
    
    def check_quota(self, tenant_id, resource_type):
        """Check if tenant is within quota"""
        if tenant_id not in self.tenant_quotas:
            return False, "Tenant not found"
        
        quota = self.tenant_quotas[tenant_id][resource_type]
        usage = self.tenant_usage[tenant_id][resource_type]
        
        if usage >= quota:
            return False, f"Quota exceeded: {usage}/{quota}"
        
        return True, None
    
    def allocate_resources(self, tenant_id, cpu=0, memory=0, request_count=1):
        """Allocate resources to tenant"""
        # Reset request counter if minute elapsed
        if time.time() - self.tenant_usage[tenant_id]['last_reset'] > 60:
            self.tenant_usage[tenant_id]['requests_this_min'] = 0
            self.tenant_usage[tenant_id]['last_reset'] = time.time()
        
        # Check quotas
        if cpu:
            allowed, msg = self.check_quota(tenant_id, 'cpu_percent')
            if not allowed:
                return False, msg
        
        if memory:
            allowed, msg = self.check_quota(tenant_id, 'memory_bytes')
            if not allowed:
                return False, msg
        
        if request_count:
            allowed, msg = self.check_quota(tenant_id, 'requests_per_min')
            if not allowed:
                return False, msg
        
        # Allocate
        self.tenant_usage[tenant_id]['cpu_percent'] += cpu
        self.tenant_usage[tenant_id]['memory_bytes'] += memory
        self.tenant_usage[tenant_id]['requests_this_min'] += request_count
        
        return True, "Resources allocated"
```

**Relationships:**
- → Load Balancing (tenant-based routing)
- → Optimization (per-tenant optimization)

---

## Resource Management Checklist

- [ ] Monitor CPU, memory, disk, network continuously
- [ ] Set resource limits for critical processes
- [ ] Implement graceful degradation under pressure
- [ ] Configure auto-scaling policies
- [ ] Set up resource usage alerts
- [ ] Test behavior under resource exhaustion
- [ ] Implement quota enforcement for multi-tenancy
- [ ] Use object pooling for expensive resources
- [ ] Configure garbage collection appropriately
- [ ] Document resource requirements
- [ ] Monitor resource trends over time
- [ ] Implement resource cleanup on shutdown

---

## Related Documentation
- Profiling: `profiling-relationships.md`
- Caching: `caching-relationships.md`
- Connection Pooling: `connection-pooling-relationships.md`
- Load Balancing: `load-balancing-relationships.md`
