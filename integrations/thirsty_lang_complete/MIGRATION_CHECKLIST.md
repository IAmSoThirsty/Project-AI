# Migration Checklist: Thirsty-Lang + TARL Integration

This checklist guides you through migrating an existing Thirsty-Lang or TARL project to use the unified integration package.

## Pre-Migration Assessment

### Current State Analysis

- [ ] **Identify current architecture**
  - [ ] Standalone Thirsty-Lang (JavaScript/TypeScript)
  - [ ] Standalone Thirsty-Lang (Python)
  - [ ] Standalone TARL (Python security runtime)
  - [ ] Partial integration (custom bridge)

- [ ] **Document existing security policies**
  - [ ] List all security rules
  - [ ] Identify policy files and formats
  - [ ] Note any custom security logic
  - [ ] Document access control requirements

- [ ] **Review dependencies**
  - [ ] List current Python packages
  - [ ] List current Node.js packages
  - [ ] Identify version conflicts
  - [ ] Check compatibility with Python 3.10+, Node.js 18+

- [ ] **Audit current codebase**
  - [ ] Count security checkpoints
  - [ ] Identify hardcoded security logic
  - [ ] Find permission check locations
  - [ ] List resource access points

## Phase 1: Environment Setup

### System Requirements

- [ ] **Verify system requirements**
  - [ ] Python 3.10 or higher installed
  - [ ] Node.js 18.0 or higher installed
  - [ ] At least 2GB RAM available
  - [ ] 500MB disk space available

- [ ] **Install base dependencies**
  ```bash
  # Python dependencies
  pip install --upgrade pip
  pip install pyyaml jsonschema cryptography psutil
  
  # Node.js dependencies
  npm install --save @thirsty-lang/core
  ```

- [ ] **Clone Project-AI repository**
  ```bash
  git clone https://github.com/your-org/Project-AI.git
  cd Project-AI
  ```

- [ ] **Verify TARL installation**
  ```bash
  python3 -c "import tarl; print('TARL OK')"
  ```

## Phase 2: Bridge Layer Installation

### Copy Integration Files

- [ ] **Create bridge directory structure**
  ```bash
  mkdir -p src/security/bridge
  ```

- [ ] **Copy bridge files**
  ```bash
  cp integrations/thirsty_lang_complete/bridge/tarl-bridge.js src/security/bridge/
  cp integrations/thirsty_lang_complete/bridge/unified-security.py src/security/bridge/
  cp integrations/thirsty_lang_complete/bridge/README.md src/security/bridge/
  ```

- [ ] **Set file permissions**
  ```bash
  chmod 644 src/security/bridge/*.js
  chmod 644 src/security/bridge/*.py
  ```

### Configuration Setup

- [ ] **Create configuration directories**
  ```bash
  mkdir -p config policies logs
  ```

- [ ] **Create environment file**
  ```bash
  cat > .env << 'EOF'
  # TARL Configuration
  TARL_POLICY_DIR=./policies
  TARL_AUDIT_LOG=./logs/audit.log
  TARL_LOG_LEVEL=INFO
  
  # Bridge Configuration
  TARL_BRIDGE_PYTHON_PATH=python3
  TARL_BRIDGE_TIMEOUT=5000
  
  # Security Configuration
  SECURITY_STRICT_MODE=true
  SECURITY_AUDIT_ENABLED=true
  EOF
  ```

- [ ] **Create security configuration file**
  ```bash
  cat > config/security.yaml << 'EOF'
  security:
    strict_mode: true
    default_action: "deny"
    
    audit:
      enabled: true
      log_file: "./logs/audit.log"
      flush_interval_sec: 30
    
    cache:
      enabled: true
      max_size: 1000
      ttl_sec: 60
  EOF
  ```

## Phase 3: Policy Migration

### Convert Existing Policies

- [ ] **Audit existing security policies**
  - [ ] List all current policies
  - [ ] Document policy formats
  - [ ] Identify policy conflicts

- [ ] **Create TARL policy files**
  ```bash
  # Example: Create default policy
  cat > policies/default.yaml << 'EOF'
  version: "1.0"
  name: "Default Security Policy"
  
  rules:
    - id: "file_read_allowed"
      operation: "file_read"
      resource: "/home/*"
      action: "allow"
      audit: true
    
    - id: "system_files_deny"
      operation: "file_*"
      resource: "/etc/*"
      action: "deny"
      reason: "System files protected"
  EOF
  ```

- [ ] **Test policy loading**
  ```bash
  python3 -m tarl.runtime --policy-dir ./policies --validate
  ```

- [ ] **Document policy mapping**
  - [ ] Old policy → New policy mapping table
  - [ ] Note any unsupported features
  - [ ] Plan for custom policy handlers

## Phase 4: Code Integration

### JavaScript Integration

- [ ] **Update imports**
  ```javascript
  // Old:
  // const security = require('./old-security');
  
  // New:
  const { TARLBridge } = require('./security/bridge/tarl-bridge');
  ```

- [ ] **Initialize bridge in application startup**
  ```javascript
  const tarlBridge = new TARLBridge({
    pythonPath: process.env.TARL_BRIDGE_PYTHON_PATH || 'python3',
    policyDir: process.env.TARL_POLICY_DIR || './policies',
    logLevel: process.env.TARL_LOG_LEVEL || 'info'
  });
  
  await tarlBridge.initialize();
  ```

- [ ] **Replace security checkpoints**
  ```javascript
  // Old:
  // if (!security.checkAccess(file)) { ... }
  
  // New:
  const decision = await tarlBridge.evaluatePolicy({
    operation: 'file_read',
    resource: file,
    user: currentUser,
    timestamp: Date.now()
  });
  
  if (!decision.allowed) {
    throw new Error(`Access denied: ${decision.reason}`);
  }
  ```

- [ ] **Add shutdown handler**
  ```javascript
  process.on('SIGINT', async () => {
    await tarlBridge.shutdown();
    process.exit(0);
  });
  ```

### Python Integration

- [ ] **Update imports**
  ```python
  # Old:
  # from old_security import SecurityManager
  
  # New:
  from security.bridge.unified_security import UnifiedSecurityManager
  ```

- [ ] **Initialize security manager**
  ```python
  security = UnifiedSecurityManager(
      policy_dir=os.getenv('TARL_POLICY_DIR', './policies'),
      audit_log=os.getenv('TARL_AUDIT_LOG', './logs/audit.log'),
      config_file='./config/security.yaml'
  )
  
  await security.initialize()
  ```

- [ ] **Replace security checks**
  ```python
  # Old:
  # if not security.check_access(resource):
  
  # New:
  decision = await security.check_permission({
      'operation': 'file_read',
      'resource': resource,
      'user': current_user,
      'timestamp': time.time()
  })
  
  if not decision['allowed']:
      raise PermissionError(f"Access denied: {decision['reason']}")
  ```

## Phase 5: Testing

### Unit Tests

- [ ] **Create test directory structure**
  ```bash
  mkdir -p tests/integration
  ```

- [ ] **Write bridge tests**
  ```javascript
  // tests/integration/bridge.test.js
  const { TARLBridge } = require('../src/security/bridge/tarl-bridge');
  const assert = require('assert');
  
  describe('TARL Bridge', () => {
    let bridge;
    
    before(async () => {
      bridge = new TARLBridge({ logLevel: 'error' });
      await bridge.initialize();
    });
    
    after(async () => {
      await bridge.shutdown();
    });
    
    it('should evaluate policy', async () => {
      const decision = await bridge.evaluatePolicy({
        operation: 'test',
        resource: 'test.txt'
      });
      assert(typeof decision.allowed === 'boolean');
    });
  });
  ```

- [ ] **Run unit tests**
  ```bash
  npm test
  pytest tests/
  ```

### Integration Tests

- [ ] **Test file system access control**
  ```javascript
  const contexts = [
    { operation: 'file_read', resource: '/home/user/doc.txt' },
    { operation: 'file_read', resource: '/etc/passwd' },
    { operation: 'file_write', resource: '/tmp/output.txt' }
  ];
  
  for (const ctx of contexts) {
    const decision = await bridge.evaluatePolicy(ctx);
    console.log(`${ctx.operation} ${ctx.resource}: ${decision.allowed ? 'ALLOWED' : 'DENIED'}`);
  }
  ```

- [ ] **Test network access control**
- [ ] **Test resource limits**
- [ ] **Test batch operations**
- [ ] **Test policy reload**

### Performance Tests

- [ ] **Benchmark policy evaluation**
  ```bash
  npm run benchmark -- --requests 1000
  ```

- [ ] **Measure memory usage**
- [ ] **Profile CPU usage**
- [ ] **Test under load**

## Phase 6: Production Deployment

### Pre-Deployment Checks

- [ ] **Review configuration**
  - [ ] Verify all paths are correct
  - [ ] Check log rotation settings
  - [ ] Confirm resource limits
  - [ ] Validate policy files

- [ ] **Security audit**
  ```bash
  npm audit
  pip-audit
  ```

- [ ] **Run full test suite**
  ```bash
  npm run test:all
  pytest tests/ -v
  ```

### Deployment Steps

- [ ] **Stage deployment**
  - [ ] Deploy to staging environment
  - [ ] Run smoke tests
  - [ ] Monitor logs for errors
  - [ ] Validate security decisions

- [ ] **Production deployment**
  - [ ] Deploy during maintenance window
  - [ ] Enable monitoring
  - [ ] Watch error rates
  - [ ] Verify audit logs

- [ ] **Post-deployment validation**
  - [ ] Test key user workflows
  - [ ] Check security metrics
  - [ ] Review audit logs
  - [ ] Verify performance metrics

### Rollback Plan

- [ ] **Document rollback procedure**
  ```bash
  # If issues occur:
  git checkout <previous-commit>
  npm install
  pm2 restart app
  ```

- [ ] **Test rollback procedure** (in staging)

## Phase 7: Monitoring and Optimization

### Monitoring Setup

- [ ] **Configure metrics collection**
  ```javascript
  setInterval(async () => {
    const metrics = await bridge.getMetrics();
    console.log('Metrics:', metrics);
    // Send to monitoring system
  }, 60000);
  ```

- [ ] **Setup alerting**
  - [ ] Alert on high error rate
  - [ ] Alert on high latency
  - [ ] Alert on Python process crashes
  - [ ] Alert on policy violations

- [ ] **Configure log aggregation**
  - [ ] Send logs to centralized system
  - [ ] Setup log retention policy
  - [ ] Configure log alerting

### Performance Optimization

- [ ] **Enable caching**
  ```javascript
  const bridge = new TARLBridge({
    cache: {
      enabled: true,
      maxSize: 10000,
      ttl: 60000
    }
  });
  ```

- [ ] **Tune batch processing**
- [ ] **Optimize policy complexity**
- [ ] **Adjust resource limits**

### Documentation

- [ ] **Update project README**
  - [ ] Document new security architecture
  - [ ] Add usage examples
  - [ ] List configuration options

- [ ] **Create runbooks**
  - [ ] Bridge troubleshooting guide
  - [ ] Policy management procedures
  - [ ] Incident response playbook

- [ ] **Document API changes**
  - [ ] List deprecated functions
  - [ ] Document new APIs
  - [ ] Provide migration examples

## Phase 8: Team Onboarding

### Training

- [ ] **Prepare training materials**
  - [ ] Architecture overview presentation
  - [ ] Hands-on integration workshop
  - [ ] Policy writing guide
  - [ ] Troubleshooting scenarios

- [ ] **Conduct training sessions**
  - [ ] Development team training
  - [ ] Operations team training
  - [ ] Security team training

### Knowledge Transfer

- [ ] **Create documentation wiki**
  - [ ] Architecture diagrams
  - [ ] Common use cases
  - [ ] FAQ section
  - [ ] Troubleshooting guides

- [ ] **Schedule Q&A sessions**
- [ ] **Establish support channels**

## Migration Complete Checklist

- [ ] **All code migrated**
  - [ ] Security checkpoints replaced
  - [ ] Policies converted
  - [ ] Tests passing

- [ ] **Production deployment successful**
  - [ ] No critical errors
  - [ ] Performance acceptable
  - [ ] Security decisions working correctly

- [ ] **Team trained**
  - [ ] All team members trained
  - [ ] Documentation complete
  - [ ] Support channels established

- [ ] **Monitoring active**
  - [ ] Metrics collecting
  - [ ] Alerts configured
  - [ ] Logs aggregating

- [ ] **Old system decommissioned**
  - [ ] Old code removed
  - [ ] Old dependencies cleaned up
  - [ ] Old documentation archived

## Post-Migration

### Week 1
- [ ] Daily metric reviews
- [ ] Monitor error rates
- [ ] Review audit logs
- [ ] Address any issues

### Week 2-4
- [ ] Weekly performance reviews
- [ ] Optimize based on metrics
- [ ] Gather team feedback
- [ ] Update documentation

### Month 2+
- [ ] Monthly security reviews
- [ ] Policy optimization
- [ ] Performance tuning
- [ ] Feature enhancements

## Troubleshooting

### Common Issues

**Issue:** Bridge fails to start
- **Solution:** Check Python installation and TARL module
- **Command:** `python3 -c "import tarl"`

**Issue:** Policy evaluation timeout
- **Solution:** Increase timeout setting
- **Command:** `new TARLBridge({ timeout: 10000 })`

**Issue:** High memory usage
- **Solution:** Reduce cache size and enable log rotation
- **Config:** `cache.max_size: 1000` in security.yaml

**Issue:** Audit log growing too large
- **Solution:** Configure log rotation
- **Config:** Add log rotation in security.yaml

## Support Resources

- **Integration Guide:** `INTEGRATION_COMPLETE.md`
- **Bridge Documentation:** `bridge/README.md`
- **Feature List:** `FEATURES.md`
- **GitHub Issues:** https://github.com/your-org/Project-AI/issues
- **Discord Community:** https://discord.gg/thirsty-lang

---

**Migration Version:** 1.0.0  
**Last Updated:** January 2025  
**Status:** Production Ready
