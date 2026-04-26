# Load Balancing System Relationships

**System ID:** PERF-004  
**Category:** Performance & Reliability  
**Layer:** Infrastructure/Network  
**Status:** Production

## Overview

Load balancing distributes workload across multiple computing resources to optimize resource utilization, maximize throughput, minimize response time, and avoid overload of any single resource.

---

## Upstream Dependencies

### Traffic Sources
- **Client Requests** → Load Balancer
  - HTTP/HTTPS traffic
  - WebSocket connections
  - Database queries
  - API calls

### Health Monitoring
- **Health Checks** → Backend Selection
  - Server availability status
  - Response time metrics
  - Resource utilization
  - Error rates

### Resource Pool
- **Backend Servers** → Distribution Targets
  - Application servers
  - Database replicas
  - Cache nodes
  - Microservices instances

---

## Downstream Impacts

### Performance Systems
- **Connection Pooling** ← Distributed Connections
  - Pools across multiple backends
  - Connection reuse optimization
  
- **Caching** ← Cache Distribution
  - Distributed cache coordination
  - Cache coherency strategies
  
- **Resource Management** ← Load Distribution
  - Even resource utilization
  - Prevents resource exhaustion
  
- **Query Optimization** ← Query Routing
  - Read/write split
  - Query type-based routing

---

## Load Balancing Algorithms

### 1. Round Robin
**Pattern:** Distribute requests sequentially across servers

```python
class RoundRobinBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.current_index = 0
        self.lock = threading.Lock()
    
    def next_server(self):
        with self.lock:
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            return server

# Usage
balancer = RoundRobinBalancer(['server1', 'server2', 'server3'])
server = balancer.next_server()  # server1
server = balancer.next_server()  # server2
server = balancer.next_server()  # server3
server = balancer.next_server()  # server1 (wraps around)
```

**Characteristics:**
- **Pros:** Simple, fair distribution
- **Cons:** Ignores server capacity, current load
- **Best For:** Homogeneous servers, uniform request cost

**Relationships:**
- → Resource Management (assumes equal capacity)
- ← Profiling (requires monitoring for verification)

### 2. Weighted Round Robin
**Pattern:** Distribute based on server capacity weights

```python
class WeightedRoundRobinBalancer:
    def __init__(self, servers_with_weights):
        # Example: [('server1', 3), ('server2', 2), ('server3', 1)]
        self.weighted_servers = []
        for server, weight in servers_with_weights:
            self.weighted_servers.extend([server] * weight)
        self.current_index = 0
    
    def next_server(self):
        server = self.weighted_servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.weighted_servers)
        return server

# Usage: Server1 gets 50%, Server2 gets 33%, Server3 gets 17%
balancer = WeightedRoundRobinBalancer([
    ('server1', 3),
    ('server2', 2),
    ('server3', 1)
])
```

**Characteristics:**
- **Pros:** Accounts for different server capacities
- **Cons:** Static weights, doesn't adapt to current load
- **Best For:** Heterogeneous servers with known capacities

**Relationships:**
- → Resource Management (weight by CPU/memory capacity)
- ← Profiling (tune weights based on performance data)

### 3. Least Connections
**Pattern:** Route to server with fewest active connections

```python
class LeastConnectionsBalancer:
    def __init__(self, servers):
        self.connection_counts = {server: 0 for server in servers}
        self.lock = threading.Lock()
    
    def next_server(self):
        with self.lock:
            server = min(self.connection_counts, key=self.connection_counts.get)
            self.connection_counts[server] += 1
            return server
    
    def release_connection(self, server):
        with self.lock:
            self.connection_counts[server] -= 1

# Usage
balancer = LeastConnectionsBalancer(['server1', 'server2', 'server3'])
server = balancer.next_server()  # Returns server with least connections
# ... process request ...
balancer.release_connection(server)  # Decrement count
```

**Characteristics:**
- **Pros:** Dynamic, adapts to actual load
- **Cons:** More complex, requires connection tracking
- **Best For:** Long-lived connections, variable request durations

**Relationships:**
- → Connection Pooling (tracks active connections)
- → Resource Management (prevents connection overload)
- ← Profiling (monitors connection distribution)

### 4. Weighted Least Connections
**Pattern:** Combine capacity weights with connection count

```python
class WeightedLeastConnectionsBalancer:
    def __init__(self, servers_with_weights):
        self.servers = {server: {'weight': weight, 'connections': 0} 
                       for server, weight in servers_with_weights}
        self.lock = threading.Lock()
    
    def next_server(self):
        with self.lock:
            # Calculate ratio: connections / weight
            server = min(
                self.servers.keys(),
                key=lambda s: self.servers[s]['connections'] / self.servers[s]['weight']
            )
            self.servers[server]['connections'] += 1
            return server
    
    def release_connection(self, server):
        with self.lock:
            self.servers[server]['connections'] -= 1
```

**Characteristics:**
- **Pros:** Best of both worlds - capacity-aware and load-aware
- **Cons:** Most complex
- **Best For:** Production environments with heterogeneous servers

**Relationships:**
- → All load balancing relationships combined

### 5. IP Hash / Session Affinity
**Pattern:** Route based on client identifier for session persistence

```python
import hashlib

class IPHashBalancer:
    def __init__(self, servers):
        self.servers = sorted(servers)  # Consistent ordering
    
    def next_server(self, client_ip):
        # Hash client IP to deterministic server
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        server_index = hash_value % len(self.servers)
        return self.servers[server_index]

# Usage
balancer = IPHashBalancer(['server1', 'server2', 'server3'])
server = balancer.next_server('192.168.1.100')  # Always routes to same server
```

**Characteristics:**
- **Pros:** Session persistence without shared state
- **Cons:** Uneven distribution if client IPs are not uniform
- **Best For:** Stateful applications, cache locality

**Relationships:**
- → Caching (maximizes cache hit rate per server)
- → Resource Management (session state locality)

### 6. Least Response Time
**Pattern:** Route to server with fastest recent responses

```python
import time
from collections import deque

class LeastResponseTimeBalancer:
    def __init__(self, servers, window_size=100):
        self.servers = servers
        self.response_times = {server: deque(maxlen=window_size) for server in servers}
        self.lock = threading.Lock()
    
    def next_server(self):
        with self.lock:
            # Calculate average response time for each server
            avg_times = {}
            for server, times in self.response_times.items():
                if times:
                    avg_times[server] = sum(times) / len(times)
                else:
                    avg_times[server] = 0  # Prefer untested servers
            
            return min(avg_times, key=avg_times.get)
    
    def record_response(self, server, duration):
        with self.lock:
            self.response_times[server].append(duration)

# Usage
balancer = LeastResponseTimeBalancer(['server1', 'server2', 'server3'])
server = balancer.next_server()
start = time.perf_counter()
# ... process request ...
duration = time.perf_counter() - start
balancer.record_response(server, duration)
```

**Characteristics:**
- **Pros:** Routes to fastest servers, adapts to performance
- **Cons:** Requires response time tracking, can create hot spots
- **Best For:** Mixed workloads, servers with varying performance

**Relationships:**
- ← Profiling (uses performance metrics)
- → Optimization (routes to optimized servers)

### 7. Random
**Pattern:** Select server randomly

```python
import random

class RandomBalancer:
    def __init__(self, servers):
        self.servers = servers
    
    def next_server(self):
        return random.choice(self.servers)
```

**Characteristics:**
- **Pros:** Simple, stateless, no coordination overhead
- **Cons:** No optimization, potential uneven distribution short-term
- **Best For:** Simple cases, testing, stateless services

---

## Load Balancing Layers

### Layer 4 (Transport Layer)
**Mechanism:** Route based on IP address and TCP/UDP port

```python
class Layer4LoadBalancer:
    """Routes TCP/UDP packets based on network info"""
    def route_packet(self, source_ip, dest_port, protocol):
        # Simple hash-based routing
        hash_key = f"{source_ip}:{dest_port}"
        server_index = hash(hash_key) % len(self.backend_servers)
        return self.backend_servers[server_index]
```

**Characteristics:**
- Fast (no payload inspection)
- Connection-based
- No application awareness
- Examples: HAProxy (TCP mode), AWS NLB

**Relationships:**
- → Connection Pooling (TCP connection distribution)

### Layer 7 (Application Layer)
**Mechanism:** Route based on application data (HTTP headers, cookies, URL path)

```python
class Layer7LoadBalancer:
    """Routes based on HTTP request attributes"""
    def __init__(self):
        self.api_servers = ['api1', 'api2', 'api3']
        self.static_servers = ['cdn1', 'cdn2']
        self.admin_servers = ['admin1']
    
    def route_request(self, http_request):
        # Path-based routing
        if http_request.path.startswith('/api/'):
            return self.route_round_robin(self.api_servers)
        elif http_request.path.startswith('/static/'):
            return self.route_round_robin(self.static_servers)
        elif http_request.headers.get('X-Admin-Token'):
            return self.admin_servers[0]
        else:
            return self.route_round_robin(self.api_servers)
    
    def route_round_robin(self, servers):
        # Implementation omitted for brevity
        pass
```

**Advanced Routing Rules:**
```python
class AdvancedL7Balancer:
    def route_request(self, request):
        # Cookie-based session affinity
        if 'session_id' in request.cookies:
            return self.get_session_server(request.cookies['session_id'])
        
        # User-Agent based routing (mobile vs desktop)
        if 'mobile' in request.headers.get('User-Agent', '').lower():
            return self.mobile_servers
        
        # Geographic routing based on IP
        user_region = self.geoip_lookup(request.client_ip)
        return self.regional_servers[user_region]
        
        # A/B testing: 10% to experimental server
        if random.random() < 0.1:
            return self.experimental_server
        
        return self.production_servers
```

**Characteristics:**
- Content-aware routing
- SSL termination
- URL rewriting
- Examples: Nginx, HAProxy (HTTP mode), AWS ALB

**Relationships:**
- → Caching (route cacheable content to CDN)
- → Optimization (specialized servers for different workloads)
- → Security (route admin traffic separately)

---

## Health Checking & Failover

### Active Health Checks
```python
import requests
import threading
import time

class HealthChecker:
    def __init__(self, servers, check_interval=10):
        self.servers = servers
        self.healthy_servers = set(servers)
        self.check_interval = check_interval
        self.lock = threading.Lock()
        
        # Start background health checking
        self.checker_thread = threading.Thread(target=self._check_loop, daemon=True)
        self.checker_thread.start()
    
    def _check_loop(self):
        while True:
            for server in self.servers:
                is_healthy = self._check_server_health(server)
                
                with self.lock:
                    if is_healthy and server not in self.healthy_servers:
                        print(f"Server {server} is now healthy")
                        self.healthy_servers.add(server)
                    elif not is_healthy and server in self.healthy_servers:
                        print(f"Server {server} is now unhealthy")
                        self.healthy_servers.remove(server)
            
            time.sleep(self.check_interval)
    
    def _check_server_health(self, server):
        try:
            response = requests.get(
                f"http://{server}/health",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_healthy_servers(self):
        with self.lock:
            return list(self.healthy_servers)
```

### Passive Health Checks
```python
class PassiveHealthChecker:
    def __init__(self, failure_threshold=3, recovery_threshold=2):
        self.failure_counts = {}
        self.failure_threshold = failure_threshold
        self.recovery_threshold = recovery_threshold
        self.unhealthy_servers = set()
    
    def record_request(self, server, success):
        if success:
            self.failure_counts[server] = max(0, self.failure_counts.get(server, 0) - 1)
            
            # Check if server has recovered
            if server in self.unhealthy_servers:
                if self.failure_counts[server] <= -self.recovery_threshold:
                    print(f"Server {server} has recovered")
                    self.unhealthy_servers.remove(server)
                    self.failure_counts[server] = 0
        else:
            self.failure_counts[server] = self.failure_counts.get(server, 0) + 1
            
            # Check if server should be marked unhealthy
            if self.failure_counts[server] >= self.failure_threshold:
                print(f"Server {server} marked unhealthy")
                self.unhealthy_servers.add(server)
    
    def is_healthy(self, server):
        return server not in self.unhealthy_servers
```

**Relationships:**
- → Resource Management (avoid unhealthy servers)
- ← Profiling (health metrics)

---

## Load Balancing Patterns

### 1. Database Read Replica Load Balancing
```python
class DatabaseLoadBalancer:
    def __init__(self, write_master, read_replicas):
        self.write_master = write_master
        self.read_balancer = RoundRobinBalancer(read_replicas)
    
    def execute_query(self, query, is_write=False):
        if is_write or query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            # Route writes to master
            return self.write_master.execute(query)
        else:
            # Load balance reads across replicas
            replica = self.read_balancer.next_server()
            return replica.execute(query)
```

**Relationships:**
- → Query Optimization (read/write split)
- → Connection Pooling (separate pools for master/replicas)
- → Caching (reduce read load)

### 2. Microservices Load Balancing
```python
class ServiceMeshBalancer:
    def __init__(self):
        self.service_instances = {
            'user-service': ['user-1', 'user-2', 'user-3'],
            'order-service': ['order-1', 'order-2'],
            'payment-service': ['payment-1', 'payment-2', 'payment-3', 'payment-4'],
        }
        self.balancers = {
            service: LeastConnectionsBalancer(instances)
            for service, instances in self.service_instances.items()
        }
    
    def route_service_call(self, service_name):
        return self.balancers[service_name].next_server()
```

**Relationships:**
- → Resource Management (per-service scaling)
- → Profiling (service-level metrics)

### 3. Cache Load Balancing (Consistent Hashing)
```python
import hashlib

class ConsistentHashingBalancer:
    """Used for distributed caching to minimize cache invalidation"""
    def __init__(self, servers, virtual_nodes=150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        
        for server in servers:
            for i in range(virtual_nodes):
                virtual_key = f"{server}:{i}"
                hash_value = int(hashlib.md5(virtual_key.encode()).hexdigest(), 16)
                self.ring[hash_value] = server
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_server(self, key):
        """Get server for given cache key"""
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        
        # Find first server clockwise on ring
        for ring_key in self.sorted_keys:
            if hash_value <= ring_key:
                return self.ring[ring_key]
        
        # Wrap around to first server
        return self.ring[self.sorted_keys[0]]
    
    def add_server(self, server):
        """Add server with minimal cache redistribution"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{server}:{i}"
            hash_value = int(hashlib.md5(virtual_key.encode()).hexdigest(), 16)
            self.ring[hash_value] = server
        self.sorted_keys = sorted(self.ring.keys())
    
    def remove_server(self, server):
        """Remove server with minimal cache redistribution"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{server}:{i}"
            hash_value = int(hashlib.md5(virtual_key.encode()).hexdigest(), 16)
            del self.ring[hash_value]
        self.sorted_keys = sorted(self.ring.keys())

# Usage
cache_balancer = ConsistentHashingBalancer(['cache1', 'cache2', 'cache3'])
server = cache_balancer.get_server('user:12345')  # Deterministic routing
# Adding/removing servers only affects ~1/N of keys (N = server count)
```

**Characteristics:**
- Minimal cache invalidation when servers added/removed
- Deterministic routing (same key → same server)
- Virtual nodes for better distribution

**Relationships:**
- → Caching (distributed cache coordination)
- → Resource Management (dynamic scaling)

---

## Cross-System Integration

### Load Balancing + Caching
```python
class CachedLoadBalancer:
    def __init__(self, servers):
        self.balancer = LeastConnectionsBalancer(servers)
        self.response_cache = {}
        self.cache_ttl = 60  # seconds
    
    def handle_request(self, request):
        cache_key = self.generate_cache_key(request)
        
        # Check cache first
        cached_response = self.response_cache.get(cache_key)
        if cached_response and not self.is_expired(cached_response):
            return cached_response['data']
        
        # Route to backend
        server = self.balancer.next_server()
        response = server.handle(request)
        
        # Cache response
        self.response_cache[cache_key] = {
            'data': response,
            'timestamp': time.time()
        }
        
        return response
```

### Load Balancing + Connection Pooling
```python
class PooledLoadBalancer:
    def __init__(self, servers):
        # Create connection pool for each backend server
        self.pools = {
            server: ConnectionPool(server, min_size=5, max_size=20)
            for server in servers
        }
        self.balancer = WeightedLeastConnectionsBalancer([
            (server, 1) for server in servers
        ])
    
    def execute_query(self, query):
        server = self.balancer.next_server()
        
        # Get connection from pool
        with self.pools[server].connection() as conn:
            result = conn.execute(query)
        
        self.balancer.release_connection(server)
        return result
```

**Relationships:**
- → Connection Pooling (pools per backend)
- → Resource Management (connection limits)

---

## Monitoring & Metrics

### Load Balancer Metrics
```python
class LoadBalancerMetrics:
    def __init__(self):
        self.metrics = {
            'requests_per_server': {},
            'avg_response_time_per_server': {},
            'error_rate_per_server': {},
            'active_connections_per_server': {},
        }
    
    def record_request(self, server, duration, success):
        # Track request count
        self.metrics['requests_per_server'][server] = \
            self.metrics['requests_per_server'].get(server, 0) + 1
        
        # Track response time
        if server not in self.metrics['avg_response_time_per_server']:
            self.metrics['avg_response_time_per_server'][server] = []
        self.metrics['avg_response_time_per_server'][server].append(duration)
        
        # Track error rate
        if not success:
            self.metrics['error_rate_per_server'][server] = \
                self.metrics['error_rate_per_server'].get(server, 0) + 1
    
    def report(self):
        print("Load Balancer Metrics:")
        for server in self.metrics['requests_per_server']:
            requests = self.metrics['requests_per_server'][server]
            errors = self.metrics['error_rate_per_server'].get(server, 0)
            avg_time = sum(self.metrics['avg_response_time_per_server'][server]) / \
                      len(self.metrics['avg_response_time_per_server'][server])
            
            print(f"  {server}:")
            print(f"    Requests: {requests}")
            print(f"    Error Rate: {errors/requests*100:.2f}%")
            print(f"    Avg Response: {avg_time*1000:.1f}ms")
```

**Relationships:**
- ← Profiling (provides metrics)
- → Optimization (identifies imbalanced load)

---

## Anti-Patterns

### 1. No Health Checks
**Problem:** Routing to dead servers
**Solution:** Implement active/passive health checking

### 2. Ignoring Server Capacity
**Problem:** Overloading weak servers
**Solution:** Use weighted algorithms

### 3. Session Stickiness Without Persistence
**Problem:** Lost sessions on server failure
**Solution:** Use distributed session store (Redis)

### 4. Single Load Balancer (SPOF)
**Problem:** Load balancer becomes bottleneck/failure point
**Solution:** High availability load balancer pairs

---

## Load Balancing Checklist

- [ ] Choose algorithm appropriate for workload
- [ ] Implement health checking (active + passive)
- [ ] Configure failover behavior
- [ ] Set up monitoring/metrics
- [ ] Test server addition/removal
- [ ] Configure session persistence if needed
- [ ] Set up SSL/TLS termination
- [ ] Implement rate limiting
- [ ] Configure connection timeouts
- [ ] Test high-availability failover
- [ ] Document routing rules
- [ ] Integrate with service discovery

---

## Related Documentation
- Connection Pooling: `connection-pooling-relationships.md`
- Caching: `caching-relationships.md`
- Resource Management: `resource-management-relationships.md`
- Profiling: `profiling-relationships.md`
