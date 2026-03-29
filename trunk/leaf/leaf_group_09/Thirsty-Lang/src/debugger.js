#!/usr/bin/env node

/**
 * Thirsty-lang Debugger
 * Step through your code and find bugs
 */

const { ThirstyInterpreter } = require('./index');
const readline = require('readline');

class ThirstyDebugger extends ThirstyInterpreter {
  constructor() {
    super();
    this.breakpoints = new Set();
    this.currentLine = 0;
    this.lines = [];
    this.stepping = false;
    this.watchVariables = new Set();
    this.callStack = [];
    
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  async debug(code) {
    this.lines = code.split('\n').map((line, i) => ({
      number: i + 1,
      code: line.trim()
    })).filter(line => line.code && !line.code.startsWith('//'));

    console.log('🐛 Thirsty-lang Debugger');
    console.log('Type "help" for debugger commands\n');

    for (let i = 0; i < this.lines.length; i++) {
      this.currentLine = this.lines[i].number;
      const line = this.lines[i].code;

      if (this.breakpoints.has(this.currentLine) || this.stepping) {
        await this.pause(line);
      }

      try {
        this.executeLine(line);
      } catch (error) {
        console.error(`❌ Error at line ${this.currentLine}: ${error.message}`);
        await this.pause(line);
      }
    }

    console.log('✓ Debugging complete');
    this.rl.close();
  }

  async pause(line) {
    console.log(`\n⏸️  Paused at line ${this.currentLine}: ${line}`);
    this.showContext();

    let continuing = false;
    while (!continuing) {
      const command = await this.getDebugCommand();
      continuing = await this.handleDebugCommand(command);
    }
  }

  showContext() {
    // Show nearby lines
    const start = Math.max(0, this.currentLine - 3);
    const end = Math.min(this.lines.length, this.currentLine + 2);
    
    console.log('\nCode context:');
    for (let i = start; i < end; i++) {
      const line = this.lines[i];
      const marker = line.number === this.currentLine ? '→' : ' ';
      const bp = this.breakpoints.has(line.number) ? '🔴' : '  ';
      console.log(`${bp} ${marker} ${line.number}: ${line.code}`);
    }

    // Show watched variables
    if (this.watchVariables.size > 0) {
      console.log('\nWatched variables:');
      for (const varName of this.watchVariables) {
        const value = this.variables[varName];
        console.log(`  ${varName} = ${JSON.stringify(value)}`);
      }
    }
  }

  async getDebugCommand() {
    return new Promise((resolve) => {
      this.rl.question('\n(debug)> ', (answer) => {
        resolve(answer.trim());
      });
    });
  }

  async handleDebugCommand(command) {
    const parts = command.split(' ');
    const cmd = parts[0];
    const args = parts.slice(1);

    switch (cmd) {
      case 'help':
      case 'h':
        this.showDebugHelp();
        return false;

      case 'continue':
      case 'c':
        this.stepping = false;
        return true;

      case 'step':
      case 's':
        this.stepping = true;
        return true;

      case 'next':
      case 'n':
        return true;

      case 'break':
      case 'b':
        if (args.length > 0) {
          const lineNum = parseInt(args[0]);
          this.breakpoints.add(lineNum);
          console.log(`✓ Breakpoint set at line ${lineNum}`);
        } else {
          console.log('Usage: break <line_number>');
        }
        return false;

      case 'clear':
        if (args.length > 0) {
          const lineNum = parseInt(args[0]);
          this.breakpoints.delete(lineNum);
          console.log(`✓ Breakpoint cleared at line ${lineNum}`);
        } else {
          console.log('Usage: clear <line_number>');
        }
        return false;

      case 'watch':
      case 'w':
        if (args.length > 0) {
          this.watchVariables.add(args[0]);
          console.log(`✓ Watching variable: ${args[0]}`);
        } else {
          console.log('Usage: watch <variable_name>');
        }
        return false;

      case 'unwatch':
        if (args.length > 0) {
          this.watchVariables.delete(args[0]);
          console.log(`✓ Stopped watching: ${args[0]}`);
        }
        return false;

      case 'vars':
      case 'v':
        console.log('\nVariables:');
        for (const [name, value] of Object.entries(this.variables)) {
          if (!value || !value.__builtin) {
            console.log(`  ${name} = ${JSON.stringify(value)}`);
          }
        }
        return false;

      case 'print':
      case 'p':
        if (args.length > 0) {
          const varName = args[0];
          if (this.variables.hasOwnProperty(varName)) {
            console.log(`${varName} = ${JSON.stringify(this.variables[varName], null, 2)}`);
          } else {
            console.log(`Variable '${varName}' not found`);
          }
        } else {
          console.log('Usage: print <variable_name>');
        }
        return false;

      case 'eval':
      case 'e':
        if (args.length > 0) {
          try {
            const expr = args.join(' ');
            const result = this.evaluateExpression(expr);
            console.log(`Result: ${JSON.stringify(result)}`);
          } catch (error) {
            console.log(`Error evaluating expression: ${error.message}`);
          }
        } else {
          console.log('Usage: eval <expression>');
        }
        return false;

      case 'stack':
        if (this.callStack.length === 0) {
          console.log('Call stack is empty');
        } else {
          console.log('\nCall Stack:');
          for (let i = this.callStack.length - 1; i >= 0; i--) {
            const frame = this.callStack[i];
            console.log(`  ${i}: ${frame.function} (line ${frame.line})`);
          }
        }
        return false;

      case 'list':
      case 'l':
        const start = Math.max(0, this.currentLine - 5);
        const end = Math.min(this.lines.length, this.currentLine + 5);
        console.log('\nCode listing:');
        for (let i = start; i < end; i++) {
          const line = this.lines[i];
          const marker = line.number === this.currentLine ? '→' : ' ';
          const bp = this.breakpoints.has(line.number) ? '🔴' : '  ';
          console.log(`${bp} ${marker} ${line.number}: ${line.code}`);
        }
        return false;

      case 'breakpoints':
        if (this.breakpoints.size === 0) {
          console.log('No breakpoints set');
        } else {
          console.log('Breakpoints:');
          for (const bp of this.breakpoints) {
            console.log(`  Line ${bp}`);
          }
        }
        return false;

      case 'quit':
      case 'q':
        console.log('Exiting debugger');
        this.rl.close();
        process.exit(0);
        break;

      default:
        console.log('Unknown command. Type "help" for available commands.');
        return false;
    }
  }

  showDebugHelp() {
    console.log('\n🐛 Debugger Commands:');
    console.log('  help, h              Show this help');
    console.log('  continue, c          Continue execution');
    console.log('  step, s              Step into next line');
    console.log('  next, n              Step over next line');
    console.log('  break <line>, b      Set breakpoint');
    console.log('  clear <line>         Clear breakpoint');
    console.log('  watch <var>, w       Watch variable');
    console.log('  unwatch <var>        Stop watching variable');
    console.log('  print <var>, p       Print variable value');
    console.log('  eval <expr>, e       Evaluate expression');
    console.log('  vars, v              Show all variables');
    console.log('  stack                Show call stack');
    console.log('  list, l              Show code listing');
    console.log('  breakpoints          List breakpoints');
    console.log('  quit, q              Exit debugger');
  }
}

async function main() {
  const fs = require('fs');
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Usage: node src/debugger.js <file.thirsty>');
    process.exit(1);
  }

  const filename = args[0];
  if (!fs.existsSync(filename)) {
    console.error(`Error: File '${filename}' not found`);
    process.exit(1);
  }

  const code = fs.readFileSync(filename, 'utf-8');
  const thirstyDebugger = new ThirstyDebugger();
  await thirstyDebugger.debug(code);
}

if (require.main === module) {
  main();
}

module.exports = ThirstyDebugger;
