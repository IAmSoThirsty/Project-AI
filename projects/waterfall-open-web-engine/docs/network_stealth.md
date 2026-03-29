<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / network_stealth.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / network_stealth.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# Advanced Network Stealth Module

## Overview

The Advanced Network Stealth module provides production-grade network anonymization and censorship circumvention capabilities for the Thirstys Waterfall project. It implements multiple layers of protection including pluggable transports, multi-layer obfuscation, protocol mimicry, and domain fronting.

## Features

### 1. Pluggable Transports

Support for multiple transport protocols to bypass censorship:

- **obfs4**: Obfuscated bridge protocol with fingerprint-based authentication and IAT obfuscation
- **meek**: Domain fronting transport that routes traffic through legitimate CDN domains
- **snowflake**: WebRTC-based transport using temporary peer proxies
- **HTTP/3**: QUIC-based protocol with built-in TLS 1.3 encryption
- **QUIC**: Low-latency UDP-based transport with 0-RTT support
- **WebSocket**: Standard WebSocket tunneling over HTTP(S)
- **Direct**: Fallback direct connection

### 2. Multi-Layer Obfuscation

Advanced traffic obfuscation techniques to prevent analysis:

- **Traffic Padding**: Adds random padding to disguise packet sizes
- **Timing Randomization**: Randomizes packet timing to prevent correlation
- **Traffic Shaping**: Normalizes packets to target size distributions
- **Fragmentation**: Splits data into variable-sized chunks
- **Protocol Mimicry**: Disguises traffic as legitimate protocols

### 3. Protocol Mimicry

Make traffic look like common protocols:

- **HTTP/HTTPS**: Regular web traffic
- **TLS**: Encrypted TLS handshakes
- **DNS**: DNS query traffic
- **BitTorrent**: P2P file sharing
- **Gaming**: Game protocol packets

### 4. Domain Fronting

Censorship circumvention via CDN fronting:

- Routes traffic through legitimate CDN domains
- Uses TLS SNI to hide true destination
- Supports major CDN providers (CloudFlare, CloudFront, Fastly, Akamai)

### 5. Per-Request Onion Routing

Dynamic circuit selection for maximum anonymity:

- Maintains pool of pre-built circuits
- Selects different circuit for each request
- Automatic circuit rotation
- Load balancing across circuits

### 6. Comprehensive Metrics

Detailed logging and monitoring:

- Request statistics
- Circuit performance
- Transport usage
- Obfuscation effectiveness
- Latency tracking

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  AdvancedStealthManager                      │
│                                                               │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────┐│
│  │ Pluggable       │  │  Obfuscation     │  │  Domain     ││
│  │ Transports      │  │  Layer           │  │  Fronting   ││
│  │                 │  │                  │  │             ││
│  │ • obfs4        │  │ • Padding        │  │ • CDN       ││
│  │ • meek         │  │ • Timing         │  │   Routing   ││
│  │ • snowflake    │  │ • Shaping        │  │ • SNI       ││
│  │ • HTTP/3       │  │ • Mimicry        │  │   Masking   ││
│  │ • QUIC         │  │ • Fragmentation  │  │             ││
│  └─────────────────┘  └──────────────────┘  └─────────────┘│
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Per-Request Circuit Pool                     │   │
│  │  [Circuit 1] [Circuit 2] [Circuit 3] ... [Circuit N] │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Integration Layer                        │   │
│  │         VPN Manager  <->  Onion Router               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### Basic Setup

```python
from thirstys_waterfall.network import AdvancedStealthManager

# Initialize with configuration

config = {
    'advanced_stealth_enabled': True,
    'per_request_routing': True,
    'circuit_pool_size': 5
}

stealth = AdvancedStealthManager(config)
stealth.start()
```

### With VPN and Onion Router Integration

```python
from thirstys_waterfall.network import AdvancedStealthManager
from thirstys_waterfall.vpn.vpn_manager import VPNManager
from thirstys_waterfall.privacy.onion_router import OnionRouter

# Initialize VPN

vpn = VPNManager({'enabled': True, 'multi_hop': True})
vpn.start()

# Initialize Onion Router

onion = OnionRouter({'onion_routing': True})
onion.start()

# Initialize Stealth Manager with integrations

stealth = AdvancedStealthManager(config)
stealth.integrate_vpn(vpn)
stealth.integrate_onion_router(onion)
stealth.start()
```

### Routing Requests

```python

# Basic request

request = {
    'url': 'https://example.com/api',
    'data': 'sensitive data',
    'domain': 'example.com'
}

routed_request = stealth.route_request(request)

# The routed request includes:

# - circuit_id: Unique circuit identifier

# - circuit_path: List of nodes in the path

# - transport: Transport type used

# - obfuscated: Whether obfuscation was applied

# - domain_fronting: Whether domain fronting is active

# - sni_domain: Front domain for SNI

```

### Using Specific Transports

```python
from thirstys_waterfall.network import TransportType

# Switch to meek for domain fronting

stealth.switch_transport(TransportType.MEEK)

# Enable HTTP/3 fallback

stealth.enable_http3_fallback()

# Enable QUIC tunnel

stealth.enable_quic_tunnel()
```

### Protocol Mimicry

```python
from thirstys_waterfall.network import ProtocolMimicry

# Make traffic look like HTTPS

request = {
    'data': 'secret message',
    'mimic_protocol': ProtocolMimicry.HTTPS,
    'domain': 'example.com'
}
routed = stealth.route_request(request)

# Other protocols: HTTP, TLS, DNS, BITTORRENT, GAMING

```

### Circuit Management

```python

# Rotate all circuits

stealth.rotate_all_circuits()

# Rotate specific circuit

stealth.rotate_circuit('circuit_id_here')

# Get circuit status

status = stealth.get_status()
circuits = status['circuits']
print(f"Active: {circuits['active']}/{circuits['total']}")
```

### Metrics and Monitoring

```python

# Get basic metrics

metrics = stealth.get_metrics()
print(f"Requests routed: {metrics.requests_routed}")
print(f"Circuits built: {metrics.circuits_built}")
print(f"Average latency: {metrics.average_latency_ms}ms")

# Get detailed metrics

detailed = stealth.get_detailed_metrics()
print(f"Transport usage: {detailed['transports_used']}")
print(f"Obfuscation applied: {detailed['obfuscation_applied']}")
print(f"Protocols mimicked: {detailed['protocols_mimicked']}")
print(f"Domain fronting: {detailed['domain_fronting_used']} times")
```

## Configuration Options

### Stealth Manager Configuration

```python
config = {

    # Enable/disable stealth features

    'advanced_stealth_enabled': True,

    # Per-request routing

    'per_request_routing': True,

    # Circuit pool size

    'circuit_pool_size': 5,

    # Obfuscation settings

    'obfuscation': {
        'padding': True,
        'timing_randomization': True,
        'traffic_shaping': True,
        'protocol_mimicry': True,
        'min_padding': 0,
        'max_padding': 1024,
        'min_delay_ms': 0,
        'max_delay_ms': 500,
        'target_packet_size': 1400
    },

    # Domain fronting settings

    'domain_fronting': {
        'domain_fronting_enabled': True
    }
}
```

### Transport Configuration

Each transport can be configured individually:

```python
from thirstys_waterfall.network import TransportConfig, TransportType

config = TransportConfig(
    transport_type=TransportType.OBFS4,
    enabled=True,
    priority=10,  # Higher = preferred
    bridge_addresses=['bridge1.example.com', 'bridge2.example.com'],
    max_padding=1024,
    timing_variance_ms=500
)
```

## Security Considerations

### Protection Layers

When fully configured, the stealth manager provides 10+ layers of protection:

1. **VPN Encryption**: Base AES-256 encryption
2. **Multi-Hop VPN**: Traffic routed through multiple VPN nodes
3. **Onion Routing**: Additional onion circuit routing
4. **Per-Request Circuits**: Different circuit for each request
5. **Transport Obfuscation**: Pluggable transport layer
6. **Traffic Padding**: Random padding added
7. **Timing Randomization**: Packet timing randomized
8. **Protocol Mimicry**: Traffic disguised as legitimate protocol
9. **Domain Fronting**: Destination hidden via CDN
10. **Transport Encryption**: Additional transport-level encryption

### Anonymity Features

- **IP Masking**: Hidden through VPN + Onion routing
- **Traffic Pattern Obfuscation**: Padding and shaping
- **Protocol Disguise**: Mimicry of legitimate traffic
- **Timing Decorrelation**: Random delays prevent correlation
- **Destination Hiding**: Domain fronting obscures target

### Censorship Resistance

- **DPI Bypass**: Deep packet inspection defeated by obfuscation
- **SNI Filtering**: Bypassed via domain fronting
- **IP Blocking**: Circumvented via pluggable transports
- **Traffic Analysis**: Prevented by timing randomization
- **Pattern Detection**: Avoided by protocol mimicry

## Performance

### Latency

Typical latency overhead:

- Base stealth: 50-200ms
- With domain fronting: +50-100ms
- With full obfuscation: +100-300ms
- Per-request routing: +20-50ms

### Throughput

Transport performance (approximate):

- obfs4: 10-50 Mbps
- meek: 5-20 Mbps
- snowflake: 5-15 Mbps
- HTTP/3: 50-200 Mbps
- QUIC: 50-200 Mbps
- Direct: 100-500 Mbps

## API Reference

### AdvancedStealthManager

Main class for managing all stealth features.

#### Methods

- `start()`: Start the stealth manager
- `stop()`: Stop the stealth manager
- `route_request(request: Dict) -> Dict`: Route request through stealth pipeline
- `switch_transport(transport_type: TransportType)`: Switch to specific transport
- `enable_http3_fallback()`: Enable HTTP/3 fallback
- `enable_quic_tunnel()`: Enable QUIC tunnel
- `rotate_circuit(circuit_id: str)`: Rotate specific circuit
- `rotate_all_circuits()`: Rotate all circuits
- `integrate_vpn(vpn_manager)`: Integrate with VPN manager
- `integrate_onion_router(onion_router)`: Integrate with onion router
- `get_status() -> Dict`: Get comprehensive status
- `get_metrics() -> StealthMetrics`: Get metrics object
- `get_detailed_metrics() -> Dict`: Get detailed metrics dictionary
- `is_active() -> bool`: Check if manager is active

### PluggableTransport

Represents a single pluggable transport.

#### Methods

- `connect() -> bool`: Establish transport connection
- `disconnect()`: Disconnect transport
- `transmit(data: bytes) -> bytes`: Transmit data through transport
- `is_active() -> bool`: Check if transport is active

### ObfuscationLayer

Handles traffic obfuscation.

#### Methods

- `obfuscate_request(data: bytes, technique: ObfuscationTechnique) -> bytes`: Apply obfuscation
- `remove_padding(padded_data: bytes) -> bytes`: Remove padding
- `apply_timing_delay() -> float`: Apply random timing delay
- `mimic_protocol(data: bytes, protocol: ProtocolMimicry) -> bytes`: Apply protocol mimicry
- `get_metrics() -> Dict`: Get obfuscation metrics

### DomainFronting

Manages domain fronting.

#### Methods

- `setup_front(target_domain: str) -> str`: Setup domain front
- `get_fronted_request(request: Dict, front_domain: str) -> Dict`: Create fronted request
- `get_active_fronts() -> List[Dict]`: Get list of active fronts

## Examples

See `examples/advanced_stealth_demo.py` for a comprehensive demonstration of all features.

## Testing

Run the included tests:

```bash
python -m pytest tests/test_network_stealth.py -v
```

Or run manual tests:

```python
from thirstys_waterfall.network import AdvancedStealthManager

config = {'advanced_stealth_enabled': True}
manager = AdvancedStealthManager(config)
manager.start()

# Test request routing

request = {'url': 'https://example.com', 'data': 'test'}
result = manager.route_request(request)

assert result['obfuscated']
assert result['circuit_id']
assert result['transport']

manager.stop()
```

## Troubleshooting

### Transport Connection Failures

If transports fail to connect:

1. Check network connectivity
2. Verify bridge addresses if using obfs4/meek
3. Try different transports
4. Check firewall settings

### High Latency

To reduce latency:

1. Reduce circuit pool size
2. Disable timing randomization
3. Use faster transports (HTTP/3, QUIC)
4. Reduce padding amounts

### Failed Requests

If requests fail:

1. Check metrics for failure reasons
2. Rotate circuits
3. Switch transports
4. Verify integration with VPN/onion router

## Contributing

When contributing to the network stealth module:

1. Follow the existing code patterns
2. Add comprehensive logging
3. Update metrics appropriately
4. Include tests for new features
5. Document configuration options

## License

See LICENSE file in the repository root.
