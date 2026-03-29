/**
 * Module System Tests for Thirsty-lang
 */

const fs = require('fs');
const os = require('os');
const path = require('path');
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

  async run() {
    console.log('Running Module System Tests...\n');

    for (const { name, fn } of this.tests) {
      try {
        await fn();
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

  assertExists(value, message) {
    if (value === undefined || value === null) {
      throw new Error(message || 'Value should exist');
    }
  }
}

const runner = new TestRunner();

// File I/O Tests
runner.test('File.write creates a file', () => {
  const testFile = path.join(os.tmpdir(), 'thirsty-test-write.txt');
  const interpreter = new ThirstyInterpreter();
  
  // Clean up before test
  if (fs.existsSync(testFile)) {
    fs.unlinkSync(testFile);
  }
  
  interpreter.execute(`drink result = File.write("${testFile}", "test content")`);
  runner.assertEqual(interpreter.variables.result, true, 'Should return true');
  runner.assertEqual(fs.existsSync(testFile), true, 'File should exist');
  
  // Clean up
  fs.unlinkSync(testFile);
});

runner.test('File.read reads file content', () => {
  const testFile = path.join(os.tmpdir(), 'thirsty-test-read.txt');
  fs.writeFileSync(testFile, 'Hello Thirsty!', 'utf8');
  
  const interpreter = new ThirstyInterpreter();
  interpreter.execute(`drink content = File.read("${testFile}")`);
  
  runner.assertEqual(interpreter.variables.content, 'Hello Thirsty!', 'Should read file content');
  
  // Clean up
  fs.unlinkSync(testFile);
});

runner.test('File.exists checks file existence', () => {
  const testFile = path.join(os.tmpdir(), 'thirsty-test-exists.txt');
  fs.writeFileSync(testFile, 'test', 'utf8');
  
  const interpreter = new ThirstyInterpreter();
  interpreter.execute(`drink exists = File.exists("${testFile}")`);
  
  runner.assertEqual(interpreter.variables.exists, true, 'Should return true for existing file');
  
  // Clean up
  fs.unlinkSync(testFile);
});

runner.test('File.delete removes a file', () => {
  const testFile = path.join(os.tmpdir(), 'thirsty-test-delete.txt');
  fs.writeFileSync(testFile, 'test', 'utf8');
  
  const interpreter = new ThirstyInterpreter();
  interpreter.execute(`drink result = File.delete("${testFile}")`);
  
  runner.assertEqual(interpreter.variables.result, true, 'Should return true');
  runner.assertEqual(fs.existsSync(testFile), false, 'File should be deleted');
});

// Module System Tests
runner.test('Export and import functions', () => {
  const moduleFile = path.join(os.tmpdir(), 'thirsty-module.thirsty');
  const mainFile = path.join(os.tmpdir(), 'thirsty-main.thirsty');
  
  // Create module
  fs.writeFileSync(moduleFile, `
glass add(a, b) {
  return a + b
}
export add
  `.trim(), 'utf8');
  
  // Create main file
  fs.writeFileSync(mainFile, `
import { add } from "${moduleFile}"
drink result = add(5, 3)
  `.trim(), 'utf8');
  
  const interpreter = new ThirstyInterpreter({ currentFile: mainFile });
  interpreter.execute(fs.readFileSync(mainFile, 'utf8'));
  
  runner.assertEqual(interpreter.variables.result, 8, 'Should import and call function');
  
  // Clean up
  fs.unlinkSync(moduleFile);
  fs.unlinkSync(mainFile);
});

runner.test('Export and import variables', () => {
  const moduleFile = path.join(os.tmpdir(), 'thirsty-module-var.thirsty');
  const mainFile = path.join(os.tmpdir(), 'thirsty-main-var.thirsty');
  
  // Create module
  fs.writeFileSync(moduleFile, `
drink PI = 3.14159
export PI
  `.trim(), 'utf8');
  
  // Create main file
  fs.writeFileSync(mainFile, `
import { PI } from "${moduleFile}"
drink circumference = 2 * PI * 5
  `.trim(), 'utf8');
  
  const interpreter = new ThirstyInterpreter({ currentFile: mainFile });
  interpreter.execute(fs.readFileSync(mainFile, 'utf8'));
  
  // Check if circumference is close to expected value
  const expected = 2 * 3.14159 * 5;
  const actual = interpreter.variables.circumference;
  if (Math.abs(actual - expected) > 0.001) {
    throw new Error(`Expected ${expected}, got ${actual}`);
  }
  
  // Clean up
  fs.unlinkSync(moduleFile);
  fs.unlinkSync(mainFile);
});

runner.test('Module caching works', () => {
  const moduleFile = path.join(os.tmpdir(), 'thirsty-cache-module.thirsty');
  const mainFile = path.join(os.tmpdir(), 'thirsty-cache-main.thirsty');
  
  // Create module with a counter
  fs.writeFileSync(moduleFile, `
drink counter = 1
export counter
  `.trim(), 'utf8');
  
  // Create main file that imports twice
  fs.writeFileSync(mainFile, `
import { counter } from "${moduleFile}"
drink first = counter
import { counter } from "${moduleFile}"
drink second = counter
  `.trim(), 'utf8');
  
  const interpreter = new ThirstyInterpreter({ currentFile: mainFile });
  interpreter.execute(fs.readFileSync(mainFile, 'utf8'));
  
  // Both should be 1 because module is cached
  runner.assertEqual(interpreter.variables.first, 1, 'First import should be 1');
  runner.assertEqual(interpreter.variables.second, 1, 'Second import should be 1 (cached)');
  
  // Clean up
  fs.unlinkSync(moduleFile);
  fs.unlinkSync(mainFile);
});

// Async function tests
runner.test('Cascade keyword defines async function', () => {
  const interpreter = new ThirstyInterpreter();
  interpreter.execute(`
cascade asyncFunc() {
  return 42
}
  `);
  
  runner.assertExists(interpreter.functions.asyncFunc, 'Async function should be defined');
  runner.assertEqual(interpreter.functions.asyncFunc.async, true, 'Function should be marked as async');
});

// Run all tests
runner.run();
