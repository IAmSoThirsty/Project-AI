#!/usr/bin/env node

/**
 * Thirsty-lang AST (Abstract Syntax Tree) Generator
 * Visualize the structure of your code
 */

const fs = require('fs');

class ThirstyAST {
  constructor() {
    this.ast = {
      type: 'Program',
      body: []
    };
  }

  parse(code) {
    const lines = code.split('\n')
      .map((line, idx) => ({ line: line.trim(), lineNumber: idx + 1 }))
      .filter(item => item.line && !item.line.startsWith('//'));

    for (const {line, lineNumber} of lines) {
      const node = this.parseStatement(line, lineNumber);
      if (node) {
        this.ast.body.push(node);
      }
    }

    return this.ast;
  }

  parseStatement(line, lineNumber) {
    // Variable declaration
    if (line.startsWith('drink ')) {
      const match = line.match(/drink\s+(\w+)\s*=\s*(.+)/);
      if (match) {
        return {
          type: 'VariableDeclaration',
          name: match[1],
          value: this.parseExpression(match[2]),
          lineNumber
        };
      }
    }

    // Output statement
    if (line.startsWith('pour ')) {
      const expr = line.substring(5).trim();
      return {
        type: 'OutputStatement',
        expression: this.parseExpression(expr),
        lineNumber
      };
    }

    return {
      type: 'UnknownStatement',
      value: line,
      lineNumber
    };
  }

  parseExpression(expr) {
    expr = expr.trim();

    // String literal
    if ((expr.startsWith('"') && expr.endsWith('"')) ||
        (expr.startsWith("'") && expr.endsWith("'"))) {
      return {
        type: 'StringLiteral',
        value: expr.slice(1, -1)
      };
    }

    // Number literal
    if (!isNaN(expr)) {
      return {
        type: 'NumberLiteral',
        value: parseFloat(expr)
      };
    }

    // Identifier (variable reference)
    return {
      type: 'Identifier',
      name: expr
    };
  }

  visualize() {
    console.log('\n🌳 Abstract Syntax Tree\n');
    console.log(JSON.stringify(this.ast, null, 2));
  }

  visualizeTree(node = this.ast, prefix = '', isLast = true) {
    const marker = isLast ? '└── ' : '├── ';
    const line = prefix + marker;

    if (node.type === 'Program') {
      console.log('Program');
      node.body.forEach((child, index) => {
        const childIsLast = index === node.body.length - 1;
        const childPrefix = '';
        this.visualizeTree(child, childPrefix, childIsLast);
      });
    } else if (node.type === 'VariableDeclaration') {
      console.log(`${line}VariableDeclaration (line ${node.lineNumber})`);
      console.log(`${prefix}${isLast ? '    ' : '│   '}├── name: ${node.name}`);
      console.log(`${prefix}${isLast ? '    ' : '│   '}└── value: ${this.formatExpression(node.value)}`);
    } else if (node.type === 'OutputStatement') {
      console.log(`${line}OutputStatement (line ${node.lineNumber})`);
      console.log(`${prefix}${isLast ? '    ' : '│   '}└── expression: ${this.formatExpression(node.expression)}`);
    }
  }

  formatExpression(expr) {
    if (expr.type === 'StringLiteral') {
      return `"${expr.value}"`;
    } else if (expr.type === 'NumberLiteral') {
      return expr.value.toString();
    } else if (expr.type === 'Identifier') {
      return expr.name;
    }
    return JSON.stringify(expr);
  }

  generateDiagram() {
    console.log('\n📊 AST Diagram\n');
    this.visualizeTree();
  }

  exportJSON(filepath) {
    fs.writeFileSync(filepath, JSON.stringify(this.ast, null, 2));
    console.log(`✓ AST exported to ${filepath}`);
  }
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('Thirsty-lang AST Generator');
    console.log('Usage: node src/ast.js <file.thirsty> [--json output.json]');
    console.log('\nGenerates and visualizes the Abstract Syntax Tree');
    process.exit(0);
  }

  const filename = args[0];
  
  if (!fs.existsSync(filename)) {
    console.error(`Error: File '${filename}' not found`);
    process.exit(1);
  }

  const code = fs.readFileSync(filename, 'utf-8');
  const astGenerator = new ThirstyAST();
  astGenerator.parse(code);
  astGenerator.generateDiagram();

  // Export JSON if requested
  const jsonIndex = args.indexOf('--json');
  if (jsonIndex !== -1 && args[jsonIndex + 1]) {
    astGenerator.exportJSON(args[jsonIndex + 1]);
  }
}

if (require.main === module) {
  main();
}

module.exports = ThirstyAST;
