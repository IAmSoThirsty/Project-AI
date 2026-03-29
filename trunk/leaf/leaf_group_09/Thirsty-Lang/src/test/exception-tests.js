/**
 * Exception Handling Tests
 * Tests for try/catch/finally/throw functionality
 */

const { ThirstyInterpreter, ThirstyError } = require('../index');

const tests = [];
let passed = 0;
let failed = 0;

function test(name, fn) {
  tests.push({ name, fn });
}

function runTests() {
  console.log('Running Exception Handling Tests...\n');

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

// Test 1: Basic try/catch
test('Basic try/catch with error', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink result = "not set"
    try {
      throw "test error"
    } catch (e) {
      drink result = e.message
    }
    pour result
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('test error')) {
    throw new Error(`Expected output to include "test error", got: ${output}`);
  }
});

// Test 2: Try/catch with no error
test('Try/catch with no error', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink result = "success"
    try {
      drink result = "no error"
    } catch (e) {
      drink result = "error occurred"
    }
    pour result
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('no error')) {
    throw new Error(`Expected "no error", got: ${output}`);
  }
});

// Test 3: Try/finally without catch
test('Try/finally without catch', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink executed = "no"
    try {
      drink executed = "yes"
    } finally {
      drink executed = executed + " and finally"
    }
    pour executed
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('yes and finally')) {
    throw new Error(`Expected "yes and finally", got: ${output}`);
  }
});

// Test 4: Try/catch/finally all together
test('Try/catch/finally all together', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink result = ""
    try {
      throw "error message"
    } catch (e) {
      drink result = "caught"
    } finally {
      drink result = result + " and cleaned"
    }
    pour result
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('caught and cleaned')) {
    throw new Error(`Expected "caught and cleaned", got: ${output}`);
  }
});

// Test 5: Nested try/catch
test('Nested try/catch blocks', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink result = ""
    try {
      drink result = "outer"
      try {
        throw "inner error"
      } catch (e) {
        drink result = "inner caught"
      }
    } catch (e) {
      drink result = "outer caught"
    }
    pour result
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('inner caught')) {
    throw new Error(`Expected "inner caught", got: ${output}`);
  }
});

// Test 6: Error object properties
test('Error object has message and type', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink msg = ""
    drink typ = ""
    try {
      throw "test message"
    } catch (e) {
      drink msg = e.message
      drink typ = e.type
    }
    pour msg
    pour typ
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('test message')) {
    throw new Error(`Expected message in output, got: ${output}`);
  }
  if (!output.includes('ThrownError') && !output.includes('Error')) {
    throw new Error(`Expected error type in output, got: ${output}`);
  }
});

// Test 7: Finally executes even with error
test('Finally executes even when error not caught', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink finallyRan = "no"
    try {
      try {
        throw "uncaught error"
      } finally {
        drink finallyRan = "yes"
      }
    } catch (e) {
      pour finallyRan
    }
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('yes')) {
    throw new Error(`Expected "yes", got: ${output}`);
  }
});

// Test 8: Throw with expression
test('Throw with evaluated expression', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink num = 42
    try {
      throw "error " + num
    } catch (e) {
      pour e.message
    }
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('error 42')) {
    throw new Error(`Expected "error 42", got: ${output}`);
  }
});

// Test 9: Multiple catch variables don't interfere
test('Multiple catch variables are independent', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink result = ""
    try {
      throw "first"
    } catch (e1) {
      drink result = e1.message
      try {
        throw "second"
      } catch (e2) {
        drink result = result + " " + e2.message
      }
    }
    pour result
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('first second')) {
    throw new Error(`Expected "first second", got: ${output}`);
  }
});

// Test 10: Return from try block
test('Return statement in try block', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    glass testFunc() {
      try {
        return "from try"
      } catch (e) {
        return "from catch"
      }
    }
    drink result = testFunc()
    pour result
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('from try')) {
    throw new Error(`Expected "from try", got: ${output}`);
  }
});

// Test 11: Return from catch block
test('Return statement in catch block', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    glass testFunc() {
      try {
        throw "error"
        return "from try"
      } catch (e) {
        return "from catch"
      }
    }
    drink result = testFunc()
    pour result
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('from catch')) {
    throw new Error(`Expected "from catch", got: ${output}`);
  }
});

// Test 12: Error in catch block is propagated
test('Error in catch block is propagated', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink result = "none"
    try {
      try {
        throw "first error"
      } catch (e) {
        throw "second error"
      }
    } catch (e2) {
      drink result = e2.message
    }
    pour result
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('second error')) {
    throw new Error(`Expected "second error", got: ${output}`);
  }
});

// Test 13: Finally after return
test('Finally executes after return', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink finallyRan = "no"
    glass testFunc() {
      try {
        return "value"
      } finally {
        drink finallyRan = "yes"
      }
    }
    drink result = testFunc()
    pour finallyRan
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('yes')) {
    throw new Error(`Expected "yes", got: ${output}`);
  }
});

// Test 14: Try without catch or finally should error
test('Try without catch or finally throws error', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    try {
      drink x = 1
    }
  `;

  let errorThrown = false;
  try {
    interpreter.execute(code);
  } catch (e) {
    if (e.message && e.message.includes('catch or finally')) {
      errorThrown = true;
    }
  }

  if (!errorThrown) {
    throw new Error('Expected error for try without catch or finally');
  }
});

// Test 15: Empty catch block
test('Empty catch block handles error', () => {
  const interpreter = new ThirstyInterpreter();
  const code = `
    drink result = "before"
    try {
      throw "error"
      drink result = "in try"
    } catch (e) {
    }
    drink result = "after"
    pour result
  `;

  let output = '';
  const originalLog = console.log;
  console.log = (msg) => { output += msg; };

  try {
    interpreter.execute(code);
  } finally {
    console.log = originalLog;
  }

  if (!output.includes('after')) {
    throw new Error(`Expected "after", got: ${output}`);
  }
});

// Run all tests
runTests();
