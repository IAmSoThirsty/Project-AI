/**
 * Comprehensive Performance Benchmark Suite
 * Tests performance of all major Thirsty-lang components
 *
 * BENCHMARK CATEGORIES:
 * 1. Interpreter Performance (execution speed, memory usage)
 * 2. Control Flow Performance (loops, conditionals, functions)
 * 3. Security Operations (shield, sanitize, armor)
 * 4. Standard Library Performance (Math, String, File, JSON)
 * 5. Exception Handling Performance (try/catch/throw)
 * 6. Class/Object Performance (instantiation, method calls)
 * 7. Expression Evaluation (arithmetic, comparisons, string ops)
 * 8. Memory Efficiency (garbage collection, reference tracking)
 */

const { ThirstyInterpreter } = require('../index');

// Benchmark utilities
class BenchmarkRunner {
  constructor() {
    this.results = [];
    this.currentSuite = null;
  }

  suite(name) {
    this.currentSuite = { name, benchmarks: [] };
    return this;
  }

  benchmark(name, fn, options = {}) {
    const iterations = options.iterations || 1000;
    const warmup = options.warmup || 100;

    // Warmup
    for (let i = 0; i < warmup; i++) {
      fn();
    }

    // Force GC if available
    if (global.gc) {
      global.gc();
    }

    // Benchmark
    const startTime = process.hrtime.bigint();
    const startMem = process.memoryUsage();

    for (let i = 0; i < iterations; i++) {
      fn();
    }

    const endTime = process.hrtime.bigint();
    const endMem = process.memoryUsage();

    // Calculate metrics
    const duration = Number(endTime - startTime) / 1000000; // Convert to ms
    const avgTime = duration / iterations;
    const opsPerSec = (iterations / duration) * 1000;
    const memDelta = endMem.heapUsed - startMem.heapUsed;

    const result = {
      name,
      iterations,
      totalTime: duration.toFixed(2) + 'ms',
      avgTime: avgTime.toFixed(4) + 'ms',
      opsPerSec: Math.round(opsPerSec),
      memoryDelta: (memDelta / 1024 / 1024).toFixed(2) + 'MB'
    };

    this.currentSuite.benchmarks.push(result);
    return this;
  }

  report() {
    if (this.currentSuite) {
      this.results.push(this.currentSuite);
      console.log(`\n${'='.repeat(80)}`);
      console.log(`Suite: ${this.currentSuite.name}`);
      console.log('='.repeat(80));

      for (const bench of this.currentSuite.benchmarks) {
        console.log(`\n${bench.name}`);
        console.log(`  Iterations:    ${bench.iterations}`);
        console.log(`  Total Time:    ${bench.totalTime}`);
        console.log(`  Avg Time:      ${bench.avgTime}`);
        console.log(`  Ops/Sec:       ${bench.opsPerSec.toLocaleString()}`);
        console.log(`  Memory Delta:  ${bench.memoryDelta}`);
      }

      this.currentSuite = null;
    }
  }

  summary() {
    console.log(`\n${'='.repeat(80)}`);
    console.log('BENCHMARK SUMMARY');
    console.log('='.repeat(80));

    for (const suite of this.results) {
      console.log(`\n${suite.name}:`);
      for (const bench of suite.benchmarks) {
        console.log(`  ${bench.name.padEnd(50)} ${bench.avgTime.padStart(12)} (${bench.opsPerSec.toLocaleString()} ops/sec)`);
      }
    }

    console.log(`\n${'='.repeat(80)}\n`);
  }
}

const runner = new BenchmarkRunner();

// ============================================================================
// 1. Interpreter Performance
// ============================================================================

runner.suite('Interpreter Performance')
  .benchmark('Simple variable assignment', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute('drink x = 42');
  }, { iterations: 10000 })
  .benchmark('Multiple statements (10 lines)', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      drink a = 1
      drink b = 2
      drink c = 3
      drink d = 4
      drink e = 5
      drink f = 6
      drink g = 7
      drink h = 8
      drink i = 9
      drink j = 10
    `);
  }, { iterations: 5000 })
  .benchmark('Expression evaluation', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute('drink result = 10 + 20 * 30 - 40 / 5');
  }, { iterations: 10000 })
  .benchmark('String concatenation', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute('drink msg = "Hello " + "World" + "!"');
  }, { iterations: 10000 })
  .report();

// ============================================================================
// 2. Control Flow Performance
// ============================================================================

runner.suite('Control Flow Performance')
  .benchmark('Simple conditional', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      drink x = 5
      thirsty x > 3 {
        drink result = "yes"
      }
    `);
  }, { iterations: 5000 })
  .benchmark('Conditional with else', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      drink x = 5
      thirsty x > 10 {
        drink result = "high"
      } hydrated {
        drink result = "low"
      }
    `);
  }, { iterations: 5000 })
  .benchmark('Loop (10 iterations)', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      drink i = 0
      refill i < 10 {
        drink i = i + 1
      }
    `);
  }, { iterations: 1000 })
  .benchmark('Function declaration and call', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      glass add(a, b) {
        return a + b
      }
      drink result = add(5, 3)
    `);
  }, { iterations: 5000 })
  .benchmark('Nested function calls', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      glass double(x) {
        return x * 2
      }
      glass quadruple(x) {
        return double(double(x))
      }
      drink result = quadruple(5)
    `);
  }, { iterations: 5000 })
  .report();

// ============================================================================
// 3. Security Operations Performance
// ============================================================================

runner.suite('Security Operations Performance')
  .benchmark('Shield block execution', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      shield testBlock {
        drink secure = "safe"
      }
    `);
  }, { iterations: 5000 })
  .benchmark('Sanitize XSS removal', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      drink input = "<script>alert('xss')</script>Hello"
      sanitize input
    `);
  }, { iterations: 5000 })
  .benchmark('Armor variable protection', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      drink secret = "password123"
      armor secret
    `);
  }, { iterations: 5000 })
  .report();

// ============================================================================
// 4. Standard Library Performance
// ============================================================================

runner.suite('Standard Library Performance')
  .benchmark('Math operations (5 operations)', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      drink a = Math.abs(-5)
      drink b = Math.sqrt(16)
      drink c = Math.pow(2, 3)
      drink d = Math.floor(4.7)
      drink e = Math.round(3.5)
    `);
  }, { iterations: 5000 })
  .benchmark('String operations (5 operations)', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      drink a = String.toUpperCase("hello")
      drink b = String.toLowerCase("WORLD")
      drink c = String.trim("  spaces  ")
      drink d = String.charAt("test", 0)
      drink e = String.substring("hello", 0, 2)
    `);
  }, { iterations: 5000 })
  .benchmark('JSON.parse', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.variables.JSON.parse('{"name": "test", "value": 42}');
  }, { iterations: 10000 })
  .benchmark('JSON.stringify', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.variables.JSON.stringify({ name: 'test', value: 42 });
  }, { iterations: 10000 })
  .benchmark('JSON round-trip', () => {
    const interpreter = new ThirstyInterpreter();
    const obj = { name: 'test', value: 42, items: [1, 2, 3] };
    const json = interpreter.variables.JSON.stringify(obj);
    interpreter.variables.JSON.parse(json);
  }, { iterations: 5000 })
  .report();

// ============================================================================
// 5. Exception Handling Performance
// ============================================================================

runner.suite('Exception Handling Performance')
  .benchmark('Try/catch with no error', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      try {
        drink x = 1
      } catch (e) {
        drink error = e.message
      }
    `);
  }, { iterations: 5000 })
  .benchmark('Try/catch with error', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      try {
        throw "test error"
      } catch (e) {
        drink msg = e.message
      }
    `);
  }, { iterations: 5000 })
  .report();

// ============================================================================
// 6. Class/Object Performance
// ============================================================================

runner.suite('Class/Object Performance')
  .benchmark('Class declaration', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      fountain Counter {
        drink count = 0
        glass increment() {
          drink count = count + 1
        }
      }
    `);
  }, { iterations: 5000 })
  .benchmark('Class instantiation', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      fountain Person {
        drink name = "John"
        drink age = 30
      }
      drink p = Person()
    `);
  }, { iterations: 3000 })
  .benchmark('Method invocation', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      fountain Calculator {
        glass add(a, b) {
          return a + b
        }
      }
      drink calc = Calculator()
      drink result = calc.add(5, 3)
    `);
  }, { iterations: 3000 })
  .benchmark('Property access', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      fountain Person {
        drink name = "Alice"
        drink age = 25
      }
      drink p = Person()
      drink n = p.name
      drink a = p.age
    `);
  }, { iterations: 3000 })
  .report();

// ============================================================================
// 7. Expression Evaluation Performance
// ============================================================================

runner.suite('Expression Evaluation Performance')
  .benchmark('Arithmetic (simple)', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute('drink result = 5 + 3');
  }, { iterations: 10000 })
  .benchmark('Arithmetic (complex)', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute('drink result = 10 + 20 * 30 - 40 / 5 + 8');
  }, { iterations: 10000 })
  .benchmark('Comparison operators', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(`
      thirsty 5 > 3 {
        drink a = "yes"
      }
      thirsty 10 < 20 {
        drink b = "yes"
      }
    `);
  }, { iterations: 5000 })
  .benchmark('String concatenation (3 parts)', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute('drink msg = "Hello" + " " + "World"');
  }, { iterations: 10000 })
  .report();

// ============================================================================
// 8. Memory Efficiency
// ============================================================================

runner.suite('Memory Efficiency')
  .benchmark('Create 100 variables', () => {
    const interpreter = new ThirstyInterpreter();
    for (let i = 0; i < 100; i++) {
      interpreter.execute(`drink var${i} = ${i}`);
    }
  }, { iterations: 100 })
  .benchmark('Array operations (100 elements)', () => {
    const interpreter = new ThirstyInterpreter();
    interpreter.execute('reservoir arr = []');
    for (let i = 0; i < 100; i++) {
      interpreter.execute(`drink arr[${i}] = ${i}`);
    }
  }, { iterations: 50 })
  .benchmark('Multiple interpreter instances', () => {
    for (let i = 0; i < 10; i++) {
      const interpreter = new ThirstyInterpreter();
      interpreter.execute('drink x = 1');
    }
  }, { iterations: 1000 })
  .report();

// Print summary
runner.summary();

// Export results for analysis
const fs = require('fs');
const path = require('path');

const reportPath = path.join(__dirname, '..', '..', 'benchmark-results.json');
fs.writeFileSync(reportPath, JSON.stringify({
  timestamp: new Date().toISOString(),
  platform: process.platform,
  nodeVersion: process.version,
  results: runner.results
}, null, 2));

console.log(`\nDetailed results saved to: ${reportPath}\n`);
