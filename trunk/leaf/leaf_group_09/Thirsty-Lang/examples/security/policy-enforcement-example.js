#!/usr/bin/env node

/**
 * Example: Policy Enforcement
 * Demonstrates loading and enforcing security policies
 */

const { SecurityManager } = require('../../src/security');
const path = require('path');

async function main() {
  console.log('=== Policy Enforcement Example ===\n');

  const security = new SecurityManager({ useTarl: true });
  
  try {
    // Initialize
    console.log('Initializing security...');
    await security.initialize();
    console.log('✓ Initialized\n');

    // Load policies
    console.log('Loading security policies...');
    const policyPath = path.join(__dirname, '..', '..', 'tarl', 'policies', 'default.json');
    const loadResult = await security.loadPolicies(policyPath);
    
    console.log('✓ Loaded', loadResult.loaded, 'policies');
    console.log('  Policies:', loadResult.policies.join(', '));
    console.log();

    // Test 1: Policy-enforced threat detection
    console.log('Test 1: Threat with Policy Enforcement');
    const maliciousCode = '<script>document.cookie</script>';
    const result = await security.detectThreats(maliciousCode, { 
      source: 'external',
      action: 'threat_detected'
    });
    
    console.log('Input:', maliciousCode);
    console.log('Detected:', result.detected);
    console.log('Action:', result.action);
    console.log('Reason:', result.reason);

    // Test 2: Defensive compilation
    console.log('\nTest 2: Defensive Compilation with Policy');
    const thirstyCode = `
drink water = "Hello"
pour water
`;
    
    const compiled = await security.compileSecure(thirstyCode, {
      source: 'trusted',
      mode: 'production'
    });
    
    console.log('Original code length:', compiled.original.length);
    console.log('Compiled code length:', compiled.code.length);
    console.log('Transformations:', compiled.transformations.join(', '));
    console.log('Threats found:', compiled.threats.length);

    // Enable hot-reload
    if (security.policyEngine) {
      console.log('\nEnabling policy hot-reload...');
      security.policyEngine.enableHotReload();
      console.log('✓ Hot-reload enabled');
      console.log('  (Policies will auto-reload when file changes)');
      
      // Disable for this demo
      security.policyEngine.disableHotReload();
    }

    // Get metrics
    console.log('\n=== Metrics ===');
    if (security.bridge) {
      const bridgeMetrics = security.bridge.getBridgeMetrics();
      console.log('Bridge requests:', bridgeMetrics.requests);
      console.log('Success rate:', 
        ((bridgeMetrics.successes / bridgeMetrics.requests) * 100).toFixed(1) + '%'
      );
      console.log('Avg response time:', bridgeMetrics.avgResponseTime.toFixed(2), 'ms');
    }

  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  } finally {
    await security.shutdown();
    console.log('\n✓ Shutdown complete');
  }
}

main();
