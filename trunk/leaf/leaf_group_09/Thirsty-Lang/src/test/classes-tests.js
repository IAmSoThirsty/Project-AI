/**
 * Test Runner for Thirsty-lang Classes
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
    console.log('Running Thirsty-lang Class Tests...\n');

    for (const { name, fn } of this.tests) {
      try {
        fn();
        this.passed++;
        console.log(`✓ ${name}`);
      } catch (error) {
        this.failed++;
        console.log(`✗ ${name}`);
        console.log(`  ${error.message}`);
        if (error.stack) {
          console.log(`  ${error.stack.split('\n')[1]}`);
        }
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

// Test class declaration
runner.test('Class declaration with properties', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
fountain Person {
  drink name = "Unknown"
  drink age = 0
}
  `;
  interpreter.execute(code);
  runner.assertEqual(typeof interpreter.classes.Person, 'object', 'Class should be declared');
  runner.assertEqual(interpreter.classes.Person.properties.length, 2, 'Class should have 2 properties');
});

runner.test('Class declaration with methods', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
fountain Calculator {
  glass add(a, b) {
    return a + b
  }
  
  glass multiply(a, b) {
    return a * b
  }
}
  `;
  interpreter.execute(code);
  runner.assertEqual(typeof interpreter.classes.Calculator, 'object', 'Class should be declared');
  runner.assertEqual(Object.keys(interpreter.classes.Calculator.methods).length, 2, 'Class should have 2 methods');
});

// Test class instantiation
runner.test('Class instantiation', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
fountain Person {
  drink name = "John"
  drink age = 30
}
drink person = Person()
  `;
  interpreter.execute(code);
  runner.assertEqual(typeof interpreter.variables.person, 'object', 'Instance should be created');
  runner.assertEqual(interpreter.variables.person.__class, 'Person', 'Instance should have class reference');
});

// Test property access
runner.test('Instance property access', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
fountain Person {
  drink name = "Alice"
  drink age = 25
}
drink person = Person()
drink personName = person.name
drink personAge = person.age
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.personName, 'Alice', 'Should access instance property');
  runner.assertEqual(interpreter.variables.personAge, 25, 'Should access instance property');
});

// Test method calls
runner.test('Instance method call', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
fountain Calculator {
  glass add(a, b) {
    return a + b
  }
}
drink calc = Calculator()
drink result = calc.add(5, 3)
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.result, 8, 'Should call instance method');
});

runner.test('Instance method with return value', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
fountain Greeter {
  glass greet(name) {
    return "Hello, " + name + "!"
  }
}
drink greeter = Greeter()
drink message = greeter.greet("World")
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.message, 'Hello, World!', 'Should return value from method');
});

// Test this reference - Note: Currently 'this' is just a reference to properties
runner.test('Method accessing properties via this', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let output = '';
  console.log = (msg) => { output = msg; };
  
  const code = `
fountain Counter {
  drink count = 0
  
  glass increment() {
    drink this.count = this.count + 1
  }
  
  glass getCount() {
    return this.count
  }
}
drink counter = Counter()
counter.increment()
drink value = counter.getCount()
pour value
  `;
  interpreter.execute(code);
  console.log = oldLog;
  
  runner.assertEqual(output, 1, 'Method should modify property via this');
});

// Test multiple instances
runner.test('Multiple instances are independent', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
fountain Person {
  drink name = "Default"
}
drink person1 = Person()
drink person2 = Person()
drink name1 = person1.name
drink name2 = person2.name
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.name1, 'Default', 'First instance should have default');
  runner.assertEqual(interpreter.variables.name2, 'Default', 'Second instance should have default');
});

// Test class with mixed properties and methods
runner.test('Class with properties and methods', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
fountain Rectangle {
  drink width = 10
  drink height = 5
  
  glass area() {
    return this.width * this.height
  }
}
drink rect = Rectangle()
drink rectArea = rect.area()
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.rectArea, 50, 'Should calculate area from properties');
});

// Test method with conditional logic
runner.test('Method with conditional logic', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
fountain Validator {
  glass isPositive(num) {
    thirsty num > 0 {
      return true
    }
    hydrated {
      return false
    }
  }
}
drink validator = Validator()
drink result = validator.isPositive(5)
  `;
  interpreter.execute(code);
  runner.assertEqual(interpreter.variables.result, true, 'Method should evaluate condition');
});

// Error handling tests
runner.test('Error: Undefined class instantiation', () => {
  const interpreter = new ThirstyInterpreter();
  try {
    interpreter.execute('drink obj = UnknownClass()');
    throw new Error('Should have thrown an error');
  } catch (error) {
    runner.assertEqual(error.message.includes('Undefined'), true, 'Should error on undefined class or function');
  }
});

runner.test('Error: Calling undefined method', () => {
  const interpreter = new ThirstyInterpreter();
  try {
    const code = `
fountain Person {
  drink name = "John"
}
drink person = Person()
person.unknownMethod()
    `;
    interpreter.execute(code);
    throw new Error('Should have thrown an error');
  } catch (error) {
    runner.assertEqual(error.message.includes('not found'), true, 'Should error on undefined method');
  }
});

runner.test('Error: Accessing undefined property', () => {
  const interpreter = new ThirstyInterpreter();
  try {
    const code = `
fountain Person {
  drink name = "John"
}
drink person = Person()
drink unknown = person.unknownProp
    `;
    interpreter.execute(code);
    throw new Error('Should have thrown an error');
  } catch (error) {
    runner.assertEqual(error.message.includes('not found'), true, 'Should error on undefined property');
  }
});

runner.run();
