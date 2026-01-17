#!/usr/bin/env node

/**
 * Thirsty-lang REPL (Read-Eval-Pour-Loop)
 * Interactive console for Thirsty-lang
 */

const readline = require('readline');
const ThirstyInterpreter = require('./index');
const fs = require('fs');
const path = require('path');

class ThirstyREPL {
  constructor() {
    this.interpreter = new ThirstyInterpreter();
    this.history = [];
    this.historyFile = path.join(process.env.HOME || process.env.USERPROFILE, '.thirsty_history');
    this.loadHistory();

    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: '💧> ',
      historySize: 1000
    });
  }

  loadHistory() {
    try {
      if (fs.existsSync(this.historyFile)) {
        this.history = fs.readFileSync(this.historyFile, 'utf-8').split('\n').filter(Boolean);
      }
    } catch (err) {
      // Ignore errors
    }
  }

  saveHistory() {
    try {
      fs.writeFileSync(this.historyFile, this.history.join('\n'));
    } catch (err) {
      // Ignore errors
    }
  }

  showWelcome() {
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║     💧 Thirsty-lang REPL v1.0.0 - Stay Hydrated! 💧      ║');
    console.log('╚════════════════════════════════════════════════════════════╝');
    console.log('\nType .help for commands or start coding!');
    console.log('Press Ctrl+C twice or type .exit to quit\n');
  }

  showHelp() {
    console.log('\n📚 REPL Commands:');
    console.log('  .help              Show this help message');
    console.log('  .exit              Exit the REPL');
    console.log('  .clear             Clear all variables');
    console.log('  .vars              Show all variables');
    console.log('  .history           Show command history');
    console.log('  .save <file>       Save session to file');
    console.log('  .load <file>       Load and execute file');
    console.log('  .version           Show version info');
    console.log('  .docs              Open documentation');
    console.log('  .examples          Show example code\n');
  }

  showVariables() {
    const vars = this.interpreter.variables;
    if (Object.keys(vars).length === 0) {
      console.log('No variables defined.');
    } else {
      console.log('\n📊 Current Variables:');
      for (const [name, value] of Object.entries(vars)) {
        console.log("  " + name + " = " + JSON.stringify(value));
      }
      console.log();
    }
  }

  showHistory() {
    console.log('\n📜 Command History:');
    this.history.slice(-20).forEach((cmd, i) => {
      console.log(`  ${i + 1}. ${cmd}`);
    });
    console.log();
  }

  showExamples() {
    console.log('\n💡 Example Code:');
    console.log('  drink water = "H2O"');
    console.log('  pour water');
    console.log('  drink temp = 25.5');
    console.log('  pour temp\n');
  }

  async start() {
    this.showWelcome();

    this.rl.prompt();

    this.rl.on('line', async (line) => {
      const input = line.trim();

      if (!input) {
        this.rl.prompt();
        return;
      }

      // Add to history
      if (input && !input.startsWith('.')) {
        this.history.push(input);
      }

      // Handle REPL commands
      if (input.startsWith('.')) {
        await this.handleCommand(input);
        this.rl.prompt();
        return;
      }

      // Execute Thirsty-lang code
      try {
        // Capture console.log output
        const oldLog = console.log;
        let output = null;
        console.log = (...args) => {
          output = args.join(' ');
        };

        this.interpreter.executeLine(input);

        console.log = oldLog;

        if (output) {
          console.log(output);
        }
      } catch (error) {
        console.error(`❌ ${error.message}`);
      }

      this.rl.prompt();
    });

    this.rl.on('close', () => {
      this.saveHistory();
      console.log('\n💧 Stay hydrated! Goodbye!\n');
      process.exit(0);
    });
  }

  async handleCommand(cmd) {
    const parts = cmd.split(' ');
    const command = parts[0];
    const args = parts.slice(1);

    switch (command) {
      case '.help':
        this.showHelp();
        break;

      case '.exit':
      case '.quit':
        this.rl.close();
        break;

      case '.clear':
        this.interpreter.variables = {};
        console.log('✓ All variables cleared');
        break;

      case '.vars':
      case '.variables':
        this.showVariables();
        break;

      case '.history':
        this.showHistory();
        break;

      case '.save':
        if (args.length === 0) {
          console.log('Usage: .save <filename>');
        } else {
          this.saveSession(args[0]);
        }
        break;

      case '.load':
        if (args.length === 0) {
          console.log('Usage: .load <filename>');
        } else {
          this.loadFile(args[0]);
        }
        break;

      case '.version':
        console.log('Thirsty-lang v1.0.0');
        console.log('Node.js ' + process.version);
        break;

      case '.examples':
        this.showExamples();
        break;

      case '.docs':
        console.log('\n📖 Documentation: https://github.com/IAmSoThirsty/Thirsty-lang/blob/main/docs/');
        break;

      default:
        console.log(`Unknown command: ${command}`);
        console.log('Type .help for available commands');
    }
  }

  saveSession(filename) {
    try {
      const code = this.history.filter(h => !h.startsWith('.')).join('\n');
      fs.writeFileSync(filename, code);
      console.log(`✓ Session saved to ${filename}`);
    } catch (error) {
      console.error(`❌ Error saving file: ${error.message}`);
    }
  }

  loadFile(filename) {
    try {
      const code = fs.readFileSync(filename, 'utf-8');
      this.interpreter.execute(code);
      console.log(`✓ Loaded and executed ${filename}`);
    } catch (error) {
      console.error(`❌ Error loading file: ${error.message}`);
    }
  }
}

async function main() {
  const repl = new ThirstyREPL();
  await repl.start();
}

if (require.main === module) {
  main();
}

module.exports = ThirstyREPL;
