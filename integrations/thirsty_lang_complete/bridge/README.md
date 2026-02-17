# Bridge Layer Documentation

## Overview

The bridge layer provides seamless integration between Thirsty-Lang's JavaScript runtime and TARL's Python security engine. It enables cross-language security policy enforcement through a robust JSON-RPC communication protocol.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    JavaScript Application                    │
│                   (Thirsty-Lang Runtime)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ require('./bridge/tarl-bridge.js')
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     TARLBridge (Node.js)                     │
│  • Spawn Python process                                      │
│  • JSON-RPC over stdin/stdout                                │
│  • Request queuing and timeout                               │
│  • Error handling and retries                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ JSON-RPC Protocol
                           │ (newline-delimited JSON)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  unified-security.py (Python)                │
│  • TARLBridge: Core policy engine                            │
│  • ThirstyLangSecurity: Language-specific checks             │
│  • UnifiedSecurityManager: Combined interface                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     TARL Runtime (Python)                    │
│  • Policy evaluation                                         │
│  • Resource monitoring                                       │
│  • Audit logging                                             │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. tarl-bridge.js

**Purpose:** JavaScript client for TARL Python runtime

**Key Features:**

- Process management with automatic restart
- JSON-RPC message protocol
- Request/response correlation
- Timeout and retry logic
- Decision caching
- Metrics collection
- Event-driven architecture

**Usage:**
```javascript
const { TARLBridge } = require('./tarl-bridge');

const bridge = new TARLBridge({
  pythonPath: 'python3',
  policyDir: './policies',
  timeout: 5000
});

await bridge.initialize();

const decision = await bridge.evaluatePolicy({
  operation: 'file_read',
  resource: '/path/to/file',
  user: 'alice'
});

await bridge.shutdown();
```

### 2. unified-security.py

**Purpose:** Unified security API combining TARL and Thirsty-Lang security

**Key Classes:**

#### TARLBridge

Core bridge to TARL runtime. Handles:

- Policy loading and evaluation
- Request processing
- Caching and metrics
- Runtime lifecycle

#### ThirstyLangSecurity

Language-specific security checks:

- Sandbox enforcement
- FFI restrictions
- File system access control
- Network filtering

#### UnifiedSecurityManager

Combined security interface implementing defense-in-depth:

- Checks both security layers
- Audit logging
- Resource monitoring
- Metrics aggregation

**Usage:**
```python
from bridge.unified_security import UnifiedSecurityManager

security = UnifiedSecurityManager(
    policy_dir='./policies',
    audit_log='./logs/audit.log'
)

await security.initialize()

decision = await security.check_permission({
    'operation': 'file_write',
    'resource': '/tmp/output.txt',
    'user': 'bob'
})

if decision['allowed']:

    # Perform operation

    pass

await security.shutdown()
```

## Communication Protocol

### Message Format

All messages are newline-delimited JSON objects.

**Request:**
```json
{
  "id": "req_123_abc456",
  "method": "evaluatePolicy",
  "params": {
    "context": {
      "operation": "file_read",
      "resource": "/etc/passwd",
      "user": "alice",
      "timestamp": 1704067200000
    }
  }
}
```

**Response (Success):**
```json
{
  "id": "req_123_abc456",
  "result": {
    "allowed": false,
    "decision_type": "deny",
    "reason": "Access to system files restricted",
    "policy_id": "system_files_protection",
    "metadata": {}
  }
}
```

**Response (Error):**
```json
{
  "id": "req_123_abc456",
  "error": {
    "code": "POLICY_ERROR",
    "message": "Policy file not found: default.yaml"
  }
}
```

### Supported Methods

#### evaluatePolicy

Evaluate single security policy.

**Parameters:**

- `context`: Security context object

**Returns:** SecurityDecision

#### evaluatePolicyBatch

Evaluate multiple policies in batch.

**Parameters:**

- `contexts`: Array of security contexts

**Returns:** Array of SecurityDecisions

#### reloadPolicies

Reload all policies from disk.

**Returns:** Status object

#### loadPolicy

Load policy from JSON/YAML object.

**Parameters:**

- `policy`: Policy definition object

**Returns:** Status object

#### setResourceLimits

Configure resource limits.

**Parameters:**

- `limits`: Resource limits object

**Returns:** Status object

#### getMetrics

Get runtime metrics.

**Returns:** Metrics object

#### shutdown

Gracefully shutdown runtime.

**Returns:** Status object

## Error Handling

### JavaScript Side

```javascript
try {
  const decision = await bridge.evaluatePolicy(context);
} catch (error) {
  if (error.message.includes('timeout')) {
    // Handle timeout
    console.error('Policy evaluation timeout');
  } else if (error.message.includes('exited')) {
    // Handle process crash
    console.error('Python process crashed');
    await bridge.initialize(); // Restart
  } else {
    // Other errors
    console.error('Policy error:', error);
  }
}
```

### Python Side

```python
try:
    decision = await bridge.evaluate_policy(context)
except RuntimeError as e:

    # Bridge not initialized

    logger.error(f"Bridge error: {e}")
    await bridge.initialize()
except Exception as e:

    # Policy evaluation error

    logger.error(f"Policy error: {e}")

    # Fail-safe: deny access

    decision = SecurityDecision(
        allowed=False,
        decision_type=DecisionType.DENY,
        reason=f"Error: {e}"
    )
```

## Performance Optimization

### Caching

Decisions are cached with TTL:

```javascript
// JavaScript caching (in bridge)
const cache = new Map();
const TTL = 60000; // 1 minute

// Python caching
self.cache_ttl = 60  # seconds
```

Cache keys are generated from:

- Operation type
- Resource path
- User identity

### Batch Processing

Process multiple decisions in single round-trip:

```javascript
const contexts = [
  { operation: 'file_read', resource: 'file1.txt' },
  { operation: 'file_read', resource: 'file2.txt' },
  { operation: 'file_read', resource: 'file3.txt' }
];

const decisions = await bridge.evaluatePolicyBatch(contexts);
```

### Connection Pooling

Reuse Python process across requests instead of spawning new process for each operation.

## Monitoring and Metrics

### Available Metrics

```javascript
const metrics = await bridge.getMetrics();

console.log({
  uptime: metrics.uptime,                    // seconds
  requestsProcessed: metrics.requestsProcessed,
  cacheHitRate: metrics.cacheHitRate,        // 0-1
  avgResponseTime: metrics.avgResponseTime,   // milliseconds
  memoryUsageMb: metrics.memoryUsageMb,
  cpuPercent: metrics.cpuPercent
});
```

### Logging

Configure logging level:

```javascript
const bridge = new TARLBridge({
  logLevel: 'debug',  // debug|info|warn|error
  logFile: './logs/bridge.log'
});
```

Logs include:

- Request/response correlation IDs
- Timestamps
- Execution times
- Error details

## Security Considerations

### Process Isolation

Python runtime runs in separate process with:

- Restricted file system access
- Network sandboxing (optional)
- Resource limits (CPU, memory)
- Non-privileged user

### Input Validation

All inputs validated before processing:

- JSON schema validation
- Size limits (10MB default)
- Type checking
- Sanitization

### Audit Logging

All security decisions logged:

- Timestamp
- User identity
- Operation and resource
- Decision and reason
- Policy ID

Logs are:

- Tamper-resistant
- Structured (JSON)
- Rotated automatically
- Optionally encrypted

## Testing

### Unit Tests

```bash

# JavaScript tests

npm test bridge/tarl-bridge.test.js

# Python tests

pytest tests/test_unified_security.py
```

### Integration Tests

```bash

# Full integration test

npm run test:integration
```

### Load Tests

```bash

# Benchmark performance

npm run benchmark -- --requests 1000 --concurrency 10
```

## Troubleshooting

### Python Process Won't Start

**Symptoms:** `Error: Python process exited with code 1`

**Solutions:**

1. Check Python installation: `python3 --version`
2. Verify TARL installed: `python3 -c "import tarl"`
3. Check stderr logs: Review `logs/bridge-stderr.log`
4. Verify policy directory exists and is readable

### Communication Timeout

**Symptoms:** `Error: Request timeout after 5000ms`

**Solutions:**

1. Increase timeout: `new TARLBridge({ timeout: 10000 })`
2. Check Python process health
3. Review policy complexity
4. Enable debug logging

### Memory Leak

**Symptoms:** Memory usage steadily increasing

**Solutions:**

1. Check audit log rotation
2. Reduce cache size
3. Monitor with metrics
4. Review pending requests: `bridge.pendingRequests.size`

### High CPU Usage

**Symptoms:** Python process consuming excessive CPU

**Solutions:**

1. Simplify policy rules
2. Enable decision caching
3. Use batch evaluation
4. Profile policy evaluation

## Development

### Adding New Methods

1. Add method to `tarl-bridge.js`:

```javascript
async myNewMethod(params) {
  return await this._sendMessage({
    method: 'myNewMethod',
    params: params
  });
}
```

2. Add handler in `unified-security.py`:

```python
elif method == 'myNewMethod':
    result = await bridge.my_new_method(params)
```

3. Add tests for new method

### Debugging

Enable verbose logging:

```javascript
const bridge = new TARLBridge({
  logLevel: 'debug'
});

bridge.on('message', (msg) => {
  console.log('Message:', msg);
});

bridge.on('log', (log) => {
  console.log('Log:', log);
});
```

## References

- [TARL Documentation](../../tarl/README.md)
- [Thirsty-Lang Documentation](../../src/thirsty_lang/README.md)
- [Integration Guide](../INTEGRATION_COMPLETE.md)
- [Security Best Practices](../../SECURITY.md)

## Support

For issues and questions:

- GitHub Issues: https://github.com/your-org/Project-AI/issues
- Documentation: https://docs.thirsty-lang.org/bridge
- Community: https://discord.gg/thirsty-lang
