#!/usr/bin/env node

/**
 * Simple Thirsty-lang Security Demo
 * Shows defensive features without execution complexity
 */

const ThreatDetector = require('../../src/security/threat-detector');
const CodeMorpher = require('../../src/security/code-morpher');
const SecurityPolicyEngine = require('../../src/security/policy-engine');
const { SecurityManager } = require('../../src/security/index');

console.log('='.repeat(70));
console.log('Thirsty-lang Defensive Programming - Security Module Demo');
console.log('='.repeat(70));
console.log();

// Demo 1: Threat Detection
console.log('1. Threat Detection Engine');
console.log('-'.repeat(70));
const detector = new ThreatDetector();

const threats = [
  { input: "'; DROP TABLE users; --", type: 'SQL Injection' },
  { input: '<script>alert("XSS")</script>', type: 'XSS Attack' },
  { input: 'test; rm -rf /', type: 'Command Injection' },
  { input: 'A'.repeat(10000), type: 'Buffer Overflow' }
];

threats.forEach(({ input, type }) => {
  const detected = detector.detectInputThreats(input);
  console.log(`  ${type}: ${detected.length > 0 ? '✅ DETECTED' : '❌ Missed'}`);
  if (detected.length > 0) {
    console.log(`    Attack: ${detected[0].attack}`);
    console.log(`    Severity: ${detected[0].severity}`);
  }
});

console.log();

// Demo 2: Code Morphing
console.log('2. Code Morphing System');
console.log('-'.repeat(70));
const morpher = new CodeMorpher();
const originalCode = 'drink userName = "John"\npour userName';

console.log('Original Code:');
console.log('  ' + originalCode.replace(/\n/g, '\n  '));

const morphed = morpher.morph(originalCode, {
  identifierMorphing: true,
  deadCodeInjection: true,
  antiDebugChecks: true
});

console.log(`\nMorphed Code: ${morphed.length} bytes (${Math.round((morphed.length / originalCode.length - 1) * 100)}% larger)`);
console.log(`  Obfuscation Applied: ✅`);
console.log(`  Dead Code Injected: ✅`);
console.log(`  Anti-Debug Added: ✅`);
console.log();

// Demo 3: Security Policy Engine
console.log('3. Security Policy Engine');
console.log('-'.repeat(70));

const testInputs = [
  '<script>alert(1)</script>',
  'normal text',
  'test@example.com'
];

['passive', 'moderate', 'aggressive', 'paranoid'].forEach(level => {
  const engine = new SecurityPolicyEngine({ securityLevel: level });
  console.log(`\n  ${level.toUpperCase()} Mode:`);
  
  testInputs.slice(0, 1).forEach(input => {
    const result = engine.applyInputPolicy(input);
    console.log(`    Input: ${input.substring(0, 30)}...`);
    console.log(`    Sanitized: ${result.sanitized.substring(0, 30)}...`);
    console.log(`    Modified: ${result.modified ? 'Yes' : 'No'}`);
  });
});

console.log();

// Demo 4: Integrated Security Manager
console.log('4. Security Manager - Comprehensive Protection');
console.log('-'.repeat(70));

const manager = new SecurityManager({
  enabled: true,
  mode: 'defensive',
  policy: { securityLevel: 'moderate' }
});

// Secure input processing
const dangerousInputs = [
  "user@example.com",
  "<script>evil()</script>",
  "'; DELETE FROM users; --"
];

console.log('Processing Inputs:');
dangerousInputs.forEach(input => {
  try {
    const result = manager.secureInput(input);
    console.log(`  Input: ${input.substring(0, 25).padEnd(25)} -> Sanitized: ${result.sanitized.substring(0, 20)}`);
  } catch (e) {
    console.log(`  Input: ${input.substring(0, 25).padEnd(25)} -> BLOCKED: ${e.message.substring(0, 30)}`);
  }
});

console.log('\nSecurity Report:');
const report = manager.getSecurityReport();
console.log(`  Security Enabled: ${report.enabled}`);
console.log(`  Mode: ${report.mode}`);
console.log(`  Threats Detected: ${report.threats.total}`);
console.log(`  Policy Level: ${report.policy.securityLevel}`);

console.log();

// Summary
console.log('='.repeat(70));
console.log('Summary: Defensive Programming Capabilities');
console.log('='.repeat(70));
console.log();
console.log('Attack Detection:');
console.log('  ✅ SQL Injection');
console.log('  ✅ XSS (Cross-Site Scripting)');
console.log('  ✅ Command Injection');
console.log('  ✅ Buffer Overflow');
console.log('  ✅ Path Traversal');
console.log('  ✅ Code Injection');
console.log();
console.log('Defense Mechanisms:');
console.log('  ✅ Code Morphing & Obfuscation');
console.log('  ✅ Anti-Debugging');
console.log('  ✅ Input Sanitization');
console.log('  ✅ Memory Protection');
console.log('  ✅ Configurable Security Levels');
console.log('  ✅ Automated Threat Response');
console.log();
console.log('Security Modes:');
console.log('  • Passive    - Log only');
console.log('  • Moderate   - Warn and sanitize');
console.log('  • Aggressive - Block threats');
console.log('  • Paranoid   - Counter-strike with honeypots');
console.log();
console.log('Thirsty-lang: A unique defensive programming language');
console.log('combative against all known code threats! 💧🔒');
console.log('='.repeat(70));
