/**
 * Test Runner for Thirsty-lang
 */

const ThirstyInterpreter = require('../index');

class TestRunner {
  constructor() {
    this.passed = 0;
    this.failed = 0;
    this.tests = [];
  }

  test(name, fn) {
    this.tests.push({ name, fn });
  }

  run() {
    console.log('Running Thirsty-lang Tests...\n');

    for (const { name, fn } of this.tests) {
      try {
        fn();
        this.passed++;
        console.log(`✓ ${name}`);
      } catch (error) {
        this.failed++;
        console.log(`✗ ${name}`);
        console.log(`  ${error.message}`);
      }
    }

    console.log(`\n${this.passed + this.failed} tests, ${this.passed} passed, ${this.failed} failed`);
    process.exit(this.failed > 0 ? 1 : 0);
  }

  assertEqual(actual, expected, message) {
    if (actual !== expected) {
      throw new Error(message || `Expected ${expected}, got ${actual}`);
    }
  }
}

const runner = new TestRunner();

// Test variable declaration and retrieval
runner.test('Variable declaration with string', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink water = "H2O"');
  runner.assertEqual(interpreter.variables.water, 'H2O', 'Variable should store string value');
});

runner.test('Variable declaration with number', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink amount = 42');
  runner.assertEqual(interpreter.variables.amount, 42, 'Variable should store number value');
});

runner.test('Pour statement with literal', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let output = '';
  console.log = (msg) => { output = msg; };
  
  interpreter.execute('pour "Hello, Thirsty World!"');
  console.log = oldLog;
  
  runner.assertEqual(output, 'Hello, Thirsty World!', 'Should output literal string');
});

runner.test('Pour statement with variable', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let output = '';
  console.log = (msg) => { output = msg; };
  
  interpreter.execute('drink message = "Hydrate!"\npour message');
  console.log = oldLog;
  
  runner.assertEqual(output, 'Hydrate!', 'Should output variable value');
});

runner.test('Multiple statements', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink a = 1\ndrink b = 2\ndrink c = 3');
  runner.assertEqual(interpreter.variables.a, 1);
  runner.assertEqual(interpreter.variables.b, 2);
  runner.assertEqual(interpreter.variables.c, 3);
});

runner.test('Comments are ignored', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('// This is a comment\ndrink water = "clean"');
  runner.assertEqual(interpreter.variables.water, 'clean', 'Comments should be ignored');
});

runner.run();
