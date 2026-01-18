#!/usr/bin/env node

/**
 * Thirsty-lang Code Morphing System
 * Dynamic code transformation to evade analysis and cripple attackers
 */

class CodeMorpher {
  constructor(options = {}) {
    this.morphLevel = options.morphLevel || 'aggressive';
    this.morphHistory = [];
    this.obfuscationTechniques = this.initializeTechniques();
  }

  /**
   * Initialize obfuscation and morphing techniques
   */
  initializeTechniques() {
    return {
      // Identifier obfuscation
      identifierMorphing: true,

      // Control flow obfuscation
      controlFlowFlattening: true,
      opaquePredicates: true,

      // String obfuscation
      stringEncryption: true,
      stringArray: true,

      // Dead code injection
      deadCodeInjection: true,

      // Code virtualization
      codeVirtualization: false, // Advanced feature

      // Anti-debugging
      antiDebugChecks: true,
      selfModifyingCode: true
    };
  }

  /**
   * Morph code dynamically
   */
  morph(code, options = {}) {
    const morphOptions = { ...this.obfuscationTechniques, ...options };
    let morphedCode = code;

    // Apply morphing techniques in sequence
    if (morphOptions.identifierMorphing) {
      morphedCode = this.morphIdentifiers(morphedCode);
    }

    if (morphOptions.stringEncryption) {
      morphedCode = this.encryptStrings(morphedCode);
    }

    if (morphOptions.controlFlowFlattening) {
      morphedCode = this.flattenControlFlow(morphedCode);
    }

    if (morphOptions.deadCodeInjection) {
      morphedCode = this.injectDeadCode(morphedCode);
    }

    if (morphOptions.antiDebugChecks) {
      morphedCode = this.insertAntiDebugChecks(morphedCode);
    }

    // Log morphing operation
    this.morphHistory.push({
      timestamp: Date.now(),
      originalLength: code.length,
      morphedLength: morphedCode.length,
      techniques: Object.keys(morphOptions).filter(function (k) { return morphOptions[k] })
    });

    return morphedCode;
  }

  /**
   * Morph variable and function identifiers
   */
  morphIdentifiers(code) {
    const identifierMap = new Map();
    let counter = 0;

    // Find all identifiers (simplified pattern)
    const identifierPattern = /\b(drink|glass)\s+([a-zA-Z_][a-zA-Z0-9_]*)/g;

    let match;
    while ((match = identifierPattern.exec(code)) !== null) {
      const identifier = match[2];
      if (!identifierMap.has(identifier)) {
        identifierMap.set(identifier, this.generateObfuscatedName(counter++));
      }
    }

    // Replace identifiers
    let morphedCode = code;
    for (const [original, obfuscated] of identifierMap.entries()) {
      const regex = new RegExp(`\\b${original}\\b`, 'g');
      morphedCode = morphedCode.replace(regex, obfuscated);
    });

    return morphedCode;
  }

  /**
   * Generate obfuscated identifier name
   */
  generateObfuscatedName(index) {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const confusingChars = ['O0', 'I1', 'l1', 'S5', 'Z2'];

    let name = '_';
    let num = index;

    // Generate confusing identifier
    while (num >= 0) {
      name += chars[num % chars.length];
      num = Math.floor(num / chars.length) - 1;
    }

    // Add confusing characters
    const confusing = confusingChars[index % confusingChars.length];
    name += confusing;

    return name;
  }

  /**
   * Encrypt string literals
   */
  encryptStrings(code) {
    const stringPattern = /(["'])(?:(?=(\\?))\2.)*?\1/g;
    const strings = [];

    // Extract strings
    let match;
    while ((match = stringPattern.exec(code)) !== null) {
      strings.push(match[0]);
    }

    // Replace with encrypted versions
    let morphedCode = code;
    for (const [index, str] of strings.entries()) {
      const encrypted = this.encryptString(str.slice(1, -1));
      const quote = str[0];
      const decryptCall = `_decrypt${index}(${quote}${encrypted}${quote})`;
      morphedCode = morphedCode.replace(str, decryptCall);
    });

    return morphedCode;
  }

  /**
   * Simple string encryption (ROT13-like)
   */
  encryptString(str) {
    return str.split('').map(char => {
      const code = char.charCodeAt(0);
      if (code >= 65 && code <= 90) {
        return String.fromCharCode(((code - 65 + 13) % 26) + 65);
      } else if (code >= 97 && code <= 122) {
        return String.fromCharCode(((code - 97 + 13) % 26) + 97);
      }
      return char;
    }).join('');
  }

  /**
   * Flatten control flow to make analysis harder
   */
  flattenControlFlow(code) {
    // Insert opaque predicates (always true/false but hard to determine)
    const opaquePredicates = [
      'if (Math.random() * 0 === 0) {',
      'if (new Date().getTime() > 0) {',
      'if (typeof undefined === "undefined") {'
    ];

    const lines = code.split('\n');
    const morphedLines = [];

    lines.forEach(line => {
      // Randomly insert opaque predicates
      if (Math.random() > 0.7 && line.trim() !== '') {
        const predicate = opaquePredicates[Math.floor(Math.random() * opaquePredicates.length)];
        morphedLines.push(predicate);
        morphedLines.push('  ' + line);
        morphedLines.push('}');
      } else {
        morphedLines.push(line);
      }
    });

    return morphedLines.join('\n');
  }

  /**
   * Inject dead code to confuse analyzers
   */
  injectDeadCode(code) {
    const deadCodeSnippets = [
      '// Anti-tamper check\nif (false) { throw new Error("Tamper detected"); }',
      '// Fake variable\nconst _fake = Math.random() * 1000000;',
      '// Decoy function\nfunction _decoy() { return null; }',
      '// Integrity check\nif (0 > 1) { process.exit(1); }'
    ];

    const lines = code.split('\n');
    const insertionPoints = Math.floor(lines.length / 4);

    for (let i = 0; i < insertionPoints; i++) {
      const position = Math.floor(Math.random() * lines.length);
      const snippet = deadCodeSnippets[Math.floor(Math.random() * deadCodeSnippets.length)];
      lines.splice(position, 0, snippet);
    }

    return lines.join('\n');
  }

  /**
   * Insert anti-debugging checks
   */
  insertAntiDebugChecks(code) {
    const antiDebugCode = `
// Anti-debug protection
(function() {
  const start = Date.now();
  debugger;
  const end = Date.now();
  if (end - start > 100) {
    throw new Error("Debug detected");
  }
})();

// Timing check
const _timing = Date.now();
`;

    return antiDebugCode + code;
  }

  /**
   * Create polymorphic variant of code
   */
  createPolymorphicVariant(code) {
    // Generate different but functionally equivalent code
    const variants = [
      (c) => this.reorderStatements(c),
      (c) => this.insertNoOps(c),
      (c) => this.substituteOperators(c)
    ];

    let variant = code;
    const technique = variants[Math.floor(Math.random() * variants.length)];
    variant = technique(variant);

    return variant;
  }

  /**
   * Reorder independent statements
   */
  reorderStatements(code) {
    // Simplified: just reverse some comment lines
    const lines = code.split('\n');
    const commentLines = lines.filter(l => l.trim().startsWith('//'));
    const nonCommentLines = lines.filter(l => !l.trim().startsWith('//'));

    return [...commentLines.reverse(), ...nonCommentLines].join('\n');
  }

  /**
   * Insert no-operation statements
   */
  insertNoOps(code) {
    const noOps = [
      'void 0;',
      '0 + 0;',
      'true && true;',
      '[] + [];'
    ];

    const lines = code.split('\n');
    for (let i = 0; i < 3; i++) {
      const position = Math.floor(Math.random() * lines.length);
      const noOp = noOps[Math.floor(Math.random() * noOps.length)];
      lines.splice(position, 0, noOp);
    }

    return lines.join('\n');
  }

  /**
   * Substitute operators with equivalent expressions
   */
  substituteOperators(code) {
    // Replace simple operators with complex equivalents
    let morphed = code;

    // Example: x + 1 => x - (-1)
    morphed = morphed.replace(/\+\s*1(?!\d)/g, '- (-1)');

    // Example: x * 2 => x << 1
    morphed = morphed.replace(/\*\s*2(?!\d)/g, '<< 1');

    return morphed;
  }

  /**
   * Generate self-modifying code wrapper
   */
  generateSelfModifyingWrapper(code) {
    const encoded = Buffer.from(code).toString('base64');

    return `
// Self-modifying code wrapper
(function() {
  const encoded = "${encoded}";
  const decoded = Buffer.from(encoded, 'base64').toString('utf-8');
  eval(decoded);
})();
`;
  }

  /**
   * Get morphing statistics
   */
  getMorphStats() {
    return {
      totalMorphs: this.morphHistory.length,
      avgSizeIncrease: this.morphHistory.reduce((acc, m) =>
        acc + (m.morphedLength - m.originalLength), 0) / this.morphHistory.length || 0,
      techniques: this.obfuscationTechniques
    };
  }

  /**
   * Reset morph history
   */
  resetHistory() {
    this.morphHistory = [];
  }
}

module.exports = CodeMorpher;
