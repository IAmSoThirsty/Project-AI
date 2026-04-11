# Network Connectivity Requirements for PSIA Readiness Gate

## Overview

The PSIA Readiness Gate includes production-ready network connectivity checks to ensure nodes can communicate with required services before entering OPERATIONAL status.

## Features

### DNS Resolution
- Validates hostname resolution using system DNS
- Configurable timeout for DNS queries
- Supports both IPv4 and IPv6 addresses
- Skips DNS resolution for IP addresses
- Detailed error reporting for DNS failures

### TCP Connectivity
- Tests TCP socket connections to specified endpoints
- Configurable connection timeout
- Detects connection refused, timeout, and other errors
- Validates both hostname and IP-based endpoints

### Retry Logic
- Configurable retry attempts for failed connections
- Configurable delay between retry attempts
- Reports which retry attempt succeeded
- Comprehensive error reporting on complete failure

## Configuration

### NetworkEndpoint

Represents a single network endpoint to check:

```python
from psia.bootstrap.readiness import NetworkEndpoint

endpoint = NetworkEndpoint(
    host="peer1.example.com",    # Hostname or IP address
    port=8443,                    # TCP port number
    protocol="tcp",               # Protocol (currently only "tcp" supported)
    timeout_seconds=5.0,          # Connection timeout
    dns_required=True             # Whether DNS resolution is required
)
```

**Parameters:**
- `host` (str): Target hostname or IP address
- `port` (int): Target port number (1-65535)
- `protocol` (str): Protocol to use, default: "tcp"
- `timeout_seconds` (float): Connection timeout in seconds, default: 5.0
- `dns_required` (bool): Whether to perform DNS resolution, default: True

### NetworkCheckConfig

Global configuration for network connectivity checks:

```python
from psia.bootstrap.readiness import NetworkCheckConfig, NetworkEndpoint

config = NetworkCheckConfig(
    endpoints=[
        NetworkEndpoint(host="peer1.example.com", port=8443),
        NetworkEndpoint(host="peer2.example.com", port=8443),
        NetworkEndpoint(host="10.0.1.100", port=8443, dns_required=False),
    ],
    dns_servers=["8.8.8.8", "1.1.1.1"],  # Custom DNS servers (informational)
    max_retries=3,                        # Maximum retry attempts
    retry_delay_seconds=1.0,              # Delay between retries
    dns_timeout_seconds=3.0,              # DNS resolution timeout
)
```

**Parameters:**
- `endpoints` (list[NetworkEndpoint]): List of endpoints to check
- `dns_servers` (list[str]): DNS servers to use (informational only, uses system DNS)
- `max_retries` (int): Maximum number of retry attempts, default: 3
- `retry_delay_seconds` (float): Delay between retries in seconds, default: 1.0
- `dns_timeout_seconds` (float): DNS resolution timeout in seconds, default: 3.0

## Usage

### Basic Usage

```python
from psia.bootstrap.readiness import (
    ReadinessGate,
    NetworkEndpoint,
    NetworkCheckConfig
)

# Create endpoints
endpoints = [
    NetworkEndpoint(host="peer1.example.com", port=8443),
    NetworkEndpoint(host="peer2.example.com", port=8443),
]

# Create readiness gate
gate = ReadinessGate(node_id="psia-node-01")

# Register network check
gate.register_network_check(endpoints, critical=True)

# Evaluate readiness
report = gate.evaluate()

if report.status == NodeStatus.OPERATIONAL:
    print("Node is ready!")
else:
    print(f"Node not ready: {report.critical_failures} critical failures")
    for check in report.checks:
        if not check.passed:
            print(f"  - {check.name}: {check.message}")
```

### Advanced Configuration

```python
from psia.bootstrap.readiness import (
    ReadinessGate,
    NetworkEndpoint,
    NetworkCheckConfig
)

# Create custom configuration
config = NetworkCheckConfig(
    endpoints=[
        NetworkEndpoint(
            host="peer1.example.com",
            port=8443,
            timeout_seconds=10.0,  # Longer timeout for slow networks
            dns_required=True
        ),
        NetworkEndpoint(
            host="10.0.1.100",
            port=8443,
            timeout_seconds=5.0,
            dns_required=False  # Skip DNS for IP addresses
        ),
    ],
    max_retries=5,              # More retries for unreliable networks
    retry_delay_seconds=2.0,    # Longer delay between retries
    dns_timeout_seconds=5.0,    # Longer DNS timeout
)

# Create readiness gate with configuration
gate = ReadinessGate(
    node_id="psia-node-01",
    strict=True,
    network_config=config
)

# Register network check (uses config endpoints)
gate.register_network_check(critical=True)

# Evaluate readiness
report = gate.evaluate()
```

### Integration with Other Checks

```python
from psia.bootstrap.readiness import ReadinessGate, NetworkEndpoint

# Create readiness gate
gate = ReadinessGate(node_id="psia-node-01")

# Register multiple checks
gate.register_genesis_check(genesis_coordinator)
gate.register_ledger_check(ledger)
gate.register_capability_check(authority)

# Register network check
endpoints = [
    NetworkEndpoint(host="peer1.example.com", port=8443),
    NetworkEndpoint(host="peer2.example.com", port=8443),
]
gate.register_network_check(endpoints, critical=True)

# Evaluate all checks
report = gate.evaluate()

print(f"Status: {report.status}")
print(f"All passed: {report.all_passed}")
print(f"Critical failures: {report.critical_failures}")
print(f"Warnings: {report.warnings}")

for check in report.checks:
    status = "✓" if check.passed else "✗"
    print(f"{status} {check.name}: {check.message} ({check.duration_ms:.2f}ms)")
```

### Kubernetes Readiness Probe Example

```python
from flask import Flask, jsonify
from psia.bootstrap.readiness import (
    ReadinessGate,
    NetworkEndpoint,
    NetworkCheckConfig,
    NodeStatus
)

app = Flask(__name__)

@app.route('/health/ready')
def readiness_probe():
    """Kubernetes readiness probe endpoint."""
    # Create readiness gate
    config = NetworkCheckConfig(
        endpoints=[
            NetworkEndpoint(host="database.svc.cluster.local", port=5432),
            NetworkEndpoint(host="redis.svc.cluster.local", port=6379),
            NetworkEndpoint(host="peer-node-1.svc.cluster.local", port=8443),
        ],
        max_retries=2,
        retry_delay_seconds=0.5,
    )
    
    gate = ReadinessGate(network_config=config)
    gate.register_network_check(critical=True)
    
    # Evaluate readiness
    report = gate.evaluate()
    
    # Return 200 if operational, 503 otherwise
    status_code = 200 if report.status == NodeStatus.OPERATIONAL else 503
    
    return jsonify({
        "status": report.status.value,
        "all_passed": report.all_passed,
        "critical_failures": report.critical_failures,
        "warnings": report.warnings,
        "checks": [
            {
                "name": check.name,
                "passed": check.passed,
                "message": check.message,
                "duration_ms": check.duration_ms,
                "critical": check.critical,
            }
            for check in report.checks
        ],
        "timestamp": report.timestamp,
    }), status_code
```

## Network Check Behavior

### DNS Resolution
1. Checks if hostname is an IP address (dotted decimal format)
2. If IP address, skips DNS resolution
3. If hostname, performs DNS resolution with configured timeout
4. Returns resolved IP addresses in success message
5. Handles DNS failures (NXDOMAIN, timeout, etc.) gracefully

### TCP Connectivity
1. Creates TCP socket
2. Sets connection timeout
3. Attempts connection to host:port
4. Closes socket after successful connection
5. Reports specific error on failure (timeout, refused, etc.)

### Retry Logic
1. Performs initial attempt
2. On failure, waits `retry_delay_seconds`
3. Retries up to `max_retries` times
4. Returns success on first successful attempt
5. Returns failure with last error after all retries exhausted
6. Reports which retry attempt succeeded

### Multiple Endpoints
1. Checks all configured endpoints
2. Each endpoint checked independently with full retry logic
3. Reports overall success if all endpoints reachable
4. Reports failure if any endpoint unreachable
5. Failure message includes count and details of failed endpoints

## Security Considerations

### Production Recommendations
- **mTLS**: In production, implement mutual TLS for peer connections
- **Firewall Rules**: Ensure firewall rules allow connections to required endpoints
- **DNS Security**: Use DNSSEC-enabled DNS servers if available
- **Network Segmentation**: Isolate PSIA nodes in dedicated network segments
- **Monitoring**: Monitor network check failures in production

### Timeout Recommendations
- **LAN**: 2-5 seconds for local network endpoints
- **WAN**: 5-10 seconds for internet endpoints
- **Slow Networks**: 10-30 seconds for high-latency connections
- **DNS**: 3-5 seconds for DNS resolution

### Retry Recommendations
- **Stable Networks**: 2-3 retries with 0.5-1 second delay
- **Unreliable Networks**: 3-5 retries with 1-2 second delay
- **Critical Services**: More retries with exponential backoff

## Error Handling

### DNS Errors
- `DNS resolution failed`: Hostname does not exist (NXDOMAIN)
- `DNS resolution timed out`: DNS server not responding
- `DNS resolution error`: Unexpected DNS error

### TCP Errors
- `TCP connection refused`: Port not listening
- `TCP connection timed out`: Network unreachable or firewall blocking
- `TCP connection failed (DNS error)`: Hostname resolution failed during TCP connect
- `TCP connection failed`: General connection error (permissions, routing, etc.)

### Retry Errors
- `All N attempts failed`: All retry attempts exhausted
- Message includes last error encountered

## Testing

Comprehensive test suite covers:
- DNS resolution (success, failure, timeout, edge cases)
- TCP connectivity (success, refused, timeout, invalid hosts)
- Retry logic (success on retry, all retries fail, timing)
- Multiple endpoints (all pass, some fail, all fail)
- Configuration variations (custom timeouts, retries, DNS settings)
- Edge cases (empty endpoints, invalid ports, special characters)
- Integration scenarios (production-like configs, degraded networks)

Run tests:
```bash
pytest tests/psia/test_network_readiness.py -v
```

## Performance

### Timing Characteristics
- **DNS Resolution**: 10-100ms (cached), 100-500ms (uncached)
- **TCP Connection**: 1-50ms (LAN), 50-500ms (WAN)
- **Retry Delays**: Configurable, default 1 second between retries
- **Total Check Time**: Varies based on endpoints, timeouts, and retries

### Resource Usage
- **Memory**: Minimal (<1MB per check)
- **CPU**: Low (socket operations are I/O-bound)
- **Network**: Minimal (single TCP SYN packet per attempt)

### Optimization Tips
- Use IP addresses when DNS resolution is not needed
- Reduce timeouts for known-fast networks
- Reduce retries for stable networks
- Run checks in parallel for multiple independent endpoints (future enhancement)

## Future Enhancements

Planned improvements:
- **UDP Support**: Add UDP connectivity checks
- **HTTP/HTTPS Support**: Add HTTP endpoint health checks
- **Parallel Checks**: Check multiple endpoints concurrently
- **Exponential Backoff**: Add exponential backoff for retries
- **Circuit Breaker**: Add circuit breaker pattern for failing endpoints
- **Metrics**: Expose Prometheus metrics for network check performance
- **Custom DNS Servers**: Support specifying DNS servers directly

## Related Documentation

- `src/psia/bootstrap/readiness.py`: Implementation
- `tests/psia/test_network_readiness.py`: Test suite
- `tests/e2e/test_production_readiness.py`: E2E tests
- PSIA Bootstrap documentation (TBD)
