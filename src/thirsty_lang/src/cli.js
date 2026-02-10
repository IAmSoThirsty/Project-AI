#!/usr/bin/env node

/**
 * Thirsty-lang CLI
 * Command-line interface for running Thirsty-lang programs
 */

const fs = require('fs');
const path = require('path');
const ThirstyInterpreter = require('./index');
const { validatePath, validateExtension, isValidFile } = require('./path-validator');

function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Thirsty-lang Interpreter v1.0.0');
    console.log('Usage: node src/cli.js <filename.thirsty>');
    console.log('       npm start <filename.thirsty>');
    console.log('\nStay hydrated! 💧');
    process.exit(0);
  }

  const filename = args[0];
  
  // Validate the filename to prevent path traversal
  try {
    const validatedPath = validatePath(filename);
    
    // Check if file exists
    if (!isValidFile(validatedPath)) {
      console.error(`Error: File '${filename}' not found or is not a valid file`);
      process.exit(1);
    }
    
    // Validate file extension (optional but recommended)
    if (!validateExtension(validatedPath, ['.thirsty', '.js'])) {
      console.warn(`Warning: File '${filename}' does not have a .thirsty extension`);
    }
    
    const code = fs.readFileSync(validatedPath, 'utf-8');
    const interpreter = new ThirstyInterpreter();
    interpreter.execute(code);
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = main;
