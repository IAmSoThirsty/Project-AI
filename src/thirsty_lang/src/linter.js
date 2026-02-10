/**
 * Thirsty-lang Linter
 * Keep your code clean and hydrated!
 */

const fs = require('fs');
const { validatePath, isValidFile } = require('./path-validator');

class ThirstyLinter {
  constructor(options = {}) {
    this.options = {
      maxLineLength: options.maxLineLength || 80,
      requireSpacesAroundEquals: options.requireSpacesAroundEquals !== false,
      noUnusedVariables: options.noUnusedVariables !== false,
      namingConvention: options.namingConvention || 'snake_case'
    };

    this.errors = [];
    this.warnings = [];
  }

  lint(code, filename = '<input>') {
    this.errors = [];
    this.warnings = [];

    const lines = code.split('\n');
    const declaredVars = new Set();
    const usedVars = new Set();

    for (const [index, line] of lines.entries()) {
      const lineNum = index + 1;
      const trimmed = line.trim();

      // Skip empty lines and comments
      if (!trimmed || trimmed.startsWith('//')) return;

      // Check line length
      if (line.length > this.options.maxLineLength) {
        this.warnings.push({
          line: lineNum,
          message: `Line exceeds ${this.options.maxLineLength} characters`,
          severity: 'warning'
        });
      }

      // Check for trailing whitespace
      if (line !== trimmed && line.endsWith(' ')) {
        this.warnings.push({
          line: lineNum,
          message: 'Trailing whitespace detected',
          severity: 'warning'
        });
      }

      // Check drink statements
      if (trimmed.startsWith('drink ')) {
        const match = trimmed.match(/drink\s+(\w+)\s*=\s*(.+)/);

        if (!match) {
          this.errors.push({
            line: lineNum,
            message: 'Invalid drink statement syntax',
            severity: 'error'
          });
          return;
        }

        const varName = match[1];
        declaredVars.add(varName);

        // Check naming convention
        if (!this.checkNamingConvention(varName)) {
          this.warnings.push({
            line: lineNum,
            message: "Variable '" + varName + "' doesn't follow " + this.options.namingConvention + " convention",
            severity: 'warning'
          });
        }

        // Check spacing around equals
        if (this.options.requireSpacesAroundEquals) {
          if (!trimmed.includes(' = ')) {
            this.warnings.push({
              line: lineNum,
              message: 'Expected spaces around = operator',
              severity: 'warning'
            });
          }
        }
      }

      // Check pour statements and track variable usage
      if (trimmed.startsWith('pour ')) {
        const expr = trimmed.substring(5).trim();

        // Check if it's a variable reference
        if (!expr.startsWith('"') && !expr.startsWith("'") && isNaN(expr)) {
          usedVars.add(expr);

          // This will be checked later after all declarations
        }
      }

      // Check for unknown statements
      const knownKeywords = ['drink', 'pour', 'sip', 'thirsty', 'hydrated', 'refill', 'glass', 'fountain'];
      const startsWithKnown = knownKeywords.some(function (kw) { return trimmed.startsWith(kw + ' ') });

      if (!startsWithKnown && !trimmed.startsWith('//')) {
        this.errors.push({
          line: lineNum,
          message: 'Unknown statement or syntax error',
          severity: 'error'
        });
      }
    });

    // Check for unused variables
    if (this.options.noUnusedVariables) {
      for (const varName of declaredVars) {
        if (!usedVars.has(varName)) {
          this.warnings.push({
            line: 0,
            message: "Variable '" + varName + "' is declared but never used",
            severity: 'warning'
          });
        }
      }
    }

    return {
      filename,
      errors: this.errors,
      warnings: this.warnings,
      isValid: this.errors.length === 0
    };
  }

  checkNamingConvention(name) {
    switch (this.options.namingConvention) {
      case 'snake_case':
        return /^[a-z_][a-z0-9_]*$/.test(name);
      case 'camelCase':
        return /^[a-z][a-zA-Z0-9]*$/.test(name);
      case 'PascalCase':
        return /^[A-Z][a-zA-Z0-9]*$/.test(name);
      default:
        return true;
    }
  }

  printResults(results) {
    console.log(`\n📋 Linting: ${results.filename}`);
    console.log('═'.repeat(60));

    if (results.errors.length === 0 && results.warnings.length === 0) {
      console.log('✓ No issues found! Code is perfectly hydrated! 💧');
      return;
    }

    // Print errors
    if (results.errors.length > 0) {
      console.log('\n❌ Errors:');
      for (const err of results.errors) {
        console.log(`  Line ${err.line}: ${err.message}`);
      });
    }

    // Print warnings
    if (results.warnings.length > 0) {
      console.log('\n⚠️  Warnings:');
      results.warnings.forEach(warn => {
        if (warn.line > 0) {
          console.log(`  Line ${warn.line}: ${warn.message}`);
        } else {
          console.log(`  ${warn.message}`);
        }
      });
    }

    console.log(`\n${results.errors.length} error(s), ${results.warnings.length} warning(s)`);
  }

  lintFile(filepath) {
    try {
      // Validate filepath to prevent path traversal
      const validatedPath = validatePath(filepath);
      if (!isValidFile(validatedPath)) {
        throw new Error('File not found or is not a valid file');
      }
      const code = fs.readFileSync(validatedPath, 'utf-8');
      const results = this.lint(code, filepath);
      this.printResults(results);
      return results.isValid;
    } catch (error) {
      console.error('❌ Error linting file: ' + error.message);
      return false;
    }
  }
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Thirsty-lang Linter');
    console.log('Usage: node src/linter.js <file.thirsty>');
    console.log('\nOptions:');
    console.log('  --max-line-length <n>    Set max line length (default: 80)');
    console.log('  --naming <convention>    Set naming convention (snake_case|camelCase|PascalCase)');
    console.log('  --no-unused-check        Disable unused variable check');
    process.exit(0);
  }

  const options = {};
  const files = [];

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--max-line-length') {
      options.maxLineLength = parseInt(args[++i]);
    } else if (arg === '--naming') {
      options.namingConvention = args[++i];
    } else if (arg === '--no-unused-check') {
      options.noUnusedVariables = false;
    } else {
      files.push(arg);
    }
  }

  const linter = new ThirstyLinter(options);
  let allValid = true;

  files.forEach(file => {
    const isValid = linter.lintFile(file);
    allValid = allValid && isValid;
  });

  process.exit(allValid ? 0 : 1);
}

if (require.main === module) {
  main();
}

module.exports = ThirstyLinter;
