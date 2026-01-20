/**
 * Thirsty-lang Performance Profiler
 * Measure execution time and optimize your code
 */

const ThirstyInterpreter = require('./index');

class ThirstyProfiler extends ThirstyInterpreter {
  constructor() {
    super();
    this.profiling = true;
    this.executionTimes = [];
    this.functionCalls = new Map();
    this.memoryUsage = [];
    this.startTime = null;
  }

  execute(code) {
    this.startTime = process.hrtime.bigint();
    const startMemory = process.memoryUsage();

    const lines = code.split('\n').map(function (line) { return line.trim() }).filter(line => line && !line.startsWith('//'));

    for (let i = 0; i < lines.length; i++) {
      const lineStartTime = process.hrtime.bigint();

      this.executeLine(lines[i]);

      const lineEndTime = process.hrtime.bigint();
      const executionTime = Number(lineEndTime - lineStartTime) / 1000000; // Convert to ms

      this.executionTimes.push({
        line: i + 1,
        code: lines[i],
        time: executionTime
      });
    }

    const endTime = process.hrtime.bigint();
    const endMemory = process.memoryUsage();

    this.totalTime = Number(endTime - this.startTime) / 1000000;
    this.memoryDelta = {
      heapUsed: endMemory.heapUsed - startMemory.heapUsed,
      external: endMemory.external - startMemory.external
    };
  }

  generateReport() {
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║            ⚡ PERFORMANCE PROFILING REPORT ⚡             ║');
    console.log('╚════════════════════════════════════════════════════════════╝');

    // Overall stats
    console.log('\n📊 Overall Statistics:');
    console.log(`   Total Execution Time: ${this.totalTime.toFixed(3)} ms`);
    console.log(`   Lines Executed: ${this.executionTimes.length}`);
    console.log(`   Average Time per Line: ${(this.totalTime / this.executionTimes.length).toFixed(3)} ms`);
    console.log(`   Memory Delta: ${(this.memoryDelta.heapUsed / 1024).toFixed(2)} KB`);

    // Slowest lines
    console.log('\n🐌 Slowest Lines:');
    const sorted = [...this.executionTimes].sort((a, b) => b.time - a.time).slice(0, 5);
    sorted.forEach((item, index) => {
      console.log("   " + index + 1 + ". Line " + item.line + ": " + item.time.toFixed(3) + " ms");
      console.log(`      ${item.code}`);
    });

    // Time distribution
    console.log('\n📈 Execution Time per Line:');
    this.executionTimes.forEach(item => {
      const bar = '█'.repeat(Math.max(1, Math.floor(item.time * 10)));
      console.log(`   Line ${item.line.toString().padStart(3)}: ${bar} ${item.time.toFixed(3)} ms`);
    });

    // Recommendations
    console.log('\n💡 Optimization Suggestions:');
    const slowLines = this.executionTimes.filter(t => t.time > 1);
    if (slowLines.length > 0) {
      console.log(`   • ${slowLines.length} line(s) took longer than 1ms to execute`);
      console.log('   • Consider optimizing these lines for better performance');
    } else {
      console.log('   • Your code is well optimized! Keep it up! 💧');
    }

    if (this.memoryDelta.heapUsed > 1024 * 1024) {
      console.log('   • High memory usage detected. Consider optimizing data structures');
    }
  }
}

function main() {
  const fs = require('fs');
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Thirsty-lang Performance Profiler');
    console.log('Usage: node src/profiler.js <file.thirsty>');
    process.exit(0);
  }

  const filename = args[0];

  if (!fs.existsSync(filename)) {
    console.error(`Error: File '${filename}' not found`);
    process.exit(1);
  }

  const code = fs.readFileSync(filename, 'utf-8');
  const profiler = new ThirstyProfiler();

  console.log('⚡ Profiling execution...\n');
  profiler.execute(code);
  profiler.generateReport();
}

if (require.main === module) {
  main();
}

module.exports = ThirstyProfiler;
