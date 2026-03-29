/**
 * Test Runner for Thirsty-lang Arrays
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
    console.log('Running Thirsty-lang Array Tests...\n');

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
}

const runner = new TestRunner();

// Test array declaration
runner.test('Array declaration with elements', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir numbers = [1, 2, 3, 4, 5]');
  runner.assertEqual(interpreter.variables.numbers, [1, 2, 3, 4, 5], 'Array should be created with elements');
});

runner.test('Array declaration with string elements', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir fruits = ["apple", "banana", "orange"]');
  runner.assertEqual(interpreter.variables.fruits, ['apple', 'banana', 'orange'], 'Array should store strings');
});

runner.test('Empty array declaration', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir empty = []');
  runner.assertEqual(interpreter.variables.empty, [], 'Empty array should be created');
});

runner.test('Array declaration with mixed types', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir mixed = [1, "two", 3]');
  runner.assertEqual(interpreter.variables.mixed, [1, 'two', 3], 'Array should support mixed types');
});

// Test array access
runner.test('Array element access', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir data = [10, 20, 30]\ndrink value = data[1]');
  runner.assertEqual(interpreter.variables.value, 20, 'Should access array element');
});

runner.test('Array access with expression index', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir data = [5, 10, 15]\ndrink index = 2\ndrink value = data[index]');
  runner.assertEqual(interpreter.variables.value, 15, 'Should access array with variable index');
});

// Test array assignment
runner.test('Array element assignment', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir data = [1, 2, 3]\ndrink data[1] = 99');
  runner.assertEqual(interpreter.variables.data, [1, 99, 3], 'Should modify array element');
});

// Test array length
runner.test('Array length property', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir items = [1, 2, 3, 4]\ndrink count = items.length');
  runner.assertEqual(interpreter.variables.count, 4, 'Should get array length');
});

// Test array methods - push
runner.test('Array push method', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir stack = [1, 2, 3]\ndrink newLen = stack.push(4)');
  runner.assertEqual(interpreter.variables.stack, [1, 2, 3, 4], 'Should push element');
  runner.assertEqual(interpreter.variables.newLen, 4, 'Should return new length');
});

// Test array methods - pop
runner.test('Array pop method', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir stack = [1, 2, 3]\ndrink last = stack.pop()');
  runner.assertEqual(interpreter.variables.stack, [1, 2], 'Should remove last element');
  runner.assertEqual(interpreter.variables.last, 3, 'Should return popped element');
});

// Test array methods - shift
runner.test('Array shift method', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir queue = [1, 2, 3]\ndrink first = queue.shift()');
  runner.assertEqual(interpreter.variables.queue, [2, 3], 'Should remove first element');
  runner.assertEqual(interpreter.variables.first, 1, 'Should return shifted element');
});

// Test array methods - unshift
runner.test('Array unshift method', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir queue = [2, 3]\ndrink newLen = queue.unshift(1)');
  runner.assertEqual(interpreter.variables.queue, [1, 2, 3], 'Should add element at start');
  runner.assertEqual(interpreter.variables.newLen, 3, 'Should return new length');
});

// Test array methods - indexOf
runner.test('Array indexOf method', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir items = [10, 20, 30]\ndrink pos = items.indexOf(20)');
  runner.assertEqual(interpreter.variables.pos, 1, 'Should find element index');
});

// Test array methods - includes
runner.test('Array includes method', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir items = [1, 2, 3]\ndrink has = items.includes(2)');
  runner.assertEqual(interpreter.variables.has, true, 'Should return true for existing element');
});

// Test array methods - join
runner.test('Array join method', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('reservoir words = ["Hello", "World"]\ndrink sentence = words.join(" ")');
  runner.assertEqual(interpreter.variables.sentence, 'Hello World', 'Should join array elements');
});

// Test arrays with functions
runner.test('Array passed to function', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
reservoir numbers = [1, 2, 3]
glass sum(arr) {
  drink total = arr[0] + arr[1] + arr[2]
  return total
}
drink result = sum(numbers)
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.result, 6, 'Should pass array to function');
});

// Test arrays in loops
runner.test('Array iteration in loop', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
reservoir items = [5, 10, 15]
drink sum = 0
drink i = 0
refill i < items.length {
  drink sum = sum + items[i]
  drink i = i + 1
}
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.sum, 30, 'Should iterate over array');
});

// Error handling tests
runner.test('Error: Array index out of bounds', () => {
  const interpreter = new ThirstyInterpreter();
  try {
    interpreter.execute('reservoir data = [1, 2, 3]\ndrink value = data[10]');
    throw new Error('Should have thrown an error');
  } catch (error) {
    runner.assertEqual(error.message.includes('out of bounds'), true, 'Should error on invalid index');
  }
});

runner.test('Error: Access non-array as array', () => {
  const interpreter = new ThirstyInterpreter();
  try {
    interpreter.execute('drink x = 42\ndrink value = x[0]');
    throw new Error('Should have thrown an error');
  } catch (error) {
    runner.assertEqual(error.message.includes('not an array'), true, 'Should error on non-array access');
  }
});

runner.test('Error: Pop from empty array', () => {
  const interpreter = new ThirstyInterpreter();
  try {
    interpreter.execute('reservoir empty = []\ndrink x = empty.pop()');
    throw new Error('Should have thrown an error');
  } catch (error) {
    runner.assertEqual(error.message.includes('empty array'), true, 'Should error on pop from empty');
  }
});

runner.run();
