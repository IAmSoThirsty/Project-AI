/**
 * Test Runner for Thirsty-lang Functions
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
    console.log('Running Thirsty-lang Function Tests...\n');

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

// Test function declaration
runner.test('Function declaration with no parameters', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
glass greet() {
  pour "Hello!"
}
  `;
  interpreter.execute(code);
  runner.assertEqual(typeof interpreter.functions.greet, 'object', 'Function should be declared');
  runner.assertEqual(interpreter.functions.greet.params.length, 0, 'Function should have no params');
});

runner.test('Function declaration with parameters', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
glass add(a, b) {
  return a + b
}
  `;
  interpreter.execute(code);
  runner.assertEqual(typeof interpreter.functions.add, 'object', 'Function should be declared');
  runner.assertEqual(interpreter.functions.add.params.length, 2, 'Function should have 2 params');
  runner.assertEqual(interpreter.functions.add.params[0], 'a', 'First param should be a');
  runner.assertEqual(interpreter.functions.add.params[1], 'b', 'Second param should be b');
});

// Test function calls
runner.test('Function call with return value', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
glass add(a, b) {
  return a + b
}
drink result = add(5, 3)
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.result, 8, 'Function should return sum');
});

runner.test('Function call with no return value', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let output = '';
  console.log = (msg) => { output = msg; };
  
  const code = `
glass greet() {
  pour "Hello, World!"
}
greet()
  `;
  interpreter.execute(code);
  console.log = oldLog;
  
  runner.assertEqual(output, 'Hello, World!', 'Function should execute and print');
});

runner.test('Function with variable scope', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
drink x = 10
glass modify(val) {
  return val * 2
}
drink result = modify(5)
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.x, 10, 'Outer variable should not be modified');
  runner.assertEqual(interpreter.variables.result, 10, 'Function should return modified value');
});

runner.test('Function with string parameters', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
glass greet(name) {
  return "Hello, " + name
}
drink message = greet("Thirsty")
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.message, 'Hello, Thirsty', 'Function should concatenate strings');
});

runner.test('Function with multiple operations', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
glass calculate(a, b, c) {
  drink sum = a + b
  drink result = sum * c
  return result
}
drink answer = calculate(2, 3, 4)
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.answer, 20, 'Function should calculate (2+3)*4');
});

runner.test('Nested function calls', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
glass double(x) {
  return x * 2
}
glass quadruple(x) {
  return double(double(x))
}
drink result = quadruple(3)
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.result, 12, 'Function should call nested functions');
});

runner.test('Function call in pour statement', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let output = '';
  console.log = (msg) => { output = msg; };
  
  const code = `
glass getMessage() {
  return "Hydrate!"
}
pour getMessage()
  `;
  interpreter.execute(code);
  console.log = oldLog;
  
  runner.assertEqual(output, 'Hydrate!', 'Function return value should be printed');
});

runner.test('Function with conditional logic', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
glass max(a, b) {
  thirsty a > b {
    return a
  }
  hydrated {
    return b
  }
}
drink result = max(10, 5)
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.result, 10, 'Function should return maximum value');
});

// Error handling tests
runner.test('Error: Undefined function call', () => {
  const interpreter = new ThirstyInterpreter();
  try {
    interpreter.execute('drink x = unknownFunc()');
    throw new Error('Should have thrown an error');
  } catch (error) {
    runner.assertEqual(error.message.includes('Undefined'), true, 'Should error on undefined function');
  }
});

runner.test('Error: Wrong number of arguments', () => {
  const interpreter = new ThirstyInterpreter();
  try {
    const code = `
glass add(a, b) {
  return a + b
}
drink result = add(5)
    `;
    interpreter.execute(code);
    throw new Error('Should have thrown an error');
  } catch (error) {
    runner.assertEqual(error.message.includes('expects 2 arguments'), true, 'Should error on wrong arg count');
  }
});

runner.run();
