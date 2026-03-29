/**
 * Thirsty-lang Optimized Benchmark Tool
 * Compares performance with console output suppressed
 */

const fs = require('fs');
const ThirstyInterpreter = require('../src/index');

class ThirstyBenchmark {
  constructor() {
    this.results = [];
  }

  async runBenchmark(name, code, iterations = 1000) {
    console.log(`\n🏃 Running benchmark: ${name}`);
    console.log(`   Iterations: ${iterations}`);

    const times = [];

    // Suppress console output during benchmarks
    const originalLog = console.log;
    console.log = () => {};

    // Warmup
    for (let i = 0; i < 10; i++) {
      const interpreter = new ThirstyInterpreter();
      interpreter.execute(code);
    }

    // Actual benchmark
    for (let i = 0; i < iterations; i++) {
      const interpreter = new ThirstyInterpreter();
      const start = process.hrtime.bigint();
      interpreter.execute(code);
      const end = process.hrtime.bigint();
      times.push(Number(end - start) / 1000000); // Convert to ms
    }

    // Restore console
    console.log = originalLog;

    const avg = times.reduce((a, b) => a + b, 0) / times.length;
    const min = Math.min(...times);
    const max = Math.max(...times);
    const median = times.sort((a, b) => a - b)[Math.floor(times.length / 2)];

    const result = {
      name,
      iterations,
      average: avg,
      min,
      max,
      median,
      totalTime: times.reduce((a, b) => a + b, 0)
    };

    this.results.push(result);

    console.log(`   ✓ Average: ${avg.toFixed(3)} ms`);
    console.log(`   ✓ Min: ${min.toFixed(3)} ms`);
    console.log(`   ✓ Max: ${max.toFixed(3)} ms`);
    console.log(`   ✓ Median: ${median.toFixed(3)} ms`);

    return result;
  }

  printSummary() {
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║              📊 BENCHMARK SUMMARY 📊                      ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log('Results sorted by average execution time:\n');

    const sorted = [...this.results].sort((a, b) => a.average - b.average);

    sorted.forEach((result, index) => {
      console.log(`${index + 1}. ${result.name}`);
      console.log(`   Average: ${result.average.toFixed(3)} ms`);
      console.log(`   Median: ${result.median.toFixed(3)} ms`);
      console.log(`   Range: ${result.min.toFixed(3)} - ${result.max.toFixed(3)} ms`);
      console.log();
    });

    // Performance comparison
    if (sorted.length > 1) {
      console.log('Performance Comparison:');
      const fastest = sorted[0];
      sorted.forEach((result, index) => {
        if (index === 0) {
          console.log(`  ${result.name}: Baseline (fastest)`);
        } else {
          const ratio = (result.average / fastest.average).toFixed(2);
          const percent = ((result.average - fastest.average) / fastest.average * 100).toFixed(1);
          console.log(`  ${result.name}: ${ratio}x slower (+${percent}%)`);
        }
      });
    }
  }

  exportResults(filepath) {
    fs.writeFileSync(filepath, JSON.stringify(this.results, null, 2));
    console.log(`\n✓ Results exported to ${filepath}`);
  }
}

async function main() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║   💧 Thirsty-lang Optimized Benchmark Suite 💧           ║');
  console.log('╚════════════════════════════════════════════════════════════╝');

  const benchmark = new ThirstyBenchmark();

  // Benchmark 1: Simple variable assignment
  await benchmark.runBenchmark(
    'Simple Assignment',
    'drink x = 42',
    10000
  );

  // Benchmark 2: String assignment
  await benchmark.runBenchmark(
    'String Assignment',
    'drink message = "Hello, World!"',
    10000
  );

  // Benchmark 3: Multiple operations (without output)
  await benchmark.runBenchmark(
    'Multiple Operations',
    'drink a = 1\ndrink b = 2\ndrink c = 3',
    10000
  );

  // Benchmark 4: Conditional (thirsty)
  await benchmark.runBenchmark(
    'Conditional Statement',
    'drink x = 5\nthirsty x == 5 {\ndrink y = 10\n}',
    5000
  );

  // Benchmark 5: Loop
  await benchmark.runBenchmark(
    'Loop (10 iterations)',
    'drink i = 0\nrefill i < 10 {\ndrink i = i + 1\n}',
    2000
  );

  // Benchmark 6: Expression evaluation
  await benchmark.runBenchmark(
    'Expression Evaluation',
    'drink result = 2 + 3 * 4',
    10000
  );

  // Benchmark 7: Complex program
  await benchmark.runBenchmark(
    'Complex Program',
    `drink water = "H2O"
drink temp = 25
drink liters = 2.5
drink total = temp + 5
drink calculated = total * 2`,
    5000
  );

  benchmark.printSummary();

  // Export if requested
  if (process.argv.includes('--export')) {
    const filepath = process.argv[process.argv.indexOf('--export') + 1] || 'benchmark-results.json';
    benchmark.exportResults(filepath);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = ThirstyBenchmark;
