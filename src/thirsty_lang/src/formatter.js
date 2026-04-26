/**
 * Thirsty-lang Code Formatter
 * Beautify your Thirsty code!
 */

const fs = require('fs');

class ThirstyFormatter {
  constructor(options = {}) {
    this.options = {
      indentSize: options.indentSize || 2,
      useTabs: options.useTabs || false,
      maxLineLength: options.maxLineLength || 80,
      insertFinalNewline: options.insertFinalNewline !== false,
      trimTrailingWhitespace: options.trimTrailingWhitespace !== false
    };
  }

  format(code) {
    var lines = code.split('\n');
    var formatted = [];
    var indentLevel = 0;

    for (var i = 0; i < lines.length; i++) {
      var line = lines[i].trim();

      // Skip empty lines
      if (!line) {
        formatted.push('');
        continue;
      }

      // Preserve comments
      if (line.startsWith('//')) {
        formatted.push(this.indent(indentLevel) + line);
        continue;
      }

      // Handle block end (future: for control structures)
      if (line === '}' || line === 'hydrated') {
        indentLevel = Math.max(0, indentLevel - 1);
      }

      // Format the line
      var formattedLine = this.formatLine(line);
      formatted.push(this.indent(indentLevel) + formattedLine);

      // Handle block start (future: for control structures)
      if (line.startsWith('thirsty ') || line.startsWith('glass ') ||
        line.startsWith('fountain ') || line.startsWith('refill ')) {
        indentLevel++;
      }
    }

    var result = formatted.join('\n');

    if (this.options.insertFinalNewline && !result.endsWith('\n')) {
      result += '\n';
    }

    return result;
  }

  formatLine(line) {
    // Format drink statements
    if (line.startsWith('drink ')) {
      const match = line.match(/drink\s+(\w+)\s*=\s*(.+)/);
      if (match) {
        return 'drink ' + match[1] + ' = ' + match[2].trim();
      }
    }

    // Format pour statements
    if (line.startsWith('pour ')) {
      const expr = line.substring(5).trim();
      return "pour " + expr;
    }

    return line;
  }

  indent(level) {
    if (this.options.useTabs) {
      return '\t'.repeat(level);
    }
    return ' '.repeat(level * this.options.indentSize);
  }

  formatFile(inputPath, outputPath = null) {
    try {
      // Validate input path
      const validatedInputPath = validatePath(inputPath);
      if (!isValidFile(validatedInputPath)) {
        throw new Error('Input path is not a valid file');
      }
      
      const code = fs.readFileSync(validatedInputPath, 'utf-8');
      const formatted = this.format(code);

      if (outputPath) {
        // Validate output path
        const validatedOutputPath = validatePath(outputPath);
        fs.writeFileSync(validatedOutputPath, formatted);
        console.log('✓ Formatted ' + inputPath + ' -> ' + outputPath);
      } else {
        fs.writeFileSync(validatedInputPath, formatted);
        console.log('✓ Formatted ' + inputPath);
      }
    } catch (error) {
      console.error('❌ Error formatting file: ' + error.message);
      throw error;
    }
  }
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Thirsty-lang Code Formatter');
    console.log('Usage: node src/formatter.js <file.thirsty> [output.thirsty]');
    console.log('\nOptions:');
    console.log('  --indent-size <n>    Set indent size (default: 2)');
    console.log('  --use-tabs           Use tabs instead of spaces');
    console.log('  --check              Check if file is formatted');
    process.exit(0);
  }

  const options = {};
  var inputFile = null;
  var outputFile = null;
  var checkMode = false;

  for (var i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--indent-size') {
      options.indentSize = parseInt(args[++i]);
    } else if (arg === '--use-tabs') {
      options.useTabs = true;
    } else if (arg === '--check') {
      checkMode = true;
    } else if (!inputFile) {
      inputFile = arg;
    } else if (!outputFile) {
      outputFile = arg;
    }
  }

  if (!inputFile) {
    console.error('Error: No input file specified');
    process.exit(1);
  }

  const formatter = new ThirstyFormatter(options);

  if (checkMode) {
    const code = fs.readFileSync(inputFile, 'utf-8');
    const formatted = formatter.format(code);

    if (code === formatted) {
      console.log('✓ File is properly formatted');
      process.exit(0);
    } else {
      console.log('✗ File needs formatting');
      process.exit(1);
    }
  } else {
    formatter.formatFile(inputFile, outputFile);
  }
}

if (require.main === module) {
  main();
}

module.exports = ThirstyFormatter;
