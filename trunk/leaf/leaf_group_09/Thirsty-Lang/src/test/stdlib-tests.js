/**
 * Test Runner for Thirsty-lang Standard Library
 */

const { ThirstyInterpreter } = require('../index');

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
    console.log('Running Thirsty-lang Standard Library Tests...\n');

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
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      throw new Error(message || `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
    }
  }

  assertNear(actual, expected, tolerance, message) {
    if (Math.abs(actual - expected) > tolerance) {
      throw new Error(message || `Expected ${expected} ± ${tolerance}, got ${actual}`);
    }
  }
}

const runner = new TestRunner();

// Math utilities tests
runner.test('Math.PI constant', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink pi = Math.PI');
  runner.assertNear(interpreter.variables.pi, 3.14159, 0.00001, 'PI should be approximately 3.14159');
});

runner.test('Math.E constant', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink e = Math.E');
  runner.assertNear(interpreter.variables.e, 2.71828, 0.00001, 'E should be approximately 2.71828');
});

runner.test('Math.abs function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = Math.abs(-5)');
  runner.assertEqual(interpreter.variables.result, 5, 'abs(-5) should be 5');
});

runner.test('Math.sqrt function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = Math.sqrt(16)');
  runner.assertEqual(interpreter.variables.result, 4, 'sqrt(16) should be 4');
});

runner.test('Math.pow function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = Math.pow(2, 3)');
  runner.assertEqual(interpreter.variables.result, 8, 'pow(2, 3) should be 8');
});

runner.test('Math.floor function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = Math.floor(4.7)');
  runner.assertEqual(interpreter.variables.result, 4, 'floor(4.7) should be 4');
});

runner.test('Math.ceil function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = Math.ceil(4.3)');
  runner.assertEqual(interpreter.variables.result, 5, 'ceil(4.3) should be 5');
});

runner.test('Math.round function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = Math.round(4.5)');
  runner.assertEqual(interpreter.variables.result, 5, 'round(4.5) should be 5');
});

runner.test('Math.min function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = Math.min(5, 3, 8, 1)');
  runner.assertEqual(interpreter.variables.result, 1, 'min(5,3,8,1) should be 1');
});

runner.test('Math.max function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = Math.max(5, 3, 8, 1)');
  runner.assertEqual(interpreter.variables.result, 8, 'max(5,3,8,1) should be 8');
});

runner.test('Math.random function returns value in range', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = Math.random()');
  const result = interpreter.variables.result;
  if (result < 0 || result >= 1) {
    throw new Error(`random() should return value in [0, 1), got ${result}`);
  }
});

// String utilities tests
runner.test('String.toUpperCase function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = String.toUpperCase("hello")');
  runner.assertEqual(interpreter.variables.result, 'HELLO', 'toUpperCase should convert to uppercase');
});

runner.test('String.toLowerCase function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = String.toLowerCase("HELLO")');
  runner.assertEqual(interpreter.variables.result, 'hello', 'toLowerCase should convert to lowercase');
});

runner.test('String.trim function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = String.trim("  hello  ")');
  runner.assertEqual(interpreter.variables.result, 'hello', 'trim should remove whitespace');
});

runner.test('String.split function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = String.split("a,b,c", ",")');
  runner.assertEqual(interpreter.variables.result, ['a', 'b', 'c'], 'split should split string');
});

runner.test('String.replace function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = String.replace("hello world", "world", "there")');
  runner.assertEqual(interpreter.variables.result, 'hello there', 'replace should replace substring');
});

runner.test('String.charAt function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = String.charAt("hello", 1)');
  runner.assertEqual(interpreter.variables.result, 'e', 'charAt should return character at index');
});

runner.test('String.substring function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink result = String.substring("hello world", 0, 5)');
  runner.assertEqual(interpreter.variables.result, 'hello', 'substring should extract substring');
});

// Combined usage tests
runner.test('Using Math in expressions', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
drink radius = 5
drink area = Math.PI * Math.pow(radius, 2)
  `;
  interpreter.execute(code);
  runner.assertNear(interpreter.variables.area, 78.5398, 0.001, 'Circle area calculation');
});

runner.test('Using String methods in functions', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
glass formatName(name) {
  drink trimmed = String.trim(name)
  drink upper = String.toUpperCase(trimmed)
  return upper
}
drink result = formatName("  john  ")
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.result, 'JOHN', 'Should format name correctly');
});

runner.run();
