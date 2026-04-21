# Connection Pooling System Relationships

**System ID:** PERF-007  
**Category:** Resource Optimization  
**Layer:** Infrastructure/Data Access  
**Status:** Production

## Overview

Connection Pooling manages a pool of reusable database/network connections to eliminate the overhead of creating new connections for each request, improving performance and resource utilization.

---

## Upstream Dependencies

### Database Systems
- **Database Servers** → Connection Targets
  - PostgreSQL, MySQL, MongoDB
  - Connection establishment protocols
  - Authentication mechanisms
  - Connection limits

### Network Infrastructure
- **Network Layer** → Connection Transport
  - TCP/IP connections
  - TLS/SSL for encrypted connections
  - Connection timeout settings
  - Keep-alive mechanisms

### Application Configuration
- **Pool Configuration** → Pool Behavior
  - Min/max pool size
  - Connection timeout
  - Idle timeout
  - Health check settings

---

## Downstream Impacts

### Performance Systems
- **Query Optimization** ← Connection Availability
  - Fast query execution
  - Reduced latency overhead
  
- **Resource Management** ← Connection Limits
  - Controlled resource usage
  - Prevents connection exhaustion
  
- **Load Balancing** ← Pool Distribution
  - Connections across replicas
  - Connection load spreading
  
- **Profiling** ← Pool Metrics
  - Connection usage patterns
  - Wait time analysis

---

## Connection Pool Implementation

### Basic Connection Pool
```python
import queue
import threading
import time
from contextlib import contextmanager

class ConnectionPool:
    def __init__(self, connection_factory, min_size=5, max_size=20, 
                 timeout=30, max_lifetime=3600):
        """
        Args:
            connection_factory: Function to create new connections
            min_size: Minimum connections to maintain
            max_size: Maximum connections allowed
            timeout: Max seconds to wait for available connection
            max_lifetime: Max seconds a connection can live
        """
        self.connection_factory = connection_factory
        self.min_size = min_size
        self.max_size = max_size
        self.timeout = timeout
        self.max_lifetime = max_lifetime
        
        self.pool = queue.Queue(maxsize=max_size)
        self.active_connections = 0
        self.total_created = 0
        self.total_reused = 0
        self.lock = threading.Lock()
        
        # Create minimum connections
        for _ in range(min_size):
            conn = self._create_connection()
            self.pool.put(conn)
    
    def _create_connection(self):
        """Create new connection with metadata"""
        with self.lock:
            conn = self.connection_factory()
            self.active_connections += 1
            self.total_created += 1
        
        return {
            'connection': conn,
            'created_at': time.time(),
            'last_used': time.time(),
            'use_count': 0,
        }
    
    @contextmanager
    def connection(self):
        """Get connection from pool (context manager)"""
        conn_wrapper = None
        
        try:
            # Try to get connection from pool
            try:
                conn_wrapper = self.pool.get(timeout=self.timeout)
                self.total_reused += 1
            except queue.Empty:
                # Pool exhausted, create new connection if under max
                with self.lock:
                    if self.active_connections < self.max_size:
                        conn_wrapper = self._create_connection()
                    else:
                        raise Exception(f"Connection pool exhausted (max: {self.max_size})")
            
            # Check connection validity
            if not self._is_connection_valid(conn_wrapper):
                # Connection expired or broken, create new one
                self._close_connection(conn_wrapper)
                conn_wrapper = self._create_connection()
            
            # Update metadata
            conn_wrapper['last_used'] = time.time()
            conn_wrapper['use_count'] += 1
            
            # Yield actual connection
            yield conn_wrapper['connection']
            
        finally:
            # Return connection to pool
            if conn_wrapper:
                try:
                    self.pool.put_nowait(conn_wrapper)
                except queue.Full:
                    # Pool full, close connection
                    self._close_connection(conn_wrapper)
    
    def _is_connection_valid(self, conn_wrapper):
        """Check if connection is still valid"""
        # Check age
        age = time.time() - conn_wrapper['created_at']
        if age > self.max_lifetime:
            return False
        
        # Check if connection is alive (database-specific)
        try:
            conn_wrapper['connection'].ping()
            return True
        except:
            return False
    
    def _close_connection(self, conn_wrapper):
        """Close and cleanup connection"""
        try:
            conn_wrapper['connection'].close()
        except:
            pass
        
        with self.lock:
            self.active_connections -= 1
    
    def stats(self):
        """Get pool statistics"""
        return {
            'pool_size': self.pool.qsize(),
            'active_connections': self.active_connections,
            'min_size': self.min_size,
            'max_size': self.max_size,
            'total_created': self.total_created,
            'total_reused': self.total_reused,
            'reuse_rate': self.total_reused / max(self.total_created, 1),
        }
    
    def close_all(self):
        """Close all connections"""
        while not self.pool.empty():
            try:
                conn_wrapper = self.pool.get_nowait()
                self._close_connection(conn_wrapper)
            except queue.Empty:
                break

# Usage
def create_db_connection():
    import psycopg2
    return psycopg2.connect(
        host='localhost',
        database='mydb',
        user='user',
        password='password'
    )

pool = ConnectionPool(
    connection_factory=create_db_connection,
    min_size=5,
    max_size=20,
    timeout=30
)

# Use connection
with pool.connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()

# Check pool health
print(pool.stats())
```

**Relationships:**
- → Resource Management (connection limits)
- → Query Optimization (fast connection availability)
- ← Profiling (pool usage metrics)

---

## Connection Pool Patterns

### 1. Lazy Connection Pool
**Pattern:** Create connections only when needed

```python
class LazyConnectionPool:
    def __init__(self, connection_factory, max_size=20):
        self.connection_factory = connection_factory
        self.max_size = max_size
        self.pool = queue.Queue(maxsize=max_size)
        self.active_count = 0
        self.lock = threading.Lock()
    
    @contextmanager
    def connection(self):
        """Get or create connection lazily"""
        conn = None
        
        try:
            # Try to get existing connection
            conn = self.pool.get_nowait()
        except queue.Empty:
            # No available connection, create new one if under limit
            with self.lock:
                if self.active_count < self.max_size:
                    conn = self.connection_factory()
                    self.active_count += 1
                else:
                    # Wait for connection to become available
                    conn = self.pool.get()
        
        try:
            yield conn
        finally:
            # Return to pool
            self.pool.put(conn)
```

**Use Case:** Variable workload, minimize idle connections
**Relationships:** → Resource Management (lazy resource allocation)

### 2. Per-Thread Connection Pool
**Pattern:** Each thread gets dedicated connection

```python
import threading

class ThreadLocalConnectionPool:
    def __init__(self, connection_factory):
        self.connection_factory = connection_factory
        self.thread_local = threading.local()
    
    def get_connection(self):
        """Get connection for current thread"""
        if not hasattr(self.thread_local, 'connection'):
            self.thread_local.connection = self.connection_factory()
        
        return self.thread_local.connection
    
    def close_current_connection(self):
        """Close connection for current thread"""
        if hasattr(self.thread_local, 'connection'):
            self.thread_local.connection.close()
            del self.thread_local.connection
```

**Use Case:** Thread-unsafe connections, transaction isolation
**Trade-offs:** More connections, no connection sharing

### 3. Health-Checked Connection Pool
**Pattern:** Verify connection health before use

```python
class HealthCheckedConnectionPool(ConnectionPool):
    def __init__(self, *args, health_check_interval=60, **kwargs):
        super().__init__(*args, **kwargs)
        self.health_check_interval = health_check_interval
        
        # Start background health checker
        self.health_checker = threading.Thread(
            target=self._health_check_loop,
            daemon=True
        )
        self.health_checker.start()
    
    def _health_check_loop(self):
        """Periodically check connection health"""
        while True:
            time.sleep(self.health_check_interval)
            self._check_all_connections()
    
    def _check_all_connections(self):
        """Check all pooled connections"""
        checked = []
        
        # Get all connections from pool
        while not self.pool.empty():
            try:
                conn_wrapper = self.pool.get_nowait()
                checked.append(conn_wrapper)
            except queue.Empty:
                break
        
        # Health check each connection
        for conn_wrapper in checked:
            if self._is_connection_valid(conn_wrapper):
                self.pool.put(conn_wrapper)
            else:
                print(f"Removing unhealthy connection (age: {time.time() - conn_wrapper['created_at']:.1f}s)")
                self._close_connection(conn_wrapper)
                
                # Create replacement if below min_size
                if self.pool.qsize() < self.min_size:
                    new_conn = self._create_connection()
                    self.pool.put(new_conn)
    
    def _is_connection_valid(self, conn_wrapper):
        """Check connection health"""
        try:
            # Database-specific health check
            cursor = conn_wrapper['connection'].cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except Exception as e:
            print(f"Connection health check failed: {e}")
            return False
```

**Relationships:**
- → Resource Management (automatic cleanup)
- → Load Balancing (remove unhealthy connections)
- ← Profiling (health check metrics)

---

## Pool Sizing Strategies

### Optimal Pool Size Calculation
```python
class PoolSizeOptimizer:
    @staticmethod
    def calculate_optimal_size(
        avg_request_duration_sec,
        requests_per_second,
        connection_overhead_sec=0.1,
        safety_factor=1.2
    ):
        """
        Calculate optimal pool size based on Little's Law
        
        L = λW
        L = Average number of items in system (pool size)
        λ = Average arrival rate (requests/sec)
        W = Average time in system (request duration + overhead)
        """
        avg_time_in_system = avg_request_duration_sec + connection_overhead_sec
        optimal_size = requests_per_second * avg_time_in_system * safety_factor
        
        return int(optimal_size)
    
    @staticmethod
    def recommend_pool_config(
        peak_requests_per_second,
        avg_query_duration_sec,
        available_db_connections=100
    ):
        """Recommend pool configuration"""
        # Calculate pool size
        pool_size = PoolSizeOptimizer.calculate_optimal_size(
            avg_query_duration_sec,
            peak_requests_per_second
        )
        
        # Cap at database connection limit (leave headroom for other apps)
        max_pool_size = min(pool_size, int(available_db_connections * 0.8))
        min_pool_size = max(5, int(max_pool_size * 0.2))
        
        return {
            'min_size': min_pool_size,
            'max_size': max_pool_size,
            'timeout': 30,  # seconds
            'max_lifetime': 3600,  # 1 hour
        }

# Usage
config = PoolSizeOptimizer.recommend_pool_config(
    peak_requests_per_second=100,
    avg_query_duration_sec=0.05,
    available_db_connections=100
)

print(f"Recommended pool config: {config}")
# Output: {'min_size': 5, 'max_size': 20, 'timeout': 30, 'max_lifetime': 3600}
```

**Relationships:**
- ← Profiling (request rate, query duration)
- → Resource Management (database connection limits)
- → Load Balancing (distribute load across replicas)

---

## Pool Monitoring & Metrics

### Connection Pool Monitor
```python
import time
from collections import deque

class ConnectionPoolMonitor:
    def __init__(self, pool):
        self.pool = pool
        self.wait_times = deque(maxlen=1000)  # Last 1000 wait times
        self.checkout_count = 0
        self.timeout_count = 0
        self.start_time = time.time()
    
    def record_checkout(self, wait_time, success):
        """Record connection checkout metrics"""
        self.checkout_count += 1
        
        if success:
            self.wait_times.append(wait_time)
        else:
            self.timeout_count += 1
    
    def get_metrics(self):
        """Get comprehensive pool metrics"""
        pool_stats = self.pool.stats()
        
        metrics = {
            **pool_stats,
            'checkout_count': self.checkout_count,
            'timeout_count': self.timeout_count,
            'timeout_rate': self.timeout_count / max(self.checkout_count, 1),
        }
        
        if self.wait_times:
            import numpy as np
            metrics['avg_wait_time'] = np.mean(self.wait_times)
            metrics['p95_wait_time'] = np.percentile(self.wait_times, 95)
            metrics['p99_wait_time'] = np.percentile(self.wait_times, 99)
        
        # Utilization
        metrics['utilization'] = (
            (pool_stats['active_connections'] - pool_stats['pool_size']) / 
            pool_stats['max_size']
        )
        
        return metrics
    
    def alert_if_needed(self):
        """Check for pool health issues"""
        metrics = self.get_metrics()
        alerts = []
        
        # High utilization
        if metrics['utilization'] > 0.9:
            alerts.append(f"⚠️ Pool utilization high: {metrics['utilization']*100:.1f}%")
        
        # High timeout rate
        if metrics['timeout_rate'] > 0.05:
            alerts.append(f"⚠️ Connection timeout rate high: {metrics['timeout_rate']*100:.1f}%")
        
        # High wait time
        if 'p95_wait_time' in metrics and metrics['p95_wait_time'] > 1.0:
            alerts.append(f"⚠️ High connection wait time: {metrics['p95_wait_time']*1000:.1f}ms")
        
        # Low reuse rate
        if metrics['reuse_rate'] < 5.0:
            alerts.append(f"⚠️ Low connection reuse: {metrics['reuse_rate']:.1f}x")
        
        return alerts

# Usage with monitoring
monitor = ConnectionPoolMonitor(pool)

@contextmanager
def monitored_connection():
    start = time.perf_counter()
    success = False
    
    try:
        with pool.connection() as conn:
            wait_time = time.perf_counter() - start
            monitor.record_checkout(wait_time, True)
            success = True
            yield conn
    except Exception as e:
        wait_time = time.perf_counter() - start
        monitor.record_checkout(wait_time, False)
        raise

# Periodic health check
alerts = monitor.alert_if_needed()
if alerts:
    for alert in alerts:
        print(alert)
```

**Relationships:**
- ← Profiling (provides metrics)
- → Optimization (identifies pool sizing issues)
- → Resource Management (capacity alerts)

---

## Cross-System Integration

### Connection Pool + Query Optimization
```python
class OptimizedDatabaseAccess:
    def __init__(self, connection_pool):
        self.pool = connection_pool
        self.prepared_statements = {}
    
    def execute_prepared(self, query_name, query, params):
        """Execute prepared statement with pooled connection"""
        with self.pool.connection() as conn:
            # Prepare statement if not already prepared
            if query_name not in self.prepared_statements:
                self.prepared_statements[query_name] = conn.prepare(query)
            
            # Execute prepared statement (faster than raw query)
            return self.prepared_statements[query_name].execute(params)
    
    def execute_batch(self, queries_with_params):
        """Execute multiple queries in one connection"""
        with self.pool.connection() as conn:
            results = []
            for query, params in queries_with_params:
                results.append(conn.execute(query, params))
            return results

# Performance: Prepared statements + connection pooling = 5-10x faster
```

**Relationships:**
- → Query Optimization (prepared statements)
- → Connection Pooling (connection reuse)

### Connection Pool + Load Balancing
```python
class LoadBalancedConnectionPool:
    def __init__(self, master_config, replica_configs):
        # Write pool (master)
        self.write_pool = ConnectionPool(
            lambda: create_connection(**master_config),
            min_size=5,
            max_size=20
        )
        
        # Read pools (replicas)
        self.read_pools = [
            ConnectionPool(
                lambda cfg=cfg: create_connection(**cfg),
                min_size=10,
                max_size=50
            )
            for cfg in replica_configs
        ]
        
        self.read_pool_index = 0
        self.lock = threading.Lock()
    
    def write_connection(self):
        """Get connection to master for writes"""
        return self.write_pool.connection()
    
    def read_connection(self):
        """Get connection to read replica (round-robin)"""
        with self.lock:
            pool = self.read_pools[self.read_pool_index]
            self.read_pool_index = (self.read_pool_index + 1) % len(self.read_pools)
        
        return pool.connection()

# Usage
lb_pool = LoadBalancedConnectionPool(
    master_config={'host': 'db-master', 'port': 5432},
    replica_configs=[
        {'host': 'db-replica-1', 'port': 5432},
        {'host': 'db-replica-2', 'port': 5432},
    ]
)

# Write to master
with lb_pool.write_connection() as conn:
    conn.execute("INSERT INTO users ...")

# Read from replica
with lb_pool.read_connection() as conn:
    results = conn.execute("SELECT * FROM users ...")
```

**Relationships:**
- → Load Balancing (distribute reads across replicas)
- → Connection Pooling (pools per backend)
- → Resource Management (separate pool limits)

---

## Connection Pool Anti-Patterns

### 1. Pool Exhaustion from Long Transactions
**Problem:** Long-running transactions hold connections
```python
# BAD: Long transaction holds connection
with pool.connection() as conn:
    results = conn.execute("SELECT * FROM huge_table")
    
    # Process results slowly (connection held for minutes)
    for row in results:
        time.sleep(1)  # Slow processing
        process_row(row)

# GOOD: Release connection after query
with pool.connection() as conn:
    results = list(conn.execute("SELECT * FROM huge_table"))
# Connection returned to pool

# Process results without holding connection
for row in results:
    process_row(row)
```

### 2. Creating Pools Inside Request Handlers
**Problem:** New pool per request defeats the purpose
```python
# BAD: New pool per request
def handle_request(request):
    pool = ConnectionPool(...)  # Creates new pool!
    with pool.connection() as conn:
        return conn.execute(query)

# GOOD: Shared pool
global_pool = ConnectionPool(...)  # Created once at startup

def handle_request(request):
    with global_pool.connection() as conn:
        return conn.execute(query)
```

### 3. Pool Size = Database Max Connections
**Problem:** Leaves no connections for other apps/maintenance
```python
# BAD: Use all available connections
pool = ConnectionPool(max_size=100)  # Database also has max 100!

# GOOD: Leave headroom (80% rule)
pool = ConnectionPool(max_size=80)  # Leaves 20 for maintenance, other apps
```

---

## Connection Pool Configuration Guide

### Configuration Matrix
| Application Type | Min Size | Max Size | Timeout | Max Lifetime |
|------------------|----------|----------|---------|--------------|
| API Server (high traffic) | 20 | 100 | 30s | 1 hour |
| API Server (low traffic) | 5 | 20 | 30s | 1 hour |
| Batch Processing | 5 | 50 | 60s | 30 min |
| Background Jobs | 2 | 10 | 60s | 2 hours |
| Development | 1 | 5 | 10s | 5 min |

### Dynamic Pool Sizing
```python
class AdaptiveConnectionPool(ConnectionPool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_adjustment = time.time()
        self.adjustment_interval = 300  # 5 minutes
    
    def auto_adjust_size(self):
        """Adjust pool size based on usage patterns"""
        if time.time() - self.last_adjustment < self.adjustment_interval:
            return
        
        stats = self.stats()
        utilization = (self.active_connections - stats['pool_size']) / self.max_size
        
        # Scale up if high utilization
        if utilization > 0.8:
            new_max = min(self.max_size + 10, 200)
            print(f"Scaling up pool: {self.max_size} → {new_max}")
            self.max_size = new_max
        
        # Scale down if low utilization
        elif utilization < 0.2 and self.max_size > self.min_size:
            new_max = max(self.max_size - 10, self.min_size)
            print(f"Scaling down pool: {self.max_size} → {new_max}")
            self.max_size = new_max
        
        self.last_adjustment = time.time()
```

---

## Connection Pool Checklist

- [ ] Set appropriate min/max pool sizes
- [ ] Configure connection timeout
- [ ] Set max connection lifetime
- [ ] Implement connection health checks
- [ ] Monitor pool utilization
- [ ] Track connection wait times
- [ ] Alert on pool exhaustion
- [ ] Test connection recovery
- [ ] Implement graceful shutdown
- [ ] Use prepared statements where possible
- [ ] Monitor connection leak (connections not returned)
- [ ] Configure separate pools for read/write
- [ ] Test pool behavior under load
- [ ] Document pool configuration rationale

---

## Performance Impact

| Scenario | Without Pooling | With Pooling | Improvement |
|----------|-----------------|--------------|-------------|
| Connection establishment | 50ms/query | 0.5ms/query | 100x faster |
| High-frequency queries (1000/sec) | Impossible (connection limit) | Handled easily | ∞ |
| Connection overhead | 50% of total time | 1% of total time | 50x reduction |
| Database connections | 1000 (one per request) | 20 (pooled) | 50x fewer |

---

## Related Documentation
- Resource Management: `resource-management-relationships.md`
- Query Optimization: `query-optimization-relationships.md`
- Load Balancing: `load-balancing-relationships.md`
- Profiling: `profiling-relationships.md`
