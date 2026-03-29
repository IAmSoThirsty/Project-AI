/**
 * Test Runner for Thirsty-lang
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

runner.test('String concatenation', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let output = '';
  console.log = (msg) => { output = msg; };
  
  interpreter.execute('drink first = "Hello"\ndrink second = "World"\npour first + " " + second');
  console.log = oldLog;
  
  runner.assertEqual(output, 'Hello World', 'Should concatenate strings');
});

runner.test('Arithmetic expression evaluation', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let outputs = [];
  console.log = (msg) => { outputs.push(msg); };
  
  interpreter.execute('pour 10 + 5\npour 10 - 5\npour 10 * 5\npour 10 / 5');
  console.log = oldLog;
  
  runner.assertEqual(outputs[0], 15, 'Should evaluate addition');
  runner.assertEqual(outputs[1], 5, 'Should evaluate subtraction');
  runner.assertEqual(outputs[2], 50, 'Should evaluate multiplication');
  runner.assertEqual(outputs[3], 2, 'Should evaluate division');
});

runner.test('Operator precedence', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let output;
  console.log = (msg) => { output = msg; };
  
  interpreter.execute('pour 2 + 3 * 4');
  console.log = oldLog;
  
  runner.assertEqual(output, 14, 'Should respect operator precedence (multiply before add)');
});

runner.test('Conditional statements (thirsty)', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let output = '';
  console.log = (msg) => { output = msg; };
  
  interpreter.execute('drink x = 10\nthirsty x > 5 {\npour "yes"\n}');
  console.log = oldLog;
  
  runner.assertEqual(output, 'yes', 'Should execute if block when condition is true');
});

runner.test('Conditional with hydrated (else) block', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let output = '';
  console.log = (msg) => { output = msg; };
  
  interpreter.execute('drink x = 3\nthirsty x > 5 {\npour "yes"\n}\nhydrated {\npour "no"\n}');
  console.log = oldLog;
  
  runner.assertEqual(output, 'no', 'Should execute else block when condition is false');
});

runner.test('Comparison operators', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let outputs = [];
  console.log = (msg) => { outputs.push(msg); };
  
  interpreter.execute('drink a = 5\ndrink b = 10\nthirsty a < b {\npour "less"\n}\nthirsty a == 5 {\npour "equal"\n}');
  console.log = oldLog;
  
  runner.assertEqual(outputs[0], 'less', 'Should handle less than');
  runner.assertEqual(outputs[1], 'equal', 'Should handle equality');
});

runner.test('Loop (refill) functionality', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let outputs = [];
  console.log = (msg) => { outputs.push(msg); };
  
  interpreter.execute('drink i = 0\nrefill i < 3 {\npour i\ndrink i = i + 1\n}');
  console.log = oldLog;
  
  runner.assertEqual(outputs.length, 3, 'Loop should execute 3 times');
  runner.assertEqual(outputs[0], 0, 'First iteration');
  runner.assertEqual(outputs[1], 1, 'Second iteration');
  runner.assertEqual(outputs[2], 2, 'Third iteration');
});

// ============================================================================
// COMPREHENSIVE LOOP TESTS - Verifying all loop functionality
// ============================================================================

runner.test('Loop: Simple countdown', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let outputs = [];
  console.log = (msg) => { outputs.push(msg); };
  
  interpreter.execute('drink count = 5\nrefill count > 0 {\npour count\ndrink count = count - 1\n}');
  console.log = oldLog;
  
  runner.assertEqual(outputs.length, 5, 'Should count down from 5 to 1');
  runner.assertEqual(outputs[0], 5, 'First: 5');
  runner.assertEqual(outputs[1], 4, 'Second: 4');
  runner.assertEqual(outputs[2], 3, 'Third: 3');
  runner.assertEqual(outputs[3], 2, 'Fourth: 2');
  runner.assertEqual(outputs[4], 1, 'Fifth: 1');
});

runner.test('Loop: Counter with multiplication', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let outputs = [];
  console.log = (msg) => { outputs.push(msg); };
  
  interpreter.execute('drink i = 1\nrefill i <= 4 {\npour i * 2\ndrink i = i + 1\n}');
  console.log = oldLog;
  
  runner.assertEqual(outputs.length, 4, 'Should execute 4 times');
  runner.assertEqual(outputs[0], 2, 'First: 1*2=2');
  runner.assertEqual(outputs[1], 4, 'Second: 2*2=4');
  runner.assertEqual(outputs[2], 6, 'Third: 3*2=6');
  runner.assertEqual(outputs[3], 8, 'Fourth: 4*2=8');
});

runner.test('Loop: Nested variable updates', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let outputs = [];
  console.log = (msg) => { outputs.push(msg); };
  
  interpreter.execute('drink total = 0\ndrink i = 1\nrefill i <= 3 {\ndrink total = total + i\ndrink i = i + 1\n}\npour total');
  console.log = oldLog;
  
  runner.assertEqual(outputs[0], 6, 'Total should be 1+2+3=6');
});

runner.test('Loop: Zero iterations when condition false', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let outputs = [];
  console.log = (msg) => { outputs.push(msg); };
  
  interpreter.execute('drink i = 10\nrefill i < 5 {\npour "should not print"\n}');
  console.log = oldLog;
  
  runner.assertEqual(outputs.length, 0, 'Loop should not execute when condition is initially false');
});

runner.test('Loop: Complex condition with multiple variables', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let outputs = [];
  console.log = (msg) => { outputs.push(msg); };
  
  interpreter.execute('drink a = 1\ndrink b = 10\nrefill a < b {\npour a\ndrink a = a + 2\n}');
  console.log = oldLog;
  
  runner.assertEqual(outputs.length, 5, 'Should execute 5 times (1,3,5,7,9)');
  runner.assertEqual(outputs[0], 1);
  runner.assertEqual(outputs[4], 9);
});

// ============================================================================
// COMPREHENSIVE ERROR CONDITION TESTS - Detailed validation
// ============================================================================

runner.test('Error: Division by zero', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('pour 10 / 0');
  } catch (error) {
    errorCaught = error.message.includes('Division by zero');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for division by zero');
});

runner.test('Error: Division by zero in expression', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  let errorMessage = '';
  
  try {
    interpreter.execute('drink x = 0\npour 100 / x');
  } catch (error) {
    errorCaught = true;
    errorMessage = error.message;
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error when dividing by variable containing zero');
  runner.assertEqual(errorMessage.includes('Division by zero'), true, 'Error message should mention division by zero');
});

runner.test('Error: Unmatched opening brace in thirsty', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  let errorMessage = '';
  
  try {
    interpreter.execute('thirsty true {\npour "test"');
  } catch (error) {
    errorCaught = true;
    errorMessage = error.message;
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for unmatched opening brace');
  runner.assertEqual(errorMessage.includes('Unmatched'), true, 'Error should mention unmatched brace');
});

runner.test('Error: Unmatched opening brace in refill', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('refill true {\npour "loop"\n// missing closing brace');
  } catch (error) {
    errorCaught = error.message.includes('Unmatched');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for unmatched brace in loop');
});

runner.test('Error: Unmatched opening brace in shield', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('shield test {\npour "secure"');
  } catch (error) {
    errorCaught = error.message.includes('Unmatched');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for unmatched brace in shield block');
});

runner.test('Error: Invalid thirsty statement', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  let errorMessage = '';
  
  try {
    interpreter.execute('thirsty');
  } catch (error) {
    errorCaught = true;
    errorMessage = error.message;
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for invalid thirsty statement');
  runner.assertEqual(errorMessage.includes('Unknown statement') || errorMessage.includes('Invalid thirsty'), true, 'Error should indicate invalid statement');
});

runner.test('Error: Invalid refill statement', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('refill {\npour "no condition"\n}');
  } catch (error) {
    errorCaught = error.message.includes('Invalid refill statement');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for refill without condition');
});

runner.test('Error: Unknown variable reference', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('pour unknownVariable');
  } catch (error) {
    errorCaught = error.message.includes('Unknown expression');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for unknown variable');
});

runner.test('Error: Unknown variable in expression', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('drink x = 5\npour x + undefinedVar');
  } catch (error) {
    errorCaught = error.message.includes('Unknown expression');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for undefined variable in expression');
});

runner.test('Error: Invalid drink statement', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('drink noValue');
  } catch (error) {
    errorCaught = error.message.includes('Invalid drink statement');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for drink without assignment');
});

runner.test('Error: Invalid shield statement', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('shield {\npour "no name"\n}');
  } catch (error) {
    errorCaught = error.message.includes('Invalid shield statement');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for shield without name');
});

runner.test('Error: Invalid sanitize statement', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('sanitize');
  } catch (error) {
    errorCaught = error.message.includes('Invalid sanitize statement') || error.message.includes('Unknown statement');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for sanitize without variable');
});

runner.test('Error: Sanitize undefined variable', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('sanitize nonExistent');
  } catch (error) {
    errorCaught = error.message.includes('Cannot sanitize undefined variable');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error when sanitizing undefined variable');
});

runner.test('Error: Armor undefined variable', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('armor nonExistent');
  } catch (error) {
    errorCaught = error.message.includes('Cannot armor undefined variable');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error when armoring undefined variable');
});

runner.test('Error: Unknown statement', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  
  try {
    interpreter.execute('unknownKeyword test');
  } catch (error) {
    errorCaught = error.message.includes('Unknown statement');
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error for unknown statement');
});

runner.test('Error: Loop iteration safety limit', () => {
  const interpreter = new ThirstyInterpreter();
  let errorCaught = false;
  let errorMessage = '';
  
  try {
    // Infinite loop should be caught by MAX_LOOP_ITERATIONS
    interpreter.execute('drink i = 0\nrefill i >= 0 {\ndrink i = i + 1\n}');
  } catch (error) {
    errorCaught = true;
    errorMessage = error.message;
  }
  
  runner.assertEqual(errorCaught, true, 'Should throw error when exceeding max iterations');
  runner.assertEqual(errorMessage.includes('exceeded maximum iterations'), true, 'Error should mention iteration limit');
});

runner.test('Security: Shield block execution', () => {
  const interpreter = new ThirstyInterpreter();
  const oldLog = console.log;
  let output = '';
  console.log = (msg) => { output = msg; };
  
  interpreter.execute('shield testBlock {\ndrink message = "protected"\npour message\n}');
  console.log = oldLog;
  
  runner.assertEqual(output, 'protected', 'Shield block should execute normally');
});

runner.test('Security: Sanitize removes XSS', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute('drink input = "<script>alert(1)</script>"\nsanitize input');
  
  const sanitized = interpreter.variables.input;
  runner.assertEqual(sanitized.includes('<script>'), false, 'Sanitize should remove script tags');
});

runner.test('Security: Armor protects variables', () => {
  const interpreter = new ThirstyInterpreter();
  const oldWarn = console.warn;
  let warned = false;
  console.warn = () => { warned = true; };
  
  interpreter.execute('drink secret = "value"\narmor secret\ndrink secret = "hacked"');
  console.warn = oldWarn;
  
  runner.assertEqual(interpreter.variables.secret, 'value', 'Armored variable should keep original value');
  runner.assertEqual(warned, true, 'Should warn when trying to modify armored variable');
});

runner.run();
