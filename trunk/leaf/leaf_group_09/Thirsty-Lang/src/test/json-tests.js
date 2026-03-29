/**
 * JSON Support Tests
 * Comprehensive test suite for JSON.parse, JSON.stringify, and utility methods
 */

const { ThirstyInterpreter } = require('../index');

const tests = [];
let passed = 0;
let failed = 0;

function test(name, fn) {
  tests.push({ name, fn });
}

function runTests() {
  console.log('Running JSON Support Tests...\n');

  for (const { name, fn } of tests) {
    try {
      fn();
      console.log(`✓ ${name}`);
      passed++;
    } catch (error) {
      console.log(`✗ ${name}`);
      console.log(`  Error: ${error.message}`);
      failed++;
    }
  }

  console.log(`\n${tests.length} tests, ${passed} passed, ${failed} failed`);
  process.exit(failed > 0 ? 1 : 0);
}

// ============================================================================
// JSON.parse Tests - Using JavaScript to test directly
// ============================================================================

// Test 1: Parse simple object
test('JSON.parse - simple object', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.parse('{"name": "John"}');

  if (result.name !== 'John') {
    throw new Error(`Expected name "John", got: ${result.name}`);
  }
});

// Test 2: Parse number
test('JSON.parse - number', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.parse('42');

  if (result !== 42) {
    throw new Error(`Expected 42, got: ${result}`);
  }
});

// Test 3: Parse boolean
test('JSON.parse - boolean true', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.parse('true');

  if (result !== true) {
    throw new Error(`Expected true, got: ${result}`);
  }
});

// Test 4: Parse boolean false
test('JSON.parse - boolean false', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.parse('false');

  if (result !== false) {
    throw new Error(`Expected false, got: ${result}`);
  }
});

// Test 5: Parse array
test('JSON.parse - array', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.parse('[1, 2, 3]');

  if (!Array.isArray(result) || result.length !== 3) {
    throw new Error(`Expected array of length 3, got: ${JSON.stringify(result)}`);
  }
  if (result[0] !== 1 || result[1] !== 2 || result[2] !== 3) {
    throw new Error(`Expected [1,2,3], got: ${JSON.stringify(result)}`);
  }
});

// Test 6: Parse nested object
test('JSON.parse - nested object', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.parse('{"user": {"name": "Alice", "age": 30}}');

  if (result.user.name !== 'Alice' || result.user.age !== 30) {
    throw new Error(`Expected nested object with Alice/30, got: ${JSON.stringify(result)}`);
  }
});

// Test 7: Parse null
test('JSON.parse - null value', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.parse('null');

  if (result !== null) {
    throw new Error(`Expected null, got: ${result}`);
  }
});

// Test 8: Parse with whitespace
test('JSON.parse - handles whitespace', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.parse('  { "key" : "value" }  ');

  if (result.key !== 'value') {
    throw new Error(`Expected value, got: ${result.key}`);
  }
});

// Test 9: Parse error - invalid JSON
test('JSON.parse - throws on invalid JSON', () => {
  const interpreter = new ThirstyInterpreter();
  let errorThrown = false;

  try {
    interpreter.variables.JSON.parse('{invalid}');
  } catch (e) {
    errorThrown = true;
    if (!e.message.includes('JSON.parse failed')) {
      throw new Error(`Wrong error message: ${e.message}`);
    }
  }

  if (!errorThrown) {
    throw new Error('Expected error for invalid JSON');
  }
});

// Test 10: Parse error - empty string
test('JSON.parse - throws on empty string', () => {
  const interpreter = new ThirstyInterpreter();
  let errorThrown = false;

  try {
    interpreter.variables.JSON.parse('');
  } catch (e) {
    errorThrown = true;
    if (!e.message.includes('empty string')) {
      throw new Error(`Wrong error message: ${e.message}`);
    }
  }

  if (!errorThrown) {
    throw new Error('Expected error for empty string');
  }
});

// Test 11: Parse error - non-string input
test('JSON.parse - throws on non-string input', () => {
  const interpreter = new ThirstyInterpreter();
  let errorThrown = false;

  try {
    interpreter.variables.JSON.parse(42);
  } catch (e) {
    errorThrown = true;
    if (!e.message.includes('expects a string')) {
      throw new Error(`Wrong error message: ${e.message}`);
    }
  }

  if (!errorThrown) {
    throw new Error('Expected error for non-string input');
  }
});

// Test 12: Parse array of objects
test('JSON.parse - array of objects', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.parse('[{"id": 1}, {"id": 2}]');

  if (!Array.isArray(result) || result.length !== 2) {
    throw new Error(`Expected array of 2 objects, got: ${JSON.stringify(result)}`);
  }
  if (result[0].id !== 1 || result[1].id !== 2) {
    throw new Error(`Expected IDs 1 and 2, got: ${JSON.stringify(result)}`);
  }
});

// Test 13: Parse with special characters
test('JSON.parse - handles special characters', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.parse('{"text": "Line 1\\nLine 2"}');

  if (!result.text.includes('\n')) {
    throw new Error(`Expected newline in text, got: ${result.text}`);
  }
});

// Test 14: Parse mixed type array
test('JSON.parse - array with mixed types', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.parse('[1, "hello", true, null]');

  if (result[0] !== 1 || result[1] !== 'hello' || result[2] !== true || result[3] !== null) {
    throw new Error(`Expected mixed types, got: ${JSON.stringify(result)}`);
  }
});

// ============================================================================
// JSON.stringify Tests
// ============================================================================

// Test 15: Stringify simple object
test('JSON.stringify - simple object', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.stringify({ name: 'Bob' });

  if (!result.includes('"name"') || !result.includes('"Bob"')) {
    throw new Error(`Expected JSON with name/Bob, got: ${result}`);
  }
});

// Test 16: Stringify array
test('JSON.stringify - array', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.stringify([1, 2, 3]);

  if (result !== '[1,2,3]') {
    throw new Error(`Expected "[1,2,3]", got: ${result}`);
  }
});

// Test 17: Stringify with indentation
test('JSON.stringify - with indentation', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.stringify({ x: 1 }, null, 2);

  // Should have newlines for indentation
  if (!result.includes('\n') || !result.includes('"x"')) {
    throw new Error(`Expected indented JSON, got: ${result}`);
  }
});

// Test 18: Stringify nested structure
test('JSON.stringify - nested structure', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.stringify({
    nested: { value: 42 }
  });

  if (!result.includes('nested') || !result.includes('value') || !result.includes('42')) {
    throw new Error(`Expected nested JSON, got: ${result}`);
  }
});

// Test 19: Stringify null
test('JSON.stringify - null value', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.stringify(null);

  if (result !== 'null') {
    throw new Error(`Expected "null", got: ${result}`);
  }
});

// Test 20: Stringify boolean
test('JSON.stringify - boolean', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.stringify(true);

  if (result !== 'true') {
    throw new Error(`Expected "true", got: ${result}`);
  }
});

// Test 21: Stringify number
test('JSON.stringify - number', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.stringify(123);

  if (result !== '123') {
    throw new Error(`Expected "123", got: ${result}`);
  }
});

// Test 22: Stringify string
test('JSON.stringify - string', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.stringify('hello');

  if (result !== '"hello"') {
    throw new Error(`Expected quoted string, got: ${result}`);
  }
});

// Test 23: Stringify circular reference detection
test('JSON.stringify - detects circular references', () => {
  const interpreter = new ThirstyInterpreter();
  const obj = { name: 'test' };
  obj.self = obj;

  let errorThrown = false;
  try {
    interpreter.variables.JSON.stringify(obj);
  } catch (e) {
    errorThrown = true;
    if (!e.message.includes('circular')) {
      throw new Error(`Wrong error message: ${e.message}`);
    }
  }

  if (!errorThrown) {
    throw new Error('Expected circular reference error');
  }
});

// Test 24: Stringify array of objects
test('JSON.stringify - array of objects', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.stringify([{ id: 1 }, { id: 2 }]);

  if (!result.includes('"id"') || !result.includes('1') || !result.includes('2')) {
    throw new Error(`Expected array of objects, got: ${result}`);
  }
});

// Test 25: Round-trip preserves data
test('JSON round-trip - parse(stringify(x)) preserves data', () => {
  const interpreter = new ThirstyInterpreter();
  const original = {
    name: 'test',
    value: 42,
    active: true,
    items: [1, 2, 3]
  };

  const json = interpreter.variables.JSON.stringify(original);
  const parsed = interpreter.variables.JSON.parse(json);

  if (parsed.name !== 'test' || parsed.value !== 42 || parsed.active !== true) {
    throw new Error(`Round-trip failed to preserve values`);
  }
  if (!Array.isArray(parsed.items) || parsed.items.length !== 3) {
    throw new Error(`Round-trip failed to preserve array`);
  }
});

// ============================================================================
// JSON Utility Method Tests
// ============================================================================

// Test 26: JSON.isValid - valid JSON
test('JSON.isValid - returns true for valid JSON', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.isValid('{"key": "value"}');

  if (result !== true) {
    throw new Error(`Expected true for valid JSON, got: ${result}`);
  }
});

// Test 27: JSON.isValid - invalid JSON
test('JSON.isValid - returns false for invalid JSON', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.isValid('{invalid}');

  if (result !== false) {
    throw new Error(`Expected false for invalid JSON, got: ${result}`);
  }
});

// Test 28: JSON.isValid - empty string
test('JSON.isValid - returns false for empty string', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.isValid('');

  if (result !== false) {
    throw new Error(`Expected false for empty string, got: ${result}`);
  }
});

// Test 29: JSON.isValid - non-string
test('JSON.isValid - returns false for non-string', () => {
  const interpreter = new ThirstyInterpreter();
  const result = interpreter.variables.JSON.isValid(42);

  if (result !== false) {
    throw new Error(`Expected false for non-string, got: ${result}`);
  }
});

// Test 30: JSON.clone - deep clone
test('JSON.clone - creates deep clone', () => {
  const interpreter = new ThirstyInterpreter();
  const original = { nested: { value: 1 } };
  const cloned = interpreter.variables.JSON.clone(original);

  // Modify the clone
  cloned.nested.value = 99;

  // Original should be unchanged
  if (original.nested.value !== 1) {
    throw new Error(`Original was modified, expected 1, got: ${original.nested.value}`);
  }
  if (cloned.nested.value !== 99) {
    throw new Error(`Clone not modified, expected 99, got: ${cloned.nested.value}`);
  }
});

// Test 31: JSON.equals - equal values
test('JSON.equals - returns true for equal values', () => {
  const interpreter = new ThirstyInterpreter();
  const obj1 = { x: 1, y: 2 };
  const obj2 = { x: 1, y: 2 };
  const result = interpreter.variables.JSON.equals(obj1, obj2);

  if (result !== true) {
    throw new Error(`Expected true for equal values, got: ${result}`);
  }
});

// Test 32: JSON.equals - different values
test('JSON.equals - returns false for different values', () => {
  const interpreter = new ThirstyInterpreter();
  const obj1 = { x: 1 };
  const obj2 = { x: 2 };
  const result = interpreter.variables.JSON.equals(obj1, obj2);

  if (result !== false) {
    throw new Error(`Expected false for different values, got: ${result}`);
  }
});

// Test 33: JSON.equals - nested objects
test('JSON.equals - deep equality for nested objects', () => {
  const interpreter = new ThirstyInterpreter();
  const obj1 = { a: { b: { c: 1 } } };
  const obj2 = { a: { b: { c: 1 } } };
  const result = interpreter.variables.JSON.equals(obj1, obj2);

  if (result !== true) {
    throw new Error(`Expected true for equal nested objects, got: ${result}`);
  }
});

// Test 34: JSON.stringify with replacer function
test('JSON.stringify - with replacer function', () => {
  const interpreter = new ThirstyInterpreter();
  const replacer = (key, value) => {
    if (typeof value === 'number') {
      return value * 2;
    }
    return value;
  };

  const result = interpreter.variables.JSON.stringify({ x: 5, y: 10 }, replacer);

  // The replacer doubles each number value
  // Native JSON.stringify applies replacer to intermediate results,
  // so 5 becomes 10 which becomes 20, and 10 becomes 20 which becomes 40
  if (!result.includes('20') || !result.includes('40')) {
    throw new Error(`Replacer didn't double numbers, got: ${result}`);
  }
});

// Test 35: JSON.stringify with replacer array (whitelist)
test('JSON.stringify - with replacer array', () => {
  const interpreter = new ThirstyInterpreter();
  const obj = { name: 'John', age: 30, secret: 'hidden' };
  const result = interpreter.variables.JSON.stringify(obj, ['name', 'age']);

  if (result.includes('secret')) {
    throw new Error(`Secret key should be filtered out, got: ${result}`);
  }
  if (!result.includes('name') || !result.includes('age')) {
    throw new Error(`Expected name and age keys, got: ${result}`);
  }
});

// Run all tests
runTests();
