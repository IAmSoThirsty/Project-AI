#!/usr/bin/env node

/**
 * Security Module Integration Tests
 * Tests threat detection, code morphing, and defense compilation
 */

const { SecurityManager } = require('../security');
const path = require('path');

async function runTests() {
  console.log('Security Module Integration Tests\n');
  
  let passed = 0;
  let failed = 0;

  // Initialize security manager with T.A.R.L.
  const security = new SecurityManager({ useTarl: true });
  
  try {
    console.log('Initializing T.A.R.L. integration...');
    await security.initialize();
    console.log('✓ T.A.R.L. integration initialized\n');
  } catch (err) {
    console.log('! T.A.R.L. integration unavailable, running basic tests only');
    console.log('  Error:', err.message, '\n');
  }

  // Test 1: Basic HTML sanitization
  console.log('Test 1: HTML sanitization');
  try {
    const xssInput = '<script>alert("xss")</script>';
    const result = security.secureInput(xssInput);
    
    if (result.sanitized.includes('&lt;script&gt;')) {
      console.log('✓ HTML sanitization works');
      console.log('  Input:', xssInput);
      console.log('  Output:', result.sanitized);
      passed++;
    } else {
      console.log('✗ HTML sanitization failed');
      failed++;
    }
  } catch (err) {
    console.log('✗ HTML sanitization error:', err.message);
    failed++;
  }

  // Test 2: Threat detection (if available)
  if (security.initialized) {
    console.log('\nTest 2: Threat detection');
    try {
      const maliciousInput = '<script>alert("xss")</script>';
      const result = await security.detectThreats(maliciousInput, { source: 'test' });
      
      if (result && result.detected !== undefined) {
        console.log('✓ Threat detection executed');
        console.log('  Detected:', result.detected);
        console.log('  Threats:', result.threats?.length || 0);
        console.log('  Action:', result.action);
        passed++;
      } else {
        console.log('✗ Threat detection failed');
        failed++;
      }
    } catch (err) {
      console.log('✗ Threat detection error:', err.message);
      failed++;
    }

    // Test 3: Policy loading
    console.log('\nTest 3: Policy loading');
    try {
      const policyPath = path.join(__dirname, '..', '..', 'tarl', 'policies', 'default.json');
      const result = await security.loadPolicies(policyPath);
      
      if (result && result.loaded !== undefined) {
        console.log('✓ Policies loaded');
        console.log('  Count:', result.loaded);
        console.log('  Policies:', result.policies.join(', '));
        passed++;
      } else {
        console.log('✗ Policy loading failed');
        failed++;
      }
    } catch (err) {
      console.log('✗ Policy loading error:', err.message);
      failed++;
    }

    // Test 4: Defensive compilation
    console.log('\nTest 4: Defensive compilation');
    try {
      const code = 'drink water = "Hello, World!"\npour water';
      const result = await security.compileSecure(code, { source: 'test' });
      
      if (result && result.code) {
        console.log('✓ Defensive compilation executed');
        console.log('  Transformations:', result.transformations?.join(', ') || 'none');
        console.log('  Threats:', result.threats?.length || 0);
        passed++;
      } else {
        console.log('✗ Defensive compilation failed');
        failed++;
      }
    } catch (err) {
      console.log('✗ Defensive compilation error:', err.message);
      failed++;
    }
  } else {
    console.log('\nSkipping T.A.R.L.-dependent tests (not initialized)');
  }

  // Cleanup
  if (security.initialized) {
    await security.shutdown();
    console.log('\n✓ Security manager shutdown');
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
