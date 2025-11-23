// Simple test file using Node.js built-in test runner
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { healthCheck } from './index.js';

test('healthCheck returns valid status object', () => {
  const result = healthCheck();
  
  assert.ok(result.status, 'Status should exist');
  assert.strictEqual(result.status, 'ok', 'Status should be ok');
  assert.ok(result.timestamp, 'Timestamp should exist');
  assert.strictEqual(result.version, '1.0.0', 'Version should be 1.0.0');
});

test('healthCheck timestamp is valid ISO string', () => {
  const result = healthCheck();
  const timestamp = new Date(result.timestamp);
  
  assert.ok(!isNaN(timestamp.getTime()), 'Timestamp should be valid date');
});
