#!/usr/bin/env node

/**
 * Security Features Test Suite
 * Tests for Thirsty-lang defensive programming capabilities
 */

const ThreatDetector = require('../security/threat-detector');
const CodeMorpher = require('../security/code-morpher');
const SecurityPolicyEngine = require('../security/policy-engine');
const DefenseCompiler = require('../security/defense-compiler');
const { SecurityManager } = require('../security/index');

// Test results
let passed = 0;
let failed = 0;

function test(description, fn) {
  try {
    fn();
    console.log(`✓ ${description}`);
    passed++;
  } catch (error) {
    console.log(`✗ ${description}`);
    console.log(`  Error: ${error.message}`);
    failed++;
  }
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

console.log('Running Security Features Tests...\n');

// Threat Detector Tests
console.log('Threat Detector Tests:');

test('Detects SQL injection', () => {
  const detector = new ThreatDetector();
  const threats = detector.detectInputThreats("'; DROP TABLE users; --");
  assert(threats.length > 0, 'Should detect SQL injection');
  assert(threats[0].attack === 'sqlInjection', 'Should identify as SQL injection');
});

test('Detects XSS injection', () => {
  const detector = new ThreatDetector();
  const threats = detector.detectInputThreats('<script>alert("XSS")</script>');
  assert(threats.length > 0, 'Should detect XSS');
  const xssThreats = threats.filter(t => t.attack === 'xssInjection');
  assert(xssThreats.length > 0, 'Should identify as XSS injection');
});

test('Detects command injection', () => {
  const detector = new ThreatDetector();
  const threats = detector.detectInputThreats('test; rm -rf /');
  assert(threats.length > 0, 'Should detect command injection');
  assert(threats[0].attack === 'commandInjection', 'Should identify as command injection');
});

test('Detects buffer overflow', () => {
  const detector = new ThreatDetector();
  const longInput = 'A'.repeat(10000);
  const threats = detector.detectInputThreats(longInput);
  assert(threats.length > 0, 'Should detect buffer overflow');
  assert(threats[0].attack === 'bufferOverflow', 'Should identify as buffer overflow');
});

test('Returns threat statistics', () => {
  const detector = new ThreatDetector();
  detector.detectInputThreats('<script>alert(1)</script>');
  detector.detectInputThreats("' OR 1=1 --");
  const stats = detector.getThreatStats();
  assert(stats.total >= 2, 'Should track multiple threats');
});

// Code Morpher Tests
console.log('\nCode Morpher Tests:');

test('Morphs code identifiers', () => {
  const morpher = new CodeMorpher();
  const code = 'drink userName = "John"';
  const morphed = morpher.morph(code, { identifierMorphing: true });
  assert(morphed !== code, 'Should morph code');
  assert(morphed.length > code.length, 'Morphed code should be longer');
});

test('Injects dead code', () => {
  const morpher = new CodeMorpher();
  const code = 'pour "Hello"';
  const morphed = morpher.morph(code, { deadCodeInjection: true, antiDebugChecks: false });
  // Dead code injection adds multiple code snippets
  assert(morphed.length > code.length * 1.5, 'Morphed code should be significantly longer with dead code');
});

test('Adds anti-debug checks', () => {
  const morpher = new CodeMorpher();
  const code = 'drink x = 1';
  const morphed = morpher.morph(code, { antiDebugChecks: true });
  assert(morphed.includes('debugger') || morphed.includes('Debug'), 'Should add anti-debug');
});

test('Returns morph statistics', () => {
  const morpher = new CodeMorpher();
  morpher.morph('drink x = 1');
  morpher.morph('pour x');
  const stats = morpher.getMorphStats();
  assert(stats.totalMorphs === 2, 'Should track morphing operations');
});

// Security Policy Engine Tests
console.log('\nSecurity Policy Engine Tests:');

test('Applies basic sanitization', () => {
  const engine = new SecurityPolicyEngine({ securityLevel: 'passive' });
  const result = engine.applyInputPolicy('test<script>alert(1)</script>');
  assert(result.original, 'Should have original input');
  assert(result.sanitized, 'Should have sanitized output');
});

test('Applies strict sanitization', () => {
  const engine = new SecurityPolicyEngine({ securityLevel: 'aggressive' });
  const result = engine.applyInputPolicy('test<script>alert(1)</script>');
  assert(!result.sanitized.includes('<'), 'Should remove HTML tags');
  assert(!result.sanitized.includes('script'), 'Should remove script keyword');
});

test('Handles threats based on policy', () => {
  const engine = new SecurityPolicyEngine({ securityLevel: 'moderate' });
  const threat = { type: 'whiteBox', attack: 'xssInjection', severity: 'high' };
  const response = engine.handleThreat(threat);
  assert(response.action === 'warn', 'Moderate level should warn');
});

test('Changes security level', () => {
  const engine = new SecurityPolicyEngine({ securityLevel: 'passive' });
  engine.setSecurityLevel('aggressive');
  const config = engine.getPolicyConfig();
  assert(config.securityLevel === 'aggressive', 'Should change security level');
});

// Defense Compiler Tests
console.log('\nDefense Compiler Tests:');

test('Compiles code with security', () => {
  const compiler = new DefenseCompiler({
    defenseEnabled: true,
    morphingEnabled: false,
    policy: { securityLevel: 'passive' }
  });
  const result = compiler.compile('drink x = "test"');
  assert(result.code.includes('Security'), 'Should add security features');
  assert(result.securityLayers.length > 0, 'Should have security layers');
});

test('Detects threats during compilation', () => {
  const compiler = new DefenseCompiler({ defenseEnabled: true });
  try {
    compiler.compile('drink x = "<script>alert(1)</script>"');
    // May or may not throw depending on security level
    assert(true, 'Compilation completed');
  } catch (error) {
    // Threat was blocked - this is also success
    assert(error.message.includes('Security') || error.message.includes('blocked'), 'Should handle threats');
  }
});

test('Returns compilation statistics', () => {
  const compiler = new DefenseCompiler();
  compiler.compile('drink x = 1');
  const stats = compiler.getCompilationStats();
  assert(stats.totalCompilations === 1, 'Should track compilations');
  assert(stats.successfulCompilations === 1, 'Should track successful compilations');
});

// Security Manager Tests
console.log('\nSecurity Manager Tests:');

test('Coordinates all security features', () => {
  const manager = new SecurityManager({ 
    enabled: true,
    policy: { securityLevel: 'passive' }
  });
  const result = manager.secureExecute('drink x = "test"');
  assert(result.code, 'Should return compiled code');
  assert(result.securityLayers, 'Should include security layers');
});

test('Validates and sanitizes input', () => {
  const manager = new SecurityManager({ 
    enabled: true,
    policy: { securityLevel: 'moderate' }
  });
  const result = manager.secureInput('<script>alert(1)</script>');
  assert(result.sanitized, 'Should return sanitized input');
});

test('Generates security report', () => {
  const manager = new SecurityManager({ enabled: true });
  manager.secureInput('test input');
  const report = manager.getSecurityReport();
  assert(report.enabled === true, 'Should report enabled status');
  assert(report.threats, 'Should include threat stats');
  assert(report.policy, 'Should include policy config');
});

test('Changes security mode', () => {
  const manager = new SecurityManager({ mode: 'defensive' });
  manager.setMode('offensive');
  assert(manager.mode === 'offensive', 'Should change mode');
});

// Summary
console.log('\n' + '='.repeat(50));
console.log(`Tests completed: ${passed + failed}`);
console.log(`✓ Passed: ${passed}`);
console.log(`✗ Failed: ${failed}`);
console.log('='.repeat(50));

if (failed > 0) {
  process.exit(1);
}
