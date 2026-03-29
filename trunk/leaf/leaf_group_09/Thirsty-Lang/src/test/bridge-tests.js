#!/usr/bin/env node

/**
 * Security Bridge Integration Tests
 * Tests the JS <-> Python T.A.R.L. bridge
 */

const { SecurityBridge } = require('../security/bridge');
const path = require('path');

async function runTests() {
  console.log('Security Bridge Integration Tests\n');
  
  let passed = 0;
  let failed = 0;

  // Test 1: Bridge initialization
  console.log('Test 1: Bridge initialization');
  try {
    const bridge = new SecurityBridge();
    await bridge.initialize();
    console.log('✓ Bridge initialized successfully');
    passed++;
    
    // Test 2: Policy evaluation
    console.log('\nTest 2: Policy evaluation');
    try {
      const result = await bridge.evaluatePolicy({
        action: 'test',
        source: 'integration_test'
      });
      
      if (result && result.verdict) {
        console.log('✓ Policy evaluation successful');
        console.log('  Verdict:', result.verdict);
        console.log('  Reason:', result.reason);
        passed++;
      } else {
        console.log('✗ Policy evaluation failed - invalid result');
        failed++;
      }
    } catch (err) {
      console.log('✗ Policy evaluation failed:', err.message);
      failed++;
    }

    // Test 3: Load policies
    console.log('\nTest 3: Load policies from file');
    try {
      const policyPath = path.join(__dirname, '..', '..', 'tarl', 'policies', 'default.json');
      const result = await bridge.loadPolicies(policyPath);
      
      if (result && result.status === 'loaded') {
        console.log('✓ Policies loaded successfully');
        console.log('  Count:', result.policy_count);
        passed++;
      } else {
        console.log('✗ Policy loading failed');
        failed++;
      }
    } catch (err) {
      console.log('✗ Policy loading failed:', err.message);
      failed++;
    }

    // Test 4: Get metrics
    console.log('\nTest 4: Get runtime metrics');
    try {
      const metrics = await bridge.getRuntimeMetrics();
      
      if (metrics) {
        console.log('✓ Metrics retrieved successfully');
        console.log('  Total evaluations:', metrics.runtime?.total_evaluations || 0);
        passed++;
      } else {
        console.log('✗ Metrics retrieval failed');
        failed++;
      }
    } catch (err) {
      console.log('✗ Metrics retrieval failed:', err.message);
      failed++;
    }

    // Test 5: Bridge metrics
    console.log('\nTest 5: Get bridge metrics');
    try {
      const metrics = bridge.getBridgeMetrics();
      
      if (metrics && metrics.requests !== undefined) {
        console.log('✓ Bridge metrics retrieved');
        console.log('  Requests:', metrics.requests);
        console.log('  Successes:', metrics.successes);
        console.log('  Avg response time:', metrics.avgResponseTime.toFixed(2), 'ms');
        passed++;
      } else {
        console.log('✗ Bridge metrics failed');
        failed++;
      }
    } catch (err) {
      console.log('✗ Bridge metrics failed:', err.message);
      failed++;
    }

    // Cleanup
    await bridge.shutdown();
    console.log('\n✓ Bridge shutdown successfully');
    
  } catch (err) {
    console.log('✗ Bridge initialization failed:', err.message);
    failed++;
  }

  // Summary
  console.log('\n' + '='.repeat(50));
  console.log(`Tests completed: ${passed + failed}`);
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);
  console.log('='.repeat(50));

  process.exit(failed > 0 ? 1 : 0);
}

// Run tests
runTests().catch(err => {
  console.error('Test suite failed:', err);
  process.exit(1);
});
