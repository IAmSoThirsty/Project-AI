#!/usr/bin/env node

/**
 * Thirsty-lang Transpiler
 * Convert Thirsty-lang to JavaScript, Python, or other languages
 */

const fs = require('fs');

class ThirstyTranspiler {
  constructor(targetLanguage = 'javascript') {
    this.target = targetLanguage;
    this.output = [];
  }

  transpile(code) {
    this.output = [];
    
    const lines = code.split('\n')
      .map(line => line.trim())
      .filter(line => line);

    for (const line of lines) {
      this.transpileLine(line);
    }

    return this.output.join('\n');
  }

  transpileLine(line) {
    // Skip comments
    if (line.startsWith('//')) {
      this.output.push(line);
      return;
    }

    // Variable declaration
    if (line.startsWith('drink ')) {
      const match = line.match(/drink\s+(\w+)\s*=\s*(.+)/);
      if (match) {
        this.transpileVariableDeclaration(match[1], match[2]);
        return;
      }
    }

    // Output statement
    if (line.startsWith('pour ')) {
      const expr = line.substring(5).trim();
      this.transpileOutput(expr);
      return;
    }
  }

  transpileVariableDeclaration(name, value) {
    switch (this.target) {
      case 'javascript':
        this.output.push(`const ${name} = ${value};`);
        break;
      case 'python':
        this.output.push(`${name} = ${value}`);
        break;
      case 'go':
        // Determine type
        const isString = value.startsWith('"') || value.startsWith("'");
        const type = isString ? 'string' : 'float64';
        this.output.push(`var ${name} ${type} = ${value}`);
        break;
      case 'rust':
        this.output.push(`let ${name} = ${value};`);
        break;
      case 'java':
        const isStr = value.startsWith('"') || value.startsWith("'");
        const javaType = isStr ? 'String' : 'double';
        this.output.push(`${javaType} ${name} = ${value};`);
        break;
      default:
        this.output.push(`${name} = ${value}`);
    }
  }

  transpileOutput(expr) {
    switch (this.target) {
      case 'javascript':
        this.output.push(`console.log(${expr});`);
        break;
      case 'python':
        this.output.push(`print(${expr})`);
        break;
      case 'go':
        this.output.push(`fmt.Println(${expr})`);
        break;
      case 'rust':
        this.output.push(`println!("{}", ${expr});`);
        break;
      case 'java':
        this.output.push(`System.out.println(${expr});`);
        break;
      case 'c':
        this.output.push(`printf("%s\\n", ${expr});`);
        break;
      default:
        this.output.push(`print(${expr})`);
    }
  }

  generateWrapper() {
    switch (this.target) {
      case 'go':
        return `package main\n\nimport "fmt"\n\nfunc main() {\n${this.indentCode(this.output.join('\n'))}\n}`;
      case 'rust':
        return `fn main() {\n${this.indentCode(this.output.join('\n'))}\n}`;
      case 'java':
        return `public class ThirstyProgram {\n  public static void main(String[] args) {\n${this.indentCode(this.output.join('\n'), 4)}\n  }\n}`;
      case 'c':
        return `#include <stdio.h>\n\nint main() {\n${this.indentCode(this.output.join('\n'))}\n  return 0;\n}`;
      default:
        return this.output.join('\n');
    }
  }

  indentCode(code, spaces = 2) {
    return code.split('\n').map(line => ' '.repeat(spaces) + line).join('\n');
  }
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Thirsty-lang Transpiler');
    console.log('Usage: node src/transpiler.js <file.thirsty> [--target <language>] [--output <file>]');
    console.log('\nSupported target languages:');
    console.log('  javascript (default), python, go, rust, java, c');
    process.exit(0);
  }

  const filename = args[0];
  
  if (!fs.existsSync(filename)) {
    console.error(`Error: File '${filename}' not found`);
    process.exit(1);
  }

  let targetLanguage = 'javascript';
  let outputFile = null;
  let wrapMain = false;

  // Parse arguments
  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--target' && args[i + 1]) {
      targetLanguage = args[i + 1];
      i++;
    } else if (args[i] === '--output' && args[i + 1]) {
      outputFile = args[i + 1];
      i++;
    } else if (args[i] === '--wrap') {
      wrapMain = true;
    }
  }

  const code = fs.readFileSync(filename, 'utf-8');
  const transpiler = new ThirstyTranspiler(targetLanguage);
  const transpiledCode = transpiler.transpile(code);
  const finalCode = wrapMain ? transpiler.generateWrapper() : transpiledCode;

  if (outputFile) {
    fs.writeFileSync(outputFile, finalCode);
    console.log(`✓ Transpiled to ${targetLanguage} and saved to ${outputFile}`);
  } else {
    console.log(`// Transpiled to ${targetLanguage}\n`);
    console.log(finalCode);
  }
}

if (require.main === module) {
  main();
}

module.exports = ThirstyTranspiler;
