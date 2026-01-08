#!/usr/bin/env node

/**
 * Thirsty-lang Defensive Programming Demo
 * Demonstrates security features in action
 */

const SecureThirstyInterpreter = require('../../src/secure-interpreter');

console.log('='.repeat(70));
console.log('Thirsty-lang Defensive Programming Demo');
console.log('Demonstrating combative security against all attack types');
console.log('='.repeat(70));
console.log();

// Demo 1: Basic Protection
console.log('Demo 1: Basic Shield Protection');
console.log('-'.repeat(70));
const demo1Code = `shield basicDemo {
  drink message = "Hello, Secure World!"
  pour message
}`;

const interpreter1 = new SecureThirstyInterpreter({
  security: true,
  securityLevel: 'moderate'
});

console.log('Code:');
console.log(demo1Code);
console.log('\nExecution:');
try {
  interpreter1.execute(demo1Code);
} catch (e) {
  console.log('Error:', e.message);
}
console.log();

// Demo 2: Attack Detection
console.log('Demo 2: SQL Injection Detection & Blocking');
console.log('-'.repeat(70));
const demo2Code = `shield sqlProtection {
  detect attacks {
    defend with: "aggressive"
  }
  drink maliciousInput = "test'; DROP TABLE users; --"
  sanitize maliciousInput
  pour maliciousInput
}`;

const interpreter2 = new SecureThirstyInterpreter({
  security: true,
  securityLevel: 'aggressive'
});

console.log('Code:');
console.log(demo2Code);
console.log('\nExecution:');
try {
  interpreter2.execute(demo2Code);
} catch (e) {
  console.log('Security Response:', e.message);
}
console.log();

// Demo 3: Paranoid Mode with Counter-Strike
console.log('Demo 3: Paranoid Mode - Counter-Strike Enabled');
console.log('-'.repeat(70));
const demo3Code = `shield paranoidDemo {
  detect attacks {
    morph on: ["injection", "overflow"]
    defend with: "paranoid"
  }
  drink xssAttempt = "<script>alert('XSS')</script>"
  sanitize xssAttempt
  armor xssAttempt
  pour xssAttempt
}`;

const interpreter3 = new SecureThirstyInterpreter({
  security: true,
  securityLevel: 'paranoid'
});

console.log('Code:');
console.log(demo3Code);
console.log('\nExecution:');
try {
  interpreter3.execute(demo3Code);
} catch (e) {
  console.log('Counter-Strike Activated:', e.message);
}
console.log();

// Demo 4: Security Report
console.log('Demo 4: Security Report');
console.log('-'.repeat(70));
const interpreter4 = new SecureThirstyInterpreter({
  security: true,
  securityLevel: 'moderate'
});

interpreter4.execute(`shield reportDemo {
  drink safe = "clean data"
  sanitize safe
  pour safe
}`);

const report = interpreter4.getSecurityReport();
console.log('Security Status:');
console.log(`  Enabled: ${report.enabled}`);
console.log(`  Active Shields: ${report.shields.length}`);
console.log(`  Morphing: ${report.morphing}`);
console.log(`  Defense Strategy: ${report.defense}`);
if (report.report && report.report.threats) {
  console.log(`  Threats Detected: ${report.report.threats.total || 0}`);
}
console.log();

// Summary
console.log('='.repeat(70));
console.log('Summary: Thirsty-lang Defensive Features');
console.log('='.repeat(70));
console.log('✅ Shield-based protection');
console.log('✅ Real-time threat detection');
console.log('✅ Automatic sanitization');
console.log('✅ Memory protection (armor)');
console.log('✅ Attack blocking (aggressive mode)');
console.log('✅ Counter-strike capabilities (paranoid mode)');
console.log('✅ Comprehensive security reporting');
console.log();
console.log('Thirsty-lang: Defensive by design, combative by nature! 💧🔒');
console.log('='.repeat(70));
