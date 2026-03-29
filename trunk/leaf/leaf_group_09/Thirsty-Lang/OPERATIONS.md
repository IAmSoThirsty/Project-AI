<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / OPERATIONS.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / OPERATIONS.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# Operational Guide: Thirsty-lang with T.A.R.L.

## Deployment Guide

### Prerequisites

#### Required

- **Node.js**: 14.0.0 or higher
- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows

#### Optional

- **PyYAML**: For YAML policy support

  ```bash
  pip install pyyaml
  ```

### Installation Steps

#### 1. Clone Repository

```bash
git clone https://github.com/IAmSoThirsty/Thirsty-lang.git
cd Thirsty-lang
```

#### 2. Install Dependencies

```bash

# Node.js dependencies

npm install

# Python dependencies (optional)

pip install pyyaml
```

#### 3. Verify Installation

```bash

# Run tests

npm test

# Check Python availability

python3 --version
```

### Configuration

#### Basic Configuration

```javascript
const { SecurityManager } = require('./src/security');

const security = new SecurityManager({
  enabled: true,
  mode: 'defensive',  // 'defensive', 'strict', 'permissive'
  useTarl: true
});
```

#### Environment Variables

```bash

# Python executable path

export PYTHON_PATH=/usr/local/bin/python3

# T.A.R.L. configuration overrides

export TARL_SECURITY_MAX_EXECUTION_TIME=60.0
export TARL_RUNTIME_ENABLE_JIT=true
export TARL_COMPILER_DEBUG_MODE=false
```

#### Custom Bridge Configuration

```javascript
const { SecurityBridge } = require('./src/security/bridge');

const bridge = new SecurityBridge({
  pythonPath: '/usr/local/bin/python3',
  tarlPath: './tarl'
});
```

## Operational Modes

### Development Mode

Permissive policies for rapid development:

```javascript
const security = new SecurityManager({
  mode: 'permissive',
  useTarl: true
});

await security.initialize();
await security.loadPolicies('./tarl/policies/development.yaml');
```

**Characteristics**:

- Threats logged but not blocked
- All operations allowed
- Detailed debugging output
- Hot-reload enabled

### Testing Mode

Strict but non-blocking:

```javascript
const security = new SecurityManager({
  mode: 'defensive',
  useTarl: true
});

await security.loadPolicies('./tarl/policies/testing.json');
```

**Characteristics**:

- Threats detected and logged
- Critical threats blocked
- Warnings for suspicious operations
- Metrics tracking enabled

### Production Mode

Maximum security enforcement:

```javascript
const security = new SecurityManager({
  mode: 'strict',
  useTarl: true
});

await security.loadPolicies('./tarl/policies/production.json');

// Enable monitoring
const metricsInterval = setInterval(async () => {
  const metrics = await security.bridge.getRuntimeMetrics();
  console.log('Security metrics:', metrics);
}, 60000); // Every minute
```

**Characteristics**:

- All threats blocked immediately
- Escalation for suspicious operations
- Comprehensive audit logging
- Performance monitoring
- Hot-reload for policy updates

## Policy Management

### Policy Lifecycle

#### 1. Create Policy

```yaml

# development-policy.yaml

policies:

  - name: dev_allow_all

    description: Development mode - allow everything
    rules:

      - condition:

          action: compile
        verdict: ALLOW
        reason: Development mode
```

#### 2. Test Policy

```javascript
await security.loadPolicies('./policies/development-policy.yaml');

// Test evaluation
const result = await security.policyEngine.evaluate('compile', {
  source: 'test'
});
console.log('Policy decision:', result.verdict);
```

#### 3. Deploy Policy

```bash

# Copy to production

cp policies/production-policy.yaml /etc/thirsty-lang/policies/

# Reload in running application

await security.policyEngine.reloadPolicies();
```

#### 4. Monitor Policy

```javascript
// Track policy performance
const metrics = security.policyEngine.getMetrics();
console.log('Policy evaluations:', metrics.policyEvaluations);
console.log('Last reload:', metrics.lastReload);
```

### Policy Hot-Reload

Enable automatic policy updates:

```javascript
// Enable hot-reload
security.policyEngine.enableHotReload();

// Listen for updates
security.policyEngine.on('policies_reloaded', () => {
  console.log('Policies updated!');
  // Optional: Notify monitoring system
});

security.policyEngine.on('reload_error', (err) => {
  console.error('Policy reload failed:', err);
  // Alert on-call engineer
});
```

## Monitoring and Metrics

### Bridge Health Monitoring

```javascript
// Monitor bridge health
setInterval(() => {
  const metrics = security.bridge.getBridgeMetrics();

  if (metrics.failures / metrics.requests > 0.1) {
    console.error('Bridge failure rate high:', metrics);
    // Alert monitoring system
  }

  if (metrics.avgResponseTime > 100) {
    console.warn('Bridge response time degraded:', metrics.avgResponseTime);
  }
}, 30000); // Every 30 seconds
```

### Runtime Performance

```javascript
// Track T.A.R.L. runtime performance
const runtimeMetrics = await security.bridge.getRuntimeMetrics();

console.log('Performance:');
console.log('  Cache hit rate:', runtimeMetrics.cache_hit_rate_percent + '%');
console.log('  Productivity improvement:',
  runtimeMetrics.productivity_improvement_percent + '%');
console.log('  Total evaluations:', runtimeMetrics.total_evaluations);
```

### Threat Tracking

```javascript
// Track threats
const threatMetrics = security.threatDetector.getMetrics();

console.log('Threats:');
console.log('  Detected:', threatMetrics.threatsDetected);
console.log('  Blocked:', threatMetrics.policyEnforced);
console.log('  False positives:', threatMetrics.falsePositives);
```

## Logging and Auditing

### Enable Audit Logging

```javascript
const fs = require('fs');
const path = require('path');

// Create audit log stream
const auditLog = fs.createWriteStream(
  path.join(__dirname, 'logs', 'security-audit.log'),
  { flags: 'a' }
);

// Log all security events
security.on('threat_detected', (event) => {
  auditLog.write(JSON.stringify({
    timestamp: new Date().toISOString(),
    type: 'threat_detected',
    ...event
  }) + '\n');
});

security.on('policy_denied', (event) => {
  auditLog.write(JSON.stringify({
    timestamp: new Date().toISOString(),
    type: 'policy_denied',
    ...event
  }) + '\n');
});
```

### Structured Logging

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({
      filename: 'security-error.log',
      level: 'error'
    }),
    new winston.transports.File({
      filename: 'security-combined.log'
    })
  ]
});

// Log security events
async function logSecureCompile(code, options) {
  logger.info('Secure compilation started', { options });

  try {
    const result = await security.compileSecure(code, options);
    logger.info('Secure compilation completed', {
      threats: result.threats.length,
      transformations: result.transformations
    });
    return result;
  } catch (err) {
    logger.error('Secure compilation failed', { error: err.message });
    throw err;
  }
}
```

## Performance Tuning

### Cache Optimization

```javascript
// Adjust cache size based on workload
const runtime = new TarlRuntime(policies, {
  enableCache: true,
  cacheSize: 256,  // Increase for high-volume workloads
  enableParallel: true
});
```

### Memory Management

```javascript
// Monitor memory usage
const used = process.memoryUsage();
console.log('Memory usage:');
console.log('  RSS:', Math.round(used.rss / 1024 / 1024) + ' MB');
console.log('  Heap:', Math.round(used.heapUsed / 1024 / 1024) + ' MB');

// Reset metrics periodically
setInterval(() => {
  security.threatDetector.resetMetrics();
  runtime.reset_metrics();
}, 3600000); // Every hour
```

### Connection Pooling

For high-volume deployments:

```javascript
// Create bridge pool
class BridgePool {
  constructor(size = 4) {
    this.bridges = [];
    this.currentIndex = 0;

    for (let i = 0; i < size; i++) {
      const bridge = new SecurityBridge();
      this.bridges.push(bridge);
    }
  }

  async initializeAll() {
    await Promise.all(this.bridges.map(b => b.initialize()));
  }

  getBridge() {
    const bridge = this.bridges[this.currentIndex];
    this.currentIndex = (this.currentIndex + 1) % this.bridges.length;
    return bridge;
  }
}

const pool = new BridgePool(4);
await pool.initializeAll();
```

## Error Handling

### Graceful Degradation

```javascript
async function initializeSecurityWithFallback() {
  const security = new SecurityManager({ useTarl: true });

  try {
    await security.initialize();
    console.log('✓ T.A.R.L. security enabled');
    return security;
  } catch (err) {
    console.warn('T.A.R.L. unavailable, using basic security:', err.message);

    // Fallback to basic security
    return new SecurityManager({ useTarl: false });
  }
}
```

### Bridge Reconnection

```javascript
let bridge = new SecurityBridge();
await bridge.initialize();

bridge.on('disconnected', async (code) => {
  console.error('Bridge disconnected, reconnecting...');

  try {
    bridge = new SecurityBridge();
    await bridge.initialize();
    console.log('Bridge reconnected');
  } catch (err) {
    console.error('Reconnection failed:', err);
    // Alert monitoring system
  }
});
```

## High Availability

### Health Checks

```javascript
// Endpoint for load balancer
app.get('/health', async (req, res) => {
  try {
    // Check bridge health
    const metrics = security.bridge.getBridgeMetrics();

    if (metrics.failures / metrics.requests > 0.2) {
      return res.status(503).json({
        status: 'unhealthy',
        reason: 'High bridge failure rate'
      });
    }

    // Test policy evaluation
    const decision = await security.bridge.evaluatePolicy({
      action: 'health_check'
    });

    res.json({
      status: 'healthy',
      metrics: {
        bridgeRequests: metrics.requests,
        avgResponseTime: metrics.avgResponseTime
      }
    });
  } catch (err) {
    res.status(503).json({
      status: 'unhealthy',
      error: err.message
    });
  }
});
```

### Zero-Downtime Updates

```javascript
// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, shutting down gracefully...');

  // Stop accepting new requests
  server.close();

  // Shutdown security bridge
  await security.shutdown();

  console.log('Shutdown complete');
  process.exit(0);
});
```

## Troubleshooting

### Common Issues

#### High Latency

```javascript
// Diagnose latency
const start = Date.now();
const decision = await security.bridge.evaluatePolicy(context);
const latency = Date.now() - start;

if (latency > 100) {
  console.warn('High latency detected:', latency, 'ms');
  // Check Python process load
  // Increase cache size
  // Consider scaling
}
```

#### Memory Leaks

```javascript
// Monitor for leaks
setInterval(() => {
  const usage = process.memoryUsage();
  const heapMB = Math.round(usage.heapUsed / 1024 / 1024);

  if (heapMB > 512) {
    console.warn('High heap usage:', heapMB, 'MB');
    // Force garbage collection if needed
    if (global.gc) {
      global.gc();
    }
  }
}, 60000);
```

## Best Practices

1. **Initialize Once**: Create SecurityManager at application startup
2. **Shutdown Cleanly**: Always call `security.shutdown()` on exit
3. **Monitor Metrics**: Track performance and threats in production
4. **Version Policies**: Use version control for policy files
5. **Test Policies**: Test policy changes in staging before production
6. **Cache Tuning**: Adjust cache size based on workload
7. **Graceful Degradation**: Have fallbacks if T.A.R.L. is unavailable
8. **Audit Logging**: Log all security events for compliance
9. **Health Monitoring**: Implement health checks for high availability
10. **Resource Limits**: Set appropriate memory and timeout limits

## Production Checklist

- [ ] Python 3.8+ installed and accessible
- [ ] All tests passing
- [ ] Production policies configured
- [ ] Hot-reload enabled
- [ ] Monitoring configured
- [ ] Audit logging enabled
- [ ] Health checks implemented
- [ ] Graceful shutdown handlers
- [ ] Error handling and fallbacks
- [ ] Performance tuning applied
- [ ] Documentation reviewed
- [ ] Team trained on new features

## Support

For operational issues:

- Check logs in `logs/` directory
- Review metrics from monitoring endpoints
- Consult [Troubleshooting Guide](./TROUBLESHOOTING.md)
- Open issue: https://github.com/IAmSoThirsty/Thirsty-lang/issues

---

**Last Updated**: February 2026
**Version**: 2.0.0
