#!/usr/bin/env node

/**
 * Example: Basic Threat Detection
 * Demonstrates threat detection with T.A.R.L. integration
 */

const { SecurityManager } = require('../../src/security');

async function main() {
  console.log('=== Threat Detection Example ===\n');

  // Initialize security manager
  const security = new SecurityManager({ useTarl: true });
  
  try {
    console.log('Initializing T.A.R.L. security...');
    await security.initialize();
    console.log('✓ Security initialized\n');

    // Test 1: XSS Detection
    console.log('Test 1: XSS Detection');
    const xssInput = '<script>alert("xss")</script>';
    const xssResult = await security.detectThreats(xssInput, { source: 'user_input' });
    
    console.log('Input:', xssInput);
    console.log('Detected:', xssResult.detected);
    console.log('Threats:', xssResult.threats.length);
    console.log('Action:', xssResult.action);
    console.log('Reason:', xssResult.reason);
    
    if (xssResult.threats.length > 0) {
      xssResult.threats.forEach((threat, i) => {
        console.log(`  Threat ${i + 1}:`, threat.type, `(${threat.severity})`);
      });
    }

    // Test 2: SQL Injection Detection
    console.log('\nTest 2: SQL Injection Detection');
    const sqlInput = "' OR '1'='1' --";
    const sqlResult = await security.detectThreats(sqlInput, { source: 'database_query' });
    
    console.log('Input:', sqlInput);
    console.log('Detected:', sqlResult.detected);
    console.log('Action:', sqlResult.action);
    
    // Test 3: Safe Input
    console.log('\nTest 3: Safe Input');
    const safeInput = 'Hello, World!';
    const safeResult = await security.detectThreats(safeInput, { source: 'user_input' });
    
    console.log('Input:', safeInput);
    console.log('Detected:', safeResult.detected);
    console.log('Action:', safeResult.action);

    // Get metrics
    console.log('\n=== Metrics ===');
    if (security.threatDetector) {
      const metrics = security.threatDetector.getMetrics();
      console.log('Threats detected:', metrics.threatsDetected);
      console.log('Policy enforced:', metrics.policyEnforced);
    }

  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  } finally {
    await security.shutdown();
    console.log('\n✓ Security shutdown complete');
  }
}

main();
